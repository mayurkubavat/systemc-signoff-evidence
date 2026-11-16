# Review: fix/reg-deterministic-order
Commit reviewed: first version (comparator dereferencing keys); current d7af0781dc5411bd0c17353331accf11b7cb53a8 is the rework after the review
Reviewer A: independent reviewer (isolated clone, macOS clang + Linux gcc 15.2, ASan+UBSan).

## Verified
- New test fails on main (reverse order) and passes on the branch, macOS and Linux. No existing golden log changes (74 common tests identical).
- examples/simple/registers/models/aliasing fails on main under a descending/shuffled allocator and passes on the branch.
- No new warnings; UVM_REG_DATA_WIDTH=128 errors are pre-existing and identical.

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| 1 | Comparator dereferenced keys of deleted objects: four deletion scenarios that ran on main crashed or reported heap-use-after-free | high | Acted on: maps are now keyed by uvm_reg_inst_key, which stores the instance id, so comparing never touches the object; ~uvm_reg_block removes itself from the root list. All five reviewer scenarios (including one that crashes on main) run clean in plain and ASan+UBSan builds |
| 2 | uvm_reg_map::m_mems_by_offset (keyed by address range struct) still address ordered; only affects the order of overlap warnings | low | Noted: stated in the commit message |

## Verdict
Ready after finding 1 (applied; regression rerun: only the six known macOS failures).
