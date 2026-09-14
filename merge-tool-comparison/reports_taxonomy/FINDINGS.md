# FINDINGS — Empirical Taxonomy of Merge-Induced Silent Failures (ISSUES #30)

**Program:** taxonomy-refresh, Sessions 0–4 (2026-07-09 → 2026-07-12). **Protocol:** [`outputs/taxonomy-protocol.md`](../../outputs/taxonomy-protocol.md) (frozen `9209327`; Amendments 1–2). **Instrument:** frozen codebook `reports_taxonomy/phase2/codebook_frozen.md` + enum schema (freeze commit `3e7d9b4`), Phase-3 prompt post-Amendment-2 (blob `0320e49c`).
**Population:** all Schesch rows with `mergiraf == Tests_failed` and a Java diff — census n = 308; **scored n = 275** (see §1). Labels: two independent `claude-opus-4-8` closed-coding passes over all 275; disagreements ruled by Ali; sampled agreements audited by Ali (G3).

> **Never blend these numbers with Stage-C R1/R2 (`reports_detection/`) or Phase-2b (`reports_detection/phase2b/`).** Different instruments, different questions (what *broke* vs. what we *detect*), different populations. Held-out-split unit **contents** do not appear in this document (labels only, §4 firewall); quoted examples are derivation-split units.

---

## 1. Population accounting

| | stratum A (≤3 files) | stratum B (>3 / unparseable) | total |
|---|--:|--:|--:|
| census (`mergiraf == Tests_failed`, has-Java) | 195 | 113 | **308** |
| not materialized | 15 | 2 | 17 |
| all files dropped by divergence rule (CONFLICT/CRASH → not silent) | 16 | 0 | 16 |
| **scored** | **164** | **111** | **275** |

Scored = every unit with ≥1 cleanly-Mergiraf-merged intersecting Java file (`merge-tools/mergiraf:0.17.0`). Base rates below are over the scored 275; the 33 exclusions are counted above, not silently dropped.

## 2. Base rates (primary label, final)

Final labels: 216 units where both passes agreed (Ali audited a stratified sample of 12 — all accepted); 47 pass-disagreements ruled by Ali; 12 sampled agreeing units confirmed (`labels_final.csv`, per-unit provenance in `source`).

| primary label | A n=164 | B n=111 | pooled n=275 | pooled % [Wilson 95%] |
|---|--:|--:|--:|---|
| `stale-usage-of-pruned-import` | 22 | 13 | **35** | 12.7% [9.3, 17.2] |
| `stale-caller-of-changed-signature` | 17 | 11 | **28** | 10.2% [7.1, 14.3] |
| `overlapping-edit-interleaving` | 11 | 7 | **18** | 6.5% [4.2, 10.1] |
| `stale-reference-to-renamed-or-relocated-declaration` | 8 | 8 | **16** | 5.8% [3.6, 9.2] |
| `stale-expectation-of-changed-behavior` | 3 | 4 | **7** | 2.5% [1.2, 5.2] |
| `stale-reference-to-removed-declaration` | 4 | 2 | **6** | 2.2% [1.0, 4.7] |
| `duplicate-concurrent-addition` | 5 | 1 | **6** | 2.2% [1.0, 4.7] |
| `insertion-anchored-to-relocated-code` | 1 | 2 | **3** | 1.1% [0.4, 3.2] |
| `residual-other` | 0 | 0 | **0** | 0.0% [0.0, 1.4] |
| **attributed subtotal** | **71** | **48** | **119** | **43.3% [37.5, 49.2]** |
| `none-identified` | 57 | 31 | **88** | 32.0% [26.8, 37.7] |
| `indeterminate` | 34 | 32 | **66** | 24.0% [19.3, 29.4] |
| `flaky-suspect` | 2 | 0 | **2** | 0.7% [0.2, 2.6] |
| **escape subtotal (not-cleanly-merge-attributable)** | **93** | **63** | **156** | **56.7% [50.8, 62.5]** |
| **total** | **164** | **111** | **275** | 100% |

**Stratum robustness:** the attributed fraction is nearly identical in the two strata (A 43.3% [35.9, 50.9] vs B 43.2% [34.4, 52.5]) — mechanism attributability does **not** collapse on the larger (>3-file) merges.

### 2.1 The escape stratum is a first-class result

**156/275 = 56.7%** of real silent-incorrect merges could not be cleanly pinned to a mechanism in the intersecting files. This is not instrument failure; it is a property of the population: the `Tests_failed` signal is **merge-level**, so the cause may sit outside the shown files, in cross-file interaction, in the build, or in test nondeterminism. This stratum was anticipated from G1 (Ali's 4 spot-check rejections were *population* objections — "not a good representation" — not labeling defects) and is reported as its own mass, never forced into mechanism categories. Within it: `none-identified` (a **positive finding of non-interaction** between the two sides, 32.0%) vs `indeterminate` (a nameable but unsettleable candidate interaction, or demonstrably hidden code, 24.0%) — the boundary is operationalized by protocol §12 Amendment 2. `flaky-suspect` carries only 0.7%.

### 2.2 Name-binding dominance (corroborates Stage C by an independent method)

The four name-binding/typing categories (`pruned-import`, `removed-declaration`, `renamed-or-relocated`, `changed-signature`) carry **85/119 = 71.4% [62.7, 78.7] of all attributed units** (30.9% of the whole scored population; A 71.8%, B 70.8%). Phase-1 open coding independently put the family at 45/60 = 75% of attributed derivation units, and Stage C (a *detector*, not a coder) found all its detection mass in the same #6 family. Three independent methods now agree: **when a clean merge silently breaks a Java program and the cause is visible, it is overwhelmingly a name-binding/typing interaction** — one side changed what a name means (import path, existence, identity, or contract) while the other side added or kept code bound to the old meaning.

### 2.3 Residual-other = 0

Closed coding assigned **zero** units to `residual-other` (upper 95% bound 1.4%): the frozen 8-category codebook covered every attributed unit in the census, including the 110 held-out units it was never derived from. The codebook generalizes beyond its derivation split.

### 2.4 Merge-tool composition artifacts

The two tool-artifact categories (`overlapping-edit-interleaving` 6.5%, `insertion-anchored-to-relocated-code` 1.1%) plus `duplicate-concurrent-addition` (2.2%) total ~10% of the population — real but minority mechanisms. The dominant failure mode is not the tool weaving wrongly; it is the tool weaving *correctly* two individually-sound changes whose composition is semantically stale.

## 3. Gates (G3)

### 3.1 Condition 1 — stability (two independent passes, all 275 units)

| run | agreement | κ | disagreements | verdict |
|---|---|---|---|---|
| v1 (frozen instrument) | 217/275 = 78.9% [73.7, 83.3] | 0.741 | 58 | **YELLOW** |
| v2 (post-Amendment-2) | **228/275 = 82.9% [78.0, 86.9]** | **0.788** | **47** | **PASS** |

v1 hit the yellow band (agreement < 80%); per §7.G3.1 the single sanctioned codebook-clarification amendment was proposed, ruled APPROVE by Ali, and **both passes were rerun in full** (no selective reuse; v1 archived in `phase3/yellow_v1/`). The v1 instability was **not** in the mechanism taxonomy — only 3/275 units flipped between two *named* categories — but in the under-specified boundary between the two no-mechanism escapes (`none-identified`↔`indeterminate` = 35/58 disagreements). Amendment 2 added an operational rule for exactly that boundary; the rerun was a controlled comparison (only the clarification changed) and moved that bucket 35→21 while cat↔cat stayed at noise level (3→6). Secondary labels: mean Jaccard 0.942 across passes (descriptive). Full confusion detail: `phase3/stability.md`.

### 3.2 Condition 2 — reliability (Ali)

Adjudication set = **all 47 disagreements + a seeded stratified sample of 12 agreeing units** (3 each from the 4 largest agree categories; the min-3 floor filled the 13 slots left under the ≤60 cap by the 47 disagreements — an honest consequence of the disagreement count, and the reason the gated sample is small). Via `phase3/adjudication/adjudication_ui.html`; rulings in `phase3_reliability_rulings.csv`; review audit trail in `adjudication_record.md`.

- **Sampled agreeing units accepted: 12/12 = 100% [75.8, 100] → PASS** (gate ≥75%). Override rate on sampled agreements: **0%**.
- The 47 disagreement rulings (which become final labels, not gated): 22 sided with pass a, 25 with pass b, 0 third labels.
- Adjudication ran in two drafts: Claude's review of draft 1 flagged 4 cases (2 hard, 1 medium, 1 soft) with code-level verification; Ali revised 3 and consciously retained 1 (see `adjudication_record.md`). Notably, one pass-b ruling candidate was rejected because its central evidence quote (conflict markers "in the merged result") **appears nowhere in the model's input** — a fabricated-evidence instance caught by the human gate (→ THREATS).

**G3 overall: PASS** (both conditions).

## 4. Relation to the historical 7-category design taxonomy

Old→new mapping (frozen codebook §3, unchanged by Phase 3 — closed coding could not invent categories):

| # | Historical (design) category | Empirical counterpart | Phase-3 mass |
|---|---|---|---|
| 1 | Atomic Updates | none observed | 0 |
| 2 | Control Flow Interference | no standalone category; partial counterparts inside `overlapping-edit-interleaving` / `stale-expectation-of-changed-behavior` | (within 6.5% / 2.5%) |
| 3 | Data Flow Interference (Stale Read) | no standalone category; nearest phenomenon lives in `stale-expectation-of-changed-behavior` | (within 2.5%) |
| 4 | Exception Handling Divergence | subsumed by `stale-caller-of-changed-signature` (throws-clause instance) | (within 10.2%) |
| 5 | Loop Semantics Divergence | none observed (the one loop-multiplicity case is an anchoring artifact → `insertion-anchored-to-relocated-code`) | (within 1.1%) |
| 6 | Method Rename | split three ways by what happened to the declaration: `renamed-or-relocated` / `removed` / `changed-signature` (+ `pruned-import` for resolution-path-only breaks) | **30.9% pooled** |
| 7 | Scope Capture | no standalone category; partial counterparts inside `pruned-import` (resolution shift) and `insertion-anchored-to-relocated-code` (scope loss) | (within 12.7% / 1.1%) |

The **four-family regrouping** (state / control-flow / data-flow / name-binding) was tested in Phase 2 and **rejected as primary structure**: it would lump ~71% of attributed mass into one family while shearing the tool-artifact categories apart (codebook §4). Phase 3's numbers reinforce that assessment.

## 5. Covariates (§8)

Attribution does **not** collapse under input truncation or unit size — the escape mass is not an artifact of hiding code from the coder:

| covariate | attributed / total (rate) |
|---|---|
| truncation T0 (full inputs) | 80/197 (40.6%) |
| truncation T2 (merged bodies omitted) | 27/50 (54.0%) |
| truncation T3 (aggressive) | 11/26 (42.3%) |
| 1 scored file | 48/128 (37.5%) |
| 2–3 files | 49/96 (51.0%) |
| 4–8 files | 17/37 (45.9%) |
| >8 files | 5/14 (35.7%) |
| stratum A / B | 71/164 (43.3%) / 48/111 (43.2%) |

(T1 = 1/2 omitted — n too small to read.)

## 6. Secondary labels (descriptive)

Per-unit union of the two passes' secondaries against the final primary (counts are units):

- `stale-caller-of-changed-signature` +→ `pruned-import` ×2, `overlapping-edit-interleaving` ×2, `changed-behavior` ×1, `removed-declaration` ×1
- `overlapping-edit-interleaving` +→ `renamed-or-relocated` ×3, `changed-signature` ×2, `removed-declaration` ×1
- `stale-reference-to-renamed-or-relocated-declaration` +→ `changed-signature` ×3, `overlapping-edit-interleaving` ×1, `pruned-import` ×1
- `stale-usage-of-pruned-import` +→ `renamed-or-relocated` ×1, `overlapping-edit-interleaving` ×1, `changed-behavior` ×1

Multi-mechanism units are real but rare (22/275 = 8.0% carry any secondary in either pass); the dominant pattern by far is a single decisive mechanism. Import-migration and signature-migration mechanisms co-travel most (both sides of the same API-migration coin).

## 7. Notable single findings

- **Census contains fork-duplicate merges.** `sander2798_enderstone__9d0d7b7ba8` and `sandergielisse_enderstone__9d0d7b7ba8` (also the kaazing `k3po`/`robot` pair) are byte-identical merges from repo forks. They were labeled consistently (verified during adjudication) but counted separately — the population is Schesch *rows*, not deduplicated merges.
- **A fabricated-evidence instance survived schema validation** (pass b on a derivation unit: quoted conflict markers that exist nowhere in its input) and was caught only by the human adjudication gate. Phase 1 ran a machine quote-provenance precheck; Phase 3 did not — future closed-coding instruments should.
- **`flaky-suspect` mass is tiny (0.7%)** — the coder did not use the flakiness escape as a dumping ground; suspected-environmental failures were argued into `none-identified`/`indeterminate` with reasons instead.

## 8. Provenance

- Passes: `claude-opus-4-8`, Message Batches, structured outputs (frozen enum), thinking adaptive, effort high, cached system prefix. v2 batches: p3a `msgbatch_01D8m745tqBwq4ormrVPcRng` (+1-unit top-up `msgbatch_01JSoZUnTwkVCxdnkzH6ExcV`), p3b `msgbatch_01NK5h7yy6npzUVKPmwc87Pm`; 275/275 conforming each, all `end_turn`; ≈$38.6 (v1 yellow run ≈$38.3, archived). Per-unit inputs byte-identical across passes and to Phase 1 (derivation units verified byte-for-byte).
- Key commits: protocol freeze `9209327`; codebook/enum freeze `3e7d9b4`; prompt finalization + §9 pin `a8734c7`; harness `1b66a13`; v1 yellow `597e535`; Amendment 2 `3474b09`; G3.1 PASS `9cce340`; reliability UI `0228e76`.
- Reproduction: `tools/taxonomy_phase3.py` (double batch), `tools/taxonomy_g3_stability.py` (G3.1), `tools/taxonomy_g3_adjudication_ui.py` (G3.2 UI, seed 20260711), `tools/taxonomy_finalize.py` (this document's numbers → `phase3/findings_stats.json`).
