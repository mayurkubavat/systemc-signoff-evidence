# Review: fix/reg-map-small-memory
Commit: 302a443cdbb773a4d7ce349b08443f7d81d70f3f
Reviewers: independent reviewer, two independent rounds (macOS clang + Linux gcc 15.2, ASan/UBSan/LSan).

## Findings
None. 19 bus/endianness/addressing configurations, set_offset/unmap/remap: 57/57 identical to a model built at the target offset.

## Verdict
Ready.
