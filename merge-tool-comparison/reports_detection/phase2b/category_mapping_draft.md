# Phase-2b category mapping — 17 labeled positives → 7-category taxonomy (DRAFT)

> **RULED 2026-07-27 (Ali, via `mapping_ui.html`): all 17 rows confirmed as drafted, 0
> overrides — including row 14 (storm → #6), which was flagged VERIFY. Final labels:
> `category_mapping_adjudicated.csv`; `category_mapping.csv` unchanged. This document is
> kept as the frozen pre-run draft.**

**Frozen 2026-07-04, BEFORE any detector run** (protocol: research/outputs/phase2b-recon.md).
Source: spgroup/mergedataset @ `04a18017`, units with `Locally Observable Interference = Yes`.
Drafted by Claude from the base→left / base→right diffs; **adjudication: Ali** (§4.6 pattern —
accept/override per row; post-run revisions must be labeled as post-hoc).

Taxonomy (semantic_merge_driver/ResearchSummary.xml): 1 atomic updates ·
2 control-flow interference (short circuit) · 3 data-flow interference (stale read) ·
4 exception divergence · 5 loop semantics · 6 method rename/dangling decl ·
7 scope capture. `none-of-7` = real interference outside all seven shapes.

| # | unit | draft | confidence | rationale |
|---|------|-------|------------|-----------|
| 1 | antlr4__69ff2669ee__…Python2Target | 1-atomic-updates | med | both parents insert different keywords into the same array initializer (`python2Keywords`); concurrent writes to one state element (OA-shape); nearest of the 7 is #1 |
| 2 | antlr4__69ff2669ee__…Python3Target | 1-atomic-updates | med | identical shape to Python2Target |
| 3 | cloud-slang__20bac30d9b__…SlangImpl | 1-atomic-updates | med | L adds EVENT_TASK_START to the returned event set; R swaps ASYNC_LOOP_* for SPLIT/JOIN_* adds — concurrent writes to the same collection build |
| 4 | fitnesse__4d9ba9d221__…SlimTableFactory | 1-atomic-updates | med | L adds ddt:/dynamic-decision: table types, R adds script: — concurrent `addTableType` writes to one map |
| 5 | retrofit__71f622ce51__…RequestBuilder | 1-atomic-updates | high | L prepends `'?'` to requestQuery append; R independently manages `first ? '?' : '&'` in the param loop — two writers of one URL-prefix invariant (double-`?` class of bug) |
| 6 | swagger-maven-plugin__e825a7fdc6__…AbstractReader | 1-atomic-updates | med | L adds RequestParam/RequestBody/PathVariable, R adds RequestParam/RequestBody to the same `validParameterAnnotations` — overlapping concurrent adds (duplicate-element/import invariant) |
| 7 | OpenTripPlanner__4c506dce43__…MultiShortestPathTree | 2-cfi-short-circuit | med | R adds an `isBikeParked` early-`return false` guard in `dominates`; L rewrites the downstream dominance computation the guard now bypasses |
| 8 | crawler4j__6fdb8f27b5__…Parser | 2-cfi-short-circuit | med | R inserts a new `else if (hasCssTextContent)` branch ahead of the plain-text branch; L modified that downstream branch (`net.extractUrls`) — R's branch diverts flow around L's change |
| 9 | jsoup__3f7d2c71db__…HttpConnection | 2-cfi-short-circuit | low | L makes 307 responses take the redirect branch; R rewrote the content-type validation those responses previously reached |
| 10 | jsoup__a8b6982de9__…HttpConnection | 2-cfi-short-circuit | low | R conditionalizes redirect data-clearing on `status != 307`; L adds proxy plumbing into `createConnection` used on the re-request path |
| 11 | moshi__afb82cb3e8__…ClassJsonAdapter | 2-cfi-short-circuit | high | R moves `if (!annotations.isEmpty()) return null;` above the platform check; L appends a Kotlin-metadata rejection loop — R's hoisted early return can bypass L's new check |
| 12 | resty-gwt__867b917c43__…DirectRestServiceInterfaceClassCreator | 2-cfi-short-circuit | med | L replaces the head guard (void → primitive-boxing early return); R adds an overlay-callback branch at the tail — L's early return bypasses R's branch for primitive returns |
| 13 | elasticsearch-river-mongodb__3d4f99516b__…Slurper | 3-dfi-stale-read | med | L conditionally re-points/reassigns `oplogDb` (auth DB selection + late `oplogDb = …getDB(LOCAL)`); R adds a new read of it (`oplogRefsCollection`) — def-use/stale-read family, though reset is reassignment, **not literal `.clear()`** (outside the detector's documented shape → expected FN even if category confirmed) |
| 14 | storm__ad2be67883__…KafkaSpoutConfig | 6-rename-family | low | L deletes the `maxRetries` field/builder/getter; R's refactor adds new references into the retry constants — draft as delete-vs-reference (dangling declaration); VERIFY whether R's `DEFAULT_MAX_RETRIES` reference actually dangles in the merge |
| 15 | Activiti__50d8e43eb5__…DeploymentEntityManager | none-of-7 | med | L fixes the process-definition comparison condition; R adds event dispatch in the timer-job loop — behavioral interference in one method, no short-circuit/def-use/rename shape |
| 16 | jsoup__a44e18aa3c__…TextNode | none-of-7 | med | L migrates `preserveWhitespace` to a static-call form; R widens the indent condition — interacting whitespace behavior, no taxonomy shape |
| 17 | netty__193acdb36c__…LengthFieldBasedFrameDecoder | none-of-7 | med | L guards the `frameLength +=` adjustment behind a new flag; R changes failure timing via another new flag — two flags interacting on one computation, no taxonomy shape |

Draft totals: #1 ×6, #2 ×6, #3 ×1, #6 ×1, none-of-7 ×3; **#4, #5, #7 — zero units.**
Pre-registered reading: the benchmark's interference mass sits in the *uncovered*
categories (#1/#2, the OA/both-write and control-flow families) — the covered
categories (#3/#5/#6) have n ≤ 1 each, so Phase-2b recall for them will be
point-estimates at best; the FP arm (66 labeled-clean units) and the expected
literal-`.clear()` FN on unit 13 carry most of the evidential value.

Machine-readable draft: `category_mapping.csv` (commit,class,category) — consumed by
`tools/materialize_phase2b.py --category-map`.
