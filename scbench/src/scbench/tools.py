"""Verification tools for AI agents working on SystemC-family libraries.

Each tool runs the real build, test, coverage or solver step and returns a
small JSON-ready dict instead of raw logs. The same functions back the MCP
server (server.py) and the grader in the harness (harness.py).

Configuration comes from the environment so one server can be pointed at any
checkout:
  SCBENCH_REPO     source tree to work on (default: current directory)
  SCBENCH_PROFILE  uvm-systemc | systemc (default: guessed from the tree)
  SCBENCH_BUILD    build directory (default: <repo>/build-scbench)
  SYSTEMC_HOME, UVM_SYSTEMC_HOME, CRAVE_HOME, FC4SC_HOME  installs
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from . import parse

MAX_LOG = 200_000


def run_cmd(cmd: list[str], cwd: Path, timeout: int) -> tuple[int, str, float]:
    """Run a command; return (exit code, combined output tail, seconds)."""
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, ((p.stdout or "") + (p.stderr or ""))[-MAX_LOG:], time.time() - t0
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return 124, out[-MAX_LOG:] + f"\n[timeout after {timeout}s]", time.time() - t0
    except FileNotFoundError as e:
        return 127, f"command not found: {e.filename}", time.time() - t0


@dataclass
class Profile:
    name: str
    test_root: str          # where test folders live, relative to the repo
    ctest_subdir: str       # where ctest runs, relative to the build dir
    strip_prefix: str       # removed from the target name
    configure: list[str]


def _env(name: str) -> str:
    return os.environ.get(name, "")


def profiles() -> dict[str, Profile]:
    sc = _env("SYSTEMC_HOME")
    common = ["-G", "Ninja", "-DCMAKE_BUILD_TYPE=Debug", "-DCMAKE_CXX_STANDARD=17",
              "-DCMAKE_CXX_STANDARD_REQUIRED=ON", "-DENABLE_REGRESSION=ON"]
    return {
        "uvm-systemc": Profile(
            "uvm-systemc", "tests/tests", "tests", "uvm-systemc-",
            common + ([f"-DCMAKE_PREFIX_PATH={sc}",
                       f"-DSystemCLanguage_DIR={sc}/lib/cmake/SystemCLanguage"] if sc else [])),
        "systemc": Profile(
            "systemc", "tests", "tests", "",
            common + ["-DENABLE_EXAMPLES=OFF"]),
    }


class Workspace:
    def __init__(self, repo: str | None = None, profile: str | None = None,
                 build: str | None = None):
        self.repo = Path(repo or _env("SCBENCH_REPO") or os.getcwd()).resolve()
        name = profile or _env("SCBENCH_PROFILE") or self._guess()
        self.profile = profiles()[name]
        self.build = Path(build or _env("SCBENCH_BUILD") or self.repo / "build-scbench").resolve()

    def _guess(self) -> str:
        if (self.repo / "src" / "uvmsc").exists():
            return "uvm-systemc"
        return "systemc"

    # -- helpers -----------------------------------------------------------
    def _run(self, cmd: list[str], cwd: Path, timeout: int) -> tuple[int, str, float]:
        return run_cmd(cmd, cwd, timeout)

    def configure(self) -> dict:
        self.build.mkdir(parents=True, exist_ok=True)
        rc, out, secs = self._run(["cmake", "-S", str(self.repo), "-B", str(self.build),
                                   *self.profile.configure], self.repo, 900)
        res = {"ok": rc == 0, "seconds": round(secs, 1)}
        if rc != 0:
            res["cmake_errors"] = [l for l in out.splitlines() if "CMake Error" in l][:10]
            res["log_tail"] = parse.tail(out)
        return res

    def target_for(self, test: str) -> str:
        t = test.strip("/").replace("/", "-")
        if self.profile.strip_prefix and t.startswith(self.profile.strip_prefix):
            t = t[len(self.profile.strip_prefix):]
        return t

    # -- tools -------------------------------------------------------------
    def build_tool(self, target: str = "") -> dict:
        """Configure if needed, then build `target` (default: the library)."""
        if not (self.build / "build.ninja").exists() or target:
            conf = self.configure()   # re-run so new test folders are discovered
            if not conf["ok"]:
                return {"ok": False, "stage": "configure", **conf}
        cmd = ["cmake", "--build", str(self.build)]
        if target:
            cmd += ["--target", target]
        rc, out, secs = self._run(cmd, self.repo, 3600)
        res = {"ok": rc == 0, "stage": "build", "target": target or "all",
               "seconds": round(secs, 1), **parse.compiler_diagnostics(out)}
        if rc != 0 and not res["errors"]:
            res["log_tail"] = parse.tail(out)
        return res

    def list_tests(self, pattern: str = "", limit: int = 50) -> dict:
        """Regression tests (folders with a golden log), filtered by substring."""
        root = self.repo / self.profile.test_root
        found = []
        for g in sorted(root.rglob("golden")):
            if g.is_dir():
                rel = str(g.parent.relative_to(root))
                if pattern in rel:
                    found.append(rel)
        return {"tests": found[:limit], "total": len(found)}

    def run_test(self, test: str) -> dict:
        """Build and run one regression test by its folder path; compare
        against its golden log; report UVM counts and the golden diff."""
        test = test.strip("/")
        target = self.target_for(test)
        b = self.build_tool(target)
        if not b["ok"]:
            return {"passed": False, "test": test, "stage": b.get("stage"), "build": b}
        cdir = self.build / self.profile.ctest_subdir
        # ctest names carry a config suffix (e.g. ".../cxx17/Debug"); allow it.
        rc, out, secs = self._run(["ctest", "-R", f"^{re.escape(test)}(/.*)?$", "--output-on-failure",
                                   "--timeout", "300"], cdir, 600)
        summ = parse.ctest_summary(out)
        if summ and summ["total"] == 0 or "No tests were found" in out:
            return {"passed": False, "test": test, "stage": "ctest",
                    "error": "no ctest test with that name; use list_tests"}
        # run-test.py writes the simulation output to a log file in the test's
        # working directory and prints nothing of it on success, so the UVM
        # report summary comes from that file (ctest output as a fallback).
        log = sim_log(cdir, test)
        sim = log.read_text(errors="replace") if log else out
        res = {"passed": rc == 0, "test": test, "seconds": round(secs, 1),
               "uvm_counts": parse.uvm_report_counts(sim),
               "first_uvm_problem": parse.first_uvm_problem(sim)}
        if log:
            res["sim_log"] = str(log)
        diff = parse.golden_diff(out)
        if diff:
            res["golden_diff"] = diff
        if rc != 0 and not diff:
            res["log_tail"] = parse.tail(out)
        return res

    def run_regression(self, pattern: str = "", jobs: int = 8) -> dict:
        """Build all tests and run those whose name contains `pattern`."""
        b = self.build_tool("all-tests")
        if not b["ok"]:
            return {"ok": False, "build": b}
        cdir = self.build / self.profile.ctest_subdir
        cmd = ["ctest", "-j", str(jobs), "--timeout", "300"]
        if pattern:
            cmd += ["-R", re.escape(pattern)]
        rc, out, secs = self._run(cmd, cdir, 3600)
        failed = re.findall(r"^\s*\d+ - (\S+) \(", out, re.M)
        return {"ok": rc == 0, "seconds": round(secs, 1),
                "summary": parse.ctest_summary(out), "failed": failed[:50]}


def sim_log(ctest_dir: Path, test: str) -> Path | None:
    """The simulation log run-test.py wrote for `test`: <leaf>.log in
    <ctest dir>/Testing/<test>/ (not the .run-test.log debug file)."""
    wd = ctest_dir / "Testing" / test.strip("/")
    if not wd.is_dir():
        return None
    logs = sorted(f for f in wd.glob("*.log")
                  if f.is_file() and not f.name.endswith(".run-test.log"))
    return max(logs, key=lambda f: f.stat().st_mtime) if logs else None


def query_coverage(xml_path: str, name_filter: str = "", max_holes: int = 50) -> dict:
    """Coverage per coverpoint and cross from an FC4SC UCIS XML file."""
    p = Path(xml_path)
    if not p.exists():
        return {"error": f"no such file: {xml_path}"}
    return parse.fc4sc_coverage(p.read_text(), name_filter, max_holes)


_VAR = re.compile(r"crv_variable\s*<[^;]*?>\s+(\w+)\s*;")

_CRAVE_MAIN = """\
#include <systemc>
#include <crave/ConstrainedRandom.hpp>
#include <crave/experimental/Experimental.hpp>
#include <iostream>
using namespace crave;
struct Item : public crv_sequence_item {
@DECLS@
  crv_constraint user{ @CONSTRAINTS@ };
  Item(crv_object_name) {}
};
int sc_main(int, char**) {
  crave::init();
  Item it("it");
  for (int i = 0; i < @N@; ++i) {
    if (!it.randomize()) { std::cout << "UNSAT" << std::endl; return 3; }
    std::cout << "S"@PRINTS@ << std::endl;
  }
  return 0;
}
"""

_CRAVE_CMAKE = """\
cmake_minimum_required(VERSION 3.16)
project(scbench_randcheck CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(SystemCLanguage CONFIG REQUIRED)
find_package(crave CONFIG REQUIRED)
add_executable(randcheck main.cpp)
target_link_libraries(randcheck PRIVATE crave::crave SystemC::systemc)
"""


def randomize_check(declarations: str, constraints: str, samples: int = 20) -> dict:
    """Compile a CRAVE item with the given variables and constraints, draw
    `samples` solutions, and report solvability and value ranges.

    declarations: C++ member lines, e.g. "crv_variable<unsigned> addr;"
    constraints:  comma-separated CRAVE expressions, e.g. "addr() < 256, addr() % 4 == 0"
    """
    names = _VAR.findall(declarations)
    if not names:
        return {"error": "declare at least one crv_variable<T> name;"}
    samples = max(1, min(int(samples), 1000))
    prints = "".join(f' << " {n}=" << it.{n}' for n in names)
    src = (_CRAVE_MAIN.replace("@DECLS@", declarations)
           .replace("@CONSTRAINTS@", constraints)
           .replace("@N@", str(samples)).replace("@PRINTS@", prints))
    prefix = ";".join(x for x in (_env("CRAVE_HOME"), _env("UVM_SYSTEMC_HOME"), _env("SYSTEMC_HOME")) if x)
    work = Path(tempfile.mkdtemp(prefix="scbench-rand-"))
    try:
        (work / "main.cpp").write_text(src)
        (work / "CMakeLists.txt").write_text(_CRAVE_CMAKE)
        rc, out, _ = run_cmd(["cmake", "-S", str(work), "-B", str(work / "b"),
                                         "-G", "Ninja", f"-DCMAKE_PREFIX_PATH={prefix}"], work, 600)
        if rc != 0:
            return {"ok": False, "stage": "configure", "log_tail": parse.tail(out)}
        rc, out, _ = run_cmd(["cmake", "--build", str(work / "b")], work, 900)
        if rc != 0:
            return {"ok": False, "stage": "compile", **parse.compiler_diagnostics(out)}
        rc, out, secs = run_cmd([str(work / "b" / "randcheck")], work, 300)
        if "UNSAT" in out:
            return {"ok": True, "solvable": False, "variables": names}
        values: dict[str, list[int]] = {n: [] for n in names}
        for line in out.splitlines():
            if not line.startswith("S "):
                continue
            for tok in line[2:].split():
                k, _, v = tok.partition("=")
                try:
                    values.setdefault(k, []).append(int(v))
                except ValueError:
                    pass
        stats = {}
        for n, vs in values.items():
            if vs:
                counts: dict[int, int] = {}
                for v in vs:
                    counts[v] = counts.get(v, 0) + 1
                top = sorted(counts.items(), key=lambda kv: -kv[1])[:10]
                stats[n] = {"min": min(vs), "max": max(vs), "distinct": len(counts),
                            "most_common": [{"value": v, "count": c} for v, c in top]}
        return {"ok": rc == 0, "solvable": True, "samples": samples,
                "seconds": round(secs, 2), "stats": stats}
    finally:
        shutil.rmtree(work, ignore_errors=True)
