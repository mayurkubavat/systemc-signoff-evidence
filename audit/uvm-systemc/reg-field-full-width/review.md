# Review: fix/reg-field-full-width
Commit: 142b260b9bf014d6d96dd2e1f380af2fa9ab7e29
Reviewers: independent reviewer, two independent rounds (macOS clang + Linux gcc 15.2, ASan/UBSan/LSan).

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| 3.2 | Warning truncated the value at 128 bits | low | Acted on: full hex value without leading zeros |

UBSan: shift by 64 reports on main, none on the branch. poke() and uvm_vreg_field paths reviewed, not executed.

## Verdict
Ready.
