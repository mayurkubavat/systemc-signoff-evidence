# Review: feature/reg-built-in-sequences

- Commit reviewed: 6f2e726 (before fixes); after fixes a895010 (3 commits)
- Reviewer A: independent reviewer (own clone, ASan+UBSan build, own register models)

## Findings and judgment
| # | Finding | Severity | Category | Action |
|---|---|---|---|---|
| F1 | uvm_reg_access_seq errors on a register with a WO field; root cause uvm_reg::do_check substr(0,1) | medium | Act on | Fixed in its own commit 2009e58; bench now has a register with a WO field |
| F2 | Test bench does not compile once PR #356 is merged (handle API); sequence headers do | low | Noted | Unavoidable until #356 lands; whoever lands second ports the bench |
| F3 | More SV differences than the commit listed | low | Act on | Listed in the commit message |
| F4 | set_seed not reachable through the wrapper sequences; all generators share the default stream | low | Consider | Left; a factory override of the single sequence can set a seed |
| F5 | msvc16 project lacks the new headers | low | Act on | Added |
| F6 | Coverage gaps (RO/WO memories, sub-blocks, size-1 memory...) | low | Noted | Reviewer ran these by hand with 0 errors |

## Library defects found, not fixed here
- uvm_reg_field.cpp:524 shift by 64 on a 64-bit field (spurious warnings)
- uvm_reg_map.cpp:2195 division by zero in lock_model for a memory of size 1
- UVM_REG_DATA_WIDTH=128 does not build on main

## Verdict
Ready after the listed fixes (applied). main 67/74, branch 69/76, same 6 known failures, 2 new tests pass.
