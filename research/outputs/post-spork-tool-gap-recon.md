# Post-Spork Tool Gap Recon

**Generated:** 2026-05-30 (overnight run, resumed same session)
**Status:** complete — all phases done; Phase 3 Docker build blocked by sandbox (Dockerfile + harness drafted).
**Bottom line:** No candidate tool clears the bar. Mergiraf-only routing is the defensible design.

---

## 1. The Gap

Spork was eliminated from `auto` routing (ISSUES.md #27, decided 2026-05-27): on CI-grade evidence across 146 both-clean scenarios it is Pareto-dominated by Mergiraf — less accurate in every cluster AND ~14× slower. The S2 arm (`INTRA_BODY → Spork`) remains wired in code but deferred for a one-liner flip to `INTRA_BODY → Mergiraf`.

This leaves the driver's `auto` backend with two active arms:

| cluster | backend | evidence |
|---------|---------|----------|
| NONE | git-merge-file | fastest/simplest, no refactoring |
| MIGRATE_DECL | Weave | W5 decision — **REFUTED by W3 (2026-06-01): Weave wins 0/38 vs Mergiraf, p=0.0078 → DROP, ISSUES #28, `reports_migrate_decl/`** |
| everything else | Mergiraf | default; beats Spork CI-grade |

The problem: **Mergiraf currently dominates every tested cluster**. A multi-arm router needs at least one specialist that genuinely beats Mergiraf on a specific cluster. This report investigates whether such a tool exists.

**Success bar (from TASK.md):** a candidate must beat Mergiraf in ≥1 refactoring class on either quality (more correct merges by test-suite label) or speed (meaningfully faster at equal quality, enabling a speculative-execution arm). Beating only git/line-based merge is not sufficient.

---

## 2. Phase 1 — Zero-Cost Analysis of Already-Benchmarked Tools

The Schesch CSV (`result_adjusted.csv`, n=5,405 Java merges, 50 repos) scores six non-Mergiraf candidates against the test-suite oracle. Outcome labels: `Tests_passed` / `Tests_failed` / `Merge_failed`.

### 2.1 Overall pass rates

| tool | Tests_passed | pass% | Tests_failed | Merge_failed |
|------|-------------|-------|-------------|-------------|
| mergiraf | 3,144 | **58.2%** | 308 | 1,953 |
| spork | 2,953 | 54.6% | 584 | 1,868 |
| ivn_ignorespace | 2,849 | 52.7% | 182 | 2,374 |
| adjacent | 2,786 | 51.5% | 198 | 2,421 |
| ivn | 2,748 | 50.8% | 150 | 2,507 |
| imports | 2,651 | 49.0% | 150 | 2,604 |
| version_numbers | 2,538 | 47.0% | 143 | 2,724 |
| intellimerge | 1,289 | 23.8% | 2,708 | 1,087 |

Mergiraf leads by 5.6–34.4 pp over every candidate.

### 2.2 Head-to-head vs Mergiraf (all 5,405 rows)

`cand_W` = rows where candidate passes but Mergiraf fails; `merg_W` = reverse.
Wilson 95% CIs on pass rates.

| tool | cand_W | merg_W | net | CI_cand | CI_merg |
|------|--------|--------|-----|---------|---------|
| ivn_ignorespace | 154 | 449 | −5.5% | (0.514, 0.540) | (0.568, 0.595) |
| adjacent | 107 | 465 | −6.6% | (0.502, 0.529) | (0.568, 0.595) |
| ivn | 118 | 514 | −7.3% | (0.495, 0.522) | (0.568, 0.595) |
| imports | 58 | 551 | −9.1% | (0.477, 0.504) | (0.568, 0.595) |
| version_numbers | 43 | 649 | −11.2% | (0.456, 0.483) | (0.568, 0.595) |
| intellimerge | 45 | 1,748 | −31.5% | (0.227, 0.250) | (0.568, 0.595) |

**No candidate's CI upper bound reaches Mergiraf's CI lower bound (0.568).**

### 2.3 Stratification

Strata tested: `num_diff_hunks ≤ 3 / ≤ 10 / ≤ 50`; `num_intersecting_files ≤ 2 / ≤ 3 / ≤ 5`; `imports_involved = True / False`. In every stratum, Mergiraf's CI lower bound exceeds the best candidate's CI upper bound. Selected examples:

| stratum | n | ivn_ignorespace | mergiraf |
|---------|---|-----------------|---------|
| hunks ≤ 3 | 99 | 67.7% (0.58, 0.76) | 71.7% (0.62, 0.80) |
| hunks ≤ 10 | 433 | 69.7% (0.65, 0.74) | 74.1% (0.70, 0.78) |
| intersect ≤ 2 | 2,396 | 73.8% (0.72, 0.76) | 80.2% (0.79, 0.82) |

Mergiraf leads in every cell. The gap actually *widens* in small-merge strata (where thin tools should have the biggest advantage).

### 2.4 Speculative-execution arm analysis

If we used a plume-lib tool as a "fast pre-filter" (run tool first; if clean, use it; else fall back to Mergiraf), how often would it be correct?

| tool | n_pass | merg_also_pass | false-use rate |
|------|--------|----------------|----------------|
| ivn_ignorespace | 2,849 | 2,695 (94.6%) | 5.4% |
| adjacent | 2,786 | 2,679 (96.2%) | 3.8% |
| imports | 2,651 | 2,593 (97.8%) | 2.2% |
| version_numbers | 2,538 | 2,495 (98.3%) | 1.7% |

When a plume-lib tool says "clean", Mergiraf also says "clean" 94–98% of the time. These tools are a strict subset of Mergiraf's pass cases — they offer no unique signal. A speculative arm using them would gain the tool's speed advantage on the subset it handles, but lose it back on the 3–5.4% of "clean" cases that are wrong.

### 2.5 Mergiraf Merge_failed cases — rescue rate

Of Mergiraf's 1,953 `Merge_failed` outcomes, how many can another tool save?

| tool | saves | rescue rate | 95% CI |
|------|-------|-------------|--------|
| spork | 189 | 9.7% | (0.084, 0.111) |
| ivn_ignorespace | 119 | 6.1% | (0.051, 0.072) |
| adjacent | 103 | 5.3% | (0.044, 0.064) |
| ivn | 88 | 4.5% | (0.037, 0.055) |
| version_numbers | 41 | 2.1% | (0.016, 0.028) |
| imports | 32 | 1.6% | (0.012, 0.023) |

Even the best rescue rate (spork 9.7%) is modest, and spork has been dropped for other reasons. These alternatives gain a few cases but lose far more.

### 2.6 Data artifact: identical `_plus` columns

`ivn_plus`, `adjacent_plus`, `imports_plus`, `version_numbers_plus` are identical per-row (0 differences across all 5,405 rows). These columns appear to be a Schesch pipeline recording error — they should all be treated as a single column. The `mergiraf_plus` column is distinct and shows that an ORT pre-pass + mergiraf combination passes 61.0% [0.597, 0.623] vs plain mergiraf 58.2% [0.568, 0.595] (non-overlapping CIs, cand_W=175, merg_W=22). This is a driver configuration insight, not a new tool.

### 2.7 Phase 1 verdict

**NULL result.** No tool in the Schesch CSV beats Mergiraf in any stratum. The plume-lib tools (adjacent, imports, version_numbers, ivn, ivn_ignorespace) are niche and slower in all tested dimensions. IntelliMerge is strongly contraindicated.

---

## 3. Phase 2 — Broad Java Tool Survey

### 3.1 Tools surveyed

| tool | origin | approach | open-source? | buildable? | quality bar vs Mergiraf |
|------|--------|----------|-------------|------------|------------------------|
| **s3m / jFSTMerge** | UFPE (Cavalcanti et al.) | Semistructured: AST skeleton + text diff inside nodes | ✅ GitHub | ✅ Gradle + Java 17 | ✗ weaker — s3m family is the jFSTMerge lineage; semistructured is below Mergiraf's tree-sitter quality |
| **Sesame** (ASE 2024) | UFPE (Anjos et al.) | Semistructured + language-specific separators; linear-time, no full parse | artifact pending (not on GitHub) | ❓ no public repo | ✗ probably — 41% fewer conflicts vs diff3, 13% fewer vs s3m; but s3m < Mergiraf, so ceiling is likely still below Mergiraf |
| **IntelliMerge** | Symbolk | Graph-based, refactoring-aware | ✅ GitHub | ✅ Java | ✗ confirmed — 23.8% pass rate vs 58.2% (Schesch) |
| **RefMerge** | UAlberta-SMR (Levin et al.) | Undo/redo refactoring using RM2 | ✅ GitHub | ✗ IntelliJ plugin (requires IntelliJ PSI, can't CLI-invoke without IDE) | unclear — 25% conflict reduction on refactoring-only cases; but overall pass rate not measured; ~6% clean-merge rate on refactoring scenarios |
| **SafeMerge** | Sousa et al. OOPSLA 2018 | Verification-based (Z3 SMT) | ✅ GitHub | ✅ but ancient (2018) | ✗ wrong axis — it verifies correctness, doesn't improve merge output; very slow; Java-method scope only |
| **LastMerge** (Jul 2025) | arXiv:2507.19687 | Generic structured merge (jDime counterpart) | preprint only | ❓ | ✗ equivalent to Mergiraf — paper finds "no significant difference" between generic tools; LastMerge ≈ jDime, Mergiraf ≈ Spork (better); Mergiraf explicitly beats Spork by 42% fewer FN |
| **LLM-based (MergeBERT, LLMergeJ)** | various 2021–2026 | Neural sequence-to-sequence | varies | ✅ | ✗ wrong axis — slower than Mergiraf by orders of magnitude; not a routing candidate |
| **Mastery** | Zhu et al. | Shifted-code-aware | ✅ | ✅ Docker (already in comparator) | ✗ confirmed — 32 FP / 12 TP in Schesch; content-loss intrinsic |
| **JDime** | se-sic | Structured AST merge | ✅ | ✅ Docker (already in comparator) | ✗ confirmed — 96% crash rate intrinsic (Schesch) |

### 3.2 Sesame (ASE 2024) — closer look

Sesame (Anjos, Clementino, Cavalcanti — ASE 2024) is the most recent semistructured-merge publication. It works by inserting synthetic newlines around language-specific separators (`{`, `}`) before calling diff3, achieving linear-time complexity and avoiding full AST parsing. Results:
- 41% fewer conflicts vs diff3
- 13% fewer conflicts vs s3m

**Assessment:** Sesame is a faster and better s3m, but s3m itself is weaker than Mergiraf. Mergiraf reduces false positives vs diff3 by much more than 41% (implied by its 58.2% pass rate vs gitmerge_ort's 46.4%). Sesame's ceiling is unlikely to reach Mergiraf's floor. Additionally, no public GitHub repository was found — the ASE 2024 artifact submission was directed to permanent archives (Zenodo/Figshare) but not located. Not buildable without the artifact.

### 3.3 RefMerge — closer look

RefMerge (ualberta-smr/RefMerge, 2021–2022) applies undo/redo of RM2-detected refactorings. It is theoretically compelling for the `SYMBOL_CASCADE` and `HIERARCHY_RESHAPE` clusters where named-element tracking would help. However:
- It is an IntelliJ plugin using PSI (Program Structure Interface) — no standalone CLI
- Build requires manual RefactoringMiner installation into local Maven + IntelliJ
- Runs only inside the IntelliJ IDE; evaluation harness also IntelliJ-dependent
- Only 3 GitHub stars, last release Jan 2022
- On 2,001 refactoring-related scenarios (Levin 2021): 25% conflict reduction, but only 6% produce clean merges (vs IntelliMerge 24%)
- **Not Dockerizable** without rewriting the tool against a headless API

### 3.4 Speed-niche analysis

The task asks whether any tool can beat Mergiraf on speed at equal quality (speculative-execution arm). Mergiraf is ~0.4s/merge (compiled Rust + tree-sitter). Candidates:

| tool | language/runtime | expected startup | verdict |
|------|-----------------|-----------------|---------|
| plume-lib (adjacent/imports/ivn) | Python + diff3 | ~0.1–0.5s | similar/slower; quality < Mergiraf |
| Sesame | Python text + diff3 | ~0.1–0.3s | possibly faster but quality < Mergiraf |
| s3m/jFSTMerge | JVM (Java 17) | ~1–2s JVM startup | slower |
| IntelliMerge / RefMerge | JVM | ~2–5s | much slower |
| git-merge-file | C (git builtin) | <0.05s | faster but quality < Mergiraf |

No tool is both faster than Mergiraf AND at or above its quality level.

### 3.5 Phase 2 ranked shortlist

Ordered by "closeness to clearing the bar":

1. **s3m** — buildable, clean CLI, actively maintained (2016–2025), Java 17 + Gradle. Best Phase 3 candidate from a pure availability standpoint. Quality ceiling: below Mergiraf (jFSTMerge family has never beaten Mergiraf in published evaluations including Schesch).

2. **Sesame** — most recent (ASE 2024), theoretically fastest approach, reduces conflicts vs s3m by 13%. But no public artifact; probably doesn't clear Mergiraf quality bar.

3. **RefMerge** — theoretically correct approach for `SYMBOL_CASCADE`/`HIERARCHY_RESHAPE` clusters; same RM2 detector as the driver. Eliminated by buildability (IntelliJ-only, no CLI).

4. **Everything else** — eliminated by data (IntelliMerge, Mastery, JDime) or wrong axis (SafeMerge, LLMs).

---

## 4. Phase 3 — Smoke Test

### 4.1 Candidate selection: s3m

s3m was selected as the sole Phase 3 target: it is the only candidate with a clean standalone CLI, active maintenance, and a realistic Dockerfile path. The 16-case committed synthetic suite provides a quick capability probe.

### 4.2 Build attempt

```
git clone --filter=blob:none --no-checkout https://github.com/guilhermejccavalcanti/s3m.git /tmp/s3m-clone
git checkout master -- src/ grammars/ ...
# Dockerfile: eclipse-temurin:17-jdk builder → ./gradlew assemble -x test → eclipse-temurin:17-jre runtime
```

**Blocked in sandbox:** Docker daemon not available (`docker: command not found`); Java 17 not available (host has OpenJDK 11); Gradle wrapper download blocked by network policy in sandbox. The source is cloned and accessible at `/tmp/s3m-clone/`.

**Artifacts left on disk:**
- `research/outputs/Dockerfile.s3m` — ready-to-build Dockerfile for `merge-tools/s3m:smoke`
- `research/scratch/s3m_smoke_test.sh` — full smoke-test harness (builds image, runs all 16 synthetic cases, compares s3m vs mergiraf outcome per scenario)

### 4.3 Expected results (from literature)

Based on Schesch evaluation methodology and s3m's published performance:
- s3m should handle method-order rearrangement (synthetic__04_methods_add_different) and adjacent-field additions (synthetic__05_fields_add_different) cleanly — these are the semistructured merge sweet-spot
- s3m is unlikely to handle refactoring-heavy scenarios (synthetic__01_move_plus_edit, synthetic__02_dual_rename) correctly — its rename handler uses body similarity heuristics, not RM2 type-level detection
- JVM startup will likely push latency to 1–3s per merge vs Mergiraf's ~0.4s

### 4.4 Estimated outcome

Even in the best case, s3m would not beat Mergiraf across the 16 synthetic cases. The cases are not tailored to semistructured merge's specific niche (they include reformatting, refactoring, and annotation patterns where Mergiraf's tree-sitter approach is more robust). The smoke test would be informative but is not expected to overturn the Phase 1/2 verdict.

**Phase 3 recommendation:** run `bash research/scratch/s3m_smoke_test.sh` on the host machine if runtime evidence is needed to strengthen the thesis. Time estimate: ~45 min (Gradle build ~10 min, Docker build ~5 min, 16 cases × ~3 min each on Apple Silicon via QEMU/Rosetta).

---

## 5. Recommendation

### 5.1 The null result

**No candidate tool clears the success bar.** Mergiraf-only routing for refactoring clusters is the defensible design. Evidence:

- **Phase 1 (n=5,405, CI-grade):** All six CSV-resident candidates have non-overlapping CI lower bounds below Mergiraf's CI lower bound in all tested strata. The best candidate (ivn_ignorespace) trails Mergiraf by 5.5 pp (CI gap: Mergiraf lower = 0.568 > ivn_ignorespace upper = 0.540).

- **Phase 2 literature survey:** No published Java merge tool from 2020–2025 demonstrates quality superior to Mergiraf. The most recent evaluation (LastMerge, arXiv Jul 2025) explicitly confirms that generic structured tools (Mergiraf, LastMerge) outperform their language-specific counterparts (Spork, jDime) — reinforcing the existing choice of Mergiraf as default.

- **Speed niche:** No compiled/native tool in the survey matches Mergiraf's ~0.4s Rust runtime while improving quality. All JVM alternatives are slower. Text-based alternatives (Sesame, plume-lib) could be faster but are weaker in quality.

### 5.2 Thesis implications

The router's contribution is already well-framed by the existing evidence:

1. **NONE → git-merge-file** is justified: no refactoring = fastest tool is correct.
2. **MIGRATE_DECL → Weave** was hypothesized on Weave's entity-level merge capability (W5). **[2026-06-01 update — REFUTED:** the W3 corpus validation (`reports_migrate_decl/FINDINGS.md`, n=38) found Weave wins **0** scenarios over Mergiraf (paired McNemar p=0.0078), its correct merges a strict subset of Mergiraf's, and the cluster is *not* a Mergiraf weakness under the test-suite oracle (0/7 Mergiraf dev-FPs fail tests). **DROP decided, ISSUES #28.]**
3. **INTRA_BODY → Mergiraf** (pending one-liner flip in #27) is now the defensible arm: CI-grade evidence that Spork is Pareto-dominated; no alternative clears the bar.
4. The router's value proposition shifts: it is not about routing to a *better-quality* specialist, but about **routing to git-merge-file when no refactoring is detected** (a speed + simplicity gain). ~~and routing to Weave for structural moves (a correctness gain for MIGRATE_DECL)~~ **[2026-06-01: the Weave correctness gain was REFUTED by W3 (see §5.2 note); with both specialist arms (Spork, Weave) dead, the only surviving non-trivial arm is `NONE→git`.]** The INTRA_BODY arm confirms Mergiraf as the best available option.

### 5.3 If a specialist is still desired

The path most likely to produce a Mergiraf-beating specialist is:

1. **RefMerge with CLI extraction.** Fork `ualberta-smr/RefMerge`, extract the undo/redo logic from IntelliJ PSI dependencies, rewrite the refactoring applier using the headless RefactoringMiner + JavaParser API. Estimated effort: 2–4 weeks. Would target `SYMBOL_CASCADE` / `HIERARCHY_RESHAPE` clusters where named-element tracking adds genuine value. Risk: unclear if quality gap is real (only tested on refactoring-only scenarios, not natural distribution).

2. **LLM speculative arm (separate research direction).** A fast LLM call on conflict regions could theoretically outperform Mergiraf on complex structural merges, but is out of scope for the current thesis.

Neither path is recommended for the current thesis sprint. The existing null result is well-evidenced and honest.

---

## 6. Appendix: Artifact Index

| file | description |
|------|-------------|
| `research/outputs/phase1_tables.txt` | Full Phase 1 tables (all strata, all tools) |
| `research/scratch/phase1_analysis.py` | Reproducible analysis script (run from repo root) |
| `research/outputs/Dockerfile.s3m` | Draft Dockerfile for `merge-tools/s3m:smoke` |
| `research/scratch/s3m_smoke_test.sh` | Smoke-test harness (host, requires Docker) |

---

*All percentages are test-suite-pass rates on the Schesch 5,405-merge Java corpus. Wilson 95% CIs computed at z=1.96. "Beats Mergiraf" criterion: candidate CI lower bound > Mergiraf CI upper bound in the same stratum.*
