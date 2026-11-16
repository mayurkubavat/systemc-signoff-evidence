# Review: feature/tlm-fifos-comparators

- Commit reviewed: 042c891 (before fixes); after fixes 0164557
- Reviewer A: independent reviewer (own clone, ASan+UBSan, 22 mutations, merge with PR #356 built and passed)

| # | Finding | Severity | Category | Action |
|---|---|---|---|---|
| 1 | flush() required a default-constructible T | medium/low | Act on | flush drains with nb_can_get/get |
| 2 | FIFO cannot be created outside a module (sc_export) | low | Act on (doc) | Documented in header and commit |
| 3 | No (int) constructor, so not usable as REQ_CHANNEL of uvm_tlm_req_rsp_channel | low | Act on | Added constructor with generated name |
| 4 | flush leaves same-delta puts | low | Act on (doc) | Documented |
| 5 | clone()/create() on pairs returned null | low | Act on | create() overridden in both pair classes, tested |
| 6 | Six test mutations survived (non-blocking ap writes, get(T&)/peek(T&), pair compare/copy) | medium | Act on | Tests extended for all six |

Unproven: MSVC, autotools, gcc link/run. Verdict: ready after fixes (applied).
main 67/74, branch 70/77, same 6 known failures, 3 new tests pass.
