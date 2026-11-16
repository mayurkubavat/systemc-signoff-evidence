# Review: fix/cross-bin-names

Reviewer A: independent reviewer, 2026-11-15.
Reviewed 7462ebf; after fixes c8a8298.

No defect found in the change: names unique for a 3-coverpoint cross, equal to
the index list, stable across runs, valid against UCIS.xsd (xmllint), and pyucis
reports and merges per name correctly (8.0% vs the library's 8.33%).

| # | Sev | Finding | Call |
| --- | --- | --- | --- |
| E1 | low | examples/fir/coverage_results_gold.xml still had empty names | Fixed: 9 names added |
| E2 | low | Pre-existing: indices follow crossExpr order, coverpointBin elements are written in reverse declaration order | Noted, follow-up |
| E3 | info | Pre-existing: ucis/UCIS.xsd has a comment before the XML declaration, xmllint rejects it | Noted, follow-up |

Proof: 59 of 59 googletest cases pass on development plus this branch (Mac).
Verdict: ready for the fork.
