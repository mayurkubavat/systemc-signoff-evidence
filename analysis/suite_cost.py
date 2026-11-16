"""Time the existing regression suites of the four libraries (B3 of the
proof-bar study). Each library is built from `main` in a temporary detached
worktree under ~/.cache/scbench/cost (removed afterwards), with the same
options as oss-workbench bin/build-install, and the full ctest run is timed.
For UVM-SystemC it also times a clean configure+build and a single-test
rebuild+run after touching the test source or one library source.

    uv run python analysis/suite_cost.py --workbench ~/Silicon/active/oss-workbench \
        --out runs/proofbar/suite_cost.json [--only uvm-systemc,fc4sc]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path

JOBS = str(os.cpu_count() or 8)
COMMON = ["-G", "Ninja", "-DCMAKE_CXX_STANDARD=17", "-DCMAKE_CXX_STANDARD_REQUIRED=ON"]
UVM_TEST = "uvm-systemc/unit_tests/00basic/99fixes/01global_comparer"
UVM_LIB_SRC = "src/uvmsc/conf/uvm_resource_pool.cpp"


def run(cmd, cwd=None, env=None, timeout=7200):
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return p.returncode, round(time.time() - t0, 1), (p.stdout or "") + (p.stderr or "")


def must(cmd, **kw):
    rc, secs, out = run(cmd, **kw)
    if rc != 0:
        raise RuntimeError(f"{' '.join(map(str, cmd))} failed ({rc}):\n{out[-3000:]}")
    return secs, out


def ctest(cdir: Path, jobs: str) -> dict:
    rc, secs, out = run(["ctest", "-j", jobs, "--timeout", "300"], cwd=cdir)
    m = re.search(r"(\d+)% tests passed, (\d+) tests failed out of (\d+)", out)
    tt = re.search(r"Total Test time \(real\) =\s*([\d.]+) sec", out)
    per = sorted(((float(t), n) for n, t in
                  re.findall(r"Test\s+#\d+: (\S+) \.+.*?\s([\d.]+) sec", out)), reverse=True)
    return {"jobs": int(jobs), "wall_s": secs, "ctest_total_s": float(tt[1]) if tt else None,
            "tests": int(m[3]) if m else None, "failed": int(m[2]) if m else None,
            "sum_test_s": round(sum(t for t, _ in per), 1),
            "slowest": [{"test": n, "s": t} for t, n in per[:3]]}


class Tree:
    def __init__(self, repo: Path, root: Path, name: str, ref: str = "main"):
        self.repo, self.path, self.ref = repo, root / name, ref

    def __enter__(self):
        if self.path.exists():
            run(["git", "-C", str(self.repo), "worktree", "remove", "--force", str(self.path)])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        must(["git", "-C", str(self.repo), "worktree", "add", "--detach", str(self.path), self.ref])
        return self.path

    def __exit__(self, *exc):
        run(["git", "-C", str(self.repo), "worktree", "remove", "--force", str(self.path)])
        run(["git", "-C", str(self.repo), "worktree", "prune"])


def head(repo: Path, ref: str = "main") -> str:
    return f"{ref} " + must(["git", "-C", str(repo), "rev-parse", "--short=9", ref])[1].strip()


def uvm(wb: Path, root: Path) -> dict:
    repo, sc = wb / "uvm-systemc/src", os.environ["SYSTEMC_HOME"]
    with Tree(repo, root, "uvm-systemc") as wt:
        b = wt / "build"
        conf, _ = must(["cmake", "-S", str(wt), "-B", str(b), *COMMON, "-DCMAKE_BUILD_TYPE=Debug",
                        "-DENABLE_REGRESSION=ON", f"-DCMAKE_PREFIX_PATH={sc}",
                        f"-DSystemCLanguage_DIR={sc}/lib/cmake/SystemCLanguage"])
        lib, lo = must(["cmake", "--build", str(b), "-j", JOBS])
        tests, to = must(["cmake", "--build", str(b), "-j", JOBS, "--target", "all-tests"])
        steps = [len(re.findall(r"^\[\d+/\d+\] Building CXX", o, re.M)) for o in (lo, to)]
        full = [ctest(b / "tests", JOBS), ctest(b / "tests", "1")]
        target = UVM_TEST.replace("/", "-").removeprefix("uvm-systemc-")
        single = {}
        for label, touched in (("touch_test_source", next((wt / "tests/tests" / UVM_TEST).glob("*.cpp"))),
                               ("touch_library_source", wt / UVM_LIB_SRC)):
            os.utime(touched)
            bs, _ = must(["cmake", "--build", str(b), "--target", target])
            rc, rs, _ = run(["ctest", "-R", f"^{re.escape(UVM_TEST)}(/.*)?$"], cwd=b / "tests")
            single[label] = {"file": str(touched.relative_to(wt)), "build_s": bs, "run_s": rs,
                             "total_s": round(bs + rs, 1), "passed": rc == 0}
        return {"commit": head(repo), "build_type": "Debug", "configure_s": conf,
                "build_library_s": lib, "build_tests_s": tests, "cxx_compiles": steps,
                "clean_configure_build_s": round(conf + lib + tests, 1),
                "full_ctest": full, "single_test": {"test": UVM_TEST, **single}}


def systemc(wb: Path, root: Path) -> dict:
    repo = wb / "systemc/src"
    with Tree(repo, root, "systemc") as wt:
        b = wt / "build"
        conf, _ = must(["cmake", "-S", str(wt), "-B", str(b), *COMMON, "-DCMAKE_BUILD_TYPE=Release",
                        "-DENABLE_EXAMPLES=ON", "-DENABLE_REGRESSION=ON"])
        build, _ = must(["cmake", "--build", str(b), "-j", JOBS, "--target", "all", "all-tests", "all-examples"])
        return {"commit": head(repo), "build_type": "Release", "configure_s": conf, "build_s": build,
                "full_ctest": {"tests": ctest(b / "tests", JOBS), "examples": ctest(b / "examples", JOBS)}}


def fc4sc(wb: Path, root: Path) -> dict:
    repo = wb / "fc4sc/src"
    with Tree(repo, root, "fc4sc", "development") as wt:
        b = wt / "build"
        conf, _ = must(["cmake", "-S", str(wt), "-B", str(b), *COMMON, "-DCMAKE_BUILD_TYPE=Release",
                        "-DFC4SC_BUILD_TESTS=ON"])
        build, _ = must(["cmake", "--build", str(b), "-j", JOBS])
        return {"commit": head(repo, "development"), "build_type": "Release", "configure_s": conf,
                "build_s": build, "full_ctest": ctest(b, JOBS)}


def crave(wb: Path, root: Path) -> dict:
    repo = wb / "crave/src"
    sc, uvmh = os.environ["SYSTEMC_HOME"], os.environ["UVM_SYSTEMC_HOME"]
    with Tree(repo, root, "crave", "development") as wt:
        b, prefix = wt / "build", wt / "prefix"
        env = {**os.environ, "SYSTEMC_HOME": sc, "UVM_SYSTEMC_HOME": uvmh}
        conf, _ = must(["cmake", "-S", str(wt), "-B", str(b), *COMMON, "-DCMAKE_BUILD_TYPE=Release",
                        f"-DCMAKE_INSTALL_PREFIX={prefix}", f"-DCMAKE_PREFIX_PATH={sc};{uvmh}",
                        "-DWITH_SYSTEMC=ON", "-DmetaSMT_USE_CUDD=ON", "-DmetaSMT_USE_Z3=ON",
                        *[f"-DmetaSMT_USE_{x}=OFF" for x in ("YICES2", "Boolector", "CVC4", "MiniSat",
                                                             "STP", "Aiger", "lingeling", "picosat")],
                        "-DCRAVE_ENABLE_TESTS=ON", "-DCRAVE_BUILD_EXAMPLES=ON"], env=env)
        build, _ = must(["cmake", "--build", str(b), "-j", JOBS], env=env)
        return {"commit": head(repo, "development"), "build_type": "Release", "configure_s": conf,
                "build_s_incl_z3_cudd": build, "full_ctest": ctest(b, JOBS)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbench", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="uvm-systemc,fc4sc,systemc,crave")
    a = ap.parse_args()
    wb = Path(a.workbench).expanduser()
    root = Path.home() / ".cache/scbench/cost"
    out = Path(a.out)
    res = json.loads(out.read_text()) if out.exists() else {"measured": {}}
    fns = {"uvm-systemc": uvm, "systemc": systemc, "fc4sc": fc4sc, "crave": crave}
    for name in a.only.split(","):
        print(f"== {name}", flush=True)
        try:
            res["measured"][name] = fns[name](wb, root)
        except Exception as e:     # keep the others; record why this one failed
            res["measured"][name] = {"error": str(e)[-2000:]}
        res["host"] = {"cpus": os.cpu_count(), "uname": os.uname().machine}
        out.write_text(json.dumps(res, indent=2))
        print(json.dumps(res["measured"][name], indent=1)[:1500], flush=True)


if __name__ == "__main__":
    main()
