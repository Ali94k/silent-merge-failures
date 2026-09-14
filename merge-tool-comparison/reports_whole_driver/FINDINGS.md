# P2/P3 — Whole-Driver End-to-End Evaluation (FINDINGS, v2)

**v2 (2026-07-03).** Supersedes v1 (git history, commit `26b8c02`): v1's cost
tables were scored in a **degraded normalization environment** — the
google-java-format image shipped to the P2 AWS instance was built arm64 on
Apple Silicon (the one image whose Dockerfile lacks `--platform linux/amd64`),
so every gjf call died with `exec format error`, silently collapsing
`contents_match` to whitespace-only for divergent outputs (tier 3 consumes
tier 2's output, so both died). v1 §7(a)'s "gjf timeout under local emulation"
mechanism was wrong — **local was the fully-normalized environment; AWS was
degraded**. The image was rebuilt natively on the instance (2026-07-02), the
repaired environment was validated by reproducing the committed canonical
six-tool numbers exactly (Spork 32/11 — the all-21-transforms acid test), and
**all tables below are scored in that repaired environment** — which agrees
with local full normalization (single canonical scoring at last).
Merge/detector *outcomes* were never affected (they don't use `contents_match`);
only TP/FP/TN/FN labels on divergent outputs shifted. The Stage-C cross-check
matched in every environment (detector-based).

**Runs:** pre-flip P2 @ driver `843e5f5` (2026-06-25/26) + post-flip P3 re-run
@ `9e25b4e` (2026-07-02/03), both AWS `c7i.2xlarge` (native x86_64; deployment
records `deploy/aws/CLI-DEPLOY.md`).
**Corpus:** 164 scored positives (Mergiraf clean-but-`Tests_failed`) + 193
scored controls (`Tests_passed`); 232 + 239 files.
**Harness:** `tools/whole_driver_eval.py`; artifacts in this directory
(`summary_v2_preflip.txt`, `postflip_summary.txt`, `scenarios_v2_preflip.csv`,
`postflip_scenarios.csv`, `postflip_derived.{md,csv}`, unified
`raw_results.json` — 2826 entries, driver configs commit-keyed).

This is the first measurement of the *assembled* driver — backend + detection
+ accept/reject — under the Schesch cost model (FP ×10, visible conflict ×1,
crash ×1, correct 0), and (v2) the first before/after of an evidence-driven
routing repair.

## 1. Configurations

| config | backend | detection | source |
|---|---|---|---|
| bare-git | `git merge-file` | — | computed |
| bare-mergiraf | Mergiraf 0.17.0 | — | assembled from Stage C |
| driver-git | git | ✓ | computed (subprocess `core/driver.py`) |
| driver-mergiraf | Mergiraf | ✓ | assembled from Stage C (≡ P1's measurement) |
| driver-auto (pre-flip) | RM2-routed: NONE→git, MIGRATE_DECL→Weave, INTRA_BODY→Spork, else→Mergiraf | ✓ | computed @ `843e5f5` |
| driver-auto (post-flip) | RM2-routed: NONE→git, **else→Mergiraf** (#27/#28 flip) | ✓ | computed @ `9e25b4e` |

Oracle is **hybrid**: accepted output matching the Mergiraf reference inherits
the Schesch test label; divergent outputs fall back to dev-match
(`comparator.classify_result`, full 3-tier normalization). Rejects cost ×1.

## 2. Headline cost table (per file; pooled n=471; repaired scoring)

| config | TP | FP | TN | FN | CR | weighted cost | cost/file |
|---|--:|--:|--:|--:|--:|--:|--:|
| bare-git | 218 | 126 | 114 | 13 | 0 | 1387 | 2.94 |
| bare-mergiraf | 236 | 207 | 28 | 0 | 0 | 2098 | 4.45 |
| driver-git | 214 | 124 | 120 | 13 | 0 | 1373 | 2.92 |
| driver-mergiraf | 232 | 195 | 42 | 1 | 1 | 1994 | 4.23 |
| driver-auto **pre-flip** | 202 | 184 | 77 | 8 | 0 | **1925** | 4.09 |
| driver-auto **post-flip** | 222 | 170 | 71 | 8 | 0 | **1779** | **3.78** |

⚠️ Not a backend beauty contest: the corpus is *defined relative to Mergiraf*
(positives = Mergiraf-clean-but-failing), so Mergiraf-like configs carry
maximal silent-wrong mass on the positive arm while git's conservatism surfaces
the same cases as cheap textual conflicts. Legitimate readings: the
**bare→driver deltas** (§3), **pre-flip vs post-flip vs always-Mergiraf** (§4),
the **three-outcome decomposition** (§5).

## 3. Result 1 — the detection layer is net-positive on both backends

| pair | silent-wrong (×10) → visible (×1) | correct wrongly rejected (0→×1) | net cost |
|---|--:|--:|--:|
| bare-mergiraf → driver-mergiraf | **12** | 4 | **−104** |
| bare-git → driver-git | **2** | 4 | **−14** |

Identical under v1's degraded and v2's repaired scoring — the deltas are
robust to the normalization regime (same-backend pairs share any bias).
**The safety net matters more the better the backend:** Mergiraf cleanly
auto-merges most positives (24/180 textual), leaving silent mass for detection
(12 conversions); git textual-conflicts 95/180 positives, leaving little (2).
driver-mergiraf reproduces Stage C exactly: R2 12/164 = 7.3% [4.2, 12.4],
R1 4/193 = 2.1% [0.8, 5.2] (cross-check MATCH — in every scoring environment).

## 4. Result 2 — routing repair, measured before/after (#27/#28 closed)

**Pre-flip** (`843e5f5`): the specialist arms ran for real — Spork 79×
(all INTRA_BODY), Weave 47× (all MIGRATE_DECL), chosen==effective 471/471,
0 crash-fallbacks. Per-backend silent-wrong (pooled): **Spork 53/79 (67%)**,
Weave 13/47, Mergiraf 57/116, git 61/229. On the *control* arm the routing
silently broke **21/239 good merges (8.8%)** — all from the Spork/Weave arms —
vs **0** for always-Mergiraf. Pre-flip cost 1925 vs driver-mergiraf 1994
(the fast-path savings partially masked the specialist damage).

**Post-flip** (`9e25b4e`, arms off by default — `SEMANTIC_MERGE_SPECIALIST_ROUTING=1`
re-enables as apparatus): routing = {git 229 (NONE), Mergiraf 242 (else)},
cluster distribution identical (RM2 deterministic).

| | pre-flip | post-flip |
|---|--:|--:|
| control FPs from routing | **21** | **0** |
| pooled weighted cost | 1925 | **1779** (−146) |
| vs always-Mergiraf (1994) | −69 | **−215** |

**Derivation verified:** the post-flip run was *predicted* file-for-file from
committed pre-flip data via the routing identity (`postflip_derived.csv`),
then measured: **471/471 joined; 100% agreement on accept/reject; 2/471
differ on reject reason** (datastax, graphity: textual→semantic — a borderline
detector verdict re-fired; cost-identical). Cost tables agree to the digit
(1759 pos + 20 ctl = 1779). The flip's effect is exactly attributable: damage
in → damage out.

**Post-flip auto is now the best driver configuration measured** — it beats
always-Mergiraf by 215 because the NONE→git fast-path both saves RM2-less
latency on 49% of files *and* surfaces conflicts more conservatively on the
no-refactoring cluster. The dev-match caveat (FP counts on divergent outputs
are upper bounds) applies equally to both sides of every comparison here.

## 5. Result 3 — the three-outcome model, measured (per merge, any-file)

Outcome-based (unaffected by any scoring environment):

| config | arm | accept | textual | semantic | crash |
|---|---|--:|--:|--:|--:|
| bare-git | pos (180) | 85 | 95 | — | 0 |
| bare-mergiraf | pos (180) | 156 | 24 | — | 0 |
| driver-git | pos (180) | 83 | 83 | 14 | 0 |
| driver-mergiraf | pos (180) | 144 | 24 | 11 | 1 |
| driver-auto pre-flip | pos (180) | 118 | 48 | 14 | 0 |
| driver-auto post-flip | pos (180) | 123 | 45 | 12 | 0 |
| bare-git | ctl (195) | 170 | 25 | — | 0 |
| bare-mergiraf | ctl (195) | 192 | 3 | — | 0 |
| driver-git | ctl (195) | 166 | 24 | 5 | 0 |
| driver-mergiraf | ctl (195) | 188 | 3 | 4 | 0 |
| driver-auto pre-flip | ctl (195) | 175 | 14 | 6 | 0 |
| driver-auto post-flip | ctl (195) | 175 | 15 | 5 | 0 |

The semantic-reject bucket exists and is non-empty in every driver config
(11–14 positive merges), carried entirely by the #6 rename/scope family.

## 6. Latency

- Native x86_64 medians: driver-git ~88 s/file, driver-auto ~90–100 s/file
  (RM2 classifier adds two Docker calls). `driver-mergiraf`'s `med_rt 0.0` is
  an assembly artifact — its real cost is Stage C's **74 s/merge median**.
- Native ≈ Apple-Silicon-emulated per-file: the driver is **Joern-bound**
  (JVM CPG per file), not Docker-emulation-bound. Parallelism, not
  architecture, is the wall-clock lever. At ~1.5 min/file this is a research
  instrument, consistent with the PoC framing.

## 7. Threats specific to P2/P3

(a) **Scoring environment must be controlled — measured, twice.** (i) The v1
degradation: an arm64 gjf image on x86 silently killed normalization tiers 2+3
(mechanism above; v1 misattributed it to local gjf timeouts). (ii) Even between
two *healthy* environments, `contents_match` can flip borderline files (the
original local-vs-AWS ±1-file observation). Resolution: one repaired
environment, validated by exact reproduction of the committed canonical
six-tool table (Spork 32/11), scores everything cited here. Silent-degradation
lesson recorded in `deploy/aws/CLI-DEPLOY.md` (always `--platform linux/amd64`;
probe the formatter, not just image presence).
(b) **Hybrid-oracle asymmetry:** divergent outputs are dev-match-scored, which
over-counts FP (the W3 lesson). FP counts on divergent outputs (e.g. the 21
pre-flip control FPs, per-backend FP rates) are **upper bounds**; same-backend
deltas and pre/post comparisons share the bias on both sides.
(c) **Enriched, Mergiraf-relative corpus** — deltas and within-corpus
comparisons only (§2 warning).
(d) **Detector nondeterminism at the margin:** 2/471 files flipped
textual↔semantic between runs (same block either way). Negligible but
disclosed.
(e) **Inherited:** Java-only, n=164/193, whole-merge labels as per-file oracle,
THREATS rows 1–15.

## 8. Provenance

- Pre-flip run 2026-06-25/26 (~23 h, ~$9.5); post-flip + six-tool cycle
  2026-07-02/03 (~14 h, ~$6.5); both torn down + verified empty.
- Unified cache `raw_results.json`: 2826 entries — 471×4 configs +
  942 driver-auto (471 @ `843e5f5` + 471 @ `9e25b4e`), driver configs keyed by
  commit (stale-cache guard, post-P2-review fix).
- Commit trail: harness `0ec0ea3` → P2 v1 results `32df839` → FINDINGS v1
  `26b8c02` → flip + derivation `9e25b4e` → reporting pack `229a22d`/`099c3ca`
  → this v2.
