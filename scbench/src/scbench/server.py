"""MCP server exposing the verification tools to AI coding agents (stdio)."""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import tools

mcp = FastMCP("scbench")
_ws: tools.Workspace | None = None


def ws() -> tools.Workspace:
    global _ws
    if _ws is None:
        _ws = tools.Workspace()
    return _ws


@mcp.tool()
def build(target: str = "") -> dict:
    """Configure (if needed) and build the library or one CMake target.
    Returns ok, seconds, and the first compiler errors as file/line/message."""
    return ws().build_tool(target)


@mcp.tool()
def list_tests(pattern: str = "", limit: int = 50) -> dict:
    """List regression tests (folders holding a golden log) whose path contains pattern."""
    return ws().list_tests(pattern, limit)


@mcp.tool()
def run_test(test: str) -> dict:
    """Build and run one regression test by folder path (as list_tests prints it).
    Returns passed, UVM report counts, the first UVM_ERROR/FATAL, and the diff
    against the golden log when the output differs."""
    return ws().run_test(test)


@mcp.tool()
def run_regression(pattern: str = "", jobs: int = 8) -> dict:
    """Build all tests and run those whose name contains pattern; returns the
    pass/fail summary and the names of failing tests."""
    return ws().run_regression(pattern, jobs)


@mcp.tool()
def query_coverage(xml_path: str, name_filter: str = "", max_holes: int = 50) -> dict:
    """Summarise an FC4SC UCIS coverage XML: coverage per coverpoint and cross,
    and the bins not yet hit."""
    return tools.query_coverage(xml_path, name_filter, max_holes)


@mcp.tool()
def randomize_check(declarations: str, constraints: str, samples: int = 20) -> dict:
    """Check CRAVE constraints: compile an item with the given crv_variable
    declarations and comma-separated constraint expressions, draw samples,
    and report whether it is solvable and the value ranges produced."""
    return tools.randomize_check(declarations, constraints, samples)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
