# Review: feature/cmdline-processor

- Commit reviewed: fde2389 (before fixes); fixes folded into 7951a5c
- Reviewer A: independent reviewer (own clone, ASan+UBSan build)

## Intent
Add uvm_cmdline_processor and apply the UVM built-in plusargs (+UVM_TESTNAME,
+UVM_VERBOSITY, +uvm_set_*, +UVM_TIMEOUT, +UVM_MAX_QUIT_COUNT, trace switches).

## Findings and judgment
| # | Finding | Severity | Category | Action |
|---|---|---|---|---|
| 1 | Merged with PR #356 the tree does not compile (m_phase_trace, uvm_factory*, uvm_report_server* in test) | high | Act on (partly) | Factory and report-server pointer types no longer named; `uvm_phase::m_phase_trace` has no spelling valid on both sides, one-line fix needed by whoever lands second |
| 2 | msvc16 project lacks the two new .cpp files | medium | Act on | Added ClCompile/ClInclude entries |
| 3 | Empty/invalid component pattern throws std::regex_error and aborts | medium | Act on | Patterns validated at parse (INVLCMDARGS), matching guarded, empty override fields rejected, get_arg_matches catches |
| 4 | Empty +UVM_TESTNAME runs no test; name matching an existing component segfaults (pre-existing null deref) | medium | Act on | Empty value ignored with INVTST warning; null deref guarded |
| 5 | get_arg_matches regex is a full match (library uvm_re_match uses regex_match) | low | Noted | Documented in header and commit; library-wide behaviour, candidate upstream issue |
| 6 | Any argument shifted uvm_object ids by 2 | low | Act on | Processor only created when a +uvm/-uvm argument is present |
| 7 | Numbers not range-checked (int overflow, nan/inf/hex times, int truncation of config value) | low | Act on | Range checks; decimal-only times; int copy only when it fits |
| 8 | Divergences: overrides also hit the test, no +uvm_set_config_bitstream, +UVM_VERBOSITY=0 | low | Noted / Dismissed | First two documented in commit; =0 matches the 1800.2-2020 reference source (NSTVERB), dismissed |
| 9 | RELEASENOTES still marks X; no tests for default_sequence and trace switches | low | Noted | RELEASENOTES left alone on purpose (PR #356 deletes that table); reviewer ran the untested switches by hand |

## Unproven concerns
Linux/gcc run, autotools build, MSVC build, static libsystemc with a test-defined main():
not run locally. Linux is covered by the weekly sync workflow build.

## Verdict
Ready after the listed fixes (applied in 7951a5c). Regression after fixes:
main 67/74, branch 71/78, same 6 known failures, 4 new tests pass.
