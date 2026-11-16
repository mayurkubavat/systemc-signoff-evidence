# Review: fix/component-schedule-lifetime
Commit: 879c015eacc3db0846e6c5a531c143a5d192e990
Reviewers: independent reviewer, two independent rounds (macOS clang + Linux gcc 15.2, ASan/UBSan/LSan).

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| 7.1 | Heap-use-after-free when a parent is deleted before its child | medium | Acted on: children are orphaned; test covers it (ASan fails without) |
| 7.2 | Schedule kept with the domain (same leak profile as main); uvm_component size changes | note | Acted on: message says so |

Second round: 36 lifetime scenarios and 4 in-phase deletions clean under ASan+UBSan on both platforms (main: 29 and 4 abort).

## Verdict
Ready.
