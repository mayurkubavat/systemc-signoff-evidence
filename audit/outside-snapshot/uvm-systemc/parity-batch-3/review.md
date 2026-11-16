# Parity batch 3: review record (2026-11-15)

Branches: fix/sequencer-rsp-export, feature/push-driver-sequencer (on it), feature/hdl-polling,
feature/reg-transaction-order-policy, feature/transaction-recording, plus follow-up commits on the
published feature/uvm-heartbeat (run flag; self-stop).

Reviewer: independent reviewer, built every tip on the Linux box, probes in
scratchpad rv/. Verdict before fixes: four ready, recording and polling need changes.

| Branch | Finding | Sev | Action |
| --- | --- | --- | --- |
| recording | uvm_root m_comp_parent uninitialised, new config lookup reads it (segfault under MALLOC_PERTURB_/ASAN) | HIGH | initialised in the init list; perturbed hello_world and ASAN probes clean |
| recording | recorders held by raw pointer after their stream was freed (3 UAF cases) | MEDIUM | components and transactions keep handles; ASAN probes clean; test cases added |
| recording | std::endl per line (27 us/transaction at UVM_FULL) | MEDIUM/LOW | '\n', flush on close, delete and at exit |
| recording | freed streams kept until db deleted | LOW | documented |
| recording | API changes | LOW | listed in the commit message |
| recording | do_record differences | LOW | commented |
| polling | any sc_interface accepted, reads then fail | MEDIUM | signal type checked at create_probe, path resolved as uvm_hdl_read |
| polling | poller dies with a killed sequence | MEDIUM | restarted when used (m_ensure_monitor); test added |
| polling, heartbeat | self-delete/self-stop kill swallowed (F539) | LOW | current process not killed; run flag checked at loop top |
| push | missing connection check, select difference | LOW | commented |
| order policy | per-value ordering; unknown address goes to byte 0 | LOW | commented; error reported, data not used |
| rsp_export | heap copy leaks when not queued | LOW | not changed (same as put_response) |

Not changed: start_item still has begin_child_tr commented out (items are not recorded, as before);
no begin_tr event; two config lookups per component retain queue objects (as in the resource pool).

Proof: each branch on Linux shows only the known 20compare_mismatch; development + all six = 115
pass on Linux except the factory example count, which is set at sync. Mac run pending (benchmark).
The fixes were not sent back for a second review.
