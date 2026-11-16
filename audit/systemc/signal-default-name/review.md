# Review: fix/signal-default-name
Commit reviewed: parent version of ad3d332ca74ab906bf0899850543ae5a0bb70db4 (amended after review to act on finding 1)
Reviewer A: independent reviewer (isolated clone, macOS clang + Linux gcc 15.2).

## Verified
- Baseline (main + simple-cpu fix) 916/916 tests and 35/35 examples; candidate 917/917 and 35/35, macOS clang and Linux gcc.
- New test on main: clang gets all four names wrong (item_0..item_3); gcc gets three wrong (sc_signal<T>() already right there).
- No sibling hazard demonstrated in sc_fifo, tlm_fifo, sc_vector, sc_in/out/inout, sc_export. Value-type matrix (PODs, sc_dt types, enums, pointers, all writer policies, sc_buffer, sc_signal_rv, sc_clock) unchanged. No warnings.
- ABI: six additive constructor symbols for the explicitly instantiated bool/sc_logic bases.

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| 1 | Current and new value were value-initialized separately; write() relies on them being equal, so a first write could be lost for a T whose default-constructed objects differ | medium | Acted on: the new value is now a copy of the current value (one default construction, as on main); the test checks the construction count |

## Unproven
- MSVC not built.

## Verdict
Ready after finding 1 (applied; full regression rerun, see proof.txt).
