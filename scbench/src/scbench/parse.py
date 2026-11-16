"""Parsers that turn raw tool output into small, structured results.

Every parser is pure (text in, dict out) so it can be unit-tested without a
compiler, a simulator or a solver.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

# clang/gcc: path:line:col: error: message
_DIAG = re.compile(
    r"^(?P<file>[^\s:][^:]*):(?P<line>\d+):(?:(?P<col>\d+):)?\s*"
    r"(?P<sev>fatal error|error|warning|note):\s*(?P<msg>.*)$"
)
_LINKER = re.compile(r"(undefined reference to|Undefined symbols for architecture|ld: |collect2: error)")


def compiler_diagnostics(log: str, limit: int = 20) -> dict:
    """First `limit` errors (with file, line, column), plus counts."""
    errors, warnings, linker = [], 0, []
    for raw in log.splitlines():
        m = _DIAG.match(raw.strip())
        if m:
            sev = m["sev"]
            if sev == "warning":
                warnings += 1
            elif sev in ("error", "fatal error"):
                if len(errors) < limit:
                    errors.append({
                        "file": m["file"], "line": int(m["line"]),
                        "col": int(m["col"]) if m["col"] else None,
                        "message": m["msg"].strip(),
                    })
            continue
        if _LINKER.search(raw) and len(linker) < 5:
            linker.append(raw.strip())
    total_errors = sum(1 for r in log.splitlines()
                       if (m := _DIAG.match(r.strip())) and m["sev"] in ("error", "fatal error"))
    return {"errors": errors, "error_count": total_errors,
            "warning_count": warnings, "linker_errors": linker}


_SEV = re.compile(r"^(UVM_INFO|UVM_WARNING|UVM_ERROR|UVM_FATAL)\s*:\s*(\d+)\s*$")


def uvm_report_counts(log: str) -> dict | None:
    """Counts from the last '--- UVM Report Summary ---' block, if any."""
    idx = log.rfind("--- UVM Report Summary ---")
    if idx < 0:
        return None
    counts = {}
    for line in log[idx:].splitlines():
        m = _SEV.match(line.strip())
        if m:
            counts[m[1]] = int(m[2])
    return counts or None


def first_uvm_problem(log: str) -> str | None:
    for line in log.splitlines():
        if (line.startswith(("UVM_ERROR", "UVM_FATAL")) and "Report counts" not in line
                and not _SEV.match(line.strip())):     # skip the summary count lines
            return line.strip()[:400]
    return None


def golden_diff(log: str, max_lines: int = 40) -> list[str] | None:
    """The unified diff run-test.py prints after 'differences in the output:'."""
    idx = log.find("differences in the output:")
    if idx < 0:
        return None
    out = []
    for line in log[idx:].splitlines()[1:]:
        if line.startswith(("failed to validate", "<end of output>")):
            break
        out.append(line)
        if len(out) >= max_lines:
            out.append("... (diff truncated)")
            break
    return out


_CTEST_SUMMARY = re.compile(r"(\d+)% tests passed, (\d+) tests failed out of (\d+)")


def ctest_summary(log: str) -> dict | None:
    m = _CTEST_SUMMARY.search(log)
    if not m:
        return None
    return {"passed_pct": int(m[1]), "failed": int(m[2]), "total": int(m[3])}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":")[-1]


def _count(elem) -> int:
    for c in elem.iter():
        if _local(c.tag) == "contents":
            return int(c.get("coverageCount", "0"))
    return 0


def fc4sc_coverage(xml_text: str, name_filter: str = "", max_holes: int = 50) -> dict:
    """Summarise an FC4SC UCIS XML database: per coverpoint and cross, the
    bins hit, the bins missed, and the coverage percentage against at_least."""
    root = ET.fromstring(xml_text)
    groups = []
    for cg in root.iter():
        if _local(cg.tag) != "cgInstance":
            continue
        cg_name = cg.get("name", "")
        cg_type = ""
        for c in cg:
            if _local(c.tag) == "cgId":
                cg_type = c.get("cgName", "")
        items = []
        for child in cg:
            kind = _local(child.tag)
            if kind not in ("coverpoint", "cross"):
                continue
            name = child.get("name", "")
            full = f"{cg_type or cg_name}.{name}"
            if name_filter and name_filter not in full:
                continue
            at_least = 1
            for o in child:
                if _local(o.tag) == "options":
                    at_least = int(o.get("at_least", "1") or 1)
            bins = []
            for b in child:
                bk = _local(b.tag)
                if bk == "coverpointBin":
                    if b.get("type", "default") in ("illegal", "ignore"):
                        continue
                    bins.append((b.get("name", ""), _count(b)))
                elif bk == "crossBin":
                    idx = [i.text for i in b if _local(i.tag) == "index"]
                    bins.append((b.get("name") or "<" + ",".join(idx) + ">", _count(b)))
            hit = [n for n, c in bins if c >= at_least]
            holes = [{"bin": n, "count": c} for n, c in bins if c < at_least]
            items.append({
                "name": full, "kind": kind, "at_least": at_least,
                "bins": len(bins), "hit": len(hit),
                "coverage_pct": round(100.0 * len(hit) / len(bins), 2) if bins else 100.0,
                "holes": holes[:max_holes],
                "holes_truncated": max(0, len(holes) - max_holes),
            })
        if items:
            groups.append({"covergroup": cg_type, "instance": cg_name, "items": items})
    all_items = [i for g in groups for i in g["items"]]
    total_bins = sum(i["bins"] for i in all_items)
    total_hit = sum(i["hit"] for i in all_items)
    return {
        "covergroups": groups,
        "overall_pct": round(100.0 * total_hit / total_bins, 2) if total_bins else None,
        "bins": total_bins, "hit": total_hit,
    }


def tail(text: str, lines: int = 30, max_chars: int = 4000) -> str:
    t = "\n".join(text.splitlines()[-lines:])
    return t[-max_chars:]
