# Threats to Validity

Project-level threats-to-validity analysis for both subprojects
(`merge-tool-comparison/` empirical evaluation; `semantic_merge_driver/`
constructive pipeline). Written for the thesis defence; resolves
[`merge-tool-comparison/ISSUES.md` #7](merge-tool-comparison/ISSUES.md).

**Snapshot date:** 2026-07-12 (refreshed for the ISSUES #30 taxonomy
program close-out, §4.4 + summary row 16; prior refresh 2026-06-12 for
the ISSUES #29 Stage-C detection run; before that 2026-06-09 for ISSUES
#27 / #28, the post-Spork tool-gap recon, and the PoC-framing decision). This
document is *derived* (per the
[source-of-truth rule](README.md#source-of-truth)): the code and
`reports/results.csv` are authoritative. The **comparator-side** numbers
(§§1–2, 4–5) carry their original **2026-05-16** adversarial-audit
provenance and are unchanged (the n=50 comparator pipeline has not moved
since); the **driver-routing** numbers (§3, §6) come from the later
#27/#28 gate runs and the recon; the **detection-layer** R1/R2 numbers
(§3) come from the #29 Stage-C run (frozen `843e5f5`). All numbers lag
the code if the pipeline changes — re-verify before citing.

Taxonomy follows Wohlin et al. / Runeson & Höst (construct, internal,
external, conclusion/statistical, reliability). The headline claims under
scrutiny are two — an *empirical* (comparator-side) claim and a
*constructive* (driver-routing) claim.

**Empirical claim:**

> Under a four-tier normalization comparator (M3.5 gjf → 3b Tier C → 3d
> Tier D → 3e Tier E), Spork scores **TP 32 / FP 11** on n=50, recovering
> X_total = 30 over the pre-3b baseline of TP 2 — exactly hitting the
> [`comparator-3b-ast-normalize.md` §3](docs/plans/comparator-3b-ast-normalize.md)
> floor of X ≥ 30 / FP ≤ 11, and reframing Spork's apparent FP rate as a
> comparator-ground-truth gap rather than a Spork defect.

**Constructive claim (added 2026-06-09):**

> Across CI-grade per-cluster evidence ([ISSUES #27](merge-tool-comparison/ISSUES.md)
> Spork, [#28](merge-tool-comparison/ISSUES.md) Weave), a 5,405-merge
> zero-cost analysis, and a 2020–2025 literature survey
> ([`research/outputs/post-spork-tool-gap-recon.md`](research/outputs/post-spork-tool-gap-recon.md)),
> **no merge tool beats Mergiraf** in any refactoring cluster on quality
> or speed. Both hypothesized specialist arms are refuted, so the `auto`
> router's honest map collapses to `NONE → git-merge-file,
> everything-else → Mergiraf`. The `semantic_merge_driver` is therefore a
> **proof of concept** of a routing *mechanism* whose specialist premise is
> currently unmet — the same framework would detect such a specialist if
> one emerged. All evaluated tools are retained as selectable backends +
> comparator baselines (2026-06-09 decision).

Independent audit (2026-05-16) reproduced `results.csv` byte-identically
and found **zero fake true-positives** on this corpus. The threats below
qualify *how far that conclusion generalises and how robustly it holds*,
not whether the measurement is fabricated (it is not).

---

## 1. Construct validity — does the metric measure correct merging?

### 1.1 The equivalence oracle is textual/AST, not behavioural — PRIMARY THREAT

TP/FP is decided by `comparator.contents_match`: a tool's clean output
is a **TP iff it is *textually* equal to the developer resolution after a
four-tier normalization ladder** (whitespace → google-java-format
roundtrip → tree-sitter AST canonicalisation → token-fold). It is *not*
decided by compilation or test-suite execution. Consequences:

- Two outputs that are AST-equivalent but behaviourally different in an
  uncovered way are scored equal; two behaviourally-equivalent outputs
  the pipeline cannot canonicalise are scored different (conservative —
  inflates FP, not TP).
- The construct "correct merge" is operationalised as "matches the
  developer's text modulo formatting", which presumes the developer
  resolution is itself correct (see §1.3).

**Mitigation:** every transform is AST-aware with explicit
parent-context / precedence guards; the pipeline fails *closed* (a
parse-fail degrades to "different", never to a spurious match); the
audit manually confirmed all 32 Spork TPs are genuine AST-equivalent
reformatting (comment placement, redundant/cast/unary parens, same-type
array shorthand, double-suffix and hex-case normalization).

**Residual risk:** the oracle is an instrument the result is sensitive
to (§2.1), and two of its transforms are not semantics-preserving in
general (§1.2). Behavioural ground truth (option 3a, test-suite
execution) is the principled fix and remains deferred.

### 1.2 Two Tier E transforms are normalization-loss, not semantics-preserving

Surfaced by the 2026-05-16 audit; tracked as
[`ISSUES.md` #25](merge-tool-comparison/ISSUES.md).

| Transform | Loss | Adversarial counterexample | Sound on n=50? |
|---|---|---|---|
| **3e.2** `strip_array_creation_shorthand` | erases array runtime component type | `Object[] x = new String[]{"a"}` ≡ `Object[] x = {"a"}` (differs in `getClass()` / `ArrayStoreException`); `var x = new int[]{}` → invalid `var x = {}` | yes — every firing had declared-component-type == created-element-type |
| **3e.9** `normalize_float_literal_suffix` | conflates `float`/`double`; one invalid-Java edge | `f(0.1f)` ≡ `f(0.1d)` (different overloads); `0x1p1d` → `0x1p1.0` (not legal Java) | yes — only `d`/`D` ever fired (double↔double, value-preserving); no `f`/`F`, no hex-float |

The plan's own [§8 risk table](docs/plans/comparator-3e-tier-e-transforms.md)
rates 3e.9 "Medium — loses semantic info"; its §13 "no semantic-change
risk has surfaced" overstates this and is the one identified
documentation overclaim. 3e.2's array-type erasure is not acknowledged
in the plan at all.

**Why the result still stands:** the audit attributed every TP that
*depends* on these two transforms (5 of 32 — see §4.1) and inspected
each: all fired strictly in their sound regime on this corpus. So the
threat is **construct soundness is dataset-contingent**, not "the
numbers are wrong". Hardening (component-type check; stop stripping
`f`/`F`; hex-float no-op) is deferred to a later cycle per ISSUES #25.

### 1.3 Developer resolution as ground truth

The committed merge is assumed correct and canonical. A developer may
have (a) introduced a bug, (b) chosen one of several valid resolutions,
or (c) post-merge-refactored, making a tool's *also-valid* output a
false FP. This biases *all* tools' FP counts upward symmetrically and is
intrinsic to the Schesch et al. methodology this project replicates.
**Unmitigated**; documented as accepted.

### 1.4 Tool-characterisation confounds

- **JDime** crashes on 48/50 (96%). Schesch et al. themselves excluded
  JDime as "unsuitable for practical use". The 1 TP / 1 FP is not a
  meaningful F1; reported with the crash-rate caveat, not as tool
  quality.
- **Mastery** 12 TP / 32 FP: the 32 FPs are dominated by intrinsic
  content loss (file headers, Javadoc) — a tool-family property shared
  with JDime, not a comparator artefact. The +2 over Tier D is a
  comment-loss-closure bonus, not evidence Mastery improved.
- **Mergiraf** (the driver default and the bar every other tool is judged
  against) is *best-available, not good in absolute terms*: on the full
  Schesch n=5,405 corpus it passes the test suite on **58.2%** of merges
  with **~36%** (1,953) `Merge_failed`, and it is not even its own best
  configuration — an ORT pre-pass (`mergiraf_plus`) beats plain Mergiraf
  **61.0% [0.597, 0.623] vs 58.2% [0.568, 0.595]** (non-overlapping CIs;
  [recon §2.6](research/outputs/post-spork-tool-gap-recon.md)). Its clean
  merges are **not** all dev-identical either: on MIGRATE_DECL it produced
  7 dev-mismatches (#28) — but **0/7 fail tests** (5 valid-alternative
  merges, 2 whole-merge granularity), so the exact-dev-match oracle
  *understates* its real accuracy. Mergiraf is reported as the strongest
  available backend, never as a solved-merge oracle.
- **The comparator-gap is symmetric.** ISSUES #2's exact-dev-match oracle
  did not only *inflate* Spork's FP rate; it also *manufactured* an
  apparent Mergiraf weakness on MIGRATE_DECL (dev-match precision ~0.54)
  that motivated the Weave specialist arm — which the test-suite oracle
  then dissolved (#28, 0/7 dev-FPs fail tests). Any "tool X is weak on
  cluster Y" claim must be cross-checked against the test-suite label
  before it drives a design decision.
- Construct risk: a *textual* oracle interacts differently with a
  pretty-printer tool (Spork) than with a content-dropping tool
  (Mastery/JDime). The per-tool caveats in
  [STATUS.md](STATUS.md) / ISSUES #2 are required for a fair
  cross-tool reading; the single F1 column is not comparable across the
  two tool families without them.

---

## 2. Internal validity — are the causal claims sound?

### 2.1 Instrumentation / researcher-degrees-of-freedom — PRIMARY THREAT

The comparator normalization pipeline was developed **iteratively
against the very Spork residuals it scores** (M3.5 → 3b → 3d → 3e, four
tiers, each tier's transforms chosen by analysing the previous tier's
still-FP set). This is textbook overfitting-to-corpus risk: the
instrument was tuned until the target metric (Spork X_total) crossed a
pre-registered floor.

**Mitigations:** (a) the floor (X ≥ 30 / FP ≤ 11) was fixed in the
[3b plan §3 on 2026-05-14](docs/plans/comparator-3b-ast-normalize.md),
*before* Tier D/E — it was **not** redefined post-hoc (audit-verified);
(b) every transform is a generic AST/precedence rule, not a
scenario-specific patch; (c) the kill switch
`MERGE_COMPARATOR_AST_NORMALIZE=off` cleanly reverts to M3.5.

**Residual risk:** transforms are generic *in form* but their *selection*
was corpus-driven; the pipeline is not validated on a held-out corpus.
The "comparator-gap, not Spork bug" reframing is well-evidenced on n=50
but is an in-sample conclusion.

### 2.2 Per-phase attribution is self-reported

The plan §13 per-phase recovery table (e.g. "+3e.3 → 23, +7") derives
from the author's prototype scratch scripts
(`merge-tool-comparison/workspace/tier_e_prototype*.py`). The audit
independently reproduced **only the cumulative** (Spork 32, the sole
floor-gating number) and the suite (112 tests). Per-phase deltas are
**not** independently verified and the plan itself flags them
"approximate"; they should not be cited as measured per-transform
effects.

### 2.3 Entanglement of transforms

The plan repeatedly notes recovery is meaningful only cumulatively
(many residual scenarios need several transforms before the canonical
forms collapse). This is honestly disclosed but means no single
transform's contribution is cleanly identifiable — limiting causal
claims about *which* normalization closes the gap.

---

## 3. External validity — generalisability

- **Language:** Java only. tree-sitter-java grammar; gjf formatter; the
  AST transforms encode JLS precedence. No claim transfers to other
  languages.
- **Corpus:** the Schesch et al. (ASE 2024) dataset, n=50. One dataset,
  one mining methodology.
- **Selection bias:** scenario sampling is most-recent-merge-first
  ([`ISSUES.md` #6](merge-tool-comparison/ISSUES.md)); recent merges in
  mature repos skew simple, plausibly favouring the textual baseline
  (git-merge-file 39/0).
- **Tool coverage:** the headline n=50 comparator numbers rest largely on
  one structured-merge tool (Spork); JDime is unusable here, Mastery is
  content-lossy, and Mergiraf + Weave were added as comparator baselines
  only later (2026-05-20). Conclusions about "structured merge vs textual
  merge" therefore lean on Spork.
- **Constructive side:** `semantic_merge_driver` is a proof-of-concept
  for **3 of 7** conflict categories (#3 Data Flow Interference via Joern
  [Phase 2a — canonical clear→read shape only, line-ordering heuristic];
  #5 Loop Semantics via Joern; #6 Method Rename — widened 2026-06-11 to a
  rename/declaration-interference family via RM2 per-branch lanes + a new
  differential unresolved-reference strategy). No claim of general
  semantic-merge coverage; GumTree and SafeMerge stages are unbuilt (see
  [STATUS.md](STATUS.md)).
- **Detection layer R1/R2 now MEASURED (ISSUES #29 Stage C, 2026-06-12,
  v2 frozen `843e5f5`):** on the full attribution-friendly populations
  (164 scored real silent failures / 193 scored good merges, Schesch
  test-suite ground truth): **R2 = 12/164 = 7.3% [4.2, 12.4]**, **R1 =
  4/193 = 2.1% [0.8, 5.2]**; 1/443 files UNANALYZABLE; G1 positive
  control 10/10. All 4 control FPs trace to two identified one-line [superseded — see row 14: ruling done 2026-06-20, amended 2026-09-04; post-fix round 1 cleared 1 of 4, round 2's guard extensions cleared the rest]
  var-lane defects (call-site exclusion; comment-stripper newline bug) —
  left in place per the pre-registered freeze, post-fix run optional.
  **Category base rates at scale: #3 and #5 produced 0 detections and 0
  FPs on 443 real files** — the detection mass is entirely
  rename/scope-consistency (#6-family), confirming the pilot's
  base-rate inversion of the taxonomy's emphasis. Hit adjudication
  (§4.6 written rationale per flag) is the remaining manual step;
  evidence in `merge-tool-comparison/reports_detection/full/`.
- **No specialist beats Mergiraf — the routing premise is currently unmet
  (the PoC framing).** The `auto` router was designed to send each
  refactoring cluster to a specialist backend, but both hypothesized
  specialist arms are now empirically refuted: `INTRA_BODY → Spork`
  ([#27](merge-tool-comparison/ISSUES.md), CI-grade — pooled precision
  0.49 [0.37, 0.60] vs Mergiraf 0.78 [0.66, 0.86], ~14× slower, 0
  synthetic strict-wins) and `MIGRATE_DECL → Weave`
  ([#28](merge-tool-comparison/ISSUES.md), W3 gate n=38 — Weave wins 0 vs
  Mergiraf, McNemar p=0.0078). The post-Spork recon generalises it: across
  the full 5,405-merge corpus and the 2020–2025 Java-merge literature,
  **no tool beats Mergiraf** in any cluster on quality or speed
  ([recon](research/outputs/post-spork-tool-gap-recon.md)). So the honest
  router collapses to `NONE → git, everything-else → Mergiraf`, and the
  multi-arm design is a **proof of concept** whose specialist premise no
  current tool satisfies. External-validity consequence: the driver's
  *demonstrated* contribution is the `NONE → git` fast-path + the semantic
  verification layer, **not** quality-improving routing. All tools are kept
  as artefacts so the mechanism stays exercisable if a future specialist
  emerges (2026-06-09 decision).
- **Auto-routing depends on RM2 recall — now MEASURED (was the Phase-1
  caveat):** the classifier is file-level, so cross-file refactoring
  evidence is invisible to it; every missed refactoring falls to the
  `NONE` cluster and routes to git-merge-file. The file-vs-project
  dual-mode measurement deferred as [`ISSUES.md` #26](merge-tool-comparison/ISSUES.md)
  ran 2026-07-03 (AWS, full Schesch n=50,
  [`reports_rm2_recall/FINDINGS.md`](merge-tool-comparison/reports_rm2_recall/FINDINGS.md)):
  file-level recall of project-level same-file evidence is **90.7%
  [83.8, 94.9]** pooled (R0's n=10 66.7% was an outlier artifact; misses
  are exactly the predicted cross-file Extract/Move family; only-file = 0,
  i.e. file-level never hallucinates). Of the 18/50 (36%) file-level
  `NONE` scenarios, **1 is a false-`NONE`** (5.6% [1.0, 25.8] of the
  bucket; 2.0% [0.4, 10.5] of all merges) — the conflation this bullet
  used to flag as unmeasured is now quantified and small, and it fails
  safe post-flip (the blind spot routes to git, the conservative backend
  per P2/P3). The same file-level blindness bounds the RM2-based #6-family
  detection lane: ~9% of same-file-visible refactoring evidence is
  cross-file-only — a limitations-chapter FN bound (the 2026-09-04 atam4j re-ruling is one measured instance: a cross-file FN that had been counted as a catch, see row 14), not otherwise a Stage-C number
  change. Whether routing *improves* outcomes was the deferred Phase-2
  soundness question — answered **negatively for both specialist arms**
  (#27/#28, see the bullet above); with #26 measured, no open piece
  remains here.

---

## 4. Conclusion / statistical validity

### 4.1 The floor is hit with zero margin on both bounds — PRIMARY THREAT

Spork **TP 32 → X_total = 32 − 2 = 30**, exactly meeting X ≥ 30; **FP 11**
exactly meeting FP ≤ 11. No slack on either bound. The audit measured
the load-bearing dependence:

| Pipeline | Spork TP | X_total | Floor (X ≥ 30 / FP ≤ 11) |
|---|---|---|---|
| Full Tier C+D+E (committed) | 32 | 30 | **met, zero margin** |
| With 3e.2 + 3e.9 disabled | 27 | 25 | **missed** |

**5 of the 32 TPs** depend on the two normalization-loss transforms of
§1.2: `adangel_pmd f9c6b0b08d` (UnusedImportsRule), and `addthis
stream-lib` HyperLogLogPlus variants `59ece5dc87`, `e4a8d65ba1`,
`323e301061`, `e221cb6ab7`. All five were manually confirmed
AST-equivalent (sound-regime firings), so the floor is *genuinely* met —
but the margin is entirely consumed by transforms whose soundness is
corpus-contingent. A corpus containing covariant-array or
float-overload merges could move ≥1 of these to fake-TP and miss the
floor. **The "floor hit exactly ✓" framing should always be reported
with this fragility caveat.**

### 4.2 No statistical confidence measures

n=50, single run, no confidence intervals / significance tests
([`ISSUES.md` #5](merge-tool-comparison/ISSUES.md)). A Wilson interval
on Spork precision (32/43 clean = 0.74) is wide at this n. F1 deltas
between tools are reported as point estimates only. Differences should
not be claimed significant.

This caveat is specific to the **n=50 comparator headline**. The
**driver-routing** verdicts (#27/#28) are, by contrast, CI-grade — Wilson
95% intervals plus a paired McNemar exact test (#28, p=0.0078) — but they
are computed in scratch scripts (`tools/select_materialize.py`,
`tools/migrate_decl_w3.py`), not in `metrics.py`; productionizing
confidence intervals into the comparator metrics is still ISSUES #5.

### 4.3 Non-linear per-tier recovery narrative

The "M3.5 +1 / 3b +5 / 3d +7 / 3e +18" acceleration is arithmetically
consistent with the committed-CSV trajectory (audit-verified) but is
partly an artefact of Tier E shipping 11 transforms vs 5–6 in prior
tiers; "acceleration" is mild narrative spin, not a measured
super-linear effect.

### 4.4 Taxonomy program (ISSUES #30) — protocol §11 additions, appended with results (2026-07-12)

Applies to `merge-tool-comparison/reports_taxonomy/FINDINGS.md` (census-308 →
275 scored; base rates: attributed 43.3% [37.5, 49.2], escape 56.7%,
name-binding 71.4% of attributed). **Never blended with Stage-C R1/R2 or
Phase-2b** — different instruments, questions, and populations.

1. **LLM coder ≠ human ground truth.** Mitigated by two human gates: G1
   spot-check (0/15 qualifying rejections) and G3 reliability (Ali accepted
   12/12 sampled agreeing labels, [75.8, 100]; ruled all 47 disagreements).
   Acceptance/override rates published with the base rates.
2. **Whole-merge test label vs per-unit mechanism.** The failure may live
   outside the shown files or in cross-file interaction; absorbed by the
   escape hatches and *reported* as the 56.7% not-cleanly-merge-attributable
   stratum, never forced into categories.
3. **Dev-diff anchoring bias.** Rule R2 (mechanism must be constructible from
   the parent-side interaction; dev-diff corroborates only) + adjudication
   convention: `merged == developer` proves nothing by itself (it is the
   population's normal case — 144/275 units — and hid both real defects and
   genuinely clean merges).
4. **Same-corpus codebook and eval.** §4 split firewall held: codebook derived
   from derivation units only; held-out contents never in codebook/FINDINGS
   prose; the Phase-3 prompt additionally **excluded the codebook's §5
   coverage table** (a 60-unit derivation answer key) so the closed relabel
   stayed independent. residual-other = 0 on the 110 held-out units is the
   generalization check.
5. **Truncation.** Recorded per unit, analyzed as a covariate: attribution
   does not collapse (T0 40.6% / T2 54.0% / T3 42.3%).
6. **Flaky Schesch labels.** `flaky-suspect` first-class: 2/275 = 0.7%.
7. **Single-model coder.** Run-variance measured (the G3 stability metric:
   82.9% [78.0, 86.9], κ 0.788 over 275 units); model-*family* bias is not
   measured and is disclosed as such.
8. **Compile-check noise.** Single-file javac RESOLVE errors are unreliable;
   only the merged-vs-dev delta was shown, under caveat (R7), auxiliary only.
9. **Fabricated evidence survived schema validation (S4 instance).** One
   pass's ruling candidate quoted conflict markers that appear nowhere in its
   input; schema-conforming, caught only by the human adjudication gate.
   Phase 1 ran a machine quote-provenance precheck; Phase 3 did not — future
   closed-coding instruments should. (One observed instance across 550
   Phase-3 responses; the G1 precheck found 0/225 fabricated in Phase 1.)
10. **Reliability gate width.** The gated agreeing sample is n=12 (a forced
    consequence of 47 disagreements under the ≤60 set cap): 12/12 = 100%
    [75.8, 100] — the lower bound sits just above the 75% gate. Cite as
    corroborating the stability metric, not as a standalone precision claim.
11. **Mid-study instrument amendment.** G3 stability first ran YELLOW (78.9%,
    κ 0.741); the single sanctioned Amendment 2 (escape-hatch boundary
    clarification only — no category/enum/threshold change) was approved and
    **both passes fully rerun** (no selective reuse; v1 archived in
    `phase3/yellow_v1/`). The rerun is a controlled comparison: the targeted
    `none-identified`↔`indeterminate` confusion fell 35→21 while
    category↔category stayed at noise level (3→6).
12. **Fork-duplicate census rows.** The census counts Schesch *rows*, so fork
    twins of the same merge appear twice (enderstone pair verified
    byte-identical; kaazing pair). Labeled consistently, counted separately;
    deduplication would change n, not the picture.

---

## 5. Reliability — reproducibility

- **Docker images unpinned.** jdime / spork / mastery / refactoring-miner
  Dockerfiles clone from `master` without a commit SHA
  ([`ISSUES.md` #10](merge-tool-comparison/ISSUES.md)); only
  `mergiraf:0.17.0` is pinned. A rebuild on another date may yield
  different tool binaries → different `results.csv`. The committed
  `reports/` artefacts are preserved precisely because re-derivation is
  not bit-reproducible.
- **Apple Silicon emulation.** All tools run `--platform linux/amd64`
  via Rosetta/QEMU ([`ISSUES.md` #17](merge-tool-comparison/ISSUES.md));
  a theoretical source of emulation-dependent behaviour, though caching
  of tool outputs makes the evaluation deterministic given fixed caches.
  **No longer purely theoretical — measured twice (P2/P3):** (i) the gjf
  image built on Apple Silicon *without* `--platform linux/amd64` (the
  one unpinned-platform image) died silently (`exec format error`) on
  x86 AWS, collapsing `contents_match` tiers 2+3 to whitespace-only —
  Spork scored 1/42 (pre-M3.5 signature) until the image was rebuilt
  natively and the environment re-validated by exact reproduction of
  the canonical six-tool numbers; (ii) even between healthy
  environments, borderline files flip (±1 file). Lesson: platform-pin
  every image AND **probe the formatter at runtime** (a loaded image is
  not a working one); one validated environment per cited table
  (`reports_whole_driver/FINDINGS.md` v2 §7a).
- **Evaluation is cache-replayable.** `evaluate` + `report` regenerate
  `results.csv` byte-identically from cached tool outputs (audit-
  confirmed). Reliability of the *scoring* is high; reliability of the
  *tool execution* is the unpinned-Docker risk above.
- **Test-suite integrity.** The 2026-05-16 audit found the 3e.0
  regression test (`test_unwrap_with_leading_comment_in_block`) was
  **non-discriminating** — it passed identically against the buggy and
  fixed D.1 code, so it did not guard the regression it claimed to. It
  has been replaced with a trailing-comment fixture
  (`test_unwrap_with_trailing_comment_in_block`) that fails under the
  buggy `is` code and passes under the fixed `==` code. Suite 112/112.
  Lesson: a green suite did not imply the D.1 fix was guarded; other
  preserve/no-op tests use weak `substring in out` assertions and may
  share this weakness.
- **Prototype scripts are scratch.** `workspace/tier_e_prototype*.py`
  are the author's own working files, not an independent oracle; per-
  phase numbers traceable only to them inherit this reliability limit
  (§2.2).

---

## 6. Summary of primary threats and disposition

| # | Threat | Category | Disposition |
|---|---|---|---|
| 1 | Textual/AST oracle, not behavioural | Construct | Mitigated (fail-closed, audited); behavioural GT (3a) deferred |
| 2 | 3e.2 / 3e.9 not semantics-preserving in general | Construct | Sound on n=50 (audited); hardening tracked ISSUES #25 |
| 3 | Comparator tuned against its own scored residuals | Internal | Floor pre-registered; transforms generic; no held-out validation |
| 4 | Floor met with zero margin; 5/32 TPs on lossy transforms | Conclusion | Genuine on this corpus; **must be cited with fragility caveat** |
| 5 | Developer resolution assumed correct | Construct | Unmitigated; intrinsic to replicated methodology |
| 6 | n=50, no confidence intervals | Conclusion | ISSUES #5; report n prominently, avoid significance claims |
| 7 | Java-only, single corpus, recent-merge bias | External | ISSUES #6; scope claims to Java/Schesch |
| 8 | Unpinned tool Docker images | Reliability | ISSUES #10; preserved `reports/` artefacts are the citable record |
| 9 | Per-phase attribution self-reported | Internal/Reliability | Only cumulative independently verified |
| 10 | Constructive side covers 3/7 categories (#3 partial) | External | PoC-scope claim only; STATUS.md authoritative |
| 11 | No specialist beats Mergiraf; both router arms refuted (#27/#28) | External/Conclusion | CI-grade (Wilson + McNemar p=0.0078); `auto` honest map collapses to NONE→git, else→Mergiraf |
| 12 | Driver is a PoC of a routing mechanism whose premise is unmet | External | Honest framing (2026-06-09); all tools kept as artefacts; contribution = NONE→git fast-path + verification layer |
| 13 | Mergiraf is best-available, not good in absolute terms | Construct/External | 58.2% pass, ~36% Merge_failed; `mergiraf_plus` (ORT pre-pass) beats it 61.0% vs 58.2%; cite as strongest backend, not an oracle |
| 14 | Detection layer measured: R2 7.3% [4.2,12.4], R1 2.1% [0.8,5.2] (Stage C, n=164/193, v2 @ `843e5f5`) | Conclusion/External | Pre-registered design (pilot→improve→frozen run); whole-merge `Tests_failed` label is a noisy per-file oracle (16/180 positives all-diverged at file level); **§4.6 adjudicated (Ali, 2026-06-20, `hit_adjudications.md`; AMENDED 2026-09-04 after audit): 9 of 11 R2 flags CAUSAL — atam4j re-ruled DETECTOR-FP (flagged file compiles; the break is in an unflagged sibling file = a measured cross-file false negative) and tcurdt DETECTOR-FP (method call; retired post-fix); citable "9 CAUSAL of 164 = 5.5% [2.9,10.1]", flag precision 9/15 overall; all 4 R1 FPs confirmed — cleared by two var-lane fixes plus two guard extensions (round 1 cleared aerospike only); the procedure was a single unblinded rater with pre-filled draft labels (0 overrides)**; **post-fix DONE (2026-07-03, two labeled AWS rounds, `5ed92a2`+`f964354`): R1 = 0/193 = 0.0% [0, 2.0], R2 = 11/164 — round 1 revealed the tcurdt flag was defect-dependent (right merge, mechanically wrong pointer → honestly retired) and characterized two residual one-char guard defects that round 2 fixed; zero positive-verdict changes between rounds; cite the frozen numbers as primary and the post-fix pair as the fix-verification** (`reports_detection/postfix{,2}/`); categories #3/#5: zero occurrences in 443 real files; **Phase-2b external oracle DONE (2026-07-05, spgroup mergedataset @ 04a18017, detectors @ `f964354`, `reports_detection/phase2b/`): recall on 17 labeled-interference units 0/17 [0, 18.4], FP on 66 labeled-clean units 0/66 [0, 5.5], G1 10/10 both arms; the single #3-family positive (reassignment-shape stale read) missed exactly as the frozen pre-run mapping predicted — the literal-`.clear()` limit is now a measured FN; benchmark's interference mass sits in uncovered #1/#2 (12/17, draft mapping pending Ali's adjudication), zero #4/#5/#7 instances; NEW labeled evaluation, never blended with Stage C** |
| 15 | P2/P3 whole-driver runs: hybrid oracle + enriched corpus + scoring-environment integrity | Construct/Conclusion/Reliability | Hybrid oracle (test label only for Mergiraf-equal outputs; divergent outputs dev-match-scored ⇒ FP over-count per the W3 lesson — pre-flip's 21 control FPs and per-backend FP rates are **upper bounds**); corpus is Mergiraf-relative + enriched ⇒ only bare→driver deltas and within-corpus comparisons are claimed; **scoring-environment integrity measured twice** — (i) an arm64 gjf image died silently on x86 AWS, collapsing `contents_match` to whitespace-only (P2 v1 tables were degraded-scored; repaired env validated by exact reproduction of the canonical six-tool numbers incl. Spork 32/11, now scores everything and agrees with local full normalization), (ii) even healthy environments flip borderline files ⇒ **one validated environment per table, formatter probed not assumed** (`reports_whole_driver/FINDINGS.md` v2 §7a; `deploy/aws/CLI-DEPLOY.md` lesson) |
| 16 | Taxonomy base rates (ISSUES #30): attributed 43.3% [37.5,49.2] / escape 56.7% / name-binding 71.4% of attributed (n=275) | Conclusion/Internal | Pre-registered 3-phase design (G0–G3 all PASS); double-pass stability 82.9% κ0.788 after the single sanctioned Amendment 2 (both passes fully rerun; yellow v1 archived); Ali ruled all 47 disagreements + accepted 12/12 sampled agreements [75.8,100] (n=12 gate — corroborating, not standalone); escape mass is a first-class stratum, never forced into categories; residual-other 0/110 held-out = generalization check; one fabricated-evidence instance caught by the human gate (§4.4.9); **never blend with Stage-C R1/R2 or Phase-2b** |

**Honest one-line framing for the defence:** the empirical result is
real, reproducible, and audited free of fabricated true-positives on the
Schesch n=50 corpus; its principal limitations are that the
correctness oracle is textual rather than behavioural, that two Tier E
normalizations are sound on this corpus but not by construction, and
that the floor is met with no margin — so the headline should be stated
as *"comparator-gap substantially closed on this corpus"*, never as an
unconditional property of Spork.

**Honest one-line framing for the constructive side:** the
`semantic_merge_driver` is a *proof of concept* — its routing *mechanism*
is built and verified, but no merge tool currently beats Mergiraf in any
cluster (CI-grade, #27/#28 + the recon), so both hypothesized specialist
arms are refuted and the honest router is *"`NONE → git`,
everything-else → Mergiraf"*. The demonstrated contribution is the
`NONE → git` fast-path plus the semantic verification layer (3 of 7
categories, #3 partial), **not** quality-improving routing; all evaluated
tools are retained as artefacts so the mechanism stays exercisable if a
future specialist clears the bar.

## 7. Detector cycle D1–D3 additions (ISSUES #31, 2026-07-20)

The detector-cycle numbers (`merge-tool-comparison/reports_detectors/FINDINGS.md`)
are a **fourth instrument** — never blended with the taxonomy base rates,
Stage-C R1/R2, or Phase-2b recall. Threats specific to it:

- **Small per-category cells.** Held-out category cells max out at 14 units;
  the pooled name-binding-family recall (16/37 = 43.2% [28.7, 59.1]) is the
  primary citable number; per-category rows are bounded, not pinned.
- **Single labeled corpus for held-out recall.** The 110 held-out units are
  Schesch-derived (same census as the taxonomy); the family-recall claim has
  no second corpus. The spgroup run bounds only the FP side externally.
- **Mergiraf-version skew in the control construct, measured once.** The
  eval-control pool's `Tests_passed` premise was computed with the dataset's
  mergiraf (0.4.x era); one of 197 controls (jgralab) is verifiably broken
  when reproduced with the pinned 0.17.0 — Ali-ruled incidental-but-true.
  The control labels are otherwise corroborated (196/197 + 100/100 clean).
- **File-local scope ceiling.** D2's category measured at 0/14 (cross-file
  declarations + same-arity shapes out of designed reach); S4/S5 cross-file
  shapes unreachable by construction; the **same-package residual** of the
  D1/D3 textual family is measured at 2 instances (1 unit-level FP, 1
  sub-flag inside a causal unit) — extract-class refactors are file-locally
  indistinguishable from deletions.
- **Single-rater rulings against pre-filled drafts.** All 20 GD4 rulings
  were made in a review page that pre-filled each unit's label and rationale
  with a one-key accept; all 20 drafts were accepted, 0 overrides, no second
  rater, rater not blind to arm or category. The identical procedure produced
  2 wrong rulings of 11 in the Stage-C round (row 14). A 2026-09-05 re-read
  of this round upheld all 20 rulings and found three rationales contradicted
  by the sources (amended in place).
- **Held-out split leaks by content (found 2026-09-05).** The 60/40 split was
  drawn over Schesch rows without grouping fork rows of one merge: six
  held-out rows are byte-identical to derivation rows, one of them a family
  catch that is also an S-D1 D1 spec unit; two merges appeared twice inside
  held-out, one pair flagged. Ruled: one unit per distinct merge, spec
  twin excluded — citable family recall 14/35 = 40.0% [25.6, 56.4]
  (as run 16/37 = 43.2%), D1 12/12 and 11/12, held-out 16/107. 12 of 110
  rows were scored on a partial file set; 61 of 110 share a repository with
  the derivation split. The 100 tune-controls in the 363 are the tuning
  population (out-of-sample zero: 0/263).
- **Experimental lanes remain flag-gated.** All recall/precision numbers are
  for `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1`; the deployed default
  configuration is unchanged, and whole-driver cost with the lanes enabled
  is measured (S-D8, 2026-07-23: 1784 → 1579, −11.5%, +8.3 s/file; FINDINGS §11).
