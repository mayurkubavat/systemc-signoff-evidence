# Review: fix/reg-compare-mismatch-test
Commit reviewed: ba4cbddd9b342bfaff951cd56437fc4445caeb55
Reviewer A: independent reviewer (isolated clone, macOS clang + Linux gcc 15.2).

## Verified
- Golden change is the offset column only (54 lines, 0 others); offsets match add_reg. W505 mechanism reproduced: clang names the signal event_N_0, gcc signal_0.
- Passes on macOS and Linux (fixes the one test that failed on both).

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| R1 | Golden log still depends on heap address order of the registers (fails under a descending/random allocator shim); same on main | low | Noted: follow-up candidate in register code, not part of this change |

## Verdict
Ready.
