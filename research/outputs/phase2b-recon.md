# Phase-2b recon — spgroup labeled benchmark for per-category FN/recall

**Date:** 2026-07-03. **Verdict: GATE PASS** — a materializable, per-unit-labeled artifact exists.
Plan context: `outputs/p1-detection-validation-plan.md` §7 (the Phase-2b complement); STATUS "Category #3 — honest scope" ("per-category FN rates still await the Phase-2b static-semantic-merge oracle").

## The artifact

**`spgroup/mergedataset`** (Paulo Borba's group, UFPE), pinned at commit
`04a180179b6098bac96a9cd83fe4f5ff5d45ea86` (2024-08-06). License **GPL-3.0**.
~17 MB without jars (blobless + sparse clone at `workspace/phase2b-mergedataset/`; jars excluded — we need only source).

Ground truth: `semantic-conflicts/sample-semantic-conflicts.csv` — **95 rows**, unit =
(merge commit, class, **method/attribute declaration**). Column `Locally Observable
Interference` ∈ {Yes, No, -}: **17 Yes / 74 No / 4 "-"** (unmarked). All rows
`Manually Analyzed = Yes` except the 4 "-". Provenance column `Sample` names the source
study: Roberto (40), DeSouza (33), Leuson (8), Guilherme (14) — these are the ground-truth
sets used across the group's papers (ICSME 2020 behavior-change; SMAT/JSS; OA/SBES 2022;
ICSE-2024-companion lightweight static analysis; the 2025 pointer-analysis and RefFilter
papers cite the same family as "99 scenarios"; our snapshot carries 95 rows / 90 unique files).

**Source materialization is shipped in-repo** — no original-repo cloning needed. Per unit:
`<project>/<merge_sha>/source/<pkg path>/<Class>/{base,left,right,merge}.java`
(plus 21 quadruples under `studies/static-analysis-results/roberto-dataset-without-dependencies/files/`).
`merge.java` is the **developer's merge commit** content (per-scenario READMEs give the
exact topology: merge SHA → parents via `git log --pretty=%P`, base via `git merge-base`;
`semantic-conflicts/results-only.csv` records left/right/base SHAs per scenario).
`changed-methods/<Class>/<decl>/{left-right,right-left}-lines.csv` gives the studies'
changed-line info per declaration.

Join CSV ↔ disk (file level, unique (commit, class), label = any-Yes across rows):

| pool | files | materializable |
|---|---|---|
| positives (Yes) | 17 | **17/17** |
| negatives (No) | 69 | 66 |
| unmarked ("-") | 4 | 4 (excluded from scoring) |

Missing 3 (all negatives): eureka `6b09030e…` ApplicationInfoManager; elasticsearch-river-mongodb
`6b6ce8e8…` MongoDBRiverDefinition.parseSettings; elasticsearch `c1d44780…` IndexRequest.
4 files carry >1 labeled declaration (rows deduplicate to file level for detector scoring;
declaration granularity is kept in the scenario metadata for adjudication).

Bonus: `studies/static-analysis-results/*/data/soot-results.csv` has **their own analyses'
per-unit outputs** (left/right × dataflow, tainted, svfa, confluence) — tool outputs, not
ground truth; usable as shape priors for category mapping and as published-baseline context.
Calibration anchor from the 2025 pointer-analysis paper (arXiv 2507.20081): their
purpose-built OA analysis scores **recall 0.28 / precision 0.47** (noPA) on this dataset —
tempers expectations for any static detector here.

## Definitional gap (pre-registered)

Their label is Horwitz-style **behavioral interference** (test-suite/manual, "locally
observable"), broader than our 7-shape taxonomy (`semantic_merge_driver/ResearchSummary.xml`:
#1 atomic updates, #2 control-flow/short-circuit, #3 data-flow/stale-read, #4 exception
divergence, #5 loop semantics, #6 method rename, #7 scope capture). Spot-check confirms
positives exist outside our taxonomy (e.g. antlr4 `69ff2669…` Python2Target: both parents
append to the same keywords array — closest to #1/OA-shape, not #3). Consequence: per-category
recall requires mapping each of the 17 positives onto {1..7, none}; expect small per-category
n and possibly 0 units in some covered categories — that is itself the honest result
(mirrors the Stage-C base-rate finding).

**Mapping protocol (freeze BEFORE any detector run):** I draft category per positive from
the base/left/right/merge diffs + soot shape hints; Ali adjudicates (§4.6 pattern). Drafts
frozen in `reports_detection/phase2b/category_mapping_draft.md` pre-run; any post-run
revision is labeled as such.

## Pre-registered evaluation design

Detectors at current committed sha, all five (DFI, UnresolvedRef, InfiniteLoop,
InvalidLoopBounds, RM2Rename), driver-faithful invocation via `tools/detect_validate.py`.
**A NEW labeled evaluation — never blended with frozen Stage-C numbers.**

- **Primary arm (oracle-faithful):** detectors on the shipped developer `merge.java`
  (the artifact the labels describe), with base/left/right as differential context.
  New `--merged-source developer` mode: no Mergiraf call; merged = `developer_resolution`.
- **Secondary arm (deployment-faithful):** existing Mergiraf re-merge mode; units whose
  re-merge CONFLICTs leave that arm (a surfaced conflict is not a silent miss) — count reported.
- **Metrics:** per-category recall on positives (Wilson 95% CIs), overall any-detector
  recall on 17 positives, FP/block rate on 66 negatives (complements Stage-C R1 on an
  independent corpus), per-detector breakdown. G1 inject-sanity gate first, unchanged.
- **Scale/cost:** ≤ (17+66) files × ~2 arms + 10 sanity ≈ ~180 detector-file runs ×
  60–90 s/file (Joern-bound, CLI-DEPLOY calibration) ≈ **3–4.5 h on c7i.2xlarge ≈ $1.5–2**
  + provisioning. Resumable cache keyed on DRIVER_COMMIT as before.

## Rejected/parked alternates

- **RefDataset** (`victorlira/ref-dataset`, 907 units) — unlabeled; no recall use.
- **RefFilter 1,087-scenario novel dataset** (arXiv 2510.01960) — recency; per-unit labels
  and packaging unverified; the 99-family is the canonical labeled set every spgroup paper
  shares. Revisit only if the 17-positive CIs prove uselessly wide.
- Re-cloning original repos per `results-only.csv` SHAs — unnecessary (source shipped);
  keep as fallback for the 3 missing negatives if ever needed.
