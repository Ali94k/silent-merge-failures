# Stage C — Frozen v2 Evaluation (the citable run)

**AMENDED 2026-09-04** (audit in `audit_2026-09-04.md`; rulings changed by Ali the same day): two of the eleven positive rulings are now DETECTOR-FP (atam4j, tcurdt_jdeb), the dual-lane count is 4, the control root-cause account is replaced by the post-fix evidence, and three predictions written on 2026-06-20 are updated with what the 2026-07-03 post-fix runs measured. This file was previously updated in place once, on 2026-06-20 (adjudication). Numbers below are otherwise the frozen run's.

**Date:** 2026-06-12. **Detectors:** v2, frozen at commit `843e5f5` (G2; pilot disclosed as the diagnostic that informed v2; no changes during this run — two defects discovered mid-run were left in place per protocol and are reported below; note `summary.txt`'s own caveat that the stamp does not detect an uncommitted working tree). **Spec:** plan §2–§5. **G1 re-run at start: 10/10 PASS.**

## Populations

| | positives (`mergiraf=Tests_failed`, intersect ≤3) | controls (`Tests_passed`, seeded, ≤3/repo, intersect ≤3) |
|---|---|---|
| population / target | 195 (complete) | 195 |
| materialized | 180 (15 unmaterializable: commits gone upstream) | 195 |
| left sample: all files CONFLICT at file-level re-merge | 16 merges (17 of the 25 diverged files / 232) | 2 merges (2 of the 3 diverged files / 239) |
| scored on a partial file set (≥1 file diverged, ≥1 kept) *(added 2026-09-04)* | 8 merges (8 files) | 1 merge (1 file) |
| **scored** | **164** | **193** |

## Headline numbers (thesis numbers)

- **R2 — block rate on real silent failures: 12/164 = 7.3% [4.2%, 12.4%]** (11 via detector FLAG, 1 via fail-closed RM2 crash). **Decomposed by §4.6 adjudication (Ali, 2026-06-20; amended 2026-09-04; final labels in `hit_adjudications.md`):** **9 of the 11 FLAGged merges = CAUSAL**, 0 REAL-BUT-INCIDENTAL, **2 DETECTOR-FP** — tcurdt_jdeb (the flagged site is the method call `options.compression()`; retired by the post-fix runs) and atam4j (the flagged L27 is the old method's surviving declaration; all callers resolve; the merge-induced break is in an unflagged sibling file). Flag precision on the positives **9/11 = 82%**; over all 15 ruled flags **9/15 = 60% [35.7, 80.2]**. **The citable headline is "9 CAUSAL of 164 = 5.5% [2.9, 10.1]"** real silent failures caught by a detector; +1 fail-closed crash (jadventure, a defensive block, not a detection). Post-fix composition: 10 flags (9 causal + the atam4j DETECTOR-FP, which stays flagged post-fix) + 1 fail-closed = 11/164 = 6.7% [3.8, 11.6] — the same figure as the frozen "11 flags", with a different composition; cite the composition. All 9 causal hits are rename/declaration-interference shapes; 4 are dual-lane corroborated (ahome-it, comatoes, erudika, softinstigate). (comatoes ruled CAUSAL via the Joern `gameState` lane; its RM2 `setReservePowerCapacity→setSectorNumber` pairing is an ambiguous artifact — see `hit_adjudications.md`.)
- **R1 — block rate on good merges: 4/193 = 2.1% [0.8%, 5.2%]** (4 FLAG, 0 fail-closed). **All four adjudicated DETECTOR-FP** (§4.6, 2026-06-20 — confirmed false alarms, not borderline). All four are Stage-B var-lane defects, identified during the run and left unfixed per the G2 freeze. **What the post-fix runs measured (2026-07-03, `reports_detection/postfix{,2}/`; replaces the two-defect account written here on 2026-06-20):**
  1. *Round 1* (`5ed92a2`): the missing call-site exclusion (`\bold\b` also matched `old(...)`; fix: skip matches followed by `(`) and the comment-stripper line-crossing (char-literal regex consumed newlines; fix: exclude `\n`). Cleared **aerospike only** — controls 3/193. Also retired one positive flag (tcurdt) that had depended on the call-site defect.
  2. *Round 2* (`f964354`): the declaration guard did not accept generics wildcards (`Class<? extends Map<?, ?>> mapType =`) or lambda parameters. Cleared cloudfoundry ×2 and podam — controls **0/193 = 0.0% [0, 2.0]**. No other verdict changed in either round (5 changes across 471 files, all FLAG→CLEAN).
  Zero control FPs from any Joern lane, the call lane, or the category detectors.
- **Analyzability: 1/443 files UNANALYZABLE (0.2%)** — a single RM2 crash (jadventure), fail-closed as designed. Joern: 0 failures across the 4,430 `joern-parse` invocations implied by the lane design (three differential lanes parse merged + ours + theirs, one parses merged only: 10 per file × 443).
- **Runtime: median 74 s/merge** (over the 375 materialized merges; 75 s over the 357 scored) — 16× under the G0 threshold; ≈ 9 h summed compute.

## The category base-rate finding holds at scale

On 443 clean-merged real files (164 silent failures + 193 good merges + their siblings): `JoernDataFlowInterference` **0 flags**, `JoernInfiniteLoop` **0**, `JoernInvalidLoopBounds` **0** — neither detections nor false positives. The taxonomy's categories #3/#5 did not occur once in the full attribution-friendly population of real-world silent failures. The detection mass is entirely rename/declaration interference: `JoernUnresolvedReference` 7 file-flags, `RM2RenameConflict` 12 (incl. the 4 control FPs and the 2 amended positives).

## Flagged positives (11 merges — ADJUDICATED 2026-06-20, AMENDED 2026-09-04: 9 CAUSAL, 2 DETECTOR-FP)

Full per-flag rationale + the 4 control DETECTOR-FPs in `hit_adjudications.md`.

| merge | lanes | shape | ruling |
|---|---|---|---|
| ahome-it_lienzo-core | both | field rename `innerLayoutContainer→m_…`, stale ref + unresolved | CAUSAL |
| atam4j | RM2 ×4 records | L27 is the surviving declaration; 3 callers resolve; break is in the unflagged sibling file | **DETECTOR-FP** *(amended)* |
| comatoes_ftl-profile-editor | Joern (+RM2 artifacts) | unresolved `gameState` (Joern carries it); RM2 rename pairing is an ambiguous artifact | CAUSAL |
| datastax_java-driver | Joern | unresolved `isShutdown` (field dropped; method survives) | CAUSAL |
| erudika_para | both | pilot hit, reconfirmed (in-sample) | CAUSAL |
| jacquesberger | Joern ×2 | pilot hit, reconfirmed (in-sample; both dangling halves) | CAUSAL |
| jcabi_jcabi-github ×2 merges | RM2 | method renames; RtGist 1 stale caller (L82), RtHooks 1 stale caller of 4 records (L60) | CAUSAL |
| jdupl_lancoder | Joern | unresolved `ctxApi` | CAUSAL |
| softinstigate_restheart | both | `request→req`/`response→res`, 3 stale sites (2 further RM2 records are method declarations) | CAUSAL |
| tcurdt_jdeb | RM2 | `options.compression()` is a method call on the live parameter — the `(`-defect | **DETECTOR-FP** *(amended)* |

## Interpretation (plan §5 matrix)

R1 low (2.1% at the frozen suite; 3/193 after the two one-line fixes, 0/193 [0, 2.0] after the guard extensions), R2 with **9 of 11 flags CAUSAL** → still **the pre-registered cell "R1 low (≲5%) | R2 >0 causal hits": the detection layer adds measurable value at acceptable cost.** In Schesch cost-model terms: v2 converts 7.3% of the silent-incorrect mass (12/164 blocked, cost ×10) into visible rejects (cost ×1), of which 5.5% (9/164) are confirmed causal, at a 2.1% (pre-fix) false-block rate on good merges; net under the model weights 12 × 9 − 4 × 1 = +104, which matches the −104 weighted-cost delta P2 measured bare-Mergiraf → driver-Mergiraf. Combined with the base-rate finding, the layer's value is carried entirely by generic rename/scope consistency — not by the category-specific detectors that motivated the original design. One measured cross-file false negative (the atam4j sibling file) marks the file-local ceiling.

## Deviations & threats to carry

- 15/195 positives unmaterializable (upstream history loss) — population attrition, not selection (not verifiable from committed artifacts).
- 16/180 positive merges (8.9%) vs 2/195 controls left the sample via file-level CONFLICT divergence — the whole-merge-label granularity asymmetry, observed here and in the pilot (the pilot's 5 all-diverged merges are among these 16, so this is one observation, not two; ISSUES #28 records a related single-file-granularity artifact: two Mergiraf dev-mismatch files whose whole-merge `Merge_failed` label came from a different file). A further 8 positive and 1 control merges were scored on a partial file set.
- The pilot's 30+30 merges are a subset of these populations (disclosed; v2 was pilot-informed, frozen before this run; the 9 *new* flagged positives are out-of-pilot evidence the detectors generalize — 7 of them CAUSAL after amendment).
- Mid-run defect protocol followed: both var-lane defects reported here on 2026-06-12, fix deferred. The post-fix runs were executed 2026-07-03 (`postfix/`, `postfix2/`); a second defect class was needed to reach 0/193, and one positive flag proved defect-dependent (see R1 above).
- The §4.6 procedure was a single unblinded rater with pre-filled draft labels (0 overrides); the 2026-09-04 audit was the first independent check and changed 2 of 11 rulings. Carry to THREATS.
