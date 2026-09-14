# Detector Cycle — Pre-Registered Plan (D1–D3)

**Program:** detector-cycle (successor to the taxonomy program, ISSUES #30).
**Tracking:** ISSUES #31 (opened in S-D1; use next free number if taken).
**Status:** FROZEN — §11 ratified by Ali 2026-07-16; the commit introducing this line is the freeze commit.
**Authority chain:** this document (+ dated §12 amendments) governs every session below.
Upstream constants it inherits and may not re-decide:
[`outputs/taxonomy-protocol.md`](taxonomy-protocol.md) §4 split firewall,
`reports_taxonomy/labels_final.csv` + `codebook_frozen.md` (freeze `3e7d9b4`),
the repo-wide Docker-only rule, and the never-blend rule (taxonomy /
Stage-C R1-R2 / Phase-2b numbers are separate instruments — new numbers here
are a fourth, never mixed with the other three).

Each step runs in its **own fresh session** with the pre-written kickoff
prompt from §8. Paste-time check before starting any session: read the
ISSUES #31 close-outs; if any contradicts a prompt line, patch that line and
note it — never improvise mid-session.

---

## 1. Goal and non-goals

**Goal:** implement and validate detectors for the highest-mass mechanism
categories of the empirical taxonomy, measured per-category on the untainted
held-out split with the project's standing zero-FP bar.

**Non-goals (this cycle):** behavioral categories
(`stale-expectation-of-changed-behavior`), tool-artifact categories
(`overlapping-edit-interleaving`, `insertion-anchored-to-relocated-code`,
`duplicate-concurrent-addition`), driver default-map changes, whole-driver
cost re-pricing (optional follow-on, §8 S-D7/S-D8), any LLM-based detection
(§2 rule N1).

## 2. Decisions already made — encode, don't re-open

**Detectors (2 new + 1 widening):**

| id | detector | target category (census mass) | shape sketch |
|---|---|---|---|
| **D1** | `ImportPruneUsage` (new) | `stale-usage-of-pruned-import` (12.7%) | differential 3-way: one side removes/changes an import; other side adds (vs base) usage of the pruned symbol; usage resolves in each parent, not in merged. Guards: wildcard imports, `java.lang`, same-package, FQN usage, local shadowing. |
| **D2** | `SignatureStaleCall` (new) | `stale-caller-of-changed-signature` (10.2%) | per-branch RM2 signature-change types on side X; side Y adds/keeps call sites with the OLD shape (arity mismatch = primary signal); conservative bias — prefer FN over FP; overload/varargs guards. |
| **D3** | widening of existing `RM2RenameConflict` / `JoernUnresolvedReference` lanes | `stale-reference-to-removed-declaration` + `stale-reference-to-renamed-or-relocated-declaration` shapes the current lanes miss (~8%) | evidence-guided à la Stage B, from the S-D1 gap inventory. |

**Rejected for this cycle** (do not re-litigate): interleaving/anchoring
detectors (FP risk vs the zero-FP differentiator), behavioral detection
(needs SDG/test-grade analysis — Phase-2b finding), duplicate-addition
(≤2.2% mass, wide CIs).

**Rules:**
- **N1 — no LLM in any detector.** Detectors are deterministic, offline,
  static lanes. The only LLM use in this cycle is S-D1's spec-extraction
  batch (`claude-opus-4-8`, Batch API — development tooling on derivation
  data). Rationale: merge-time architecture + label circularity (held-out
  labels were produced by Opus 4.8; an Opus-based detector graded on them
  is void).
- **N2 — experimental flag.** New/widened lanes run under
  `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1` until this cycle validates
  them; enabling by default is a post-cycle decision, out of scope.
- **N3 — sessions on `claude-opus-4-8`** (default effort); no Fable
  workload calls anywhere in this cycle.

## 3. Firewall and freeze discipline

- **Design/tuning inputs (allowed):** derivation-split units only (contents,
  labels, quotes, S-D1 specs), synthetic fixtures derived from them, and the
  **tune-controls** draw (§4). Nothing else.
- **Never seen during development:** held-out unit contents, the
  **eval-controls** draw (list committed in S-D1, contents materialized only
  in S-D5), spgroup files.
- **Detector freeze:** S-D5 records the detector suite commit in the cycle
  manifest before the first evaluation run. After that, any detector change
  = dated §12 amendment + full S-D5 rerun. (Stage-C G2 discipline.)
- **Prose firewall:** held-out unit contents never appear in committed prose
  (FINDINGS quotes = derivation units or fixtures only). Ali sees held-out
  contents in the adjudication UI — that is measurement, not design.
- **Regression floor:** existing lanes' committed fixture/regression tests
  (driver suite, currently 122 green + Stage-C postfix regression tests)
  must stay green in every build session. D3 widens lanes — it may not
  change any existing test's expected verdict.

## 4. Corpus assets

| asset | contents | when drawn/materialized |
|---|---|---|
| derivation split | 165 units (labels, quotes, contents) — design corpus | exists (`reports_taxonomy/`) |
| held-out split | 110 units, labeled, materialized | exists; contents untouched until S-D5 |
| **tune-controls** | n=100 fresh `mergiraf == Tests_passed` merges, **excluding** the 195 Stage-C control merges | list + materialization in S-D1, `SEED_TUNE=20260715` |
| **eval-controls** | n=200 fresh `Tests_passed` merges, excluding Stage-C controls AND tune-controls | **list committed in S-D1**; contents materialized only in S-D5, `SEED_EVAL=20260716` |
| spgroup | 66 labeled-clean + 17 labeled-interference units | exists (`reports_detection/phase2b/`), untouched until S-D5 |

**Draw constraints (both control draws):** (i) ≤3 merges per repo (Stage-C
control precedent — no single repo dominates the zero-FP claim);
(ii) stratified to the census file-count mix — ~60% with
`num_intersecting_files ≤ 3`, ~40% with `> 3` (mirrors A/B 164/111), so the
FP surface matches the population the recall claim is about; (iii) drawn
with the stated seeds via a committed script, not hand-picked.

Both control lists are committed in S-D1 — before any detector code exists —
with seeds, draw script, and list hashes in the cycle manifest (split-first
discipline).

## 5. Gates

- **GD1 (after S-D1):** spec extraction covers ≥80% of the target-category
  derivation units with a usable machine-readable spec (pruned import +
  stale usage site / old+new signature + stale call site); D3 gap inventory
  lists ≥5 concrete missed shapes with unit ids; both control lists
  committed. Light gate: machine check + Ali eyeballs the spec table
  (~10 min, no formal ruling). **Failure path:** coverage <80% → Ali rules
  between (a) extraction-prompt fix + batch rerun or (b) scope reduction
  (drop the uncovered shapes from the relevant detector's targets) — either
  way a dated §12 amendment.
- **GD2 (per build session, S-D2/S-D3/S-D4):** (i) new unit tests green,
  full driver suite green, no existing expected verdict changed;
  (ii) fixture battery: detector fires on all its own-category fixtures,
  stays silent on all cross-category fixtures; (iii) **0 flags on the 100
  tune-controls** — any flag is fixed before the session closes (this is
  tuning, allowed here and only here). Tune-control runs execute **locally**
  — a documented exception to the AWS-over-local standing rule: bounded,
  iterative tuning loops where per-iteration deploys are impractical. (The
  Joern-bearing D3 pass may take ~1–2 h emulated; accept or run overnight.)
- **GD3 (S-D5, frozen suite):** evaluation numbers produced from **two
  arms** — a **baseline arm** (current default lanes, experimental flag
  OFF) and the **experimental arm** (full suite, flag ON) — so the cycle's
  *added* recall is attributable, which matters most for D3 (a widening of
  lanes that already catch some of its categories). Deliverables:
  (i) held-out recall per category + pooled name-binding family, per arm
  **and as the added-recall delta** (primary citable number = experimental
  pooled family recall, with the delta reported beside it), Wilson CIs;
  (ii) **0 flags on the 200 eval-controls** (experimental arm; baseline arm
  reported); (iii) **0 flags on spgroup labeled-clean (66)**. Any eval-control or
  spgroup flag → Ali adjudicates it: genuine FP ⇒ dated amendment
  (fix or disable the lane) + full S-D5 rerun; incidental-but-true finding
  ⇒ recorded, gate re-judged by Ali.
- **GD4 (S-D6, Ali):** every held-out flag adjudicated
  (CAUSAL / INCIDENTAL / FP, §4.6 style, written rationale). Citable recall
  counts **causal flags only**. No numeric floor — the gate is completeness
  of adjudication; precision is reported, not assumed.

## 6. Conventions (declared once)

- **Artifacts root:** `merge-tool-comparison/reports_detectors/`
  (`manifest.json`, `specs/`, `controls/`, `eval/`, `adjudication/`,
  `FINDINGS.md`, `summary.txt`).
- **Lane code:** new lanes under `semantic_merge_driver/strategies/`
  following the existing registration pattern; names `ImportPruneUsage`,
  `SignatureStaleCall`; D3 keeps existing lane names.
- **Manifest pins:** detector-suite commit (at S-D5 freeze), control seeds +
  list hashes, harness commits, Docker image tags/digests (RM2 2.4.0,
  mergiraf 0.17.0, temurin javac), spec-batch model + params + batch ids.
- **Environment:** `ANTHROPIC_API_KEY` in `~/.zshenv`; anthropic SDK in the
  **repo-root `.venv`** (not the merge-tool-comparison venv); Docker
  required; all merge/RM2 tooling via pinned images only.
- **Close-out (every session):** commits referencing #31; summary appended
  to ISSUES #31; manifest updated; STOP at the session's stated endpoint.

## 7. Session plan (one step = one session)

| session | step | gate | Ali touchpoint |
|---|---|---|---|
| S-D1 | spec-extraction batch + gap inventory + control draws + ISSUES #31 | GD1 | ~10 min spec-table eyeball |
| S-D2 | build D1 `ImportPruneUsage` | GD2 | none |
| S-D3 | build D2 `SignatureStaleCall` | GD2 | none |
| S-D4 | build D3 lane widening | GD2 | none |
| S-D5 | freeze suite + full evaluation battery | GD3 | only if a control/spgroup flag appears |
| S-D6 | adjudication + FINDINGS + close-out | GD4 | the adjudication (~1–2 h) |
| S-D7 | *(optional, decide at S-D6)* Stage-C-protocol rerun with extended suite (blend-safe before/after) | — | — |
| S-D8 | *(optional)* P2-style whole-driver re-pricing | — | — |

Sessions run serially by default (WIP limit 1). S-D2 and S-D4 are
technically independent — parallelize only if calendar pressure demands two
touchpoints at once.

---

## 8. Session kickoff prompts

Paste verbatim into a fresh session at the repo root; patch only what the
paste-time check (header) demands. Every prompt carries the same
**ambiguity gate**: the session must surface ambiguities as questions to
Ali *before* producing work products — improvised resolutions are the drift
this plan exists to prevent.

### S-D1 — specs, gap inventory, control draws

```
Session S-D1 of the detector cycle — open ISSUES #31 (or next free number;
then patch the plan header via dated amendment). AUTHORITY:
outputs/detector-cycle-plan.md (FROZEN; read fully) — §2 decisions, §3
firewall, §4 assets, §5 GD1.

STATE: taxonomy program #30 CLOSED; labels at
reports_taxonomy/labels_final.csv; derivation/held-out assignment at
reports_taxonomy/split_assignment.csv; codebook frozen at
reports_taxonomy/phase2/codebook_frozen.md.

FIRST — AMBIGUITY CHECK: after reading the authority doc and ISSUES
#31, if anything is ambiguous, contradictory, or underspecified (plan vs
repo state vs this prompt), ask Ali concrete questions and WAIT for
answers — never resolve ambiguity by improvising. Material resolutions =
dated §12 amendment; trivial clarifications → session log + close-out.

SCOPE:
1. Create merge-tool-comparison/reports_detectors/ + manifest.json skeleton
   (§6 pins known so far).
2. Control draws FIRST (§4, incl. the draw constraints: ≤3 merges/repo,
   ~60/40 file-count stratification, committed draw script):
   tune-controls n=100 (SEED_TUNE=20260715) and eval-controls n=200
   (SEED_EVAL=20260716) from the Tests_passed pool, both excluding the 195
   Stage-C control merges, mutually disjoint. Commit both lists + script +
   hashes to controls/ BEFORE any other work product.
   Materialize tune-controls now (select_materialize semantic_ctl path);
   eval-controls stay a list — do NOT materialize (§3).
3. Spec-extraction batch (the cycle's only LLM use, §2 N1):
   claude-opus-4-8 via Batch API over the ATTRIBUTED DERIVATION units
   whose primary label is one of the four target categories (D1's
   pruned-import, D2's changed-signature, D3's removed-declaration +
   renamed-or-relocated) — no other units. Structured outputs. Per unit extract:
   D1 — pruned import + stale usage site(s); D2 — old signature, new
   signature, stale call site(s); D3 — for removed/renamed-relocated
   units, whether existing lanes (RM2RenameConflict,
   JoernUnresolvedReference — read their code first) would plausibly fire,
   and if not, the concrete missed shape. Verbatim quotes with file+line;
   an explicit cannot-extract escape per field. Cost ≈ $2–5. Results →
   specs/ (raw_results.json + specs.csv + gap_inventory.md).
4. Evaluate GD1 (§5); write the spec table summary for Ali's eyeball.

GUARDRAILS: derivation units only in the batch; no detector code in this
session; no held-out/eval-control/spgroup access. ENVIRONMENT per plan §6.
EXIT: lists + specs + gap inventory + manifest committed (refs #31); GD1
verdict recorded; ISSUES #31 opened with S-D1 close-out. STOP.
```

### S-D2 — build D1 `ImportPruneUsage`

```
Session S-D2 of the detector cycle — ISSUES #31. AUTHORITY:
outputs/detector-cycle-plan.md §2 (D1 row), §3, §5 GD2. Paste-time check
against ISSUES #31 done.

STATE: S-D1 DONE — specs at reports_detectors/specs/specs.csv (D1 rows),
tune-controls materialized, GD1 PASS.

FIRST — AMBIGUITY CHECK: after reading the authority doc and ISSUES
#31, if anything is ambiguous, contradictory, or underspecified (plan vs
repo state vs this prompt), ask Ali concrete questions and WAIT for
answers — never resolve ambiguity by improvising. Material resolutions =
dated §12 amendment; trivial clarifications → session log + close-out.

SCOPE:
1. Implement ImportPruneUsage as a new lane under
   semantic_merge_driver/strategies/ (existing registration pattern;
   behind SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1, §2 N2). Differential
   3-way per §2 sketch; guards per §2 + whatever the specs demand. Design
   from specs.csv + derivation unit contents ONLY.
2. Fixtures: one per distinct D1 spec shape (positive) + cross-category
   negatives (signature-change, rename, clean-refactor shapes must NOT
   fire) + guard negatives (wildcard import, java.lang, FQN, shadowing).
3. Unit tests + full driver suite green; no existing expected verdict
   changes (§3 regression floor).
4. GD2(iii): run the lane over the 100 tune-controls — 0 flags required;
   fix any flag in-session (tuning is allowed here and only here).

GUARDRAILS: no held-out/eval-controls/spgroup access; no changes to
existing lanes (that is S-D4); no evaluation-split numbers of any kind.
EXIT: lane + fixtures + tests committed (refs #31); GD2 verdict + lane
commit recorded in manifest + ISSUES close-out. STOP.
```

### S-D3 — build D2 `SignatureStaleCall`

```
Session S-D3 of the detector cycle — ISSUES #31. AUTHORITY:
outputs/detector-cycle-plan.md §2 (D2 row), §3, §5 GD2. Paste-time check
against ISSUES #31 done.

STATE: S-D1/S-D2 DONE (see ISSUES #31 close-outs). Specs at
reports_detectors/specs/specs.csv (D2 rows).

FIRST — AMBIGUITY CHECK: after reading the authority doc and ISSUES
#31, if anything is ambiguous, contradictory, or underspecified (plan vs
repo state vs this prompt), ask Ali concrete questions and WAIT for
answers — never resolve ambiguity by improvising. Material resolutions =
dated §12 amendment; trivial clarifications → session log + close-out.

SCOPE: as S-D2, for SignatureStaleCall — per-branch RM2 signature-change
types (read the existing rm2 lane machinery first; reuse, don't fork);
arity mismatch as primary signal; CONSERVATIVE bias (prefer FN over FP);
explicit guards: overloads with matching arity, varargs, builder/chained
calls, cross-file targets the file-local view cannot type. Fixtures incl.
overload/varargs negatives. GD2 (i)-(iii) identical, incl. 0 flags on
tune-controls.

REVIEW (§12 Amendment 3): before closing, review the lane three ways —
(a) as PROJECT CODE: idioms, registration, config wiring, and test
patterns consistent with the existing lanes (running /code-review at
high effort is sanctioned); (b) as a STANDALONE ANALYSIS: correctness
against Java language semantics for its shape (overloads, varargs,
generics, static vs instance calls), consulting JLS where unclear;
(c) as an OPEN-SOURCE PRACTICE COMPARISON: check the approach against
how established open-source analyzers solve this same problem — for
signature/call matching: Error Prone's method matchers, PMD, SpotBugs,
IntelliJ inspections — via their docs/source. Record in the close-out
which comparators were consulted and any divergence adopted or
deliberately rejected. Bounded: consult, don't port; no new runtime
dependencies. Each finding is either fixed — with GD2 (i)-(iii) rerun
if the lane changed after its gate run — or recorded as a documented
non-fix with a reason. Timeboxed: a review pass, not a rewrite.

GUARDRAILS/EXIT: as S-D2. STOP after GD2 verdict recorded.
```

### S-D4 — D3 lane widening

```
Session S-D4 of the detector cycle — ISSUES #31. AUTHORITY:
outputs/detector-cycle-plan.md §2 (D3 row), §3 (regression floor!), §5
GD2. Paste-time check against ISSUES #31 done.

STATE: S-D1..S-D3 DONE. Gap inventory at
reports_detectors/specs/gap_inventory.md lists the concrete shapes the
existing RM2RenameConflict / JoernUnresolvedReference lanes miss on
removed-declaration + renamed-or-relocated derivation units.

FIRST — AMBIGUITY CHECK: after reading the authority doc and ISSUES
#31, if anything is ambiguous, contradictory, or underspecified (plan vs
repo state vs this prompt), ask Ali concrete questions and WAIT for
answers — never resolve ambiguity by improvising. Material resolutions =
dated §12 amendment; trivial clarifications → session log + close-out.

SCOPE:
1. Widen the existing lanes to cover the inventoried shapes — smallest
   change that covers each shape, with guards; Stage-B style
   evidence-guided edits. NO behavior change on any shape the lanes
   already handle: every existing fixture/regression test keeps its
   expected verdict (this is the hard constraint of the session).
2. New fixtures per inventoried shape (positive) + negatives mirroring
   the lanes' existing guard patterns.
3. GD2 (i)-(iii): full driver suite + Stage-C postfix regression tests
   green; 0 flags on the 100 tune-controls with the widened lanes (run
   the FULL suite incl. D1/D2 — interactions count).
4. REVIEW (§12 Amendment 3): before closing, review the widened lanes
   three ways — (a) as PROJECT CODE: the widening stays idiomatic to the
   lanes it modifies (guards, config, test patterns; /code-review at
   high effort sanctioned); (b) as a STANDALONE ANALYSIS: correctness
   against Java language semantics for the widened shapes (field/method
   removal, rename propagation, inner classes, qualified references),
   consulting JLS where unclear; (c) as an OPEN-SOURCE PRACTICE
   COMPARISON: check the approach against how established open-source
   analyzers handle unresolved/dangling references and rename
   propagation — Error Prone, SpotBugs, IntelliJ unresolved-reference
   inspections, Checkstyle — via their docs/source; record comparators
   consulted + divergences adopted or deliberately rejected. Bounded:
   consult, don't port; no new runtime dependencies. Fix (with GD2
   rerun if a lane changed post-gate) or document the non-fix.
   Timeboxed: a review pass, not a rewrite.

GUARDRAILS/EXIT: as S-D2; additionally record in the close-out which
inventoried shapes were deliberately NOT covered and why (FP risk beats
coverage — §2 rejected-list logic applies at shape level too). STOP.
```

### S-D5 — freeze + evaluation battery

```
Session S-D5 of the detector cycle — ISSUES #31. AUTHORITY:
outputs/detector-cycle-plan.md §3 (freeze), §4, §5 GD3, §9. Paste-time
check against ISSUES #31 done.

STATE: S-D1..S-D4 DONE, GD2 PASS ×3. The detector suite is complete.

FIRST — AMBIGUITY CHECK: after reading the authority doc and ISSUES
#31, if anything is ambiguous, contradictory, or underspecified (plan vs
repo state vs this prompt), ask Ali concrete questions and WAIT for
answers — never resolve ambiguity by improvising. Material resolutions =
dated §12 amendment; trivial clarifications → session log + close-out.

SCOPE:
1. FREEZE: record the suite commit in reports_detectors/manifest.json as
   detector_suite_commit BEFORE any evaluation run. From here, detector
   changes = dated §12 amendment + full rerun of this session.
2. Materialize eval-controls (n=200, committed list from S-D1) and the
   spgroup quadruples (existing phase2b tooling).
3. Evaluation battery — TWO ARMS per §5 GD3 (baseline = current default
   lanes, experimental flag OFF; experimental = full suite, flag ON),
   resumable caches in eval/ keyed by arm:
   a. Held-out recall: both arms over the 110 held-out units (unit =
      merge, any-file-flag; machine-caught = any lane flag on the unit).
      Report per final-label category and pooled name-binding family, per
      arm + the added-recall delta (Wilson CIs). Also run over derivation
      units — descriptive only, labeled TUNING-TAINTED everywhere shown.
   b. FP: both arms over the 200 eval-controls — record every flag.
   c. spgroup: experimental arm over 66 labeled-clean (+ 17
      labeled-positive, descriptive) via the phase2b harness pattern.
   Ship scenario JSONs with the deploy and materialize eval-controls
   on-instance (blobless clones are fast on EC2; CLI-DEPLOY precedent).
   Runtime: one AWS cycle per deploy/aws/CLI-DEPLOY.md (standing rule:
   AWS over local — c7i.2xlarge native x86_64, images built on-instance,
   env validated by reproducing a canonical table before scoring, teardown
   verified; ~$5-10). Local is acceptable only for the pre-flight smoke
   subset (<=20 units).
4. GD3: (ii) and (iii) require ZERO flags. Any control/spgroup flag →
   STOP, package it for Ali's adjudication with full context, and wait —
   the amendment path is his call. Held-out flags do NOT gate here; they
   go to S-D6 adjudication.
5. Build the S-D6 adjudication UI (make_adjudication_ui.py style): every
   held-out flag with unit inputs, lane evidence, final taxonomy label,
   CAUSAL/INCIDENTAL/FP controls + rationale field → adjudication/.

GUARDRAILS: no detector edits post-freeze; held-out contents appear only
inside eval caches + the UI. EXIT: eval numbers + stability of the zero-FP
record recorded in manifest + ISSUES close-out; UI delivered. STOP —
S-D6 begins with Ali's rulings.
```

### S-D6 — adjudication, FINDINGS, close-out

```
Session S-D6 of the detector cycle — ISSUES #31, FINAL session. AUTHORITY:
outputs/detector-cycle-plan.md §5 GD4, §9. Paste-time check against
ISSUES #31 done.

STATE: S-D5 DONE, GD3 PASS (zero FP on eval-controls + spgroup). Ali's
rulings at reports_detectors/adjudication/<rulings file> — all held-out
flags ruled CAUSAL/INCIDENTAL/FP with rationale.

FIRST — AMBIGUITY CHECK: after reading the authority doc and ISSUES
#31, if anything is ambiguous, contradictory, or underspecified (plan vs
repo state vs this prompt), ask Ali concrete questions and WAIT for
answers — never resolve ambiguity by improvising. Material resolutions =
dated §12 amendment; trivial clarifications → session log + close-out.

SCOPE:
1. Apply rulings: citable held-out recall = CAUSAL flags only, per
   category + pooled name-binding family, Wilson CIs; precision =
   causal/(all flags), reported per lane. GD4 = completeness of
   adjudication.
2. FINDINGS.md + summary.txt per §9: recall table (held-out primary,
   baseline + experimental arms + added-recall delta; derivation numbers
   present but marked TUNING-TAINTED), the zero-FP record extension
   (eval-controls + spgroup), per-lane precision, honest small-n framing
   (per-category cells are small — pooled family number is the citable
   one), and the never-blend banner.
3. Close-out: THREATS additions (new instrument, small cells, file-local
   scope); STATUS update (lanes stay behind the experimental flag — §2
   N2; default-enabling is explicitly deferred); ISSUES #31 → resolved
   with the citable one-liner; decide-and-record whether optional S-D7
   (Stage-C-protocol rerun) and S-D8 (whole-driver re-pricing) run now,
   later, or not at all — with one sentence of rationale each.

EXIT: labels applied, FINDINGS committed, #31 resolved, decisions on
S-D7/S-D8 recorded. Commits ref #31. Program CLOSED (or handed to S-D7).
```

### S-D7 / S-D8 — optional follow-ons (stubs)

Prompts to be instantiated from this template only if S-D6 green-lights
them: S-D7 = rerun the Stage-C frozen-evaluation protocol
(`detect_validate.py`, its original populations) with the extended suite —
the only blend-safe "before/after R2" comparison; S-D8 = P2-style
whole-driver re-pricing with the experimental lanes enabled. Both inherit
§3 freeze (same suite commit) and the never-blend rule.

---

## 9. Metrics and reporting rules

- Wilson 95% CIs on every fraction; per-category held-out cells are small
  (~14 max) — the **pooled name-binding-family recall is the primary
  citable number**; per-category rows are reported with CIs and framed as
  bounded, not pinned.
- **Definitions:** machine-caught = ≥1 lane flag on the unit (any lane —
  lane-vs-label attribution happens at adjudication, not in machine
  numbers); added recall = experimental-arm recall − baseline-arm recall
  on the same units.
- Citable recall counts **adjudicated-causal flags only**; machine flag
  rates appear beside them, labeled.
- Derivation-split numbers are always labeled TUNING-TAINTED.
- The zero-FP record statement covers: 100 tune-controls (development),
  200 eval-controls + 66 spgroup-clean (evaluation, gated).
- Never blend with taxonomy base rates, Stage-C R1/R2, or Phase-2b recall.

## 10. Budget and calendar

API ≈ $2–5 (S-D1 batch only). AWS ≈ $5–10 (S-D5 evaluation cycle — the
default per the standing AWS-over-local rule; S-D7/S-D8, if green-lit, are
one further cycle each). Ali's time: ~10 min (GD1) + adjudication
~1–2 h (GD4) + rulings only if GD3 surfaces a flag. At two implementation
touchpoints/week alongside thesis writing: **~3 calendar weeks**; sessions
are paste-and-go from §8.

## 11. Ratify at freeze (Ali)

1. Control-draw design (§4): sizes (tune 100 / eval 200), seeds, and the
   draw constraints (≤3/repo, ~60/40 file-count stratification).
   — **ratified (2026-07-16)**
2. GD3 zero-FP bar as an absolute gate (vs. Ali-adjudicated tolerance) —
   plan encodes: absolute, with Ali adjudicating any flag before the
   amendment decision. — **ratified (2026-07-16)**
3. Optional S-D7/S-D8 deferred to an S-D6 decision (vs. pre-committed).
   — **ratified (2026-07-16)**

All three items ratified by Ali 2026-07-16; the commit introducing these
marks is the freeze commit.

## 12. Amendments

### Amendment 1 — 2026-07-16 (S-D1): control-draw attrition mechanism + eval-pool wording

Ruled by Ali in-session (S-D1 ambiguity gate); two questions, both material.

1. **Attrition/replacement.** §4 commits control lists in S-D1, but
   materialization can fail per merge (clone timeout/fail, multi-merge-base,
   missing file content — Stage C absorbed these by counting only successes,
   impossible for a list-first draw). Ruling: **viability + spares.**
   - *Tune-controls:* Stage-C-style draw-with-materialization — the seeded
     walk (SEED_TUNE) materializes candidates as it goes; the first 60
     stratum-≤3 + 40 stratum->3 successes ARE the committed list (tune
     contents are allowed design inputs under §3, so materializing during
     the draw leaks nothing).
   - *Eval-controls:* the committed list = the first 120 + 80 candidates in
     the seeded walk (SEED_EVAL) passing a **viability check without content
     extraction** (blobless clone + by-SHA parent fetch + exactly-one
     merge-base), plus **40 committed ordered spares** (24 ≤3 / 16 >3)
     passing the same check. S-D5 materializes the 200 primaries; any
     failure is replaced by the next unused spare of the same stratum that
     keeps per-repo ≤3 among effective members — deterministic, no session
     ever hand-picks. Replacement events are recorded in the manifest.
   - GD2(iii)/GD3(ii) "the 100 / the 200" = the effective materialized
     lists under this rule.
2. **Eval-pool wording.** §4's eval-controls row "fresh `Tests_passed`
   merges" means the **same pool as tune-controls**: has-Java rows with
   mergiraf == `Tests_passed` (the `semantic_ctl` criterion; the S-D1
   prompt's single "Tests_passed pool"). One pool, two seeded draws;
   exclusions make the three control sets (Stage-C 195, tune, eval)
   mutually disjoint.

### Amendment 2 — 2026-07-16 (S-D1): GD1 failure-path ruling — file-local scope reduction

GD1 machine coverage came in at **37/48 = 77.1% < 80%** (specs batch
`msgbatch_01EwsTTHk1AHnDw1b98AXwxY`; per-unit record in
`reports_detectors/specs/gd1_machine.json`). Decomposition: **9
cross-file-declaration units** (the changed/removed/renamed declaration
lives outside the unit's intersecting files — unreachable for the
file-local detectors this cycle builds, by construction) + **2
truncation-limited units**; quote provenance 91 exact / 3 normalized /
0 absent — the misses are honest escapes, not extraction defects.

Ali ruled failure-path option **(b) scope reduction**:

- D2/D3 **design targets are the file-local shapes** — units whose
  declaration change is visible within the unit's intersecting files.
  The 9 cross-file units (ids in `gd1_machine.json`
  `unusable_decomposition.cross_file_declaration`) are out-of-target for
  detector design; they **remain in every held-out recall denominator**,
  and the file-local ceiling is reported honestly in FINDINGS (S-D6).
- The 2 truncation-limited units remain in-target (counted unusable).
- GD1 re-scored on the file-local target set: **37/39 = 94.9% ≥ 80% →
  GD1 PASS.** D1 unaffected (21/21). No batch rerun.

### Amendment 3 — 2026-07-16 (post-S-D2): dual review pass in build sessions

**Process amendment — no measurement surface touched** (gates, corpora,
firewall, detector targets, and the two-arm evaluation design are all
unchanged).

- The S-D3 and S-D4 prompts gain a REVIEW step: the new/changed lane is
  reviewed (a) as **project code** — idioms, registration, config wiring,
  test patterns consistent with the existing lanes (`/code-review` at high
  effort sanctioned); (b) as a **standalone analysis** — correctness
  against Java language semantics for its shape, consulting JLS where a
  rule is unclear; and (c) as an **open-source practice comparison** —
  the approach is checked against how established open-source analyzers
  (Error Prone, Checkstyle, PMD, SpotBugs, IntelliJ inspections) solve the
  same problem for that shape, via their docs/source; the close-out
  records which comparators were consulted and which divergences were
  adopted or deliberately rejected. Bounded: consult, don't port; no new
  runtime dependencies. Every finding is either fixed or recorded as a
  documented non-fix with a reason. Timeboxed: a review pass, not a
  rewrite. *(rev. 2026-07-16-b: clause (c) made explicit at Ali's
  direction — before any session consumed this amendment.)*
- **S-D2 / D1 is already compliant** — an equivalent review was conducted
  in its own session after the GD2 verdict (addendum commits `bed3638` +
  `c14670a`: clause-keyword FN fix, enum-constant parse, marker check on
  stripped text; GD2 rerun green — suite 197/197, 0-flag tune-control run,
  recorded in runs.md run 3 + manifest + ISSUES #31). No retroactive
  action required.
- Review-driven code changes remain subject to the §3 detector freeze:
  before the S-D5 freeze ⇒ a GD2 (i)-(iii) rerun suffices; after it ⇒
  full S-D5 rerun. Rationale: post-gate code changes invalidate the gate
  verdict, not the plan.
