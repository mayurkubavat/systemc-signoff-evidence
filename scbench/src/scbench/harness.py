"""Run agents on benchmark tasks, with and without the verification tools.

For each task and arm the harness:
  1. makes a workspace holding a one-commit snapshot of the task's base tree,
     with no history, branches or remote, so the reference change and the
     hidden regression test are not reachable from it,
  2. runs an agent with the task text through a generic adapter (below),
     either shell-only or with the scbench MCP server configured,
  3. restores the hidden test files from the gold commit and grades the
     agent's tree with the same run_test tool, in a fresh build directory,
  4. writes one JSON record per run.

Runs go seed-major, a rerun with the same --out skips graded runs, and
--jobs runs several at a time (each with its own worktree and build dirs).

Agent adapter
-------------
The agent is any command line given by --agent-cmd or the AGENT_CMD
environment variable. The harness runs it with cwd = the task worktree and:
  * the prompt on stdin,
  * SCBENCH_PROMPT_FILE   path of a file holding the same prompt,
  * SCBENCH_MCP_CONFIG    path of an MCP config file ({"mcpServers": {...}});
                          empty server list in the shell arm, scbench in the tools arm,
  * SCBENCH_ARM           shell | tools | shell-guided | tools-guided,
  * SCBENCH_MAX_TURNS     the turn budget the agent must enforce,
  * SCBENCH_SUMMARY_FILE  where the agent may write a JSON summary:
        {"num_turns": int, "tool_calls": {name: count},
         "usage": {"input_tokens": int, "output_tokens": int},
         "status": "ok" | "error" | "rate_limited", "error": str}
The command's stdout and stderr are saved as agent.stdout.txt and
agent.stderr.txt. The run is graded unless the summary says "error" or
"rate_limited". The pilot used two vendor CLIs through adapters of this
shape, each in an isolated home and with only shell, file and MCP tools.

    python -m scbench.harness --workbench <workbench> --tasks tasks/pilot.json \
        --arms shell,tools --seeds 3 --out results/baseline-model-c --agent-cmd "my-agent --headless"
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import tools

PROMPT = """You are working in a checkout of the {project} library at {cwd}.

Task:
{description}

Change the library source to resolve the task. You may add or change tests.
Do not commit, push, or modify anything outside this directory.
{arm_note}"""

ARM_NOTES = {
    "shell": ("Build and test with the shell (cmake, ninja, ctest). SystemC is installed "
              "at $SYSTEMC_HOME. Use a build directory inside this checkout."),
    "tools": ("Verification tools are available through the scbench MCP server: build, "
              "list_tests, run_test, run_regression, query_coverage, randomize_check. "
              "Prefer them over raw shell builds."),
}

UVM_REF = os.path.expanduser("~/Tools/uvm-core/src")

GUIDED_FILE = Path(__file__).resolve().parents[2] / "prompts" / "guided.md"

RUN_HINTS = {
    "shell": ("ctest -R <test path> in your build directory; build only that test's target",
              "ctest -R <area> in your build directory"),
    "tools": ("run_test", "run_regression with a pattern for the area"),
}

def base_arm(arm: str) -> str:
    """shell-guided -> shell; the tool set depends only on the base arm."""
    return arm.split("-")[0]

def guided_text(arm: str, max_turns: int) -> str:
    run, reg = RUN_HINTS[base_arm(arm)]
    return GUIDED_FILE.read_text().format(run_hint=run, regression_hint=reg,
                                          uvm_ref=UVM_REF, max_turns=max_turns)

def guided_hash() -> str:
    return hashlib.sha256(GUIDED_FILE.read_bytes()).hexdigest()[:16]

def make_prompt(task: dict, wt: Path, arm: str, max_turns: int) -> str:
    note = ARM_NOTES[base_arm(arm)]
    if arm.endswith("-guided"):
        note = note + "\n\n" + guided_text(arm, max_turns)
    return PROMPT.format(project=task["project"], cwd=wt,
                         description=task["description"], arm_note=note)

def sh(cmd: list[str], cwd: Path | None = None, check: bool = True) -> str:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check).stdout

_SNAP_LOCK = threading.Lock()


def snapshot_repo(repo: Path, base: str, cache: Path) -> tuple[Path, str]:
    """A repository holding one commit: the tree of `base`, with no history,
    branches or other objects. Agent workspaces are made from it, so the gold
    commits and task branches of the fork are not reachable from a workspace.
    Returns the snapshot path and its single commit id."""
    snap = cache / f"{repo.parent.name}-{base[:12]}"
    with _SNAP_LOCK:
        head = snap / ".snapshot-head"
        if not head.exists():
            snap.mkdir(parents=True, exist_ok=True)
            arch = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", base],
                                  capture_output=True, check=True).stdout
            subprocess.run(["tar", "-x", "-C", str(snap)], input=arch, check=True)
            env = dict(os.environ, GIT_AUTHOR_NAME="scbench", GIT_AUTHOR_EMAIL="scbench@localhost",
                       GIT_COMMITTER_NAME="scbench", GIT_COMMITTER_EMAIL="scbench@localhost",
                       GIT_AUTHOR_DATE="2000-01-01T00:00:00Z", GIT_COMMITTER_DATE="2000-01-01T00:00:00Z")
            for cmd in (["init", "-q", "-b", "base"], ["add", "-A", "-f"],
                        ["commit", "-q", "--no-verify", "-m", "base snapshot"]):
                subprocess.run(["git", "-C", str(snap), *cmd], check=True, env=env, capture_output=True)
            head.write_text(sh(["git", "-C", str(snap), "rev-parse", "HEAD"]).strip())
        return snap, head.read_text().strip()


def make_worktree(snap: Path, snap_head: str, dest: Path) -> None:
    if dest.exists():
        sh(["git", "-C", str(snap), "worktree", "remove", "--force", str(dest)], check=False)
    dest.parent.mkdir(parents=True, exist_ok=True)
    sh(["git", "-C", str(snap), "worktree", "add", "--detach", str(dest), snap_head])


def drop_worktree(snap: Path, dest: Path) -> None:
    sh(["git", "-C", str(snap), "worktree", "remove", "--force", str(dest)], check=False)


def mcp_servers(wt: Path, profile: str, arm: str) -> dict:
    servers = {}
    if arm == "tools":
        servers["scbench"] = {
            "command": sys.executable, "args": ["-m", "scbench.server"],
            "env": {"SCBENCH_REPO": str(wt), "SCBENCH_PROFILE": profile,
                    "SCBENCH_BUILD": str(wt / "build-scbench"),
                    "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
                    **{k: os.environ[k] for k in ("SYSTEMC_HOME", "UVM_SYSTEMC_HOME",
                                                  "CRAVE_HOME", "FC4SC_HOME", "PATH")
                       if k in os.environ}},
        }
    return servers

def mcp_config(path: Path, wt: Path, profile: str, arm: str) -> Path:
    path.write_text(json.dumps({"mcpServers": mcp_servers(wt, profile, arm)}, indent=2))
    return path

def grade(task: dict, repo: Path, wt: Path, snap_head: str) -> dict:
    # Agents may have created files with the hidden names; the gold version wins.
    # The hidden files come from the full fork clone, never from the workspace.
    for f in task["hidden_files"]:
        data = subprocess.run(["git", "-C", str(repo), "show", f"{task['gold']}:{f}"],
                              capture_output=True, check=True).stdout
        p = wt / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    diff = sh(["git", "-C", str(wt), "diff", "--stat", snap_head, "--",
               *[f":(exclude){f}" for f in task["hidden_files"]]], check=False)
    ws = tools.Workspace(str(wt), task["project"], str(wt / "build-grade"))
    results = [ws.run_test(t) for t in task["tests"]]
    return {"passed": all(r.get("passed") for r in results), "tests": results,
            "agent_diffstat": diff.strip().splitlines()[-1:] if diff.strip() else []}


GRADED = ("pass", "fail")

def run_tag(task_id: str, arm: str, seed: int) -> str:
    return f"{task_id.replace(':', '__')}__{arm}__s{seed}"

def is_done(run_dir: Path) -> bool:
    """True when the run has a graded record (pass or fail). Runs that
    errored, were rate limited or never finished are run again."""
    try:
        rec = json.loads((run_dir / "record.json").read_text())
    except (OSError, ValueError):
        return False
    return rec.get("status") in GRADED

def schedule(tasks: list[dict], arms: list[str], seeds: int) -> list[tuple[dict, str, int]]:
    """(task, arm, seed) in seed-major order; gold/base checks run once."""
    if set(arms) <= {"gold", "base"}:
        return [(t, a, 0) for t in tasks for a in arms]
    return [(t, a, s) for s in range(seeds) for t in tasks for a in arms]

def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def run_agent(task: dict, wt: Path, arm: str, agent_cmd: str, max_turns: int,
              timeout: int, out_dir: Path) -> dict:
    """Run the configured agent command on one task (see the module docstring)."""
    prompt = make_prompt(task, wt, arm, max_turns)
    cfg = mcp_config(out_dir / "mcp.json", wt, task["project"], base_arm(arm))
    pfile = out_dir / "prompt.txt"
    pfile.write_text(prompt)
    summary_file = out_dir / "agent.summary.json"
    env = dict(os.environ, SCBENCH_PROMPT_FILE=str(pfile), SCBENCH_MCP_CONFIG=str(cfg),
               SCBENCH_ARM=arm, SCBENCH_MAX_TURNS=str(max_turns), SCBENCH_SUMMARY_FILE=str(summary_file))
    t0 = time.time()
    with (out_dir / "agent.stdout.txt").open("w") as out, (out_dir / "agent.stderr.txt").open("w") as err:
        try:
            rc = subprocess.run(agent_cmd, shell=True, cwd=wt, input=prompt, text=True, stdout=out,
                                stderr=err, env=env, timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            rc = 124
    info = {"exit": rc, "status": "ok"}
    if summary_file.exists():
        try:
            info.update(json.loads(summary_file.read_text()))
        except ValueError:
            info.update({"status": "error", "error": "unreadable agent summary"})
    elif rc == 127:
        info.update({"status": "error", "error": "agent command not found"})
    if rc == 124:
        info["timed_out"] = True
    info["max_turns"] = max_turns
    info["wall_s"] = round(time.time() - t0, 1)
    (out_dir / "agent.json").write_text(json.dumps(info, indent=2))
    return info


def run_one(t: dict, arm: str, seed: int, a: argparse.Namespace, wb: Path, out_root: Path) -> dict:
    repo = wb / t["project"] / "src"
    tag = run_tag(t["id"], arm, seed)
    run_dir = out_root / tag
    run_dir.mkdir(parents=True, exist_ok=True)
    wt = Path(a.worktrees) / tag
    snap, snap_head = snapshot_repo(repo, t["base"], Path(a.worktrees) / "_snapshots")
    make_worktree(snap, snap_head, wt)
    rec = {"task": t["id"], "arm": arm, "seed": seed, "model": a.model or "unspecified"}
    try:
        if arm == "gold":
            patch = subprocess.run(["git", "-C", str(repo), "diff", "--binary", t["base"], t["gold"]],
                                   capture_output=True, check=True).stdout
            subprocess.run(["git", "-C", str(wt), "apply", "--whitespace=nowarn"], input=patch, check=True,
                           capture_output=True)
        elif arm != "base":
            rec["agent"] = run_agent(t, wt, arm, a.agent_cmd, a.max_turns, a.timeout, run_dir)
        st = rec.get("agent", {}).get("status")
        if st in ("error", "rate_limited"):
            rec["status"] = st
            rec["error"] = rec["agent"].get("error", "")
        else:
            rec["grade"] = grade(t, repo, wt, snap_head)
            rec["status"] = "pass" if rec["grade"]["passed"] else "fail"
    except subprocess.CalledProcessError as e:
        rec["status"] = "error"
        rec["error"] = f"{e.cmd}: {e.stderr[-2000:] if e.stderr else ''}"
    finally:
        drop_worktree(snap, wt)
    (run_dir / "record.json").write_text(json.dumps(rec, indent=2))
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbench", required=True)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--arms", default="shell,tools")
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--only", default="", help="comma-separated task ids")
    ap.add_argument("--agent-cmd", default=os.environ.get("AGENT_CMD", ""))
    ap.add_argument("--model", default="", help="label recorded with each run")
    ap.add_argument("--max-turns", type=int, default=60)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--worktrees", default=os.path.expanduser("~/.cache/scbench/wt"))
    ap.add_argument("--gold-check", action="store_true",
                    help="no agent: apply the gold change and grade (validates each task)")
    a = ap.parse_args()
    if not a.gold_check and not a.agent_cmd:
        ap.error("set --agent-cmd or AGENT_CMD")
    wb = Path(a.workbench).expanduser()
    tasks = json.loads(Path(a.tasks).read_text())
    if a.only:
        keep = set(a.only.split(","))
        tasks = [t for t in tasks if t["id"] in keep]
    out_root = Path(a.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    arms = ["gold", "base"] if a.gold_check else a.arms.split(",")
    plan = schedule(tasks, arms, a.seeds)

    def process(i: int, t: dict, arm: str, seed: int) -> None:
        tag = run_tag(t["id"], arm, seed)
        if is_done(out_root / tag):
            log(f"{i}/{len(plan)} {tag}: skip (graded)")
            return
        rec = run_one(t, arm, seed, a, wb, out_root)
        log(f"{i}/{len(plan)} {tag}: {rec['status'].upper()}")

    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as pool:
        for f in [pool.submit(process, i, t, arm, seed) for i, (t, arm, seed) in enumerate(plan, 1)]:
            f.result()


if __name__ == "__main__":
    main()
