# Pilot results

Model `model-c`, vendor CLI, max turns 60, timeout 3600 s, 3 seeds, arms shell, tools, harness 97ed3e0, started 2026-11-15T13:49:42-08:00. Runs recorded: 14 of 90 (fail 1, pass 13). Rate-limited attempts in the log: 0, error attempts: 0, limit probes: 0.

Subscription usage window (seven_day): 39.0% at the first recorded run, 47.0% at the last.

## All 15 tasks

| Metric | shell | tools |
|---|---|---|
| graded runs | 7 | 7 |
| passes | 6 | 7 |
| pass@1 (mean over seeds) | 85.7% | 100.0% |
| pass@1 per seed | s0: 6/7 | s0: 7/7 |
| pass@3 (tasks with 3 graded seeds) | - of 0 | - of 0 |
| turns mean / median | 27.71 / 25 | 38.14 / 36 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 0 / 0 | 0 / 0 |
| agent wall time mean / median / total (min) | 5.60 / 5.90 / 39.40 | 5.40 / 5.40 / 37.90 |
| API-equivalent cost mean / total (USD) | 0.68 / 4.76 | 0.73 / 5.09 |
| output tokens mean / total | 10,882 / 76,180 | 10,749 / 75,248 |
| tool calls per run: scbench / shell | 0 / 20.57 | 10.29 / 12.14 |
| tool calls total: scbench / shell / all | 0 / 144 / 187 | 72 / 85 / 260 |

## Excluding uvm-sequence-library (golden log depends on the gold random generator)

| Metric | shell | tools |
|---|---|---|
| graded runs | 7 | 7 |
| passes | 6 | 7 |
| pass@1 (mean over seeds) | 85.7% | 100.0% |
| pass@1 per seed | s0: 6/7 | s0: 7/7 |
| pass@3 (tasks with 3 graded seeds) | - of 0 | - of 0 |
| turns mean / median | 27.71 / 25 | 38.14 / 36 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 0 / 0 | 0 / 0 |
| agent wall time mean / median / total (min) | 5.60 / 5.90 / 39.40 | 5.40 / 5.40 / 37.90 |
| API-equivalent cost mean / total (USD) | 0.68 / 4.76 | 0.73 / 5.09 |
| output tokens mean / total | 10,882 / 76,180 | 10,749 / 75,248 |
| tool calls per run: scbench / shell | 0 / 20.57 | 10.29 / 12.14 |
| tool calls total: scbench / shell / all | 0 / 144 / 187 | 72 / 85 / 260 |

## Per task

P = pass, F = fail, E = error, R = rate limited, . = not run

| Task | shell | tools |
|---|---|---|
| component-schedule-lifetime | P . . | P . . |
| config-db-exists | P . . | P . . |
| global-forward-declarations | P . . | P . . |
| hdl-type-mismatch-message | P . . | P . . |
| re-match-search | P . . | P . . |
| reg-deterministic-order | F . . | P . . |
| reg-map-internal-names | P . . | P . . |

## Failures (first failing reason)

- reg-deterministic-order / shell / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [completed, 36 turns]
