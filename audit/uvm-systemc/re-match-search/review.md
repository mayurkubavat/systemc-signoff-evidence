# Review: fix/re-match-search
Commit: 36483c08d50ddcc32a47e4c52e226f4f7c126875
Reviewers: independent reviewer, two independent rounds (macOS clang + Linux gcc 15.2, ASan/UBSan/LSan).

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| 1.1 | wait_modified not woken by set(cntxt, relative inst) | medium/high | Acted on: waiters match the full path |
| 1.2 | Empty glob matched every scope on libstdc++ | medium | Acted on: empty glob is /^$/ as in UVM-SV |
| 1.3 | Message overclaimed unchanged glob matching ('|' globs) | low | Acted on |
| 1.4 | development get_arg_matches('/regex/') doc says 'has to match' | low | Noted: follow-up on feature/cmdline-processor |
| R1 | Test did not detect a revert of 1.2 on libstdc++ | medium | Acted on: get_by_name checks; revert now fails on macOS and Linux |
| R2 | Waiter on uvm_top not woken by set(nullptr, '') | low | Acted on: wait_modified builds the name like set() |
| - | Explicit '//' still throws on libc++ | info | Noted, pre-existing |

## Verdict
Ready.
