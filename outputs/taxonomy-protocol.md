# Taxonomy Refresh at Scale — Pre-Registered Protocol

**Date frozen:** 2026-07-09 (Session 0). **Decisions ruled by Ali 2026-07-09:** census-308 stratified population; primary + ≤2 secondary label arity; Dockerized javac compile check included; corpus split at Phases 1–2 with closed coding on the full census. Tracking: `merge-tool-comparison/ISSUES.md` **#30**. Gate style mirrors [`p1-detection-validation-plan.md`](p1-detection-validation-plan.md) (G0/G1/G2 precedent).

**Amendment rule (Stage-B precedent):** once any labeling data exists, every change to this protocol, the prompts, the schemas, or the gates is a dated, numbered amendment appended to §12 — never a silent edit. Changes before the first G0 pilot run are ordinary edits.

**Two encoded deviations from the session brief** (surfaced to Ali 2026-07-09, unobjected): (1) this doc lives at repo-root `outputs/` beside its precedent, not `merge-tool-comparison/outputs/`; (2) the Schesch table carries **no failing-test names** (per-tool pass/fail only — already noted in the p1 plan §4.6), so the per-unit inputs substitute the **merged-vs-developer-resolution diff** as the strongest available causal signal, with prompt rules (§5, R2) that demote it to corroborating evidence.

---

## 1. Question and non-goals

**Question:** what mechanisms actually cause merge-induced silent failures in the wild? Derive an empirically grounded taxonomy by LLM-assisted inductive coding over the full real silent-incorrect population, with measured base rates + Wilson 95% CIs per category.

**Downstream use:** the taxonomy and base rates feed *future* detector design. The protocol therefore builds the tuning-on-test firewall in from the start (§4).

**Non-goals (hard):** no detector code changes; no labeling of controls; **never blend these numbers with Stage-C R1/R2 or Phase-2b oracle numbers** — this is a NEW labeled evaluation of a different question (what broke, not what we detect). The frozen Stage-C and Phase-2b results remain the citable detector-performance numbers.

## 2. Population, unit, strata

- **Population:** all Schesch rows with `mergiraf == Tests_failed` and a Java diff — the `semantic` criterion in `merge-tool-comparison/tools/select_materialize.py`. **Census n = 308 merges** (p1 plan §2).
- **Unit of analysis: one merge** (`merge_id`). The `Tests_failed` label is whole-merge; coding per merge sidesteps per-file attribution of a merge-level signal (the #28 granularity lesson). All intersecting Java files of a unit are presented together.
- **Strata (fixed by the CSV `num_intersecting_files` field):**
  - **A** — `≤ 3` intersecting files: 195 merges. Reuses Stage-C artifacts wholesale: scenario JSONs in `data/scenarios_semantic/`, mergiraf-reproduced merged files from `reports_detection/full/raw_results.json` (backend `merge-tools/mergiraf:0.17.0`, identical to Stage C). Stage-C accounting carries over: 180 materialized, 164 scored.
  - **B** — `> 3` or unparseable count: ~113 merges. Newly materialized to `data/scenarios_taxonomy_hi/` with the same `select_materialize.py` machinery (`CRITERION=semantic`, all-files mode; Session 1 adds a lower-bound/complement filter or post-filters — the population definition above is what's pinned, not the tool flag). Merged files reproduced with the same pinned mergiraf comparator adapter. Unparseable-count rows are counted and reported separately inside B.
- **Divergence rule (identical to Stage C):** a file where mergiraf CONFLICTs or crashes is not a *silent* merge — dropped from the unit and counted. A unit losing all files leaves the scored population (counted; itself a granularity finding). Materialization losses likewise counted per stratum.
- **Reporting:** every base rate reported per stratum and pooled, Wilson 95% CI each. The per-stratum escape-hatch rate (§5) is a first-class result — attribution is expected to be harder in B, and *measuring* that is part of the point.

## 3. Three-phase design

| Phase | What | Runs on | Model / API |
|---|---|---|---|
| **1 — Open coding** | Per-unit structured extraction: per-side changes vs base, interaction point, mechanism draft with open-vocabulary tags, verbatim evidence quotes, confidence, escape hatches | **Derivation split only** (§4) | `claude-opus-4-8`, Message Batches API |
| **2 — Consolidation** | Cluster Phase-1 tags into a codebook: definitions, inclusion/exclusion, anchor examples, boundary notes; old→new mapping; four-family assessment. **Frozen after Ali adjudicates** (mapping_ui.html precedent) | Phase-1 outputs of derivation units only | `claude-fable-5` interactive, `betas=["server-side-fallback-2026-06-01"]`, `fallbacks=[{"model": "claude-opus-4-8"}]` |
| **3 — Closed coding** | Relabel with the frozen codebook, **twice** (two independent identical batch submissions, `::a`/`::b`) → stability metric; Ali adjudicates reliability subset via visual UI (make_adjudication_ui.py precedent) | **Full census** (both splits) | `claude-opus-4-8`, Message Batches API — same model as Phase 1 so the stability metric is comparable |

Model/workload rationale (frozen in the session brief): the `fallbacks` parameter is rejected on the Batch API, hence Fable-5-with-fallback only on the interactive Phase 2; Opus 4.8 batch runs at 50% token pricing; these models expose no sampling parameters — **run-variance is measured by the §8 stability metric, not controlled by temperature**.

## 4. Corpus split — recorded before any labels exist

- **Derivation split:** seeded random **60%** of scored units, stratified by A/B (`SEED=20260709`). Assignment computed and committed as `reports_taxonomy/split_assignment.csv` **before the first Phase-1 request is sent**; the manifest records the seed and the file's hash.
- **Held-out split:** the remaining 40%. **Firewall:** held-out unit *contents* (diffs, code, quotes) never appear in the codebook, its anchor examples, FINDINGS prose, or any future detector-design document. Held-out units receive Phase-3 labels (labeling eval data with a frozen instrument is legitimate), so census base rates survive intact.
- **Future detector evaluation** (out of scope here, recorded for the record): new detectors may be designed against derivation-split examples and fixtures only; their detection rates are measured on the held-out split and on the external spgroup corpus (`reports_detection/phase2b/`), never quoted back on derivation units as headline numbers.

## 5. Per-unit inputs and Phase-1 rules

**Inputs per unit** (assembled per file, all scored files of the merge; exact template in `merge-tool-comparison/prompts_taxonomy/phase1_open_coding.md`):

1. `ours` vs `base` unified diff (context `-U8`),
2. `theirs` vs `base` unified diff (`-U8`),
3. the mergiraf-merged file — full if ≤ 700 lines, else windowed excerpts (±40 lines around every region differing from base, plus package/imports and enclosing signatures),
4. merged vs `developer_resolution` unified diff (`-U8`) — the causal signal replacing the nonexistent failing-test names,
5. compile-check delta block (below),
6. unit metadata: repo, merge SHA, stratum, file count, dropped-file paths.

**Compile check (decided: yes).** Best-effort single-file `javac` inside a pinned `eclipse-temurin:17-jdk` Docker image (`--platform linux/amd64`, repo Docker-only convention; javac is a checker here, not a merge tool) on each merged file *and* the corresponding dev file. Errors classified `PARSE` / `RESOLVE` (`cannot find symbol`, `package does not exist`) / `OTHER`; the model receives only the **delta** — errors present on merged but absent on dev (matched ignoring line numbers) — under an explicit caveat that single-file RESOLVE errors are expected noise. Raw results kept as `reports_taxonomy/compile_checks.json`; the fraction of silent-incorrect merges with a merged-only PARSE/RESOLVE delta is a standalone descriptive stat. Rationale: 4 of 8 adjudicated #6-family pilot misses were compile errors.

**Truncation strategy (justified: diffs carry the interacting changes; the full merged body is largely redundant with base+diffs; the level is measured, not hidden).** Per-unit input budget ≤ **30k tokens** (counted with `count_tokens` against `claude-opus-4-8`). Ladder, applied per unit until under budget, level recorded in `units.csv` as an analysis covariate:

- **T0** — nothing truncated.
- **T1** — merged files switch from full to windowed form (item 3).
- **T2** — merged-file bodies dropped entirely; diffs + dev-diff + compile delta only.
- **T3** — diff context reduced to `-U3`; if the unit has > 12 files, keep the 12 with the largest merged-vs-dev diffs and list the remainder by path with one-line diffstats.

G0 measures the level distribution; if > 25% of stratum-B units land at T3, the assembly is revisited before Phase 1 (pre-G0, ordinary edit).

**Phase-1 hard rules** (full text in the committed template; summarized here because the gates reference them):

- **R1 — escape hatches are first-class outcomes:** `none-identified` / `indeterminate` / `flaky-suspect`. Pilot precedent stated in the prompt: only 13/23 manually adjudicated misses were attributable. Confident hallucinated causality is the #1 failure mode designed against.
- **R2 — mechanism from the parents, not the dev-diff:** the mechanism must be constructible from the two parent-side changes interacting. The dev-diff corroborates; "the developer did it differently" alone is not a mechanism → escape hatch.
- **R3 — merge-induced test:** the failing pattern must plausibly be absent in each parent alone; code present verbatim in a parent is not merge-induced (Stage-A InfiniteLoop lesson).
- **R4 — evidence:** ≥ 2 verbatim quotes from the provided inputs for an `attributed` verdict, each with source + role.
- **R5 — tags name mechanisms, not symptoms:** 1–4 kebab-case open-vocabulary tags describing the semantic interaction (e.g. `concurrent-guard-bypass`), never the observable (`test-failure`, `compile-error`) or the code domain.
- **R6 — confidence rubric** high/medium/low; at low confidence prefer the escape hatch over a speculative attribution.

Output is machine-parsed: both batch phases use **structured outputs** (`output_config.format` json_schema; schemas committed beside the templates), which removes schema-validity failures as a G0 risk.

## 6. Codebook rules (Phase 2)

- **Granularity rule (fixed now): categories are mechanisms, not symptoms.** Two units share a category iff the same *class of semantic interaction* broke the program, regardless of how it surfaced (test failure, exception, wrong value, compile error).
- **Label arity (decided): one primary + up to two secondary labels.** Base rates, stability, and reliability are computed on the primary label only; secondaries feed a reported co-occurrence matrix.
- Each category ships: kebab-case id, name, one-line mechanism, definition, inclusion criteria, exclusion criteria, ≥ 1 anchor example **quoted from derivation units only** (split firewall), and boundary notes against its nearest neighbor. Singleton categories allowed, flagged `provisional`.
- A `residual-other` bucket exists in the frozen codebook (Phase 3 may not invent categories).
- **Relation to the historical 7-category design taxonomy** (`semantic_merge_driver/ResearchSummary.xml`: Atomic Updates, Control Flow Interference, Data Flow Interference, Exception Handling Divergence, Loop Semantics Divergence, Method Rename, Scope Capture): the 7 remain the *design* taxonomy; Phase 2 must produce a complete old→new mapping table (each old category → new category/-ies or "no empirical counterpart"). The regrouped **four-family view** (state / control-flow / data-flow / name-binding + residual) is a candidate structure to *test against* the clusters — the deliverable states whether the empirical clusters align with it, not the reverse.
- **Freeze:** Ali adjudicates the draft codebook (edit/merge/split/rename via a mapping_ui.html-style review). The frozen codebook + the Phase-3 schema with its category enum are committed; the manifest records the commit. Post-freeze changes only via dated amendment + full Phase-3 relabel.

## 7. Gates — pass criteria fixed now

- **G0 — calibration pilot (before the Phase-1 batch).** 10 derivation units (7 A / 3 B) through the full assembly + Phase-1 prompt. Pass: 10/10 parseable outputs (structured outputs should make this trivial — a failure indicates schema/assembly bugs); no unit over the 30k hard cap; truncation-level distribution acceptable (above); escape-hatch plumbing verified end-to-end. Pilot outputs are discarded; the 10 units are relabeled in the real run.
- **G1 — Phase 1 → Phase 2.** Three conditions, all required:
  1. **Attribution-rate floor:** `attributed` fraction ≥ **35%** of scored derivation units (manual precedent: 57% on ≤3-intersect units; the census includes harder stratum-B units, hence the lower floor). Below → inputs inadequate; amend assembly, rerun.
  2. **Escape-hatch sanity band:** combined escape-hatch fraction in **[15%, 65%]**. Below 15% = over-attribution red flag (the hallucinated-causality failure mode); above 65% = inputs inadequate. Either → investigate + dated amendment before consolidation.
  3. **Ali spot-check:** 15 drafts stratified by confidence (5 high / 5 medium / 5 low-or-escape) via a review UI. Pass: ≤ 3/15 rejected as hallucinated or unsupported-by-quotes. > 3 → prompt revision + full Phase-1 rerun (dated amendment).
- **G2 — codebook freeze.** (i) Coverage: ≥ 90% of attributed derivation units map to a non-residual category (residual ≤ 10% of attributed). (ii) Granularity audit passes (every category a mechanism; definitions + inclusion/exclusion + anchors complete; anchors derivation-only). (iii) Old→new mapping complete; four-family assessment written. (iv) **Ali's ruling** on the draft → freeze commit. No Phase-3 request before the freeze commit exists.
- **G3 — Phase-3 acceptance.** Two conditions:
  1. **Stability (pass a vs pass b, primary label, escape hatches count as labels):** exact agreement ≥ **80%** (Wilson CI reported) **and** Cohen's κ ≥ **0.70**, over all scored census units. Agreement 60–80% or κ 0.50–0.70 → exactly one sanctioned codebook-clarification amendment, then both passes rerun. Below that → codebook not reliable; return to Phase 2 (documented failure — a writable outcome, not a discarded one). Disagreement count > 60 fails the gate regardless.
  2. **Reliability (Ali):** adjudication set = **all** pass-a/b disagreements **plus** a stratified random sample of agreeing units to a total of 40–60 (proportional to primary label, min 3 per category where available, escape-hatch strata included), via a make_adjudication_ui.py-style visual UI with written rationale per override. Pass: Ali accepts ≥ **75%** of the sampled *agreeing* units' labels. Below → amendment + relabel.

**Final labels:** agreeing units keep their label (Ali's sampled overrides applied); disagreeing units take Ali's ruling. The override rate is reported alongside the base rates, not hidden.

## 8. Metrics

- **Base rates:** per-category fraction of scored units (primary label), per stratum + pooled, Wilson 95% CI. Escape-hatch and residual rates reported in the same table — the population accounting must sum to 100% (honest-coverage framing).
- **Stability:** primary-label exact agreement % (+ Wilson CI) and Cohen's κ between the two Phase-3 passes; per-category confusion reported descriptively. Secondary labels: Jaccard overlap, descriptive only (not gated).
- **Reliability:** Ali's acceptance rate on the sampled agreeing units (+ Wilson CI); override direction table.
- **Covariates reported:** truncation level, stratum, file count vs verdict (checks whether attribution collapses on big/truncated units).

## 9. Pinning and reproducibility

`reports_taxonomy/manifest.json` records, per phase: model ID; API surface (batch vs interactive) and full request parameters (`thinking: {"type": "adaptive"}` + `output_config: {"effort": "high"}` and the json_schema for the Opus 4.8 batch phases; effort + fallbacks config for Phase 2); prompt-file git blob SHAs and the repo commit; the protocol commit; the frozen-codebook commit (Phase 3); mergiraf image tag; scenario-file SHA-256 list; split seed + `split_assignment.csv` hash; javac image digest.

- **custom_id scheme:** `p1::<merge_id>`, `p3a::<merge_id>`, `p3b::<merge_id>`. Batch results are unordered — always keyed by custom_id.
- **Resumable cache:** per-phase `raw_results.json` keyed by custom_id (detect_validate.py precedent); a rerun submits only missing/failed ids. Amendments that change the prompt invalidate the affected phase's cache wholesale (recorded in the amendment).
- **Prompt caching:** the static prefix (role + rules + schema; + frozen codebook in Phase 3) carries `cache_control: {"type": "ephemeral"}` on its last block, ordered before all per-unit content. Opus 4.8's minimum cacheable prefix is 4096 tokens — the Phase-3 prefix (rules + codebook) clears this naturally; if the Phase-1 prefix falls short it simply doesn't cache (harmless). Batch-mode cache hits are best-effort; the budget assumes partial hit rates.
- **Budget sanity:** ~170 Phase-1 + ~2×285 Phase-3 unit-requests ≈ 740 requests × ~15k in / ~2k out at Opus 4.8 batch rates ($2.50/$12.50 per MTok) ≈ $50–60 + pilot + Phase-2 interactive Fable 5 ≪ the $90–110 envelope, with headroom for one full sanctioned rerun.

## 10. Artifact layout and session plan

```
merge-tool-comparison/
├── prompts_taxonomy/
│   ├── phase1_open_coding.md          committed now (full text; slots marked)
│   ├── phase1_output.schema.json      committed now
│   ├── phase2_consolidation.md        skeleton; {PHASE1_TAGS} slot
│   ├── phase3_closed_coding.md        skeleton; {FROZEN_CODEBOOK} slot
│   └── phase3_output.schema.json      skeleton; category enum frozen at G2
├── data/scenarios_taxonomy_hi/        stratum-B scenario JSONs (Session 1)
└── reports_taxonomy/
    ├── manifest.json                  §9 pinning record
    ├── split_assignment.csv           committed before any Phase-1 request
    ├── units.csv                      per-unit: stratum, files, scored/dropped, truncation level
    ├── compile_checks.json
    ├── phase1/raw_results.json        + spotcheck/ (UI + Ali's 15 rulings)
    ├── phase2/codebook_draft.md, codebook_frozen.md, old_new_mapping.md
    ├── phase3/raw_results_a.json, raw_results_b.json, stability.md, adjudication/
    ├── labels_final.csv
    ├── FINDINGS.md
    └── summary.txt
```

**Handoff is committed artifacts only** — prompts, schemas, split file, caches, manifest. Session plan: **S1** stratum-B materialization + input assembly + compile checks + split file + G0 → **S2** Phase-1 batch + G1 (Ali spot-check) → **S3** Phase 2 + G2 (Ali freeze) → **S4** Phase-3 double batch + G3 (Ali adjudication) + FINDINGS + STATUS/THREATS updates.

## 11. THREATS_TO_VALIDITY.md additions (to be appended with results)

1. **LLM coder ≠ human ground truth** — mitigated by Ali's G1 spot-check and G3 reliability subset; the acceptance/override rates are published with the base rates.
2. **Whole-merge test label vs per-unit mechanism** — the failure may live outside the shown files or in cross-file interaction; absorbed by escape hatches and reported as the indeterminate rate, not forced into categories.
3. **Dev-diff anchoring bias** — the strongest input signal is what the developer changed, which risks symptom-led coding; mitigated by rule R2 (mechanism must come from the parent-side interaction) and checked in the G1 spot-check.
4. **Same-corpus codebook and detector eval** — mitigated by the §4 split: the codebook never sees held-out units; detector design never quotes them.
5. **Truncation** — level recorded per unit and analyzed as a covariate (§8).
6. **Flaky Schesch labels** — `flaky-suspect` is a first-class verdict; its rate is reported.
7. **Single-model coder** — run-variance is measured (stability metric); model-family bias is not, and is disclosed as such.
8. **Compile-check noise** — single-file javac RESOLVE errors are unreliable; only the merged-vs-dev delta is shown, under caveat, and the signal is auxiliary.

## 12. Amendments

**Amendment 1 — 2026-07-09 (S1, pre-labeling; before the first successful G0 run).**
custom_id wire-encoding. The §9/§10 notation `p1::<merge_id>` (and `p3a::`/`p3b::`)
uses `:`, which the Message Batches API rejects — its custom_id must match
`^[a-zA-Z0-9_-]{1,64}$`. Additionally the longest census merge_id is 61 chars
(a `p3a-`/`p3b-` prefix pushes it to 65 > 64) and one merge_id contains a `.`.
The **logical** per-phase per-merge key is unchanged; only its wire encoding
changes: `<phase>-<sanitized merge_id>` (out-of-charset chars → `-`),
truncated and `-<sha1(merge_id)[:8]>`-suffixed to ≤ 64 chars when the readable
form would overflow or is non-conforming. Batch results are recovered to
merge_id by inverting the deterministic submit-time `{custom_id: merge_id}`
map (never by string-splitting the id). Implemented in
`tools/taxonomy_common.py::custom_id`; recorded in `manifest.json`
(`conventions.custom_id`). No labeling data existed at amendment time, so per
§5 this was an ordinary pre-G0 edit; it is recorded here as an amendment
because it touches a §9 pinned field.

**Amendment 2 — 2026-07-11 (S4, G3 yellow band; the single sanctioned §7.G3.1
clarification).** G3 condition 1 (stability) returned yellow: exact primary-label
agreement 217/275 = **78.9%** [73.7, 83.3] (below the 80% floor) with Cohen's
**κ = 0.741** (≥ 0.70) and **58** disagreements (≤ 60). Per §7.G3.1 the yellow band
admits exactly one codebook-clarification amendment followed by a rerun of both
passes. Analysis of the 58 disagreements: only **3** are named-category ↔
named-category (three unrelated one-offs — the mechanism taxonomy is reliable and
κ already passes); **35** are `none-identified` ↔ `indeterminate` and **18** are
escape ↔ named-category. The instability is concentrated in the boundary between
the two "no-mechanism" escape hatches, which the instrument defined (rule R1) but
gave no operational rule to choose between. This amendment adds one clarification
of R1 to the Phase-3 SYSTEM prefix, distinguishing `none-identified` (no
articulable cross-side interaction — a positive finding of non-interaction) from
`indeterminate` (a nameable but unsettleable interaction, or demonstrably hidden
code). It invents / merges / splits / renames **no** category, changes no
inclusion criterion, and does not move the attributed-vs-escape threshold; the
frozen codebook file and the Phase-3 category **enum are unchanged**, so
`frozen_codebook_commit` (3e7d9b4) still holds. Per §9 the prompt change
invalidates the Phase-3 cache wholesale: the yellow-band pass results
(`raw_results_{a,b}.json`, `batches_{a,b}.json`, `stability.{md,json}`) are
archived under `reports_taxonomy/phase3/yellow_v1/` and both passes are
resubmitted on the amended instrument. Exact clarification text + the disagreement
analysis: `reports_taxonomy/phase3/amendment2_proposal.md` (ruled **APPROVE** by
Ali, 2026-07-11). Implemented in `tools/taxonomy_phase3_prompt.py`
(`R1_CLARIFICATION`), regenerating `prompts_taxonomy/phase3_closed_coding.md`.
