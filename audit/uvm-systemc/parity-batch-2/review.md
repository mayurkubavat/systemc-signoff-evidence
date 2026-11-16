# Parity batch 2: review record (2026-11-15)

Branches: fix/sequencer-killed-requests, feature/uvm-pool, feature/uvm-barrier (on pool),
feature/objection-callbacks, feature/uvm-heartbeat (on objection-callbacks),
feature/uvm-sequence-library.

Reviewer: independent reviewer, read-only, built each tip and ran reproductions
(scratchpad review-parity/exp). Verdict before fixes: objection-callbacks ready, five need changes.

## Findings and what was done

| Branch | Finding | Sev | Action |
| --- | --- | --- | --- |
| sequencer | zombie request left in queue after its sequence was restarted, read after delete | MEDIUM | zombie removed by position (`m_remove_zombie_request`), test restarts the sequence |
| sequencer | request leaked when a waiting sequence is killed | MEDIUM | arbitration queue is the single owner; deleted in `remove_sequence_from_queues`, `m_select_sequence`, grant |
| sequencer | back-to-back lock loop skipped the zombie check | LOW | loop checks, zombie handled in next round |
| pool | double delete when `uvm_object_string_pool` is copy-constructed | HIGH | copy constructor and assignment deleted |
| pool | `clone()` refers to objects it does not own | MEDIUM | documented (same shallow copy as SV) |
| pool | `uvm_pool<KEY,T>` needed `operator<<` for T | MEDIUM | SFINAE print helper, test with a plain struct |
| barrier | `reset(false)` let old waiters pass with new arrivals | MEDIUM | generation counter, old waiters stay waiting as in SV, test added |
| barrier | `do_copy` copied waiter count but not the event | LOW | copy starts with no waiters, documented |
| barrier | `cancel()` took count from the event | (own) | decrements own count |
| objection-callbacks | `UVM_DO_OBJ_CALLBACKS_EXIT_ON` leaked its iterator | INFO | stack iterator |
| heartbeat | destructor after end of simulation threw E572 and terminated | HIGH | kill only while running, destructor catches, test deletes a started heartbeat after `run_test` |
| heartbeat | `stop()` decremented another waiter's count | LOW | `m_waiting` flag, test added |
| heartbeat | umbrella include collided with barrier's at merge | (own) | include moved after uvm_event_callback.h |
| sequence library | default REQ (`uvm_sequence_item`) did not compile | MEDIUM | registration detected at compile time, `SEQLIB/BASE_ITEM` at run time, test added |
| sequence library | test catcher was a local used after `run_phase` | MEDIUM | catcher is a test member |
| sequence library | fixed seed, macro limits, SV differences undocumented | LOW | documented in the class and macro comments |

Not changed (stated in comments or accepted): no factory registration of uvm_pool,
uvm_object_string_pool and uvm_sequence_library_cfg (keeps the factory example golden stable);
a library killed inside `execute` leaks the object it was running; phase-scoped config lookup
of the sequence library is not tested.

## Proof

- Each branch alone on macOS: only the six known failures of upstream main.
- development + the six branches: 103/103 on macOS (clang) after the fixes.
- Reviewer reproductions rerun against the fixed build: zombie_restart no fatal, pool_copy is now
  a compile error, pool_noprint compiles, barrier_reset passes only the three new arrivals,
  hb_dtor exits 0, seqlib_item and seqlib_noreg compile and report SEQLIB/BASE_ITEM.
- The fixes themselves were not sent back for a second independent review.

## Sync note

`feature/uvm-barrier` changes the factory example golden count (22 to 23); on development the
merged value is 34. Resolve once on the partial development so rerere replays it.
