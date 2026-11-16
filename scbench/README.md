# scbench: agent tasks and verification tools for SystemC/UVM-SystemC

A small benchmark of real maintenance tasks for the open SystemC verification
libraries, and a tool server that exposes their build and regression flow to
a coding agent. It measures whether an agent fixes a task with shell access
only, or with typed verification tools.

## What is here

| Path | What it is |
| --- | --- |
| `tasks/pilot.json` | The 15 tasks: library, branch, base and gold commits, hidden test files, and the task statement. `description` is the statement given to the agent; `description_original` is the commit text it was edited from; `description_note` says why it changed. |
| `tasks/hidden/` | The hidden regression test of each task (test source and golden log), taken from the gold commit. The agent never sees these; grading restores them. |
| `src/scbench/tools.py`, `server.py`, `parse.py` | The verification tools and their MCP server: `build`, `list_tests`, `run_test`, `run_regression`, `query_coverage` (FC4SC), `randomize_check` (CRAVE). |
| `src/scbench/harness.py` | The harness: worktree at the base commit, agent run, grading with the hidden test, one record per run. It runs any agent through a generic command adapter (`--agent-cmd` or `AGENT_CMD`; the interface is in the module docstring). |
| `src/scbench/mine.py` | Builds task definitions from fix and feature branches. |
| `prompts/guided.md` | The frozen instruction file used by the guided arms, with its sha256. |
| `analysis/` | `summarize_pilot.py` (per-arm tables) and `edit_descriptions.py` (the task-statement edits). |
| `results/` | Graded results of the pilot: one `record.json` per run (pass or fail, first failing reason, turns, tool-call counts, tokens), each directory's `config.json`, `summary.md/json` and `run.log`, and `agent2027-results.md` with all tables. |

## The pilot

15 tasks (UVM-SystemC 14, SystemC 1), two arms (`shell`, `tools`), three seeds,
60-turn cap and one hour per run, with three models labelled Model A, Model B
and Model C. Two guided arms (`shell-guided`, `tools-guided`) add
`prompts/guided.md` and run one seed. Each run starts from a clean worktree at
the task's base commit, and the agent ran with only shell, file and (in the
tools arm) MCP tools, with no user settings, memory or instructions loaded.

## Rerunning

You need the four library forks checked out as `<workbench>/<library>/src`
(see the repository README), SystemC and UVM-SystemC installed
(`SYSTEMC_HOME`, `UVM_SYSTEMC_HOME`), Python 3.10 or later and
[uv](https://docs.astral.sh/uv/).

```bash
cd scbench
uv run python -m scbench.harness --workbench <workbench> --tasks tasks/pilot.json \
    --gold-check --out runs/gold                         # every task: gold passes, base fails
AGENT_CMD="<your agent command>" uv run python -m scbench.harness \
    --workbench <workbench> --tasks tasks/pilot.json --arms shell,tools --seeds 3 \
    --model <label> --out runs/mine --jobs 3
uv run python analysis/summarize_pilot.py runs/mine
uv run --extra dev pytest -q
```

## Limits of the pilot

- The guided prompt was written after seeing the baseline failures on these
  same tasks, so the guided results are not an independent test of it.
- One of the vendor CLIs could not disable web search. Web-search calls are
  counted per run, and the guided prompt forbids web use.
- That CLI has no turn limit of its own; the harness counted model turns in its
  output and stopped the agent at 60. The other CLI enforced the limit itself.
- Model C's runs are partial: they were stopped at 14 of 90 runs to stay within
  a usage quota.
- One task (uvm-sequence-library) has a golden log that prints the order chosen
  by the gold implementation's random generator, so an independent correct
  implementation can fail it. Summaries also report pass rates without it.
- Task statements were edited to remove fix hints and to add the public API or
  exact message text that the hidden test checks (see `description_note`).

## License

Apache License 2.0, as for the rest of the repository.
