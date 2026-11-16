# Review: fix/phase-schedule-order
Commit reviewed: ae77928221d3feae9361c2af7689454aecadd5c8 (commit message amended after review; code unchanged)
Reviewer A: independent reviewer (isolated clone, macOS clang + Linux gcc 15.2).

## Verified
- macOS: main 68/74, branch 72/74 (fixes exactly the four 10domains tests). Linux: main and branch both fail only 20compare_mismatch; all 10domains tests pass with the new golden logs.
- 19 phasing tests x 200 runs under five macOS allocator settings: 0 failures. Linux heap-shuffling shim: branch gives one output over 40 seeds; main gives two outputs for 05simple_sync and 06simple_unsync.
- Comparator is a strict weak ordering (unique ids, phases not copyable). Golden changes are same-time reorderings only. Warnings unchanged (68).

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| P1 | Commit message said 02reusedom fails on Linux; it passes 25/25 on main there | low | Acted on: message now states what was observed |

## Unproven
- Comparator dereferences keys; no dangling-key path found, ASan not run. Other pointer-keyed maps (objections, register code) untouched.

## Verdict
Ready.
