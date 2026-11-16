# Pilot results

Model `model-a`, vendor CLI, max turns 60, timeout 3600 s, 1 seeds, arms shell-guided, tools-guided, harness e281cad, started 2026-11-16T00:16:19-08:00. Runs recorded: 30 of 30 (fail 25, pass 5). Rate-limited attempts in the log: 3, error attempts: 0, limit probes: 12.

## All 15 tasks

| Metric | shell-guided | tools-guided |
|---|---|---|
| graded runs | 15 | 15 |
| passes | 3 | 2 |
| pass@1 (mean over seeds) | 20.0% | 13.3% |
| pass@1 per seed | s0: 3/15 | s0: 2/15 |
| pass@3 (tasks with 3 graded seeds) | 20.0% of 15 | 13.3% of 15 |
| turns mean / median | 59.73 / 60 | 60 / 60 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 14 / 0 | 15 / 0 |
| agent wall time mean / median / total (min) | 3.50 / 3.40 / 52.40 | 3.50 / 3.50 / 52.90 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 23,747 / 356,219 | 25,149 / 377,247 |
| tool calls per run: scbench / shell | 0 / 37.33 | 6.20 / 26.67 |
| tool calls total: scbench / shell / all | 0 / 560 / 874 | 93 / 400 / 878 |

## Excluding uvm-sequence-library (golden log depends on the gold random generator)

| Metric | shell-guided | tools-guided |
|---|---|---|
| graded runs | 14 | 14 |
| passes | 3 | 2 |
| pass@1 (mean over seeds) | 21.4% | 14.3% |
| pass@1 per seed | s0: 3/14 | s0: 2/14 |
| pass@3 (tasks with 3 graded seeds) | 21.4% of 14 | 14.3% of 14 |
| turns mean / median | 59.71 / 60.00 | 60 / 60.00 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 13 / 0 | 14 / 0 |
| agent wall time mean / median / total (min) | 3.60 / 3.40 / 49.90 | 3.60 / 3.60 / 49.90 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 24,631 / 344,836 | 25,110 / 351,549 |
| tool calls per run: scbench / shell | 0 / 35.79 | 6.43 / 26.71 |
| tool calls total: scbench / shell / all | 0 / 501 / 815 | 90 / 374 / 820 |

## Per task

P = pass, F = fail, E = error, R = rate limited, . = not run

| Task | shell-guided | tools-guided |
|---|---|---|
| signal-default-name | F | F |
| component-schedule-lifetime | F | F |
| config-db-exists | P | P |
| global-forward-declarations | P | P |
| hdl-type-mismatch-message | F | F |
| objection-callbacks | F | F |
| re-match-search | F | F |
| reg-deterministic-order | F | F |
| reg-map-internal-names | P | F |
| reg-map-small-memory | F | F |
| resource-pool-spell-check | F | F |
| sequencer-killed-requests | F | F |
| uvm-heartbeat | F | F |
| uvm-pool | F | F |
| uvm-sequence-library | F | F |

## Failures (first failing reason)

- signal-default-name / shell-guided / s0: golden: expected 'default constructed items: 4', got 'default constructed items: 8' [max_turns, 60 turns]
- signal-default-name / tools-guided / s0: golden: expected 'default constructed items: 4', got 'default constructed items: 8' [max_turns, 60 turns]
- component-schedule-lifetime / shell-guided / s0: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- component-schedule-lifetime / tools-guided / s0: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- hdl-type-mismatch-message / shell-guided / s0: golden: expected 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow (sc_object) can', got 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow is not of type ' [max_turns, 60 turns]
- hdl-type-mismatch-message / tools-guided / s0: golden: expected 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow (sc_object) can', got 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow is not of type ' [max_turns, 60 turns]
- objection-callbacks / shell-guided / s0: build: test.cpp:32: expected class name [max_turns, 60 turns]
- objection-callbacks / tools-guided / s0: build: test.cpp:32: expected class name [max_turns, 60 turns]
- re-match-search / shell-guided / s0: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- re-match-search / tools-guided / s0: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- reg-deterministic-order / shell-guided / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / tools-guided / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-map-internal-names / tools-guided / s0: golden: expected 'created the user class reg_rw, marker 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] The factor' [max_turns, 60 turns]
- reg-map-small-memory / shell-guided / s0: golden: expected 'one: offset 0x100, addresses 0x100 to 0x100, stride 4', got 'one: offset 0x100, addresses 0x100 to 0x100, stride 0' [max_turns, 60 turns]
- reg-map-small-memory / tools-guided / s0: golden: expected 'one: offset 0x100, addresses 0x100 to 0x100, stride 4', got 'one: offset 0x100, addresses 0x100 to 0x100, stride 0' [max_turns, 60 turns]
- resource-pool-spell-check / shell-guided / s0: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- resource-pool-spell-check / tools-guided / s0: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- sequencer-killed-requests / shell-guided / s0: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got '' [max_turns, 60 turns]
- sequencer-killed-requests / tools-guided / s0: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got 'UVM_FATAL @ 10 ns: test.sqr [uvm_sequence_controller] is_blocked passe' [max_turns, 60 turns]
- uvm-heartbeat / shell-guided / s0: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-heartbeat / tools-guided / s0: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-pool / shell-guided / s0: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-pool / tools-guided / s0: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-sequence-library / shell-guided / s0: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
- uvm-sequence-library / tools-guided / s0: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
