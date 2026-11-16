# Pilot results

Model `model-a`, vendor CLI, max turns 60, timeout 3600 s, 3 seeds, arms shell, tools, harness e281cad, started 2026-11-15T21:51:10-08:00. Runs recorded: 90 of 90 (fail 70, pass 20). Rate-limited attempts in the log: 0, error attempts: 0, limit probes: 0.

## All 15 tasks

| Metric | shell | tools |
|---|---|---|
| graded runs | 45 | 45 |
| passes | 10 | 10 |
| pass@1 (mean over seeds) | 22.2% | 22.2% |
| pass@1 per seed | s0: 3/15, s1: 4/15, s2: 3/15 | s0: 3/15, s1: 3/15, s2: 4/15 |
| pass@3 (tasks with 3 graded seeds) | 33.3% of 15 | 33.3% of 15 |
| turns mean / median | 60 / 60 | 59.87 / 60 |
| web searches (one vendor CLI only) | 384 | 450 |
| hit max turns / timed out | 45 / 0 | 44 / 0 |
| agent wall time mean / median / total (min) | 4.40 / 4.30 / 196.50 | 5.00 / 4.80 / 224.20 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 21,380 / 962,114 | 24,877 / 1,119,487 |
| tool calls per run: scbench / shell | 0 / 28.73 | 6.27 / 20.24 |
| tool calls total: scbench / shell / all | 0 / 1293 / 2620 | 282 / 911 / 2643 |

## Excluding uvm-sequence-library (golden log depends on the gold random generator)

| Metric | shell | tools |
|---|---|---|
| graded runs | 42 | 42 |
| passes | 10 | 10 |
| pass@1 (mean over seeds) | 23.8% | 23.8% |
| pass@1 per seed | s0: 3/14, s1: 4/14, s2: 3/14 | s0: 3/14, s1: 3/14, s2: 4/14 |
| pass@3 (tasks with 3 graded seeds) | 35.7% of 14 | 35.7% of 14 |
| turns mean / median | 60 / 60.00 | 59.86 / 60.00 |
| web searches (one vendor CLI only) | 307 | 350 |
| hit max turns / timed out | 42 / 0 | 41 / 0 |
| agent wall time mean / median / total (min) | 4.40 / 4.30 / 183.40 | 5.00 / 4.70 / 209.20 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 22,372 / 939,631 | 26,080 / 1,095,372 |
| tool calls per run: scbench / shell | 0 / 29.55 | 6.55 / 20.95 |
| tool calls total: scbench / shell / all | 0 / 1241 / 2444 | 275 / 880 / 2467 |

## Per task

P = pass, F = fail, E = error, R = rate limited, . = not run

| Task | shell | tools |
|---|---|---|
| signal-default-name | P F F | F F F |
| component-schedule-lifetime | F F F | F F F |
| config-db-exists | P P P | P F P |
| global-forward-declarations | F P F | P P P |
| hdl-type-mismatch-message | F P P | F F P |
| objection-callbacks | F F F | F F F |
| re-match-search | F F F | F F F |
| reg-deterministic-order | F F F | F F F |
| reg-map-internal-names | P P P | P P P |
| reg-map-small-memory | F F F | F P F |
| resource-pool-spell-check | F F F | F F F |
| sequencer-killed-requests | F F F | F F F |
| uvm-heartbeat | F F F | F F F |
| uvm-pool | F F F | F F F |
| uvm-sequence-library | F F F | F F F |

## Failures (first failing reason)

- signal-default-name / shell / s1: golden: expected 'default constructed items: 4', got 'default constructed items: 8' [max_turns, 60 turns]
- signal-default-name / shell / s2: golden: expected 'default constructed items: 4', got 'default constructed items: 8' [max_turns, 60 turns]
- signal-default-name / tools / s0: golden: expected 'default constructed items: 4', got 'default constructed items: 8' [max_turns, 60 turns]
- signal-default-name / tools / s1: golden: expected 'default constructed items: 4', got 'default constructed items: 8' [max_turns, 60 turns]
- signal-default-name / tools / s2: golden: expected 'default constructed items: 4', got 'default constructed items: 8' [max_turns, 60 turns]
- component-schedule-lifetime / shell / s0: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- component-schedule-lifetime / shell / s1: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- component-schedule-lifetime / shell / s2: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- component-schedule-lifetime / tools / s0: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- component-schedule-lifetime / tools / s1: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- component-schedule-lifetime / tools / s2: golden: expected 'parent and child deleted', got '' [max_turns, 60 turns]
- config-db-exists / tools / s1: golden: expected "context '' inst 'test.env' field 'from_top': get=1 exists=1", got "context '' inst 'test.env' field 'from_top': get=1 exists=0" [max_turns, 60 turns]
- global-forward-declarations / shell / s0: build: test.cpp:31: reference to 'uvm_object' is ambiguous [max_turns, 60 turns]
- global-forward-declarations / shell / s2: build: test.cpp:31: reference to 'uvm_object' is ambiguous [max_turns, 60 turns]
- hdl-type-mismatch-message / shell / s0: golden: expected 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow (sc_object) can', got 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow is not of type ' [max_turns, 60 turns]
- hdl-type-mismatch-message / tools / s0: golden: expected 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow (sc_object) can', got 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow is not of type ' [max_turns, 60 turns]
- hdl-type-mismatch-message / tools / s1: golden: expected 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow (sc_object) can', got 'UVM_ERROR @ 0 s: reporter [HDL_READ] Object top.narrow is not of type ' [max_turns, 60 turns]
- objection-callbacks / shell / s0: build: test.cpp:32: expected class name [max_turns, 60 turns]
- objection-callbacks / shell / s1: build: test.cpp:32: expected class name [max_turns, 60 turns]
- objection-callbacks / shell / s2: build: test.cpp:32: expected class name [max_turns, 60 turns]
- objection-callbacks / tools / s0: build: test.cpp:32: expected class name [max_turns, 60 turns]
- objection-callbacks / tools / s1: build: test.cpp:32: expected class name [max_turns, 60 turns]
- objection-callbacks / tools / s2: build: test.cpp:32: expected class name [max_turns, 60 turns]
- re-match-search / shell / s0: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- re-match-search / shell / s1: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- re-match-search / shell / s2: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- re-match-search / tools / s0: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- re-match-search / tools / s1: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- re-match-search / tools / s2: golden: expected "get 'in_env' in 'test.env': 1", got "get 'in_env' in 'test.env': not found" [max_turns, 60 turns]
- reg-deterministic-order / shell / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / shell / s1: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / shell / s2: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / tools / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / tools / s1: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / tools / s2: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-map-small-memory / shell / s0: golden: expected 'one: offset 0x100, addresses 0x100 to 0x100, stride 4', got 'one: offset 0x100, addresses 0x100 to 0x100, stride 0' [max_turns, 60 turns]
- reg-map-small-memory / shell / s1: golden: expected 'one: offset 0x100, addresses 0x100 to 0x100, stride 4', got 'one: offset 0x100, addresses 0x100 to 0x100, stride 0' [max_turns, 60 turns]
- reg-map-small-memory / shell / s2: golden: expected 'one: offset 0x100, addresses 0x100 to 0x100, stride 4', got 'one: offset 0x100, addresses 0x100 to 0x100, stride 0' [max_turns, 60 turns]
- reg-map-small-memory / tools / s0: build: uvm_reg_map.cpp:2214: member reference base type 'uint_type' (aka 'unsigned long long') is not a structure or union [max_turns, 60 turns]
- reg-map-small-memory / tools / s2: golden: expected 'one: offset 0x100, addresses 0x100 to 0x100, stride 4', got 'one: offset 0x100, addresses 0x100 to 0x100, stride 0' [max_turns, 60 turns]
- resource-pool-spell-check / shell / s0: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- resource-pool-spell-check / shell / s1: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- resource-pool-spell-check / shell / s2: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- resource-pool-spell-check / tools / s0: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- resource-pool-spell-check / tools / s1: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- resource-pool-spell-check / tools / s2: golden: expected 'num_packets = 42', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [Test] read_by_na' [max_turns, 60 turns]
- sequencer-killed-requests / shell / s0: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got '' [max_turns, 60 turns]
- sequencer-killed-requests / shell / s1: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got 'UVM_FATAL @ 10 ns: test.sqr [uvm_sequence_controller] is_blocked passe' [max_turns, 60 turns]
- sequencer-killed-requests / shell / s2: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got '' [max_turns, 60 turns]
- sequencer-killed-requests / tools / s0: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got '' [max_turns, 60 turns]
- sequencer-killed-requests / tools / s1: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got '' [max_turns, 60 turns]
- sequencer-killed-requests / tools / s2: golden: expected 'UVM_ERROR <removed by verify-uvm.pl> @ 10 ns: test.sqr [SEQLCKZMB] The', got 'UVM_FATAL @ 30 ns: test.sqr [uvm_sequencer] is_child passed nullptr ch' [max_turns, 60 turns]
- uvm-heartbeat / shell / s0: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-heartbeat / shell / s1: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-heartbeat / shell / s2: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-heartbeat / tools / s0: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-heartbeat / tools / s1: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-heartbeat / tools / s2: build: test.cpp:80: unknown type name 'uvm_heartbeat' [max_turns, 60 turns]
- uvm-pool / shell / s0: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-pool / shell / s1: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-pool / shell / s2: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-pool / tools / s0: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-pool / tools / s1: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-pool / tools / s2: build: test.cpp:32: no template named 'uvm_pool' [max_turns, 60 turns]
- uvm-sequence-library / shell / s0: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
- uvm-sequence-library / shell / s1: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
- uvm-sequence-library / shell / s2: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
- uvm-sequence-library / tools / s0: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
- uvm-sequence-library / tools / s1: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
- uvm-sequence-library / tools / s2: build: test.cpp:86: no template named 'uvm_sequence_library' [max_turns, 60 turns]
