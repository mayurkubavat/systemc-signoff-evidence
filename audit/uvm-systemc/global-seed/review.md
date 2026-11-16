# Review: feature/random-seed and feature/cmdline-seed

- Reviewed: feature/random-seed 2cc4074, feature/cmdline-seed 0d6a0f7 (2026-11-15).
- After fixes: feature/random-seed e807d3a, feature/cmdline-seed de608d3.
- Reviewer A: independent reviewer.

## Intent
Random sequencer arbitration never selected the longest-waiting request
(`urandom_range` never returned min) and used `srand(25)`. Give each sequencer
its own seedable generator, add `uvm_create_random_seed` and a global seed, and
a `+UVM_SEED=<n>|random` argument.

## Findings (all proven by the reviewer's runs)
| # | Sev | Finding | Call |
| --- | --- | --- | --- |
| F1 | medium | +UVM_SEED applied in run_test, so components built in sc_main saw seed 1 | Fixed: parsed in `init`; 05seed test covers it |
| F2 | low | Weighted arbitration with priority sum 0 became seed dependent | Fixed: no draw when the sum is 0, same fatal as before |
| F3 | low | ABI: sequencer grows by an mt19937, `uvm::urandom_range` symbol removed | Noted: beta library, users rebuild; say so in a PR |
| F4 | low | +UVM_SEED=1 differed from no argument | Fixed by F1 (seed set before any seed is created) |
| F5 | low | Parser accepted leading space and `+` | Fixed: decimal digits only, 0..4294967295 |
| F6 | low | Merge commit had no sign-off | Fixed: merge redone with --signoff |
| F7 | info | Late `uvm_set_random_seed` does not reseed a sequencer that already drew | Noted, documented behaviour |
| F8 | info | No regression test for SEQ_ARB_WEIGHTED | Noted, follow-up |

Not broken: range edge cases, uniformity (chi-square), identical numbers on
libc++ and libstdc++ (Mac and Linux gcc 15), seed table matches uvm_misc.svh,
autotools/MSVC file lists need no change, legacy verify-uvm.pl finds the tests.

## Unproven
Windows LLP64 parsing (now moot: digits-only parser with unsigned long long);
`std::random_device` on old MinGW; legacy verify-uvm.pl golden comparison on macOS.

## Proof after fixes
Mac, Debug, C++17: 76 of 82 pass on feature/cmdline-seed; the 6 failures are the
known upstream macOS failures (ubus, 10domains 01-04, 20compare_mismatch).
New arbitration test on old code: sequence 0 gets 0 of the first 40 grants (fails);
with the fix 9/13/12/6 (passes). The fixes were not re-reviewed or rerun on Linux.

## Verdict
Ready for the fork after a Linux regression of the fixed commits; mention the ABI change in any PR.
