"""Read-only recount of the proof-bar numbers for the engrXiv paper, on the
branches that were pushed to the forks (refs/remotes/fork/{fix,feature}/*).

Items follow the "Recount task list" in the paper's review-response.md:
 a) branch counts and the local-only duplicate,
 b) adds-test with rename detection, stubs excluded, own diff (vs parent) and diff vs main,
 c) distinct new UVM-SystemC golden-log test folders (union over branches; development vs main),
 d) UVM-SystemC per-branch test/source ratio (C++ only; with golden logs),
 e) CCN on branches that modify existing library source,
 f) review-report facts (sanitizer build, no-new-warnings check, reviewed branches, parity-batch-2),
 g) review topics with a second round.

    uv run --with lizard python analysis/recount.py     # writes runs/proofbar/recount.{json,md}
"""
from __future__ import annotations

import json
import os
import re
import statistics as st
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import proofbar as pb  # noqa: E402  (category, is_golden, CXX, TEST_CASE, complexity)

WB = Path(os.environ.get("PBP_WORKBENCH", Path.home() / "Silicon" / "active" / "oss-workbench"))
PROJECTS = ["uvm-systemc", "crave", "fc4sc", "systemc"]
OUT = HERE.parent / "runs" / "proofbar"
STUB = re.compile(r"(^|/)[^/]*stub[^/]*$", re.I)


def git(repo: Path, *args: str, check: bool = False) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          errors="replace", check=check).stdout


def is_ancestor(repo: Path, a: str, b: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", a, b],
                          capture_output=True).returncode == 0


def fork_branches(repo: Path) -> dict[str, str]:
    out = {}
    for line in git(repo, "for-each-ref", "--format=%(refname)%09%(objectname)",
                    "refs/remotes/fork/fix", "refs/remotes/fork/feature").splitlines():
        ref, sha = line.split("\t")
        out[ref.removeprefix("refs/remotes/fork/")] = sha
    return out


def parent_of(repo: Path, name: str, sha: str, others: dict[str, str], main: str) -> str | None:
    """The nearest other fork branch whose tip is a proper ancestor of this tip
    and not already in main: the branch this one is stacked on."""
    best, best_n = None, -1
    for o, osha in others.items():
        if o == name or osha == sha or is_ancestor(repo, osha, main):
            continue
        if is_ancestor(repo, osha, sha):
            n = int(git(repo, "rev-list", "--count", f"{main}..{osha}").strip() or 0)
            if n > best_n:
                best, best_n = o, n
    return best


def diff_facts(repo: Path, base: str, tip: str) -> dict:
    """Test and source facts of base..tip with rename detection."""
    status = {}
    for line in git(repo, "diff", "--name-status", "-M", base, tip).splitlines():
        parts = line.split("\t")
        st_ = parts[0][0]
        path = parts[-1]
        status[path] = st_
    added = Counter()
    files = {}
    for line in git(repo, "diff", "--numstat", "-M", base, tip).splitlines():
        a, d, path = line.split("\t", 2)
        if "=>" in path:      # renamed: numstat shows old => new
            path = re.sub(r"\{[^{}]*=> ([^{}]*)\}", r"\1", path).replace("//", "/")
            path = path.split(" => ")[-1]
        cat = pb.category(path)
        files[path] = cat
        if a == "-":
            continue
        key = cat
        if cat == "test":
            key = "test_golden" if pb.is_golden(path) else (
                "test_code" if PurePosixPath(path).suffix in pb.CXX else "test_other")
        added[key] += int(a)
    tests = [p for p, c in files.items() if c == "test"]
    new_test_files = [p for p in tests if status.get(p) == "A" and PurePosixPath(p).suffix in pb.CXX
                      and not STUB.search(p)]
    new_golden = set()
    for p in tests:
        if status.get(p) == "A" and "/golden/" in p:
            d = p.split("/golden/")[0]
            if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{base}:{d}/golden"],
                              capture_output=True).returncode != 0:
                new_golden.add(d)
    cases = 0
    code_tests = [p for p in tests if not STUB.search(p)]
    if code_tests:
        cases = sum(1 for l in git(repo, "diff", "-U0", "-M", base, tip, "--", *code_tests).splitlines()
                    if pb.TEST_CASE.match(l))
    src = [p for p, c in files.items() if c == "source"]
    return {"new_test_files": new_test_files, "new_golden_dirs": sorted(new_golden), "new_test_cases": cases,
            "adds_test": bool(new_test_files or new_golden or cases),
            "test_code_loc": added["test_code"], "test_golden_loc": added["test_golden"],
            "source_loc": added["source"], "source_files": src,
            "stubs_touched": [p for p in tests if STUB.search(p)]}


def ccn(repo: Path, base: str, tip: str, src: list[str]) -> dict | None:
    if not src:
        return None
    c = pb.complexity(repo, base, tip, src)
    if not c["base"]["functions"]:
        return None          # only new files: no existing library source modified
    return {"before": c["base"]["mean_ccn"], "after": c["tip"]["mean_ccn"], "delta": c["delta"]["mean_ccn"]}


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 3) if xs else None


def ccn_summary(rows: list[dict]) -> dict:
    ds = [r["delta"] for r in rows]
    top = max(rows, key=lambda r: r["delta"]) if rows else None
    return {"branches": len(rows), "lowered": sum(d < 0 for d in ds), "raised": sum(d > 0 for d in ds),
            "unchanged": sum(d == 0 for d in ds), "median_delta": med(ds),
            "largest_increase": top}


def audit_facts(fork_set: set[tuple[str, str]]) -> dict:
    audit = json.loads((HERE / "audit_findings.json").read_text())
    topics = {}
    for p in PROJECTS:
        for d in sorted((WB / p / ".audit").glob("*/")):
            files = sorted(d.glob("review*.md"))
            if not files:
                continue
            text = "\n".join(f.read_text(errors="replace") for f in files)
            topics[f"{p}:{d.name}"] = {
                "sanitizer": bool(re.search(r"ASan|UBSan|sanitiz|-fsanitize", text, re.I)),
                "no_new_warnings": bool(re.search(r"no (new )?warnings|warnings unchanged|\b0 (new )?warnings",
                                                  text, re.I)),
            }
    reviewed = set()
    for t in audit["topics"]:
        for b in t["branches"]:
            if (t["project"], b) in fork_set:
                reviewed.add((t["project"], b))
    coded = {f"{t['project']}:{t['topic']}" for t in audit["topics"]}
    topics = {k: v for k, v in topics.items() if k in coded}   # the 30 hand-coded topics
    pb2 = topics.get("uvm-systemc:parity-batch-2", {})
    return {"topics_with_report": len(topics),
            "topics_sanitizer": sum(v["sanitizer"] for v in topics.values()),
            "topics_no_new_warnings": sum(v["no_new_warnings"] for v in topics.values()),
            "sanitizer_topics": sorted(k for k, v in topics.items() if v["sanitizer"]),
            "warnings_topics": sorted(k for k, v in topics.items() if v["no_new_warnings"]),
            "fork_branches_with_review": len(reviewed),
            "fork_branches_without_review": len(fork_set) - len(reviewed),
            "parity_batch_2_sanitizer": pb2.get("sanitizer"),
            "topics_second_round": sum((t.get("rounds") or 1) >= 2 for t in audit["topics"]),
            "audit_topics": len(audit["topics"])}



def main() -> None:
    res = {"branches": {}, "manifest": {}}
    all_rows = []
    for p in PROJECTS:
        repo = WB / p / "src"
        main_ref = "main" if git(repo, "rev-parse", "-q", "--verify", "main").strip() else "master"
        fb = fork_branches(repo)
        local = git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads/fix", "refs/heads/feature").split()
        res["branches"][p] = {"fork": len(fb), "local": len(local),
                              "local_only": sorted(set(local) - set(fb))}
        for name, sha in sorted(fb.items()):
            base_main = git(repo, "merge-base", main_ref, sha).strip()
            parent = parent_of(repo, name, sha, fb, main_ref)
            base_own = fb[parent] if parent else base_main
            vs_main = diff_facts(repo, base_main, sha)
            own = diff_facts(repo, base_own, sha) if parent else vs_main
            row = {"project": p, "branch": name, "sha": sha, "parent": parent,
                   "adds_test_vs_main": vs_main["adds_test"], "adds_test_own": own["adds_test"],
                   "new_golden_dirs_vs_main": vs_main["new_golden_dirs"],
                   "new_golden_dirs_own": own["new_golden_dirs"],
                   "stubs_touched": vs_main["stubs_touched"],
                   "own": {k: own[k] for k in ("test_code_loc", "test_golden_loc", "source_loc")},
                   "vs_main": {k: vs_main[k] for k in ("test_code_loc", "test_golden_loc", "source_loc")},
                   "ccn_own": ccn(repo, base_own, sha, own["source_files"]),
                   "ccn_vs_main": ccn(repo, base_main, sha, vs_main["source_files"])}
            all_rows.append(row)
            res["manifest"][f"{p}:{name}"] = sha
        print(f"{p}: {len(fb)} fork branches", flush=True)

    # local-only duplicate check
    dup = {}
    fc = WB / "uvm-systemc" / "src"     # the duplicate is a local branch of the UVM-SystemC fork
    if git(fc, "rev-parse", "-q", "--verify", "refs/heads/feature/fc4sc-coverage-rebased").strip():
        tip = git(fc, "rev-parse", "refs/heads/feature/fc4sc-coverage-rebased").strip()
        same_tree = [n for n, s in fork_branches(fc).items()
                     if git(fc, "rev-parse", f"{s}^{{tree}}").strip() == git(fc, "rev-parse", f"{tip}^{{tree}}").strip()]
        patch_eq = [n for n, s in fork_branches(fc).items()
                    if not git(fc, "diff", "--stat", s, tip).strip()]
        dup = {"exists_locally": True, "on_fork": bool(git(fc, "rev-parse", "-q", "--verify",
                                                           "refs/remotes/fork/feature/fc4sc-coverage-rebased").strip()),
               "same_tree_as": same_tree, "no_diff_with": patch_eq}
    else:
        dup = {"exists_locally": False}

    uvm = [r for r in all_rows if r["project"] == "uvm-systemc"]
    union_main = sorted({d for r in uvm for d in r["new_golden_dirs_vs_main"]})
    union_own = sorted({d for r in uvm for d in r["new_golden_dirs_own"]})
    urepo = WB / "uvm-systemc" / "src"
    dev = next((r for r in ("development", "refs/remotes/fork/development") if
                git(urepo, "rev-parse", "-q", "--verify", r).strip()), None)
    dev_dirs = diff_facts(urepo, git(urepo, "merge-base", "main", dev).strip(), dev)["new_golden_dirs"] if dev else None

    def ratio(r, key, golden):
        d = r[key]
        t = d["test_code_loc"] + (d["test_golden_loc"] if golden else 0)
        return t / d["source_loc"] if d["source_loc"] else None

    res["a_counts"] = {"total": len(all_rows), "per_library": dict(Counter(r["project"] for r in all_rows)),
                       "fc4sc_coverage_rebased": dup,
                       "local_only": {p: v["local_only"] for p, v in res["branches"].items() if v["local_only"]}}
    res["b_adds_test"] = {
        "stacked_branches": [{"branch": f"{r['project']}:{r['branch']}", "parent": r["parent"]}
                             for r in all_rows if r["parent"]],
        "own_diff_adds_test": sum(r["adds_test_own"] for r in all_rows),
        "diff_vs_main_adds_test": sum(r["adds_test_vs_main"] for r in all_rows),
        "per_library_own": dict(Counter(r["project"] for r in all_rows if r["adds_test_own"])),
        "per_library_vs_main": dict(Counter(r["project"] for r in all_rows if r["adds_test_vs_main"])),
        "branches_touching_stubs": [f"{r['project']}:{r['branch']}" for r in all_rows if r["stubs_touched"]],
        "no_test_own": [f"{r['project']}:{r['branch']}" for r in all_rows if not r["adds_test_own"]]}
    res["c_golden_dirs"] = {"distinct_union_vs_main": len(union_main), "distinct_union_own": len(union_own),
                            "sum_over_branches_vs_main": sum(len(r["new_golden_dirs_vs_main"]) for r in uvm),
                            "development_vs_main": len(dev_dirs) if dev_dirs is not None else None,
                            "development_ref": dev}
    res["d_ratio_uvm"] = {
        "own_cxx_only": med(ratio(r, "own", False) for r in uvm),
        "own_with_golden": med(ratio(r, "own", True) for r in uvm),
        "vs_main_cxx_only": med(ratio(r, "vs_main", False) for r in uvm),
        "vs_main_with_golden": med(ratio(r, "vs_main", True) for r in uvm),
        "branches_with_source": sum(1 for r in uvm if r["own"]["source_loc"])}
    def ccn_rows(rows, key):
        return [{"branch": f"{r['project']}:{r['branch']}", **r[key]} for r in rows if r[key]]
    res["e_ccn"] = {"uvm_own": ccn_summary(ccn_rows(uvm, "ccn_own")),
                    "uvm_vs_main": ccn_summary(ccn_rows(uvm, "ccn_vs_main")),
                    "all_own": ccn_summary(ccn_rows(all_rows, "ccn_own")),
                    "all_vs_main": ccn_summary(ccn_rows(all_rows, "ccn_vs_main"))}
    fork_set = {(r["project"], r["branch"]) for r in all_rows}
    res["f_audit"] = audit_facts(fork_set)
    res["rows"] = all_rows
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "recount.json").write_text(json.dumps(res, indent=2) + "\n")
    (OUT / "recount.md").write_text(render(res))
    print((OUT / "recount.md").read_text())


def render(r: dict) -> str:
    a, b, c, d, e, f = (r[k] for k in ("a_counts", "b_adds_test", "c_golden_dirs", "d_ratio_uvm",
                                        "e_ccn", "f_audit"))
    def cc(x):
        t = x["largest_increase"]
        top = f"{t['branch']} ({t['before']} to {t['after']}, +{t['delta']})" if t else "-"
        return (f"{x['branches']} branches: {x['lowered']} lowered, {x['raised']} raised, {x['unchanged']} unchanged; "
                f"median delta {x['median_delta']}; largest increase {top}")
    L = ["# Recount of the proof-bar numbers (fork branches only)", "",
         "Read-only; branch set = refs/remotes/fork/{fix,feature}/* in the four forks. "
         "The branch-SHA manifest is in recount.json. Generated by `analysis/recount.py`.", "",
         "## a) Branches", "",
         f"- Total {a['total']}: " + ", ".join(f"{k} {v}" for k, v in a["per_library"].items()) + ".",
         f"- feature/fc4sc-coverage-rebased: {json.dumps(a['fc4sc_coverage_rebased'])}.",
         f"- Local-only fix/feature branches: {json.dumps(a['local_only'])}.", "",
         "## b) Adds a test (rename detection, stubs excluded)", "",
         f"- Stacked branches: {len(b['stacked_branches'])}: " +
         "; ".join(f"{x['branch']} on {x['parent']}" for x in b["stacked_branches"]) + ".",
         f"- (i) Own diff (vs parent) adds a test: {b['own_diff_adds_test']} of {a['total']} "
         f"({json.dumps(b['per_library_own'])}).",
         f"- (ii) Diff vs main adds a test: {b['diff_vs_main_adds_test']} of {a['total']} "
         f"({json.dumps(b['per_library_vs_main'])}).",
         f"- Branches touching a stub file: {', '.join(b['branches_touching_stubs']) or 'none'}.", "",
         "## c) New UVM-SystemC golden-log test folders", "",
         f"- Distinct across branches (vs main): {c['distinct_union_vs_main']}; sum over branches without "
         f"dedupe: {c['sum_over_branches_vs_main']}; distinct own-diff folders: {c['distinct_union_own']}.",
         f"- {c['development_ref']} vs main: {c['development_vs_main']}.", "",
         "## d) UVM-SystemC test/source ratio (median per branch)", "",
         f"- Own diff: C++ tests only {d['own_cxx_only']}, with golden logs {d['own_with_golden']}.",
         f"- Diff vs main: C++ tests only {d['vs_main_cxx_only']}, with golden logs {d['vs_main_with_golden']}.",
         f"- Branches adding library source: {d['branches_with_source']}.", "",
         "## e) Cyclomatic complexity (lizard, branches modifying existing library source)", "",
         f"- UVM-SystemC, own diff: {cc(e['uvm_own'])}.",
         f"- UVM-SystemC, vs main: {cc(e['uvm_vs_main'])}.",
         f"- All four libraries, own diff: {cc(e['all_own'])}.",
         f"- All four libraries, vs main: {cc(e['all_vs_main'])}.", "",
         "## f) Review reports", "",
         f"- Topics with a review report: {f['topics_with_report']}; recording a sanitizer build: "
         f"{f['topics_sanitizer']}; recording a no-new-warnings check vs base: {f['topics_no_new_warnings']}.",
         f"- Fork branches with a review report: {f['fork_branches_with_review']}; without: "
         f"{f['fork_branches_without_review']}.",
         f"- parity-batch-2 used a sanitizer: {f['parity_batch_2_sanitizer']}.", "",
         "## g) Review rounds", "",
         f"- Review topics with a second round: {f['topics_second_round']} of {f['audit_topics']}.", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
