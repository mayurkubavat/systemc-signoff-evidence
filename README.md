# systemc-signoff-evidence

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24267898.svg)](https://doi.org/10.5281/zenodo.24267898)

Review reports, measurement scripts and data for the report "Proof Before
Push", a sign-off checklist applied to changes in four open SystemC
verification libraries (engrXiv preprint). It holds the evidence behind
Table 1 and RQ1 to RQ3: the independent review reports, the branch manifest,
the measurement scripts and their outputs.

## Contents

| Path | What it is |
| --- | --- |
| `audit/<library>/<topic>/review.md` | Independent review reports, one per review topic (the 30 hand-coded topics). A topic can cover several stacked branches. |
| `audit/outside-snapshot/` | Review reports for work outside the measured set (see Notes). Not counted in any figure. |
| `audit/<library>/<topic>/proof.txt`, `before.txt`, `after.txt` | Recorded test output (fail at base, pass at the change) where the review kept it. Local paths are shortened to `~` or `<workbench>`. |
| `analysis/audit_findings.json` | The review reports hand-coded into topics (branches, fail-then-pass, baseline, rounds) and every high or medium finding with its class and outcome. |
| `analysis/proofbar.py` | Git-only measurement of each branch: tests added, golden-log tests, test and source lines, lizard complexity. Produces `data/proofbar.json`. |
| `analysis/recount.py` | The recount on the 58 pushed branches with rename detection and stubs excluded, own-diff and diff-vs-main views. Produces `data/recount.json`. |
| `analysis/suite_cost.py` | Build and suite timings. Produces `data/suite_cost.json`. |
| `scbench/` | A benchmark of 15 maintenance tasks built from these branches, the verification tool server and harness used to run coding agents on them, and the graded pilot results (see `scbench/README.md`). |
| `data/branches.tsv` | Manifest: library, branch, commit SHA and the branch it is stacked on, for all 58 branches. |
| `data/*.md` | Human-readable versions of the JSON outputs. |

## The branches

The 58 branches are the `fix/*` and `feature/*` branches of these public forks:

- UVM-SystemC (36): https://github.com/mayurkubavat/uvm-systemc
- CRAVE (12): https://github.com/mayurkubavat/crave
- FC4SC (8): https://github.com/mayurkubavat/fc4sc
- SystemC (2): https://github.com/mayurkubavat/systemc

`data/branches.tsv` pins each branch to the commit that was measured, so the
numbers can be reproduced even if a branch moves later.

## Reproducing Table 1

1. Clone each fork into `<workbench>/<library>/src` (library = `uvm-systemc`,
   `crave`, `fc4sc`, `systemc`), with the upstream default branch as `main`
   and the fork as the remote `fork`. Check that `git rev-parse
   refs/remotes/fork/<branch>` matches `data/branches.tsv`.
2. Copy `audit/<library>/` to `<workbench>/<library>/.audit/`.
3. Run, with Python 3.10 or later and [uv](https://docs.astral.sh/uv/):

   ```bash
   PBP_WORKBENCH=<workbench> uv run --with lizard python analysis/recount.py
   uv run --with lizard python analysis/proofbar.py --workbench <workbench> --out data
   ```

   The scripts only read git objects; they do not check out or change any
   branch. `recount.py` writes `runs/proofbar/recount.{json,md}` next to the
   `analysis` folder. Compare it with `data/recount.json`.
4. The review-derived rows of Table 1 (reports, fail-then-pass, baseline,
   sanitizer, findings) come from `analysis/audit_findings.json`, which was
   coded by hand from `audit/`. Check any row against the report it names.

## Notes

- The report parity-batch-3 reviews five branches pushed after the measurement
  snapshot, and later commits on feature/uvm-heartbeat, so it is outside the
  measured set. It is kept in `audit/outside-snapshot/` and is not counted.
- The review reports are published as written, apart from shortened local
  paths.
- Build logs from the review runs are not included; they contain only
  compiler and test output already summarized in the reports.

## License

Apache License 2.0, see `LICENSE`.
