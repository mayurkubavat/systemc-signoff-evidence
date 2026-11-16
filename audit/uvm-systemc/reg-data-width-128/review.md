# Review: fix/reg-data-width-128
Commit: c137759bd5d8c1f361a9a72d538ea2ed8e0d34eb
Reviewers: independent reviewer, two independent rounds (macOS clang + Linux gcc 15.2, ASan/UBSan/LSan).

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| 3.1 | Fixes memory backdoor reads at 64 bits too, not stated, no test | low | Acted on: message says so; 20mem_access reads back through the backdoor (fails on main) |
| 3.3 | 20mem_access does not compile at 128 bits | low | Noted: its DUT has 64-bit storage, so it cannot pass at 128 anyway |

## Verdict
Ready.
