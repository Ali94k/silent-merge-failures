# Stage-B Findings — v2 Detectors on the Pilot Sample

**Date:** 2026-06-11. **Detectors:** v2 (Stage B), run on the SAME 30+30 pilot sample as Stage A — disclosed as the pilot-informed improvement check (plan G2); **not the citable evaluation** (Stage C runs v2 frozen on the full populations). Caveat: the working tree was uncommitted during this run, so the cache/report key still reads `2eed882` (v1's commit); freeze v2 at its own commit before Stage C.

## Headline: v1 → v2 on identical merges

| metric | v1 | v2 |
|---|---|---|
| **R1** (controls blocked) | 1/30 = 3.3% [0.6, 16.7] | **0/30 = 0.0% [0.0, 11.4]** |
| **R2** (positives blocked) | 2/25 = 8.0% — both hits provisional DETECTOR-FP | **2/25 = 8.0% [2.2, 25.0] — both hits TRUE detections** (pending Ali's §4.6 written adjudication) |
| causal hits | 0 | **2** |
| UNANALYZABLE files | 0/64 | 0/64 |
| median runtime/merge | 34 s | 68 s (5 strategies, three 3-way differential; still ~18× under G0) |

The two v2 hits are exactly the two intra-file compile-error misses from the adjudicated Stage-A classification:

- **erudika** — dual-lane corroboration: `JoernUnresolvedReference` (merge-induced unresolved `m` in `invoke`) + `RM2RenameConflict` v2 (per-branch Rename Variable `m→method`, stale reference, old name no longer declared).
- **jacquesberger** — `JoernUnresolvedReference` caught **both dangling halves**: `bookTitleList` unresolved in `saveToFiles` AND `outputList` unresolved in `initializeBookList`.

All five v1 false positives are gone (4 pos-side `JoernInfiniteLoop` sites + the 1 control, jcloisterzone): WHILE/DO/FOR-only killed the `if(true)` hit, exit-awareness killed the deliberate `while(true){…break/return/throw}` idioms, and the differential filter would have killed all five anyway (every site was in base+ours+theirs).

## What Stage B changed (all in `semantic_merge_driver/`, the sanctioned exception)

1. **`RM2RenameConflict` v2** — rename types widened to Variable/Parameter/Attribute (codeElement `name : type`, image-probed; the image does NOT report static-final constant renames); per-branch RM2 on (base,ours)/(base,theirs); mixed-state guard for parent-only renames; var-lane declaration guard + comment/string stripping.
2. **`JoernUnresolvedReference` (new)** — differential-only: identifiers with no `refsTo` declaration, unresolved in merged but in neither parent. Abstains without parents (single-file would FP on every inherited field); fail-closed once analysis starts.
3. **`JoernInfiniteLoop` v2** — loop-only, exit-aware, differential (DFI Phase-2a pattern).
4. `JoernDataFlowInterference`, `JoernInvalidLoopBounds`: untouched (no Stage-A evidence for changes).

## Negative results (kept deliberately — each is a refuted detector design)

- **Type-resolution lane dropped after two stopped runs.** Built to catch the jnr import-deletion shape; on real files javasrc2cpg's type inference proved version-unstable (camsys: flagged "import merged away" on a merged file byte-identical to the dev resolution that compiled) and method-level keys collide across nested classes (`Compiler.java`'s many `parse`/`<init>`). Import-deletion breakage is NOT covered by v2 — needs a compile-check oracle (future work, pairs with Phase 2b).
- **Synthetic-name/lambda hardening was mandatory**: `$objN` temporaries and `<lambda>N` method numbering shift between file versions, breaking naive (method, name) differential keys. The id lane keys by name only.
- **Change-Return-Type detection skipped** (winder shape): RM2 reports it without the method name in `codeElement[0]`, and a `return`-statement type check would be pilot-overfit.

## Evidence correction (Stage-A classification, surfaced not silently fixed)

Stage A claimed **5** confirmed compile errors among attributable misses; the correct count is **4**. Joern's scope analysis shows blockchain's `baseURL` IS declared in the merged file (ours introduced it; the earlier `baseURL =` regex was too narrow) — blockchain is a **mixed-rename behavioral inconsistency** (GET path on `BASE_URL`, other paths on `baseURL`; tests fail), not a compile error. Ali's `#6` label stands; the compile-error sub-claim is withdrawn. Corrected in `../pilot/misses_classification_draft.md`.

## v2 coverage of the 8 adjudicated #6-family misses

| miss | v2 | why |
|---|---|---|
| erudika (var rename, compile error) | ✅ both lanes | intra-file, unresolved id |
| jacquesberger (var rename, compile error) | ✅ id lane | intra-file, unresolved id (decl guard correctly deferred RM2) |
| blockchain (constant mixed-rename, behavioral) | ❌ | identifier resolves; RM2 image silent on constant renames |
| winder (return-type change, compile error) | ❌ | CRT codeElement name-less; type checking = overfit risk |
| cloudfoundry ×2 (external API rename) | ❌ | no declaration in file for RM2; nothing unresolved |
| nysenate (cross-file migration) | ❌ | cross-file |
| tabula (cross-file ctor signature) | ❌ | cross-file |

2/8 caught, each remaining miss attributed to a documented, named limitation — the honest-scope statement Stage C will quantify.

## Stage-C go/no-go

v2 is ready to freeze: R1 point estimate 0% on the pilot controls, R2 strictly better than v1 (2 causal vs 0), no UNANALYZABLE, runtime fine. Remaining pre-Stage-C steps: (1) commit the Stage-B tree (G2 freeze — cache keys depend on it), (2) Ali's written §4.6 adjudication of the 2 v2 hits, (3) re-run G1 inject-sanity at Stage-C start per plan.
