# Review: register randomization, register-sequence and CRAVE seeding

Reviewer A: independent reviewer, 2026-11-15.
Reviewed: feature/reg-randomize dabcdf2, feature/reg-seq-seed 1da4029, feature/random-seed 44c1270, feature/crave-seed 87753f7, feature/crave-reg-randomize f79dfbb.
After fixes:
- feature/random-seed 0814dcb
- feature/cmdline-seed 28973d2
- feature/reg-seq-seed 8d343ce
- feature/reg-randomize 7946e8d
- feature/crave-seed 6a32781
- feature/crave-reg-randomize bb5d44f

## Findings (proven by the reviewer's runs) and calls
| # | Sev | Finding | Call |
| --- | --- | --- | --- |
| A1 | medium | Fields with the same full name got order-dependent values | Fixed: state is a hash of seed and name, no seed table; same name gives same values (documented, tested) |
| A2 | medium | block.randomize dropped pending uvm_reg_fifo writes via the now-live post_randomize | Fixed: fifo post_randomize no longer clears the set count |
| A3 | medium | 32-bit seeds collided (22 pairs in 300k fields) | Fixed: 64-bit FNV-1a into the 64-bit state |
| A4 | medium | Register hooks ran in heap-address order | Fixed: branch now includes fix/reg-deterministic-order |
| A5 | low-med | Seed frozen at first randomize | Fixed for a later uvm_set_random_seed (tested); a rename after first use is documented |
| A6 | low | Source/ABI break for subclasses using the names | Noted in the commit message |
| A7 | low | Undefined shift for a field wider than uvm_reg_data_t | Fixed: size bounded |
| A8 | low | Lower-case access policy left a read-only field random | Fixed: compare in upper case (tested) |
| A9 | low | About 190 bytes per field in the seed table | Fixed with A1 |
| B1 | medium | Built-in sequences overwrote a user seed | Fixed: seed only when none is set; has_seed added |
| C1 | low | Weighted arbitration test failed for 5 of 150 seeds | Fixed: weights 100/100/100/500, 100 grants; 300 of 300 seeds pass |
| D1 | medium | CRAVE register example failed its spread check for 2 of 61 seeds | Fixed: limits lowered; 200 of 200 seeds pass |
| D2 | low | Spread limits only detect near-constant output | Accepted, said so in the comment |

Not changed: no rand_mode at register or block level; the built-in shared access
sequences still iterate registers in map order (needs fix/reg-deterministic-order
in the same build); uvm_reg_fifo values are not randomized.

## Proof after fixes
Mac, Debug, C++17, CRAVE on: 81 of 87 pass on feature/crave-reg-randomize; the 6
failures are the known upstream macOS ones. The fixes were not re-reviewed.

## Verdict
Ready for the fork after the combined Linux regression.
