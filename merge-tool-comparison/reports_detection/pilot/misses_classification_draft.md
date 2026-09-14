# Miss Classification — ADJUDICATED (plan §4.7)

**Status: ADJUDICATED 2026-06-11 — Ali reviewed all 23 merges via `review_ui.html` (side-by-side dev-vs-Mergiraf diffs) and accepted every draft label unchanged (23/23).** Final labels live in [`misses_to_classify.csv`](misses_to_classify.csv); the table below is now the adjudicated record, not a draft. Evidence per merge in [`misses_evidence.md`](misses_evidence.md); compile-level claims verified against cached merged content (`raw_results.json`). Taxonomy: the 7 categories of `semantic_merge_driver/ResearchSummary.xml` (1 Atomic Updates, 2 Control-Flow Interference, 3 Data-Flow/Stale Read, 4 Exception Handling, 5 Loop Semantics, 6 Method Rename/dangling reference, 7 Scope Capture).

Labels used: `#6-family` (rename/declaration-change with stale reference — the taxonomy-6 shape generalized to fields, locals, signatures, external APIs), `none-of-7` (real merge-induced breakage outside all 7 categories), `none-identified` (every scored file ≈ dev resolution; failure not attributable to scored files), `indeterminate` (candidate culprit file diverged at file-level re-merge).

> **CORRECTION (2026-06-11, post-adjudication, Stage B):** the blockchain row below claimed "**does not compile**"; that sub-claim is **withdrawn**. Joern scope analysis (v2 `JoernUnresolvedReference`) shows `baseURL` IS declared in the merged file — the original check used a too-narrow `baseURL =` regex. blockchain is a *mixed-rename behavioral inconsistency* (BASE_URL vs baseURL on different paths; tests fail), still correctly labeled #6. Confirmed compile errors among attributable misses: **4**, not 5 (erudika, jacquesberger — both re-confirmed by Joern in the v2 run — winder, jnr). See `../pilot_v2/FINDINGS.md`.

## Adjudicated labels (23 merges — all drafts accepted)

| merge | label | one-line rationale |
|---|---|---|
| blockchain_api…abdf54e6ab | **#6-family (field rename)** ✓compile | merged declares `BASE_URL` but references `baseURL` 5× (one side renamed the field, other side's uses survived) — **does not compile** |
| erudika_para…a9e67cc8b3 | **#6-family (local-var rename)** ✓compile | declares `Method method`, stale `detectNestedInvocations(m)` survives — **does not compile** |
| jacquesberger…ac521954c2 | **#6-family (local-var rename)** ✓compile | `outputList` declared, `saveAsRawJsonFile(bookTitleList)` references the old name out of scope — **does not compile** |
| winder_ugs…84d687330a | **#6-family (return-type change, within-file)** ✓compile | `public Optional<IController> getController()` contains stale `return new FluidNCController();` — **does not compile** |
| cloudfoundry…80d0a0dff9 | **#6-family (external API rename)** | one side migrated Reactor `Mono.when→zip` / `.then→flatMap`; Mergiraf kept old calls where dev updated them |
| cloudfoundry…9f6b79e294 | **#6-family (external API rename)** | same Reactor migration pattern, 5 hunks |
| nysenate_openleg…9c7cf034c1 | **#6-family (cross-file API migration)** | stale `getResults()/getResult()` callers of a class another file migrated to `resultList()/result()` + DI-constructor refactor |
| tabulapdf…767699f3aa | **#6-family (cross-file ctor signature change)** | merged test keeps 5-arg `new RegexSearch(...)`, dev passes a 6th `null` arg; declaring file itself diverged (conflict) in re-merge |
| jnr_jnr-unixsocket…467698b6bd | **none-of-7 (import-deletion interference)** ✓compile | merged uses `Struct`/`Pointer` but both imports were merged away — **does not compile** |
| kaazing_robot…084cc0b426 | **none-of-7 (additive duplication)** | two `@Ignore` annotations on one method (non-repeatable → compile error) + `@Test` dev had removed |
| thenewcircle…7ec9c1b4bb | **none-of-7 (additive duplication)** | Mergiraf kept a block of `@RequestMapping("/contact")` handlers dev deleted → ambiguous Spring mappings |
| cternes_openkeepass…bb53512ab2 | **none-of-7 (additive interference)** | Mergiraf kept a CustomIcons test the dev resolution dropped; sibling file's changes plausibly invalidate it |
| javaparser…a23c6aa3b8 | **none-of-7 (stale-side selection; low confidence)** | merged keeps narrow BDD `@Given` binding + drops `DumpVisitor` import vs dev; Spork passed this merge |
| apache_shiro…13806fc623 | none-identified | scored file ≡ dev (ws-norm); all 3 tools fail → culprit in unscored intersecting file or environment |
| camsys_onebusaway…915e2f3ffe | none-identified | scored file ≡ dev |
| mikera_vectorz…d93ef1b341 | none-identified | scored file ≡ dev |
| mitre_http-proxy…b7a68118f2 | none-identified | scored file ≡ dev |
| named-data_jndn…3d47402192 | none-identified | scored file ≡ dev; Spork passed |
| openhft_chronicle…5bad7e86ea | none-identified | scored file ≡ dev |
| openhft_chronicle…e3ac571d25 | none-identified | differs from dev only in ordering of two `@Ignore`d methods (semantically ≡); Spork passed |
| prism_prism-bukkit…6dfb9ef0cf | none-identified | scored file ≡ dev |
| xebia_xebium…a82603c978 | none-identified | scored file ≡ dev |
| prism_prism-bukkit…74927cacad | indeterminate | scored sibling ≡ dev; the candidate culprit (`ActionsQuery.java`) CONFLICTed in the file-level re-merge |

## In-the-wild base rates (the §4.7 deliverable, n=23 pilot positives — adjudicated)

| bucket | n | share |
|---|---:|---:|
| **#6-family** rename/declaration-change interference | **8** | 35% (62% of the 13 attributable) |
| none-of-7 merge-induced breakage | 5 | 22% |
| none-identified (scored files ≡ dev) | 9 | 39% |
| indeterminate (culprit diverged) | 1 | 4% |
| categories #1, #2, #3, #4, #5, #7 | **0** | 0% |

## Implications (feeds the Stage-B shortlist)

1. **#6-family dominates attributable misses — but v1 R3's shape misses all 8.** v1 detects within-file **Rename Method/Class** where the *declaration* was renamed base→merged. The observed cases are: locals/fields (RM2 types `Rename Variable`/`Rename Attribute`, filtered out by v1), the **inverse shape** (declaration kept old name, *uses* renamed — invisible to (base, merged) RM2; needs per-branch base→ours/base→theirs RM2, i.e. the existing `rm2_tag` machinery, + merged-consistency scan), signature changes (`Change Return Type`, `Change/Add Parameter`), and cross-file/external-API renames (out of single-file reach).
2. **5 of 13 attributable misses are confirmed compile errors** (blockchain, erudika, jacquesberger, winder, jnr; kaazing very likely too). A cheap single-file unresolved-identifier/scope check (Joern or javac-parse level) would catch the locals/fields subset outright — arguably the highest-value, lowest-effort Stage-B detector.
3. **Zero observed instances of the covered categories (#3, #5)** in 23 real silent failures — consistent with the pilot's 0 causal hits and the pre-registered "categories rare at corpus scale" reading.
4. **The 39% none-identified cluster** is a granularity/label-noise finding: the whole-merge `Tests_failed` signal is not reproducible from the scored intersecting Java files. Carry into THREATS at Stage C (echoes ISSUES #28's whole-merge-label lesson).
