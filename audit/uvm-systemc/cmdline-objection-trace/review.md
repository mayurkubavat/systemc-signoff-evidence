# Review: feature/cmdline-objection-trace
Commit reviewed: parent of d35776f76a140f49098d7465f9999eff607ad07c (amended after review to act on the findings below)
Reviewer A: independent reviewer (isolated clone, macOS clang + Linux gcc 15.2).

## Verified
- macOS 72/79 (only the six known failures), Linux 78/79 (only 20compare_mismatch); no existing test output changes; new test 15/15.
- Prefix matching equals SV get_arg_matches; trace_mode(0) still turns it off; cost about 2 us per objection.

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| F1 | Objections created before the command line settings are initialised (static component or objection, uvm_root::get() before sc_elab_and_sim) were not traced | medium-low | Acted on: settings init now turns on tracing for existing objections; test covers an objection created before main |

## Verdict
Ready after F1 fix (applied, regression rerun: only the six known failures).
