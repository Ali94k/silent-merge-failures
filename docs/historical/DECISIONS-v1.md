> **ARCHIVED — v1 of the decision record, superseded 2026-07-25.**
> This is the single-session build that reported complete coverage on a measured
> 61.5% read; the v2 rebuild that replaced it lives at [`docs/DECISIONS.md`](../DECISIONS.md)
> (protocol: [`docs/decision-record/PROTOCOL.md`](../decision-record/PROTOCOL.md)).
> **v1 `D-nn` numbers do not map to v2 `D-nnn` numbers.** Kept verbatim below this
> banner per the archive-never-delete convention (v2 D-342) and Ali's 2026-07-26 ruling.

# Decision Record

Design, architecture and methodology decisions for this thesis project, reconstructed
**2026-07-25** from the Claude Code session transcripts plus git history and the plan
documents.

## How to read this

Each entry is `D-nn | date | title`, with **Decision**, **Why**, **Status** and **Source**.

**Provenance tags** — every entry carries one:

| Tag | Meaning |
|---|---|
| `[chat]` | Traced to a specific chat transcript (session id + date given in *Source*). The reasoning below is what was actually argued at the time, not a later rationalisation. |
| `[reconstructed]` | No surviving transcript. Rebuilt from commit messages, `docs/plans/`, and `docs/historical/`. Faithful to the record, but the deliberation behind it is lost. |

**Coverage and limitations — read before citing this document**

- Transcripts survive for **2026-05-18 → 2026-07-25** (32 sessions, 73.7 MB raw). Everything
  in that window is `[chat]`.
- **59 commits predate the first surviving transcript** (2026-04-15 → 2026-05-16, ~36% of the
  project's history: initial import, the comparator normalization tiers M3.5/3b/3d/3e, RM2 and
  Mergiraf integration, the 2026-05-16 audit). Those entries are `[reconstructed]` and are
  necessarily thinner — commit messages record *what* was decided far better than *why*.
- Session transcripts capture deliberation, not the full artifact. Where a decision is also
  recorded in `ISSUES.md`, `STATUS.md`, `THREATS_TO_VALIDITY.md` or a `docs/plans/` file, **those
  remain authoritative** — this document is an index and a rationale archive, not a replacement.
- **Reading coverage is partial and was audited.** Of the 15,354 distilled lines, **9,442 (61.5%)
  were read in full**; the remaining **38.5% were keyword-searched only**. A follow-up spot-check of
  the two highest-risk unread sessions recovered three decisions that the first pass had missed
  ([D-65](#d-65), [D-66](#d-66), [D-67](#d-67)) plus the local-run carve-out in [D-52](#d-52) — so
  **treat the unread remainder as a known, non-zero source of omissions**, not as verified-empty.
  Files never read in full: `4c7b0828` (2,092 lines, presentation work), `2e726dc0` (1,009, S-D5
  execution), `9e4b6896` lines 500–1257 (case-by-case Phase-3 adjudication Q&A), `acf7e1d0` (503,
  S-D3), `16127d04` (354, deck), `68c24033` (293, S-D8), `06ec13eb` (277, S-D7), `6a84a6b3` (81).
- **Subagent transcripts were not read at all** — 21 files, 5.4 MB, under `<session>/subagents/`.
  Their *final reports* survive inline in the parent sessions (that is where the four
  architecture-explorer syntheses in [D-61](#d-61) came from), but their internal reasoning does not.
- Per `CLAUDE.md`, source code and `semantic_merge_driver/initial architecture.md` outrank every
  document here, including this one.

---

## Index

| # | Decision | Date | Tag |
|---|---|---|---|
| **Scope & project architecture** | | | |
| [D-01](#d-01) | Reframe the thesis around Schesch's IVn composition finding | 2026-04-17 | `[recon]` |
| [D-02](#d-02) | Abandon the RefMerge/IntelliMerge pipeline | 2026-04–05 | `[recon]` |
| [D-03](#d-03) | Pin RefactoringMiner 2.4.0; RM 3.x out of scope | 2026-05-06 | `[recon]` |
| [D-04](#d-04) | All merge tools invoked via Docker only | 2026-05-12 | `[recon]` |
| [D-05](#d-05) | Backend-pluggable driver (`MergeBackend` ABC) | 2026-05-12 | `[recon]` |
| [D-06](#d-06) | Cluster taxonomy keyed on *kind of 3-way merge difficulty* | 2026-05-13 | `[recon]` |
| [D-07](#d-07) | Comparator tracks the driver's backends; driver is primary | 2026-05-20 | `[chat]` |
| [D-08](#d-08) | Descope GumTree / SafeMerge-Z3 / IntelliMerge on evidence | 2026-06-11 | `[chat]` |
| [D-09](#d-09) | Reorganise detection by cost/yield tiers, not taxonomy categories | 2026-06-11 | `[chat]` |
| [D-10](#d-10) | Driver's identity: a verifier on top of any merger | 2026-06-11 | `[chat]` |
| **Merge backends & routing** | | | |
| [D-11](#d-11) | Route on `ours ∪ theirs`, never on the developer resolution | 2026-05-18 | `[chat]` |
| [D-12](#d-12) | Taxonomy reuse = parity-tested copy, not cross-project import | 2026-05-18 | `[chat]` |
| [D-13](#d-13) | Drop `INTRA_BODY → Spork`; keep Spork selectable | 2026-05-26 | `[chat]` |
| [D-14](#d-14) | Drop `MIGRATE_DECL → Weave` | 2026-06-01 | `[recon]` |
| [D-15](#d-15) | Measure the pre-flip router before flipping it | 2026-06-24 | `[chat]` |
| [D-16](#d-16) | Land the flip behind a flag, not by deletion | 2026-07-02 | `[chat]` |
| **Detection layer** | | | |
| [D-17](#d-17) | Differential 3-way is the keystone rule | 2026-06-11 | `[chat]` |
| [D-18](#d-18) | Three detector designs built and dropped, kept on record | 2026-06-11 | `[chat]` |
| [D-19](#d-19) | Fail-closed aggregation | 2026-05 | `[recon]` |
| [D-20](#d-20) | New detector lanes ship flag-gated by default | 2026-07-16 | `[chat]` |
| [D-21](#d-21) | D1 is pure-textual, using the parents as semantic oracles | 2026-07-16 | `[chat]` |
| [D-22](#d-22) | D2 conservative bias: arity-primary, half-recall accepted | 2026-07-16 | `[chat]` |
| [D-65](#d-65) | D3 widens the existing lane; `RM2RenameConflict` untouched | 2026-07-16 | `[chat]` |
| [D-66](#d-66) | Amendment 3: mandated triple review before any gate closes | 2026-07-16 | `[chat]` |
| [D-67](#d-67) | Joern rejected for the import lane; the upgrade ladder recorded | 2026-07-16 | `[chat]` |
| [D-23](#d-23) | Default-enabling the experimental lanes is deferred to Ali | 2026-07-23 | `[chat]` |
| **Evaluation methodology & oracles** | | | |
| [D-24](#d-24) | Four-tier canonicalising oracle for the comparator | 2026-05-14/16 | `[recon]` |
| [D-25](#d-25) | Normalization applies uniformly to all tools | 2026-05-26 | `[chat]` |
| [D-26](#d-26) | The normalizer is a scoring device, never a merge step | 2026-05-26 | `[chat]` |
| [D-27](#d-27) | Cross-tab exact-match FPs against the test-suite oracle | 2026-05-26 | `[chat]` |
| [D-28](#d-28) | Ground truth for detection = Schesch test labels, not dev-match | 2026-06-11 | `[chat]` |
| [D-29](#d-29) | Hybrid oracle for the whole-driver evaluation | 2026-06-24 | `[chat]` |
| [D-30](#d-30) | Four instruments, never blended | 2026-07-03 | `[chat]` |
| [D-31](#d-31) | Promote the six-tool run to canonical | 2026-07-02 | `[chat]` |
| **Corpus construction & sampling** | | | |
| [D-32](#d-32) | Targeted tool-discriminating selection, not first-N | 2026-05-25 | `[chat]` |
| [D-33](#d-33) | Skip multi-base merges at materialization | 2026-05-25 | `[chat]` |
| [D-34](#d-34) | Blobless `--no-checkout` clones with a per-clone timeout | 2026-05-26 | `[chat]` |
| [D-35](#d-35) | Condition the detection population on ≤3 intersecting files | 2026-06-11 | `[chat]` |
| [D-36](#d-36) | Seeded split committed before any content-bearing API call | 2026-07-09 | `[chat]` |
| [D-37](#d-37) | Controls drawn and committed before any other work product | 2026-07-15 | `[chat]` |
| [D-38](#d-38) | Document a corpus overlap rather than redraw the lists | 2026-07-16 | `[chat]` |
| **Gate & freeze discipline** | | | |
| [D-39](#d-39) | Pre-registered gates G0/G1/G2 | 2026-06-11 | `[chat]` |
| [D-40](#d-40) | Freeze protocol: never fix a defect mid-run | 2026-06-11 | `[chat]` |
| [D-41](#d-41) | Pre-registration and numeric pass criteria before data exists | 2026-07-08 | `[chat]` |
| [D-42](#d-42) | Protocol changes only as dated, sanctioned amendments | 2026-07-08 | `[chat]` |
| [D-43](#d-43) | Regression tests must be *proven discriminating* | 2026-07-02 | `[chat]` |
| [D-44](#d-44) | Cache keys must include the code commit | 2026-07-02 | `[chat]` |
| **Human adjudication** | | | |
| [D-45](#d-45) | The tool cannot grade its own homework | 2026-06-12 | `[chat]` |
| [D-46](#d-46) | Every human-judgment round gets a purpose-built visual tool | 2026-06-20 | `[chat]` |
| [D-47](#d-47) | Escape hatches are first-class outcomes | 2026-07-08 | `[chat]` |
| [D-48](#d-48) | Score the gate on its pre-registered criterion, not the raw count | 2026-07-10 | `[chat]` |
| [D-49](#d-49) | One sanctioned clarification amendment on the G3 yellow band | 2026-07-11 | `[chat]` |
| [D-50](#d-50) | A ruling without a written rationale is not an adjudication | 2026-07-20 | `[chat]` |
| [D-51](#d-51) | Two control-gate flags ruled incidental-but-true, not FP | 2026-07-20/22 | `[chat]` |
| **Infrastructure & execution** | | | |
| [D-52](#d-52) | Prefer AWS over local for compute runs | 2026-06-25 | `[chat]` |
| [D-53](#d-53) | Scoped IAM user; credentials never enter the conversation | 2026-06-25 | `[chat]` |
| [D-54](#d-54) | Collect and commit results *before* teardown | 2026-06-26 | `[chat]` |
| [D-55](#d-55) | One canonical scoring environment; validate it by reproduction | 2026-07-02 | `[chat]` |
| **Repository & documentation conventions** | | | |
| [D-56](#d-56) | Plan docs are hypotheses; the code wins | 2026-05-18 | `[chat]` |
| [D-57](#d-57) | Artifact policy: data regenerable and ignored, reports committed | 2026-05-25 | `[chat]` |
| [D-58](#d-58) | Surface doc/code mismatches; never reconcile them silently | ongoing | `[chat]` |
| [D-59](#d-59) | Honest coverage framing: "partial — \<shape\>" | ongoing | `[chat]` |
| [D-60](#d-60) | Never delete `*.key` files | ongoing | `[recon]` |
| **Thesis framing & write-up** | | | |
| [D-61](#d-61) | Position against Schesch et al. explicitly and structurally | 2026-07-18 | `[chat]` |
| [D-62](#d-62) | Lead with the census and the zero-FP record, not with routing | 2026-07-18 | `[chat]` |
| [D-63](#d-63) | Add a methodology/infrastructure chapter and an AI-contribution chapter | 2026-07-22 | `[chat]` |
| [D-64](#d-64) | Claims ledger + LaTeX macros; write in order of frozenness | 2026-07-22 | `[chat]` |

---

# Scope & project architecture

<a id="d-01"></a>
## D-01 | 2026-04-17 | Reframe the thesis around Schesch's IVn composition finding

**Decision.** Reorient both subprojects around the ASE 2024 finding that *simple specialized
handlers composed on top of `git merge-file` outperform single complex tools* (their `IVn` =
Git + Imports + Version-Numbers). The thesis hypothesis becomes: no single tool is good at
everything; compose specialized tools at progressively more concrete abstraction levels —
simpler first, complex only where needed.

**Why.** Gives the constructive side a testable hypothesis with a published anchor, and gives
the empirical side a reason to exist beyond replication.

**Status.** The founding premise. Its *specialist-dispatch generalisation* was later refuted
(→ D-13, D-14, D-16); the `NONE→git` fast-path is what survived.

**Source.** `[reconstructed]` — commit `7856a76`; `README.md`.

<a id="d-02"></a>
## D-02 | 2026-04 → 2026-05 | Abandon the RefMerge/IntelliMerge pipeline

**Decision.** Drop the original architecture (RefactoringMiner 3.0 + **RefMerge** operation-based
merge + Mergiraf + Joern), including its design principle "prefer operation-based over
graph-based merging". Adopt Mergiraf as the structured backend and the bar everything is judged
against. RM2 survives as a *classifier* and rename detector, not as RefMerge's engine.

**Why.** `tool-evaluation-findings.md` gated RefMerge as "do NOT integrate yet" pending evidence
that Mergiraf actually fails on refactoring scenarios — evidence that never materialised.
IntelliMerge was contraindicated by the same recon.

**Status.** Superseded design preserved in `docs/historical/ARCHITECTURE-refmerge.md`.

**Source.** `[reconstructed]` — `docs/plans/tool-evaluation-findings.md`,
`docs/plans/multi_refactoring_merge_landscape.md`, `docs/historical/`.

<a id="d-03"></a>
## D-03 | 2026-05-06 | Pin RefactoringMiner 2.4.0; RM 3.x out of scope

**Decision.** Roll the pin back from 3.0.13 to **2.4.0**; JDK base 21 → 17 (RM 2.4.0 ships Java 11
bytecode). Capture every observed 2.x-vs-3.x delta in a standalone reference doc.

**Why.** RM 3.0.x is incremental Java-only maintenance over 2.x with new APIs but **no
thesis-relevant capability**; 3.1.x adds multi-language detection, which is out of scope. Two
version-specific detector deltas were measured and documented rather than assumed away
(`Replace Generic With Diamond` only in 3.0.13; `Extract And Move Method` only in 2.4.0).

**Status.** Live. F-harness recall on n=10 moved 75.0% → 66.7%, still inside the Path-D bracket,
so the selection was unchanged. (That 66.7% was later shown to be an n=10 outlier → D-30 note.)

**Source.** `[reconstructed]` — commit `5e687ce`; `docs/plans/rm2-vs-rm3-differences.md`.

<a id="d-04"></a>
## D-04 | 2026-05-12 | All merge tools invoked via Docker only

**Decision.** Every evaluated or integrated merge tool (Mergiraf, JDime, Spork, Mastery, Weave,
RefactoringMiner) is invoked through a Docker image in the `merge-tools/<name>` namespace, never
via a host PATH binary. Host installs are dev convenience only. `git` is the sole exception.
Version-pinned tags, never `:latest`.

**Why.** Reproducibility. Host installs drift silently and cannot be pinned in the repo.

**Status.** Standing rule in `CLAUDE.md`. It **overrode** the earlier `weave-integration.md`
"native, no Docker" W1 decision when Weave was integrated 2026-05-18. Retroactive pinning of
jdime/mastery/refactoring_miner remains open. Framework preprocessing is explicitly *not* covered
— tree-sitter-java runs in-process precisely because the rule targets evaluated merge tools
(commit `6cfcdfc`).

**Source.** `[reconstructed]` — commit `cafa71c`; `CLAUDE.md`.

<a id="d-05"></a>
## D-05 | 2026-05-12 | Backend-pluggable driver (`MergeBackend` ABC)

**Decision.** Route the driver's three-way merge step through a `MergeBackend` ABC selected by
`SEMANTIC_MERGE_BACKEND`. Backends mutate `ours_path` in place, **must not raise**, and return
`CLEAN`/`CONFLICT`/`CRASH`.

**Why.** Makes the backend an experimental variable rather than a hard-coded assumption — which is
what later allowed routing arms to be tested and refuted without rewriting the driver.

**Status.** Live. Shipped with an explicit honesty caveat in the commit: *"Mergiraf-as-default
lacks empirical backing until M4 lands … the git-merge-file backend is one env-flip away."*

**Source.** `[reconstructed]` — commit `3fef834`.

<a id="d-06"></a>
## D-06 | 2026-05-13 | Cluster taxonomy keyed on *kind of 3-way merge difficulty*

**Decision.** Reframe the 7-cluster RM2 taxonomy from a mix of lexical/structural criteria to one
principled criterion: **what makes each refactoring hard for a line-based merger**. Rename the
clusters accordingly and fix a total-order precedence, hardest-for-line-merge first:

```
MIGRATE_DECL > INTRA_BODY > SYMBOL_CASCADE > CONTAINER_MOVE
             > HIERARCHY_RESHAPE > LOCAL_DECL_EDIT > NONE
```

**Why.** The criterion has to be the question dispatch actually asks. When several kinds of change
coexist, route to the tool suited to the *most disruptive* one and assume the easier changes
survive it.

**Status.** Live (`core/refactoring_classifier.py`, 98 RM2 types → 7 clusters). Two limitations
were stated openly rather than discovered later: **one label routes the whole file** (no per-hunk
routing), and **the union is presence-only** — it loses branch-of-origin and count, so "both
branches renamed the same method" is indistinguishable from one branch doing it.

**Source.** `[reconstructed]` — commit `976e4b0`; limitations articulated in session `e1df1610`
(2026-05-20) `[chat]`.

<a id="d-07"></a>
## D-07 | 2026-05-20 | Comparator tracks the driver's backends; driver is primary

**Decision.** Ali's steer: *"merge tool comparator and semantic merge driver should focus on same
tool. Main focus is merge driver."* Add comparator adapters for `mergiraf` and `weave`; demote
jdime and mastery to non-driver baselines.

**Why.** Before the steer the two projects overlapped on only git-merge-file and spork — the
comparator was spending effort on tools the driver never uses while skipping the driver's two
specialist backends. The comparison exists to *justify the driver's routing*, not to stand alone.

**Status.** Standing rule in `CLAUDE.md`. Consequence accepted explicitly at the time: the
comparator's headline work (Spork gap closure, JDime crash analysis, Mastery content-loss) becomes
partly legacy.

**Source.** `[chat]` — session `e1df1610`, 2026-05-20 16:24.

<a id="d-08"></a>
## D-08 | 2026-06-11 | Descope GumTree / SafeMerge-Z3 / IntelliMerge on evidence

**Decision.** Formally descope the unbuilt half of `initial architecture.md`. Present the
architecture as *evolved by measurement* — planned pipeline → what the evidence kept, with each
removal citing its refutation (#27, #28, #29).

**Why.** Specialist arms refuted, IntelliMerge contraindicated in recon, category detectors
low-yield. Descoping on evidence is a decision; leaving them listed is an implied promise.

**Status.** Adopted as framing. Note: `initial architecture.md` was **deliberately not edited** —
it is authoritative per `CLAUDE.md`, so revising it is Ali's call. That gap is still open.

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

<a id="d-09"></a>
## D-09 | 2026-06-11 | Reorganise detection by cost/yield tiers, not taxonomy categories

**Decision.** The detection layer's real structure is cost/yield tiers, not one-file-per-category:

| Tier | Content | Evidence |
|---|---|---|
| 0 (future) | parse/compile-level sanity | cheapest check would catch the largest catchable share (4 compile errors) |
| 1 | generic differential name-resolution consistency | carries **all** true positives |
| 2 | declaration-change consistency via per-branch RM2 | corroborates and extends Tier 1 |
| 3 | category-specific queries (DFI, loops) | zero yield, zero FP — kept as honest coverage |

**Why.** Measured base rates, not design intent, should determine structure.

**Status.** Adopted as the conceptual map; the file layout still mirrors categories.
The **shared-CPG refactor** is the one structural change the data demands — each strategy
re-parses all three versions (~15 parses/file) and the zero-yield category queries consume roughly
60 of the ~74 s/merge median. ~5× latency win; decides CI-viable vs interactive-viable. Not done.

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

<a id="d-10"></a>
## D-10 | 2026-06-11 | Driver's identity: a verifier on top of any merger

**Decision.** Reframe the driver from "a smarter merger" to "**a verifier that sits on top of any
merger**": commodity merge backbone + differential verification layer + fail-closed gate, with
value measured entirely by R1/R2.

**Why.** The middle "intelligence" layer was hollowed out twice — routing collapsed to
`NONE→git, else→Mergiraf` (#27/#28) and the category detectors yield ~0 (#29). What remains is
architecturally simple and honestly describable.

**Status.** Adopted. It also produced the project's one-sentence moral, stated from two
independent experiments: *at every layer of this pipeline, well-engineered generic mechanisms beat
category-specialized cleverness, and the way to discover that is measurement against real data.*

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

---

# Merge backends & routing

<a id="d-11"></a>
## D-11 | 2026-05-18 | Route on `ours ∪ theirs`, never on the developer resolution

**Decision.** Bucket every scenario by `cluster_of(RM2(base,ours) ∪ RM2(base,theirs))` at file
level. **Overrides** `docs/plans/rm2-integration.md`, which specified the `resolution` axis.

**Why.** Two decisive reasons:

1. **Circularity.** `developer_resolution` is the oracle that *defines* TP/FP. Bucketing by a
   function of it confounds the grouping variable with the outcome variable — "cluster C has high
   FP for tool X" would partly restate "X diverged from the resolution that also produced C".
2. **Dispatch-faithfulness.** At runtime the classifier sees `(base, ours, theirs)`; **the
   resolution does not exist yet — it is what the merge is trying to produce.** A resolution-derived
   cluster is not computable at dispatch time, so even a perfectly clean signal could never feed a
   routing decision.

Costs accepted deliberately: two RM2 runs per scenario instead of one, and a noisier label (it
captures *attempted* refactorings, including ones the human later discarded). *"That noise is the
right noise"* — the router faces exactly it, which is what makes **negative** evidence valid.

**Status.** Live (`src/evaluation/categorizer.py`). This is the single most load-bearing
methodological decision on the routing side.

**Source.** `[chat]` — sessions `20b53f98` and `dc624d63`, 2026-05-18.

<a id="d-12"></a>
## D-12 | 2026-05-18 | Taxonomy reuse = parity-tested copy, not cross-project import

**Decision.** The comparator holds a **verbatim copy** of the driver's `Cluster` /
`TYPE_TO_CLUSTERS` (98 entries) / `PRECEDENCE`, guarded by `test_taxonomy_parity`. Claude
recommended a cross-project `sys.path` import; Ali chose the copy.

**Why.** Two sources of truth accepted in exchange for project independence; drift is caught
mechanically rather than prevented structurally.

**Status.** Live, with a follow-up refinement: the parity test **skips** (not fails) when the
sibling driver source is absent — *"parity unverifiable ≠ parity failure"*. Hard-failing would
redden the entire comparator suite if the subproject were checked out alone.

**Source.** `[chat]` — session `20b53f98`, 2026-05-18.

<a id="d-13"></a>
## D-13 | 2026-05-26 → 2026-05-27 | Drop `INTRA_BODY → Spork`; keep Spork selectable

**Decision.** Route `INTRA_BODY` to Mergiraf. Keep Spork as a **selectable backend**
(`SEMANTIC_MERGE_BACKEND=spork`) and as a **comparator baseline**.

**Why.** Refuted from five independent angles: file-level n=6 (Spork 1 TP/5 FP vs Mergiraf 4/0)
and an n=10 replication (5/5 vs 6/2); pooled `INTRA_BODY` precision with non-overlapping Wilson
CIs (Spork 0.49 [0.37, 0.60] vs Mergiraf 0.78 [0.66, 0.86]); Spork ~14× slower and faster in
0/146 both-clean cases; and **0 strict wins on 16 synthetic cases hand-built to favour it**.
Mergiraf beat Spork in *every* cluster with data.

**Status.** ISSUES #27, `decided` → `resolved` when the flip landed (D-16). Three-way split by
context recorded: auto-routing **no**, selectable **yes**, baseline **yes**.

**Note on the search's limits, stated at the time:** `CONTAINER_MOVE` had **0** cases and
`HIERARCHY_RESHAPE` ≤1 in both samples — **unmeasured, not refuted**. The taxonomy is
driver-centric, not Spork-centric; selection was by tool *outcome*, never by a Spork-favourable
mechanism; and there was no within-`INTRA_BODY` sub-stratification.

**Source.** `[chat]` — session `e1df1610`, 2026-05-26.

<a id="d-14"></a>
## D-14 | 2026-06-01 | Drop `MIGRATE_DECL → Weave`

**Decision.** Route `MIGRATE_DECL` to Mergiraf. Keep Weave selectable and as a comparator baseline.

**Why.** A targeted W3 run (n=38 pooled `MIGRATE_DECL` scenarios) found Weave wins **0** scenarios
over Mergiraf; its correct merges are a strict subset (paired McNemar p=0.0078) and it abstains on
all 7 Mergiraf dev-FPs. Decisively, the cluster is **not** a Mergiraf weakness under the test-suite
oracle: 0/7 of Mergiraf's dev-match "FPs" fail tests. **The opening that motivated building a Weave
specialist was itself a comparator artifact.**

**Status.** ISSUES #28, resolved with the flip (D-16).

**Source.** `[reconstructed]` — commit `a86b560`; `reports_migrate_decl/FINDINGS.md`. Corroborated
in `[chat]` session `fb0fa5c5`.

<a id="d-15"></a>
## D-15 | 2026-06-24 | Measure the pre-flip router before flipping it

**Decision.** Run the P2 whole-driver evaluation against the **committed, pre-flip** router with
the Spork/Weave arms live, even though both had already been decided DROP.

**Why.** Two reasons, both stated in the approved plan:

1. **Evaluation honesty — you measure the code that exists, not the code you intend.** Pretending
   the flip was done would have described a driver that was never committed.
2. It converts a *statistical* decision (Wilson CIs, McNemar) into **end-to-end evidence**. The
   thesis story becomes "the router as designed measurably hurts — here is the evidence-based fix",
   not "we changed the router before ever measuring it."

**Status.** Executed. Result: `driver-auto` (2055) worse than `driver-mergiraf` (1994);
**33/239 good merges silently broken** by the specialist arms vs **0** for always-Mergiraf. Verified
from per-file route records that Spork ran 79× (all `INTRA_BODY`) and Weave 47× (all
`MIGRATE_DECL`), `chosen == effective` for all 471, **zero crash-fallbacks** — so the damage is
genuine specialist behaviour, not a fallback artifact.

**Source.** `[chat]` — session `fb0fa5c5`, 2026-06-24 → 07-02.

<a id="d-16"></a>
## D-16 | 2026-07-02 | Land the flip behind a flag, not by deletion

**Decision.** Default `auto` becomes `NONE → git, everything else → Mergiraf`. The two refuted arms
stay reachable behind opt-in `SEMANTIC_MERGE_SPECIALIST_ROUTING=1`.

**Why.** Preserves the mechanism as *apparatus* — it reproduces the P2 before/after and supports
the claim that the router can dispatch to any future candidate — without letting refuted code touch
default behaviour. Plain deletion was the alternative and was judged defensible but weaker.

**Status.** Live (`9e25b4e`). Measured before/after in one validated environment:
**1925 → 1779 (−146)**, matching the pre-computed derivation *to the digit*; routing control-FPs
**21 → 0**; derivation confirmed file-for-file (471/471 accept/reject agreement). **Post-flip auto
is the best measured driver config**, beating always-Mergiraf by 215 via the `NONE→git` fast-path.
ISSUES #27/#28 → resolved.

**Source.** `[chat]` — session `fb0fa5c5`, 2026-07-02.

---

# Detection layer

<a id="d-17"></a>
## D-17 | 2026-06-11 | Differential 3-way is the keystone rule

**Decision.** Every detector analyses base, ours, theirs **and** merged, and flags only what is
present in merged and in **neither** parent. Parent contents are captured *before* the backend
overwrites the file.

**Why.** Every detector that skipped it died of false positives (v1 `JoernInfiniteLoop` drowned in
pre-existing `while(true)` idioms; the type-resolution lane drowned in parser artifacts). The
generalisable technique the thesis exports is exactly this: *apply standard static analysis
differentially across the merge triple, flag only merge-induced deltas.*

**Status.** Live and mandatory for new lanes. Each lane cancels a different noise class with the
same epistemic move — DFI cancels pre-existing stale reads via parent pattern sets,
`JoernUnresolvedReference` cancels parse blindness via parent unresolved sets, `ImportPruneUsage`
cancels import-free resolution via the absorption guard on parent usages.

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

<a id="d-18"></a>
## D-18 | 2026-06-11 | Three detector designs built and dropped, kept on record

**Decision.** Record refuted detector designs with named causes as thesis material rather than
deleting them quietly:

1. **Type-resolution lane — built, then dropped.** javasrc2cpg's type inference is version-unstable
   on real files; it flagged "import merged away" on a merged file *byte-identical* to the
   developer's resolution. Import-deletion breakage is therefore a **documented out-of-scope FN**,
   not a silent miss. (Later filled by D-21.)
2. **`(method, name)` differential keys — rejected.** Auto-numbered lowering temporaries (`$obj178`)
   and lambda names (`<lambda>20`) drift between file versions and defeat the key → name-only keys.
3. **Change-Return-Type detection — skipped as pilot-overfit.**

**Why.** The governing principle discovered here: *a detector lane survives only if it is stable
under the parser's per-version quirks, not merely correct on fixtures.*

**Status.** Recorded in `reports_detection/pilot_v2/FINDINGS.md`.

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

<a id="d-19"></a>
## D-19 | 2026-05 | Fail-closed aggregation

**Decision.** Any strategy returning `is_clean=False` → exit 1. Any strategy *raising* → exit 1.
Every strategy converts its own subprocess/parse failures into an "inconclusive" issue rather than
a silent pass, so broken tooling **blocks** merges rather than waving them through.

**Why.** A verification gate that fails open is worse than no gate.

**Status.** Live and validated by data: 1 real crash in 443 files, converted to a block exactly as
designed, contributing 0 to control-side cost.

**Source.** `[reconstructed]` — commits `044051f`, `51aa3f2`, `0d52fdb`; validated in `[chat]`
session `bfc672b4`.

<a id="d-20"></a>
## D-20 | 2026-07-16 | New detector lanes ship flag-gated by default

**Decision.** D1/D2/D3 live behind `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1`, with the flag checked
at `analyze()` **line one** — before any file I/O.

**Why.** With the flag off the default driver is bit-identical to pre-cycle behaviour. That is not
politeness: it is what makes the two-arm (`flag0` baseline / `flag1` experimental) GD3 delta
**attributable to the new lanes alone**.

**Status.** Live. Still flag-gated as of 2026-07-25 (→ D-23).

**Source.** `[chat]` — session `f0d70a59`, 2026-07-16.

<a id="d-21"></a>
## D-21 | 2026-07-16 | D1 is pure-textual, using the parents as semantic oracles

**Decision.** `ImportPruneUsage` detects import-loss breakage by **exact set algebra over import
declarations**, not by type resolution:
`lost = (imports(ours) ∪ imports(theirs)) − imports(merged)`, then a guard chain
(coverage → shadowing → occurrence → **absorption**).

**Why.** Three alternatives were considered and rejected on evidence:

- **Type inference** — built and dropped in Stage B (D-18).
- **A compile oracle** — single-file `javac` cannot resolve cross-file or classpath symbols, so the
  missing import drowns in uniform resolution noise. The spec table's `COMPILE DELTA` column reads
  "(none)" on most of the 21 true breaks. A real compile oracle needs the whole project's classpath
  at merge time, which a merge driver does not have.
- Text alone can't resolve names either — **so it never tries.** Import declarations are the one
  island of exact syntax, and **the parents act as semantic oracles**: if the pruning parent uses
  `S` *without* the import, that parent demonstrates `S` resolves import-free, so absorption
  suppresses. The semantic knowledge text lacks is *read off a compiling artifact* rather than
  computed. Every guard has the same logical form: "an alternative explanation exists that I cannot
  rule out, so abstain" — which is why the error budget is spent almost entirely on FN.

**Anti-overfitting decisions made explicitly:**
- The core predicate has **no fitted parameters** — it follows from the category definition plus
  JLS import semantics. The 21 derivation units supplied *requirements coverage*, not training data.
- The single tuning fix was made at **class** level, not instance level: a lost `java.*` wildcard
  may only be credited with names actually in the JDK's public API. Contrasted at the time with the
  overfit alternatives (a length threshold that happens to exclude the offending symbol, or
  suppressing by package).
- An **"extends ⇒ suppress inherited-member risk" guard was rejected** even though it would have
  cheaply hardened the FP surface — a real TP exists in an extending class, and a fixture now pins
  that so a future session cannot reintroduce it.

**Status.** Live, flag-gated. A post-gate critical review (Ali: *"review it critically … against
other open source projects and best practices"*) found four real defects, all fixed and **both gates
re-run** rather than assumed: `throws`/`implements`/`extends`/`permits` treated as usage positions;
enum-constant declarations added to the shadow guard; the conflict-marker check moved to stripped
text; and a `merged == parent ⇒ never flags` **soundness invariant test** added.

**Source.** `[chat]` — sessions `f0d70a59` and `734e4529`, 2026-07-16.

<a id="d-22"></a>
## D-22 | 2026-07-16 | D2 conservative bias: arity-primary, half-recall accepted

**Decision.** `SignatureStaleCall` uses **arity mismatch as the primary signal**, with an explicit
conservative bias (prefer FN over FP).

**Why.** A call site passing 3 arguments to a method whose new signature takes 4 is detectable
file-locally **by counting** — parse-level, no type resolution, small and guardable FP surface.
Return-type changes, parameter retypes and throws-clause changes all need type-level reasoning that
a single-file view without a classpath cannot do reliably — the lesson already paid for in D-18.

**Consequence measured and disclosed in advance, not discovered afterwards:** only 7 of the 14 D2
derivation units are arity-changing, so **D2's recall ceiling on its own category is roughly half**.
Framed at the time as *"not a failure mode — the designed FN cost of the conservative bias"*, with
the pooled name-binding-family number as the citable primary.

**Status.** Live, flag-gated. Final held-out result was an **honest 0** on its own category — the
file-local ceiling, reported as such.

**Source.** `[chat]` — sessions `506d875b` and `acf7e1d0`, 2026-07-16.

<a id="d-65"></a>
## D-65 | 2026-07-16 | D3 widens the existing lane; `RM2RenameConflict` untouched

**Decision.** Cover the gap-inventory shapes by **widening `JoernUnresolvedReference`** with a
flag-gated *textual* removed/renamed-declaration differential — not by adding a third new lane.
`RM2RenameConflict` was **deliberately not touched**.

**Why.** Smallest change that covers each shape. `RM2RenameConflict` was left alone because **no
inventoried shape is an RM2-record shape** — RM2 does not report the removals and relocations in
question, so widening it would add surface without adding reach.

**The session's hard constraint:** **no behaviour change on any shape the lanes already handle** —
every existing fixture and regression test keeps its expected verdict. Flag-off behaviour is
byte-identical.

**Coverage boundary recorded explicitly, per "FP risk beats coverage":** four in-reach shapes covered
(bare and `this.`-qualified field references, removed methods still called, removed inner types still
constructed); **S4/S5 cross-file shapes not covered** — out of file-local reach by construction — plus
a rejected sub-shape list in the lane header (bare type positions merged-side, `this.`-method calls,
type-param shadowing, partial overload removals).

**A probe correction to the S-D1 gap inventory was recorded rather than left to surprise S-D5:** the
*existing* lane already fires on the bare-receiver shapes (absent ≠ unresolved), so those units were
predicted to show up as **baseline-arm** catches. The genuinely Joern-invisible shapes are what drove
the widening.

**Status.** Live, flag-gated, frozen at `732d8ff`. GD2 PASS: suite 340/340, and **0 flags / 0
UNANALYZABLE** on the 100 tune-controls running the full 7-lane composition for the first time,
with zero tuning iterations needed.

**Source.** `[chat]` — session `82dd479f`, 2026-07-16.

<a id="d-66"></a>
## D-66 | 2026-07-16 | Amendment 3: mandated triple review before any gate closes

**Decision.** Before a detector session may close, review the code three ways:
**(a) as project code** — does the change stay idiomatic to the lane it modifies (guards, config, test
patterns); **(b) as standalone analysis** — is it correct against **Java language semantics**, consulting
the JLS where unclear; **(c) as an open-source practice comparison** — how do Error Prone, SpotBugs,
IntelliJ's unresolved-reference inspections and Checkstyle handle the same sub-problem? Record the
comparators consulted and every divergence adopted or deliberately rejected. **Bounded: consult, don't
port; no new runtime dependencies.** Timeboxed to a review pass, not a rewrite.

**Why.** It earned its keep immediately: the S-D4 triple pass found and fixed **8 execution-verified
false-positive vectors before the gate ran** — multi-declarators, `case ->` phantoms, lambda
scope-blindness, JLS 6.5.2 receiver re-binding, label positions, Java-14 multi-labels (fixed at the
root so D1 inherits it), and bare-position remover absorption. JLS probes 8/8.

The (c) angle also produced a genuinely useful external finding: mature AST-based tools **fail in the
same wildcard and static-member corners** this project fences off — Checkstyle's `UnusedImports`
states outright that it does not support wildcard imports *with a full AST in hand*, and PMD's
`UnnecessaryImport` has a decade-long FP tail in exactly that corner. Without a classpath, that
resolution problem has no clean answer for textual **or** AST tools, which makes the conservative
stance the right call for a CRITICAL-severity gate rather than a limitation to apologise for.

**Status.** Live for the detector cycle; recorded in `reports_detectors/tune_d3/review_record.md`.

**Source.** `[chat]` — sessions `82dd479f` and `734e4529`, 2026-07-16.

<a id="d-67"></a>
## D-67 | 2026-07-16 | Joern rejected for the import lane; the upgrade ladder recorded

**Decision.** Do **not** put Joern behind `ImportPruneUsage`. Record two ranked upgrade paths instead.

**Why Joern is the wrong tool *here* specifically** — three reasons, none of them "Joern is bad":

1. **Wrong altitude.** Import and name binding are a *frontend* concern. Joern's Java frontend is
   JavaParser plus best-effort type solving, so asking Joern "does this simple name resolve?" is
   asking JavaParser with extra layers and extra nondeterminism. A CPG earns its cost on *flow*
   properties — which is exactly why the #3/#5 detectors use it and this lane should not.
2. **Already measured, not speculative.** This repo built a Joern type-inference lane for this exact
   breakage in Stage B and dropped it (D-18). Joern costs ~34 s/merge; the textual lane runs in
   milliseconds.
3. **It would not fix the actual defects.** The verified FP shapes are *syntax-recognition* failures
   and the JDK-set gap is an *index-maintenance* failure. Neither needs a code property graph.

**The ladder, recorded for future work:**

- **Rung 1 — tree-sitter-java (tactical).** Exact `type_parameters` and `local_variable_declaration`
  nodes; error-tolerant, deterministic, no JVM, ~ms/file. Eliminates the verified FP shapes, the JLS
  §3.3 unicode-escape gap and the `case Foo f ->` blind spot **while leaving the differential and
  absorption logic byte-for-byte intact**. The key argument: the Stage-B failure argues against
  heavyweight *semantic* inference, not against exact *syntactic* parsing — regex lexing and
  tree-sitter sit in the same "no resolution" class, one just lexes Java correctly.
- **Rung 2 — differential single-file compilation with ecj (strategic).** Compile merged/ours/theirs
  with `-proceedOnError`, no classpath; key errors by (error-id, symbol), never by line; flag
  `errors(merged) − errors(ours) − errors(theirs)`. **It subsumes the lane:** the absorption guard
  becomes error-set subtraction, the hand-typed JDK sets vanish, and generics/shadowing/
  multi-declarators/patterns are handled for free. It also **generalises past imports** to any
  single-file-visible compile break — including the 4 compile-error misses from the Stage-A
  adjudication. Cost: a JVM per version and careful noise discipline.

**One honest ceiling, stated at the time:** the documented assertj FN (a side that prunes the import
but keeps its own usages) survives **every** rung, including differential ecj — the parent carries the
same unresolved-name error, so it subtracts. That FN is a property of *file-local differential
evidence*, not of the regex implementation. Only project-context compilation (a speculative merge plus
a real build) lifts it, which is a different cost class.

**Related external anchor recorded:** **Bucond** (ASE 2022) detects Java merge build conflicts without
compiling by diffing program-entity graphs across base/left/right and pattern-matching 57 cross-branch
edit combinations — this lane is effectively a single-pattern Bucond specialised to imports, and its
pattern catalogue is the obvious shopping list for sibling detectors.

**Status.** Recommendation, not implemented. Three reported JDK-set omissions from the same review
(`Map`, `InheritableThreadLocal`, the `*To*Function` family) are **still absent from the committed
file** as of 2026-07-25 — I could not determine from the transcript whether that was a deliberate
non-fix or an untracked one. The review's own recommendation was to **generate** the sets mechanically
(the goimports `mkstdlib.go` precedent) plus a sentinel test, rather than hand-maintain ~300 names.

**Source.** `[chat]` — session `734e4529`, 2026-07-16.

<a id="d-23"></a>
## D-23 | 2026-07-23 | Default-enabling the experimental lanes is deferred to Ali

**Decision.** The three new lanes remain behind the experimental flag. Default-enabling is
explicitly Ali's decision and was deliberately deferred until the **price** was measured.

**Why.** Recall without a measured cost is half a decision. S-D8 supplied the other half:
whole-driver flag-ON cost **1784 → 1579 (−11.5%)** at **+8.3 s/file**, with only 2 control blocks —
and those two are the same flags already ruled incidental-but-true (D-51), so the rulings transfer
1:1.

**Status.** **Open** as of 2026-07-25. The numbers to weigh are −205 cost against +8.3 s/file.

**Source.** `[chat]` — sessions `2e726dc0`, `06ec13eb`, `68c24033`, 2026-07-20 → 07-23.

---

# Evaluation methodology & oracles

<a id="d-24"></a>
## D-24 | 2026-05-14 → 2026-05-16 | Four-tier canonicalising oracle for the comparator

**Decision.** Build `contents_match` as a cumulative ladder: whitespace → **google-java-format**
roundtrip (M3.5, Docker) → **tree-sitter AST normalization** in tiers C (3b), D (3d) and E (3e).
Host tree-sitter-java **in-process, not in Docker**, explicitly justified against D-04 (the rule
targets evaluated merge tools, not framework preprocessing; gjf's Dockerization was driven by its
JAR+JVM distribution form).

**Why.** Under naive normalization the structured tools scored ~0.0 F1 (Spork TP 1 / FP 42), which
looked like adapter bugs. The stage-γ diagnostic and the 3j stratified manual labelling
(15/15 sampled Spork FPs AST-equivalent) showed the identical symptom had **different causes**:
Spork's residuals were AST-equivalent reformatting = a **comparator/ground-truth gap**, while
Mastery's were genuine content loss and JDime's were crashes = **intrinsic tool defects**.

**Status.** ISSUES #2, resolved at Tier E: Spork TP 32 / FP 11, hitting the pre-registered floor
(X ≥ 30) **exactly**. Two caveats are permanent and must accompany the headline: the normalizer was
tuned against the very residuals it scores (no held-out validation), and 3e.2/3e.9 are
**normalization-loss, not semantics-preserving in general** — sound on this corpus only (ISSUES #25).

**Source.** `[reconstructed]` — commits `caf33e2`, `6cfcdfc`, `3dfecf0`, `4db9329`, `60802e8`;
`docs/plans/comparator-3{b,d,e}-*.md`.

<a id="d-25"></a>
## D-25 | 2026-05-26 | Normalization applies uniformly to all tools

**Decision.** `contents_match` is generic and loops over tools — there is **no per-tool
special-casing** anywhere.

**Why.** It pre-empts the obvious objection to the routing verdict. Spork is in fact the
normalizer's **biggest beneficiary** (25 FPs recovered, vs Mergiraf's 3) and still loses — so
dropping `INTRA_BODY → Spork` is **not a normalization artifact**; it holds on the fairest
comparison available.

**Status.** Live.

**Source.** `[chat]` — session `e1df1610`, 2026-05-26.

<a id="d-26"></a>
## D-26 | 2026-05-26 | The normalizer is a scoring device, never a merge step

**Decision.** The AST normalizer is a **comparator** component only. The driver never uses it; it
decides clean-vs-conflict purely by `<<<<<<<` markers and return codes.

**Why.** Structural: the comparator *measures* correctness and has ground truth; the driver
*produces* merges and has none at merge time.

**Status.** Live, and a required framing in the thesis: **every FP figure is a comparator
measurement**, not a property of the file the driver would emit.

**Source.** `[chat]` — session `e1df1610`, 2026-05-26.

<a id="d-27"></a>
## D-27 | 2026-05-26 | Cross-tab exact-match FPs against the test-suite oracle

**Decision.** Split every apparent FP three ways rather than reporting the raw rate.

**Why.** On the Spork-focused 60: of Spork's 60 clean merges, **25 match the developer after
normalization** (pure reformatting), **19 differ but pass Schesch's test suite** (valid alternative
merges = comparator gap), and only **16 are genuinely wrong**. The headline "58% FP rate" overstates
real errors by roughly 2×; the honest number is ~27%.

**Status.** Live as a reporting convention. It is also the reason the project ultimately treats the
Schesch test-suite label as the truer oracle.

**Source.** `[chat]` — session `e1df1610`, 2026-05-26.

<a id="d-28"></a>
## D-28 | 2026-06-11 | Ground truth for detection = Schesch test labels, not dev-match

**Decision.** Positives = merges where Mergiraf merged **clean but `Tests_failed`** (the silent-
failure population the driver claims to catch). Controls = `Tests_passed`. Metrics **R1**
(false-block rate on good merges) and **R2** (block rate on real silent failures), both with
**Wilson 95% CIs**.

**Why.** The claim under test is about *silent* failures, so the population must be defined by
behaviour, not by textual divergence.

**Status.** Live and the frozen instrument for all detection numbers.
Citable: **R2 = 11 CAUSAL of 164 = 6.7% [3.8, 11.6]** with 11/11 flag precision;
**R1 frozen 4/193 = 2.1% → post-fix 0/193 = 0.0% [0, 2.0]**.

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

<a id="d-29"></a>
## D-29 | 2026-06-24 | Hybrid oracle for the whole-driver evaluation

**Decision.** Five configs (`bare-git`, `bare-mergiraf`, `driver-git`, `driver-mergiraf`,
`driver-auto`) scored on the Schesch cost model (FP ×10, conflict/crash ×1), with a hybrid oracle:
test-suite label where the driver's output matches Mergiraf's, developer-match otherwise.

**Why.** Stage C already *is* the `driver-mergiraf` arm, so only two arms needed fresh compute.
Crucially, the **legitimate comparisons are the bare→driver deltas and the routing distribution —
not cross-backend cost**, because positives are *defined* relative to Mergiraf (clean-but-failing),
which structurally disadvantages Mergiraf-like backends. This constraint is stated in FINDINGS
rather than left to the reader.

**Status.** Live. The oracle asymmetry is a documented threat.

**Source.** `[chat]` — session `fb0fa5c5`, 2026-06-24.

<a id="d-30"></a>
## D-30 | 2026-07-03 onwards | Four instruments, never blended

**Decision.** Stage-C, Phase-2b (spgroup), the taxonomy census, and the detector cycle are **four
separate instruments** with different populations and labels. No figure may combine them.

**Why.** Different populations, different label semantics, different freezes. Blending would make
every number uninterpretable.

**Status.** Standing rule, restated in every session brief since. Related supporting results:
- **Phase-2b** (external oracle): recall **0/17 [0, 18.4]**, FP **0/66 [0, 5.5]**, G1 10/10 fired
  minutes before the zeros — which is what separates "detectors are blind" from "harness is broken".
  The single #3-family unit was **predicted missed in the frozen pre-run mapping and was**.
- **#26**: file-level RM2 recall **90.7% [83.8, 94.9]** at n=50 — R0's alarming 66.7% was an n=10
  outlier; file-level is a strict subset (misses only, never spurious); the one routing-visible
  miss is a false-`NONE` at ~2% that **fails safe** to git.

**Source.** `[chat]` — sessions `8740dbd3`, `7b3b2669`, `cfe6365a`, 2026-07-03 → 07-08.

<a id="d-31"></a>
## D-31 | 2026-07-02 | Promote the six-tool run to canonical

**Decision.** Replace the 4-tool canonical `reports/results.csv` with the six-tool table (archiving
the legacy), and add Wilson CIs, a per-scenario pivot and a 5-chart pack.

**Why.** The old canonical excluded the driver's own backbones (Mergiraf, Weave) — the thesis
headline must include them.

**Status.** Live; ISSUES #4/#5/#9 resolved. **Environment-validity acid test:** the four legacy
tools reproduced their committed canonical numbers *exactly* — Spork 32/11 in particular, because it
rides all 21 normalization transforms.

**Honest caveat attached to the table:** Weave's spectacular row (precision 1.0, cost 10) is an
**abstention artifact** — it is conservative, and on the targeted `MIGRATE_DECL` gate its correct
merges were a strict subset of Mergiraf's. High precision on an easy corpus ≠ specialist value. The
corpus is "not a backend beauty contest".

**Source.** `[chat]` — session `fb0fa5c5`, 2026-07-02.

---

# Corpus construction & sampling

<a id="d-32"></a>
## D-32 | 2026-05-25 | Targeted tool-discriminating selection, not first-N

**Decision.** Select scenarios by querying Schesch's **per-tool outcome columns** (e.g.
`spork == Tests_passed AND gitmerge_ort == Merge_failed`) — free, no cloning — then clone only the
chosen rows.

**Why.** The canonical 50 are alphabetical first-N across 15 repos with **46% from just 2 repos**.
Raising the cap compounds the bias rather than fixing it. Result: expanded-60 across **50 repos**
(top-2 share 46% → 8%).

**Status.** Live (`tools/select_materialize.py`). Selection bias is stated honestly: these sets are
deliberately git-fails/structured-wins, so their FP rates are **upper bounds**, not a random sample.

**Source.** `[chat]` — session `e1df1610`, 2026-05-25.

<a id="d-33"></a>
## D-33 | 2026-05-25 | Skip multi-base merges at materialization

**Decision.** Call `git merge-base --all`; **skip** when the result is not exactly one base.

**Why.** Measured first, decided second. Prevalence is **1/50 (2%)** — `adangel_pmd 312d4c60c0` —
and it is **non-vacuous** there: the two bases differ by real code, and the stored base blob
(`f545e551`) differs from git's reconstructed `ort` virtual base (`8a58c56d`). Two alternatives were
weighed: flag-and-keep, and full virtual-base synthesis (faithful but heavy, needs git ≥ 2.38, and
the virtual base can itself conflict). **Exclude** was chosen — the data cost is trivial and the
confound is removed outright.

A mechanism correction was recorded rather than smoothed: GitPython's `merge_base()` without
`all=True` returns a **length-1 list**, so the alternative base is dropped inside `git merge-base`,
not by the `[0]` index.

**Status.** Live. Fired once on real data.

**Source.** `[chat]` — sessions `4f4f0f87` (2026-05-20, measurement) and `e1df1610` (2026-05-25,
decision).

<a id="d-34"></a>
## D-34 | 2026-05-26 | Blobless `--no-checkout` clones with a per-clone timeout

**Decision.** Clone with `--filter=blob:none --no-checkout` and a **120 s per-clone timeout**.

**Why.** Only 4 files at 4 commits are ever read, so fetching every blob and checking out the whole
tree is wasted work. The timeout converts worst case into a predictable bound (`N × timeout`) and —
more importantly — kills the **renamed/404-repo hang**, which no size-based prediction can catch.
Reaper's `size` column was tested as a predictor and **rejected** (stale 2017 metric, wrong
quantity; `clueweb` was wrongly blamed and is actually 2 MB).

**Status.** Live. Later hardened with a transient-blob-fetch crash guard and a `_ensure_commits`
by-SHA fetch that recovered all 19 unreachable-parent merges (~18% of a stratum) — GitHub *does*
serve deleted/rebased parent commits by SHA.

**Source.** `[chat]` — session `e1df1610` (2026-05-26); hardening in `92a3e464` (2026-07-08).

<a id="d-35"></a>
## D-35 | 2026-06-11 | Condition the detection population on ≤3 intersecting files

**Decision.** Restrict the Stage-A/B/C population to merges with ≤3 intersecting files
("attribution-friendly"), so a whole-merge test label can plausibly be attributed to a file.

**Why.** Necessary for causal attribution; stated as a scope limit rather than hidden.

**Status.** Live. The related **granularity finding** was replicated three times: 16/180 positives
vs 2/195 controls dissolve into file-level conflicts despite whole-merge "clean" labels — so
**whole-merge test labels are a noisy per-file oracle**. That is a methods-chapter constraint on any
future experiment design.

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

<a id="d-36"></a>
## D-36 | 2026-07-09 | Seeded split committed before any content-bearing API call

**Decision.** Compute the seeded 60/40 derivation/held-out split (`SEED=20260709`, stratified) and
**commit `split_assignment.csv` + `manifest.json` before any API request that contains unit
content**. Held-out contents are firewalled from the codebook, from anchors, from FINDINGS prose,
and from future detector design; closed coding still covers the full census so base rates stay
census-wide.

**Why.** A split decided after seeing data is not a split. The commit is the proof of ordering — the
first content-bearing call was `count_tokens` during assembly, *after* `d12cf4a`.

**Status.** Live; the firewall held through all four taxonomy sessions and the detector cycle.

**Source.** `[chat]` — sessions `cfe6365a` (protocol) and `92a3e464` (execution), 2026-07-08/09.

<a id="d-37"></a>
## D-37 | 2026-07-15 | Controls drawn and committed before any other work product

**Decision.** In the detector cycle, draw and commit tune-controls (n=100, `SEED_TUNE=20260715`) and
eval-controls (n=200, `SEED_EVAL=20260716`) **first**, before specs, before any detector code.
Tune-controls are materialized; **eval-controls stay a list and are deliberately not materialized.**

**Why.** Same principle as D-36, applied to the FP side: the zero-FP claim is only meaningful if the
control set was fixed before the detectors existed.

**Status.** Live. Both lists exclude the 195 Stage-C controls and are mutually disjoint;
disjointness, caps and strata were machine-verified and hashed into the manifest.

**Source.** `[chat]` — session `506d875b`, 2026-07-15.

<a id="d-38"></a>
## D-38 | 2026-07-16 | Document a corpus overlap rather than redraw the lists

**Decision.** 32 of the 240 eval/spare merges already had scenario JSONs on local disk, left over
from the May comparator programs (~13% overlap, expected — same Schesch table, different criteria).
**Documented and quarantined**, not redrawn.

**Why.** Stated plainly at the time: *"hand-adjusting committed lists after seeing results is the
real discipline breach."* None were git-tracked, none were read, none are sanctioned inputs to any
build session. Recorded with the full id list, an access guard in the manifest, and a paste-time
note; S-D5 materializes eval fresh from the committed list anyway. A redraw would have needed a §12
amendment.

**Status.** Live.

**Source.** `[chat]` — session `506d875b`, 2026-07-16.

---

# Gate & freeze discipline

<a id="d-39"></a>
## D-39 | 2026-06-11 | Pre-registered gates G0/G1/G2

**Decision.** Three gates fixed before the run:

- **G0** — abort thresholds (median runtime per merge, UNANALYZABLE share).
- **G1** — **inject-sanity positive control**: splice the canonical clear→read pattern into real
  merged files; the detector must fire **10/10** before scoring is allowed.
- **G2** — the freeze protocol (→ D-40).

**Why.** G1 in particular is what makes a *negative* result scientific rather than embarrassing: it
separates "the detectors are blind" from "the harness is broken". It fired 10/10 minutes before the
Phase-2b zeros, which is precisely why those zeros are citable.

**Status.** Live; the template for every later gate design.

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

<a id="d-40"></a>
## D-40 | 2026-06-11 | Freeze protocol: never fix a defect mid-run

**Decision.** A defect discovered mid-run is **not fixed mid-run**. Finish the frozen run, report it
as-is, then do a *separately labelled* post-fix run.

**Why.** Patching mid-run makes the numbers uncitable — the instrument would have been tuned on its
own test set.

**Status.** Live and honoured under pressure: the var-lane `(`-exclusion defect was identified during
Stage C and deliberately left in place; the two labelled post-fix rounds followed.

**A three-stage sequencing decision follows from it:** pilot (A) → evidence-guided v2 (B) → frozen
full run (C). Justified in practice — v2's first attempt flagged 4 of the first 7 positives from
parser artifacts, and the staged design caught it at ~10 minutes of compute instead of contaminating
a 9-hour citable run.

**Source.** `[chat]` — session `bfc672b4`, 2026-06-11.

<a id="d-41"></a>
## D-41 | 2026-07-08 | Pre-registration and numeric pass criteria before data exists

**Decision.** The taxonomy program's Session 0 produced **only** a pre-registered protocol and
committed prompt templates — no labelling, no detector changes, no blending. All gate criteria were
fixed numerically before any data existed: G0 attribution ≥35%, escape band 15–65%, spot-check ≤3/15
rejects; G2 codebook coverage ≥90% + Ali's ruling; G3 stability ≥80% agreement ∧ κ ≥0.70; reliability
acceptance ≥75%.

**Why.** Prevents tuning-on-test from the start. Also fixed in advance: the workload models (**the
same model for both batch passes, so the stability metric is comparable**; run-variance is measured
by the stability metric, not by temperature) and the rule that the old 7-category taxonomy stays as
the *historical design* taxonomy while the four-family regrouping is a candidate structure **to test
against the data, not to impose on it**.

**Status.** Live; frozen at `9209327`. ISSUES #30.

**Source.** `[chat]` — session `cfe6365a`, 2026-07-08.

<a id="d-42"></a>
## D-42 | 2026-07-08 onwards | Protocol changes only as dated, sanctioned amendments

**Decision.** Any change to a frozen protocol after data exists is a **dated §12 amendment**, never
a silent edit.

**Why.** The audit trail is the point. Amendments actually used:

| # | Change | Why it needed an amendment |
|---|---|---|
| Taxonomy A1 | `custom_id` wire encoding | The Batches API rejects `p1::<merge_id>` (pattern forbids `:`, 64-char cap). The **logical** key was unchanged — only its wire encoding — but it touches a §9-pinned field. |
| Taxonomy A2 | Escape-boundary clarification | The one sanctioned yellow-band amendment (→ D-49). |
| Detector A1 | Attrition = viability + spares | Materialization losses were not specified up front. |
| Detector A2 | GD1 rescored on the file-local target set | 9 of 11 machine-misses are cross-file declarations, **unreachable for a file-local detector by construction** — the wrong denominator. Cross-file shapes S4/S5 recorded as the documented FN ceiling rather than quietly excluded. |

Contrast: the **T3 hard-fit refinement** (18 pathological units overflowing the 30k cap) was an
*ordinary pre-G0 edit* explicitly sanctioned by §5 — and its aggressiveness was recorded per unit
(`T3/cap5`, `T3/cap1/trunc400`) **as a covariate** rather than hidden.

**Status.** Live.

**Source.** `[chat]` — sessions `92a3e464`, `9e4b6896`, `506d875b`.

<a id="d-43"></a>
## D-43 | 2026-07-02 | Regression tests must be *proven discriminating*

**Decision.** A regression test for a fixed defect must be **verified to fail on the pre-fix code
and pass on the post-fix code**.

**Why.** The 2026-05-16 audit had already caught a non-discriminating test (the 3e.0 regression test
passed identically against buggy `is` and fixed `==` code). Asserting a test "covers" a fix without
demonstrating it is not evidence. When the first attempt at this proof failed — a bad `git stash`
invocation meant both runs used the fixed code — it was **redone properly rather than accepted**.

**Status.** Live standard; applied to all four #29 post-fix tests and the detector-cycle fixtures.

**Source.** `[reconstructed]` origin (commit `4db9329`); `[chat]` session `fb0fa5c5`, 2026-07-02.

<a id="d-44"></a>
## D-44 | 2026-07-02 | Cache keys must include the code commit

**Decision.** Every resumable result cache keys on the **driver/lane commit**, not just
`config::scenario_id`.

**Why.** A self-review found the P2 harness keyed without it. The concrete failure mode: land the
route flip, re-run, and the harness **silently serves the pre-flip results for all 471 files**,
printing a "new" table that is byte-for-byte the old behaviour — no error, no warning, and the
conclusion "the flip changed nothing", which is exactly wrong. Chosen over "remember to clear the
cache" precisely because the trap fails silently.

**Status.** Live in `detect_validate.py` (which had it first) and now `whole_driver_eval.py`.

**Source.** `[chat]` — session `fb0fa5c5`, 2026-07-02.

---

# Human adjudication

<a id="d-45"></a>
## D-45 | 2026-06-12 | The tool cannot grade its own homework

**Decision.** Every detection claim is adjudicated by Ali against three questions —
**(1) is the pattern really present? (2) is it merge-induced (present in merged, in *neither*
parent)? (3) does it plausibly explain the failure?** — yielding one of three labels: **CAUSAL /
REAL-BUT-INCIDENTAL / DETECTOR-FP**, each with a written rationale. Claude drafts; Ali rules.

**Why.** "The detector fired 15 times" is a raw count. The claim the thesis wants is "caught the
actual cause", and only a human reading the source can close that gap. Claude's own assessment is
circular at one remove because it built the detectors. The gap is concrete: *measured* = "blocked 12
of 164 failing merges"; *claimed* = "caught the actual cause of 12 failures".

**Status.** The project's standing evidence standard, used for the 3j Spork residual labelling, the
23-miss classification, the 15 Stage-C hits, the Phase-2b category mapping, the taxonomy
disagreements and reliability sample, and the detector-cycle GD3/GD4 rulings. It also **legitimises
the false positives**: adjudicating the 4 control flags as DETECTOR-FP with documented root causes
turns "the tool has false positives" into "the tool's false positives are fully characterised and
fixable".

**Source.** `[chat]` — session `bfc672b4`, 2026-06-12 / 06-16.

<a id="d-46"></a>
## D-46 | 2026-06-20 onwards | Every human-judgment round gets a purpose-built visual tool

**Decision.** Each adjudication round ships a **standalone, self-contained HTML tool** plus its
committed generator, browser-verified before handover: `review_ui` (23 misses) → `adjudication_ui`
(15 Stage-C hits) → `mapping_ui` (17 Phase-2b categories) → `spotcheck_ui` (15 Phase-1 drafts) →
Phase-3 `adjudication_ui` (59 units) → S-D6 UI (20 held-out flags).

**Why.** Rulings must be made against *frozen* evidence, offline, and committed — which is what makes
"Ali-adjudicated" a citable label rather than an anecdote.

**One design decision inside the tooling deserves its own note.** RM2 **var-lane** line numbers are
computed on comment/string-stripped text and are shifted by the newline bug. The UI therefore shows
the detector's output **verbatim, with a `stripped-coord` vs `merged-coord` pill** for provenance,
but **re-locates every identifier in the actual merged file** for context. Showing the raw wrong line
would have corrupted the adjudication itself.

**A second one:** the Phase-1 spot-check UI's binary verbatim-quote checker flagged ~7% of evidence
quotes as missing. Investigation showed they were **diff-gutter/whitespace artifacts and
non-contiguous multi-line concatenations, not hallucinations**. The checker was upgraded to
**graded** matching (exact → gutter/whitespace-normalized → per-line-present → genuinely absent),
yielding **0/225 absent** — because a brittle checker showing false-red would have made the
adjudicator over-reject.

**Source.** `[chat]` — sessions `0e14484d`, `8740dbd3`, `788e483b`, `9e4b6896`, `2e726dc0`.

<a id="d-47"></a>
## D-47 | 2026-07-08 | Escape hatches are first-class outcomes

**Decision.** The LLM coder may return `none-identified`, `indeterminate` or `flaky-suspect` instead
of a mechanism, and the gate actively checks that the escape rate sits in **[15%, 65%]** — too low
means over-attribution, too high means the inputs are inadequate.

**Why.** *"Confident hallucinated causality is the #1 failure mode to design against."* The pilot
precedent (only 13 of 23 misses attributable) is quoted **inside the prompt**. Related prompt rules:
an attributed verdict needs **≥2 verbatim quotes**, and the mechanism must be constructible from the
**parent-side** interaction — the developer diff is corroboration only, to contain anchoring bias.

**Status.** Live. The escape mass turned out to be a **first-class finding**, not noise:
**156/275 = 56.7% [50.8, 62.5]** of real silent failures cannot be cleanly pinned to an in-file
mechanism.

**Source.** `[chat]` — session `cfe6365a`, 2026-07-08.

<a id="d-48"></a>
## D-48 | 2026-07-10 | Score the gate on its pre-registered criterion, not the raw count

**Decision.** Ali rejected 4 of 15 spot-check drafts; the raw count 4 > 3 would **fail** gate G1(iii).
All four were **escape-hatch** verdicts (the model claimed no mechanism, so there was no causal story
to hallucinate) rejected for a **population/selection** reason — *"not a good representation of
silent merge conflicts"* — not the pre-registered criterion *"rejected as hallucinated or
unsupported-by-quotes"*. **0 of the 11 drafts where the model did claim a mechanism were rejected.**
Ruling: **PASS, criterion-scoped.**

**Why.** The failure mode the gate exists to catch did not fire. Claude refused to score it silently
either way, laid out both readings and their consequences, and left the call to Ali — whose protocol
it is.

**Status.** **No §12 amendment was filed**, because the gate was applied exactly as written rather
than changed. The four objections were preserved verbatim and logged as a **marked Phase-2
carry-forward**: the 63.6% escape mass becomes a first-class "not-cleanly-merge-attributable"
stratum in the honest-coverage accounting.

**Source.** `[chat]` — session `788e483b`, 2026-07-10.

<a id="d-49"></a>
## D-49 | 2026-07-11 | One sanctioned clarification amendment on the G3 yellow band

**Decision.** G3 stability's first run landed **YELLOW** (78.9% agreement [73.7, 83.3], κ 0.741,
58 disagreements). The pre-registered remedy — exactly one codebook-clarification amendment, then
rerun **both** passes — was proposed to Ali and approved as **§12 Amendment 2**: an R1 clarification
distinguishing the two escape hatches by **whether a concrete cross-side interaction is even
articulable**. **No category, enum, base-rate definition, or attribution threshold changed.**

**Why.** Diagnosis first: **35 of 58 disagreements were `none-identified` ↔ `indeterminate`** — both
escapes — and only **3 of 275** flipped between two *named* categories. The mechanism taxonomy was
already reliable; the instability was an under-specified boundary between two "no-mechanism" labels,
which is exactly what one clarification can fix.

**A tempting tie-breaker was rejected on the data.** Claude nearly keyed the rule on
`merged == developer resolution`, then corrected itself: that is the **normal** case here
(144/275, 36 of them carrying real named mechanisms), so it is not a no-mechanism signal — and rule
R2 forbids leaning on the dev-diff anyway.

**Status.** Rerun **PASSED: 82.9% [78.0, 86.9], κ 0.788, 47 disagreements**, with the delta landing
exactly where the amendment targeted (`none-identified`↔`indeterminate` 35 → 21). Because the *only*
variable was the escape rule, this is a clean controlled comparison.

**Source.** `[chat]` — session `9e4b6896`, 2026-07-11.

<a id="d-50"></a>
## D-50 | 2026-07-20 | A ruling without a written rationale is not an adjudication

**Decision.** Gate GD4 requires **every** held-out flag to carry a written rationale, with a
first-card convention so later cards may cite it rather than re-derive the reasoning 20 times.

**Why.** The gate's definition is *completeness of adjudication*, and a bare verdict is not an
adjudication. Mirrors the Stage-C §4.6 round, whose rationales became the committed
`hit_adjudications.md`.

**Status.** Live.

**Source.** `[chat]` — session `2e726dc0`, 2026-07-20.

<a id="d-51"></a>
## D-51 | 2026-07-20 / 2026-07-22 | Two control-gate flags ruled incidental-but-true, not FP

**Decision.** GD3's two zero-FP gates each failed by **exactly one flag**. Both were ruled
**INCIDENTAL-BUT-TRUE**; the gates were re-judged accordingly and **no rerun was triggered**. The
alternative branch had been pre-stated: *DETECTOR-FP ⇒ dated §12 amendment + full S-D5 rerun*.

**Why, per flag:**

- **`jgralab`** — the mergiraf-**0.17.0**-reproduced merge keeps 9 bare `IOException` uses with no
  covering import, i.e. verifiably uncompilable. The "clean control" premise comes from the dataset's
  **0.4.x-era** mergiraf column: the `Tests_passed` label belongs to a *different artifact*
  (version skew), so the control premise does not describe the file that was scored.
- **`jOOQ DSL`** — the **developer's own shipped merge** dropped both `org.jooq.conf` imports while
  keeping 34 bare `Settings` uses; the dataset file is byte-identical to the real repo, and the very
  next mainline commit — titled **"Grr Git"** — restores exactly those imports. The benchmark's
  "No interference" label is a *behavioural* construct. This one doubles as **external validation**
  of the detector.

**Status.** Recorded; ISSUES #31. Final record: **0 adjudicated FPs across 363 control units**;
held-out name-binding family recall **5.4% → 43.2% [28.7, 59.1]**; D1 own-category 13/14 at 14/14
unit precision.

**Source.** `[chat]` — sessions `2e726dc0` (S-D5/S-D6) and `06ec13eb` (S-D7).

---

# Infrastructure & execution

<a id="d-52"></a>
## D-52 | 2026-06-25 | Prefer AWS over local for compute runs

**Decision.** Evaluation batteries, corpus runs and anything Docker-emulation-bound go to an EC2
cycle (`c7i.2xlarge`, native x86_64, Ubuntu 24.04, 80 GB gp3) rather than an overnight local run.
Local runs remain fine for unit tests, fixtures and small pilots (≤ ~20 units).

**Why — and this matters, because the stated rationale changed.** The driver was **not speed**: it
was Ali's constraint — *"I can not run 20 h; I need to be stationary for that long and it will
exhaust my laptop."* Any remote host solves that. Claude predicted a 5–10× native-x86 speedup;
**that did not materialise** — measured ~87 s/file on AWS vs ~80 s locally, because the bottleneck is
**Joern (JVM CPG construction), which was already native on the Mac**. The error was stated plainly
and written into `CLI-DEPLOY.md` so no later cycle repeats the assumption.

Ali also chose **sequential over `--shard`**, even after Claude showed parallel would be *both*
faster (~5 h) and cheaper (~$2–3 vs $8–9) — the simple path kept the validated harness unchanged.

**Status.** Standing rule in `CLAUDE.md`. Seven-plus cycles run, ~$5–10 each, all torn down.
Sub-rules: build images on-instance, validate the environment by reproducing a canonical table
before scoring, tear down and verify empty.

**One pre-registered carve-out.** The detector cycle's plan §5 exempts the **GD2 tune-control runs**
from this rule and runs them **locally**, by design: GD2 is the one gate where tuning is *allowed*, so
every flag triggers an in-session fix and re-score — on EC2 each iteration would be a redeploy. The
exemption held up in practice (the S-D4 Amendment-3 review landed 8 FP fixes mid-run, invalidating the
first pass for 3 of 7 lanes), and the usual reason for AWS mostly does not apply there: Joern runs
natively on PATH, the merge reproductions are cached, and only short RM2 containers are emulated. The
AWS cycle is reserved for **S-D5's frozen evaluation battery**. Cost of the carve-out, disclosed: the
plan's 1–2 h estimate was wrong for the full 7-lane composition (~6.5 h serial measured), so it was
sharded 4-way to ~2 h wall.

**Source.** `[chat]` — session `fb0fa5c5`, 2026-06-25.

<a id="d-53"></a>
## D-53 | 2026-06-25 | Scoped IAM user; credentials never enter the conversation

**Decision.** A dedicated IAM user (`claude-p2`) with **EC2-only** permissions, not root. Ali runs
`aws configure` and pastes the secret himself; Claude invokes the CLI but **never reads the
credentials file**. A budget alarm as backstop. Explicit confirmation before every spend and every
irreversible action.

**Why.** Bounded blast radius, bounded spend, and no secret ever enters the transcript.

**Status.** Live; documented in `deploy/aws/CLI-DEPLOY.md`.

**Source.** `[chat]` — session `fb0fa5c5`, 2026-06-25.

<a id="d-54"></a>
## D-54 | 2026-06-26 | Collect and commit results *before* teardown

**Decision.** Mandatory ordering: **run finishes → copy results down → verify counts → commit (and
push) → only then terminate.** Interim backup snapshots on request during long runs.

**Why.** The EBS volume is `DeleteOnTermination`; anything not copied back is gone. Each cached entry
represents ~90 s of compute.

**Status.** Live and honoured on every cycle. Deploy kit committed (`bundle.sh`, `provision.sh`,
`RUNBOOK.md` for the console path, and **`CLI-DEPLOY.md`** for the CLI path actually used, with
resource IDs, the teardown block and per-cycle records) — written specifically because the RUNBOOK
documented the console path while the CLI path was what happened.

**A cost lesson recorded rather than buried:** one Phase-2b cycle overran to ~$10 against a ~$2
estimate because the instance idled overnight after an ssh watcher died of a broken pipe without
firing its completion notification. Three concrete fixes went into `CLI-DEPLOY.md`.

**Source.** `[chat]` — sessions `fb0fa5c5` and `8740dbd3`.

<a id="d-55"></a>
## D-55 | 2026-07-02 | One canonical scoring environment; validate it by reproduction

**Decision.** Declare a single canonical scoring environment and **never mix scoring environments in
one table**. Before any scoring run, **validate the environment by reproducing the canonical
six-tool table**, and **probe the formatter** explicitly. Platform-pin every image
(`--platform linux/amd64`).

**Why — this is the project's most instructive infrastructure failure.** Identical merges scored
differently local vs AWS. Claude's *first* diagnosis (local gjf Docker timeouts under Rosetta) was
**wrong**. The real cause: the **google-java-format image had been built on Apple Silicon without a
platform pin and died silently with an exec-format error on x86**, collapsing `contents_match` to
whitespace-only normalization. So the AWS run — not the local one — was the under-normalized
environment, inverting the stated mechanism.

**Status.** The correction was published as **FINDINGS v2 with the mechanism corrected**, not
silently edited, plus THREATS row 15 and the rule set above in `CLI-DEPLOY.md`. Post-repair, the four
legacy tools reproduced their canonical numbers exactly (Spork 32/11), which is what makes the
repaired environment citable.

**Related, same lesson:** a poisoned round-2 post-fix attempt was caught when a silent `scp` failure
meant ~130 files were recomputed with round-1 code under a round-2 label. Killed, re-shipped via
`ssh cat`, md5-verified on both sides, poisoned directory wiped, restarted. **Probe, don't assume.**

**Source.** `[chat]` — session `fb0fa5c5`, 2026-07-02.

---

# Repository & documentation conventions

<a id="d-56"></a>
## D-56 | 2026-05-18 | Plan docs are hypotheses; the code wins

**Decision.** Before implementing any plan phase, validate the plan against the source and produce a
written findings memo ("Phase 0") naming every place the plan is stale — *then* plan and implement.

**Why.** Ali's framing at the time: two sibling plan docs had already been found materially stale.
The first application found three staleness items immediately, including one that would have sent the
work in the wrong direction (the plan's claimed "dead code path to activate" in `report.py` did not
exist; the real root cause was an unconditional concat in `metrics.py`).

**Status.** Standing practice. `CLAUDE.md` codifies the source-of-truth order: **code → `initial
architecture.md` → everything else is derived and may lag.**

**Source.** `[chat]` — session `20b53f98`, 2026-05-18.

<a id="d-57"></a>
## D-57 | 2026-05-25 | Artifact policy: data regenerable and ignored, reports committed

**Decision.** For every corpus: `data/scenarios_*` and `data/results_*` are **gitignored**
(regenerable via the committed selection script + seed); `reports_*/` are **committed as evidence**.
Large caches are committed when they are the resumable evidence (`raw_results.json` at 9.9 MB and
42 MB were both kept, deliberately).

**Why.** Reproducibility without bloating history with derivable bytes; the evidence a claim rests on
must be in git.

**Status.** Live. The top-level `workspace/` is gitignored — it held Joern CPG scratch (including a
`bin1` suffix escaping the `*.cpg.bin` pattern) and the spgroup `mergedataset` clone, which is its
own git repo (would commit as a broken gitlink) with GPL-3.0 content.

**Source.** `[chat]` — sessions `e1df1610`, `fb0fa5c5`, `5c9bc50d`.

<a id="d-58"></a>
## D-58 | ongoing | Surface doc/code mismatches; never reconcile them silently

**Decision.** When documentation and code disagree, surface the mismatch, ask, and record the marked
decision. Never quietly edit one to match the other.

**Why.** A silent reconciliation destroys the evidence that a decision was ever made.

**Status.** Standing rule. Applied repeatedly — e.g. refusing to bundle six unreviewed pre-session
hunks of `THREATS_TO_VALIDITY.md` into a commit until each was reviewed against documented project
state; asking before bumping a snapshot date; flagging (rather than fixing) the `make_synthetic_spork_cases.py`
docstring that claimed 6 Mergiraf strict-wins where the committed data said 3.

**Source.** `[chat]` — multiple sessions; recorded in memory as `feedback_doc_code_mismatch`.

<a id="d-59"></a>
## D-59 | ongoing | Honest coverage framing: "partial — \<shape\>"

**Decision.** Narrow proofs-of-concept are described as **"partial — \<shape\>"** with their limits
and evidence status, never as a bare "implemented".

**Why.** The clearest case: category #3's `JoernDataFlowInterference` is a **line-ordering heuristic
over literal `.clear()`**, and its name is conceded as aspirational. Phase-2b then *measured* the
consequence — the one reassignment-shape stale read in the external benchmark was missed exactly as
the frozen pre-run mapping predicted. Any phrasing that could read as "the driver detects data-flow
interference" is forbidden; the permitted claim is *"partial — literal clear→read shape, measured FN
on the one benchmark instance outside that shape."*

**Status.** Standing rule. The general form of the permitted claim, agreed 2026-07-04: never claim
*"detects semantic conflicts"* unqualified — claim *detects the rename/declaration family; screens the
rest at zero cost; measured recall bounds published for everything else.*

**Source.** `[chat]` — sessions `8740dbd3`, `bfc672b4`; recorded in memory as
`feedback_honest_coverage_framing`.

<a id="d-60"></a>
## D-60 | ongoing | Never delete `*.key` files

**Decision.** Keynote presentations stay in the repo even when seemingly stale. Ask before any
destructive action outside `data/`, caches, or `workspace/` scratch.

**Status.** Standing rule in `CLAUDE.md`. Honoured even in the awkward case: a `.key` with a macOS
Finder-duplicate `" 3"` suffix, sitting in the wrong directory, was **committed as-is and flagged**
rather than renamed or removed.

**Source.** `[reconstructed]` + `[chat]` session `42acccac`, 2026-06-09.

---

# Thesis framing & write-up

<a id="d-61"></a>
## D-61 | 2026-07-18 | Position against Schesch et al. explicitly and structurally

**Decision.** Treat the overlap with *Evaluation of Version Control Merge Tools* (Schesch et al.,
ASE 2024) as a framing problem to be solved in the text, with five concrete moves:

1. A **~1-page "Relation to Schesch et al." section in the introduction**, with a delta table.
2. **Restate the RQs so none is theirs** — theirs ask *which tool*; this thesis asks (i) how merge
   output should be judged, (ii) what mechanisms break textually clean merges, (iii) what fraction
   can be blocked fail-closed and at what FP cost, (iv) does per-case dispatch pay.
3. **Per-chapter claim hygiene** — the n=50 six-tool table is **never** presented as a rival ranking
   (n=50 vs their 6,045); its legitimate roles are backend-selection evidence and the vehicle for the
   oracle finding.
4. Keep *"evaluation of merge tools"* out of the title.
5. **Credit the dependence loudly** — their dataset and test labels are this project's ground truth,
   and IVn is the intellectual ancestor of the router.

**Why.** The overlap is real but **localized**, and the main contributions sit inside gaps that paper
*explicitly concedes*. Tool overlap is only Spork + git (Mergiraf, Weave, JDime and Mastery are
absent from it). The oracles are **inverted**: they use test-suite execution and explicitly *reject*
dev-resolution comparison as "the wrong metric" — this thesis then **quantified** that bias
(~30× FP inflation) and showed the repaired oracle converges toward theirs. The census, the zero-FP
detection record and the in-vivo routing refutations have **no counterpart** in their ten sections;
their own motivating numbers (~1% of clean merges incorrect, >9% failing build/test) are this
thesis's opening lines.

*"The only way this thesis becomes dangerously close is if the n=50 table and a simple-beats-complex
moral are its headline."*

**A Passau-specific corollary:** JDime is a Passau artifact and plausibly the examiners' home turf.
Report its 96% crash rate strictly scoped ("in this harness, on this corpus", citing Schesch's own
exclusion) while crediting the *idea* — **JDime's auto-tuning is the direct intellectual ancestor of
the `NONE→git` fast-path**, generalising "expensive precision only where needed" from intra-tool
switching to inter-tool dispatch. Framing the routing refutation as *measuring the limits of the
Passau principle* turns an awkward result into a contribution to their own line.

**Source.** `[chat]` — session `dc3bc182`, 2026-07-18.

<a id="d-62"></a>
## D-62 | 2026-07-18 | Lead with the census and the zero-FP record, not with routing

**Decision.** Frame the thesis around the two results that are simultaneously novel, positive and
gate-hardened — the **anatomy of silent merge failures** and the **zero-false-positive detection
record** — with routing refutation and comparator methodology as chapters beneath. Recommended title
direction: *"Where Merges Break Silently"*.

**Why.** **Never put "composition" or "routing" in the main title as a promise** — the evidence
supports them as questions, not achievements. Avoid overclaiming verbs ("solving", "preventing");
the defensible claims are measured rates. Keep "Java" or "Git" in the title (external validity is
Java-only).

**Status.** Recommendation on the table; final title is Ali's call. Supporting reframings agreed
earlier and carried forward:
- Contribution restated from *"we built detectors"* to *"the first base-rate measurement of the
  hypothesized semantic-conflict categories on a real corpus with test-suite ground truth"* — and the
  taxonomy chapter changes role from design spec to **tested hypothesis space**.
- *"The smarter your merge tool, the more you need a semantic safety net on top of it"* — the
  bare→driver delta is much larger on Mergiraf (−104) than on git (−14), because a weak backend
  already surfaces failures as textual conflicts for free.

**Source.** `[chat]` — session `dc3bc182`, 2026-07-18; earlier framings in `bfc672b4` and `8740dbd3`.

<a id="d-63"></a>
## D-63 | 2026-07-22 | Add a methodology/infrastructure chapter and an AI-contribution chapter

**Decision.** Extend the 60-page structure with two chapters at Ali's request:

- **Ch. 5 — Experimental methodology & infrastructure.** The shared discipline stated *once*:
  pre-registered gates and floors, instrument freezes at named commits, four firewalled instruments
  never blended, two-arm flag designs, control materialization, deterministic caches and shards,
  Wilson CIs, human adjudication as the final label. Plus the AWS execution environment (including
  the arm64-gjf incident presented as **a lesson turned into method**) and the adjudication
  instrumentation. Each evidence chapter then uses an identical skeleton — *Design &
  pre-registration → Materials → Execution → Results → Interpretation* — with Execution reduced to a
  pointer.
- **Ch. 9 — AI and author contributions.** Structured by the three *different scientific roles* AI
  played: (1) **engineering collaborator** (most implementation), (2) **measurement instrument** —
  in the census an LLM *is* the closed-coder, double-coded with stability gates and human
  adjudication on top, which is **method, not assistance** — and (3) writing assistant. Plus a
  **contribution-delineation table** (Artifact/Decision × author role × AI role).

**Why.** Both requests came from Ali. The AI chapter's design point: the author's column of that
table is the *scientific* side — problem formulation and RQs, every design decision and standing
rule, every gate verdict and ruling, and accountability for every claim. The chapter closes with its
strongest exhibit: **the human gate demonstrably caught AI failures** (the fabricated quote in the
census, the incidental-flag rulings, the v1 mis-scoring correction) — which converts "AI did a lot"
from a liability into evidence that the methodology was designed for exactly that risk.

**Caution recorded:** Ch. 5 stays strictly about *how* and Ch. 9 strictly about *who*; the moment
either restates results, the evidence chapters lose their claim to them. The formal AI-use
declaration in the front matter is separate and prescribed by examination regulations, not by this
design.

**Source.** `[chat]` — session `dc3bc182`, 2026-07-22.

<a id="d-64"></a>
## D-64 | 2026-07-22 | Claims ledger + LaTeX macros; write in order of frozenness

**Decision.** Three writing-phase rules:

1. **Spine first, prose later** — fix the title, RQs, contributions and a one-page bullet skeleton per
   chapter, and get supervisor sign-off on *that*. A supervisor correcting a skeleton costs an hour;
   correcting a written chapter costs a week.
2. **A claims ledger** mapping every citable number to its frozen source
   (`6.7% [3.8, 11.6] → reports_detection/full/FINDINGS.md @ 843e5f5`), with each number defined
   **once as a LaTeX macro** and never typed inline. This kills number-drift across 60 pages, makes
   the final audit mechanical, and — given the fabricated-quote lesson — is the **mechanical guard**
   when AI drafts prose from the reports.
3. **Write in order of frozenness, not chapter order**: evidence chapters → artifact/infrastructure →
   framing → polish. Interpretation can shift while framing chapters are unwritten; frozen results
   cannot.

**Why.** This thesis's results already exist as frozen, committed FINDINGS files with adjudicated
numbers, so the writing is mostly **transcription and reframing of frozen evidence, not generation** —
which inverts the usual ordering. Corollary: do not block on a pending result; the pre-registered
design makes either outcome writable.

**Status.** Not yet started as of 2026-07-25.

**Source.** `[chat]` — session `dc3bc182`, 2026-07-22.

---

## Open decisions as of 2026-07-25

| # | Question | Owner |
|---|---|---|
| [D-23](#d-23) | Default-enable the experimental detector lanes? (−205 cost vs +8.3 s/file) | Ali |
| [D-08](#d-08) | Revise `semantic_merge_driver/initial architecture.md` to the evolved, evidence-kept design | Ali |
| [D-09](#d-09) | Shared-CPG refactor (~5× latency; decides CI-viable vs interactive-viable) | — |
| [D-62](#d-62) | Final thesis title and framing | Ali |
| [D-04](#d-04) | Retroactive version-pinning of the jdime / mastery / refactoring_miner images | — |
| — | P5 (`mergiraf_plus` ORT pre-pass) — optional, the one remaining cheap positive result | Ali |
