from pathlib import Path

from scbench import parse

FIX = Path(__file__).parent / "fixtures"

UVM_LOG = """\
** UVM TEST PASSED **
--- UVM Report Summary ---
** Report counts by severity
UVM_INFO      :   1
UVM_WARNING   :   0
UVM_ERROR     :   2
UVM_FATAL     :   0
"""

DIFF_LOG = """\
starting 'uvm-systemc/unit_tests/40phasing/10domains/01twodomains'
differences in the output:
--- 01twodomains/golden/test.log
+++ test.log.stripped
@@ -2,8 +2,8 @@
-UVM_INFO a
+UVM_INFO b
failed to validate golden log: output mismatch detected, check test.diff
<end of output>
"""

CLANG = """\
/src/uvmsc/conf/uvm_config_db.h:120:5: error: use of undeclared identifier 'foo'
/src/uvmsc/conf/uvm_config_db.h:12:1: warning: unused variable 'x'
ld: symbol(s) not found for architecture arm64
"""


def test_uvm_counts():
    assert parse.uvm_report_counts(UVM_LOG) == {
        "UVM_INFO": 1, "UVM_WARNING": 0, "UVM_ERROR": 2, "UVM_FATAL": 0}
    assert parse.uvm_report_counts("no summary") is None


def test_golden_diff():
    d = parse.golden_diff(DIFF_LOG)
    assert d[0].startswith("---") and "-UVM_INFO a" in d and "+UVM_INFO b" in d
    assert not any("failed to validate" in x for x in d)


def test_compiler_diagnostics():
    r = parse.compiler_diagnostics(CLANG)
    assert r["error_count"] == 1 and r["warning_count"] == 1
    assert r["errors"][0] == {"file": "/src/uvmsc/conf/uvm_config_db.h", "line": 120,
                              "col": 5, "message": "use of undeclared identifier 'foo'"}
    assert r["linker_errors"]


def test_ctest_summary():
    assert parse.ctest_summary("100% tests passed, 0 tests failed out of 3") == {
        "passed_pct": 100, "failed": 0, "total": 3}


def test_fc4sc_coverpoints():
    r = parse.fc4sc_coverage((FIX / "basic_sample_expression.xml").read_text())
    items = {i["name"]: i for g in r["covergroups"] for i in g["items"]}
    assert items["cvp_sample_test.factorial_cvp"]["coverage_pct"] == 100.0
    assert r["overall_pct"] == 100.0 and r["bins"] == 3


def test_fc4sc_cross_and_at_least():
    r = parse.fc4sc_coverage((FIX / "basic_at_least2.xml").read_text())
    kinds = {i["kind"] for g in r["covergroups"] for i in g["items"]}
    assert "cross" in kinds
    cross = [i for g in r["covergroups"] for i in g["items"] if i["kind"] == "cross"][0]
    assert cross["at_least"] == 2 and cross["holes"]


def test_first_uvm_problem_skips_summary_counts():
    assert parse.first_uvm_problem(UVM_LOG) is None
    log = "UVM_ERROR t.cpp(3) @ 0 s: top [ID] boom\n" + UVM_LOG
    assert parse.first_uvm_problem(log).startswith("UVM_ERROR t.cpp(3)")
