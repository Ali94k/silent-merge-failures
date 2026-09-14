# Known Issues & Improvements

Tracked issues identified during project review. Each should be addressed before final presentation.

---

## CRITICAL

### Issue #1: Sample Size Too Small (n=10) — RESOLVED

**Priority:** Critical
**Area:** Data / Evaluation
**Files:** `src/cli.py`, `config/datasets.yaml`, `Makefile`
**Status:** Fixed

**Problem:**
Only 10 scenarios collected from 2 repos (junit4, javaparser). 8 of 10 come from a single merge commit (`junit4__ab7c961572`). Results are not statistically meaningful and won't survive peer scrutiny.

**Resolution:**
- The Schesch et al. (ASE 2024) dataset is now the **default data source** for the pipeline.
- The `load-dataset` CLI command now reads defaults from `config/datasets.yaml` (no `--dataset-path` required).
- The `all` command uses `--source dataset` by default; `--source collect` still available for repo mining.
- Scenario-level caching: previously extracted scenario JSONs are skipped on subsequent runs (`--force` to re-extract).
- Missing dataset directory produces a helpful error with Zenodo/GitHub download URLs.
- Makefile targets added: `make load-dataset`, `make load-dataset-force`.
- 3 new tests added for caching, `--force`, and missing-dir behavior.

---

### Issue #2: Structured Tools All Score 0.0 F1 — Likely Adapter Bugs

**Priority:** Critical
**Area:** Tool Adapters / Evaluation
**Files:** `src/tools/jdime.py`, `src/tools/spork.py`, `src/tools/mastery.py`, `src/evaluation/comparator.py`
**Status:** **resolved** (2026-05-15) — Tier E (3e.0 D.1 identity-bug fix + 10 new transforms) recovered 18 more Spork FPs on top of Tier D. Cumulative Spork TP 1 → 32, X_total = 30 — **HITS the original plan §3 floor exactly.** Mastery +2 bonus (10 → 12) from D.1 fix + array trailing comma. The 11 remaining Spork FPs are dominated by genuinely irrecoverable cases (2 gjf parse-fail, 2 content disagreements) + 7 long-tail patterns (multi-decl split, FQN scope, numeric underscore, redundant `abstract`) deferred to Tier F or 3a. The comparator-gap framing is now fully empirically validated: Spork's residuals were AST-equivalent reformatting under text comparison; once normalized by the four-tier pipeline (M3.5 gjf + 3b Tier C + 3d Tier D + 3e Tier E), they collapse to equivalent canonical forms. Earlier status: decided — 3e implemented (M3.5, 2026-05-14); 3j manual labelling completed (n=15, all AST-equivalent reformatting); 3b Tier C implemented (2026-05-14) — recovered 5 FPs; 3d Tier D implemented (2026-05-15) — recovered 7 more FPs (X_total = 12); 3e Tier E implemented (2026-05-15) — recovered 18 more (X_total = 30; **floor HIT**).

**Problem:**
- JDime crashes on 48/50 scenarios (96% crash rate) — likely a Docker build or runtime issue, not a legitimate tool limitation.
- Mastery produces 44 FP and 0 TP — output doesn't match developer resolution, but AST-based tools may reformat code (imports, braces, whitespace) that `normalize_content()` doesn't account for.
- Spork produces 42 FP and only 1 TP — same normalization concern as Mastery.
- Current normalization only strips trailing whitespace and normalizes line endings. AST tools may produce semantically identical but textually different output.

**Stage γ diagnostic (2026-05-14, Mastery extension same day):** The FPs split by failure mode, not by single root cause:

- **Spork (42 FPs)** — bucketing produced 1 whitespace-only / 2 imports+whitespace / **39 structural**. *Three of 39* `structural` cases (size-stratified eyeball: small/median/largest) are AST-equivalent reformatting by Spork's pretty-printer — extra parens around casts, FQN expansion (`InstantiationException` → `java.lang.InstantiationException`), brace-style differences, blank lines between fields, method-signature line breaks. **The other 36 `structural` cases are unsampled** — hypothesis is they share the pattern, but this is not yet measured. One residual non-formatting pathology surfaced (comment duplication: `//PBKDF2` appearing twice).
- **Mastery (44 FPs)** — bucketing produced **0** whitespace-only / **0** imports+whitespace / **44 structural**. Size-stratified eyeball reveals *content loss*: Mastery's output drops file-header comments (small case: 71 vs 793 chars — the entire GPL header dropped), Javadoc blocks (medium case: ~4.7KB dropped), and blank-line structure. This is a Mastery characteristic, **not a comparator artefact**, and parallels Schesch et al.'s framing of JDime as "unsuitable for practical use" because it "discards comments, discards file headers, and arbitrarily reorders methods and fields." Mastery shares the family weakness.

Full write-up: [`docs/plans/stage-gamma-fp-diagnostic.md`](../docs/plans/stage-gamma-fp-diagnostic.md) (§6 Mastery extension).

**Decision (M3 option):**
- For **Spork**: **3e** (formatter-based normalisation via `google-java-format` roundtrip) as primary; **3i** (cite upstream Mergiraf numbers) + **3h** (multi-criteria reporting) additively; **3j** (manual labelling) on the residual after 3e; defer **3a** (test-suite ground truth) unless 3e+3j leave > ~10% unexplained.
- For **Mastery**: 3e still useful (recovers any whitespace/format component) but **the headline FP rate needs an intrinsic-limitation caveat** parallel to the JDime crash-rate caveat — Mastery's AST roundtrip discards comments, and that's a tool property not a measurement bug. 3i-style write-up of this limitation alongside Mastery's row in the final report.

**3e contingency:** the recommendation is built from *prior knowledge* of what `google-java-format` does, not empirical verification against these specific diffs. M3.5 implementation is the verification step — if 3e doesn't recover the Spork FPs in practice, upgrade to **3b** (AST-aware normalize) or **3d** (token-level comparison). Implementation lives in Mergiraf plan Phase M3.5.

**M3.5 empirical outcome (2026-05-14):** comparator now invokes `google-java-format` 1.22.0 Docker roundtrip when whitespace normalize disagrees ([`src/evaluation/comparator.py::contents_match`](src/evaluation/comparator.py), [`docker/google-java-format/Dockerfile`](docker/google-java-format/Dockerfile)). Re-run on n=50:

| Tool | Pre-3e | Post-3e | Recovered |
|---|---|---|---:|
| Spork | TP 1 / FP 42 | TP 2 / FP 41 | **1 FP** |
| Mastery | TP 0 / FP 44 | TP 0 / FP 44 | **0 FPs** |

The contingency hedge has fired. Across the 39 unsampled Spork `structural` cases, the dominant residuals after formatter roundtrip are `} else { if (X) }` ↔ `} else if (X)` restructuring, comment-placement differences (standalone above `if` ↔ trailing after `{`), and redundant cast parens (`((Long) (value))` ↔ `(Long) value`) — none of which `google-java-format` normalises. The §5 hypothesis ("all 39 unsampled structural cases follow the small-sample reformatting pattern") was incorrect; the structural bucket is heterogeneous. Full breakdown: [`docs/plans/stage-gamma-fp-diagnostic.md §8`](../docs/plans/stage-gamma-fp-diagnostic.md).

Mastery's 0-FP recovery matches §6's intrinsic-content-loss prediction and reinforces the "Mastery shares JDime's family weakness" framing.

**Fix (status: implemented; follow-up needed):**
- ✓ Implementation per [`docs/plans/mergiraf-integration.md §Phase 3.5`](../docs/plans/mergiraf-integration.md) shipped — `google-java-format` Docker layer added; comparator does two-tier comparison (whitespace → formatter roundtrip).
- ✗ Spork/Mastery FP rates did NOT drop sharply — Spork 42→41, Mastery 44→44.
- ✓ Option **3j** (stratified manual labelling, n=15 from the 39 still-differ Spork residuals) executed 2026-05-14. **15 of 15 sampled scenarios are AST-equivalent reformatting** that gjf preserves rather than normalises (blank-line placement, comment placement, cast parens, FQN expansion, `} else { if }` restructuring, long array-literal line-break). No content loss / duplication / method reordering observed. Original §3 hypothesis survives at higher sample size; what failed in §8 was the prediction that gjf alone would handle these patterns. Full classification: [`docs/plans/stage-gamma-fp-diagnostic.md §9`](../docs/plans/stage-gamma-fp-diagnostic.md).
- **Reframing (post-3j):** Spork's FP rate is a comparator-ground-truth gap, **not a Spork bug** in the Mastery / JDime sense — Mastery drops content (intrinsic), JDime crashes (intrinsic); Spork's outputs are AST-equivalent to dev's, just textually distinct under gjf's minimally-opinionated normalisation.
- **Deferred to post-tool-integration:** option **3b** (AST-aware normalize via tree-sitter-java — the principled fix that would recover the ~93% AST-equivalent FPs; design drafted in [`comparator-3b-ast-normalize.md`](../docs/plans/comparator-3b-ast-normalize.md), Tier C scope, 5 phased commits, ~2.5-3d); option **3h** (multi-criteria reporting matrix); option **3i** (cite upstream Mergiraf test-suite numbers). All three become more valuable *after* the full tool comparison (mergiraf, plus revisited spork/mastery/jdime) ships, so the headline numbers reported under multi-criteria are complete. Tracked in [`mergiraf-integration.md §Phase 3.5`](../docs/plans/mergiraf-integration.md) TODO list.
- Debug JDime Docker image — check logs for StackOverflowError or build failures (orthogonal to the comparator fix; JDime crashes happen *before* the comparator runs).

**3b Tier C empirical outcome (2026-05-14):** five-transform AST normalize implemented per [`docs/plans/comparator-3b-ast-normalize.md`](../docs/plans/comparator-3b-ast-normalize.md) (5 phased commits `3c39f8b…535a1a3`). `src/evaluation/ast_normalize.py` shipped via tree-sitter-java 0.23.5; wired into `comparator.contents_match` as Tier 3 behind `MERGE_COMPARATOR_AST_NORMALIZE=on` (default; conftest defaults off). Suite 41 → 58 passing. Re-run on n=50:

| Tool | Pre-3b (post-M3.5) | Post-3b Tier C | Recovered |
|---|---|---|---:|
| Spork | TP 2 / FP 41 | TP 7 / FP 36 | **5 FPs** |
| Mastery | TP 0 / FP 44 | TP 0 / FP 44 | **0 FPs** |
| git-merge-file | TP 39 / FP 0 | TP 39 / FP 0 | unchanged |
| JDime | TP 0 / FP 2 | TP 0 / FP 2 | unchanged |

Recovery X=5 vs plan §3 floor X≥30 (Wilson 95% lower bound × 39) and pause threshold X<25 (~65% recovery). **Plan §3 pause trigger fires: ISSUES.md #2 stays `decided`, not `resolved`.**

Root cause diagnosis (verified against §9 scenarios `ab0oo APRSPacket`, `aerospike PartitionTracker`, `adangel pmd DOMLineNumbers`): comment-only and blank-line-only residuals DO close under Tier 3 (e.g. DOMLineNumbers matches). The shortfall is that §9's per-scenario "dominant pattern" labels described the *raw* pre-gjf diff — but after gjf normalises, the *residual* diff is dominated by patterns Tier C's 5 transforms don't cover:

- `((cast_expr) (value))` ↔ `(cast_expr) value` — outer paren wraps a `cast_expression` (not another `parenthesized_expression`), so `strip_redundant_parens` does not fire by design.
- `if (c) { s; }` ↔ `if (c) s;` — single-statement block ↔ no block. Distinct from `} else { if }` ↔ `} else if`; not in the Tier C set.
- `(a | b | c)` ↔ `a | b | c` — paren around same-precedence binary chain. Conservatively preserved by Tier C (would need precedence reasoning).
- `0xf0` ↔ `0xF0` — hex-literal case. Textual, not AST.

The §9 hypothesis that residuals are AST-equivalent reformatting still holds; the framing "comparator-gap, not Spork bug" survives. What broke is the §3 mapping from "AST-equivalent" to "recoverable by these 5 transforms" — Tier C is a strict subset. Closing the gap fully requires either broader transforms (Tier D / cast-aware paren strip / single-stmt block unwrap / paren-around-binary stripping) or test-suite ground truth (3a). Both deferred.

Per the plan's stop-and-document decision: kept Tier C code (it does close real comment / blank-line / FQN / `} else { if }` cases; reverting would lose verified recovery), regenerated `reports/results.csv` with post-3b numbers, kept ISSUES.md #2 at `decided`. Closing the issue cleanly requires a follow-up cycle.

**3d Tier D empirical outcome (2026-05-15):** six additional AST + token-canonical transforms shipped per [`docs/plans/comparator-3d-extended-ast-transforms.md`](../docs/plans/comparator-3d-extended-ast-transforms.md) (6 phased commits `99a5f90…1c6eb87`):

- `unwrap_single_stmt_block` (D.1) — if/while/for/do/else `{ stmt; }` → `stmt;`; supersedes Tier C `flatten_else_if`. Dangling-else guard preserves consequence-block when outer has `else` and inner contains a bare-if.
- `strip_paren_around_primary` (D.2) — paren around any Java primary; supersedes Tier C `strip_redundant_parens`. Syntactic-paren guard preserves if/while/do/synchronized/switch condition parens.
- `strip_paren_around_cast` (D.3) — `((cast) val)` → `(cast) val`; postfix-rebinding guard preserves `((Long) x).f`.
- `strip_paren_around_binary_safe_parent` (D.4) — paren around binary/ternary in standalone-position contexts (return / throw / arg / initializer / etc).
- `strip_paren_around_binary_precedence_aware` (D.5) — Java operator precedence table; strip when inner-op > outer-op OR same-op-assoc-safe (`&&`, `||`, `&`, `|`, `^`). `+`/`*` excluded for type-promotion concerns.
- `token_canonical_fold` (D.6) — re-parse + leaf-emit with single-space separator; string/character/text-block literals atomic. Closes line-wrap / indentation differences that gjf preserves.

Suite 58 → 82 (16 new unit tests + 2 new integration; some Tier C tests repurposed). Re-run on n=50:

| Tool | Pre-3d (post-3b) | Post-3d Tier D | Recovered | Cumulative since pre-3b |
|---|---|---|---:|---:|
| Spork | TP 7 / FP 36 | TP 14 / FP 29 | **7** | **12** |
| Mastery | TP 0 / FP 44 | TP 10 / FP 34 | **10** | **10** |
| JDime | TP 0 / FP 2 | TP 1 / FP 1 | **1** | **1** |
| git-merge-file | TP 39 / FP 0 | TP 39 / FP 0 | 0 | 0 |

Tier D matches the prototype recovery exactly (Spork +7) AND hits its own §3 (3d) stretch target. Mastery's surprise +10 comes from scenarios where the §6 "content loss" is exclusively comment-loss; Tier C `strip_comments` + Tier D `token_canonical_fold` close them. The remaining 34 Mastery FPs involve genuine code-content loss — recoverable only via 3a test-suite ground truth, if at all.

**3b plan §3 floor (Spork TP ≥ 32 / FP ≤ 11; X ≥ 30) STILL NOT HIT.** X_total = 12 vs target 30. ISSUES.md #2 stays at `decided`, not `resolved`. The remaining 29 Spork residuals are dominated by long-array-literal whitespace (6 scenarios; deferred Tier E), `+`/`*` same-op-strip with mixed-type concerns (~5-8; Tier E with type-inference), and a long tail of mixed patterns (15+; each requires multiple transforms in concert).

Closing the issue cleanly now requires Tier E or 3a. Both deferred.

**3e Tier E empirical outcome (2026-05-15):** 11 phases shipped per [`docs/plans/comparator-3e-tier-e-transforms.md`](../docs/plans/comparator-3e-tier-e-transforms.md). The Tier E residual analysis surfaced two surprises against the original brief: (1) D.1 had an identity bug — `c is cons` always failed because tree-sitter returns fresh `Node` wrappers; the cons block was walked twice, producing overlapping edits and D.6 fold parse-fail on 6 scenarios; (2) "long-array whitespace" (the brief's expected dominant pattern) was NOT a residual driver — that closed correctly once the D.1 bug was fixed. The actual dominant patterns were paren strips for unary `!`/`~`, `new T[]{}` array shorthand, `+`/`-`/`*` same-op chains, plus small textual differences (enum trailing `;`, hex case, float suffix `d`/`D`/`f`/`F`).

Phases: 3e.0 D.1 identity-bug fix; 3e.1 strip_paren_around_unary (`{!, ~}` in safe contexts); 3e.2 strip_array_creation_shorthand (`new T[]{}` in var_decl / array_initializer parents — incl. nested); 3e.3 strip_paren_around_arith_same_op_left_assoc (`+`/`-`/`*`/`/`/`%` left position, string-concat-safe); 3e.4 strip_paren_around_instanceof (precedence < 9 in binary parents); 3e.5 strip_empty_enum_body_declarations (`enum X { A; }` → `enum X { A }`); 3e.6 expand SAFE_BINARY_PAREN_PARENTS (+ `assert_statement`, `array_access`); 3e.7 strip_array_initializer_trailing_comma; 3e.8 strip_paren_around_assignment (in parenthesized_expression / expression_statement parents); 3e.9 normalize_float_literal_suffix (strip d/D/f/F suffix when literal has `.`/exp; convert `Nd` → `N.0`); 3e.10 normalize_hex_literal_case (lowercase). Suite 82 → 112 (+30 unit tests). Re-run on n=50:

| Tool | Pre-3e (post-3d) | Post-3e Tier E | Recovered | Cumulative since pre-3b |
|---|---|---|---:|---:|
| Spork | TP 14 / FP 29 | TP 32 / FP 11 | **18** | **30** ✓ |
| Mastery | TP 10 / FP 34 | TP 12 / FP 32 | **2** | **12** |
| JDime | TP 1 / FP 1 | TP 1 / FP 1 | 0 | 1 |
| git-merge-file | TP 39 / FP 0 | TP 39 / FP 0 | 0 | 0 |

**Plan §3 floor of X_total ≥ 30 HIT exactly** (Spork TP 32; X_total = 32 − 2 baseline = 30). Committed numbers match the in-memory prototype recovery exactly. **ISSUES.md #2 moves `decided → resolved`.**

The 11 remaining Spork FPs are 4 irrecoverable (2 gjf parse-fail on aerospike proxy files; 2 content disagreements — one dropped import in `adamd_z`, one kept debug `println` in `adoptopenjdk SFNode`) + 7 long-tail patterns (multi-declarator split `long a; long b;` ↔ `long a, b;`, FQN outside `java.lang`, numeric underscore `5_000_000`, redundant `abstract` modifier on interface, 3 mixed-pattern scenarios). Closing these requires Tier F (non-trivial AST rewriting) or 3a (test-suite ground truth) — neither in scope.

Mastery's +2 bonus: D.1 fix recovered 1 comment-only case (overlapping edits had been corrupting D.6 fold), and 3e.7 array-initializer trailing-comma strip recovered 1 more. The remaining 32 Mastery FPs are genuine code-content loss, recoverable only via 3a if at all.

---

### Issue #3: All Scenarios Categorized as "unknown" — RESOLVED

**Priority:** Critical
**Area:** Evaluation / Metrics
**Files:** `src/evaluation/categorizer.py`, `src/cli.py`, `src/evaluation/metrics.py`
**Status:** **resolved** (2026-05-18) — RM2 R1+R2.

**Problem:**
The category system exists in `compute_metrics()` (`scenarios_categories` parameter) but is never populated. Every scenario gets `category=unknown`, producing duplicate rows in reports (one "all", one "unknown" — identical).

*Phase-0 correction:* the param was not "unused" — `cli._classify_results` did wire it (`categories[sid] = scenario.category`) and pass it to `compute_metrics`; every value was the constant `"unknown"` because `MergeScenario.category` defaulted to it and nothing computed a real value. The fix is upstream (produce a real category), not inside `compute_metrics`.

**Resolution:**
- **R1** (`tools/rm2_tag.py`) tags every scenario with RM2-detected refactoring types per branch axis, file-level (`refactorings: {ours, theirs}`).
- **R2** adds `src/evaluation/categorizer.py` — `cluster_of(ours, theirs)` maps the union of the two axes onto the 7-cluster merge-difficulty taxonomy (a parity-tested copy of R4a's `semantic_merge_driver/core/refactoring_classifier.py`; drift guarded by `tests/test_categorizer.py::test_taxonomy_parity`). Deliberate deviation from the plan's `resolution` axis: the cluster is computed exactly as the runtime dispatcher computes it (`ours∪theirs`), so the evidence can justify/refute the W5/S2 routing elifs and is not quasi-circular against the resolution that defines TP/FP.
- `cli._classify_results` now derives the category from the R1 tags instead of the `"unknown"` default.
- The regenerated `reports/results.csv` (and `.json` / `.tex`) carry genuine per-cluster rows. On the Schesch n=50 the file-level distribution is `NONE` 18 / `INTRA_BODY` 16 / `MIGRATE_DECL` 8 / `LOCAL_DECL_EDIT` 4 / `SYMBOL_CASCADE` 4 (`CONTAINER_MOVE` / `HIERARCHY_RESHAPE` absent — file-level cannot see cross-file moves; honest, expected). Per-cluster n is small (4–18), so the pivot is **suggestive, not statistically defensible** (cf. #5 / plan §2 Wilson-CI rule); reported as such, not tuned.

---

## HIGH

### Issue #4: No Visualizations

**Priority:** High
**Area:** Reporting
**Files:** `src/evaluation/report.py`
**Status:** **resolved (2026-07-03)** — `to_charts()` in `report.py` (new `charts` format; matplotlib via the `[viz]` optional extra, headless Agg, graceful skip when absent): F1 bars, precision-with-Wilson-CI error bars, stacked TP/FP/TN/FN/CRASH outcome bars, log-scale runtime bars, per-scenario heatmap. Generated for the six-tool canonical run → committed at `reports/chart_*.pdf`. Tests in `tests/test_report_extensions.py` (charts smoke skips without matplotlib).

**Problem:**
Reports are only tables (console, CSV, JSON, LaTeX). For a presentation, tables of raw numbers are hard to absorb quickly.

**Fix:**
- Add matplotlib/seaborn chart generation to `report.py`.
- Key charts needed:
  - Bar chart of F1 score per tool
  - Stacked bar chart of TP/FP/TN/FN/CRASH per tool
  - Runtime comparison (box plot or bar chart)
  - Optional: heatmap of per-scenario results

---

### Issue #5: No Statistical Confidence Measures

**Priority:** High
**Area:** Evaluation / Metrics
**Files:** `src/evaluation/metrics.py`
**Status:** **resolved (2026-07-03)** — `wilson()` + `precision_ci`/`recall_ci` in `metrics.py`; CI columns in all report formats + error bars on the precision chart. In the canonical table (`reports/results.csv`): e.g. jdime 0.50 [0.09, 0.91] on n=2 non-crash — exactly the misleading-point-estimate case this issue flagged. Bootstrap-F1 + McNemar remain optional future work (McNemar already used ad hoc in the #28 W3 gate); sample size was already reported.

**Problem:**
No confidence intervals, significance tests, or error bars. Presenting precision=1.0 on 10 scenarios without confidence bounds is misleading.

**Fix:**
- Add Wilson score confidence intervals for precision/recall.
- Add bootstrap confidence intervals for F1.
- Consider McNemar's test for pairwise tool comparison significance.
- At minimum, report sample size prominently alongside every metric.

---

### Issue #6: Biased Scenario Selection

**Priority:** High
**Area:** Data Collection
**Files:** `src/data/collector.py`

**Problem:**
`_find_merge_commits()` takes the most recent commits first via `iter_commits(max_count=limit)`. Recent merges in mature projects tend to be simpler (version bumps, docs). The junit4 scenarios include `Version.java` and `Test.java` — likely trivial files. This biases toward easy merges where the textual baseline naturally wins.

**Fix:**
- Sample across the full commit history (random sampling instead of most-recent-first).
- Or use stratified sampling: ensure variety in file complexity, change size, and merge difficulty.
- Filter out trivially small files (e.g., files with < 20 lines of change).

---

### Issue #7: No Threats to Validity Discussion — RESOLVED

**Priority:** High
**Area:** Documentation / Presentation
**Status:** Fixed (2026-05-16)

**Problem:**
For a research presentation, threats to validity must be explicitly addressed.

**Resolution:**
Dedicated project-level document created:
[`THREATS_TO_VALIDITY.md`](../THREATS_TO_VALIDITY.md) (covers both
subprojects). Structured by the standard empirical-SE taxonomy and
incorporating the 2026-05-16 adversarial audit:
- **Construct validity:** the equivalence oracle is textual/AST not
  behavioural; transforms 3e.2/3e.9 are normalization-loss (ISSUES #25);
  developer resolution assumed correct; JDime/Mastery tool-family
  confounds.
- **Internal validity:** the comparator was tuned against the residuals
  it scores (overfitting-to-corpus); floor was pre-registered (not
  redefined post-hoc); per-phase attribution self-reported.
- **External validity:** Java-only, single Schesch n=50 corpus,
  recent-merge selection bias (#6), constructive side covers 2/7
  categories.
- **Conclusion/statistical validity:** floor hit with zero margin; 5/32
  Spork TPs depend on the two lossy transforms (disabling them →
  TP 27 / X 25, floor missed); no confidence intervals (#5).
- **Reliability:** unpinned tool Docker images (#10); Rosetta/QEMU;
  preserved `reports/` artefacts are the citable record; a
  non-discriminating regression test was found and fixed during the
  audit.

---

## MODERATE

### Issue #8: Schesch Dataset Integration is Built but Unused — RESOLVED

**Priority:** Moderate
**Area:** Data
**Files:** `src/data/schesch_loader.py`, `config/datasets.yaml`, `src/cli.py`
**Status:** Fixed (resolved together with Issue #1)

**Problem:**
`schesch_loader.py` is fully implemented and tested but was never actually run. This is the easiest path to a credible, larger dataset (Schesch et al. ASE 2024).

**Resolution:**
- Schesch dataset is now the default data source. The `all` and `load-dataset` commands read from `config/datasets.yaml` automatically.
- Run `python -m src.cli load-dataset` (or `make load-dataset`) to load scenarios.
- Re-run the full pipeline: `python -m src.cli all` (or `make all`).

---

### Issue #9: No Per-Scenario Breakdown in Reports

**Priority:** Moderate
**Area:** Reporting
**Files:** `src/evaluation/report.py`
**Status:** **resolved (2026-07-03)** — `to_per_scenario()` (new `per-scenario` format): rows = scenarios, cols = tools, cells = classification; plus the per-scenario heatmap chart (#4). Canonical pivot committed at `reports/per_scenario.csv` (50 × 6). The confusion-matrix-per-tool view was subsumed by the stacked outcome chart.

**Problem:**
Reports only show aggregate metrics per tool. There's no way to see which specific scenarios each tool got right or wrong.

**Fix:**
- Add a per-scenario results table: rows = scenarios, columns = tools, cells = classification (TP/FP/TN/FN/CRASH).
- Add a confusion-matrix-style view per tool.
- This enables qualitative analysis of failure patterns.

---

### Issue #10: Docker Builds Not Reproducible

**Priority:** Moderate
**Area:** Infrastructure
**Files:** `docker/jdime/Dockerfile`, `docker/mastery/Dockerfile`
**Status:** partially advanced (2026-05-18) — image tags now pinned for the
constructive backends: `merge-tools/spork:0.5.0` (Spork JAR was already
release-pinned in `docker/spork/Dockerfile`; the build now also emits the
`:0.5.0` tag, dual-tagged with the legacy `merge-tools/spork` so the empirical
adapter is unaffected) and the new `merge-tools/weave:0.3.2` (multi-stage,
`git clone --branch v0.3.2` + `cargo install --locked --path crates/weave-driver`).
JDime and Mastery still clone unpinned `master`/`main` — the open part of this
issue.

**Problem:**
JDime and Mastery Dockerfiles clone from `master`/`main` without pinning to a specific git commit SHA. Builds on different dates may produce different binaries, making results non-reproducible.

**Fix:**
- Pin each `git clone` to a specific commit SHA (e.g., `git clone ... && git checkout <sha>`).
- Document the exact versions/commits used in README or a `VERSIONS.md`.
- Consider publishing pre-built Docker images to a registry.

---

### Issue #11: Misleading Recall for Mastery/Spork

**Priority:** Moderate
**Area:** Metrics
**Files:** `src/evaluation/metrics.py`

**Problem:**
When `tp + fn == 0`, recall defaults to 0.0 (line 28). For Mastery/Spork, this happens because all their clean outputs were classified as FP (wrong), not because there were no mergeable files. The 0.0 recall hides the fact that these tools attempted to merge everything and failed on all of them.

**Fix:**
- Add a note/flag when recall is 0.0 due to no TP+FN (as opposed to genuinely no mergeable scenarios).
- Consider reporting "attempted merge rate" or "clean output rate" as a supplementary metric.
- At minimum, document this edge case in the report output.

---

### Issue #12: Hardcoded `.java` File Extension in Docker Runner

**Priority:** Moderate
**Area:** Code Quality
**Files:** `src/core/docker_runner.py` (write_workspace_files function)

**Problem:**
`write_workspace_files()` always writes files as `ours.java`, `base.java`, `theirs.java`. If a non-Java file is ever passed (e.g., Kotlin, Scala, XML), the tools that rely on file extension for language detection will fail or produce incorrect results.

**Fix:**
- Extract the file extension from `MergeScenario.file_path` and use it when writing workspace files.
- Pass the extension through the adapter chain so tools receive correctly-named files.

---

### Issue #13: Hardcoded Cost Model Weights

**Priority:** Moderate
**Area:** Metrics
**Files:** `src/evaluation/metrics.py` (lines ~48-50)

**Problem:**
The Schesch et al. weighted cost model uses hardcoded weights: `tp*0 + fp*10 + (fn+tn)*1 + (crash+timeout)*1`. These are not configurable and not documented in reports, making it unclear to readers what the "weighted cost" actually represents.

**Fix:**
- Make weights configurable via `config/` YAML or CLI parameters.
- Document the cost model formula in report output and README.

---

### Issue #14: Missing Tests for JDime, Spork, CLI, and Collector

**Priority:** Moderate
**Area:** Testing
**Files:** `tests/`

**Problem:**
No test files exist for:
- JDime adapter (`src/tools/jdime.py`)
- Spork adapter (`src/tools/spork.py`)
- Docker runner (`src/core/docker_runner.py`)
- Plugin loader (`src/core/plugin_loader.py`)
- CLI commands (`src/cli.py`) — only `load-dataset` caching is tested via `test_schesch_loader.py`
- Data collector (`src/data/collector.py`)
- Error paths: timeout, crash, network failure, corrupted JSON

Note: Mastery adapter **is tested** (`test_mastery.py`, 7 tests).

**Fix:**
- Add unit tests with mocked Docker calls for JDime and Spork adapters.
- Add integration tests for CLI commands using Click's `CliRunner`.
- Add tests for collector with a small fixture repo.
- Add error-path tests: corrupted JSON, missing files, Docker unavailable.

---

### Issue #15: Race Condition in Result Caching

**Priority:** Moderate
**Area:** Code Quality
**Files:** `src/core/runner.py` (line ~102)

**Problem:**
Result caching uses naive `path.write_text()` without file locking. If the framework is ever run with parallel workers, multiple processes could write to the same result file simultaneously, causing data corruption.

**Fix:**
- Use atomic writes (write to temp file, then rename) for result caching.
- Or add file-level locking with `fcntl.flock()`.

---

### Issue #16: No Input Validation on Scenario IDs

**Priority:** Moderate
**Area:** Security / Code Quality
**Files:** `src/data/collector.py` (line ~112)

**Problem:**
Scenario IDs are used directly in file paths without validation. A malicious or malformed scenario ID containing `../` could cause path traversal, writing files outside the intended directory.

**Fix:**
- Sanitize scenario IDs: strip `/`, `..`, and special characters.
- Use `pathlib.Path.resolve()` and verify the result is within the expected data directory.

---

### Issue #17: Docker Platform Hardcoded to `linux/amd64`

**Priority:** Moderate
**Area:** Infrastructure
**Files:** `src/core/docker_runner.py` (line ~36)

**Problem:**
`--platform linux/amd64` is hardcoded. On Apple Silicon Macs, this forces QEMU emulation, adding ~1-3s overhead per invocation and potentially causing subtle behavior differences. On native ARM Linux hosts, this is unnecessary and wasteful.

**Fix:**
- Make platform configurable via `config/tools.yaml` or auto-detect host architecture.
- Default to native platform when possible; only force `linux/amd64` when tool requires it.

---

### Issue #18: Output Truncation Loses Debug Information

**Priority:** Moderate
**Area:** Code Quality
**Files:** `src/core/runner.py` (lines 16-17, in `_serialize_result`)

**Problem:**
stdout/stderr are truncated to 5000 characters during result serialization. For tools that produce verbose error output (stack traces, AST dumps), this may cut off the most important diagnostic information at the end.

**Fix:**
- Keep full output in debug/verbose mode.
- Truncate only for display/logging, not for stored results.
- Consider truncating from the beginning (keep tail) for error output, since the root cause is usually at the end.

---

### Issue #23: Duplicate Per-Tool Rows in Reports (Downstream of #3) — RESOLVED

**Priority:** Moderate
**Area:** Reporting
**Files:** `src/evaluation/metrics.py` (~line 138)
**Status:** **resolved** (2026-05-18) — RM2 R2.

**Problem:**
`compute_metrics()` concatenates the per-tool overall list with the per-(tool, category) list. While categorization is unpopulated (#3), every tool appears in every report twice — once with `category="all"` and once with `category="unknown"` — with identical TP/FP/TN/FN/F1/cost values. Console, CSV, JSON, and LaTeX outputs all carry the spurious rows.

*Phase-0 correction:* the second listed file `src/evaluation/report.py` is **not** involved — `report.py` has no per-category logic and renders whatever rows it is given (the plan's "activate the dead path in report.py" was stale). The entire root cause is the unconditional concat at `metrics.py:138`.

**Resolution:**
- `compute_metrics()` now tracks the distinct category set and appends the per-(tool, category) rows **only when ≥2 distinct categories exist**. A degenerate single-category run (legacy all-`unknown`, or all-`NONE`) emits only the `all` rows — no byte-duplicate. Fixed in `metrics.py` only; `report.py` untouched (deviation from the plan, which named `report.py`).
- With #3 resolved, the regenerated `reports/results.{csv,json,tex}` now carry `all` + genuine per-cluster rows and zero `unknown` rows. Verified before/after: 8 rows (4 tools × identical {all, unknown}) → 24 rows (4 tools × {5 clusters + all}).
- Covered by `tests/test_metrics.py::test_single_category_emits_no_duplicate_rows` and `::test_multi_category_emits_pivot_rows`.

---

### Issue #24: Mergiraf Docker Image `-p` Filename Semantics — RESOLVED

**Priority:** Moderate
**Area:** Infrastructure / Tool Adapters
**Files:** `docker/mergiraf/Dockerfile`, image `merge-tools/mergiraf:0.17.0`
**Status:** Fixed (verified 2026-05-13)

**Problem:**
The `merge-tools/mergiraf:0.17.0` image (built here) is consumed by `semantic_merge_driver/core/backends/mergiraf_backend.py`, which mounts staged files as `/workspace/base`, `/workspace/ours`, `/workspace/theirs` (no extension) and relies on `-p <Path(ours_path).name>` for language detection. If Mergiraf actually inspects the on-disk extension rather than the `-p` hint, the backend silently degrades to text mode for `.java` inputs — defeating the reason for choosing Mergiraf over `git merge-file` as the semantic driver's default backend.

**Resolution:**
Smoke-tested all three combinations against the 0.17.0 image with a discriminating fixture (both branches add a *different* new method at the end of a class — text-mode conflicts, AST-mode merges cleanly):

| Setup | Mode | RC |
|---|---|---|
| extensionless files + `-p Foo.java` (current backend pattern) | **AST** ("Solved 1 conflict") | 0 |
| `.java` files on disk, no `-p` | AST | 0 |
| extensionless files, no `-p` | **text** (conflict markers in stdout) | 1 |

The `-p` hint is sufficient to trigger AST mode even when on-disk filenames are extensionless. Current `MergirafBackend.merge()` invocation is correct as-is. Contract documented in [`mergiraf_backend.py`](../semantic_merge_driver/core/backends/mergiraf_backend.py)'s module docstring.

---

### Issue #25: Tier E transforms 3e.2 / 3e.9 not provably semantics-preserving (defensive hardening — deferred)

**Priority:** Moderate
**Area:** Comparator / Evaluation soundness
**Files:** `src/evaluation/ast_normalize.py` (`_collect_edits` array branch ~382-392; `_normalize_float_token` 584-603), `tests/test_ast_normalize.py`
**Status:** open — deferred to a later cycle (Tier F / hardening pass). **Does NOT block ISSUES.md #2 `resolved`** — see "Audit disposition" below.

**Problem (surfaced by the independent adversarial audit, 2026-05-16):**
Two Tier E transforms are sound *on the Schesch corpus* but not semantics-preserving *in general*. They are normalization-loss transforms whose soundness is dataset-contingent:

- **3e.2 `strip_array_creation_shorthand`.** The branch checks only `node.parent.type in ARRAY_SHORT_PARENTS`; it never verifies the declared variable's component type equals the `new T[]` element type. So `Object[] x = new String[]{"a"}` and `Object[] x = {"a"}` canonicalise EQUAL, erasing the array's runtime component type (`getClass()`, `ArrayStoreException` behaviour differ). `Number[] n = new Integer[]{1}` ≡ `{1}` likewise. Also `var x = new int[]{1,2}` → `var x = {1,2}` (not legal Java; tree-sitter parses it permissively so the fold still runs). The plan does not acknowledge this anywhere.
- **3e.9 `normalize_float_literal_suffix`.** Strips `f`/`F`, so `100f` ≡ `100d` ≡ `100.0`, conflating `float` and `double` (different types; can select different overloads — `f(0.1f)` vs `f(0.1d)`). The plan's own §8 already rates this "Medium — loses semantic info"; §13's "no semantic-change risk has surfaced" overstates it.
- **3e.9 latent correctness bug.** `_normalize_float_token`'s exponent check `"e" in body.lower()` (line ~601) does not recognise hex-float `p`/`P` binary exponents. A hex float with integer significand + suffix, e.g. `0x1p1d`, becomes `0x1p1.0` — **invalid Java**. This contradicts the plan §6 invariant "All Tier E edits preserve the post-edit text's parseability." No occurrence in the n=50 corpus; impact is effectively zero, but it is a genuine defect.

**Audit disposition (why this is deferred, not blocking):**
The 2026-05-16 audit independently reproduced Spork TP 32 / FP 11 and manually confirmed **all 32 TPs are genuine AST-equivalence on this corpus — zero fake TPs**. Disabling 3e.2 + 3e.9 drops Spork to TP 27 / X_total 25 (floor would be missed): **5 of the 30-margin TPs ride on these two transforms** (`adangel_pmd f9c6b0b08d` UnusedImportsRule; `addthis stream-lib` HLLP `59ece5dc87`/`e4a8d65ba1`/`323e301061`/`e221cb6ab7`). Inspection showed every firing was in the sound regime: 3e.2 always had declared-component-type == created-element-type (`Pattern[] = new Pattern[]{}`, `double[]/double[][]` shorthand); 3e.9 only ever normalised `d`/`D` (double↔double, value-preserving), never `f`/`F`. So the current `resolved` status stands, but the floor is met with **zero margin on both bounds** and rests on transforms that are not robust to a different corpus.

**Fix (later cycle — defensive hardening):**
- 3e.2: before stripping, resolve the declared component type and only fire when it equals the `array_creation_expression` element type; skip when the enclosing declarator type is `var`.
- 3e.9: stop stripping `f`/`F` (normalise only `d`/`D`/dotted double forms — those are value- and type-preserving); or gate the `f`/`F` behaviour behind an env-var A/B as the plan §8 mitigation suggested.
- `_normalize_float_token`: return `None` (no-op) for hex floats — detect `0x`/`0X` prefix or `p`/`P` exponent — to restore the parseability invariant.
- Tests: add soundness-boundary cases — `Object[] x = new String[]{}` must NOT canon-equal `Object[] x = {}`; `f` vs `d` literal must NOT canon-equal in an overload-sensitive context; hex-float-with-suffix must remain parseable. (Closes the 3e.2/3e.9 test gap: current tests only exercise the sound happy paths and bake the conflation in as expected behaviour.)

---

### Issue #19: No Network Retry Logic

**Priority:** Low
**Area:** Robustness
**Files:** `src/data/collector.py`, `src/data/schesch_loader.py`

**Problem:**
Git clone operations have no retry logic. Transient network failures (DNS timeout, connection reset) will abort the entire collection run.

**Fix:**
- Add simple retry with exponential backoff (e.g., 3 attempts) for `git.Repo.clone_from()` calls.

---

### Issue #20: No Parallelization of Tool Execution

**Priority:** Low
**Area:** Performance
**Files:** `src/core/runner.py`

**Problem:**
Tools are run sequentially on each scenario. With 4 tools and 100+ scenarios, the total runtime grows linearly. Docker startup overhead (~1-5s per invocation) dominates.

**Fix:**
- Run tools in parallel using `concurrent.futures.ThreadPoolExecutor` or `ProcessPoolExecutor`.
- Or keep Docker containers running and batch-process scenarios.
- Add a `--parallel` CLI flag to opt in.

---

### Issue #21: Dependencies Use `>=` Without Upper Bounds

**Priority:** Low
**Area:** Infrastructure
**Files:** `pyproject.toml`

**Problem:**
All dependencies use `>=` (e.g., `click>=8.0`), allowing major version bumps that could introduce breaking changes.

**Fix:**
- Pin to compatible ranges (e.g., `click>=8.0,<9.0`) or use a lockfile.

---

### Issue #22: Dead Code — `ground_truth.py` — RESOLVED

**Priority:** Low
**Area:** Code Quality
**Files:** `src/data/ground_truth.py`
**Status:** Fixed

**Problem:**
`ground_truth.py` contained a single 4-line function (`get_developer_resolution`) that just returned `scenario.developer_resolution`. It was never imported anywhere in the codebase.

**Resolution:**
- Deleted `src/data/ground_truth.py`.

---

### Issue #26: RM2 file-vs-project recall-delta finding not produced (R1/R2 scope cut) — RESOLVED

**Priority:** Low
**Area:** Evaluation / Methodology
**Files:** `tools/rm2_tag.py`, `tools/rm2_fharness.py`, `tools/rm2_recall_delta.py`, `docs/plans/rm2-integration-recon.md`, `reports_rm2_recall/`
**Status:** **resolved (2026-07-03)** — the n=50 delta is produced (`reports_rm2_recall/FINDINGS.md`). `rm2_tag.py --project-level` landed (fharness worktree machinery + same-file `types_in` filter, cached, fail-closed; 7 Docker-free tests, suite 215 green); run on AWS (4th CLI-DEPLOY cycle, `rm2-recall-delta`, ~1 h, <$1: shipped only the 15 needed clones (604 MB), built the RM2 image natively on x86, probed with toy known-answers + exact reproduction of 3 cached file-level tags; 50/50 tagged, 0 errors, 3.8 min wall). **Finding: pooled file-level recall = 98/108 = 90.7% [83.8, 94.9]** (ours 81.6% [68.6, 90.0], theirs 98.3% [91.0, 99.7]; only-file = 0 → file-level is a strict subset). The R0 n=10 66.7% was an outlier artifact — its sole gap-driver (`ab0oo_javaprslib`) reproduces exactly but is the extreme, not the norm; all 10 missed occurrences are the predicted cross-file Extract/Move family (+1 annotation rider). Cluster impact: 2/50 flip; **1/50 = 2.0% [0.4, 10.5] false-`NONE`** (= 1/18 = 5.6% of the `NONE` bucket) — the only routing-visible kind post-flip, and it fails safe (git = conservative per P2/P3). Framed as methodology/limitation-tightening: THREATS §3 routing-coverage threat now quantified; detection-lane cross-file FN bound ≈9%; no code change recommended (validates file-level R4a).

**Problem:**
R0 reconnaissance ([`rm2-integration-recon.md`](../docs/plans/rm2-integration-recon.md) §5–§6) selected **Path D** and explicitly designated the file-level-vs-project-level RM2 recall delta a *publishable R2 finding* ("on n=10 with RM 2.4.0, file-level recall is 66.7% of project-level … R2 reports the recall delta on the full Schesch n=50, which will tighten this number considerably"). The 2026-05-18 R1/R2 cycle scoped tagging down to **file-level `ours`/`theirs` only** (a deliberate, user-approved decision: it is the cheapest path that fully answers the dispatch-faithful cluster question). Consequence: the n=50 recall-delta number R0 teed up is **not produced**, and until this entry it was deferred with no tracker — a silent loss of a planned deliverable, exactly the kind of plan/code drift this project is trying to avoid.

**Impact:** the R4a runtime classifier is file-level; its known blind spot (cross-file Extract/Move refactorings fall through to `NONE` → Mergiraf default) is currently quantified only at n=10 (R0). The thesis can still state the *direction* (file-level systematically misses cross-file moves) but not the tightened n=50 magnitude.

**Fix (when picked up):**
- Extend `tools/rm2_tag.py` with an opt-in `--project-level` mode reusing the existing git-worktree machinery in `tools/rm2_fharness.py` (`project_level()` + same-file `types_in` filter).
- Tag `ours`/`theirs` at project level for the n=50 cached scenarios; compute the file-vs-project recall delta; report it as the R0-promised finding.
- Cost is the reason it was cut: project-level needs `git worktree` on the ~2 GB `data/repos/` clones (~3× the file-level Docker cost). Cacheable; run once.

---

### Issue #27: Driver `INTRA_BODY → Spork` routing contraindicated by expanded-run evidence (Phase 2)

**Priority:** High
**Area:** Driver routing / Evaluation
**Files:** `semantic_merge_driver/core/backends/auto_backend.py` (S2 arm), `tools/select_materialize.py`, `tools/make_synthetic_spork_cases.py`, `reports_expanded/`, `reports_spork/` (+`_raw`), `reports_ci/` (+`_raw`), `reports_neutral/`, `reports_synthetic/`
**Status:** **resolved (2026-06-27)** — the `auto_backend._route` flip **landed**: default map is now `NONE→git, everything-else→Mergiraf`; the refuted S2 arm is preserved behind the opt-in `SEMANTIC_MERGE_SPECIALIST_ROUTING=1` (apparatus: reproduces the P2 pre-flip behavior; `workspace/e2e_routing.sh` runs flag-on to keep the full-arm mechanism exercised). Driver suite 158 green. **P2 corroborated the DROP in vivo before the flip** (2026-06-26 AWS run, `reports_whole_driver/FINDINGS.md` §4): pre-flip `driver-auto` pooled cost 2055 vs always-Mergiraf 1994; Spork FP **64/79** on its routed INTRA_BODY files; routing verified genuine (chosen==effective 471/471, 0 crash-fallbacks). **Post-flip re-run MEASURED (2026-07-03, @ `9e25b4e`, AWS repaired env): pooled cost 1925 (pre-flip) → 1779; control FPs from routing 21 → 0; derivation confirmed file-for-file (471/471 joined, 100% accept/reject agreement, 2 reject-reason flips = detector nondeterminism); post-flip auto beats always-Mergiraf by 215 via the NONE→git fast-path — the best measured driver config (`reports_whole_driver/FINDINGS.md` v2 §4).** Original decision (2026-05-27): CI-grade Phase-2 evidence, **DROP**: route `INTRA_BODY → Mergiraf`, keep Spork selectable (`SEMANTIC_MERGE_BACKEND=spork`) + comparator baseline. Reproduced across **3 file-level samples (n=6 + n=10 + n=43 INTRA_BODY) + the full 5,405-merge table + a Spork-rigged synthetic battery**; see Updates 2026-05-21 and 2026-05-27.

**Problem:**
The driver's `auto` backend routes the `INTRA_BODY` cluster to Spork (the S2 arm). The first empirical test of that decision — a 60-scenario, tool-discriminating, 50-repo expansion run with the comparator now tracking the driver's backends (`tools/select_materialize.py`, criterion = git-fails / structured-wins) — contradicts it. On the 6 `INTRA_BODY` scenarios:

| tool | TP | FP |
|---|---|---|
| **Spork** (routing target) | 1 | **5** |
| **Mergiraf** (default the router overrides) | **4** | **0** |
| git-merge-file | 1 | 0 |
| weave | 2 | 0 |

Spork produces a clean-but-wrong merge on 5 of 6 `INTRA_BODY` cases; Mergiraf is correct on 4, wrong on 0. So `INTRA_BODY → Spork` routes merges to the *worse* backend here. Spork's whole-set FP rate is also high (27/60) vs Mergiraf (10/60).

**Impact:** Sharpest Phase-2 routing-soundness signal to date (Phase 1 = mechanism wired + synthetic-verified; Phase 2 = soundness on real data). Suggests the S2 arm should route `INTRA_BODY → Mergiraf` instead.

**Update (2026-05-21) — independent confirmation + FP-nature.** A second, dedicated 60-scenario, 53-repo *Spork-focused* run (`CRITERION=spork`: Spork-wins ∪ Spork-wrong-merges) reproduced the signal on a larger, independent sample:

| cluster | Spork tp/fp | Mergiraf tp/fp | n |
|---|---|---|---|
| INTRA_BODY | 5/5 | **6/2** | **10** |
| LOCAL_DECL_EDIT | 2/4 | 4/1 | 6 |
| MIGRATE_DECL | 1/5 | 4/1 | 6 |
| SYMBOL_CASCADE | 1/4 | 3/2 | 5 |
| NONE | 16/17 | 25/2 | 33 |

Mergiraf beats Spork in **every** cluster, INTRA_BODY included (now n=10). Two independent samples (n=6 + n=10) agree.

Separately, **Spork's FP rate is inflated by the exact-match ground truth.** Cross-tabbing Spork's 60 clean merges against the Schesch test-suite label (`reports_spork_raw` = no normalization): 25 match the dev after Tier-E normalization (pure reformatting); of the 35 that still differ, **19 pass tests but ≠ dev (valid alternative merge / cleanup) and 16 fail tests (genuine wrong-merge)**. So Spork's *genuine* error rate ≈ **16/60 (27%)**, not the headline 58% FP — the remainder is comparator-gap, consistent with ISSUES #2.

**Caveat (do not over-claim):** combined n=16 `INTRA_BODY` across two deliberately discriminating sets, so FP rates are upper bounds, not a natural distribution. Still not CI-grade — a cluster-stratified sample is needed for Wilson CIs before flipping the arm. *(Addressed by the 2026-05-27 update below.)*

**Update (2026-05-27) — CI-grade confirmation + per-cluster + runtime + synthetic (closes the evidence gate).** A third, larger, more-neutral sample (`CRITERION=disagree`, 240 scenarios → `reports_ci/` normalized + `reports_ci_raw/` raw) plus a re-run of the neutral Schesch-50 with Mergiraf added (`reports_neutral/`) supply the cluster-stratified Wilson CIs the Caveat asked for.

- *Per-cluster (ci-240, normalized precision):* Mergiraf beats Spork in **every** cluster — INTRA_BODY **0.68 vs 0.43** (n=43), LOCAL_DECL_EDIT 0.54 vs 0.08, MIGRATE_DECL 0.54 vs 0.18, SYMBOL_CASCADE 0.73 vs 0.40, NONE 0.85 vs 0.52; all 0.76 vs 0.43.
- *Pooled INTRA_BODY precision + Wilson 95% CI:* all samples (n_clean 72 vs 63) Spork **0.49 [0.37, 0.60]** vs Mergiraf **0.78 [0.66, 0.86]** — non-overlapping (caveat: pools mixed selection criteria); neutral-only (least-biased) Spork **0.52 [0.39, 0.64]** vs Mergiraf **0.76 [0.63, 0.86]** — large separation, CI edges touch ~0.01.
- *Comparator-gap controlled:* raw (no-normalize) Spork INTRA_BODY 0/42 → normalized 18/24 (the AST-normalizer, built mainly to recover *Spork's* reformatting per #2, lifts 18); applied identically it also lifts Mergiraf (raw 19/19 → 26/12). **Under the same oracle Mergiraf still wins**, so Spork's deficit is not a measurement artifact.
- *Runtime:* across the 146 both-clean scenarios in all samples Spork is faster in **0**; median 7–18× slower (ci-240: Spork 6.3s vs Mergiraf 0.45s). Routing `INTRA_BODY → Spork` would be both less accurate **and** ~14× slower — Spork is Pareto-dominated here.
- *Synthetic capability check:* a 16-case battery hand-built to favor Spork (`tools/make_synthetic_spork_cases.py` → `reports_synthetic/`) yields **0 Spork strict-wins over Mergiraf**; Mergiraf strict-wins 3 (concurrent annotations, records, switch-patterns — Spork-0.5.0 Spoon conflicts/chokes where Mergiraf's tree-sitter merges). Spork beats only git/line-based. Synthetic = Phase-1 capability demo, **not** routing evidence (memory `routing-two-phase`).
- *Full-table prior (n=5405, Schesch test oracle):* Mergiraf 419 > Spork 228 head-to-head; where both merge clean and tests disagree, Mergiraf is right 272 vs 39 (~7:1); the "import-heavy = Spork-favorable" hypothesis is **refuted** (imports are 90% baseline). The only Spork niche is whole-commit robustness when Mergiraf can't parse — already covered by the driver's git fallback.

**Fix (S3 evidence gate now MET — 2026-05-27):**
- ✅ Larger cluster-stratified sample + Wilson CIs — **done** (Update 2026-05-27). The condition the arm-flip was waiting on is satisfied; the evidence is consistent across 5 independent angles, all favoring Mergiraf.
- ☐ Remaining one-liner (deferred): change `auto_backend._route()` so `INTRA_BODY` falls to the Mergiraf default (drop the S2 Spork elif). Keep `SporkBackend` selectable via `SEMANTIC_MERGE_BACKEND=spork` + as a comparator baseline. When this lands, #27 moves `decided → resolved`.
- Cross-ref: `MIGRATE_DECL → Weave` got the same targeted treatment and was **also dropped** — see **#28** (W3 gate, n=38: Weave wins 0 vs Mergiraf, McNemar p=0.0078). Weave is safe-but-conservative (0 FP, 71% abstention); the smoke-tested field-loss bug did **not** dominate real data, but conservatism is not a routing win.

---

### Issue #28: Driver `MIGRATE_DECL → Weave` routing contraindicated by W3 gate (Phase 2)

**Priority:** High
**Area:** Driver routing / Evaluation
**Files:** `semantic_merge_driver/core/backends/auto_backend.py` (W5/MIGRATE_DECL arm), `tools/migrate_decl_w3.py`, `reports_migrate_decl/` (`FINDINGS.md`, `summary.txt`, `scenarios.csv`, `raw_results.json`)
**Status:** **resolved (2026-06-27)** — the `auto_backend._route` flip **landed** (bundled with #27's): default map `NONE→git, everything-else→Mergiraf`; the refuted W5 arm preserved behind `SEMANTIC_MERGE_SPECIALIST_ROUTING=1` (see #27 for flip details). **P2 corroborated in vivo** (2026-06-26, `reports_whole_driver/FINDINGS.md` §4): Weave ran on all 47 routed MIGRATE_DECL files (0 crash-fallbacks), FP 16/47 under the hybrid oracle, contributing to pre-flip auto's 33/239 broken control merges vs 0 for always-Mergiraf. **Post-flip re-run MEASURED (2026-07-03) — see #27 for the full before/after (1925 → 1779; control FPs 21 → 0, of which Weave contributed via 13/47 pooled FP on its routed files).** Original decision (2026-06-01): W3 gate complete, **DROP**: route `MIGRATE_DECL → Mergiraf`, keep Weave selectable (`SEMANTIC_MERGE_BACKEND=weave`) + comparator baseline. Mirrors the Spork verdict (#27). Evidence: `reports_migrate_decl/FINDINGS.md` (n=38, 31 repos).

**Problem:**
The driver's `auto` backend routes the `MIGRATE_DECL` cluster to Weave (the W5 arm), on the hypothesis that Weave's entity-level matching handles declaration-migration extractions Mergiraf can't. The deferred W5 evidence gate ([`weave-integration.md §W5`](../docs/plans/weave-integration.md)) required Weave to *strictly outperform* Mergiraf on this cluster. The W3 run (`tools/migrate_decl_w3.py`) pooled all distinct, already-materialized + RM2-tagged `MIGRATE_DECL` scenarios across `data/scenarios{,_ci,_expanded,_spork}` → **n=38** (31 repos), ran git/mergiraf/weave through the real adapters + the comparator's own `classify_result` under both oracles, joined the Schesch test-suite label for Mergiraf, and computed Wilson CIs + a paired McNemar exact test. It refutes the hypothesis.

**Normalized oracle (n=38):**

| tool | TP | FP | TN(conflict) | precision (Wilson95) | clean-correct |
|---|--:|--:|--:|---|---|
| git-merge-file | 12 | 0 | 26 | 1.000 [0.757, 1.000] | 0.316 |
| **mergiraf** | **19** | 7 | 12 | 0.731 [0.539, 0.863] | **0.500** |
| weave | 11 | 0 | 27 | 1.000 [0.741, 1.000] | 0.289 |

**Two decisive findings:**

1. **Weave wins zero scenarios over Mergiraf (paired, significant).** Paired clean-correct: both 11, Mergiraf-only **8**, Weave-only (the W3 win cell) **0**, neither 19 — McNemar exact **p = 0.0078**. Weave's correct merges are a strict **subset** of Mergiraf's (11 ⊂ 19); on all 7 scenarios where Mergiraf is dev-mismatched, Weave **abstains** (conflict) rather than merging correctly. Weave resolved nothing Mergiraf couldn't; it only declined more (71% abstention). It doesn't even beat git-merge-file (11 vs 12 clean-correct, both 0 FP).
2. **`MIGRATE_DECL` is *not* a Mergiraf weakness under the test oracle — the "opening" was a comparator artifact.** Of Mergiraf's 7 dev-match "FPs", **zero fail the test suite**: 5 **pass** (valid-alternative merges ≠ dev's choice — pure comparator-gap), 2 are whole-merge `Merge_failed` (a different file in the merge; single-file-granularity artifact). By the test oracle Mergiraf has **no confirmed silent errors** on this cluster; the dev-match weakness that motivated a Weave specialist evaporates once tests replace exact-dev-match.

**Impact:** Both hypothesized specialist arms — Spork (`INTRA_BODY`, #27) and Weave (`MIGRATE_DECL`, #28) — are now empirically refuted. The honest `auto` router collapses to `NONE → git-merge-file, everything-else → Mergiraf`. This corroborates and extends the post-Spork recon null result ([`research/outputs/post-spork-tool-gap-recon.md`](../research/outputs/post-spork-tool-gap-recon.md)): not only does no *new* tool beat Mergiraf, the one *integrated* specialist arm doesn't either. The driver's routing contribution reduces to the `NONE → git` fast-path.

**Fix (W3 evidence gate MET — 2026-06-01):**
- ✅ Pooled cluster-stratified sample + Wilson CIs + paired McNemar — **done** (`reports_migrate_decl/`). The condition the arm-flip was waiting on is satisfied.
- ☐ Remaining one-liner (deferred, bundled with #27): drop the `MIGRATE_DECL → Weave` elif in `auto_backend._route()` so the cluster falls to the Mergiraf default. Keep `WeaveBackend` selectable + as a comparator baseline. When this lands, #28 moves `decided → resolved`.

**Caveat:** n=38, one cluster; CIs are wide (Weave precision [0.74, 1.0]), but the *paired* test is significant (discordance 8:0). The single-file dev-match oracle carries finding 1 independently of the whole-merge test-label proxy used in finding 2.

---

### Issue #29: Driver detection layer unvalidated — R1/R2 unmeasured (Stages A–C)

**Priority:** High
**Area:** Driver detection / Evaluation
**Files:** `tools/detect_validate.py`, `tools/select_materialize.py` (`semantic`/`semantic_ctl` criteria + `INTERSECT_MAX`), `data/scenarios_semantic{,_ctl}/`, `reports_detection/`, `semantic_merge_driver/strategies/` (Stage B only)
**Status:** **resolved (2026-07-03)** — all stages + adjudication + the post-fix runs complete. **Citable frozen numbers (Stage C, v2 @ `843e5f5`): R2 flags 11/164 = 6.7% [3.8, 11.6] (+1 fail-closed = 12/164) — **9 CAUSAL of 164 = 5.5% [2.9, 10.1]** after the 2026-09-04 re-ruling (atam4j, tcurdt → DETECTOR-FP; `reports_detection/full/audit_2026-09-04.md`); R1 = 4/193 = 2.1% [0.8, 5.2].** **Post-fix (two labeled rounds on AWS, RM2-lane-only recompute with the four untouched lanes carried at their frozen verdicts): R1 = 0/193 = 0.0% [0.0, 2.0]; R2 = 11/164 (10 flags — 9 causal + atam4j DETECTOR-FP — + 1 fail-closed).** Round 1 (`5ed92a2`: call-site exclusion + char-literal newline fix) cleared 1 of 4 control FPs and *characterized two residual one-char defects* (generics-wildcard `?` missing from the decl-guard type charclass — podam; lambda parameters invisible to the guard — cloudfoundry ×2); it also **retired the tcurdt_jdeb positive flag as defect-dependent** (its only `compression` site is the method call `options.compression()` — the frozen flag existed only because the call-site exclusion was missing; the merge remains a real test failure, the *detector* just can't honestly claim it → R2 12→11). Round 2 (`f964354`: `?` in the guard charclass + lambda-param alternation) → R1 = 0/193 with **zero positive-verdict changes** (verified per-file). All four regression tests proven discriminating (fail on pre-fix code). Evidence: `reports_detection/postfix{,2}/`. Plan: [`outputs/p1-detection-validation-plan.md`](../outputs/p1-detection-validation-plan.md).

**Problem:**
The thesis's surviving constructive claim — the driver catches semantic conflicts in textually-clean merges and converts silent-incorrect (cost ×10) into visible-reject (cost ×1) — rests on four detectors (`JoernDataFlowInterference` #3, `JoernInfiniteLoop`/`JoernInvalidLoopBounds` #5, `RM2RenameConflict` #6) whose false-alarm rate (R1, on clean-and-correct merges) and detection rate (R2, on clean-but-incorrect merges) are **unmeasured**. STATUS honestly frames category #3 as "narrow PoC, FP/FN unmeasured"; this issue tracks converting that into measured numbers with Wilson 95% CIs against the Schesch test-suite ground truth (positives: `mergiraf == Tests_failed`, n=308, 195 at `num_intersecting_files ≤ 3`; controls: `Tests_passed`, pool 3,144).

**Plan (pre-registered, sequence decided 2026-06-10):**
- **Stage A — diagnostic pilot** (30 positives + 30 controls, v1 detectors frozen at current commit): calibrates runtime + Joern crash rate (G0 abort: median >20 min/merge or >30% UNANALYZABLE), G1 inject-sanity positive control (canonical clear→read spliced into 10 control merged-files must fire 10/10), miss-classification of all pilot positives → Stage-B shortlist. Explicitly *not* the citable evaluation.
- **Stage B — evidence-guided detector improvement** (timeboxed; the one sanctioned exception to the no-driver-changes rule).
- **Stage C — full frozen evaluation** of v2 on the complete populations; produces the thesis numbers (G2 freeze; pilot disclosed as the diagnostic that informed v2).

Unit of analysis: per merge, any-file-flag (driver/gitattributes deployment semantics); fail-closed UNANALYZABLE counts as a block. Scoring is against Mergiraf-reproduced merged files (`merge-tools/mergiraf:0.17.0`, the driver's de-facto backbone post-#27/#28); file-level CONFLICT/CRASH → MERGE_DIVERGED, dropped from scoring (counted — itself a granularity finding).

**Progress:**
- ✅ Stage A harness: `semantic`/`semantic_ctl` criteria + `INTERSECT_MAX` + all-intersecting-files materialization with `merge_id` in `select_materialize.py`; `tools/detect_validate.py` (driver-faithful invocation, resumable cache keyed (scenario, detector, driver-commit), G0/G1 gates, R1/R2 + Wilson CIs, `misses_to_classify.csv`); tests in `tests/test_detect_validate.py` (2026-06-11).
- ✅ Stage A pilot run (2026-06-11, v1 frozen at `2eed882`) → [`reports_detection/pilot/FINDINGS.md`](reports_detection/pilot/FINDINGS.md). **All gates passed:** G1 sanity 10/10 fired; G0 median 34 s/merge (≈35× under threshold — Stage C extrapolates to ~3–4 h, shared-CPG not needed for feasibility); **0/64 files UNANALYZABLE** (Joern/RM2 crash rate on real-world Java = 0% in sample). Pilot numbers (n small, not citable): R1 = 1/30 = 3.3% [0.6, 16.7], R2 = 2/25 = 8.0% [2.2, 25.0] — but **all 5 flagged sites are `JoernInfiniteLoop` constant-condition hits present verbatim in base+ours+theirs** (pre-existing deliberate idioms, one an `if(true)`, not merge-induced) → provisional DETECTOR-FP across the board; causal-hit count 0 (the §5 "mechanism sound / categories rare" cell). Granularity finding: 5/30 positive merges lost all files to file-level Mergiraf CONFLICT (scored n=25). **Stage-B shortlist:** (1) make InfiniteLoop differential, (2) restrict its query to WHILE/DO/FOR, (3) exit-path awareness; DFI/bounds/RM2 widening waits on the manual miss-classification.
- ✅ Miss-classification of 23 unblocked positives **ADJUDICATED 2026-06-11** — Ali reviewed all 23 via the side-by-side `review_ui.html` and accepted every draft label (23/23). Final labels in `misses_to_classify.csv`. **Base rates (n=23): #6-family rename/decl-change interference 8 (35%; 62% of 13 attributable, 5 confirmed compile errors), none-of-7 5, none-identified (scored files ≡ dev) 9, indeterminate 1; categories #1–#5/#7 zero.** **Stage-B scope is now final:** (priority) widen R3 — RM2 rename types beyond Method/Class + per-branch RM2 (base→ours/base→theirs, reuse `rm2_tag`) + merged-consistency scan for the inverse rename shape + cheap unresolved-identifier check; (secondary, R1-motivated) InfiniteLoop differential + WHILE/DO/FOR-only + exit-awareness. DFI/loop-bounds widening: no evidence — 0/23 misses in covered categories.
- ✅ **Stage B complete (2026-06-11, code in `semantic_merge_driver/` — the sanctioned exception):** (B1) `RM2RenameConflict` v2 — rename types widened to Variable/Parameter/Attribute (RM2 2.4.0 codeElement shapes image-probed; constant renames NOT reported by the image), per-branch RM2 on (base,ours)/(base,theirs), mixed-state + declaration guards; (B2) **new `JoernUnresolvedReference` strategy** — differential-only unresolved-identifier detection (`refsTo`-based; abstains without parents; `$`-synthetics excluded; name-only keys after two stopped pilot runs exposed parser version-instability; a type-resolution lane for import-deletion was **built and dropped** — javasrc2cpg type inference is version-unstable on real files, so the jnr shape stays uncovered pending a compile-check oracle); (B3) `JoernInfiniteLoop` v2 — WHILE/DO/FOR-only, break/return/throw exit-aware, differential. Driver suite 151 green (+17); comparator harness runs all 5 strategies driver-faithfully (182 green). **v2 on the same pilot sample (`reports_detection/pilot_v2/FINDINGS.md`): R1 1/30→0/30, R2 2/25 with both hits now TRUE detections (erudika dual-lane, jacquesberger both dangling halves) vs v1's 0 causal; 0 UNANALYZABLE; 68 s/merge.** v2 catches 2/8 adjudicated #6-family misses; each remaining miss has a named limitation (cross-file, external-API, constant-rename, return-type). **Evidence correction surfaced:** blockchain's "confirmed compile error" withdrawn (Joern shows `baseURL` declared; mixed-rename behavioral, label #6 stands) — 4 confirmed compile errors, not 5.
- ✅ G2 freeze: v2 committed at `843e5f5` (2026-06-12).
- ✅ **Stage C frozen run complete (2026-06-12)** → [`reports_detection/full/FINDINGS.md`](reports_detection/full/FINDINGS.md). Populations: 195 positives → 180 materialized (15 upstream-lost) → 164 scored (16 all-diverged); 195 controls → 193 scored. **R2 = 12/164 = 7.3% [4.2, 12.4]** (11 FLAG — all rename/decl-interference shapes, 4 dual-lane, 9 outside the pilot; 1 fail-closed RM2 crash); **R1 = 4/193 = 2.1% [0.8, 5.2]** — all 4 traced to two one-line var-lane defects found mid-run and left per freeze protocol (missing `(`-exclusion ×3; comment-stripper newline bug ×1). G1 10/10; 1/443 UNANALYZABLE; 74 s/merge median. **Category base rates hold at scale: #3/#5 = 0 detections AND 0 FPs on 443 real files** — detection mass is entirely the #6 family. STATUS §strategies + THREATS (§3 bullet + row 14) updated with measured numbers.
- ✅ **§4.6 hit adjudication DONE (Ali, 2026-06-20, via `adjudication_ui.html` — `reports_detection/full/make_adjudication_ui.py`):** all 15 flags ruled, **every draft label accepted (0 overrides)** → final `reports_detection/full/hit_adjudications.md`. **R2: all 11 detector flags = CAUSAL at the time** (11/11) → **AMENDED 2026-09-04 (Ali, on `reports_detection/full/audit_2026-09-04.md`): 9/11 CAUSAL, 2 DETECTOR-FP** — atam4j (flagged L27 is the surviving declaration; the file compiles; the break is in the unflagged sibling `PassingTestAcceptanceTest.java` = a measured cross-file FN) and tcurdt (`options.compression()` is a method call; the `(`-defect; already retired post-fix). Citable "**9 CAUSAL of 164 = 5.5% [2.9, 10.1]**"; flag precision 9/15 overall. **R1: all 4 control flags = confirmed DETECTOR-FP**; the 06-20 claim "no causal hit depends on either defect" is withdrawn (tcurdt did), and the two-defect account is replaced by the post-fix evidence (round 1 cleared aerospike only; round 2's guard extensions cleared the rest). comatoes ruled CAUSAL via the Joern `gameState` lane (its RM2 rename pairing is an ambiguous artifact). FINDINGS/STATUS/THREATS row 14 updated.
- ✅ **Post-fix runs DONE (decided + executed 2026-07-03, two labeled rounds on AWS):** round 1 (`5ed92a2`) applied the two identified one-line fixes → R1 4→3 (characterized two residual one-char guard defects + retired the defect-dependent tcurdt positive flag); round 2 (`f964354`, decided with Ali) extended the decl-guard (generics `?`, lambda params) → **R1 = 0/193 = 0.0% [0.0, 2.0], R2 = 11/164, zero positive-verdict changes between rounds (verified per-file)**. Methodology: RM2-lane-only recompute, four untouched lanes carried at frozen verdicts, fresh G1 sanity each round (10/10), regression tests discriminating. **#29 → `resolved`.**

---

### Issue #30: In-the-wild taxonomy of merge-induced silent failures unmeasured (taxonomy-refresh program, Sessions 0–4) — RESOLVED

**Priority:** High
**Area:** Evaluation / Taxonomy
**Files:** [`outputs/taxonomy-protocol.md`](../outputs/taxonomy-protocol.md) (pre-registered protocol), `prompts_taxonomy/` (Phase-1 template + output schema committed; Phase-2/3 skeletons with data-dependent slots), `data/scenarios_semantic/` (stratum A, reused from Stage C), `data/scenarios_taxonomy_hi/` (stratum B, Session 1), `reports_taxonomy/`
**Status:** **resolved (2026-07-12)** — all four sessions complete, gates G0–G3 all PASS. **Citable one-liner: closed coding of the full 275-unit silent-incorrect census against the frozen 8-category codebook measured the first CI-bearing mechanism base rates — 119/275 = 43.3% [37.5, 49.2] attributable to a named mechanism (the name-binding family = 85/119 = 71.4% [62.7, 78.7] of attributed, corroborating Stage C by an independent method), 156/275 = 56.7% [50.8, 62.5] not-cleanly-merge-attributable (first-class escape stratum), residual-other = 0 (the codebook generalizes to all 110 held-out units); double-pass stability 82.9% [78.0, 86.9] / κ 0.788 (after the single sanctioned Amendment 2), Ali reliability 12/12 sampled agreements accepted [75.8, 100].** Never blend with Stage-C R1/R2 or Phase-2b. Evidence: `reports_taxonomy/FINDINGS.md` + `summary.txt` + `labels_final.csv`. Session history: S0 protocol frozen (2026-07-09, four rulings); S1 pipeline + G0 PASS; S2 Phase-1 batch + G1 PASS (Ali spot-check 2026-07-10); S3 Phase-2 + G2 PASS (Ali APPROVE 2026-07-11) → codebook FROZEN (`3e7d9b4`); S4 Phase-3 double batch + G3 PASS (Ali adjudication 2026-07-12) → FINDINGS (summary below).

**Problem:**
The 7-category taxonomy (ResearchSummary.xml) is a *design* taxonomy; Stage C measured that its covered categories carry near-zero mass in the wild (#3/#5 fired 0 times on 443 files; all detection mass in the #6 family), and the Stage-A miss adjudication (n=23) is the only empirical view of what actually breaks — too small to design detectors against. No measured, CI-bearing base rates exist for failure *mechanisms* over the real silent-incorrect population (`mergiraf == Tests_failed`, n=308).

**Plan (pre-registered — see the protocol for gates G0–G3 with pass criteria fixed in advance):**
- **Phase 1** — LLM open coding (claude-opus-4-8, Batch API) on the seeded 60% derivation split: per-side changes, interaction point, mechanism drafts with open-vocabulary tags, verbatim-quote evidence, mandatory escape hatches (none-identified / indeterminate / flaky-suspect — designed against confident hallucinated causality, the pilot-established #1 failure mode). Gate G1: attribution ≥ 35%, escape band [15%, 65%], Ali spot-checks 15 drafts (≤ 3 rejections).
- **Phase 2** — consolidation into a mechanism-granularity codebook (claude-fable-5 interactive with opus-4-8 fallback); old→new mapping over the 7; four-family regrouping tested against the clusters, not imposed. Frozen at a named commit after Ali adjudicates (G2: ≥ 90% coverage).
- **Phase 3** — closed coding of the **full census** with the frozen codebook, run twice → stability (G3: agreement ≥ 80%, κ ≥ 0.70); Ali adjudicates all pass-disagreements + a stratified reliability sample (40–60 units, ≥ 75% acceptance) via a visual UI. Deliverable: per-category base rates + Wilson CIs, per stratum and pooled.
- **Firewall for future detector work:** codebook derived from derivation units only; held-out 40% contents never quoted in codebook or detector-design docs; detector eval later runs on held-out + spgroup. **Never blend with Stage-C R1/R2 or Phase-2b numbers** — new labeled evaluation.

**Progress:**
- ✅ Session 0 (2026-07-09): protocol + Phase-1 prompt/schema + Phase-2/3 skeletons committed; API workload smoke-tested (`workspace/api_smoke_test.py`); budget ≈ $90–110 with batch pricing + prompt caching.
- ✅ Session 1 (2026-07-09): data pipeline + G0 PASS (summary below).
- ✅ Session 2 (2026-07-09→10): Phase-1 batch DONE + **G1 = PASS** (i+ii machine, iii Ali spot-check ruled criterion-scoped 2026-07-10; summary below).
- ✅ Session 3 (2026-07-10→11): Phase-2 codebook draft + **G2 = PASS** (machine i–iii + Ali APPROVE 2026-07-11); codebook **FROZEN** (8 categories, 2 `vs`-renames applied) + Phase-3 enum frozen in one freeze commit (summary below).
- ✅ Session 4 (2026-07-11→12): Phase-3 double batch + **G3 = PASS** (stability after Amendment 2 + Ali reliability adjudication) + `labels_final.csv` + `FINDINGS.md` + STATUS/THREATS updates → **#30 resolved** (summary below).

**Session 1 summary (2026-07-09, commits `87424be`→final).** The S1 data pipeline is built and **G0 passed**; handoff to S2 is committed artifacts only. `tools/select_materialize.py` gained an `INTERSECT_MIN` complement filter (stratum-B = the `>3 intersecting files` complement of the ≤3 Stage-C pool), a blobless-extraction crash guard, and by-SHA fetch of unreachable merge parents (this recovered the 19 `merge-base`-"unresolved" B merges → 0). Stratum B materialized to `data/scenarios_taxonomy_hi/` at **111/113** merges (2 transient extract losses); stratum A reuses the Stage-C 180-materialized/164-scored artifacts. Applying the divergence rule over the pinned Mergiraf cache (`merge-tools/mergiraf:0.17.0`; A from `reports_detection/full/raw_results.json`, B newly produced in `reports_taxonomy/mergiraf_hi.json`) gives a **scored population of 275** (A=164, B=111); the full census accounting (275 scored + 16 divergence-dropped + 17 materialization-loss = 308) is in `reports_taxonomy/units.csv`. The seeded 60% derivation split (`split_assignment.csv`, `SEED=20260709`, stratified A/B → derivation 165 / held-out 110) was computed and **committed before any content-bearing API request** (§4 firewall). Single-file `javac` compile-deltas (`eclipse-temurin:17-jdk`, PARSE/RESOLVE/OTHER) are complete for all **798** scored files (`compile_checks.json`; 33 carry a merged-minus-dev delta). The T0–T3 assembly ladder (measured with `count_tokens` against `claude-opus-4-8`) keeps **every unit ≤ 30k** — a pre-G0 revisit (protocol §5, ordinary edit) strengthened T3 to a hard-fit search (reduce file cap 12→1, then truncate per-diff line counts) because 18 pathological units overflowed the fixed T3; stratum-B at-T3 = 23/111 = **20.7% ≤ 25%**. `manifest.json` pins the §9 fields (protocol commit `9209327`, prompt blob SHAs, mergiraf + javac image IDs, seed + split hash, 853 scenario SHA-256s, Phase-1 request params). **G0 = PASS** (batch `msgbatch_01B3n7tikcL5WUoGmKKyTjME`; 10 derivation units = 7 A / 3 B): 10/10 conforming structured outputs, all `end_turn`, 0 over-cap, escape-hatch plumbing exercised (3 attributed / 3 indeterminate / 4 none-identified); pilot outputs are **discarded** and the 10 units relabel in the S2 real run. **§12 Amendment 1** records the one forced deviation — the custom_id wire-encoding, because the Batches API rejects the frozen `p1::<merge_id>` notation (pattern `^[a-zA-Z0-9_-]{1,64}$`); the logical per-phase per-merge key is unchanged.

**Session 2 summary (2026-07-09).** Phase-1 open coding ran on the **165 derivation units only** (§4 firewall — held-out got zero content-bearing requests) via `tools/taxonomy_phase1.py` (adapts the G0 pilot; resumable multi-batch cache in `reports_taxonomy/phase1/{raw_results,batches}.json`; recovery strictly by inverting the submit-time `{custom_id: merge_id}` map). Single batch `msgbatch_015zPxvSVtcKHuMRs86SLaTo` (`claude-opus-4-8`, structured outputs, adaptive thinking, effort high, cached system prefix): **165/165 succeeded, all `end_turn`, 0 errored**; in=2.45M / out=485k tok ≈ **$12.20** at batch rate. Assembly reused `assemble_best` unchanged so the text is byte-identical to G0 — truncation ladder reproduced exactly (T0:118 / T1:2 / T2:29 / T3×15; max **29,870 ≤ 30k**). The batch was slow to finalize (0/165 for ~2 h, then a late burst; the first 2 h-budgeted poller exited on its self-timer — a spurious `tee`-to-missing-dir exit-1, no data lost — and a re-attach with a longer budget collected it). **G1 machine conditions PASS** (`tools/taxonomy_g1_eval.py` → `phase1/summary.txt`): (i) attribution **60/165 = 36.4% [29.4, 43.9] ≥ 35%** floor (A 37.8%, B 34.3%); (ii) escape-hatch **105/165 = 63.6% [56.1, 70.6] ∈ [15%, 65%]** (A 62.2%, B 65.7%). Both clear with **modest margins** (attribution just over the floor; escape near the ceiling — honest caveat). Verdict split attributed 60 / indeterminate 56 / none-identified 46 / flaky-suspect 3; `merge_induced=yes` count (60) coincides exactly with the attributed set, and high confidence never attaches to an escape hatch — internal consistency checks out. §8 covariate clean: attribution does **not** collapse on truncated units (T0 34.7%, T2 44.8%, T3 31.2%, CI-overlapping). Open-vocabulary tags: **166 distinct across the 60 attributed**, overwhelmingly the #6 name-binding/import/rename family (stale-caller-of-changed-signature ×5, stale/removed-import, unresolved-symbol, half-applied-api-migration …) — corroborates the Stage-C "all mass in #6" base-rate finding, but this is Phase-2 input, not gated here. **Quote-provenance precheck (auxiliary, not a gate): 0/225 attributed-unit evidence quotes are ABSENT** under graded matching (208/225 exact; the rest differ only by diff-gutter/whitespace or concatenate non-contiguous diff lines) — a strong R4-compliance signal, and the reason the spot-check UI grades matches rather than a brittle exact-substring test. **G1 condition (iii) is PENDING Ali:** `tools/taxonomy_spotcheck_ui.py` drew a seeded (20260709) stratified **5 high / 5 medium / 5 low-or-escape** sample and rendered `reports_taxonomy/phase1/spotcheck/spotcheck_ui.html` (make_adjudication_ui.py-style; per draft shows the exact model input, the mechanism/tags/quotes, per-quote verbatim-in-input badges, and accept / reject-hallucinated / reject-unsupported controls). Pass rule: ≤ 3/15 rejected. **G1(iii) ruled by Ali 2026-07-10 → PASS (criterion-scoped); G1 = PASS overall.** Raw tally 11 ACCEPT / 4 REJECT-UNSUPPORTED, but the gate scores rejections *"as hallucinated or unsupported-by-quotes"* (§7 iii) and **all 4 rejections are escape-hatch verdicts** (3 indeterminate + 1 none-identified) rejected for *"not a good representation of the silent merge conflicts"* — a population/selection objection that agrees with the escape-hatch call, not a labeling defect; **0/11 mechanism-claiming drafts were rejected** (the confident-hallucination failure mode did not fire), so 0/15 qualifying → PASS. Applied as-written (gate criterion already scopes by reason), ruled by Ali, so **no §12 amendment**; full record in `reports_taxonomy/phase1/spotcheck/g1_iii_adjudication.md` (+ `spotcheck_rulings.csv`). **Marked Phase-2 carry-forward:** Ali's population concern is logged — the 63.6% escape-hatch mass is a first-class "not-cleanly-merge-attributable" stratum for the FINDINGS honest-coverage accounting (whole-merge `Tests_failed` admits failures caused outside the intersecting files or nondeterministically); does not reopen the frozen §2 population. `manifest.json` records the batch id, full request params, prompt/schema blob SHAs, and the `phase1.g1` verdict block (now `g1_overall = PASS`). Handoff to S3 is committed artifacts only.

**Session 3 summary (2026-07-10, commits `f5935ba`→`8a2b916`).** Phase-2 consolidation into a mechanism-granularity codebook. **Ordering (S3 requirement): the Phase-2 prompt wording was finalized + committed (`f5935ba`) BEFORE any `{PHASE1_TAGS}` content was read or assembled** — visible in the git log (finalize → commit → then `tools/taxonomy_phase2.py` assembled the data). **Workload call (pinned):** `claude-fable-5`, interactive `beta.messages.stream` (NOT batch — `fallbacks` is rejected there), `betas=["server-side-fallback-2026-06-01"]`, `fallbacks=[{"model":"claude-opus-4-8"}]`, **no `thinking` param** (Fable 5: always on), `output_config={"effort":"xhigh"}`, streamed. **Served by `claude-fable-5`** (no fallback fired; `usage.iterations` carried no `fallback_message`), `stop_reason=end_turn`, 312 s, response `msg_011CctsTSGUwQxTqmKfECJJF`, 32,814 input tok (~a few $). Assembly was **derivation-only** (165 units = 60 attributed / 105 escape-hatch), each row restricted to the seven §6 fields (unit_id, stratum, verdict, confidence, tags, mechanism.summary, interaction_point); the runner asserts no non-derivation id enters the table (§4 firewall). **Codebook draft (`reports_taxonomy/phase2/codebook_draft.md`): 8 mechanism categories + `residual-other`.** The #6 name-binding family **dominates** — 4 categories (`import-pruning-vs-concurrent-usage` 15, `stale-caller-of-changed-signature` 14, `stale-reference-to-removed-declaration` 9, `stale-reference-to-renamed-or-relocated-declaration` 7) = **45/60 = 75%** of attributed units, corroborating the Stage-C "all detection mass in #6" base-rate finding; the rest are `changed-behavior-vs-stale-expectation` 5, `overlapping-edit-interleaving` 5, `duplicate-concurrent-addition` 3, `insertion-anchored-to-relocated-code` 2. **Old→new mapping (all 7):** Atomic Updates + Loop Semantics Divergence = **no empirical counterpart observed**; DFI/Stale Read + CFI + Scope Capture = no standalone category (partial counterparts absorbed); Exception Handling = an instance of the signature-change mechanism; Method Rename splits three ways (renamed/removed/re-signatured). **Four-family view REJECTED as a primary scheme** (would lump 75% into "name-binding" and shear the two tool-artifact categories apart) — kept the empirical clusters; it survives only as a secondary descriptive axis. **G2 machine conditions (i)–(iii) all PASS** (`tools/taxonomy_g2_eval.py` → `phase2/g2_eval.md`, no revision round needed): (i) coverage **60/60 attributed mapped, residual 0/60 = 0.0% ≤ 10%**, firewall OK (every anchor + coverage `unit_id` is a real derivation unit — 0 held-out/phantom), 0 missing / 0 extra / 0 dup; (ii) **9/9 categories** structurally complete (id/name/mechanism/definition/inclusion/exclusion/anchors/boundary), all 25 anchors derivation-only, 0 symptom-named ids; (iii) 7/7 historical mapped + four-family written. **G1(iii) carry-forward honored:** the draft preamble states the codebook covers the 60 attributed units only and names the 105 escape-hatch units as the first-class **not-cleanly-merge-attributable** stratum reported in FINDINGS — no categories invented for them. **Condition (iv) is PENDING Ali:** `tools/taxonomy_mapping_ui.py` rendered `reports_taxonomy/phase2/mapping_ui.html` (make_adjudication_ui.py-style; per category ACCEPT/RENAME/EDIT/MERGE/SPLIT/REJECT + reason, each anchor enriched with its Phase-1 summary/tags + a firewall badge, plus the old→new mapping table, four-family text, an escape-hatch-stratum acknowledgment, and a top-level APPROVE/REVISE ruling; exports rulings JSON+CSV + copy-for-Claude). Verified rendering in-browser (all screens display, controls work, no console errors; serve via `.claude/launch.json` `taxonomy-g2-ui`, port 8745). **STOP point:** no `codebook_frozen.md`, no filled `prompts_taxonomy/phase3_output.schema.json` category enum, and no Phase-3 request exist — per §7 the freeze is one commit gated on Ali's (iv) ruling; on APPROVE apply rulings → write `codebook_frozen.md` + freeze the Phase-3 schema enum → single FREEZE COMMIT recorded in the manifest; on REVISE one sanctioned Fable-5 round pre-freeze. `manifest.json` records the full `phase2` request params, served model / fallback detection, response id, usage, and the `phase2.g2` verdict block. Handoff is committed artifacts only. **G2 condition (iv) — Ali ruled APPROVE 2026-07-11** (`g2_codebook_rulings.json`; overall confirmed in-session as the UI export left `overall=null`, escape-hatch framing acknowledged): 2 RENAME + 7 ACCEPT, no merges/splits, categories 3/4 (`stale-reference-to-renamed-or-relocated-declaration` / `stale-caller-of-changed-signature`) kept **split** per Ali, category 6 kept. The two `vs`-named categories were renamed (id + display name) to the relational style of their siblings: `import-pruning-vs-concurrent-usage` → **`stale-usage-of-pruned-import`**, `changed-behavior-vs-stale-expectation` → **`stale-expectation-of-changed-behavior`**. `tools/taxonomy_freeze.py` applied the rulings (APPROVE-guarded; RENAME/ACCEPT only, id-collision-checked) and wrote the **single freeze commit's** two frozen artifacts: `reports_taxonomy/phase2/codebook_frozen.md` (draft + renames + a frozen provenance header) and the filled `prompts_taxonomy/phase3_output.schema.json` category enum (primary = the 8 frozen ids + `residual-other` + the 3 escape hatches; secondary = 8 + `residual-other`; skeleton note removed). Verified: old ids/display-names absent from the frozen body, 9 headings (0 `vs`), coverage 60/60 with every category defined, schema enum complete. `manifest.phase2.freeze` records the ruling, renames, frozen artifacts, and both enums; the §9 `frozen_codebook_commit` sha is pinned at Phase-3 time (S4), pointing back to this commit. **STOP point honored: no Phase-3 request exists.** Next = S4 (Phase-3 double Batch + G3 + FINDINGS).

**Session 4 summary (2026-07-11→12, commits `a8734c7`→final).** Phase-3 closed coding + G3 + FINDINGS; the program's final session. **Pre-request pinning honored:** manifest `phase3` block (frozen_codebook_commit `3e7d9b4`, prompt/schema/assembler blob SHAs, full request params) committed BEFORE any Phase-3 request existed (`a8734c7`); the finalized `phase3_closed_coding.md` inlines the frozen codebook §1–§4 **verbatim** but deliberately **excludes §5** (the 60-unit derivation coverage table = an answer key) so the closed relabel stays independent. **Double batch** (`tools/taxonomy_phase3.py`; per-unit assembly byte-identical to Phase 1, verified on-disk for all 165 derivation units — a CRLF/read_text false-alarm in the byte-identity guard was fixed before submission, no API waste): two request-identical passes over all 275 scored units, 275/275 conforming each, all `end_turn`, ≈$38.3/run. **G3.1 first ran YELLOW** (78.9% [73.7, 83.3], κ 0.741, 58 disagreements): the instability was NOT the taxonomy — only 3/275 named↔named flips — but the `none-identified`↔`indeterminate` boundary (35/58). **§12 Amendment 2** (Ali APPROVE 2026-07-11): one R1 clarification operationalizing that boundary (nameable ours×theirs candidate interaction vs positive non-interaction; no category/enum/threshold change); per §9 the cache was invalidated wholesale — yellow run archived to `phase3/yellow_v1/`, **both passes fully rerun** on the amended instrument. **Rerun = controlled comparison → G3.1 PASS:** 228/275 = **82.9% [78.0, 86.9]**, **κ 0.788**, 47 disagreements; the targeted bucket fell 35→21 while named↔named stayed at noise (3→6). **G3.2 (Ali, 2026-07-12) PASS:** adjudication set = all 47 disagreements + seeded (20260711) stratified sample of 12 agreeing units (min-3 × the 4 largest agree categories; 47+12 ≤ 60 cap) via `phase3/adjudication/adjudication_ui.html`; **12/12 sampled agreements ACCEPTED = 100% [75.8, 100]** (0 overrides), 47/47 disagreements ruled (22 pass-a / 25 pass-b / 0 third-label). Two-draft process with code-level review (`adjudication_record.md`): 4 flags — notably one pass's ruling candidate was **rejected for fabricated evidence** (quoted conflict markers appearing nowhere in its input; caught by the human gate → THREATS §4.4.9) and the byte-identical enderstone fork twins were aligned. **Final labels** (`labels_final.csv`, `tools/taxonomy_finalize.py`): 216 agree + 12 sampled-accepted + 47 Ali-ruled. **FINDINGS** (`reports_taxonomy/FINDINGS.md` + `summary.txt` + `phase3/findings_stats.json`): attributed **119/275 = 43.3% [37.5, 49.2]** (top: pruned-import 12.7%, changed-signature 10.2%, interleaving 6.5%, renamed/relocated 5.8%; tool-artifact categories ≈10%); **name-binding family 85/119 = 71.4% [62.7, 78.7] of attributed** (30.9% of scored — three independent methods now agree on #6-family dominance); **escape stratum 156/275 = 56.7% [50.8, 62.5]** (none-identified 32.0% / indeterminate 24.0% / flaky 0.7%) as the first-class not-cleanly-merge-attributable mass; **residual-other = 0/275** (upper bound 1.4% — the frozen codebook covered all 110 held-out units); attribution stratum-robust (A 43.3% vs B 43.2%) and truncation-robust (T0 40.6% / T2 54.0% / T3 42.3%); secondary labels rare (8.0% of units) with mean cross-pass Jaccard 0.942. THREATS §4.4 (12 items incl. the n=12 gate width, the mid-study amendment discipline, fork-duplicate census rows) + summary row 16; STATUS taxonomy block added; old→new mapping + four-family rejection carried into FINDINGS §4 unchanged. **Never blend with Stage-C R1/R2 or Phase-2b.**

---

### Issue #31: Taxonomy's top mechanism categories have no detectors — detector cycle D1–D3 (Sessions S-D0–S-D6)

**Priority:** High
**Area:** Driver detection / Eval
**Files:** [`outputs/detector-cycle-plan.md`](../outputs/detector-cycle-plan.md) (FROZEN plan + §12 amendments — the authority), `reports_detectors/` (manifest, controls, specs), `prompts_detectors/`, `tools/detector_controls_draw.py`, `tools/detector_specs_batch.py`
**Status:** **resolved (2026-07-20)** — all gates PASS (GD1, GD2 ×3, GD3 re-judged by Ali, GD4 complete). **Citable (held-out, adjudicated-CAUSAL only, suite frozen `732d8ff`): pooled name-binding-family recall 2/37 = 5.4% (baseline) → 16/37 = 43.2% [28.7, 59.1] (experimental) — added recall 14/37 = 37.8% [24.1, 53.9]; all-category 4/110 = 3.6% → 18/110 = 16.4% [10.6, 24.4]; D1 `ImportPruneUsage` own-category 13/14 = 92.9% [68.5, 98.7] at 14/14 unit precision. Zero adjudicated false positives across 363 control units** (100 tune + 197 eval-controls + 66 spgroup-clean; the two raised flags — jgralab, jOOQ "Grr Git" — both Ali-ruled INCIDENTAL-BUT-TRUE: real breakage outside the pools' label constructs). D2 measured honestly at 0 (file-local ceiling); D3 widening 0-causal/1-FP on unseen data (same-package residual, 2 instances measured). Lanes stay behind `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1`; default-enabling deferred (plan §2 N2). Never blend with taxonomy/Stage-C/Phase-2b. FINDINGS at `reports_detectors/FINDINGS.md`. **S-D7 follow-on complete (2026-07-22):** blend-safe Stage-C-instrument before/after — machine R2' 6.7% → 22.0% [16.3, 28.9], R1' 0 → 2/193, both flags Ali-ruled INCIDENTAL-BUT-TRUE 2026-07-22 (incl. D2's first real-data catch, developer-confirmed by the next upstream commit) — 0 adjudicated FPs on this instrument's 193 controls; FINDINGS §10.

**Problem:**
The #30 taxonomy measured where the silent-failure mass actually is: name-binding family 71.4% of attributed, led by `stale-usage-of-pruned-import` (12.7% of scored), `stale-caller-of-changed-signature` (10.2%), and the removed/renamed-or-relocated declaration pair (~8%) — but the driver detects only slices of the third group (RM2RenameConflict + JoernUnresolvedReference; import-deletion breakage explicitly not covered since Stage B dropped the type lane). The two largest categories have **no detection logic at all**. This cycle builds D1 `ImportPruneUsage` (new), D2 `SignatureStaleCall` (new), and D3 (evidence-guided widening of the existing lanes), validated per-category on the untainted held-out split with the standing zero-FP bar.

**Plan:** pre-registered in the frozen [`outputs/detector-cycle-plan.md`](../outputs/detector-cycle-plan.md) — §2 decisions (incl. N1 no-LLM-in-detectors), §3 firewall/freeze discipline, §4 corpus assets, §5 gates GD1–GD4, §7 one-session-per-step (S-D1 specs/controls → S-D2/3/4 builds → S-D5 frozen evaluation → S-D6 adjudication+FINDINGS; optional S-D7/S-D8 decided at S-D6). New numbers are a **fourth instrument — never blend** with taxonomy base rates, Stage-C R1/R2, or Phase-2b.

**Progress:**
- ✅ S-D0 (2026-07-16): plan frozen (`10b7528`); §11 items 1–3 ratified by Ali.
- ✅ S-D1 (2026-07-16): control draws committed first + spec-extraction batch + gap inventory + **GD1 = PASS** (via §12 Amendment 2 scope ruling; summary below).
- ✅ S-D2 (2026-07-16): D1 `ImportPruneUsage` built + fixture battery + **GD2 = PASS** (one sanctioned tuning iteration; summary below). Addendum same day: post-review fixes `bed3638`, gates rerun green (suite 197/197, tune 0 flags).
- ✅ S-D3 (2026-07-16): D2 `SignatureStaleCall` built + fixture battery + §12-Amendment-3 triple review + **GD2 = PASS** (zero tuning iterations; summary below).
- ✅ S-D4 (2026-07-16/17): D3 lanes widened (`732d8ff`) + fixture battery + §12-Amendment-3 triple review (8 FP-vector fixes pre-gate) + **GD2 = PASS** — first FULL 7-lane composition run, 0 flags on the 100 tune-controls (summary below).
- ✅ S-D7 (2026-07-22, follow-on): Stage-C-protocol rerun DONE — baseline reproduced the frozen post-fix verdicts 2215/2215 (env gate PASS); machine before/after **R2' 6.7% → 22.0%**, R1' 0 → 2/193; **both control flags Ali-ruled INCIDENTAL-BUT-TRUE (2026-07-22)** — 0 adjudicated FPs on this instrument's 193 controls (summary below).

**Session S-D6 summary (2026-07-20, FINAL — program CLOSED).** Entry-state paste-time patch (noted per plan header rule): the pre-written S-D6 prompt assumed "GD3 PASS" — actual state was GD3-STOPPED; resolved in-session by Ali's two rulings BEFORE any number was applied. **GD3 re-judged PASS: both control flags ruled INCIDENTAL-BUT-TRUE** (jgralab — real breakage in the 0.17.0-reproduced merge, control label a mergiraf-version-skew artifact; jOOQ — the developer's own shipped merge broken, their "[#3992] Grr Git" commit restores exactly the dropped imports; the latter doubles as external validation of D1). No amendment, no rerun; zero-FP record final: **0 adjudicated FPs / 363 control units**. **GD4 PASS (completeness): 20/20 held-out flagged units adjudicated** via the UI — 22 lane rows, all with written rationales; Ali accepted all 20 probe-verified drafts (18 CAUSAL / 2 DETECTOR-FP; every draft was verified against unit sources — presence tables, JLS rules, body diffs, and real-repo probes that: confirmed the commons-collections/mcprotocollib/jOOQ breakages from post-merge history ("Fix missing imports??", feature back-out), flipped dabsquared to FP via the extracted same-package class file at the merge commit, and flipped scribble to FP via the still-declared "renamed" method). **Adjudication convention recorded:** rulings judge the merged artifact; a dev-identical resolution is noted, never a downgrade — 10/18 causal units were dev-identical (2 developer-confirmed), 8/18 mergiraf-specific. **Citable numbers** (adjudication/causal_numbers.json via apply_rulings.py): family 5.4% → **43.2% [28.7, 59.1]**, added **37.8% [24.1, 53.9]**; all-category 3.6% → **16.4% [10.6, 24.4]**; D1 own-category **13/14 = 92.9%**, D1 unit precision **14/14**; RM2Rename 3/4 (scribble partial-split misread — name-level granularity); UR[Joern] 3/3 incl. two tool-artifact-category catches (any-lane rule, outside the family pool); D3-widened 0/1 (same-package residual measured at 2 instances incl. the mcprotocollib sub-flag inside a causal unit); D2 0 flags = honest ceiling per its S-D3 decomposition, with D1 cross-covering the import-visible relocation slice (vojtechhabarta). FINDINGS.md + summary.txt shipped (never-blend banner, Amendment-2 ceiling report, TUNING-TAINTED derivation block, dev-identical section, threats). Close-out: THREATS_TO_VALIDITY.md + STATUS.md updated (lanes remain flag-gated; default-enabling deferred); **S-D7/S-D8 decision (Ali, 2026-07-20): BOTH GREEN-LIT to run now.** S-D7 (Stage-C-protocol rerun, extended suite): the only blend-safe before/after on the Stage-C instrument — worth one cycle while the infrastructure is warm. S-D8 (whole-driver re-pricing, lanes ON): completes the enabling-decision input immediately rather than reopening cold later. Kickoff prompts instantiated below from the plan §8 stubs (both inherit the §3 freeze at `732d8ff` and never-blend; the frozen plan file is untouched — §8 itself provides for instantiation on S-D6 green-light). Manifest: GD3/GD4 verdicts, causal numbers, session rows.

**S-D7 kickoff prompt (paste into a fresh session at the repo root):**
```
Session S-D7 of the detector cycle — ISSUES #31 follow-on (green-lit at
S-D6, 2026-07-20). AUTHORITY: outputs/detector-cycle-plan.md §8 stub + §3
freeze (suite commit 732d8ff — NO detector edits; any change = dated §12
amendment) + never-blend. Paste-time check against ISSUES #31 done.
STATE: #31 resolved; S-D5 eval harness tools/detector_eval_run.py proven;
Stage-C frozen numbers R2=11/164 (12/164 incl. fail-closed), R1=0/193
post-fix (@ f964354 lanes; R1 frozen-instrument history in #29).
FIRST — AMBIGUITY CHECK: as always; ask Ali and WAIT on anything material.
SCOPE: the blend-safe before/after R2/R1 on the STAGE-C INSTRUMENT's own
populations (data/scenarios_semantic 164 pos / scenarios_semantic_ctl 193
ctl): run BOTH arms with the S-D5 two-arm harness pattern (baseline = 5
default lanes flag OFF — MUST reproduce the frozen Stage-C verdicts as the
known-answer env gate; experimental = FULL 7-lane suite flag ON) on one AWS
cycle per CLI-DEPLOY (budget ~2.4x-Stage-C lesson: expect ~$8-12; shard
work-queue or seeded half-shards, not naive merge-count shards). detect_
validate.py stays FROZEN — do not edit it; the new runs live in
reports_detectors/stagec_rerun/. Report R2'/R1' per arm + deltas (Wilson),
fail-closed separately, per-lane attribution; flags on the 193 controls
gate NOTHING automatically but any experimental-arm control flag goes to
Ali with a package (Stage-C controls overlap the S-D5 instrument's
exclusions — these are the ORIGINAL 193). NEVER blend with S-D5 numbers in
any derived figure; the deliverable is the before/after table on this one
instrument. EXIT: numbers + FINDINGS addendum + manifest block + ISSUES
#31 addendum. STOP.
```

**Session S-D7 summary (2026-07-22, follow-on; suite unchanged at `732d8ff`, zero detector edits, zero §12 amendments).** The blend-safe before/after on the STAGE-C INSTRUMENT's own populations, per the §8 stub. **Ambiguity gate: no material ambiguities → proceeded without waiting;** trivial clarifications (session log, recorded in the manifest block): (1) the kickoff STATE-line "R2=11/164 (12/164 incl. fail-closed)" conflates rounds — the reproducible target at the frozen suite is postfix2's **11/164 = 10 flag + 1 fail-closed** (12/164 = 11+1 was the pre-fix frozen instrument @843e5f5); (2) "MUST reproduce the frozen Stage-C verdicts" operationalized as file×lane verdict + merged-content-sha equality vs `reports_detection/postfix2` — stronger than unit-number equality; (3) work-queue sharding (S-D5 static-shard lesson); (4) new harness `tools/detector_stagec_rerun.py` (`d63d5e9`) — `detect_validate.py`, `detector_eval_run.py`, and every lane untouched; (5) taxonomy-split membership rows reported as labeled corpus-fact context only. **AWS sixth cycle** (`i-01b7db6337b2bd523`, c7i.2xlarge, ~9.5 h ≈ $4 vs the ~$8–12 budget; images built on-instance, transfers checksum-verified, teardown verified empty): smoke 8/8 → tune_d3 known-answer 42/42 → 4 work-queue workers over 180+195 merges (8 lane-execs/file; queue completeness 180/180 + 195/195) → on-instance score (authoritative; local re-score byte-identical). **Env gate PASS at three layers**, the S-D7-specific one being: baseline arm ≡ frozen post-fix Stage-C run **verdict-for-verdict — 471/471 merge outcomes, 443/443 merged sha256, 2215/2215 file×lane verdicts** (R2' baseline 11/164 = 10+1, R1' 0/193); plus 1,871 overlapping S-D5 cache keys, 0 disagreements (descriptive). **Machine before/after (unit = merge, Stage-C BLOCKED semantics, Wilson): R2' 11/164 = 6.7% [3.8, 11.6] → 36/164 = 22.0% [16.3, 28.9]** (via-FLAG 10→36, fail-closed 1→0 — the `progether_jadventure` RM2-invocation fc unit is D1-FLAG-blocked in the experimental arm), added blocked 25/164 = 15.2% [10.5, 21.5], 0 nestedness violations; **R1' 0/193 → 2/193 = 1.0% [0.3, 3.7]**. File-level attribution (pos, exp): D1 23, UR[Joern] 6, UR[D3-widened] 5, RM2 7, D2 0. Context (labeled, corpus-fact): the 164 scored positives = 98 derivation-split (7→22 blocked; tuning-tainted for the exp arm) + 66 held-out-split (4→14). **Both experimental-arm control flags packaged and RULED — Ali, 2026-07-22, both INCIDENTAL-BUT-TRUE (`stagec_rerun/ctl_flag_package.md`; the jgralab ruling followed an explicit FP challenge resolved against the four-version differential):** `jgralab_jgralab__d631209030` (D1; 9 bare `IOException` uses, no covering import, 0.17.0-reproduced merge only — dev resolution has 0 uses; same repo + version-skew class as the S-D5 flag Ali ruled incidental-but-true) and `yubico_ykneo-openpgp__2766bd7444` (**D2's first real-data flag**; full chain ours-arity-2→3 / theirs-adds-2-arg-tests / merged-declares-only-3 with 12 stale sites; merged **byte-identical to the developer's shipped resolution**, and the immediate next upstream commit `de02622` "Fix tests for PDOs" converts exactly the flagged calls — developer-confirmed breakage invisible to the `Tests_passed` label construct). Artifacts: `reports_detectors/stagec_rerun/` (summary, units CSVs, flags, known_answer, crosscheck, package) + FINDINGS §10 + manifest `stagec_rerun` block. NEVER BLEND: Stage-C-instrument numbers only. **Paste-time note for S-D8:** the S-D7 rerun changes nothing S-D8 depends on (suite still `732d8ff`, flag-gated); rulings landed 2026-07-22 (both incidental-but-true) — no amendment, no rerun, freeze intact.

**S-D8 kickoff prompt (paste into a fresh session at the repo root):**
```
Session S-D8 of the detector cycle — ISSUES #31 follow-on (green-lit at
S-D6, 2026-07-20). AUTHORITY: outputs/detector-cycle-plan.md §8 stub + §3
freeze (732d8ff) + never-blend. Paste-time check against ISSUES #31 done.
STATE: #31 resolved; P2/P3 whole-driver baseline measured (post-flip auto
= 1779 pooled cost @ 9e25b4e, reports_whole_driver/FINDINGS.md);
experimental lanes validated but flag-gated.
PARALLEL-RUN NOTE (added 2026-07-22 — S-D7 runs CONCURRENTLY in another
session): (1) do NOT create or delete the `p2key` key pair or S-D7's
security group — reuse the existing ~/.ssh/p2key.pem for this cycle's
instance (or create a differently-named key), and teardown ONLY this
session's own instance id + SG; (2) if run-instances returns
VcpuLimitExceeded the account cap is 8 vCPUs — wait for S-D7's teardown
and run serially; (3) `git pull` before starting AND again before any
ISSUES.md/manifest.json close-out edits (S-D7 will likely close out
first); commit early, never rebase away the other session's commits.
FIRST — AMBIGUITY CHECK: as always; ask Ali and WAIT on anything material.
SCOPE: P2-style whole-driver re-pricing with the experimental lanes ON —
tools/whole_driver_eval.py pattern over the P1 corpus (164 pos / 193 ctl,
471 files), config pair driver-auto (flag OFF; must reproduce the
post-flip 1779 within nondeterminism bounds — env gate) vs driver-auto
(SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1), Schesch cost model + repaired
scoring env (canonical six-tool table reproduction incl. the gjf probe —
the arm64 lesson). One AWS cycle per CLI-DEPLOY (~20h-class; budget
~$10-15; latency per file will rise — record the detection-latency delta
as a first-class result, it IS the enabling-decision price). Deliverable:
cost table + blocked/broken decomposition + latency; the DEFAULT-ENABLING
DECISION itself stays out of scope (Ali decides post-S-D8 with the
numbers). Artifacts → reports_detectors/whole_driver_flagon/. EXIT:
FINDINGS addendum + manifest + ISSUES #31 addendum. STOP.
```

**Session S-D8 summary (2026-07-22..23, follow-on; suite unchanged at `732d8ff`, zero detector edits, zero §12 amendments).** Whole-driver re-pricing with the experimental lanes ON, per the §8 stub. **Ambiguity gate: two material items, both asked and RULED by Ali 2026-07-22 before any run** (recorded as paste-time patches in `reports_detectors/whole_driver_flagon/RUN_NOTES.md`): (1) the kickoff's literal-1779 env gate is unsatisfiable at the frozen suite (which includes the #29 post-fix commits `5ed92a2`+`f964354`) → **derived-target gate**: pre-registered per-file prediction (`tools/sd8_predict_flagoff.py` → `predicted_flagoff.csv`, committed `50d2754` BEFORE launch) = 1779 shifted by exactly the five adjudicated post-fix movements → **1784**; both arms stay at HEAD (pinning flag-OFF to `9e25b4e` would smuggle the post-fixes into the flag delta); (2) image provisioning split by reproducibility — pinned images built on-instance, unpinned jdime/mastery shipped as the exact canonical-table amd64 bits. New harness `tools/whole_driver_flagon.py` (`whole_driver_eval.py` imported, untouched); config pair `driver-auto-off`/`-on` differs ONLY by `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS`. **AWS seventh cycle** (eu-north-1 — Ali asked to run parallel with S-D7; per-region vCPU quota gives true concurrency with zero shared resources; `i-0006f73fee2019c40`, c7i.2xlarge, ~23.5 h ≈ $8.5 vs the $10–15 budget; teardown verified empty): lane-pytest + harness smoke → **canonical six-tool gate PASS (36/36 count rows exact, Spork 32/11)** → flag-OFF arm → **reconciliation gate PASS: measured 1784 = pre-registered 1784 to the digit** (5/5 post-fix movements on exactly the predicted files; only the 2 documented borderline textual↔semantic flips, cost-identical) → flag-ON arm → report. **Headline: pooled Schesch cost 1784 → 1579 (−205, −11.5%) — the best driver configuration measured to date** (always-Mergiraf 1994; P3 post-flip 1779 @ `9e25b4e`). Decomposition: 25 files moved, all accept→semantic-reject — **23 positive-arm silent-wrongs surfaced** (D1 19, D3-widened-UR 4; cost 10→1 each) + **2 control blocks (+1 each): the SAME jgralab-D1 + yubico-D2 flags S-D7 packaged and Ali ruled INCIDENTAL-BUT-TRUE** (both Mergiraf-routed under auto → identical merged content → rulings transfer 1:1; whole-driver control cost of the lanes = 2/239 files, both true-in-artifact). **Latency (the enabling-decision price, first-class): +8.3 s/file median (79.5→87.8, +10.4%), p90 +9.7, uniform across arms/routes**; within-arm drift symmetric (+6.6/+6.5 s first-vs-last-100 — corpus-order, not warm-box; sequential arm order does not confound). Ops notes: first-launch `PendingVerification` in the new region cleared in ~10 min (documented gotcha); mid-run local-IP rotation broke the SG /32 — instance unaffected, rule updated (add to the runbook's long-poll checklist). Artifacts: `reports_detectors/whole_driver_flagon/` (summary, env_gate, scenarios.csv, raw cache, logs) + FINDINGS §11 + manifest S-D8 block. **The default-enabling decision stays out of scope — Ali decides post-S-D8 with the cost/latency pair (−205 vs +8.3 s/file).** NEVER BLEND: whole-driver cost-model instrument only.

**Session S-D5 summary (2026-07-16..19, STOPPED at GD3 per plan §5).** Freeze FIRST: `detector_suite_commit = 732d8ff` recorded in the manifest (`21dcda1`) after a 340/340 suite rerun and an empty `732d8ff..HEAD` driver diff — before any evaluation. **Ambiguity gate: no material ambiguities → zero §12 amendments;** trivial clarifications (session log): held-out/derivation inputs = the S1-materialized scenario JSONs (`scenarios_semantic` A / `scenarios_taxonomy_hi` B), machine-verified 836/836 against the taxonomy manifest's committed sha256 pins — the prompt's "materialize" applies to eval-controls + spgroup only; machine-caught = FLAG only per §9 (UNANALYZABLE reported separately); baseline arm ≡ the frozen Stage-C 5-lane DETECTORS flag-OFF, experimental ≡ the tune-runner FULL_SUITE flag-ON; the 4 lanes that never read the flag (source-scan tripwire) execute once and serve both arms (paired design — the added-recall contrast carries no Joern re-run noise); added recall = experimental-only catches/n (arms provably nested, 0 violations) so Wilson applies directly; spgroup = developer-merged phase2b pattern, experimental arm only. **Two-arm harness** `tools/detector_eval_run.py` (`0e4b35b`): arm+flag-keyed resumable shard caches (`::flag0/::flag1/::flagX` namespaces; the S-D4 `::exp1` lesson), closed-world message-STEM verdict classifier (the S-D3 prefix note; drift quarantine — 0 rows), D3-widened vs Joern attribution by message stem, per-(lane,flag-state) smoke gate incl. a new old-lane flag0 UnresolvedReference positive, known-answer env validation vs the committed tune_d3 GD2(iii) cache, sha-pin integrity gate on held-out loading. Local pre-flight on tune contents only: smoke 8/8, known-answer 42/42, shard/resume/score plumbing PASS. **AWS fifth cycle** (`i-0a3193cadee961264`, ~40.3 h, ~$17–18 vs ~$5–10 §10 estimate — structural: 8 lane-execs/file × 1,751 files, Joern-bound, CPU-saturated at 4 shards; CLI-DEPLOY record + `eval/runs.md` incidents: materializer CSV fix `027ec4c` after run 1 died post-materialization on the first spare row; static-shard imbalance → seeded half-shard surgery on evalctl recovered ~10 h; local `--score` briefly overwrote instance artifacts with an evalctl-less view — restored from the pulled tarball, completeness guard added post-run). **Eval-controls materialized on-instance under Amendment 1**: 200/200 effective (120/80), 832 files, TWO deterministic replacements (`urbanairship_datacube__61755d7739` clone_fail → spare#1 `pablissimo_sonartsplugin__6a86fcb79d`; `ymnk_jsch-agent-proxy__be10f22b86` extract_fail → spare#25 `valotrading_silvertip__9d31f81110`) — recorded in manifest. Spgroup quadruples verified byte-identical to a fresh rematerialization from the pinned clone (@`04a1801`). **Held-out machine numbers (110/110 scored; adjudication pending — GD4)**: baseline 5/110 = 4.5% [2.0,10.2] (+1 UNANALYZABLE-only), experimental **20/110 = 18.2% [12.1,26.4]**, added **15/110 = 13.6%**; pooled name-binding family **2/37 → 16/37 = 43.2% [28.7,59.1]**, family added **14/37 = 37.8% [24.1,53.9]**. Per-lane (exp arm, file rows): **D1 ImportPruneUsage 16** (13/14 of its category's held-out units — generalizes at near-derivation strength), UnresolvedRef[Joern] 6, RM2Rename 4, **D3-widened 1** (a `dabsquared` indeterminate unit — the probe-correction prediction held: bare-receiver shapes are BASELINE catches), **D2 SignatureStaleCall 0** (consistent with its 0/14-in-reach decomposition). Derivation (TUNING-TAINTED, descriptive): 11/165 → 39/165; family 5/48 → 30/48. spgroup-positives (descriptive) 0/17 — unchanged from Phase-2b (benchmark mass sits in uncovered #1/#2). **GD3 GATES: (ii) baseline 0/197, experimental 1/197 — `jgralab_jgralab__d1a767cb2d`; (iii) 1/66 — `jOOQ__d96120f327__org.jooq.impl.DSL`; both flags = D1, both packaged in `eval/gd3_flag_package.md` with execution-verified evidence:** jgralab's mergiraf-0.17.0-reproduced merge keeps 9 bare `IOException` uses with no covering import (JLS 6.5.5 — uncompilable; control premise = the dataset-mergiraf Tests_passed column, a version-skew class); jOOQ's **developer-shipped** merge dropped both `org.jooq.conf` imports while keeping 34 bare `Settings` uses — dataset byte-identical to the real repo file, and the next mainline commit `9e404cff0f` **"Grr Git"** (2015-01-28) restores exactly those imports (benchmark label is the behavioral-interference construct). STOP per plan §5 — the amendment path is Ali's. **S-D6 UI delivered** (`adjudication/adjudication_ui.html`, generator `de04302`): 20 held-out flagged units (15 experimental-only), per-lane CAUSAL/REAL-BUT-INCIDENTAL/DETECTOR-FP + rationale, localStorage + CSV export. **Paste-time notes: S-D6** — GD4 rulings = the UI's export; citable recall counts CAUSAL only; per-lane precision from the per-lane rulings; the file-local ceiling report owes S4/S5 + D2's 0-in-reach decomposition + the D1-dominance reading; never blend. **If a GD3 flag is ruled DETECTOR-FP** → dated §12 amendment + full S-D5 rerun (freeze discipline); if INCIDENTAL-BUT-TRUE → record the ruling in the manifest GD3 block and proceed to S-D6.

**Session S-D4 summary (2026-07-16/17, lane commit `732d8ff`, artifacts final).** Widened the D3 lanes for the S-D1 gap-inventory file-local shapes — a **flag-gated TEXTUAL removed/renamed-declaration differential added to `JoernUnresolvedReference`**; `RM2RenameConflict` deliberately untouched (no inventoried shape is an RM2-record shape; jline S1b is covered without RM2 exactly as the inventory sketch predicted). **Ambiguity gate: no material ambiguities → zero §12 amendments;** trivial clarifications (session log): (1) plan §2 N2 "widened lanes run under the flag" + GD3's two arms resolve to *flag-gating only the widened paths* — the host lane stays default-on and its flag-off behavior is byte-identical (the §3 regression floor's mechanism); (2) "widen the lanes (plural)" is satisfied where the evidence points — all four in-reach shapes are resolution differentials, none rename-record shapes, so the widening lands in one lane; (3) GD2(iii) "FULL suite incl. D1/D2" = the S-D5 experimental-arm composition (all 5 default lanes + D1 + D2, flag ON) — first time it runs together anywhere; (4) plan §3's "122 green" is stale as in S-D2/S-D3 — actual pre-session baseline **292**, floor applied as all-green + no verdict change. **Design (probe-driven, Stage-B style):** live-Joern probes on minimal unit reconstructions CORRECTED two S-D1 lane-fire verdicts before any code — the bare-receiver S1/S1b shapes (datastax `isShutdown.get()`, jline `nonBlockingInput.peek`) **already fire the existing lane** (a name ABSENT from the removing parent is not in that parent's unresolved set — the inventory's "both-parents guard self-defeats" conflated absent with unresolved; dated addendum appended to `specs/gap_inventory.md`, GD1 floor unaffected), while the genuinely Joern-invisible shapes are `this.`-qualified field refs (yandex — fieldIdentifier nodes), method calls (S2), and type/ctor refs (S3). The widening is therefore textual (the D1 lesson: exact-text evidence instead of the dropped javasrc2cpg lane), one engine × three kinds: **candidate** = name kind-declared in base + EXACTLY ONE parent (keeper), gone from remover and merged — var-kind candidates from the FIELD tier only (declarators directly inside a named type body, brace-depth checked); **signal** = kind-matched merged reference (var: bare + `this.`-qualified non-call, never case/multi-case labels, statement labels, annotation-element names; method: unqualified calls via D2's probed site classifier by adapter; type: `new`/`extends`/`implements`/`throws`-anchored); **guards** = remover-absorption (BROAD matchers, suppression-only — kills the pull-up/move-refactor class structurally) vs keeper-attribution (precise), kind-matched import coverage, shadowing/enum-constants, D2's absorbable spans + Object names + static imports (method kind), java.lang + surviving type imports (type kind, and var kind per JLS 6.5.2 receiver re-binding). Deliberate span-suppression ASYMMETRY documented in-lane: method sites inside supertyped bodies absorb (JLS 15.12.1); var/type sites do not (yandex extends AbstractPGProcess, gwt extends FormElementContainer — suppression would zero both units; the differential carries the burden; registered residual = re-binding to identical inherited field/nested type/same-package type when the remover also dropped every use). All 6 in-reach units flag on reconstruction; **all Joern behavior and all flag-off behavior byte-identical** (dedupe: widened names seed the Joern loop's seen-set; Joern-failure fail-closed now carries widened findings along — genuine evidence wins in verdict_of, flag-off shape pinned by test). **§12 Amendment 3 triple review (BEFORE the definitive gate run; record at `reports_detectors/tune_d3/review_record.md`):** *(a)* /code-review high, 8 angles, 19 candidates → **8 execution-verified FP-vector fixes**: multi-declarator `int a, b;` + C-style `int b[];` (comma-chain walk + `[` follower; refuted the header's "neutralized" claim), `case MODE ->` phantom declarations, lambda/local scope-blindness (→ field-tier candidates), JLS 6.5.2 receiver re-binding under a surviving type import, statement labels after `)`/`else`, **Java 14 multi-label `case FOO, MODE:` fixed at the root in the shared `_ipu._FileView._qualified_or_case` — the one existing-lane touch (D1 inherits; Amendment-3 gate rerun = this session's 340/340 suite + the FULL tune run, both including D1)**, and type-kind remover absorption blind to bare positions (broad `_type_mentions`/`_method_mentions` for the remover side only); plus harness adoptions (D2 call-site classifier reused by adapter, factored FP-critical guard tail, FULL_SUITE↔LANES asserts, tune cache keys hardened with a working-tree dirty-digest + `::exp1` namespace vs the frozen Stage-C keys, argparse rc-2 lane validation, per-scenario save batching, type-regex drift-tripwire test). Non-fixes with reasons (separate-strategy altitude — §6 lane-name mandate, message-prefix attribution instead; regex-copy hoisting — tripwire over touching more gated lanes; O(k·n) line counting — immaterial vs subprocess dominance; per-scenario durability — deliberate; Joern-differential message text — Stage-C artifacts cite it verbatim). *(b)* standalone JLS review: 8/8 probes (super.f exclusion 15.11.2, assert-position reads, ctor-only removal ≠ type removal 8.8, record headers 8.10, varargs-removal coverage, generic methods, plain-interface default-method calls FLAG vs extends-interface absorb 9.2/15.12.1). *(c)* OSS comparison (`review_oss_comparison.md`): Error Prone (javac-resolved only; zero-FP ERROR-check policy = citable precedent), SpotBugs (bytecode — the defect class is structurally pre-compile/merge-time), IntelliJ (red-code-on-incomplete-model = environment noise; rename residue demoted to human-previewed textual search — our suppression replaces that gate), Checkstyle (the architectural relative: resolution-free single-file analysis viable only with documented shape limits), + three-way-differential prior art (SafeMerge OOPSLA18, IntelliMerge/RefMerge, Towqir ASE22 build-conflict detection = nearest neighbor); nothing ported, no new runtime deps. **GD2(i)** 57 new tests (63 total in the lane suite incl. 8 review-FP regressions + tripwire), suite **340/340** (292-baseline verdicts unchanged; Stage-C postfix regression tests untouched and green). **GD2(ii)** battery per shape + wiring + guard + cross-category negatives (see manifest). **GD2(iii): definitive run at `732d8ff` PASS — 0 flags, 0 UNANALYZABLE over the FULL 7-lane composition** (100 merges, 1701 file×lane rows, 1673 CLEAN / 28 DIVERGED = the four known mergiraf-conflict files × 7; zero tuning iterations post-review; run mechanics — aborted pre-review run, 4-lane harvest, 4 parallel shards, unified re-scoring pass — documented in `tune_d3/runs.md`; local execution per the plan's GD2 exception, with the caveat that the FULL composition measured ~6.5 h serial locally vs the plan's 1–2 h guess → sharded to ~2 h). **Deliberately NOT covered (shape-level rejected list, FP-risk-beats-coverage):** S4 cross-file relocation + S5 cross-file/external API rename (out of file-local reach by construction — no (base,version) pair of any unit file shows the declaration change; Amendment-2 ceiling, S-D6 FINDINGS obligation); jdeparser boundary case (removal visible, no stale site in-unit — nothing to flag); and sub-shape non-covers documented in the lane header: both-parents removals + mergiraf-dropped-declarations (no side attribution), bare type positions in MERGED-site matching (locals/params/casts/generics/annotations — remover-side broad matcher does see them), `this.`-qualified method calls, multi-item throws/implements tails, type-parameter shadowing, anonymous-class fields, partial overload removals (name-level granularity; arity-level = D2's lane), casts before a ternary colon. **Paste-time notes: S-D5** — the tune caches are tune-side; eval materializes fresh (Amendment 1) and the new two-arm harness should adopt the `::exp1`-style key namespacing + flag-state separation (the frozen Stage-C instrument's keys are flag-blind); attribute D3-widened vs Joern mechanism by the message prefix "Stale reference to a removed/renamed declaration"; expect datastax/jline-shaped held-out units to be BASELINE-arm catches (gap-inventory addendum) — D3's added-recall delta should come from yandex-shape/S2/S3 units; a Joern env failure with a widened finding classifies FLAG (genuine wins — deliberate), without one it stays UNANALYZABLE; FULL-composition runtime ≈ 10 Joern spawns/file locally — budget accordingly or lean on the AWS cycle (plan §8 already routes S-D5 there). **S-D6** — the file-local ceiling report now includes S4/S5 + the sub-shape rejected list above; cite the probe correction when interpreting D3 per-category rows. (2026-07-16, lane commit `6523ab0`, artifacts final).** Built D2 `SignatureStaleCall` — detector for `stale-caller-of-changed-signature` (10.2% of the #30 census): side X changes a method's arity in this file (per-branch RM2 `Add Parameter`/`Remove Parameter` on (base, X) — the probed contract of `merge-tools/refactoring-miner:2.4.0`); side Y adds or keeps a call with the OLD argument count; the merged file combines them. **Ambiguity gate: no material ambiguities → zero §12 amendments;** trivial clarifications (session log): (1) **arity is the only signal** — plan §2 names it primary + orders FN-over-FP, and the S-D1 note frames the same-arity rest (return/param-type/throws, 4/8 usable specs) as the conservative-bias call: flagging them would revive the dropped Stage-B type-inference approach → documented FNs; (2) **per-file reach** — the driver is a git merge driver (analyze() sees one file); the prompt's own "cross-file targets the file-local view cannot type" guard confirms; (3) "reuse, don't fork" vs "no changes to existing lanes" resolved by **composition** (internal `RM2RenameConflictStrategy` supplies `_run_rm2_pair`; D1's `_FileView`/stripper imported AS MODULES — importing strategy classes by name would double-register them in `plugin_loader`, now pinned by a loader-dedup test); (4) missing base/ours/theirs → abstain-clean (D1's experimental-lane convention), RM2/infra failure → fail-closed "inconclusive" (rename-lane β-pattern); (5) harness extension per the S-D2 note — `detector_tune_run.py` LANES became a registry of (class, smoke builder), and tune_d2 seeded merge reproductions from tune_d1's lane-independent `::__merge__::` cache keys. **Evidence chain (all must hold):** exactly one (old,new) arity pair for the name on X, none on Y (concurrent-edit guard); no varargs in either signature nor any `name(… ...)` form in base/ours/theirs/merged (JLS 15.12.2.4); merged declares the name at the NEW arity and NOT at the old (overload guard — Java has no default arguments); ≥1 UNQUALIFIED merged call at the old arity (constructors: `new Name(…)` only — JLS 8.8, never inherited; methods: `new`-prefixed rejected; `expr.`/`this.`/`super.`/`::` excluded = the builder/chained + cross-file guards); the site is not absorbable (bodies of supertyped types, enums (implicit `extends Enum`), anonymous classes — JLS 15.12.1 resolves unqualified names through inherited members of every enclosing class; `java.lang.Object` method names suppressed everywhere; static/type imports of the name suppress); X's text has NO old-arity call (self-consistency) and Y's HAS one (attribution). **RM2 contract probes** (image-gated tests): Add/Remove Parameter carry full old/new METHOD_DECLARATIONs (`name Type` params, ` : ret` suffix — absent for constructors; varargs as `Type...`; generics unspaced); multi-param adds emit one record per param with identical full decls (set-dedupe); **kept-overload emits nothing** (the core FP-safety pin); constructors ARE reported when statement matching succeeds. **Honest coverage decomposition (derivation D2 units, n=14):** 5 cross-file out-of-target (Amendment 2) + 1 truncation; of the 8 usable — 4 same-arity shapes (FN by design), buddycloud + sonar-findbugs have cross-file declarations (call-site-drift inference deliberately rejected: overload guard impossible without seeing the declaration), enderstone's declaration and stale calls live in DIFFERENT files of the unit (per-file runtime cannot join them), and jcabi's replace-helper resolves in RM2 as **Rename Method repo()→repos(), not Add Parameter** (probe on the real bodies) — rename-lane territory. **Net: 0/14 derivation units are expected catches for this lane**; it targets the category's same-file arity-change shape (census mass says the shape exists at scale; the derivation sample simply holds none in reach). S-D5 measures held-out recall; the Amendment-2 file-local-ceiling reporting obligation extends to this decomposition (S-D6). **GD2(i)** 95 new tests, suite **292/292** (197-baseline verdicts unchanged). **GD2(ii)** battery: positives P1–P7 (param added/removed, constructor, kept-from-base, 0→1, symmetric, multi-record dedupe, literal-only argument); cross-category negatives (pure rename, rename+arity composite, D1 import-prune shape, clean refactor, same-arity type change, Split Parameter — the last two = documented-FN tests); guard negatives (overload, varargs ×2, qualified/chained/this/methodref, static import, extends/anonymous/enum absorbability, Object names, X-leftover ×2, Y-unattributable, concurrent, change-dropped, markers, flag-off, missing-parents, non-java, merged==parent invariant ×3). **GD2(iii): run 1 PASS (0 flags, 0 UNANALYZABLE — zero tuning iterations); definitive run 2 at `6523ab0` PASS** (239 CLEAN / 4 DIVERGED files; real-RM2 smoke FLAGged both runs; `tune_d2/runs.md`). **§12 Amendment 3 review record:** *(a) project code* — /code-review high, 8 finder angles + verification; four CONFIRMED lane defects fixed pre-gate-rerun: PascalCase comparison pairs misread as generics (`dispatch(Width < Height, Depth > (n))` undercounted → could false-flag; fix = a `(`-followed generic span is trusted only when `new`-rooted), literal-only arguments counted as arity 0 (`send("boom")` — false-flag vector when old arity = 0, plus X-guard bypass; fix = `_strip_for_arity`, a literal-placeholder projection — deliberate documented fork of the D1 stripper whose blank-to-space projection is semantically wrong for counting), single-letter type params poisoned (`new Box<T>()` — subsumed by the new-rooted rule; SCREAMING_CASE veto deleted), annotated anonymous classes not absorbable (`new @NonNull Base(){…}`); plus structure fixes (single `sig_lists` map replaces the changes/sigs pair, dead equal-arity disjunct removed, no-candidate early-out, LANES registry, contract probes now exercise the PRODUCTION RM2 runner). Non-fixes with reasons: `verdict_of`'s "inconclusive" substring sentinel can collide with a genuine flag naming a Java identifier like `inconclusiveResult()` (pre-existing across all lanes; detect_validate.py is the frozen Stage-C instrument; both buckets gate-fail identically → recorded as an S-D5 note: the new two-arm harness should key on a message PREFIX); stale "four strategies" docstring in the frozen instrument; per-suite test-helper copies kept (project test idiom — rename suite precedent; RM2_IMAGE imported from the lane module in both suites so tag bumps propagate); `_patch_rm2` near-dup is by design (different patch target than `_patch_rm2_renames`); `_prev_token` double-compute (coupling cost > benefit); P1 fixture test↔smoke duplication intentional (tune tool cannot import test fixtures). *(b) standalone Java semantics* — verified against JLS 15.12.1/6.5.7.1 (unqualified-name search incl. inherited members → the absorbability design), 15.12.2.4 (variable-arity phase → the varargs net), 8.8/8.8.9 (constructors not inherited; default-ctor analysis shows no FP vector), record canonical-ctor headers (a `record` prefix now counts as a declaration), enum implicit supertype, Object method names; docstring citations corrected. *(c) open-source practice comparison* — **Error Prone** (MethodMatchers javadoc + issue #1283): matches javac-RESOLVED symbols; its matchers skip method references — parity with our `::` exclusion; **PMD** (UnusedPrivateMethod, issues #770/#1226/#1531): documented FP history states matching "solely on argument count … will obviously lead to wrong matches if method overloading is used" — the exact failure our declared-arities union + varargs net + absorbability spans guard; **SpotBugs** (docs): bytecode-only — post-compile, where a stale-arity call cannot exist (javac rejects it), corroborating that this defect class is merge-time-specific with no porting source; **IntelliJ** (resolve model + support guidance): full-project resolution, unresolved-reference reds on incomplete models treated as configuration noise — the suppress-when-unresolvable stance our absorbability encodes. Adopted from comparators: nothing ported (no new runtime deps — Amendment 3 bound); deliberately divergent: no type resolution at all (Stage-B lesson) and unqualified-calls-only (stricter than all four, which type receivers). **Paste-time notes: S-D4** — LANES registry rows are now `(strategy class, smoke builder)` — add D3's row in that shape if a tune run is needed (widened existing lanes are default-on, so the flag-gating differs — read plan §5 GD2(iii) wording: the tune run covers the FULL suite incl. D1/D2); D2's guards are new-lane patterns, not a licence to touch existing lanes'; gap-inventory shape S2 (removed-method-still-called) remains D3's target — deliberately NOT covered here (removals are not signature changes; RM2 reports no record). **S-D5** — wire `SignatureStaleCall` into the experimental arm explicitly (same DETECTORS-tuple caveat as D1); the new harness's verdict classifier should key on the `"<Lane> analysis inconclusive:"` message PREFIX, not substring (see non-fix above); tune_d2/raw_results.json is a tune-side cache — eval materializes fresh; runtime budget: worst-case 2 RM2 docker runs per changed file (byte-identical parents and wholesale merges skip RM2 entirely).

**Session S-D2 summary (2026-07-16, commits `9f871b1`, `423c215`, final).** Built D1 `ImportPruneUsage` — the first detector for the census-top category `stale-usage-of-pruned-import` (12.7%), covering exactly the breakage class Stage B measured and dropped (the `unresolved_reference.py` docstring's "import-deletion breakage is NOT covered by v2" gap) with a **pure-textual differential** instead of the failed Joern type-inference lane. **Ambiguity gate: no material ambiguities → zero §12 amendments;** trivial clarifications (session log): (1) usage provenance "kept-from-base" (movsim/segmentio/assertj spec rows) is in scope — the S-D2 prompt's "guards per §2 + whatever the specs demand" delegates this to specs.csv, and the lane's `lost = imports(ours) ∪ imports(theirs) − imports(merged)` differential covers added and kept-from-base uniformly (base_content deliberately unused — documented in-lane); (2) plan §3's "122 green" baseline is stale — actual pre-session suite = **162**, floor applied as all-green + no verdict change; (3) N2 flag mechanics = `config/strategies.yaml` gains the lane name (loader discovery) while `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1` is checked first-line in `analyze()` (flag off ⇒ return-clean before any I/O — a lane bug cannot affect default-config driver verdicts); (4) "replaced" import sub-shape needs no special handling — both replaced spec units change the simple name (PassingTest→PassingTestWithNoCategory, ArrayList→ArrayDeque), reducing to removal of the old name. **Lane** (`strategies/text_strategies/import_prune_usage.py`, ~330 lines + comment/string-stripper): flags symbol S iff a lost import provided S ∧ merged uses S unqualified (outside comments/strings/imports, not `.`/`::`-qualified, not a `case` label) ∧ merged retains no covering import (kind-matched: type wildcards can't provide bare members — a surviving `java.util.*` cannot suppress a pruned static `fail`) ∧ no local declaration of S (type/method/var shadow guards, overbroad by design) ∧ **absorption guard** = plan §2's "usage resolves in each parent" operationalized (any parent lacking the import yet using S uncovered ⇒ S resolves import-free (same-package/inherited) or that parent was already broken ⇒ suppress). Guards per §2 + specs: java.lang-package imports harmless; same-package imports harmless (jumblr) while same-package *collision* still flags (ninja); wildcard-narrowing mined conservatively (CamelCase len≥3 types / call-form + ALL_CAPS members). **Two documented FNs by design** (tested, close-out record): the assertj pruner-kept-usages shape (file-locally indistinguishable from deliberate re-bind; zero-FP bar wins — 1/21 D1 derivation units) and member candidates under a surviving unrelated static wildcard. **GD2(i)** new tests 30, suite **192/192** (162-baseline verdicts unchanged). **GD2(ii)** fixture battery: positives for every D1 spec sub-shape (removed/replaced/narrowed × type/static × other-side-added/kept-from-base, incl. the P7 extends-class static-wildcard case and P9 double symmetric prune), cross-category negatives (D2 signature-change, D3 rename, clean dead-import refactor) all silent. **GD2(iii): run 1 = 1 flag/243 files** — dynjs `ExecutionContext`: same-package `VariableValues` credited to a lost `java.util.*`; **tuning fix `423c215`** (sanctioned in-session): lost `java.*` type wildcards yield candidates only from embedded JDK public-type sets (`_JDK_WILDCARD_TYPES`, 8 packages; unknown `java.*` ⇒ no candidates, FN-only; non-JDK wildcards keep conservative mining — the jnr.ffi/log4j spec shapes); **run 2 = PASS 0 flags, 0 UNANALYZABLE** (239 CLEAN / 4 DIVERGED files; smoke positive-control gate fired both runs). Harness: `tools/detector_tune_run.py` (detect_validate reuse; merge reproductions cached image-keyed, verdicts cached per driver commit; embedded positive micro-fixture aborts vacuous runs). Firewall: only `data/scenarios_detector_tune/` opened; the 32 quarantined pre-existing scenario dirs untouched; no held-out/eval/spgroup access. Artifacts: `reports_detectors/tune_d1/{summary.txt, runs.md, raw_results.json}`, manifest `gates.GD2.D1 = PASS`. **Paste-time notes: S-D3** — reuse the absorption-guard/`_FileView` machinery reading `text_strategies/import_prune_usage.py` first is NOT required by the plan (D2 is RM2-based per §2), but the stripper/occurrence helpers are import-safe if needed; 5/14 D2 units are Amendment-2 out-of-target (cross-file), `arity_changed` on only 7/14 (S-D1 note stands). **S-D4** — D1's JDK-set fix is a *new-lane* pattern, not a licence to touch existing lanes' guards. **S-D5** — tune_d1/raw_results.json is a tune-side cache; eval materializes fresh (Amendment 1 replacement rule) and must not reuse it; the two-arm harness must wire `ImportPruneUsage` into the experimental arm explicitly (`detect_validate.py`'s DETECTORS tuple deliberately excludes it — frozen Stage-C instrument).

**S-D2 addendum (2026-07-16, Ali-requested critical review; fixes `bed3638` + the artifacts commit that follows it).** Post-close-out review of the lane (as project component, standalone module, and against the open-source import-tool ecosystem — Checkstyle UnusedImports / PMD UnnecessaryImport / google-java-format RemoveUnusedImports guard taxonomies independently corroborate the java.lang/same-package/wildcard-opt-out structure; gjf's refusal to touch wildcards mirrors the JDK-set unknowable-membership stance). Three probe-verified defects fixed: (1) **FN, confirmed e2e** — `throws`/`implements`/`extends`/`permits` operands were treated as declarations by `declares_member`, so pruned exception/interface imports used in multi-item clauses were missed (e.g. one side prunes `import com.foo.FooEx`, other adds `void m() throws FooEx, RuntimeException`) → clause keywords added to `_EXPR_KEYWORDS`, e2e positives P10/P11; (2) **FP-residual** — enum-constant declarations matched no declaration regex, breaking the overbroad-suppression contract → dedicated depth-tracked constant-list parse (`_enum_constants`) feeds `declares_member`, guard negative with annotated/arg/body constants; (3) **FN, minor** — conflict-marker abstention ran on raw text (an exactly-7-char comment banner could silence a file) → moved to stripped text. Plus the **merged==parent soundness invariant test** (byte-identical merged ⇒ never flags, run over the flag-adjacent fixture sets). Suite **197/197**; **GD2(iii) rerun at `bed3638`: PASS — 0 flags, 0 UNANALYZABLE** (the widened clause-position surface produced no new tune flags; run 3 in `tune_d1/runs.md`). Known-and-accepted after review (documented in-lane, FN-direction): Unicode identifiers, `\uXXXX` pre-lexing, SE-17-vintage JDK/java.lang sets, static members inherited via `extends` under a lost static wildcard. Residual FP class unchanged and registered for GD3: lost **non-JDK** wildcard + concurrently-added same-package-type usage.

**Session S-D1 summary (2026-07-16, commits `cf59d37`→final).** Controls FIRST, then the cycle's only LLM use, then GD1. **Ambiguity gate produced two Ali rulings pre-work → §12 Amendment 1:** (1) list-vs-materialization attrition = **viability + spares** — tune draws Stage-C-style (draw-with-materialization: the 100 successes ARE the committed list; tune contents are sanctioned §3 design inputs), eval list viability-checked only (blobless clone + by-SHA parent fetch + exactly-one merge-base, **no content extraction**) + 40 ordered spares + a deterministic S-D5 replacement rule (next unused same-stratum spare keeping ≤3/repo; replacements recorded in the manifest); (2) eval pool = the **same** `semantic_ctl` pool as tune (`mergiraf == Tests_passed`), resolving §4's wording split. **Controls committed before any other work product (`cf59d37`):** pool = 3,144 `semantic_ctl` rows − 195 Stage-C controls (all 195 found in-pool; frozen as `controls/stagec_exclusion_195.csv`) − 0 unparseable-file-count rows = **2,949 fresh merges** (≤3: 2,365 / >3: 584); `tools/detector_controls_draw.py` (SEED_TUNE=20260715, SEED_EVAL=20260716, ≤3/repo per list, exact 60/40 file-count stratification) → **tune 100** (60+40; **243 files materialized** to gitignored `data/scenarios_detector_tune/`; walk skips 4 extract-fail + 4 multibase), **eval 200** (120+80) **+ 40 spares** (24+16; walk skips 2 clone-fail + 11 multibase); three-way disjointness, zero Stage-C overlap, and per-repo caps machine-verified; list sha256s in `controls/draw_log.json` + `manifest.json`. **Spec batch** (`msgbatch_01EwsTTHk1AHnDw1b98AXwxY`; claude-opus-4-8, adaptive thinking, effort high, structured outputs against `prompts_detectors/spec_output.schema.json`; prompt/schema blob SHAs pinned in the manifest pre-submission; inputs = the committed Phase-3 unit texts byte-identical to what labeling saw; runner asserts every unit derivation-split against `split_assignment.csv`): **48/48 succeeded, all `end_turn`**, in=768,732 / out=250,488 tok ≈ **$5.0** batch-rate. **Quote provenance: 91 exact / 3 normalized / 14 empty / 0 absent — zero fabricated evidence** (the #30 fabricated-quote lesson, now a built-in machine precheck in `report` mode). **GD1: machine 37/48 = 77.1% < 80% → failure path → §12 Amendment 2 (Ali ruled option (b), scope reduction):** the 11 misses are honest escapes — **9 cross-file-declaration units** (changed/removed/renamed declaration lives outside the unit's intersecting files: unreachable for the file-local detectors this cycle builds, by construction; ids in `specs/gd1_machine.json`) + **2 truncation-limited**; ruling: D2/D3 **design targets = file-local shapes**, the 9 cross-file units stay in every held-out recall denominator (S-D6 FINDINGS must report the file-local ceiling), the 2 truncation units stay in-target as unusable; re-scored **37/39 = 94.9% → GD1 PASS** (per-detector raw: D1 **21/21**, D2 8/14, D3 8/13). **Gap inventory (GD1 floor ≥5): 6 shapes / 12 units** (`specs/gap_inventory.md`) — in-file-local-reach S-D4 targets: **S1/S1b Joern both-parents-guard self-defeat** (one side removed/renamed a field → the old name is unresolvable in the *changing* parent, so "resolvable in BOTH parents" suppresses exactly the merge-induced case; datastax, yandex-qatools, jline), **S2 removed-method-still-called** (calls are not identifier nodes; removals are not renames; javaparser + jcabi are file-local), **S3 removed inner class referenced via `new T()`** (gwtbootstrap3; must NOT revive the dropped Stage-B type lane — narrower textual differential); out-of-reach: **S4 cross-file class relocation breaking imports** (elisarver, gitools) + **S5 cross-file/external API rename** (imixs javax→jakarta, openpnp, qcadoo) — the Stage-B documented miss class; `softinstigate` = rm2-would-fire **sanity anchor** (existing lanes not empty on D3's categories). **S-D3 design note:** `arity_changed` on only **7/14** D2 derivation units — the arity-primary conservative signal covers ~half the category's mass; the rest are return/param-type changes needing the conservative-bias call. **D1 sub-shapes:** removed 14 / replaced 3 / narrowed-from-wildcard 4 (wildcard narrowing needs its own guard handling; one unit shows a same-package type that could silently absorb the unqualified name — exactly the §2 guard class). Trivial clarifications (session log, no amendment): per-repo cap applied per list; exact stratum quotas (60/40, 120/80, 24/16); unparseable `num_intersecting_files` rows excluded from the pool (0 such); quote rule = verbatim-in-input graded matching with optional line numbers (unit texts are diffs; -1 = unknown); manifest skeleton bundled into the controls-first commit (both pre-spec). **Paste-time notes for later sessions:** S-D3 — 5/14 D2 units are Amendment-2 out-of-target (cross-file); S-D5 — eval materialization must execute the Amendment-1 replacement rule and record replacement events; S-D6 — FINDINGS reports the file-local ceiling. **Pre-push review finding (recorded, not a breach):** 32 eval/spare merges already have gitignored scenario JSONs on local disk from the May comparator programs (`scenarios_ci` 21 / `scenarios_expanded` 7 / `scenarios_spork` 5 / canonical `scenarios` 2 — same Schesch table, different criteria; ids + guard in `manifest.json` `controls.preexisting_scenario_overlap`); none read in S-D1, none git-tracked, none are sanctioned design inputs — S-D2..S-D4 must not open those dirs for these ids, and S-D5 materializes eval contents fresh from the committed list. Artifacts: `reports_detectors/specs/{raw_results.json, specs.csv, spec_table.md, gd1_machine.json, gap_inventory.md}`, `controls/*`, `manifest.json`.

---

## Summary Table

| #  | Issue                                  | Priority | Area              |
|----|----------------------------------------|----------|-------------------|
| 1  | ~~Sample size too small (n=10)~~       | ~~Critical~~ | ~~Data~~ RESOLVED |
| 2  | ~~Structured tools all 0.0 F1~~ (comparator-gap; four-tier normalization, floor HIT 2026-05-15) | ~~Critical~~ | ~~Adapters/Eval~~ RESOLVED |
| 3  | ~~All scenarios "unknown" category~~   | ~~Critical~~ | ~~Evaluation~~ RESOLVED |
| 4  | ~~No visualizations~~ (charts format + 5 canonical PDFs, 2026-07-03) | ~~High~~ | ~~Reporting~~ RESOLVED |
| 5  | ~~No statistical confidence measures~~ (Wilson CIs in all formats, 2026-07-03) | ~~High~~ | ~~Metrics~~ RESOLVED |
| 6  | Biased scenario selection              | High     | Data Collection   |
| 7  | ~~No threats to validity discussion~~  | ~~High~~ | ~~Documentation~~ RESOLVED |
| 8  | ~~Schesch dataset unused~~             | ~~Moderate~~ | ~~Data~~ RESOLVED |
| 9  | ~~No per-scenario breakdown~~ (per-scenario format + heatmap, 2026-07-03) | ~~Moderate~~ | ~~Reporting~~ RESOLVED |
| 10 | Docker builds not reproducible         | Moderate | Infrastructure    |
| 11 | Misleading recall for Mastery/Spork    | Moderate | Metrics           |
| 12 | Hardcoded `.java` extension            | Moderate | Code Quality      |
| 13 | Hardcoded cost model weights           | Moderate | Metrics           |
| 14 | Missing tests for JDime/Spork/CLI/etc (not Mastery) | Moderate | Testing  |
| 15 | Race condition in result caching       | Moderate | Code Quality      |
| 16 | No input validation on scenario IDs    | Moderate | Security          |
| 17 | Docker platform hardcoded to amd64     | Moderate | Infrastructure    |
| 18 | Output truncation loses debug info     | Moderate | Code Quality      |
| 19 | No network retry logic                 | Low      | Robustness        |
| 20 | No parallelization of tool execution   | Low      | Performance       |
| 21 | Dependencies use >= without bounds     | Low      | Infrastructure    |
| 22 | ~~Dead code — `ground_truth.py`~~      | ~~Low~~  | ~~Code Quality~~ RESOLVED |
| 23 | ~~Duplicate per-tool rows in reports~~ | ~~Moderate~~ | ~~Reporting~~ RESOLVED |
| 24 | ~~Mergiraf `-p` semantics unverified~~ (verified 2026-05-13) | ~~Moderate~~ | ~~Infrastructure~~ RESOLVED |
| 25 | Tier E 3e.2/3e.9 not provably sound (defensive; deferred) | Moderate | Comparator soundness |
| 26 | ~~RM2 file-vs-project recall-delta not produced~~ — **RESOLVED 2026-07-03**: n=50 measured (AWS), pooled recall **90.7% [83.8, 94.9]**, false-`NONE` 1/50; R0's 66.7% was an n=10 outlier artifact | ~~Low~~ | ~~Evaluation/Methodology~~ RESOLVED |
| 27 | ~~Driver INTRA_BODY→Spork routing contraindicated~~ — **DROP flip LANDED 2026-06-27** (default NONE→git else→Mergiraf; arm opt-in via `SEMANTIC_MERGE_SPECIALIST_ROUTING=1`; P2 in-vivo corroboration) | ~~High~~ | ~~Driver routing/Eval~~ RESOLVED |
| 28 | ~~Driver MIGRATE_DECL→Weave routing contraindicated~~ — **DROP flip LANDED 2026-06-27** (bundled with #27; W3 gate n=38: Weave 0 wins, McNemar p=0.0078; P2 in-vivo corroboration) | ~~High~~ | ~~Driver routing/Eval~~ RESOLVED |
| 29 | ~~Driver detection layer unvalidated~~ — **RESOLVED 2026-07-03**: frozen R2 6.7% [3.8,11.6] / R1 2.1%, adjudicated 11/11 causal at the time — **amended 2026-09-04: 9/11 causal, citable 9 CAUSAL of 164 = 5.5% [2.9, 10.1]** (atam4j, tcurdt → DETECTOR-FP); post-fix (2 labeled rounds) R1 **0/193 = 0.0% [0, 2.0]**, R2 11/164 | ~~High~~ | ~~Driver detection/Eval~~ RESOLVED |
| 30 | **RESOLVED (2026-07-12)** — in-the-wild silent-failure taxonomy MEASURED at census scale: attributed 119/275 = 43.3% [37.5,49.2] (name-binding family 71.4% of attributed), escape stratum 156/275 = 56.7%, residual-other 0; G0–G3 all PASS (stability 82.9%/κ0.788 post-Amendment-2; Ali reliability 12/12 [75.8,100]); `reports_taxonomy/FINDINGS.md`; never blend with Stage-C/Phase-2b | High | Evaluation/Taxonomy |
| 31 | **RESOLVED (2026-07-20)** — detector cycle D1–D3 complete, all gates PASS: held-out causal family recall 5.4% → **43.2% [28.7, 59.1]** (added 37.8%) — **amended 2026-09-05: 5.7% → 40.0% [25.6, 56.4] (14/35; one unit per distinct merge, design-spec fork twin excluded; audit in `reports_detectors/audit_2026-09-05.md`)**, D1 own-category 13/14 at 14/14 (amended 11/12 at 12/12) precision, **0 adjudicated FPs / 363 controls** (2 flags Ali-ruled incidental-but-true incl. jOOQ "Grr Git" external validation); D2 honest 0 (file-local ceiling), D3 widening 0-causal/1-FP; lanes stay flag-gated; `reports_detectors/FINDINGS.md` | High | Driver detection/Eval |
