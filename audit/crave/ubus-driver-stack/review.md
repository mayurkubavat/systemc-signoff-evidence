# Review: fix/ubus-driver-stack
Commit reviewed: 0978f92a13c32b601fa3b9571bde2d67f5e4bb9f
Reviewer A: independent reviewer (isolated clone).

## Verified
- main: 8/8 runs exit 138 (SIGBUS). Branch: 8/8 runs exit 0 with UVM TEST PASSED (Release and -O0), macOS arm64.
- sizeof(ubus_transfer) = 55272; default stack 262144; both drivers fail up to 0x40000 and pass from 0x50000, so 1 MB is about 3x margin.
- Process names unique per driver, no W505; SC_FORK/SC_JOIN behaviour unchanged.

## Findings
None proven.

## Unproven / noted
- Not run on Linux. SystemC 2.3.4 API checked by reading, not compiling. The slave driver's unused local rsp is left in place.
- The example has no ctest entry; the run itself is the regression check.

## Verdict
Ready.
