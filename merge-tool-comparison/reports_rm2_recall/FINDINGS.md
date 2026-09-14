# RM2 file-level vs project-level recall delta — the R0-promised n=50 finding

**Generated:** 2026-07-03 via `tools/rm2_tag.py --project-level` (AWS, instance `rm2-recall-delta`) + `tools/rm2_recall_delta.py`. Closes [ISSUES #26](../ISSUES.md).
**Bottom line:** file-level RM2 recall of project-level (same-file filter) is **90.7% [83.8, 94.9]** pooled on the full Schesch n=50 — far better than the n=10 point estimate of 66.7% [39.1, 86.2] that R0 teed up (its sole gap-driver was an outlier that this run reproduces exactly). The miss is **entirely the predicted cross-file Extract/Move family** and is small: **2/50 scenarios change cluster, 1/50 is a false-`NONE`** (the only routing-visible kind post-flip). This is a methodology/limitation-tightening finding, not a routing problem — it *strengthens* the file-level R4a design choice.

## Method

R0 reconnaissance ([rm2-integration-recon.md §5–§6](../../docs/plans/rm2-integration-recon.md)) measured on n=10 that file-level RM2 (what the driver's classifier and detection lane actually see at merge time) recalls 66.7% of project-level same-file refactorings, picked Path D on that basis, and designated the tightened n=50 delta a publishable R2 finding. The R1/R2 cycle deliberately cut it (user-approved); #26 tracked the un-produced number. This run:

- **Extended `tools/rm2_tag.py` with `--project-level`** (opt-in; R1 file-level path untouched): per axis, `git worktree` the clone at the merge-base and the side parent (`merge_commit^1`/`^2`), run RM2 2.4.0 (Docker, `merge-tools/refactoring-miner:2.4.0`) on the two full trees, then **filter to refactorings touching the scenario's `file_path`** — the fharness same-file filter, i.e. the apples-to-apples denominator for "what could R4a have seen in THIS file". Unfiltered sets kept as `refactorings_project_full` for inspection.
- **Ran on AWS** (c7i.2xlarge, native x86_64; CLI-DEPLOY.md pattern, 4th cycle): shipped repo + the 50 scenario JSONs + only the 15 clones they need (604 MB, not the full 2.1 GB `data/repos`); built the RM2 image natively on the instance from the committed Dockerfile (the arm64-image-dies-silently-on-x86 lesson). **Probes before the run:** toy-rename/toy-empty known-answers + exact reproduction of the cached file-level tags on 3 scenarios (the "reproduce the canonical table" validation bar). 50/50 tagged, **0 errors**, 3.8 min wall (~4.7 s/scenario — the R0 "~3× file-level Docker cost" estimate was Rosetta-dominated; native project-level RM2 is ~2 s/call even on full trees).
- **Recall** = file-level detected type-occurrences / project-level same-file type-occurrences (R0's aggregation: sums of per-scenario-axis type-set sizes), Wilson 95% CIs. **Cluster impact** via the comparator's parity-tested `cluster_of` on both tag sets per scenario.

## Result (n=50, 33 active)

| axis | recall (file / proj same-file) | Wilson 95% | only-file types |
|---|--:|---|--:|
| ours | 40/49 = **81.6%** | [68.6, 90.0] | 0 |
| theirs | 58/59 = **98.3%** | [91.0, 99.7] | 0 |
| **pooled** | 98/108 = **90.7%** | **[83.8, 94.9]** | **0** |

All 10 missed occurrences sit in **4 scenarios**; the missed types:

| missed type | occurrences | cross-file by construction? |
|---|--:|---|
| Move Method | 2 | yes |
| Extract Class | 2 | yes |
| Extract And Move Method | 2 | yes |
| Move Attribute | 2 | yes |
| Pull Up Method | 1 | yes |
| Remove Method Annotation | 1 | no — rode along with the Pull Up (annotation left with the method; destination file invisible file-level) |

## The three findings

**1. The n=10 number was an outlier artifact; the true delta is ~9%, not ~33%.**
R0's 66.7% came from 4 effective scenarios, with the entire gap in one (`ab0oo_javaprslib`, 4 cross-file refactorings). This run reproduces that row *exactly* (same 4 missed types) — and shows it is the extreme, not the norm: pooled n=50 recall 90.7% [83.8, 94.9] excludes the old point estimate. Direction confirmed, magnitude corrected. Retrospectively the pooled number lands in R0 §6's **Path B** bracket (≥80% ⇒ "file-level everywhere"), though the ours-axis CI [68.6, 90.0] still straddles the B/D boundary — Path D (dual-mode tagging, file-level at runtime) remains the defensible pick, and this measurement is itself the Path-D deliverable.

**2. File-level detection is a strict subset of project-level (only-file = 0, 108 occurrences).**
No file-level hallucinations: everything file-level RM2 detects, project-level confirms on the same file. The file-level tags R2's cluster pivot and the runtime classifier rely on are *conservative*, never spurious — misses only. And the misses are exactly the R0-predicted mechanism: Extract/Move semantics need the destination file, which single-file staging cannot supply (9 of 10 missed occurrences; the 10th is annotation fallout of a Pull Up).

**3. Cluster/routing impact is marginal — and post-flip, almost invisible.**
2/50 scenarios (4.0% [1.1, 13.5]) classify into a different cluster at project level (`INTRA_BODY→MIGRATE_DECL`, `NONE→MIGRATE_DECL`). Post-flip (`NONE→git, else→Mergiraf`), only the **false-`NONE`** matters: **1/50 = 2.0% [0.4, 10.5]** of merges would route git-merge-file where the ground truth says Mergiraf. Equivalently: of the 18 file-level `NONE` scenarios (36% of Schesch-50), **1/18 = 5.6% [1.0, 25.8]** is "RM2 missed it" rather than "no refactoring" — the conflation THREATS §3 flagged as unmeasured is now measured and small. The `INTRA_BODY→MIGRATE_DECL` flip is routing-neutral post-flip (both route Mergiraf).

## Threats to validity

- **Same-file filter as denominator.** Whole-project recall is far lower (R0's discarded unfiltered measurement was 26.1%) — but that conflates project refactoring volume with what a merge driver handed one file could ever use. The filtered question is the load-bearing one for R4a and the detection lane; `refactorings_project_full` is retained in the scenario JSONs for anyone wanting the other number.
- **Occurrence counting** (R0's aggregation) weights scenarios by their type-set sizes; the 4 miss-carrying scenarios contribute 10 of 108 trials. Scenario-level framing is reported alongside (cluster flips 2/50) and agrees.
- **n=50, one dataset, Java only.** The false-`NONE` rate's CI is wide (1/18 → [1.0, 25.8]); the direction (small) is solid, the point estimate is not precise. Same Schesch-50 external-validity caveats as everything else in this project (THREATS §3).
- **Ours/theirs asymmetry** (81.6% vs 98.3%) is descriptive: the cross-file refactorings in this sample happen to sit on ours-side parents. No mechanism makes ours-sides systematically worse.

## Consequences

- **THREATS §3 routing-coverage threat: quantified.** False-`NONE` ≈ 2% of merges (upper bound ~10%); post-flip stakes = git instead of Mergiraf on those, and P2/P3 measured git as the *conservative* backend (conflicts, not silent errors) — so the blind spot fails safe.
- **Detection-lane cross-file FN story: quantified.** The #6-family lane (RM2-based) inherits the same file-level blindness: ~9% of same-file-visible refactoring evidence is cross-file-only and invisible to it. This bounds the lane's achievable recall on Extract/Move-adjacent conflicts and belongs in the thesis's limitations chapter — it does **not** change the Stage-C R1/R2 numbers (those measure what the shipped file-level lane does; this measures what it cannot see).
- **No code change recommended.** The 90.7% recall + fail-safe blind spot validates file-level R4a at runtime; project-level at runtime would cost ~2 worktree checkouts + full-tree RM2 per merge for ~9% more evidence, almost all of it routing-neutral post-flip.

Artifacts: `summary.txt`, `scenarios.csv`, `raw_results.json`, `run.log` (this dir); project-level tags cached in `data/scenarios/*.json` (`refactorings_project{,_full}` keys, gitignored with the rest of the scenario cache).
