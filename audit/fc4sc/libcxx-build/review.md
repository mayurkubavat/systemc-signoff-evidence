# oss-review: fc4sc fix/libcxx-build

- Commit reviewed: 7d082865171be3c58ce04564558551653b72ff57 (a2dc102 + 7d08286 on master 31b9339)
- Reviewer A: independent reviewer, 2026-11-15.
- Intent: make FC4SC compile with clang/libc++ (macOS) without changing behaviour on libstdc++.

## Findings
- INFO: integral_constant<bool, !is_convertible<...>::value> is exactly what libstdc++'s __not_ expands to.
- INFO: IntervalComp const / const-ref change is semantics-neutral.
- MEDIUM (applied): CG_CONS_DECL/DEF default-argument move is source-breaking for users that put defaulted extra
  arguments on CG_CONS_DEF; that form is ill-formed C++. Migration now stated in the commit message and macro docs;
  CG_SCOPED_* aligned.
- No CRITICAL/HIGH. Not verified: GCC/libstdc++ run (local Homebrew g++-14 broken).

## Verdict
Ready for PR.
