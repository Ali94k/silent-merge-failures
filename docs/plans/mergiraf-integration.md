# Plan: Integrate Mergiraf via Schesch's Upstream Framework

**Status:** active — M0 complete (2026-05-11); user pinned **Mergiraf 0.17.0** (not upstream's 0.4.0) and chose Docker install (2026-05-12). M6-lite complete (commit `3fef834`, 2026-05-12); M3.5 (3e + 3j) complete 2026-05-14 — Spork FPs reframed as comparator-gap (not tool bug), 3b/3h/3i deferred to post-tool-integration TODO; M1 ready to start. See [`mergiraf-integration-recon.md`](mergiraf-integration-recon.md) §0 (update callout) for the deviation rationale.
**Owner:** Ali
**Created:** 2026-04-21
**Depends on:** none (empirical-side plan, independent of `semantic_merge_driver` work)

---

## 1. Context

The Schesch et al. ASE 2024 framework Ali already replicates ([`merge-tool-comparison/`](../../merge-tool-comparison/)) **has already been extended upstream to evaluate Mergiraf**. Per [the upstream README](https://github.com/benedikt-schesch/AST-Merging-Evaluation): *"the framework has been expanded to evaluate newer algorithms, such as Mergiraf."* The upstream framework uses **project test suites as ground truth**, not textual equivalence — which sidesteps the [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #2 FP-inflation problem by construction.

Two consequences for this plan:

1. We do **not** need to invent a Mergiraf adapter from scratch; upstream has one.
2. The ground-truth methodology choice (textual equivalence vs. test-suite execution) becomes a **load-bearing decision** — upstream's approach produces more defensible numbers, but importing it is larger than just adding one tool.

## 2. Constraints (from user standing rules and project memory)

- **Clean tracked incremental steps.** Each phase is one reviewable commit / PR, not a big-bang merge. (This is *why* the prior RefMerge/Mergiraf architecture was reverted; see [`CLAUDE.md`](../../CLAUDE.md) and project memory.)
- **Do not delete `*.key` files**; preserve historical design docs in place.
- **Ask before destructive actions** (including git operations beyond the local feature branch).
- **Report confidence intervals on headline numbers.** Wilson 95% CI for F1/precision/recall on any n<1000 dataset; a claim "tool A better than tool B" requires non-overlapping CIs. Unifies with [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #5 on statistical confidence — without this, n=50 comparisons are suggestive, not defensible.
- **Timebox escape rule.** If any phase exceeds its estimate by 2×, stop and write a revisit note to [`STATUS.md`](../../STATUS.md) before continuing. Prevents open-ended phase creep when "one more edge case" keeps moving the finish line.
- Keep Ali's two co-equal thesis contributions intact: (1) Joern/CPG semantic-conflict detection, (2) case-based tool dispatch in the composition pipeline. This plan serves contribution (2) by adding Mergiraf as a candidate handler; it does not affect (1).

## 3. Goals

Primary:
- Add Mergiraf to `merge-tool-comparison/`, either by local adapter or by syncing with upstream.
- Produce a TP/FP/TN/FN/F1/weighted-cost row for Mergiraf on the same dataset used for the current four tools.

Secondary:
- Decide whether to adopt Schesch's test-suite ground truth (resolves [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #2) or stay with the current textual comparator.

MVP track (per [`execution-sequence.md`](execution-sequence.md) §2 ε MVP-first ordering):
- **Phase 6-lite** ships the `MergeBackend` ABC + `MergirafBackend` + `GitMergeFileBackend` *before* Phases 1–5 finish, as the merge-layer half of the end-to-end MVP (paired with [rm2-integration.md](rm2-integration.md) R4a + R4b).
- **Phase 6-validate** runs after Phase 4 to retroactively confirm the M6-lite default choice — Mergiraf F1 ≥ `git merge-file`'s on the Schesch subset, with zero crashes.

Non-goals:
- Not reimplementing or forking Schesch's full upstream framework.
- Not building out the refactoring-detection branch (RM-ASTDiff / RefMerge / IntelliMerge) — separate track.
- Not expanding Joern strategy coverage — separate track.

## 4. Phased plan

Each phase is **one branch, one PR**, with explicit acceptance criteria. Stop between phases; re-evaluate. Effort estimates are rough ceilings, not commitments.

### Phase 0 — Reconnaissance (read-only, ~2h)

**Status:** complete (2026-05-11) — see [`mergiraf-integration-recon.md`](mergiraf-integration-recon.md). Recommended **Path A**. Original recon recommended pinning **0.4.0** + native install to match upstream Schesch numbers; user overrode 2026-05-12 to **0.17.0** + Dockerized for framework consistency (Homebrew bottle availability avoids Rust toolchain install; QEMU build cost on Apple Silicon accepted). Standalone three-file CLI (`mergiraf merge BASE LEFT RIGHT -p PATH`) confirmed via `--help`. Upstream Mergiraf results (still citable, but against 0.17.0 framework — threat to validity): 3456 Tests_passed / 335 Tests_failed / 2180 Merge_failed on n=5971.

**Purpose:** understand exactly what upstream offers before writing any code.

**Actions:**
- Clone upstream at a pinned commit into a scratch location (NOT into `merge-tool-comparison/`).
- Locate upstream's Mergiraf adapter: how it invokes `mergiraf`, which version, what inputs/outputs.
- Locate upstream's ground-truth classifier: test-suite invocation, pass/fail mapping to TP/FP/TN/FN.
- Check whether upstream has published Mergiraf results (CSV, paper, blog). If yes, capture them as the baseline to reproduce.
- Write a 1-page `docs/plans/mergiraf-integration-recon.md` summarising findings and recommending either Path A (local adapter) or Path B (sync-with-upstream).

**Acceptance:** one-page reconnaissance doc exists, with explicit Path A-or-B recommendation and evidence.

### Phase 1 — Local Mergiraf adapter (~1 day)

**Purpose:** smallest possible change that produces a Mergiraf row in the current reports.

**Files to add (all new, no edits to existing logic):**
- `merge-tool-comparison/src/tools/mergiraf.py` — ~80-line adapter, mirrors [`spork.py`](../../merge-tool-comparison/src/tools/spork.py) (Dockerized). Invocation inside the container: `mergiraf merge BASE LEFT RIGHT -p PATH` — standalone three-file CLI, no git or driver setup. Output: merged content to stdout. Exit code: 0 = clean, 1 = conflict (markers in stdout), other = crash. Spork-style `<<<<<<<`-counting on stdout detects conflict.
- `merge-tool-comparison/tests/test_mergiraf.py` — three tests: CLEAN merge, CONFLICT with markers, CRASH recovery. Mirrors [`test_mastery.py`](../../merge-tool-comparison/tests/).
- One new entry appended to [`config/tools.yaml`](../../merge-tool-comparison/config/tools.yaml): `docker_image: merge-tools/mergiraf:0.17.0`, `timeout: 60`.

**Install:** **Docker** (user decision 2026-05-12; overrides M0's native-install recommendation for framework consistency). [`docker/mergiraf/Dockerfile`](../../merge-tool-comparison/docker/mergiraf/Dockerfile) created — multi-stage build, `rust:1-bookworm` → `debian:bookworm-slim` (both bookworm to keep GLIBC matched), cargo installs Mergiraf 0.17.0. Build via existing `make docker-build` (the Makefile target now includes mergiraf). Per [`CLAUDE.md`](../../CLAUDE.md) standing rule, framework invocation is Docker-only; `brew install mergiraf` is optional dev convenience for ad-hoc CLI use (e.g., `mergiraf --help` queries during development), not a runtime dependency.

**Files NOT touched:** `comparator.py`, `metrics.py`, `runner.py`, `plugin_loader.py`. The plugin loader auto-discovers the new adapter via `pkgutil.walk_packages()`.

**Acceptance:**
- `make docker-build` builds `merge-tools/mergiraf:0.17.0` image successfully (no `:latest` tag — version is the only tag).
- `docker run --rm --platform linux/amd64 merge-tools/mergiraf:0.17.0 --version` returns `mergiraf-merge 0.17.0` (the `--platform` flag is required on non-amd64 hosts, e.g., Apple Silicon).
- `pytest tests/test_mergiraf.py -v` passes.
- `make run` produces `data/results/{scenario_id}/mergiraf.json` files alongside existing tools.

### Phase 2 — Validate on current n=50 (~0.5 day)

**Purpose:** catch Docker/invocation issues before running at scale.

**Actions:**
- Run Mergiraf on the existing n=50 Schesch subset already cached under `data/scenarios/`.
- Generate `reports/results.csv` including Mergiraf.
- Sanity checks:
  - Zero CRASH rows (Mergiraf is a maintained binary, unlike JDime).
  - Non-zero TP count — if TP=0 like Spork/Mastery, the classifier bug is biting Mergiraf too, which would actually be useful evidence for Phase 3.
  - Conflict-marker count parses correctly.

**Acceptance:** updated `reports/results.csv` has a `mergiraf` row with numeric values in each TP/FP/TN/FN column. Write findings (especially: does Mergiraf exhibit the same FP inflation as Spork/Mastery?) into a short commit message.

**Expected outcome:** one of two diagnostic forks —
- **(a)** Mergiraf shows high TP / low FP → textual comparator is fine; Spork/Mastery genuinely produce different output. Proceed to Phase 4.
- **(b)** Mergiraf shows high FP like Spork/Mastery → classifier bug confirmed; Phase 3 becomes mandatory.

### Phase 3 — Ground-truth methodology decision (~1 day)

**Purpose:** resolve [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #2 using upstream's methodology rather than patching `normalize_content()`.

**Options evaluated:**

The decision is multi-axis: *what's the ground truth* × *what's the comparison* × *what's the scope*.

- **3a — Adopt Schesch's test-suite ground truth.** Per-scenario: run the project's test suite against the merged file; pass = dev's intent preserved. Defensible, matches upstream, but requires per-project build/test infrastructure and significantly more runtime per scenario. Cost: ~1–5d optimistic; realistically more given Docker QEMU + Maven/Gradle on ~6k scenarios.
- **3b — Fix `normalize_content()` to be AST-aware (strip formatting via an AST roundtrip).** javalang or tree-sitter canonicalisation. Cheap, adds a dependency, leaves us still textually comparing. Cost: ~1–2d.
- **3c — Keep textual comparison, narrow the dataset to scenarios where developer resolution is textually identical to a tool-reformatted output.** Punts the problem.
- **3d — Token-level comparison.** Lex with javalang, ignore whitespace / comments / import order, compare token streams. Cheaper than 3b, handles most reformatting except member reordering. Cost: ~1d.
- **3e — Formatter-based normalisation.** Run both sides through `google-java-format` (or `spotless`), then text-compare. One binary on PATH, no parser dependency. Solves whitespace, brace style, indentation, *some* import ordering. **Closest to what tools actually do** — Spork claims token-preservation; this gives both sides a fair lexical baseline. Cost: ~0.5d.
- **3g — Compile-only sanity filter.** Does the merged file *parse* / *build* via `javac`? Catches "tool produced unparseable Java" → silent FP. Not a comparator standalone — a hygiene gate that complements anything else. Cost: low per-scenario, no setup beyond JDK.
- **3h — Multi-criteria reporting.** Don't pick one comparator — emit several labels per scenario (textual / AST-equivalent / formatter-equivalent / compiles / passes-tests) and present the matrix. Lets the report say *"under criterion X, Spork's FP rate is 42; under Y, it's 7"* — reader picks. Compatible with any of 3a/b/d/e. Cost: medium (mostly reporting code).
- **3i — Cite upstream Mergiraf numbers.** Sidesteps the comparator for *that one tool* by citing Schesch's published test-suite results. M0 captured the numbers (see [recon doc](mergiraf-integration-recon.md) §5): n=5971 merges from `results/combined/result_adjusted.csv` at upstream HEAD `9238a737f`, classification — 3456 Tests_passed (57.9% correct merges) / 335 Tests_failed (5.6% silent semantic errors) / 2180 Merge_failed (36.5% reported conflicts). The 5.6% silent-error rate is the headline number that justifies a semantic-conflict detection layer downstream of any merge tool, including Mergiraf itself. **Version-skew threat:** upstream pinned Mergiraf 0.4.0; our framework runs 0.17.0 (user decision 2026-05-12). Write-up must acknowledge — Mergiraf may have improved silent-error rate in v0.4 → v0.17 (~16 months of fixes). Doesn't help Spork/Mastery/JDime. Cost: near-zero — just a write-up with the skew caveat; numbers in hand.
- **3j — Sample manual labelling.** Stratified manual inspection of ~10 of the 86 Spork+Mastery FPs. Validates whichever automated comparator wins. Cost: ~3–4h.

**Recommendation** (revisit after Phase 2 evidence and stage γ diagnostic): **γ first → 3e → 3j on remaining FPs → upgrade to 3b only if 3e+3j leave > ~10% unexplained → 3a only if thesis defence specifically requires test-suite methodology.** Add **3i** unconditionally (free credibility for Mergiraf row). Add **3h** to the report regardless of primary comparator — showing FP rate under multiple criteria *is* a thesis result. Skip 3a unless ≥2 weeks earmarked; the timebox-escape rule is likely to fire and you fall back to 3e/3b having burned days. The original 3a-first recommendation (pre-2026-04-30) is preserved as the maximalist option but is no longer the default path.

**Deliverable:** decision recorded in [`STATUS.md`](../../STATUS.md) and [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #2 resolution note. Implementation (if 3a) is a separate phase, not in scope here.

**Acceptance:** written decision with rationale; ISSUES.md #2 status moved from "open" to "decided — see plan."

### Phase 3.5 — Ground-truth implementation (~0.5-5 days, conditional)

**Status:** 3e implemented (2026-05-14); 3j stratified manual labelling completed (2026-05-14, n=15/39 all AST-equivalent reformatting). Spork FPs reframed as **comparator-gap, not tool bug**. ISSUES.md #2 stays at `decided` (not `resolved`). 3b / 3h / 3i deferred to post-tool-integration TODO list (below). See "M3.5 empirical outcome" + "3j outcome" below; [`stage-gamma-fp-diagnostic.md §8`](stage-gamma-fp-diagnostic.md) (3e bucketing) and §9 (3j classification).

**Trigger:** Phase 3 chose any option that requires code changes. Skipped only if Phase 3 chose 3c (keep textual) or 3i alone (cite upstream Mergiraf numbers without changing the comparator). This phase exists because Phase 3's acceptance moves ISSUES.md #2 to `decided — see plan`, not `resolved` — the decision alone does not fix the headline-number credibility problem.

The Actions sections below are per-option. The recommended path from Phase 3 (3e + 3j + 3i + 3h) maps to the 3e Actions below, plus the 3h Actions if multi-criteria reporting is included; 3j is a manual-labelling validation step that does not require its own implementation block.

**Actions (3e path — formatter-based normalisation, current default recommendation):**
- Add `google-java-format` (or `spotless`) as a Docker layer in `docker/git-merge-file/Dockerfile` (or wherever the comparator runs); pin the formatter version, since comparator output changes when the formatter changes.
- Replace `normalize_content()` in `src/evaluation/comparator.py:15-22` with a formatter-roundtrip: run both candidates through the formatter, then text-diff.
- Re-run Phase 2's n=50 validation; verify Spork/Mastery FP rate drops.

**Actions (3d path — token-level comparison):**
- Add `javalang` to `pyproject.toml`.
- Replace `normalize_content()` with token-stream extraction; compare token lists ignoring whitespace, comments, and import order.
- Re-run Phase 2's n=50 validation.

**Actions (3h path — multi-criteria reporting, additive to any primary comparator):**
- Extend `classify_result` in `src/evaluation/comparator.py` to emit a label per criterion (textual / formatter-equivalent / token-equivalent / compiles / passes-tests), not a single classification.
- Extend `src/evaluation/report.py` to render the matrix — one column per criterion.
- Compatible with 3a / 3b / 3d / 3e as the primary axis; 3h adds columns rather than replacing the comparator.

**Actions (3a path — Schesch test-suite ground truth):**
- Import the per-project test runner from Schesch's upstream framework rather than reimplementing. Pin upstream commit.
- Per-scenario pipeline: checkout project at merge commit → substitute the merged file → run declared test suite in an isolated container → map PASS/FAIL to TP/FP/TN/FN.
- Add a scenario-level cache so re-runs skip already-evaluated scenarios (mirrors the existing extraction cache from [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #1 resolution).
- Document per-project build/test prerequisites in a new `docs/testing-prerequisites.md` — what breaks on fresh clones, not an install guide.

**Actions (3b path — AST-aware comparator):**
- Replace `normalize_content()` in `src/evaluation/comparator.py:15-22` with parser-based canonicalisation (javalang or tree-sitter). Diff the canonicalised form.
- Pin the new parser dependency in `pyproject.toml`.
- Re-run Phase 2's n=50 validation; sanity-check that Mergiraf's FP count shifts in the expected direction (should drop sharply if ISSUES.md #2 diagnosis was correct).

**Acceptance:**
- ISSUES.md #2 status moves from `decided — see plan` to `resolved`.
- `reports/results.csv` regenerated under the new methodology; commit message explains the methodology change so downstream consumers know the numbers shifted and why.
- Phase 2's surprises — if any — revisited under the new methodology; findings recorded in [`STATUS.md`](../../STATUS.md).

**M3.5 empirical outcome (2026-05-14):** 3e path implemented. Files: [`merge-tool-comparison/src/evaluation/comparator.py`](../../merge-tool-comparison/src/evaluation/comparator.py) (`contents_match` two-tier: whitespace → gjf roundtrip; cached per content hash; env-disable via `MERGE_COMPARATOR_FORMATTER=off`), [`merge-tool-comparison/docker/google-java-format/Dockerfile`](../../merge-tool-comparison/docker/google-java-format/Dockerfile) (`merge-tools/google-java-format:1.22.0`), [`merge-tool-comparison/Makefile`](../../merge-tool-comparison/Makefile) (`docker-build` includes gjf), [`merge-tool-comparison/tests/conftest.py`](../../merge-tool-comparison/tests/conftest.py) (env-disables formatter in tests; 4 new comparator tests mock the formatter path).

Recovery on n=50: Spork TP 1→2 / FP 42→41; Mastery TP 0→0 / FP 44→44. Acceptance criteria — Spork FP rate drops sharply — **not met**; the §3.5 contingency hedge has fired. **ISSUES.md #2 stays at `decided`, not `resolved`.** Diagnostic shows the 39 unsampled Spork structural FPs are not all AST-equivalent reformatting: dominant residuals are `} else { if (X) }` ↔ `} else if (X)` restructuring, comment-placement (standalone-above-`if` ↔ trailing-after-`{`), and redundant cast parens (`((Long) (value))` ↔ `(Long) value`) that gjf does not normalise. Mastery's 0-recovery matches §6's intrinsic-content-loss framing — comments dropped pre-comparator.

**M3.5 follow-up direction.** Per the §3 ladder: 3d (token-level) is unlikely to recover the else-if residuals (token-different). 3b (AST normalize via javalang/tree-sitter — collapse redundant blocks, harmonise cast paren style) is the next defensible step. Alternatively, 3j (manual labelling of a stratified sample of the 39 still-differ Spork residuals) may reveal that part of Spork's FP rate is intrinsic (parallel to Mastery's §6 framing), which would shift the framing rather than chase recovery. Either path is a separate follow-up plan; neither is M3.5 scope.

**3j outcome (2026-05-14):** stratified manual labelling on n=15 of 39 still-differ Spork residuals (5 size quintiles × 3 picks each, 2.6KB → 161KB) executed. **15 of 15 sampled scenarios are AST-equivalent reformatting** — patterns are blank-line placement, comment placement, cast parens, FQN expansion, `} else { if (X) }` ↔ `} else if (X)` restructuring, and long array-literal line-break, all of which gjf preserves rather than canonicalises. No content loss, content duplication, method reordering, or different-resolution disagreement observed. Original §3 hypothesis (structural FPs are AST-equivalent) **survives at higher sample size**; what failed in §8 was specifically the prediction that gjf alone would normalise these patterns. Full classification table: [`stage-gamma-fp-diagnostic.md §9`](stage-gamma-fp-diagnostic.md).

**Reframing.** Post-3j, Spork's FP rate is best described as a **comparator-ground-truth gap, not a tool bug**: under stronger ground truth (3b AST normalize, 3a test-suite execution) the AST-equivalent FPs would clear. This distinguishes Spork from Mastery (§6 content-loss intrinsic) and JDime (intrinsic crash family-weakness). The reframing is what's available to land *now*; the comparator-gap is closed by 3b.

**TODO list (post-tool-integration phase; tracked here per user direction 2026-05-14):**
- **3b — AST-aware normalize** (~2.5-3d, design drafted). Full design and phased plan in [`comparator-3b-ast-normalize.md`](comparator-3b-ast-normalize.md). Tier C scope: 5 transforms (blank-strip, comment-strip, block-flatten, paren-strip, java.lang FQN-strip) via tree-sitter-java as a Tier 3 in `contents_match`. Defers Tier D (long array-literal handling). Recovery: point estimate TP 37 / FP 6, acceptance floor TP ≥ 32 / FP ≤ 11; closes ISSUES.md #2 cleanly.
- **3h — multi-criteria reporting** (~1-2d). Extend `classify_result` to emit per-criterion labels (textual / formatter-equivalent / AST-equivalent / compiles / passes-tests). Extend `report.py` to render the matrix. Becomes informative *after* 3b adds the AST-equivalent column.
- **3i — upstream Mergiraf citation** (~2-4h). Numbers captured at M0 (n=5971, 3456/335/2180 pass/fail/merge-fail). Write-up as a footnote / section in `merge-tool-comparison/README.md` or `STATUS.md` headline-numbers block. Note the v0.4.0 → v0.17.0 version skew. Free credibility win for the Mergiraf row; doesn't depend on the comparator.

Ordering rationale: 3i is doc-only and can land any time. 3b is the principled fix; 3h is additive on top. All three become more valuable once the full tool comparison (mergiraf + revisited spork/mastery/jdime) ships, so the post-3b headline can be reported under multiple criteria simultaneously.

**Non-actions:** no new tools added; no scope expansion beyond closing ISSUES.md #2. If 3a's infrastructure turns out larger than 5 days, invoke the timebox escape rule (section 2) — stop, write a revisit note, consider falling back to 3e or 3b.

### Phase 4 — Full-scale comparison (~1-2 days)

**Purpose:** headline numbers for the thesis.

**Actions:**
- Run all 5 tools (git-merge-file + JDime + Spork + Mastery + Mergiraf) on the full Schesch subset Ali has available — start with whichever `max-scenarios` value is tractable given Docker/QEMU slowdown on Apple Silicon.
- Regenerate `reports/results.{csv,json,tex}`.
- Per-category breakdown once [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #3 is resolved (scenario categorization currently "unknown" for all rows — independent track, may block per-category analysis here).

**Acceptance:** `reports/results.csv` contains Mergiraf row across full N, reproducible via `make all`. LaTeX table `reports/results.tex` includes Mergiraf column.

### Phase 5 — Thesis positioning (~0.5 day)

**Purpose:** write Mergiraf into the thesis narrative, not just the numbers table.

**Write-ups (all in existing docs, no new files):**
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md) §3 "How the two projects fit the thesis" — add Mergiraf as a case study of *composition-by-abstraction embedded in a single tool* (line-based → tree-aware → markers), supporting Ali's thesis independently of Schesch's `IVn`.
- [`merge-tool-comparison/README.md`](../../merge-tool-comparison/README.md) — add Mergiraf row to "Tools under evaluation" table and "Headline numbers" table.
- [`STATUS.md`](../../STATUS.md) — update implementation status.

**Acceptance:** Mergiraf appears in all three docs with consistent numbers.

### Phase 6-lite — `MergeBackend` ABC + initial backends (~1 day, MVP — no evidence gate)

**Track switch.** Phases 0–5 modify `merge-tool-comparison/` (the empirical-side framework). Phase 6-lite modifies `semantic_merge_driver/` (the constructive-side driver). Phase numbering is contiguous because both tracks contribute to the same MVP rollout, but the files touched and the test suite are entirely separate.

**Trigger:** none. Ships as part of the MVP track in [`execution-sequence.md`](execution-sequence.md) §2 ε *before* Phases 1–5 finish. The MVP commitment is "ship the dispatch mechanism end-to-end with two tools (git + Mergiraf), then validate empirically afterward."

**Purpose:** introduce the backend abstraction and the two initial backend implementations. Does not change the existing default merge behavior — a separate phase ([rm2-integration.md](rm2-integration.md) R4b) is what flips the default to classifier-based dispatch.

**Files to add:**
- `semantic_merge_driver/core/backends/__init__.py`
- `semantic_merge_driver/core/backends/base.py` — `MergeBackend` ABC. Separate from existing `MergeStrategy` ABC: backends *merge*, strategies *analyse*.
- `semantic_merge_driver/core/backends/git_merge_file_backend.py` — `GitMergeFileBackend`. Wraps the previously inline `git merge-file` call from `core/driver.py:27-30` (location pre-M6-lite; now resides in this backend file).
- `semantic_merge_driver/core/backends/mergiraf_backend.py` — `MergirafBackend`. Pin Mergiraf **0.17.0** via the `merge-tools/mergiraf:0.17.0` Docker image. Invocation: `docker run --rm -v <workdir>:/workspace merge-tools/mergiraf:0.17.0 /workspace/base /workspace/ours /workspace/theirs -p <path>`; capture stdout; parse `<<<<<<<` markers for conflict detection. Same image as `merge-tool-comparison/` builds — single Dockerfile, single image, both subprojects. **Docker-only per [`CLAUDE.md`](../../CLAUDE.md) standing rule** — no host-PATH `mergiraf` invocation. Estimated ~50 LOC (temp-dir + volume-mount + subprocess + stdout capture + cleanup).
- `semantic_merge_driver/tests/test_git_merge_file_backend.py` — three tests: clean, conflict-with-markers, crash-recovery.
- `semantic_merge_driver/tests/test_mergiraf_backend.py` — three tests: clean, conflict-with-markers, crash-recovery.

**Files to touch:**
- `semantic_merge_driver/core/driver.py` — refactor the inline `git merge-file` block into a call through `GitMergeFileBackend`. Add `SEMANTIC_MERGE_BACKEND` env-flag handling: values `git` and `mergiraf` route to the corresponding backend. **Default: `mergiraf`** — chosen as MVP second-tool pending Phase 4 validation. (R4b later adds `auto` and flips default to `auto`.)
- Preserve fail-closed semantics across both backends — subprocess failure in either backend → reject, don't silently accept. Matches the β-stage principle from [`execution-sequence.md`](execution-sequence.md).

**Acceptance:**
- All tests pass.
- Default behavior of `core/driver.py` shifts to invoking Mergiraf as the merge step. With explicit `SEMANTIC_MERGE_BACKEND=git`, prior inline behavior is recovered exactly. With explicit `=mergiraf`, the MergirafBackend runs.
- Joern strategies still reject via exit 1 when they flag an issue, regardless of which backend produced the merged file.

**Honest caveat in commit message:** Mergiraf chosen as MVP specialized backend pending Phase 4 validation (Phase 6-validate below). If Phase 4 shows Mergiraf F1 < git-merge-file, the default-flip is reversed.

**Evidence-vs-mechanism trade-off — explicit.** The MVP-first directive ([`execution-sequence.md`](execution-sequence.md) §2 ε) ships the mechanism before the evidence: between M6-lite landing and M6-validate confirming, runtime users of `semantic_merge_driver` are routed to Mergiraf without empirical backing. The alternative ordering — ship M6-lite with default = `git`, flip to `mergiraf` only after M4 — preserves "no untested defaults" at the cost of a second commit that just flips a flag. Current ordering chosen because (a) the mechanism is the load-bearing contribution; (b) the flag is one line, the validation gate is real, and (c) M3.5 should close ISSUES.md #2 *before* M4 runs, so the M4 numbers Mergiraf is judged on will already be credible. If M0 or M2 surface unexpected concerns about Mergiraf stability or correctness (M0 reading upstream's adapter and release cadence; M2 actually running Mergiraf on n=50), reconsider and default to `git` until M4.

### Phase 6-validate — Empirical validation of MVP backend choice (~conditional)

**Trigger:** Phase 4 has landed (full-scale Mergiraf evaluation complete).

**Purpose:** retroactively confirm — or refute — the MVP-time decision in Phase 6-lite to use Mergiraf as the second backend. Role inverts vs. the original (pre-MVP) Phase 6: validation rather than gate.

**Actions:**
- Confirm Mergiraf F1 ≥ `git merge-file`'s on the Schesch subset, with zero crashes, against Phase 4 results.
- **If yes:** the Phase 6-lite default-flip is supported. STATUS.md notes the validation outcome. No code change.
- **If no:** Phase 6-lite's default-flip is unsupported. File a follow-up plan (likely: switch the default in M6-lite back to `git`, or pick a different second backend such as Spork via S2). STATUS.md flags the open issue.

**Acceptance:** STATUS.md updated with explicit validation outcome. If outcome is negative, follow-up plan filed.

## 5. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Upstream Mergiraf adapter does something clever we miss (custom flags, output parsing) | Medium | Phase 0 reconnaissance is explicitly about this. |
| Mergiraf Docker build slow on Apple Silicon | Medium | User chose Docker for framework consistency (2026-05-12) — multi-stage cargo build inside `rust:1-slim` under QEMU takes ~5-15min on M-series. One-time cost per Dockerfile change; image caches between builds. Dev convenience: `brew install mergiraf` provides a native 0.17.0 binary for ad-hoc use without rebuild. |
| Fallback-to-markers classified as CLEAN because conflict markers aren't detected properly | Low | [`spork.py:68`](../../merge-tool-comparison/src/tools/spork.py) already has this logic; copy exactly. Test it in Phase 1. |
| Phase 3 decision (ground truth) reveals upstream's test-suite approach needs per-scenario build infra we can't easily replicate | Medium | Fall back to option 3b (AST-aware normalize) rather than stalling. |
| Mergiraf's "production-grade" reputation doesn't match research-quality numbers (e.g., it's tuned for interactive developer use, not batch evaluation) | Low | If Phase 2 shows surprises, write them up as a finding — either way, data is useful. |
| Scope creep: Phase 6-lite or 6-validate balloons into rebuilding `semantic_merge_driver` pipeline | Medium | Phase 6-lite is scoped to ABC + two backends (~1d ceiling); Phase 6-validate is doc-only retroactive validation. The `auto`-mode dispatch and default flip live in [rm2-integration.md](rm2-integration.md) R4b, not here. |

## 6. Rollback

Every phase is one branch. `git revert` the merge commit or drop the branch; nothing before Phase 6-lite modifies existing runtime code paths.

Phase 6-lite touches `semantic_merge_driver/core/driver.py` — the existing `git merge-file` behavior remains accessible via `SEMANTIC_MERGE_BACKEND=git`, so rollback of the default-flip is a flag flip, not a code change. Phase 6-validate is doc-only.

## 7. Open questions (to resolve in Phase 0)

1. Has upstream Schesch published Mergiraf numbers we can cite directly, or do we need to re-run?
2. Does upstream's test-suite ground truth require per-project test runners we don't have locally?
3. Is there a non-Docker Mergiraf invocation path that's reproducible enough for thesis-defence-grade results?
4. Which Mergiraf version does upstream pin, and is it compatible with the Java syntax in the Schesch dataset?

---

## Appendix A — Why this plan and not alternatives

**Why split Phase 6 into 6-lite (MVP) and 6-validate (post-MVP)?** The earlier draft (pre-2026-05-04) gated all of Phase 6 on Phase 4 evidence. The MVP-first directive recorded in [`execution-sequence.md`](execution-sequence.md) §2 ε reframes this: ship the dispatch *mechanism* end-to-end first (Phase 6-lite + R4a + R4b), then validate the second-backend choice empirically afterward (Phase 6-validate via Phase 4 numbers). The evidence discipline is preserved — but applied retroactively to the MVP choice rather than gating the architectural plumbing. If validation fails, the default-flip is reversed; the architectural mechanism stays in place.

**Why not start directly with `semantic_merge_driver` integration *without* the M6 split?** Because pure (non-split) Phase 6 would either (a) gate on M2-M5 evidence and delay the MVP by ~3-4 days, or (b) ship the driver promotion without evidence and lose the empirical-justification story. The split lets us have both: ship the mechanism early (option a's UX without its delay), then do the evaluation honestly (option b's evidence without its premature commitment).

**Why not adopt Schesch's whole framework instead of extending ours?** Two reasons. (1) Ali has invested in the current framework's plumbing (Click CLI, caching, adapter ABC) and the extensions Ali wants for the thesis (Joern strategies as a separate axis) don't exist upstream. (2) The minimal patch — add one adapter — is cheap and reversible; a full sync is expensive and irreversible.

**Why not skip Phase 3?** Because the Spork/Mastery FP numbers are currently *the* biggest credibility risk in Ali's empirical results. Adding Mergiraf without resolving ISSUES.md #2 risks Mergiraf showing suspect numbers too, and the reader cannot tell whether that's Mergiraf's fault or the framework's.
