"""Measure the proof bar behind the fix/* and feature/* branches of the
oss-workbench forks (read-only: git plumbing only, no checkout).

    uv run --with lizard python analysis/proofbar.py \
        --workbench ~/Silicon/active/oss-workbench --out runs/proofbar

Inputs besides git: analysis/audit_findings.json (hand-coded from the
.audit review reports) and <out>/suite_cost.json (timings, measured
separately). Writes <out>/proofbar.json and <out>/proofbar.md.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics as st
import subprocess
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

import lizard

PROJECTS = ["uvm-systemc", "systemc", "crave", "fc4sc"]
CXX = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".ipp", ".tpp"}
BUILD_NAMES = {"CMakeLists.txt", "Makefile.am", "configure.ac", "configure.in"}
BUILD_EXT = {".cmake", ".am", ".in", ".vcxproj", ".filters", ".sln", ".ac", ".pc"}
TEST_CASE = re.compile(r"^\+\s*(TEST|TEST_F|TEST_P|BOOST_AUTO_TEST_CASE|BOOST_FIXTURE_TEST_CASE)\s*\(")
HERE = Path(__file__).resolve().parent


def git(repo: Path, *args: str, check: bool = True) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, check=check, errors="replace").stdout


def category(path: str) -> str:
    p = PurePosixPath(path)
    parts = set(p.parts[:-1])
    if parts & {"tests", "test"}:
        return "test"
    if "examples" in parts:
        return "example"
    if p.name in BUILD_NAMES or p.suffix in BUILD_EXT or parts & {"msvc16", "msvc10", "cmake"}:
        return "build"
    if p.suffix in CXX:
        return "source"
    if p.suffix in {".md", ".txt", ".rst"} or p.name in {"RELEASENOTES", "NEWS", "ChangeLog", "AUTHORS"}:
        return "doc"
    return "other"


def is_golden(path: str) -> bool:
    return "/golden/" in path or "_gold." in path or path.endswith(".golden")


def comment_or_code(line: str) -> str | None:
    s = line.strip()
    if not s:
        return None
    if s.startswith(("//", "/*", "*", "*/")):
        return "comment"
    return "code"


def func_stats(funcs: list) -> dict:
    if not funcs:
        return {"functions": 0, "mean_ccn": 0.0, "max_ccn": 0, "mean_nloc": 0.0, "ccn_gt15": 0}
    ccn = [f.cyclomatic_complexity for f in funcs]
    return {"functions": len(funcs), "mean_ccn": round(st.mean(ccn), 3), "max_ccn": max(ccn),
            "mean_nloc": round(st.mean(f.nloc for f in funcs), 2),
            "ccn_gt15": sum(c > 15 for c in ccn)}


def lizard_funcs(repo: Path, rev: str, paths: list[str]) -> list:
    out = []
    for p in paths:
        r = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{p}"], capture_output=True,
                           text=True, errors="replace")
        if r.returncode != 0:
            continue                      # file does not exist at this revision
        out += lizard.analyze_file.analyze_source_code(p, r.stdout).function_list
    return out


def complexity(repo: Path, base: str, tip: str, paths: list[str]) -> dict:
    b, t = func_stats(lizard_funcs(repo, base, paths)), func_stats(lizard_funcs(repo, tip, paths))
    d = {k: round(t[k] - b[k], 3) for k in b}
    return {"files": len(paths), "base": b, "tip": t, "delta": d}


def branch_metrics(repo: Path, branch: str) -> dict:
    base = git(repo, "merge-base", "main", branch).strip()
    tip = git(repo, "rev-parse", branch).strip()
    commits = int(git(repo, "rev-list", "--count", f"{base}..{tip}").strip())
    status = {}
    for line in git(repo, "diff", "--name-status", "--no-renames", base, tip).splitlines():
        st_, path = line.split("\t", 1)
        status[path] = st_[0]
    added = Counter()
    files_by_cat = defaultdict(list)
    for line in git(repo, "diff", "--numstat", "--no-renames", base, tip).splitlines():
        a, d, path = line.split("\t", 2)
        cat = category(path)
        files_by_cat[cat].append(path)
        if a == "-":
            continue
        key = cat
        if cat == "test":
            key = "test_golden" if is_golden(path) else (
                "test_code" if PurePosixPath(path).suffix in CXX else "test_other")
        added[key] += int(a)
    test_files = files_by_cat.get("test", [])
    new_test_files = [p for p in test_files if status.get(p) == "A"
                      and PurePosixPath(p).suffix in CXX]
    new_golden_dirs = set()
    for p in test_files:
        if status.get(p) == "A" and "/golden/" in p:
            d = p.split("/golden/")[0]
            if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{base}:{d}/golden"],
                              capture_output=True).returncode != 0:
                new_golden_dirs.add(d)
    new_cases = 0
    if test_files:
        diff = git(repo, "diff", "-U0", "--no-renames", base, tip, "--", *test_files)
        new_cases = sum(1 for l in diff.splitlines() if TEST_CASE.match(l))
    src = files_by_cat.get("source", [])
    cmt = Counter()
    if src:
        for l in git(repo, "diff", "-U0", "--no-renames", base, tip, "--", *src).splitlines():
            if l.startswith("+") and not l.startswith("+++"):
                k = comment_or_code(l[1:])
                if k:
                    cmt[k] += 1
    cxx_all = [p for cat, ps in files_by_cat.items() for p in ps if PurePosixPath(p).suffix in CXX]
    adds_test = bool(new_golden_dirs or new_test_files or new_cases)
    fork = git(repo, "rev-parse", "-q", "--verify", f"refs/remotes/fork/{branch}", check=False).strip()
    return {
        "branch": branch, "base": base[:12], "tip": tip[:12], "commits": commits,
        "fork_tip": fork[:12] or None, "fork_equals_local": fork == tip,
        "files_changed": {k: len(v) for k, v in files_by_cat.items()},
        "loc_added": dict(added),
        "test_loc_added": added["test_code"] + added["test_golden"] + added["test_other"],
        "test_code_loc_added": added["test_code"],
        "source_loc_added": added["source"],
        "new_test_dirs_with_golden": sorted(new_golden_dirs),
        "new_test_files": new_test_files,
        "new_test_cases": new_cases,
        "adds_test": adds_test,
        "touches_test": bool(test_files),
        "source_lines_added": {"comment": cmt["comment"], "code": cmt["code"]},
        "complexity_source": complexity(repo, base, tip, src),
        "complexity_all_cxx": complexity(repo, base, tip, cxx_all),
    }


def med(xs):
    xs = list(xs)
    return round(st.median(xs), 3) if xs else None


def fork_has_fix(repo: Path, b: dict, after: str | None) -> bool | None:
    if not b["fork_tip"]:
        return None
    if after:
        return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", after,
                               f"refs/remotes/fork/{b['branch']}"]).returncode == 0
    return b["fork_equals_local"]


FINDING_BRANCH = {"sequencer": "fix/sequencer-killed-requests", "pool": "feature/uvm-pool",
                  "barrier": "feature/uvm-barrier", "heartbeat": "feature/uvm-heartbeat",
                  "seqlib": "feature/uvm-sequence-library"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbench", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    wb, out = Path(a.workbench).expanduser(), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    audit = json.loads((HERE / "audit_findings.json").read_text())
    cost_path = out / "suite_cost.json"
    cost = json.loads(cost_path.read_text()) if cost_path.exists() else None

    branches: dict[str, list[dict]] = {}
    for p in PROJECTS:
        repo = wb / p / "src"
        names = git(repo, "for-each-ref", "--format=%(refname:short)",
                    "refs/heads/fix", "refs/heads/feature").split()
        branches[p] = [branch_metrics(repo, n) for n in names]
        print(f"{p}: {len(names)} branches", flush=True)

    # -- 2. fail-then-pass evidence, joined to branches via audit topics ---------
    by_branch = defaultdict(list)
    for t in audit["topics"]:
        for b in t["branches"]:
            by_branch[(t["project"], b)].append(t)
    for p, bs in branches.items():
        for b in bs:
            ts = by_branch.get((p, b["branch"]), [])
            ftp = [t["fail_then_pass"] for t in ts]
            b["audit"] = {
                "topics": [t["topic"] for t in ts],
                "reviewed": bool(ts),
                "fail_then_pass": "yes" if "yes" in ftp else ("repro-only" if "repro-only" in ftp else ("no" if ts else None)),
                "baseline": any(t["baseline"] for t in ts) if ts else None,
                "rounds": max((t["rounds"] for t in ts), default=None),
            }

    # -- 5. findings, with whether the fork branch carries the fix -----------
    topic_of = {(t["project"], t["topic"]): t for t in audit["topics"]}
    bmap = {(p, b["branch"]): b for p, bs in branches.items() for b in bs}
    findings = []
    for f in audit["findings"]:
        t = topic_of[(f["project"], f["topic"])]
        pre = f["id"].split("-")[0]
        brs = ([f["branch"]] if "branch" in f else
               [FINDING_BRANCH[pre]] if pre in FINDING_BRANCH else t["branches"])
        states = [fork_has_fix(wb / f["project"] / "src", bmap[(f["project"], br)],
                               (t.get("after") or {}).get(br)) for br in brs if (f["project"], br) in bmap]
        if f["fixed"] not in ("fixed", "partly"):
            pushed = "n/a (not a code fix)"
        elif all(s is None for s in states):
            pushed = "not pushed"
        elif all(s for s in states if s is not None):
            pushed = "fork has fix"
        else:
            pushed = "fork behind fix"
        findings.append({**f, "branches": brs, "fork": pushed})

    # -- aggregates --------------------------------------------------------
    summary = {}
    for p, bs in branches.items():
        # Deltas are only meaningful where the base had functions in the
        # changed files; branches that only add new files are reported apart.
        allcs = [b["complexity_source"] for b in bs if b["complexity_source"]["files"]]
        cs = [c for c in allcs if c["base"]["functions"]]
        newonly = [c for c in allcs if not c["base"]["functions"] and c["tip"]["functions"]]
        dm = [c["delta"]["mean_ccn"] for c in cs]
        summary[p] = {
            "branches": len(bs),
            "commits_total": sum(b["commits"] for b in bs), "commits_median": med(b["commits"] for b in bs),
            "test_loc_total": sum(b["test_loc_added"] for b in bs),
            "test_code_loc_total": sum(b["test_code_loc_added"] for b in bs),
            "source_loc_total": sum(b["source_loc_added"] for b in bs),
            "test_loc_median": med(b["test_loc_added"] for b in bs),
            "source_loc_median": med(b["source_loc_added"] for b in bs),
            "test_to_source_ratio_median": med(b["test_loc_added"] / b["source_loc_added"]
                                               for b in bs if b["source_loc_added"]),
            "new_test_dirs_total": sum(len(b["new_test_dirs_with_golden"]) for b in bs),
            "new_test_files_total": sum(len(b["new_test_files"]) for b in bs),
            "new_test_cases_total": sum(b["new_test_cases"] for b in bs),
            "branches_adding_test": sum(b["adds_test"] for b in bs),
            "branches_touching_test": sum(b["touches_test"] for b in bs),
            "branches_no_test": [b["branch"] for b in bs if not b["adds_test"]],
            "branches_no_test_but_touch_test": [b["branch"] for b in bs
                                                if not b["adds_test"] and b["touches_test"]],
            "reviewed": sum(b["audit"]["reviewed"] for b in bs),
            "fail_then_pass": sum(b["audit"]["fail_then_pass"] == "yes" for b in bs),
            "fail_then_pass_repro_only": sum(b["audit"]["fail_then_pass"] == "repro-only" for b in bs),
            "baseline_compare": sum(bool(b["audit"]["baseline"]) for b in bs),
            "complexity": {
                "branches_with_source_changes": len(allcs),
                "branches_modifying_existing_functions": len(cs),
                "branches_new_files_only": len(newonly),
                "new_files_only_tip_mean_ccn_median": med(c["tip"]["mean_ccn"] for c in newonly),
                "new_files_only_functions": sum(c["tip"]["functions"] for c in newonly),
                "mean_ccn_delta_median": med(dm),
                "mean_ccn_delta_mean": round(st.mean(dm), 3) if dm else None,
                "lowered": sum(d < -0.005 for d in dm), "raised": sum(d > 0.005 for d in dm),
                "unchanged": sum(abs(d) <= 0.005 for d in dm),
                "functions_added": sum(c["delta"]["functions"] for c in cs),
                "ccn_gt15_delta": sum(c["delta"]["ccn_gt15"] for c in cs),
                "max_ccn_raised": sum(c["delta"]["max_ccn"] > 0 for c in cs),
                "mean_nloc_delta_median": med(c["delta"]["mean_nloc"] for c in cs),
            },
            "source_comment_lines_added": sum(b["source_lines_added"]["comment"] for b in bs),
            "source_code_lines_added": sum(b["source_lines_added"]["code"] for b in bs),
        }
    allb = [(p, b) for p, bs in branches.items() for b in bs]
    top = sorted((x for x in allb if x[1]["complexity_source"]["base"]["functions"]),
                 key=lambda x: -x[1]["complexity_source"]["delta"]["mean_ccn"])[:5]
    topics = audit["topics"]
    fsum = Counter(f["class"] for f in findings)
    result = {
        "generated": "analysis/proofbar.py", "branch_count": len(allb),
        "summary": summary,
        "totals": {
            "branches": len(allb),
            "branches_no_test": sum(not b["adds_test"] for _, b in allb),
            "branches_no_test_but_touch_test": sum(not b["adds_test"] and b["touches_test"] for _, b in allb),
            "reviewed_branches": sum(b["audit"]["reviewed"] for _, b in allb),
            "fail_then_pass_branches": sum(b["audit"]["fail_then_pass"] == "yes" for _, b in allb),
            "baseline_branches": sum(bool(b["audit"]["baseline"]) for _, b in allb),
            "topics": len(topics),
            "topics_fail_then_pass": sum(t["fail_then_pass"] == "yes" for t in topics),
            "topics_baseline": sum(t["baseline"] for t in topics),
            "topics_both": sum(t["fail_then_pass"] == "yes" and t["baseline"] for t in topics),
            "review_rounds": dict(Counter(t["rounds"] for t in topics)),
        },
        "top5_mean_ccn_increase": [
            {"project": p, "branch": b["branch"], **b["complexity_source"]["delta"],
             "base_mean_ccn": b["complexity_source"]["base"]["mean_ccn"],
             "tip_mean_ccn": b["complexity_source"]["tip"]["mean_ccn"]} for p, b in top],
        "findings": findings,
        "findings_by_class": dict(fsum.most_common()),
        "findings_by_severity": dict(Counter(f["sev"] for f in findings)),
        "findings_by_fix": dict(Counter(f["fixed"] for f in findings)),
        "findings_by_fork": dict(Counter(f["fork"] for f in findings)),
        "suite_cost": cost,
        "branches": branches,
    }
    (out / "proofbar.json").write_text(json.dumps(result, indent=2))
    (out / "proofbar.md").write_text(render_md(result))
    print(json.dumps(result["totals"], indent=2))


def render_md(r: dict) -> str:
    S, T = r["summary"], r["totals"]
    L = ["# Proof bar of the oss-workbench change branches", "",
         f"{T['branches']} fix/feature branches across UVM-SystemC, SystemC, CRAVE and FC4SC "
         "(base = merge-base with main). Generated by `analysis/proofbar.py`; data in `proofbar.json`.", "",
         "## 1. Test-first evidence", "",
         "| Library | Branches | Commits (median) | Test LOC added (total / median) | Source LOC added (total / median) | Test:source LOC (median) | New golden test dirs | New test files | New test cases (gtest/boost) | Branches adding a test | Touching a test |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for p, s in S.items():
        L.append(f"| {p} | {s['branches']} | {s['commits_total']} ({s['commits_median']}) | "
                 f"{s['test_loc_total']} / {s['test_loc_median']} | {s['source_loc_total']} / {s['source_loc_median']} | "
                 f"{s['test_to_source_ratio_median']} | {s['new_test_dirs_total']} | {s['new_test_files_total']} | "
                 f"{s['new_test_cases_total']} | {s['branches_adding_test']} | {s['branches_touching_test']} |")
    L += ["", f"Branches that add no test: {T['branches_no_test']} of {T['branches']} "
          f"({T['branches_no_test_but_touch_test']} of them change an existing test or its golden log, "
          "marked *).", ""]
    for p, s in S.items():
        if s["branches_no_test"]:
            star = set(s["branches_no_test_but_touch_test"])
            L.append(f"- {p}: " + ", ".join(b + ("*" if b in star else "") for b in s["branches_no_test"]))
    L += ["", "Test LOC includes golden logs; source LOC is library C/C++ outside tests, examples and build "
          "files. Stacked branches (e.g. uvm-barrier on uvm-pool, fc4sc-coverage and fc4sc-coverage-rebased) "
          "share commits, so library totals count shared work more than once; medians are less affected.", "",
          "## 2. Fail-then-pass evidence (from .audit review reports)", "",
          f"{T['topics']} review topics cover {T['reviewed_branches']} of {T['branches']} branches. "
          f"Topics recording fail-at-base/pass-at-fix: {T['topics_fail_then_pass']}; with a baseline regression comparison: "
          f"{T['topics_baseline']}; both: {T['topics_both']}. Review rounds per topic: "
          + ", ".join(f"{k} round(s): {v}" for k, v in sorted(T["review_rounds"].items())) + ".", "",
          "| Library | Branches | Reviewed | Fail-then-pass | Repro only | Baseline comparison |",
          "| --- | --- | --- | --- | --- | --- |"]
    for p, s in S.items():
        L.append(f"| {p} | {s['branches']} | {s['reviewed']} | {s['fail_then_pass']} | {s['fail_then_pass_repro_only']} | {s['baseline_compare']} |")
    L += ["", "## 3. Cost of the existing suites", ""]
    c = r.get("suite_cost")
    if c and c.get("measured"):
        m = c["measured"]
        L += [f"Measured by `analysis/suite_cost.py` on this Mac ({c['host']['cpus']} CPUs), each library "
              "built in a clean temporary worktree (no existing build dir reused); commit per row.", "",
              "| Library | Commit | Configure (s) | Build incl. tests (s) | Tests | Full ctest wall, parallel (s) | Full ctest wall, serial (s) |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
        def row(name, conf, build, cts, commit=""):
            par = [x for x in cts if x["jobs"] > 1]; ser = [x for x in cts if x["jobs"] == 1]
            tests = sum(x["tests"] or 0 for x in par or cts)
            L.append(f"| {name} | {commit} | {conf if conf is not None else 'n/t'} | {build} | {tests} | "
                     f"{round(sum(x['wall_s'] for x in par), 1) if par else '-'} | "
                     f"{round(sum(x['wall_s'] for x in ser), 1) if ser else '-'} |")
        for name, v in m.items():
            if "error" in v:
                L.append(f"| {name} | not measured: {v['error'].splitlines()[0][:120]} | | | | |"); continue
            if name == "uvm-systemc":
                row(name, v["configure_s"], round(v["build_library_s"] + v["build_tests_s"], 1), v["full_ctest"], v.get("commit", ""))
            elif name == "systemc":
                row(name, v["configure_s"], v["build_s"], list(v["full_ctest"].values()), v.get("commit", ""))
            elif name == "crave":
                row(name, v["configure_s"], v["build_s_incl_z3_cudd"], [v["full_ctest"]], v.get("commit", ""))
            else:
                row(name, v["configure_s"], v["build_s"], [v["full_ctest"]], v.get("commit", ""))
        u = m.get("uvm-systemc", {})
        if "single_test" in u:
            st_ = u["single_test"]
            L += ["", f"UVM-SystemC clean configure+build (library and all tests): {u['clean_configure_build_s']} s. "
                  f"Single-test loop on `{st_['test']}`: after touching the test source, rebuild "
                  f"{st_['touch_test_source']['build_s']} s + run {st_['touch_test_source']['run_s']} s; after touching "
                  f"one library source (`{st_['touch_library_source']['file']}`), rebuild "
                  f"{st_['touch_library_source']['build_s']} s + run {st_['touch_library_source']['run_s']} s."]
        L += ["", "n/t = not timed."] + [f"- {x}" for x in c.get("notes", [])]
    else:
        L.append("Not measured yet (suite_cost.json missing).")
    L += ["", "## 4. Readability and complexity (lizard, changed library source files, base vs tip)", "",
          "Deltas cover branches that change files with existing functions; branches whose library source is only new files are counted apart (their base has no functions).", "",
          "| Library | Branches changing existing functions | Mean CCN delta (median / mean) | Lowered / raised / unchanged | Functions added | Functions CCN>15 delta | Max CCN raised | Mean NLOC/function delta (median) | New-files-only branches (functions, median mean CCN) | Comment : code lines added (all source) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for p, s in S.items():
        x = s["complexity"]
        L.append(f"| {p} | {x['branches_modifying_existing_functions']} | {x['mean_ccn_delta_median']} / {x['mean_ccn_delta_mean']} | "
                 f"{x['lowered']} / {x['raised']} / {x['unchanged']} | {x['functions_added']} | {x['ccn_gt15_delta']} | "
                 f"{x['max_ccn_raised']} | {x['mean_nloc_delta_median']} | {x['branches_new_files_only']} "
                 f"({x['new_files_only_functions']}, {x['new_files_only_tip_mean_ccn_median']}) | "
                 f"{s['source_comment_lines_added']} : {s['source_code_lines_added']} |")
    L += ["", "Comment lines include license headers of new files.", "",
          "Largest mean-CCN increases (branches changing existing functions):", "", "| Branch | Mean CCN base -> tip | Max CCN delta | Functions added | CCN>15 delta |", "| --- | --- | --- | --- | --- |"]
    for t in r["top5_mean_ccn_increase"]:
        L.append(f"| {t['project']} {t['branch']} | {t['base_mean_ccn']} -> {t['tip_mean_ccn']} | {t['max_ccn']} | {t['functions']} | {t['ccn_gt15']} |")
    L += ["", "## 5. Review defects (high and medium findings)", "",
          "| Library / topic | Id | Sev | Class | Fixed | Fork | Finding |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for f in r["findings"]:
        L.append(f"| {f['project']} {f['topic']} | {f['id']} | {f['sev']} | {f['class']} | {f['fixed']} | {f['fork']} | {f['text']} |")
    L += ["", "By class: " + ", ".join(f"{k} {v}" for k, v in r["findings_by_class"].items()) + ".",
          "By fix: " + ", ".join(f"{k} {v}" for k, v in r["findings_by_fix"].items()) + ".",
          "Fork state: " + ", ".join(f"{k} {v}" for k, v in r["findings_by_fork"].items()) + ".", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
