# Detector Cycle D1–D3 — FINDINGS (ISSUES #31, S-D5/S-D6)

**AMENDED 2026-09-05** (audit in `audit_2026-09-05.md`; counting ruled by Ali the same day). The held-out split was firewalled by unit id, not by content: six of the 110 held-out rows are fork twins of derivation rows, and one of them — `sandergielisse_enderstone__9d0d7b7ba8`, a family catch — is byte-identical to derivation unit `sander2798_enderstone__9d0d7b7ba8`, which is S-D1 spec row 37 (D1, `RegionSet`). Two pairs inside the held-out split are one merge commit counted twice: `sander2798`/`sandergielisse` enderstone at b515bac1b0 (both flagged) and at 3de930e0ed (both clean). Ruling: **one unit per distinct merge content, and the design-spec twin excluded from the citable counts.** All 22 rulings are unchanged and hold on the merged source; every as-run digit reproduced. Citable population 107 units, family 35. Amended cells are marked below; as-run values are kept beside them. Exclusions: `eval/heldout_exclusions_2026-09-05.csv`; amended counts: `adjudication/causal_numbers_amended_2026-09-05.json`. Three committed rationales that contradicted the sources were amended in place (rulings unchanged).

**NEVER BLEND:** these numbers are a **fourth instrument** — separate from the
taxonomy base rates (#30), Stage-C R1/R2 (#29), and Phase-2b recall. They are
never combined with those in any derived figure.

**Provenance.** Pre-registered frozen plan `outputs/detector-cycle-plan.md`
(freeze `10b7528`, §12 Amendments 1–3); detector suite frozen at commit
**`732d8ff`** before any evaluation run (manifest record `21dcda1`; suite
340/340 green at freeze). Two-arm battery per §5 GD3 (baseline = the 5
default lanes, experimental flag OFF; experimental = the full 7-lane suite,
flag ON), run on one AWS c7i.2xlarge cycle (2026-07-16→18, images built
on-instance, per-lane smoke + known-answer validation against the committed
GD2(iii) cache: 42/42 verdict match). Harness `tools/detector_eval_run.py`;
caches + machine tables in `eval/`; Ali's GD4 rulings in
`adjudication/sd6_rulings.csv` (20/20 held-out flags; the rationales are the assistant's drafts accepted with one key, three of them amended 2026-09-05);
GD3 control-flag analysis in `eval/gd3_flag_package.md`; the ruling text itself is the `manifest.json` GD3 verdict.

## 1. Held-out recall (PRIMARY; n=107 citable units after the 2026-09-05 ruling — 110 as run; unit = merge, any-file-flag)

Citable recall counts **adjudicated-CAUSAL units only** (plan §9); machine
flag rates appear beside, labeled. Wilson 95% CIs.

| measure | baseline arm | experimental arm | added (exp-only) |
|---|---|---|---|
| machine-caught *(amended)* | 5/107 = 4.7% [2.0, 10.5] | 18/107 = 16.8% [10.9, 25.0] | 13/107 |
| **causal recall** *(amended)* | 4/107 = 3.7% [1.5, 9.2] | **16/107 = 15.0% [9.4, 22.9]** | **12/107 = 11.2% [6.5, 18.6]** |
| **pooled name-binding family (n=35) — PRIMARY CITABLE** *(amended)* | 2/35 = 5.7% [1.6, 18.6] | **14/35 = 40.0% [25.6, 56.4]** | **12/35 = 34.3% [20.8, 50.8]** |

As run (110 census rows, family 37; superseded for citation): machine-caught 5/110, 20/110, 15/110; causal 4/110, 18/110 = 16.4% [10.6, 24.4], 14/110 = 12.7%; family 2/37 = 5.4% [1.5, 17.7], 16/37 = 43.2% [28.7, 59.1], 14/37 = 37.8% [24.1, 53.9]. Held-out unit precision (amended): 16/18 units = 88.9% [67.2, 96.9].

The name-binding family = `stale-usage-of-pruned-import`,
`stale-reference-to-removed-declaration`,
`stale-reference-to-renamed-or-relocated-declaration`,
`stale-caller-of-changed-signature` (71.4% of attributed mass in the #30
census). The cycle multiplied the family's causal recall **7×** (5.7% →
40.0%; 8× as run), with the added recall wholly attributable to the new lanes (the arms
differ only through flag-gated code; zero nestedness violations).

## 2. Per-category causal recall (experimental arm; small cells — bounded, not pinned)

| final-label category | causal | Wilson 95% |
|---|---|---|
| **stale-usage-of-pruned-import** (D1's target) *(amended; 13/14 as run)* | **11/12 = 91.7%** | [64.6, 98.5] |
| stale-reference-to-renamed-or-relocated-declaration | 3/9 = 33.3% | [12.1, 64.6] |
| stale-caller-of-changed-signature (D2's target) | 0/14 = 0% | [0, 21.5] |
| stale-reference-to-removed-declaration | — | 0 units in held-out |
| insertion-anchored-to-relocated-code | 1/1 | [20.7, 100] |
| overlapping-edit-interleaving | 1/6 = 16.7% | [3.0, 56.4] |
| duplicate-concurrent-addition | 0/2 | [0, 65.8] |
| stale-expectation-of-changed-behavior | 0/1 | [0, 79.3] |
| indeterminate | 0/29 | [0, 11.7] |
| none-identified | 0/34 | [0, 10.2] |

The pooled family number is the citable one; per-category cells are small by
construction. The two tool-artifact catches (insertion-anchored,
overlapping-edit) are baseline Joern-lane catches of name-binding *symptoms*
of those mechanisms — machine-caught is any-lane by design (§9), and both
sit outside the family pool.

## 3. Per-lane precision (held-out flagged units; GD4 rulings)

| lane | causal / flagged | Wilson 95% | notes |
|---|---|---|---|
| **ImportPruneUsage (D1)** *(amended; 14/14 as run)* | **12/12 = 100%** | [75.8, 100] | workhorse: 11 own-category + 1 cross-category (vojtechhabarta: JUnit4→5 relocation caught through the import lens) |
| RM2RenameConflict | 3/4 = 75% | [30.1, 95.4] | FP: scribble — RM2 read a partial method-split as a rename; old method still declared (name-level granularity limit) |
| JoernUnresolvedReference — Joern path | 3/3 | [43.9, 100] | lienzo, erudika, email-ext (the last = static-context splice, tool-artifact symptom) |
| JoernUnresolvedReference — **D3-widened path** | **0/1** | [0, 79.3] | FP: dabsquared — ours *extracted* the class to a same-package file invisible to the file-local view (the lane's registered same-package residual) |
| SignatureStaleCall (D2) | 0 flags | — | no held-out unit in its designed reach (§5 below) |

A second same-package instance appeared *inside* a causal unit
(mcprotocollib's `MetadataType.java` sub-flag: the referenced class sits in
the same package at the merge commit; the unit stays causal via its two
other, verified-broken files — one developer-confirmed by a "Fix missing
imports??" follow-up commit). The same-package blind spot is therefore
measured at **2 occurrences / 20 flagged files** (22 as run) and stands as the D1/D3
family's dominant residual FP class.

## 4. Zero-FP record (gated populations)

- **Development side:** 0 flags on the 100 tune-controls (GD2(iii), full
  7-lane composition).
- **GD3(ii) eval-controls (n=200 effective; 197 scored, 3 all-diverged):**
  baseline arm 0 flags; experimental arm **1 flag — jgralab**, adjudicated
  by Ali **INCIDENTAL-BUT-TRUE**: the mergiraf-0.17.0-reproduced merge
  verifiably does not compile (9 uncovered `throws IOException` sites); the
  unit is a "control" only under the Schesch table's old-mergiraf verdict
  (version skew). Gate re-judged **PASS** with the finding recorded.
- **GD3(iii) spgroup labeled-clean (n=66):** experimental arm **1 flag —
  jOOQ `DSL.java`**, adjudicated **INCIDENTAL-BUT-TRUE**: the *developer's
  own shipped merge* dropped `org.jooq.conf.Settings` held by both parents
  while keeping 8 code uses (34 occurrences counting Javadoc); the developer's next commit ("[#3992] Grr Git")
  restores exactly those imports. The benchmark's "No" label attests
  behavioral non-interference, not compile-cleanliness. Gate re-judged
  **PASS** with the finding recorded — and the flag doubles as external
  validation: D1 caught a real, developer-confirmed silent breakage in a
  13k-line file of a major OSS project on a corpus curated as clean.
- **Statement:** across **363 control units** (100 + 197 + 66) the suite
  produced **zero ruled false positives** (the 100 tune-controls are the population the lanes were tuned against — D1's first run flagged one, `dynjs`, and commit `423c215` was written to clear it — so their zero is a tuning outcome; the out-of-sample zero is 0/263; the 197 eval-controls hold one fork-twin pair, so 196 distinct merges); the two flags it did raise
  are both real breakage outside the pools' label constructs. The held-out
  FP count (2 units, §3) is a *recall-side precision* figure, not part of
  this record.
- spgroup labeled-positive (17): 0 machine flags (descriptive) — consistent
  with Phase-2b's construct finding (that benchmark's interference is
  overwhelmingly behavioral #1/#2, outside all seven lanes' categories).

## 5. Honest ceilings and decompositions (Amendment-2 obligation)

- **D2 `SignatureStaleCall`: 0 held-out flags, 0/14 on its category** — the
  measured ceiling matches the S-D3 decomposition: of its derivation units,
  5 were cross-file (out of file-local reach by construction), 4 same-arity
  shapes (documented FNs under the conservative arity-only signal), and the
  rest unjoinable per-file. The census says the category carries 10.2% of
  attributed mass; detecting it at merge time needs either cross-file view
  or type resolution — both explicitly rejected this cycle (Stage-B lesson,
  plan §2). D2's fixture battery + zero-FP record stand; its recall claim
  is honestly **0 measured**.
- **D3 widening: held-out added value 0 causal / 1 FP.** The S-D4 probe
  correction predicted this direction: the bare-receiver shapes it was
  aimed at already fire the *old* Joern lane (which delivered 3/3 causal in
  baseline), and the genuinely-widened shapes are rare + same-package-prone
  on unseen data (derivation-side, TUNING-TAINTED: the widened path flagged
  7 units it was built from). The widening's value is bounded to its
  tuning corpus; its FP class is now measured.
- **Cross-file shapes (S4/S5)** remain out of reach by construction and are
  fully inside the recall denominators above; the sub-shape rejected list
  is in the S-D4 close-out (ISSUES #31).
- **Cross-category compensation:** D1 reaches the import-visible slice of
  the relocation category (1 causal catch there), partially offsetting the
  cross-file ceiling from the side.
- **D1 wildcard ceiling (added 2026-09-05).** `_FileView.covers()` treats any surviving non-static wildcard import as covering every type name, whatever its package, so one surviving `import java.util.*;` silences every pruned-import candidate in the file. D1's one own-category held-out miss (`jenkinsci_ldap-plugin__3eee59e25a`: theirs pruned `org.kohsuke.accmod.Restricted` / `NoExternalUse`, ours added 30 `@Restricted(NoExternalUse.class)` uses) is this guard. It is a designed abstention, not a bug, and it bounds D1's recall from below.

## 6. Developer-identical resolutions (convention + finding)

10 of the 16 citable causal units (10 of 18 as run) have the flagged file **byte-identical to the
developer's own resolution** (2 of them developer-confirmed broken by
immediate fix-commits: mcprotocollib "Fix missing imports??", and the jOOQ
control flag's "Grr Git" — same class). Ruling convention (set in card 1,
applied throughout, recorded in every rationale): **rulings judge the
merged artifact** — real, merge-induced, compile-breaking — and a
dev-identical resolution is noted, never a downgrade. The other 6 citable causal
units (8 as run) diverge from the developer's resolution (the break is
mergiraf-specific relative to the shipped merge).

## 7. TUNING-TAINTED derivation-split numbers (descriptive only, never citable)

Machine-caught (no adjudication performed): baseline 11/165 = 6.7%
[3.8, 11.5]; experimental 39/165 = 23.6% [17.8, 30.7]; added 28/165 = 17.0%
[12.0, 23.4]; family (n=48): baseline 5/48 = 10.4% [4.5, 22.2], experimental
30/48 = 62.5% [48.4, 74.8], family added 25/48. The D3 widened path's 7
derivation catches vs 1 held-out flag (an FP) is the clearest
split-discipline illustration in the program: the widening was built from
exactly these shapes. Full table in `eval/summary.txt`.

**Correction (2026-07-26, per the D-388 surface-don't-bury convention).**
The family cells above previously read 4/48 / 28/48 — transcribed from the
S-D5 mid-run status snapshot taken while ~44 derivation lane-rows were still
computing (that snapshot read 10/165 → 37/165 overall, family 4/48 → 28/48;
see `docs/decision-record/distilled/2026-07-16_2e726dc0.txt`). The overall
cells were updated to the final run; the family cells were not. Re-derived
2026-07-26 from the committed raw shard caches
(`eval/eval_cache_derivation_shard{0..3}_4.json`, verdicts recomputed from
the raw issue messages via the frozen stem classifier, categories from
`reports_taxonomy/labels_final.csv`): baseline **5/48**, experimental
**30/48**, added **25/48** — matching `eval/summary.txt`, `eval/runs.md`,
and `units_derivation.csv` exactly (165/165 unit statuses agree, nestedness
0 violations). This paragraph's other figures (11/165, 39/165, 28/165, the
D3-widened 7) were verified correct in the same pass. The citable held-out
numbers (§1) are a different split and are unaffected.

## 8. Runtime and cost record

One c7i.2xlarge cycle, ~40 h instance time ≈ **$17 all-in** (vs the plan's
$5–10 estimate; the battery is 8 lane
executions × 1,751 files, about 6× the Stage-C lane executions (5 × 443), and Joern-bound, so native x86 does not
accelerate it and 4-way sharding saturates the 8 vCPUs; static-shard
stragglers cost ~6 h, mitigated mid-run by cache-seeded half-shards).
Run mechanics, shard provenance, and watcher hygiene in `eval/runs.md` +
`deploy/aws/CLI-DEPLOY.md` fifth-cycle record.

## 9. Threats (summary; full list in THREATS_TO_VALIDITY.md)

Small per-category cells (pooled family number is primary); single labeled
corpus for held-out (Schesch-derived; mergiraf-version skew measured once in
its control labels); file-local scope ceiling (S4/S5, D2 decomposition);
same-package residual (2 measured instances); rulings by a single rater
(Ali) against pre-filled draft labels and rationales with a one-key accept —
all 20 drafts accepted, 0 overrides, no second rater, the rater not blind to
arm or category; the same procedure produced 2 wrong rulings of 11 in the
Stage-C round (audited 2026-09-04), and the 2026-09-05 re-read of this round
upheld all 20 rulings but found three rationales contradicted by the sources;
the held-out split is a firewall by unit id, not by content (six fork twins
crossed it, one flagged — excluded from the citable counts; two merges were
counted twice — deduplicated); 12 of the 110 held-out rows were scored on a
partial file set (1 of the causal units); 61 of 110 held-out rows share a
repository with the derivation split; detector suite frozen pre-measurement,
rulings post-hoc by design.

## 10. S-D7 addendum (2026-07-22) — Stage-C-protocol rerun: the blend-safe before/after

Green-lit at S-D6; plan §8 stub; suite unchanged at `732d8ff` (zero detector
edits, zero §12 amendments). New harness `tools/detector_stagec_rerun.py`
re-ran the frozen Stage-C instrument's PROTOCOL (detect_validate.py itself
untouched) over its ORIGINAL populations — 180-merge/232-file positives,
195-merge/239-file controls — in the S-D5 two-arm pattern, one AWS cycle
(sixth; ~9.5 h, ~$4, teardown verified). Artifacts: `stagec_rerun/`.

**Environment gate (PASS, three layers):** smoke 8/8 lane×flag rows; tune_d3
known-answer 42/42; and the S-D7-specific gate — the baseline arm reproduced
the frozen post-fix Stage-C run (`reports_detection/postfix2`, lanes
`f964354`) **verdict-for-verdict: 471/471 merge outcomes, 443/443 merged-file
sha256, 2215/2215 file×lane verdicts** — R2' baseline 11/164 (10 flag +
1 fail-closed), R1' baseline 0/193, identical to the citable Stage-C
post-fix numbers. Consistency cross-check vs S-D5 raw caches on 1,871
overlapping (scenario, lane, flag) keys: 0 disagreements (descriptive).

**Before/after on the Stage-C instrument (machine numbers; unit = merge;
BLOCKED = any scored file FLAG, else fail-closed; Wilson 95%):**

| metric | baseline (5 lanes, flag OFF) | experimental (7 lanes, flag ON) | added (exp-only units) |
|---|---|---|---|
| R2' positives blocked | 11/164 = 6.7% [3.8, 11.6] | **36/164 = 22.0% [16.3, 28.9]** | 25/164 = 15.2% [10.5, 21.5] |
| — via FLAG / fail-closed | 10 / 1 | 36 / 0 | added FLAG-blocked 26/164 = 15.9% [11.1, 22.2] |
| R1' controls blocked | 0/193 = 0.0% [0, 2.0] | 2/193 = 1.0% [0.3, 3.7] | 2/193 (both ruled INCIDENTAL-BUT-TRUE) |

Nestedness: 0 violations (no baseline-only blocks). The baseline's one
fail-closed unit (`progether_jadventure`, RM2 invocation failure) is
D1-FLAG-blocked in the experimental arm. File-level FLAG attribution
(positives, experimental): ImportPruneUsage 23, UnresolvedReference[Joern] 6,
UnresolvedReference[D3-widened] 5, RM2Rename 7; SignatureStaleCall 0 on
positives. Context rows (corpus fact, labeled): of the 164 scored positives,
98 are taxonomy-derivation units (7→22 blocked; tuning-tainted for the
experimental arm — D1–D3 were designed on them) and 66 are held-out-split
units (4→14); the 16 all-diverged merges are outside the taxonomy census.
These rows are Stage-C-instrument annotations — NOT the S-D5 held-out
instrument, whose numbers (§1) remain the citable recall claims.

**Control flags (gate nothing automatically; packaged and RULED by Ali
2026-07-22 — both INCIDENTAL-BUT-TRUE, rulings + rationales in
`stagec_rerun/ctl_flag_package.md`; per-instrument record: 0 adjudicated
FPs on the 193 Stage-C controls, never summed with the S-D5 record):**
`jgralab_jgralab__d631209030` — D1; 9 bare `IOException` uses, no covering
import, in the 0.17.0-reproduced merge only (developer resolution has 0
uses); same repo + same version-skew class as the S-D5 flag Ali ruled
incidental-but-true. `yubico_ykneo-openpgp__2766bd7444` — **D2's first flag
on real data**; full evidence chain (ours arity 2→3, theirs' new tests call
arity 2, merged declares only arity 3 with 12 stale call sites); merged is
byte-identical to the developer's shipped resolution, and the immediate next
upstream commit `de02622` "Fix tests for PDOs" converts exactly the flagged
calls — developer-confirmed breakage the `Tests_passed` label construct does
not see.

**Reading (one sentence):** on the instrument that measured the driver's
detection layer at 6.7%, the flag-ON suite triples the machine detection
rate to 22.0% at a machine control-flag cost of 2/193 — both control flags
Ali-ruled incidental-but-true (real breakage outside the label construct,
one developer-confirmed) — with the frozen baseline reproduced exactly. NEVER BLEND: these are Stage-C-instrument
numbers; the S-D5/S-D6 held-out recall + zero-FP record are a separate
instrument (§§1–4).

## 11. S-D8 addendum (2026-07-23) — whole-driver re-pricing with the lanes ON

Green-lit at S-D6; plan §8 stub; suite unchanged at `732d8ff` (zero detector
edits, zero §12 amendments). New harness `tools/whole_driver_flagon.py`
(P2 instrument `whole_driver_eval.py` imported, untouched) ran the assembled
driver — auto routing + detection + accept/reject, Schesch cost model, hybrid
oracle — over the P1 corpus (164 pos / 193 ctl merges, 232 + 239 files) as a
config pair differing ONLY by `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS`.
One AWS cycle (seventh; eu-north-1, parallel with S-D7's sixth, ~23.5 h,
~$8.5, teardown verified empty). Artifacts: `whole_driver_flagon/`.

**Environment gates (both PASS):** (1) canonical six-tool table reproduced
exactly — 36/36 count rows incl. the all-21-transforms acid row Spork 32/11;
(2) the pre-registered derived-target reconciliation (RUN_NOTES.md paste-time
patch, Ali 2026-07-22): measured flag-OFF pooled cost **1784 = predicted 1784
to the digit** (471/471 files; the five #29 post-fix movements confirmed 5/5;
only deviations = the two documented borderline textual↔semantic files,
cost-identical). The flag-OFF arm thereby ties this cycle's scoring to the
committed P3 1779 by derivation.

**Headline cost table (per file; pooled n=471; both arms @ `732d8ff`):**

| config | TP | FP | TN | FN | CR | weighted cost | cost/file |
|---|--:|--:|--:|--:|--:|--:|--:|
| driver-auto flag OFF | 226 | 171 | 66 | 8 | 0 | **1784** | 3.79 |
| driver-auto flag ON | 224 | 148 | 89 | 10 | 0 | **1579** | **3.35** |

Delta **−205 (−11.5%)**; the flag-ON driver-auto is the best driver
configuration measured to date (vs always-Mergiraf 1994, post-flip auto
1784-at-HEAD / 1779 @ `9e25b4e`). Decomposition — 25 files moved, ALL
accept→semantic-reject (zero reject→accept, as construction requires):
**23 positive-arm silent-wrongs surfaced** (cost 10→1 each, −207; lanes:
ImportPruneUsage 19, UnresolvedReference[D3-widened textual pre-pass] 4 —
dabsquared, gwtbootstrap3, javaparser, jcabi) and **2 control-arm blocks**
(cost 0→1 each, +2). Per merge (three-outcome): positives semantic-blocked
11→33, accepts 124→103; controls accepts 179→177.

**The 2 control blocks are the SAME two flags S-D7 packaged and Ali ruled
INCIDENTAL-BUT-TRUE (2026-07-22)** — `jgralab_jgralab__d631209030` (D1,
version-skew class: 9 bare `IOException` uses with no covering import in the
0.17.0-reproduced merge) and `yubico_ykneo-openpgp__2766bd7444` (D2's first
real-data catch, developer-confirmed by upstream `de02622`). Both files are
Mergiraf-routed under auto, so the merged content — and therefore the ruling
— transfers 1:1 to this instrument. The whole-driver control cost of the
lanes is +2/239 files (0.8%), both blocks true-in-artifact.

**Latency — the enabling-decision price (FIRST-CLASS):** paired per-file
delta **+8.3 s/file median** (79.5 → 87.8 s, +10.4%), mean +8.3, p90 +9.7 —
strikingly uniform across arms (pos +8.5 / ctl +8.1), routes (git +8.1 /
mergiraf +8.5), and flagged files (+8.7). Composition: two extra lane
executions per file (D2's two per-branch RM2 Docker calls dominate; D1 is
text-only; D3 rides the existing Joern pass). Within-arm runtime drift is
symmetric (first-100 vs last-100 mean: +6.6 s off-arm, +6.5 s on-arm —
corpus-order composition, not box warm-up), so the sequential arm order does
not confound the delta. At ~88 s/file the flag-ON driver remains a research
instrument (P2/P3 framing unchanged).

**Threats:** hybrid-oracle FP counts on divergent outputs are upper bounds
(shared by both arms); enriched Mergiraf-relative corpus — deltas and
within-corpus comparisons only; the two borderline files' reject-reason
nondeterminism (cost-identical); Java-only; whole-merge labels as per-file
oracle. Provenance: instance `i-0006f73fee2019c40` (c7i.2xlarge, eu-north-1
— region deviation recorded in RUN_NOTES.md), repo `50d2754`,
`DRIVER_COMMIT=732d8ff`, arms sequential (off → gate → on), `_JAVA_OPTIONS`
unset (P2/P3 latency comparability).

**Reading (one sentence):** with the experimental lanes on, the assembled
driver converts 23 silently-wrong merges into visible semantic conflicts and
lowers the whole-corpus Schesch cost by 11.5% (1784 → 1579, its best measured
configuration), at a price of +8.3 s/file (+10.4%) and two control blocks
that Ali has already ruled true-in-artifact. **The default-enabling decision
itself remains out of scope — Ali decides post-S-D8 with these numbers.**
NEVER BLEND: whole-driver cost-model numbers; the held-out recall (§§1–4),
Stage-C R2' (§10), taxonomy, and Phase-2b instruments are separate.
