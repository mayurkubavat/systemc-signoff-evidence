# Pilot results

Model `model-a`, vendor CLI, max turns 60, timeout 3600 s, 1 seeds, arms shell-guided, tools-guided, harness 0b6f107, started 2026-11-15T17:36:23-08:00. Runs recorded: 30 of 30 (fail 23, pass 7). Rate-limited attempts in the log: 0, error attempts: 0, limit probes: 0.

## All 15 tasks

| Metric | shell-guided | tools-guided |
|---|---|---|
| graded runs | 15 | 15 |
| passes | 5 | 2 |
| pass@1 (mean over seeds) | 33.3% | 13.3% |
| pass@1 per seed | s0: 5/15 | s0: 2/15 |
| pass@3 (tasks with 3 graded seeds) | 33.3% of 15 | 13.3% of 15 |
| turns mean / median | 60 / 60 | 60 / 60 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 15 / 0 | 15 / 0 |
| agent wall time mean / median / total (min) | 3.80 / 3.60 / 56.50 | 3.50 / 3.60 / 53.20 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 23,878 / 358,171 | 24,679 / 370,187 |
| tool calls per run: scbench / shell | 0 / 34.87 | 5.40 / 28.27 |
| tool calls total: scbench / shell / all | 0 / 523 / 878 | 81 / 424 / 880 |

## Excluding uvm-sequence-library (golden log depends on the gold random generator)

| Metric | shell-guided | tools-guided |
|---|---|---|
| graded runs | 14 | 14 |
| passes | 5 | 2 |
| pass@1 (mean over seeds) | 35.7% | 14.3% |
| pass@1 per seed | s0: 5/14 | s0: 2/14 |
| pass@3 (tasks with 3 graded seeds) | 35.7% of 14 | 14.3% of 14 |
| turns mean / median | 60 / 60.00 | 60 / 60.00 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 14 / 0 | 14 / 0 |
| agent wall time mean / median / total (min) | 3.80 / 3.60 / 52.80 | 3.60 / 3.60 / 50.20 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 24,130 / 337,828 | 24,684 / 345,581 |
| tool calls per run: scbench / shell | 0 / 35.57 | 5.57 / 27.93 |
| tool calls total: scbench / shell / all | 0 / 498 / 820 | 78 / 391 / 822 |

## Per task

P = pass, F = fail, E = error, R = rate limited, . = not run

| Task | shell-guided | tools-guided |
|---|---|---|
| signal-default-name | F | F |
| component-schedule-lifetime | F | F |
| config-db-exists | P | F |
| global-forward-declarations | P | P |
| hdl-type-mismatch-message | P | F |
| objection-callbacks | F | F |
| re-match-search | F | F |
| reg-deterministic-order | F | F |
| reg-map-internal-names | P | P |
| reg-map-small-memory | P | F |
| resource-pool-spell-check | F | F |
| sequencer-killed-requests | F | F |
| uvm-heartbeat | F | F |
| uvm-pool | F | F |
| uvm-sequence-library | F | F |

## Failures (first failing reason)

- signal-default-name / shell-guided / s0: golden: expected 'signal_0', got 'item_0' [max_turns, 60 turns]
- signal-default-name / tools-guided / s0: golden: expected 'default constructed items: 4', got 'default constructed items: 8' [max_turns, 60 turns]
- component-schedule-lifetime / shell-guided / s0: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- component-schedule-lifetime / tools-guided / s0: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- config-db-exists / tools-guided / s0: golden: expected "context '' inst 'test.env' field 'from_top': get=1 exists=1", got "context '' inst 'test.env' field 'from_top': get=1 exists=0" [max_turns, 60 turns]
- hdl-type-mismatch-message / tools-guided / s0: golden: expected 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow (sc_object) can', got 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow is not of type ' [max_turns, 60 turns]
- objection-callbacks / shell-guided / s0: build: test.cpp:32: expected class name [max_turns, 60 turns]
- objection-callbacks / tools-guided / s0: build: test.cpp:32: expected class name [max_turns, 60 turns]
- re-match-search / shell-guided / s0: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- re-match-search / tools-guided / s0: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- reg-deterministic-order / shell-guided / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / tools-guided / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-map-small-memory / tools-guided / s0: golden: expected 'one: offset 0x100, addresses 0x100 to 0x100, stride 4', got 'one: offset 0x100, addresses 0x100 to 0x100, stride 0' [max_turns, 60 turns]
- resource-pool-spell-check / shell-guided / s0: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- resource-pool-spell-check / tools-guided / s0: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- sequencer-killed-requests / shell-guided / s0: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got 'UVM_FATAL @ 10 ns: test.sqr [uvm_sequence_controller] is_blocked passe' [max_turns, 60 turns]
- sequencer-killed-requests / tools-guided / s0: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got 'UVM_FATAL @ 10 ns: test.sqr [uvm_sequence_controller] is_blocked passe' [max_turns, 60 turns]
- uvm-heartbeat / shell-guided / s0: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-heartbeat / tools-guided / s0: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-pool / shell-guided / s0: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-pool / tools-guided / s0: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-sequence-library / shell-guided / s0: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
- uvm-sequence-library / tools-guided / s0: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
