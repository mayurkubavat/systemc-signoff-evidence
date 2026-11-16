# Pilot results

Model `model-b`, vendor CLI, max turns 60, timeout 3600 s, 1 seeds, arms shell-guided, tools-guided, harness 0b6f107, started 2026-11-15T17:36:03-08:00. Runs recorded: 30 of 30 (fail 9, pass 21). Rate-limited attempts in the log: 0, error attempts: 0, limit probes: 0.

## All 15 tasks

| Metric | shell-guided | tools-guided |
|---|---|---|
| graded runs | 15 | 15 |
| passes | 10 | 11 |
| pass@1 (mean over seeds) | 66.7% | 73.3% |
| pass@1 per seed | s0: 10/15 | s0: 11/15 |
| pass@3 (tasks with 3 graded seeds) | 66.7% of 15 | 73.3% of 15 |
| turns mean / median | 29.20 / 27 | 25.33 / 25 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 0 / 0 | 0 / 0 |
| agent wall time mean / median / total (min) | 3.30 / 2.90 / 49.40 | 3.20 / 3.20 / 47.60 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 17,522 / 262,843 | 17,507 / 262,611 |
| tool calls per run: scbench / shell | 0 / 23.73 | 9.80 / 11.40 |
| tool calls total: scbench / shell / all | 0 / 356 / 701 | 147 / 171 / 719 |

## Excluding uvm-sequence-library (golden log depends on the gold random generator)

| Metric | shell-guided | tools-guided |
|---|---|---|
| graded runs | 14 | 14 |
| passes | 10 | 11 |
| pass@1 (mean over seeds) | 71.4% | 78.6% |
| pass@1 per seed | s0: 10/14 | s0: 11/14 |
| pass@3 (tasks with 3 graded seeds) | 71.4% of 14 | 78.6% of 14 |
| turns mean / median | 28.36 / 26.50 | 24.79 / 24.50 |
| web searches (one vendor CLI only) | 0 | 0 |
| hit max turns / timed out | 0 / 0 | 0 / 0 |
| agent wall time mean / median / total (min) | 3.20 / 2.80 / 44.90 | 3.00 / 3.10 / 42.60 |
| API-equivalent cost mean / total (USD) | n/a | n/a |
| output tokens mean / total | 16,181 / 226,542 | 16,035 / 224,496 |
| tool calls per run: scbench / shell | 0 / 22.93 | 9.86 / 11.14 |
| tool calls total: scbench / shell / all | 0 / 321 / 625 | 138 / 156 / 648 |

## Per task

P = pass, F = fail, E = error, R = rate limited, . = not run

| Task | shell-guided | tools-guided |
|---|---|---|
| signal-default-name | F | P |
| component-schedule-lifetime | P | P |
| config-db-exists | P | P |
| global-forward-declarations | P | P |
| hdl-type-mismatch-message | P | P |
| objection-callbacks | P | P |
| re-match-search | P | P |
| reg-deterministic-order | F | F |
| reg-map-internal-names | P | P |
| reg-map-small-memory | P | P |
| resource-pool-spell-check | P | P |
| sequencer-killed-requests | F | F |
| uvm-heartbeat | P | P |
| uvm-pool | F | F |
| uvm-sequence-library | F | F |

## Failures (first failing reason)

- signal-default-name / shell-guided / s0: configure: -- SystemCTLM_VERSION = 2.0.6
-- INSTALL_TO_LIB_BUILD_TYPE_DIR = OFF
-- INSTALL_TO_LIB_TARGET_ARCH_DIR = OFF
-- INSTALL_LIB_TARGET_ARCH_SYMLINK = OFF
-- -------
- reg-deterministic-order / shell-guided / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got ''
- reg-deterministic-order / tools-guided / s0: golden: expected 'registers of the block: reg0 reg1 reg2 reg3', got ''
- sequencer-killed-requests / shell-guided / s0: uvm: UVM_ERROR <worktree>/uvm-systemc__sequencer-killed-requests__shell-guided__s0/src/uvmsc/seq/uvm_sequencer_base.cpp(851) @
- sequencer-killed-requests / tools-guided / s0: uvm: UVM_ERROR <worktree>/uvm-systemc__sequencer-killed-requests__tools-guided__s0/src/uvmsc/seq/uvm_sequencer_base.cpp(852) @
- uvm-pool / shell-guided / s0: golden: expected 'copy           uvm_pool          -     @<removed by verify-uvm.pl>', got 'copy           uvm::uvm_pool     -     @<removed by verify-uvm.pl>'
- uvm-pool / tools-guided / s0: golden: expected 'copy           uvm_pool          -     @<removed by verify-uvm.pl>', got 'copy           uvm::uvm_pool     -     @<removed by verify-uvm.pl>'
- uvm-sequence-library / shell-guided / s0: build: uvm_sequence_library.h:521: assigning to 'uvm_object_wrapper *' from 'const uvm_object_wrapper *' discards qualifiers
- uvm-sequence-library / tools-guided / s0: build: uvm_sequence_library.h:519: assigning to 'uvm_object_wrapper *' from 'const uvm_object_wrapper *' discards qualifiers
