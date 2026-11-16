# Review: feature/reg-backdoor-access
Commit reviewed: first version of the top commit; current 95f2f76248ade6664c6b2c4fdd1bd3b4ace56fe5 is amended after the review
Reviewer A: independent reviewer (isolated clone, macOS clang + Linux gcc 15.2).

## Verified
- macOS: parent 71/76, branch 72/77 (five known failures); Linux: parent 76/76, branch 77/77. Only 20compare_mismatch and the new test differ.
- kind (RTL/GATES), regfile and block hierarchy, field peek/poke, access policies on backdoor write/read, mirror with check, update, user uvm_reg_backdoor precedence, missing object, sc_vector and bit-select paths all behave as the SV reference.
- 20compare_mismatch reports exactly one UVM_ERROR, from the mirror check, on both platforms.

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| 1 | uvm_reg_mem_hdl_paths_seq read register paths with uvm_hdl_data_t, rejecting objects the backdoor accepts | medium | Acted on: the sequence reads with uvm_reg_data_t; the test runs it |
| 2 | A slice beyond the register width aborted the simulation (sc_uint index out of bounds) | low | Acted on: such a slice is reported and gives UVM_NOT_OK; test added |
| 3 | Commit message described the empty-path case inaccurately | low | Acted on: message reworded |
| - | Stale comments in the 20compare_mismatch test about the DUT value | nit | Acted on |

## Noted (pre-existing in uvm_hdl.h, not changed)
- The design object must have exactly the type uvm_reg_data_t; another T gives a misleading "not of type uvm_sc_if or sc_signal" error.
- sc_signal targets update one delta after a backdoor write; uvm_sc_if objects are immediate.

## Verdict
Ready after findings 1 to 3 (applied; regression rerun).
