# Review: fix/ubus-portable-readback
Commit reviewed: db68776eeb2b11a0869ad961189ba6414b8a8bea
Reviewer A: independent reviewer (isolated clone, macOS clang + Linux gcc 15.2).

## Verified
- rng() >> 24 equals libstdc++ uniform_int_distribution<int>(0,255) over 20,000,000 draws (gcc 15); libc++ differs in 19,921,658.
- macOS: fixes only ubus (69/74). Linux: ubus still passes. Both copies of the header identical.

## Findings
None.

## Unproven
- libstdc++ older than about gcc 11 not run.

## Verdict
Ready.
