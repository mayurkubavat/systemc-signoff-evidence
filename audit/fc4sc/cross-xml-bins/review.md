# Review: fix/cross-xml-bins (capped design)
Commit: 691ae519c466d6eaa79a964cbf5faf4e047306ce
Reviewer: independent reviewer (follow-up round).

| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| F1 | Save was O(cross product) even with the cap (65536x65536: 21.8 s) | medium | Acted on: enumeration stops at the cap, remaining hits from the map (0.056 s) |
| F2 | FC4SC_SAVE_ALL_CROSS_BINS changes inline code; mixing TUs undocumented | low | Acted on: documented in the option comment and commit |
| F3 | Unused-variable warning with the define | low | Acted on: 0 warnings in both modes |
| - | Covergroup-level cross_num_print_missing not used as default | info | Noted in the commit message |

58/58 capped and uncapped (macOS, Linux); all test XML validates. Verdict: ready.
