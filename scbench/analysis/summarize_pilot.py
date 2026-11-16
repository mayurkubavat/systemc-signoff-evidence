"""Summarize a benchmark run directory (results/baseline-model-c) into summary.json and
summary.md: pass@1 and pass@3 per arm, a per-task table, turns, wall time,
API-equivalent cost, output tokens, tool calls, errors and rate limits, and
the first failing reason of each failed run.

    uv run python analysis/summarize_pilot.py results/baseline-model-c
"""
from __future__ import annotations

import json
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Tasks whose golden log depends on the gold implementation's random choices
# (see results/baseline-model-c/descriptions.md); reported, and excluded in the "valid" rows.
SUSPECT = {"uvm-systemc:uvm-sequence-library"}


def load(root: Path) -> list[dict]:
    recs = []
    for f in sorted(root.glob("*/record.json")):
        try:
            recs.append(json.loads(f.read_text()))
        except ValueError:
            pass
    return recs


def first_reason(rec: dict) -> str:
    if rec["status"] in ("error", "rate_limited"):
        return f"{rec['status']}: {rec.get('error', '')[:160]}"
    for t in rec.get("grade", {}).get("tests", []):
        if t.get("passed"):
            continue
        if "build" in t or t.get("stage"):
            b = t.get("build") or {}
            errs = b.get("errors") or b.get("first_errors") or []
            if errs:
                e = errs[0]
                if isinstance(e, dict):
                    return f"build: {Path(str(e.get('file', ''))).name}:{e.get('line')}: {e.get('message', '')[:140]}"
                return f"build: {str(e)[:160]}"
            return f"{t.get('stage') or 'build'}: {str(t.get('error') or b.get('log_tail') or b)[:160]}"
        diff = t.get("golden_diff") or []
        body = [l for l in diff if l[:1] in "+-" and not l.startswith(("---", "+++"))]
        if body:
            exp = next((l for l in body if l.startswith("-")), "")
            got = next((l for l in body if l.startswith("+")), "")
            return f"golden: expected {exp[1:][:70]!r}, got {got[1:][:70]!r}"
        if t.get("first_uvm_problem"):
            return f"uvm: {str(t['first_uvm_problem'])[:160]}"
        if t.get("log_tail"):
            tail = t["log_tail"] if isinstance(t["log_tail"], str) else "\n".join(t["log_tail"])
            return f"test: {tail.strip().splitlines()[-1][:160] if tail.strip() else 'failed'}"
        return "test failed"
    return "failed"


def tool_split(calls: dict) -> tuple[int, int, int]:
    scb = sum(v for k, v in calls.items() if k.startswith("mcp__scbench"))
    shell = calls.get("Bash", 0) + calls.get("run_command", 0)   # Model C / vendor CLI shell tool
    return scb, shell, sum(calls.values())


def stats(xs: list[float]) -> dict:
    return {"n": len(xs), "mean": round(st.mean(xs), 2) if xs else None,
            "median": round(st.median(xs), 2) if xs else None,
            "total": round(sum(xs), 2) if xs else 0}


def arm_summary(recs: list[dict], tasks: list[str], seeds: list[int]) -> dict:
    graded = [r for r in recs if r["status"] in ("pass", "fail")]
    per_seed = {}
    for s in seeds:
        g = [r for r in graded if r["seed"] == s and r["task"] in tasks]
        if g:
            per_seed[s] = {"graded": len(g), "pass": sum(r["status"] == "pass" for r in g),
                           "rate": round(sum(r["status"] == "pass" for r in g) / len(g), 3)}
    by_task = defaultdict(list)
    for r in graded:
        if r["task"] in tasks:
            by_task[r["task"]].append(r["status"] == "pass")
    full = [t for t, v in by_task.items() if len(v) >= len(seeds)]
    agents = [r["agent"] for r in graded if "agent" in r]
    scb = [tool_split(a.get("tool_calls", {})) for a in agents]
    return {
        "graded": len(graded),
        "pass": sum(r["status"] == "pass" for r in graded),
        "pass_at_1": round(st.mean(v["rate"] for v in per_seed.values()), 3) if per_seed else None,
        "pass_at_1_per_seed": per_seed,
        "pass_at_3": round(sum(any(by_task[t]) for t in full) / len(full), 3) if full else None,
        "pass_at_3_tasks": len(full),
        "any_pass_tasks": sum(any(v) for v in by_task.values()),
        "turns": stats([a["num_turns"] for a in agents if a.get("num_turns") is not None]),
        "wall_s": stats([a["wall_s"] for a in agents if a.get("wall_s") is not None]),
        "cost_usd": stats([a["total_cost_usd"] for a in agents if a.get("total_cost_usd") is not None]),
        "output_tokens": stats([(a.get("usage") or {}).get("output_tokens", 0) for a in agents]),
        "tool_calls": {"scbench": sum(x[0] for x in scb), "Bash": sum(x[1] for x in scb),
                       "total": sum(x[2] for x in scb),
                       "scbench_per_run": round(st.mean(x[0] for x in scb), 2) if scb else None,
                       "Bash_per_run": round(st.mean(x[1] for x in scb), 2) if scb else None},
        "web_search_calls": sum(a.get("tool_calls", {}).get("search_web", 0) for a in agents),
        "hit_max_turns": sum(a.get("terminal_reason") == "max_turns" for a in agents),
        "timed_out": sum(bool(a.get("timed_out")) for a in agents),
    }


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "results/baseline-model-c").resolve()
    cfg = json.loads((root / "config.json").read_text())
    recs = load(root)
    arms = cfg["arms"]
    seeds = list(range(cfg["seeds"]))
    all_tasks = sorted({r["task"] for r in recs})
    valid_tasks = [t for t in all_tasks if t not in SUSPECT]

    log = (root / "run.log").read_text(errors="replace") if (root / "run.log").exists() else ""
    limited_events = len(re.findall(r": RATE_LIMITED", log))
    error_events = len(re.findall(r": ERROR", log))
    probes = len(re.findall(r"\] probe: ", log))

    util = []
    for f in sorted(root.glob("*/agent.json"), key=lambda p: p.stat().st_mtime):
        rl = (json.loads(f.read_text()).get("rate_limit") or {}).get("unifiedWindows") or {}
        for w, v in rl.items():
            util.append((w, v.get("utilization")))

    summary = {
        "config": cfg,
        "runs_planned": cfg.get("runs_planned"),
        "records": len(recs),
        "status_counts": dict(Counter(r["status"] for r in recs)),
        "rate_limited_events_in_log": limited_events,
        "error_events_in_log": error_events,
        "limit_probes": probes,
        "usage_window_first_last": [util[0], util[-1]] if util else None,
        "suspect_tasks": sorted(SUSPECT),
        "arms": {a: arm_summary([r for r in recs if r["arm"] == a], all_tasks, seeds) for a in arms},
        "arms_valid": {a: arm_summary([r for r in recs if r["arm"] == a], valid_tasks, seeds)
                       for a in arms},
        "per_task": {t: {a: {"seeds": {r["seed"]: r["status"] for r in recs
                                       if r["task"] == t and r["arm"] == a}}
                         for a in arms} for t in all_tasks},
        "failures": [{"task": r["task"], "arm": r["arm"], "seed": r["seed"], "status": r["status"],
                      "reason": first_reason(r),
                      "turns": (r.get("agent") or {}).get("num_turns"),
                      "terminal_reason": (r.get("agent") or {}).get("terminal_reason")}
                     for r in sorted(recs, key=lambda r: (r["task"], r["arm"], r["seed"]))
                     if r["status"] != "pass"],
    }
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (root / "summary.md").write_text(render(summary, arms, seeds))
    print((root / "summary.md").read_text())


def fmt(x, pct=False):
    if x is None:
        return "-"
    return f"{100 * x:.1f}%" if pct else (f"{x:,.2f}" if isinstance(x, float) else f"{x:,}")


def render(s: dict, arms: list[str], seeds: list[int]) -> str:
    c = s["config"]
    L = ["# Pilot results", "",
         f"Model `{c['model']}`, vendor CLI, max turns {c['max_turns']}, "
         f"timeout {c['timeout_s']} s, {len(seeds)} seeds, arms {', '.join(arms)}, harness {c.get('harness_commit')}, "
         f"started {c.get('first_start')}. Runs recorded: {s['records']} of {s['runs_planned']} "
         f"({', '.join(f'{k} {v}' for k, v in sorted(s['status_counts'].items()))}). "
         f"Rate-limited attempts in the log: {s['rate_limited_events_in_log']}, error attempts: "
         f"{s['error_events_in_log']}, limit probes: {s['limit_probes']}.", ""]
    if s.get("usage_window_first_last"):
        (w0, u0), (w1, u1) = s["usage_window_first_last"]
        L += [f"Subscription usage window ({w0}): {fmt(u0, True)} at the first recorded run, "
              f"{fmt(u1, True)} at the last.", ""]
    for title, key in (("All 15 tasks", "arms"),
                       (f"Excluding {', '.join(t.split(':')[1] for t in s['suspect_tasks'])} "
                        "(golden log depends on the gold random generator)", "arms_valid")):
        L += [f"## {title}", "",
              "| Metric | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
        A = s[key]
        rows = [
            ("graded runs", lambda a: fmt(a["graded"])),
            ("passes", lambda a: fmt(a["pass"])),
            ("pass@1 (mean over seeds)", lambda a: fmt(a["pass_at_1"], True)),
            ("pass@1 per seed", lambda a: ", ".join(f"s{k}: {v['pass']}/{v['graded']}"
                                                     for k, v in a["pass_at_1_per_seed"].items())),
            ("pass@3 (tasks with 3 graded seeds)", lambda a: f"{fmt(a['pass_at_3'], True)} of {a['pass_at_3_tasks']}"),
            ("turns mean / median", lambda a: f"{fmt(a['turns']['mean'])} / {fmt(a['turns']['median'])}"),
            ("web searches (one vendor CLI only)", lambda a: fmt(a["web_search_calls"])),
            ("hit max turns / timed out", lambda a: f"{a['hit_max_turns']} / {a['timed_out']}"),
            ("agent wall time mean / median / total (min)",
             lambda a: " / ".join(fmt(round(x / 60, 1) if x is not None else None)
                                  for x in (a["wall_s"]["mean"], a["wall_s"]["median"], a["wall_s"]["total"]))),
            ("API-equivalent cost mean / total (USD)",
             lambda a: f"{fmt(a['cost_usd']['mean'])} / {fmt(a['cost_usd']['total'])}" if a['cost_usd']['n'] else "n/a"),
            ("output tokens mean / total",
             lambda a: f"{fmt(int(a['output_tokens']['mean'] or 0))} / {fmt(int(a['output_tokens']['total']))}"),
            ("tool calls per run: scbench / shell",
             lambda a: f"{fmt(a['tool_calls']['scbench_per_run'])} / {fmt(a['tool_calls']['Bash_per_run'])}"),
            ("tool calls total: scbench / shell / all",
             lambda a: f"{a['tool_calls']['scbench']} / {a['tool_calls']['Bash']} / {a['tool_calls']['total']}"),
        ]
        for name, f in rows:
            L.append(f"| {name} | " + " | ".join(f(A[a]) for a in arms) + " |")
        L.append("")
    L += ["## Per task", "", "P = pass, F = fail, E = error, R = rate limited, . = not run", "",
          "| Task | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    sym = {"pass": "P", "fail": "F", "error": "E", "rate_limited": "R"}
    for t, by_arm in s["per_task"].items():
        cells = []
        for a in arms:
            sd = by_arm[a]["seeds"]
            cells.append(" ".join(sym.get(sd.get(k) or sd.get(str(k)), ".") for k in seeds))
        L.append(f"| {t.split(':')[1]} | " + " | ".join(cells) + " |")
    L += ["", "## Failures (first failing reason)", ""]
    for f in s["failures"]:
        extra = f" [{f['terminal_reason']}, {f['turns']} turns]" if f.get("terminal_reason") else ""
        L.append(f"- {f['task'].split(':')[1]} / {f['arm']} / s{f['seed']}: {f['reason']}{extra}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
