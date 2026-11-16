# Pilot results

Model `model-b`, vendor CLI, max turns 60, timeout 3600 s, 3 seeds, arms shell, tools, harness 25d9f0c, started 2026-11-15T15:15:24-08:00. Runs recorded: 90 of 90 (fail 33, pass 57). Rate-limited attempts in the log: 0, error attempts: 0, limit probes: 0.

## All 15 tasks

| Metric | shell | tools |
|---|---|---|
| graded runs | 45 | 45 |
| passes | 28 | 29 |
| pass@1 (mean over seeds) | 62.2% | 64.5% |
| pass@1 per seed | s0: 10/15, s1: 9/15, s2: 9/15 | s0: 9/15, s1: 10/15, s2: 10/15 |
| pass@3 (tasks with 3 graded seeds) | 66.7% of 15 | 66.7% of 15 |
| turns mean / median | 44.49 / 44 | 32.78 / 34 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 8 / 0 | 0 / 0 |
| agent wall time mean / median / total (min) | 4.50 / 4.30 / 200.60 | 4.70 / 4.60 / 213.40 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 23,623 / 1,063,064 | 23,490 / 1,057,050 |
| tool calls per run: scbench / shell | 0 / 24.89 | 11.20 / 14.24 |
| tool calls total: scbench / shell / all | 0 / 1120 / 2415 | 504 / 641 / 2570 |

## Excluding uvm-sequence-library (golden log depends on the gold random generator)

| Metric | shell | tools |
|---|---|---|
| graded runs | 45 | 45 |
| passes | 28 | 29 |
| pass@1 (mean over seeds) | 66.7% | 69.0% |
| pass@1 per seed | s0: 10/14, s1: 9/14, s2: 9/14 | s0: 9/14, s1: 10/14, s2: 10/14 |
| pass@3 (tasks with 3 graded seeds) | 71.4% of 14 | 71.4% of 14 |
| turns mean / median | 44.49 / 44 | 32.78 / 34 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 8 / 0 | 0 / 0 |
| agent wall time mean / median / total (min) | 4.50 / 4.30 / 200.60 | 4.70 / 4.60 / 213.40 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 23,623 / 1,063,064 | 23,490 / 1,057,050 |
| tool calls per run: scbench / shell | 0 / 24.89 | 11.20 / 14.24 |
| tool calls total: scbench / shell / all | 0 / 1120 / 2415 | 504 / 641 / 2570 |

## Per task

P = pass, F = fail, E = error, R = rate limited, . = not run

| Task | shell | tools |
|---|---|---|
| signal-default-name | P F F | F P P |
| component-schedule-lifetime | P P P | P P P |
| config-db-exists | P P P | P P P |
| global-forward-declarations | P P P | P P P |
| hdl-type-mismatch-message | P P P | P P P |
| objection-callbacks | P P P | P P P |
| re-match-search | P P P | P P P |
| reg-deterministic-order | F F F | F F F |
| reg-map-internal-names | P P P | P P P |
| reg-map-small-memory | P P P | P P P |
| resource-pool-spell-check | P P P | P P P |
| sequencer-killed-requests | F F F | F F F |
| uvm-heartbeat | F F F | F F F |
| uvm-pool | F F F | F F F |
| uvm-sequence-library | F F F | F F F |

## Failures (first failing reason)

- signal-default-name / shell / s1: configure: -- SystemCTLM_VERSION = 2.0.6
-- INSTALL_TO_LIB_BUILD_TYPE_DIR = OFF
-- INSTALL_TO_LIB_TARGET_ARCH_DIR = OFF
-- INSTALL_LIB_TARGET_ARCH_SYMLINK = OFF
-- -------
- signal-default-name / shell / s2: golden: expected 'default constructed items: 4', got 'default constructed items: 8'
- signal-default-name / tools / s0: golden: expected 'default constructed items: 4', got 'default constructed items: 8'
- reg-deterministic-order / shell / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / shell / s1: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / shell / s2: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got '' [max_turns, 60 turns]
- reg-deterministic-order / tools / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got ''
- reg-deterministic-order / tools / s1: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got ''
- reg-deterministic-order / tools / s2: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got ''
- sequencer-killed-requests / shell / s0: uvm: UVM_ERROR <worktree>/uvm-systemc__sequencer-killed-requests__shell__s0/src/uvmsc/seq/uvm_sequencer_base.cpp(852) @ 10 ns: te
- sequencer-killed-requests / shell / s1: uvm: UVM_ERROR <worktree>/uvm-systemc__sequencer-killed-requests__shell__s1/src/uvmsc/seq/uvm_sequencer_base.cpp(853) @ 10 ns: te
- sequencer-killed-requests / shell / s2: uvm: UVM_ERROR <worktree>/uvm-systemc__sequencer-killed-requests__shell__s2/src/uvmsc/seq/uvm_sequencer_base.cpp(856) @ 10 ns: te [max_turns, 60 turns]
- sequencer-killed-requests / tools / s0: uvm: UVM_ERROR <worktree>/uvm-systemc__sequencer-killed-requests__tools__s0/src/uvmsc/seq/uvm_sequencer_base.cpp(857) @ 10 ns: te
- sequencer-killed-requests / tools / s1: uvm: UVM_ERROR <worktree>/uvm-systemc__sequencer-killed-requests__tools__s1/src/uvmsc/seq/uvm_sequencer_base.cpp(852) @ 10 ns: te
- sequencer-killed-requests / tools / s2: uvm: UVM_ERROR <worktree>/uvm-systemc__sequencer-killed-requests__tools__s2/src/uvmsc/seq/uvm_sequencer_base.cpp(856) @ 10 ns: te
- uvm-heartbeat / shell / s0: golden: expected 'UVM_WARNING @ 0 s: test [NOEVNT] start() was called for: hb with a nul', got ''
- uvm-heartbeat / shell / s1: golden: expected 'UVM_WARNING @ 0 s: test [NOEVNT] start() was called for: hb with a nul', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [NOEVNT] start() ' [max_turns, 60 turns]
- uvm-heartbeat / shell / s2: golden: expected 'UVM_WARNING @ 0 s: test [NOEVNT] start() was called for: hb with a nul', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [NOEVNT] start() ' [max_turns, 60 turns]
- uvm-heartbeat / tools / s0: golden: expected 'UVM_WARNING @ 0 s: test [NOEVNT] start() was called for: hb with a nul', got 'UVM_ERROR <removed by verify-uvm.pl> @ 0 s: reporter [NOEVNT] start() '
- uvm-heartbeat / tools / s1: golden: expected 'UVM_WARNING @ 0 s: test [NOEVNT] start() was called for: hb with a nul', got 'UVM_ERROR @ 0 s: test [NOEVNT] start() was called for: hb with a null '
- uvm-heartbeat / tools / s2: golden: expected 'UVM_WARNING @ 0 s: test [NOEVNT] start() was called for: hb with a nul', got ''
- uvm-pool / shell / s0: golden: expected "UVM_WARNING @ 0 s: reporter [POOLDEL] delete: pool key doesn't exist. ", got "UVM_WARNING @ 0 s: reporter [POOLDEL] delete: key doesn't exist"
- uvm-pool / shell / s1: golden: expected "UVM_WARNING @ 0 s: reporter [POOLDEL] delete: pool key doesn't exist. ", got "UVM_WARNING @ 0 s: reporter [POOLDEL] do_delete: pool key doesn't exis"
- uvm-pool / shell / s2: golden: expected "UVM_WARNING @ 0 s: reporter [POOLDEL] delete: pool key doesn't exist. ", got "UVM_WARNING @ 0 s: reporter [POOLDEL] do_delete: pool key doesn't exis"
- uvm-pool / tools / s0: golden: expected "UVM_WARNING @ 0 s: reporter [POOLDEL] delete: pool key doesn't exist. ", got "UVM_WARNING @ 0 s: reporter [POOLDEL] do_delete: key doesn't exist"
- uvm-pool / tools / s1: golden: expected "UVM_WARNING @ 0 s: reporter [POOLDEL] delete: pool key doesn't exist. ", got "UVM_WARNING @ 0 s: reporter [POOLDEL] delete: key doesn't exist"
- uvm-pool / tools / s2: golden: expected "UVM_WARNING @ 0 s: reporter [POOLDEL] delete: pool key doesn't exist. ", got "UVM_WARNING @ 0 s: reporter [POOLDEL] do_delete: pool key doesn't exis"
- uvm-sequence-library / shell / s0: build: test.cpp:90: redefinition of 'IsSequenceItem'
- uvm-sequence-library / shell / s1: build: test.cpp:90: redefinition of 'IsSequenceItem'
- uvm-sequence-library / shell / s2: build: test.cpp:90: redefinition of 'IsSequenceItem'
- uvm-sequence-library / tools / s0: golden: expected 'caught SEQLIB/BAD_SEQ_TYPE', got 'caught SEQLIB/NULLSEQ'
- uvm-sequence-library / tools / s1: build: test.cpp:90: redefinition of 'IsSequenceItem'
- uvm-sequence-library / tools / s2: build: test.cpp:90: redefinition of 'IsSequenceItem'
