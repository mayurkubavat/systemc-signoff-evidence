# Review: fix/global-forward-declarations
Commit: 0ae0ff273d160e26869ac73760ab09ef62e57cbf
Reviewers: independent reviewer, two independent rounds (macOS clang + Linux gcc 15.2, ASan/UBSan/LSan).

## Findings
| # | Finding | Severity | Call |
| --- | --- | --- | --- |
| 6.1 | Also fixes uvm_event::add_callback with a uvm::uvm_event_callback | note | Acted on: message says so |
| 6.2 | Code naming ::uvm_object explicitly no longer compiles | low | Acted on: message says so (incomplete types) |

## Verdict
Ready.
