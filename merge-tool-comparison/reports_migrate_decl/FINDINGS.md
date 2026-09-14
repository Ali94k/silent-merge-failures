# MIGRATE_DECL W3 gate — does Weave beat Mergiraf on its own cluster?

**Generated:** 2026-06-01 via `tools/migrate_decl_w3.py` (no commit).
**Bottom line:** **No. The W3/W5 gate fails — decisively and significantly.** Weave wins **0** scenarios over Mergiraf on the cluster it was designed to own. `MIGRATE_DECL → Weave` is contraindicated for `auto` routing, exactly as `INTRA_BODY → Spork` was (ISSUES #27).

## Method

The deferred W3 gate ([weave-integration.md §W5](../docs/plans/weave-integration.md)) requires Weave to *strictly outperform* Mergiraf on MIGRATE_DECL (non-overlapping CIs, or handle cases Mergiraf can't). Prior reports carried only incidental n=19 slices. This run:

- **Pooled all distinct, already-materialized + RM2-tagged MIGRATE_DECL scenarios** across `data/scenarios{,_ci,_expanded,_spork}` → **n=38** (31 repos), recomputed with the comparator's own `cluster_of`. No new cloning.
- Ran git-merge-file / mergiraf / weave through the **real adapters** + the comparator's own `classify_result` (consistent-by-construction with `reports_ci`).
- Classified under **two oracles**: `normalized` (google-java-format + AST, canonical) and `raw` (whitespace).
- Joined the **Schesch test-suite label** for Mergiraf from `result_adjusted.csv` (38/38 join). *No `weave` column exists in the CSV — Weave has no test-suite label; this asymmetry is why the test-oracle cross-tab is Mergiraf-only.*
- Wilson 95% CIs + a **paired McNemar exact** test on clean-correct outcomes.

## Result — normalized oracle (n=38)

| tool | TP | FP | TN(conflict) | precision (Wilson95) | clean-correct rate | mean_rt_s |
|---|--:|--:|--:|---|---|--:|
| git-merge-file | 12 | 0 | 26 | 1.000 [0.757, 1.000] | 0.316 | 0.02 |
| **mergiraf** | **19** | 7 | 12 | 0.731 [0.539, 0.863] | **0.500** | 0.42 |
| weave | 11 | 0 | 27 | 1.000 [0.741, 1.000] | 0.289 | 0.32 |

## The two decisive findings

**1. Weave wins zero scenarios over Mergiraf (paired, significant).**

| paired clean-correct (normalized) | n |
|---|--:|
| both correct | 11 |
| Mergiraf only correct | **8** |
| **Weave only correct (the W3 win cell)** | **0** |
| neither | 19 |

McNemar exact **p = 0.0078** — Mergiraf strictly dominates. The Mergiraf×Weave cross-tab shows Weave's correct merges are a **strict subset** of Mergiraf's (11 ⊂ 19), and on **all 7** scenarios where Mergiraf's output is dev-mismatched, Weave **abstains** (conflict) rather than producing a correct merge. Weave resolved nothing Mergiraf couldn't; it only declined more (TN 27/38 = **71% abstention**). The W5 premise — "Weave's entity-level matching handles MIGRATE_DECL extractions Mergiraf can't" — is **refuted on this dataset**.

**2. MIGRATE_DECL is *not* a Mergiraf weakness under the test-suite oracle — the "opening" was a comparator artifact.**

Mergiraf dev-class × Schesch test-suite label:

| Mergiraf dev-class | Tests_passed | Tests_failed | Merge_failed |
|---|--:|--:|--:|
| TP (dev-match, 19) | 17 | 1 | 1 |
| **FP (dev-mismatch, 7)** | **5** | **0** | 2 |
| TN (conflict, 12) | 5 | 2 | 5 |

Of Mergiraf's 7 dev-match "FPs", **zero fail the test suite**: 5 **pass** tests (valid-alternative merges ≠ dev's choice — pure comparator-gap), 2 are whole-merge `Merge_failed` (a different file in the merge; single-file granularity artifact). So Mergiraf's apparent MIGRATE_DECL precision (0.54 in the old incidental slice, 0.73 here) **massively understates** its real accuracy: by the test oracle it has **no confirmed silent errors** on this cluster. The weakness that motivated a Weave specialist evaporates once you use tests instead of exact-dev-match — exactly the [TASK.md gotcha](../../research/TASK.md).

## Secondary observations

- **Weave has no silent errors in this sample, but is *only* conservative.** Its 2 raw-oracle FPs both normalize to TP (formatting differences gjf folds away) — the known field-declaration-loss bug did **not** trigger on these 38. Weave's weakness here is pure over-abstention, not wrong merges. That is *safe* but useless for routing: a backend that punts 71% of its own cluster to a human, and is a strict subset of Mergiraf on the rest, adds nothing over "route to Mergiraf."
- **No speed case.** Weave 0.32s vs Mergiraf 0.42s mean is (a) QEMU-bound, not the native comparison, and (b) Weave is "fast" largely by abstaining. The success bar needs faster *at equal quality*; quality is strictly worse.
- **git-merge-file edges Weave** (12 vs 11 clean-correct, both 0 FP) — Weave doesn't even beat line-merge on MIGRATE_DECL.

## Threats to validity

- **Single-file scenario vs whole-merge test label.** The Schesch test label reflects the whole merge; several discordant scenarios touch many files (`nfiles` up to 283). This only affects the *test-oracle calibration* (finding 2). The **core verdict (finding 1, Weave wins 0)** rests on the exact per-file dev-match oracle and is independent of the test-label proxy.
- **n = 38**, one cluster. CIs are wide (Weave precision [0.74, 1.0]); but the *paired* test is significant because the discordance is 8:0.
- These 38 are positively RM2-tagged MIGRATE_DECL, so cluster-assignment recall is not a confound here (it would only add *more* MIGRATE_DECL cases elsewhere, not change these).

## Recommendation

Drop `MIGRATE_DECL → Weave` from `auto`, mirroring the Spork decision (ISSUES #27). Keep Weave **selectable** (`SEMANTIC_MERGE_BACKEND=weave`) and as a **comparator baseline**. The honest `auto` routing now collapses to:

```
NONE          → git-merge-file   (speed/simplicity; decided)
everything else → Mergiraf        (dominates every measured cluster)
```

Both hypothesized specialist arms — Spork (INTRA_BODY) and Weave (MIGRATE_DECL) — are now empirically refuted. This **corroborates and extends** the post-Spork recon null result ([post-spork-tool-gap-recon.md](../../research/outputs/post-spork-tool-gap-recon.md)): not only does no *new* tool beat Mergiraf, the one *integrated* specialist arm doesn't either. The driver's routing contribution reduces to the `NONE → git` fast-path; the thesis story should be reframed around that honestly (Mergiraf-only-plus-fast-path is the defensible design), not around multi-arm quality routing.

Artifacts: `summary.txt`, `scenarios.csv`, `raw_results.json` (this dir).
