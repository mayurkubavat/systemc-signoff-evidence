"""Mine benchmark tasks from fix/* and feature/* branches.

A task is: the commit the change started from (base), the finished change
(gold), the regression test the change added (hidden from the agent until
grading), and a problem description taken from the commit message.

    python -m scbench.mine --workbench ~/Silicon/active/oss-workbench \
        --list tasks/pilot-branches.txt --out tasks/pilot.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from .tools import profiles


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


_HOW = re.compile(r"^(Build|Make|Use|Add|Keep|Return|Call|Move|Replace|Guard|Check|Store|Fix|"
                  r"Implement|Set|Remove|Look|Let|Teach|Track|Give|Pass|Compare|Treat|Report|"
                  r"Drop|Clear|Copy|Defer|Hold|Skip|Read|Write|Register|Mark|Erase|Delete|Sort|"
                  r"Iterate|Derive|Port|Provide|Expose|Wire|Route|Reject|Accept|Validate)\b")


def describe(message: str) -> str:
    """Subject plus the problem part of the first body paragraph, as the
    author explained it. Sentences that say how it was fixed (they start
    with an imperative verb) and trailers are dropped."""
    lines = [l for l in message.splitlines() if not l.startswith(("Signed-off-by", "Co-Authored-By"))]
    subject = lines[0] if lines else ""
    body = "\n".join(lines[1:]).strip().split("\n\n")
    first = body[0].replace("\n", " ").strip() if body and body[0] else ""
    kept = []
    for sent in re.split(r"(?<=[.!?])\s+", first):
        if _HOW.match(sent):
            break
        kept.append(sent)
    return f"{subject}\n\n{' '.join(kept)}".strip()


def mine_one(workbench: Path, project: str, branch: str, stop_at: set[str] = frozenset()) -> dict:
    """stop_at: gold commits of other tasks. A branch stacked on another
    task's branch starts after that branch's tip, so the two never overlap."""
    repo = workbench / project / "src"
    prof = profiles()[project]
    main = git(repo, "rev-parse", "main")
    base = git(repo, "merge-base", main, branch)
    gold = git(repo, "rev-parse", branch)
    for c in git(repo, "rev-list", "--reverse", f"{base}..{gold}").splitlines():
        if c in stop_at and c != gold:
            base = c
    added = git(repo, "diff", "--name-only", "--diff-filter=A", base, gold).splitlines()
    changed = git(repo, "diff", "--name-only", base, gold).splitlines()
    root = prof.test_root.rstrip("/") + "/"
    hidden = [f for f in added if f.startswith(root)]
    tests = sorted({str(Path(f).parent.relative_to(prof.test_root)).removesuffix("/golden")
                    for f in hidden if f.endswith((".cpp", ".log"))})
    tests = sorted({t[:-len("/golden")] if t.endswith("/golden") else t for t in tests})
    first_msg = git(repo, "log", "--reverse", "--format=%B%x00", f"{base}..{gold}").split("\x00")[0]
    return {
        "id": f"{project}:{branch.split('/', 1)[-1]}",
        "project": project, "branch": branch, "base": base, "gold": gold,
        "commits": int(git(repo, "rev-list", "--count", f"{base}..{gold}")),
        "hidden_files": hidden, "tests": tests,
        "gold_source_files": [f for f in changed if not f.startswith(root)],
        "description": describe(first_msg),
        "description_reviewed": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbench", required=True)
    ap.add_argument("--list", required=True, help="lines of '<project> <branch>'")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    wb = Path(a.workbench).expanduser()
    pairs = []
    for line in Path(a.list).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            pairs.append(tuple(line.split()))
    golds = {git(wb / p / "src", "rev-parse", b) for p, b in pairs}
    tasks = []
    for project, branch in pairs:
        t = mine_one(wb, project, branch, golds)
        if not t["tests"]:
            print(f"skip {t['id']}: no added regression test")
            continue
        tasks.append(t)
        print(f"ok   {t['id']}: tests={t['tests']} commits={t['commits']}")
    Path(a.out).write_text(json.dumps(tasks, indent=2) + "\n")
    print(f"{len(tasks)} tasks -> {a.out}")


if __name__ == "__main__":
    main()
