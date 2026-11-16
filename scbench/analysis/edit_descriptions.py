"""One-off: apply the agent-edited task descriptions (pilot, 2026-11-15) and
write results/baseline-model-c/descriptions.md with the before/after text for review."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks" / "pilot.json"

# id -> (new description, note). Tasks not listed keep their text.
EDITS = {
"uvm-systemc:component-schedule-lifetime": (None,
 "No sentence states the fix; unchanged (the root-cause sentences are diagnosis and were kept)."),
"uvm-systemc:config-db-exists": (None, "No sentence states the fix; unchanged."),
"uvm-systemc:reg-deterministic-order": (None,
 "No sentence states the fix; unchanged (the title states the required order, not the change)."),
"systemc:signal-default-name": (None, "No sentence states the fix; unchanged."),

"uvm-systemc:global-forward-declarations": ("""\
Unqualified uvm class names are ambiguous at global scope after using namespace uvm

uvm_event.h and three data access policy headers declared uvm_object, uvm_printer and uvm_event_callback at global scope, in addition to the classes of namespace uvm. After using namespace uvm, unqualified uses of these names at global scope were ambiguous and did not compile. uvm_event::add_callback() and delete_callback() were even declared with the global uvm_event_callback, so user code could not call them with a uvm::uvm_event_callback.

Required: after #include <uvm> and using namespace uvm, global-scope declarations such as
  uvm_object* p;  uvm_printer* q;  uvm_event_callback* r;
compile, and uvm_event::add_callback() and delete_callback() take a uvm::uvm_event_callback*.""",
 "Title stated the fix (move the declarations into namespace uvm); reworded as the symptom. Added the global-scope uses the hidden test compiles."),

"uvm-systemc:hdl-type-mismatch-message": ("""\
uvm_hdl: explain why an object in the design cannot be accessed

uvm_hdl_read() and uvm_hdl_deposit() find the object by name and then need a uvm_sc_if<T> or an sc_signal<T, SC_MANY_WRITERS> with exactly the value type T of the access. When the object had another value type, they reported that it was "not of type uvm_sc_if or sc_signal", which is wrong for a uvm_sc_if of another type and does not say which type is needed. The errors of uvm_hdl_read() also used the id HDL_DEPOSIT.

Required message, as UVM_ERROR with id HDL_READ from uvm_hdl_read() and HDL_DEPOSIT from uvm_hdl_deposit(), where <path> is the object's name, <kind> its kind() and <N> the number of bits of T:
  Object <path> (<kind>) cannot be accessed: it is not a uvm_sc_if<T> or an sc_signal<T, SC_MANY_WRITERS>, or an sc_vector of them, with exactly the value type T of the access, a type of <N> bits (register and memory backdoor accesses use uvm_reg_data_t).
All errors of uvm_hdl_read() use the id HDL_READ.""",
 "No fix sentence. Added the exact message text and ids: the hidden golden log compares it verbatim, so the task was not passable without it."),

"uvm-systemc:re-match-search": ("""\
uvm_re_match: search the regular expression in the string

uvm_re_match() only matched when the expression covered the whole string, unlike the UVM reference implementation and the fallback for compilers without <regex>. A configuration setting for the scope "/env/" was therefore not found in "test.env.agent". Globs must still match whole names.

Related problems in the same lookups:
- uvm_config_db<T>::wait_modified() was woken by settings for other instances, and was not woken by a setting for its own instance when that setting was made relative to a context, e.g. set(this, "a", "speed", 1) for a waiter wait_modified(a, "", "speed"), or by set(nullptr, "", "level", 1) for a waiter wait_modified(nullptr, "", "level").
- A resource set with an empty scope (uvm_resource_db<T>::set("", name, value)) was found in every scope; it should be found only for the empty name.""",
 "Removed the sentence on how globs are anchored after the change and the regexec() wording that named the fix. Added the wait_modified() and empty-scope symptoms the hidden test checks but the commit text did not mention."),

"uvm-systemc:reg-map-internal-names": ("""\
uvm_reg_map: the library registers a factory type named "reg_rw"

uvm_reg_map.cpp defined a sequence item class reg_rw and registered it with the factory under the name "reg_rw". This is the name of the bus item in the register examples and in many user environments, so the factory reported that the name was registered twice and created the library class when such a user class was requested by name.""",
 "Title stated the fix (remove the class) and 'used nowhere' pointed at it; reworded as the symptom."),

"uvm-systemc:reg-map-small-memory": ("""\
uvm_reg_map: wrong address stride and crash when a memory offset changes

The address interval between the locations of a memory was computed by dividing by the number of locations minus one, which is a division by zero for a memory with one location. When a memory was moved with uvm_mem::set_offset(), the interval was computed from the wrong pair of addresses, and the loop removing the old address range erased map elements while iterating over them, which crashed.

Required: a memory with one location gets the stride it would have with two locations.""",
 "Title said 'fix the address stride ...'; reworded as the symptom. Added the expected stride for a one-location memory, which the golden log checks."),

"uvm-systemc:resource-pool-spell-check": ("""\
uvm_resource_pool: implement spell_check()

uvm_resource_pool::spell_check() was a stub that always returned false. lookup_name() calls it whenever rpterr is set, so every by-name lookup with error reporting enabled returned an empty queue. This made uvm_resource_db<T>::read_by_name() and get_by_name() with the default rpterr=true fail even for resources that exist.

Required behaviour, as uvm_spell_chkr in UVM-SV: spell_check(s) returns true when a resource named s exists. Otherwise it returns false and reports UVM_INFO with id UVM/CONFIGDB/SPELLCHK and verbosity UVM_NONE, with the text
  <s> not located, did you mean <name1>|<name2>
listing the existing names at the smallest edit distance from s in table order, or "<s> not located, no alternatives to suggest" when there are none.""",
 "No fix sentence. Added the report id, verbosity and text: the hidden golden log compares them verbatim."),

"uvm-systemc:sequencer-killed-requests": ("""\
seq: requests of killed processes stay in the sequencer

A process which waits for a lock, a grab or a grant on a sequencer and is killed left its request in the arbitration queue. For a grant, the request was owned by the killed process and freed with it, so the sequencer read freed memory at the next arbitration. For a lock, the lock was granted to nobody and the sequencer stayed blocked.

Required, as in the UVM reference implementation: such a request is reported as UVM_ERROR, id SEQLCKZMB for a lock or grab and SEQREQZMB for a grant, with the text
  The task responsible for requesting a <lock|wait_for_grant> on sequencer '<sequencer>' for sequence '<sequence>' has been killed, to avoid a deadlock the sequence will be removed from the arbitration queues.
and the sequencer keeps serving the other sequences.""",
 "Title stated the fix (drop the requests); reworded as the symptom. Added the report ids and text, which the golden log compares (the base source has them, with a leading space in the SEQREQZMB text)."),

"uvm-systemc:uvm-pool": ("""\
conf: add uvm_pool and make uvm_object_string_pool usable

uvm_pool, the associative array as an object, was missing, and uvm_object_string_pool could not be instantiated: it derived from std::map and used a member which did not exist.

Required public API (namespace uvm, available through #include <uvm>), following UVM 1.2:
- template <typename KEY = int, typename T = int> class uvm_pool : public uvm_object
    explicit uvm_pool(const std::string& name = "");
    static uvm_pool* get_global_pool();  static T get_global(const KEY& key);
    T get(const KEY& key);  // adds a default T when the key is missing
    void add(const KEY& key, const T& item);
    int num() const;  void do_delete(const KEY& key);  bool exists(const KEY& key) const;
    bool first(KEY& key) const;  bool last(KEY& key) const;
    bool next(KEY& key) const;   bool prev(KEY& key) const;
  copy(), print() and sprint() work. T need not have an operator<<; such a value prints as <value>.
- template <typename T> class uvm_object_string_pool : public uvm_pool<std::string, T*>
    explicit uvm_object_string_pool(const std::string& name = "");
    static uvm_object_string_pool* get_global_pool();  static T* get_global(const std::string& key);
    T* get(const std::string& key);  // creates a T named key when missing
    void do_delete(const std::string& key);
- typedef uvm_object_string_pool<uvm_event> uvm_event_pool;
Warnings (id POOLDEL), their texts and the print format follow the UVM 1.2 reference.""",
 "No fix sentence. Added the public API of the hidden test (it does not compile at base), names and signatures only."),

"uvm-systemc:uvm-heartbeat": ("""\
base: add uvm_heartbeat

uvm_heartbeat watches a set of components through an objection: each of them has to raise or drop the objection between two triggers of the heartbeat event, and HBFAIL is reported when the activity does not fit the mode UVM_ALL_ACTIVE, UVM_ANY_ACTIVE or UVM_ONE_ACTIVE. It follows the UVM reference implementation.

Required public API (namespace uvm, available through #include <uvm>):
  enum uvm_heartbeat_modes { UVM_ALL_ACTIVE, UVM_ONE_ACTIVE, UVM_ANY_ACTIVE, UVM_NO_HB_MODE };
  class uvm_heartbeat : public uvm_object
    uvm_heartbeat(const std::string& name, uvm_component* cntxt, uvm_objection* objection = nullptr);
    virtual ~uvm_heartbeat();
    uvm_heartbeat_modes set_mode(uvm_heartbeat_modes mode = UVM_NO_HB_MODE);  // returns the mode
    void set_heartbeat(uvm_event* e, const std::vector<uvm_component*>& comps);
    void add(uvm_component* comp);
    void remove(uvm_component* comp);
    void start(uvm_event* e = nullptr);
    void stop();
The reports (HBFAIL, NOEVNT, ILHBVNT) and their texts follow the UVM 1.2 reference. stop() leaves other processes waiting on the same event alone, and a heartbeat can be deleted after the simulation, also while started.""",
 "Removed 'uses the objection callbacks' (names the mechanism). Added the public API of the hidden test (it does not compile at base) and the stop/delete behaviour it checks."),

"uvm-systemc:uvm-sequence-library": ("""\
seq: add uvm_sequence_library

Required public API (namespace uvm, available through #include <uvm>), following UVM 1.2:
  enum uvm_sequence_lib_mode { UVM_SEQ_LIB_RAND, UVM_SEQ_LIB_RANDC, UVM_SEQ_LIB_ITEM, UVM_SEQ_LIB_USER };
  class uvm_sequence_library_cfg : public uvm_object
    explicit uvm_sequence_library_cfg(const std::string& name = "", uvm_sequence_lib_mode mode = UVM_SEQ_LIB_RAND,
                                      unsigned int min = 1, unsigned int max = 10);
    uvm_sequence_lib_mode selection_mode;  unsigned int min_random_count, max_random_count;
  template <typename REQ = uvm_sequence_item, typename RSP = REQ>
  class uvm_sequence_library : public uvm_sequence<REQ,RSP>
    explicit uvm_sequence_library(const std::string& name = "");
    uvm_sequence_lib_mode selection_mode;   // default UVM_SEQ_LIB_RAND
    unsigned int min_random_count, max_random_count;  // default 10 each
    unsigned int sequence_count;
    virtual unsigned int select_sequence(unsigned int max);
    static void add_typewide_sequence(uvm_object_wrapper* seq_type);
    static void add_typewide_sequences(const std::vector<uvm_object_wrapper*>& seq_types);
    void add_sequence(uvm_object_wrapper* seq_type);
    virtual void add_sequences(const std::vector<uvm_object_wrapper*>& seq_types);
    virtual void remove_sequence(uvm_object_wrapper* seq_type);
    virtual void get_sequences(std::vector<uvm_object_wrapper*>& seq_types);
    virtual uvm_object_wrapper* get_sequence(unsigned int idx);
    void init_sequence_library();
   protected:
    unsigned int sequences_executed;
    std::map<std::string, int> seqs_distrib;
  Macros UVM_SEQUENCE_LIBRARY_UTILS(TYPE) and UVM_ADD_TO_SEQ_LIB(TYPE, LIBTYPE).
The library reads "default_sequence.config" (a uvm_sequence_library_cfg*), "default_sequence.selection_mode", "default_sequence.min_random_count" and "default_sequence.max_random_count" from uvm_config_db in the scope of its sequencer. Reports (SEQLIB/...), their texts and the print format follow the UVM 1.2 reference.""",
 "Description was the title only. Added the public API of the hidden test (it does not compile at base). Caveat: the golden log prints the random order of the executed sequences and their counts, which depend on the gold random generator, so an independent correct implementation may still fail the golden comparison."),

"uvm-systemc:objection-callbacks": ("""\
phasing: add uvm_objection_callback

Callbacks could not be attached to an objection: the class uvm_objection_callback and the callback type uvm_objection_cbs_t were missing, and uvm_objection did not call any callbacks.

Required public API (namespace uvm, available through #include <uvm>), following UVM 1.2:
  class uvm_objection_callback : public uvm_callback
    explicit uvm_objection_callback(const std::string& name = "uvm_objection_callback");
    virtual void raised(uvm_objection* objection, uvm_object* obj, uvm_object* source_obj,
                        const std::string& description, int count);
    virtual void dropped(uvm_objection* objection, uvm_object* obj, uvm_object* source_obj,
                         const std::string& description, int count);
    virtual void all_dropped(uvm_objection* objection, uvm_object* obj, uvm_object* source_obj,
                             const std::string& description, int count);
  typedef uvm_callbacks<uvm_objection, uvm_objection_callback> uvm_objection_cbs_t;
uvm_objection_cbs_t::add(nullptr, cb) attaches a callback to every objection, add(&objection, cb) to one; do_delete() and callback_mode(0) stop it. The callbacks are called with the same arguments and in the same places (each level of the hierarchy) as in the UVM 1.2 reference.""",
 "No fix sentence. Added the public API of the hidden test (it does not compile at base)."),
}


def main() -> None:
    tasks = json.loads(TASKS.read_text())
    md = ["# Pilot task descriptions: agent edits for review", "",
          "Edited 2026-11-15. Rule: remove sentences that state how to fix; for the five tasks whose "
          "hidden test does not compile at base, add the public API it uses (names and signatures). "
          "Where the hidden golden log compares library message text verbatim, the required text was "
          "added too, since otherwise no correct fix can pass. All tasks keep "
          "`description_reviewed: false`.", ""]
    for t in tasks:
        new, note = EDITS[t["id"]]
        before = t.get("description_original", t["description"])
        t["description_original"] = before
        if new is not None:
            t["description"] = new
        t["description_reviewed"] = False
        t["description_edited"] = "agent"
        t["description_note"] = note
        md += [f"## {t['id']}", "", f"**Note:** {note}", ""]
        if new is None:
            md += ["Unchanged:", "", "```text", before, "```", ""]
        else:
            md += ["Before:", "", "```text", before, "```", "", "After:", "", "```text", new, "```", ""]
    TASKS.write_text(json.dumps(tasks, indent=2) + "\n")
    out = ROOT / "runs" / "pilot" / "descriptions.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md))
    print(f"edited {sum(1 for v in EDITS.values() if v[0])} of {len(tasks)}; wrote {out}")


if __name__ == "__main__":
    main()
