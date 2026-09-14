# Decision Record

Design, architecture and methodology decisions for this thesis project — **v2, rebuilt
2026-07-25** from the complete distilled session corpus plus git history and the plan
documents (statuses resolved against the repo 2026-07-26), under the frozen protocol in
[`docs/decision-record/PROTOCOL.md`](decision-record/PROTOCOL.md). This file is
**generated** by `docs/decision-record/render_decisions.py` from the consolidated
entries in `docs/decision-record/entries/` — edit those and re-render; do not edit
this file by hand. For browsing, an interactive navigator over the same entries
lives at [`docs/decisions_ui.html`](decisions_ui.html) (self-contained, works
offline; regenerate with `make_decisions_ui.py`).

## How to read an entry

Each entry is `D-nnn — title`, then one metadata line, then **Decision**, **Why**,
**Status**, optional **Cross-theme**, and **Source** with verbatim evidence quotes.

- **Date** — when the position was *first* taken (a range when it was argued across
  days). **Status** is the state as of 2026-07-26: `adopted` (in force),
  `superseded` (replaced — the replacing entry is linked), `reversed` (undone, not
  replaced), `open` (live question, no ruling), `proposed` (recommended and still
  genuinely pending), `abandoned` (never enacted, no ruling anywhere). The 96
  entries that were `proposed` at consolidation were resolved against the repo
  on 2026-07-26 (PROTOCOL §8 Amendment 5, Ali's ruling); their status notes
  carry the code evidence, prefixed `S12 (2026-07-26):`. A code-confirmed
  `adopted` is a post-hoc verification against the repo, not a record-visible
  ratification — the prefix keeps that distinction.
- **Provenance** — `[chat]`: every source is a session transcript; the *Why* is
  what was argued at the time, not a later rationalisation. `[recon]`: rebuilt
  from commit messages and planning documents (2026-04-15 → 2026-05-16 has no
  transcripts); faithful to the record, but the deliberation is lost, and a plan
  proves intent, not survival. `[mixed]`: both.
- **Corroboration** — extraction ran twice, independently, over every file.
  `both`: every source decision was found by both passes. `single-pass`: none was
  (weakest evidence tier; the audit samples these preferentially). `mixed`: some
  of each.
- **Actors** — who made the call (`ali` / `claude` / `joint` / `unclear`), for the
  thesis contribution-delineation table. Ali ruled (2026-07-26, PROTOCOL §8
  Amendment 7) that the distribution stands as extracted, with this caveat
  attached wherever it is cited: extraction assigns actors from transcripts in
  which Claude does most of the *writing* even where Ali makes the *call*, and
  most `unclear` entries rest on commit messages, which rarely name a decider.
- **Source** — the union uids this entry consolidates (`a:`/`b:` = transcript
  extraction passes, `preA:`/`preB:` = reconstructed-period passes), then verbatim
  quotes with `file:line` into `docs/decision-record/distilled/`. Every quote is
  machine-verified to be an exact substring of that file starting at that line.

## Coverage — numbers, not adjectives

This rebuild exists because v1 claimed complete coverage on a measured **61.5%**
read. v1 is archived verbatim at
[`docs/historical/DECISIONS-v1.md`](historical/DECISIONS-v1.md) (Ali's ruling,
2026-07-26) — **v1 `D-nn` numbers do not map to v2 numbers.** The v2 chain is
checkable end to end; every figure below is re-derived by
`docs/decision-record/preflight.py`.

| | |
|---|---|
| Corpus | 69 distilled files: 32 session + 21 subagent transcripts (2026-05-18 → 2026-07-25), 15 plan documents + 1 commit log (pre-transcript period, 2026-04-15 → 2026-05-16) |
| Reading coverage | **69/69 files, 100.0%** of 23,934 distilled lines — structural, not asserted: each extraction request contains the whole file (PROTOCOL §8 Amendment 1), and `lines_read == lines_total` is machine-checked on every file |
| Extraction | two independent passes per file; transcript-era agreement **73.6%** of 881 distinct decisions (either pass alone captures only ~86–87% of their union); reconstructed-period agreement **80.7%** of 455 |
| Union | **1,336** source decisions, partitioned into 11 theme slices (167 dual-placed) |
| Consolidation | **469 entries**; 1310 of 1336 primary decisions cited in entries, the other 26 individually listed with reasons in `not_promoted` (per-theme JSONs); mean 2.8 primary sources per entry |
| Evidence | **999 quotes**, all machine-verified verbatim at their stated lines |
| Status | 393 adopted · 21 proposed · 44 superseded · 4 open · 0 reversed · 7 abandoned |
| Provenance | 300 `[chat]` · 133 `[recon]` · 36 `[mixed]` |
| Corroboration | 255 both · 188 mixed · **26 single-pass** (weakest tier, flagged for audit) |
| Confidence | 350 high · 118 medium · 1 low (kept and flagged, not dropped) |
| Actors | 229 claude · 90 joint · 41 ali · 109 unclear — accepted as extracted (Ali, 2026-07-26); cite only with the caveat above |
| Cross-theme reconciliation | 81 flags raised by the per-theme sessions; **78 resolved** to located entries, **3 have no counterpart entry** (searched, recorded), 0 unaccounted — full rulings in `docs/decision-record/cross_theme_resolutions.json` |

**Known limits, stated rather than smoothed:**

- The consolidation-time `proposed` residue (96 entries) was **resolved against
  the repo on 2026-07-26** (Amendment 5): 53 confirmed adopted on artifact
  evidence, 11 superseded, 7 abandoned, and **21 remain genuinely
  pending** — almost all thesis-writing decisions awaiting a draft. Per-entry
  verdicts and evidence: `docs/decision-record/proposed_resolutions.json`.
- The pre-transcript period is reconstructed: what landed is reliable, *why* is
  thin, and plan-sourced statuses are status-as-of-the-plan unless confirmed by a
  later source (PROTOCOL §8 Amendment 4).
- Two independent extraction passes disagree on roughly a quarter of what counts
  as a decision in conversational text; the union is deliberately inclusive and
  consolidation carries the corroboration tier per entry.
- The residual risk no checker covers: a quote that is verbatim and correctly
  located but attached to the wrong decision. S11 samples for exactly this,
  preferentially in `single-pass` and low-confidence entries.
- 111 titles exceed the 90-character style limit; they are rendered
  verbatim rather than rewritten, because rewriting risks semantic drift.
- Per `CLAUDE.md` and PROTOCOL §7: `ISSUES.md`, `STATUS.md`,
  `THREATS_TO_VALIDITY.md`, `docs/plans/` and the source code remain
  authoritative. This document is an index and a rationale archive — the value is
  the reasoning that exists only in chat.

---

## Index

### Scope & project architecture

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-001](#d-001) | Dataset and framework are Java-only, fixed at seven semantic-conflict categories | 2026-04-16 | adopted | `[recon]` |
| [D-002](#d-002) | Semantic verification is mandatory and applied differentially across the merge triple | 2026-04-16 | adopted | `[mixed]` |
| [D-003](#d-003) | Driver stays a Python plugin host invoking external tools by subprocess | 2026-04-16 | adopted | `[recon]` |
| [D-004](#d-004) | Ban LLM-based approaches; classic program analysis only | 2026-04-16 | adopted | `[recon]` |
| [D-005](#d-005) | Decompose work into small independently testable phases, one PR each | 2026-04-16 | adopted | `[recon]` |
| [D-006](#d-006) | Take Path A: a local Mergiraf adapter, not Schesch's upstream harness | 2026-04-21 | adopted | `[recon]` |
| [D-007](#d-007) | MVP-first: ship end-to-end dispatch with two backends before empirical validation | 2026-04-22 | adopted | `[recon]` |
| [D-008](#d-008) | Add Mergiraf as a fifth comparison tool ungated; keep RM2 out of the tools table | 2026-04-22 | adopted | `[recon]` |
| [D-009](#d-009) | Keep the refactoring-aware merging track out of scope: RefMerge, IntelliMerge, RM-ASTDiff | 2026-04-22 | adopted | `[recon]` |
| [D-010](#d-010) | Drop taint analysis from the plan until it is raised again | 2026-04-22 | adopted | `[recon]` |
| [D-011](#d-011) | Leave the merger slot empty and the dispatcher diamond undrawn until a second merger | 2026-04-22 | superseded | `[recon]` |
| [D-012](#d-012) | Redefine case-based dispatch as multi-layer, not merge-backend routing | 2026-04-22 | superseded | `[recon]` |
| [D-013](#d-013) | Pre-agree a cut list if under two weeks remain before the deadline | 2026-04-22 | open | `[recon]` |
| [D-014](#d-014) | Integrate RM 2.0 only if the Method Rename Joern strategy is built with it | 2026-04-22 | adopted | `[recon]` |
| [D-015](#d-015) | Add Weave as a sixth tool; no fork, no exclusive backend, MCP out of scope | 2026-04-25 | adopted | `[recon]` |
| [D-016](#d-016) | Define four scope tiers A–D for the RM2 cycle, lean Tier D, hard floor Tier A | 2026-05-05 | superseded | `[recon]` |
| [D-017](#d-017) | Defer the scope-tier pin until R0 and M0 recon land | 2026-05-05 | adopted | `[recon]` |
| [D-018](#d-018) | The driver is a proof-of-concept verification gate, not a smarter merger or a service | 2026-05-11 | adopted | `[mixed]` |
| [D-019](#d-019) | Keep mergiraf_plus post-processing out of scope; P5 stays optional | 2026-05-11 | adopted | `[mixed]` |
| [D-020](#d-020) | Defer the comparator closure ladder: 3a rejected on cost, 3h/3i and Tiers D–F deferred | 2026-05-14 | adopted | `[recon]` |
| [D-021](#d-021) | Driver is the primary deliverable; comparator tracks its backends and must not touch it | 2026-05-14 | adopted | `[mixed]` |
| [D-022](#d-022) | Bound the empirical claim: file-level tagging only, routing soundness and #26 as limits | 2026-05-18 | adopted | `[chat]` |
| [D-023](#d-023) | Skip the shared-CPG rework after the pilot came in far under the abort threshold | 2026-06-11 | adopted | `[chat]` |
| [D-024](#d-024) | Formally descope IntelliMerge, GumTree and SafeMerge/Z3 as evidence-based removals | 2026-06-11 | adopted | `[chat]` |
| [D-025](#d-025) | Fence each session's scope explicitly, with artifacts-only handoff between sessions | 2026-06-20 | adopted | `[chat]` |
| [D-026](#d-026) | Gate any SafeMerge/Z3 proof-of-concept behind the three higher-priority moves | 2026-06-24 | superseded | `[chat]` |
| [D-027](#d-027) | Sequence the endgame: P2 next, then P3 code, overnight compute, then P4 desk work | 2026-06-24 | adopted | `[chat]` |
| [D-028](#d-028) | Retire the SSM Dockerization and heavy oracle build | 2026-07-04 | adopted | `[chat]` |
| [D-029](#d-029) | Recode the taxonomy inductively; the four-family view is a hypothesis, not a frame | 2026-07-08 | adopted | `[chat]` |
| [D-030](#d-030) | Bound the open-source comparison to consultation; position the class as pre-compile | 2026-07-16 | adopted | `[chat]` |
| [D-031](#d-031) | Treat core/sq.md as the as-built architecture; audit from primary sources, not the README | 2026-07-18 | adopted | `[chat]` |
| [D-032](#d-032) | Green-light S-D7 and S-D8; the default-enabling decision stays with Ali | 2026-07-22 | adopted | `[chat]` |

### Merge backends & routing

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-033](#d-033) | Prefer operation-based RefMerge over graph-based IntelliMerge as the refactoring-aware backend | 2026-04-16 | superseded | `[recon]` |
| [D-034](#d-034) | Choose Mergiraf as the structural merge engine and reject JDime/Spork as the standard backend | 2026-04-16 | adopted | `[recon]` |
| [D-035](#d-035) | Introduce a MergeBackend ABC separate from MergeStrategy, with env-selected backends | 2026-04-16 | adopted | `[recon]` |
| [D-036](#d-036) | Route merges by RM-detected refactoring: refactoring-aware backend if detected, Mergiraf otherwise | 2026-04-16 | superseded | `[recon]` |
| [D-037](#d-037) | Every merge backend fails closed: subprocess failure rejects, never silently accepts | 2026-04-21 | adopted | `[recon]` |
| [D-038](#d-038) | Define seven RM2 clusters by 3-way merge difficulty, resolved by a fixed precedence order | 2026-04-22 | adopted | `[mixed]` |
| [D-039](#d-039) | Ship AutoBackend and flip the SEMANTIC_MERGE_BACKEND default from mergiraf to auto | 2026-04-22 | adopted | `[recon]` |
| [D-040](#d-040) | AutoBackend falls back to git-merge-file once on CRASH only, never on CONFLICT | 2026-04-22 | adopted | `[recon]` |
| [D-041](#d-041) | Split routing into Phase-1 mechanism (no evidence gate) and deferred Phase-2 soundness | 2026-04-22 | adopted | `[recon]` |
| [D-042](#d-042) | Ship both S2 and W5 routing elifs together; the Tier-D pick rule is moot | 2026-04-22 | adopted | `[recon]` |
| [D-043](#d-043) | Accept Mergiraf as default backend before empirical validation, with git one env-flip away | 2026-04-22 | adopted | `[recon]` |
| [D-044](#d-044) | Invoke Mergiraf via a temp git repo and merge driver, mirroring upstream | 2026-04-22 | superseded | `[recon]` |
| [D-045](#d-045) | Do not integrate RefMerge until three empirical conditions hold | 2026-04-22 | adopted | `[recon]` |
| [D-046](#d-046) | Use RM output for cost-aware strategy dispatch and refactoring-density tiering | 2026-04-22 | abandoned | `[recon]` |
| [D-047](#d-047) | Reframe R4 from a binary gate to a cluster-and-language classifier feeding 4-way dispatch | 2026-04-25 | adopted | `[recon]` |
| [D-048](#d-048) | Split R4 into R4a classifier and R4b default flip to break the circular dispatch dependency | 2026-04-25 | superseded | `[recon]` |
| [D-049](#d-049) | Adopt the 4-backend cluster-keyed dispatch map in AutoBackend._route() | 2026-04-25 | superseded | `[recon]` |
| [D-050](#d-050) | Keep Spork Java-only and non-default; the Spoon constraint is the dispatch signal | 2026-04-25 | adopted | `[recon]` |
| [D-051](#d-051) | Accept missed Spork dispatches from extension-only language detection | 2026-04-25 | adopted | `[recon]` |
| [D-052](#d-052) | Register SporkBackend in the BACKENDS dict, pin spork:0.5.0, drop conflict-count gating | 2026-04-25 | adopted | `[recon]` |
| [D-053](#d-053) | Invoke weave-driver with the `-o` flagged form and key CONFLICT off exit code 1 | 2026-04-25 | adopted | `[recon]` |
| [D-054](#d-054) | Plan the Weave comparator adapter as a native (non-Docker) tool mirroring git_merge_file.py | 2026-04-25 | superseded | `[recon]` |
| [D-055](#d-055) | W5 depends on RM2 phase R4a, not R1, and rolls back by env-flag flip | 2026-04-25 | adopted | `[recon]` |
| [D-056](#d-056) | MVP-first reframe: R4b ships the dispatch skeleton, evidence gates move to per-cluster elifs | 2026-05-05 | adopted | `[recon]` |
| [D-057](#d-057) | Ship only one routing elif per cycle, chosen by an S2-vs-W5 pick rule | 2026-05-05 | superseded | `[recon]` |
| [D-058](#d-058) | Tier A ships Mergiraf-as-default as an explicitly unvalidated hypothesis | 2026-05-05 | adopted | `[recon]` |
| [D-059](#d-059) | RM2 wrapper contract: empty array is no-signal, exit 1 is a crash consumed fail-closed as NONE | 2026-05-05 | adopted | `[recon]` |
| [D-060](#d-060) | Accept file-level RM2 tagging at runtime, losing cross-file Extract/Move refactorings | 2026-05-05 | adopted | `[recon]` |
| [D-061](#d-061) | Use Mergiraf's standalone three-file CLI in Docker; temp-git-repo plumbing declared obsolete | 2026-05-12 | adopted | `[recon]` |
| [D-062](#d-062) | Ship backends-only for the 2026-05-18 cycle: four selectable backends, no routing elif | 2026-05-18 | superseded | `[recon]` |
| [D-063](#d-063) | R2 per-cluster contrasts inform but do not justify the S2/W5 routing elifs | 2026-05-18 | adopted | `[chat]` |
| [D-064](#d-064) | Reframe the INTRA_BODY+Java condition as a defensive language guard, not a second dispatch axis | 2026-05-19 | adopted | `[recon]` |
| [D-065](#d-065) | Routing is whole-file and presence-only by construction, documented as a design limitation | 2026-05-20 | adopted | `[chat]` |
| [D-066](#d-066) | Add mergiraf and weave comparator adapters, keeping jdime and mastery as baselines | 2026-05-20 | adopted | `[chat]` |
| [D-067](#d-067) | Withdraw the Weave field-loss severity alarm after corpus measurement | 2026-05-25 | adopted | `[chat]` |
| [D-068](#d-068) | File ISSUES #27: INTRA_BODY→Spork routing is contraindicated by the corpus | 2026-05-25 | superseded | `[chat]` |
| [D-069](#d-069) | Keep the S2 Spork arm live in code while the DROP flip stays deferred | 2026-05-27 | superseded | `[chat]` |
| [D-070](#d-070) | Run driver-auto on the committed pre-flip router and capture the routed backend per merge | 2026-06-24 | adopted | `[chat]` |
| [D-071](#d-071) | Propose flipping auto_backend._route to NONE→git, everything else→Mergiraf | 2026-06-24 | superseded | `[chat]` |
| [D-072](#d-072) | Land the route flip as an opt-in env flag rather than deleting the specialist arms | 2026-07-02 | adopted | `[chat]` |
| [D-073](#d-073) | RefMerge/RefactoringMiner-3.0 architecture direction confirmed reverted; gate never met | 2026-07-18 | adopted | `[chat]` |
| [D-074](#d-074) | Drop the INTRA_BODY→Spork routing arm on five independent angles of refutation | 2026-07-18 | adopted | `[chat]` |
| [D-075](#d-075) | Drop the MIGRATE_DECL→Weave routing arm after the W3 gate run | 2026-07-18 | adopted | `[chat]` |
| [D-076](#d-076) | Collapse the auto router to NONE→git, else→Mergiraf; routing benefit is the fast-path only | 2026-07-18 | adopted | `[chat]` |
| [D-077](#d-077) | Default-enable ruling for the experimental detector lanes remains open with the user | 2026-07-23 | open | `[chat]` |

### Detection layer

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-078](#d-078) | Strategies fail closed on internal errors instead of returning is_clean=True | 2026-04-16 | adopted | `[mixed]` |
| [D-079](#d-079) | Three-way refactoring information is built from pairwise RM2 calls against base, per branch | 2026-04-16 | adopted | `[mixed]` |
| [D-080](#d-080) | Adopt RM-ASTDiff (RefactoringMiner 3.0) instead of GumTree plus RefactoringMiner 2.0 | 2026-04-16 | superseded | `[recon]` |
| [D-081](#d-081) | The driver rejects a merge only on CRITICAL issues; WARNING does not block | 2026-04-16 | abandoned | `[recon]` |
| [D-082](#d-082) | Atomic-update invariants get a hybrid RM-ASTDiff plus Joern structural strategy | 2026-04-16 | abandoned | `[recon]` |
| [D-083](#d-083) | Detect rename conflicts from RM refactoring metadata, scoped to within-file stale callers | 2026-04-16 | adopted | `[mixed]` |
| [D-084](#d-084) | Classifier and tagger fail closed to Cluster.NONE; empty RM2 output is a normal result | 2026-04-22 | adopted | `[mixed]` |
| [D-085](#d-085) | Use RefactoringMiner 2.x pinned at 2.4.0, with RM 3.x out of thesis scope | 2026-04-22 | adopted | `[mixed]` |
| [D-086](#d-086) | Strategy enablement comes from a YAML config file, not environment variables | 2026-04-22 | adopted | `[recon]` |
| [D-087](#d-087) | Consume only structured RM2 JSON fields; never parse descriptions or assume location[0] | 2026-04-22 | adopted | `[recon]` |
| [D-088](#d-088) | Ship D1 as a pure-textual differential lane, extension-scoped and behind an experimental flag | 2026-04-25 | adopted | `[mixed]` |
| [D-089](#d-089) | Select Path D dual-mode tagging and accept file-level blindness to cross-file refactorings | 2026-05-05 | adopted | `[recon]` |
| [D-090](#d-090) | R0 declares the -bc equivalence question moot and defers coverage validation to R1 | 2026-05-05 | adopted | `[recon]` |
| [D-091](#d-091) | Any future port of the cluster taxonomy to RM 3.x needs an explicit label migration table | 2026-05-06 | proposed | `[recon]` |
| [D-092](#d-092) | Adopt a seven-cluster taxonomy keyed on kind of three-way merge difficulty | 2026-05-13 | adopted | `[recon]` |
| [D-093](#d-093) | Ship regex call-site detection for the rename lane with Joern as the documented escape hatch | 2026-05-14 | adopted | `[recon]` |
| [D-094](#d-094) | Correct the Rename Class codeElement shape and pin it with a probe test | 2026-05-14 | adopted | `[recon]` |
| [D-095](#d-095) | Keep a parity-tested copy of the runtime taxonomy so empirical clusters equal runtime clusters | 2026-05-18 | adopted | `[chat]` |
| [D-096](#d-096) | Stage B widens coverage before fixing false positives, and widens nothing for DFI or loop bounds | 2026-06-11 | adopted | `[chat]` |
| [D-097](#d-097) | Add JoernUnresolvedReference as a differential-only detector that abstains without parents | 2026-06-11 | adopted | `[chat]` |
| [D-098](#d-098) | Make JoernUnresolvedReference the primary detector and reorganise strategies into yield tiers | 2026-06-11 | proposed | `[chat]` |
| [D-099](#d-099) | Harden the unresolved-identifier lane against parser artifacts by keying on name only | 2026-06-11 | superseded | `[chat]` |
| [D-100](#d-100) | Drop the type-resolution lane; import-deletion breakage is out of v2 scope | 2026-06-11 | adopted | `[chat]` |
| [D-101](#d-101) | Proposed upgrade ladder: tree-sitter-java tactically, differential ecj strategically | 2026-06-11 | superseded | `[chat]` |
| [D-102](#d-102) | Fix the two var-lane FP defects and re-run, with tests proven discriminating, across two rounds | 2026-06-20 | adopted | `[chat]` |
| [D-103](#d-103) | Upgrade the stale-read detector to a Joern DDG query and bring loop bounds to v2 parity | 2026-06-24 | superseded | `[chat]` |
| [D-104](#d-104) | Withdraw the 66.7% file-level recall figure; n=50 measures 90.7% and the design stands | 2026-07-03 | adopted | `[chat]` |
| [D-105](#d-105) | Scope the detector cycle to two new lanes plus one widening, targeting the census mass | 2026-07-15 | adopted | `[chat]` |
| [D-106](#d-106) | No LLM-backed detector lane; detectors are deterministic static analysis with a zero-FP bar | 2026-07-15 | adopted | `[chat]` |
| [D-107](#d-107) | One narrow carve-out: a Batch API pass for fixture and spec extraction on derivation data | 2026-07-15 | adopted | `[chat]` |
| [D-108](#d-108) | Restrict D2 to the same-file arity-change shape and document the rest as false negatives | 2026-07-16 | adopted | `[chat]` |
| [D-109](#d-109) | Declare cross-file shapes out of file-local reach and record them as the FN ceiling | 2026-07-16 | adopted | `[chat]` |
| [D-110](#d-110) | Widen JoernUnresolvedReference with a flag-gated textual differential, fixed at the shared root | 2026-07-16 | adopted | `[chat]` |
| [D-111](#d-111) | Let flag-ON widened issues ride along after the fail-closed inconclusive Issue | 2026-07-16 | adopted | `[chat]` |
| [D-112](#d-112) | Correct the gap inventory: the baseline lane already fires on the bare-receiver shapes | 2026-07-16 | adopted | `[chat]` |
| [D-113](#d-113) | Review sub-agents refute the widened lane's documented safety claims and propose shared fixes | 2026-07-16 | adopted | `[chat]` |
| [D-114](#d-114) | Detector review briefs rank false-positive slips worst and require execution-reproduced findings | 2026-07-16 | adopted | `[chat]` |
| [D-115](#d-115) | Under incomplete information the lanes suppress rather than accept precision loss | 2026-07-16 | adopted | `[chat]` |
| [D-116](#d-116) | Calibrate D1's suppression toward false negatives, but reject blanket extends-suppression | 2026-07-16 | adopted | `[chat]` |
| [D-117](#d-117) | Keep the absorption guard and document the textual tier's inherent false negatives | 2026-07-16 | adopted | `[chat]` |
| [D-118](#d-118) | Reject Joern, type inference, compile oracles and the heavy parsers for the import lane | 2026-07-16 | adopted | `[chat]` |
| [D-119](#d-119) | Three proposed fixes for the remaining verified D1 guard defects | 2026-07-16 | proposed | `[chat]` |
| [D-120](#d-120) | Defer tree-sitter token classification to keep the import lane dependency-free | 2026-07-16 | adopted | `[chat]` |
| [D-121](#d-121) | Accept the lanes' known inefficiencies and one warty misdetection at experimental scale | 2026-07-16 | adopted | `[chat]` |
| [D-122](#d-122) | Proposed but unratified optimisations to the widened and D2 textual scans | 2026-07-16 | adopted | `[chat]` |
| [D-123](#d-123) | Reuse sibling lanes by composition and module import, with zero edits to frozen lane files | 2026-07-16 | adopted | `[chat]` |
| [D-124](#d-124) | Fix D2's arity projection and generic-span rule; affirm the rest of its guard set | 2026-07-16 | adopted | `[chat]` |
| [D-125](#d-125) | Proposed structural cleanups against silent drift in the lanes and the tune harness | 2026-07-16 | adopted | `[chat]` |
| [D-126](#d-126) | The tune harness duplicates the lane registry and forces the experimental flag ON | 2026-07-16 | adopted | `[chat]` |
| [D-127](#d-127) | Record the legacy Joern detectors as heuristics that fire nothing in the wild | 2026-07-18 | adopted | `[chat]` |
| [D-128](#d-128) | The new detector lanes ship flag-gated; default-enabling is deferred to Ali after S-D8 | 2026-07-22 | adopted | `[chat]` |

### Evaluation methodology & oracles

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-129](#d-129) | Required report contents — metric set, latency, CIs, per-scenario pivot — stated but not confirmed shipped | 2026-04-16 | adopted | `[mixed]` |
| [D-130](#d-130) | Headline numbers carry Wilson 95% CIs and tool-superiority claims require non-overlapping CIs | 2026-04-21 | adopted | `[mixed]` |
| [D-131](#d-131) | Add a multi-criteria FP matrix and a separate granularity-axis pivot to the report | 2026-04-21 | abandoned | `[recon]` |
| [D-132](#d-132) | Adopt google-java-format roundtrip (3e) as the primary comparator fix, implemented as a cached two-tier match | 2026-04-22 | adopted | `[recon]` |
| [D-133](#d-133) | Pivot per-cluster evidence on ours∪theirs, rejecting the resolution axis as circular | 2026-04-22 | adopted | `[mixed]` |
| [D-134](#d-134) | Accept that NONE absorbs RM2 recall failures and measure the gap with a dual-mode F-harness | 2026-04-22 | adopted | `[recon]` |
| [D-135](#d-135) | Benchmark RM2 on isolated scenario files, but skip replicating its published oracle numbers | 2026-04-22 | adopted | `[recon]` |
| [D-136](#d-136) | Cite upstream's published Mergiraf numbers as free credibility and check its test-suite ground truth | 2026-04-22 | proposed | `[recon]` |
| [D-137](#d-137) | Detect Mergiraf's fallback-to-markers by counting conflict markers as spork.py does | 2026-04-22 | adopted | `[recon]` |
| [D-138](#d-138) | Ground truth follows a γ→3e→3j→3b ladder; test-suite ground truth demoted to maximalist fallback | 2026-04-30 | adopted | `[recon]` |
| [D-139](#d-139) | Record the exact command per version-comparison finding and recover old numbers from git history | 2026-05-06 | adopted | `[recon]` |
| [D-140](#d-140) | Bucket every false positive by the cheapest normalization that makes it match, per tool | 2026-05-14 | adopted | `[recon]` |
| [D-141](#d-141) | Downgrade "all structural FPs are AST-equivalent reformatting" to a 3-of-39 hypothesis | 2026-05-14 | adopted | `[recon]` |
| [D-142](#d-142) | gjf recovered 1 of 42 FPs: prediction withdrawn, Spork's FP rate reframed as a comparator gap | 2026-05-14 | adopted | `[recon]` |
| [D-143](#d-143) | Mastery's FPs are intrinsic content loss, later refined to 10 comment-only and 34 genuine | 2026-05-14 | adopted | `[recon]` |
| [D-144](#d-144) | Rule out token-level comparison (3d); AST normalize (3b) is the next defensible step | 2026-05-14 | superseded | `[recon]` |
| [D-145](#d-145) | Scope 3b to Tier C's five tree-sitter transforms, deferred out of M3.5 to a follow-up phase | 2026-05-14 | adopted | `[recon]` |
| [D-146](#d-146) | Tier 3 is strictly additive with parse-fail fall-through and one whole-tier kill switch | 2026-05-14 | adopted | `[recon]` |
| [D-147](#d-147) | Use tree-sitter-java for AST canonicalisation; reject javalang, JavaParser, Spoon and gjf internals | 2026-05-14 | adopted | `[recon]` |
| [D-148](#d-148) | Tier C guards else-if flattening and paren stripping ultra-conservatively | 2026-05-14 | superseded | `[recon]` |
| [D-149](#d-149) | Strip java.lang FQNs only for a hardcoded allowlist of common names | 2026-05-14 | adopted | `[recon]` |
| [D-150](#d-150) | Treat all comments as semantically irrelevant, with a threats-to-validity entry instead of a warning | 2026-05-14 | adopted | `[mixed]` |
| [D-151](#d-151) | Withdraw the ~90% Tier C recovery estimate but keep the tier landed and the AST-equivalence finding | 2026-05-14 | adopted | `[recon]` |
| [D-152](#d-152) | Measure recovery with an in-memory prototype and attribute it only cumulatively | 2026-05-14 | adopted | `[recon]` |
| [D-153](#d-153) | Defer both Tier D and 3a after Tier C and publish the post-Tier-C numbers as interim | 2026-05-14 | superseded | `[recon]` |
| [D-154](#d-154) | Pin the RM2 output-shape contract with an image-gated shape-probe test | 2026-05-14 | adopted | `[recon]` |
| [D-155](#d-155) | Expand Tier D to six transforms absorbing Tier E's paren strip and token fold, and ship them | 2026-05-15 | adopted | `[recon]` |
| [D-156](#d-156) | Tier D paren-stripping is fenced by syntactic, postfix, safe-parent and precedence guards | 2026-05-15 | adopted | `[recon]` |
| [D-157](#d-157) | Delete Tier C's paren rule once D.2 subsumes it, but keep flatten_else_if | 2026-05-15 | superseded | `[recon]` |
| [D-158](#d-158) | Defer long-array, hex and typed paren work to Tier E/F and bound the comparator-side ceiling | 2026-05-15 | adopted | `[recon]` |
| [D-159](#d-159) | Fix D.1's node-identity bug, replace the non-discriminating test, and set Tier E scope from measured residuals | 2026-05-16 | adopted | `[recon]` |
| [D-160](#d-160) | Tier E's eleven transforms are narrowly guarded, with normalization losses admitted as corpus-contingent | 2026-05-16 | adopted | `[recon]` |
| [D-161](#d-161) | ISSUES #23/#3 corrected: the fix is a metrics.py concat guard, report.py is untouched | 2026-05-18 | adopted | `[mixed]` |
| [D-162](#d-162) | Turn the per-cluster-rows-partition-the-all-row property into a regression test | 2026-05-18 | adopted | `[chat]` |
| [D-163](#d-163) | Record R2's per-cluster result as weak-yes, not statistically defensible | 2026-05-18 | adopted | `[recon]` |
| [D-164](#d-164) | Verify a methodological claim against code, corpus or the primary text before recording it | 2026-05-20 | adopted | `[chat]` |
| [D-165](#d-165) | The four-tier canonical oracle is an evaluation-only scoring device applied uniformly to all tools | 2026-05-26 | adopted | `[chat]` |
| [D-166](#d-166) | Cross-tab comparator FPs against Schesch test labels and treat the test label as the truer oracle | 2026-05-26 | adopted | `[chat]` |
| [D-167](#d-167) | Reuse the driver-faithful harness and key every cache on the driver commit | 2026-06-11 | adopted | `[chat]` |
| [D-168](#d-168) | Report fail-closed blocks and defect-shaped control blocks in separate decomposition rows | 2026-06-11 | adopted | `[chat]` |
| [D-169](#d-169) | Whole-merge test labels are a noisy per-file oracle; judge recall against attributable mass | 2026-06-11 | adopted | `[chat]` |
| [D-170](#d-170) | Scope P2 as one cost-model table over five configs, reusing Stage C as the driver-mergiraf arm | 2026-06-18 | adopted | `[chat]` |
| [D-171](#d-171) | Score P2 with a hybrid oracle: test label where output matches Mergiraf, dev-match otherwise | 2026-06-24 | adopted | `[chat]` |
| [D-172](#d-172) | An arm64 gjf image had silently disabled normalization: re-score everything in the repaired environment | 2026-06-24 | adopted | `[chat]` |
| [D-173](#d-173) | Derive the post-flip driver-auto table from existing per-file data rather than re-running 12 h | 2026-07-02 | superseded | `[chat]` |
| [D-174](#d-174) | Declare the AWS run the canonical scoring environment and never mix environments in a table | 2026-07-02 | superseded | `[chat]` |
| [D-175](#d-175) | Revise file-level RM2 recall from 66.7% at n=10 to 90.7% at n=50 | 2026-07-03 | adopted | `[chat]` |
| [D-176](#d-176) | Adopt spgroup/mergedataset as the external oracle, scored on the developer's shipped merge | 2026-07-04 | adopted | `[chat]` |
| [D-177](#d-177) | Retire the defect-dependent tcurdt flag, revising the headline R2 from 7.3% to 6.7% | 2026-07-06 | superseded | `[chat]` |
| [D-178](#d-178) | Read only cost-model deltas, never the raw per-config column | 2026-07-06 | adopted | `[chat]` |
| [D-179](#d-179) | Always present base rates per corpus with the selection predicate attached | 2026-07-08 | adopted | `[chat]` |
| [D-180](#d-180) | Three-phase inductive coding with a javac compile delta, truncation ladder and parent-side rule | 2026-07-08 | adopted | `[chat]` |
| [D-181](#d-181) | Escape hatches are first-class outputs and the escape mass is a reported stratum | 2026-07-08 | adopted | `[chat]` |
| [D-182](#d-182) | Clarify only the escape-hatch boundary, and not via the merged-vs-developer diff | 2026-07-11 | adopted | `[chat]` |
| [D-183](#d-183) | Scope S4 as the full 308-merge double closed-coding census under the frozen codebook | 2026-07-11 | adopted | `[chat]` |
| [D-184](#d-184) | S-D5 runs a baseline arm in a new two-arm harness that refuses no-op runs | 2026-07-15 | adopted | `[chat]` |
| [D-185](#d-185) | Add a machine quote-provenance precheck to future closed-coding instruments | 2026-07-15 | adopted | `[chat]` |
| [D-186](#d-186) | Build quote grading into the spec batch tooling as a machine precheck | 2026-07-15 | adopted | `[chat]` |
| [D-187](#d-187) | Cite Error Prone's default-on ERROR criteria as precedent for the lane's zero-FP bar | 2026-07-16 | adopted | `[chat]` |
| [D-188](#d-188) | Classify the verdict_of "inconclusive" substring collision as harness-only, not blocking | 2026-07-16 | adopted | `[chat]` |
| [D-189](#d-189) | Pivot the comparison from four academic tools to six centred on the driver's own backends | 2026-07-18 | adopted | `[chat]` |
| [D-190](#d-190) | Keep the four detection instruments firewalled and never blend their numbers | 2026-07-18 | adopted | `[chat]` |
| [D-191](#d-191) | A flag is a detector FP only if its claim about the scored artifact is false | 2026-07-22 | adopted | `[chat]` |

### Corpora & sampling

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-192](#d-192) | Require a positive and a negative scenario per conflict category in tests/data | 2026-04-16 | abandoned | `[recon]` |
| [D-193](#d-193) | Schesch's AST-Merging-Evaluation is the pipeline corpus; ConflictBench/ConGra/RefMerge rejected | 2026-04-22 | adopted | `[mixed]` |
| [D-194](#d-194) | Tag scenarios with RM2 file-level on ours/theirs only, ungated; resolution axis and project-level deferred | 2026-04-22 | adopted | `[mixed]` |
| [D-195](#d-195) | Let an R0 recall-delta harness decide file-level vs project-level RM2 tagging | 2026-04-22 | superseded | `[recon]` |
| [D-196](#d-196) | Select FP inspection samples by size stratification plus programmatic bucketing, not arbitrarily | 2026-04-22 | adopted | `[recon]` |
| [D-197](#d-197) | Skip scenarios with more than one merge-base, and describe the mechanism correctly | 2026-05-20 | adopted | `[chat]` |
| [D-198](#d-198) | Do not replicate git ort's virtual-base synthesis; exclude and note instead | 2026-05-20 | adopted | `[chat]` |
| [D-199](#d-199) | Expand the corpus by targeted, diversity-capped selection on Schesch outcome columns, not first-N | 2026-05-20 | adopted | `[chat]` |
| [D-200](#d-200) | Report the discriminating corpus's rates as upper bounds and set-up comparisons, not absolute rates | 2026-05-25 | adopted | `[chat]` |
| [D-201](#d-201) | Build the Spork pool from cheap outcome-based criteria, not the cluster-targeted option | 2026-05-26 | adopted | `[chat]` |
| [D-202](#d-202) | Materialize every intersecting Java file per merge, keyed so units cannot collapse | 2026-06-11 | adopted | `[chat]` |
| [D-203](#d-203) | Count materialization losses as census attrition, after recovering unreachable parents by SHA | 2026-06-11 | adopted | `[chat]` |
| [D-204](#d-204) | Scope any taxonomy refresh at scale as a stratified ~150–200 sample, not a full census | 2026-07-06 | superseded | `[chat]` |
| [D-205](#d-205) | Taxonomy population is the full 308-merge semantic census, stratified by intersecting files ≤3/>3 | 2026-07-08 | adopted | `[chat]` |
| [D-206](#d-206) | Commit a seeded 60/40 derivation/held-out split before any labeling, firewalling held-out | 2026-07-08 | adopted | `[chat]` |
| [D-207](#d-207) | Carry the escape-hatch mass forward as a 'not-cleanly-merge-attributable' stratum | 2026-07-10 | adopted | `[chat]` |
| [D-208](#d-208) | Held-out units are labeled in Phase 3, but their contents never appear in prose | 2026-07-11 | adopted | `[chat]` |
| [D-209](#d-209) | Constrain, seed and firewall the fresh Tests_passed control draws | 2026-07-15 | adopted | `[chat]` |
| [D-210](#d-210) | Document the pre-existing eval-content overlap rather than redraw the committed control lists | 2026-07-16 | adopted | `[chat]` |
| [D-211](#d-211) | State the single-labeled-corpus limitation: recall and cost numbers rest on Schesch alone | 2026-07-24 | adopted | `[chat]` |

### Adjudication & human oversight

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-212](#d-212) | Re-test the AST-equivalence hypothesis by hand on a 15-sample stratified eyeball | 2026-05-14 | adopted | `[recon]` |
| [D-213](#d-213) | Final adjudication rulings are Ali's; Claude may only draft and must not auto-label | 2026-06-11 | adopted | `[chat]` |
| [D-214](#d-214) | Every adjudication round gets a self-contained browser review UI in the house pattern | 2026-06-11 | adopted | `[chat]` |
| [D-215](#d-215) | Ali ruled every adjudication round and accepted the drafts unchanged | 2026-06-11 | adopted | `[chat]` |
| [D-216](#d-216) | Pilot hits labelled DETECTOR-FP; the blockchain compile-error claim withdrawn | 2026-06-11 | adopted | `[chat]` |
| [D-217](#d-217) | Adjudication UIs are browser-verified and handed over in a fresh unlabelled state | 2026-06-20 | adopted | `[chat]` |
| [D-218](#d-218) | UI shows detector output verbatim but re-locates identifiers in the merged file | 2026-06-20 | adopted | `[chat]` |
| [D-219](#d-219) | Applying rulings is a mechanical edit that must survive regeneration | 2026-07-05 | adopted | `[chat]` |
| [D-220](#d-220) | Overnight LLM labels are a pre-registered drafting instrument, never an autonomous oracle | 2026-07-08 | adopted | `[chat]` |
| [D-221](#d-221) | The codebook freezes only on Ali's explicit APPROVE, recorded in the ruling artifact | 2026-07-08 | adopted | `[chat]` |
| [D-222](#d-222) | Spot-check UI grades whether each evidence quote is really in the model input | 2026-07-09 | adopted | `[chat]` |
| [D-223](#d-223) | Ali may state rulings in plain text instead of using the review UI | 2026-07-10 | adopted | `[chat]` |
| [D-224](#d-224) | Withhold per-unit guidance during the reliability adjudication, explaining layout only | 2026-07-11 | superseded | `[chat]` |
| [D-225](#d-225) | Adjudicate the primary label only; report unruled disagreements as holes | 2026-07-11 | adopted | `[chat]` |
| [D-226](#d-226) | Escape hatches need an ours×theirs interaction; a visible mechanism beats an escape | 2026-07-13 | adopted | `[chat]` |
| [D-227](#d-227) | Three category-boundary conventions fixed during the census adjudication | 2026-07-14 | adopted | `[chat]` |
| [D-228](#d-228) | merged == developer proves nothing; verify the merged code itself | 2026-07-14 | adopted | `[chat]` |
| [D-229](#d-229) | Ali's draft rulings are audited programmatically, review-only, before being applied | 2026-07-14 | adopted | `[chat]` |
| [D-230](#d-230) | Reject a pass's ruling whose decisive evidence quote is fabricated | 2026-07-14 | adopted | `[chat]` |
| [D-231](#d-231) | Escalate to Ali rather than improvise: control flags, gate flags and plan ambiguity | 2026-07-15 | adopted | `[chat]` |
| [D-232](#d-232) | Every held-out ruling carries a written rationale; the convention is fixed in card 1 | 2026-07-19 | adopted | `[chat]` |
| [D-233](#d-233) | GD3 control flags are ruled from their package, outside the held-out UI and convention | 2026-07-20 | adopted | `[chat]` |
| [D-234](#d-234) | Three held-out drafts corrected: two DETECTOR-FPs and one sub-flag fix | 2026-07-20 | adopted | `[chat]` |
| [D-235](#d-235) | Both control-flag pairs ruled INCIDENTAL-BUT-TRUE: gates re-judged PASS, no rerun | 2026-07-22 | adopted | `[chat]` |
| [D-236](#d-236) | Document the adjudication instrumentation and frozen-evidence ruling protocol in Ch. 5 | 2026-07-22 | proposed | `[chat]` |
| [D-237](#d-237) | Rule the last open Phase-2b mapping late, disclosing the lateness as a threat | 2026-07-23 | adopted | `[chat]` |

### Gates, freezes & pre-registration

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-238](#d-238) | Mergiraf may fill the structured-merge slot only on Phase 4 evidence: F1 ≥ git merge-file, zero crashes | 2026-04-21 | abandoned | `[recon]` |
| [D-239](#d-239) | Pin the formatter version used by the comparator's Docker layer | 2026-04-21 | adopted | `[recon]` |
| [D-240](#d-240) | Both integration plans gain a significance gate on F1 criteria and a 2× timebox escape rule | 2026-04-22 | adopted | `[recon]` |
| [D-241](#d-241) | Each execution stage is one commit, gated on the previous, with a mandatory stop and a replan gate at ε | 2026-04-22 | adopted | `[recon]` |
| [D-242](#d-242) | R2's per-cluster answer is publishable either way and does not gate the dispatch mechanism | 2026-04-22 | adopted | `[mixed]` |
| [D-243](#d-243) | Evidence-before-integration binds per-cluster routing claims, not the dispatch mechanism or the default | 2026-04-22 | adopted | `[recon]` |
| [D-244](#d-244) | W5 promotion originally gated on five conditions including a MIGRATE_DECL-specific W3 win | 2026-04-25 | superseded | `[recon]` |
| [D-245](#d-245) | Routing elifs ship as Phase-1 mechanism; the S3/W3 evidence gates become Phase-2 validation | 2026-04-25 | adopted | `[recon]` |
| [D-246](#d-246) | S3 and W3 are hard-gated on ISSUES #2, with the failure branch pre-registered | 2026-04-25 | adopted | `[recon]` |
| [D-247](#d-247) | Pre-register the comparator's recovery floor from Wilson bounds, with per-phase floors and an escalation rule | 2026-05-14 | adopted | `[mixed]` |
| [D-248](#d-248) | Every comparator tier carries an undershoot pause trigger and a 2× timebox escape budget | 2026-05-14 | adopted | `[recon]` |
| [D-249](#d-249) | Honour the pre-registered pause trigger: finish 3b.5 in stop-and-document mode | 2026-05-14 | adopted | `[recon]` |
| [D-250](#d-250) | ISSUES #2 is held at `decided` every time a tier misses the pre-registered floor | 2026-05-14 | superseded | `[recon]` |
| [D-251](#d-251) | Phase 3d.3 is allowed a zero per-phase recovery floor because it only pays off paired with D.2 | 2026-05-15 | adopted | `[recon]` |
| [D-252](#d-252) | Tiers D and E are judged against their own lower floors, not the original X ≥ 30 | 2026-05-15 | adopted | `[recon]` |
| [D-253](#d-253) | Tier E hits the floor exactly: ISSUES #2 resolved and post-3e results.csv frozen as the final state | 2026-05-16 | adopted | `[recon]` |
| [D-254](#d-254) | Paren-strip rules carry a safe-parents whitelist whose semantics later tiers may widen but not change | 2026-05-16 | adopted | `[recon]` |
| [D-255](#d-255) | categorizer.cluster_of is parity-locked to the runtime classifier, with a test that fails on drift | 2026-05-18 | adopted | `[chat]` |
| [D-256](#d-256) | Record the freeze commit before the run, then do not patch the instrument during it | 2026-06-11 | adopted | `[chat]` |
| [D-257](#d-257) | Stage B is the one sanctioned exception to the no-driver-changes rule, timeboxed 3–5 days | 2026-06-11 | adopted | `[chat]` |
| [D-258](#d-258) | Whether to run the separately labeled post-fix detector run is left as Ali's call | 2026-06-12 | superseded | `[chat]` |
| [D-259](#d-259) | Every number is labelled by what it can support: validation-only, tuning-tainted, coarse-n, or corrected | 2026-06-24 | adopted | `[chat]` |
| [D-260](#d-260) | Close #29 with a three-run audit trail, the frozen run as the citable primary | 2026-07-02 | adopted | `[chat]` |
| [D-261](#d-261) | No run counts until the environment reproduces known answers exactly | 2026-07-03 | adopted | `[chat]` |
| [D-262](#d-262) | Numbers from separate labeled evaluations are never blended | 2026-07-03 | adopted | `[chat]` |
| [D-263](#d-263) | Phase-2b is gated on recon where a documented dead-end is an acceptable outcome | 2026-07-03 | adopted | `[chat]` |
| [D-264](#d-264) | Gates are enforced by machine checks that abort, not by reading the output | 2026-07-04 | adopted | `[chat]` |
| [D-265](#d-265) | Instrument wording and predictions are committed before the data they will be applied to exists | 2026-07-04 | adopted | `[chat]` |
| [D-266](#d-266) | The split and control draws are committed before any content-bearing work, and held-out content never touches the instrument | 2026-07-08 | adopted | `[chat]` |
| [D-267](#d-267) | Pre-register the whole taxonomy protocol, with numeric gate criteria, in Session 0 | 2026-07-08 | adopted | `[chat]` |
| [D-268](#d-268) | Frozen authority documents: harness adapts, and changes only via dated §12 amendments | 2026-07-08 | adopted | `[chat]` |
| [D-269](#d-269) | Workload models, prompts and request parameters are pinned in the manifest; session models are not | 2026-07-08 | adopted | `[chat]` |
| [D-270](#d-270) | The G0 pilot exercises production plumbing but its outputs are discarded and its units relabelled | 2026-07-08 | adopted | `[chat]` |
| [D-271](#d-271) | One G2 freeze commit locks the codebook and the Phase-3 category enum together | 2026-07-08 | adopted | `[chat]` |
| [D-272](#d-272) | Yellow-band stability buys exactly one clarification amendment and a full controlled rerun | 2026-07-08 | adopted | `[chat]` |
| [D-273](#d-273) | A gate is scored against its written criterion, and the re-scoring ruling goes into the record | 2026-07-10 | adopted | `[chat]` |
| [D-274](#d-274) | One frozen authority doc per program, artifact-only handoff, pre-written prompts with STOP points | 2026-07-15 | adopted | `[chat]` |
| [D-275](#d-275) | GD3 requires literally zero control flags, and any flag stops the session for Ali | 2026-07-15 | adopted | `[chat]` |
| [D-276](#d-276) | The optional S-D7/S-D8 stages are decided at S-D6 close-out, not pre-committed | 2026-07-15 | adopted | `[chat]` |
| [D-277](#d-277) | Hard-stop S-D5 at the ambiguity gate when the brief's state contradicts the repo | 2026-07-16 | adopted | `[chat]` |
| [D-278](#d-278) | Lane widening must not change any verdict the lanes already produce | 2026-07-16 | adopted | `[chat]` |
| [D-279](#d-279) | Amendment 3: three-angle review of each detector before its gate may close | 2026-07-16 | adopted | `[chat]` |
| [D-280](#d-280) | Post-gate code changes are reported not applied, then authorized and both gates rerun | 2026-07-16 | adopted | `[chat]` |
| [D-281](#d-281) | Land the two verified FP-shape guards before D1 leaves the experimental flag | 2026-07-16 | proposed | `[chat]` |
| [D-282](#d-282) | Frozen files are not edited: reviews work around them and their defects are documented | 2026-07-16 | adopted | `[chat]` |
| [D-283](#d-283) | S-D8's flag-OFF gate is a derived target (1779 + Δ = 1784), pre-registered and committed before the run | 2026-07-22 | adopted | `[chat]` |
| [D-284](#d-284) | Extraction v2 must carry a mechanical coverage gate: lines_read equals lines_total | 2026-07-25 | adopted | `[chat]` |

### Infrastructure, Docker & compute

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-285](#d-285) | Accept per-merge latency as the price of semantic detection, document it, defer the mitigations | 2026-04-16 | adopted | `[recon]` |
| [D-286](#d-286) | Bound external tool invocations: configurable timeouts everywhere, a cold-start budget for the driver | 2026-04-16 | abandoned | `[recon]` |
| [D-287](#d-287) | All evaluated merge tools run from pinned merge-tools/<name> Docker images, never host PATH | 2026-04-21 | adopted | `[recon]` |
| [D-288](#d-288) | git is the only tool exempt from Docker-only; host installs are ad-hoc dev convenience | 2026-04-21 | adopted | `[recon]` |
| [D-289](#d-289) | M0 plan: pin Mergiraf 0.4.0, install natively via cargo, invoke through a temp git repo | 2026-04-22 | superseded | `[recon]` |
| [D-290](#d-290) | Weave ships as a Dockerized backend, overriding the plan's native-Rust invocation | 2026-04-22 | adopted | `[recon]` |
| [D-291](#d-291) | Invoke RefactoringMiner through a DirPairMain Java wrapper in Docker, built from the released ZIP | 2026-04-22 | adopted | `[recon]` |
| [D-292](#d-292) | Whether Joern and the JVM merge tools can share one Java 17 runtime in the driver is unresolved | 2026-04-22 | open | `[recon]` |
| [D-293](#d-293) | Hard-pin Weave v0.3.2 and drop the adapter rather than fix forward on v0.4 | 2026-04-25 | adopted | `[recon]` |
| [D-294](#d-294) | Force a clean CWD per Weave invocation so a stray .weave.toml cannot poison batch evaluation | 2026-04-25 | adopted | `[recon]` |
| [D-295](#d-295) | Build the RefactoringMiner image on eclipse-temurin:17-jdk for Joern compatibility | 2026-05-05 | adopted | `[recon]` |
| [D-296](#d-296) | First RefactoringMiner pin: 3.0.13 on eclipse-temurin:21-jdk with dual-mode Path D tagging | 2026-05-05 | superseded | `[recon]` |
| [D-297](#d-297) | Roll the RefactoringMiner pin back to 2.4.0, dropping the JDK base to 17 with zero Java edits | 2026-05-06 | adopted | `[recon]` |
| [D-298](#d-298) | Override M0: pin Mergiraf 0.17.0, install via Docker, invoke the standalone three-file CLI | 2026-05-12 | adopted | `[recon]` |
| [D-299](#d-299) | Docker-only rule covers evaluated merge tools, not framework tooling, Joern, or one-off renders | 2026-05-14 | adopted | `[mixed]` |
| [D-300](#d-300) | Keep Tier-3 AST normalize off by default in tests and cache it on the post-gjf hash | 2026-05-14 | adopted | `[recon]` |
| [D-301](#d-301) | Cache expensive container work per unit, make it resumable, and batch to amortize startup | 2026-05-18 | adopted | `[chat]` |
| [D-302](#d-302) | Treat meaningful runs as unattended background jobs, not interactive sessions | 2026-05-20 | adopted | `[chat]` |
| [D-303](#d-303) | Operate AWS under least privilege with an explicit go-ahead gate and a $20 budget backstop | 2026-05-20 | adopted | `[chat]` |
| [D-304](#d-304) | Account for the Apple Silicon emulation tax by measurement, and never promise a native speedup | 2026-05-25 | adopted | `[chat]` |
| [D-305](#d-305) | Probe images and checksum transfers before running anything that depends on them | 2026-05-25 | adopted | `[chat]` |
| [D-306](#d-306) | Clone blobless with a per-clone timeout, and harden the reuse path instead of predicting cost | 2026-05-26 | adopted | `[chat]` |
| [D-307](#d-307) | Lift the per-strategy triple parse into a shared-CPG component as the one data-demanded refactor | 2026-06-11 | superseded | `[chat]` |
| [D-308](#d-308) | Watch runs by process exit and anomalies only, and use the wait to build downstream tooling | 2026-06-11 | adopted | `[chat]` |
| [D-309](#d-309) | Verify HTML deliverables over a localhost static server, and link to them by http not file | 2026-06-20 | adopted | `[chat]` |
| [D-310](#d-310) | Either run the two remaining Docker P2 configs or document the 3-of-5 partial | 2026-06-24 | adopted | `[chat]` |
| [D-311](#d-311) | Seed each run's cache from the previous run's, invalidating only what changed | 2026-06-25 | adopted | `[chat]` |
| [D-312](#d-312) | Run long unattended evaluations on a one-shot x86_64 EC2 instance instead of the laptop | 2026-06-25 | adopted | `[chat]` |
| [D-313](#d-313) | First AWS arrangement: user launches the instance, assistant drives it over SSH | 2026-06-25 | superseded | `[chat]` |
| [D-314](#d-314) | Ship locally-built amd64 images to the instance with docker save/load rather than rebuilding | 2026-06-25 | superseded | `[chat]` |
| [D-315](#d-315) | Run the P2 harness sequentially on AWS with no sharding code change | 2026-06-25 | adopted | `[chat]` |
| [D-316](#d-316) | Commit the AWS kit and record each cycle's real commands, costs and lessons in CLI-DEPLOY.md | 2026-06-25 | adopted | `[chat]` |
| [D-317](#d-317) | Collect, commit and push results before teardown; then verify the account is empty | 2026-06-26 | adopted | `[chat]` |
| [D-318](#d-318) | Move each compute run to AWS and shrink the bundle so the move is cheap | 2026-07-02 | adopted | `[chat]` |
| [D-319](#d-319) | Do not run P3 and P4 as parallel sessions or worktree agents | 2026-07-02 | adopted | `[chat]` |
| [D-320](#d-320) | Run the #26 project-level tagging locally because shipping 2.1 GB of clones is not worth it | 2026-07-03 | superseded | `[chat]` |
| [D-321](#d-321) | Rewrite the Phase-2b prompt to run evaluation on AWS and carry the four paid-for lessons | 2026-07-03 | adopted | `[chat]` |
| [D-322](#d-322) | Trace apparent failures to the wrapper before blaming the run | 2026-07-03 | adopted | `[chat]` |
| [D-323](#d-323) | Freeze workload models by phase: Opus 4.8 batch for both labeling passes, Fable 5 for consolidation | 2026-07-08 | adopted | `[chat]` |
| [D-324](#d-324) | Run bulk labeling through the Batch API from a committed harness, with structured outputs | 2026-07-08 | adopted | `[chat]` |
| [D-325](#d-325) | Keep the API key in ~/.zshenv and span the two venvs with stdlib-only shared code | 2026-07-08 | adopted | `[chat]` |
| [D-326](#d-326) | Harden request assembly and the manifest before G0 as ordinary pre-gate edits | 2026-07-09 | adopted | `[chat]` |
| [D-327](#d-327) | Verify the request instrument before submitting and compare artifacts on their bytes | 2026-07-09 | adopted | `[chat]` |
| [D-328](#d-328) | Standing rule: always prefer AWS over local for compute runs, with a ≤20-unit local exception | 2026-07-15 | adopted | `[chat]` |
| [D-329](#d-329) | Tune-control runs are a documented local exception to the AWS-first rule | 2026-07-15 | adopted | `[chat]` |
| [D-330](#d-330) | Shard long runs into static round-robin shards, re-partitioning stragglers mid-run | 2026-07-16 | superseded | `[chat]` |
| [D-331](#d-331) | Adopt the audit fixes to the tune runner: cache-key namespace, exit codes, stale cache, one registry | 2026-07-16 | adopted | `[chat]` |
| [D-332](#d-332) | Two regressions the multi-lane rewrite introduced: ABORT exit code and a latent lane-key coupling | 2026-07-16 | superseded | `[chat]` |
| [D-333](#d-333) | Persist the tune-runner cache once per scenario, accepting weaker crash durability | 2026-07-16 | adopted | `[chat]` |
| [D-334](#d-334) | Move save() out of the per-lane loop (or append JSONL) to stop quadratic cache rewrites | 2026-07-16 | adopted | `[chat]` |
| [D-335](#d-335) | Replace static shards with a 4-worker work queue — deferred out of the frozen run, adopted in S-D7 | 2026-07-17 | adopted | `[chat]` |
| [D-336](#d-336) | Run independent cycles concurrently in separate regions, sharing no AWS resource or commit | 2026-07-22 | adopted | `[chat]` |
| [D-337](#d-337) | Build pinned images on-instance but ship the unpinned ones, and set no _JAVA_OPTIONS | 2026-07-22 | adopted | `[chat]` |
| [D-338](#d-338) | Proposed v2 model split: Sonnet 5 for extraction, Opus 5 for consolidation and prose, no Haiku | 2026-07-25 | superseded | `[chat]` |
| [D-339](#d-339) | v2 orchestration route and the two-pass token budget are left open for Ali | 2026-07-25 | open | `[chat]` |

### Repository & working conventions

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-340](#d-340) | Source of truth is the source code, not the documentation | 2026-04-15 | adopted | `[mixed]` |
| [D-341](#d-341) | Gitignore anything regenerable; keep only evidence and irreplaceable binaries | 2026-04-15 | adopted | `[mixed]` |
| [D-342](#d-342) | Root-level docs are authoritative; superseded material is archived, never deleted | 2026-04-16 | adopted | `[mixed]` |
| [D-343](#d-343) | Naming and checklist conventions for adding a strategy | 2026-04-16 | adopted | `[recon]` |
| [D-344](#d-344) | Enabled strategies are configured in YAML, not hardcoded and not env vars | 2026-04-16 | adopted | `[recon]` |
| [D-345](#d-345) | Each integration phase is one branch and one PR with explicit acceptance criteria | 2026-04-21 | superseded | `[recon]` |
| [D-346](#d-346) | A new tool adapter phase adds only new files; the evaluation core is untouched | 2026-04-21 | adopted | `[recon]` |
| [D-347](#d-347) | Each plan file is independently gated and owns its components alone | 2026-04-25 | adopted | `[recon]` |
| [D-348](#d-348) | A commit fixes the docs it stales; wrong claims are retracted, out-of-scope staleness is flagged | 2026-05-06 | adopted | `[mixed]` |
| [D-349](#d-349) | Committed reports_* directories are preserved evidence; new runs get their own directory | 2026-05-06 | adopted | `[mixed]` |
| [D-350](#d-350) | Findings, deferrals and deviations go into durable artifacts, not just the commit message | 2026-05-14 | adopted | `[mixed]` |
| [D-351](#d-351) | Work lands as small ordered commits, each reviewable and each leaving the tree green | 2026-05-15 | adopted | `[mixed]` |
| [D-352](#d-352) | Test-suite conventions: no redundant integration tests, keep extra coverage, scope collection | 2026-05-15 | adopted | `[mixed]` |
| [D-353](#d-353) | Generated diagrams stay scratch unless a file is asked for, then self-contained under docs/ | 2026-05-18 | adopted | `[chat]` |
| [D-354](#d-354) | The taxonomy is duplicated as a parity-tested copy, not imported across subprojects | 2026-05-18 | adopted | `[mixed]` |
| [D-355](#d-355) | Commit and push only on explicit instruction, and only after a review pass | 2026-05-19 | adopted | `[chat]` |
| [D-356](#d-356) | Presentation binaries are tracked, never renamed or deleted, and named by month precedent | 2026-06-09 | adopted | `[chat]` |
| [D-357](#d-357) | List the calls made without asking when committing on Ali's behalf | 2026-06-09 | proposed | `[chat]` |
| [D-358](#d-358) | Unreviewed and draft content is held out of commits and the omission is recorded | 2026-06-11 | adopted | `[chat]` |
| [D-359](#d-359) | STATUS/THREATS disclosure of new work waits for its planned stage gate | 2026-06-12 | adopted | `[chat]` |
| [D-360](#d-360) | Large raw result caches are committed as auditable evidence, once final | 2026-06-16 | adopted | `[chat]` |
| [D-361](#d-361) | Programme work commits directly to main, not on feature branches | 2026-06-20 | adopted | `[chat]` |
| [D-362](#d-362) | Review-flagged cleanups batched as one low-risk pass, awaiting a ruling | 2026-06-24 | proposed | `[chat]` |
| [D-363](#d-363) | Repo reviews inventory only real source and tag every file with one of six verdicts | 2026-06-24 | adopted | `[chat]` |
| [D-364](#d-364) | Report-directory run.log is force-added despite the global *.log ignore | 2026-07-03 | adopted | `[chat]` |
| [D-365](#d-365) | Commit before running anything that snapshots HEAD | 2026-07-03 | adopted | `[chat]` |
| [D-366](#d-366) | Sessions hand off through committed artifacts only, never through chat | 2026-07-08 | adopted | `[chat]` |
| [D-367](#d-367) | Review finder agents return at most 6 conclusions as a bare JSON array | 2026-07-16 | adopted | `[chat]` |
| [D-368](#d-368) | A convention violation counts only with the exact rule and the exact line quoted | 2026-07-16 | adopted | `[chat]` |
| [D-369](#d-369) | Duplication is accepted rather than edit a frozen lane or diverge from the ABC | 2026-07-16 | adopted | `[chat]` |
| [D-370](#d-370) | Test files should import the docker probe and call the production pair helper | 2026-07-16 | adopted | `[chat]` |
| [D-371](#d-371) | Parallel sessions keep hands off the tree and coordinate via the committed prompt | 2026-07-22 | adopted | `[chat]` |
| [D-372](#d-372) | DECISIONS.md: methodology included, provenance per entry, coverage stated, not authoritative | 2026-07-25 | adopted | `[chat]` |
| [D-373](#d-373) | v2 of the decision record should add supersession fields and a JSON sidecar | 2026-07-25 | adopted | `[chat]` |

### Thesis framing & reporting

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-374](#d-374) | Reframe the thesis around composition-by-abstraction with exit-1 as a third merge outcome | 2026-04-17 | adopted | `[mixed]` |
| [D-375](#d-375) | Report JDime's 96% crash rate as partly intrinsic and harness-scoped, crediting the Passau lineage | 2026-04-17 | adopted | `[mixed]` |
| [D-376](#d-376) | Report Mastery's FP rate with an intrinsic-limitation caveat instead of normalising it away | 2026-04-22 | adopted | `[recon]` |
| [D-377](#d-377) | Write up language as a second dispatch axis alongside refactoring cluster | 2026-04-25 | superseded | `[recon]` |
| [D-378](#d-378) | Pre-commit to publishing null results as findings rather than tuning toward a signal | 2026-04-25 | adopted | `[mixed]` |
| [D-379](#d-379) | Do not cite Weave's 31/31 upstream headline without the project's own numbers | 2026-04-25 | adopted | `[recon]` |
| [D-380](#d-380) | Restate coverage as "2 strategies, 1 of 7 categories" across all docs | 2026-05-13 | adopted | `[recon]` |
| [D-381](#d-381) | Reframe Spork's FP rate as a comparator-ground-truth gap, substantially closed on this corpus | 2026-05-14 | adopted | `[mixed]` |
| [D-382](#d-382) | Publish the undershooting Tier C numbers as the honest interim state | 2026-05-14 | adopted | `[recon]` |
| [D-383](#d-383) | Cite upstream Mergiraf numbers and report FP rate under each criterion alongside 3e | 2026-05-14 | proposed | `[recon]` |
| [D-384](#d-384) | Maintain a project-level THREATS_TO_VALIDITY.md under the standard empirical-SE taxonomy | 2026-05-16 | adopted | `[mixed]` |
| [D-385](#d-385) | Report the weak per-cluster signal as suggestive with the hedge attached, not tuned or softened | 2026-05-18 | adopted | `[mixed]` |
| [D-386](#d-386) | Keep presentation notes as a standalone markdown file in the slide-by-slide convention | 2026-05-20 | adopted | `[chat]` |
| [D-387](#d-387) | Bound the "Spork is best nowhere" negative: two clusters untested, taxonomy not Spork-centric | 2026-05-26 | adopted | `[chat]` |
| [D-388](#d-388) | Surface corrections explicitly and keep refuted designs as named negative results | 2026-06-11 | adopted | `[chat]` |
| [D-389](#d-389) | Describe the zero-yield category detectors as low-yield cheap coverage, not broken | 2026-06-11 | adopted | `[chat]` |
| [D-390](#d-390) | Restate the contribution as the first base-rate measurement of the hypothesized categories | 2026-06-11 | adopted | `[chat]` |
| [D-391](#d-391) | Frame the deck around a second pivot: from category-specific detection to generic consistency-checking | 2026-06-18 | adopted | `[chat]` |
| [D-392](#d-392) | Keep the 7-slide spine tight; demote granularity asymmetry, dropped lane and flag table to backups | 2026-06-18 | adopted | `[chat]` |
| [D-393](#d-393) | Present R2 as provisional rather than rushing adjudication before the talk | 2026-06-18 | adopted | `[chat]` |
| [D-394](#d-394) | QA every deck build: text-extraction of numbers, then a Keynote PNG render check | 2026-06-18 | adopted | `[chat]` |
| [D-395](#d-395) | Slides use impersonal voice, speaker notes use first person, bylines keep the name | 2026-06-18 | adopted | `[chat]` |
| [D-396](#d-396) | Reframe the contribution around the routing null result: Mergiraf-only plus fast-path | 2026-06-24 | adopted | `[chat]` |
| [D-397](#d-397) | Only deltas and pre-vs-post comparisons are legitimate readings of the enriched corpus | 2026-06-24 | adopted | `[chat]` |
| [D-398](#d-398) | Carry the P2 FINDINGS honesty caveats: corroboration framing, ≤33 FPs, route verification, provenance footnotes | 2026-06-26 | adopted | `[chat]` |
| [D-399](#d-399) | Rewrite FINDINGS as v2 rather than patching, leaving v1 in git history | 2026-07-02 | adopted | `[chat]` |
| [D-400](#d-400) | Promote the six-tool neutral run to the canonical thesis headline table | 2026-07-02 | adopted | `[chat]` |
| [D-401](#d-401) | Footnote driver-mergiraf's med_rt = 0.0 as assembled from Stage C | 2026-07-02 | adopted | `[chat]` |
| [D-402](#d-402) | Produce report charts with matplotlib+seaborn, accepting a pyproject dependency bump | 2026-07-02 | adopted | `[chat]` |
| [D-403](#d-403) | Frame the n=50 RM2 recall delta as methodology-tightening, citing the pooled number | 2026-07-03 | adopted | `[chat]` |
| [D-404](#d-404) | Withdraw the "maybe our corpus was unusual" hedge on the base-rate finding | 2026-07-04 | adopted | `[chat]` |
| [D-405](#d-405) | Bar the unqualified "detects semantic conflicts" claim; shift weight to what is measured | 2026-07-04 | adopted | `[chat]` |
| [D-406](#d-406) | Claim bounded severity of false blocks, not impossibility of false blocks | 2026-07-06 | adopted | `[chat]` |
| [D-407](#d-407) | Attribute R2 and R1 to their own runs, never to one | 2026-07-06 | adopted | `[chat]` |
| [D-408](#d-408) | Ship decks without embedded notes and carry an AWS provenance band on the data slides | 2026-07-06 | adopted | `[chat]` |
| [D-409](#d-409) | Present the 7-category taxonomy as fixture-derived design apparatus, not a validated classification | 2026-07-08 | proposed | `[chat]` |
| [D-410](#d-410) | Never blend numbers across instruments; state every result per-instrument | 2026-07-11 | adopted | `[chat]` |
| [D-411](#d-411) | Start the thesis write-up now and treat detector work as the optional parallel track | 2026-07-15 | adopted | `[chat]` |
| [D-412](#d-412) | Verify cited numbers against the underlying data and artifacts before publishing | 2026-07-15 | adopted | `[chat]` |
| [D-413](#d-413) | Cite the pooled name-binding family number; per-category cells stay bounded, not pinned | 2026-07-16 | adopted | `[chat]` |
| [D-414](#d-414) | Scope literature and prior-art consultations tightly: research-only, cited, compact | 2026-07-16 | adopted | `[chat]` |
| [D-415](#d-415) | Report the D2 file-local ceiling decomposition as a boundary result, not a detector failure | 2026-07-16 | adopted | `[chat]` |
| [D-416](#d-416) | Lead the thesis title with the empirical finding, keeping Java/Git and barring collision phrases | 2026-07-18 | proposed | `[chat]` |
| [D-417](#d-417) | Ground thesis framing in the code and measured artifacts, not a single README | 2026-07-18 | adopted | `[chat]` |
| [D-418](#d-418) | Draft the abstract with Zeller's five moves, labelled blocks and a bracketed pending slot | 2026-07-18 | adopted | `[chat]` |
| [D-419](#d-419) | The n=50 six-tool table may never be presented as a rival tool ranking | 2026-07-18 | adopted | `[chat]` |
| [D-420](#d-420) | Credit Schesch et al. openly with a dedicated relation section, delta table and disjoint RQs | 2026-07-18 | proposed | `[chat]` |
| [D-421](#d-421) | Report the 56.7% escape stratum as a first-class result, not instrument failure | 2026-07-18 | adopted | `[chat]` |
| [D-422](#d-422) | Verify evolution.md is the genuine paper text before using it as a primary source | 2026-07-18 | adopted | `[chat]` |
| [D-423](#d-423) | Structure the write-up on the Passau empirical-SE house style, 11 chapters over 60 pages | 2026-07-22 | superseded | `[chat]` |
| [D-424](#d-424) | Revise to 12 chapters, adding methodology/infrastructure and AI-contributions chapters | 2026-07-22 | proposed | `[chat]` |
| [D-425](#d-425) | Thesis must cover experiment mechanics, AWS deployment, AI-use transparency and adjudication tooling | 2026-07-22 | adopted | `[chat]` |
| [D-426](#d-426) | Fix a shared evidence-chapter skeleton with execution mechanics and AWS environment in Ch. 5 | 2026-07-22 | proposed | `[chat]` |
| [D-427](#d-427) | Organise Ch. 9 by three AI roles, with a delineation table and AI-use log started now | 2026-07-22 | proposed | `[chat]` |
| [D-428](#d-428) | Enforce one claim, one home: Ch. 5 is how, Ch. 9 is who, neither restates results | 2026-07-22 | adopted | `[chat]` |
| [D-429](#d-429) | Write evidence-out in order of frozenness, ugly-but-complete first, polish last | 2026-07-22 | proposed | `[chat]` |
| [D-430](#d-430) | Fix the spine and claims ledger first, get supervisor sign-off before any prose | 2026-07-22 | proposed | `[chat]` |
| [D-431](#d-431) | The chair's formal template overrides the proposed outline's cosmetics | 2026-07-22 | proposed | `[chat]` |
| [D-432](#d-432) | Use the as-built sq.md architecture figure, not the aspirational pipeline diagram | 2026-07-22 | proposed | `[chat]` |
| [D-433](#d-433) | Cite S-D7's improved R2' as an instrument comparison, not fresh validation | 2026-07-23 | adopted | `[chat]` |
| [D-434](#d-434) | Build the late-July delta deck as v7 in the existing series style | 2026-07-24 | adopted | `[chat]` |
| [D-435](#d-435) | State ceilings, unsummed controls and the latency price as first-class numbers on slides | 2026-07-24 | adopted | `[chat]` |
| [D-436](#d-436) | Close the deck with the default-enable switch as an explicit discussion question | 2026-07-24 | adopted | `[chat]` |
| [D-437](#d-437) | Add a method slide documenting the taxonomy pipeline, tooling and Ali's gate rulings | 2026-07-24 | adopted | `[chat]` |
| [D-438](#d-438) | Plain-language register for slides; precision terms stay in FINDINGS | 2026-07-24 | adopted | `[chat]` |
| [D-439](#d-439) | Make denominators explicit: 71% is a share of the 119 visible-cause cases | 2026-07-24 | adopted | `[chat]` |
| [D-440](#d-440) | Hold all speaker-notes edits until Ali asks at the end | 2026-07-24 | adopted | `[chat]` |
| [D-441](#d-441) | Publish deck renders to a stable-URL private artifact viewer for phone review | 2026-07-24 | adopted | `[chat]` |
| [D-442](#d-442) | Replace the pricing table with bars and show the cost arithmetic on the slide | 2026-07-24 | adopted | `[chat]` |
| [D-443](#d-443) | Insert a slide mapping the 2025 guessed categories onto the measured patterns | 2026-07-24 | adopted | `[chat]` |
| [D-444](#d-444) | Offer to name the three clean control pools explicitly on slide 7 | 2026-07-24 | proposed | `[chat]` |
| [D-445](#d-445) | Pose four RQs closable by frozen evidence, each with a one-sentence answer preview | 2026-07-25 | proposed | `[chat]` |

### Cross-cutting & meta

| # | Decision | Date | Status | Tag |
|---|---|---|---|---|
| [D-446](#d-446) | Timebox escape rule: a 2× overrun stops work until a STATUS.md revisit note is written | 2026-04-21 | adopted | `[recon]` |
| [D-447](#d-447) | Validate the plan against the code in a Phase 0 memo before entering plan mode | 2026-05-18 | adopted | `[chat]` |
| [D-448](#d-448) | Make MergeScenario.from_dict filter to known fields, accepting a silent-failure cost | 2026-05-18 | adopted | `[chat]` |
| [D-449](#d-449) | Surface doc/data inconsistencies and honesty nuances instead of reconciling them silently | 2026-05-18 | adopted | `[chat]` |
| [D-450](#d-450) | Cover the CLI classification wiring with a Docker-free unit test | 2026-05-18 | adopted | `[chat]` |
| [D-451](#d-451) | Hand work to fresh sessions with self-contained prompts and artifact-only handoff | 2026-05-26 | adopted | `[chat]` |
| [D-452](#d-452) | Keep the empirical clusters as the primary codebook scheme over the four-family view | 2026-07-10 | adopted | `[chat]` |
| [D-453](#d-453) | Rename the two `vs` category ids and record the old→new crosswalk gaps explicitly | 2026-07-10 | adopted | `[chat]` |
| [D-454](#d-454) | Withdraw the phantom-unit_id suspicion after a mechanical manifest check | 2026-07-10 | adopted | `[chat]` |
| [D-455](#d-455) | Open every session prompt with a mandatory ambiguity check that must stop and ask | 2026-07-15 | adopted | `[chat]` |
| [D-456](#d-456) | Serialize the detector cycle at a WIP limit of one while writing has priority | 2026-07-15 | adopted | `[chat]` |
| [D-457](#d-457) | Brief finder agents on one angle, capped at six findings each with a failure scenario | 2026-07-16 | adopted | `[chat]` |
| [D-458](#d-458) | Bar style-level and micro-optimization findings from review, and never pad to the cap | 2026-07-16 | adopted | `[chat]` |
| [D-459](#d-459) | Rank detector review findings false-flag first, then crash, then silent FN | 2026-07-16 | adopted | `[chat]` |
| [D-460](#d-460) | Verify borrowed-helper contracts by running probes, not by reading the code | 2026-07-16 | adopted | `[chat]` |
| [D-461](#d-461) | Give cross-lane grammar and predicates a single source of truth | 2026-07-16 | adopted | `[chat]` |
| [D-462](#d-462) | Derive or assert parallel state instead of hand-maintaining it, and drop dead guards | 2026-07-16 | adopted | `[chat]` |
| [D-463](#d-463) | Two duplications deliberately kept: coupled helper signature and the tune-tool fixture | 2026-07-16 | adopted | `[chat]` |
| [D-464](#d-464) | Review the file standalone against open-source prior art, making no changes | 2026-07-16 | adopted | `[chat]` |
| [D-465](#d-465) | Reconstruct the project's identity from four parallel read-only explorations | 2026-07-18 | adopted | `[chat]` |
| [D-466](#d-466) | Run S-D6 in the current session at Ali's direction, overriding the fresh-session rule | 2026-07-22 | adopted | `[chat]` |
| [D-467](#d-467) | Distil the transcripts with a deterministic script and spend no model on it | 2026-07-25 | adopted | `[chat]` |
| [D-468](#d-468) | Withdraw the read-end-to-end claim and put measured 61.5% coverage on the record | 2026-07-25 | adopted | `[chat]` |
| [D-469](#d-469) | Run v2 extraction as two independent passes with a frozen decision definition | 2026-07-25 | adopted | `[chat]` |

---

## Scope & project architecture

*91 primary source decisions → 32 entries; 1 not promoted (reasons in `docs/decision-record/entries/scope-architecture.json`).*

### <a id="d-001"></a>D-001 — Dataset and framework are Java-only, fixed at seven semantic-conflict categories

`2026-04-16 → 2026-05-19` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

**Decision.** The evaluation dataset is fixed at 7 named categories of semantic merge conflict, all in Java; test cases and merge scenarios are Java-only. The comparison framework keeps hardcoding `.java` (ISSUES.md #12) and deliberately does not exploit Mergiraf's 25+ language support, leaving multi-language extension to a future cycle; work that would make the driver's language-dispatch axis genuinely load-bearing (a multi-language refactoring detector, or a non-Java sub-method specialist) is also out of scope. The 7-category taxonomy was later reframed as the historical design taxonomy — see [D-029](#d-029).

**Why.** No reason is recorded for the Java-only boundary itself or for the 7 categories. The only reason recorded on this axis is for not pursuing multi-language work: under the RM2-only toolchain the language guard is inert, and making it load-bearing would need a multi-language refactoring detector or a non-Java sub-method specialist — both declared out of scope.

**Status.** adopted. S12 (2026-07-26): the boundary held to the end — ISSUES.md #12 still tracks the hardcoded .java extension as accepted scope, no multi-language work exists anywhere, the language axis was demoted to a defensive guard (adopted), and every corpus and detector is Java-only.

**Source.** `preA:pre-architecture-refmerge-16`, `preA:pre-mergiraf-integration-recon-13`, `preA:pre-spork-driver-integration-02` · Artifacts: `merge-tool-comparison/ISSUES.md #12`, `docs/plans/spork-driver-integration.md`

> **Java focus**: Test cases and merge scenarios are in Java
>
> — `2026-04-16_pre-architecture-refmerge.txt:876`

> Making the axis load-bearing would need a multi-language refactoring detector
>
> — `2026-04-25_pre-spork-driver-integration.txt:32`

> Mergiraf's broader support (25+ languages) is something to take advantage of in a future multi-language extension, not now.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:192`

### <a id="d-002"></a>D-002 — Semantic verification is mandatory and applied differentially across the merge triple

`2026-04-16 → 2026-06-11` · **adopted** · `[mixed]` · corroboration: mixed · confidence: medium · actors: unclear

*Actors note: The 2026-04-16 plan statement carries no attribution; the 2026-06-11 restatement of the same discipline as the project's exportable technique is Claude's, in a review Ali did not visibly ratify. Recorded as unclear rather than taking a majority.*

**Decision.** Joern CPG analysis is a required stage of every merge run, not an optional or deferred step: the merged result is always analysed before accept/reject. After the 2026-06 pilot, the technique is stated more precisely and made a conformance rule — apply standard static analysis differentially across the merge triple and flag only merge-induced deltas — which every new detector must follow.

**Why.** Semantic conflicts (stale reads, infinite loops, scope capture, control-flow interference) can only be detected by dataflow and control-flow analysis on the merged result; no amount of structural merging or refactoring detection substitutes for analysing how the merged code actually behaves. The differential framing was argued from the detector record: every deployable detector became so only after merge-induced filtering against both parents, while every single-version analysis drowned in inherited fields, deliberate idioms or parser artifacts, and every detector that skipped the filter (v1 InfiniteLoop, the dropped type lane) died of false positives.

**Status.** adopted. S12 (2026-07-26): both halves are the shipped design — core/driver.py:70-101 runs the analysis stage unconditionally on every merge before accept/reject (fail-safe reject on strategy crash), and the differential merge-induced-only conformance rule is the standard every lane follows (the five defaults and all three experimental lanes are differential; ISSUES.md #31 records the widening as 'resolution differentials', and the D2 lane header states 'differential 3-way, merge-induced only').

**Cross-theme.** *depends-on* → [D-097](#d-097), [D-127](#d-127) — The differential principle was ratified in practice for the lanes that shipped (differential-only abstention, merge-induced filtering); the plan-era universal mandate as stated was never ratified. Stays proposed.

**Source.** `preA:pre-architecture-refmerge-04`, `b:bfc672b4-23` · Artifacts: `strategies/joern_strategies/`

> No amount of structural merging or refactoring detection can substitute for analyzing how the merged code actually behaves.
>
> — `2026-04-16_pre-architecture-refmerge.txt:206`

> "Apply standard static analysis differentially across the merge triple, flag only merge-induced deltas" is the exportable idea, independent of any category.
>
> — `2026-06-11_bfc672b4.txt:465`

### <a id="d-003"></a>D-003 — Driver stays a Python plugin host invoking external tools by subprocess

`2026-04-16` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

**Decision.** The driver remains Python and invokes all external analysis/merge tools (Java RefactoringMiner and RefMerge, Rust Mergiraf, Scala/Java Joern) through subprocess calls rather than in-process APIs or a single-language reimplementation. All new analysis capability is added as `MergeStrategy` subclasses discovered by the plugin loader, with strategy selection moving from hardcoding in driver.py to config/strategies.yaml; and the plugin interface changes from `analyze(file_path, base_content)` to `analyze(context: MergeContext)`, where MergeContext carries base/ours/theirs/merged paths, per-branch RM-ASTDiff refactoring lists and the merge backend used.

**Why.** Strategies need merge context — refactoring metadata and branch information — in addition to the merged file; RefactoringConflictStrategy, for example, operates on refactoring metadata rather than on the merged file itself. No reason is recorded for the Python/subprocess choice or for the plugin-loader rule.

**Status.** adopted. S12 (2026-07-26): the shipped architecture — core/plugin_loader.py discovers MergeStrategy subclasses under strategies/, config/strategies.yaml drives enablement (adopted sibling), all external tools (Joern, RM2, Mergiraf, Spork, Weave) are subprocess/Docker invocations, and the driver never left Python. Supersedes: *core/interfaces.py MergeStrategy.analyze(file_path, base_content)*; *hardcoded strategy selection in driver.py*.

**Source.** `preA:pre-architecture-refmerge-09`, `preA:pre-architecture-refmerge-23`, `preA:pre-architecture-refmerge-24` · Artifacts: `core/interfaces.py`, `config/strategies.yaml`, `core/plugin_loader.py`

> The `MergeStrategy` interface is extended to receive merge context (refactoring metadata, branch information) in addition to the merged file:
>
> — `2026-04-16_pre-architecture-refmerge.txt:210`

> **Plugin architecture**: All new analysis tools are added as `MergeStrategy` subclasses
>
> — `2026-04-16_pre-architecture-refmerge.txt:874`

> **Language**: Python driver, calling Java/Scala/Rust tools via subprocess
>
> — `2026-04-16_pre-architecture-refmerge.txt:872`

### <a id="d-004"></a>D-004 — Ban LLM-based approaches; classic program analysis only

`2026-04-16` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** The research must use classic program-analysis techniques only; no LLM-based approaches are permitted in the driver or its strategies.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted. S12 (2026-07-26): held in the pipeline — no LLM appears anywhere in the driver or its strategies (all seven lanes are deterministic static analysis), reaffirmed 2026-07-15 by the adopted no-LLM-detector-lane decision. The instrument-side uses (labeling, coding) sit outside the analysis pipeline under the drafts-not-oracles discipline, with the one pipeline-adjacent use recorded as an explicit carve-out — the boundary the S10z contradiction-resolution documents.

**Cross-theme.** *contradicts* → [D-106](#d-106), [D-220](#d-220), [D-107](#d-107) — The tension resolves as a scope boundary the record itself draws: the ban holds inside the analysis pipeline (reaffirmed 2026-07-15 by [D-106](#d-106), which cites the circularity of LLM-labeled ground truth), while LLM-as-measurement-instrument was adopted separately under drafts-not-oracles discipline, with the one pipeline-adjacent use recorded as an explicit carve-out (fixture-spec extraction). No entry narrows the ban in writing — the boundary is enacted, not stated — and it is rendered as exactly that on both ends.

**Source.** `preA:pre-architecture-refmerge-07`

> **No LLM approaches**: Research must use classic program analysis techniques only
>
> — `2026-04-16_pre-architecture-refmerge.txt:873`

### <a id="d-005"></a>D-005 — Decompose work into small independently testable phases, one PR each

`2026-04-16 → 2026-04-22` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Work is decomposed into numbered phases, one PR per phase, each adding one capability and independently testable, with results compared against the previous phase over the same 7 conflict categories: the pipeline as Step 0 (baseline) → Step 1 (Mergiraf) → Step 2 (RM-ASTDiff + RefMerge) → Step 3 (full Joern strategy suite); Mergiraf integration as six phases via Schesch upstream's adapter, with P3 resolving ISSUES.md #2 before headline numbers and a new M3.5 separating implementation from decision; RM2 integration as five phases (scenario tagger resolving ISSUES.md #3, Method Rename detector taking coverage 2/7 → 3/7, conditional pipeline gate). Within RM2 the splits follow dependency rather than convenience: R4a ships the runtime classifier and `language_of` as importable components touching no driver or backend file, with driver activation held to R4b, and R3 is sequenced as an independent phase depending only on R0.

**Why.** Each step must be independently testable before proceeding, and every step's results are compared to the previous step on the same categories. Splitting Phase 3 into decide (P3) and implement (M3.5) was needed because otherwise acceptance would only mark ISSUES.md #2 decided-pending-implementation rather than resolved. R4a exists separately from R4b because the W5 and S2 plans need to import a *runtime* classifier, whereas the R1 offline tagger writes scenario JSON for merge-tool-comparison only and is not callable at merge time. R3 stays standalone because it only needs the merged file and the base, works whether or not the dispatch flip exists, and coupling it would gate a 1-day deliverable on a multi-day prerequisite — R3 is verification-side, R4a/R4b are merging-side.

**Status.** adopted.

**Source.** `preA:pre-architecture-refmerge-13`, `preA:pre-commits-06`, `preA:pre-commits-11`, `preA:pre-commits-08`, `preA:pre-rm2-integration-24`, `preA:pre-rm2-integration-30` · Artifacts: `5cee722`, `77d988a`, `b990a52`, `docs/plans/mergiraf-integration.md`, `docs/plans/rm2-integration.md`, `semantic_merge_driver/core/refactoring_classifier.py`, `semantic_merge_driver/core/language_detect.py`

> Each step adds one major capability. Each step is independently testable. Results from each step are compared against the previous step using the same 7 conflict categories.
>
> — `2026-04-16_pre-architecture-refmerge.txt:370`

> Coupling them would gate a 1-day deliverable on a multi-day prerequisite. R3 is verification-side; R4a/R4b are merging-side; the architectural split is principled.
>
> — `2026-04-22_pre-rm2-integration.txt:435`

> New M3.5 (mergiraf): implementation phase for the ISSUES.md #2 fix.
>
> — `2026-04-15_pre-commits.txt:113`

### <a id="d-006"></a>D-006 — Take Path A: a local Mergiraf adapter, not Schesch's upstream harness

`2026-04-21 → 2026-05-11` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** Mergiraf is added to the existing `merge-tool-comparison/` framework as a local ~80-line adapter mirroring `spork.py` (one adapter, one `tools.yaml` row, three tests, Mergiraf pinned at 0.4.0, invoked through the Git merge-driver convention with a temp git repo), with the comparator left textual and ISSUES.md #2 tracked under M3/γ. Reimplementing, forking, vendoring or syncing benedikt-schesch/AST-Merging-Evaluation is ruled out, as is building out the refactoring-detection branch in this plan; project-test-suite ground truth is out of scope for Path A (3a kept as maximalist fallback). The M0 phase that produced this decision was read-only inspection using an untracked depth-50 scratch clone in /tmp, changing no code or config in the repo.

**Why.** Ali has live investment in the current framework's plumbing (Click CLI, caching, adapter ABC) plus the thesis extensions — the Joern strategy axis, the R0 RM2 wrapper, the dataset loader — none of which exist upstream and all of which Path B obsoletes; the minimal patch of one adapter is cheap and reversible while a full sync is expensive and irreversible. Path B costs an 84 GB test cache plus Maven, three JDKs and GraalVM, would kill our CLI, plugin loader and Docker runner, does not compose with the semantic_merge_driver/Joern track, and has known Apple Silicon + GraalVM + JDK8 problems with stacking QEMU slowdown; it would burn the cycle on framework replacement rather than on the contribution, which the MVP-first directive forbids. Test-suite ground truth stays reachable later via M3 option 3a.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-043](#d-043) (see the reconciliation note there)

**Source.** `preA:pre-mergiraf-integration-05`, `preB:pre-mergiraf-integration-09`, `preA:pre-mergiraf-integration-04`, `preA:pre-mergiraf-integration-recon-01`, `preA:pre-mergiraf-integration-recon-02`, `preB:pre-mergiraf-integration-recon-17`, `preA:pre-commits-28` · Artifacts: `c1034c0`, `merge-tool-comparison/src/tools/mergiraf.py`, `docs/plans/mergiraf-integration-recon.md`

> 84 GB cache + Maven + 3 JDKs + GraalVM. Massive install.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:121`

> The minimal patch — add one adapter — is cheap and reversible; a full sync is expensive and irreversible.
>
> — `2026-04-21_pre-mergiraf-integration.txt:283`

> Not reimplementing or forking Schesch's full upstream framework.
>
> — `2026-04-21_pre-mergiraf-integration.txt:45`

### <a id="d-007"></a>D-007 — MVP-first: ship end-to-end dispatch with two backends before empirical validation

`2026-04-22 → 2026-05-04` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: joint

*Actors note: Sources disagree: the MVP-first directive is attributed to Ali (execution-sequence.md), the Phase-6 split is Claude's drafting in the findings and Mergiraf plans, and one source carries no attribution. Recorded as joint because the directive was Ali's and the phase restructuring was the response to it.*

**Decision.** Stage ε is reordered so the MVP track ships the dispatch mechanism end-to-end with two backends (git-merge-file + Mergiraf) first — R0+M0, then R4a with Phase 6-lite in parallel, then R4b with the default flip — deferring the empirical validation/extension track (M1–M5, R1–R2, W5/S2/S3) until after. As a consequence Phase 6 of the Mergiraf plan is split: Phase 6-lite delivers the `MergeBackend` ABC plus the git and Mergiraf backends inside the MVP track, before Phases 1–5 finish, and Phase 6-validate afterwards confirms or refutes the backend choice against Phase 4 numbers. Each is one PR.

**Why.** Stated as an MVP-first directive: ship the dispatch mechanism end-to-end with two backends first, then validate empirically and extend. A non-split Phase 6 would either gate on M2–M5 evidence and delay the MVP by ~3–4 days, or ship the driver promotion with no evidence and lose the empirical-justification story; the split ships the mechanism early and does the evaluation honestly afterwards, applying evidence discipline retroactively.

**Status.** adopted. S12 (2026-07-26): executed — Phase 6-lite shipped the MergeBackend ABC + git/mergiraf backends before the validation track (3fef834, with the honest-caveat message), R4a+R4b followed, and execution-sequence.md records 'ε MVP track complete (R0 + M0 + M6-lite + R4a + R4b done — end-to-end auto-mode dispatch shipping)' with M1-M5/R1-R2 deferred exactly as this reordering prescribed. Supersedes: *earlier stage-ε ordering that gathered evidence before shipping dispatch*; *pre-2026-05-04 draft gating all of Phase 6 on Phase 4 evidence*.

**Source.** `preA:pre-execution-sequence-13`, `preA:pre-mergiraf-integration-18`, `preA:pre-tool-evaluation-findings-12` · Artifacts: `docs/plans/execution-sequence.md §2.ε`, `docs/plans/mergiraf-integration.md`, `docs/plans/rm2-integration.md`

> Order updated 2026-05-04 to reflect the **MVP-first directive**: ship the dispatch mechanism end-to-end with two backends first (git + Mergiraf), then validate empirically and extend.
>
> — `2026-04-22_pre-execution-sequence.txt:93`

> The split lets us have both: ship the mechanism early (option a's UX without its delay), then do the evaluation honestly (option b's evidence without its premature commitment).
>
> — `2026-04-21_pre-mergiraf-integration.txt:281`

### <a id="d-008"></a>D-008 — Add Mergiraf as a fifth comparison tool ungated; keep RM2 out of the tools table

`2026-04-22 → 2026-05-09` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: claude

*Actors note: The ungated recommendation is Claude's in tool-evaluation-findings.md; the commit that left the tools table unchanged carries no attribution. Recorded as claude because that is the only attribution the record gives.*

**Decision.** Proceed immediately, with no gate, on a Mergiraf adapter in `merge-tool-comparison/` alongside git merge-file, JDime, Spork and Mastery, using the same `MergeTool` adapter contract. When R0's RM2 artifacts are surfaced in the repo layout, the "Tools under evaluation" table is left unchanged.

**Why.** Mergiraf is expected to produce cleaner numbers than JDime (96% crash rate, partly intrinsic per Schesch) and Spork/Mastery (suspect FP inflation per ISSUES #2), because its fallback-to-conflict-markers behaviour makes conflict detection textually explicit. RM2 stays out of the table because it is reconnaissance for the upcoming integration, not a comparison tool.

**Status.** adopted.

**Source.** `preA:pre-tool-evaluation-findings-01`, `preA:pre-commits-26` · Artifacts: `cc55735`, `docs/plans/mergiraf-integration.md`, `merge-tool-comparison/README.md`, `merge-tool-comparison/src/tools/`

> Likely to produce cleaner numbers than JDime (which has a 96% crash rate — partly intrinsic per Schesch)
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:39`

> "Tools under evaluation" table left unchanged — RM2 is reconnaissance
>
> — `2026-04-15_pre-commits.txt:316`

### <a id="d-009"></a>D-009 — Keep the refactoring-aware merging track out of scope: RefMerge, IntelliMerge, RM-ASTDiff

`2026-04-22 → 2026-05-06` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

*Actors note: One source attributes the IntelliMerge skip to Claude's findings document; the other five carry no attribution. Recorded as unclear rather than generalising one source's attribution to the whole exclusion.*

**Decision.** No refactoring-aware merger is built or integrated in this cycle. RefMerge integration is ruled out until three stated conditions hold and RefMerge/IntelliMerge stay gated in tool-evaluation-findings.md §5, so the router dispatches only among Weave, Spork, Mergiraf and git-merge-file; IntelliMerge is skipped outright, revisited only if RefMerge integration fails. Plain RM2 is used for the classifier and detector, with RM-ASTDiff a non-goal unless R0 reconnaissance shows plain RM2 insufficient, and no upgrade to RM2 3.0 / RM-ASTDiff is attempted. Semantic strategy coverage beyond conflict category #6 is likewise out of scope, and no complete detector diff between RM 2.4.0 and 3.0.13 will be run — the recorded diffs are limited to what surfaced on the 10 F-harness scenarios.

**Why.** For the gate use case ("refactoring yes/no, which types") plain RM2 suffices; RM-ASTDiff is only needed if a downstream merger such as RefMerge or IntelliMerge consumes the AST-diff output, which is out of scope. IntelliMerge is strictly inferior to RefMerge per the literature. Naming these absences guards against scope creep at R4b, which is a default-flip phase only, so their absence from the router is deliberate rather than accidental. The version-diff data is a byproduct of the R0 F-harness run rather than a dedicated study, so a full diff on the Schesch set is out of scope. tool-evaluation-findings.md is the governing rationale document for the cycle exclusions.

**Status.** adopted.

**Source.** `preA:pre-commits-07`, `preA:pre-execution-sequence-24`, `preA:pre-rm2-integration-17`, `preA:pre-tool-evaluation-findings-07`, `preA:pre-rm2-integration-16`, `preA:pre-rm2-vs-rm3-differences-08` · Artifacts: `c5c96c3`, `docs/plans/tool-evaluation-findings.md`, `docs/plans/tool-evaluation-findings.md §5`, `docs/plans/rm2-recon-samples/fharness-10.json`

> For the gate use case ("refactoring yes/no, which types") plain RM2 suffices. RM-ASTDiff is only needed if a downstream *merger* (RefMerge/IntelliMerge) consumes the AST-diff output — which is out of scope here.
>
> — `2026-04-22_pre-rm2-integration.txt:132`

> **Not doing this cycle** (per [`tool-evaluation-findings.md`](tool-evaluation-findings.md)): RefMerge integration; strategy coverage beyond category #6; RM2 3.0 / RM-ASTDiff upgrade.
>
> — `2026-04-22_pre-execution-sequence.txt:112`

> Full detector-diff between the two versions on the Schesch full set is out of scope; the data above is the F-harness byproduct.
>
> — `2026-05-06_pre-rm2-vs-rm3-differences.txt:159`

### <a id="d-010"></a>D-010 — Drop taint analysis from the plan until it is raised again

`2026-04-22` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: ali

**Decision.** Taint analysis is omitted from the plan-triad sequence entirely and removed from the stage list, per Ali's decision of 2026-04-21; it is revisited only if he raises it again.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Source.** `preA:pre-execution-sequence-01` · Artifacts: `docs/plans/execution-sequence.md`

> Taint analysis — per user decision 2026-04-21, omit until next mention. Dropped from sequence.
>
> — `2026-04-22_pre-execution-sequence.txt:21`

### <a id="d-011"></a>D-011 — Leave the merger slot empty and the dispatcher diamond undrawn until a second merger

`2026-04-22` · **superseded** · `[recon]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** In the minimal viable composition, RM 2.0's output bypasses the merger entirely: it does not gate which merger runs but flows forward as metadata into post-merge Joern analysis. The `yes → [refactoring-aware merger]` slot in the target pipeline stays empty and the dispatcher diamond is deliberately omitted from the diagram; the diamond is drawn only once a second merger is empirically justified.

**Why.** The diamond has only one destination, so drawing it would be cosmetic; an empty slot in the diagram is not a bug but the design honestly reflecting where evidence has not yet justified added complexity.

**Status.** superseded. S12 (2026-07-26): overtaken — R4b subsequently built the real dispatcher (the 4-backend cluster-keyed map, backends-routing D-049), which the evidence then collapsed to NONE→git/else→Mergiraf (D-076); RM2 output does gate the merge step in the shipped driver. The aspirational diagram in initial architecture.md meanwhile still shows its own decision diamond (:12) and is superseded as a description of reality by the as-built sq.md ruling. Cross-cutting superseders, so superseded_by stays null.

**Source.** `preA:pre-tool-evaluation-findings-08`, `preB:pre-tool-evaluation-findings-10` · Artifacts: `semantic_merge_driver/initial architecture.md`

> An empty slot in the diagram is not a bug — it's the design honestly reflecting where evidence has not yet justified added complexity.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:215`

> The dispatcher diamond from the target architecture is **deliberately absent** because it only has one destination.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:251`

### <a id="d-012"></a>D-012 — Redefine case-based dispatch as multi-layer, not merge-backend routing

`2026-04-22` · **superseded** · `[recon]` · corroboration: both · confidence: medium · actors: claude

**Decision.** The pre-2026-04-21 framing that treated thesis contribution #2 (case-based dispatch) as primarily about routing between merge backends is withdrawn as too narrow. Dispatch is instead defined at every abstraction layer where a classification informs a downstream decision: pre-merge (RM 2.0 classification), merge (currently case-agnostic), post-merge (Joern strategies enabled, parameterised or selected per RM classification). Corollary: RM 2.0 is not vestigial metadata pending RefMerge but the pre-merge abstraction-reduction layer in its own right.

**Why.** Contribution #2 is enacted at the analysis layer even when the merge layer has only one destination; and without RM 2.0 there is no *case* to dispatch on at the pre-merge abstraction level.

**Status.** superseded. S12 (2026-07-26): narrowed again by the later reframe this entry's own note anticipated — the driver was restated as a verification gate (adopted, 2026-05-11), and the post-flip reality (routing collapsed, value in the detection layer) matches that framing, not the multi-layer-dispatch one. Superseded by [D-018](#d-018) — The driver is a proof-of-concept verification gate, not a smarter merger or a service. Supersedes: *earlier framing of case-based dispatch as merge-backend routing (framing prior to 2026-04-21)*.

**Source.** `preA:pre-tool-evaluation-findings-09`

> An earlier framing (prior to 2026-04-21) treated "case-based dispatch" as primarily about routing between merge backends. That framing is too narrow.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:303`

> The corollary: RM 2.0 is **not** vestigial metadata pending RefMerge. It is the pre-merge abstraction-reduction layer of the thesis, with or without RefMerge.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:311`

### <a id="d-013"></a>D-013 — Pre-agree a cut list if under two weeks remain before the deadline

`2026-04-22` · **open** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** If under two weeks of runway remain, the sequence is cut to α + β + γ + M1 + R1 + R3 + M5 only, skipping full-scale M4.

**Why.** The sequence as written assumes roughly 3–4 weeks of available time, so the thesis deadline is an open dependency that would force a reduced scope.

**Status.** open. The runway question is never resolved anywhere in this slice — no source records which branch was taken. Check STATUS.md and the git log for whether M4 ran at full scale, and docs/plans/execution-sequence.md §5 for any later amendment.

**Source.** `preA:pre-execution-sequence-25` · Artifacts: `docs/plans/execution-sequence.md §5`

> 1. Thesis deadline — this sequence assumes ~3-4 weeks available. If <2 weeks, cut to α + β + γ + M1 + R1 + R3 + M5 only; skip M4 full-scale.
>
> — `2026-04-22_pre-execution-sequence.txt:143`

### <a id="d-014"></a>D-014 — Integrate RM 2.0 only if the Method Rename Joern strategy is built with it

`2026-04-22` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: claude

**Decision.** RefactoringMiner 2.0 integration into `semantic_merge_driver` is conditional on committing to build the Method Rename Joern strategy (category #6) alongside it, in the same unit of work.

**Why.** RM 2.0 alone yields only scenario tagging (D5) plus future-proofing — a weak case for adding a JVM dependency, integration surface and failure modes. RM 2.0 together with the Method Rename strategy raises category coverage 2/7 → 3/7 and unlocks uses D1–D6, a strong case. The strategy alone (pure CPG, no RM) detects symptom without intent and is less reliable. Further RM-cluster-driven strategies are then built incrementally, only after Method Rename has validated the pattern.

**Status.** adopted. S12 (2026-07-26): the condition was honoured — RM2 integration came with the category-#6 lane in the same arc: strategies/rm2_strategies/rename_conflict.py (RM2RenameConflictStrategy) exists and is the family the record's detection mass lives in.

**Source.** `preA:pre-tool-evaluation-findings-04`, `preA:pre-tool-evaluation-findings-14` · Artifacts: `docs/plans/rm2-integration.md`, `semantic_merge_driver/`

> Integrate RM 2.0 **only if** you commit to building the **Method Rename Joern strategy (category #6)** alongside it.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:159`

> RM 2.0 alone (no new strategy) → functional payoff is scenario tagging (D5) and future-proofing → weak case.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:161`

### <a id="d-015"></a>D-015 — Add Weave as a sixth tool; no fork, no exclusive backend, MCP out of scope

`2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** Weave is added as a sixth tool in `merge-tool-comparison/` alongside Mergiraf rather than stopping the framework at five. Of the three tools in the RefactoringMiner-output-mapping PDF not yet in project plans, SemanticMerge is skipped as proprietary and RePatch as wrong-dataset; only Weave is taken forward. Explicit non-goals: reimplementing or forking Weave, adopting Weave as the exclusive merge backend, expanding Joern strategy coverage, and integrating Weave's `weave-mcp` server into any runtime pipeline — MCP gets only a ~5-line epilogue in ARCHITECTURE.md, and any AI-agent empirical question becomes a separate plan.

**Why.** Mergiraf and Weave occupy different granularity slots (entity vs AST-subtree), which is exactly the axis thesis contribution #2 is about: integrating only Mergiraf leaves the PDF's taxonomy claim untested, whereas integrating both lets it be confirmed or refuted — either result is publishable, a single-tool integration is not. The plan serves contribution (2) by adding a distinct granularity on the merge axis, leaving contribution (1) Joern/CPG detection untouched. MCP is adjacent rather than core because the thesis is about composing merge and analysis tools, not multi-agent coordination, so its value is positioning rather than extra experiments.

**Status.** adopted. S12 (2026-07-26): enacted within its non-goals — Weave is the sixth comparator tool (src/tools/weave.py + config/tools.yaml, e334cb3) and a selectable driver backend, never forked, never exclusive, MCP untouched; SemanticMerge and RePatch appear nowhere.

**Source.** `preA:pre-weave-integration-10`, `preA:pre-weave-integration-09`, `preA:pre-weave-integration-11`, `preA:pre-weave-integration-12` · Artifacts: `merge-tool-comparison/`, `ARCHITECTURE.md`, `~/Downloads/RefactoringMiner Output Merge Tool Mapping.pdf`

> Either result is publishable; a single-tool integration is not.
>
> — `2026-04-25_pre-weave-integration.txt:264`

> Because the thesis is about composing merge and analysis tools, not about multi-agent coordination.
>
> — `2026-04-25_pre-weave-integration.txt:272`

> **SemanticMerge** (proprietary — skip), **RePatch** (wrong dataset — skip)
>
> — `2026-04-25_pre-weave-integration.txt:51`

### <a id="d-016"></a>D-016 — Define four scope tiers A–D for the RM2 cycle, lean Tier D, hard floor Tier A

`2026-05-05` · **superseded** · `[recon]` · corroboration: mixed · confidence: medium · actors: ali

**Decision.** Enumerate exactly four stopping points for the RM2 integration cycle — A: MVP (R0+M0 → R4a‖M6-lite → R4b, ~3d); B: A+R3 (~4d); C: B+R1→R2 (~5d); D: C + one specialized routing elif + M1–M5 + 6-validate (~7–9d) — each of which ships the named phases, declares the cycle done and defers the rest. Tier D is the current lean with Tier C as fall-back if the calendar tightens, and Tier A is the hard floor: no smaller scope is an acceptable stopping point.

**Why.** The plan files define every phase and execution-sequence.md orders them, but neither pins how much of the integration ships in this cycle; each tier is framed as a coherent stopping point. Tier D has the highest defensibility for thesis purposes because it ships the complete contribution-#2 story — case-based dispatch with evidence backing one specific routing claim — rather than stopping at a built-but-unvalidated mechanism. Below Tier A the cycle has shipped no end-to-end deliverable and is not a coherent stopping point.

**Status.** superseded. Superseded by [D-062](#d-062) — Ship backends-only for the 2026-05-18 cycle: four selectable backends, no routing elif.

**Cross-theme.** *superseded-by* → [D-062](#d-062) — Located via the mirror flag backends-routing:6: the 2026-05-18 backends-only cycle explicitly superseded the tier menu (and was itself later superseded by the two-phase reframe, which the chain in backends-routing records). The null superseded_by was filled.

**Source.** `preA:pre-scope-tier-options-01`, `preA:pre-scope-tier-options-02`, `preA:pre-scope-tier-options-03` · Artifacts: `docs/plans/scope-tier-options.md`, `docs/plans/execution-sequence.md`

> Each tier is a coherent stopping point: ship the named phases, declare the cycle done, defer the rest to a future cycle.
>
> — `2026-05-05_pre-scope-tier-options.txt:58`

> **Most likely: Tier D — Full single-elif.** Highest defensibility for thesis purposes;
>
> — `2026-05-05_pre-scope-tier-options.txt:135`

> **Hard floor:** Tier A — the MVP. Below this the cycle has shipped no end-to-end deliverable and isn't a coherent stopping point.
>
> — `2026-05-05_pre-scope-tier-options.txt:139`

### <a id="d-017"></a>D-017 — Defer the scope-tier pin until R0 and M0 recon land

`2026-05-05` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: ali

*Actors note: The two plan-document sources attribute the deferral to Ali; the commit that recorded it carries no attribution. Recorded as ali on the strength of the plan text.*

**Decision.** The tier decision is deferred until R0 + M0 reconnaissance has landed and per-phase costs are clearer; R0 and M0 proceed without waiting for it. The three open tier questions — whether recon blockers force a downgrade, which routing elif lands first if both are supported, and whether to downgrade to Tier C if R2 supports neither routing claim — are left unresolved to be settled as evidence accumulates.

**Why.** R0 and M0 outputs (RM2 version pin, JSON schema, F-harness recall delta, Mergiraf version pin, Path A vs B) are useful at every tier and so do not block on the pin, and the specific per-phase costs are only clear afterwards. On the open questions the instruction is explicit: resolve as evidence accumulates, do not pre-commit.

**Status.** adopted.

**Source.** `preA:pre-commits-20`, `preA:pre-scope-tier-options-06`, `preA:pre-scope-tier-options-08` · Artifacts: `5ad4822`, `docs/plans/scope-tier-options.md`

> The pin happens after **R0 + M0 recon** lands and the specific per-phase costs are clearer.
>
> — `2026-05-05_pre-scope-tier-options.txt:143`

> R0 + M0 do not block on this decision — their outputs (RM2 version pin, JSON schema, F-harness recall delta, Mergiraf version pin, Path A vs B for Mergiraf) are useful at every tier.
>
> — `2026-05-05_pre-scope-tier-options.txt:145`

> Resolve these as evidence accumulates; do not pre-commit.
>
> — `2026-05-05_pre-scope-tier-options.txt:164`

### <a id="d-018"></a>D-018 — The driver is a proof-of-concept verification gate, not a smarter merger or a service

`2026-05-11 → 2026-07-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Sources disagree: the 2026-05-11 commit and the 2026-07-18 doc audit carry no attribution, while the June reframing and the AWS scoping are Claude's. Recorded as claude because the reframing argument is his throughout; the documents that record it do not attribute.*

**Decision.** The driver's architecture is stated as commodity text merge (Mergiraf backbone) plus a differential verification layer plus a fail-closed gate — a semantic-conflict detection layer downstream of Mergiraf — dropping the "intelligence in the middle". Success on the constructive side is defined as demonstrating a mechanism: extending Git's two outcomes (clean / textual conflict) with a third, "semantic conflict", surfaced via exit-1, with the demonstrated contribution stated as the NONE→git fast-path plus the verification layer and explicitly not quality-improving routing. The docs disclaim industry-grade ambition: the deliverable is a proof-of-concept to prove or disprove the composition hypothesis, and running the driver live as a CI/PR merge gate is a separate productionization track and Future Work — AWS use is scoped to speeding up and legitimising the evaluation only.

**Why.** Mergiraf's captured outcomes on n=5971 (57.9% tests passed, 5.6% tests failed, 36.5% merge failed) give a 5.6% silent-error rate, which justifies a semantic-conflict detection layer downstream of Mergiraf. The evidence then hollowed out the middle layer twice — routing collapsed to NONE→git, else→Mergiraf — so the driver's value is measured entirely by R1/R2, which the harness measures. Since no tool beats Mergiraf, the aim that a composed pipeline improves merging over any single tool cannot be shown, so the claim narrows to the mechanism and the verification layer. And the docs frame the driver as a research instrument, so a live merge gate would be a heavier, separate project.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-074](#d-074), [D-075](#d-075), [D-076](#d-076) — The #27/#28 refutations and the router collapse the reframe rests on.

**Source.** `preA:pre-commits-29`, `a:bfc672b4-23`, `a:dc3bc182-sub-sub-agent-a74c7a-04`, `a:dc3bc182-sub-sub-agent-a74c7a-09`, `a:fb0fa5c5-09` · Artifacts: `c1034c0`, `auto_backend._route()`, `THREATS_TO_VALIDITY.md`, `STATUS.md`, `README.md`, `ARCHITECTURE.md`

> The driver's identity shifts from "a smarter merger" to "a verifier that sits on top of any merger"
>
> — `2026-06-11_bfc672b4.txt:475`

> THREATS states this outright: "the driver's demonstrated contribution is the NONE→git fast-path + verification layer, **not** quality-improving routing."
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:54`

> heavier, and the docs frame the driver as a *research instrument*, so that's Future Work, not thesis-core.
>
> — `2026-06-24_fb0fa5c5.txt:441`

### <a id="d-019"></a>D-019 — Keep mergiraf_plus post-processing out of scope; P5 stays optional

`2026-05-11 → 2026-07-03` · **adopted** · `[mixed]` · corroboration: both · confidence: medium · actors: claude

*Actors note: The 2026-05-11 recon exclusion carries no attribution; the 2026-07-03 optional-P5 position is Claude's. Recorded as claude for the position that governs, with the earlier source unattributed.*

**Decision.** The `mergiraf_plus` variant (Mergiraf output post-processed with the Plume-lib merging pipeline) is out of scope for the integration cycle and flagged for a future "post-processing" track, despite upstream showing 57.9%→60.6% Tests_passed and 36.5%→33.8% Merge_failed. In the endgame it remains optional as P5: implement `mergiraf_plus` and run only the cheap stage-1 bare-level check, escalating to a ~12 h driver-level AWS arm only if stage 1's numbers are striking.

**Why.** No reason is recorded for the 2026-05-11 exclusion beyond the scope call itself. In 2026-07 the argument given is that the thesis stands complete without it and the Schesch-table evidence alone is citable as Future Work; the honest ORT pre-pass also raises a real design question, since Schesch's number is whole-merge-level while the driver is file-level and uses git merge-file, which is not ORT.

**Status.** adopted. S12 (2026-07-26): the scoping held — no mergiraf_plus adapter exists (src/tools/ has exactly git_merge_file/jdime/mastery/mergiraf/spork/weave), no stage-1 numbers were ever produced, and P5 was never exercised.

**Source.** `preA:pre-mergiraf-integration-recon-12`, `a:fb0fa5c5-48` · Artifacts: `src/scripts/merge_tools/mergiraf_plus.sh`

> Out of scope this cycle but worth flagging in a future "post-processing" track.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:191`

> **My honest take:** it's genuinely optional. The thesis stands complete without it; the Schesch-table evidence alone is citable as Future Work
>
> — `2026-06-24_fb0fa5c5.txt:2270`

### <a id="d-020"></a>D-020 — Defer the comparator closure ladder: 3a rejected on cost, 3h/3i and Tiers D–F deferred

`2026-05-14 → 2026-05-16` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: the 3b/3h/3i deferral is recorded as 'per user direction' (Ali), one tier plan attributes its deferral list to Claude, and three carry no attribution. Recorded as joint because Claude drafted the option ladder and Ali picked what was deferred.*

**Decision.** Options 3b (AST-aware normalize), 3h (multi-criteria reporting) and 3i (upstream Mergiraf citation) are deferred out of M3.5 to a post-tool-integration TODO tracked in the plans, with 3h and 3i split into separate plans; test-suite ground truth (3a) is rejected for now. The successive comparator tiers are named as the deferred routes to full closure of ISSUES.md #2 rather than started: Tier D's broader transforms, then Tier E (`+`/`*` same-op strip with type inference, long-array whitespace normalisation, hex literal case), then Tier F for the residual categories declared out of Tier E scope — multi-declarator split, FQN outside `java.lang`, numeric underscore strip and redundant `abstract` on an interface — with neither Tier F nor 3a in scope at all.

**Why.** 3i is doc-only and can land any time; 3b is the principled fix and 3h is additive on top of it, only becoming informative once 3b adds the AST-equivalent column; all three become more valuable once the full tool comparison ships so the headline can be reported under multiple criteria at once. 3a is days of build-infra and far larger, rejected per the §3 cost analysis in mergiraf-integration.md. The residual Tier F categories need non-trivial AST rewriting with ambiguous direction (multi-declarator), resolution against the active import set (FQN) or modifier-list editing (redundant `abstract`), and the numeric underscore strip — recoverable with a small text-level transform — is deferred for scope discipline. The 3b/3h/3i deferral was per Ali's direction of 2026-05-14.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-253](#d-253), [D-250](#d-250), [D-382](#d-382) — The ISSUES #2 closure arc and the interim-numbers publication the ladder existed to serve.

**Source.** `preA:pre-commits-64`, `preA:pre-comparator-3b-ast-normalize-19`, `preA:pre-comparator-3b-ast-normalize-28`, `preA:pre-comparator-3d-extended-ast-transforms-23`, `preA:pre-comparator-3e-tier-e-transforms-05`, `preA:pre-stage-gamma-fp-diagnostic-25` · Artifacts: `caf33e2`, `docs/plans/mergiraf-integration.md`, `docs/plans/comparator-3b-ast-normalize.md`, `docs/plans/comparator-3e-tier-e-transforms.md`, `merge-tool-comparison/ISSUES.md #2`

> **Option 3a** (test-suite ground truth). Far larger; rejected per §3 cost analysis in `mergiraf-integration.md`.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:413`

> Recoverable with a small text-level transform; deferred for scope discipline.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:64`

> Both remain deferred. The post-3b Tier C numbers are committed in `reports/results.csv` as the current honest interim state.
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:280`

### <a id="d-021"></a>D-021 — Driver is the primary deliverable; comparator tracks its backends and must not touch it

`2026-05-14 → 2026-05-20` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: Two sources attribute the boundary to Ali (the standing rule and the R1/R2 fence were his instructions); the plan-sourced 3b constraint carries no attribution. Recorded as ali rather than unclear because the standing rule is quoted in his words.*

**Decision.** Standing rule recorded in CLAUDE.md and noted in STATUS.md: the empirical merge-tool comparator and the semantic merge driver focus on the same tool set, with the driver as the primary deliverable — the comparison exists to justify the driver's routing. The boundary is enforced in both directions: comparator-side work must not touch driver runtime (the 3b AST normalize is comparator-only, adds no tree_sitter dependency to semantic_merge_driver, and never becomes a merge strategy or runs inside the driver; the R1→R2 work touches only merge-tool-comparison/, leaving the driver runtime, auto_backend.py and the merge backends alone), and driver-side stages must not modify merge-tool-comparison runtime code or published report numbers.

**Why.** Ali's scope steer was that the comparator and the driver should focus on the same tools with the driver as the main focus; the restatement Claude recorded and Ali accepted was that the comparator should benchmark the driver's backends because the driver is the primary deliverable. On the other side, 3b is comparator-only so the driver's existing fail-closed strategies and backend-dispatch logic are unaffected. No reason is recorded for the R1/R2 confinement beyond the instruction itself.

**Status.** adopted.

**Source.** `a:e1df1610-05`, `a:20b53f98-02`, `preA:pre-comparator-3b-ast-normalize-18`, `preB:pre-execution-sequence-23` · Artifacts: `CLAUDE.md`, `STATUS.md`, `merge-tool-comparison/`, `semantic_merge_driver/`

> note that merge tool comparator and semantic merge drive should focus on same tool. Main focus is merge driver
>
> — `2026-05-20_e1df1610.txt:578`

> AST normalize does NOT become a strategy / does NOT run inside the driver.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:414`

> - Empirical side only (merge-tool-comparison/). Do NOT touch
>
> — `2026-05-18_20b53f98.txt:71`

### <a id="d-022"></a>D-022 — Bound the empirical claim: file-level tagging only, routing soundness and #26 as limits

`2026-05-18 → 2026-07-03` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: the file-level scope cut is recorded as joint and explicitly 'your call' (Ali's), while the delineation of the end-to-end claim and the cite-as-limitation calls are Claude's. Recorded as joint.*

**Decision.** R1's tagger extracts only base→ours and base→theirs at file level; the resolution axis and project-level extraction are dropped, which removes the planned file-vs-project recall-delta finding from R2. What "tested end to end" covers is delineated accordingly: cluster classification of the 50 real scenarios is done via the tagger, but AutoBackend *routing* over those 50 is verified only on synthetic fixtures, with real-data routing soundness (S3/W3, Wilson CIs) deferred by design to Phase 2. The RM2 file-vs-project recall delta (#26) and the Phase-2b static-semantic-merge per-category oracle stay undone and are cited as documented limitations; neither blocks the defence.

**Why.** Only ours/theirs file-level is on the categorization path, and the expensive part of Path D is project-level (git-worktree over ~2 GB clones), so the single dispatch-faithful axis is the methodologically cleanest. Phase 2 routing soundness is deferred by design rather than missing by oversight — STATUS.md records that synthetic full-arm fixtures verify every cluster routes correctly while results.csv measures each tool run standalone, not the driver's decision, and THREATS flags real-data routing soundness as unmeasured. For the undone items: the base-rate finding gutted Phase-2b's urgency, since #3 conflicts occur ~never in the wild so even a perfect #3 detector would have caught 0 additional real failures; and post-flip a misclassification only flips git↔Mergiraf, both of which P2 measured, collapsing #26's misrouting cost to one sentence of methodological honesty.

**Status.** adopted. Supersedes: *rm2-integration.md R1 spec of 3 RM2 runs per scenario (ours, theirs, resolution)*.

**Cross-theme.** *depends-on* → [D-404](#d-404), [D-127](#d-127) — The base-rate finding (category #3 conflicts essentially absent in the wild) is owned by these.

**Source.** `a:20b53f98-09`, `a:e1df1610-02`, `a:fb0fa5c5-42` · Artifacts: `merge-tool-comparison/tools/rm2_tag.py`, `docs/plans/rm2-integration-recon.md`, `STATUS.md`, `THREATS_TO_VALIDITY.md`, `ISSUES.md #26`

> The scope decision to drop `resolution`+project-level (your call, correctly flagged at the time) kills it
>
> — `2026-05-18_20b53f98.txt:253`

> Phase 2 routing-soundness is **deferred by design**, not missing by oversight.
>
> — `2026-05-20_e1df1610.txt:77`

> the base-rate finding gutted its urgency — since #3 conflicts occur ~never in the wild, even a *perfect* #3 detector would have caught 0 additional real failures in our corpus.
>
> — `2026-06-24_fb0fa5c5.txt:2284`

### <a id="d-023"></a>D-023 — Skip the shared-CPG rework after the pilot came in far under the abort threshold

`2026-06-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Because the pilot measured a 34 s/merge median against a 1200 s G0 abort threshold with 0/64 UNANALYZABLE files, the shared-CPG rework planned as a feasibility fallback is not needed for Stage C, which is projected at ~3–4 h.

**Why.** Measured runtime and analyzability made the plan's feared 12–30 h compute cost wrong, so the fallback's motivating risk was empirically absent.

**Status.** adopted.

**Cross-theme.** *declines* ← [D-307](#d-307) — see the note there

**Source.** `a:bfc672b4-01` · Artifacts: `reports_detection/pilot/FINDINGS.md`

> The plan's fear of 12–30 h compute for the full evaluation was wrong — Stage C will take ~3–4 h. No shared-CPG rework needed.
>
> — `2026-06-11_bfc672b4.txt:101`

### <a id="d-024"></a>D-024 — Formally descope IntelliMerge, GumTree and SafeMerge/Z3 as evidence-based removals

`2026-06-11 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

*Actors note: The 2026-06 and 2026-06-24 recommendations are Claude's; the 2026-07-18 audit source reports the descope as done without attribution. Recorded as claude, noting the record explicitly reserves the revision of initial architecture.md to Ali.*

**Decision.** The unbuilt half of the target pipeline — IntelliMerge-class refactoring-aware/structured specialist backends, GumTree edit-script overlap, SafeMerge/Z3 verification — is formally descoped to Future Work rather than left as an implied promise, with a 'target vs delivered' table in ARCHITECTURE.md or the thesis naming each dropped component and its one-line rationale. Claude did not edit `initial architecture.md`; revising it is Ali's call, recommended post-Stage-C as an "evolved by measurement" narrative with each removal citing its refutation.

**Why.** Specialist arms were refuted, IntelliMerge was contraindicated in the recon, and category detectors are low-yield, so descoping is an evidence-based decision rather than an admission of incompleteness. The shipped pipeline is narrower but defensible; left undocumented the gap reads as an implied promise, whereas the table turns a perceived gap into a scoping decision. `initial architecture.md` is the authoritative target per CLAUDE.md, so Claude does not edit it.

**Status.** adopted.

**Source.** `a:bfc672b4-26`, `a:ce56e78d-04`, `a:dc3bc182-sub-sub-agent-a74c7a-03` · Artifacts: `ARCHITECTURE.md`, `semantic_merge_driver/initial architecture.md`, `STATUS.md`, `CLAUDE.md`

> says: don't build them — descoping is now an evidence-based decision, not an admission of incompleteness
>
> — `2026-06-11_bfc672b4.txt:486`

> The pipeline that ships is *narrower but defensible* — it just needs to be stated as a deliberate de-scope, not left as an implied promise.
>
> — `2026-06-24_ce56e78d.txt:29`

> GumTree and SafeMerge/Z3 were formally descoped to Future Work.
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:47`

### <a id="d-025"></a>D-025 — Fence each session's scope explicitly, with artifacts-only handoff between sessions

`2026-06-20 → 2026-07-17` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: three scopes were set by Ali in kickoff prompts and three were stated by Claude in-session as deliberate exclusions. Recorded as joint because the pattern is Ali fencing the session and Claude reporting and extending the fence, not one party alone.*

**Decision.** Every work session runs under an explicit scope with named exclusions and hands off to the next only through committed artifacts. Recorded instances: S1 builds the data pipeline and passes G0 but does not run the Phase-1 production labeling batch (S2's job); S3 Phase-2 consolidation is a fresh session on committed artifacts and is not started unprompted; the 2026-06-20 fold-back is limited to promoting hit_adjudications.md, recomputing R2 by label and updating STATUS/THREATS row 14 and ISSUES #29, excluding the post-fix detector run and the §4.7 miss list; the spec batch runs only over the 48 attributed derivation units in the four target categories, with no detector code and no held-out/eval-control access; D1 deliberately does not look at method arity or signatures (D2/S-D3) and does not touch existing lanes' guards, including the known Joern both-parents-guard self-defeat (S-D4); and the S-D5 battery exercises only the detection lanes via the driver's analyze() call shape, leaving the git-merge-driver entry point, backend routing, Spork/Weave backends, crash-fallback chain and plugin/config wiring to the optional S-D8 re-pricing.

**Why.** The scopes are argued from the protocol: the handoff is committed artifacts only, which keeps the derivation/held-out firewall intact; each excluded item is assigned to a named later session (arity to D2/S-D3, existing lanes to S-D4, whole-driver behaviour to the S-D8 re-pricing per plan §1) rather than dropped.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-209](#d-209) (see the reconciliation note there)

**Source.** `a:92a3e464-02`, `a:788e483b-10`, `a:0e14484d-06`, `a:f0d70a59-20`, `a:2e726dc0-05`, `a:506d875b-06` · Artifacts: `ISSUES #30`, `ISSUES #31`, `merge-tool-comparison/ISSUES.md`, `outputs/detector-cycle-plan.md`, `specs/raw_results.json`, `core/driver.py`

> Per the protocol that's a fresh session — the handoff is committed artifacts only, so it's ready whenever you want to start it. I won't kick it off unprompted.
>
> — `2026-07-09_788e483b.txt:351`

> Two deliberate non-overlaps with future sessions: D1 does not look at method arity or signatures (that's D2/S-D3), and it didn't touch the existing lanes' guards
>
> — `2026-07-16_f0d70a59.txt:184`

> deliberately out of this cycle's scope (plan §1)
>
> — `2026-07-16_2e726dc0.txt:247`

### <a id="d-026"></a>D-026 — Gate any SafeMerge/Z3 proof-of-concept behind the three higher-priority moves

`2026-06-24` · **superseded** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** A minimal SafeMerge/Z3 proof-of-concept on one category is to be considered only after the routing flip, the P2 closeout and the target-vs-delivered table are done.

**Why.** Its only value is letting the thesis show the verification arm was attempted rather than only specified, which does not outweigh the higher-priority moves.

**Status.** superseded. S12 (2026-07-26): no proof-of-concept was ever built (no Z3 artifact anywhere); SafeMerge/Z3 was formally descoped to Future Work by the adopted removal decision, which replaces this conditional. Superseded by [D-024](#d-024) — Formally descope IntelliMerge, GumTree and SafeMerge/Z3 as evidence-based removals.

**Source.** `a:ce56e78d-08`

> purely so the thesis can show the verification arm was attempted rather than only specified — but only if moves 1–3 are done first.
>
> — `2026-06-24_ce56e78d.txt:49`

### <a id="d-027"></a>D-027 — Sequence the endgame: P2 next, then P3 code, overnight compute, then P4 desk work

`2026-06-24 → 2026-07-02` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: the P2-next pick is recorded as joint (Claude ranked the gap, Ali said to plan for P2), the P3/P4 ordering is Claude's. Recorded as joint on that basis.*

**Decision.** The remaining roadmap is sequenced with P2 — the whole-driver end-to-end run across auto/mergiraf/git on the cost model — as the immediate next work item, with P3+P6 issue-closure and P4 reporting queued behind it. P3 and P4 are not run as two parallel sessions: P3's code lands first (cache-key fix → flip → tests → docs), the optional post-flip re-run is kicked off as unattended compute, and P4's reporting work is done during or after it.

**Why.** The three-outcome model is the thesis's central pitch and had never been scored end-to-end on a corpus; it reuses the P1 harness, so it is the highest-leverage remaining gap and gives the defence its missing second leg. P3 and P4 have no logical dependency either way, but both edit STATUS.md and ISSUES.md — trivial in one session, conflict-prone across parallel worktrees — so the natural parallelism is compute vs desk work, and for a half-day P3 the merge-the-docs tax would eat the saving.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-456](#d-456) (see the reconciliation note there)

**Source.** `b:fb0fa5c5-01`, `a:fb0fa5c5-30` · Artifacts: `outputs/project-review-future-directions-2026-06-10.md`, `STATUS.md`, `ISSUES.md`

> This is now the highest-leverage gap
>
> — `2026-06-24_fb0fa5c5.txt:36`

> **The natural parallelism isn't two sessions — it's compute vs. desk work:**
>
> — `2026-06-24_fb0fa5c5.txt:1541`

### <a id="d-028"></a>D-028 — Retire the SSM Dockerization and heavy oracle build

`2026-07-04` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The planned static-semantic-merge (SSM/s3m) Dockerization and heavy oracle build recorded in the old memory file is retired and will not be built.

**Why.** The dataset turned out to ship labels *and* source quadruples, so the heavy oracle build was never needed.

**Status.** adopted. Supersedes: *SSM-Dockerization plan recorded in the memory file*.

**Source.** `a:8740dbd3-09` · Artifacts: `research/outputs/Dockerfile.s3m`

> the SSM-Dockerization plan from the old memory is retired — the dataset turned out to ship labels *and* source quadruples, so the heavy oracle build was never needed.
>
> — `2026-07-03_8740dbd3.txt:416`

### <a id="d-029"></a>D-029 — Recode the taxonomy inductively; the four-family view is a hypothesis, not a frame

`2026-07-08 → 2026-07-10` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

*Actors note: Both primary sources are Ali's rulings; the cited also-source recording the four-family rejection is Claude's finding within that frame.*

**Decision.** The existing 7 categories (ResearchSummary.xml) remain the historical design taxonomy; the new codebook must carry an old→new mapping table, and the regrouped four-family view (state / control-flow / data-flow / name-binding, plus residual) is recorded only as a candidate structure to test against the data, not imposed on it. The Phase-2 codebook categorizes only the 60 attributed derivation units; the 105 escape-hatch units are reported as a first-class "not-cleanly-merge-attributable" stratum in FINDINGS, no categories may be invented for them, and the draft preamble must say so.

**Why.** The candidate structure is to be tested against the data rather than imposed on it, preserving the inductive character of the coding; and per the G1(iii) carry-forward ruling the escape-hatch units are not cleanly merge-attributable, so they are reported as their own stratum rather than forced into mechanism categories. When tested, the four-family view was rejected as the primary scheme because it would lump 75% of the data into one family.

**Status.** adopted.

**Cross-theme.** *duplicated by* ← [D-207](#d-207) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-109](#d-109) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-105](#d-105) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-452](#d-452) — other_uid a:6296f4f6-08 landed there: the keep-the-empirical-clusters ruling is the outcome of the hypothesis this entry set up.

**Source.** `a:cfe6365a-09`, `a:6296f4f6-03`, `a:6296f4f6-08` · Artifacts: `ResearchSummary.xml`, `reports_taxonomy/phase2/codebook_draft.md`

> candidate structure to test against the data, not to impose on it.
>
> — `2026-07-08_cfe6365a.txt:59`

> CARRY-FORWARD (G1 iii): the codebook covers the 60 attributed units;
>
> — `2026-07-10_6296f4f6.txt:39`

### <a id="d-030"></a>D-030 — Bound the open-source comparison to consultation; position the class as pre-compile

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

*Actors note: Sources disagree: the consult-don't-port bound is Ali's kickoff constraint, while the comparator findings and the pre-compile positioning are Claude's. Recorded as joint.*

**Decision.** The open-source practice comparison (Error Prone, PMD, SpotBugs, IntelliJ) is bounded to consulting docs and source: nothing is ported and no new runtime dependencies are added, and the review is timeboxed — a review pass, not a rewrite — with the comparators consulted and the parity/divergence outcomes recorded in the ISSUES #31 close-out. The comparison also fixes the detector's position: the stale-reference-to-removed-declaration defect class is framed as inherently merge-time/pre-compile, so the detector's niche is between merge and build.

**Why.** Parity findings justified existing choices: Error Prone leaves method references unmatched, matching our exclusion; PMD's UnusedPrivateMethod FP history shows arity-only matching fails under overloading, which the declared-arities union plus varargs guard address; SpotBugs analyses only compiled .class files, whose input has by construction passed javac name resolution, so a reference to a removed or renamed declaration is a compile error that can never reach its analysis stage. Error Prone and SpotBugs both sit strictly after resolution/compilation, corroborating that stale-reference defects are a pre-compile, merge-time class no mainstream analyzer owns.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-464](#d-464) (see the reconciliation note there)

**Source.** `a:82dd479f-02`, `a:acf7e1d0-13`, `a:82dd479f-sub-sub-agent-aadfd1-03` · Artifacts: `ISSUES #31 close-out`, `https://spotbugs.readthedocs.io/en/stable/introduction.html`

> consult, don't port; no new runtime dependencies.
>
> — `2026-07-16_82dd479f.txt:41`

> Error Prone and SpotBugs sit strictly *after* resolution/compilation, so they corroborate that stale-reference defects are a pre-compile, merge-time class no mainstream analyzer owns
>
> — `2026-07-16_82dd479f_sub-agent-aadfd1.txt:62`

### <a id="d-031"></a>D-031 — Treat core/sq.md as the as-built architecture; audit from primary sources, not the README

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: the primary-sources-only instruction is Ali's in the sub-agent brief, the sq.md-is-authoritative determination is Claude's finding. Recorded as joint.*

**Decision.** Architecture audits of semantic_merge_driver/ read the primary sources directly — 'initial architecture.md', core/driver.py, core/backends/*, strategies/*, ResearchSummary.xml, core/sq.md — and must not rely on the top-level repo README as evidence for the pipeline design or implementation state. Where the two pipeline diagrams disagree, core/sq.md is taken as the accurate description of the system (Git → driver.py → AutoBackend default → RM2 classifier → Mergiraf → plugin loader → strategies → Joern → exit 0/1), and 'initial architecture.md' is treated as the target/aspirational design describing a system largely not built.

**Why.** sq.md documents the as-built flow while initial architecture.md describes the target; the two diagrams disagree and sq.md is the one that matches the code. No reason is recorded for excluding the README beyond the instruction itself.

**Status.** adopted.

**Source.** `a:dc3bc182-sub-agent-a7bb0f-01`, `a:dc3bc182-sub-agent-a7bb0f-03` · Artifacts: `core/sq.md`, `semantic_merge_driver/initial architecture.md`, `core/driver.py`, `core/backends/`, `strategies/`, `ResearchSummary.xml`

> Do NOT rely on the top-level repo README; go to primary sources:
>
> — `2026-07-18_dc3bc182_sub-agent-a7bb0f.txt:3`

> The two diagrams disagree, and sq.md is the accurate one.
>
> — `2026-07-18_dc3bc182_sub-agent-a7bb0f.txt:53`

### <a id="d-032"></a>D-032 — Green-light S-D7 and S-D8; the default-enabling decision stays with Ali

`2026-07-22` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** Both follow-on cycles are green-lit and their kickoff prompts instantiated verbatim in the ISSUES #31 close-out as paste-and-go prompts, inheriting the 732d8ff freeze and carrying the sharding and budget lessons: S-D7 (blend-safe Stage-C before/after) and S-D8 (whole-driver re-pricing with lanes ON). S-D8 delivers the cost table, blocked/broken decomposition and the detection-latency delta as a first-class result, but the decision whether to enable the experimental detectors by default is explicitly excluded from that session and reserved for Ali afterwards, weighing −205 cost against +8.3 s/file.

**Why.** The plan's §8 stubs anticipate exactly these two follow-ons, and committing the prompts makes them survive the session. The latency rise IS the enabling-decision price, so it must be measured; the enabling decision itself is Ali's to make with the numbers.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-077](#d-077) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-128](#d-128) (see the reconciliation note there)

**Source.** `a:2e726dc0-23`, `a:68c24033-16` · Artifacts: `ISSUES.md`, `outputs/detector-cycle-plan.md §8`, `merge-tool-comparison/reports_detectors/FINDINGS.md`

> Both green-lit. Recording the decision + instantiating the two kickoff prompts in the ISSUES close-out (the §8 stubs anticipate exactly this)
>
> — `2026-07-16_2e726dc0.txt:722`

> **Per the kickoff, the default-enabling decision itself is yours** — the numbers to weigh are −205 cost against +8.3 s/file. STOP.
>
> — `2026-07-22_68c24033.txt:293`


## Merge backends & routing

*80 primary source decisions → 45 entries; 0 not promoted (reasons in `docs/decision-record/entries/backends-routing.json`).*

### <a id="d-033"></a>D-033 — Prefer operation-based RefMerge over graph-based IntelliMerge as the refactoring-aware backend

`2026-04-16` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The pre-transcript architecture selected RefMerge's operation-based invert-merge-replay pipeline as the refactoring-aware merge backend, with IntelliMerge relegated to a comparison baseline only. This direction was later reverted (see [D-045](#d-045) and [D-073](#d-073)).

**Why.** A 2,001-scenario / 20-project study showed IntelliMerge resolved only 4% of refactoring conflicts and increased conflicting LOC in 30% of scenarios, while RefMerge nearly doubled the resolution rate, reduced false positives by 23% vs Git and eliminated false negatives.

**Status.** superseded. Superseded by [D-045](#d-045) — Do not integrate RefMerge until three empirical conditions hold.

**Source.** `preA:pre-architecture-refmerge-02` · Artifacts: `core/merge_backends.py`, `docs/historical/ARCHITECTURE-refmerge.md`

> **Prefer operation-based over graph-based merging.**
>
> — `2026-04-16_pre-architecture-refmerge.txt:37`

> RefMerge, using the operation-based paradigm, nearly doubled IntelliMerge's resolution rate (7% vs 4%), reduced false positives by 23% compared to Git, and completely eliminated false negatives.
>
> — `2026-04-16_pre-architecture-refmerge.txt:200`

### <a id="d-034"></a>D-034 — Choose Mergiraf as the structural merge engine and reject JDime/Spork as the standard backend

`2026-04-16` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Mergiraf (Rust, tree-sitter-backed) replaces the textual baseline as the standard structural merge backend; JDime and Spork are not used as the general structural engine. This choice held throughout: Mergiraf remained the default backend and, after the specialist arms were refuted, the only non-git target of the auto router.

**Why.** JDime and Spork are exclusively Java-engineered (JDime needs an extensible Java compiler, Spork depends on Spoon's Java-only AST), whereas Mergiraf is production-ready, needs no threshold tuning, understands Java commutativity (import/annotation ordering), and falls back to conflict markers when uncertain, giving negligible latency overhead as a drop-in Git merge driver.

**Status.** adopted.

**Source.** `preA:pre-architecture-refmerge-03` · Artifacts: `core/merge_backends.py`

> **Why Mergiraf instead of JDime/Spork:**
>
> — `2026-04-16_pre-architecture-refmerge.txt:202`

> JDime and Spork are strictly and exclusively engineered for the Java programming language.
>
> — `2026-04-16_pre-architecture-refmerge.txt:203`

### <a id="d-035"></a>D-035 — Introduce a MergeBackend ABC separate from MergeStrategy, with env-selected backends

`2026-04-16 → 2026-05-12` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: preB:pre-commits-22 attributes the Phase-6 split to ali; the other sources record no actor. Recorded as unclear because the ABC design itself is not attributed.*

**Decision.** Merge backends are pluggable behind a `MergeBackend` ABC in `core/backends/base.py`, kept deliberately separate from the existing `MergeStrategy` ABC, with `GitMergeFileBackend` retained as the baseline alongside `MergirafBackend`. Backends mutate `ours_path` in place, must NOT raise, and return a `MergeOutcome` of CLEAN/CONFLICT/CRASH; the driver selects one via the `SEMANTIC_MERGE_BACKEND` env var (validated against a `BACKENDS` dict, default `mergiraf` at M6-lite) and fails closed with exit 1 on CRASH. `SEMANTIC_MERGE_BACKEND=git` recovers the prior inline behaviour.

**Why.** Backends merge, strategies analyse — the two abstractions do different jobs, so they get separate ABCs. Keeping git merge-file as a retained backend makes the merge step configurable rather than hardcoded, so the prior behaviour stays one env-flip away.

**Status.** adopted.

**Source.** `preA:pre-architecture-refmerge-17`, `preA:pre-mergiraf-integration-20`, `preA:pre-commits-32`, `preB:pre-commits-41`, `preB:pre-commits-22` · Artifacts: `semantic_merge_driver/core/backends/base.py`, `semantic_merge_driver/core/backends/git_merge_file_backend.py`, `semantic_merge_driver/core/backends/mergiraf_backend.py`, `3fef834`, `core/driver.py`, `docs/plans/mergiraf-integration.md`

> `MergeBackend` ABC. Separate from existing `MergeStrategy` ABC: backends *merge*, strategies *analyse*.
>
> — `2026-04-21_pre-mergiraf-integration.txt:219`

> base.py            MergeBackend ABC + MergeOutcome enum (CLEAN/CONFLICT/CRASH).
>
> — `2026-04-15_pre-commits.txt:424`

>     """Baseline textual 3-way merge via git merge-file."""
>
> — `2026-04-16_pre-architecture-refmerge.txt:328`

### <a id="d-036"></a>D-036 — Route merges by RM-detected refactoring: refactoring-aware backend if detected, Mergiraf otherwise

`2026-04-16` · **superseded** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** The original MergeRouter selects the backend from RM-ASTDiff output: if any refactoring is detected on either branch, use the refactoring-aware backend (then RefMergeBackend); otherwise use MergirafBackend. This binary gate was later reframed into a cluster-and-language classifier (see [D-047](#d-047)).

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** superseded. Superseded by [D-047](#d-047) — Reframe R4 from a binary gate to a cluster-and-language classifier feeding 4-way dispatch.

**Source.** `preA:pre-architecture-refmerge-08` · Artifacts: `core/merge_router.py`

>     """Routes to RefMerge if refactorings detected, Mergiraf otherwise."""
>
> — `2026-04-16_pre-architecture-refmerge.txt:356`

> │ Refactoring detected?       │
>
> — `2026-04-16_pre-architecture-refmerge.txt:156`

### <a id="d-037"></a>D-037 — Every merge backend fails closed: subprocess failure rejects, never silently accepts

`2026-04-21 → 2026-05-12` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: preA:pre-spork-driver-integration-05 attributes the Spork instance to ali and preA:pre-commits-34 the encoding fix to claude; the general principle is unattributed across the other sources.*

**Decision.** Fail-closed semantics are preserved across all merge backends: a subprocess failure (CRASH/TIMEOUT/missing tool) in Mergiraf, Spork or Weave must surface as a rejectable outcome rather than a silent fall-through or a clean result, and Joern strategies still reject via exit 1 regardless of which backend produced the merged file. As part of this, `subprocess.run` in the backends uses `encoding="utf-8", errors="replace"` so non-UTF-8 output cannot raise an uncaught `UnicodeDecodeError`.

**Why.** Matches the β-stage fail-closed principle already applied at the strategy layer (tool-evaluation-findings.md §3) and set as the pattern in Mergiraf's Phase 6-lite; an unhandled decode error on non-UTF-8 subprocess output was identified as a real fail-open risk.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-078](#d-078) — other_uid preA:pre-architecture-refmerge-06 landed there: the strategy-layer fail-closed switch is the origin of the principle this entry extends to backends.

**Source.** `preA:pre-mergiraf-integration-22`, `preA:pre-spork-driver-integration-05`, `preA:pre-weave-integration-15`, `preA:pre-commits-34` · Artifacts: `semantic_merge_driver/core/backends/spork_backend.py`, `semantic_merge_driver/core/backends/`, `docs/plans/execution-sequence.md`, `3fef834`

> Preserve fail-closed semantics across both backends — subprocess failure in either backend → reject, don't silently accept.
>
> — `2026-04-21_pre-mergiraf-integration.txt:227`

> - **Fail-closed semantics.** Any Spork subprocess failure → reject, don't silently fall through. Aligns with the β-stage principle and the pattern set in the other backends.
>
> — `2026-04-25_pre-spork-driver-integration.txt:77`

> uncaught — was a real fail-open risk).
>
> — `2026-04-15_pre-commits.txt:451`

### <a id="d-038"></a>D-038 — Define seven RM2 clusters by 3-way merge difficulty, resolved by a fixed precedence order

`2026-04-22 → 2026-07-18` · **adopted** · `[mixed]` · corroboration: both · confidence: high · actors: unclear

*Actors note: a:dc3bc182-sub-agent-a7bb0f-05 attributes the taxonomy-separation note to claude; the pre-transcript cluster design is unattributed.*

**Decision.** The classifier's seven clusters (MIGRATE_DECL, INTRA_BODY, SYMBOL_CASCADE, CONTAINER_MOVE, HIERARCHY_RESHAPE, LOCAL_DECL_EDIT, NONE) group RM2 refactoring types by the kind of 3-way merge difficulty they create, not by lexical name similarity. When a merge yields several clusters, dispatch resolves deterministically by the order MIGRATE_DECL > INTRA_BODY > SYMBOL_CASCADE > CONTAINER_MOVE > HIERARCHY_RESHAPE > LOCAL_DECL_EDIT > NONE; compound RM2 types map to a frozenset of clusters and resolve to the highest-priority member. These clusters exist solely to drive backend routing and must not be conflated with the seven semantic-conflict categories in ResearchSummary.xml.

**Why.** What makes a refactoring hard for a line-based merger is precisely the question the composition pipeline's dispatch is meant to answer, so the grouping criterion must be merge difficulty; the precedence is ordered hardest-for-line-merge first, so the most difficult profile wins the dispatch. The two seven-member taxonomies are unrelated: clusters map RM2 refactoring-type display names to merge difficulty for backend selection, whereas the categories are conflict shapes detectors target.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-06`, `preA:pre-rm2-integration-07`, `a:dc3bc182-sub-agent-a7bb0f-05` · Artifacts: `semantic_merge_driver/core/refactoring_classifier.py`, `ResearchSummary.xml`

> which is precisely the question the composition pipeline's dispatch is meant to answer
>
> — `2026-04-22_pre-rm2-integration.txt:41`

> **Precedence on multi-cluster scenarios** (highest dispatch-priority first — hardest-for-line-merge first):
>
> — `2026-04-22_pre-rm2-integration.txt:61`

> These clusters drive **backend routing only** — they are unrelated to the 7 semantic-conflict categories in (d).
>
> — `2026-07-18_dc3bc182_sub-agent-a7bb0f.txt:68`

### <a id="d-039"></a>D-039 — Ship AutoBackend and flip the SEMANTIC_MERGE_BACKEND default from mergiraf to auto

`2026-04-22 → 2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** R4b wires the classifier into the driver, adds `AutoBackend` (name="auto") and flips `DEFAULT_BACKEND` from `mergiraf` to `auto`. AutoBackend classifies per merge, logs cluster / language / chosen backend on every invocation, and at that point dispatches every cluster to Mergiraf. The commit message must state honestly that `auto` is functionally identical to `mergiraf` until W5/S2 land.

**Why.** Auto mode is functionally equivalent to mergiraf mode at that point, but it exercises the classifier and logs a dispatch decision on every merge; having the dispatch infrastructure and per-merge logging in place makes W5/S2 pure additions and gives early classifier-correctness signal from production-style usage.

**Status.** adopted. Supersedes: *SEMANTIC_MERGE_BACKEND default of `mergiraf` set in Phase 6-lite (commit 3fef834)*.

**Cross-theme.** *depended on by* ← [D-238](#d-238) (see the reconciliation note there)

**Source.** `preA:pre-execution-sequence-15`, `preA:pre-rm2-integration-26`, `preA:pre-commits-45` · Artifacts: `semantic_merge_driver/core/backends/auto_backend.py`, `tests/test_auto_backend.py`, `tests/test_driver_dispatch.py`, `8fcc44e`, `core/driver.py`

> functionally equivalent to `mergiraf` mode, but with classifier exercised + dispatch decision logged on every merge
>
> — `2026-04-22_pre-execution-sequence.txt:99`

> until W5 / S2 land, `auto` mode is functionally identical to `mergiraf` (every cluster falls through). The mechanism is real plumbing + logging
>
> — `2026-04-22_pre-rm2-integration.txt:307`

### <a id="d-040"></a>D-040 — AutoBackend falls back to git-merge-file once on CRASH only, never on CONFLICT

`2026-04-22 → 2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: preB:pre-commits-50 attributes the CRASH-only rule to ali; the other two sources record no actor.*

**Decision.** AutoBackend wraps the classifier defensively, logs `language_of(ours_path)`, and on a CRASH outcome — and only CRASH — logs and retries exactly once via `GitMergeFileBackend`; a double CRASH propagates. CONFLICT never triggers fallback. `_route()`'s docstring additionally requires future elif arms to return pre-constructed backend instances held on `self` and never to construct backends inside `_route`.

**Why.** CONFLICT is a valid outcome with markers and does not indicate failure, so it must not trigger fallback. Backend constructors may touch Docker or the filesystem and can fail, so that work must happen in `__init__` to preserve AutoBackend.merge()'s must-not-raise contract.

**Status.** adopted.

**Source.** `preA:pre-execution-sequence-16`, `preB:pre-commits-50`, `preA:pre-commits-46` · Artifacts: `semantic_merge_driver/core/backends/auto_backend.py`, `8fcc44e`

> markers and does NOT trigger fallback) log and retry once via
>
> — `2026-04-15_pre-commits.txt:704`

> held on self, never construct backends inside _route — backend
>
> — `2026-04-15_pre-commits.txt:708`

> primary→Mergiraf, single-shot fallback to GitMergeFileBackend on CRASH
>
> — `2026-04-22_pre-execution-sequence.txt:99`

### <a id="d-041"></a>D-041 — Split routing into Phase-1 mechanism (no evidence gate) and deferred Phase-2 soundness

`2026-04-22 → 2026-05-19` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Routing is a two-phase deliverable. Phase 1 wires the routing elifs and verifies them end-to-end with synthetic fixtures for full arm coverage, carrying no evidence gate; Phase 2 validates soundness on real data with Wilson CIs (the S3 and W3 gates) and remains deferred. S2 and W5 are Phase-1 mechanism work; S3/S4 and W0–W4 are reclassified as Phase-2 soundness validation and are no longer preconditions. The Tier A–D menu, which conflated mechanism with evidence gates, becomes historical.

**Why.** The phase split is what made the routing cycle coherent: it let the mechanism ship and be synthetically verified end-to-end while the soundness question waited for real data and Wilson CIs. Phase 1 carries no evidence burden, so the Tier framing that bundled the two no longer applies.

**Status.** adopted. Supersedes: *stage-ε item 7 gating each routing elif on its own evidence (W3 / S3)*; [D-062](#d-062) — Ship backends-only for the 2026-05-18 cycle: four selectable backends, no routing elif.

**Cross-theme.** *depended on by* ← [D-245](#d-245) (see the reconciliation note there)

**Source.** `preA:pre-execution-sequence-21`, `preA:pre-scope-tier-options-12` · Artifacts: `docs/plans/rm2-integration.md §1.2`, `workspace/route_fixtures/`, `AutoBackend._route()`, `memory routing-two-phase`

> The phase split that made this coherent: S2/W5 = Phase-1 *mechanism* (no evidence gate); **S3/W3 decoupled** → Phase-2 *soundness* (real data + Wilson CIs), still deferred.
>
> — `2026-04-22_pre-execution-sequence.txt:110`

> Tier A–D menu conflated these; it is now historical.
>
> — `2026-05-05_pre-scope-tier-options.txt:24`

### <a id="d-042"></a>D-042 — Ship both S2 and W5 routing elifs together; the Tier-D pick rule is moot

`2026-04-22 → 2026-05-19` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Both the S2 (INTRA_BODY+Java→Spork) and W5 (MIGRATE_DECL→Weave) routing elifs are wired in AutoBackend._route() in the same Phase-1 cycle and synthetic-verified end-to-end, retiring the single-elif constraint and the S2-vs-W5 pick rule.

**Why.** Picking one was only ever an evidence-budget constraint, and Phase 1 carries no evidence burden, so both could ship together as mechanism.

**Status.** adopted. Supersedes: [D-057](#d-057) — Ship only one routing elif per cycle, chosen by an S2-vs-W5 pick rule.

**Cross-theme.** *depended on by* ← [D-245](#d-245) (see the reconciliation note there)

**Source.** `preA:pre-execution-sequence-22`, `preA:pre-scope-tier-options-13` · Artifacts: `AutoBackend._route()`, `docs/plans/rm2-integration.md §1.2`

> The "Tier-D pick rule" is moot — both elifs shipped together (picking one was only an evidence-budget constraint; Phase 1 carries none).
>
> — `2026-04-22_pre-execution-sequence.txt:110`

> was only ever an evidence-budget constraint and Phase 1 carries no evidence
>
> — `2026-05-05_pre-scope-tier-options.txt:26`

### <a id="d-043"></a>D-043 — Accept Mergiraf as default backend before empirical validation, with git one env-flip away

`2026-04-22 → 2026-05-12` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: preB:pre-commits-31 attributes the M6-lite escape clause to ali; the remaining sources record no actor.*

**Decision.** `core/driver.py` defaults `SEMANTIC_MERGE_BACKEND` to `mergiraf` at M6-lite, before Phase 4 evidence exists, with the commit message carrying an honest caveat; Phase 4 and Phase 6-validate are scheduled to retroactively confirm or refute the choice, and the default reverses if Phase 4 shows Mergiraf F1 below git-merge-file. M6-lite additionally carries an explicit escape clause: default to the `git` backend if M0/M2 surface Mergiraf stability or correctness concerns, and M3.5's trigger is broadened to enumerate all Phase-3 options needing code.

**Why.** Knowingly accepted cost: between M6-lite and M6-validate, runtime users are routed to Mergiraf without empirical backing. Chosen because the mechanism is the load-bearing contribution, the flag is one line while the validation gate is real, and M3.5 should close ISSUES.md #2 before M4 runs so the M4 numbers are credible; the git-merge-file backend stays one env-flip away, so the risk is bounded. The M3.5 broadening was needed because otherwise Phase 3's recommended 3e path would never get implemented and ISSUES.md #2 would stay `decided`.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-006](#d-006) — other_uid preA:pre-commits-28 is cited there: the M0 Path-A choice this default rests on.

**Cross-theme.** *depended on by* ← [D-238](#d-238) (see the reconciliation note there)

**Source.** `preA:pre-mergiraf-integration-19`, `preA:pre-commits-33`, `preA:pre-execution-sequence-14`, `preA:pre-commits-27`, `preB:pre-commits-31` · Artifacts: `semantic_merge_driver/core/driver.py`, `3fef834`, `ef4bb89`, `docs/plans/mergiraf-integration.md`

> between M6-lite landing and M6-validate confirming, runtime users of `semantic_merge_driver` are routed to Mergiraf without empirical backing
>
> — `2026-04-21_pre-mergiraf-integration.txt:236`

> git-merge-file backend is one env-flip away.
>
> — `2026-04-15_pre-commits.txt:467`

>   the evidence-vs-mechanism trade-off explicit, including the escape clause
>
> — `2026-04-15_pre-commits.txt:338`

### <a id="d-044"></a>D-044 — Invoke Mergiraf via a temp git repo and merge driver, mirroring upstream

`2026-04-22 → 2026-05-11` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Per the M0 recon deliverable, take Path A and integrate Mergiraf as a Git merge driver rather than calling the CLI directly: per merge, `git init` a temp dir, commit base, branch `theirs` and `ours`, configure `merge.mergiraf.driver "mergiraf merge --git %O %A %B -s %S -x %X -y %Y -p %P"`, append `mergiraf languages --gitattributes` to `.gitattributes`, run `git merge --no-edit theirs` and read the merged file from the working tree. Applies to both M6-lite's `MergirafBackend` and M1. Mergiraf 0.4.0 is pinned and upstream comparison numbers (n=5971: 3456 / 335 / 2180) captured for citation.

**Why.** The standalone three-file CLI surface is not fully documented and upstream ignores it entirely; the git-driver path is the documented, verified route and matches upstream's methodology exactly, even though it is more verbose.

**Status.** superseded. Superseded by [D-061](#d-061) — Use Mergiraf's standalone three-file CLI in Docker; temp-git-repo plumbing declared obsolete.

**Source.** `preA:pre-execution-sequence-11`, `preA:pre-mergiraf-integration-recon-08` · Artifacts: `docs/plans/mergiraf-integration-recon.md`, `src/scripts/merge_tools/mergiraf.sh`

> **Invocation strategy:** mirror upstream — set up a temp git repo per merge, configure mergiraf as the driver, run `git merge`. Resist the temptation to use the undocumented direct CLI.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:160`

> Path A recommendation; Mergiraf 0.4.0 pinned; invocation = Git merge driver, not direct CLI
>
> — `2026-04-22_pre-execution-sequence.txt:86`

### <a id="d-045"></a>D-045 — Do not integrate RefMerge until three empirical conditions hold

`2026-04-22` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: claude

**Decision.** RefMerge stays unbuilt and the refactoring branch of the architecture falls back to Mergiraf plus RM-2.0-informed Joern detection. RefMerge earns its slot only when all three hold: (1) refactoring-containing scenarios are ≥ ~15% of the dataset, (2) Mergiraf's failure rate on those scenarios is materially higher than on non-refactoring scenarios, and (3) RefMerge measurably resolves those failures without new FP inflation or crashes.

**Why.** The four arguments for adopting RefMerge (technical convenience, an empty architectural slot, literature headline numbers, symmetry) are all a priori, not evidence about this dataset. The thesis argues complexity should be added only where simpler tools demonstrably fall short; adopting a complex merger without empirical justification and having it silently corrupt merges would falsify the thesis in its own codebase. Detection via a Method Rename strategy plus exit 1 may already be sufficient for the stated aim.

**Status.** adopted. Supersedes: [D-033](#d-033) — Prefer operation-based RefMerge over graph-based IntelliMerge as the refactoring-aware backend.

**Source.** `preA:pre-tool-evaluation-findings-03` · Artifacts: `docs/historical/ARCHITECTURE-refmerge.md`, `docs/plans/tool-evaluation-findings.md`

> Adopting it without empirical justification — and having it silently corrupt merges on your dataset — quietly falsifies your own thesis in your own codebase.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:201`

> Until all three hold, RefMerge stays unbuilt.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:215`

### <a id="d-046"></a>D-046 — Use RM output for cost-aware strategy dispatch and refactoring-density tiering

`2026-04-22` · **abandoned** · `[recon]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** Use RM 2.0 output for cost-aware strategy dispatch (D1) and refactoring-density tiering (D3): when both branches show no refactorings, run only the Joern loop strategies; otherwise add MethodRename and RefactoringConflict. Tier analysis light/standard/escalate on refactoring count. In the accompanying type-cluster → strategy mapping (D4), `INTRA_BODY`, `LOCAL_DECL_EDIT` and `NONE` deliberately trigger no specific cross-cutting checks at this stage; only SYMBOL_CASCADE, MIGRATE_DECL, CONTAINER_MOVE and HIERARCHY_RESHAPE route to strategies.

**Why.** Non-refactoring scenarios skip JVM-heavy refactoring-aware analysis, scaling analysis cost to case complexity. The three excluded clusters are either intra-method — where Joern's existing strategies suffice if applicable — or trivial.

**Status.** abandoned. S12 (2026-07-26): never built — no RM-output-driven strategy selection or refactoring-density tiering exists anywhere; config/strategies.yaml is a static enablement list, and the driver reached its final form (post-flip router, flag-gated lanes) without it. Plan-era idea, dropped without a ruling.

**Cross-theme.** *depends-on* → **no counterpart entry exists** — Searched detection and infrastructure for a strategy-cost dispatch entry; none exists. Nearest cost decisions (infrastructure/[D-285](#d-285), infrastructure/[D-286](#d-286)) do not state RM-output-driven dispatch. Entry is sole owner; stays proposed.

**Source.** `preB:pre-tool-evaluation-findings-17`, `preA:pre-tool-evaluation-findings-11` · Artifacts: `docs/plans/rm2-integration.md §1.2`, `docs/plans/tool-evaluation-findings.md`

> Non-refactoring scenarios skip JVM-heavy refactoring-aware analysis.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:110`

> those merges are either intra-method (Joern's existing strategies suffice if applicable) or trivial.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:135`

### <a id="d-047"></a>D-047 — Reframe R4 from a binary gate to a cluster-and-language classifier feeding 4-way dispatch

`2026-04-25` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

**Decision.** R4 stops being a binary pipeline gate and becomes a cluster-and-language classifier feeding 4-way backend dispatch, with the estimate growing from 1-2d to 3-4d and diagrams, risks and rollback updated accordingly. In parallel, spork-driver-integration.md (phases S0–S4) promotes Spork from empirical-only to a MergeBackend, gated on ISSUES.md #2 resolution and language-axis dispatch evidence, growing the router to 4-backend dispatch with graceful degradation when sibling plans have not landed.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted. Supersedes: [D-036](#d-036) — Route merges by RM-detected refactoring: refactoring-aware backend if detected, Mergiraf otherwise.

**Source.** `preA:pre-commits-15`, `preA:pre-commits-14` · Artifacts: `3549314`, `docs/plans/rm2-integration.md`, `docs/plans/spork-driver-integration.md`

> rm2-integration.md: R4 reframed from binary gate to cluster-and-language
>
> — `2026-04-15_pre-commits.txt:158`

> from empirical-only to MergeBackend in semantic_merge_driver, gated on
>
> — `2026-04-15_pre-commits.txt:152`

### <a id="d-048"></a>D-048 — Split R4 into R4a classifier and R4b default flip to break the circular dispatch dependency

`2026-04-25` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** R4 is split: R4a ships `RefactoringClusterClassifier` and `language_detect.py` as standalone importable tested components with no router change, and R4b conditionally flips the `SEMANTIC_MERGE_BACKEND` default from `mergiraf` to `auto`, originally gated on R2 cluster signal + R4a + at least one of {W5, S2}. Ownership of `language_detect.py` transfers from S2 to R4a. The {W5,S2} gate on R4b was later removed (see [D-056](#d-056)).

**Why.** W5 and S2 each called rm2_classifier at runtime, but the classifier was introduced in R4 whose trigger required W5 or S2 to have landed — a cycle; the split makes the dependency graph acyclic, and single ownership of language_detect.py avoids duplication.

**Status.** superseded. Superseded by [D-056](#d-056) — MVP-first reframe: R4b ships the dispatch skeleton, evidence gates move to per-cluster elifs.

**Source.** `preA:pre-commits-16` · Artifacts: `416e020`, `docs/plans/rm2-integration.md`, `docs/plans/execution-sequence.md`

> W5 and S2 each called rm2_classifier at runtime, but the classifier was
>
> — `2026-04-15_pre-commits.txt:166`

> introduced in R4 — and R4's trigger required W5 or S2 to have landed.
>
> — `2026-04-15_pre-commits.txt:167`

### <a id="d-049"></a>D-049 — Adopt the 4-backend cluster-keyed dispatch map in AutoBackend._route()

`2026-04-25 → 2026-05-19` · **superseded** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: preA:pre-rm2-integration-08 attributes the NONE resolution to ali; the other sources record no actor for the map itself.*

**Decision.** AutoBackend._route() implements the §1.2 map: `MIGRATE_DECL` → Weave, `INTRA_BODY` + Java → Spork, `NONE` → git-merge-file, everything else (SYMBOL_CASCADE / CONTAINER_MOVE / HIERARCHY_RESHAPE / LOCAL_DECL_EDIT) → Mergiraf as default, and any routed-backend crash → git-merge-file. git-merge-file thereby plays two roles: the NONE-cluster target and the universal crash fallback. Verified end-to-end with 8 synthetic full-arm fixtures. Both specialist arms were later refuted and removed from the default (see [D-076](#d-076)).

**Why.** Weave owns MIGRATE_DECL because its entity-level matching handles methods extracted independently on different branches, where Mergiraf's AST-subtree approach generates spurious conflicts from spatial proximity; Mergiraf handles the other clusters natively via PCS triples. NONE routes to git-merge-file because no refactoring detected ⇒ use the fastest/simplest tool; the doc/code mismatch on NONE was resolved in favour of §1.2 under the standing rule that when doc and code disagree the mismatch is surfaced, asked about, and the decision recorded.

**Status.** superseded. Superseded by [D-076](#d-076) — Collapse the auto router to NONE→git, else→Mergiraf; routing benefit is the fast-path only. Supersedes: *auto mode routing all clusters to Mergiraf*; *R4b AutoBackend code routing NONE → Mergiraf, treating git-merge-file as crash-fallback only*.

**Source.** `preA:pre-weave-integration-08`, `preA:pre-execution-sequence-23`, `preA:pre-rm2-integration-08`, `preB:pre-scope-tier-options-11` · Artifacts: `semantic_merge_driver/core/backends/auto_backend.py`, `semantic_merge_driver/core/driver.py`, `workspace/route_fixtures/`, `docs/plans/rm2-integration.md §1.2`

> because its entity-level matching handles the common case (methods extracted independently on different branches)
>
> — `2026-04-25_pre-weave-integration.txt:64`

> **Resolution: §1.2 is authoritative — `NONE → git-merge-file`**
>
> — `2026-04-22_pre-rm2-integration.txt:57`

> full §1.2 map: `MIGRATE_DECL`→Weave, `INTRA_BODY`+Java→Spork, `NONE`→git, rest→Mergiraf, routed-crash→git
>
> — `2026-04-22_pre-execution-sequence.txt:110`

### <a id="d-050"></a>D-050 — Keep Spork Java-only and non-default; the Spoon constraint is the dispatch signal

`2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Spork is not made the default backend for Java: Mergiraf remains the Java default whenever the cluster is not `INTRA_BODY`, and Spork owns only the `INTRA_BODY`+Java branch. Spork is also not expanded beyond Java; the Java-only nature of Spoon is treated as the router's dispatch signal rather than a limitation to work around.

**Why.** On non-`INTRA_BODY` scenarios Mergiraf's multi-granularity hybrid (line → tree → markers) likely ties or beats Spork in practice at lower runtime cost, and Spork's claimed strength is sub-method granularity via Spoon, so outside that claim the simpler default applies. Spoon is Java-only by construction, so the constraint is the dispatch signal and the language axis is the thesis-relevant artefact.

**Status.** adopted.

**Source.** `preA:pre-spork-driver-integration-08`, `preA:pre-spork-driver-integration-09` · Artifacts: `docs/plans/spork-driver-integration.md`

> **Why not make Spork the default for all Java?** Because on non-`INTRA_BODY` scenarios, Mergiraf's multi-granularity hybrid (line → tree → markers) likely ties or beats Spork in practice, at lower runtime cost.
>
> — `2026-04-25_pre-spork-driver-integration.txt:234`

> - Not expanding Spork to non-Java. Spoon is Java-only by construction; this plan uses the constraint as the dispatch signal.
>
> — `2026-04-25_pre-spork-driver-integration.txt:93`

### <a id="d-051"></a>D-051 — Accept missed Spork dispatches from extension-only language detection

`2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Accept that extension-only language detection may miss polyglot files (e.g. `.gradle` containing Java, or `.kt`), costing some Spork dispatches; Mergiraf is the safe default for anything not `.java`.

**Why.** The worst case under extension-only detection is missing a Spork dispatch, not making an incorrect one — misclassified Kotlin simply falls to Mergiraf, which handles it.

**Status.** adopted.

**Source.** `preA:pre-spork-driver-integration-11` · Artifacts: `core/language_detect.py`

> Worst case is missing a Spork dispatch, not an incorrect one.
>
> — `2026-04-25_pre-spork-driver-integration.txt:204`

### <a id="d-052"></a>D-052 — Register SporkBackend in the BACKENDS dict, pin spork:0.5.0, drop conflict-count gating

`2026-04-25 → 2026-05-18` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** `SporkBackend` ships at `semantic_merge_driver/core/backends/spork_backend.py`, registered in `driver.py`'s `BACKENDS` dict rather than via a `core/driver.py` env-handler edit as §S2 sketched, with the image pinned to `merge-tools/spork:0.5.0` dual-tagged with the legacy `merge-tools/spork` tag. The backend reuses the empirical adapter's subprocess/Docker plumbing but returns `MergeBackendResult` (not `MergeResult`) and applies no conflict-count heuristic gating — conflict markers in output map directly to a CONFLICT outcome.

**Why.** R4b had already centralised backend selection into the BACKENDS dict, so registration there is the natural shape; the dual tag keeps the empirical adapter unaffected. No reason was recorded for dropping the conflict-count heuristic.

**Status.** adopted. Supersedes: *§S2 pseudocode's `core/driver.py` env-handler edit*.

**Source.** `preA:pre-spork-driver-integration-04`, `preA:pre-spork-driver-integration-17` · Artifacts: `semantic_merge_driver/core/backends/spork_backend.py`, `merge-tools/spork:0.5.0`

> `driver.py` `BACKENDS` dict (not via a `core/driver.py` env-handler edit as §S2's
>
> — `2026-04-25_pre-spork-driver-integration.txt:45`

>   - No conflict-count heuristic gating; conflict markers in output → CONFLICT outcome exactly as in
>
> — `2026-04-25_pre-spork-driver-integration.txt:123`

### <a id="d-053"></a>D-053 — Invoke weave-driver with the `-o` flagged form and key CONFLICT off exit code 1

`2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Pin the Weave invocation to the jj-style flagged form `weave-driver <base> <ours> <theirs> -o <output>` with a tempfile output path, never the positional form; W0 records the chosen form and reasoning and W1 asserts input files are unchanged after a run. The shipped `WeaveBackend` determines CONFLICT from return code 1 and preserves ours, rather than detecting `<<<<<<<` markers in the output.

**Why.** The positional form mutates `ours` in place by git convention and would pollute the workspace; empirically, on a whole-entity conflict the v0.3.2 positional form empties the ours file — silent data loss — which the `-o` form avoids. Marker detection was rejected because for whole-entity conflicts v0.3.2 emits a conflict summary on stdout and no git-style marker file at all, so Appendix B's regex assumption does not hold.

**Status.** adopted. Supersedes: *Appendix B's assumption that Weave conflicts always produce `^<<<<<<<` markers in the output file*.

**Source.** `preA:pre-weave-integration-03`, `preA:pre-weave-integration-04` · Artifacts: `docs/plans/weave-integration-recon.md`, `semantic_merge_driver/core/backends/weave_backend.py`

> v0.3.2's positional form **empties the ours file** (silent data loss)
>
> — `2026-04-25_pre-weave-integration.txt:38`

> the backend keys CONFLICT off rc 1, not marker presence, and preserves ours
>
> — `2026-04-25_pre-weave-integration.txt:43`

### <a id="d-054"></a>D-054 — Plan the Weave comparator adapter as a native (non-Docker) tool mirroring git_merge_file.py

`2026-04-25` · **superseded** · `[recon]` · corroboration: single-pass · confidence: medium · actors: unclear

**Decision.** The planned `merge-tool-comparison/src/tools/weave.py` adapter (~80 lines) mirrors `git_merge_file.py` rather than `spork.py`, using `run_native()` with `docker_image: null` in `config/tools.yaml`, writing output to a temp file via `-o` and counting `^<<<<<<<` markers.

**Why.** Weave is a native Rust binary, so no Docker layer is needed.

**Status.** superseded. Superseded by [D-062](#d-062) — Ship backends-only for the 2026-05-18 cycle: four selectable backends, no routing elif.

**Cross-theme.** *superseded-by* → [D-290](#d-290) — Mirror of infrastructure:0. The entry's in-theme superseded_by ([D-062](#d-062)) is kept; the Dockerization decision that concretely overrode the plan is infrastructure/[D-290](#d-290). Both rendered.

**Source.** `preA:pre-weave-integration-02` · Artifacts: `merge-tool-comparison/src/tools/weave.py`, `merge-tool-comparison/config/tools.yaml`

> Weave is native Rust; no Docker.
>
> — `2026-04-25_pre-weave-integration.txt:137`

> `name: weave`, `adapter: weave`, `docker_image: null`, `timeout: 60`, `enabled: true`
>
> — `2026-04-25_pre-weave-integration.txt:139`

### <a id="d-055"></a>D-055 — W5 depends on RM2 phase R4a, not R1, and rolls back by env-flag flip

`2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** W5's classifier dependency is RM2 Phase R4a (`RefactoringClusterClassifier` and `language_of` importable from `semantic_merge_driver/core/`), explicitly not Phase R1. W5 ships behind `SEMANTIC_MERGE_BACKEND` (value set `git|mergiraf|weave|spork|auto`, default `auto` from R4b), so rolling it back is a flag flip to `mergiraf`/`git`, or removal of the single elif arm.

**Why.** R1 writes scenario JSON for `merge-tool-comparison/` only and is not callable from the runtime driver. Keeping the change to one elif arm behind an existing env flag makes rollback a flag flip rather than a code change.

**Status.** adopted. S12 (2026-07-26): both halves held — the W5 elif was wired only after R4a landed (routing Phase 1, c0a32f5), and rollback happened literally by env-flag: the refuted specialist arms survive only behind SEMANTIC_MERGE_SPECIALIST_ROUTING=1 (core/backends/auto_backend.py).

**Source.** `preA:pre-weave-integration-14`, `preA:pre-weave-integration-23` · Artifacts: `docs/plans/rm2-integration.md`, `semantic_merge_driver/core/driver.py`, `SEMANTIC_MERGE_BACKEND`

> R1 is *not* the right dependency: R1 writes scenario JSON for `merge-tool-comparison/` only and is not callable from the runtime driver.
>
> — `2026-04-25_pre-weave-integration.txt:197`

> W5: behind `SEMANTIC_MERGE_BACKEND` env flag — rollback is a flag flip to `mergiraf` or `git`, not a code change.
>
> — `2026-04-25_pre-weave-integration.txt:250`

### <a id="d-056"></a>D-056 — MVP-first reframe: R4b ships the dispatch skeleton, evidence gates move to per-cluster elifs

`2026-05-05` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** R4b's trigger softens to just R4a + M6-lite landed, and R4b ships the auto-mode dispatch skeleton itself rather than waiting for W5 or S2; W5 and S2 are thereby reduced to adding single elif arms against a pre-existing skeleton, and rolling either back is removing its arm (after which auto routes that cluster to Mergiraf again). Phase 6 splits into 6-lite (MergeBackend ABC + GitMergeFileBackend + MergirafBackend, no evidence gate) and 6-validate (retroactive Phase 4 validation), and execution-sequence stage ε is re-staged MVP-track first.

**Why.** Evidence discipline lives at the per-cluster elif level, not at the mechanism level; the MVP track gets an end-to-end pipeline working with two backends in ~3-4 days, and because the dispatch mechanism and default flip are already in place, W5's only contribution is the routing claim itself.

**Status.** adopted. Supersedes: [D-048](#d-048) — Split R4 into R4a classifier and R4b default flip to break the circular dispatch dependency.

**Source.** `preA:pre-commits-19`, `preB:pre-weave-integration-12` · Artifacts: `513ada6`, `docs/plans/execution-sequence.md`, `semantic_merge_driver/core/driver.py`

> Evidence discipline lives at the per-cluster elif level,
>
> — `2026-04-15_pre-commits.txt:218`

> W5 then adds one elif arm to that pre-existing skeleton, rather than introducing it.
>
> — `2026-04-25_pre-weave-integration.txt:21`

### <a id="d-057"></a>D-057 — Ship only one routing elif per cycle, chosen by an S2-vs-W5 pick rule

`2026-05-05` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: ali

**Decision.** Even at the fullest tier, only one specialized routing elif was to ship in the cycle — either S2 (INTRA_BODY+Java→Spork) or W5 (MIGRATE_DECL→Weave). The pick rule: S2 first when S3 evidence supports the INTRA_BODY+Java claim AND ISSUES.md #2 has resolved; W5 first when W3 evidence supports the MIGRATE_DECL claim AND ISSUES.md #2 has not.

**Why.** Shipping both W5 and S2 in one cycle is ~10-12 days, outside this cycle's budget. Between the two, Spork is more mature (5+ years, peer-reviewed) and matches the Java-only Schesch corpus exactly, but its empirical numbers are only trustworthy once ISSUES #2 resolves; Weave is multi-language and more general but 2.5 months old with single-contributor risk, and its evidence path does not depend on ISSUES #2 as tightly.

**Status.** superseded. Superseded by [D-042](#d-042) — Ship both S2 and W5 routing elifs together; the Tier-D pick rule is moot.

**Source.** `preA:pre-scope-tier-options-04`, `preA:pre-scope-tier-options-05` · Artifacts: `docs/plans/scope-tier-options.md`, `merge-tool-comparison/ISSUES.md #2`

> **Why single-elif and not dual-elif:** shipping both W5 and S2 in one cycle is ~10-12 days; outside this cycle's budget. Pick one based on R2 evidence and tool-track readiness.
>
> — `2026-05-05_pre-scope-tier-options.txt:114`

> **S2 first** if S3 evidence supports the `INTRA_BODY`+Java claim AND [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #2 has resolved (so Spork's empirical numbers are trustworthy).
>
> — `2026-05-05_pre-scope-tier-options.txt:117`

### <a id="d-058"></a>D-058 — Tier A ships Mergiraf-as-default as an explicitly unvalidated hypothesis

`2026-05-05` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: ali

**Decision.** At Tier A all clusters route to the Mergiraf default with no specialized routing claims, and the commit carries an honest caveat that Mergiraf-as-default is a hypothesis until M2-M5 lands.

**Why.** Tier A ships the architectural mechanism only; the M6-lite default choice is unvalidated because M1-M5 and 6-validate defer.

**Status.** adopted. S12 (2026-07-26): the commit carried exactly the required caveat — 3fef834's message reads 'Honest caveat: Mergiraf-as-default lacks empirical backing until M4 lands', and all clusters routed to the Mergiraf default until the routing elifs landed.

**Source.** `preA:pre-scope-tier-options-09` · Artifacts: `docs/plans/scope-tier-options.md`

> **Defensibility:** ships the architectural mechanism. Honest caveat in commit: Mergiraf-as-default is hypothesis until M2-M5 lands.
>
> — `2026-05-05_pre-scope-tier-options.txt:75`

> - All clusters route to Mergiraf default (no specialized routing claims yet).
>
> — `2026-05-05_pre-scope-tier-options.txt:67`

### <a id="d-059"></a>D-059 — RM2 wrapper contract: empty array is no-signal, exit 1 is a crash consumed fail-closed as NONE

`2026-05-05` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** An empty `refactorings: []` with exit 0 means 'no signal'; a wrapper exception (exit 1) is a crash that consumers R3/R4a handle fail-closed by returning the `NONE` cluster.

**Why.** The two outcomes are distinguishable by exit code, so the fail-closed consumer design maps cleanly onto them.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-recon-07` · Artifacts: `merge-tool-comparison/docker/refactoring_miner/DirPairMain.java`, `docs/plans/rm2-recon-samples/toy-empty.json`

> empty array → no signal; non-zero exit → fail-closed.
>
> — `2026-05-05_pre-rm2-integration-recon.txt:62`

### <a id="d-060"></a>D-060 — Accept file-level RM2 tagging at runtime, losing cross-file Extract/Move refactorings

`2026-05-05` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** R4a uses file-level RM2 tagging at runtime, accepting that cross-file refactorings (Extract And Move Method, Extract Class, Move Attribute, Move Method) are systematically missed and fall through to the `NONE` cluster.

**Why.** Extract/Move semantics require RM2 to see both source and destination files in one project tree, which file-level tagging by construction cannot; falling through to NONE is the safe choice because that route was the simplest/default backend.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-recon-11` · Artifacts: `semantic_merge_driver/core/refactoring_classifier.py`

> File-level by construction cannot see the destination file, so these systematically fall through to the `NONE` cluster.
>
> — `2026-05-05_pre-rm2-integration-recon.txt:96`

### <a id="d-061"></a>D-061 — Use Mergiraf's standalone three-file CLI in Docker; temp-git-repo plumbing declared obsolete

`2026-05-12 → 2026-05-13` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: preA:pre-mergiraf-integration-recon-09 attributes the CLI confirmation to ali; preA:pre-commits-40 records no actor for the ISSUES #24 resolution.*

**Decision.** Use the standalone CLI directly in both M6-lite and M1: `mergiraf merge BASE LEFT RIGHT -p PATH` (exit 0 clean, exit 1 conflict with `<<<<<<<` markers on stdout), invoked as `docker run --rm -v <workdir>:/workspace merge-tools/mergiraf:0.17.0 ... -p <path>`, capturing stdout and counting markers. The §6 temp-git-repo sketch is marked OBSOLETE and kept only for historical traceability. A follow-up smoke test of all three filename/`-p` combinations (ISSUES #24) confirmed the `-p` hint alone suffices for AST mode even with extensionless on-disk filenames, so `MergirafBackend.merge()`'s invocation stays as-is with the contract documented in the module docstring.

**Why.** The temp-git-repo plumbing rested on the then-assumption that the standalone CLI was undocumented; the CLI is now confirmed working, and project policy is Docker-only invocation. The discriminating fixture shows extensionless plus `-p Foo.java` gives AST mode rc=0, matching the current backend invocation.

**Status.** adopted. Supersedes: [D-044](#d-044) — Invoke Mergiraf via a temp git repo and merge driver, mirroring upstream.

**Cross-theme.** *depends-on* → [D-298](#d-298), [D-287](#d-287) — The Docker-only policy and the 0.4.0->0.17.0 pin override the note references are both owned by infrastructure.

**Source.** `preA:pre-mergiraf-integration-recon-09`, `preA:pre-commits-40` · Artifacts: `docs/plans/mergiraf-integration-recon.md`, `51aa3f2`, `ISSUES.md #24`, `core/backends/mergiraf_backend.py`

> **⚠ §6 is OBSOLETE per the §0 update callout (2026-05-12).** The temp-git-repo plumbing was the M0 recommendation under the then-assumption that the standalone CLI was undocumented.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:157`

> The `-p` hint is sufficient for AST mode even with extensionless
>
> — `2026-04-15_pre-commits.txt:579`

### <a id="d-062"></a>D-062 — Ship backends-only for the 2026-05-18 cycle: four selectable backends, no routing elif

`2026-05-18` · **superseded** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** For the 2026-05-18 cycle the Tier A–D menu is superseded by a 'backends-only' outcome: both Spork and Weave ship as explicitly selectable backends via `SEMANTIC_MERGE_BACKEND=spork|weave`, Weave newly Dockerized, with no routing elif and no S3/W3 evidence gate. Tiers A–D are retained as the menu for a future routing cycle.

**Why.** It builds the four-backend spine without asserting any cluster→tool routing claim — deliberately neither single-elif (Tier D) nor evidence-only (Tier C).

**Status.** superseded. Superseded by [D-041](#d-041) — Split routing into Phase-1 mechanism (no evidence gate) and deferred Phase-2 soundness.

**Cross-theme.** *supersedes* → [D-016](#d-016) — pre-scope-tier-options-01/-02 consolidate into scope-architecture/[D-016](#d-016). Its null superseded_by was filled with this entry's slug (see also scope-architecture:1, the mirror).

**Source.** `preA:pre-scope-tier-options-11` · Artifacts: `SEMANTIC_MERGE_BACKEND`

> routing elif and no S3/W3 evidence gate**. This is deliberately *neither*
>
> — `2026-05-05_pre-scope-tier-options.txt:9`

> *spine* without asserting any cluster→tool routing claim.
>
> — `2026-05-05_pre-scope-tier-options.txt:11`

### <a id="d-063"></a>D-063 — R2 per-cluster contrasts inform but do not justify the S2/W5 routing elifs

`2026-05-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The observed per-cluster contrasts (Spork best on INTRA_BODY F1 0.88; Mastery collapsing on SYMBOL_CASCADE) are reported as suggestive only and explicitly declared insufficient to justify enabling the S2/W5 auto-routing elifs.

**Why.** Per-cluster n is 4–18, below the Wilson-CI bar, so the signal informs but cannot justify a routing decision; reported as-is rather than tuned.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-133](#d-133) (see the reconciliation note there)

**Source.** `a:20b53f98-18` · Artifacts: `merge-tool-comparison/reports/results.csv`

> but per-cluster n is 4–18, below the Wilson-CI bar, so it *informs* but does not *justify* a future S2/W5 elif. Reported as-is, not tuned.
>
> — `2026-05-18_20b53f98.txt:224`

### <a id="d-064"></a>D-064 — Reframe the INTRA_BODY+Java condition as a defensive language guard, not a second dispatch axis

`2026-05-19` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Withdraw the "second dispatch axis" claim made throughout spork-driver-integration.md (§3, S3(a), S4). The `INTRA_BODY`+Java→Spork condition is to be described as a defensive language guard on the Java-only Spork backend, and the thesis claim is "cluster-based dispatch with a language guard on the Java-only specialist", not "two-axis dispatch demonstrated".

**Why.** The only producer of `INTRA_BODY` is RM2, which is Java-only, so `cluster==INTRA_BODY` always co-occurs with `language==JAVA` in production — the guard never diverts anything and is inert under the current RM2-only toolchain; it is only unit-demonstrated via a stub classifier.

**Status.** adopted. Supersedes: *the "second dispatch axis" claim in spork-driver-integration.md (§3, S3(a), S4)*.

**Cross-theme.** *depended on by* ← [D-396](#d-396) (see the reconciliation note there)

**Source.** `preA:pre-spork-driver-integration-01` · Artifacts: `docs/plans/spork-driver-integration.md`, `test_auto_backend.py`

> The honest thesis claim is "cluster-based dispatch with a language
>
> — `2026-04-25_pre-spork-driver-integration.txt:30`

> RM2, which is Java-only, so `cluster==INTRA_BODY` always co-occurs with
>
> — `2026-04-25_pre-spork-driver-integration.txt:24`

### <a id="d-065"></a>D-065 — Routing is whole-file and presence-only by construction, documented as a design limitation

`2026-05-20` · **adopted** · `[chat]` · corroboration: single-pass · confidence: medium · actors: unclear

**Decision.** Two consequences of the cluster/precedence design are recorded as design limitations rather than bugs: one label yields one backend for the entire file (no per-hunk or per-region routing), and the set union of both branches' refactoring types loses branch-of-origin and count, so concurrent same-type edits cannot be distinguished from one-sided ones.

**Why.** The precedence order is "hardest-for-a-line-based-merger first": when several kinds of change coexist, route to the tool suited to the most disruptive one, assuming easier changes survive that tool too — the resulting flattening trades the richer per-branch picture for a single deterministic route.

**Status.** adopted.

**Source.** `a:e1df1610-28` · Artifacts: `semantic_merge_driver/core/refactoring_classifier.py`

> 1. **One label → one backend for the *entire file*.** There's no per-hunk/per-region routing.
>
> — `2026-05-20_e1df1610.txt:444`

> 2. **The union is presence-only — it loses branch-of-origin and count.**
>
> — `2026-05-20_e1df1610.txt:446`

### <a id="d-066"></a>D-066 — Add mergiraf and weave comparator adapters, keeping jdime and mastery as baselines

`2026-05-20` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

**Decision.** Write `src/tools/mergiraf.py` and `src/tools/weave.py` mirroring the driver's invocations and enable both in `config/tools.yaml`, so the loader resolves six tools (git-merge-file, jdime, mastery, mergiraf, spork, weave); jdime and mastery are retained as baselines rather than removed.

**Why.** Docker images for mergiraf and weave already existed in the comparator, so only adapters and yaml entries were missing. Realigning the tool set keeps git and spork but makes the jdime/mastery findings legacy, so those two are kept as baselines.

**Status.** adopted.

**Cross-theme.** *duplicated by* ← [D-189](#d-189) (see the reconciliation note there)

**Source.** `a:e1df1610-06` · Artifacts: `merge-tool-comparison/src/tools/mergiraf.py`, `merge-tool-comparison/src/tools/weave.py`, `merge-tool-comparison/config/tools.yaml`, `e334cb3`

> "Record + wire mergiraf/weave" it is — keep jdime/mastery as baselines.
>
> — `2026-05-20_e1df1610.txt:600`

> Loader now resolves **6 tools**: git-merge-file, jdime, mastery, mergiraf, spork, weave (jdime/mastery kept as baselines).
>
> — `2026-05-20_e1df1610.txt:629`

### <a id="d-067"></a>D-067 — Withdraw the Weave field-loss severity alarm after corpus measurement

`2026-05-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Downgrade the smoke-test Weave field-loss warning: on the expanded-60 corpus Weave produced only 2 FP, so the lossy-field bug is real but rare, and Weave's entity-level conservatism makes it conflict rather than silently mis-merge on hard cases.

**Why.** Corpus measurement (2 FP total; MIGRATE_DECL 2 TP / 0 FP) contradicted the predicted Mastery-like content-loss FP pattern.

**Status.** adopted. Supersedes: *the smoke-test prediction that Weave would rack up content-loss FPs like Mastery*.

**Source.** `a:e1df1610-18` · Artifacts: `merge-tool-comparison/reports_expanded/results.csv`

> **Weave correction:** my smoke-test field-loss alarm did **not** dominate real data — only 2 FP total.
>
> — `2026-05-20_e1df1610.txt:798`

### <a id="d-068"></a>D-068 — File ISSUES #27: INTRA_BODY→Spork routing is contraindicated by the corpus

`2026-05-25 → 2026-05-26` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: a:e1df1610-17 (the filing) is joint — options were put and Ali picked; a:e1df1610-26 (the DROP recommendation) is claude's. Recorded joint for the entry as a whole.*

**Decision.** Record as ISSUES #27, with a Summary-Table row, that on the 6 INTRA_BODY cases Spork scored 1 TP / 5 FP while default Mergiraf scored 4 TP / 0 FP, so the S2 routing arm sends merges to the worse tool — filed with the explicit caveat that n=6 on a biased set and CIs are needed before changing the arm. The follow-up recommendation is to stop auto-routing INTRA_BODY to Spork (route it to Mergiraf) while keeping Spork as an explicitly selectable backend (`SEMANTIC_MERGE_BACKEND=spork`) and as a comparator baseline, offered either as an immediate engineering change or preceded by a cluster-stratified Wilson-CI sample.

**Why.** It is the sharpest Phase-2 routing-soundness signal and bears on the primary deliverable (the driver). Mergiraf beats Spork in every cluster on two independent samples including INTRA_BODY (n=6 then n=10), with no cluster where Spork wins, and Spork runs ~6 s vs Mergiraf's ~0.5 s. Spork is not bad — its FPs are mostly comparator-gap (≈27% genuine) and it does beat git — so it stays available as a baseline and explicit backend.

**Status.** superseded. S12 (2026-07-26): the filing landed at the time (7086844); the drop it recommended was enacted by the later CI-grade refutation decision. Superseded by [D-074](#d-074) — Drop the INTRA_BODY→Spork routing arm on five independent angles of refutation.

**Source.** `a:e1df1610-17`, `a:e1df1610-26` · Artifacts: `merge-tool-comparison/ISSUES.md #27`, `7086844`

> **Track the `INTRA_BODY → Spork` finding** in ISSUES.md — it's the sharpest Phase-2 signal and bears on the primary deliverable.
>
> — `2026-05-20_e1df1610.txt:805`

> Short answer: **the evidence says stop *auto-routing* to Spork (let Mergiraf handle INTRA_BODY), but keep Spork available as a selectable backend and as a comparator baseline.**
>
> — `2026-05-20_e1df1610.txt:1247`

### <a id="d-069"></a>D-069 — Keep the S2 Spork arm live in code while the DROP flip stays deferred

`2026-05-27` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Leave the S2 routing arm (INTRA_BODY + Java → Spork) in place at `auto_backend.py:120` despite the DROP verdict; the one-line flip remains deferred to a future cycle, and this decided-but-not-implemented state is treated as deliberate rather than drift.

**Why.** Code matches the docs — ISSUES #27 and CLAUDE.md both say decided=DROP with the flip deferred — so the state is consistent across code and prose and is a deliberate state, not drift.

**Status.** superseded. Superseded by [D-072](#d-072) — Land the route flip as an opt-in env flag rather than deleting the specialist arms.

**Source.** `a:3302d287-03` · Artifacts: `semantic_merge_driver/core/backends/auto_backend.py:120`, `ISSUES.md #27`

> the docs explicitly flag the flip as deferred. Good — that's a deliberate state, not drift.
>
> — `2026-05-27_3302d287.txt:13`

> exactly as ISSUES #27 / CLAUDE.md say (decided=DROP, one-line flip deferred to a future cycle)
>
> — `2026-05-27_3302d287.txt:34`

### <a id="d-070"></a>D-070 — Run driver-auto on the committed pre-flip router and capture the routed backend per merge

`2026-06-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: a:fb0fa5c5-03 is joint (options put, Ali picked); a:fb0fa5c5-04 is claude's implementation call. Recorded joint for the entry.*

**Decision.** The `driver-auto` arm in P2 executes the current committed `auto_backend._route` with the Spork/Weave specialist arms live, deferring the post-flip re-run to P3. The harness is extended to parse `AutoBackend: cluster=X language=Y → BACKEND` and the crash-fallback line from driver stderr, storing cluster / chosen / effective route per merge, and the report gains a routing-distribution table with per-backend FP rates.

**Why.** You measure the code that exists, not the code you intend — pretending the flip was done would make the whole-driver claim describe a driver never committed; and on this rename-heavy corpus the pre-flip router's results corroborate #27/#28 end-to-end. Outcome labels (clean/conflict) do not reveal which backend was chosen, so capturing the route turns an indirect signal into quantified end-to-end evidence and shows how often Spork/Weave were chosen versus crash-fell-back.

**Status.** adopted.

**Source.** `a:fb0fa5c5-03`, `a:fb0fa5c5-04` · Artifacts: `semantic_merge_driver/core/backends/auto_backend.py`, `tools/whole_driver_eval.py`

> **Evaluation honesty: you measure the code that exists, not the code you intend.**
>
> — `2026-06-24_fb0fa5c5.txt:1417`

> I'll capture both — cluster, chosen backend, and whether it fell back — so the FINDINGS can show the actual routing distribution
>
> — `2026-06-24_fb0fa5c5.txt:262`

### <a id="d-071"></a>D-071 — Propose flipping auto_backend._route to NONE→git, everything else→Mergiraf

`2026-06-24` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Recommend changing `auto_backend._route` (~4 lines plus test update) so routing collapses to `NONE→git, else→Mergiraf`, removing the `MIGRATE_DECL→Weave` and `INTRA_BODY→Spork` specialist arms.

**Why.** Both specialist arms were refuted with CI-grade evidence (#27 Spork, #28 Weave) and the docs already state the honest map, so the code currently contradicts the project's own conclusion; the flip removes the single worst code/doc mismatch at lowest risk and highest credibility.

**Status.** superseded. S12 (2026-07-26): the collapse landed 2026-07-02 in modified form — arms kept behind an opt-in flag rather than deleted, exactly as the superseding entry records. Superseded by [D-072](#d-072) — Land the route flip as an opt-in env flag rather than deleting the specialist arms.

**Source.** `a:ce56e78d-02` · Artifacts: `semantic_merge_driver/core/backends/auto_backend.py`, `ISSUES.md #27`, `ISSUES.md #28`

> **Land the auto-routing flip.** ~4 lines in `_route` + test update, collapsing to `NONE→git, else→Mergiraf`. Removes the single worst code/doc mismatch and matches the evidence you already gathered.
>
> — `2026-06-24_ce56e78d.txt:35`

> even though both specialist arms were refuted with CI-grade evidence (#27 Spork, #28 Weave)
>
> — `2026-06-24_ce56e78d.txt:25`

### <a id="d-072"></a>D-072 — Land the route flip as an opt-in env flag rather than deleting the specialist arms

`2026-07-02` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The `_route` fix keeps `NONE→git` and sends everything else to Mergiraf by default, with the refuted `MIGRATE_DECL→Weave` and `INTRA_BODY→Spork` arms retained behind `SEMANTIC_MERGE_SPECIALIST_ROUTING=1`.

**Why.** The 06-10 review recommended opt-in over delete: it preserves the mechanism as apparatus — supporting the "can route to any future candidate" claim and reproducing the P2 before/after — without letting the refuted arms touch default behaviour.

**Status.** adopted. Supersedes: [D-069](#d-069) — Keep the S2 Spork arm live in code while the DROP flip stays deferred.

**Source.** `a:fb0fa5c5-29` · Artifacts: `semantic_merge_driver/core/backends/auto_backend.py`, `9e25b4e`

> I'd go with the flag — it preserves the mechanism as apparatus without letting it touch default behavior. Plain delete is also defensible if you prefer minimal code.
>
> — `2026-06-24_fb0fa5c5.txt:1503`

> The flip: default `auto` = `NONE→git, else→Mergiraf`; refuted arms opt-in via `SEMANTIC_MERGE_SPECIALIST_ROUTING=1`
>
> — `2026-06-24_fb0fa5c5.txt:2029`

### <a id="d-073"></a>D-073 — RefMerge/RefactoringMiner-3.0 architecture direction confirmed reverted; gate never met

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Retrospectively confirm that the original operation-based RefMerge + RefactoringMiner-3.0 pipeline direction was reverted and RefMerge integration was never built.

**Why.** RefMerge integration was conditioned on evidence that Mergiraf actually fails on refactoring scenarios, and that evidence never materialized.

**Status.** adopted. Supersedes: [D-033](#d-033) — Prefer operation-based RefMerge over graph-based IntelliMerge as the refactoring-aware backend.

**Source.** `a:dc3bc182-sub-sub-agent-a74c7a-01` · Artifacts: `docs/historical/ARCHITECTURE-refmerge.md`, `docs/plans/tool-evaluation-findings.md`

> RefMerge was gated "do NOT integrate yet" pending evidence Mergiraf actually fails on refactoring scenarios — evidence that never materialized.
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:43`

> That direction was **reverted**.
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:43`

### <a id="d-074"></a>D-074 — Drop the INTRA_BODY→Spork routing arm on five independent angles of refutation

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The INTRA_BODY→Spork specialist routing arm is dropped (Issue #27), based on five independent angles: file-level n=6 and n=10 replication, ci-240 pooled precision with non-overlapping CIs, Pareto-dominance on latency, a Spork-rigged 16-case synthetic battery, and the 5,405-merge test oracle.

**Why.** Spork lost on every angle: pooled INTRA_BODY precision 0.49 [0.37,0.60] vs Mergiraf 0.78 [0.66,0.86] (non-overlapping), 7–18× slower and faster in 0/146 cases, 0 strict-wins on a battery rigged in its favour, and 39 vs Mergiraf's 272 right on the test oracle.

**Status.** adopted. Supersedes: *auto router arm INTRA_BODY→Spork*.

**Cross-theme.** *depended on by* ← [D-018](#d-018) (see the reconciliation note there)

**Source.** `a:dc3bc182-sub-sub-agent-ab4c4f-03` · Artifacts: `ISSUES.md #27`

> **#27 INTRA_BODY→Spork** — refuted across five angles
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:61`

> and the 5,405-merge test oracle (Mergiraf right 272 vs Spork 39, ~7:1). DROP.
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:61`

### <a id="d-075"></a>D-075 — Drop the MIGRATE_DECL→Weave routing arm after the W3 gate run

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The MIGRATE_DECL→Weave specialist routing arm is dropped (Issue #28), per the W3 gate run over n=38 scenarios across 31 repos.

**Why.** Weave wins 0 scenarios over Mergiraf (McNemar exact p=0.0078), its correct merges are a strict subset (11⊂19), it abstains on all 7 Mergiraf dev-mismatches (71% abstention), and under the test oracle zero of Mergiraf's 7 dev-match 'FPs' fail tests — so the MIGRATE_DECL weakness that motivated a Weave specialist was itself a comparator artifact.

**Status.** adopted. Supersedes: *auto router arm MIGRATE_DECL→Weave*.

**Cross-theme.** *depended on by* ← [D-018](#d-018) (see the reconciliation note there)

**Source.** `a:dc3bc182-sub-sub-agent-ab4c4f-04` · Artifacts: `ISSUES.md #28`, `reports_migrate_decl/FINDINGS.md`

> **Weave wins 0 scenarios over Mergiraf; McNemar exact p=0.0078**
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:62`

> The "opening" that motivated a Weave specialist was itself a comparator artifact. DROP.
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:62`

### <a id="d-076"></a>D-076 — Collapse the auto router to NONE→git, else→Mergiraf; routing benefit is the fast-path only

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The multi-arm specialist routing premise is abandoned: the default `auto` router became `NONE→git, else→Mergiraf` (landed 2026-06-27), with the refuted specialist arms preserved only behind `SEMANTIC_MERGE_SPECIALIST_ROUTING=1` as demonstrable apparatus. The record also states the honest scope of the remaining benefit: it reduces to the NONE→git fast-path, not quality routing.

**Why.** CI-grade gates (#27 Spork, #28 Weave) plus the refactoring-merge landscape survey empirically refuted both hypothesized specialist arms — no tool beats Mergiraf in any cluster. The in-vivo whole-driver run measured pre-flip auto breaking 21/239 control merges (8.8%), all from the Spork/Weave arms, versus 0 for always-Mergiraf; post-flip is the best config measured (pooled weighted cost 1779, 3.78/file), beating always-Mergiraf by 215 and pre-flip auto by 146, with routing-caused control FPs going 21→0. The entire routing benefit reduces to the NONE→git fast-path (49% of files: saves RM2 latency and surfaces the no-refactoring cluster more conservatively).

**Status.** adopted. Supersedes: [D-049](#d-049) — Adopt the 4-backend cluster-keyed dispatch map in AutoBackend._route().

**Cross-theme.** *depended on by* ← [D-018](#d-018) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-396](#d-396) (see the reconciliation note there)

**Source.** `a:dc3bc182-sub-sub-agent-a74c7a-02`, `a:dc3bc182-sub-sub-agent-ab4c4f-05` · Artifacts: `docs/plans/multi_refactoring_merge_landscape.md`, `reports_whole_driver/FINDINGS.md`, `ISSUES #27`, `ISSUES #28`

> The `auto` router therefore *collapsed* from an ambitious per-cluster dispatch to an honest `NONE→git, everything-else→Mergiraf`
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:47`

> The entire routing benefit reduces to the **`NONE→git` fast-path** (49% of files: saves RM2 latency + surfaces the no-refactoring cluster more conservatively) — not quality routing.
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:64`

### <a id="d-077"></a>D-077 — Default-enable ruling for the experimental detector lanes remains open with the user

`2026-07-23` · **open** · `[chat]` · corroboration: both · confidence: medium · actors: ali

**Decision.** Whether the experimental detector lanes graduate to default-on in the driver (plan §2 N2, deferred past the cycle) is left as an open user ruling; Claude's read is that S-D8's −11.5% cost at +8.3 s/file with zero adjudicated FPs makes default-enabling defensible, while keeping them flag-gated and reporting both configs is equally honest.

**Why.** S-D8 is the evidence that decision needed: −11.5% cost for +8.3 s/file on an already-research-grade latency budget, with zero adjudicated FPs anywhere.

**Status.** open. Ali's ruling was never recorded in the transcripts read here; would be settled by outputs/detector-cycle-plan.md §2 N2 or the driver's default lane configuration in a later cycle.

**Cross-theme.** *depends-on* → [D-128](#d-128), [D-032](#d-032) — Not a duplication to merge: detection owns the adopted flag-gating decision, scope-architecture the S-D7/S-D8 green-light that reserved the call, this entry the still-open ruling itself. All three cross-linked; the open entry is the live question and is on Ali's open-calls list.

**Cross-theme.** *depended on by* ← [D-281](#d-281) (see the reconciliation note there)

**Source.** `a:4c7b0828-39` · Artifacts: `outputs/detector-cycle-plan.md §2 N2`

> **The default-enable ruling is yours and still open** (plan §2 N2 deferred it past the cycle).
>
> — `2026-07-06_4c7b0828.txt:2022`

> My read: default-enabling is now the defensible choice, but "lanes stay flag-gated, thesis reports both configs" is equally honest
>
> — `2026-07-06_4c7b0828.txt:2022`


## Detection layer

*174 primary source decisions → 51 entries; 5 not promoted (reasons in `docs/decision-record/entries/detection.json`).*

### <a id="d-078"></a>D-078 — Strategies fail closed on internal errors instead of returning is_clean=True

`2026-04-16 → 2026-07-16` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: The plan- and commit-era sources do not attribute the rule; only the 2026-07-16 D2 refinement is attributed (Claude).*

**Decision.** Every analysis strategy must report is_clean=False with a CRITICAL "analysis inconclusive" issue when it fails internally, rather than silently accepting the merge. Applied to the Joern strategies for CalledProcessError and FileNotFoundError (044051f), extended in the β.1 fix to check process.returncode after each shelled joern query (51aa3f2, infinite_loop.py:37 / invalid_loop_bounds.py:78), required of the RM2 R3 lane from day one rather than letting it inherit the residual fail-silent path, and refined in the later D2 lane into two conventions: missing inputs abstain clean, infra/RM2 failures emit the fail-closed inconclusive result.

**Why.** Fail-open was diagnosed as a defect in the Step 0 audit — a strategy returning is_clean=True on error silently accepts a merge it never analysed. FileNotFoundError was added because "joern-parse not on PATH" previously escaped the strategy-level handler entirely; the returncode check was added because a crashed Joern query yields empty stdout that parsed as zero issues and reported is_clean=True, a fail-silent path distinct from the already-fixed exception path. The D2 lane split the two conventions along precedent: missing inputs follow D1's experimental-lane abstention, tool failures follow the rename lane's β-pattern.

**Status.** adopted. Supersedes: *baseline fail-open behaviour in core/driver.py and the Joern strategies*.

**Cross-theme.** *depended on by* ← [D-037](#d-037) (see the reconciliation note there)

**Source.** `preA:pre-architecture-refmerge-06`, `preA:pre-commits-12`, `preA:pre-execution-sequence-05`, `preA:pre-execution-sequence-07`, `preA:pre-commits-39`, `preB:pre-rm2-integration-27`, `a:acf7e1d0-05` · Artifacts: `044051f`, `51aa3f2`, `strategies/joern_strategies/infinite_loop.py`, `strategies/joern_strategies/invalid_loop_bounds.py`, `semantic_merge_driver/tests/test_fail_closed.py`, `ISSUES.md #24`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`

> **Fail closed**: All strategies must reject (report issue) on internal errors, never silently accept
>
> — `2026-04-16_pre-architecture-refmerge.txt:877`

> A crashed Joern query yields empty stdout → parsed as zero issues → reported `is_clean=True`.
>
> — `2026-04-22_pre-execution-sequence.txt:30`

### <a id="d-079"></a>D-079 — Three-way refactoring information is built from pairwise RM2 calls against base, per branch

`2026-04-16 → 2026-05-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: medium · actors: unclear

*Actors note: Plan- and commit-era sources are unattributed; the cited transcript-era acceptance of the doubled cost is Claude's.*

**Decision.** RefactoringMiner is only ever invoked pairwise against the base (originally `-bf base changed`, later detectAtDirectories), so every consumer calls it several times and combines the result sets: R1 three calls per scenario, R4a two per merge, R3 one per merge. Tagging runs on the ours and theirs axes rather than the resolution axis alone, and the evaluation computes the refactoring cluster on ours∪theirs.

**Why.** RM2's API is pairwise only and there is no "3-way RM2 mode" to wait for, so set algebra over pairwise output is where three-way semantics is implemented and the merge intelligence lives in the consuming strategies. Per-branch axes are required by the R4 gate and finding D2; computing the cluster on ours∪theirs rather than the plan's resolution axis makes the evidence dispatch-faithful and non-circular, which is also why the transcript-era session accepted the doubled RM2 cost for that axis.

**Status.** adopted. Supersedes: *R1 tagging on the resolution axis only*.

**Cross-theme.** *superseded-by* → [D-194](#d-194), [D-089](#d-089) — Not a supersession: the pairwise-per-branch principle stands (entry adopted). R1-as-built narrowed the comparator-side tagging to file-level ours/theirs (corpus-sampling), with the Path-D dual-mode deferral recorded in-theme. Rendered as narrowed-by links.

**Cross-theme.** *depended on by* ← [D-133](#d-133) (see the reconciliation note there)

**Source.** `preA:pre-architecture-refmerge-25`, `preA:pre-rm2-integration-05`, `preA:pre-commits-10`, `preA:pre-scope-tier-options-15`, `a:dc624d63-02` · Artifacts: `core/rm_astdiff.py`, `merge-tool-comparison/tools/rm2_tag.py`, `src/evaluation/categorizer.py`, `77d988a`

> There is no "3-way RM2 mode" to wait for — the decomposition pattern is the design.
>
> — `2026-04-22_pre-rm2-integration.txt:37`

> cluster is computed on `ours∪theirs` (deviation from the plan's `resolution`
>
> — `2026-05-05_pre-scope-tier-options.txt:37`

### <a id="d-080"></a>D-080 — Adopt RM-ASTDiff (RefactoringMiner 3.0) instead of GumTree plus RefactoringMiner 2.0

`2026-04-16` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The RefMerge architecture plan adopts RefactoringMiner 3.0 / RM-ASTDiff as the single pre-merge tool for both AST differencing and refactoring detection, replacing a GumTree diffing stage plus a separate RefactoringMiner 2.0 pass.

**Why.** RM-ASTDiff unifies AST differencing and refactoring detection in one pass, breaks GumTree's one-to-one mapping constraint (1-to-n and n-to-1), uses language-specific semantic clues for full inter-file mapping precision and covers 100+ refactoring types versus 40; running two tools is "computationally wasteful when RM-ASTDiff does both, better, in one pass".

**Status.** superseded. Superseded by [D-085](#d-085) — Use RefactoringMiner 2.x pinned at 2.4.0, with RM 3.x out of thesis scope.

**Source.** `preA:pre-architecture-refmerge-01` · Artifacts: `core/rm_astdiff.py`

> **Why RM-ASTDiff instead of GumTree + RefactoringMiner 2.0:**
>
> — `2026-04-16_pre-architecture-refmerge.txt:196`

> Running GumTree for AST differencing and then a separate RefactoringMiner pass for refactoring detection is computationally wasteful when RM-ASTDiff does both, better, in one pass.
>
> — `2026-04-16_pre-architecture-refmerge.txt:197`

### <a id="d-081"></a>D-081 — The driver rejects a merge only on CRITICAL issues; WARNING does not block

`2026-04-16` · **abandoned** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** The driver's verdict filters all collected issues to severity == 'CRITICAL'; if any exist it reports them and returns exit 1, otherwise exit 0. WARNING-level issues do not block a merge.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** abandoned. S12 (2026-07-26): never implemented — core/driver.py:83-101 blocks on ANY issue regardless of severity (all_clean flips on every non-clean result; no severity filter exists). The 'Critical Logic Bugs Found' message is cosmetic. Under shipped code a WARNING-severity issue does block, contra this plan rule.

**Source.** `preA:pre-architecture-refmerge-10` · Artifacts: `core/driver.py`

> critical_issues = [i for i in all_issues if i.severity == 'CRITICAL']
>
> — `2026-04-16_pre-architecture-refmerge.txt:302`

### <a id="d-082"></a>D-082 — Atomic-update invariants get a hybrid RM-ASTDiff plus Joern structural strategy

`2026-04-16` · **abandoned** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** Atomic update / invariant violations are given their own structural_strategies/atomic_update_check.py combining RM-ASTDiff edit information (which branch modified which field) with Joern CPG analysis locating the validation methods that enforce the invariant, rather than being a pure CPG strategy.

**Why.** The invariant category needs both which-branch-changed-what edit information and detection of the assertion/validation methods that enforce the invariant, so neither tool alone suffices.

**Status.** abandoned. S12 (2026-07-26): never built — no atomic_update_check.py or structural_strategies/ directory exists; the strategies tree is joern/rm2/text lanes only. The census later found Atomic Updates has no empirical counterpart, and the category was descoped.

**Source.** `preA:pre-architecture-refmerge-19` · Artifacts: `strategies/structural_strategies/atomic_update_check.py`

> This strategy uses a combination of RM-ASTDiff edit information
>
> — `2026-04-16_pre-architecture-refmerge.txt:740`

### <a id="d-083"></a>D-083 — Detect rename conflicts from RM refactoring metadata, scoped to within-file stale callers

`2026-04-16 → 2026-06-11` · **adopted** · `[mixed]` · corroboration: mixed · confidence: medium · actors: unclear

*Actors note: The plan and most commit records are unattributed; one commit-era source attributes the within-file scoping to Ali, and the Stage-B widening is Claude's.*

**Decision.** Rename conflicts are detected from RefactoringMiner metadata rather than by inspecting the merged file: the strategy cross-references the per-branch refactoring lists for dangling references, lost changes, stale imports and naming conflicts, and the shipped RM2RenameConflictStrategy runs RM2 file-level on (base, merged), filters to {Rename Method, Rename Class}, scans the merged file for stale callers and emits CRITICAL issues, failing closed on every error path. base_content reaches strategies through the already-optional second positional parameter of MergeStrategy.analyze. Scope is within-file only; cross-file stale callers are tracked as a follow-up. Stage B widened the lane to Variable/Parameter/Attribute renames with per-branch RM2 on (base,ours)/(base,theirs) for half-applied renames, a mixed-state guard so wholly-dropped renames stay clean, a declaration guard and comment/string stripping.

**Why.** The strategy operates on refactoring metadata, not the merged file, because cross-referencing the detected refactorings on both branches is what identifies conflicting operations — a metadata lookup with no CPG cost that catches the Method Rename category before Joern runs. The lane reuses RM2 already in the toolchain for R4a's classifier and is independent of the R1/R2/R4a/R4b and Mergiraf tracks. Project-level RM2 on (base, merged) would require synthesising a project tree by overlaying the merged file over a base checkout — messy and not worth the latency — so cross-file detection waits for evidence that it is a frequent miss. The Stage-B widening was designed against codeElement shapes probed on the real RM2 2.4.0 image first, including the negative finding that static-final constant renames are not reported.

**Status.** adopted.

**Source.** `preA:pre-architecture-refmerge-18`, `preB:pre-tool-evaluation-findings-18`, `preA:pre-commits-52`, `preA:pre-commits-54`, `preA:pre-rm2-integration-21`, `preB:pre-commits-59`, `b:bfc672b4-42` · Artifacts: `strategies/rm2_strategies/rename_conflict.py`, `core/driver.py`, `core/interfaces.py`, `0d52fdb`, `docs/plans/rm2-integration.md`

> This strategy operates on the refactoring metadata, not on the merged
>
> — `2026-04-16_pre-architecture-refmerge.txt:572`

> Within-file scope only; cross-file stale callers tracked as a
>
> — `2026-04-15_pre-commits.txt:964`

### <a id="d-084"></a>D-084 — Classifier and tagger fail closed to Cluster.NONE; empty RM2 output is a normal result

`2026-04-22 → 2026-05-18` · **adopted** · `[mixed]` · corroboration: both · confidence: high · actors: unclear

*Actors note: The plan and commit records do not attribute the classifier decisions; the 2026-05-18 tagger mirror is attributed to Claude.*

**Decision.** RefactoringClusterClassifier.cluster() never raises: missing Docker, FileNotFoundError, CalledProcessError, non-zero returncode, malformed JSON and timeout all return Cluster.NONE, which routes to the Mergiraf default backend; the empirical tagger mirrors this by returning an empty refactoring set for the pair. Separately, `refactorings: []` with exit 0 is a normal path, not an error: R1 writes an empty axis, R3 returns is_clean=True, R4a returns NONE. NONE therefore conflates "Docker error" with "no refactorings detected".

**Why.** Both failure and no-signal cases route to the Mergiraf default anyway (rm2-integration.md §1.3), so conflating them costs nothing at the dispatch level; and absence of a rename signal is not evidence of conflict, so there is nothing to act on. Fail-closed matches the β-stage pattern the Joern strategies adopted. In the tagger the same behaviour means a missing Docker image degrades a scenario to NONE rather than aborting the verification run.

**Status.** adopted.

**Source.** `preA:pre-execution-sequence-17`, `preA:pre-rm2-integration-20`, `preA:pre-commits-41`, `preA:pre-rm2-integration-18`, `a:20b53f98-12` · Artifacts: `semantic_merge_driver/core/refactoring_classifier.py`, `merge-tool-comparison/tools/rm2_tag.py`, `docs/plans/rm2-integration.md §1.3`, `b37479c`

> Fail-closed: missing Docker, non-zero rc, malformed JSON, timeout —
>
> — `2026-04-15_pre-commits.txt:620`

> no detected renames → return `is_clean=True` with empty issues list. Correct semantics — there is no rename signal to act on, and absence of evidence is not evidence of conflict.
>
> — `2026-04-22_pre-rm2-integration.txt:263`

### <a id="d-085"></a>D-085 — Use RefactoringMiner 2.x pinned at 2.4.0, with RM 3.x out of thesis scope

`2026-04-22 → 2026-07-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: The recon and difference documents are unattributed; the initial "start with 2.0" recommendation is Claude's.*

**Decision.** RefactoringMiner 2.0 is the starting point rather than 3.0/RM-ASTDiff, pinned at release 2.4.0 (last 2.x, published 2023-03-04, consumed as the GitHub release ZIP) and used with the default `detectAtDirectories` detection rather than RM-ASTDiff. RM 3.x is out of thesis scope; R1's per-scenario tags are drawn from the 2.4.0 detector catalog only, and RM2 survives in the design as a runtime cluster classifier and rename detector, not as RefMerge's merge engine.

**Why.** 2.0 is simpler and "does one thing", is a widely cited stable JAR and aligns with the adjacent literature, whereas 3.0 unifies two concerns, has less track record and needs an adapter; the plan's non-goal was to avoid RM-ASTDiff unless R0 showed plain RM2 insufficient, and the toy fixture and F-harness showed no insufficiency. 2.4.0 satisfies R0's "2.4+ recommended" criterion, and the rm2-vs-rm3 comparison was written so "why didn't we use the newer one?" has a concrete answer: identical wrapper API and JSON output, 2.4.0 about 1s faster per call, and both versions land in the same 50–80% F-harness bracket so the Path D selection is unaffected. The accepted cost is a detector roster roughly three years old, losing `Replace Generic With Diamond` (one scenario drops out of the active set, 5/10 → 4/10). A 3.x catalog would not match the pinned tool's output, since scenarios that are "no-refactoring" on 2.4.0 may become active on 3.x.

**Status.** adopted. Supersedes: [D-080](#d-080) — Adopt RM-ASTDiff (RefactoringMiner 3.0) instead of GumTree plus RefactoringMiner 2.0; *the R0 wrapper's RefactoringMiner 3.0.13 pin*.

**Source.** `preA:pre-tool-evaluation-findings-05`, `preA:pre-rm2-integration-recon-02`, `preA:pre-rm2-integration-recon-01`, `preB:pre-rm2-integration-recon-01`, `preA:pre-rm2-vs-rm3-differences-01`, `preA:pre-rm2-vs-rm3-differences-02`, `preA:pre-rm2-vs-rm3-differences-06`, `a:dc3bc182-sub-sub-agent-a74c7a-08` · Artifacts: `docs/plans/rm2-integration-recon.md`, `docs/plans/rm2-vs-rm3-differences.md`, `RefactoringMiner-2.4.0.zip`, `5e687ce`, `merge-tool-comparison/docker/refactoring_miner/`

> Recommendation: start with 2.0.** Simpler, matches the principle of "specialized tool doing one thing,"
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:155`

> This doc exists so that "why didn't we use the newer one?" has a concrete answer pointing at observed deltas, not just a date or a version-string preference.
>
> — `2026-05-06_pre-rm2-vs-rm3-differences.txt:10`

> We're pinning to the 2.x line knowingly, accepting that the detector roster is ~3 years older than what RM 3.x offers (§6).
>
> — `2026-05-06_pre-rm2-vs-rm3-differences.txt:208`

### <a id="d-086"></a>D-086 — Strategy enablement comes from a YAML config file, not environment variables

`2026-04-22` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Open question 1 is resolved with a YAML file at semantic_merge_driver/config/strategies.yaml loaded via PyYAML in core/config.py's load_enabled_strategies(); schema `enabled: [StrategyName, ...]`, absent or null loads all discovered strategies, an empty list runs none, and no environment variables are used. driver.py main() calls the loader instead of a literal strategy list.

**Why.** It is forward-compatible — R3 adds one line to the list — and it replaces the hardcoded single strategy so R3 (Method Rename) inherits a working multi-strategy path by default.

**Status.** adopted. Supersedes: *the hardcoded single strategy list in core/driver.py*.

**Cross-theme.** *duplicated by* ← [D-344](#d-344) (see the reconciliation note there)

**Source.** `preA:pre-execution-sequence-06` · Artifacts: `semantic_merge_driver/config/strategies.yaml`, `semantic_merge_driver/core/config.py`, `requirements.txt (pyyaml>=6.0)`

> **Decision on open question 1 (resolved):** YAML file at `config/strategies.yaml`, loaded via PyYAML. No env vars.
>
> — `2026-04-22_pre-execution-sequence.txt:50`

### <a id="d-087"></a>D-087 — Consume only structured RM2 JSON fields; never parse descriptions or assume location[0]

`2026-04-22 → 2026-05-05` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** The Docker wrapper emits one JSON document per invocation on stdout with `directories` (left/right absolute paths) and `refactorings` as an array of `Refactoring.toJSON()` elements matching Appendix B of the integration plan. Downstream code consumes only `type`, `leftSideLocations[].codeElement`, `rightSideLocations[].codeElement`, `filePath` and `startLine`/`endLine`; human-readable `description` strings must not be parsed, and code must not assume index `[0]` for anything other than simple renames.

**Why.** Field names are stable across RM2 2.x while descriptions are human-readable; the location fields are lists, and Extract Method has one left location and multiple right locations, so `[0]` is not general.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-29`, `preB:pre-rm2-integration-recon-08` · Artifacts: `merge-tool-comparison/docker/refactoring_miner/DirPairMain.java`, `docs/plans/rm2-integration.md Appendix B`

> descriptions are human-readable and should **not** be parsed.
>
> — `2026-04-22_pre-rm2-integration.txt:443`

> Do not assume `[0]` for types other than simple renames.
>
> — `2026-04-22_pre-rm2-integration.txt:473`

### <a id="d-088"></a>D-088 — Ship D1 as a pure-textual differential lane, extension-scoped and behind an experimental flag

`2026-04-25 → 2026-07-16` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: The 2026-04-25 extension-based rule is unattributed in the plan; the lane and its gates are Claude's.*

**Decision.** ImportPruneUsage is a pure-text differential MergeStrategy under strategies/text_strategies/, gated by SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1 with the flag check as the first line of analyze(). It abstains (is_clean=True) on four entry gates: flag off, path not ending .java, ours_content or theirs_content None, and merged text containing conflict markers — extension-based language detection being the standing rule, with content-sniffing out of scope. _FileView blanks comments, strings, chars and text blocks by space-substitution preserving newlines so byte offsets and line numbers are unchanged, including javadoc; each import's identity is the tuple (is_static, path, is_wildcard) with whitespace and newlines tolerated inside the statement; and the differential is lost = (imports(ours) ∪ imports(theirs)) − imports(merged), deliberately excluding base.

**Why.** The first-line flag check means the lane cannot crash, flag or slow anything with the flag off, so the default driver is bit-identical to pre-S-D2 behaviour — which is what makes the GD3 baseline arm meaningful. The driver runs strategies on any merged file, so a non-.java gate is needed or Python `import x` lines would parse as Java imports; a textual conflict is already surfaced, so abstaining there hides nothing while parsing marker soup would produce garbage. Preserving offsets keeps the comments-and-strings guard in one place, and keying import identity on the tuple means reordering or reformatting by mergiraf never looks like a prune. Base is excluded because an import present in base but in neither parent was removed by both sides, so any surviving usage is parent-side breakage rather than merge-induced. Stripping javadoc too is validated by the direction of the problem: google-java-format must count javadoc references because removing an import breaks `{@link}`, whereas a javadoc-only usage of a pruned import does not break compilation, which is the failure mode being detected.

**Status.** adopted.

**Source.** `preA:pre-spork-driver-integration-10`, `a:f0d70a59-01`, `a:f0d70a59-19`, `b:f0d70a59-26`, `b:f0d70a59-27`, `a:f0d70a59-05`, `a:734e4529-06` · Artifacts: `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`, `semantic_merge_driver/config/strategies.yaml`, `core/language_detect.py`, `9f871b1`

> With the env flag unset D1 returns clean at line one, so the default driver is bit-identical to pre-S-D2 behavior — that's not just politeness, it's what makes the GD3 baseline arm meaningful.
>
> — `2026-07-16_f0d70a59.txt:166`

> Base is deliberately **not** in the union — an import present in base but in neither parent was removed by both sides; any surviving usage is a parent-side breakage, not merge-induced
>
> — `2026-07-16_f0d70a59.txt:112`

> - Language detection rule for the router: extension-based (`.java`) is sufficient for S1; content-sniffing is out of scope.
>
> — `2026-04-25_pre-spork-driver-integration.txt:106`

### <a id="d-089"></a>D-089 — Select Path D dual-mode tagging and accept file-level blindness to cross-file refactorings

`2026-05-05 → 2026-05-13` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: Mostly unattributed plan/commit records; one commit-era source attributes the Path D selection to Ali.*

**Decision.** R1 runs the tagger in dual mode (file-level plus project-level) while R4a uses file-level detection at runtime, staging each file to its basename in two single-file temp directories mirroring rm2_fharness.py. Cross-file Extract/Move refactorings — Extract And Move Method, Extract Class, Move Attribute/Method/Class — are therefore systematically missed and fall through to the NONE cluster.

**Why.** The F-harness measured file-level recall of project-level inside the 50–80% bracket (75.0% with RM 3.0.13, 66.7% with 2.4.0, n=10), and the R1 decision table maps that bracket to Path D, described as the most defensible; the bracket also bounds the wide confidence interval of the n=10 point estimate. File-level detection by construction cannot see the destination file, so those refactorings are undetectable at this API surface, and NONE routes to the Mergiraf default — the safe choice — so the miss is tolerable.

**Status.** adopted.

**Cross-theme.** *supersedes* ← [D-079](#d-079) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-297](#d-297) — other_uid preA:pre-commits-23 landed there: the pin rollback that forced the Path-D bracket re-derivation.

**Source.** `preA:pre-rm2-integration-recon-10`, `preB:pre-commits-25`, `preA:pre-commits-22`, `preA:pre-commits-42` · Artifacts: `docs/plans/rm2-integration.md`, `tools/rm2_fharness.py`, `713b337`, `b37479c`, `core/refactoring_classifier.py`

> **Decision: Path D.** 66.7% recall sits in the 50-80% bracket.
>
> — `2026-05-05_pre-rm2-integration-recon.txt:112`

> Extract/Move refactorings are systematically missed by file-level → fall
>
> — `2026-04-15_pre-commits.txt:247`

### <a id="d-090"></a>D-090 — R0 declares the -bc equivalence question moot and defers coverage validation to R1

`2026-05-05` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Two R0 open questions are closed rather than pursued: the wrapper uses `detectAtDirectories` (Path API form) exclusively on both the file-level and project-tree axes and never invokes the CLI `-bc` form, so the detectAtDirectories-vs-`-bc` equivalence question is moot; and R0 deliberately does not enumerate the full 2.4.0 refactoring-type roster, deferring coverage validation to R1 once the tagger runs across the Schesch n=50, with detector types added only in 3.0.x out of scope along with the version pin.

**Why.** Since the CLI `-bc` form is never invoked the equivalence question does not arise; the question that matters for Path B/C/D selection is file-level versus project-level recall using the same API, which the F-harness measures. Full coverage validation belongs to R1 because only then does the tagger run across the whole scenario set, and the 2.4.0 roster is the published TSE-2020 set with later additions excluded by the pin.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-recon-15`, `preA:pre-rm2-integration-recon-16` · Artifacts: `docs/plans/rm2-integration-recon.md`

> **Moot for this pipeline** — the wrapper exclusively uses `detectAtDirectories` (Path API form) on both axes
>
> — `2026-05-05_pre-rm2-integration-recon.txt:143`

> R0 did not exhaustively enumerate the refactoring types RM 2.4.0 supports — full coverage validation belongs to R1 once the tagger runs across the Schesch n=50.
>
> — `2026-05-05_pre-rm2-integration-recon.txt:133`

### <a id="d-091"></a>D-091 — Any future port of the cluster taxonomy to RM 3.x needs an explicit label migration table

`2026-05-06` · **proposed** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** If the cluster taxonomy is ever ported from RM 2.x to RM 3.x, the mapping must use an explicit label migration table rather than string-equality lookup on refactoring type names.

**Why.** Some 2.x labels may not exist verbatim on 3.x — `Extract And Move Method` appears on 2.4.0 but not on 3.0.13, which may split or relabel the same detection — so name equality is unsafe.

**Status.** proposed. S12 (2026-07-26): condition never fired — the RM 3.x port never happened (core/refactoring_classifier.py TYPE_TO_CLUSTERS at :79 still keys RM2 type names; RM 3.x is out of thesis scope per the adopted pin). The migration-table rule remains the recorded requirement for any future port.

**Source.** `preA:pre-rm2-vs-rm3-differences-07` · Artifacts: `docs/plans/rm2-vs-rm3-differences.md`

> Some 2.x labels may not exist verbatim on 3.x — the cluster mapping needs an explicit migration table, not a string-equality lookup.
>
> — `2026-05-06_pre-rm2-vs-rm3-differences.txt:157`

### <a id="d-092"></a>D-092 — Adopt a seven-cluster taxonomy keyed on kind of three-way merge difficulty

`2026-05-13` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** The RM2 cluster taxonomy is reframed on one principled criterion — kind of three-way merge difficulty — with the clusters MIGRATE_DECL, INTRA_BODY, SYMBOL_CASCADE, CONTAINER_MOVE, HIERARCHY_RESHAPE, LOCAL_DECL_EDIT, NONE and a hardest-for-line-merge-first precedence order, and these identifiers become code symbols in R4a. The 98-entry display-name → frozenset[Cluster] map is derived by reflection over org.refactoringminer.api.RefactoringType inside the pinned Docker image, with a drift-detection test asserting 98 entries and a test showing unknown types degrade gracefully.

**Why.** The previous taxonomy mixed lexical and structural criteria, whereas "what makes each refactoring hard for a line-based merger" is precisely the question the composition pipeline's dispatch is meant to answer. Reflection plus the 98-entry assertion proves graceful degradation if RM2 grows the enum: an unknown type contributes NONE and is dominated by any known higher-priority cluster.

**Status.** adopted. Supersedes: *the previous mixed lexical/structural cluster taxonomy*.

**Source.** `preA:pre-commits-37`, `preA:pre-commits-43` · Artifacts: `976e4b0`, `b37479c`, `docs/plans/rm2-integration.md`, `core/refactoring_classifier.py`, `tests/test_cluster_classifier.py`

> structural criteria to one principled criterion: **kind of 3-way merge
>
> — `2026-04-15_pre-commits.txt:511`

> Added test_unknown_type_dominated_by_known: proves graceful
>
> — `2026-04-15_pre-commits.txt:654`

### <a id="d-093"></a>D-093 — Ship regex call-site detection for the rename lane with Joern as the documented escape hatch

`2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Stale callers are detected with the regex `\b<old_name>\s*\(`, knowingly false-positive on old names in string literals and comments, missing method references (`Foo::foo`), and for Rename Class catching only constructor calls rather than type declarations, static-member access or extends clauses. Upgrading to a Joern call-site query is deferred and triggered only by a precision complaint on realistic scenarios.

**Why.** Acceptable for the MVP per the plan's regex-precision risk row: ship regex first and upgrade only if R3 shows precision problems on realistic scenarios, with the Joern call-site query kept as the documented escape hatch.

**Status.** adopted.

**Source.** `preA:pre-commits-53`, `preA:pre-rm2-integration-22` · Artifacts: `semantic_merge_driver/strategies/rm2_strategies/rename_conflict.py`, `0d52fdb`

> false-positives on old-name in string literals / comments. Acceptable
>
> — `2026-04-15_pre-commits.txt:1002`

> Acceptable for MVP per the plan's regex-precision risk row; upgrade-to-Joern remains the documented escape hatch.
>
> — `2026-04-22_pre-rm2-integration.txt:240`

### <a id="d-094"></a>D-094 — Correct the Rename Class codeElement shape and pin it with a probe test

`2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** RM2 2.4.0's Rename Class `codeElement` is a fully-qualified class name as a single token (`com.example.OldName`), not the declaration string (`public class OldName`) the original implementation assumed; `_extract_identifier` now takes the last dot-separated component after the last whitespace token, and an image-gated shape-probe test pins the contract.

**Why.** The old extractor returned the whole FQN, so the regex never matched at call sites because callers write `new OldName(...)` rather than the FQN. The shape-probe test exists so that a shape change on a future RM2 upgrade is detected rather than silently mis-parsed.

**Status.** adopted. Supersedes: *the assumption that Rename Class codeElement is a declaration string*.

**Source.** `preA:pre-commits-55`, `preA:pre-rm2-integration-23` · Artifacts: `c099187`, `strategies/rm2_strategies/rename_conflict.py`, `semantic_merge_driver/tests/test_rename_conflict.py`

> **Actual RM2 2.4.0 output:** codeElement for Rename Class is the
>
> — `2026-04-15_pre-commits.txt:1027`

> fully-qualified class name as one token, e.g. `"com.example.OldName"` (NOT `"public class OldName"` as the original implementation assumed)
>
> — `2026-04-22_pre-rm2-integration.txt:238`

### <a id="d-095"></a>D-095 — Keep a parity-tested copy of the runtime taxonomy so empirical clusters equal runtime clusters

`2026-05-18 → 2026-05-20` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Ali chose the parity-tested copy and the skip-when-absent test against Claude's recommendations; the basename staging, the withdrawal and the timeout fix are Claude's.*

**Decision.** categorizer.py carries a byte-exact copy of the driver's Cluster enum, 98-entry TYPE_TO_CLUSTERS and PRECEDENCE, guarded by a parity test that imports the driver module by file path — chosen over the sys.path cross-project import recommended in Phase 0; the test pytest.skips when the driver source is absent and hard-fails only on real drift. The tagger stages files basename-only to replicate R4a's _detect_pair. The unconditional claim "empirical cluster == runtime cluster" was withdrawn as overstated once the tagger's RM2_TIMEOUT_SECONDS = 300 was found to diverge from R4a's 120, and the tagger timeout was then aligned to 120s so the claim holds by construction. A separate assessment — that nothing had ever run the classifier over the real 50 scenarios — was also retracted.

**Why.** Staging basename-only makes the empirical cluster equal the runtime cluster the dispatcher would assign. Hard-coupling the two projects' filesystem layout would turn the whole merge-tool-comparison suite red for an unrelated reason if the subproject were checked out alone, and parity unverifiable is not parity violated. Fixing the timeout divergence at the root makes the equivalence claim true rather than merely caveated. And because the tagger's docstring states it mirrors _detect_pair exactly, the per-cluster pivot already in reports/results.csv is the runtime cluster distribution over the 50 — so the proposed classifier-over-the-50 runner was not the missing step.

**Status.** adopted. Supersedes: *the Phase 0 recommendation to import the taxonomy from semantic_merge_driver via a sys.path shim*; *R2's hard-fail test_driver_source_present assertion (2b95aa3)*.

**Cross-theme.** *depends-on* → [D-133](#d-133) — other_uid a:dc624d63-02 is cited there: the ours-union-theirs axis (and its accepted doubled RM2 cost) the equivalence claim rests on.

**Cross-theme.** *depended on by* ← [D-255](#d-255) (see the reconciliation note there)

**Source.** `a:20b53f98-08`, `a:20b53f98-19`, `a:20b53f98-11`, `a:20b53f98-20`, `a:20b53f98-21`, `a:e1df1610-01` · Artifacts: `merge-tool-comparison/src/evaluation/categorizer.py`, `merge-tool-comparison/tests/test_categorizer.py`, `merge-tool-comparison/tools/rm2_tag.py`, `merge-tool-comparison/reports/results.csv`, `eabaddd`, `cbac926`

> Stage files **basename-only** to match R4a's `_detect_pair` exactly, so the empirical cluster == the runtime cluster.
>
> — `2026-05-18_20b53f98.txt:127`

> **3. "Empirical cluster == runtime cluster" is overstated.** Confirmed divergence: tagger `RM2_TIMEOUT_SECONDS = 300` vs R4a runtime `= 120`.
>
> — `2026-05-18_20b53f98.txt:251`

### <a id="d-096"></a>D-096 — Stage B widens coverage before fixing false positives, and widens nothing for DFI or loop bounds

`2026-06-11` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Stage-B priority order is fixed as: (1) widen R3 — RM2 rename types beyond Method/Class, per-branch RM2 on base→ours and base→theirs with a merged-consistency scan, plus a cheap unresolved-identifier check; (2) JoernInfiniteLoop false-positive fixes, namely flagging only loops absent from both parents, restricting the query to WHILE/DO/FOR, and adding exit-path awareness; (3) explicitly no DFI or loop-bounds widening. Change-Return-Type detection is skipped as pilot-overfit and kept on record as a refuted design.

**Why.** The adjudicated base rates put 8 of 13 attributable misses in the #6 rename/decl-change family with 5 compile errors, and zero misses in the already-covered categories #3/#5, so coverage widening beats FP-fixing and there is zero evidence in 23 real misses for DFI or loop bounds; a single-file unresolved-identifier check alone catches the confirmed compile errors. The three InfiniteLoop changes would have zeroed all five pilot false positives, and the other detectors produced no false alarms. Change-Return-Type was judged pilot-overfit and retained as thesis material — a refuted detector design with a named cause.

**Status.** adopted.

**Source.** `b:bfc672b4-05`, `a:bfc672b4-07`, `a:bfc672b4-03`, `a:bfc672b4-13` · Artifacts: `merge-tool-comparison/ISSUES.md #29`, `semantic_merge_driver/strategies/joern_strategies/infinite_loop.py`, `reports_detection/pilot/FINDINGS.md`, `merge-tool-comparison/reports_detection/pilot_v2/FINDINGS.md`

> Notably **zero** misses fall in the already-covered categories #3/#5 — coverage widening beats FP-fixing.
>
> — `2026-06-11_bfc672b4.txt:138`

> make `JoernInfiniteLoop` differential (only flag loops absent from both parents — would have zeroed all 5 FPs), restrict its query to WHILE/DO/FOR, add exit-path awareness. The other detectors need no FP fixes.
>
> — `2026-06-11_bfc672b4.txt:112`

### <a id="d-097"></a>D-097 — Add JoernUnresolvedReference as a differential-only detector that abstains without parents

`2026-06-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** A new strategy JoernUnresolvedReference flags identifiers unresolved in the merged file but resolvable in both parents (refsTo-based), abstains entirely when parents are missing, fails closed once analysis has started, and is enabled in strategies.yaml. No Stage-B detector is implemented without first probing what RM2 2.4.0 and Joern actually report for the new refactoring and query shapes.

**Why.** The detector targets the four confirmed compile-error shapes among the adjudicated misses, and abstaining without parents is deliberate because the detector is differential by construction. Probing first means the design is grounded in verified tool behaviour rather than assumption — including negative findings such as static-final constant renames not being reported and `<operator>.throw` being confirmed.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-002](#d-002) (see the reconciliation note there)

**Source.** `a:bfc672b4-10`, `a:bfc672b4-09` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`, `semantic_merge_driver/config/strategies.yaml`

> differential-only — flags identifiers unresolved in merged but resolvable in both parents (`refsTo`-based, probe-verified no phantom locals)
>
> — `2026-06-11_bfc672b4.txt:261`

> All probes done — `<operator>.throw` confirmed. The Stage-B design is fully grounded in verified tool behavior.
>
> — `2026-06-11_bfc672b4.txt:238`

### <a id="d-098"></a>D-098 — Make JoernUnresolvedReference the primary detector and reorganise strategies into yield tiers

`2026-06-11` · **proposed** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Two architecture recommendations from the Stage-B close-out: designate JoernUnresolvedReference "first among equals" in the gate — the one detector to ship if only one could be — and make its differential-only, abstain-without-parents design the template new detectors follow; and reorganise strategies/ from one-file-per-taxonomy-category into cost/yield tiers (Tier 0 parse/compile sanity, Tier 1 generic differential name-resolution consistency, Tier 2 declaration-change consistency via per-branch RM2, Tier 3 category-specific queries kept as labelled low-yield coverage).

**Why.** JoernUnresolvedReference produced 7 file-flags with zero false positives and zero crashes and independently corroborated 5 of the RM2 hits, while every detector that skipped merge-induced filtering died of false positives. All observed true positives flow through the generic name-resolution lane, so the per-category layout does not reflect the measured cost/yield structure — the cheapest check would have caught the largest catchable share.

**Status.** proposed. S12 (2026-07-26): split outcome — the template half was realized in practice (the differential/abstain design is the shipped standard: the D3 widening extended exactly this lane, and every new lane follows the differential template per ISSUES #31), but the strategies/ cost/yield-tier reorganisation never happened: the tree is still one-directory-per-tool (joern_strategies/, rm2_strategies/, text_strategies/) as of 2026-07-26.

**Cross-theme.** *depends-on* → [D-307](#d-307) — other_uid a:bfc672b4-25 landed there: the shared-CPG refactor paired with the tier reorganisation in the same close-out. See extra_edges: that proposal was later declined by scope-architecture/[D-023](#d-023).

**Source.** `a:bfc672b4-33`, `a:bfc672b4-24` · Artifacts: `semantic_merge_driver/strategies/`, `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`

> Architecturally it earns "first among equals" status in the gate: if you had to ship exactly one detector, it's this one. Its differential-only design (abstain without parents) also sets the template new detectors should follow.
>
> — `2026-06-11_bfc672b4.txt:677`

> Today `strategies/` is laid out one-file-per-category (#3, #5, #6). The findings suggest the real structure is cost/yield tiers:
>
> — `2026-06-11_bfc672b4.txt:477`

### <a id="d-099"></a>D-099 — Harden the unresolved-identifier lane against parser artifacts by keying on name only

`2026-06-11` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** After the first v2 attempt flagged 4 of the first 7 positives, exclude `$`-prefixed synthetics, re-key the identifier lane by name only instead of by (method, name), and restrict the type lane to named-method parameters.

**Why.** Inspection showed all four flags were parser artifacts rather than merge semantics: javasrc2cpg's auto-numbered lowering temporaries (`$obj178`) and lambda method names (`<lambda>20`) shift between file versions, defeating (method, name) differential keys.

**Status.** superseded. Superseded by [D-100](#d-100) — Drop the type-resolution lane; import-deletion breakage is out of v2 scope.

**Source.** `a:bfc672b4-11` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`

> inspection showed all four were **parser artifacts, not merge semantics**: javasrc2cpg's auto-numbered lowering temporaries (`$obj178`) and lambda method names (`<lambda>20`) shift between file versions, defeating `(method, name)` differential keys
>
> — `2026-06-11_bfc672b4.txt:291`

### <a id="d-100"></a>D-100 — Drop the type-resolution lane; import-deletion breakage is out of v2 scope

`2026-06-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The type lane is removed from JoernUnresolvedReference, leaving it identifier-lane only, and the jnr test is rewritten to document the abstention: import-deletion breakage is explicitly out of v2 scope.

**Why.** javasrc2cpg's type inference proved version-unstable on real files — the lane flagged "import merged away" on a merged file byte-identical to the developer's resolution that demonstrably compiled. The general lesson recorded is that a detector lane survives only if it is stable under the parser's per-version quirks, not merely correct on fixtures.

**Status.** adopted. Supersedes: [D-099](#d-099) — Harden the unresolved-identifier lane against parser artifacts by keying on name only.

**Source.** `a:bfc672b4-12` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`

> import-deletion breakage is explicitly out of v2 scope because javasrc2cpg's type inference proved version-unstable on real files — the lane flagged "import merged away" on a merged file that was byte-identical to the developer's resolution and demonstrably compiled
>
> — `2026-06-11_bfc672b4.txt:308`

> each detector lane survives only if it's stable under the parser's per-version quirks, not just correct on fixtures
>
> — `2026-06-11_bfc672b4.txt:310`

### <a id="d-101"></a>D-101 — Proposed upgrade ladder: tree-sitter-java tactically, differential ecj strategically

`2026-06-11 → 2026-07-16` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Two rungs are proposed for moving the text-scanning half of the detection layer to parser-grade analysis: tactically, replace the regex declaration heuristics with tree-sitter-java (error-tolerant, no JVM, pure-Python wheel) keeping the differential/absorption algorithm byte-for-byte intact; strategically, run the Eclipse batch compiler (`-proceedOnError`, `--release 17`, no classpath) on merged/ours/theirs, key errors by (error-id, symbol) never by line, and flag `errors(merged) − errors(ours) − errors(theirs)`, which subsumes the absorption guard and the hand-typed JDK sets and generalises past imports.

**Why.** Every defect lived in the regex half of the box and none in the RM2 half, and the comment-stripper newline bug shows hand-rolled lexing of Java in a research detector is a liability the architecture should shed. The stated reason for going textual was a Joern/javasrc2cpg nondeterminism failure, which argues against heavyweight semantic inference, not against exact syntactic parsing — the regex lexer and tree-sitter sit in the same no-resolution class, one just lexes Java correctly — making it the cheapest meaningful upgrade with no new failure modes. The existing design falls out of error-set subtraction naturally: the absorption guard becomes subtraction, ecj knows the JDK including the missing Map, generics, shadowing, multi-declarators and patterns come free, and any single-file-visible compile break including the four Stage-A compile-error misses falls out of the same subtraction — at the price of a JVM per version and error-normalisation discipline.

**Status.** superseded. S12 (2026-07-26): neither rung taken — no tree_sitter dependency exists in the driver (only the comparator uses tree-sitter, its own codebase) and no ecj harness exists. The same-day adopted decision to keep the lane dependency-free governs; the zero-FP suppression design was chosen over parser-grade analysis. Superseded by [D-120](#d-120) — Defer tree-sitter token classification to keep the import lane dependency-free.

**Source.** `a:bfc672b4-32`, `a:734e4529-09`, `a:734e4529-10` · Artifacts: `semantic_merge_driver/strategies/rm2_strategies/rename_conflict.py`, `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`

> the Joern failure argues against heavyweight *semantic* inference, not against exact *syntactic* parsing. Cheapest meaningful upgrade, no new failure modes.
>
> — `2026-07-16_734e4529.txt:88`

> Differential ecj is the strategic one — it replaces this lane's entire guard stack with a compiler and gives the next detector categories for free, at the price of a JVM in the loop.
>
> — `2026-07-16_734e4529.txt:105`

### <a id="d-102"></a>D-102 — Fix the two var-lane FP defects and re-run, with tests proven discriminating, across two rounds

`2026-06-20 → 2026-07-02` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Claude identified the defects and produced the runs; the decisions to do the post-fix run at all and to disclose a second round were taken with Ali.*

**Decision.** The two confirmed var-lane defects behind all four R1 false positives — matches immediately followed by `(` not being skipped, and `\n` not excluded from the char-literal class — are fixed and a separately labelled post-fix run is produced: the cached verdicts of the four untouched detectors are migrated to the new commit as exact carry-over and only the RM2RenameConflict lane is recomputed. Each fix ships with a regression test demonstrated to fail on pre-fix code and pass post-fix. When round 1 exposed two residual one-character guard defects (generics wildcard, lambda parameters) they were fixed and a second run was made, disclosed as "round 2", documenting the trail frozen 4/193 → round-1 3/193 → round-2 0/193; the tcurdt detection was retired as defect-dependent, making post-fix R2 11/164 rather than the predicted 12/164.

**Why.** The outcome was predictable because the fixes can only remove matches, and carry-over made the run cheap (~1 h rather than 9 h) while avoiding injecting Joern's margin nondeterminism; leaving known one-line defects in shipped code behind a "plausibly ~0%" hypothesis invites the committee question "the run was cheap — why didn't you do it?". The discriminating-test requirement is the standard the 2026-05-16 audit demanded: a test that passes on both pre- and post-fix code proves nothing. The tcurdt flag had to be retired because, although the merge really fails, the flag existed only because of the missing call-site exclusion and cannot be claimed post-fix.

**Status.** adopted. Supersedes: *the prediction that post-fix R2 would stay at 12/164*.

**Cross-theme.** *depended on by* ← [D-184](#d-184) (see the reconciliation note there)

**Cross-theme.** *duplicated by* ← [D-260](#d-260) (see the reconciliation note there)

**Source.** `a:0e14484d-11`, `a:fb0fa5c5-37`, `b:fb0fa5c5-59`, `b:fb0fa5c5-58`, `a:fb0fa5c5-39`, `b:fb0fa5c5-57` · Artifacts: `ISSUES.md #29`, `5ed92a2`, `f964354`, `45a87e6`, `merge-tool-comparison/ISSUES.md:696`, `tools/detect_validate.py`

> leaving one-line defects in shipped code with a "plausibly ~0%" hypothesis invites the obvious committee question: *"the run was cheap — why didn't you do it?"*
>
> — `2026-06-24_fb0fa5c5.txt:2064`

> Two regression tests **proven discriminating** (fail on pre-fix code, pass post-fix) — the exact standard the 2026-05-16 audit demanded
>
> — `2026-06-24_fb0fa5c5.txt:2089`

### <a id="d-103"></a>D-103 — Upgrade the stale-read detector to a Joern DDG query and bring loop bounds to v2 parity

`2026-06-24` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Two remedies recommended for the weakest detectors: replace the line-ordering heuristic in the stale-read (category #3) detector with a real Joern DDG reachability query using `reachableBy` on the already-built CPG; and strip the `--- START JOERN ANALYSIS ---` / `[DEBUG]` / `print(output)` stdout noise from invalid_loop_bounds.py and bring it to v2 differential parity with its three peers, or explicitly document why it stays non-differential.

**Why.** The CPG is already built, so the DDG change is modest effort and closes the biggest FP/FN credibility gap in the detection layer, directly answering whether this is real dataflow analysis. invalid_loop_bounds.py is the weakest, FP-prone detector — pre-Stage-B vintage left un-modernised, lacking the merge-induced filter its peers have — and the most likely to draw a committee question.

**Status.** superseded. S12 (2026-07-26): neither remedy was applied — taint_check.py contains no reachableBy query (0 occurrences), and invalid_loop_bounds.py still carries the '--- START JOERN ANALYSIS ---'/[DEBUG]/print(output) noise at :34/:59/:95. The detector cycle deliberately targeted the census mass instead, and the 2026-07-18 decision recorded the legacy detectors as fire-nothing heuristics — that recording is the superseding disposition. Superseded by [D-127](#d-127) — Record the legacy Joern detectors as heuristics that fire nothing in the wild.

**Source.** `a:ce56e78d-07`, `a:ce56e78d-11` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/taint_check.py`, `semantic_merge_driver/strategies/joern_strategies/invalid_loop_bounds.py`

> **Upgrade the stale-read detector from line-ordering to a real Joern DDG reachability query.**
>
> — `2026-06-24_ce56e78d.txt:47`

> **not differential** (no merge-induced filter like its 3 peers); `WARNING` severity. Pre-Stage-B vintage left un-modernized.
>
> — `2026-06-24_ce56e78d.txt:99`

### <a id="d-104"></a>D-104 — Withdraw the 66.7% file-level recall figure; n=50 measures 90.7% and the design stands

`2026-07-03` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Ali chose the opt-in project-level mode reusing the existing harness; Claude produced the measurement, the withdrawal and the no-code-change recommendation.*

**Decision.** Project-level tagging was implemented as an opt-in `--project-level` mode of tools/rm2_tag.py reusing the git-worktree machinery of tools/rm2_fharness.py, and the R0 recon claim that file-level RM2 recall is 66.7% of project-level was replaced by the n=50 measurement of 90.7% [83.8, 94.9] pooled (98/108; ours 81.6%, theirs 98.3%), with the n=10 figure recorded as an outlier artifact. No code or design change follows: file-level RM2 remains the runtime design.

**Why.** The sole gap-driver of the n=10 sample (ab0oo_javaprslib, four cross-file refactorings) reproduces exactly in the larger run — it was the extreme, not the norm. File-level is a strict subset (only-file = 0 across 108 occurrences), so the errors are misses only and never spurious; cluster impact is 2/50 flips with just 1/50 a false-NONE, which fails safe to the conservative git backend, so the number strengthens rather than undermines the file-level R4a design.

**Status.** adopted. Supersedes: *the R0 recon's 66.7% n=10 file-level recall figure*.

**Cross-theme.** *depended on by* ← [D-318](#d-318) (see the reconciliation note there)

**Source.** `a:7b3b2669-02`, `a:7b3b2669-11`, `a:7b3b2669-13` · Artifacts: `merge-tool-comparison/tools/rm2_tag.py`, `merge-tool-comparison/reports_rm2_recall/FINDINGS.md`, `merge-tool-comparison/ISSUES.md #26`, `THREATS_TO_VALIDITY.md §3`, `c9ca9f8`

> file-level RM2 recall is 90.7% [83.8, 94.9] of project-level at n=50 — the n=10 figure of 66.7% was an outlier artifact.
>
> — `2026-07-03_7b3b2669.txt:104`

> no code change recommended — the number *strengthens* the file-level R4a design.
>
> — `2026-07-03_7b3b2669.txt:112`

### <a id="d-105"></a>D-105 — Scope the detector cycle to two new lanes plus one widening, targeting the census mass

`2026-07-15 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

*Actors note: The retrospective summary source is unattributed; the plan decisions are Claude's, frozen with Ali's ratification of the plan document.*

**Decision.** The D1–D3 cycle builds exactly three things and no more: D1 ImportPruneUsage (pure-textual differential) for stale-usage-of-pruned-import (12.7% census mass), D2 SignatureStaleCall (RM2 arity-primary) for stale-caller-of-changed-signature (10.2%), and D3 a flag-gated textual widening of JoernUnresolvedReference for gap-inventory shapes S1/S1b/S2/S3 (~8%). Overlapping-edit-interleaving, stale-expectation-of-changed-behavior and all categories at or below 2.2% are excluded. The frozen plan carries only shape sketches and non-negotiable guard lists (and no shapes at all for D3); parsing approach, AST/tree-sitter versus Joern choices, data structures and lane wiring are left to the build sessions reading specs.csv and gap_inventory.md.

**Why.** The two largest census categories had no detection logic at all and the driver detected only slices of the renamed/removed group, so that is where the lanes go. Interleaving detection carries high FP risk against the zero-FP bar, "which is the layer's whole differentiator"; behavioural shapes are out of reach by mechanism, not by effort; small categories give near-vacuous confidence intervals; and every added detector is added FP surface, so three focused lanes beat six speculative ones. Implementation detail was withheld from the frozen plan because it was not knowable at pre-registration time without guessing, and guessed implementation detail in a frozen document would have been a liability — either wrong and needing amendments, or wrong and silently obeyed.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-029](#d-029) — other_uid a:cfe6365a-09 is cited there: the codebook/census the cycle's two target categories come from.

**Source.** `a:4c7b0828-24`, `a:dc3bc182-sub-sub-agent-a495a0-06`, `a:4c7b0828-35` · Artifacts: `outputs/detector-cycle-plan.md`, `ISSUES.md #31`, `10b7528`, `reports_detectors/specs/specs.csv`, `reports_detectors/specs/gap_inventory.md`

> ## How many: 2 new detectors + 1 widening — not more
>
> — `2026-07-06_4c7b0828.txt:1527`

> Every added detector is added FP surface; three focused lanes beat six speculative ones.
>
> — `2026-07-06_4c7b0828.txt:1539`

> the gap the taxonomy exposed: the two largest census categories had *no detection logic at all*, and the driver detected only slices of the renamed/removed group.
>
> — `2026-07-18_dc3bc182_sub-agent-a495a0.txt:62`

### <a id="d-106"></a>D-106 — No LLM-backed detector lane; detectors are deterministic static analysis with a zero-FP bar

`2026-07-15 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

*Actors note: The retrospective summary source is unattributed; the ruling itself is Claude's.*

**Decision.** Detectors D1–D3 must be deterministic static-analysis code in strategies/; there is no LLM-backed detector lane and no Batch API use in the build or the evaluation, and every detector must clear a standing zero-false-positive bar on controls before passing its gate.

**Why.** Circularity is the fatal objection: the held-out labels were produced by `claude-opus-4-8` closed coding, so an Opus-based detector evaluated against Opus-produced labels is the model grading its own homework. Architecturally an LLM lane is nondeterministic, costs money per merge, needs network at merge time and has unknown FP behaviour — a different and weaker thesis. The rule is encoded in the plan with its rationale so no later session re-invents the shortcut.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-180](#d-180), [D-220](#d-220) — The closed-LLM-coding instrument behind the circularity rationale, and the drafts-not-oracles discipline it runs under.

**Cross-theme.** *in tension with* ← [D-004](#d-004) (see the reconciliation note there)

**Source.** `a:4c7b0828-25`, `a:dc3bc182-sub-sub-agent-a495a0-09` · Artifacts: `outputs/detector-cycle-plan.md §2 N1`, `merge-tool-comparison/reports_detectors/`

> **Circularity, the fatal one:**
>
> — `2026-07-06_4c7b0828.txt:1583`

> the no-LLM-detector rule (§2 N1) is encoded with the circularity rationale so no session re-invents that shortcut
>
> — `2026-07-06_4c7b0828.txt:1729`

### <a id="d-107"></a>D-107 — One narrow carve-out: a Batch API pass for fixture and spec extraction on derivation data

`2026-07-15` · **adopted** · `[chat]` · corroboration: single-pass · confidence: high · actors: claude

**Decision.** A single cheap Batch API pass over the roughly 70 attributed derivation units is permitted, before the build, to extract machine-readable fixture and spec details (the exact pruned import and stale usage line; the exact old/new signature and stale call site) — the only sanctioned LLM use inside the detector cycle.

**Why.** It is methodologically clean because it is development-side tooling on derivation data (derivation split only — firewall), not measurement, and it plausibly saves half a day to a day of the build for a couple of dollars.

**Status.** adopted.

**Cross-theme.** *in tension with* ← [D-004](#d-004) (see the reconciliation note there)

**Source.** `b:4c7b0828-32` · Artifacts: `reports_detectors/specs/specs.csv`

> One narrow slot: **fixture and spec extraction before the build.** A single cheap batch over the ~70 attributed derivation units (derivation split only — firewall)
>
> — `2026-07-06_4c7b0828.txt:1588`

> It's methodologically clean because it's *development-side tooling on derivation data*, not measurement.
>
> — `2026-07-06_4c7b0828.txt:1588`

### <a id="d-108"></a>D-108 — Restrict D2 to the same-file arity-change shape and document the rest as false negatives

`2026-07-16 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: The retrospective summary source is unattributed; the flag and the resolution are Claude's.*

**Decision.** D2 SignatureStaleCall detects arity changes only. The finding that arity changed in just 7 of 14 D2 spec units (5 of 9 in the file-local target set) was first raised as an open flag for the S-D3 session rather than decided at plan time; S-D3 then resolved it by shipping arity-only and documenting the return-type, parameter-type and throws shapes (4 of 8 usable derivation units) as false negatives, with the standing honest framing "partial — arity-mismatch shape".

**Why.** Plan §2 makes arity the primary signal and orders FN over FP; detecting the non-arity shapes needs type-level reasoning that a single-file, classpath-less view cannot do reliably, and would revive the javasrc2cpg type-inference approach Stage B built and dropped for nondeterminism, while GD2/GD3 demand literally zero flags on the controls. The resulting half-category recall ceiling is therefore not a failure mode but the designed FN cost of the conservative bias. The split was recorded as a paste-time fact so it would not be rediscovered, with the call left to the session that owned it.

**Status.** adopted.

**Source.** `a:4c7b0828-36`, `a:506d875b-13`, `a:acf7e1d0-02`, `a:dc3bc182-sub-sub-agent-a495a0-10` · Artifacts: `ISSUES #31`, `reports_detectors/specs/specs.csv`, `reports_detectors/specs/gap_inventory.md`, `outputs/detector-cycle-plan.md §2`

> That's not a failure mode — it's the designed FN cost of the conservative bias, and it gets the standing honest framing ("partial — arity-mismatch shape").
>
> — `2026-07-15_506d875b.txt:151`

> Resolved: those shapes are documented FNs; typing arguments file-locally would revive the dropped Stage-B type-inference approach.
>
> — `2026-07-16_acf7e1d0.txt:54`

### <a id="d-109"></a>D-109 — Declare cross-file shapes out of file-local reach and record them as the FN ceiling

`2026-07-16 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Claude drew the reach boundaries and reported the measured zero; the requirement to record uncovered shapes and their reasons came from Ali's session prompt.*

**Decision.** The detection layer's evidence horizon is a single file, because git merge drivers run per file and the driver's analyze() is per-file. Units whose changed declaration and stale calls live in different files are declared out of reach rather than pursued; D3's scope was cut to file-local shapes after GD1 machine-scored 37/48 = 77.1% (Amendment 2, rescored 37/39 = 94.9% PASS), with cross-file S4 (class relocation) and S5 (external API rename, e.g. javax→jakarta) excluded by construction and recorded as the documented FN ceiling. A sub-shape rejected list (bare type positions merged-side, `this.`-qualified method calls, type-parameter shadowing, partial overload removals) is documented in the lane header as deliberately uncovered, and every close-out must list the inventoried shapes deliberately not covered together with the reason. D2's measured zero positives on the Stage-C instrument is reported as this ceiling being honest and predicted, the lane credited as existence-proven by the one developer-confirmed control catch.

**Why.** Cross-file shapes are out of file-local reach by construction, so no amount of effort inside the lane reaches them, and the session prompts' own guard lists already suppress cross-file targets the file-local view cannot type. The reporting rule follows the plan's §2 rejected-list logic applied at shape level: FP risk beats coverage. D2's zero is kept and reported rather than fixed or removed because the ceiling was measured and predicted, and the yubico control catch supplies the existence proof that the shape occurs catchably in the wild.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-453](#d-453), [D-029](#d-029) — other_uid b:6296f4f6-09 landed in the crosswalk entry; the census masses that define what the ceiling excludes are in the recode entry.

**Source.** `a:acf7e1d0-03`, `a:dc3bc182-sub-sub-agent-a495a0-08`, `a:06ec13eb-16`, `a:82dd479f-13`, `a:82dd479f-04` · Artifacts: `merge-tool-comparison/reports_detectors/`, `ISSUES.md #31`, `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`, `outputs/detector-cycle-plan.md §2`, `9580e1f`

> the driver's `analyze()` is per-file (git merge drivers run per file), and the prompt's own guard list suppresses "cross-file targets the file-local view cannot type"
>
> — `2026-07-16_acf7e1d0.txt:55`

> S4/S5 cross-file shapes (out of file-local reach by construction)
>
> — `2026-07-16_82dd479f.txt:295`

### <a id="d-110"></a>D-110 — Widen JoernUnresolvedReference with a flag-gated textual differential, fixed at the shared root

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: One retrospective summary source is unattributed; the design and fixes are Claude's.*

**Decision.** The four in-reach gap shapes (bare and `this.`-qualified field references, removed methods still called, removed inner types still constructed) are covered by a flag-gated textual removed/renamed-declaration differential added inside the existing JoernUnresolvedReference lane, with flag-off behaviour byte-identical to before; the arrow-matching regex is converted to lookahead form and `_widened_issues` plus the usage scanner rewired to a (names, offsets) pair; the false-positive vectors surfaced by the review (multi-declarators, `case ->` phantoms, lambda scope-blindness, JLS 6.5.2 receiver re-binding, label positions, Java-14 multi-label case, bare-position remover absorption) are repaired in the shared helper `_qualified_or_case` rather than locally, with D1's full lane suite re-run against the shared change. RM2RenameConflict is deliberately not touched.

**Why.** The headline target is the Joern both-parents-guard self-defeat: when one side removes or renames a field the old name is unresolvable in that parent, so the "resolvable in both parents" rule suppresses exactly the merge-induced case it exists to catch. Flag-gating with byte-identical flag-off behaviour is what satisfies the session's regression floor, and the genuinely Joern-invisible shapes (`this.`-qualified, calls, types) are what drove the widening. The consuming arrow regex swallowed multi-parameter lambdas whole, missing the second parameter as an enumerator. Fixing at the shared root means the D1 lane inherits the correction instead of each lane carrying its own patch. No inventoried gap shape is an RM2-record shape, so the rename lane needs no change.

**Status.** adopted.

**Source.** `b:506d875b-13`, `a:82dd479f-09`, `a:82dd479f-05`, `a:82dd479f-10`, `a:82dd479f-12`, `a:dc3bc182-sub-sub-agent-a495a0-07` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`, `732d8ff`, `merge-tool-comparison/reports_detectors/tune_d3/review_record.md`, `reports_detectors/specs/gap_inventory.md`, `ISSUES #31`

> The headline S-D4 target is the **Joern both-parents-guard self-defeat**: when one side *removes or renames* a field, the old name is unresolvable in that parent, so the "resolvable in both parents" rule suppresses exactly the merge-induced case it exists to catch.
>
> — `2026-07-15_506d875b.txt:137`

> Flag-off behavior byte-identical.
>
> — `2026-07-16_82dd479f.txt:199`

### <a id="d-111"></a>D-111 — Let flag-ON widened issues ride along after the fail-closed inconclusive Issue

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** In _fail_closed(), when SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS is ON, widened issues are appended after the single "inconclusive" Issue; flag-OFF the shape is unchanged. The consequence is accepted rather than coded around: verdict_of's "genuine issues win" rule reclassifies a Joern-broken file from UNANALYZABLE to FLAG in the flag-ON arm, so such files no longer count toward the UNANALYZABLE target-0 line or the G0 abort threshold; this is documented as deliberate and carried to S-D5 as a harness-accounting note.

**Why.** The mixed-verdict semantics are deliberate and flag-OFF behaviour is verified unchanged (widened is empty and tests pin it), so the accounting risk — Joern breakage under-reported as detections — is handled by a note to S-D5 rather than a lane change.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-184](#d-184), [D-283](#d-283) — Located by content: the UNANALYZABLE->FLAG reclassification was carried to S-D5 as a harness-accounting note (the two-arm harness) and priced into S-D8's derived flag-OFF target.

**Source.** `a:82dd479f-08`, `a:82dd479f-sub-sub-agent-a46641-04` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py:264`

> now appends widened issues after the inconclusive Issue when the flag is ON
>
> — `2026-07-16_82dd479f_sub-agent-a46641.txt:37`

> the flag-ON mixed-verdict semantics are deliberate, with an S-D5 note
>
> — `2026-07-16_82dd479f.txt:173`

### <a id="d-112"></a>D-112 — Correct the gap inventory: the baseline lane already fires on the bare-receiver shapes

`2026-07-16 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

*Actors note: The retrospective summary source is unattributed; the probe correction is Claude's.*

**Decision.** An addendum to the gap inventory records — and the refuted claim is struck from the lane module header — that the pre-existing lane already flags the bare-receiver S1/S1b minimal shapes (absent ≠ unresolved), so the datastax/jline-shaped units should be expected as baseline-arm catches in S-D5; D3's incremental-recall claim is narrowed to the yandex `this.`-qualified units plus S2 and S3.

**Why.** Established by execution probes against the engine — including a live-Joern probe — which showed the existing lane fires on those shapes, so the inventory's assumption that they were missed does not hold and they cannot count as D3-added recall.

**Status.** adopted. Supersedes: *the gap inventory's claim that the existing lanes miss the bare-receiver S1/S1b shapes*.

**Source.** `a:82dd479f-11`, `a:dc3bc182-sub-sub-agent-a495a0-12` · Artifacts: `merge-tool-comparison/reports_detectors/specs/gap_inventory.md`, `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`

> the existing lane already fires on the bare-receiver S1/S1b minimal shapes (absent ≠ unresolved), so those two units may be baseline-arm catches in S-D5
>
> — `2026-07-16_82dd479f.txt:202`

> a live-Joern probe correction found the datastax/jline bare-receiver shapes **already fire the baseline lane**, so D3's added recall must come from the yandex `this.`-qualified / S2 / S3 units.
>
> — `2026-07-18_dc3bc182_sub-agent-a495a0.txt:68`

### <a id="d-113"></a>D-113 — Review sub-agents refute the widened lane's documented safety claims and propose shared fixes

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Four documented safety claims of the widened lane are recorded as refuted by execution against the real code: the module header's "asymmetric-visibility risk is neutralized by the exactly-one-parent rule" (declarator forms _scan_var_decls cannot parse are counted as usage sites, so a clean merge is flagged CRITICAL); the inline comment that the _ARROW_DECL_RE direction "only ever ADDS a declaration entry … (FN-safe)" (matching `case MODE ->` manufactures a candidate); the registered residual FP class, which is narrower than the detector's actual scope-blindness (any deleted lambda parameter or local whose name coincides with an externally-resolved name); and the emitted message "nor retains an import covering it", which is false because the var-kind guard consults only member-import coverage. Two shared-helper fixes are proposed with them: repair the multi-label `case FOO, MODE:` exclusion in `_ipu._FileView._qualified_or_case`, and let absorption/attribution scans over parent views count bare identifier occurrences while keeping the anchor restriction for merged-site scanning.

**Why.** Each finding was reproduced by execution rather than line-reading: `_widened_issues returned flags {'b'}`, `{'MODE'}`, `{'x'}` and `{'Config'}` on merges that compile. The shared-helper placement is argued on two grounds: the same multi-label gap exists latently in D1's occurrences(), so one fix covers both lanes; and relaxing the parent-view scans is suppression-only, hence FN-safe, so it does not need the zero-FP anchor restriction that merged-side scanning requires.

**Status.** adopted. S12 (2026-07-26): the refutations were accepted and fixed before the gate rerun — ISSUES.md #31 (S-D4 record) lists '8 execution-verified FP-vector fixes' covering the named shapes (multi-declarator + C-style arrays 'refuted the header's neutralized claim', case-arrow phantoms, lambda/local scope-blindness → field-tier candidates, JLS 6.5.2 re-binding), and the shipped lane carries the fixes with '(S-D4 review, verified FP)' comments (unresolved_reference.py, field-tier and receiver-position guards).

**Source.** `a:82dd479f-sub-sub-agent-a3fb5c-01`, `a:82dd479f-sub-sub-agent-a3fb5c-02`, `a:82dd479f-sub-sub-agent-a3fb5c-03`, `a:82dd479f-sub-sub-agent-a3fb5c-04`, `a:82dd479f-sub-agent-a9ce95-01`, `a:82dd479f-sub-agent-a9ce95-02` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`, `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`

> The module header's claim that the 'asymmetric-visibility risk is neutralized by the exactly-one-parent rule' is refuted: the keeper can hold both a recognized declaration and the unrecognized one.
>
> — `2026-07-16_82dd479f_sub-agent-a3fb5c.txt:28`

> Asymmetric fix available: the absorption/attribution scans on PARENT views don't need the zero-FP anchor restriction that merged-site scanning needs
>
> — `2026-07-16_82dd479f_sub-agent-a9ce95.txt:33`

### <a id="d-114"></a>D-114 — Detector review briefs rank false-positive slips worst and require execution-reproduced findings

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

*Actors note: Claude drafted the amendment and the sub-agent briefs; Ali ratified the amendment and directed the open-source comparison leg, and one brief is attributed to Ali.*

**Decision.** Amendment 3 adds a bounded three-leg review pass to the remaining build prompts: (a) as project code with /code-review at high effort, (b) as standalone Java-semantics analysis consulting JLS, Error Prone and Checkstyle, (c) explicit comparison against named open-source comparators (Error Prone matchers, PMD, SpotBugs, IntelliJ inspections, Checkstyle) with consulted comparators and adopted/rejected divergences recorded in the close-out; fix-or-document, GD2 rerun if a gated lane changes, review before the S-D5 freeze. The finder sub-agents implementing it are scoped tightly — a line-by-line diff scan for one, five named cross-file contract families for another, four changed/new files for a third, and a simplification angle instructed to read the module docstring first and not flag guards that serve the documented FP-suppression design — each capped at six candidates, and every returned finding must be verified by concrete execution against the real detector code, not reported from line-reading.

**Why.** The project has a hard zero-false-positive bar: a false flag on a clean merge is the worst outcome while false negatives are acceptable and documented, so FP-slip paths get top severity in the hunt and guard density must not be flagged as complexity. The freeze protects measurement surfaces only, and a code-review instruction touches none of them — it is process/quality, the same epistemic category as "write unit tests" — but it had to be bounded because the open-ended wording is the kind of instruction that makes a session wander the web collecting generic advice; leg (c) was made explicit at Ali's direction after he noted it was missing. The cross-file brief was scoped by contract family because the new module deliberately imports modules rather than classes and borrows private helpers from two sibling strategies.

**Status.** adopted. Supersedes: *Amendment 3 rev. a (two-leg version without the explicit open-source comparison leg)*.

**Source.** `a:4c7b0828-37`, `b:82dd479f-sub-sub-agent-a3fb5c-01`, `a:82dd479f-sub-sub-agent-a3fb5c-05`, `a:acf7e1d0-sub-agent-afc4ad-01`, `a:acf7e1d0-sub-sub-agent-a5d889-01` · Artifacts: `outputs/detector-cycle-plan.md Amendment 3`, `22779a7`, `d437e19`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`, `semantic_merge_driver/core/plugin_loader.py`

> The project has a hard zero-false-positive bar: a false flag on a clean merge is the worst outcome; false negatives are acceptable and documented.
>
> — `2026-07-16_82dd479f_sub-agent-a3fb5c.txt:5`

> the open-source comparison is now its own explicit review leg, committed (`d437e19`) and pushed
>
> — `2026-07-06_4c7b0828.txt:1926`

### <a id="d-115"></a>D-115 — Under incomplete information the lanes suppress rather than accept precision loss

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The lanes are to err toward false negatives on ambiguity and pair the resolution-free single-file regime with explicitly documented shape restrictions — diverging deliberately from SpotBugs' acceptance of precision loss and going beyond Checkstyle's ceiling by adding three-way differential evidence; and a name match without resolution is only a candidate, with the lane's automated guards (surviving same-kind declaration, inheritance, import/static-import coverage, remover-side-still-uses) substituting for the human Preview gate IntelliJ uses when rename refactoring falls back to textual search.

**Why.** SpotBugs accepts precision loss when the auxiliary classpath is incomplete and Checkstyle's own docs show resolution-free single-file analysis works only with documented shape limits and ambiguity suppression; a zero-FP bar cannot absorb precision loss, so it must suppress instead. IntelliJ propagates renames only over resolved references and demotes anything unresolvable to opt-in textual search behind a human-reviewed Preview, and JetBrains treats red code under an incomplete project model as an environment false alarm — so "unresolved" is a reliable defect signal only when the resolver's world model is known-complete, and an automated lane with no human gate must use conservative suppression.

**Status.** adopted. S12 (2026-07-26): written in as required — reports_detectors/tune_d3/review_oss_comparison.md exists; ISSUES.md #31 (c) records the comparator-grounded stance (Checkstyle as 'the architectural relative: resolution-free single-file analysis viable only with documented shape limits'); the lanes document shape restrictions and FN-direction suppression in their headers (e.g. signature_stale_call.py:10-19, 'Overbroad on purpose … FN direction' at :523).

**Source.** `a:82dd479f-sub-sub-agent-aadfd1-04`, `a:82dd479f-sub-sub-agent-aadfd1-05` · Artifacts: `https://checkstyle.sourceforge.io/writingchecks.html#Limitations`, `https://spotbugs.readthedocs.io/en/stable/faq.html`, `https://www.jetbrains.com/help/idea/rename-refactorings.html`

> Divergence: SpotBugs accepts precision loss under incomplete information; a zero-FP lane must instead suppress.
>
> — `2026-07-16_82dd479f_sub-agent-aadfd1.txt:35`

> a zero-FP automated lane must replace that human gate with conservative suppression (which is precisely what the survives-declaration / inheritance / import / remover-side-still-uses guards do)
>
> — `2026-07-16_82dd479f_sub-agent-aadfd1.txt:45`

### <a id="d-116"></a>D-116 — Calibrate D1's suppression toward false negatives, but reject blanket extends-suppression

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** D1's shadowing and declaration regexes are kept deliberately overbroad, admitting extra suppression; candidates mined from a lost `java.*` type wildcard must be members of the embedded _JDK_WILDCARD_TYPES sets for the eight commonly-wildcarded JDK packages (a `java.*` package with no embedded set yields no candidates, while non-JDK wildcards keep conservative mining), and the asymmetric wildcard policy — surviving wildcards suppress unconditionally, lost wildcards require positive JDK-membership evidence — is retained. No "extends ⇒ suppress inherited-member risk" guard is added, with fixture P7 pinning the prohibition. One confirmed breach of the overbroad-suppression contract was corrected: clause keywords (throws/implements/extends/permits) were missing from _EXPR_KEYWORDS so clause operands were read as declarations, and enum-constant declarations matched neither declares-pattern — an FP-direction failure.

**Why.** A missed shadow would be a false positive while an over-detected one is only a false negative, so the design spends its error budget on FN. The wildcard restriction closes a class of error with externally knowable, invariant knowledge and fails toward FN only, whereas non-JDK wildcard membership is genuinely unknowable file-locally; and without a classpath, wildcard and static-member resolution is where both textual and AST tools bleed FPs — Checkstyle punts on wildcards outright and PMD has a decade-long FP bug tail there — so being more conservative than PMD is right for a CRITICAL-severity gate. The extends guard was rejected because the java-faker unit (AddressTest extends AbstractFakerTest) proves the category contains true positives in extending classes, so it would trade real recall for cheap FP hardening. The clause/enum breach was found by probing (`void m() throws FooEx;`, `implements FooIntf, Bar`, `interface I extends FooIntf, Bar` all wrongly "declare" the type, and an end-to-end pruned-exception-import case was silently missed).

**Status.** adopted. Supersedes: *the claim that _EXPR_KEYWORDS made declares_member suppression-safe in the FN direction only*.

**Source.** `a:f0d70a59-06`, `a:f0d70a59-04`, `a:f0d70a59-07`, `a:734e4529-07`, `a:f0d70a59-15` · Artifacts: `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`, `423c215`, `bed3638`

> Deliberately overbroad: a missed shadow would be an FP, an over-detected one only an FN.
>
> — `2026-07-16_f0d70a59.txt:135`

> I rejected it because the java-faker unit (`AddressTest extends AbstractFakerTest`) proves the category contains true positives in extending classes; the P7 fixture now pins that a future session can't sneak that guard in either
>
> — `2026-07-16_f0d70a59.txt:224`

### <a id="d-117"></a>D-117 — Keep the absorption guard and document the textual tier's inherent false negatives

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The absorption guard — suppress when a parent lacking the lost import still uses the symbol uncovered — is retained, which makes the assertj pruner-kept-usages unit an intentional, tested false negative that no rung of the upgrade ladder including differential ecj would lift; only project-context speculative-merge compilation (full Crystal) would, and that cost class is not being taken. Unicode identifiers (the ASCII first-char class, FN-only), `\uXXXX` pre-lexing and text-block escape pathology near the closing delimiter are classified inherent-to-tier and documented rather than fixed, with a stripper unit test on text-block edges noted as cheap insurance.

**Why.** The zero-FP bar wins over recovering 1 of 21 derivation units: a parent using the name import-free proves it resolves without the import (same-package type, inherited member) — or that the parent was already broken; either way the breakage is not merge-induced, so the FN is a property of file-local differential evidence rather than of the regex implementation. The inherent-tier items are left alone because nobody outside javac handles `\uXXXX` pre-lexing and the text-block FP path requires the pathology plus the FP conjunction in a pre-2020 corpus, making the risk negligible.

**Status.** adopted.

**Source.** `a:f0d70a59-03`, `a:734e4529-12`, `a:f0d70a59-16` · Artifacts: `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py:550`

> A parent using the name import-free proves it resolves without the import (same-package type, inherited member) — or that the parent was already broken; either way not merge-induced.
>
> — `2026-07-16_f0d70a59.txt:137`

> That FN is a property of file-local differential evidence, not of the regex implementation. The only thing that lifts it is project-context compilation (speculative merge + real build, i.e., full Crystal), which is a different cost class entirely.
>
> — `2026-07-16_734e4529.txt:103`

### <a id="d-118"></a>D-118 — Reject Joern, type inference, compile oracles and the heavy parsers for the import lane

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** The import-prune lane does not use javasrc2cpg type inference, a compiler oracle, or Joern — Joern stays only where it earns its keep, the flow-shaped detectors (#3/#5) — and Spoon noClasspath mode, JavaParser-with-symbol-solver, CodeQL build-less Java extraction and Semgrep are all ruled out; the lane operates on import declarations plus the parent versions as semantic oracles.

**Why.** The type-inference route was built and dropped in Stage B because javasrc2cpg's single-file inference gives up nondeterministically and misflagged, at ~34 s per merge against milliseconds for textual; a real compile oracle needs the whole project's classpath at merge time, which a git merge driver does not have, and single-file javac shows "(none)" COMPILE DELTA on most of the 21 true breaks. Joern is the wrong altitude — import and name binding is a frontend concern and Joern's Java frontend is JavaParser plus best-effort typing — and the verified defects are syntax-recognition and index-maintenance failures that a CPG does not fix. Spoon and JavaParser sit strictly between the two chosen rungs in cost and authority; CodeQL is repo-scale, slow per invocation and license-encumbered, wrong for a per-file merge driver; Semgrep parses Java via tree-sitter but has no way to express three-version differential logic.

**Status.** adopted.

**Cross-theme.** *duplicates* → [D-147](#d-147) — Two decisions, not one: the comparator normalization parser choice (2026-05-14) and the detector import-lane rejection (2026-07-16) rest on the same JVM-cost and maintenance arguments two months apart, against different objects. Kept separate, cross-linked.

**Source.** `b:f0d70a59-07`, `a:734e4529-08`, `a:734e4529-11` · Artifacts: `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`

> Short answer: Joern specifically, no — for this lane it was the right thing to drop, and re-adding it wouldn't fix the defects found in review.
>
> — `2026-07-16_734e4529.txt:78`

> A real compile oracle needs the whole project's classpath at merge time — not something a git merge driver has.
>
> — `2026-07-16_f0d70a59.txt:214`

### <a id="d-119"></a>D-119 — Three proposed fixes for the remaining verified D1 guard defects

`2026-07-16` · **proposed** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Three review recommendations for import_prune_usage.py: teach `declares_type` (or the mining exclusion) to recognise type-parameter declarations so `class Box<KeyType>` no longer mines `KeyType` as a candidate; fix the multi-declarator FP with a dedicated declarator-list pattern (`Type a, b, c;`) rather than adding `,` to the preceding-character class in `declares_member`; and replace the hand-typed `_JDK_WILDCARD_TYPES`/`_JAVA_LANG` sets with mechanically generated ones from a real JDK, plus a sentinel assertion in the test battery.

**Why.** The type-parameter FP violates the zero-FP bar and was reproduced against committed code, and the fix belongs on the suppression side because that direction errs toward false negatives, matching the lane's bias discipline. Adding `,` to the preceding-char class would classify call arguments (`foo(x, count)`) as declarations and kill legitimate true positives for explicit static member imports, so a dedicated pattern is the safer extension. Hand-typing ~300 names produced exactly the drift the embedded index was meant to avoid (Map and other names missing), and the goimports precedent shows the stdlib symbol table is machine-generated — nobody hand-types 300 symbol names.

**Status.** proposed. S12 (2026-07-26): none of the three applied — import_prune_usage.py declares_type (:369-372) has no type-parameter clause, no declarator-list pattern exists, and _JDK_WILDCARD_TYPES (:157) remains hand-typed with no generator or sentinel assertion. Still-live candidate work tied to [D-281](#d-281) and the open default-enable ruling.

**Source.** `a:734e4529-01`, `a:734e4529-02`, `a:734e4529-03` · Artifacts: `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`

> A dedicated declarator-list pattern (`Type a, b, c;`) is the safer extension.
>
> — `2026-07-16_734e4529.txt:13`

> hand-typing ~300 names produced exactly the drift it was meant to avoid. Suggest regenerating the sets mechanically (one-shot script over a real JDK's `ct.sym`/`javap`) and adding a sentinel assertion
>
> — `2026-07-16_734e4529.txt:15`

### <a id="d-120"></a>D-120 — Defer tree-sitter token classification to keep the import lane dependency-free

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Replacing the declares_member regex family with tree-sitter-java token classification is deliberately not done; it stays a contingency triggered only by a GD3 flag traced to token misclassification.

**Why.** It would be semantic_merge_driver's first parsing dependency in a lane whose selling points are zero dependencies and zero runtime cost, and the current zero-FP evidence does not justify it.

**Status.** adopted.

**Source.** `a:f0d70a59-12` · Artifacts: `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py:353`

> it would be `semantic_merge_driver`'s first parsing dependency in a lane whose selling points are zero deps and zero runtime cost. The current zero-FP evidence doesn't justify it; a GD3 flag traced to token misclassification would.
>
> — `2026-07-16_f0d70a59.txt:252`

### <a id="d-121"></a>D-121 — Accept the lanes' known inefficiencies and one warty misdetection at experimental scale

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Several known costs are accepted rather than fixed: the per-lost-wildcard recomputation of `_identifier_pool` and the full-text `declares_member` scans are not cached or hoisted; the `call_form` 40-character window examined before `lstrip` is left as-is, so pathological whitespace misdetects; and in signature_stale_call.py neither the reordering of `_any_varargs_form` after the cheaper `_declared_arities` nor the unification of the three `_name_paren_sites` passes is done. The brief's premise that the lane repeatedly recomputes text views and recompiles regexes in hot loops is withdrawn.

**Why.** Harmless at experimental scale — cache and hoist only if the lane ever runs on large corpora; the whitespace case is pathological and not worth fixing; and at three or fewer candidate names the reorder saves sub-milliseconds while the unified scan is well under the noise floor next to the dominating Docker runs. The premise was withdrawn on inspection: `_FileView.stripped` is computed once in __init__, view_of() memoises construction, enum_constants is a lazy cached property, `_absorbable_spans`/base_stripped are hoisted out of the per-name loop, and Python's re._cache keys on the pattern string with the same names recurring, so nothing recompiles inside a call.

**Status.** adopted. Supersedes: *the review brief's premise of per-call view recomputation and hot-loop regex recompilation*.

**Source.** `a:734e4529-14`, `a:734e4529-13`, `a:acf7e1d0-sub-agent-af6a03-05`, `a:acf7e1d0-sub-agent-af6a03-02` · Artifacts: `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`

> Harmless at experimental scale; cache the pool and hoist the declares checks if this ever runs on large corpora.
>
> — `2026-07-16_734e4529.txt:21`

> So the "repeated per-call recomputation" and "regex recompilation in hot loops" concerns from the brief mostly do not apply here — the structure is already careful.
>
> — `2026-07-16_acf7e1d0_sub-agent-af6a03.txt:15`

### <a id="d-122"></a>D-122 — Proposed but unratified optimisations to the widened and D2 textual scans

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Three performance recommendations are recorded as non-blocking: the widened pass's `_declared_method_names` slicing the whole stripped file per call site and the three site scanners' per-occurrence `s.count("\n", 0, start)` plus up to three whole-file regex scans per candidate are logged as warts rather than defects, with cheaper forms named (pass `(stripped, after_paren)` and scan in place; precompute newline offsets per `_FileView` and bisect via a shared `line_of(pos)` helper); and signature_stale_call.py should early-out immediately after the RM2 loop when neither side has arity changes, or defer `_absorbable_spans(merged.stripped)` and the base-content strip to first use.

**Why.** Runtime is dominated by subprocesses: the lane already pays three multi-second joern-parse invocations per file, 10–100× the textual cost, and the exactly-one-parent `split_sides` filter leaves near-zero candidates on typical merges — but this is the widened pass's dominant pure-Python cost and would become the floor if the textual lane were ever run without Joern. The early-out matters because both values are consumed only inside the per-name loop, which never executes when RM2 reports no Add/Remove Parameter change — the overwhelming majority of merged files — so on that path the driver throws away a multi-KB allocation and two full-file passes.

**Status.** adopted. S12 (2026-07-26): the record-as-non-blocking disposition was enacted — ISSUES.md #31 lists 'O(k·n) line counting — immaterial vs subprocess dominance' among non-fixes-with-reasons, the accept-lane-inefficiencies decision carries the same ruling, and one named cheaper form (memoized view/arity-text construction) is in signature_stale_call.py:225-237.

**Source.** `a:82dd479f-sub-sub-agent-a87c1f-02`, `b:82dd479f-sub-agent-a87c1f-02`, `a:acf7e1d0-sub-agent-af6a03-04` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py:350`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py:232-233`

> NOT material in practice: the exactly-one-parent `split_sides` filter leaves near-zero candidates on typical merges, and Joern subprocess time dominates by 10-100x. Flag only as a worst-case note.
>
> — `2026-07-16_82dd479f_sub-agent-a87c1f.txt:25`

> There is no early-out for `changes["ours"]` and `changes["theirs"]` both being empty.
>
> — `2026-07-16_acf7e1d0_sub-agent-af6a03.txt:23`

### <a id="d-123"></a>D-123 — Reuse sibling lanes by composition and module import, with zero edits to frozen lane files

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** "Reuse, don't fork" is implemented as composition: the new D2 lane holds an internal RM2RenameConflictStrategy and calls its `_run_rm2_pair`, and imports D1's stripper and helpers by importing the *modules* (`_rc`, `_ipu`) and reaching helpers as module attributes rather than importing the sibling strategy classes. No existing lane file is edited, and the resulting reliance on another class's private method and another module's private helpers is left in place rather than flagged.

**Why.** This reconciles the prompt's reuse instruction with the standing no-changes-to-existing-lanes constraint, and the S-D2 close-out explicitly sanctioned importing D1's stripper. Modules rather than classes because plugin_loader instantiates any MergeStrategy subclass found in a module namespace with no arguments, so importing sibling strategy classes by name would register them twice; importing MergeStrategy itself is safe because the loader excludes it, matching the precedent in rename_conflict.py and import_prune_usage.py. The public alternatives are insufficient — `_rm2_renames` filters to renames and would drop the Add/Remove-Parameter records D2 depends on, and `_FileView.occurrences()` cannot do arity counting, new-prefix discrimination or decl-shape rejection — and every less-fragile refactor (a shared RM2Runner, promoting the scan helpers to public) requires editing the frozen lane files, so no better altitude was available within the constraints.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-461](#d-461) (see the reconciliation note there)

**Source.** `a:acf7e1d0-04`, `b:acf7e1d0-sub-sub-agent-a5d889-02`, `a:acf7e1d0-sub-agent-a88268-03` · Artifacts: `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`, `semantic_merge_driver/core/plugin_loader.py`

> resolved by composition: the new lane holds an internal `RM2RenameConflictStrategy` and calls its `_run_rm2_pair`; D1's stripper is imported (S-D2 close-out explicitly sanctioned this). Zero edits to existing lane files.
>
> — `2026-07-16_acf7e1d0.txt:56`

> Every less-fragile alternative (extract a shared `RM2Runner`, promote `_FileView` scan helpers to public) requires editing the frozen lane files, which the stated constraint forbids this session.
>
> — `2026-07-16_acf7e1d0_sub-agent-a88268.txt:21`

### <a id="d-124"></a>D-124 — Fix D2's arity projection and generic-span rule; affirm the rest of its guard set

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Two D2 defects are fixed: a lane-local variant of the D1 stripper blanks string/char/text-block literals to a placeholder (comments still to spaces) so single-literal arguments count as arity 1 — a deliberate, documented fork; and `_generic_span`'s SCREAMING_CASE poison heuristic is replaced by one rule, a `(`-followed generic span is trusted only when the type is `new`-rooted. The rest of the guard set is affirmed rather than simplified: the `record` contextual-keyword exception stays narrow, `_OBJECT_METHODS` stays a fixed list, and the long `continue` chain in analyze() plus the `change.varargs`/`_any_varargs_form` pair are cleared as intentional, with `_CallSite.start`, `new_prefixed` and all seven `_SigChange` fields confirmed read.

**Why.** The arity projection is semantically different from D1's presence projection — under D1's stripper `send("boom")` counts as arity 0, both a missed defect and a false-flag vector when old_arity == 0 — so the fork is justified. The generic-span and comparison fixes collapse into one rule that subsumes the SCREAMING_CASE special case entirely. `record` is a restricted keyword, so the general "keyword ⇒ not type-ish" rule misfires for canonical-constructor headers specifically and the exception is exactly as narrow as the language wart; java.lang.Object methods are inherited by every class including one with no explicit extends, which the span-based `_absorbable_spans` mechanism structurally cannot cover, so a fixed list is the only mechanism; and each `continue` maps to a documented FP-suppression rule in the evidence chain while the mocked tests decouple RM2-reported varargs from file text, making the two varargs checks genuine dual coverage.

**Status.** adopted. Supersedes: *the SCREAMING_CASE poison classification in _generic_span*.

**Source.** `a:acf7e1d0-09`, `a:acf7e1d0-08`, `a:acf7e1d0-sub-agent-a88268-04`, `a:acf7e1d0-sub-agent-a88268-05`, `b:acf7e1d0-sub-sub-agent-afc4ad-06` · Artifacts: `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`, `6523ab0`

> fixes 1 and 3 collapse into one rule — a `(`-followed generic span is only trusted when the type is `new`-rooted
>
> — `2026-07-16_acf7e1d0.txt:423`

> each `continue` maps to a documented FP-suppression rule in the evidence chain — not unnecessary nesting.
>
> — `2026-07-16_acf7e1d0_sub-agent-afc4ad.txt:66`

### <a id="d-125"></a>D-125 — Proposed structural cleanups against silent drift in the lanes and the tune harness

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Four unratified structural recommendations: add runtime invariants to detector_tune_run.py (`assert set(FULL_SUITE) == set(LANES)`, each `strategies[lane].name == lane`, and `{n for n,_,_ in detect_validate.DETECTORS} <= set(LANES)`); or better, replace the separate `_SMOKES` dict with one registry co-locating each lane's strategy class and smoke fixture; collapse the lockstep `changes`/`sigs` dicts in analyze() into a single `Dict[str, Dict[str, List[_SigChange]]]`; and extract the D3 widened textual pass out of the Joern strategy's pre-pass into its own flag-gated strategy module with its own LANES/FULL_SUITE row.

**Why.** Nothing currently enforces agreement between the duplicated registries — the comment states the name invariant without checking it — so an eighth lane added to LANES but not FULL_SUITE would let GD3 record a PASS for an arm that never executed, and a missing `_SMOKES` entry yields an opaque KeyError after preflight has already spun up Docker. `sigs[label][change.name] = change` silently keeps only the last _SigChange for a name, and the two dicts stay consistent only because the len(pairs) != 1 guard skips multi-pair names, so a future per-name branch would consume a stale last-writer value with no error. The widened pass is a fully independent detector (pure text, own guards, own issue class, 400+ lines), and embedding it costs measurement attribution and couples a deterministic detector to Joern infra noise, which would make D3's zero-FP and recall numbers unrecoverable if Joern were flaky during S-D5 — though keeping one category-#6 lane and one-flag-per-name was a deliberate documented choice, so it is a judgment call, not a defect.

**Status.** adopted. S12 (2026-07-26): landed — detector_tune_run.py now has the one-registry design ('One registry row per lane: (strategy class, smoke-fixture builder)', :63-72) plus the exact invariant 'assert set(FULL_SUITE) == set(LANES)' at :81, and ISSUES.md #31 records 'single sig_lists map replaces the changes/sigs pair, dead equal-arity disjunct removed, no-candidate early-out' for D2.

**Cross-theme.** *duplicates* → [D-461](#d-461) — Same S-D4 review, same duplication-drift risk, both proposed. Kept as a cross-linked pair (mirror: other:3); both sit in the proposed residue for Ali.

**Source.** `a:82dd479f-sub-sub-agent-a87c1f-04`, `a:acf7e1d0-sub-agent-a88268-07`, `a:acf7e1d0-sub-agent-a88268-06`, `a:82dd479f-sub-sub-agent-a87c1f-05` · Artifacts: `merge-tool-comparison/tools/detector_tune_run.py`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`, `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`

> the comment at L55-57 states the name invariant but nothing checks it
>
> — `2026-07-16_82dd479f_sub-agent-a87c1f.txt:37`

> A separate flag-gated strategy module (own LANES/FULL_SUITE row) is the concretely better altitude; the dedupe it would lose is bounded
>
> — `2026-07-16_82dd479f_sub-agent-a87c1f.txt:43`

### <a id="d-126"></a>D-126 — The tune harness duplicates the lane registry and forces the experimental flag ON

`2026-07-16` · **adopted** · `[chat]` · corroboration: single-pass · confidence: medium · actors: claude

*Actors note: One of the two sub-agent findings is unattributed in the record; both come from Claude-run reviews.*

**Decision.** Two carve-outs for the tuning harness are confirmed: detector_tune_run.py duplicates the lane composition in LANES/FULL_SUITE rather than editing frozen detect_validate.py or extracting a shared registry outside it; and it sets `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1` at detector_tune_run.py:37, before importing the lane, so both lanes' analyze() do real work during the smoke gate — an explicit exception to the flag-OFF short-circuit that governs driver behaviour.

**Why.** detect_validate.py is a frozen instrument that must not be edited, so duplication is preferred over touching it and the drift risk is closed inside the runner instead. Without the flag ON, analyze() short-circuits on its first line and returns clean, so the smoke gate could never fire; forcing it ON is why the D1 gate has always worked and why the D2 gate will too.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-462](#d-462) (see the reconciliation note there)

**Source.** `b:82dd479f-sub-agent-a87c1f-05`, `b:acf7e1d0-sub-sub-agent-af9ecb-03` · Artifacts: `merge-tool-comparison/tools/detector_tune_run.py:37`, `merge-tool-comparison/tools/detect_validate.py`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py:190-191`

> sets `os.environ["SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"] = "1"` before lane import, so the smoke gate itself runs with the flag ON
>
> — `2026-07-16_acf7e1d0_sub-agent-af9ecb.txt:32`

> this is why the D1 gate has always worked and the D2 gate will too.
>
> — `2026-07-16_acf7e1d0_sub-agent-af9ecb.txt:32`

### <a id="d-127"></a>D-127 — Record the legacy Joern detectors as heuristics that fire nothing in the wild

`2026-07-18` · **adopted** · `[chat]` · corroboration: single-pass · confidence: medium · actors: claude

*Actors note: Two of the five retrospective sub-agent findings are unattributed in the record; the other three are Claude's, and all five come from Claude-run primary-source reads.*

**Decision.** The pre-Stage-B detectors are documented for what they are: the category-#3 strategy (joern_strategies/taint_check.py, named JoernDataFlowInterference) is a line-ordered clear-then-read "stale read" heuristic, not taint or dataflow analysis, and its name is conceded as aspirational; loop coverage is limited to constant-literal conditions (while(1)/while(true)) and start>end dead FOR loops, so the canonical continue-skips-increment case with a non-literal condition is out of scope. On 443 real files categories #3 and #5 produced 0 detections and 0 false positives, with all detection mass in the #6 rename/declaration family (R1 = 0/193, R2 = 11 causal/164 = 6.7%). ResearchSummary.xml's claim of only two strategies is withdrawn: seven concrete strategy classes exist, wired via config/strategies.yaml, with abstract_strategy.py and scala_queries/infinite_loop.sc empty stubs.

**Why.** Established by primary-source reads of the code rather than the documentation: reading taint_check.py shows a line-ordered heuristic despite the filename; the two loop detectors only handle literal conditions and dead ranges, so a non-literal continue case falls outside what they can flag; and the in-the-wild measurement shows all detection mass is the #6 family, contradicting the assumption that the dataflow and loop detectors were the centrepiece.

**Status.** adopted. Supersedes: *ResearchSummary.xml's claim that the system has two detection strategies*; *the characterisation of category #3 detection as dataflow/taint analysis*.

**Cross-theme.** *depended on by* ← [D-002](#d-002) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-022](#d-022) (see the reconciliation note there)

**Source.** `b:dc3bc182-sub-sub-agent-a74c7a-11`, `b:dc3bc182-sub-sub-agent-a7bb0f-04`, `b:dc3bc182-sub-sub-agent-a7bb0f-05`, `b:dc3bc182-sub-sub-agent-a7bb0f-06`, `a:dc3bc182-sub-sub-agent-ab4c4f-11` · Artifacts: `strategies/joern_strategies/taint_check.py`, `strategies/joern_strategies/infinite_loop.py`, `strategies/joern_strategies/invalid_loop_bounds.py`, `ResearchSummary.xml`, `STATUS.md`, `ISSUES.md #29`

> #3 is explicitly a "line-ordering heuristic," not real dataflow
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:31`

> fire **0 detections and 0 FPs on 443 real files**; all detection mass is the #6 rename family.
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:74`

### <a id="d-128"></a>D-128 — The new detector lanes ship flag-gated; default-enabling is deferred to Ali after S-D8

`2026-07-22 → 2026-07-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Claude framed and reported the gating; the deferred default-enabling decision is explicitly reserved to Ali.*

**Decision.** All new detector lanes remain behind SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1 at the close of ISSUES #31 and are reported that way in the thesis alongside the committed measured results (43.2% / 22.0% / −11.5%); whether to enable them by default is explicitly out of scope of the evaluation cycle and remains open as of 2026-07-25, to be decided by Ali once S-D8's latency and cost re-pricing lands.

**Why.** Default-enabling awaits S-D8's price: the detection latency and cost delta is the input to that decision, and both halves of it should be measured on the instruments that matter. Default-enabling is a decision, not a measurement, so it is not settled by closing the evaluation cycle.

**Status.** adopted. Supersedes: *the ⟨pending⟩ placeholder for S-D5 held-out recall in the earlier abstract drafts*.

**Cross-theme.** *depended on by* ← [D-077](#d-077) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-032](#d-032), [D-283](#d-283) — No dedicated cost-and-latency theme exists; S-D8 (the re-pricing the deferral waits on) is owned by its green-light and its pre-registered environment gate.

**Cross-theme.** *depended on by* ← [D-281](#d-281) (see the reconciliation note there)

**Source.** `a:2e726dc0-22`, `a:06ec13eb-14`, `a:dc3bc182-38` · Artifacts: `merge-tool-comparison/reports_detectors/FINDINGS.md`, `76ee2f0`, `67ccce7`

> The lanes stay behind `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1` — default-enabling deliberately awaits S-D8's price.
>
> — `2026-07-16_2e726dc0.txt:735`

> The only open flag is default-enabling, which is a decision, not a measurement — the thesis reports the lanes as flag-gated.
>
> — `2026-07-18_dc3bc182.txt:624`


## Evaluation methodology & oracles

*202 primary source decisions → 63 entries; 1 not promoted (reasons in `docs/decision-record/entries/evaluation-oracles.json`).*

### <a id="d-129"></a>D-129 — Required report contents — metric set, latency, CIs, per-scenario pivot — stated but not confirmed shipped

`2026-04-16 → 2026-07-02` · **adopted** · `[mixed]` · corroboration: both · confidence: medium · actors: unclear

*Actors note: The plan requirement has no recorded author; the two reporting-stack findings are Claude's sub-agent survey.*

**Decision.** Every evaluation step is required to record TP/FN/FP/TN, precision, recall, F1, categories-covered (of 7) and separate merge/analysis/total runtimes on a standardized hardware profile, filled into the §5.2 comparison and §5.4 latency tables. Two later gaps in the reporting stack were flagged against this requirement: Wilson CI computation should move into src/evaluation/metrics.py compute_metrics() (adding precision/recall CI bound keys to ToolMetrics.to_dict() and CI columns to report.py), and the per-scenario × tool pivot (ISSUES #9) cannot be served by report.py at all because it exports only per-tool aggregates and would need new aggregation logic beyond ToolMetrics.

**Why.** For the CI integration: working wilson() helpers already exist in tools/detect_validate.py and tools/migrate_decl_w3.py but are not wired into the main aggregator, and the existing CI-enhanced reports_ci/ CSVs appear to have been produced externally with no implementation visible in src/. For the per-scenario pivot: no code path in report.py pivots results by scenario × tool.

**Status.** adopted. S12 (2026-07-26): the reporting stack carries the requirement — wilson() lives in src/evaluation/metrics.py:8 (the recommended integration), report.py has the per-scenario pivot exporter (to_per_scenario, :78, 'ISSUES #9') plus to_table/csv/json/latex and to_charts (:106), and runtime columns ship in reports/results.csv.

**Source.** `preA:pre-architecture-refmerge-14`, `a:fb0fa5c5-sub-sub-agent-a7dbb3-02`, `a:fb0fa5c5-sub-sub-agent-a7dbb3-04` · Artifacts: `merge-tool-comparison/src/evaluation/metrics.py`, `merge-tool-comparison/src/evaluation/report.py`, `merge-tool-comparison/tools/detect_validate.py`, `merge-tool-comparison/ISSUES.md`

> ### 5.1 Metrics (recorded at every step)
>
> — `2026-04-16_pre-architecture-refmerge.txt:774`

> **Per-scenario breakdown infrastructure missing entirely:** No code path in report.py to pivot results by scenario (rows) × tool (columns). Would require new aggregation logic beyond current ToolMetrics model.
>
> — `2026-07-02_fb0fa5c5_sub-agent-a7dbb3.txt:214`

### <a id="d-130"></a>D-130 — Headline numbers carry Wilson 95% CIs and tool-superiority claims require non-overlapping CIs

`2026-04-21 → 2026-06-20` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: the standing rule is recorded as Ali's in the mergiraf/spork/weave plans (one source unclear); the independent recomputation and the CI correction are Claude's.*

**Decision.** Any headline F1/precision/recall figure on an n<1000 dataset is reported with a Wilson 95% confidence interval, and a claim that tool A beats tool B (Spork vs Mergiraf, Weave vs Mergiraf) counts only when the CIs do not overlap; the same applies to per-cluster recall deltas and to any "X wins Y% of cases" line in a commit message. In practice the intervals are recomputed independently before a verdict is endorsed — the pooled per-cluster precision CIs behind ISSUES #27's DROP conclusion were re-derived from reports_ci/results.csv, and the drafted CI for "11 CAUSAL of 164" was corrected from [3.7, 11.6] to [3.8, 11.6] before publication.

**Why.** Without CIs, n=50 comparisons are suggestive rather than defensible; the rule unifies with ISSUES.md #5 on statistical confidence. The independent recomputation was undertaken because a possible discrepancy in strict-win counts between files was noticed and because strict-win reasoning needed the comparator's TP/FP/TN/FN semantics pinned down.

**Status.** adopted.

**Source.** `preA:pre-mergiraf-integration-06`, `preA:pre-rm2-integration-11`, `preA:pre-spork-driver-integration-06`, `preA:pre-weave-integration-13`, `b:3302d287-05`, `a:0e14484d-08` · Artifacts: `merge-tool-comparison/ISSUES.md #5`, `merge-tool-comparison/reports_ci/results.csv`, `FINDINGS.md`

> Wilson 95% CI for F1/precision/recall on any n<1000 dataset; a claim "tool A better than tool B" requires non-overlapping CIs
>
> — `2026-04-21_pre-mergiraf-integration.txt:27`

> without this, n=50 comparisons are suggestive, not defensible
>
> — `2026-04-21_pre-mergiraf-integration.txt:27`

> I recomputed the pooled Wilson 95% CIs — Spork [0.378, 0.603], Mergiraf [0.664, 0.865] — they match the cited intervals and are non-overlapping. The DROP conclusion is well-supported.
>
> — `2026-05-27_3302d287.txt:33`

### <a id="d-131"></a>D-131 — Add a multi-criteria FP matrix and a separate granularity-axis pivot to the report

`2026-04-21 → 2026-04-25` · **abandoned** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** Two report artefacts are proposed on top of the primary comparison: multi-criteria reporting (3h), where classify_result emits a label per criterion — textual, formatter-equivalent, token- or AST-equivalent, compiles, passes-tests — and report.py renders the matrix; and a dedicated granularity-axis pivot reports/granularity-axis.{csv,tex} (scenarios × tools, coloured by outcome, focused on disagreement cases and segmented by RM2 cluster if R1 has landed), regenerable via `make all`, with results.csv still carrying the Weave row.

**Why.** Showing the FP rate under multiple criteria is itself a thesis result — the report can say "under criterion X, Spork's FP rate is 42; under Y, it's 7" and let the reader pick — and 3h adds columns rather than replacing the comparator. The thesis claim is about the granularity axis rather than about Weave specifically, so a separate pivot makes the axis visible as a thesis artefact.

**Status.** abandoned. S12 (2026-07-26): neither artifact was ever built — no reports/granularity-axis.csv, no per-criterion columns in report.py or comparator.py. 3h's deferral was recorded by the adopted Tier-C scope decision; the comparator results have been frozen since Tier E. Dropped without a ruling.

**Source.** `preA:pre-mergiraf-integration-11`, `preA:pre-weave-integration-17` · Artifacts: `merge-tool-comparison/src/evaluation/comparator.py`, `merge-tool-comparison/src/evaluation/report.py`, `reports/granularity-axis.csv`

> Add **3h** to the report regardless of primary comparator — showing FP rate under multiple criteria *is* a thesis result.
>
> — `2026-04-21_pre-mergiraf-integration.txt:123`

> A separate pivot makes the axis visible as a thesis artefact.
>
> — `2026-04-25_pre-weave-integration.txt:268`

### <a id="d-132"></a>D-132 — Adopt google-java-format roundtrip (3e) as the primary comparator fix, implemented as a cached two-tier match

`2026-04-22 → 2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: claude

*Actors note: One source records claude making the call; the other(s) do not record who decided. Taken as claude on the only positive evidence, not by majority.*

**Decision.** Formatter-based normalisation via a google-java-format roundtrip (option 3e) is the primary M3 comparator fix, with 3i (upstream citation) and 3h (multi-criteria reporting) additive and 3j (manual labelling) validating the residual; 3a is deferred unless 3e+3j leave more than ~10% unexplained. It is implemented in `comparator.py::contents_match` as two tiers — cheap whitespace normalisation, then a gjf 1.22.0 Docker roundtrip on mismatch — cached per sha256 content hash, shipped as its own `merge-tools/google-java-format:1.22.0` image in docker-build, disableable via `MERGE_COMPARATOR_FORMATTER=off`, with conftest.py setting it off so the suite stays Docker-free; a missing docker, parse error or timeout returns False.

**Why.** Mapped against the three inspected diffs, gjf handles import reordering, whitespace/blank-line insertion, redundant cast parens, brace style, method-signature line breaks and boolean-expression parens, and was expected to recover ≥90% of the FPs; 3e is more specific than the 3a-vs-3b binary in the original γ acceptance wording and matches the richer mergiraf-integration §Phase 3 taxonomy. The recommendation was explicitly contingent on M3.5 empirically confirming gjf normalises the observed differences. The implementation fails closed rather than masking real disagreement as a match.

**Status.** adopted.

**Source.** `preA:pre-execution-sequence-08`, `preA:pre-commits-50`, `preA:pre-stage-gamma-fp-diagnostic-05`, `preA:pre-mergiraf-integration-12`, `preA:pre-commits-60` · Artifacts: `merge-tool-comparison/src/evaluation/comparator.py`, `merge-tool-comparison/docker/google-java-format/Dockerfile`, `merge-tool-comparison/tests/conftest.py`, `d7a4046`, `6c272da`, `10c8a54`

> **M3 option chosen:** **3e** (formatter-based normalisation via `google-java-format` roundtrip) as primary **for Spork**
>
> — `2026-04-22_pre-execution-sequence.txt:78`

> contents_match now tries cheap whitespace normalize first, then falls back
>
> — `2026-04-15_pre-commits.txt:1175`

### <a id="d-133"></a>D-133 — Pivot per-cluster evidence on ours∪theirs, rejecting the resolution axis as circular

`2026-04-22 → 2026-05-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources split between claude, unclear and joint; the 2026-05-18 session records the deviation as put to Ali and resolved with him, so joint.*

**Decision.** Per-cluster tool-performance metrics bucket each scenario by the file-level refactoring cluster of union(base→ours, base→theirs) — computed by running RM2 on the two sides separately, as the runtime dispatcher does — instead of the rm2-integration plan's base→resolution axis. Clustering the developer's final merged file is explicitly rejected even though it is the cleaner and cheaper single-axis label. The cost is accepted: two RM2 runs per scenario (~100 cached Docker calls instead of ~50) and a noisier label that counts intended refactorings later discarded and can over-count when ours and theirs disagree.

**Why.** The resolution defines TP/FP, so bucketing by a function of it makes grouping and outcome variables derive from the same artifact — a confounded, quasi-circular statistic that cannot justify the W5/S2 per-cluster routing elifs. A resolution-based cluster is also not computable at dispatch time: the runtime classifier only ever sees base/ours/theirs, so mirroring it keeps the evidence dispatch-faithful and makes negative evidence valid — if cluster does not predict tool performance, that honestly refutes the routing elifs, whereas under the resolution axis any result is uninformative. The added noise is the right noise, because the dispatcher faces exactly it, seeing only branch attempts before reconciliation.

**Status.** adopted. Supersedes: *rm2-integration.md R2 spec pivoting on the resolution axis*; *R1 running RM2 only on base → resolution*.

**Cross-theme.** *depended on by* ← [D-095](#d-095) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-079](#d-079), [D-063](#d-063) — other_uid preA:pre-scope-tier-options-15 is cited by the pairwise entry; the deferred W5/S2 routing-evidence question the pivot exists to serve is backends-routing/[D-063](#d-063).

**Source.** `preA:pre-execution-sequence-04`, `preA:pre-execution-sequence-18`, `preA:pre-rm2-integration-01`, `a:20b53f98-07`, `a:dc624d63-01`, `b:dc624d63-02`, `a:dc624d63-02`, `a:dc624d63-04` · Artifacts: `merge-tool-comparison/src/evaluation/categorizer.py`, `merge-tool-comparison/src/evaluation/metrics.py`, `semantic_merge_driver/core/refactoring_classifier.py`, `docs/plans/rm2-integration.md`, `2b95aa3`

> If you also bucket by a function of the resolution, the grouping variable and the outcome variable are both derived from the same artifact.
>
> — `2026-05-18_dc624d63.txt:25`

> `ours∪theirs` is the only axis that can do the job — which is why the plan overrides `rm2-integration.md` here.
>
> — `2026-05-18_dc624d63.txt:38`

### <a id="d-134"></a>D-134 — Accept that NONE absorbs RM2 recall failures and measure the gap with a dual-mode F-harness

`2026-04-22 → 2026-05-06` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The design accepts that "no refactoring found" is indistinguishable from "RM2 missed it", so the NONE cluster silently absorbs RM2's recall failures; the only way to measure it is dual-mode tagging. The measurement harness tools/rm2_fharness.py runs RM2 twice per scenario — once on single-file directories holding base/ours content at the scenario's file_path, once on full project trees materialised via git worktree at the merge-base and ours-side parent SHAs — and diffs the refactoring-type sets, with the project-level set filtered to refactorings touching the scenario's file_path before comparison. The unfiltered 26.1% result is discarded (the unfiltered set kept per row as proj_full), and the filtered n=10 recall is restated as 66.7% (was 75.0% under RM 3.0.13), still inside the 50–80% Path D bracket.

**Why.** RM2's recall is below 100% and the file-level pipeline has no other signal for a missed detection. At merge time the driver only sees the merging file, so the apples-to-apples question is whether file-level recall matches project-level for refactorings in THIS file; the unfiltered measurement conflates whole-project refactoring volume with single-file recall. The 75.0%→66.7% restatement follows from re-measuring under the 2.4.0 pin, whose detector roster differs from 3.0.13.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-19`, `preA:pre-rm2-integration-recon-08`, `preA:pre-rm2-integration-recon-09`, `preA:pre-commits-25` · Artifacts: `merge-tool-comparison/tools/rm2_fharness.py`, `docs/plans/rm2-recon-samples/fharness-10.json`, `5e687ce`

> **Caveat:** "no refactoring found" is *indistinguishable from* "RM2 missed it" (recall <100%). The `NONE` cluster silently absorbs RM2's recall failures.
>
> — `2026-04-22_pre-rm2-integration.txt:79`

> An earlier (unfiltered) measurement gave 26.1% — discarded because it conflates whole-project refactoring volume with single-file recall.
>
> — `2026-05-05_pre-rm2-integration-recon.txt:71`

### <a id="d-135"></a>D-135 — Benchmark RM2 on isolated scenario files, but skip replicating its published oracle numbers

`2026-04-22` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: claude

*Actors note: One source records unclear, one claude; both are recommendations in Claude-authored plan text.*

**Decision.** Before committing to RM 2.0, benchmark its detection quality on n=50 isolated Schesch-style scenario files rather than assuming project-level performance carries over; reproducing RM2's published 99.6% precision / 94% recall against its own ~538-commit oracle is treated as an optional ~1–2h sanity check, skipped unless the F harness produces unexpected results.

**Why.** RM was designed for full-project analysis, so on isolated scenario files detection quality may drop — that is the question worth measuring. The oracle replication's only purpose is confirming the install isn't broken.

**Status.** adopted. S12 (2026-07-26): both halves resolved as specified — the scenario-file benchmark exists (tools/rm2_fharness.py; the recall question was answered at n=50 in reports_rm2_recall/), and the published-oracle replication was skipped exactly as the plan allowed (no surprise from the F harness; no replication artifact exists).

**Source.** `preA:pre-rm2-integration-15`, `preA:pre-tool-evaluation-findings-10` · Artifacts: `merge-tool-comparison/tools/rm2_fharness.py`

> RM was designed for full-project analysis. On isolated scenario files (Schesch dataset style), detection quality may drop. Benchmark on n=50 before committing.
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:168`

> Reproduces the published 99.6% precision / 94% recall — confirms install isn't broken. Skip unless F harness produces unexpected results.
>
> — `2026-04-22_pre-rm2-integration.txt:141`

### <a id="d-136"></a>D-136 — Cite upstream's published Mergiraf numbers as free credibility and check its test-suite ground truth

`2026-04-22 → 2026-05-11` · **proposed** · `[recon]` · corroboration: both · confidence: medium · actors: claude

*Actors note: One source records claude, one unclear; both sit in Claude-authored plan text.*

**Decision.** Mergiraf plan Phase 0 must verify whether Schesch's upstream AST-Merging-Evaluation has already published Mergiraf numbers and whether adopting upstream's test-suite ground truth is feasible for this thesis; the numbers computed from upstream's results/combined/result_adjusted.csv (n=5971: 57.9% Tests_passed / 5.6% Tests_failed / 36.5% Merge_failed) are then cited directly as M3 option 3i, marked unambiguously free since M0 already captured them.

**Why.** It is free credibility — the numbers come from the same code that produced upstream's published results, at no additional cost — and adopting upstream's test-suite ground truth would retire ISSUES #2 by construction while potentially saving Phase 4 work. Mergiraf's 5.6% silent-error rate is the headline number justifying a semantic-conflict detection layer downstream of any merge tool, including Mergiraf itself.

**Status.** proposed. S12 (2026-07-26): half done, half pending — Phase 0 verified and captured upstream's numbers (the recon doc records n=5971: 3456/335/2180), but the 3i citation appears in no report or thesis text (no draft exists; reports/ carries only the project's own numbers). Settled only when the thesis cites or declines to cite them.

**Cross-theme.** *depended on by* ← [D-298](#d-298) (see the reconciliation note there)

**Source.** `preA:pre-tool-evaluation-findings-15`, `preA:pre-mergiraf-integration-recon-03` · Artifacts: `results/combined/result_adjusted.csv`, `docs/plans/mergiraf-integration.md`, `merge-tool-comparison/ISSUES.md #2`

> **Cite upstream's Mergiraf numbers directly** under M3 option 3i. This is free credibility
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:133`

> Mergiraf's silent-error rate (5.6%) is the headline number that justifies a semantic-conflict detection layer downstream of any merge tool, including Mergiraf itself.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:151`

### <a id="d-137"></a>D-137 — Detect Mergiraf's fallback-to-markers by counting conflict markers as spork.py does

`2026-04-22` · **adopted** · `[recon]` · corroboration: single-pass · confidence: medium · actors: claude

**Decision.** The classifier must detect Mergiraf's fallback-to-conflict-markers behaviour using the same logic as spork.py:68 — counting `^<<<<<<<`.

**Why.** Mergiraf falls back to conflict markers when structural resolution is uncertain, and that behaviour must be detected by the classifier; the logic is identical to the existing Spork adapter.

**Status.** adopted. S12 (2026-07-26): implemented exactly — src/tools/mergiraf.py:20-21 classifies 'rc 0 or 1 + no <<<<<<< -> CLEAN; rc 0 or 1 + <<<<<<< -> CONFLICT', the spork.py-style marker detection this entry required.

**Source.** `preB:pre-tool-evaluation-findings-04` · Artifacts: `merge-tool-comparison/src/tools/spork.py`

> Fallback-to-markers must be detected by the classifier; identical logic to [`spork.py:68`](../../merge-tool-comparison/src/tools/spork.py) (count `^<<<<<<<`).
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:54`

### <a id="d-138"></a>D-138 — Ground truth follows a γ→3e→3j→3b ladder; test-suite ground truth demoted to maximalist fallback

`2026-04-30 → 2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: claude

*Actors note: One source records claude making the call; the other(s) do not record who decided. Taken as claude on the only positive evidence, not by majority.*

**Decision.** Ground-truth resolution escalates: stage γ diagnostic first, then 3e formatter-based normalisation (google-java-format), then 3j stratified manual labelling of the residual FPs, upgrading to 3b AST-aware normalisation only if 3e+3j leave more than ~10% unexplained, and to 3a test-suite ground truth only if thesis defence specifically requires it. The earlier 3a-first recommendation is withdrawn as the default and preserved only as the maximalist option; the Mergiraf P3 plan section was rewritten accordingly with options 3d/3e/3g/3h/3i/3j added.

**Why.** 3e is closest to what the tools actually do — Spork claims token-preservation, so a formatter gives both sides a fair lexical baseline — at ~0.5d. 3a requires per-project build/test infrastructure and far more runtime per scenario; the timebox-escape rule is likely to fire on it, leaving the work falling back to 3e/3b having burned days, and the γ diagnostic did not justify the 1–5d build-infra investment when 3e was expected to recover ≥90% of the FPs.

**Status.** adopted. Supersedes: *3a-first ground-truth recommendation in the Mergiraf integration plan (pre-2026-04-30)*.

**Source.** `preA:pre-commits-17`, `preA:pre-mergiraf-integration-09`, `preA:pre-mergiraf-integration-10`, `preA:pre-stage-gamma-fp-diagnostic-07` · Artifacts: `713b337`, `docs/plans/mergiraf-integration.md`, `docs/plans/stage-gamma-fp-diagnostic.md`, `merge-tool-comparison/ISSUES.md`

> **γ first → 3e → 3j on remaining FPs → upgrade to 3b only if 3e+3j leave > ~10% unexplained → 3a only if thesis defence specifically requires test-suite methodology.**
>
> — `2026-04-21_pre-mergiraf-integration.txt:123`

> Skip 3a unless ≥2 weeks earmarked; the timebox-escape rule is likely to fire and you fall back to 3e/3b having burned days.
>
> — `2026-04-21_pre-mergiraf-integration.txt:123`

### <a id="d-139"></a>D-139 — Record the exact command per version-comparison finding and recover old numbers from git history

`2026-05-06` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** Every empirical claim in the RM2-vs-RM3 comparison document carries its provenance command — javap -v for bytecode version, ls/du/docker images for sizes, RefactoringMiner -h for CLI flags, diffed javap -classpath output for API surface, per-scenario `types` comparison for detector roster, diff against committed JSON for output format, and manual date-bracketed docker runs (3 runs after warm-up) for latency. The RM 3.0.13 side of the detector-roster comparison is sourced from the prior committed fharness-10.json at revision 1f76a00 rather than re-run, with regeneration instructions documented for anyone needing fresh 3.0.13 numbers.

**Why.** Stated explicitly as being "For reproducibility"; the F-harness was executed once, on RM 2.4.0, during the rollback session, so the 3.0.13 numbers were not re-measured.

**Status.** adopted.

**Source.** `preB:pre-rm2-vs-rm3-differences-11`, `preA:pre-rm2-vs-rm3-differences-11` · Artifacts: `docs/plans/rm2-vs-rm3-differences.md`, `1f76a00`, `docs/plans/rm2-recon-samples/fharness-10.json`

> For reproducibility:
>
> — `2026-05-06_pre-rm2-vs-rm3-differences.txt:216`

> The F-harness was run once during the rollback session on RM 2.4.0; the 3.0.13 numbers were not re-measured here.
>
> — `2026-05-06_pre-rm2-vs-rm3-differences.txt:222`

### <a id="d-140"></a>D-140 — Bucket every false positive by the cheapest normalization that makes it match, per tool

`2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** The stage-γ diagnostic classifies each claims-CLEAN false positive by applying progressively stricter normalizations (baseline normalize, aggressive whitespace, strip imports, imports+whitespace) and assigns it to the cheapest one that produced a match, or to `structural` if none did. The same bucketing plus a size-stratified three-case eyeball was extended beyond the original Spork-only scope to Mastery's 44 FPs; JDime is excluded from the treatment entirely.

**Why.** Extending the bucketing to Mastery revealed a qualitatively different failure mode — content loss rather than AST-formatter artefacts. JDime is excluded because its crashes happen before the comparator runs, so formatter normalisation cannot apply.

**Status.** adopted.

**Source.** `preA:pre-stage-gamma-fp-diagnostic-01`, `preA:pre-stage-gamma-fp-diagnostic-09`, `preA:pre-stage-gamma-fp-diagnostic-11` · Artifacts: `docs/plans/stage-gamma-fp-diagnostic.md`

> Bucketed each FP by the cheapest normalization that produced a match (or `structural` if none did).
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:25`

> For **JDime**: unchanged — crashes happen before the comparator runs; 3e doesn't apply.
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:121`

### <a id="d-141"></a>D-141 — Downgrade "all structural FPs are AST-equivalent reformatting" to a 3-of-39 hypothesis

`2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: One source records claude making the call; the other(s) do not record who decided. Taken as claude on the only positive evidence, not by majority.*

**Decision.** The claim that all `structural` Spork FPs are AST-equivalent reformatting is restated as a hypothesis supported by 3 confirmed instances out of 39 — "3 of 39 sampled structural cases are AST-equivalent; 36 unsampled" — with the extension to the unsampled 36 flagged as hypothesis-not-measurement. It is further documented that 0–5 of the 39 may be genuine Spork pathologies (e.g. the aerogear comment duplication), that a 3-case sample cannot estimate that residual fraction, and that the 3e recommendation itself came from prior knowledge of google-java-format rather than from running it on the sampled diffs.

**Why.** The qualitative finding rests on 3 of 39 eyeballed structural cases; the original wording overclaimed from a 3-sample eyeball to a 39-case property. The observed comment duplication is not a pretty-printing artefact and would survive a formatter roundtrip because formatters preserve content, so the 3e prediction was presented as empirically backed when it was not — M3.5 implementation is the verification step.

**Status.** adopted.

**Source.** `preA:pre-stage-gamma-fp-diagnostic-03`, `preA:pre-stage-gamma-fp-diagnostic-04`, `preA:pre-commits-57`, `preA:pre-commits-58` · Artifacts: `docs/plans/stage-gamma-fp-diagnostic.md §7`, `c099187`, `STATUS.md`, `merge-tool-comparison/ISSUES.md #2`

> Treat "all structural FPs are AST-equivalent reformatting" as a hypothesis backed by 3 confirmed instances, not a measured property of the full bucket.
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:10`

> Original γ doc presented the 3e recommendation as if empirically
>
> — `2026-04-15_pre-commits.txt:1129`

### <a id="d-142"></a>D-142 — gjf recovered 1 of 42 FPs: prediction withdrawn, Spork's FP rate reframed as a comparator gap

`2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: One source records claude making the call; the other(s) do not record who decided. Taken as claude on the only positive evidence, not by majority.*

**Decision.** The M3.5 acceptance criterion (Spork FP rate drops sharply under formatter normalisation) is recorded as NOT met — Spork TP 1→2, FP 42→41, Mastery 0 recovery — so ISSUES #2 stays at `decided` rather than `resolved`; the structural bucket is declared heterogeneous rather than uniformly formatter-erasable. No fix is made to the 3e code: the implementation is correct and the §5 recommendation was over-confident. After 3j stratified manual labelling put 15/15 sampled residuals at AST-equivalent, Spork's FP rate is reframed as a comparator-ground-truth gap, distinct from Mastery's content-loss family weakness with JDime.

**Why.** The dominant residuals — `} else { if (X) }` ↔ `} else if (X)` restructuring, comment placement, redundant cast parens — are patterns gjf does not normalise, and those patterns were unrepresented in the 3-case inspection; the formatter does what it advertises and the §5 cast-paren prediction was empirically false. No content loss, duplication, reordering or different-resolution disagreement appeared in any of the 15 manual labels, so the §3 hypothesis survives at higher sample size — what failed in §8 was specifically gjf's inability to normalise these patterns.

**Status.** adopted.

**Source.** `preA:pre-stage-gamma-fp-diagnostic-12`, `preA:pre-mergiraf-integration-14`, `preA:pre-stage-gamma-fp-diagnostic-13`, `preA:pre-commits-63` · Artifacts: `reports/results.csv`, `merge-tool-comparison/ISSUES.md #2`, `docs/plans/stage-gamma-fp-diagnostic.md`, `caf33e2`

> The hypothesis "all 39 unsampled structural FPs follow the small-sample reformatting pattern" was wrong — the structural bucket is heterogeneous.
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:162`

> Reframing: Spork's FP rate is a comparator-ground-truth gap, NOT a tool
>
> — `2026-04-15_pre-commits.txt:1229`

### <a id="d-143"></a>D-143 — Mastery's FPs are intrinsic content loss, later refined to 10 comment-only and 34 genuine

`2026-05-14 → 2026-05-15` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Two sources record actors as unclear and two as claude; the reasoning is Claude's in the transcript-era-adjacent plan text.*

**Decision.** 3e is not the primary fix for Mastery: its FP rate is reported with an intrinsic-limitation caveat parallel to JDime's crash-rate caveat instead. The blanket framing is then refined — 10 of 44 Mastery scenarios are exclusively comment loss and normalise to byte-identical canonical text under strip_comments plus token_canonical_fold (the unplanned +10 recovery under Tier D), while the JDime-family framing stands only for the remaining 34 genuine code-content-loss cases, recoverable only via 3a if at all. The plan's prediction that Mastery and JDime rows would be unchanged under Tier D is withdrawn, and the recoveries are accepted as legitimate under the existing comment-equivalence threat.

**Why.** Mastery systematically discards comments and blank-line structure during AST roundtrip, and no amount of formatting recovers textual equivalence when one side is missing content entirely — the same family weakness Schesch cites for JDime. D.6's token-canonical fold then revealed that in 10/44 scenarios the dev side has 80+ comment tokens and Mastery's output has 0, so canonical forms coincide after comment-strip; the spot-check of 47deg_firebrand showed 84 comment tokens vs 0 with identical 18473-char canonical forms.

**Status.** adopted. Supersedes: *uniform 3e treatment across Spork and Mastery*.

**Source.** `preA:pre-commits-56`, `preA:pre-stage-gamma-fp-diagnostic-28`, `preA:pre-commits-81`, `preA:pre-comparator-3d-extended-ast-transforms-19` · Artifacts: `c099187`, `8cd83c1`, `docs/plans/stage-gamma-fp-diagnostic.md`, `comparator-3b-ast-normalize.md §7.1`, `reports/results.csv`

> For **Mastery**, 3e is *not the primary fix*. No amount of formatting
>
> — `2026-04-15_pre-commits.txt:1097`

> §6 framed Mastery as "intrinsic content loss" parallel to JDime. Tier D's D.6 token-canonical fold revealed a finer-grained truth
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:302`

### <a id="d-144"></a>D-144 — Rule out token-level comparison (3d); AST normalize (3b) is the next defensible step

`2026-05-14` · **superseded** · `[recon]` · corroboration: mixed · confidence: medium · actors: claude

*Actors note: One source records actors as unclear, the other as claude; the argument is Claude's in the plan text.*

**Decision.** Token-level normalisation is ruled out as the follow-up comparator and 3b AST normalize (javalang/tree-sitter canonicalisation — collapse redundant blocks, harmonise cast paren style) is designated the next defensible step, with 3j manual labelling as a parallel re-test.

**Why.** Token-level comparison would recover even less than 3e for these residuals because the else-if restructuring is also token-different.

**Status.** superseded. Superseded by [D-155](#d-155) — Expand Tier D to six transforms absorbing Tier E's paren strip and token fold, and ship them.

**Source.** `preB:pre-mergiraf-integration-18`, `preA:pre-stage-gamma-fp-diagnostic-15` · Artifacts: `docs/plans/comparator-3b-ast-normalize.md`

> 3d (token-level) is unlikely to recover the else-if residuals (token-different). 3b (AST normalize via javalang/tree-sitter — collapse redundant blocks, harmonise cast paren style) is the next defensible step.
>
> — `2026-04-21_pre-mergiraf-integration.txt:172`

> token-level (3d) would recover even less than 3e for these residuals (else-if restructuring is also token-different)
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:168`

### <a id="d-145"></a>D-145 — Scope 3b to Tier C's five tree-sitter transforms, deferred out of M3.5 to a follow-up phase

`2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: the M3.5 deferral is recorded as Ali's direction, the Tier C scoping as unclear/claude plan authorship — options were put and Ali set the scheduling.*

**Decision.** 3b AST normalize is named the principled fix but pushed out of M3.5 scope onto the Mergiraf plan's post-tool-integration TODO (together with 3h and 3i), then scoped to Tier C: exactly five canonicalisation transforms — strip_comments, strip_blank_lines, flatten_else_if, strip_redundant_parens (paren-wrapping-paren only), strip_javalang_fqn — added as a Tier 3 inside contents_match via tree-sitter-java 0.23.5, with a point estimate of TP 37 / FP 6 and an acceptance floor of TP ≥ 32 / FP ≤ 11. Pattern 6 (long array-literal line breaks) is deferred to a later Tier D.

**Why.** Deferral out of M3.5 is recorded as per user direction; all three deferred items become more valuable once the full tool comparison ships, and 3h only becomes informative after 3b adds the AST-equivalent column while 3i is doc-only and can land any time. Tier C is scoped this way as closing ISSUES #2 cleanly at ~2.5–3d; pattern 6 is dropped on 1-of-15 evidence frequency, edge-case-heaviness and low marginal return.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-250](#d-250) (see the reconciliation note there)

**Source.** `preA:pre-stage-gamma-fp-diagnostic-19`, `preA:pre-mergiraf-integration-16`, `preA:pre-mergiraf-integration-17`, `preA:pre-comparator-3b-ast-normalize-01`, `preA:pre-stage-gamma-fp-diagnostic-20` · Artifacts: `docs/plans/comparator-3b-ast-normalize.md`, `merge-tool-comparison/src/evaluation/ast_normalize.py`, `merge-tool-comparison/src/evaluation/comparator.py`

> Tier C scope: 5 transforms (blank-strip, comment-strip, block-flatten, paren-strip, java.lang FQN-strip) via tree-sitter-java as a Tier 3 in `contents_match`. Defers Tier D (long array-literal handling).
>
> — `2026-04-21_pre-mergiraf-integration.txt:179`

> Defer pattern 6 (long array-literal handling) to Tier D — 1-of-15 evidence frequency, edge-case-heavy, low marginal return.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:32`

### <a id="d-146"></a>D-146 — Tier 3 is strictly additive with parse-fail fall-through and one whole-tier kill switch

`2026-05-14 → 2026-05-16` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: claude

*Actors note: Sources split between unclear and claude authorship of the plan text; no source attributes the wiring choice to Ali.*

**Decision.** AST canonicalisation is wired as comparator Tier 3, running only when Tiers 1 and 2 disagree and only on Tier 2's gjf-formatted output; a parse failure returns None so the verdict falls through to Tier 2's already-False result. It is controlled by its own env switch `MERGE_COMPARATOR_AST_NORMALIZE` (default on; conftest sets it off to keep the suite parser-free), leaving `MERGE_COMPARATOR_FORMATTER` in charge of Tier 2; the proposal to rename FORMATTER→NORMALIZE and control both tiers together is rejected. No per-transform env vars are introduced at any tier: Tier D and Tier E extend `_collect_edits` in place with no new tier and no new variable, so AST_NORMALIZE=off disables Tier C+D+E together, and finer rollback means reverting the phase commits.

**Why.** Tier 3 must never make Tier 2 worse, so parse failure degrades to the existing verdict. The independent switch lets per-tier recovery be measured cleanly when validating Tier C against the §3 acceptance criteria, whereas the combined rename is simpler but harder to A/B-test. Per-transform env vars are overkill for kill-switch scope; a separate Tier 4 would allow independent toggling but adds matrix complexity for marginal value when both default on, and Tier C's existing switch already covers the later transforms, which are AST-level and conservative with the same parse-fail semantics.

**Status.** adopted.

**Source.** `preA:pre-comparator-3b-ast-normalize-03`, `preA:pre-commits-68`, `preA:pre-comparator-3b-ast-normalize-04`, `preA:pre-comparator-3b-ast-normalize-17`, `preA:pre-comparator-3d-extended-ast-transforms-05`, `preA:pre-comparator-3d-extended-ast-transforms-06`, `preA:pre-comparator-3e-tier-e-transforms-14`, `preA:pre-comparator-3e-tier-e-transforms-15` · Artifacts: `merge-tool-comparison/src/evaluation/comparator.py`, `merge-tool-comparison/src/evaluation/ast_normalize.py`, `MERGE_COMPARATOR_AST_NORMALIZE`, `MERGE_COMPARATOR_FORMATTER`, `7354b15`

> Tier 3 is **strictly additive**.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:96`

> Recommend (a). Both default `on`. The independent switch lets us measure per-tier recovery cleanly when validating Tier C against the §3 acceptance criteria.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:129`

> Per-transform env vars NOT introduced (overkill for a kill-switch scope). The whole AST tier flips together.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:421`

### <a id="d-147"></a>D-147 — Use tree-sitter-java for AST canonicalisation; reject javalang, JavaParser, Spoon and gjf internals

`2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** tree-sitter-java via its Python bindings is the parser for comparator Tier C (pinned tree-sitter>=0.21,<1.0 and tree-sitter-java>=0.21,<1.0), documented against the alternatives in plan §5. javalang, JavaParser-via-subprocess, Spoon and reusing google-java-format internals are all rejected.

**Why.** tree-sitter-java has active maintenance, prebuilt wheels for macOS arm64 and linux/amd64, Java 17+ support, fast in-process parsing, and a concrete syntax tree that preserves comments and whitespace as nodes — at the cost of ~2–3h of unfamiliar API learning. javalang is unmaintained since ~2017 and Java 8 only, so it would break on Schesch scenarios using modern lambdas or var-binding; JavaParser needs JVM startup per parse (~1–2s) and puts the work back in Docker territory; Spoon is massive overkill with a JVM dependency; gjf exposes no AST API and would require forking.

**Status.** adopted.

**Cross-theme.** *duplicated by* ← [D-118](#d-118) (see the reconciliation note there)

**Source.** `preA:pre-commits-67`, `preA:pre-comparator-3b-ast-normalize-09`, `preA:pre-comparator-3b-ast-normalize-10`, `preA:pre-comparator-3b-ast-normalize-11` · Artifacts: `merge-tool-comparison/src/evaluation/ast_normalize.py`, `merge-tool-comparison/pyproject.toml`, `6cfcdfc`, `3c39f8b`

> active maintenance; binary wheels for macOS arm64 + linux/amd64; Java 17+ support; fast in-process parse; concrete syntax tree preserves comments/whitespace as nodes
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:191`

> unmaintained (~2017); Java 8 only; will break on Schesch scenarios using lambdas-with-modern-types or var-binding | rejected
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:192`

### <a id="d-148"></a>D-148 — Tier C guards else-if flattening and paren stripping ultra-conservatively

`2026-05-14` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** flatten_else_if fires only when the wrapping block has exactly one structural child that is an if_statement AND contains no variable_declarator / local_variable_declaration descendant; strip_redundant_parens matches only a parenthesized_expression whose sole structural child is itself a parenthesized_expression, with no precedence analysis.

**Why.** The variable-declaration check prevents scope-change bugs, since block removal is only semantics-preserving when the block declares nothing — a conservative trade of a few unrecovered FPs for zero scope-change risk. Paren-wrapping-paren is unambiguously redundant so no operator-precedence reasoning is needed; the admitted cost is that `(a + b) * c` is preserved and cases like `(Long) value` vs `(Long) (value)` do not close, while the dominant double-paren-on-cast pattern does.

**Status.** superseded. Superseded by [D-155](#d-155) — Expand Tier D to six transforms absorbing Tier E's paren strip and token fold, and ship them.

**Source.** `preA:pre-comparator-3b-ast-normalize-13`, `preA:pre-comparator-3b-ast-normalize-14`, `preA:pre-commits-69`, `preA:pre-commits-70` · Artifacts: `merge-tool-comparison/src/evaluation/ast_normalize.py`, `0b1cfc0`, `c857675`

> Conservative variable-decl check prevents scoping-change bugs.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:241`

> only matches paren-wrapping-paren — does NOT try to remove single parens based on precedence analysis
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:328`

### <a id="d-149"></a>D-149 — Strip java.lang FQNs only for a hardcoded allowlist of common names

`2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** strip_javalang_fqn collapses scoped_identifier / scoped_type_identifier of the form "java.lang." + name only for names in a hardcoded JAVALANG_SIMPLE_NAMES frozenset of ~30–40 common members; names outside the set and non-java.lang FQNs keep their prefix, and out-of-grammar method-invocation chains are not matched.

**Why.** Conservative by design: covering only common cases gives at-most-equal recovery and never false matches against user-shadowed types; the user-shadowed-name risk (e.g. a user-defined `class String`) is vanishingly rare and, if hit, simply leaves the FP as an FP. The observed §9 cases were all in type position.

**Status.** adopted.

**Source.** `preA:pre-comparator-3b-ast-normalize-15`, `preA:pre-commits-71` · Artifacts: `merge-tool-comparison/src/evaluation/ast_normalize.py`, `535a1a3`

> conservative; produces at-most-equal recovery, never false matches
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:339`

> outside the set retain the prefix (conservative — at-most-equal recovery,
>
> — `2026-04-15_pre-commits.txt:1360`

### <a id="d-150"></a>D-150 — Treat all comments as semantically irrelevant, with a threats-to-validity entry instead of a warning

`2026-05-14 → 2026-05-27` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Plan-era sources record unclear authorship; the 2026-05-27 application is recorded as joint (Claude proposed the rewrite, Ali's challenge prompted it).*

**Decision.** strip_comments skips line_comment, block_comment and Javadoc nodes during emit, so comment-only differences never register as tool disagreement — knowingly making the §3 comment-duplication finding invisible. The risk is handled by a documented threats-to-validity entry in STATUS.md only; an informational report warning ("N scenarios have differential comments stripped before comparison") is deferred as separate work. The consequence is applied downstream: the 3 synthetic comment cases score TP for both tools because the canonical oracle's AST tier strips comments, and would favour Mergiraf only under a raw byte oracle the numbers do not use.

**Why.** Comments are declared not semantically meaningful for AST equivalence. The acknowledged risk is that stripping them could hide a real Spork pathology such as comment duplication; the §9 evidence found no comment-duplication residuals across 15 samples, and the earlier aerogear observation was one example on a different scenario set, not the population. In the synthetic-cases correction, the docstring described raw byte-comparison behaviour while labelling it the normalized-oracle outcome, and Spork's FP=0 confirms it never produced a wrong clean merge there.

**Status.** adopted.

**Source.** `preA:pre-comparator-3b-ast-normalize-16`, `preB:pre-comparator-3b-ast-normalize-21`, `preA:pre-stage-gamma-fp-diagnostic-22`, `a:3302d287-02` · Artifacts: `STATUS.md`, `merge-tool-comparison/src/evaluation/ast_normalize.py`, `merge-tool-comparison/src/evaluation/comparator.py:119`, `merge-tool-comparison/tools/make_synthetic_spork_cases.py`

> comments are not semantically meaningful for AST equivalence
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:296`

> But the canonical oracle the docstring claims to use **strips comments** ([comparator.py:119](merge-tool-comparison/src/evaluation/comparator.py:119)) — so those quality differences wash out to TP-for-both
>
> — `2026-05-27_3302d287.txt:43`

### <a id="d-151"></a>D-151 — Withdraw the ~90% Tier C recovery estimate but keep the tier landed and the AST-equivalence finding

`2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: the withdrawal analyses are unclear/claude-authored plan text, while the single-end-of-phase evaluation cadence is recorded as Ali's direction.*

**Decision.** The §3/§6 prediction that Tier C's five transforms would recover ~90% of the 39 still-differ Spork FPs (target TP 37 / FP 6) is withdrawn — actual recovery was X=5 (TP 7 / FP 36) — and with it the mapping from "AST-equivalent" to "recoverable by these five transforms". §9's conclusion that the sampled residuals are AST-equivalent reformatting is explicitly NOT withdrawn, and §9's per-scenario pattern labels are corrected as descriptions of the raw pre-gjf diff rather than of the residual. Only one end-of-phase n=50 report was run (per user direction) rather than the plan's per-phase re-runs, and the Tier C code is not reverted despite missing the acceptance floor.

**Why.** Tier C is a strict subset of a full AST normalizer: gjf absorbs the blank-line and comment churn that dominated the raw-diff labels, leaving residuals dominated by paren-wrapping-cast, single-statement block unwrap, paren-around-binary-chain and hex-literal case — patterns Tier C does not cover and which were minor or invisible in the raw-diff labelling. The code stays because it closes 5 real FPs that the M3.5 + 3j pipeline did not, and reverting would lose verified recovery.

**Status.** adopted.

**Source.** `preA:pre-comparator-3b-ast-normalize-24`, `preA:pre-stage-gamma-fp-diagnostic-23`, `preB:pre-commits-77`, `preA:pre-stage-gamma-fp-diagnostic-24`, `preA:pre-comparator-3b-ast-normalize-21`, `preA:pre-comparator-3b-ast-normalize-23` · Artifacts: `docs/plans/stage-gamma-fp-diagnostic.md §10`, `merge-tool-comparison/reports/results.csv`, `merge-tool-comparison/src/evaluation/ast_normalize.py`

> §9's 15/15 "AST-equivalent reformatting" conclusion is empirically intact. The §3 + §6 estimate that Tier C's 5 transforms would recover ~90% of those FPs was the failed prediction.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:502`

> Tier C code remains landed (it closes 5 real FPs that the M3.5 + 3j pipeline did not; reverting would lose verified recovery).
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:526`

### <a id="d-152"></a>D-152 — Measure recovery with an in-memory prototype and attribute it only cumulatively

`2026-05-14 → 2026-05-16` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Two sources record unclear and two claude; the methodology is stated in Claude-authored plan text with no Ali involvement recorded.*

**Decision.** Recovery estimates must not be derived by matching §9-style per-scenario pattern labels onto a transform set: each scenario is verified against the actual transforms and against the post-gjf residual rather than the raw diff. Tier D and Tier E targets are therefore established by running an in-memory prototype of all transforms over the residual scenarios / the full n=50 dataset before the plan is drafted, and per-phase attribution is obtained by progressively enabling phases. Per-transform recovery is treated as meaningful only cumulatively; per-phase delta tables are labelled approximate and only the final cumulative figure is exact.

**Why.** 3b's §3 estimation error showed that recovery estimates inferred from raw-diff pattern labels do not hold, because the labels overstate the post-gjf relevance of blank-line and comment patterns and understate paren-wrapping-cast and single-statement block patterns. Multiple residual patterns co-occur in single scenarios, so closing one without the others does not change a scenario's TP/FP status — a lesson confirmed across all four tiers.

**Status.** adopted.

**Source.** `preA:pre-comparator-3b-ast-normalize-25`, `preA:pre-comparator-3d-extended-ast-transforms-02`, `preB:pre-comparator-3e-tier-e-transforms-06`, `preA:pre-comparator-3e-tier-e-transforms-04` · Artifacts: `docs/plans/stage-gamma-fp-diagnostic.md`, `workspace/tier_e_prototype_v3.py`, `docs/plans/comparator-3e-tier-e-transforms.md §3`

> Measured empirically via in-memory prototype (all 6 transforms enabled) before drafting this plan — the lesson from 3b's §3 estimation error is that recovery estimates must be measured against the actual transform set, not inferred from raw-diff pattern labels.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:52`

> The lesson — confirmed across all four tiers — is that per-transform recovery is meaningful only cumulatively, never independently.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:410`

### <a id="d-153"></a>D-153 — Defer both Tier D and 3a after Tier C and publish the post-Tier-C numbers as interim

`2026-05-14` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: claude

**Decision.** After Tier C, both closure routes stay deferred — Tier D's broader transforms (cast-aware paren strip, single-statement block unwrap, precedence-guarded binary paren strip, ~3–5 days) and 3a test-suite ground truth — and the post-3b Tier C numbers are committed in reports/results.csv as the current honest interim state.

**Why.** Each Tier D transform adds the same risk/scope discussion as the original Tier C transforms and collectively amounts to a separate cycle; 3a is expensive per the mergiraf-integration §3 cost analysis, though principled.

**Status.** superseded. Superseded by [D-155](#d-155) — Expand Tier D to six transforms absorbing Tier E's paren strip and token fold, and ship them.

**Source.** `preA:pre-stage-gamma-fp-diagnostic-25` · Artifacts: `reports/results.csv`, `mergiraf-integration.md §3`

> Both remain deferred. The post-3b Tier C numbers are committed in `reports/results.csv` as the current honest interim state.
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:280`

### <a id="d-154"></a>D-154 — Pin the RM2 output-shape contract with an image-gated shape-probe test

`2026-05-14` · **adopted** · `[recon]` · corroboration: single-pass · confidence: medium · actors: ali

**Decision.** Add test_integration_rename_class_shape_probe, an image-gated test that runs real RM2 and asserts the codeElement is FQN-shaped and that _extract_identifier returns the bare class name.

**Why.** The test will fire if a future RM2 upgrade changes the shape, preventing silent regression.

**Status.** adopted.

**Source.** `preB:pre-commits-61` · Artifacts: `tests/test_rename_conflict.py`

> - New `test_integration_rename_class_shape_probe` — image-gated. Runs
>
> — `2026-04-15_pre-commits.txt:1046`

### <a id="d-155"></a>D-155 — Expand Tier D to six transforms absorbing Tier E's paren strip and token fold, and ship them

`2026-05-15` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: The scope expansion is explicitly Ali's direction; the individual transform designs are recorded as unclear/claude.*

**Decision.** Tier D's scope is widened from D.1–D.4 to six phases, pulling in what the 3b plan had filed as Tier E work — precedence-aware binary paren strip (D.5) and token-canonical whitespace fold (D.6) — with acceptance floor TP ≥ 10 and stretch TP ≥ 14. All six ship: unwrap_single_stmt_block (superseding flatten_else_if, loosening the guard to direct-children-only plus a dangling-else guard), strip_paren_around_primary over ~17 JLS primaries (superseding Tier C's paren-wrapping-paren rule) with a syntactic-paren guard, strip_paren_around_cast, strip_paren_around_binary_safe_parent over ten no-outer-op parents, precedence-aware same-op strip limited to {&&,||,&,|,^}, and token_canonical_fold with atomic literal leaves and re-parse fall-through. Measured recovery on n=50: Spork FP 36→29, Mastery 44→34, JDime 2→1.

**Why.** The scope expansion is recorded as user direction of 2026-05-15. The looser var-decl guard is semantically equivalent because var-decls inside the inner statement's own block are already scoped there, so stripping the outer braces changes no scoping — Tier C's rule was over-conservative; the dangling-else case could re-bind under Java's dangling-else rule. Parens are preserved where Java syntax requires them (`if (cond)`), where postfix would rebind a cast, and where an outer operator could re-bind; `+`, `-`, `*`, `/`, `%` are excluded because `+` is non-associative with mixed types (string-concat-vs-numeric) and the others carry mixed-type concerns. The token fold exists because gjf line-wrap decisions differ when token counts differ, and literals are atomic because naively joining tree-sitter's decomposition with spaces would corrupt their contents.

**Status.** adopted. Supersedes: [D-148](#d-148) — Tier C guards else-if flattening and paren stripping ultra-conservatively; [D-144](#d-144) — Rule out token-level comparison (3d); AST normalize (3b) is the next defensible step; [D-153](#d-153) — Defer both Tier D and 3a after Tier C and publish the post-Tier-C numbers as interim; *Tier D draft with D.1-D.4 only*; *3b plan §11/§13 filing of precedence-aware paren strip and whitespace fold as Tier E*.

**Cross-theme.** *depended on by* ← [D-250](#d-250) (see the reconciliation note there)

**Source.** `preA:pre-commits-73`, `preA:pre-comparator-3d-extended-ast-transforms-01`, `preA:pre-stage-gamma-fp-diagnostic-26`, `preA:pre-commits-75`, `preA:pre-commits-76`, `preA:pre-commits-77`, `preA:pre-commits-78`, `preA:pre-commits-79`, `preA:pre-commits-80` · Artifacts: `docs/plans/comparator-3d-extended-ast-transforms.md`, `merge-tool-comparison/src/evaluation/ast_normalize.py`, `3dfecf0`, `99a5f90`, `9333692`, `ac9114e`, `1eff174`, `9e90b23`, `1c6eb87`

> **Expanded scope** per user direction 2026-05-15: includes precedence-aware paren strip (D.5) and token-canonical whitespace fold (D.6) — what the original 3b plan §11 / §13 had filed as Tier E.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:6`

> semantically equivalent: var-decls inside the inner statement's own block
>
> — `2026-04-15_pre-commits.txt:1465`

### <a id="d-156"></a>D-156 — Tier D paren-stripping is fenced by syntactic, postfix, safe-parent and precedence guards

`2026-05-15` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Tier D's paren transforms carry explicit guards, each with a unit or integration test: skip when the parent is if/while/do/synchronized/switch (syntax requires the paren); strip around a cast only when the parent is not field_access, method_invocation or array_access; strip around binary/ternary only for the ten whitelisted SAFE_BINARY_PAREN_PARENTS, excluding binary, unary, cast and postfix parents; strip same-op parens only for {&&,||,&,|,^} with arithmetic operators deferred to Tier E; refuse single-statement unwrap when the outer `if` has no else and the inner statement is an `if`, or when the single child is a local_variable_declaration; and fall back to the unfolded emit whenever the token fold's re-parse reports has_error, never raising.

**Why.** Java syntax requires the parentheses in those statement contexts, so stripping would produce invalid Java. In the unsafe cast parents the postfix `.`, `()` or `[]` would rebind from the cast result to the cast value; in all other contexts the outer paren adds no semantic information. The whitelisted binary parents are "no-outer-operator" contexts where the paren can never affect precedence, while excluded ones would change meaning (`-(a + b)` ≠ `-a + b`, `(Long)(a + b)` ≠ `(Long) a + b`). The associative-safe set is pure boolean/bitwise with no implicit type promotion; `+` carries the string-concat associativity gotcha and `*` similar mixed-type concerns, which would need type inference. The dangling-else skip is conservative because the dev source may have written the explicit block to clarify scoping, and the re-parse fall-through avoids corrupting a bad emit.

**Status.** adopted.

**Source.** `preA:pre-comparator-3d-extended-ast-transforms-09`, `preA:pre-comparator-3d-extended-ast-transforms-10`, `preA:pre-comparator-3d-extended-ast-transforms-11`, `preA:pre-comparator-3d-extended-ast-transforms-12`, `preA:pre-comparator-3d-extended-ast-transforms-13`, `preA:pre-comparator-3d-extended-ast-transforms-14`, `preA:pre-stage-gamma-fp-diagnostic-29` · Artifacts: `merge-tool-comparison/src/evaluation/ast_normalize.py`, `merge-tool-comparison/tests/test_comparator.py`, `comparator-3d-extended-ast-transforms.md`

> **Syntactic-paren guard:** skip when parent is `if_statement`, `while_statement`, `do_statement`, `synchronized_statement`, `switch_statement`, or `switch_expression` — Java syntax requires the paren in these contexts.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:34`

> These parent types are all "no-outer-operator" contexts where the paren can never affect precedence — the expression is the full RHS / arg / return value / etc.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:285`

### <a id="d-157"></a>D-157 — Delete Tier C's paren rule once D.2 subsumes it, but keep flatten_else_if

`2026-05-15` · **superseded** · `[recon]` · corroboration: both · confidence: medium · actors: claude

**Decision.** When D.2 strip_paren_around_primary lands, Tier C's narrower strip_redundant_parens is removed rather than kept alongside, with its tests retained but reframed as primary-paren-strip cases. flatten_else_if is retained rather than folded into D.1: D.1's else-clause handling fires only when the else block contains a single non-if statement, and the final call is deferred to D.1 implementation when the dangling-else interaction is concrete.

**Why.** Single source of truth for paren-strip logic avoids two rules expressing the same intent, and the new rule is a strict superset so existing tests should pass unchanged. Generalising D.1 to cover `else { if }` would require also recursing the dangling-else question; absent that, keeping the specific safe handler is preferred.

**Status.** superseded. S12 (2026-07-26): half enacted, half resolved the other way at exactly the deferred decision point — strip_redundant_parens is gone as recommended, but flatten_else_if was not kept: ast_normalize.py:227 records 'Supersedes Tier C's narrower flatten_else_if per plan §4.3', with the dangling-else guard (:431-432) covering the concern that motivated keeping it. The Tier-D implementation decision governs. Superseded by [D-155](#d-155) — Expand Tier D to six transforms absorbing Tier E's paren strip and token fold, and ship them.

**Source.** `preA:pre-comparator-3d-extended-ast-transforms-07`, `preA:pre-comparator-3d-extended-ast-transforms-08` · Artifacts: `merge-tool-comparison/src/evaluation/ast_normalize.py`, `merge-tool-comparison/tests/test_ast_normalize.py`

> Tier C's `strip_redundant_parens` (paren-wrapping-paren) is now a subset; remove it in favor of D.2 to avoid two rules expressing the same intent.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:156`

> Keep `flatten_else_if`; D.1 fires for else-block-containing-non-if-stmt only.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:146`

### <a id="d-158"></a>D-158 — Defer long-array, hex and typed paren work to Tier E/F and bound the comparator-side ceiling

`2026-05-15 → 2026-05-16` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: One source records unclear authorship; two record claude. No Ali involvement is recorded.*

**Decision.** Out of Tier D scope and deferred: same-op `+`/`*` paren strip (needs type inference), hex literal case/leading-zero normalisation, long array-literal whitespace canonicalisation, and text-level line-wrap collapse; the ~15-scenario mixed-pattern long tail is not pursued. The 3a test-suite ground-truth approach is rejected outright on cost. Tier E then fixes an upper bound on comparator-side normalization of roughly Spork TP 38–39 / FP 4–5, with 4 scenarios (2 gjf parse-fails, 2 genuine content disagreements) declared irrecoverable — anything beyond requires test-suite execution.

**Why.** Long-array work is heavy effort and even D.6's token fold may stop short on multi-MB array literals — gjf wraps them differently depending on token count and the fold cannot normalise that without exponential time; hex case affects ~0–1 dominant cases; each long-tail scenario has multiple residual patterns needing several transforms in concert, so returns diminish. 3a is a different approach entirely and was rejected per the mergiraf-integration §3 cost analysis. The four irrecoverable scenarios are irrecoverable by construction, since gjf parse-fails never reach Tier 3.

**Status.** adopted.

**Source.** `preA:pre-comparator-3d-extended-ast-transforms-18`, `preA:pre-stage-gamma-fp-diagnostic-30`, `preA:pre-comparator-3e-tier-e-transforms-22` · Artifacts: `mergiraf-integration.md`, `docs/plans/comparator-3e-tier-e-transforms.md §10`, `docs/plans/comparator-3e-tier-e-transforms.md §12`

> **3a test-suite ground truth.** Different approach entirely; bypasses textual ground truth. Far larger; rejected per `mergiraf-integration.md §3` cost analysis.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:356`

> Maximum reachable Spork TP via any combination of comparator-side transforms is ~38-39 / FP 4-5. Beyond that needs test-suite execution (3a).
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:325`

### <a id="d-159"></a>D-159 — Fix D.1's node-identity bug, replace the non-discriminating test, and set Tier E scope from measured residuals

`2026-05-16` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Phase 3e.0 changes `c is cons` / `c is body` to `==` (with an is-not-None guard) in _try_unwrap_if/_try_unwrap_loop, and the 3e.0 regression test — which passed identically against buggy and fixed code — is replaced with a trailing-comment fixture that fails under the bug. Tier E's scope is then set from the empirically measured residual patterns on the 29 remaining Spork FPs (same-op arithmetic paren strip, unary paren, array-creation shorthand, enum trailing `;`, trailing comma, float suffix, hex case) rather than the brief's predicted list, and long-array whitespace is dropped as a residual driver.

**Why.** tree-sitter returns fresh Python Node wrappers per access so `is` is always False; the cons-block including leading comments got walked twice, producing overlapping edits that corrupt brace balance and make D.6's token fold parse-fail on 6 of the 29 still-FP scenarios. The original test was non-discriminating. The measured prototype patterns contradicted the brief's list, and long-array whitespace closes correctly under D.6's token fold once the D.1 bug is fixed.

**Status.** adopted. Supersedes: *Tier D D.1 `_try_unwrap_if`/`_try_unwrap_loop` identity check using `is`*.

**Source.** `preA:pre-comparator-3e-tier-e-transforms-01`, `preA:pre-commits-84`, `preA:pre-comparator-3e-tier-e-transforms-03` · Artifacts: `merge-tool-comparison/src/evaluation/ast_normalize.py`, `docs/plans/comparator-3e-tier-e-transforms.md`, `workspace/tier_e_prototype_v3.py`, `4db9329`

> but tree-sitter returns fresh Python `Node` wrappers per access — `is` is always False
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:21`

> **The dominant residual patterns are NOT what the brief expected.** Brief listed: `+`/`*` paren strip, long-array whitespace, hex case.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:23`

### <a id="d-160"></a>D-160 — Tier E's eleven transforms are narrowly guarded, with normalization losses admitted as corpus-contingent

`2026-05-16` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** Tier E's transforms are each fenced: unary paren strip only for `!`/`~` in safe parents; same-op arithmetic strip only when the parenthesized expression is the LEFT operand, declined for `+` when the outer-right side contains a string_literal descendant and the inner does not; assignment paren strip only under parenthesized_expression or expression_statement; array-creation shorthand only under variable_declarator or array_initializer; float suffixes stripped and `Nd` canonicalised to `N.0`; hex literals lowercased with no leading-zero normalization; and `assert_statement`/`array_access` added to the existing SAFE_BINARY_PAREN_PARENTS rather than given a new branch. The two text-level transforms emit replacement bytes through the existing _collect_edits mechanism. ISSUES #25 records that 3e.2 and 3e.9 are normalization-loss rather than semantics-preserving in general — sound on this corpus only, hardening deferred.

**Why.** `!` and `~` bind tighter than all binary ops (precedence 14 vs max 12), whereas `-`/`+` have the tricky `(-a).method()` postfix rebind, so those are skipped until needed. Left-associativity makes `(a + b) + c` equal to `a + b + c` while the right position would re-bind, and the string-concat guard is deliberately conservative — worst case a few `+` chains don't close. Assignment is right-associative so changing AST shape in operator contexts could change the parse; the array-creation whitelist excludes method-return and argument contexts; the float-suffix loss is documented as accepted because such suffixes vary cosmetically in numeric-heavy code and the masked disagreement is cosmetic; hex leading-zero direction is ambiguous on the dataset and rarely matters; the widened parent set needs no new branch because no outer operator can rebind there. The independent audit reproduced results byte-identically and found no fake TPs on this corpus.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-250](#d-250) (see the reconciliation note there)

**Source.** `preA:pre-comparator-3e-tier-e-transforms-06`, `preA:pre-comparator-3e-tier-e-transforms-07`, `preA:pre-comparator-3e-tier-e-transforms-08`, `preA:pre-comparator-3e-tier-e-transforms-09`, `preA:pre-comparator-3e-tier-e-transforms-10`, `preA:pre-comparator-3e-tier-e-transforms-11`, `preA:pre-comparator-3e-tier-e-transforms-12`, `preA:pre-comparator-3e-tier-e-transforms-13`, `preB:pre-comparator-3e-tier-e-transforms-02`, `preA:pre-commits-85` · Artifacts: `merge-tool-comparison/src/evaluation/ast_normalize.py`, `ISSUES.md #25`, `THREATS_TO_VALIDITY.md`, `4db9329`

> Conservative direction: skip the strip if guard fires. Worst case: a few `+` chains don't close that could have.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:296`

> ISSUES.md: #25 added (3e.2/3e.9 are normalization-loss, not
>
> — `2026-04-15_pre-commits.txt:1687`

### <a id="d-161"></a>D-161 — ISSUES #23/#3 corrected: the fix is a metrics.py concat guard, report.py is untouched

`2026-05-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: One source records claude making the call; the other(s) do not record who decided. Taken as claude on the only positive evidence, not by majority.*

**Decision.** The plan's and ISSUES' characterisations are rejected as false: report.py contains no dead per-category code path to activate (R2 touches it 0 lines), and compute_metrics's scenarios_categories parameter is wired and passed from cli.py — it is a live wire fed the constant "unknown". ISSUES #23 is fixed by guarding the unconditional concat of tool_metrics and category_metrics at metrics.py:138 so per-category rows are emitted only when more than one distinct category exists; the real remedy for #3 is upstream, producing real categories.

**Why.** report.py (98 lines) has zero category logic and merely renders whatever rows metrics contains, so the duplicate all/unknown rows are produced entirely by metrics.py's unconditional list concatenation. cli.py populates categories[sid] = scenario.category and passes it; interfaces.py defaults category to "unknown" and all 50 cached JSONs contain "unknown".

**Status.** adopted. Supersedes: *rm2-integration.md R2 spec §4/§7: activate the dead per-category path in report.py*; *ISSUES #3 wording that scenarios_categories is never populated*.

**Cross-theme.** *depended on by* ← [D-194](#d-194) (see the reconciliation note there)

**Source.** `preA:pre-rm2-integration-03`, `a:20b53f98-06`, `a:20b53f98-05`, `a:20b53f98-14` · Artifacts: `merge-tool-comparison/src/evaluation/metrics.py`, `merge-tool-comparison/src/evaluation/report.py`, `merge-tool-comparison/src/cli.py`, `merge-tool-comparison/ISSUES.md #23`, `2b95aa3`

> 1. **`report.py` "dead code path; activate it"** — false; no such path. R2 touches `report.py` **0 lines**.
>
> — `2026-05-18_20b53f98.txt:115`

> Plan/ISSUES wording **wrong**. Not "dead param to activate" — it's a live wire fed a constant.
>
> — `2026-05-18_20b53f98.txt:107`

### <a id="d-162"></a>D-162 — Turn the per-cluster-rows-partition-the-all-row property into a regression test

`2026-05-18` · **adopted** · `[chat]` · corroboration: single-pass · confidence: medium · actors: claude

**Decision.** Proposed: assert as a regression test that per-cluster rows sum exactly to the 'all' row (scenarios/tp/fp/tn/fn/crashes across all four tools).

**Why.** It is the strongest correctness evidence for the pivot and was not checked in the original run, where only the existence of categories was verified.

**Status.** adopted. S12 (2026-07-26): tests/test_metrics.py:78-113 pins the partition property — single-category input must emit only 'all' rows, and the multi-category case asserts per-cluster cells that exactly partition the 'all' row. Case-pinned rather than property-quantified, but the regression is covered.

**Source.** `b:20b53f98-20` · Artifacts: `merge-tool-comparison/src/evaluation/metrics.py`

> I did *not* check this in the original run (only that categories existed); it's the strongest correctness evidence and arguably belongs as a regression test.
>
> — `2026-05-18_20b53f98.txt:262`

### <a id="d-163"></a>D-163 — Record R2's per-cluster result as weak-yes, not statistically defensible

`2026-05-18` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The R2 answer is recorded as weak-yes: the direction is consistent with the routing hypotheses (Spork's best cluster is INTRA_BODY, F1 0.88) but per-cluster n is 4–18, so R2 informs but does not by itself justify a future S2/W5 routing elif — a routing cycle still needs S3/W3 evidence at adequate n.

**Why.** Per-cluster n of 4–18 is far below the Wilson-CI bar set in §2, so the signal cannot carry a routing justification on its own.

**Status.** adopted. Supersedes: *Tier C framing that a 'Yes' from R2 justifies adding W5/S2 elifs in a follow-up cycle*.

**Source.** `preA:pre-scope-tier-options-14` · Artifacts: `tools/rm2_tag.py`, `src/evaluation/categorizer.py`, `reports/results.csv`, `ISSUES.md #3`, `ISSUES.md #23`

> performance on this dataset?"*: **weak-yes, not statistically defensible.** The
>
> — `2026-05-05_pre-scope-tier-options.txt:36`

> *informs* but does not by itself *justify* a future S2/W5 elif. A routing cycle
>
> — `2026-05-05_pre-scope-tier-options.txt:41`

### <a id="d-164"></a>D-164 — Verify a methodological claim against code, corpus or the primary text before recording it

`2026-05-20 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: the threat-verification decision is Claude's, the baseline-paper review scoping is Ali's brief to a sub-agent.*

**Decision.** An incoming methodological caveat is treated as a candidate only: first confirm the literal claim at the code sites (schesch_loader.py:180, collector.py:76), then measure its actual prevalence on the n=50 corpus using the locally present repos, before writing it into THREATS_TO_VALIDITY.md. The same discipline is applied to the baseline paper: a sub-agent must first confirm that repo-root evolution.md really is the Schesch et al. text, and if not say so and reconstruct the method from the most detailed secondary descriptions, explicitly marked as secondhand — with the review scoped specifically to how the baseline judges a merge correct (textual equality vs normalization vs test execution) and whether semantic/silent failures were measured at all.

**Why.** A true statement is not automatically a meaningful threat — "The crux is prevalence" — and since the repos are present locally the prevalence can be measured rather than speculated about. The paper file only "reportedly" contains the text, so its provenance must be established before its content is used, and any fallback is lower-grade evidence that must be labelled; the oracle question matters because the thesis positions itself on how much output normalization the baseline did and whether it measured silent failures at all.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-384](#d-384) (see the reconciliation note there)

**Source.** `a:4f4f0f87-01`, `a:dc3bc182-sub-sub-agent-a71788-03` · Artifacts: `merge-tool-comparison/src/data/schesch_loader.py:180`, `merge-tool-comparison/src/data/collector.py:76`, `THREATS_TO_VALIDITY.md`, `evolution.md`

> But before validating it as worth adding, I'll measure actual prevalence on the n=50 corpus, since the repos are present locally.
>
> — `2026-05-20_4f4f0f87.txt:15`

> This matters: I need to know how much output normalization THEY did, and whether they measured semantic/silent failures at all.
>
> — `2026-07-18_dc3bc182_sub-agent-a71788.txt:8`

### <a id="d-165"></a>D-165 — The four-tier canonical oracle is an evaluation-only scoring device applied uniformly to all tools

`2026-05-26 → 2026-07-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

*Actors note: Two sources record unclear (audit sub-agent findings) and two claude; no Ali decision is recorded.*

**Decision.** contents_match's cumulative canonicalization pipeline — whitespace, gjf Docker roundtrip, Tier C's 5 tree-sitter transforms, Tier D's 6 further AST/token transforms, Tier E's 11 phases, with MERGE_COMPARATOR_AST_NORMALIZE defaulting on — replaces naive normalization and is applied identically to all six tools, inside the comparator only. The driver decides clean-vs-conflict purely by conflict markers / exit code and applies no normalization. The oracle is therefore textual/AST equality after the normalizer, not compilation or test execution, and developer resolutions are assumed correct and canonical (unmitigated). The FP-inflation figure for naive textual oracles on AST-reforming tools is stated as ~4× (Spork 42→11), replacing an earlier ~30× characterisation of the same change.

**Why.** Naive text comparison systematically inflates the FP rate of AST-reforming tools (Spork TP 1 / FP 42 under naive normalization), conflating "textually different but semantically identical" with "silently wrong", so a shared canonicalization oracle was needed to separate measurement artifact from intrinsic tool defect. The comparator has ground truth — the developer's resolution — and must avoid scoring reformatting as a wrong merge, while the driver has nothing to compare against at merge time, so there is nothing to normalize-and-compare. Uniform application also answers the objection that Spork looks bad because normalization is not applied to it: normalization benefits Spork most (25 FP recovered) and Mergiraf still dominates.

**Status.** adopted. Supersedes: *naive normalization (strip trailing whitespace + line endings only)*.

**Source.** `a:e1df1610-27`, `a:dc3bc182-sub-sub-agent-ab4c4f-01`, `a:dc3bc182-sub-sub-agent-a74c7a-07`, `a:dc3bc182-39` · Artifacts: `src/evaluation/comparator.py`, `semantic_merge_driver/core/backends/mergiraf_backend.py`, `ISSUES.md #2`, `reports/results.csv`, `THREATS_TO_VALIDITY.md`

> So the AST normalizer is a **scoring device**, not a merge step.
>
> — `2026-05-20_e1df1610.txt:1327`

> naive text comparison **systematically inflates the FP rate of AST-reforming tools**, conflating "textually different but semantically identical" with "silently wrong."
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:55`

### <a id="d-166"></a>D-166 — Cross-tab comparator FPs against Schesch test labels and treat the test label as the truer oracle

`2026-05-26 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

*Actors note: One source records claude making the call; the other(s) do not record who decided. Taken as claude on the only positive evidence, not by majority.*

**Decision.** FP diagnosis re-classifies already-stored tool outputs with normalization off and reports every expansion run at both normalization levels; for each scenario the stored spork.json output is then re-classified under full normalization and crossed with the Schesch test-suite label, splitting FPs into "passes Schesch tests but ≠ dev resolution" (valid alternative merge / comparator gap) and "fails Schesch tests" (genuine wrong merge) — only 16/60 (27%) genuinely wrong. Where exact-dev-match scoring and the test label disagree, the test-suite label is treated as the truer oracle.

**Why.** Exact dev-resolution match overstates errors, and the test-suite label provides an independent ground truth, so the cross-tab is what separates Spork's genuine errors from comparator artefacts. Normalization happens in the report step (re-reading stored tool outputs), so the raw/normalized split needs no tool re-run and no Docker contention with the running clone job. An irreducible floor of residuals remains after canonicalization — including gjf parse-fails and genuine content disagreements — and several exact-dev-match "FPs" actually pass tests.

**Status.** adopted.

**Source.** `a:e1df1610-20`, `a:e1df1610-21`, `a:dc3bc182-sub-sub-agent-ab4c4f-02` · Artifacts: `merge-tool-comparison/reports_spork/`, `merge-tool-comparison/reports_spork_raw/`, `merge-tool-comparison/data/results_spork/`, `reports/results.csv`

> the per-scenario cross-tab that separates Spork's *genuine* errors from comparator-artefacts (does the hard-residual FP fall on Schesch test-failures or test-passes?)
>
> — `2026-05-20_e1df1610.txt:1142`

> an irreducible floor remains (11 Spork residuals, incl. gjf parse-fails and genuine content disagreements), which is *why* the project ultimately treats the Schesch test-suite label as the truer oracle: several exact-dev-match "FPs" actually pass tests (valid alternative merges).
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:55`

### <a id="d-167"></a>D-167 — Reuse the driver-faithful harness and key every cache on the driver commit

`2026-06-11 → 2026-07-03` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources split: the harness reuse mandate is recorded as Ali's, the cache-key fixes as Claude's.*

**Decision.** The scoring harness detect_validate.py is built with driver-faithful invocation of the frozen strategies, Mergiraf-reproduced merges, fail-closed UNANALYZABLE verdicts, a resumable cache keyed on the driver commit, per-merge any-file-flag aggregation, Wilson CIs and G0/G1 gate enforcement; later work extends it (adding a per-category report dimension) rather than writing new harnesses. whole_driver_eval.py's cache key is changed from `{cfg}::{sid}` to include the driver commit for the two subprocess configs, and for the post-fix detector run the four unchanged detectors' cached verdicts are carried across to the new commit key exactly while only the RM2RenameConflict lane is recomputed, with a fresh G1 sanity gate each round.

**Why.** The commit-keyed cache is what makes runs resumable and the frozen numbers auditable. Without the commit in whole_driver_eval's key, a post-flip driver-auto run would silently return pre-flip results for all 471 files with no error or warning, leading to the wrong conclusion — the code fix removes a "remember to clear the cache" step from a trap that fails silently, and detect_validate already keyed by commit. Carrying the four untouched detectors across is exact because their code is identical, and it avoids injecting Joern's margin nondeterminism, cutting the run from ~9h to ~1h.

**Status.** adopted.

**Source.** `b:bfc672b4-41`, `a:8740dbd3-02`, `a:fb0fa5c5-25`, `b:fb0fa5c5-54` · Artifacts: `merge-tool-comparison/tools/detect_validate.py`, `tools/whole_driver_eval.py`, `9e25b4e`

> driver-faithful invocation of the four v1 strategies, Mergiraf-reproduced merges, fail-closed UNANALYZABLE, resumable cache keyed on driver commit `2eed882`, per-merge any-file-flag aggregation, Wilson CIs, G0/G1 gates
>
> — `2026-06-11_bfc672b4.txt:51`

> The code fix is better because it removes the "remember to" from a trap that fails silently.
>
> — `2026-06-24_fb0fa5c5.txt:1396`

### <a id="d-168"></a>D-168 — Report fail-closed blocks and defect-shaped control blocks in separate decomposition rows

`2026-06-11` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** The single RM2 UNANALYZABLE crash counts as blocked but is reported in R2's fail-closed decomposition row, separated from genuine detector flags; the Stage-C report likewise decomposes control-side blocks by shape, quantifying how much of R1 the `old_name(`-pattern defect accounts for, without touching the frozen detectors.

**Why.** Separating the fail-closed component means it cannot inflate the headline detection claim — plan §1 anticipated exactly this — and the old_name( pattern is mechanically identifiable in the recorded issues, so its contribution can be measured without modifying frozen code.

**Status.** adopted.

**Source.** `a:bfc672b4-30`, `a:bfc672b4-29` · Artifacts: `merge-tool-comparison/reports_detection/full/FINDINGS.md`

> that lands in R2's `fail-closed` decomposition row — reported separately from genuine detector flags, so it can't inflate the headline detection claim
>
> — `2026-06-11_bfc672b4.txt:556`

> the report will decompose control blocks by shape (the `old_name(`-pattern is mechanically identifiable in the recorded issues, so I can quantify exactly how much of R1 this one bug accounts for, without touching the detectors)
>
> — `2026-06-11_bfc672b4.txt:603`

### <a id="d-169"></a>D-169 — Whole-merge test labels are a noisy per-file oracle; judge recall against attributable mass

`2026-06-11 → 2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The file-level divergence asymmetry (5/30 positives vs 0 controls in the pilot; 16/180 vs 2/195 at scale) is recorded as evidence that whole-merge test labels are a noisy per-file oracle — a methods-chapter point and a constraint on future experiment design, not a code change. Consequently the 43.3% attributed share of the taxonomy census is treated as the honest ceiling for any file-local detection layer on this population, and detector recall is judged against attributable mass rather than against all 275 units.

**Why.** Positive merges dissolve into file-level Mergiraf conflicts despite the whole-merge "clean" label, and the asymmetry against controls replicates three times, echoing the #28 lesson. The Tests_failed signal is merge-level while the coder only sees intersecting Java files, so the escape mass is a property of the evidence, not a labeling failure — and the ~43% split holds in both strata and across truncation levels.

**Status.** adopted.

**Source.** `a:bfc672b4-39`, `a:16127d04-04` · Artifacts: `merge-tool-comparison/reports_detection/full/FINDINGS.md`, `reports_taxonomy/FINDINGS.md`

> the 16-vs-2 file-level-divergence asymmetry is now a three-times-replicated argument that whole-merge test labels are a noisy per-file oracle — that's a methods-chapter point and a constraint on any future experiment design, not a code change
>
> — `2026-06-11_bfc672b4.txt:685`

> the 43.3% is the honest ceiling for what any file-local detection layer can address on this population — so detector recall gets judged against attributable mass, not against all 275
>
> — `2026-07-24_16127d04.txt:47`

### <a id="d-170"></a>D-170 — Scope P2 as one cost-model table over five configs, reusing Stage C as the driver-mergiraf arm

`2026-06-18 → 2026-06-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources split between claude and joint; the scope was proposed by Claude and settled with Ali in the same session.*

**Decision.** P2 — the whole-driver end-to-end evaluation against the cost model — is named as the next experiment and scoped as a single unified cost-model table over five configurations (bare-git, bare-mergiraf, driver-git, driver-mergiraf, driver-auto) on P1's 164 positives + 193 controls, reporting the three-outcome decomposition per config, the bare→driver cost delta, Wilson CIs and latency with the native-amd64 caveat. The existing Stage C detection run is reused as the driver-mergiraf arm, so only driver-git and driver-auto need fresh Docker compute plus two fast bare baselines. The delta attribution line is corrected to count all 12 merges that became non-clean, not just the 11 FP→conflict cases.

**Why.** P2 is "the actual three-outcome claim, never yet run". Running the detectors over Mergiraf-merged files is exactly what SEMANTIC_MERGE_BACKEND=mergiraf does end-to-end, so re-running Stage C would duplicate ~15h of compute for identical results. The "cost saved ≈99" line undercounted by omitting the fail-closed crash, even though the net cost of 104, computed from real weighted cost, was already right.

**Status.** adopted. Supersedes: *driver-mergiraf 'cost saved ≈99' (11 FP→conflict only)*.

**Source.** `a:12c77ea5-08`, `a:fb0fa5c5-01`, `b:fb0fa5c5-02`, `b:fb0fa5c5-11` · Artifacts: `tools/whole_driver_eval.py`, `reports_detection/full/raw_results.json`, `presentation/thesis_progress_late_jun2026.pptx`

> **Stage C already *is* the `driver-mergiraf` arm** (running the detectors over Mergiraf-merged files is exactly what `SEMANTIC_MERGE_BACKEND=mergiraf` does end-to-end)
>
> — `2026-06-24_fb0fa5c5.txt:91`

> **P2 = one unified cost-model table across 5 configs** on P1's 164+193 corpus, with the hybrid oracle you chose.
>
> — `2026-06-24_fb0fa5c5.txt:101`

### <a id="d-171"></a>D-171 — Score P2 with a hybrid oracle: test label where output matches Mergiraf, dev-match otherwise

`2026-06-24` · **adopted** · `[chat]` · corroboration: single-pass · confidence: medium · actors: ali

**Decision.** P2 correctness uses a hybrid oracle — the Schesch test-suite label where the driver's output matches Mergiraf's reference output, developer-resolution matching otherwise — with the asymmetry documented as a threat.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Source.** `b:fb0fa5c5-03` · Artifacts: `tools/whole_driver_eval.py`, `reports_whole_driver/FINDINGS.md`

> **Hybrid oracle.** Correctness = test-suite label where the driver's output matches Mergiraf's, developer-match otherwise — a documented asymmetry.
>
> — `2026-06-24_fb0fa5c5.txt:1097`

### <a id="d-172"></a>D-172 — An arm64 gjf image had silently disabled normalization: re-score everything in the repaired environment

`2026-06-24 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: One source records unclear (audit sub-agent); the rest are Claude's diagnosis and remediation.*

**Decision.** P2 must run with Docker up for the whole run so contents_match uses the canonical oracle (gjf + AST normalization, both defaulting on), with a "Docker-up required for the citable numbers" reproducibility note in FINDINGS. The earlier attribution of the local/AWS scoring discrepancy to local gjf timeouts is then withdrawn: the google-java-format image had been built on Apple Silicon without --platform linux/amd64, so it exec-format-errored on x86 EC2 and contents_match silently degraded to whitespace-only — it was AWS, and P2's committed AWS scoring, that were under-normalized. The P2 cache, Job A and Job B are re-scored in the repaired instance environment (native amd64 + working gjf + AST), which becomes the definition of canonical; the re-scored pre-flip 5-config table replaces the degraded numbers as the citable pre-flip baseline with pre-flip cache entries migrated to ::843e5f5 keys. CLI-DEPLOY.md records the standing rule to platform-pin images, probe the formatter live, and validate a scoring environment by reproducing the committed canonical numbers; a local re-score verification that had "passed" from the wrong working directory (comparing two missing files) was redone with absolute paths and came back byte-identical. Whole-driver v1's numbers and its stated mechanism are superseded by v2 (pre-flip cost 2055→1925, Spork silent-wrong 64/79→53/79).

**Why.** With Docker down, contents_match silently degrades to whitespace-only normalization and the numbers shift (bare-git pos TN 101/FN 0 → 92/9); the gjf-normalized numbers are the correct ones and match reports/results.csv. The gjf image was the only one in the set without the platform pin, and rebuilding it natively on the instance restored the full 3-tier pipeline. Re-scoring is cheap and loses no compute because all caches store outcomes and content rather than scores, and scoring the same P2 data in one environment makes pre- and post-flip directly comparable. The four legacy tools reproducing exactly — Spork's 32/11 being the acid test since it rides on all 21 normalization transforms — is what proved the repaired instance equalled the canonical environment. The first local diff was a false pass, not evidence.

**Status.** adopted. Supersedes: [D-174](#d-174) — Declare the AWS run the canonical scoring environment and never mix environments in a table; *whole-driver v1 scoring and its stated mechanism*; *P2 AWS-scored pre-flip cost table as citable*.

**Cross-theme.** *depended on by* ← [D-305](#d-305) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-305](#d-305) (see the reconciliation note there)

**Source.** `a:fb0fa5c5-07`, `a:fb0fa5c5-32`, `a:fb0fa5c5-33`, `b:fb0fa5c5-51`, `a:fb0fa5c5-34`, `a:dc3bc182-sub-sub-agent-ab4c4f-07`, `a:06ec13eb-07` · Artifacts: `reports_whole_driver/FINDINGS.md`, `deploy/aws/CLI-DEPLOY.md`, `THREATS_TO_VALIDITY.md`, `ISSUES.md #27`, `b6ae027`

> The **gjf image was arm64** (built on your Mac without `--platform linux/amd64` — the only image in the set without that pin). On x86 EC2 it exec-format-errors on every call, and `contents_match` silently degrades to whitespace-only
>
> — `2026-06-24_fb0fa5c5.txt:1892`

> the "platform-pin + probe the formatter + validate scoring environments by reproducing canonical numbers" rule in CLI-DEPLOY
>
> — `2026-06-24_fb0fa5c5.txt:2037`

### <a id="d-173"></a>D-173 — Derive the post-flip driver-auto table from existing per-file data rather than re-running 12 h

`2026-07-02` · **superseded** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Recommendation adopted at the time: obtain the post-flip driver-auto numbers by derivation (~1 h, zero compute) from the existing 471 route records plus the complete driver-git and driver-mergiraf results, keeping the measured 12 h re-run as optional confirmation.

**Why.** Post-flip auto is by construction "git result if cluster=NONE, else mergiraf result", and RM2 classification is deterministic, so the derivation is exact rather than an estimate — only latency would differ.

**Status.** superseded. Superseded by [D-318](#d-318) — Move each compute run to AWS and shrink the bundle so the move is cheap.

**Cross-theme.** *superseded-by* → [D-318](#d-318) — Located: the superseding decision is the AWS cycle that ran the measured post-flip re-run after all ('the six-tool canonical promotion is produced on the instance alongside the post-flip driver-auto re-run in a single cycle'). The null superseded_by was filled.

**Source.** `a:fb0fa5c5-28` · Artifacts: `tools/whole_driver_eval.py`, `reports_whole_driver/FINDINGS.md`

> Post-flip auto is *by construction* "git result if cluster=NONE, else mergiraf result" — so the post-flip table can be assembled exactly from existing data. RM2 classification is deterministic, so this isn't an estimate
>
> — `2026-06-24_fb0fa5c5.txt:1441`

### <a id="d-174"></a>D-174 — Declare the AWS run the canonical scoring environment and never mix environments in a table

`2026-07-02` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** A single scoring environment is declared canonical — initially the AWS run, as the apparently more-normalized one — results scored in different environments are never mixed in one table, and THREATS records that scoring is environment-sensitive at the ±1-file level.

**Why.** Identical bare-git merge outputs scored differently locally and on AWS (TP 5/FP 126/TN 92/FN 9 vs 6/125/101/0) because contents_match's gjf normalization behaved differently; if one cited table were scored locally and another on AWS, a sharp reader could find rows that disagree.

**Status.** superseded. Superseded by [D-172](#d-172) — An arm64 gjf image had silently disabled normalization: re-score everything in the repaired environment.

**Source.** `a:fb0fa5c5-24` · Artifacts: `THREATS_TO_VALIDITY.md`, `reports_whole_driver/FINDINGS.md`

> **Rule that follows: pick one scoring environment as canonical (AWS — its normalization is the more complete one) and never mix.**
>
> — `2026-06-24_fb0fa5c5.txt:1384`

### <a id="d-175"></a>D-175 — Revise file-level RM2 recall from 66.7% at n=10 to 90.7% at n=50

`2026-07-03 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: The measurement design is recorded as Ali's instruction; the revised finding is Claude's (recorded unclear in the audit source).*

**Decision.** The recall-delta analysis computes per-side and pooled recall (file-level detected types / project-level detected types) with Wilson 95% CIs plus the cluster-assignment impact, and restates file-level RM2 recall as 90.7% [83.8, 94.9] pooled at n=50 (98/108; ours 81.6%, theirs 98.3%), superseding R0's 66.7% point estimate at n=10. File-level detections are a strict subset of project-level (0 hallucinations) and the residual routing-visible miss is a false-NONE of ~2% [0.4, 10.5] that fails safe to conservative git.

**Why.** The n=10 sample's sole gap-driver (ab0oo_javaprslib, 4 cross-file refactorings) reproduces exactly in the larger run — it was the extreme, not the norm; the larger measurement confirmed the direction but corrected the magnitude roughly 4×, and the residual gap fails safe.

**Status.** adopted. Supersedes: *file-level RM2 recall 66.7% at n=10 (R0 recon)*.

**Source.** `b:7b3b2669-07`, `a:dc3bc182-sub-sub-agent-ab4c4f-08` · Artifacts: `merge-tool-comparison/tools/rm2_recall_delta.py`, `reports_rm2_recall/FINDINGS.md`, `ISSUES.md #26`

> 3. Compute per-side and pooled recall delta (file-level detected types /
>
> — `2026-07-03_7b3b2669.txt:30`

> R0's pessimistic n=10 point estimate (66.7%) tightened to 90.7% at n=50 — direction confirmed, magnitude corrected ~4×, and the residual gap fails safe.
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:73`

### <a id="d-176"></a>D-176 — Adopt spgroup/mergedataset as the external oracle, scored on the developer's shipped merge

`2026-07-04 → 2026-07-17` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Phase 2b uses spgroup/mergedataset (UFPE, pinned 04a18017, GPL-3.0) sample-semantic-conflicts.csv as the external benchmark: 17 positives and 66 materializable negatives at method-declaration granularity with in-repo {base,left,right,merge}.java quadruples. detect_validate.py gains `--merged-source developer` as the primary oracle-faithful arm, scoring the developer's shipped merge.java with Mergiraf not used at all for this population, and the Mergiraf re-merge arm runs second as the deployment view; for other populations Mergiraf reproduces the merged file and textual conflicts are marked DIVERGED and skipped. Expectations are anchored on spgroup's own purpose-built OA static analysis (recall 0.28 / precision 0.47, 9 FPs) on the same dataset, and the definitional gap is pre-registered: the broad behavioral-interference label maps to #1×6, #2×6, #3×1, #6×1, none-of-7×3 with zero units for #4/#5/#7.

**Why.** The source quadruples ship in-repo so all 17/17 positives and 66/74 negatives materialize without cloning original repos, and merge.java is the developer's real merge — it is the ground-truth family behind all their papers. Scoring the shipped merge is oracle-faithful (the phase2b pattern), while the Mergiraf arm answers the deployment question of how many units even survive re-merge as silent merges. Because their own purpose-built analysis scores 0.28 recall, nobody should expect big recall numbers here; and because the label taxonomy does not align with the 7 categories, per-category recall for covered categories will be point estimates and the evidential weight sits in the 66-negative FP arm and the single genuine #3-family unit.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-405](#d-405) (see the reconciliation note there)

**Source.** `a:8740dbd3-08`, `a:8740dbd3-24`, `a:8740dbd3-11`, `a:8740dbd3-12`, `a:2e726dc0-06` · Artifacts: `research/outputs/phase2b-recon.md`, `merge-tool-comparison/tools/materialize_phase2b.py`, `merge-tool-comparison/tools/detect_validate.py`

> **Source quadruples ship in-repo** — `{base,left,right,merge}.java` per unit, no original-repo cloning.
>
> — `2026-07-03_8740dbd3.txt:222`

> Calibration anchor: their own purpose-built OA static analysis scores **recall 0.28 / precision 0.47** on this same dataset — nobody should expect big recall numbers here.
>
> — `2026-07-03_8740dbd3.txt:223`

### <a id="d-177"></a>D-177 — Retire the defect-dependent tcurdt flag, revising the headline R2 from 7.3% to 6.7%

`2026-07-06 → 2026-09-04` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

*Actors note: Source records actors unclear; the reasoning and the retirement are Claude's in the transcript, with no separate Ali ruling recorded.*

**Decision.** The headline detection rate is cited as 11 causal / 164 = 6.7% [3.8, 11.6] rather than the June deck's 12/164 = 7.3%; the tcurdt flag is retired because it fired only through a missing call-site exclusion bug.

**Why.** "It was a lucky detection that depended on a bug — so an honest eleven beats a lucky twelve."

**Status.** superseded. Superseded 2026-09-04 — decision text left verbatim; no numbered successor entry (post-close chat ruling, no distilled transcript) (Ali's re-ruling on the audit in merge-tool-comparison/reports_detection/full/audit_2026-09-04.md; recorded 2026-09-05 on branch housekeeping/stage-c-amendment-2026-09-04). The headline is now 9 CAUSAL of 164 = 5.5% [2.9, 10.1]. Two of the eleven positive rulings were changed to DETECTOR-FP: tcurdt (this entry's flag — merged L95 is the method call options.compression() on a live TarOptions parameter, so the 2026-06-20 'undeclared' check was wrong, not merely defect-dependent) and atam4j (merged L27 is the surviving declaration of the renamed method, the file compiles, and the merge-induced break sits in the unflagged sibling PassingTestAcceptanceTest.java — a measured cross-file false negative). The frozen-run block rate stays 12/164 = 7.3% and the post-fix block rate 11/164 = 6.7% (10 flags = 9 causal + the atam4j FP, plus 1 fail-closed); 6.7% is no longer the causal catch. Records amended in place: hit_adjudications.md, FINDINGS.md, claims-ledger [StageCCatch]/[StageCFlagged]/[StageCPostFixBlocked]. Actors: the 2026-07 retirement reasoning was Claude's (see actors_note); the 2026-09-04 re-ruling is Ali's. Supersedes: *June deck headline R2 = 12/164 (7.3%)*.

**Source.** `a:4c7b0828-01` · Artifacts: `presentation/thesis_progress_jul2026.pptx`, `ISSUES #29`, `merge-tool-comparison/reports_detection/full/audit_2026-09-04.md`, `merge-tool-comparison/reports_detection/full/hit_adjudications.md (amended 2026-09-04)`, `thesis/claims-ledger.md [StageCCatch]`

> the adjudication moved the headline R2 from the June deck's 7.3% (12/164) to **6.7% (11/164)** — the tcurdt flag was retired as defect-dependent
>
> — `2026-07-06_4c7b0828.txt:79`

> It was a lucky detection that depended on a bug — so an honest eleven beats a lucky twelve.
>
> — `2026-07-06_4c7b0828.txt:102`

### <a id="d-178"></a>D-178 — Read only cost-model deltas, never the raw per-config column

`2026-07-06` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** In the whole-driver cost tables only deltas that share the corpus bias on both sides — bare→driver and pre→post-flip — may be cited; the raw per-config column (e.g. bare-git 2.94 < bare-mergiraf 4.45) must not be read as a backend comparison.

**Why.** The corpus is defined relative to Mergiraf (positives = "Mergiraf merged clean but tests failed"), so by construction Mergiraf-like configs carry the maximal silent-wrong mass on the positive arm, making the raw column an artifact of corpus construction rather than a backend result.

**Status.** adopted.

**Source.** `a:4c7b0828-03` · Artifacts: `reports_whole_driver/FINDINGS.md`

> **This is not a backend beauty contest, and the raw column is biased.**
>
> — `2026-07-06_4c7b0828.txt:347`

> The only readings that are valid are the **deltas that share the bias on both sides**: bare→driver (the value of detection) and pre→post-flip (the value of the routing repair). Lead with the deltas; never the raw column.
>
> — `2026-07-06_4c7b0828.txt:347`

### <a id="d-179"></a>D-179 — Always present base rates per corpus with the selection predicate attached

`2026-07-08` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Never report a single pooled "in the wild" base-rate number; always present base rates per corpus with the mining/selection predicate stated alongside.

**Why.** The two corpora disagree about the dominant category because of their mining predicates, and that disagreement is itself informative and honest.

**Status.** adopted. S12 (2026-07-26): enacted throughout the reporting — reports_taxonomy/FINDINGS.md states its population predicate in the header ('all Schesch rows with mergiraf == Tests_failed and a Java diff — census n = 308') and opens with the never-blend banner; STATUS.md reports Stage-C, Phase-2b and census rates separately, each with its predicate; no pooled 'in the wild' number appears anywhere.

**Source.** `a:4c7b0828-09` · Artifacts: `reports_taxonomy/FINDINGS.md`

> **Always present base rates per-corpus with the selection predicate attached** — never a single pooled "in the wild" number.
>
> — `2026-07-06_4c7b0828.txt:616`

### <a id="d-180"></a>D-180 — Three-phase inductive coding with a javac compile delta, truncation ladder and parent-side rule

`2026-07-08` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources split between ali (the protocol design brief) and claude (the prompt rules and substitutions); options were put and Ali set the design.*

**Decision.** The taxonomy is derived in three phases: Phase 1 per-unit open coding with structured extraction and open-vocabulary tags; Phase 2 consolidation into a codebook with an explicit granularity rule (mechanism, not symptom) and label arity fixed up front; Phase 3 closed coding of all units with the frozen codebook, reporting pass-1-vs-pass-2 label stability. Per-unit inputs are the per-side diffs, a windowed merged file, the merged-vs-dev diff and a javac compile-delta (single-file javac on each merged and dev file, failures classified PARSE/RESOLVE/OTHER, only the merged-minus-dev delta entering the prompt, raw results to reports_taxonomy/compile_checks.json with the image digest in the manifest), sized by a measured T0–T3 truncation ladder capped at 30k tokens. The prompt requires that the mechanism be constructible from the parent-side interaction alone with the merged-vs-dev diff as corroboration only (rule R2) and that any attributed verdict carry at least two verbatim quotes. The brief's requirement to supply failing-test names is dropped, the dev diff taking its place. No sampling-parameter control is used: run-to-run variance is characterised solely by the pass-1-vs-pass-2 stability metric.

**Why.** The dev-diff is demoted to corroborating evidence by rule R2 to contain anchoring bias. Failing-test names are unavailable because the Schesch table carries no per-test traces. Sampling parameters do not exist on the chosen models, so variance must be measured by the stability metric rather than by temperature.

**Status.** adopted. Supersedes: *brief requirement that per-unit inputs include failing-test names*.

**Cross-theme.** *depended on by* ← [D-106](#d-106) (see the reconciliation note there)

**Source.** `a:cfe6365a-02`, `a:cfe6365a-12`, `a:cfe6365a-14`, `a:cfe6365a-16`, `a:92a3e464-27`, `a:cfe6365a-07` · Artifacts: `merge-tool-comparison/outputs/taxonomy-protocol.md`, `merge-tool-comparison/prompts_taxonomy/phase1_open_coding.md`, `merge-tool-comparison/prompts_taxonomy/phase1_output.schema.json`, `reports_taxonomy/compile_checks.json`

> the mechanism must be constructible from the parent-side interaction (dev-diff is corroboration only), and attributed verdicts need ≥2 verbatim quotes
>
> — `2026-07-08_cfe6365a.txt:91`

> "failing-test names" were replaced by the merged-vs-developer diff because the Schesch table carries no per-test traces
>
> — `2026-07-08_cfe6365a.txt:95`

### <a id="d-181"></a>D-181 — Escape hatches are first-class outputs and the escape mass is a reported stratum

`2026-07-08 → 2026-07-10` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources record claude, ali and joint; the design was Claude's recommendation, adopted and then ruled on by Ali.*

**Decision.** The Phase-1 prompt protocol includes mandatory escape hatches (none-identified / indeterminate / flaky-suspect), required evidence quotes drawn from the actual diffs, and per-side change summaries before any mechanism claim, with the 13/23 pilot precedent quoted in the prompt to make the hatches legitimate outputs. The resulting 105 escape-hatch units are reported as a first-class "not-cleanly-merge-attributable" stratum in FINDINGS; the codebook covers only the 60 attributed units and must not invent categories to rescue escapes, stated explicitly in the draft preamble.

**Why.** In the pilot only 13/23 misses were attributable to the scored files; an LLM run overnight without escape hatches will produce a confident causal story for every unit, including the unattributable ones, and plausible hallucinated mechanisms are the failure mode. The G1(iii) ruling then found the user's four raw spot-check rejects were population objections rather than mechanism hallucinations, making the escape mass a real, first-class stratum rather than a labeling failure.

**Status.** adopted.

**Cross-theme.** *duplicated by* ← [D-207](#d-207) (see the reconciliation note there)

**Source.** `b:4c7b0828-12`, `a:cfe6365a-03`, `a:4c7b0828-21` · Artifacts: `prompts_taxonomy/`, `merge-tool-comparison/prompts_taxonomy/phase1_open_coding.md`, `reports_taxonomy/phase2/codebook_draft.md`, `reports_taxonomy/FINDINGS.md`

> An LLM run overnight without escape hatches will produce a confident causal story for every unit, including the unattributable ones — plausible hallucinated mechanisms are the failure mode.
>
> — `2026-07-06_4c7b0828.txt:639`

> "not-cleanly-merge-attributable" stratum reported in FINDINGS — do NOT
>    invent categories for them, and say so in the draft's preamble.
>
> — `2026-07-06_4c7b0828.txt:1211`

### <a id="d-182"></a>D-182 — Clarify only the escape-hatch boundary, and not via the merged-vs-developer diff

`2026-07-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Amendment 2 clarifies only the escape-hatch boundary between none-identified and indeterminate, and must not use "merged output equals the developer's shipped resolution" as the discriminator; the 3 named-category↔category disagreements are deliberately left unaddressed by rule.

**Why.** merged==dev is the normal case for this population — Schesch units are developer merge commits and Mergiraf reproducing them is expected (144/275, 36 of them carrying real named-category mechanisms) — so it is not a no-mechanism signal, and rule R2 forbids leaning on the dev-diff. The named-category instability is 3 idiosyncratic one-off boundary calls across three different pairs: noise, not systematic, and not fixable by one rule.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-226](#d-226) (see the reconciliation note there)

**Source.** `a:9e4b6896-07`, `a:9e4b6896-09` · Artifacts: `reports_taxonomy/phase3/amendment2_proposal.md`

> I explicitly did *not* key it on "merged == developer resolution" — that's the normal case here (144/275, 36 with real mechanisms) and R2 forbids leaning on the dev-diff.
>
> — `2026-07-11_9e4b6896.txt:235`

> The named-category instability is just 3 idiosyncratic one-off boundary calls (three different pairs) — noise, not systematic, and not fixable by one rule.
>
> — `2026-07-11_9e4b6896.txt:213`

### <a id="d-183"></a>D-183 — Scope S4 as the full 308-merge double closed-coding census under the frozen codebook

`2026-07-11` · **adopted** · `[chat]` · corroboration: single-pass · confidence: medium · actors: claude

**Decision.** Session 4 will closed-code the full census (all 308 merges, both splits) twice with the frozen codebook, evaluate G3 stability (agreement ≥80% ∧ κ≥0.70), take Ali's reliability adjudication, and produce FINDINGS.md with base rates and Wilson CIs.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted. S12 (2026-07-26): executed as specified — reports_taxonomy/FINDINGS.md records the S4 census (2026-07-09→12): both splits closed-coded twice under the frozen codebook, G3 stability 82.9%/κ0.788 PASS, Ali's reliability adjudication 12/12, base rates with Wilson CIs.

**Cross-theme.** *depended on by* ← [D-220](#d-220) (see the reconciliation note there)

**Source.** `a:6296f4f6-20` · Artifacts: `FINDINGS.md`

> that's Session 4: closed-code the **full census** (all 308, both splits) twice with this frozen codebook → G3 stability (agreement ≥80% ∧ κ≥0.70) + your reliability adjudication → `FINDINGS.md` with base rates + Wilson CIs
>
> — `2026-07-10_6296f4f6.txt:420`

### <a id="d-184"></a>D-184 — S-D5 runs a baseline arm in a new two-arm harness that refuses no-op runs

`2026-07-15 → 2026-07-23` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** S-D5 runs two arms — a baseline arm with current lanes and the experimental flag off, plus the experimental arm — and reports *added* recall as a first-class deliverable. It must use a new two-arm harness rather than the frozen, flag-blind detect_validate.py or its cache keys, adopting ::exp1-style flag-state namespacing, wiring D1/D2 into the experimental arm explicitly, keying the verdict classifier on the "<Lane> analysis inconclusive:" prefix, and attributing D3-widened vs Joern findings by message prefix. detector_tune_run.py is a thin wrapper reusing Stage-C conventions (same mergiraf image, same CLEAN/FLAG/UNANALYZABLE mapping, merge reproductions cached by image and detector verdicts by driver commit), sets the experimental env var before importing the lane, and refuses to score at all unless the lane first FLAGs an embedded positive micro-fixture. Held-out recall is counted any-lane per unit for the citable number, with per-lane attribution reported separately; and because the two arms ran sequentially, within-arm runtime drift must be checked before the paired latency delta is cited.

**Why.** D3 widens existing lanes, so some held-out units in its categories would be flagged by the current lanes anyway — without a baseline run the FINDINGS cannot honestly claim *added* recall, the one number that justifies the cycle. The frozen detect_validate.py is flag-blind, so its cache keys cannot distinguish flag-ON from flag-OFF verdicts and would corrupt a default-vs-experimental comparison; reusing rather than reimplementing the Stage-C machinery keeps the numbers comparable-in-kind, and the micro-fixture precondition ensures a 0-flag run cannot silently be a no-op lane. Per-lane attribution does not matter for the citable number, which is pooled any-lane family recall, so a D2-category unit caught by the rename lane still counts. Sequential arm order means EBS lazy-restore and RAM caches favour the second arm, so the latency delta could be confounded.

**Status.** adopted. Supersedes: *single-arm S-D5 evaluation design*.

**Cross-theme.** *depended on by* ← [D-111](#d-111) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-102](#d-102) — other_uid a:fb0fa5c5-39 landed there: the discriminating-regression-test standard is the companion requirement from the 2026-05-16 audit.

**Source.** `a:4c7b0828-31`, `a:82dd479f-17`, `a:f0d70a59-08`, `b:f0d70a59-08`, `a:acf7e1d0-16`, `a:68c24033-15` · Artifacts: `outputs/detector-cycle-plan.md §9`, `merge-tool-comparison/tools/detector_tune_run.py`, `merge-tool-comparison/tools/detect_validate.py`, `merge-tool-comparison/reports_detectors/FINDINGS.md`

> S-D5 now runs a **baseline arm** (current lanes, flag off) and the **experimental arm**, reporting *added recall* as a first-class deliverable.
>
> — `2026-07-06_4c7b0828.txt:1805`

> it refuses to score at all unless the lane FLAGs an embedded positive micro-fixture first — a 0-flag run can't silently be a no-op lane
>
> — `2026-07-16_f0d70a59.txt:147`

### <a id="d-185"></a>D-185 — Add a machine quote-provenance precheck to future closed-coding instruments

`2026-07-15` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Recommended as an optional, not-started follow-up: a machine precheck that verifies model-supplied evidence quotes actually occur in the model's input.

**Why.** The fabricated-quote instance caught during adjudication is recorded in THREATS §4.4.9 as the motivation.

**Status.** adopted. S12 (2026-07-26): the optional follow-up was built — the adopted quote-grading decision put a machine quote-provenance check into the spec-batch tooling (the detector-cycle instrument), and this decision-record's own pipeline enforces the same check mechanically (verify_extractions.py G-QUOTE).

**Source.** `a:9e4b6896-32` · Artifacts: `THREATS_TO_VALIDITY.md §4.4.9`

> One optional follow-up worth considering (not started): a machine quote-provenance precheck for future closed-coding instruments — the fabricated-quote instance you caught is recorded in THREATS §4.4.9 as the motivation.
>
> — `2026-07-11_9e4b6896.txt:1304`

### <a id="d-186"></a>D-186 — Build quote grading into the spec batch tooling as a machine precheck

`2026-07-15` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Extracted specs must carry verbatim quotes with file+line and an explicit cannot-extract escape per field, and quote grading runs as a machine precheck (91 exact / 3 normalized / 0 absent on 48 units) rather than being left to manual inspection.

**Why.** The fabricated-quote lesson from program #30 is now enforced mechanically instead of by review.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-469](#d-469) — other_uid a:c4c4d030-08 landed there: the two-pass extraction proposal reuses the same stability protocol and quote-provenance discipline on the decision-record corpus.

**Source.** `a:506d875b-07` · Artifacts: `detector_specs_batch.py`, `specs/specs.csv`

> **Zero fabricated quotes** (91 exact / 3 normalized / 0 absent) — the #30 fabricated-quote lesson is now a built-in machine precheck.
>
> — `2026-07-15_506d875b.txt:133`

### <a id="d-187"></a>D-187 — Cite Error Prone's default-on ERROR criteria as precedent for the lane's zero-FP bar

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Use Error Prone's published criteria for default-on ERROR checks — "the bug pattern should have no false positives" — as the citable external precedent justifying the stale-reference lane's zero-false-positive criterion, while treating Error Prone itself as non-applicable at the mechanism level.

**Why.** Error Prone runs inside javac after attribution, so an unresolved name is a compile error before any check fires and it can have no dangling-reference check; what transfers is not the mechanism but its published FP bar.

**Status.** adopted. S12 (2026-07-26): formally adopted into the review record — ISSUES.md #31 (c) reads 'Error Prone (javac-resolved only; zero-FP ERROR-check policy = citable precedent)', with the comparison in reports_detectors/tune_d3/review_oss_comparison.md. The thesis text does not exist yet; the precedent is on the record it would cite.

**Source.** `a:82dd479f-sub-sub-agent-aadfd1-02` · Artifacts: `https://errorprone.info/docs/criteria`

> its published bar for default-on ERROR checks — "the bug pattern should have no false positives; in essentially no cases should the detected code actually be working as intended" — is direct precedent for the lane's zero-FP criterion.
>
> — `2026-07-16_82dd479f_sub-agent-aadfd1.txt:27`

### <a id="d-188"></a>D-188 — Classify the verdict_of "inconclusive" substring collision as harness-only, not blocking

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** The finding that verdict_of distinguishes fail-closed blocks from genuine flags purely by the substring "inconclusive" in the issue message — while SignatureStaleCall interpolates raw Java identifiers and full declaration strings — is reported as a candidate finding but explicitly not treated as a blocking defect.

**Why.** Impact is harness-only: driver.py uses result.is_clean directly so the merge is still rejected, and in detector_tune_run.py both buckets fail the gate so the FAIL verdict is preserved and only the reported reason is wrong; the same fragility already exists in RM2RenameConflict and ImportPruneUsage messages.

**Status.** adopted. S12 (2026-07-26): the non-blocking disposition was enacted and recorded — detect_validate.py:227-234 still keys on the 'inconclusive' substring (the frozen Stage-C instrument, deliberately untouched), and ISSUES.md #31 records the non-fix with its reason plus the S-D5 guidance that the new harness key on a message prefix.

**Source.** `a:acf7e1d0-sub-sub-agent-a5d889-02` · Artifacts: `merge-tool-comparison/tools/detect_validate.py:234`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py:277-284`

> Impact is harness-only (driver.py uses `result.is_clean` directly, so the merge is still rejected)
>
> — `2026-07-16_acf7e1d0_sub-agent-a5d889.txt:49`

### <a id="d-189"></a>D-189 — Pivot the comparison from four academic tools to six centred on the driver's own backends

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** The tool comparison moves from the legacy 4-tool academic table (git, jdime, mastery, spork; no Wilson CIs) to a six-tool table adding Mergiraf and Weave — the driver's own backends — with all six adapters enabled in config/tools.yaml and the old table kept as reports/results_4tool_legacy.csv.

**Why.** Two of the four original academic tools give no usable signal: JDime crashes on 96% of cases in this harness and Mastery is intrinsically lossy (drops GPL headers, Javadoc), so the pivot was forced by the data.

**Status.** adopted. Supersedes: *4-tool academic comparison (reports/results_4tool_legacy.csv)*.

**Cross-theme.** *duplicates* → [D-066](#d-066), [D-400](#d-400) — Not merged: the adapter work (2026-05-20), the comparison-design pivot (this entry) and the headline-table promotion (thesis-framing) are three decisions on one arc. Cross-linked.

**Source.** `a:dc3bc182-sub-sub-agent-ab4c4f-09` · Artifacts: `config/tools.yaml`, `src/tools/`, `reports/results_4tool_legacy.csv`

> so the 4-tool→6-tool pivot toward the driver's own backends was itself forced by the data.
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:76`

### <a id="d-190"></a>D-190 — Keep the four detection instruments firewalled and never blend their numbers

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The Stage-C real-data evaluation, the spgroup external oracle, the taxonomy census and the D1/D2/D3 detector cycle are treated as four separate instruments whose results are reported separately and never pooled into a combined figure.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-410](#d-410) (see the reconciliation note there)

**Source.** `a:dc3bc182-sub-sub-agent-a495a0-01` · Artifacts: `merge-tool-comparison/reports_detection/`, `merge-tool-comparison/reports_taxonomy/FINDINGS.md`, `merge-tool-comparison/reports_detectors/`

> Four deliberately firewalled instruments (never blended): Stage-C real-data eval, the spgroup external oracle, the taxonomy census, and the in-flight D1/D2/D3 detector cycle.
>
> — `2026-07-18_dc3bc182_sub-agent-a495a0.txt:32`

### <a id="d-191"></a>D-191 — A flag is a detector FP only if its claim about the scored artifact is false

`2026-07-22` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The standing adjudication test is restated and applied: a flag counts as a DETECTOR-FP only when the claim about the scored artifact is false — the name resolves, the uses are in comments or strings, or the breakage pre-existed in theirs. A stale `Tests_passed` label disagreeing with the flag does not make it an FP.

**Why.** D1's claim is verifiably true of the scored file (javac rejects it), and calling it an FP would require D1 to stay silent on a file that provably cannot compile, inverting the lane's purpose; the version-skew problem lives in the corpus and its labels, recorded in THREATS, not in the lane.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-216](#d-216) — other_uid a:bfc672b4-14 landed there: the blockchain reclassification is an application of this FP test.

**Source.** `a:06ec13eb-10` · Artifacts: `Stage-C §4.6`, `THREATS_TO_VALIDITY.md`

> **The FP test this program has used since Stage-C §4.6 is: "is the detector's claim about the scored artifact true?"**
>
> — `2026-07-22_06ec13eb.txt:208`

> if we called it DETECTOR-FP, the required "fix" would be to make D1 stay silent on a file that provably can't compile because a stale label disagrees — which inverts what the lane is for.
>
> — `2026-07-22_06ec13eb.txt:212`


## Corpora & sampling

*49 primary source decisions → 20 entries; 2 not promoted (reasons in `docs/decision-record/entries/corpus-sampling.json`).*

### <a id="d-192"></a>D-192 — Require a positive and a negative scenario per conflict category in tests/data

`2026-04-16` · **abandoned** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Each of the 7 conflict categories must have at minimum one positive scenario (should be rejected) and one negative scenario (clean merge of the same structure, should be accepted), stored as tests/data/<category>/{base,ours,theirs}.java plus expected_result.txt.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** abandoned. S12 (2026-07-26): never built — semantic_merge_driver/tests/data/ contains only dfi_stale_read/ and loop_bounds/, not the planned 7-category positive/negative tree. The RefMerge-era plan this came from was reverted and no later work revived the requirement.

**Source.** `preA:pre-architecture-refmerge-15` · Artifacts: `tests/data/`

> Each conflict category requires **at minimum**:
>
> — `2026-04-16_pre-architecture-refmerge.txt:801`

> - 1 negative scenario (clean merge of same structure — should be accepted)
>
> — `2026-04-16_pre-architecture-refmerge.txt:803`

### <a id="d-193"></a>D-193 — Schesch's AST-Merging-Evaluation is the pipeline corpus; ConflictBench/ConGra/RefMerge rejected

`2026-04-22 → 2026-05-20` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Two sources attribute the dataset evaluation and the filter correction to Claude; the plan-era pipeline-use source does not attribute the call, so 'claude' is taken from the attributed sources rather than by majority.*

**Decision.** From R1 onward the pipeline's corpus is Schesch's AST-Merging-Evaluation dataset (6,045 merges, test-suite ground truth), which RM2 tags; ConflictBench (180 scenarios, manual labels) is at most a secondary source and ConGra is treated as a dataset only, never as a Mergiraf-vs-git comparison, with the RefMerge dataset also rejected (recorded in tool-evaluation-findings.md §9). When the thesis states Schesch/Reaper's repo-selection criterion it must cite the criterion the code actually applies — language == Java AND stars > 5 — not the get_repos.py comment's '>10 stars and unit_test > 0.25', whose unit_test filter is commented out.

**Why.** Schesch is already aligned with Ali's merge-tool-comparison and explicitly includes Mergiraf, and RM2 generates the tags, so Schesch is the input to tag rather than a validation set; ConflictBench has cleaner labels but a much smaller N, and ConGra evaluates LLMs rather than merge tools. For the repo filter, the get_repos.py comment and the executed code disagree, so only the applied criterion is accurate to cite.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-14`, `preB:pre-tool-evaluation-findings-20`, `b:e1df1610-04` · Artifacts: `docs/plans/tool-evaluation-findings.md §9`, `merge-tool-comparison/data/schesch-dataset/src/get_repos.py`

> **Pipeline use (R1 onward):** Schesch dataset. RM2 *generates* the tags; Schesch is the input to tag, not a validation set. ConflictBench / ConGra / RefMerge dataset evaluated and rejected
>
> — `2026-04-22_pre-rm2-integration.txt:142`

> primary — already aligned with Ali's `merge-tool-comparison` |
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:321`

> the get_repos.py *comment* says ">10 stars and unit_test > 0.25", but the *code* applies `stars > 5` with the unit_test filter commented out
>
> — `2026-05-20_e1df1610.txt:184`

### <a id="d-194"></a>D-194 — Tag scenarios with RM2 file-level on ours/theirs only, ungated; resolution axis and project-level deferred

`2026-04-22 → 2026-05-20` · **adopted** · `[mixed]` · corroboration: both · confidence: medium · actors: claude

*Actors note: The two rm2-integration plan sources do not attribute the call; the ungated-tagging recommendation and the May correction of the pipeline order are both Claude's, so 'claude' is taken from the attributed sources.*

**Decision.** Add RefactoringMiner-2.0-derived per-scenario tagging (refactoring presence and type cluster) to merge-tool-comparison with no gate, via tools/rm2_tag.py. Tagging is file-level on the `ours` and `theirs` axes only: the `resolution` axis and project-level (Path-D dual-mode) tagging, together with the file-vs-project recall-delta finding, are deliberately not done. MergeScenario gained a `refactorings` field read by a schema-tolerant `from_dict` rather than the plan's `cls(**data)`. The tags are generated by this project after cloning — they are not present in Schesch's tables, so refactoring cluster cannot be used as a selection filter at step 1.

**Why.** Tagging resolves half of ISSUES #3, where all scenarios currently carry category="unknown", so it was worth proceeding ungated. The plan's claim that schesch_loader.py's `cls(**data)` was already backwards-compatible with a nested refactorings field was simply false. And Schesch's result_adjusted.csv has zero refactoring/cluster columns — Schesch never ran RefactoringMiner and measures merge correctness via test suites — so classification is a step the project generates after cloning, not a filter available at selection time.

**Status.** adopted. Supersedes: *R1 spec: three RM2 runs per scenario (base→ours, base→theirs, base→resolution)*; [D-195](#d-195) — Let an R0 recall-delta harness decide file-level vs project-level RM2 tagging.

**Cross-theme.** *depends-on* → [D-161](#d-161) — Located by content: the per-category metric rows ISSUES #3 unblocks are owned by the metrics entry (the #3/#23 concat-guard fix).

**Cross-theme.** *supersedes* ← [D-079](#d-079) (see the reconciliation note there)

**Source.** `preA:pre-tool-evaluation-findings-13`, `preA:pre-rm2-integration-04`, `preA:pre-rm2-integration-27`, `a:e1df1610-08` · Artifacts: `merge-tool-comparison/tools/rm2_tag.py`, `merge-tool-comparison/src/data/schesch_loader.py`, `merge-tool-comparison/ISSUES.md #3`

> Tagging is file-level `ours`/`theirs` only (no `resolution`, no project-level — the Path-D recall-delta finding is deferred).
>
> — `2026-04-22_pre-rm2-integration.txt:6`

> Partially resolves [`ISSUES.md`](../../merge-tool-comparison/ISSUES.md) #3 (all scenarios currently `category="unknown"`)
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:138`

> **classification is step 4 (you generate it), not a filter you can apply at step 1.**
>
> — `2026-05-20_e1df1610.txt:499`

### <a id="d-195"></a>D-195 — Let an R0 recall-delta harness decide file-level vs project-level RM2 tagging

`2026-04-22` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** R0 was to run RM2 both file-level and project-level on 5–10 scenarios and diff the refactoring sets, with the recall delta picking the tagging mode: ≥80% file-level recall ⇒ file-level everywhere (Path B), 50–80% ⇒ Path D dual-mode tagging with file-level runtime, <50% ⇒ project-level mandatory with runtime caching treated as an engineering problem.

**Why.** The harness output was treated as load-bearing: it determines R1's tagging mode and whether R4a can be file-level at runtime.

**Status.** superseded. Superseded by [D-194](#d-194) — Tag scenarios with RM2 file-level on ours/theirs only, ungated; resolution axis and project-level deferred.

**Source.** `preA:pre-rm2-integration-13` · Artifacts: `docs/plans/rm2-integration-recon.md`

> **Load-bearing decision** — output determines R1's tagging mode and whether R4a can be file-level at runtime:
>
> — `2026-04-22_pre-rm2-integration.txt:135`

> 50–80% → hybrid: R1 dual-mode (Path D in R1), R3 file-level, R4a file-level
>
> — `2026-04-22_pre-rm2-integration.txt:137`

### <a id="d-196"></a>D-196 — Select FP inspection samples by size stratification plus programmatic bucketing, not arbitrarily

`2026-04-22 → 2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

*Actors note: One pass attributed the diagnostic's stratification choice to Claude; the plan and commit-log sources do not attribute it, so the record does not settle authorship.*

**Decision.** Resolve execution-sequence.md §5 open-question #1 in favour of size-stratified plus programmatic sampling: bucket all 42 Spork false positives programmatically by diff type via four normalizations, and choose the three diffs for qualitative inspection by size stratification (smallest / median / largest by merged-content length of the largest bucket), rather than arbitrary or random selection.

**Why.** Arbitrary 3-scenario selection would have over-weighted whatever the random sample happened to catch; size-stratification covers Spork's behaviour across input sizes without manual selection bias.

**Status.** adopted. Supersedes: *arbitrary sample selection for stage-γ FP inspection*.

**Source.** `preA:pre-execution-sequence-10`, `preA:pre-commits-49`, `preA:pre-stage-gamma-fp-diagnostic-02` · Artifacts: `10c8a54`, `docs/plans/stage-gamma-fp-diagnostic.md`, `docs/plans/execution-sequence.md §5`

> Size-stratification ensures the sample covers Spork's behavior across input sizes without manual selection bias.
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:27`

> vs arbitrary selection) in favour of size-stratified + programmatic.
>
> — `2026-04-15_pre-commits.txt:835`

### <a id="d-197"></a>D-197 — Skip scenarios with more than one merge-base, and describe the mechanism correctly

`2026-05-20` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Claude verified the threat, corrected the mechanism and recommended detect-and-exclude; Ali made the ruling that fixed 'skip' rather than 'flag' as the default, so the call is joint.*

**Decision.** Rule the merge-base simplification a genuine but rare threat to validity (prevalence 1/50 — adangel_pmd 312d4c60c0, PMD.java — where the stored base blob f545e551 genuinely differs from git's reconstructed virtual base 8a58c56d by real code, not whitespace) and record it in THREATS_TO_VALIDITY.md with the mechanism stated correctly: `repo.merge_base()` is called without `all=True`, so GitPython returns a length-1 list (git's single reported ancestor) even in criss-cross histories — the alternative base is dropped inside `git merge-base`, not by the `[0]` index, and the loader never sees the multiplicity. Adopt detect-and-exclude: materialization queries `git merge-base --all left right` and skips any merge with more than one base, reporting the drop count. This is the baked-in safety rule of tools/select_materialize.py, at a cost of at most one scenario on the canonical corpus (n 50→49, ~2%).

**Why.** Every clause of the caveat was verified against the code and the corpus, prevalence was measured at 1 of 50, and the affected case was shown to differ by real code on the file under test, so the simplification is non-vacuous while the topic appears nowhere in the existing threats document. Exclusion is methodologically clean — only scenarios with an unambiguous base are scored, so the fidelity gap cannot arise — it needs minimal code and no new git-version dependency, and at ~2% the data cost is trivial while it fully removes the ambiguous-ancestry confound from a comparison whose ground truth is the developer merge.

**Status.** adopted. Supersedes: *Claude's earlier proposal to wire the --all detector defaulting to *flag* rather than drop*.

**Cross-theme.** *depended on by* ← [D-384](#d-384) (see the reconciliation note there)

**Source.** `b:4f4f0f87-02`, `a:4f4f0f87-02`, `a:e1df1610-03`, `a:4f4f0f87-04`, `b:4f4f0f87-07`, `a:e1df1610-04` · Artifacts: `merge-tool-comparison/src/data/schesch_loader.py:180`, `merge-tool-comparison/tools/select_materialize.py`, `THREATS_TO_VALIDITY.md`

> **Detect-and-exclude (recommended).** Call `repo.merge_base(ours, theirs, all=True)`; if it returns >1 base, skip or flag the scenario.
>
> — `2026-05-20_4f4f0f87.txt:88`

> if it has more than one base skip it to be safe
>
> — `2026-05-20_e1df1610.txt:467`

> At ~2% the data cost is trivial and it fully removes the confound
>
> — `2026-05-20_e1df1610.txt:324`

> The loader never sees the multiplicity — it gets git's single default pick and uses it.
>
> — `2026-05-20_e1df1610.txt:309`

### <a id="d-198"></a>D-198 — Do not replicate git ort's virtual-base synthesis; exclude and note instead

`2026-05-20` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Advise against building a replica of git's `ort` virtual-base synthesis (recursively merging all merge-bases via `git merge-tree --write-tree` and feeding the resulting blob as base); for the thesis defense, exclude-and-note is preferred.

**Why.** It is disproportionate effort for 2% of cases, requires git ≥ 2.38, and has its own edge case — the virtual base can itself conflict, as changelog.md did in the test — all for a single scenario that is not even on the §4.1 floor path.

**Status.** adopted. S12 (2026-07-26): the advice was followed — no merge-tree/virtual-base synthesis code exists; tools/select_materialize.py:43 documents skipping multi-base scenarios (the adopted skip-multi-merge-base rule), which is the exclude-and-note path this entry recommended.

**Source.** `a:4f4f0f87-05`

> but it's disproportionate effort for 2% of cases, needs git ≥ 2.38, and has its own edge case: the virtual base can itself conflict
>
> — `2026-05-20_4f4f0f87.txt:90`

> For a thesis defense I'd exclude-and-note rather than build the `ort` replica
>
> — `2026-05-20_4f4f0f87.txt:92`

### <a id="d-199"></a>D-199 — Expand the corpus by targeted, diversity-capped selection on Schesch outcome columns, not first-N

`2026-05-20 → 2026-05-26` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

*Actors note: Claude ruled out first-N expansion, found the outcome-column lever, mapped its tool coverage and set the cap/seed/buffer mechanics; Ali chose targeted expansion ('Targeted expansion it is.'), so the call is joint.*

**Decision.** Do not scale the corpus by raising the loader's alphabetical first-N cap. Instead expand via a 5-step pipeline: select tool-discriminating rows from result_adjusted.csv using Schesch's per-tool outcome columns (e.g. git fails but a structured tool passes), clone on demand, materialize with the multi-base skip, RM2-tag, then run the 6 aligned tools — implemented as the reusable, resumable tools/select_materialize.py with TARGET=60 for the first run. The draw caps how many merges come from any one repo and uses a fixed seed, yielding 60 scenarios across 50 distinct repos against the canonical 50 from 15 repos with 46% from two. The outcome-column lever exists only for git, spork and mergiraf; candidates for jdime, mastery and weave must still be found by materializing and running the tools locally. A requested explicit +20% candidate over-provisioning was declined in favour of logging the existing buffer ratio.

**Why.** The current 50 are alphabetical first-N rather than sampled, with 46% from just two repos, so the next alphabetical batch compounds the existing bias rather than fixing it — and the dominant uncertainty, the false-NONE recall gap, cannot be resolved by more cases without ground-truth labels. Schesch's per-tool outcome columns are a free filter that yields tool-discriminating, non-synthetic scenarios while paying clone cost only on the wanted rows, and the per-repo cap plus seed delivers the diversity that 'better statistics' actually needs. Header inspection showed Schesch tested ~16 algorithms but deliberately excluded jdime as 'unsuitable for practical use', never evaluated mastery, and has no weave column. The +20% buffer is covered by design: the criterion yields 811 candidates for target 60 (13–34× over-provisioning), failures simply trigger more attempts, and only successes count toward TARGET.

**Status.** adopted. Supersedes: *raising max_scenarios on the alphabetical first-N loader*.

**Source.** `b:e1df1610-02`, `a:e1df1610-09`, `a:e1df1610-07`, `a:e1df1610-10`, `a:e1df1610-25` · Artifacts: `merge-tool-comparison/tools/select_materialize.py`, `merge-tool-comparison/src/data/schesch_loader.py`, `merge-tool-comparison/config/datasets.yaml`, `merge-tool-comparison/data/schesch-dataset/results/reaper/result_adjusted.csv`

> **Sampling bias compounds.** The loader walks repos alphabetically and takes first-N, so bumping the cap just extends the same skew
>
> — `2026-05-20_e1df1610.txt:117`

> Schesch's **per-tool outcome columns are the free filter you were missing.**
>
> — `2026-05-20_e1df1610.txt:503`

> Targeted expansion it is.
>
> — `2026-05-20_e1df1610.txt:695`

> **60/60 materialized across 50 distinct repos** — major diversity win vs the canonical 50 (15 repos, 46% from 2).
>
> — `2026-05-20_e1df1610.txt:727`

### <a id="d-200"></a>D-200 — Report the discriminating corpus's rates as upper bounds and set-up comparisons, not absolute rates

`2026-05-25 → 2026-07-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** Knowingly build the expanded corpus from deliberately discriminating rows and disclose the bias as a caveat rather than switching to random sampling: FP rates from that corpus are reported as upper bounds relative to a random sample, and the damage-score bars are valid only for comparing set-ups against each other, never for claiming absolute damage rates in the wild.

**Why.** The set is deliberately git-fails/structured-wins and the corpus is built around cases where the smart merger goes silently wrong, so it is harder than a natural sample; the trade buys tool-discriminating, non-synthetic scenarios at low clone cost, and both corpora are reported separately rather than conflated.

**Status.** adopted.

**Source.** `a:e1df1610-12`, `a:16127d04-15` · Artifacts: `merge-tool-comparison/reports_expanded/results.csv`

> **Selection bias:** this set is deliberately git-fails/structured-wins, so FP rates are **upper bounds** vs a random sample.
>
> — `2026-05-20_e1df1610.txt:802`

> this corpus is built around cases where the smart merger goes silently wrong, so the bars are for comparing *set-ups against each other*, not for claiming absolute damage rates in the wild.
>
> — `2026-07-24_16127d04.txt:278`

### <a id="d-201"></a>D-201 — Build the Spork pool from cheap outcome-based criteria, not the cluster-targeted option

`2026-05-26` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** For the Spork niche question, pursue the two outcome-based selections — Spork-wins (`spork=Tests_passed AND gitmerge_ort≠passed`) and Spork-wrong-merges (`spork=Tests_failed`) — as a single 60-scenario pool, instead of Claude's recommended Option 1 (large pool → tag → keep INTRA_BODY & Java for a CI-grade verdict).

**Why.** Both criteria are cheap one-line criterion flips with no cluster problem, and the two goals pair naturally because one Spork-focused pool yields both wins and wrong-merges (688 + 584 disjoint rows across 485 repos).

**Status.** adopted.

**Source.** `a:e1df1610-19` · Artifacts: `merge-tool-comparison/tools/select_materialize.py`, `merge-tool-comparison/data/scenarios_spork/`

> Both are outcome-based selections — cheap to target, no cluster problem. And they pair naturally: one Spork-focused pool yields both
>
> — `2026-05-20_e1df1610.txt:986`

> My read: given ISSUES #27 just landed, **Option 1** is the one that actually moves the thesis
>
> — `2026-05-20_e1df1610.txt:984`

### <a id="d-202"></a>D-202 — Materialize every intersecting Java file per merge, keyed so units cannot collapse

`2026-06-11 → 2026-07-04` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** Extend select_materialize.py with `semantic`/`semantic_ctl` criteria, an INTERSECT_MAX bound (≤3 intersecting files) and per-merge multi-file materialization keyed by merge_id, keeping only Java files that have all four revisions present. The same keying principle is applied at unit granularity in materialize_phase2b.py: scenario JSONs carry a unit-level merge_id (17 pos / 66 ctl in gitignored data/scenarios_phase2b{,_ctl}/) so multiple method-declaration units from one merge commit do not collapse into a single scenario.

**Why.** num_intersecting_files counts all intersecting files while only Java files with all four revisions present are usable, so extraction keeps exactly that subset (pool sizes were verified to match the plan); and keying at unit level is what prevents cross-unit collapsing.

**Status.** adopted.

**Source.** `b:bfc672b4-40`, `a:8740dbd3-23` · Artifacts: `merge-tool-comparison/tools/select_materialize.py`, `merge-tool-comparison/tools/materialize_phase2b.py`

> `num_intersecting_files` counts all intersecting files, while we keep only Java files with all four revisions present
>
> — `2026-06-11_bfc672b4.txt:33`

> → 17 pos / 66 ctl scenario JSONs in gitignored `data/scenarios_phase2b{,_ctl}/` (unit-level `merge_id`, so no cross-unit collapsing).
>
> — `2026-07-03_8740dbd3.txt:228`

### <a id="d-203"></a>D-203 — Count materialization losses as census attrition, after recovering unreachable parents by SHA

`2026-06-11 → 2026-07-09` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Treat materialization shortfalls as population attrition to be reported, not as a sampling choice: the Stage-C 180-of-195 yield is reported in FINDINGS as attrition from commits no longer reachable upstream (controls were refilled to 195/195 from the candidate buffer). Later, add an `_ensure_commits` step to select_materialize.py, wired before merge_base, that fetches the exact parent commit SHAs from origin, recovering merges whose parents sit on deleted/rebased branches; accept the residual 17 failures (2 persistent transient B losses + 15 A losses) as counted losses in units.csv, giving A=180 + B=111 = 291/308 (94%) materialized and 275 scored, with the accounting stated exactly as 275 scored + 16 divergence-dropped + 17 materialization-loss = 308.

**Why.** The 15 Stage-C losses are all `unresolved` — force-pushed or GC'd upstream history — rather than clone failures or timeouts, so they are population attrition to report. GitHub does serve unreachable parent commits by SHA, so an explicit pre-merge_base fetch recovers ~18% of the stratum-B census, which justified the targeted enhancement. The remaining losses are small (1.8% of B) and counting them per protocol keeps the census accounting exact.

**Status.** adopted. Supersedes: *accept the 19/20 merge_base-unresolved B merges as materialization losses*.

**Source.** `a:bfc672b4-20`, `a:92a3e464-12`, `a:92a3e464-13` · Artifacts: `tools/select_materialize.py`, `reports_taxonomy/units.csv`, `data/scenarios_semantic`, `data/scenarios_semantic_ctl`

> The 15 losses are all `unresolved` — commits no longer reachable in the upstream repos (force-pushed/GC'd history), not clone failures or timeouts. That's population attrition to report in FINDINGS, not a sampling choice.
>
> — `2026-06-11_bfc672b4.txt:408`

> GitHub **does** serve these unreachable parent commits by SHA. So the 20 "unresolved" merges are recoverable by explicitly fetching the exact commits before `merge_base`. That recovers ~18% of the B census — worth a targeted enhancement to the materializer.
>
> — `2026-07-08_92a3e464.txt:190`

> Census accounting is exact: 275 scored + 16 divergence-dropped + 17 materialization-loss = 308.
>
> — `2026-07-08_92a3e464.txt:281`

### <a id="d-204"></a>D-204 — Scope any taxonomy refresh at scale as a stratified ~150–200 sample, not a full census

`2026-07-06` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Scope the 'taxonomy refresh at scale' future-work item as a stratified ~150–200-unit sample with LLM-drafted labels plus a reliability subset (~1.5–2 weeks part-time, ~$15 of AWS), rather than a full 300–600-unit census.

**Why.** It reuses all existing harness and UI, costs ~$15 of AWS, and yields a citable base-rate table with CIs — 80% of the value for ~30% of the effort — with the full 300–600 census left defensible as further future work if a reviewer pushes for it.

**Status.** superseded. S12 (2026-07-26): the program that actually ran (S0 2026-07-08 onward) censused the full 308-merge population rather than the proposed ~150-200 stratified sample; the census-population decision replaced this scoping. Superseded by [D-205](#d-205) — Taxonomy population is the full 308-merge semantic census, stratified by intersecting files ≤3/>3.

**Source.** `a:4c7b0828-07` · Artifacts: `outputs/taxonomy-protocol.md`

> I'd **scope it as a stratified ~150–200 sample with LLM-drafted labels + a reliability subset**, not a full census.
>
> — `2026-07-06_4c7b0828.txt:523`

> 80% of the value for ~30% of the effort. The full 300–600 census is defensible as *further* future work if a reviewer pushes for it.
>
> — `2026-07-06_4c7b0828.txt:523`

### <a id="d-205"></a>D-205 — Taxonomy population is the full 308-merge semantic census, stratified by intersecting files ≤3/>3

`2026-07-08 → 2026-07-08` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: two record Ali as ruling the population and the stratum-B materialization route, two record Claude as specifying the census/stratification and unit definition. Options were put and Ali ruled, so 'joint'.*

**Decision.** The taxonomy population is the Schesch merges satisfying the `semantic` criterion in merge-tool-comparison/tools/select_materialize.py (mergiraf == Tests_failed; ~308 full, 195 at num_intersecting_files ≤ 3), and the full census-308 is labeled rather than a 195 cap or a sample. It is stratified into stratum A (intersect ≤3) and stratum B (>3); coding units are merge-level, defined by the Stage-C divergence rule. Stratum A reuses the existing data/scenarios_semantic/ JSONs and the mergiraf-merged files cached in reports_detection/full/raw_results.json verbatim; stratum B is materialized by an opt-in complement filter (num_intersecting_files > 3, INTERSECT_MIN) on the `semantic` criterion into data/scenarios_taxonomy_hi/, with merged files produced by merge-tools/mergiraf:0.17.0 under the Docker-only convention. Unit inputs are trimmed by a measured T0–T3 truncation ladder capped at 30k tokens.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted. Supersedes: *195-cap or stratified-sample alternatives for the labeling population*.

**Cross-theme.** *superseded-by* → [D-326](#d-326) — Partial, exactly as the flag says: only the fixed-12-file T3 truncation clause was replaced by the T3-floor + hard-fit search (a:92a3e464-17, landed in [D-326](#d-326)). The entry stays adopted; rendered as a clause-level refinement, not a supersession.

**Cross-theme.** *depends-on* → [D-287](#d-287) — The Docker-only rule under which stratum-B merged files are produced.

**Source.** `b:cfe6365a-02`, `a:cfe6365a-11`, `b:cfe6365a-17`, `a:92a3e464-26` · Artifacts: `merge-tool-comparison/outputs/taxonomy-protocol.md`, `merge-tool-comparison/tools/select_materialize.py`, `data/scenarios_taxonomy_hi/`, `87424be`

> - Population: Schesch merges where mergiraf == Tests_failed (the `semantic`
>
> — `2026-07-08_cfe6365a.txt:16`

> census-308 population stratified by intersect ≤3/>3 (stratum A reuses Stage-C scenarios + cached mergiraf merges verbatim)
>
> — `2026-07-08_cfe6365a.txt:90`

### <a id="d-206"></a>D-206 — Commit a seeded 60/40 derivation/held-out split before any labeling, firewalling held-out

`2026-07-08 → 2026-07-09` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: The split rule and firewall were ruled jointly (options put, Ali ratified); the S1 ordering requirement that the split file be committed before any content-bearing request is Claude's specification.*

**Decision.** A seeded 60/40 taxonomy-derivation vs held-out split is committed before any labels exist: S1 computes and commits reports_taxonomy/split_assignment.csv (SEED=20260709, 60% derivation, stratified A/B) before any API request containing unit content is made, and held-out units receive no Phase-1 requests. Held-out contents are firewalled from the codebook and from future detector design, while closed coding still covers the full census so reported base rates stay census-wide.

**Why.** The split is committed before labels exist and the held-out side firewalled specifically to protect future detector evaluation, while retaining full-census closed coding so the reported base rates remain census-wide.

**Status.** adopted.

**Source.** `a:cfe6365a-13`, `a:4c7b0828-18` · Artifacts: `reports_taxonomy/split_assignment.csv`, `outputs/taxonomy-protocol.md §4`

> seeded 60/40 split committed before any labeling, held-out contents firewalled from the codebook and future detector design, closed coding still covering the full census so base rates stay census-wide
>
> — `2026-07-08_cfe6365a.txt:90`

> Split file FIRST: compute the seeded 60% derivation split (SEED=20260709,
>
> — `2026-07-06_4c7b0828.txt:1006`

### <a id="d-207"></a>D-207 — Carry the escape-hatch mass forward as a 'not-cleanly-merge-attributable' stratum

`2026-07-10 → 2026-07-10` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Claude proposed the carry-forward in response to Ali's objection; Ali issued the G1(iii) ruling that fixed the codebook scope, so the call is joint. The ruling source is placement='also' and belongs to another theme.*

**Decision.** Log Ali's population objection as a marked Phase-2 carry-forward rather than reopening the frozen §2 population definition: the 63.6% escape-hatch mass becomes a first-class 'not-cleanly-merge-attributable' stratum in the FINDINGS honest-coverage accounting. The codebook therefore categorizes only the 60 attributed derivation units, no categories are invented for the 105 escape-hatch units, and the draft's preamble must say so.

**Why.** Ali's 'not a good representation' reaction points at how much of the frozen Tests_failed population is not a clean merge-induced mechanism — worth its own accounting regardless of how G1(iii) scores — but the §2 population is frozen, so the mass is reported as its own stratum instead of being forced into mechanism categories.

**Status.** adopted.

**Cross-theme.** *duplicates* → [D-029](#d-029), [D-181](#d-181), [D-421](#d-421) — a:6296f4f6-03 is primary here and cited as 'also' by the recode entry. Four entries state distinct facets (population stratum / coding outputs / recode ruling / reporting); kept separate and cross-linked. Coverage is owned here only.

**Source.** `a:788e483b-08`, `a:6296f4f6-03` · Artifacts: `ISSUES #30`, `reports_taxonomy/phase2/codebook_draft.md`

> the 63.6% escape-hatch mass becomes a first-class "not-cleanly-merge-attributable" stratum in the FINDINGS honest-coverage accounting — the frozen §2 population is untouched
>
> — `2026-07-09_788e483b.txt:341`

> CARRY-FORWARD (G1 iii): the codebook covers the 60 attributed units;
>
> — `2026-07-10_6296f4f6.txt:39`

### <a id="d-208"></a>D-208 — Held-out units are labeled in Phase 3, but their contents never appear in prose

`2026-07-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Phase 3's double closed-coding batch covers all 275 scored census units, derivation and held-out alike, which is legitimate because the instrument is frozen by then; but held-out unit contents never appear in FINDINGS prose, codebook anchors or examples — only their labels do.

**Why.** Labeling held-out units with a frozen instrument is legitimate under §4: the firewall protects against instrument tuning, not against label production.

**Status.** adopted.

**Source.** `a:4c7b0828-23` · Artifacts: `outputs/taxonomy-protocol.md §4`, `reports_taxonomy/FINDINGS.md`

> ALL 275 scored census units — derivation + held-out (labeling held-out
>
> — `2026-07-06_4c7b0828.txt:1303`

> Held-out unit CONTENTS still never appear in FINDINGS
>
> — `2026-07-06_4c7b0828.txt:1353`

### <a id="d-209"></a>D-209 — Constrain, seed and firewall the fresh Tests_passed control draws

`2026-07-15 → 2026-07-15` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Claude raised the under-specification finding and proposed the constraints; Ali ruled the ambiguity gate twice, producing §12 Amendment 1 and the materialize-tune-only instruction, so the call is joint.*

**Decision.** The two fresh Tests_passed control draws (tune n=100, SEED 20260715; eval n=200, SEED_EVAL 20260716) come from the same `semantic_ctl` pool, mutually disjoint and excluding the 195 Stage-C control merges, and are constrained to ≤3 merges per repo with ~60/40 file-count stratification mirroring the census A/B mix, produced by a committed seeded script. Tune-controls are materialized immediately via the select_materialize semantic_ctl path (100 merges / 243 files into data/scenarios_detector_tune/), drawn Stage-C-style so the 100 materialized successes ARE the committed list; eval-controls remain a committed metadata-only list under the §3 firewall, handled by viability checks that read no content plus 40 ordered spares and a deterministic replacement rule applied at S-D5 (§12 Amendment 1).

**Why.** The plan's unconstrained 'n=100 / n=200 fresh Tests_passed merges' wording was a serious under-specification: unconstrained, a single busy repo could dominate the draw, weakening what the zero-FP claim generalizes over, and the file-count mix could differ wildly from the census — more files means more FP surface, so an easy draw flatters the gate. Eval-controls stay unmaterialized because the §3 firewall requires that eval content not be readable during build sessions.

**Status.** adopted. Supersedes: *unconstrained "n=100 / n=200 fresh Tests_passed merges" wording in detector-cycle-plan §4*.

**Cross-theme.** *depends-on* → [D-025](#d-025) — other_uid a:506d875b-06 landed there: the session-scope guardrails this draw specification operates under.

**Source.** `a:4c7b0828-30`, `a:506d875b-03`, `a:506d875b-05`, `a:506d875b-02` · Artifacts: `outputs/detector-cycle-plan.md §4`, `outputs/detector-cycle-plan.md §11`, `outputs/detector-cycle-plan.md §12 Amendment 1`, `data/scenarios_detector_tune/`, `controls/`

> **Finding 1 (serious): the control draws are under-specified.**
>
> — `2026-07-06_4c7b0828.txt:1790`

> ≤3 merges/repo (Stage-C precedent), ~60/40 file-count stratification mirroring the census A/B mix, seeded draw via a *committed script*
>
> — `2026-07-06_4c7b0828.txt:1804`

> eval-controls stay a list — do NOT materialize (§3).
>
> — `2026-07-15_506d875b.txt:29`

> and eval-controls draw from the same `semantic_ctl` pool as tune.
>
> — `2026-07-15_506d875b.txt:129`

### <a id="d-210"></a>D-210 — Document the pre-existing eval-content overlap rather than redraw the committed control lists

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** 32 of the 240 eval/spare merges already have scenario JSONs on local disk from the May comparator programs; the committed lists are not redrawn. The overlap is recorded with the full id list plus an access guard in the manifest (`controls.preexisting_scenario_overlap`) and a note in ISSUES #31, and flagged to Ali as reversible only via a §12 amendment.

**Why.** Hand-adjusting committed lists after seeing results is judged the worse discipline breach; the files are untracked, were not read in the session, and are not sanctioned inputs to any build session.

**Status.** adopted.

**Source.** `a:506d875b-10` · Artifacts: `manifest.json (controls.preexisting_scenario_overlap)`, `ISSUES #31`

> I judged a redraw worse than documentation (hand-adjusting committed lists after seeing results is the real discipline breach)
>
> — `2026-07-15_506d875b.txt:183`

> None are git-tracked, none were read this session, and none are sanctioned inputs to any build session.
>
> — `2026-07-15_506d875b.txt:183`

### <a id="d-211"></a>D-211 — State the single-labeled-corpus limitation: recall and cost numbers rest on Schesch alone

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Frame the detector cycle's dataset scope explicitly as a limitation in the FINDINGS threats section: every headline number (43%, 22%, −11.5%) rests on Schesch alone, with the spgroup mergedataset used only on the false-alarm side.

**Why.** Only Schesch supplies the labeled held-out corpus needed for recall and cost, while spgroup contributes only clean/broken false-alarm pools, so the single-labeled-corpus threat has to be acknowledged.

**Status.** adopted.

**Source.** `a:16127d04-17` · Artifacts: `reports_detectors/FINDINGS.md`

> So the catch-rate claims (43%, 22%) and the damage score (−11.5%) rest on Schesch alone this cycle — that's stated as a limitation in the FINDINGS threats section ("single labeled corpus for held-out").
>
> — `2026-07-24_16127d04.txt:348`

> the second, independent benchmark, used on the false-alarm side only
>
> — `2026-07-24_16127d04.txt:350`


## Adjudication & human oversight

*75 primary source decisions → 26 entries; 3 not promoted (reasons in `docs/decision-record/entries/adjudication.json`).*

### <a id="d-212"></a>D-212 — Re-test the AST-equivalence hypothesis by hand on a 15-sample stratified eyeball

`2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: claude

*Actors note: Ruled by Ali 2026-08-06 (housekeeping PR #10): performed by Claude - Ali does not recall doing the pass himself; the 'your 3j labelling' quote in the 2026-06-11 distillate is thereby ruled a misattribution. actors=claude confirmed.*

**Decision.** Execute option 3j as a 15-scenario stratified manual labelling over the 39 still-differ Spork CLEAN outputs — 5 size quintiles × 3 picks (low/mid/high index within bin) — classifying each post-format diff by dominant pattern with hunk and +/- line counts. The one non-trivial call in the sample (scenario [31], where a `// ---` separator comment appears 3× in Spork vs 1× in dev) is classified as AST-equivalent style rather than duplication pathology and flagged explicitly as the borderline case.

**Why.** To re-test the §3 hypothesis that all 39 unsampled structural FPs are AST-equivalent reformatting at higher sample size, after §8 falsified the 3-sample naive generalisation, and to determine whether the residuals are dominantly AST-equivalent (3b would recover them) or dominantly intrinsic tool pathology. The borderline scenario is arguable either way — on closer reading dev collapses three sibling comments into one in the same hunk while Spork preserves all three — so it is called AST-equivalent for this classification and flagged as the one residual where the call is non-trivial.

**Status.** adopted.

**Source.** `preA:pre-stage-gamma-fp-diagnostic-16`, `preA:pre-stage-gamma-fp-diagnostic-17`

> 15-sample stratified eyeball across the 39 still-differ Spork CLEAN outputs. Size-binned (5 quintiles by merged-file size), 3 picks per quintile (low/mid/high index within bin).
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:177`

> Treating as AST-equivalent style for the purposes of this classification; flagged as the one residual where the call is non-trivial.
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:216`

> it must be a human judgment with written rationale — same protocol as your 3j labelling and the 23-miss classification — because "the tool graded its own homework" is the first thing an examiner will probe
>
> — `2026-06-11_bfc672b4.txt:667`

### <a id="d-213"></a>D-213 — Final adjudication rulings are Ali's; Claude may only draft and must not auto-label

`2026-06-11 → 2026-07-20` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: Claude argued the circularity rationale and the DRAFT protocol (a:bfc672b4-36, a:bfc672b4-04), Ali imposed the no-auto-label constraint (a:0e14484d-01) and later chose the draft-first variant (a:2e726dc0-12). Options were put and Ali picked, so joint.*

**Decision.** In every adjudication round Claude may gather evidence and propose draft labels with written rationales — marked DRAFT, with the original label file left untouched — but no label counts until Ali confirms or overrides it; adjudication UIs are handed over unlabelled and auto-labelling is forbidden. From S-D6 the protocol is explicitly draft-first: Claude generates probe-verified draft labels plus rationales for all 20 held-out flagged units, embedded in the UI with an accept key ('a') and override keys (1/2/3), and the GD4 gate stays Ali's because the rulings only count once he accepts or overrides each one.

**Why.** Plan §4.7 keeps the miss labelling a manual call, so nothing counts until Ali acts on it. More fundamentally the tool cannot grade its own homework: Claude built the detectors, so his own assessment carries the same circularity at one remove, while Ali's independent ruling (he did not write the detection logic) is what carries evidential weight, with the written rationales as the audit trail — "the tool graded its own homework" being the first thing an examiner will probe. Ali restated it as a flat constraint ("the rulings are mine"), and when he later accepted Claude-drafted rationales the precedent cited was that the Stage-C §4.6 UI shipped drafts as starting points rather than answers, with the gate still his.

**Status.** adopted.

**Source.** `a:bfc672b4-04`, `a:bfc672b4-36`, `a:0e14484d-01`, `a:2e726dc0-12` · Artifacts: `reports_detection/pilot/misses_classification_draft.md`, `reports_detection/pilot/misses_classified_draft.csv`, `outputs/p1-stage-c-adjudication-handoff.md`, `merge-tool-comparison/reports_detectors/adjudication/adjudication_ui.html`, `c531017`

> my draft has the same circularity problem at one remove — I built the detectors and I'm assessing them. Your independent ruling (you didn't write the detection logic) is what carries evidential weight.
>
> — `2026-06-11_bfc672b4.txt:794`

> Every label is marked `DRAFT` and needs your confirm/override (plan §4.7 keeps this a manual call); the original `misses_to_classify.csv` is untouched.
>
> — `2026-06-11_bfc672b4.txt:124`

> The GD4 gate stays yours — the rulings only count once you accept or override each one.
>
> — `2026-07-16_2e726dc0.txt:559`

### <a id="d-214"></a>D-214 — Every adjudication round gets a self-contained browser review UI in the house pattern

`2026-06-11 → 2026-07-10` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: Ali specified the browser side-by-side UI (a:bfc672b4-05); Claude built it, wrote the handoff mandating tool-first, and matched the pattern in later rounds (a:bfc672b4-37, b:6296f4f6-10, a:6296f4f6-09); a:8740dbd3-18 is recorded as joint. Options put and Ali picked, so joint.*

**Decision.** Rulings are collected through a generated, self-contained HTML review UI rather than an inline chat widget or ad-hoc tooling: the two artifacts side by side, line-aligned with intraline highlighting, long unchanged runs collapsed, localStorage persistence and CSV/clipboard export. The Stage-C tool (make_adjudication_ui.py, adding a parent-presence table showing whether the flagged name appears in base/ours/theirs plus special handling for the two "verify" cases) becomes the house pattern that later rounds explicitly match — the Phase-2b 17-row mapping_ui.html and the G2 codebook mapping_ui.html with edit/merge/split/rename/accept/reject controls and anchors enriched with Phase-1 summary/tags. The Stage-C adjudication handoff requires the next session to build the tool first, before any labelling, under guardrails forbidding auto-labelling, touching the frozen detectors, or conflating the run with the post-fix run or the §4.7 miss list.

**Why.** Ali asked for a browser version showing the files under question side by side with the non-matching parts highlighted; collapsing long unchanged stretches keeps 1,500-line files scannable. The parent-presence table makes the "merge-induced" question answerable on-page, and the handoff opens by explaining what adjudication is and why it cannot be automated so the next session does not skip to mechanics. Later rounds reuse rather than reinvent because there is an established house pattern for this (the Stage-C adjudication_ui.html), so each new tool is built to match its conventions.

**Status.** adopted. Supersedes: *inline label widget delivered earlier in the pilot session*.

**Source.** `a:bfc672b4-05`, `a:bfc672b4-37`, `a:8740dbd3-18`, `b:6296f4f6-10`, `a:6296f4f6-09` · Artifacts: `merge-tool-comparison/reports_detection/pilot/review_ui.html`, `merge-tool-comparison/reports_detection/pilot/make_review_ui.py`, `outputs/p1-stage-c-adjudication-handoff.md`, `make_adjudication_ui.py`, `mapping_ui.html`, `reports_taxonomy/phase2/mapping_ui.html`, `8856ceb`

> generate browser version and i want to see files under question side by side with non matching part being highlighted
>
> — `2026-06-11_bfc672b4.txt:153`

> the key addition is a **parent-presence table** (does the flagged name appear in base/ours/theirs?) that makes the "merge-induced" question answerable on-page
>
> — `2026-06-11_bfc672b4.txt:804`

> Yes — there's an established house pattern for this (the Stage-C `adjudication_ui.html`). Let me look at how that one was built so this tool matches it:
>
> — `2026-07-03_8740dbd3.txt:427`

### <a id="d-215"></a>D-215 — Ali ruled every adjudication round and accepted the drafts unchanged

`2026-06-11 → 2026-06-20` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: ali

**Decision.** Ali ruled on all 23 pilot misses via review_ui.html, accepting every draft label; these became the adjudicated labels written into misses_to_classify.csv and fixed the final base-rate table (#6-family 8, none-of-7 5, none-identified 9, indeterminate 1, categories #1–#5/#7 zero). He then ruled all 15 Stage-C flags via adjudication_ui.html — all 11 positives CAUSAL, all 4 controls DETECTOR-FP, no draft overridden, with a recorded note on the comatoes case. He directed the fold-back per handoff §3: promote the draft to reports_detection/full/hit_adjudications.md marked ADJUDICATED, recompute R2 decomposed by label in FINDINGS.md, and update STATUS, THREATS row 14 and ISSUES #29.

**Why.** No reason was recorded for accepting the drafts wholesale. The only written reasoning Ali left was on the comatoes unit: the two methods' implementations are very similar (setReservePowerCapacity→setSectorNumber) but the naming gives no hint whether they are the same method, so the developers' intention is hard to tell — while mostly agreeing with the draft.

**Status.** adopted.

**Source.** `a:bfc672b4-06`, `a:0e14484d-10`, `b:0e14484d-07` · Artifacts: `merge-tool-comparison/reports_detection/pilot/misses_to_classify.csv`, `merge-tool-comparison/reports_detection/pilot/FINDINGS.md`, `merge-tool-comparison/reports_detection/full/hit_adjudications.md`, `merge-tool-comparison/reports_detection/full/FINDINGS.md`, `STATUS.md`, `THREATS_TO_VALIDITY.md`, `merge-tool-comparison/ISSUES.md`

> Miss-classification review complete (23/23 labeled via review_ui.html). Final labels:
>
> — `2026-06-11_bfc672b4.txt:188`

> CAUSAL | note: additionally, implementation of this two method are very similar setReservePowerCapacity→setSectorNumber, but naming does not give a hint about if they are same method or not. hard to tell devs intention. mostly agree on the draft
>
> — `2026-06-20_0e14484d.txt:153`

> Please fold these into reports_detection/full/hit_adjudications.md (promote the draft, mark ADJUDICATED), recompute R2 decomposed by label in FINDINGS.md, and update STATUS/THREATS/ISSUES #29 per the handoff §3.
>
> — `2026-06-20_0e14484d.txt:167`

### <a id="d-216"></a>D-216 — Pilot hits labelled DETECTOR-FP; the blockchain compile-error claim withdrawn

`2026-06-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** All 5 flagged sites from the detection pilot are provisionally labelled DETECTOR-FP, giving 0 causal hits. Separately, the Stage-A sub-claim that blockchain's merged file was a confirmed compile error is withdrawn: it is reclassified as a mixed-rename behavioural inconsistency, the confirmed-compile-error count is corrected from 5 to 4 (erudika, jacquesberger, winder, jnr), and blockchain is documented as legitimately undetectable by the v2 id lane and by RM2.

**Why.** Each flagged pattern exists verbatim in base, ours and theirs (one is `if(true)`, not even a loop), so the sites are pre-existing code rather than merge-induced, and the Joern query matches any control structure with a constant condition rather than loops only. The blockchain claim rested on a too-narrow declaration regex (`baseURL =`) while Joern's scope analysis, treated as authoritative, shows `baseURL` does resolve in the merged file.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-191](#d-191) (see the reconciliation note there)

**Source.** `a:bfc672b4-02`, `a:bfc672b4-14` · Artifacts: `reports_detection/pilot/FINDINGS.md`, `reports_detection/pilot/misses_classification_draft.md`, `merge-tool-comparison/reports_detection/pilot_v2/FINDINGS.md`

> all 5 flagged sites are `JoernInfiniteLoop` constant-condition hits **present verbatim in base, ours, and theirs**
>
> — `2026-06-11_bfc672b4.txt:81`

> Provisional label: DETECTOR-FP for all five → **0 causal hits**.
>
> — `2026-06-11_bfc672b4.txt:108`

> My Stage-A "confirmed compile error" claim for blockchain rested on a too-narrow declaration regex (`baseURL =`); Joern proves the identifier is declared.
>
> — `2026-06-11_bfc672b4.txt:338`

### <a id="d-217"></a>D-217 — Adjudication UIs are browser-verified and handed over in a fresh unlabelled state

`2026-06-20 → 2026-07-11` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Before an adjudication UI is handed to Ali it is verified by actually loading it in a browser through a per-UI preview/static-server config — checking for JS console errors, that all units list, exercising the ruling interaction end to end, and measuring the real layout rather than trusting zoomed screenshots — and the underlying data extraction (line numbers, identifier parsing, parent-presence logic, plus every FP and verify case: aerospike, cloudfoundry, mtedone, comatoes) is prototyped and manually confirmed against the actual merged files before the generator is written. Claude's own test labels are then cleared so Ali starts from a fresh 0/n state. Where the preview renders a squished main panel, that is diagnosed as the preview tool's mobile-width viewport crowding out `#main` beside the fixed 320px sidebar — the same flex layout Ali used successfully on his desktop — so no layout change is made and the guidance is simply to use a wide window.

**Why.** Ali will actually drive the UI and it gates the session, so a structural HTML check is insufficient — and with no node available for a JS syntax check the real browser is the check. The extraction must be validated first so the UI surfaces the truth rather than propagating detector artifacts. Test labels are cleared so Ali starts fresh with no Claude-produced labels present at handoff. The narrow-strip diagnosis rests on the DOM and JS having been verified correct via eval with no console errors.

**Status.** adopted.

**Source.** `a:0e14484d-15`, `a:0e14484d-05`, `a:8740dbd3-19`, `a:9e4b6896-13`, `b:6296f4f6-12` · Artifacts: `make_adjudication_ui.py`, `adjudication_ui.html`, `mapping_ui.html`, `reports_taxonomy/phase2/mapping_ui.html`, `reports_taxonomy/phase3/adjudication/adjudication_ui.html`, `.claude/launch.json`, `0228e76`

> Since Ali will actually drive this UI and it gates the session, let me render it in a browser to catch any JS runtime error.
>
> — `2026-07-11_9e4b6896.txt:412`

> Let me verify the actual merged content so the UI surfaces the truth.
>
> — `2026-06-20_0e14484d.txt:20`

> Let me clear my test labels so Ali starts fresh, then take a screenshot for the handoff.
>
> — `2026-06-20_0e14484d.txt:57`

### <a id="d-218"></a>D-218 — UI shows detector output verbatim but re-locates identifiers in the merged file

`2026-06-20` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The adjudication UI displays the detector's reported line numbers verbatim, tagged with a `stripped-coord` vs `merged-coord` pill for provenance, while independently re-locating every flagged identifier in the real merged file to build the context windows (Joern and RM2 call-lane numbers are shown as-is since they map directly). It also drops the declaration-guard regex as a way of deciding whether an identifier is still declared, surfacing all merged-file occurrences of the identifier instead and leaving the judgment to the adjudicator.

**Why.** RM2 var-lane line numbers are computed on comment/string-stripped text and the char-literal newline bug shifts them (ahome "L78" is really merged L248; mtedone "L1538" is a Javadoc line), so showing the reported line would display wrong context and corrupt the adjudication. The DECL-guard regex is fragile — it misses generic types such as `Class<? extends Map<?,?>> mapType` because `?` breaks its character class — whereas all merged occurrences necessarily include the declarations.

**Status.** adopted.

**Source.** `a:0e14484d-02`, `a:0e14484d-03` · Artifacts: `merge-tool-comparison/reports_detection/full/make_adjudication_ui.py`, `adjudication_ui.html`

> showing a wrong line would corrupt the adjudication
>
> — `2026-06-20_0e14484d.txt:16`

> So the UI shows the detector's output **verbatim** (with a `stripped-coord` vs `merged-coord` pill) for provenance, but **re-locates** every identifier in the actual merged file for context.
>
> — `2026-06-20_0e14484d.txt:79`

> my DECL-guard regex misses generic types like `Class<? extends Map<?,?>> mapType` (the `?` breaks its char class), so I'll rely on **showing all merged occurrences** (which already include declarations) rather than the fragile guard
>
> — `2026-06-20_0e14484d.txt:22`

### <a id="d-219"></a>D-219 — Applying rulings is a mechanical edit that must survive regeneration

`2026-07-05 → 2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Rulings are applied to artifacts by hand, without recomputation: Ali's renames, edits, merges and splits are mechanical text changes Claude applies himself when building codebook_frozen.md, and only a REVISE ruling — reserved for wholesale re-clustering because the category structure itself is wrong — reruns Fable-5. Renames are held back and applied inside the freeze commit rather than mid-review. Phase-2b mapping rulings are folded into category_mapping.csv with the per-category FINDINGS table regenerated from cached results and no re-run of the evaluation. And `detector_specs_batch.py report` is changed so that a rerun preserves hand-recorded adjudication blocks and emits the final verdict into the spec table itself, verified idempotent.

**Why.** Renames, edits, merges and splits are mechanical text changes applicable directly, while REVISE is meant for wholesale re-clustering, not renames or a merge or two. Editing category ids mid-review would orphan rulings already saved in the UI, whose saved state is keyed by the old ids. For Phase-2b, since every unit scored 0 detections any relabeling only moves rows between 0/n cells, so the headline numbers cannot change — a low-stakes pass needing no re-run. And as written the report command would have regenerated gd1_machine.json and spec_table.md from scratch, silently wiping the Amendment-2 ruling.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-453](#d-453) (see the reconciliation note there)

**Source.** `a:6296f4f6-12`, `a:6296f4f6-15`, `a:8740dbd3-20`, `a:506d875b-12` · Artifacts: `reports_taxonomy/phase2/codebook_frozen.md`, `merge-tool-comparison/reports_detection/phase2b/FINDINGS.md`, `category_mapping.csv`, `detector_specs_batch.py`, `gd1_machine.json`, `spec_table.md`

> Renames, edits, merges, and splits are mechanical text changes I apply *myself* when building `codebook_frozen.md`
>
> — `2026-07-10_6296f4f6.txt:337`

> because editing the category ids mid-review would orphan the rulings you've already saved in the UI (its saved state is keyed by the old ids)
>
> — `2026-07-10_6296f4f6.txt:285`

> Since every unit scored 0 detections, any relabeling only moves rows between 0/n cells — the headline numbers can't change, which makes this a low-stakes pass.
>
> — `2026-07-03_8740dbd3.txt:450`

> would have regenerated `gd1_machine.json` and `spec_table.md` from scratch, silently wiping your Amendment-2 ruling
>
> — `2026-07-15_506d875b.txt:185`

### <a id="d-220"></a>D-220 — Overnight LLM labels are a pre-registered drafting instrument, never an autonomous oracle

`2026-07-08 → 2026-07-10` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: a:4c7b0828-10 records the acceptance-with-three-fixes as joint (Ali's idea, Claude's conditions, Ali accepted); b:4c7b0828-10 and a:788e483b-09 record Claude stating the validation-loop requirement and reviewer task. Options were put and Ali picked, so joint.*

**Decision.** The overnight LLM taxonomy run is accepted only as a pre-registered drafting instrument inside the existing methodology: its raw output is a draft codebook plus draft labels and nothing more, and it must be followed by a frozen-codebook relabeling pass, a stratified reliability subset (~40–60 units) adjudicated by Ali through a mapping_ui-style tool with reported agreement, a corpus split decided up front so detector evaluation is not run on derivation data, and mandatory attribution escape hatches (none-identified / indeterminate / flaky-suspect) with required evidence quotes. The human reviewer's task in that loop (G1(iii)) is a plausibility + grounding check with exactly two reject grounds — REJECT-HALLUCINATED and REJECT-UNSUPPORTED: the reviewer does not re-derive the ground-truth cause, and an escape-hatch verdict is a legitimate answer to be accepted unless the model clearly ducked an obvious mechanism or fabricated its stated reason.

**Why.** Without the loop the output is vibes, not findings: by the project's own standard (Stage C, Phase-2b) an unadjudicated machine label is provisional and uncitable. Deriving the taxonomy from the Schesch positives and then evaluating the new detectors on the Schesch positives would be tuning on the test set. And an LLM will produce a confident causal story for every unit, including the unattributable ones, so escape hatches must be first-class outcomes rather than failures — the worst error in the study is a confident, well-written, wrong causal story. Hence: run overnight, yes; trust overnight, no.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-183](#d-183) — other_uid a:6296f4f6-20 landed there. S4 (the census run this validation loop governs) itself remains proposed.

**Cross-theme.** *depended on by* ← [D-106](#d-106) (see the reconciliation note there)

**Cross-theme.** *in tension with* ← [D-004](#d-004) (see the reconciliation note there)

**Source.** `a:4c7b0828-10`, `b:4c7b0828-10`, `a:788e483b-09` · Artifacts: `ISSUES #30`, `outputs/taxonomy-protocol.md`

> **1. No validation loop stated → the output is vibes, not findings.** By your own standard (Stage C, Phase-2b), an unadjudicated machine label is *provisional* and uncitable.
>
> — `2026-07-06_4c7b0828.txt:635`

> do it — but as a *pre-registered drafting instrument inside the existing methodology*, not as an autonomous oracle. Run overnight, yes; trust overnight, no.
>
> — `2026-07-06_4c7b0828.txt:653`

> An **escape-hatch verdict is a legitimate answer**, not a failure. Only reject one if the model clearly ducked an obvious mechanism or fabricated something.
>
> — `2026-07-09_788e483b.txt:269`

### <a id="d-221"></a>D-221 — The codebook freezes only on Ali's explicit APPROVE, recorded in the ruling artifact

`2026-07-08 → 2026-07-10` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: a:cfe6365a-04 and a:cfe6365a-10 attribute the freeze-gate and question-first rule to Ali; a:6296f4f6-17 attributes the refusal-to-freeze to Claude and a:6296f4f6-16 is joint. Claude put the interpretation and Ali confirmed, so joint.*

**Decision.** The Phase-2 codebook is frozen only after Ali adjudicates it (mapping_ui.html precedent), and the open protocol questions (census ~308 vs 195-cap vs stratified sample; single- vs multi-label; compile-check yes/no; corpus-split choice) are put to him as concise questions and ruled before the document is frozen and committed. With `overall: null` in the exported rulings JSON the freeze is blocked pending an explicit APPROVE; where the JSON is ambiguous the `action` field is authoritative (category 2's ACCEPT beats its leftover `new_id`) but the reading is put to Ali for confirmation rather than guessed, and his in-session approval is written back into g2_codebook_rulings.json (overall=APPROVE, stray field cleared) before the freeze.

**Why.** ACCEPT wins and honouring the stray value would collide with category 5's new id, and the freeze is irreversible-ish for the program, so Claude would not guess. An explicit APPROVE is required to freeze at all; since the approval arrived in chat rather than via the UI button it was recorded into the ruling artifact, keeping the artifact the record of the decision. (The two cfe6365a sources state the freeze-after-adjudication rule and the ask-before-freezing sequence without recording a reason.)

**Status.** adopted.

**Source.** `a:cfe6365a-04`, `a:cfe6365a-10`, `a:6296f4f6-17`, `a:6296f4f6-16` · Artifacts: `merge-tool-comparison/outputs/taxonomy-protocol.md`, `9209327`, `reports_taxonomy/phase2/g2_codebook_rulings.json`

> is FROZEN after Ali adjudicates it (mapping_ui.html precedent).
>
> — `2026-07-08_cfe6365a.txt:29`

> I can't freeze without an explicit APPROVE.
>
> — `2026-07-10_6296f4f6.txt:377`

> the freeze is irreversible-ish for the program, so I won't guess
>
> — `2026-07-10_6296f4f6.txt:357`

### <a id="d-222"></a>D-222 — Spot-check UI grades whether each evidence quote is really in the model input

`2026-07-09` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The spot-check UI generator draws a seeded stratified sample of 15, shows the exact model inputs beside the model output, and client-side checks whether each evidence quote appears in that input so the reviewer can judge 'unsupported-by-quotes'. The initial binary exact-substring test is replaced the same day by a graded matcher (exact → diff-gutter/whitespace-normalized → per-line-present → genuinely-absent) rendering graded badges.

**Why.** The reviewer needs to know whether a cited quote actually appears in what the model saw — this is crucial for judging 'unsupported-by-quotes'. But the binary checker showed false-red on ~7% of quotes, and the misses were almost all diff-gutter/whitespace artifacts or non-contiguous multi-line concatenations rather than hallucinations, so a brittle exact test would cry wolf and risk Ali over-rejecting; under graded matching zero quotes are absent.

**Status.** adopted. Supersedes: *binary verbatim-substring quote checker in the spot-check UI*.

**Source.** `a:788e483b-02`, `a:788e483b-04` · Artifacts: `taxonomy_spotcheck_ui.py`, `reports_taxonomy/phase1/spotcheck/`

> crucially for judging "unsupported-by-quotes" — verifies client-side whether each evidence quote is a verbatim substring of the input
>
> — `2026-07-09_788e483b.txt:92`

> My binary checker is too strict and would cry wolf, risking Ali over-rejecting.
>
> — `2026-07-09_788e483b.txt:178`

### <a id="d-223"></a>D-223 — Ali may state rulings in plain text instead of using the review UI

`2026-07-10` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Ali may bypass the mapping UI entirely and state his category rulings in plain text in chat, and Claude will apply them; the UI (with a JSON download as a third path) is only a convenience for collecting decisions.

**Why.** The UI is only a convenience for collecting the decisions — if it is fiddly it should not block the ruling.

**Status.** adopted.

**Source.** `a:6296f4f6-10` · Artifacts: `reports_taxonomy/phase2/mapping_ui.html`

> The UI is just a convenience for collecting your decisions — **if it's fiddly, skip it entirely and just tell me in plain text**
>
> — `2026-07-10_6296f4f6.txt:201`

### <a id="d-224"></a>D-224 — Withhold per-unit guidance during the reliability adjudication, explaining layout only

`2026-07-11` · **superseded** · `[chat]` · corroboration: single-pass · confidence: medium · actors: claude

**Decision.** During Ali's G3 reliability adjudication Claude will not say which way an individual unit should go; it will explain the instrument, the rule and the UI layout, but the substantive call on each unit is left entirely to Ali. (Later in the same session Claude did supply general adjudication conventions — see [D-226](#d-226) and [D-227](#d-227) — which narrowed this to per-unit answers only.)

**Why.** Ali's independent call on these units is the whole point of the reliability check.

**Status.** superseded. Superseded by [D-213](#d-213) — Final adjudication rulings are Ali's; Claude may only draft and must not auto-label.

**Source.** `a:9e4b6896-15`

> I'm deliberately not telling you which way this one goes — your independent call on these is the whole point of the reliability check. Ping me if a unit's inputs are confusing to read and I'll explain the *layout*, not the answer.
>
> — `2026-07-11_9e4b6896.txt:530`

### <a id="d-225"></a>D-225 — Adjudicate the primary label only; report unruled disagreements as holes

`2026-07-11 → 2026-07-12` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The adjudication UI resolves the single dominant (primary) mechanism only — that is what the gate and the base rates use; where Ali judges a second mechanism present he notes it in the free-text box, and secondary labels stay reported descriptively as a co-occurrence matrix taken straight from the two passes. Ruling all 47 disagreements is not strictly required for the gate, and any left unruled are reported explicitly as units with no final label — a flagged hole in the 275-unit base rates — rather than silently filled.

**Why.** Per §8 secondaries are reported descriptively while the primary is what the gate and base rates consume. The disagreements are not gated but do supply final labels, so leaving one unruled creates a hole in the base rates which must be flagged and handled as a caveat rather than papered over.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-259](#d-259) — other_uid a:9e4b6896-14 landed there: the rule that the n=12 reliability number is reported as corroborating-only (coarse-n) governs how these rulings are published.

**Source.** `a:9e4b6896-16`, `a:9e4b6896-17` · Artifacts: `labels_final.csv`, `reports_taxonomy/phase3/adjudication/`

> Any disagreement you leave UNREVIEWED has no final label — it becomes a hole in the 275-unit base rates that I'd have to flag and handle as a caveat (not ideal).
>
> — `2026-07-11_9e4b6896.txt:605`

> **1. The UI adjudicates the *primary* only.** The "Final ruling" selector picks the single **dominant** mechanism — that's what the gate and the base rates use.
>
> — `2026-07-11_9e4b6896.txt:653`

### <a id="d-226"></a>D-226 — Escape hatches need an ours×theirs interaction; a visible mechanism beats an escape

`2026-07-13 → 2026-07-14` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Conventions locked in for all escape↔category disagreements in the census adjudication: (a) when one clear, sufficient, merge-induced mechanism is visible, attribute it to the named category rather than escaping, even if other collateral dependencies are off-screen; (b) 'concrete candidate interaction' means an ours×theirs coupling, so a one-sided change whose callers or resources merely sit off-screen is none-identified, not indeterminate — including a broad one-sided refactor whose unshown callers might be inconsistent; (c) the full tree — no ours×theirs interaction → none-identified; interaction visible and breaks → named category; interaction visible and composes cleanly → none-identified; interaction present but the deciding evidence off-screen → indeterminate. An ours×theirs interaction is therefore necessary but not sufficient for indeterminate. Applied the same way each time.

**Why.** Derived from R1 plus Amendment 2: escape hatches are for when no mechanism can be pinned, so you do not bail merely because some other collateral is off-screen. Letting a one-sided "I can't see the callers" slide into indeterminate would push every large merge with off-screen callers to indeterminate, which is precisely what Amendment 2 was written to prevent; and any break in a one-sided refactor would be pre-existing in that side rather than merge-induced (R3), so it cannot escape into a merge mechanism. Where the interaction is visible and clearly breaks, a category is owed.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-182](#d-182), [D-272](#d-272) — Amendment 2 itself (the none-identified vs indeterminate boundary) is evaluation-oracles/[D-182](#d-182); the one-amendment-plus-rerun machinery it spent is gates-freeze/[D-272](#d-272), where other_uid a:9e4b6896-08 landed.

**Source.** `a:9e4b6896-18`, `a:9e4b6896-19`, `a:9e4b6896-20`, `a:9e4b6896-26`

> **escape hatches are for when *no* mechanism can be pinned. When one clear, sufficient, merge-induced mechanism *is* visible, you attribute it** — you don't bail just because some *other* collateral is off-screen.
>
> — `2026-07-11_9e4b6896.txt:719`

> lock in the convention: **"candidate interaction" means ours × theirs; a one-sided change with off-screen callers, where you can't show the other side supplies a stale user, is `none-identified`, not `indeterminate`.**
>
> — `2026-07-11_9e4b6896.txt:764`

> No — that's the key subtlety, so let me correct it cleanly: an ours×theirs interaction is **necessary but not sufficient** for `indeterminate`. Having one does **not** force `indeterminate`.
>
> — `2026-07-11_9e4b6896.txt:768`

### <a id="d-227"></a>D-227 — Three category-boundary conventions fixed during the census adjudication

`2026-07-14` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Three boundary conventions govern the primary label: (1) compile-level beats runtime-level — where a unit has both a pruned-import/changed-signature compile break and a behavioural interaction, the compile break is primary and the behavioural mechanism becomes secondary; (2) for removed vs renamed-or-relocated, the 'successor' must genuinely be the same declaration moved or renamed, so a deleted declaration whose references were switched to a distinct (often library) type sharing the simple name is removed, not relocated; (3) overlapping-edit-interleaving is only labelled when the merged region is a fused hybrid neither side wrote — if the merged region equals one side's version and the break is a reference in a different file, it routes to the removal/rename/signature categories per the interleaving exclusion.

**Why.** A compile error fails the entire suite, and if the file does not compile the changed runtime behaviour never even runs, so the runtime divergence is secondary. The codebook boundary requires the declaration to survive under a new identity; in gwtbootstrap3 the local SubmitEvent was deleted and GWT's FormPanel.SubmitEvent merely shares the simple name — a coincidental match, not a rename lineage. In jdeparser2 the merged definition region was exactly ours' version, failing interleaving's core criterion, and the codebook's interleaving exclusion explicitly routes 'one side's declaration-level change consumed by code the other side added in a different region' to the removal/rename/signature categories.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-452](#d-452) — other_uid b:6296f4f6-17 is cited there; the frozen codebook's own tie-break rule is the parent these adjudication-time conventions extend.

**Source.** `a:9e4b6896-23`, `a:9e4b6896-24`, `a:9e4b6896-25`

> a compile error fails the *entire* suite, and if the file doesn't compile, ours' rewritten `switchWorld` behavior **never even runs**
>
> — `2026-07-11_9e4b6896.txt:886`

> The name match between `AbstractForm.SubmitEvent` (a `GwtEvent<SubmitHandler>` subclass) and GWT's `FormPanel.SubmitEvent` is **coincidental**, not a rename lineage.
>
> — `2026-07-11_9e4b6896.txt:907`

> **when a pass says "overlapping-edit-interleaving," check for an actual hybrid neither side wrote.** If the merged region just equals one side's version and the break is a reference in a *different* file, it's a removal/rename/signature case, not interleaving.
>
> — `2026-07-11_9e4b6896.txt:950`

### <a id="d-228"></a>D-228 — merged == developer proves nothing; verify the merged code itself

`2026-07-14` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Treat a pass's justification of none-identified via 'merged equals developer resolution' as suspect and check the actual merged file; and for disagreement units at truncation level T2/T3, where the line that decides the call was not shown to either pass, verify against the full merged file pulled from the repo data before ruling.

**Why.** merged==dev only means the tool reproduced the developer's own broken merge commit — which is why its tests failed and it is in the dataset — so it carries no information by itself: the paired javapoet/bungeecord cases show it hid a real bug in one and reflected a clean merge in the other, and the discriminator is always whether the merged code contains an actual defect. In the bungeecord case T2 truncation hid ours' surviving `default:` line, which is what flipped pass a into an incorrect overlapping-edit-interleaving call.

**Status.** adopted.

**Source.** `a:9e4b6896-21`, `a:9e4b6896-22`

> whenever a pass justifies `none-identified` with *"merged equals developer, so no mechanism,"* distrust it and check the actual merged code
>
> — `2026-07-11_9e4b6896.txt:832`

> When a unit is T2/T3-truncated and the deciding line isn't visible, that's exactly when it's worth having me pull the full merged file, like here — the truncation is what flipped pass a.
>
> — `2026-07-11_9e4b6896.txt:865`

### <a id="d-229"></a>D-229 — Ali's draft rulings are audited programmatically, review-only, before being applied

`2026-07-14` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

*Actors note: Sources disagree: a:9e4b6896-27 records Ali's instruction to review only, a:9e4b6896-29 records Claude's inconsistency flag, and a:9e4b6896-30 / b:9e4b6896-27 record joint resolutions. Claude flagged, Ali ruled, so joint.*

**Decision.** Ali's draft rulings are assessed programmatically before anything is applied: validate the draft against the adjudication set and both passes, code-verify the risky rulings, flag cases for re-review with severity labels, and change no files. The audit's findings are then resolved individually — the byte-identical fork twins sander2798_enderstone__9d0d and sandergielisse_enderstone__9d0d must carry the same label under Ali's own compile-beats-runtime convention or an explicit written reason for divergence; frankbille_scoreboard__890ecd0bdb is re-ruled from overlapping-edit-interleaving to indeterminate as the rule-faithful call; and Ali's conscious retention of stale-expectation-of-changed-behavior for vkostyukov_la4j__d216 is recorded in the adjudication record as a ruled judgment call with its hinge acknowledged rather than reopened.

**Why.** Ali directed that the draft was exclusively for review with no changes made from it. The twins have the same 3 scored files with EnderPlayer.java byte-for-byte equal and both carry the same two used-but-unimported symbols, so differing labels are internally inconsistent with Ali's own convention. For frankbille the hybrid is real but whether it breaks hinges on the unshown pom.xml (JPA dependency dropped → compile break; retained → inert annotation), and by the Amendment-2 tree a nameable interaction with breakage unsettleable from the shown files is indeterminate. For la4j the mechanism is plausible but hinges on the unshown AbstractVectorTest hierarchy, so indeterminate is defensible and the retention stands as Ali's call with the hinge documented.

**Status.** adopted. Supersedes: *draft v1 ruling frankbille_scoreboard__890ecd0bdb => overlapping-edit-interleaving*.

**Source.** `a:9e4b6896-27`, `a:9e4b6896-29`, `a:9e4b6896-30`, `b:9e4b6896-27` · Artifacts: `reports_taxonomy/phase3/adjudication/adjudication_record.md`, `labels_final.csv`

> dont make any changed based on this draft it is exclusively
>
> — `2026-07-11_9e4b6896.txt:1011`

> You ruled the twins differently (SEC vs SPI). Under your own compile-beats-runtime convention (applied to sandergielisse), sander2798 should also be **SPI** — or the divergence needs an explicit written reason.
>
> — `2026-07-11_9e4b6896.txt:1157`

> By your Amendment-2 tree — nameable interaction, breakage unsettleable from shown files — **IND (pass b)** is the more rule-faithful call
>
> — `2026-07-11_9e4b6896.txt:1161`

### <a id="d-230"></a>D-230 — Reject a pass's ruling whose decisive evidence quote is fabricated

`2026-07-14` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** apache_opennlp__8240a2c660 is flagged for re-review with a recommendation to flip to none-identified, because pass b's decisive evidence — conflict markers in the merged result — appears nowhere in the merged files or in the model's actual input (grep = 0 hits).

**Why.** The quoted evidence does not exist in the input; the remaining support is single-file classpath RESOLVE noise under R7, leaving pass a's reading as the only one grounded in the input.

**Status.** adopted.

**Source.** `a:9e4b6896-28` · Artifacts: `THREATS_TO_VALIDITY.md §4.4.9`

> **2. `apache_opennlp__8240` — HARD (ruling rests on a fabricated quote).** Pass b's core evidence — `<<<<<<< HEAD` conflict markers "in the merged result" — **appears nowhere**: not in any merged file, not anywhere in the model's actual input (grep = 0 hits).
>
> — `2026-07-11_9e4b6896.txt:1159`

### <a id="d-231"></a>D-231 — Escalate to Ali rather than improvise: control flags, gate flags and plan ambiguity

`2026-07-15 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: Claude enacted the escalation and packaging (a:2e726dc0-10, a:06ec13eb-09, a:f0d70a59-10) while Ali set the ambiguity-check and stop-and-ask rules in the session brief (a:506d875b-01, a:68c24033-03). Both ends of the same rule, so joint.*

**Decision.** A detector firing on a control never passes silently: each such flag is packaged with full evidence (reports_detectors/eval/gd3_flag_package.md for the two GD3 gate failures — eval-control jgralab and spgroup-clean jOOQ DSL; reports_detectors/stagec_rerun/ctl_flag_package.md for the jgralab D1 and yubico D2 experimental-arm flags), Claude's reading is explicitly labelled as analysis, and the session stops for Ali's personal ruling, with both consequences spelled out — DETECTOR-FP implies a dated §12 amendment plus full reruns, INCIDENTAL-BUT-TRUE is recorded with the gate re-judged and nothing rerun. The known residual FP class (a lost non-JDK wildcard plus the other side concurrently adding usage of a same-package type) is registered in writing beforehand as an accepted limitation to be measured on the 200 eval-controls + spgroup at S-D5/GD3 with Ali adjudicating any hit. More generally, a session must read the frozen authority doc and ISSUES entry first and, on any ambiguity, contradiction or underspecification between plan, repo state and prompt, ask Ali concrete questions and wait — material resolutions becoming dated §12 amendments, trivial clarifications going to the session log and close-out — and if a verdict delta Δ cannot be derived purely from committed artifacts for some file, the session halts and asks rather than improvising a value.

**Why.** Per plan §5 any control/spgroup flag stops the session and the amendment path is Ali's call, and the program's rules say a detector firing on a control is never allowed to pass silently — Ali personally rules on each one, the machine numbers publishing either way while his ruling determines how the flags are characterised. Pre-registering the residual FP class means a hit on the eval corpora confirms a known limitation rather than surprising anyone, because that case is file-locally indistinguishable from the jnr true-positive shape. Ambiguity must never be resolved by improvising: resolutions have to be traceable in the frozen plan's amendment section, and a non-computable Δ is a genuine question, not arithmetic.

**Status.** adopted.

**Source.** `a:2e726dc0-10`, `a:06ec13eb-09`, `a:f0d70a59-10`, `a:506d875b-01`, `a:68c24033-03` · Artifacts: `merge-tool-comparison/reports_detectors/eval/gd3_flag_package.md`, `merge-tool-comparison/reports_detectors/stagec_rerun/ctl_flag_package.md`, `outputs/detector-cycle-plan.md`, `ISSUES #31`, `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`

> the program's rules say **a detector firing on a control is never allowed to pass silently — you personally rule on each one**. The package is just the evidence file for those rulings.
>
> — `2026-07-22_06ec13eb.txt:160`

> never resolve ambiguity by improvising
>
> — `2026-07-15_506d875b.txt:16`

> If Δ turns out NOT to be computable purely from committed artifacts for some file, STOP and ask Ali — that would be a genuine question, not arithmetic.
>
> — `2026-07-22_68c24033.txt:76`

> I've already registered the residual FP class in writing (lost **non-JDK** wildcard + concurrent same-package-type usage; tune saw only the JDK variant), so a hit there confirms a known limitation rather than surprising us
>
> — `2026-07-16_f0d70a59.txt:226`

### <a id="d-232"></a>D-232 — Every held-out ruling carries a written rationale; the convention is fixed in card 1

`2026-07-19 → 2026-07-20` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: a:2e726dc0-13 records Claude stating the gate definition, a:2e726dc0-14 and a:2e726dc0-15 record the convention structure and card-1 convention as agreed with Ali. Options were put and Ali agreed, so joint.*

**Decision.** Every held-out flag's ruling must carry a one-line written rationale naming the evidence that carried it, exported in the rulings CSV and committed with the rulings in S-D6. Rationales are split into a convention — written once, in the first card where it bites (card 1, apache_commons-collections), stated as a rule and cited by later cards — and per-card case facts (which symbol, which side pruned what, where the use survives) which must be written for every card; if a later card forces the convention to be revised, the earlier cards that cited it are re-touched. The card-1 convention itself is that the ruling judges the merged artifact, not the mergiraf-vs-developer delta, so a file byte-identical to the developer's resolution is noted in the rationale but does not downgrade CAUSAL, applied uniformly across all 20 units.

**Why.** Plan §5 GD4 defines the gate as adjudication with written rationale, so a ruling without reasoning does not count as adjudicated and a bare radio-button label is unfalsifiable; the citable recall number inherits its defensibility from the rationales, and rationales on edge cases document the ruling convention for future cases and reruns. Writing the convention once keeps GD4 honest without re-deriving the philosophy 20 times, while "same as before" is not adjudication — and a convention changed halfway silently forks the labels, the failure Amendment 2's rerun existed to prevent. For dev-identical files either convention was defensible, but it had to be one convention across all 20, so it was fixed in card 1 and referenced thereafter.

**Status.** adopted.

**Source.** `a:2e726dc0-13`, `a:2e726dc0-14`, `a:2e726dc0-15`

> **It's the gate definition.** Plan §5 GD4: "every held-out flag adjudicated (CAUSAL / INCIDENTAL / FP, **§4.6 style, written rationale**)"
>
> — `2026-07-16_2e726dc0.txt:506`

> These must stay **per-card** — "same as before" is not adjudication.
>
> — `2026-07-16_2e726dc0.txt:539`

> CONVENTION: dev file is byte-identical (same human mistake; feature later backed out of mainline) — ruling judges the merged artifact, so dev-identical does not downgrade.
>
> — `2026-07-16_2e726dc0.txt:581`

### <a id="d-233"></a>D-233 — GD3 control flags are ruled from their package, outside the held-out UI and convention

`2026-07-20` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The two GD3 control flags (jgralab, jOOQ) are adjudicated from gd3_flag_package.md rather than through the S-D6 adjudication UI, and are explicitly exempt from the held-out rationale convention.

**Why.** They are a different instrument — FP gates on controls, not recall — and their package already isolates the question each one turns on.

**Status.** adopted.

**Source.** `a:2e726dc0-16` · Artifacts: `merge-tool-comparison/reports_detectors/eval/gd3_flag_package.md`

> they're a different instrument (FP gates, not recall), and their package already isolates the question each one turns on.
>
> — `2026-07-16_2e726dc0.txt:545`

> so they deliberately don't use this UI or its convention.
>
> — `2026-07-16_2e726dc0.txt:574`

### <a id="d-234"></a>D-234 — Three held-out drafts corrected: two DETECTOR-FPs and one sub-flag fix

`2026-07-20 → 2026-07-22` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: joint

*Actors note: Sources disagree: a:2e726dc0-17 and a:2e726dc0-18 are recorded joint (Claude drafted, Ali ruled) while a:2e726dc0-19 is Claude's draft refinement. Under the draft-first protocol the rulings count only on Ali's acceptance, so joint.*

**Decision.** Three S-D6 held-out drafts were changed by scrutiny: (1) the single D3-widened catch, dabsquared_gitlab-plugin, is recorded DETECTOR-FP because ours extracted the class to a same-package top-level file (verified present at the merge commit) so the bare name needs no import — D3's held-out added value becomes 0/110 with the FP charged to its precision line; (2) scribble_scribble-java's RM2RenameConflict flag is ruled DETECTOR-FP because the supposedly renamed method is still declared in the merged file and its callers resolve, so the four flagged call sites are false alarms, with the cost falling on the baseline lane's precision (3/4 causal), touching no gate and not the name-binding family number; (3) steveice10_mcprotocollib stays CAUSAL at unit level with two sub-flag corrections recorded in the rationale — D1's wildcard-provenance clause is imprecise and the MetadataType/LongMetadataType sub-flag is a same-package FP — the UI regenerated with the refined draft (e62f7cc) and the extra-scrutiny chip removed.

**Why.** For dabsquared, the lane's assertion of breakage is false one level above the file it can see — a new sibling file in the same package is invisible to a file-local lane, which is the registered residual FP class documented at S-D4 and the Amendment-2 file-local ceiling; corroborated by the unit's indeterminate label and merged == developer's resolution. For scribble, RefactoringMiner recorded a partial responsibility split as a Rename Method and the RM2 call lane trusts that record without re-verifying that the old declaration vanished (unlike its var lane) — a documented name-level granularity limitation. For mcprotocollib the operative claim ("retains no import covering the name") was checked directly and holds — only the which-import-provided-it clause is wrong — and the codec break alone carries the unit, confirmed by the developer's later "Fix missing imports??" commit, while the same-package sub-flag gives the residual-FP blind spot a second held-out instance for FINDINGS.

**Status.** adopted.

**Source.** `a:2e726dc0-17`, `a:2e726dc0-18`, `a:2e726dc0-19` · Artifacts: `e62f7cc`, `merge-tool-comparison/reports_detectors/adjudication/adjudication_ui.html`

> **2 × DETECTOR-FP** — dabsquared (the D3-widened catch: ours had *extracted* the class to a same-package file, verified present at the merge commit — the file-local lane can't see it; its documented residual class)
>
> — `2026-07-16_2e726dc0.txt:570`

> the call lane doesn't re-verify that the old declaration actually vanished
>
> — `2026-07-16_2e726dc0.txt:628`

> The *operative* claim ("retains no import covering the name") was checked directly and holds; only the "which import provided it" clause is off.
>
> — `2026-07-16_2e726dc0.txt:658`

### <a id="d-235"></a>D-235 — Both control-flag pairs ruled INCIDENTAL-BUT-TRUE: gates re-judged PASS, no rerun

`2026-07-22 → 2026-07-23` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: the rulings themselves are Ali's (a:2e726dc0-11, a:06ec13eb-11) while the provenance recording and the 1:1 carry-forward are Claude's (a:06ec13eb-12, a:68c24033-17). Options were put and Ali picked, so joint.*

**Decision.** Ali ruled the two GD3 control flags (jgralab, jOOQ) incidental-but-true rather than detector FPs: the GD3 gates were re-judged PASS in the manifest, no §12 amendment or S-D5 rerun was triggered, and the record stands as zero adjudicated FPs across 363 control units. He likewise ruled both Stage-C-rerun experimental-arm control flags incidental-but-true (jgralab D1 version-skew class; yubico D2 developer-confirmed), recorded in ctl_flag_package.md's rulings section, manifest stagec_rerun.ctl_flag_rulings, ISSUES #31, FINDINGS §10 and memory, with no amendment and no rerun — the 732d8ff freeze stands. Ali's initial FP challenge and its evidence-based resolution against the four-version differential are documented in the package alongside the ruling, and the same two rulings are then applied unchanged (1:1) to S-D8's two flag-ON control blocks rather than re-adjudicated.

**Why.** For the Stage-C-rerun pair, Ali ruled after the four-version differential resolved his FP challenge: the flags are true of the scored artifacts and their presence in the control pool is an artifact of the label construct. The challenge-and-resolution provenance is kept because it shows the ruling was contested then evidence-settled, not rubber-stamped. The S-D8 blocks are exactly the same flags Ali already ruled in S-D7 and both are Mergiraf-routed in that run, so the rulings transfer 1:1. (No reason was recorded for the GD3 pair beyond the ruling itself.)

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-275](#d-275), [D-273](#d-273) — Located by content: GD3's zero-control-flag definition and the score-against-the-written-criterion rule are the gates this entry's 're-judged PASS, no rerun' outcome is meaningful against.

**Source.** `a:2e726dc0-11`, `a:06ec13eb-11`, `a:06ec13eb-12`, `a:68c24033-17` · Artifacts: `reports_detectors/manifest.json`, `merge-tool-comparison/reports_detectors/FINDINGS.md`, `ctl_flag_package.md`, `ISSUES.md #31`, `e978585`

> ok both incidental-but-true, record them
>
> — `2026-07-22_06ec13eb.txt:216`

> with your FP challenge and its resolution against the four-version differential documented in the package (that provenance is worth keeping for the thesis: the ruling was contested, then evidence-settled, not rubber-stamped).
>
> — `2026-07-22_06ec13eb.txt:228`

> which are exactly the jgralab-D1 and yubico-D2 flags Ali already ruled **incidental-but-true** in S-D7 — both Mergiraf-routed here, so the rulings transfer 1:1
>
> — `2026-07-22_68c24033.txt:285`

### <a id="d-236"></a>D-236 — Document the adjudication instrumentation and frozen-evidence ruling protocol in Ch. 5

`2026-07-22` · **proposed** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Add a Ch. 5 "Adjudication instrumentation" section describing the offline adjudication UIs, the committed ruling files and the census adjudication workflow, with a UI screenshot in the appendix and a contribution-delineation row separating the AI-built instrument from the author-made ruling.

**Why.** Capturing rulings against frozen evidence, offline and committed, is what makes "Ali-adjudicated" a citable label rather than an anecdote.

**Status.** proposed. S12 (2026-07-26): still pending — no thesis draft, Ch. 5 text or contribution-delineation table exists in the repo. The instrumentation artifacts it would describe (make_adjudication_ui.py, hit_adjudications.md, make_sd6_adjudication_ui.py) all exist.

**Cross-theme.** *depends-on* → [D-425](#d-425), [D-426](#d-426) — Located by content. The parent thesis-structure ruling (adopted) explicitly covers adjudication tooling; the Ch. 5 skeleton entry is the writing-plan home. The skeleton is itself proposed, so ratification of the parent does not promote this entry.

**Source.** `a:dc3bc182-24` · Artifacts: `make_adjudication_ui.py`, `adjudication_ui.html`, `reports_detectors/adjudication/make_sd6_adjudication_ui.py`, `hit_adjudications.md`

> rulings are captured against *frozen* evidence, offline, and committed — which is what makes "Ali-adjudicated" a citable label rather than an anecdote.
>
> — `2026-07-18_dc3bc182.txt:549`

### <a id="d-237"></a>D-237 — Rule the last open Phase-2b mapping late, disclosing the lateness as a threat

`2026-07-23` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Complete the long-pending Phase-2b 17-row category-mapping adjudication — the project's last DRAFT label — and record in the ruling that it was adjudicated 2026-07-23 against a mapping frozen 2026-07-04 by an adjudicator who had already seen subsequent program results, listing confirmation bias as a threat mitigated by per-row written rationale; if any rows flip, the 12/17 references are traced and corrected.

**Why.** Lateness does not compromise validity because the mapping was drafted and committed before the Phase-2b run and has not changed since, and the ruling is label-only with no downstream tuning path; the genuine remaining threat is confirmation bias toward the draft already seen quoted, mitigated by per-row written rationale plus an explicit disclosure line. It is also the last open ruling in the entire project and cheap.

**Status.** adopted. S12 (2026-07-26): still pending — reports_detection/phase2b/FINDINGS.md:37,80 still say the category mapping is a frozen DRAFT with Ali's adjudication pending; category_mapping.csv unchanged; no commit to phase2b/ after 2026-07-05. The 17-row ruling remains with Ali. Adopted/executed 2026-07-27 (commit 25db694): Ali ruled all 17 rows via mapping_ui.html — 17/17 confirm the frozen draft, 0 overrides (incl. VERIFY-flagged row 14 storm→#6) → category_mapping_adjudicated.csv; category_mapping.csv unchanged; FINDINGS/STATUS/CLAUDE updated; per-category table final. No rows flipped, so no 12/17 tracing was needed. Two deviations from the proposal text, disclosed in FINDINGS §Threats: the ruling date is 2026-07-27 (not 2026-07-23), and the rulings carry no per-row written rationales — each confirmation adopts the frozen draft's own per-row reasoning as its rationale.

**Source.** `a:4c7b0828-40` · Artifacts: `reports_detection/phase2b/mapping_ui.html`, `reports_detection/phase2b/FINDINGS.md`, `reports_detection/phase2b/category_mapping_adjudicated.csv`

> rule it if you want the Phase-2b table clean in the thesis (my recommendation — it's the last open ruling in the entire project and cheap)
>
> — `2026-07-06_4c7b0828.txt:2068`

> the ruling record should simply say so: *adjudicated 2026-07-23 on the mapping frozen 2026-07-04; the adjudicator had seen subsequent program results; listed as a threat, mitigated by per-row written rationale.*
>
> — `2026-07-06_4c7b0828.txt:2090`


## Gates, freezes & pre-registration

*154 primary source decisions → 47 entries; 2 not promoted (reasons in `docs/decision-record/entries/gates-freeze.json`).*

### <a id="d-238"></a>D-238 — Mergiraf may fill the structured-merge slot only on Phase 4 evidence: F1 ≥ git merge-file, zero crashes

`2026-04-21 → 2026-04-22` · **abandoned** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

*Actors note: One source attributes the promotion gate to Claude and the other records actors as unclear; both are plan documents, so the record does not establish who chose the criterion.*

**Decision.** Gate Mergiraf's promotion into semantic_merge_driver's vacant structured-merge slot on Phase 4 empirical evidence: F1 at least that of `git merge-file` on the Schesch subset with zero crashes. Phase 6-validate is triggered once Phase 4 lands and checks exactly this; if satisfied, the default-flip is supported and STATUS.md records the outcome with no code change, and if not, a follow-up plan is filed (switch the default back to `git`, or pick another second backend such as Spork via S2) with STATUS.md flagging the open issue.

**Why.** Phase 6's role inverts versus the original pre-MVP plan — validation rather than gate — because under the MVP-first ordering the mechanism ships first, so the check retroactively confirms or refutes the MVP-time choice of Mergiraf as second backend.

**Status.** abandoned. S12 (2026-07-26): the named procedure never ran — no Phase-4/Phase-6-validate execution record exists in docs/plans/mergiraf-integration.md, STATUS.md or the reports. The default shipped pre-evidence with a commit caveat (3fef834) and was later sustained by different instruments (the six-tool canonical table and P2), but the F1-vs-git zero-crash check as specified was dropped without a ruling.

**Cross-theme.** *depends-on* → [D-043](#d-043), [D-039](#d-039) — The linked entries settle what the flag asked: the default shipped before empirical validation (MVP-first), matching this entry's own framing of Phase 6 as retroactive validation rather than a gate. Whether Phase-6-validate ever ran under that name is not in the record; the entry stays proposed and its status_note already points at STATUS.md.

**Source.** `preA:pre-mergiraf-integration-23`, `preA:pre-tool-evaluation-findings-02` · Artifacts: `docs/plans/mergiraf-integration.md`, `STATUS.md`, `semantic_merge_driver/initial architecture.md`

> Confirm Mergiraf F1 ≥ `git merge-file`'s on the Schesch subset, with zero crashes, against Phase 4 results.
>
> — `2026-04-21_pre-mergiraf-integration.txt:245`

> retroactively confirm — or refute — the MVP-time decision in Phase 6-lite to use Mergiraf as the second backend. Role inverts vs. the original (pre-MVP) Phase 6: validation rather than gate.
>
> — `2026-04-21_pre-mergiraf-integration.txt:242`

> Promote Mergiraf to `semantic_merge_driver` | Mergiraf plan Phase 4 evidence: F1 ≥ git-merge-file, zero crashes
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:290`

### <a id="d-239"></a>D-239 — Pin the formatter version used by the comparator's Docker layer

`2026-04-21` · **adopted** · `[recon]` · corroboration: single-pass · confidence: medium · actors: unclear

**Decision.** The google-java-format (or spotless) version used in the comparator's Docker layer is pinned.

**Why.** Comparator output changes when the formatter changes.

**Status.** adopted. S12 (2026-07-26): pinned — docker/google-java-format/Dockerfile:19 'ARG GJF_VERSION=1.22.0', image tagged merge-tools/google-java-format:1.22.0, jar fetched by that exact version.

**Source.** `preA:pre-mergiraf-integration-13` · Artifacts: `merge-tool-comparison/docker/google-java-format/Dockerfile`

> pin the formatter version, since comparator output changes when the formatter changes
>
> — `2026-04-21_pre-mergiraf-integration.txt:138`

### <a id="d-240"></a>D-240 — Both integration plans gain a significance gate on F1 criteria and a 2× timebox escape rule

`2026-04-22` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** Edit §2 Constraints of both integration plans so that headline numbers must carry a Wilson 95% confidence interval, "F1 ≥ X" acceptance criteria carry a statistical-significance gate, and any phase overrunning 2× its estimate stops and writes a revisit note to STATUS.md before continuing. Landed as commit 77d988a together with the other plan-gap fixes (separate base→ours/base→theirs RM2 runs, R3 merged-file-only reality, a separate implementation phase for ISSUES #2).

**Why.** The pre-execution review found two concrete gaps: no statistical-significance gate existed on the F1 acceptance criteria, and nothing in the plans prevented phases ballooning.

**Status.** adopted.

**Cross-theme.** *duplicates* → [D-446](#d-446) — Same 2x escape rule. Kept separate rather than merged (merging would move uids across slice boundaries): this entry owns the integration-plan gates, other/ owns the plan-era origin statement. Mirror: other:8.

**Source.** `preA:pre-commits-09`, `preA:pre-execution-sequence-03`, `preB:pre-execution-sequence-16` · Artifacts: `77d988a`, `docs/plans/mergiraf-integration.md`, `docs/plans/rm2-integration.md`, `STATUS.md`

> 4. No statistical-significance gate on "F1 ≥ X" acceptance criteria.
>
> — `2026-04-22_pre-execution-sequence.txt:19`

> No timebox escape rule; nothing prevented phases ballooning.
>
> — `2026-04-22_pre-execution-sequence.txt:20`

> Both §2 Constraints: Wilson 95% CI requirement on headline numbers,
>
> — `2026-04-15_pre-commits.txt:116`

### <a id="d-241"></a>D-241 — Each execution stage is one commit, gated on the previous, with a mandatory stop and a replan gate at ε

`2026-04-22` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

**Decision.** Structure the α/β/β.1/γ/δ/ε rollout so every stage is a single commit gated on the previous stage, with a mandatory stop-and-re-evaluate between stages and rollback by `git revert` or branch-drop of that one commit; constrain α–δ so none of them touches merge-tool-comparison runtime code or published report numbers; and insert a replan gate at ε requiring both execution plans to be refreshed with stage γ and δ findings before execution proceeds.

**Why.** Stated in the rollback section: because each stage is exactly one commit, rollback is a single revert or branch drop, and because none of α–δ touches merge-tool-comparison runtime code or published numbers, no stage can move a published number by accident.

**Status.** adopted. S12 (2026-07-26): executed as specified — docs/plans/execution-sequence.md tracks every stage done with its commit (α 77d988a, β 044051f, β.1, γ 2026-05-14, δ R0 1f76a00+5e687ce) and header 'Status: active — α, β, β.1, γ, δ done; ε MVP track complete', including the ε replan gate outcomes recorded as dated items.

**Source.** `preA:pre-execution-sequence-02`, `preB:pre-execution-sequence-28`, `preB:pre-execution-sequence-23` · Artifacts: `docs/plans/execution-sequence.md §2`, `docs/plans/execution-sequence.md §4`

> Each stage is one commit, gated on the previous. Stop between stages and re-evaluate.
>
> — `2026-04-22_pre-execution-sequence.txt:34`

> None of α–δ modifies `merge-tool-comparison/` runtime code or published report numbers.
>
> — `2026-04-22_pre-execution-sequence.txt:139`

> After stages α–δ, refresh both execution plans with stage γ + δ findings.
>
> — `2026-04-22_pre-execution-sequence.txt:93`

### <a id="d-242"></a>D-242 — R2's per-cluster answer is publishable either way and does not gate the dispatch mechanism

`2026-04-22 → 2026-05-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: Two sources attribute the position to Ali (the scope-tier options ruling and the transcript-era evidence-first statement); the plan-text source records actors as unclear. Attributed to Ali on the strength of the transcript-era source rather than by majority.*

**Decision.** Commit in advance to reporting R2's answer to "does refactoring cluster predict tool performance on this dataset?" whichever way it comes out: a yes justifies adding the W5/S2 elifs in a follow-up cycle, a no means merge-layer dispatch is not load-bearing for this dataset and W5/S2 stay empirical-only data points while the R4b mechanism ships as honest plumbing. The per-cluster signal itself is labelled suggestive only (per-cluster n 4–18, sub-CI) and explicitly does not gate R4b. No tuning toward a desired answer is permitted.

**Why.** Per-cluster n of 4–18 is below confidence-interval sufficiency, so the signal cannot carry the routing claim statistically; and because the question is publishable either way, Tier C can be the strongest decision-grade output without committing to a specific routing claim.

**Status.** adopted.

**Source.** `preA:pre-execution-sequence-19`, `preA:pre-scope-tier-options-10`, `a:20b53f98-03` · Artifacts: `reports/results.csv`, `ISSUES.md #3`, `src/evaluation/categorizer.py`

> Signal is **suggestive only** (per-cluster n 4–18, sub-CI)
>
> — `2026-04-22_pre-execution-sequence.txt:106`

> Never tune toward a desired answer.
>
> — `2026-05-18_20b53f98.txt:79`

> **What R2 produces:** a yes/no answer to *"does refactoring cluster predict tool performance on this dataset?"* Either outcome is publishable:
>
> — `2026-05-05_pre-scope-tier-options.txt:98`

### <a id="d-243"></a>D-243 — Evidence-before-integration binds per-cluster routing claims, not the dispatch mechanism or the default

`2026-04-22 → 2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** Scope the inherited "evidence before integration" constraint to per-cluster routing claims (W5's MIGRATE_DECL→Weave, S2's INTRA_BODY+Java→Spork), each of which carries its own evidence gate. Shipping the classifier and auto-mode skeleton (R4a+R4b) is exempt, and choosing Mergiraf as the default/fallback cluster target at MVP time is likewise accepted without empirical evidence.

**Why.** The dispatch mechanism is honest plumbing — it makes no routing claim — and Mergiraf is the fallback for unmatched clusters rather than a routing claim; a routing elif does encode a specific claim, and adding one without evidence is "adding a tool because it seems nice", the move the thesis argues against.

**Status.** adopted. S12 (2026-07-26): the scoping was honoured end to end — R4a+R4b shipped ungated (M6-lite 3fef834, default accepted pre-evidence per its own commit caveat), while the per-cluster claims got their evidence gates: the S2 arm fell to the CI-grade run (ISSUES #27) and W5 to the W3 gate run (ISSUES #28, reports_migrate_decl/), exactly the split this entry prescribed.

**Source.** `preA:pre-rm2-integration-10`, `preA:pre-weave-integration-19` · Artifacts: `docs/plans/mergiraf-integration.md Appendix A`

> The dispatch *mechanism* itself (R4a + R4b shipping the classifier and auto-mode skeleton) is honest plumbing; it doesn't make a routing claim and so doesn't require routing evidence.
>
> — `2026-04-22_pre-rm2-integration.txt:84`

> is acceptable because Mergiraf is the *fallback* for unmatched clusters, not a routing claim
>
> — `2026-04-25_pre-weave-integration.txt:266`

### <a id="d-244"></a>D-244 — W5 promotion originally gated on five conditions including a MIGRATE_DECL-specific W3 win

`2026-04-25` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** W5 (promoting Weave into semantic_merge_driver) may only proceed when all five triggers hold: W3 shows Weave strictly outperforming Mergiraf on the MIGRATE_DECL cluster with non-overlapping 95% CIs (or handling extraction cases Mergiraf crashes on), RM2 R4a has landed, mergiraf Phase 6-lite has landed, the rm2 R4b dispatch skeleton has landed, and W2/W3 show zero crashes. Without all five, Weave remains an empirical data point only.

**Why.** The elif arm encodes a specific routing claim ("MIGRATE_DECL cluster → Weave") which must be empirically justified; adding it without evidence is "adding a tool because it seems nice", the move the thesis argues against.

**Status.** superseded. Superseded by [D-245](#d-245) — Routing elifs ship as Phase-1 mechanism; the S3/W3 evidence gates become Phase-2 validation.

**Source.** `preA:pre-weave-integration-07` · Artifacts: `docs/plans/mergiraf-integration.md`, `docs/plans/rm2-integration.md`

> **This is the load-bearing evidence gate for W5**
>
> — `2026-04-25_pre-weave-integration.txt:196`

> Without all five, Weave stays an empirical data point only.
>
> — `2026-04-25_pre-weave-integration.txt:202`

### <a id="d-245"></a>D-245 — Routing elifs ship as Phase-1 mechanism; the S3/W3 evidence gates become Phase-2 validation

`2026-04-25 → 2026-05-19` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** Split routing work in two phases: the S2 (INTRA_BODY+Java) and W5 (MIGRATE_DECL) auto-mode elifs ship as a Phase-1 mechanism deliverable, wired and synthetic-verified end-to-end, while W0–W4 and S3/S4 become Phase-2 soundness validation (real data, Wilson CIs) and are no longer preconditions for the mechanism. R4b's trigger likewise becomes only that R4a and M6-lite have landed, not R2 evidence plus W5/S2. Where the phase bodies of spork-driver-integration.md, weave-integration.md and scope-tier-options.md read as hard-coupling S2↔S3 or W5↔W3, the rm2-integration.md §1.2 marked decision governs.

**Why.** The evidence gates are soundness validation and not a precondition for the mechanism; splitting R4a from R4b across the evidence gate had created a long dead-code window for R4a and forced cross-plan scheduling pressure, and R4b ships only the mechanism so per-cluster routing evidence belongs in W5/S2.

**Status.** adopted. Supersedes: [D-244](#d-244) — W5 promotion originally gated on five conditions including a MIGRATE_DECL-specific W3 win; *original rm2 draft in which R4b waited on R2 evidence plus W5/S2*; *spork-driver-integration.md §S3 'before flipping the router default' coupling text*.

**Cross-theme.** *depends-on* → [D-041](#d-041), [D-042](#d-042) — The flag's criterion — a transcript-era source showing the elifs shipped — is met in backends-routing: [D-041](#d-041) (adopted) records the same two-phase decision, and the elifs' later life is transcript-era fact ([D-069](#d-069) 2026-05-27, [D-072](#d-072) 2026-07-02 'rather than deleting the specialist arms'). Status moved proposed->adopted exactly as the flag prescribes; status_note cleared.

**Source.** `preA:pre-weave-integration-06`, `preA:pre-rm2-integration-09`, `preA:pre-spork-driver-integration-03`, `preA:pre-rm2-integration-25` · Artifacts: `docs/plans/rm2-integration.md §1.2`, `docs/plans/spork-driver-integration.md`, `docs/plans/weave-integration.md`, `AutoBackend._route()`, `memory routing-two-phase`

> The S2/W5 routing **elifs are wired and synthetic-verified end-to-end** as a *Phase-1 mechanism* deliverable.
>
> — `2026-04-22_pre-rm2-integration.txt:59`

> This is **decoupled** from the S3/W3 evidence gates: those are *Phase-2 soundness validation* (real data + Wilson CIs) and are **not** a precondition for the mechanism.
>
> — `2026-04-22_pre-rm2-integration.txt:59`

> Splitting them across the evidence gate (the original draft had R4b waiting on R2 + W5/S2) created a long dead-code window for R4a and forced cross-plan scheduling pressure.
>
> — `2026-04-22_pre-rm2-integration.txt:433`

### <a id="d-246"></a>D-246 — S3 and W3 are hard-gated on ISSUES #2, with the failure branch pre-registered

`2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

*Actors note: The S3 gate is attributed to Ali in one source; the sibling revert rule and the W3 gate are recorded as unclear. Left unclear because all three are plan text and the record does not show the choice being put and taken.*

**Decision.** S3 may not run until merge-tool-comparison/ISSUES.md #2 moves from `decided — see plan` to `resolved`, and no granularity-axis claims are published until then (with the same caveat attached to Weave's numbers if its FP count mirrors Spork/Mastery). The outcome branch is pre-registered: if S3 shows Spork's F1 is not strictly higher than Mergiraf's with non-overlapping CIs, the S2 router change is reverted — Mergiraf keeps the cluster, the plan lands only S1, and Spork stays available via explicit SEMANTIC_MERGE_BACKEND=spork; if Spork wins, `auto` is flipped to include the Spork dispatch branch.

**Why.** Spork's empirical numbers are currently distrusted — the suspected normalize_content() bug inflates its FP rate — so promoting on them would be promoting on numbers known to be wrong and F1 differences would be noise; the same FP inflation would muddy W2/W3, so the ground-truth methodology must be settled first.

**Status.** adopted. S12 (2026-07-26): the gate was honoured precisely — ISSUES.md #2 shows the pause trigger firing and #2 held at 'decided' (:84, :117) until the Tier-E floor was hit exactly and #2 moved to resolved (2026-05-15, :132); the granularity evidence runs came after (Spork CI-grade 2026-05-25/27, W3 2026-06-01), and the pre-registered failure branch executed as the router flip when both arms were refuted.

**Source.** `preA:pre-spork-driver-integration-07`, `preA:pre-spork-driver-integration-13`, `preA:pre-weave-integration-18` · Artifacts: `merge-tool-comparison/ISSUES.md #2`, `docs/plans/spork-driver-integration.md`, `docs/plans/weave-integration.md`

> **Why gate on ISSUES.md #2?** Because Spork's empirical numbers are currently distrusted
>
> — `2026-04-25_pre-spork-driver-integration.txt:230`

> - If Spork's F1 is not strictly higher than Mergiraf's with non-overlapping CIs, **revert** the S2 router change; Mergiraf owns the cluster and this plan lands only S1
>
> — `2026-04-25_pre-spork-driver-integration.txt:173`

> W3 is gated on that having landed; don't publish granularity-axis claims until ISSUES.md #2 is `resolved`.
>
> — `2026-04-25_pre-weave-integration.txt:240`

### <a id="d-247"></a>D-247 — Pre-register the comparator's recovery floor from Wilson bounds, with per-phase floors and an escalation rule

`2026-05-14` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: The escalation-threshold source attributes the rule to Claude; the floor and ladder sources record actors as unclear, and the later threats-review source is unclear. Left unclear because the plan-era record does not say who set the numbers.*

**Decision.** Pre-register numeric acceptance criteria for the FP-diagnostic ladder before running it: Tier C's point estimate is Spork TP 37 / FP 6 (X≈35 of the 39 still-differ residuals), its acceptance floor is TP ≥ 32 / FP ≤ 11 (X ≥ 30), and ISSUES.md #2 may move decided→resolved only on hitting that floor; Mastery, git-merge-file and JDime rows are expected unchanged. Implement as five small commits (3b.0–3b.5), each one reviewable commit leaving the tree working, with cumulative per-phase Spork TP floors of ≥7 / ≥14 / ≥22 / ≥32 and STATUS.md/ISSUES.md touched only after the final phase. Earlier in the ladder, 3j manual labelling runs on the residual after 3e and escalation to 3b or 3a is triggered if more than ~10% of FPs remain unexplained.

**Why.** The point estimate comes from §9's 15/15 stratified AST-equivalence labelling (~90% recovery × 39 = 35) and the floor from the Wilson 95% lower bound (~80% × 39 ≈ 30); the per-phase floors are deliberately conservative so that a miss is a real progress signal rather than a point-estimate shortfall. The later threats review records the same floor as the sole mitigation for the normalizer having been tuned iteratively against the very Spork residuals it scores, with no held-out validation.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-384](#d-384) — The iteratively-tuned-no-held-out-validation (overfitting) finding has no dedicated entry anywhere; its home is the THREATS document decision, linked as nearest owner.

**Source.** `preA:pre-commits-66`, `preA:pre-comparator-3b-ast-normalize-02`, `preB:pre-comparator-3b-ast-normalize-03`, `preA:pre-comparator-3b-ast-normalize-12`, `preA:pre-stage-gamma-fp-diagnostic-08`, `a:dc3bc182-sub-sub-agent-a74c7a-05` · Artifacts: `docs/plans/comparator-3b-ast-normalize.md`, `merge-tool-comparison/ISSUES.md #2`, `6cfcdfc`, `THREATS_TO_VALIDITY.md`

> Point estimate: §9's 15/15 → ~90% recovery × 39 = 35. Floor: Wilson 95% lower bound (~80%) × 39 ≈ 30.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:60`

> Per-phase floors below are conservative — a real progress signal if missed, not the point-estimate from §3.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:203`

> A pre-registered numeric gate governs the comparator: Spork must recover X_total ≥ 30 / FP ≤ 11 over baseline.
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:25`

### <a id="d-248"></a>D-248 — Every comparator tier carries an undershoot pause trigger and a 2× timebox escape budget

`2026-05-14 → 2026-05-16` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

*Actors note: The Tier D trigger is attributed to Claude; the Tier C and Tier E triggers are recorded as unclear. Left unclear because the plan-era record does not establish authorship of the thresholds.*

**Decision.** Each tier plan pre-registers stop conditions as well as targets. Tier C: 2.5–3 days with a 2× (6 day) escape, stopping on parse failures over 10% of the n=50 scenarios or any single phase exceeding 1.5d. Tier D: ~4 days with a 2× (8 day) escape, pausing to re-examine the prototype assumptions if any phase delivers 0 recovery or commits more than 1 below its prototype-attributed estimate. Tier E: 4–5 days with a 2× (8–10 day) escape, pausing if any phase commits 2 or more below its prototype-attributed cumulative estimate.

**Why.** Prototype recovery measurements are treated as upper bounds, because real recovery may be lower where the prototype's parent-context checks have edge cases the committed version does not share; and each phase is small and independently shippable, so failing fast on tree-sitter unfamiliarity is acceptable.

**Status.** adopted.

**Cross-theme.** *duplicated by* ← [D-446](#d-446) (see the reconciliation note there)

**Source.** `preA:pre-comparator-3b-ast-normalize-20`, `preA:pre-comparator-3d-extended-ast-transforms-17`, `preA:pre-comparator-3e-tier-e-transforms-18` · Artifacts: `docs/plans/comparator-3b-ast-normalize.md`, `docs/plans/comparator-3d-extended-ast-transforms.md`, `docs/plans/comparator-3e-tier-e-transforms.md §3`, `STATUS.md`

> **Undershoot trigger:** if any phase delivers 0 recovery, pause and re-examine the prototype assumptions.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:83`

> **Undershoot trigger:** if any phase commits 2+ below its prototype-attributed estimate (cumulative), pause and re-examine.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:100`

> Timebox-escape budget per [`mergiraf-integration.md §2`](mergiraf-integration.md): 2× = 6 days. Triggers: parse failures on >10% of n=50 scenarios; any one phase exceeding 1.5d.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:286`

### <a id="d-249"></a>D-249 — Honour the pre-registered pause trigger: finish 3b.5 in stop-and-document mode

`2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: joint

*Actors note: One source records the stop-and-document mode as taken per the plan trigger plus explicit user direction; another attributes it to Claude and a third records unclear. Recorded as joint because the trigger was pre-registered and the mode was confirmed by Ali's direction.*

**Decision.** With Tier C recovering X=5 against a floor of X≥30 and a pause threshold of X<25, declare the plan §3 pause trigger fired: complete phase 3b.5 as documentation only in stop-and-document mode, regenerate reports, append the empirical outcome to the docs, and keep ISSUES.md #2 at `decided` rather than moving it to `resolved`. Follow-up options (Tier D, 3a) are recorded and deferred.

**Why.** Recovery of ~12% of the still-differ residuals is far below the §3 point estimate of ~90% and below the X<25 pause threshold, and the plan's §3 pause trigger, §6 phase 3b.4 acceptance and §10 acceptance criteria all require the status to stay `decided`. The §9 conclusion that residuals are AST-equivalent survives, but the §3 mapping from "AST-equivalent" to "recoverable by these 5 transforms" broke — Tier C is a strict subset.

**Status.** adopted.

**Source.** `preA:pre-commits-72`, `preA:pre-comparator-3b-ast-normalize-22`, `preA:pre-stage-gamma-fp-diagnostic-21` · Artifacts: `b22cb54`, `merge-tool-comparison/ISSUES.md #2`, `STATUS.md`, `docs/plans/comparator-3b-ast-normalize.md §6`

> Phase 3b.5 doc-finalisation completed in stop-and-document mode (per plan §3 pause trigger + user direction) rather than ISSUES.md-#2-resolved mode.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:477`

> X=5 vs the plan §3 floor X≥30 and pause threshold X<25 (~65% recovery). **Plan §3 pause trigger fires.** Per plan §6 Phase 3b.4 + §10 acceptance, ISSUES.md #2 stays `decided`, not `resolved`.
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:244`

### <a id="d-250"></a>D-250 — ISSUES #2 is held at `decided` every time a tier misses the pre-registered floor

`2026-05-14 → 2026-05-15` · **superseded** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

*Actors note: Two of the six sources attribute the holding decision to Claude; the remaining four record actors as unclear. Left unclear because most instances are commit-log and plan text that do not name a decider.*

**Decision.** Refuse to promote ISSUES.md #2 from `decided` to `resolved` whenever the pre-registered floor is not hit, and keep the headline FP rates labelled `presentation-suspect` while publishing the new empirical breakdown alongside them. Applied after 3e (Spork TP 1→2 / FP 42→41, Mastery 0 rows: acceptance criterion not met, status recorded as `decided — 3e implemented, partial`), after M3.5, and after Tier D (cumulative X_total = 12 against the 3b §3 floor of X ≥ 30), with the Tier D plan stating up front that Tier D is incremental and not a closure and that closing requires Tier E or 3a.

**Why.** Recovery is well below the stage-γ hypothesis and the §3.5 contingency hedge fired: the dominant residuals (else-if restructuring, comment placement, redundant cast parens) are patterns gjf does not normalise, Mastery's zero recovery matches the intrinsic-content-loss prediction, and the headline-number credibility problem is therefore not actually fixed. Even the expanded Tier D scope falls short of TP ≥ 32, and the plan is to be honest about that by design.

**Status.** superseded. Superseded by [D-253](#d-253) — Tier E hits the floor exactly: ISSUES #2 resolved and post-3e results.csv frozen as the final state.

**Cross-theme.** *depends-on* → [D-145](#d-145), [D-155](#d-155), [D-160](#d-160) — The normalizer-tier decisions these gates scored are owned by evaluation-oracles.

**Cross-theme.** *depended on by* ← [D-020](#d-020) (see the reconciliation note there)

**Source.** `preA:pre-commits-61`, `preB:pre-mergiraf-integration-15`, `preA:pre-stage-gamma-fp-diagnostic-14`, `preA:pre-commits-74`, `preA:pre-commits-82`, `preA:pre-comparator-3d-extended-ast-transforms-04` · Artifacts: `merge-tool-comparison/ISSUES.md #2`, `STATUS.md`, `60c5e2b`, `3dfecf0`, `8cd83c1`, `docs/plans/stage-gamma-fp-diagnostic.md`

> ISSUES.md #2 stays at `decided — 3e implemented, partial`, NOT moved to
>
> — `2026-04-15_pre-commits.txt:1199`

> Acceptance criteria — Spork FP rate drops sharply — **not met**; the §3.5 contingency hedge has fired. **ISSUES.md #2 stays at `decided`, not `resolved`.**
>
> — `2026-04-21_pre-mergiraf-integration.txt:170`

> this is BY DESIGN — Tier D is incremental, not a closure. Per §3 framing: ISSUES.md #2 STAYS `decided`. The plan is honest about this.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:330`

### <a id="d-251"></a>D-251 — Phase 3d.3 is allowed a zero per-phase recovery floor because it only pays off paired with D.2

`2026-05-15` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: claude

**Decision.** Documented exception to the per-phase undershoot trigger: phase 3d.3 may ship with 0 additional measured recovery on its own, its acceptance being instead that D.2 + D.3 combined recover at least +1 cumulative over D.1, plus a cast-only fixture test.

**Why.** Prototype measurement shows D.2 alone and D.3 alone each recover 0 of the cast-paren scenarios; those scenarios close only when both are active, because D.2 strips the inner value paren and D.3 then strips the outer paren-around-cast.

**Status.** adopted.

**Source.** `preA:pre-comparator-3d-extended-ast-transforms-15` · Artifacts: `docs/plans/comparator-3d-extended-ast-transforms.md`

> Per-phase floor: 0 (acceptable when paired with D.2).
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:170`

> D.3 must land alongside D.2 for measurable recovery.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:169`

### <a id="d-252"></a>D-252 — Tiers D and E are judged against their own lower floors, not the original X ≥ 30

`2026-05-15 → 2026-05-16` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

*Actors note: The Tier D floor and its acceptance are attributed to Claude; the Tier E floor source records actors as unclear. Left unclear for the merged entry because the Tier E numbers, which set the closure bar, have no recorded decider.*

**Decision.** Give each later tier its own acceptance criteria and judge it against them: Tier D passes at Spork TP ≥ 10 / FP ≤ 33 (X_total ≥ 8, at least +3 over Tier C) with TP ≥ 14 / FP ≤ 29 as a prototype-matching stretch, and is accepted on that basis even though cumulative X = 12 does not reach the original 3b §3 floor; Tier E's floor is Spork TP ≥ 30 / FP ≤ 13 (X_total ≥ 28) with TP ≥ 32 / FP ≤ 11 as the stretch that would hit the 3b §3 floor and let ISSUES #2 move decided→resolved. Mastery, JDime and git-merge-file rows are expected unchanged throughout.

**Why.** The Tier D bar is deliberately modest — "sets a modest but real bar" — with the stretch tied to all six phases landing cleanly with no test regressions; Tier E's floor is a modest pull-back from the prototype's measured 32 in case some transforms under-recover once integrated. The comparator-gap framing remains intact even though full closure is reassigned to Tier E or 3a.

**Status.** adopted.

**Source.** `preA:pre-comparator-3d-extended-ast-transforms-03`, `preA:pre-stage-gamma-fp-diagnostic-27`, `preA:pre-comparator-3e-tier-e-transforms-17` · Artifacts: `reports/results.csv`, `merge-tool-comparison/ISSUES.md #2`

> **Floor:** Tier D acceptance is **TP ≥ 10 / FP ≤ 33** (X_total ≥ 8 — at least +3 over Tier C). Sets a modest but real bar.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:70`

> Tier D HITS its own (lower) acceptance floor (X_d ≥ 3) and stretch (X_d = 7).
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:319`

> **Floor:** Tier E acceptance is **Spork TP ≥ 30 / FP ≤ 13** (X_total ≥ 28). Modest pull-back from prototype's 32 in case some transforms under-recover when integrated.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:89`

### <a id="d-253"></a>D-253 — Tier E hits the floor exactly: ISSUES #2 resolved and post-3e results.csv frozen as the final state

`2026-05-16` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Land Tier E (3e.0 D.1 identity-bug fix plus 3e.1–3e.10 transforms), regenerate reports at Spork TP 32 / FP 11 (X_total = 30 — the 3b §3 floor hit exactly) and flip ISSUES.md #2 from `decided` to `resolved`. The post-3e reports/results.csv (Spork 32/50, F1 0.84; git-merge-file 39/50; Mastery 12/50) is committed as the final evaluation state for the thesis, all Tier E code stays landed, and no further tiers are pursued.

**Why.** The pre-registered 3b plan §3 floor of X ≥ 30 is hit exactly; at that point the comparator-gap framing is treated as fully empirically validated and the remaining work (Tier F non-trivial AST rewriting, or 3a test-suite ground truth) is declared out of scope.

**Status.** adopted. Supersedes: [D-250](#d-250) — ISSUES #2 is held at `decided` every time a tier misses the pre-registered floor.

**Cross-theme.** *depended on by* ← [D-020](#d-020) (see the reconciliation note there)

**Source.** `preA:pre-commits-83`, `preA:pre-comparator-3e-tier-e-transforms-23` · Artifacts: `4db9329`, `merge-tool-comparison/ISSUES.md #2`, `ast_normalize.py`, `reports/results.csv`, `reports/results.json`, `reports/results.tex`

> (Spork TP 32 / FP 11; X_total = 30 — 3b plan §3 floor hit exactly).
>
> — `2026-04-15_pre-commits.txt:1677`

> `reports/results.csv` post-3e Tier E committed as the **final** evaluation state for the thesis.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:407`

> require either Tier F (non-trivial AST rewriting) or 3a (test-suite ground truth). Neither is in scope.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:408`

### <a id="d-254"></a>D-254 — Paren-strip rules carry a safe-parents whitelist whose semantics later tiers may widen but not change

`2026-05-16` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** Every paren-strip rule must carry an explicit safe-parents whitelist; the whitelist may be widened in future tiers, but transform semantics for already-listed contexts must not change. Tier E edits must additionally be well-formed, non-overlapping byte-range replacements that keep the post-edit text parseable, and must not touch the atomic literal handling in D.6's `_emit_leaves`.

**Why.** Framed as the key invariants that keep token-fold compatibility and avoid overlapping edits or invalid Java — the same conservative pattern as the 11 shipped Tier C+D transforms, which produced zero semantic-change bugs.

**Status.** adopted. S12 (2026-07-26): the invariant is in the code — ast_normalize.py carries SAFE_BINARY_PAREN_PARENTS (:83) and UNARY_SAFE_PARENTS (:125) as explicit whitelists guarding every paren-strip site (:288, :304); no later tier ran, so no listed context's semantics were ever changed.

**Source.** `preA:pre-comparator-3e-tier-e-transforms-20` · Artifacts: `docs/plans/comparator-3e-tier-e-transforms.md §6`

> **Conservative parent-context checks.** Every paren-strip rule has an explicit safe-parents whitelist. The whitelist is open to expansion in future tiers without changing transform semantics for already-listed contexts.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:259`

> None of them introduces overlapping edits or invalid Java.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:262`

### <a id="d-255"></a>D-255 — categorizer.cluster_of is parity-locked to the runtime classifier, with a test that fails on drift

`2026-05-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Maintain merge-tool-comparison's `categorizer.cluster_of` as a parity-locked copy of `RefactoringClusterClassifier.cluster(base, ours, theirs)`, with `test_taxonomy_parity` failing on drift.

**Why.** So that a "tool X wins in cluster C" result computed offline is directly actionable by the runtime router, which can compute C from the same inputs.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-095](#d-095) — other_uid a:20b53f98-19 landed there: the pytest.skip softening narrows this entry without changing it. Linked, no status change.

**Cross-theme.** *depended on by* ← [D-354](#d-354) (see the reconciliation note there)

**Source.** `a:dc624d63-03` · Artifacts: `merge-tool-comparison/tests/test_categorizer.py`, `semantic_merge_driver/core/refactoring_classifier.py`

> `categorizer.cluster_of` is a parity-locked copy of that exact function (`test_taxonomy_parity` fails on drift).
>
> — `2026-05-18_dc624d63.txt:27`

### <a id="d-256"></a>D-256 — Record the freeze commit before the run, then do not patch the instrument during it

`2026-06-11 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: The freeze step was mandated in Ali's S-D5 brief; the enforcement decisions (not patching mid-run, which commit to record) are Claude's, and two sources record actors as unclear. Recorded as joint.*

**Decision.** Every evaluation is preceded by committing and recording the instrument's freeze: Stage B's changes are committed before Stage C (843e5f5) because the dirty tree makes the harness cache mis-report v1's commit 2eed882 and the G2 freeze depends on a real commit; the detector suite commit is recorded in reports_detectors/manifest.json as detector_suite_commit before any evaluation runs (freeze commit 21dcda1 naming 732d8ff, the last commit touching the driver, rather than the artifacts-only 9580e1f), after which any detector change requires a dated §12 amendment plus a full rerun of S-D5; and all three detectors were built and frozen at 732d8ff before the two-arm held-out evaluation. Defects found mid-run are not patched: the var-lane declaration-guard defect identified during Stage C is left in place, the frozen run finishes and is reported as-is, the control flags are adjudicated DETECTOR-FP, and the fix goes into a separately-labelled post-fix run.

**Why.** The G2 freeze and the harness's cache keys both depend on the commit, so an uncommitted tree mis-attributes the run. And the plan's G2 rule applies to mid-run discoveries — finish the frozen run, report it as-is, then a separately-labeled post-fix run — because "patching now would make the Stage-C numbers uncitable".

**Status.** adopted.

**Source.** `a:bfc672b4-17`, `a:bfc672b4-28`, `a:12c77ea5-09`, `a:2e726dc0-01`, `a:82dd479f-18`, `a:dc3bc182-sub-sub-agent-a495a0-13` · Artifacts: `843e5f5`, `21dcda1`, `732d8ff`, `reports_detectors/manifest.json`, `semantic_merge_driver/strategies/rm2_strategies/rename_conflict.py`, `merge-tool-comparison/reports_detection/full/FINDINGS.md`

> the working tree is uncommitted, so the harness cache still keys on `2eed882` (v1's commit). For the G2 freeze discipline, v2 should get its own commit before Stage C
>
> — `2026-06-11_bfc672b4.txt:265`

> G2 rule from the plan applies: fix discovered mid-C → **finish the frozen run, report it as-is, then a separately-labeled post-fix run**. Patching now would make the Stage-C numbers uncitable.
>
> — `2026-06-11_bfc672b4.txt:570`

> all three detectors built and **frozen 2026-07-17 at `732d8ff`**
>
> — `2026-07-18_dc3bc182_sub-agent-a495a0.txt:68`

### <a id="d-257"></a>D-257 — Stage B is the one sanctioned exception to the no-driver-changes rule, timeboxed 3–5 days

`2026-06-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Detector changes under semantic_merge_driver/strategies/ are permitted for Stage B as the single sanctioned exception to the standing no-driver-changes rule, timeboxed to 3–5 days and scoped by the adjudicated shortlist.

**Why.** Stated as sanctioned by the plan: the exception is bounded because it is scoped by the adjudicated shortlist and timeboxed.

**Status.** adopted.

**Source.** `a:bfc672b4-08` · Artifacts: `semantic_merge_driver/strategies/`

> Next cycle is Stage B (detector changes in `semantic_merge_driver/strategies/` — the one sanctioned exception to the no-driver-changes rule), timeboxed 3–5 days per the plan.
>
> — `2026-06-11_bfc672b4.txt:230`

### <a id="d-258"></a>D-258 — Whether to run the separately labeled post-fix detector run is left as Ali's call

`2026-06-12 → 2026-06-20` · **superseded** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Leave the post-fix re-run decision open and with Ali: applying the two one-line var-lane fixes cannot be folded into the existing results because the G2 protocol requires a separate labeled run (~9 h), so Claude leaves the fix and run untouched and puts the go/hold call to Ali; the frozen numbers are held to be citable as they stand once the defect is disclosed. It is recorded as the only open item blocking ISSUES #29 → resolved.

**Why.** Both fixes are one-liners and the re-run is worth it for the defense slide, but the frozen numbers are already citable with the defect disclosure, and the commit-keyed cache invalidates wholesale so the re-run costs another overnight.

**Status.** superseded. Superseded by [D-260](#d-260) — Close #29 with a three-run audit trail, the frozen run as the citable primary.

**Source.** `a:bfc672b4-41`, `a:0e14484d-12` · Artifacts: `merge-tool-comparison/ISSUES.md:696`

> **Post-fix run?** Both fixes are one-liners; a separately-labeled re-run (~9 h, another overnight) plausibly takes R1 to 0/193 [0, 1.9%]. Worth it for the defense slide, but the frozen numbers are already citable with the defect disclosure.
>
> — `2026-06-11_bfc672b4.txt:647`

> Per the G2 protocol that's a separate labeled run (~9 h). Want me to make that fix + run, or hold? That's your call — I left it untouched.
>
> — `2026-06-20_0e14484d.txt:230`

### <a id="d-259"></a>D-259 — Every number is labelled by what it can support: validation-only, tuning-tainted, coarse-n, or corrected

`2026-06-24 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Five instances are Claude's reporting decisions; the TUNING-TAINTED labelling requirement was issued in Ali's session brief. Recorded as joint to reflect both.*

**Decision.** Report measurements with the qualification that matches their provenance and precision: the 20-merge/arm smoke's cost numbers are directional validation of the harness and explicitly not citable results; GD2 is scoped to mechanism correctness and zero false positives on tune-controls, with any claim about real-world catch rate deferred to the pre-registered frozen-suite evaluation at S-D5; the same detector run over derivation units is descriptive only and must be labelled TUNING-TAINTED everywhere shown, held-out recall being the gating measurement; the G1 pass is reported together with the caveat that both machine conditions clear with modest margins (attribution 36.4% just above the 35% floor, escape-hatch 63.6% near the top of the [15%,65%] band, Wilson upper 70.6%); the n=12 reliability gate is published with its Wilson CI and framed as a coarse corroborating check rather than primary evidence; and a misprinted gate figure is corrected rather than left standing (stratum-B at-T3-floor fraction 6.3% → 23/111 = 20.7%).

**Why.** The smoke ran the first 20 merges per arm — a non-random subset — so its purpose was plumbing validation, not results. Claims about real-world catch rates are deliberately reserved for the frozen-suite evaluation so they cannot be an artifact of tuning. n=12 gives a wide CI in which one override swings the result ~8 points and 9/12 = 75.0% is a knife-edge, so it must not be oversold. The 6.3% figure was a display bug from exact-string matching that excluded the T3/cap* hard-fit variants.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-225](#d-225) (see the reconciliation note there)

**Source.** `b:fb0fa5c5-13`, `a:acf7e1d0-14`, `a:6a84a6b3-06`, `a:788e483b-06`, `a:9e4b6896-14`, `a:92a3e464-19` · Artifacts: `reports_taxonomy/phase1/summary.txt`, `reports_taxonomy/phase3/adjudication/`, `outputs/detector-cycle-plan.md §5 GD3`, `tools/taxonomy_assemble.py`

> **Purpose was validation, not citable results**
>
> — `2026-06-24_fb0fa5c5.txt:375`

> GD2 was never meant to prove claim 3 — it's the build-time bar (mechanism + zero-FP); claims about real-world catch rates are deliberately reserved for the frozen-suite evaluation so they can't be an artifact of tuning.
>
> — `2026-07-16_acf7e1d0.txt:491`

> n=12 is a small denominator, so the gate is a coarse validity check with a wide CI — one override swings it ~8 points (9/12 = 75.0% is the knife-edge). I'll publish it with the Wilson CI and frame it as corroborating, not decisive on its own
>
> — `2026-07-11_9e4b6896.txt:493`

> units — descriptive only, labeled TUNING-TAINTED everywhere shown.
>
> — `2026-07-16_6a84a6b3.txt:28`

### <a id="d-260"></a>D-260 — Close #29 with a three-run audit trail, the frozen run as the citable primary

`2026-07-02 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: One source attributes the closing decision to Claude; the retrospective source records actors as unclear. Attributed to Claude on the stronger source; Ali's approval of the round-2 rerun is recorded separately in the run-labelling decision cited as context.*

**Decision.** Publish the detector results as a three-run audit trail rather than a single corrected number: frozen R1 4/193 = 2.1% is the citable primary, with post-fix round 1 (5ed92a2) at 3/193 and round 2 (f964354) at 0/193 [0, 2.0] published as separately labeled runs, the tcurdt flag retired as defect-dependent and R2 recorded as 11/164. The round-2 run was re-scored end to end (R2 unchanged, zero verdict flips) and closes ISSUES #29.

**Why.** The frozen run is honest and pre-registered while the post-fix runs verify the fixes, and the wrinkles — a defect-dependent lucky true positive, two residual guard defects — are documented rather than smoothed over.

**Status.** adopted. Supersedes: [D-258](#d-258) — Whether to run the separately labeled post-fix detector run is left as Ali's call.

**Cross-theme.** *duplicates* → [D-102](#d-102) — Same closing arc, two facets: gate discipline (here) and the fix work with its two disclosed rounds (detection). Kept separate, cross-linked.

**Cross-theme.** *depended on by* ← [D-405](#d-405) (see the reconciliation note there)

**Source.** `a:fb0fa5c5-38`, `a:dc3bc182-sub-sub-agent-a495a0-02` · Artifacts: `45a87e6`, `ISSUES.md #29`, `THREATS_TO_VALIDITY.md`, `f964354`, `5ed92a2`

> Closes #29 with the clean citable pair: frozen-run R1 2.1% (honest, pre-registered) + post-fix R1 ~0% (the fixes verified).
>
> — `2026-06-24_fb0fa5c5.txt:2065`

> The post-fix round-2 run (`f964354`) drove **R1 → 0/193 = 0.0% [0, 2.0]** with R2 unchanged and zero verdict flips → **ISSUES #29 resolved**.
>
> — `2026-07-18_dc3bc182_sub-agent-a495a0.txt:39`

### <a id="d-261"></a>D-261 — No run counts until the environment reproduces known answers exactly

`2026-07-03 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Four instances are Claude's design of the gate; the S-D8 live-probe requirement was mandated in Ali's session brief. Recorded as joint to reflect both, not because options were put and picked.*

**Decision.** Every remote or scoring run is preceded by a known-answer environment gate that must reproduce committed results exactly before results are trusted: the RM2 image is built natively on x86 from the committed Dockerfile and must pass 4 probes (toy known-answer cases plus exact reproduction of 3 cached file-level tags); the detector known-answer gate compares mergiraf outcomes as well as lane verdicts against the committed tune_d3 cache; the S-D7 baseline gate is operationalised as fresh mergiraf outcomes, merged-content hashes and all 5-lane baseline verdicts equal to postfix2's per file, rather than equality of aggregate unit-level numbers; and on the S-D8 instance every image is live-probed (including the real gjf format probe) with the exact canonical six-tool table required to reproduce before scoring. Gate outcomes are confirmed by pulling the gate log and file counts rather than trusting a step label or heartbeat. The kickoff's "R2=11/164 (12/164 incl. fail-closed)" is withdrawn as a conflation of two rounds: the operational target is postfix2's 11/164 = 10 flag + 1 fail-closed.

**Why.** Named as "the gjf-lesson validation bar": an environment must be shown to reproduce known answers before its outputs are accepted, and the canonical table is what makes the ship-images path safe because it excludes the arm64-class failure. Per-file verdict and hash equality is a stronger check than unit-level number equality, and only postfix2's verdict set is reproducible by the 732d8ff lanes flag-OFF.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-305](#d-305) (see the reconciliation note there)

**Source.** `a:7b3b2669-06`, `a:2e726dc0-02`, `a:06ec13eb-02`, `a:06ec13eb-06`, `a:68c24033-07`, `b:68c24033-15` · Artifacts: `merge-tools/refactoring-miner:2.4.0`, `reports_detection/postfix2/`, `run_sd8.sh`, `ISSUES.md #31`

> with toy known-answer probes plus exact reproduction of 3 cached file-level tags before the run (the gjf-lesson validation bar)
>
> — `2026-07-03_7b3b2669.txt:114`

> live-probe every image on-instance AND require the exact canonical six-tool table reproduction before scoring — the table itself is what makes path 2 safe.
>
> — `2026-07-22_68c24033.txt:85`

> Known-answer gate operationalized as: fresh mergiraf outcomes + merged-content hashes + all 5-lane baseline verdicts equal to postfix2's, per file — stronger than unit-level number equality.
>
> — `2026-07-22_06ec13eb.txt:35`

### <a id="d-262"></a>D-262 — Numbers from separate labeled evaluations are never blended

`2026-07-03 → 2026-07-22` · **adopted** · `[chat]` · corroboration: single-pass · confidence: high · actors: ali

*Actors note: Ali stated the never-blend rule (a:8740dbd3-03, "this is a NEW labeled evaluation, separate"); the second source records Claude applying it to the S-D7 cycle by freezing detect_validate.py, not deciding it independently. The sources differ on who acted, not on who ruled.*

**Decision.** Each evaluation is a distinct labeled run whose numbers are kept apart from every other: the Phase-2b evaluation runs detectors at the current committed code with the short sha recorded and is treated as a NEW labeled evaluation whose numbers must never be blended with the frozen Stage-C numbers; and in S-D7, detect_validate.py stays frozen with new runs living in reports_detectors/stagec_rerun/, the baseline arm reproducing the frozen Stage-C verdicts as its known-answer gate, and S-D7 numbers never blended with S-D5 numbers in any derived figure.

**Why.** Stated as authority rather than argued: "this is a NEW labeled evaluation, separate from the frozen Stage-C numbers — never blend them", with the S-D7 deliverable being the before/after table on one instrument.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-410](#d-410) (see the reconciliation note there)

**Source.** `a:8740dbd3-03`, `b:2e726dc0-25` · Artifacts: `merge-tool-comparison/reports_detection/phase2b/`, `reports_detectors/stagec_rerun/`, `tools/detect_validate.py`

> this is a NEW labeled evaluation, separate
>
> — `2026-07-03_8740dbd3.txt:157`

> NEVER blend with S-D5 numbers in
>
> — `2026-07-16_2e726dc0.txt:784`

### <a id="d-263"></a>D-263 — Phase-2b is gated on recon where a documented dead-end is an acceptable outcome

`2026-07-03` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Claude drafted the gate-first session prompt (recorded as proposed) and Ali issued it as the Phase-2b brief; recorded as joint because the gate only became binding when Ali issued it.*

**Decision.** Make Stage 0 of Phase-2b a local, timeboxed recon with an explicit gate: Phase-2b proceeds only if the recon locates a materializable labeled artifact (per-scenario semantic conflicts with retrievable base/ours/theirs). If not, write the findings to research/outputs/phase2b-recon.md, update STATUS's Phase-2b sentence to "investigated, no usable artifact — documented YYYY-MM-DD", and stop. Do not force a poor-fit dataset, and no AWS spend before the gate passes.

**Why.** "This is gated recon-first work: a documented dead-end is an acceptable outcome" — the honest failure mode should be an explicit documented deliverable rather than a forced result, which avoids committing compute and evaluation credibility to a poor-fit dataset.

**Status.** adopted.

**Source.** `a:fb0fa5c5-43`, `a:8740dbd3-01` · Artifacts: `research/outputs/phase2b-recon.md`, `STATUS.md`

> gated recon-first work: a documented dead-end is an acceptable outcome.
>
> — `2026-07-03_8740dbd3.txt:6`

> Prompt 2 is **gate-first** — the honest failure mode ("no usable artifact") is an explicit, documented deliverable rather than a forced result
>
> — `2026-06-24_fb0fa5c5.txt:2400`

### <a id="d-264"></a>D-264 — Gates are enforced by machine checks that abort, not by reading the output

`2026-07-04 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Enforce gate conditions mechanically at the point of execution: the harness refuses to score until a G1 --inject-sanity run passes (10/10 injected stale-read probes fired) and sanity.json is recorded under the DRIVER_COMMIT, with the G1 run executed in the same --merged-source developer mode as the scoring arms; the Phase-3 runner validates freshly-assembled per-unit input text against the committed Phase-1 inputs for all 165 derivation units and aborts before submitting any batch on mismatch; the G2 conditions are formalised as a machine evaluator (g2_eval.md) that checks every model-cited anchor and coverage unit_id is a genuine derivation unit rather than judging by reading; the adjudication sample allocator always reserves a minimum number of agreeing units so the ≥75% acceptance gate is scorable in every scenario that passes condition 1; and a post-hoc scoring guard runs before results are written into the manifest.

**Why.** The G1 pass "separates 'detectors are blind' from 'harness is broken'", so subsequent misses are attributable to detector scope rather than environment, which is what makes the recall numbers citable. The assembly check is the guardrail working — it caught 13 apparent mismatches and aborted before submission. The mechanical G2 check guards against the confident-hallucination failure mode, where cited unit_ids and SHAs look plausible but do not match the real derivation units. The allocator change exists because a high-disagreement edge case (n_dis=52) left 0 agreeing units and the gate uncomputable. The post-hoc scoring guard prevents a repeat of incident 3.

**Status.** adopted.

**Source.** `a:8740dbd3-13`, `a:9e4b6896-02`, `a:9e4b6896-05`, `a:6296f4f6-06`, `a:2e726dc0-33` · Artifacts: `reports_taxonomy/phase2b/dev/sanity.json`, `reports_taxonomy/phase2/g2_eval.md`, `phase3/inputs`, `1b66a13`

> The G1 pass is the important checkpoint: it separates "detectors are blind" from "harness is broken"
>
> — `2026-07-03_8740dbd3.txt:297`

> it caught 13 derivation units whose freshly-assembled text differs from the committed Phase-1 inputs, and aborted **before** submitting any batch. This is exactly the guardrail working.
>
> — `2026-07-11_9e4b6896.txt:141`

> before trusting it I must run the **firewall + gate checks mechanically** — several cited unit_ids/SHAs look like they may not match the real derivation units (the confident-hallucination failure mode)
>
> — `2026-07-10_6296f4f6.txt:114`

### <a id="d-265"></a>D-265 — Instrument wording and predictions are committed before the data they will be applied to exists

`2026-07-04 → 2026-07-10` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: The Phase-2 ordering instruction came from Ali's session brief; the fresh-session requirement and the frozen pre-run mapping are Claude's. Recorded as joint.*

**Decision.** Finalize and commit each measurement instrument before any of its data is assembled, and do it in a session that has not seen the data: the 17-row mapping of spgroup positives onto the 7-category taxonomy is written and frozen in category_mapping_draft.md before the AWS run (remaining a draft pending Ali's row-by-row adjudication, with row 14 flagged VERIFY, and only adjudication making the per-category table citable); Phase-2 consolidation is run in a brand-new session, not the S2 session; and its instruction wording is committed (f5935ba) before any {PHASE1_TAGS} content is read or assembled, so the ordering is visible in the git log.

**Why.** Freezing before the run means a predicted expected-FN can be confirmed rather than post-hoc rationalised. A fresh session is required because "the S2 session already has the Phase-1 tags, verdicts, and mechanism summaries in its context" — wording finalized there would be finalized by an assistant that had already seen the data it is supposed to be blind to, and the log could not demonstrate otherwise; committing first makes the pre-registration auditable in git.

**Status.** adopted.

**Source.** `a:8740dbd3-10`, `a:4c7b0828-20`, `a:6296f4f6-01` · Artifacts: `merge-tool-comparison/reports_detection/phase2b/category_mapping_draft.md`, `prompts_taxonomy/phase2_consolidation.md`, `f5935ba`

> FINALIZE THE PROMPT BEFORE TOUCHING DATA.
>
> — `2026-07-10_6296f4f6.txt:11`

> A fresh session makes the pre-data finalization genuinely pre-data and auditable.
>
> — `2026-07-06_4c7b0828.txt:1247`

> category mapping frozen before the run, G1 positive control firing 10/10 minutes before the zeros — this is a defensible negative result
>
> — `2026-07-03_8740dbd3.txt:356`

### <a id="d-266"></a>D-266 — The split and control draws are committed before any content-bearing work, and held-out content never touches the instrument

`2026-07-08 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Three instances were issued in Ali's session briefs (split file first, derivation-only anchors, controls committed first) and four are Claude's design or refusals. Recorded as joint to reflect the mixed authorship of one discipline.*

**Decision.** Fix the population split before any labelling exists and keep held-out material out of every instrument: decide and record the corpus split up front (taxonomy derivation on one partition, detector evaluation frozen-run-style on a held-out partition or the other corpus); compute and commit reports_taxonomy/split_assignment.csv (seeded 60% derivation split, SEED=20260709, stratified A/B) before issuing any API request containing unit content, with held-out content appearing nowhere except the assembly cache; draw all codebook anchors, examples and prose only from the 165 derivation-split Phase-1 outputs with restricted fields, verified by a mechanical firewall check on cited unit_ids; exclude frozen codebook §5 (the provisional coverage table) from the Phase-3 prompt; commit the tune-controls and eval-controls lists, the draw script and their hashes before any other session artifact; forbid build sessions S-D2–S-D4 from opening the pre-existing scenario directories of the 32 overlapping eval/spare merge ids, with S-D5 materialising eval-controls fresh from the committed list; and refuse to touch held-out units for early true-positive evidence, the only permissible earlier demonstration being a reproduced merge from outside the study corpora, explicitly labelled a demo rather than a measurement.

**Why.** Deriving the taxonomy from the Schesch positives and then evaluating new detectors on the same positives is tuning on the test set — "the exact sin the G2 freeze protocol exists to prevent" — and the thesis's credibility visibly rests on avoiding it. Inlining §5 would leak labels for 60/275 units into an independent relabel and corrupt the stability and reliability metrics. Committing the draw first means results cannot influence it, and touching anything held-out early would poison the number that actually matters.

**Status.** adopted.

**Source.** `b:4c7b0828-11`, `a:92a3e464-03`, `a:6296f4f6-05`, `a:9e4b6896-01`, `a:506d875b-04`, `a:506d875b-11`, `a:acf7e1d0-15` · Artifacts: `reports_taxonomy/split_assignment.csv`, `d12cf4a`, `controls/`, `cf59d37`, `prompts_taxonomy/phase3_closed_coding.md`, `a8734c7`, `outputs/taxonomy-protocol.md §4`

> You need a split *decided up front*: derive taxonomy on corpus A (or a partition), evaluate detectors frozen-run-style on a held-out partition or the other corpus.
>
> — `2026-07-06_4c7b0828.txt:637`

> Controls committed first (`cf59d37`) — split-first discipline honored.
>
> — `2026-07-15_506d875b.txt:97`

> Inlining it into the closed-coding prompt would leak labels for 60/275 units into an independent relabel, corrupting the stability/reliability metrics.
>
> — `2026-07-11_9e4b6896.txt:107`

> Within the study, touching anything held-out early would poison the number that actually matters.
>
> — `2026-07-16_acf7e1d0.txt:493`

### <a id="d-267"></a>D-267 — Pre-register the whole taxonomy protocol, with numeric gate criteria, in Session 0

`2026-07-08` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Claude argued for Session 0 and drafted the gate numbers; Ali issued the Session-0 brief and adopted the proposal. Recorded as joint.*

**Decision.** Run the taxonomy program phase-by-phase in separate sessions, but require a Session 0 whose only output is a pre-registered protocol document plus committed prompt templates — no labeling runs, no detector changes, no blending with Stage-C or Phase-2b numbers. Session 0 commits all phase definitions, prompt templates with data-dependent slots, escape hatches, reliability-subset size, the corpus split, and gates G0–G3 with numeric pass criteria fixed before any data exists: attribution ≥35%, escape band 15–65%, spot-check ≤3/15 rejects, coverage ≥90% for codebook freeze, stability ≥80% agreement ∧ κ ≥0.70, Ali's reliability acceptance ≥75%. Later phases are mechanical instantiation.

**Why.** "If each phase's design is decided only *after* seeing the previous phase's results, a reviewer can ask: 'did you shape the codebook to make the numbers look good?' — garden-of-forking-paths." The taxonomy finding later feeds new-detector design, so the protocol must be pre-registered to prevent tuning-on-test from the start, and the criteria are therefore fixed now; the gate style mirrors the G0/G1/G2 gates of p1-detection-validation-plan.md.

**Status.** adopted.

**Source.** `a:4c7b0828-13`, `a:cfe6365a-01`, `a:cfe6365a-05` · Artifacts: `merge-tool-comparison/outputs/taxonomy-protocol.md`, `merge-tool-comparison/outputs/p1-detection-validation-plan.md`, `ISSUES #30`

> **step-by-step execution is right, but the design must not be step-by-step.**
>
> — `2026-07-06_4c7b0828.txt:693`

> gates G0–G3 with numeric pass criteria fixed now (attribution ≥35%, escape band 15–65%, spot-check ≤3/15 rejects; coverage ≥90%; stability ≥80% agreement ∧ κ ≥0.70; your reliability acceptance ≥75%)
>
> — `2026-07-08_cfe6365a.txt:90`

> so the protocol must prevent tuning-on-test from the start.
>
> — `2026-07-08_cfe6365a.txt:13`

### <a id="d-268"></a>D-268 — Frozen authority documents: harness adapts, and changes only via dated §12 amendments

`2026-07-08 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Ali's briefs declared the freeze and the amendment rule; Claude applied and enforced them (Amendment 1, the trivial-clarification calls, the new runner). Recorded as joint.*

**Decision.** Treat the pre-registered protocol and its prompt/schema artifacts as frozen authorities pinned to a commit (outputs/taxonomy-protocol.md at 9209327; prompts_taxonomy/'s Phase-1 prompt and schema): harness code adapts to them, never the reverse, and detect_validate.py and the detector suite at 732d8ff are likewise left unedited, with a new runner built alongside them. Once data exists, any change to a frozen document is a dated, sanctioned §12 amendment inside the document — never a silent edit — while resolutions that do not change the measurement design are recorded as session-log clarifications or paste-time patches instead. Amendment 1 is the worked example: the Batches API custom_id pattern rejects the frozen p1::<merge_id> scheme, so an API-safe custom_id() is added to the harness keeping the logical key unchanged, the scheme is recorded in the manifest, and a dated §12 amendment is appended with §1–§11 left byte-identical.

**Why.** The pre-registered protocol is "the sole authority" and changes must be non-silent so deviations are auditable, following the Stage-B precedent for sanctioned amendments. The custom_id change is "a real, forced deviation from a §9-pinned detail", so the §12 amendment is used as the sanctioned, non-silent mechanism rather than silently reconciling — only the wire encoding changes, not the logical key. Conversely, where the measurement design is not changing (only a gate's target arithmetic, resolved from committed artifacts), a session-log record is the honest instrument.

**Status.** adopted.

**Source.** `a:92a3e464-01`, `b:4c7b0828-23`, `a:06ec13eb-03`, `b:cfe6365a-11`, `a:acf7e1d0-01`, `a:2e726dc0-30`, `a:92a3e464-20` · Artifacts: `outputs/taxonomy-protocol.md`, `9209327`, `merge-tool-comparison/prompts_taxonomy/`, `tools/taxonomy_common.py`, `63298b0`, `reports_detectors/stagec_rerun/`, `ISSUES #31`

> data exists = dated, sanctioned amendment in the doc (Stage-B precedent),
>
> — `2026-07-08_cfe6365a.txt:53`

> This is a real, forced deviation from a §9-pinned detail, so I'll (1) add an API-safe `custom_id()` to the harness, (2) record it in the manifest, and (3) append a dated **§12 amendment** to the protocol (the sanctioned, non-silent mechanism) rather than silently reconciling.
>
> — `2026-07-08_92a3e464.txt:311`

> Suite untouched at `732d8ff`, zero amendments, `detect_validate.py` unedited.
>
> — `2026-07-22_06ec13eb.txt:127`

> the session should record it in its session log as a paste-time patch (no §12 amendment; the measurement design isn't changing, only the gate's target arithmetic)
>
> — `2026-07-16_2e726dc0.txt:953`

### <a id="d-269"></a>D-269 — Workload models, prompts and request parameters are pinned in the manifest; session models are not

`2026-07-08 → 2026-07-09` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Pin the measurement instruments' provenance and freeze their parameters: workload models (claude-opus-4-8 for both labeling passes, claude-fable-5 for consolidation) are frozen at Session 0 together with prompts and commit hashes, recorded per phase run in reports_taxonomy/manifest.json (model, prompt, commit), and the Phase-1 batch requests' output_config {"effort": "high"} stays exactly as pinned — changing either mid-stream is a §12 protocol amendment. Session models and session effort used inside Claude Code are scaffolding, free to vary, and do not appear in the thesis.

**Why.** A mid-stream workload-model change "breaks pass-to-pass comparability", whereas session models are "scaffolding, not measurement instruments"; the workload effort is a pinned request parameter recorded in the manifest and so is not the session's to vary, while extra session reasoning depth buys little on mechanical work against a frozen spec.

**Status.** adopted.

**Source.** `a:4c7b0828-15`, `b:4c7b0828-24`, `a:cfe6365a-20` · Artifacts: `outputs/taxonomy-protocol.md §9`, `merge-tool-comparison/reports_taxonomy/manifest.json`

> **Session models are free to vary** — they're scaffolding, not measurement instruments.
>
> — `2026-07-06_4c7b0828.txt:746`

> The **workload** effort is a different knob and it's already frozen by the protocol: the Phase-1 batch requests themselves carry `output_config: {"effort": "high"}` per §9, recorded in the manifest. That one isn't yours to vary at session time; changing it would be a §12 amendment because it's a pinned request parameter.
>
> — `2026-07-06_4c7b0828.txt:1127`

> model/prompt/commit pinning via `reports_taxonomy/manifest.json`; eight THREATS additions; dated-amendment rule in §12
>
> — `2026-07-08_cfe6365a.txt:90`

### <a id="d-270"></a>D-270 — The G0 pilot exercises production plumbing but its outputs are discarded and its units relabelled

`2026-07-08 → 2026-07-09` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: The Batch-API-path and discard instructions came in Ali's session brief; the manifest verdict recording and the relabel handling are Claude's. Recorded as joint.*

**Decision.** Run the G0 calibration pilot (10 derivation units, 7 A / 3 B) through the Batch API path with the frozen Phase-1 prompt, structured outputs from phase1_output.schema.json, thinking adaptive, effort high, model claude-opus-4-8. Discard the pilot's model outputs, record that fact in the manifest, and relabel the 10 units from scratch in the production run like any other unit. Record the verdict as G0 PASS in manifest.json (10/10 parseable and conforming, all end_turn, 0 over the 30k cap, escape hatches exercised 3 attributed / 3 indeterminate / 4 none-identified, T3/cap1 path exercised) with the discard and relabel-in-S2 flags attached, and append the S1 summary to ISSUES #30.

**Why.** "Prefer the Batch API path so G0 exercises the production plumbing end-to-end." The G0 pass criteria as written were met, and the protocol requires the discard/relabel status to be recorded in the manifest.

**Status.** adopted.

**Source.** `a:92a3e464-04`, `b:92a3e464-05`, `a:4c7b0828-19`, `a:92a3e464-23` · Artifacts: `reports_taxonomy/g0_pilot/`, `reports_taxonomy/manifest.json`, `phase1_output.schema.json`, `f724e0a`, `ISSUES #30`

> Pilot outputs are DISCARDED (record that in the manifest); the 10 units
>
> — `2026-07-08_92a3e464.txt:50`

> **G0 PASS** — 10/10 parseable/conforming, all `end_turn` (no truncation/refusals), 0 over the 30k cap, escape hatches exercised
>
> — `2026-07-08_92a3e464.txt:349`

### <a id="d-271"></a>D-271 — One G2 freeze commit locks the codebook and the Phase-3 category enum together

`2026-07-08 → 2026-07-11` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: The stop-at-the-freeze-commit and residual-other requirements came from Ali's brief; the enum contents and freeze commit are Claude's execution. Recorded as joint.*

**Decision.** Ship the Phase-2/3 prompts as skeletons with {PHASE1_TAGS} / {FROZEN_CODEBOOK} slots and populate the Phase-3 output-schema category enum only at the G2 codebook-freeze commit. That commit (3e7d9b4) freezes codebook_frozen.md (8 mechanism categories plus residual-other, with a provenance header recording Ali's ruling) together with phase3_output.schema.json — primary enum = 8 ids + residual-other + 3 escape hatches (12 values), secondary = 8 + residual-other (9), skeleton note removed — and is recorded in manifest.phase2.freeze, with S4 pinning frozen_codebook_commit = 3e7d9b4. A residual-other category ships even though zero units land in it, Phase-3 coders may use only the frozen set, and no Phase-3 request, codebook_frozen.md or filled enum may exist before the freeze commit does.

**Why.** The residual bucket is required so Phase-3 always has somewhere to put a merge that fits nothing, given that Phase-3 may not invent categories. No reason is recorded for the single-commit freeze or the stop-at-the-gate rule beyond the protocol's own sequencing.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-452](#d-452) (see the reconciliation note there)

**Source.** `a:cfe6365a-19`, `a:6296f4f6-04`, `b:6296f4f6-04`, `a:6296f4f6-18`, `b:6296f4f6-22` · Artifacts: `3e7d9b4`, `reports_taxonomy/phase2/codebook_frozen.md`, `prompts_taxonomy/phase3_output.schema.json`, `prompts_taxonomy/phase3_closed_coding.md`, `reports_taxonomy/manifest.json`

> NO Phase-3 request may exist before the freeze commit does.
>
> — `2026-07-10_6296f4f6.txt:57`

> It's the mandatory empty "none of the above" bucket the protocol requires so Phase-3 always has somewhere to put a merge that fits nothing.
>
> — `2026-07-10_6296f4f6.txt:248`

> category enum locked: **primary** = the 8 ids + `residual-other` + the 3 escape hatches; **secondary** = 8 + `residual-other`. Skeleton note removed.
>
> — `2026-07-10_6296f4f6.txt:413`

### <a id="d-272"></a>D-272 — Yellow-band stability buys exactly one clarification amendment and a full controlled rerun

`2026-07-08 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: The pre-registered path and the amendment proposal are Claude's; Ali approved Amendment 2 and the rerun ("Approved. Executing the amendment path"). One retrospective source records actors as unclear.*

**Decision.** Pre-register the yellow-band path (G3 stability gates at ≥80% agreement and κ ≥0.70 with ≤60 disagreements; 60–80% or κ 0.50–0.70 triggers exactly one sanctioned dated codebook-clarification amendment followed by rerunning both passes; below the band the program returns to Phase 2, written up as a documented failure) and honour it when v1 lands at 78.9% agreement / κ 0.741 with 58 disagreements: commit the yellow outcome as a documented result, propose Amendment 2 and wait for Ali before touching the instrument. The amendment adds one R1 clarification distinguishing the escape hatches by whether a concrete cross-side interaction is articulable — none-identified when none can be named, indeterminate when a nameable-but-unsettleable interaction exists or the code is demonstrably hidden — with no change to categories, enum, base-rate definitions or attribution thresholds. The yellow raw results are then archived to invalidate the cache per §9 so both passes resubmit fresh, and everything else is held constant (population, byte-identical per-unit inputs, model/API/params, codebook §1–§4, enum/schema, rules R2–R7/C1–C4); the rerun scores 82.9% [78.0, 86.9] / κ 0.788 = PASS.

**Why.** The yellow-band cycle is pre-priced in the budget and returning to Phase 2 is explicitly a writable outcome, so landing there is the protocol working rather than failing. The clarification is narrowly scoped because 35 of 58 disagreements were none-identified ↔ indeterminate and 37/58 escape↔escape while only 3 were category↔category: on the flip units both passes agreed on the substance and split only on which escape to use, because the instrument gave no operational rule to choose. Holding everything else fixed makes it a clean controlled comparison, so any change in stability is attributable to the single clarification.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-226](#d-226) (see the reconciliation note there)

**Source.** `b:4c7b0828-29`, `a:9e4b6896-10`, `a:9e4b6896-08`, `a:9e4b6896-12`, `a:9e4b6896-11`, `a:dc3bc182-sub-sub-agent-a495a0-05` · Artifacts: `reports_taxonomy/phase3/stability.md`, `reports_taxonomy/phase3/amendment2_proposal.md`, `597e535`, `3474b09`, `outputs/taxonomy-protocol.md §12`, `merge-tool-comparison/reports_taxonomy/FINDINGS.md`

> The yellow-band path (one clarification amendment + full rerun) is pre-priced in the budget, so if it lands there, that's the protocol working, not failing.
>
> — `2026-07-06_4c7b0828.txt:1366`

> This is the mandated **STOP point** — the yellow band permits exactly one codebook-clarification amendment, and the protocol says propose it and wait for you.
>
> — `2026-07-11_9e4b6896.txt:219`

> On every one of the 35, both passes *agree on the substance* (disjoint/self-consistent sides, clean composition) and split only on which escape label to use, because the instrument never gave an operational rule to choose between them.
>
> — `2026-07-11_9e4b6896.txt:231`

> So this is a **clean controlled comparison**: the *only* variable is the escape-hatch decision rule.
>
> — `2026-07-11_9e4b6896.txt:378`

### <a id="d-273"></a>D-273 — A gate is scored against its written criterion, and the re-scoring ruling goes into the record

`2026-07-10 → 2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** When a gate appears to fail, score it against the criterion as pre-registered and record the scoping ruling in the machine record rather than either waving it through or failing it on a proxy count. G1 condition (iii) is scored as 0/15 qualifying rejections → PASS, scoping rejections to 'hallucinated or unsupported-by-quotes' and reclassifying Ali's 4 REJECT-UNSUPPORTED clicks as population/selection objections excluded from the gate count, with no §12 amendment filed because the gate was applied as written. GD1's machine coverage of 37/48 = 77.1% is decomposed into 9 cross-file-declaration units (unreachable for file-local detectors by construction) plus 2 truncation-limited, and re-scored on the file-local target set as 37/39 = 94.9% → PASS, recorded as §12 Amendment 2 with the ruling written into gd1_machine.json.

**Why.** All 4 G1 rejections were on escape-hatch verdicts where the model claimed no mechanism, so there was no causal story to be hallucinated or unsupported; the stated reason ("not a good representation of the silent merge conflicts") is a population/selection objection that actually agrees with the model's escape-hatch call, and the prescribed FAIL remedy — a full rerun — would reproduce the same correct escape hatches without addressing the concern. For GD1, the excluded units are out of reach of file-local detectors by construction, so counting them against a file-local gate misstates coverage.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-235](#d-235) (see the reconciliation note there)

**Source.** `a:788e483b-07`, `a:506d875b-09` · Artifacts: `merge-tool-comparison/reports_taxonomy/phase1/spotcheck/g1_iii_adjudication.md`, `f2b9818`, `gd1_machine.json`, `outputs/detector-cycle-plan.md §12 Amendment 2`, `ISSUES #31`

> your reason is a **population/selection** objection ("these aren't good silent-merge examples") — which is *different* from the criterion the gate is scored on
>
> — `2026-07-09_788e483b.txt:307`

> **GD1 went through its failure path and passed via your Amendment 2 ruling**: machine coverage 37/48 = 77.1% decomposed into 9 cross-file-declaration units (unreachable for file-local detectors by construction) + 2 truncation-limited — file-local re-score 37/39 = 94.9%.
>
> — `2026-07-15_506d875b.txt:135`

### <a id="d-274"></a>D-274 — One frozen authority doc per program, artifact-only handoff, pre-written prompts with STOP points

`2026-07-15 → 2026-07-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Claude codified the instrument; Ali ruled "lets do S0 first — write the distiller and freeze the schema" for its reuse. Recorded as joint.*

**Decision.** Codify the cross-session instrument and reuse it: every multi-session program has one frozen, commit-pinned authority document that each session prompt references rather than copies; state passes only through committed artifacts, never chat context or a summary handoff; each prompt carries an explicit STOP point and a uniform close-out (commit referencing the issue, summary appended to ISSUES, manifest/memory updated); all prompts are written at planning time in the plan document itself; and deviations become dated amendments. Applied to the extraction program: kickoff prompts reuse the S-D1..S-D8 shape (AUTHORITY / STATE / SCOPE / GUARDRAILS / EXIT / STOP), each session commits its JSON for the consolidator to read from disk, and S0 must produce the frozen extraction schema before any extraction session runs.

**Why.** "Alignment across sessions never comes from the prompts themselves; it comes from one frozen authority document that every prompt points to, plus artifact-only state", and writing all prompts at planning time gives "One author, one sitting, one consistent intent — that's where alignment is actually manufactured." Without a frozen schema, seven sessions will use seven different granularities for "decision" and the consolidator inherits an incoherent pile — the same problem the frozen codebook solved for closed coding.

**Status.** adopted.

**Source.** `a:4c7b0828-27`, `a:c4c4d030-19` · Artifacts: `outputs/detector-cycle-plan.md`, `outputs/taxonomy-protocol.md`, `ISSUES #30`

> **One authority doc per program, frozen, commit-pinned.**
>
> — `2026-07-06_4c7b0828.txt:1662`

> Use your own #30 rule — *"handoff between sessions is committed artifacts only."*
>
> — `2026-07-25_c4c4d030.txt:195`

> The one thing S0 must produce that v1 lacked: **the frozen extraction schema**.
>
> — `2026-07-25_c4c4d030.txt:197`

### <a id="d-275"></a>D-275 — GD3 requires literally zero control flags, and any flag stops the session for Ali

`2026-07-15 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: ali

**Decision.** Keep GD3's false-positive bar absolute: zero flags on the 200 eval-controls and the 66 spgroup-clean units, with a small adjudicated tolerance ("≤2 adjudicated-benign flags pass") considered and not adopted. Any control or spgroup flag halts the session and is packaged for Ali's adjudication with full context, the amendment path being his call; flags on held-out units do not gate S-D5 and route to S-D6 adjudication via the delivered adjudication UI.

**Why.** The absolute bar is kept as "defensible and consistent with the layer's identity" — the zero-FP record is the layer's differentiator — with §11 leaving the option of softening it consciously; and the amendment path after a control flag is Ali's call, not the agent's.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-235](#d-235) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-462](#d-462) (see the reconciliation note there)

**Source.** `a:4c7b0828-32`, `b:2e726dc0-03`, `a:6a84a6b3-05` · Artifacts: `outputs/detector-cycle-plan.md §11`, `outputs/detector-cycle-plan.md §5 GD3`, `gd3_flag_package.md`

> The alternative would have been a small tolerance (e.g., "≤2 adjudicated-benign flags pass"). The plan encodes *absolute*; you're confirming that's the bar you want to defend.
>
> — `2026-07-06_4c7b0828.txt:1760`

> the absolute zero-FP bar (defensible and consistent with the layer's identity — and §11 lets you soften it consciously if you disagree)
>
> — `2026-07-06_4c7b0828.txt:1809`

> 4. GD3: (ii) and (iii) require ZERO flags. Any control/spgroup flag →
>
> — `2026-07-16_2e726dc0.txt:39`

### <a id="d-276"></a>D-276 — The optional S-D7/S-D8 stages are decided at S-D6 close-out, not pre-committed

`2026-07-15` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** Do not pre-commit the optional Stage-C-protocol rerun (S-D7) or the whole-driver re-pricing (S-D8); record a run/later/never decision with one sentence of rationale at S-D6 close-out, so the detector cycle can close without them.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Source.** `a:4c7b0828-33` · Artifacts: `outputs/detector-cycle-plan.md §11`

> **S-D7/S-D8 deferred** — the optional Stage-C rerun and whole-driver re-pricing are decided at S-D6 close-out rather than pre-committed now.
>
> — `2026-07-06_4c7b0828.txt:1761`

### <a id="d-277"></a>D-277 — Hard-stop S-D5 at the ambiguity gate when the brief's state contradicts the repo

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Halt session S-D5 before any scope step and withdraw the brief's STATE line ("S-D1..S-D4 DONE, GD2 PASS ×3. The detector suite is complete.") as false, on five independent repo axes: ISSUES #31's status line, git HEAD at 83d3a23 with no S-D4 commits or stashes, reports_detectors/ lacking tune_d3, untouched unresolved_reference.py and RM2 rename lane, and only two GD2 build gates passed. Improvise no resolution: put the question to Ali and wait (he confirmed the premise was a mistake). Refuse in particular to record detector_suite_commit in reports_detectors/manifest.json at the current HEAD — the freeze and the whole evaluation battery wait until S-D4 lands.

**Why.** The discrepancy is material rather than trivial, and the prompt's own ambiguity gate requires asking Ali and waiting instead of improvising. Freezing now would freeze a suite without the D3 widening, so if S-D4 landed afterwards it would cost a dated §12 amendment plus a full S-D5 rerun — a second ~$5–10 AWS cycle and a wasted battery; and per §5 GD3 the two-arm added-recall delta exists to attribute D3, so without S-D4 the experimental arm is D1+D2 only and the D3 delta over the ~8% removed/renamed mass is zero by construction.

**Status.** adopted.

**Source.** `a:6a84a6b3-01`, `b:6a84a6b3-02`, `a:6a84a6b3-02` · Artifacts: `ISSUES #31`, `83d3a23`, `reports_detectors/manifest.json`, `unresolved_reference.py`, `outputs/detector-cycle-plan.md §3`

> **AMBIGUITY CHECK: HARD STOP — the prompt's STATE line contradicts every repo authority. S-D4 has not been run.**
>
> — `2026-07-16_6a84a6b3.txt:56`

> Per the ambiguity gate I'm not improvising a resolution — asking and waiting.
>
> — `2026-07-16_6a84a6b3.txt:71`

> Freezing now freezes a suite without the D3 widening; if S-D4 lands afterwards, that's a dated §12 amendment
>
> — `2026-07-16_6a84a6b3.txt:68`

### <a id="d-278"></a>D-278 — Lane widening must not change any verdict the lanes already produce

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: The regression floor was declared in Ali's session briefs; the corrected baselines and the full-suite GD2(iii) requirement are Claude's, and one sub-agent source records actors as unclear.*

**Decision.** Bind each build session to a regression floor: the widening is the smallest guarded change per inventoried shape and must not alter behaviour on any shape the existing lanes already handle, every existing fixture and regression test keeping its expected verdict — declared the hard constraint of the session. The unresolved_reference strategy's pre-existing behaviour must be byte-identical with SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS unset, and the tune runner's old CLI surface (--lane, --out dir, cache reuse, per-(scenario,lane,driver-commit) cache keys, vacuous-run smoke guard, exit codes) must survive the multi-lane rewrite. The floor is the actual pre-session suite count, not the plan's stale figure — 162 green tests rather than plan §3's 122, and 292 rather than the plan's stale count for S-D4 — recorded as a trivial clarification in the session log, with S-D4's GD2(iii) run executing the full suite including D1/D2.

**Why.** The strategy is a DEFAULT-ON merge-driver strategy, so any change to flag-unset behaviour is a hard regression, and the tune runner already worked for the ImportPruneUsage and SignatureStaleCall lanes. Interactions between lanes count, so the gate run must execute the full suite. The plan's stated baselines were simply out of date versus repo state.

**Status.** adopted. Supersedes: *plan §3's "122 green" regression baseline*; *plan §8's stale test-count baseline*.

**Source.** `a:82dd479f-03`, `a:82dd479f-sub-sub-agent-a46641-02`, `a:acf7e1d0-18`, `a:f0d70a59-02`, `b:f0d70a59-10` · Artifacts: `outputs/detector-cycle-plan.md §3`, `outputs/detector-cycle-plan.md §8`, `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`, `merge-tool-comparison/tools/detector_tune_run.py`, `ISSUES #31`

> expected verdict (this is the hard constraint of the session).
>
> — `2026-07-16_82dd479f.txt:23`

> a DEFAULT-ON merge-driver strategy whose pre-existing behavior must be BYTE-IDENTICAL when the env flag SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS is unset (hard regression constraint: every existing test keeps its verdict, and default driver behavior must not change at all)
>
> — `2026-07-16_82dd479f_sub-agent-a46641.txt:5`

> plan §3's "122 green" baseline is stale — the real pre-session suite was **162**, applied as the floor
>
> — `2026-07-16_f0d70a59.txt:69`

### <a id="d-279"></a>D-279 — Amendment 3: three-angle review of each detector before its gate may close

`2026-07-16 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: The requirement is issued in Ali's session brief; the retrospective source records actors as unclear. Attributed to Ali on the brief.*

**Decision.** Before a detector's build gate closes, review the widened lanes three ways: as project code (idiomatic to the lanes modified, /code-review at high effort sanctioned), as a standalone analysis against Java language semantics with the JLS consulted where unclear, and as an open-source practice comparison (Error Prone, SpotBugs, IntelliJ unresolved-reference inspections, Checkstyle) recording the comparators consulted plus divergences adopted or rejected. Each finding must be fixed — with GD2 rerun if a lane changed post-gate — or the non-fix documented. Applied across the cycle, e.g. 8 FP-vector fixes pre-gate on D3.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Cross-theme.** *duplicated by* ← [D-457](#d-457) (see the reconciliation note there)

**Source.** `a:82dd479f-01`, `a:dc3bc182-sub-sub-agent-a495a0-11` · Artifacts: `outputs/detector-cycle-plan.md §12 Amendment 3`, `merge-tool-comparison/reports_detectors/tune_d3/review_record.md`, `merge-tool-comparison/reports_detectors/`

> REVIEW (§12 Amendment 3): before closing, review the widened lanes
>
> — `2026-07-16_82dd479f.txt:29`

> Amendment-3 triple reviews (code-review high + standalone JLS + OSS-practice comparison; e.g. 8 FP-vector fixes pre-gate on D3)
>
> — `2026-07-18_dc3bc182_sub-agent-a495a0.txt:68`

### <a id="d-280"></a>D-280 — Post-gate code changes are reported not applied, then authorized and both gates rerun

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Claude reported and recommended without applying; Ali authorized. Options were put and Ali picked, so joint.*

**Decision.** Report post-gate review findings without applying any of them, because post-GD2 code changes are Ali's call and each requires a suite plus tune rerun to stay protocol-clean before the S-D5 freeze. Ali then authorized the recommended patch — throws/implements/extends/permits added to _EXPR_KEYWORDS, a depth-tracked enum-constant-list parser feeding declares_member, the conflict-marker abstention moved to the stripped text, plus the merged==parent soundness invariant test — with the suite and GD2(iii) rerun and the change recorded in the manifest as a post-GD2 patch with rerun.

**Why.** Post-GD2 changes are Ali's call, and each would require the suite plus tune rerun to stay protocol-clean before the S-D5 freeze (cached merges make the rerun ~2 min). The recommendation argued fixes #1–#3 plus invariant tests as one small pre-S-D3 commit, all in the false-negative direction except #2, which tightens suppression.

**Status.** adopted.

**Source.** `a:f0d70a59-13`, `a:f0d70a59-14` · Artifacts: `bed3638`, `c14670a`, `merge-tool-comparison/reports_detectors/tune_d1/runs.md`

> nothing applied — post-GD2 changes are your call, and each would require the suite + tune rerun (protocol-clean before the S-D5 freeze, cached merges make the rerun ~2 min)
>
> — `2026-07-16_f0d70a59.txt:234`

> go ahead with the fixes and rerun the gates
>
> — `2026-07-16_f0d70a59.txt:266`

### <a id="d-281"></a>D-281 — Land the two verified FP-shape guards before D1 leaves the experimental flag

`2026-07-16` · **proposed** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Add the generics and multi-declarator false-positive shapes as tune fixtures and land the two suppression-side guard extensions before D1 graduates from behind the experimental flag; the repro probes at scratchpad/repro_ipu.py can be folded into the fixture battery.

**Why.** Both shapes are realistic — generics plus IDE import-optimization, and multi-declarators in older Java — even though GD2's 0/100 tune-control result stands.

**Status.** proposed. S12 (2026-07-26): still pending — no generics/multi-declarator fixtures exist in detector_tune_run.py, the two suppression-side guard extensions are not in import_prune_usage.py, and the default-enable ruling this precedes is still open with Ali. Nothing has been dropped; the precondition simply has not arrived.

**Cross-theme.** *depends-on* → [D-128](#d-128), [D-077](#d-077) — Default-enabling remains open (backends-routing entry, status=open), so the condition this proposal waits on has not occurred. Stays proposed; cross-linked to the open call.

**Source.** `a:734e4529-04` · Artifacts: `scratchpad/repro_ipu.py`

> both shapes are realistic (generics plus IDE import-optimization; multi-declarators in older Java), so I'd add both as tune fixtures and land the two suppression-side guard extensions before D1 graduates from behind the experimental flag
>
> — `2026-07-16_734e4529.txt:24`

### <a id="d-282"></a>D-282 — Frozen files are not edited: reviews work around them and their defects are documented

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: The no-edit constraint is stated as a project constraint in Ali's sub-agent brief; the dispositions (documented non-fix, explicit arm wiring, capped review scope) are Claude's.*

**Decision.** Treat the frozen Stage-C harness and the existing lane files as uneditable for the duration of a build session and route findings accordingly: existing detector lane files must not be modified (shared-helper extraction — a shared RM2Runner, promoting _FileView scan helpers — is scheduled for a later session at the earliest); the efficiency/altitude review may only raise findings where a concretely better alternative exists with detect_validate.py frozen and lane behaviour unchanged flag-off, capped at 6 candidate findings; the verdict_of substring sentinel ('inconclusive' in message) in the frozen Stage-C harness is left unchanged as a documented non-fix with a note that the new harness should key on a message prefix; and detect_validate.py's DETECTORS tuple continues to exclude ImportPruneUsage, so S-D5's two-arm harness must wire the experimental arm explicitly.

**Why.** detect_validate.py is a frozen instrument that must not be edited and existing lane behaviour must not change flag-off, so any proposed restructuring has to fit inside those constraints to be actionable. Gate outcomes are unaffected by the sentinel collision, and the exclusion of the lane from DETECTORS is correct today because detect_validate is the frozen Stage-C instrument — but it would otherwise silently produce no experimental-arm coverage at S-D5.

**Status.** adopted.

**Source.** `a:acf7e1d0-12`, `a:acf7e1d0-sub-agent-a88268-02`, `a:82dd479f-sub-sub-agent-a87c1f-01`, `a:f0d70a59-18` · Artifacts: `merge-tool-comparison/tools/detect_validate.py`, `semantic_merge_driver/strategies/rm2_strategies/rename_conflict.py`, `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`, `STATUS.md`

> documented non-fixes include the `verdict_of` "inconclusive"-substring sentinel in the frozen Stage-C harness (gate outcomes unaffected; S-D5 note: the new harness should key on a message prefix).
>
> — `2026-07-16_acf7e1d0.txt:453`

> is there a less fragile seam AVAILABLE WITHOUT editing the existing lane files (a hard project constraint from a frozen plan: existing lanes must not be modified this session; moving/extracting shared helpers is scheduled for a later session at the earliest)?
>
> — `2026-07-16_acf7e1d0_sub-agent-a88268.txt:5`

> Only flag when a concretely better altitude exists within the constraint that detect_validate.py is frozen and existing lane behavior must not change flag-off.
>
> — `2026-07-16_82dd479f_sub-agent-a87c1f.txt:9`

### <a id="d-283"></a>D-283 — S-D8's flag-OFF gate is a derived target (1779 + Δ = 1784), pre-registered and committed before the run

`2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Claude proposed the derived-target design and computed the target; Ali issued it in the session brief and made the rejection of the 9e25b4e pinning explicit. Options were put and Ali picked.*

**Decision.** Redefine the flag-OFF environment gate as a derived-target gate rather than literal reproduction of the P3 post-flip pooled cost of 1779: before running, compute the expected flag-OFF cost at the frozen suite 732d8ff from committed artifacts only (P3 post-flip per-file results re-priced for the five files whose verdicts the #29 post-fix commits 5ed92a2 and f964354 changed, under the same Schesch cost model), pre-register it — fixed and committed as 1784 pooled (pos 1768 / ctl 16) file-for-file — and require per-file agreement with the P3 post-flip table everywhere except those five files plus the two documented borderline-nondeterminism flips. The pre-registration must be in git before bundling, enforced by bundle_sd8.sh, and the deploy battery sequences smoke → canonical six-tool gate → flag-OFF arm → reconciliation gate against 1784 → flag-ON arm, with a --check-gate step that aborts between arms. Both arms stay on 732d8ff: pinning the flag-OFF arm back to 9e25b4e (where 1779 was measured) is rejected, as is the more expensive option of an extra redundant run.

**Why.** The frozen suite HEAD contains the #29 post-fix commits that changed default-lane behaviour, so a correct environment must NOT reproduce 1779 exactly; a naive "must equal 1779" gate would fail a healthy environment or push the session into "close enough" hand-waving that could mask a real env fault (the arm64-gjf class). The derived-target pattern is established practice, not improvisation — P3 used it for the −146 pre-flip/post-flip derivation and #29 for carried-frozen verdicts — and the derivation reproduced P3's 1779 to the digit, cross-validating the machinery. Pinning the flag-OFF arm to 9e25b4e would smuggle the post-fix changes into the flag-ON delta and break the freeze, and the third option buys ~$5.5 of redundancy the derivation already provides. The mid-battery gate exists so the flag-ON arm does not burn ~14 h of compute on a wrong environment.

**Status.** adopted. Supersedes: *kickoff env gate requiring literal reproduction of the post-flip 1779*.

**Cross-theme.** *depended on by* ← [D-111](#d-111) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-128](#d-128) (see the reconciliation note there)

**Source.** `a:2e726dc0-28`, `a:2e726dc0-29`, `a:68c24033-01`, `a:68c24033-02`, `a:68c24033-09`, `a:68c24033-10`, `a:68c24033-11` · Artifacts: `merge-tool-comparison/reports_detectors/whole_driver_flagon/predicted_flagoff.csv`, `merge-tool-comparison/reports_whole_driver/raw_results.json`, `reports_detection/postfix2/`, `bundle_sd8.sh`, `run_sd8.sh`, `732d8ff`, `9e25b4e`, `50d2754`

> Use a DERIVED-TARGET gate, not literal 1779.
>
> — `2026-07-22_68c24033.txt:69`

> A naive "must equal 1779" gate would fail on a healthy environment, or push the session into "close enough" hand-waving that could mask a real env fault
>
> — `2026-07-16_2e726dc0.txt:944`

> Do NOT pin the flag-OFF arm to `9e25b4e` — both arms stay on the frozen suite; pinning would smuggle the post-fix changes into the flag-ON delta and break the freeze.
>
> — `2026-07-22_68c24033.txt:74`

> mid-battery reconciliation gate that aborts before the flag-ON arm burns
>
> — `2026-07-22_68c24033.txt:63`

### <a id="d-284"></a>D-284 — Extraction v2 must carry a mechanical coverage gate: lines_read equals lines_total

`2026-07-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Diagnose v1's under-coverage as the absence of an enforced accounting step rather than prompt wording, and require any v2 design to carry a mechanical coverage gate whatever model runs it: each extraction unit reads its distilled file in full and emits {file, lines_total, lines_read, decisions:[...]} with a hard gate that lines_read equals lines_total, paging large files rather than sampling, and reporting coverage honestly because "an audited 80% beats a claimed 100%".

**Why.** Triage decisions were made under context pressure and the optimistic version was reported; without an enforced accounting step that failure reproduces on any model. Grep is no substitute for reading because design rationale is usually stated in ordinary prose containing none of the obvious keywords.

**Status.** adopted. S12 (2026-07-26): adopted by this record's own rebuild — PROTOCOL.md §5 G-COV requires lines_read == lines_total enforced by verify_extractions.py, Amendment 1 made the gate structural (whole file in the prompt), and preflight.py re-runs it; the v2 record was built under it (69/69 files, 100%).

**Cross-theme.** *depends-on* → [D-468](#d-468), [D-469](#d-469) — Siblings located. Ratification is not in the corpus: the gate was subsequently adopted by this rebuild's own PROTOCOL.md (G-COV, frozen 2026-07-25; made structural by Amendment 1), which postdates the distillation. Stays proposed within the record; surfaced to Ali with the proposed residue.

**Source.** `a:c4c4d030-07`, `a:c4c4d030-12`

> v1's failure wasn't a bad prompt — it was **no mechanical coverage gate**.
>
> — `2026-07-25_c4c4d030.txt:81`

> Why grep failed here: design rationale is usually stated in ordinary prose containing none of the obvious keywords.
>
> — `2026-07-25_c4c4d030.txt:69`

> - Report coverage honestly. An audited 80% beats a claimed 100%.
>
> — `2026-07-25_c4c4d030.txt:159`


## Infrastructure, Docker & compute

*186 primary source decisions → 55 entries; 3 not promoted (reasons in `docs/decision-record/entries/infrastructure.json`).*

### <a id="d-285"></a>D-285 — Accept per-merge latency as the price of semantic detection, document it, defer the mitigations

`2026-04-16 → 2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

**Decision.** The pipeline knowingly absorbs its per-merge latency rather than optimising it: Joern CPG generation on every merge, ~1.2–1.6 s per RM2 Docker invocation (~3–4 s per merge warm), rising to ~5.3 s/merge on Apple Silicon once R4a makes two `docker run` calls under Rosetta/QEMU `--platform linux/amd64`, and ~7.5–8 s/merge in default auto mode once R3 adds a third RM2 call. The costs are written into STATUS.md "Known costs" and a README latency note, with bypasses documented (`SEMANTIC_MERGE_BACKEND=mergiraf|git`, an env flag for R4a, YAML disable for R3), and three mitigations deferred: the R4b language short-circuit, parallelising the two `_detect_pair` calls, and a long-running persistent-JVM RM2 daemon.

**Why.** "While CPG generation introduces latency, this cost is justified because the entire purpose of the project is to catch semantic conflicts that all other layers miss." Container spin-up plus the Rosetta tax dominates while RM2 detection itself is sub-second, and the cost sits within the budget acknowledged when the container strategy was pinned — so it is flagged as known UX cost in the commit messages rather than engineered away, with the persistent-JVM container reserved as the post-MVP optimisation "if UX feedback complains". Accepting auto mode's cost before W5/S2 land is justified by having the dispatch infrastructure in place so those phases are pure additions, plus early classifier-correctness signal from production-style usage.

**Status.** adopted.

**Source.** `preA:pre-architecture-refmerge-05`, `preA:pre-rm2-integration-recon-13`, `preA:pre-commits-44`, `preA:pre-commits-47`, `preA:pre-commits-59` · Artifacts: `b37479c`, `8fcc44e`, `c099187`, `STATUS.md`, `README.md`

> While CPG generation introduces latency, this cost is justified because the entire purpose of the project is to catch semantic conflicts that all other layers miss.
>
> — `2026-04-16_pre-architecture-refmerge.txt:206`

> This sits within the budget acknowledged when D2 was pinned. Worth flagging in the M6-lite / R4b commit messages as known UX cost.
>
> — `2026-05-05_pre-rm2-integration-recon.txt:127`

### <a id="d-286"></a>D-286 — Bound external tool invocations: configurable timeouts everywhere, a cold-start budget for the driver

`2026-04-16 → 2026-04-25` · **abandoned** · `[recon]` · corroboration: both · confidence: low · actors: unclear

**Decision.** Two planned bounds on external tool cost: every external tool invocation (Mergiraf, RefactoringMiner, RefMerge, Joern) must have a configurable timeout, configured in `config/strategies.yaml`; and Phase S0 measures one `docker run` cold start against `java -jar` on a toy fixture, switching the driver to a native JAR if Docker adds more than ~500 ms per invocation — with Spork staying empirical-only and S2/S3/S4 skipped if both are too slow.

**Why.** No reason is recorded for the timeout rule. The cold-start threshold is argued from the driver running in a developer's critical path, so container startup cost matters in a way it does not in batch evaluation.

**Status.** abandoned. S12 (2026-07-26): neither bound was implemented as specified — config/strategies.yaml is an enablement list with no timeout keys (timeouts exist but are hardcoded per call site), the S0 cold-start measurement has no artifact (docs/plans/spork-driver-integration-recon.md does not exist), and the native-JAR option was mooted by the Docker-only standing rule. Dropped without a ruling.

**Source.** `preA:pre-architecture-refmerge-11`, `preA:pre-spork-driver-integration-12` · Artifacts: `config/strategies.yaml`, `docs/plans/spork-driver-integration-recon.md`

> **Timeout management**: All external tool invocations must have configurable timeouts
>
> — `2026-04-16_pre-architecture-refmerge.txt:878`

> The driver runs in a developer's critical path, so container startup cost matters in a way it doesn't in batch eval.
>
> — `2026-04-25_pre-spork-driver-integration.txt:104`

### <a id="d-287"></a>D-287 — All evaluated merge tools run from pinned merge-tools/<name> Docker images, never host PATH

`2026-04-21 → 2026-05-18` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: The standing rule itself is attributed to Ali (user decision, 2026-05-12, commit cafa71c); the derived tag/namespace/registry conventions are recorded without attribution, so sources disagree between 'ali' and 'unclear'. Attributed to Ali because the load-bearing rule is his.*

**Decision.** A CLAUDE.md standing rule requires every evaluated/integrated merge tool (Mergiraf, JDime, Spork, Mastery, Weave, RefactoringMiner) to be invoked through a Docker image in the `merge-tools/<name>` namespace, in both subprojects — the driver's backends and the comparison framework's adapters alike. Images carry an explicit version tag and never `:latest` (e.g. `merge-tools/mergiraf:0.17.0`, `merge-tools/refactoring-miner:2.4.0`, `merge-tools/spork:0.5.0` dual-tagged with the legacy `merge-tools/spork` so the empirical adapter is unaffected). One Dockerfile/image serves both subprojects per tool, and images are built locally and reproducible from the Dockerfile alone rather than pushed to a registry.

**Why.** The rule itself is recorded in CLAUDE.md without an argued justification; the supporting conventions are argued only as consistency and reproducibility — the image tag "matches `merge-tools/<tool>:<version>` convention from existing Dockerized tools", one Dockerfile/image avoids divergence between the framework and the driver, and keeping the image local is acceptable because "it is reproducible from the Dockerfile alone".

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-061](#d-061) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-205](#d-205) (see the reconciliation note there)

**Source.** `preA:pre-commits-30`, `preA:pre-mergiraf-integration-recon-10`, `preB:pre-mergiraf-integration-recon-06`, `preA:pre-rm2-integration-recon-06`, `preA:pre-rm2-integration-recon-17`, `preA:pre-mergiraf-integration-21`, `preB:pre-spork-driver-integration-04` · Artifacts: `CLAUDE.md`, `cafa71c`, `merge-tools/mergiraf:0.17.0`, `merge-tools/refactoring-miner:2.4.0`, `merge-tools/spork:0.5.0`, `merge-tool-comparison/docker/`

> CLAUDE.md: new standing rule. All evaluated/integrated merge tools
>
> — `2026-04-15_pre-commits.txt:395`

> **Docker-only invocation rule (project-wide).** Both M6-lite (`MergirafBackend`) and M1 (the comparison-framework adapter) invoke Mergiraf via `docker run merge-tools/mergiraf:0.17.0 ...` — never via host PATH binaries.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:16`

### <a id="d-288"></a>D-288 — git is the only tool exempt from Docker-only; host installs are ad-hoc dev convenience

`2026-04-21 → 2026-05-12` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: ali

*Actors note: One source attributes the carve-out to Ali's 2026-05-12 standing-rule decision; the other records it unattributed. Attributed to Ali on the strength of the first.*

**Decision.** `git` is the sole exception to the Docker-only invocation rule. A host install of a merge tool (specifically the `brew install mergiraf` done during M0) is permitted only as developer convenience for ad-hoc CLI queries (`mergiraf --help`, manual sanity checks) and is never a runtime dependency; the MergirafBackend must not invoke a host-PATH binary.

**Why.** Recorded as a scoping of the standing rule: the host binary exists only for ad-hoc queries and manual sanity checks during development, so it must not become a runtime dependency, while framework invocation stays Docker-only for reproducibility. The same carve-out appears in the commit-era CLAUDE.md rule (cafa71c), which is what confirms it survived the plan.

**Status.** adopted.

**Source.** `preA:pre-mergiraf-integration-03`, `preA:pre-mergiraf-integration-recon-11` · Artifacts: `CLAUDE.md`, `semantic_merge_driver/core/backends/mergiraf_backend.py`

> framework invocation is Docker-only; `brew install mergiraf` is optional dev convenience for ad-hoc CLI use (e.g., `mergiraf --help` queries during development), not a runtime dependency
>
> — `2026-04-21_pre-mergiraf-integration.txt:77`

> `git` itself is the only exception.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:16`

### <a id="d-289"></a>D-289 — M0 plan: pin Mergiraf 0.4.0, install natively via cargo, invoke through a temp git repo

`2026-04-22 → 2026-05-11` · **superseded** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

*Actors note: Sources disagree: the pin is attributed to Ali in one commit-era source, the native-install recommendation to Claude in one, and the remaining recon statements are unattributed. The record does not settle who owned the M0 plan as a whole.*

**Decision.** The M0 reconnaissance plan specified: pin Mergiraf 0.4.0 (the version upstream's run.sh pins), install it as a native binary via `cargo install --locked mergiraf --version 0.4.0` from a setup script / Makefile target with no Dockerfile and `docker_image: null` in tools.yaml, invoke it through Mergiraf's documented Git merge-driver convention (temp git repo + driver config + `git merge`) rather than the direct CLI, accepting ~100 ms of git setup per scenario for n=50–6000, and accept the resulting asymmetry against the Dockerised JDime/Spork/Mastery as a documented con. An earlier tool-evaluation note had argued for native-binary invocation on the same lines.

**Why.** Pinning 0.4.0 keeps the upstream published-numbers citation valid and gives a known-good Mergiraf to stabilise the rest of the MVP; native install mirrors upstream, which runs Mergiraf from `cargo install` with no Docker layer, and avoids the Rosetta/QEMU slowdown that hits Rust images on Apple Silicon (ISSUES #17) — with reproducibility preserved by pinning the version. The temp-repo overhead was judged acceptable at the planned scales, to be revisited only if profiling showed it dominating.

**Status.** superseded. Superseded by [D-298](#d-298) — Override M0: pin Mergiraf 0.17.0, install via Docker, invoke the standalone three-file CLI.

**Source.** `preB:pre-commits-33`, `preA:pre-mergiraf-integration-recon-04`, `preA:pre-mergiraf-integration-recon-06`, `preA:pre-mergiraf-integration-recon-14`, `preA:pre-tool-evaluation-findings-06` · Artifacts: `docs/plans/mergiraf-integration-recon.md`, `merge-tool-comparison/config/tools.yaml`, `merge-tool-comparison/ISSUES.md #17`

> we want the published-numbers cite to be valid, and we want a known-good Mergiraf to stabilise the rest of the MVP
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:189`

> **No Dockerfile required** — install via `cargo install` in a setup script or `Makefile` target. Asymmetry vs other tools is intentional. Document it.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:175`

### <a id="d-290"></a>D-290 — Weave ships as a Dockerized backend, overriding the plan's native-Rust invocation

`2026-04-22 → 2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: ali

*Actors note: One source attributes the override to Ali's directive; the other records the Dockerization unattributed.*

**Decision.** Weave is invoked via Docker as `merge-tools/weave:0.3.2`, built from a new `merge-tool-comparison/docker/weave/Dockerfile` (multi-stage clone + `cargo install --locked --path crates/weave-driver` at tag v0.3.2), not as a native binary. The plan's §1 facts table, Phase W1 and Appendix B `run_native` sketch are overridden, and SporkBackend and WeaveBackend become explicitly selectable entries in driver.py's BACKENDS dict.

**Why.** The CLAUDE.md standing rule requires merge tools to be invoked via Docker only, in the `merge-tools/<name>` namespace, and Ali directed integrating Weave "as other ones (mergiraf)"; the earlier "native, no Docker" W1 decision is explicitly described as stale.

**Status.** adopted. Supersedes: *Plan §1 / Phase W1 / Appendix B native `run_native` invocation of weave-driver (preA:pre-weave-integration-02)*.

**Cross-theme.** *supersedes* → [D-054](#d-054) — Mirror of backends-routing:3: preA:pre-weave-integration-02 consolidates into that entry. Rendered on both ends.

**Source.** `preA:pre-execution-sequence-20`, `preA:pre-weave-integration-01` · Artifacts: `merge-tool-comparison/docker/weave/Dockerfile`, `merge-tools/weave:0.3.2`, `semantic_merge_driver/core/backends/weave_backend.py`, `semantic_merge_driver/core/driver.py`

> That is **overridden** by the CLAUDE.md standing rule
>
> — `2026-04-25_pre-weave-integration.txt:26`

> Weave is newly Dockerized as `merge-tools/weave:0.3.2`, overriding the stale "native, no Docker" W1 decision
>
> — `2026-04-22_pre-execution-sequence.txt:109`

### <a id="d-291"></a>D-291 — Invoke RefactoringMiner through a DirPairMain Java wrapper in Docker, built from the released ZIP

`2026-04-22 → 2026-05-05` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** RefactoringMiner is integrated via Path D: a custom `DirPairMain.java` wrapper compiled inside a Docker image, calling `GitHistoryRefactoringMiner.detectAtDirectories`, rather than the CLI-with-throwaway-git approach; the Dockerfile pulls `RefactoringMiner-<version>.zip` from GitHub releases rather than building from source; and the existing `pyrefactoringminer` Python binding is rejected, deferred indefinitely.

**Why.** RM 2.4.0's CLI is commit-oriented with no directory-pair entry point, so the Java API is the only way to run detection on raw directory pairs; the wrapper also saves ~1 s per call against the CLI throwaway-git approach. Pulling the released ZIP is simpler than building from source and matches the existing "trust upstream artifact" pattern, and wrapper-via-Docker was chosen for tech-stack consistency with JDime/Spork/Mastery.

**Status.** adopted.

**Source.** `preA:pre-execution-sequence-12`, `preA:pre-rm2-integration-recon-03`, `preA:pre-rm2-integration-recon-04`, `preA:pre-rm2-integration-recon-14` · Artifacts: `merge-tool-comparison/docker/refactoring_miner/DirPairMain.java`, `merge-tool-comparison/docker/refactoring_miner/Dockerfile`, `docs/plans/rm2-integration-recon.md`, `1f76a00`, `5e687ce`, `713b337`

> no directory-pair entry point. The Java API (`GitHistoryRefactoringMiner.detectAtDirectories`) is the only way to invoke detection on raw directory pairs
>
> — `2026-05-05_pre-rm2-integration-recon.txt:19`

> None used — wrapper-via-Docker chosen for tech-stack consistency with JDime/Spork/Mastery. Python binding deferred indefinitely.
>
> — `2026-05-05_pre-rm2-integration-recon.txt:144`

### <a id="d-292"></a>D-292 — Whether Joern and the JVM merge tools can share one Java 17 runtime in the driver is unresolved

`2026-04-22 → 2026-04-25` · **open** · `[recon]` · corroboration: single-pass · confidence: medium · actors: unclear

*Actors note: One source attributes the open question to Claude; the other records the shared-17-LTS choice unattributed, so the record does not settle ownership.*

**Decision.** The intent is a single shared Java 17 LTS runtime inside `semantic_merge_driver` — Joern needs 17+, Spork/Spoon works on 11+, so 17 LTS is the stated safe overlap — but confirming that Joern and RM 2.0 can actually share one Java 17+ runtime (rather than having incompatible JVM requirements) was left as an open question, deferred to a future RM 2.0 integration plan and to Phase S0.

**Why.** RM adds a JVM dependency to the driver runtime; the marginal cost is small given Joern already needs a JVM — but only if they can share the runtime, which is why the question is flagged rather than assumed.

**Status.** open. Never resolved in the record. It would be settled by the driver's runtime setup in semantic_merge_driver (which JVM(s) are actually installed/invoked) or by the S0 / RM 2.0 integration recon output.

**Source.** `preB:pre-tool-evaluation-findings-22`, `preA:pre-spork-driver-integration-18` · Artifacts: `semantic_merge_driver/`

> **Shared JVM runtime** — can Joern and RM 2.0 share a Java 17+ runtime in `semantic_merge_driver`, or do they have incompatible JVM requirements?
>
> — `2026-04-22_pre-tool-evaluation-findings.txt:334`

> Joern needs Java 17+; Spork/Spoon works on 11+. Shared 17 LTS is the safe choice.
>
> — `2026-04-25_pre-spork-driver-integration.txt:202`

### <a id="d-293"></a>D-293 — Hard-pin Weave v0.3.2 and drop the adapter rather than fix forward on v0.4

`2026-04-25` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: unclear

**Decision.** Weave is hard-pinned at v0.3.2 — version locked in the brew/cargo install and recorded in the adapter's comment header — and stays pinned even though upstream latest is v0.3.3, until a fresh reconnaissance validates a bump. If a breaking v0.4.x ships, the policy is to drop the adapter, not adapt to it.

**Why.** Weave is 2.5 months old with a one-person-dominated commit graph, so immaturity breaking the CLI contract mid-project is rated a high-likelihood risk; hard pinning plus a drop-don't-fix-forward rollback policy means a broken v0.4 delays nothing — at worst the Weave row goes stale.

**Status.** adopted.

**Source.** `preA:pre-weave-integration-05`, `preB:pre-weave-integration-05` · Artifacts: `merge-tools/weave:0.3.2`, `merge-tool-comparison/src/tools/weave.py`

> Hard pinning + a "drop, don't fix forward" rollback policy means a broken v0.4 delays nothing
>
> — `2026-04-25_pre-weave-integration.txt:270`

> **Pin hard.** Weave is 2.5 months old with a one-person-dominated commit graph.
>
> — `2026-04-25_pre-weave-integration.txt:90`

### <a id="d-294"></a>D-294 — Force a clean CWD per Weave invocation so a stray .weave.toml cannot poison batch evaluation

`2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Phase W0 checks whether Weave reads `.weave.toml` from the current working directory; if so, the adapter runs every invocation with a clean CWD (the temp dir).

**Why.** A surprise `.weave.toml` config picked up from the CWD during batch evaluation would poison results.

**Status.** adopted. S12 (2026-07-26): implemented — src/tools/weave.py:39-53 runs every invocation inside a fresh tempfile.TemporaryDirectory() workspace, so a stray .weave.toml in any inherited CWD cannot poison batch evaluation.

**Source.** `preA:pre-weave-integration-16` · Artifacts: `merge-tool-comparison/src/tools/weave.py`

> W0 checks for this; adapter uses a clean CWD (e.g. the temp dir) for each invocation.
>
> — `2026-04-25_pre-weave-integration.txt:242`

### <a id="d-295"></a>D-295 — Build the RefactoringMiner image on eclipse-temurin:17-jdk for Joern compatibility

`2026-05-05 → 2026-05-06` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The RefactoringMiner wrapper image uses `eclipse-temurin:17-jdk` as its base — not the JDK 11 minimum that RM 2.4.0's bytecode would allow, nor the JDK 21 base RM 3.0.13 requires.

**Why.** RM 2.4.0 ships Java 11 bytecode (class file v55), which JDK 17 reads fine, and JDK 17 matches Joern's 17+ requirement; compiling the wrapper against 3.0.13's lib on JDK 17 fails with `class file has wrong version 65.0, should be 61.0`, so the version pin forces the base image. The 17-jdk base is confirmed to have landed by the rollback commit recorded in [D-297](#d-297) (5e687ce, 21-jdk → 17-jdk) and by the transcript-era use of a pinned `eclipse-temurin:17-jdk` for compile checks.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-recon-05`, `preA:pre-rm2-vs-rm3-differences-03` · Artifacts: `merge-tool-comparison/docker/refactoring_miner/Dockerfile`

> **`eclipse-temurin:17-jdk`** | RM 2.4.0 ships Java 11 bytecode (class file v55) — JDK 17 reads it fine and matches Joern's 17+ requirement.
>
> — `2026-05-05_pre-rm2-integration-recon.txt:21`

> JDK 11+ — JDK 17 used here for Joern compatibility
>
> — `2026-05-06_pre-rm2-vs-rm3-differences.txt:36`

### <a id="d-296"></a>D-296 — First RefactoringMiner pin: 3.0.13 on eclipse-temurin:21-jdk with dual-mode Path D tagging

`2026-05-05` · **superseded** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** RefactoringMiner is pinned at 3.0.13 (the last Java-only release) on `eclipse-temurin:21-jdk` behind the thin DirPairMain.java Docker wrapper; R1 runs dual-mode tagging (Path D) and R4a uses file-level detection at runtime.

**Why.** The F-harness on n=10 measured 75.0% file-level recall against project-level, which sits in the 50–80% bracket that selects Path D.

**Status.** superseded. Superseded by [D-297](#d-297) — Roll the RefactoringMiner pin back to 2.4.0, dropping the JDK base to 17 with zero Java edits.

**Source.** `preA:pre-commits-21` · Artifacts: `713b337`, `merge-tool-comparison/tools/rm2_fharness.py`, `merge-tool-comparison/docker/refactoring_miner/`

> Pins RefactoringMiner 3.0.13 (last Java-only release) on eclipse-temurin:21-jdk
>
> — `2026-04-15_pre-commits.txt:242`

### <a id="d-297"></a>D-297 — Roll the RefactoringMiner pin back to 2.4.0, dropping the JDK base to 17 with zero Java edits

`2026-05-06` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** The RM pin rolls back from 3.0.13 to 2.4.0 (last 2.x release) and RM 3.x is declared out of thesis scope; Path D selection is unchanged. The rollback is implemented entirely as (1) Dockerfile `RM_VERSION` plus base-image edits (`eclipse-temurin:21-jdk` → `17-jdk`) and (2) an image-tag substitution in `rm2_fharness.py`, leaving `DirPairMain.java` untouched — the pattern future version swaps follow. Two recon-doc errors are corrected as a side effect: "RM 2.4.0 compiles to Java 17" becomes "ships Java 11 bytecode (v55)", and "RM 2.4.0's CLI lacks `-bd`" becomes both versions having identical CLI flag sets with no directory-pair flag.

**Why.** 2.4.0 matches the plan's "2.4+ recommended" guidance, and 3.0.x is incremental Java-only maintenance over 2.x — new APIs but no thesis-relevant capability — while 3.1.x adds multi-language detection. RM 2.4.0's Java 11 bytecode means 17-jdk suffices. All four wrapper imports exist with identical signatures in both versions, and `detectAtDirectories(Path,Path,Handler)` plus the `toJSON()` schema are unchanged, so the same source compiles against either lib. The corrected recon statements would otherwise have affected R1's interpretation of the version pin.

**Status.** adopted. Supersedes: [D-296](#d-296) — First RefactoringMiner pin: 3.0.13 on eclipse-temurin:21-jdk with dual-mode Path D tagging.

**Cross-theme.** *depended on by* ← [D-089](#d-089) (see the reconciliation note there)

**Source.** `preA:pre-commits-23`, `preA:pre-commits-24`, `preA:pre-rm2-vs-rm3-differences-05` · Artifacts: `5e687ce`, `docs/plans/rm2-vs-rm3-differences.md`, `merge-tool-comparison/docker/refactoring_miner/Dockerfile`, `merge-tool-comparison/tools/rm2_fharness.py`

> is out of thesis scope — 3.0.x is incremental Java-only maintenance over
>
> — `2026-04-15_pre-commits.txt:256`

> source compiles **without modification** against either version's lib
>
> — `2026-05-06_pre-rm2-vs-rm3-differences.txt:116`

### <a id="d-298"></a>D-298 — Override M0: pin Mergiraf 0.17.0, install via Docker, invoke the standalone three-file CLI

`2026-05-12` · **adopted** · `[recon]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: Five sources attribute the override to Ali (user decision 2026-05-12); two commit/recon sources record it unattributed.*

**Decision.** Ali overrode M0 on 2026-05-12: Mergiraf is pinned at 0.17.0 (image `merge-tools/mergiraf:0.17.0`), installed and invoked through a multi-stage Docker image (`rust:1-bookworm` builder → `debian:bookworm-slim` runtime, ARG-driven MERGIRAF_VERSION, `ENTRYPOINT ["mergiraf", "merge"]`) built by `make docker-build`, and invoked as a standalone three-file CLI — `docker run --rm -v <workdir>:/workspace merge-tools/mergiraf:0.17.0 /workspace/base /workspace/ours /workspace/theirs -p <path>`, capturing stdout and counting `<<<<<<<` markers. The M0 temp-git-repo plumbing sketch is kept only below an OBSOLETE marker for traceability, and write-ups citing upstream numbers must carry the version-skew caveat.

**Why.** Framework consistency was chosen over mirroring upstream: one image per tool preserves the reproducibility story, at the cost of a ~5–15 min multi-stage cargo build under QEMU per Dockerfile change (accepted because the image caches between builds). The version bump to 0.17.0 was additionally justified by the dev machine having no Rust toolchain while Homebrew bottles 0.17.0 in seconds. Both stages stay on bookworm because `rust:1-slim` defaults to trixie/GLIBC 2.39 and broke against bookworm's GLIBC 2.36 on the first attempt. The consequence — upstream's numbers were produced against 0.4.0 — is recorded as a threat to validity.

**Status.** adopted. Supersedes: [D-289](#d-289) — M0 plan: pin Mergiraf 0.4.0, install natively via cargo, invoke through a temp git repo.

**Cross-theme.** *depended on by* ← [D-061](#d-061) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-136](#d-136), [D-384](#d-384) — Located by content: the 0.17.0-pinned vs 0.4.0-published version mismatch is the caveat attached to the cite-upstream proposal, and the THREATS document owns the recording convention.

**Source.** `preA:pre-commits-31`, `preA:pre-mergiraf-integration-01`, `preA:pre-mergiraf-integration-02`, `preA:pre-mergiraf-integration-recon-05`, `preA:pre-mergiraf-integration-recon-07`, `preB:pre-commits-39`, `preB:pre-mergiraf-integration-recon-11` · Artifacts: `cafa71c`, `merge-tool-comparison/docker/mergiraf/Dockerfile`, `merge-tool-comparison/Makefile`, `merge-tools/mergiraf:0.17.0`, `docs/plans/mergiraf-integration-recon.md`

> User chose Docker for framework consistency (2026-05-12) — multi-stage cargo build inside `rust:1-slim` under QEMU takes ~5-15min on M-series. One-time cost per Dockerfile change; image caches between builds.
>
> — `2026-04-21_pre-mergiraf-integration.txt:256`

> User chose framework-consistency over upstream-mirror — Mergiraf gets a `docker/mergiraf/Dockerfile` like JDime/Spork/Mastery, not a native cargo install.
>
> — `2026-05-11_pre-mergiraf-integration-recon.txt:14`

### <a id="d-299"></a>D-299 — Docker-only rule covers evaluated merge tools, not framework tooling, Joern, or one-off renders

`2026-05-14 → 2026-07-16` · **adopted** · `[mixed]` · corroboration: mixed · confidence: medium · actors: claude

*Actors note: The transcript-era scoping arguments are Claude's; the plan-era statements of the same carve-out are recorded unattributed, so sources split between 'claude' and 'unclear'.*

**Decision.** The Docker-only standing rule is read as applying to tools under evaluation, not to everything the project runs. Consequences: the comparator's Tier-3 AST normalization runs tree-sitter-java in-process in Python with no container, pinned instead via `tree-sitter>=0.21,<1.0` / `tree-sitter-java>=0.21,<1.0` in pyproject.toml; a one-off mermaid diagram render uses the upstream `minlag/mermaid-cli` image directly, outside the `merge-tools/` namespace; and the tune runner's PATH-only Joern check is ruled in scope-compliant because Joern is not one of the rule's enumerated merge tools.

**Why.** The rule exists to version-pin and hermetically isolate the tools being measured; the comparator's preprocessing layer is framework infrastructure, not a tool under evaluation (normalize_content was already not Dockerized). google-java-format was Dockerized because of its JAR+JVM distribution and stdin→stdout CLI shape, properties a PyPI wheel library (<10 ms per call) does not share — so the hosting and pinning mechanism should follow the distribution form of the artifact (JAR+JVM → Docker; PyPI wheel → pyproject pin). The mermaid render is scratch output, not a pipeline dependency; Joern is simply not one of the enumerated tools.

**Status.** adopted.

**Source.** `preA:pre-commits-65`, `preA:pre-comparator-3b-ast-normalize-07`, `preA:pre-comparator-3b-ast-normalize-08`, `a:20b53f98-26`, `b:acf7e1d0-14`, `a:acf7e1d0-sub-sub-agent-aaed4d-03` · Artifacts: `CLAUDE.md`, `6cfcdfc`, `merge-tool-comparison/src/evaluation/ast_normalize.py`, `merge-tool-comparison/pyproject.toml`, `merge-tool-comparison/tools/detector_tune_run.py`

> The standing rule applies to **evaluated merge tools** (Mergiraf, JDime, Spork, Mastery, RefactoringMiner) — things being measured by the framework.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:147`

> The line-74 comment "Joern check is harmless: PATH-only" refers to Joern, which is not one of the rule's enumerated merge tools (Mergiraf/JDime/Spork/Mastery/Weave/RefactoringMiner), so it is out of scope of the Docker-only rule.
>
> — `2026-07-16_acf7e1d0_sub-agent-aaed4d.txt:32`

### <a id="d-300"></a>D-300 — Keep Tier-3 AST normalize off by default in tests and cache it on the post-gjf hash

`2026-05-14` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** conftest.py sets `MERGE_COMPARATOR_AST_NORMALIZE=off` by default alongside the existing `MERGE_COMPARATOR_FORMATTER=off`, so unit tests must opt into Tier 3; and the comparator gains `_ast_cache: dict[str, str | None]` mirroring `_format_cache`, keyed on the sha256 of the gjf-normalized (Tier-2 output) text rather than the raw input.

**Why.** Defaulting off keeps the test suite Docker-free and parser-fast, mirroring M3.5's formatter-off default. Keying the cache on post-gjf text lets already-cached gjf results be reused and the AST result cached on top, saving redundant tree-sitter parses across the n=50 run, since Tier 3 always runs on Tier 2's output.

**Status.** adopted. S12 (2026-07-26): implemented exactly — tests/conftest.py:8-9 sets both MERGE_COMPARATOR_FORMATTER=off and MERGE_COMPARATOR_AST_NORMALIZE=off, and comparator.py carries _ast_cache (:35) 'keyed by sha256 of the gjf-normalized content' (:32), mirroring _format_cache as specified.

**Source.** `preA:pre-comparator-3b-ast-normalize-05`, `preA:pre-comparator-3b-ast-normalize-06` · Artifacts: `merge-tool-comparison/tests/conftest.py`, `merge-tool-comparison/src/evaluation/comparator.py`

> also default `MERGE_COMPARATOR_AST_NORMALIZE=off` so the test suite stays Docker-free and parser-fast (mirrors M3.5's `MERGE_COMPARATOR_FORMATTER=off` default)
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:107`

> keyed by sha256 of the *gjf-normalized* input (not the raw input)
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:135`

### <a id="d-301"></a>D-301 — Cache expensive container work per unit, make it resumable, and batch to amortize startup

`2026-05-18 → 2026-06-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

*Actors note: Sources split: the caching/resumability requirement is stated in Ali's briefs (20b53f98-04, 7b3b2669-06) while the invocation design and batching judgment are Claude's. Recorded as joint rather than taking a majority.*

**Decision.** Expensive containerised work is cached per scenario with a `--force` re-extract flag, following the existing schesch_loader scenario-caching pattern: the RM2 tagger mirrors R4a's `_detect_pair` Docker semantics at one container invocation per pair (base→ours, base→theirs — ~100 calls, one-time, cached) rather than importing the driver's classifier or batching many pairs per container; project-level tagging caches per scenario so an interrupted run resumes; the javac compile-check tool batches each chunk of files into a single `eclipse-temurin:17-jdk` container and is resumable per chunk; and new harnesses (whole_driver_eval.py) are built to mirror detect_validate.py's resumable cache, preflight and G0 guard. Batching one container over many pairs is recorded as future work.

**Why.** RM2 Docker invocations cost ~2.5 s each on the Apple-Silicon/QEMU host, so results must be cached and only recomputed on demand; categorization needs only the two pairings, and batching only matters at full-Schesch scale (6045×), so per-scenario calls are fine for n=50 with caching and `--force`. Chunk-batching the compile checks exists specifically to amortize QEMU container startup.

**Status.** adopted.

**Source.** `a:20b53f98-04`, `a:20b53f98-10`, `b:7b3b2669-06`, `a:92a3e464-08`, `a:fb0fa5c5-02` · Artifacts: `merge-tool-comparison/tools/rm2_tag.py`, `merge-tool-comparison/tools/taxonomy_compile_checks.py`, `tools/whole_driver_eval.py`, `merge-tool-comparison/src/data/schesch_loader.py`

> - Cache expensive RM2 output per scenario; support --force re-extract, mirroring
>
> — `2026-05-18_20b53f98.txt:75`

> **Batching** one container over many pairs is a real optimization but only matters at full-Schesch (6045×); for n=50 cached + `--force`, per-scenario calls are fine. Flag batching as future-work.
>
> — `2026-05-18_20b53f98.txt:140`

### <a id="d-302"></a>D-302 — Treat meaningful runs as unattended background jobs, not interactive sessions

`2026-05-20 → 2026-06-25` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** The 5–10 minute interactive budget for corpus expansion is abandoned: real runs are background jobs. Operationally that means launching detached with output redirected to a log file on the host (`reports_whole_driver/full_run.log`) so the user can tail it independently rather than the output streaming only into the assistant's SSH session; stopping double-backgrounded `nohup` + run_in_background launches in favour of properly harness-tracked background tasks; attaching `caffeinate -i -w <pid>` to a local overnight run so macOS will not idle-sleep for exactly the job's duration (lid open, Claude Code session and Docker Desktop running); and monitoring remote runs via SSH `tail -f`, EC2 Instance Connect from a browser or phone, and on-request reports, with CloudWatch Logs ruled out.

**Why.** Cloning dominates wall-clock and the Rosetta/QEMU amd64 emulation tax makes each tool run ~10 s, so "your earlier 5–10 min budget can't coexist with meaningfully more data on this hardware". A double-backgrounded process is not harness-tracked, so no real completion signal arrives for a ~2 h run, and the resumable cache makes a restart nearly free. Sleep does not lose work (the run resumes from the commit-keyed cache) but stretches the ETA to awake-time only. CloudWatch is skipped because it needs a CloudWatch agent plus an IAM role the EC2-only IAM user cannot create — not worth the extra IAM step for a one-off ~10 h run.

**Status.** adopted. Supersedes: *5–10 minute interactive budget for corpus expansion*.

**Source.** `b:e1df1610-03`, `a:bfc672b4-27`, `b:fb0fa5c5-15`, `b:fb0fa5c5-28`, `a:fb0fa5c5-16` · Artifacts: `STATUS.md`, `reports_whole_driver/full_run.log`, `reports_detection/full/raw_results.json`

> real expansion is a **background job**, not interactive.
>
> — `2026-05-20_e1df1610.txt:685`

> I attached `caffeinate -i -w 24406` to the scoring process — the Mac won't idle-sleep while it runs, and the hold releases itself the moment the run exits.
>
> — `2026-06-11_bfc672b4.txt:541`

### <a id="d-303"></a>D-303 — Operate AWS under least privilege with an explicit go-ahead gate and a $20 budget backstop

`2026-05-20 → 2026-07-04` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Four sources record Claude proposing and adopting the guardrails; one (the hours × $0.42 rule) appears as a standing rule in Ali's kickoff prompt.*

**Decision.** Resource-consuming or paid actions require Ali's explicit authorization: repository cloning (network + GBs) is not kicked off without his go-ahead, and nothing that costs money or is irreversible — launching or terminating instances — happens without showing the exact command and the hourly cost first, with the estimate stated as hours × $0.42 at launch time ("~5 h × $0.42/h ≈ $2, cap $3" was held at the gate until Ali replied "launch"). AWS access runs through a scoped `claude-p2` IAM user with EC2-only (plus optional S3) permissions, MFA on root and root unused; `aws configure` is run by Ali, keys are never pasted into the conversation and Claude never reads `~/.aws/credentials`. A monthly $20 AWS Budgets cost budget is created as a backstop.

**Why.** EC2-only permissions bound the blast radius — they cannot touch billing, IAM or other services — and keeping the secret in `~/.aws` means it never enters the conversation transcript. Launching paid infrastructure is the user's to authorize. The budget alarm is "the #1 first-timer safeguard against a forgotten-running-instance bill", but it is explicitly a lagging safety net: AWS cost data lags ~a day, so it fires after the threshold is crossed and terminating the instance is the real control.

**Status.** adopted.

**Source.** `a:e1df1610-34`, `a:fb0fa5c5-14`, `a:fb0fa5c5-15`, `b:fb0fa5c5-24`, `a:8740dbd3-22` · Artifacts: `deploy/aws/CLI-DEPLOY.md`

> **I confirm before anything that costs money or is irreversible** (launching/terminating instances) — I'll show you the exact command and the hourly cost first, every time.
>
> — `2026-06-24_fb0fa5c5.txt:583`

> **It's a safety net, not real-time.** AWS cost data lags ~a day, so a budget alert fires *after* you've crossed the threshold
>
> — `2026-06-24_fb0fa5c5.txt:966`

### <a id="d-304"></a>D-304 — Account for the Apple Silicon emulation tax by measurement, and never promise a native speedup

`2026-05-25 → 2026-07-04` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Three sources attribute the reasoning to Claude; one (the ETA rule) appears in Ali's kickoff prompt, which restates Claude's earlier finding.*

**Decision.** The Rosetta/QEMU tax is treated as a measured quantity, not an assumption. Concretely: local Docker workloads are serialized (the comparator run is held until RM2 tagging finishes) because both at once contend on the single amd64-emulated daemon; the estimate that native x86_64 on AWS would cut the ~20 h run to ~8–12 h is withdrawn, since per-file time on the instance is ~85 s (77–93 s) against the local ~80 s; AWS ETAs are budgeted from dataset size at ~60–90 s/file as Joern-bound with an explicit instruction not to promise speedups; and R0's "~3× file-level Docker cost" expectation for project-level tagging is corrected as Rosetta tax rather than RM2 work, the full n=50 run taking 3.8 minutes natively.

**Why.** Measured per-file timings on the instance matched the local ones, showing Docker emulation is a small fraction of each merge while Joern — already native on the Mac — dominates: "I was wrong about the speedup." Where the work genuinely is containerised and emulated, contention on the single emulated daemon is real, which is why those workloads are serialized rather than run in parallel.

**Status.** adopted. Supersedes: *estimate that native x86_64 would land the run at ~8–12 h*; *R0 expectation of ~3× file-level Docker cost for project-level tagging*.

**Source.** `a:e1df1610-13`, `a:fb0fa5c5-17`, `a:8740dbd3-21`, `a:7b3b2669-12` · Artifacts: `deploy/aws/CLI-DEPLOY.md`

> Honest implication: **the full run is still ~20 h on AWS, not the 8–12 h I optimistically estimated.** I was wrong about the speedup.
>
> — `2026-06-24_fb0fa5c5.txt:887`

> is NOT faster than Apple Silicon — do not promise speedups).
>
> — `2026-07-03_8740dbd3.txt:168`

### <a id="d-305"></a>D-305 — Probe images and checksum transfers before running anything that depends on them

`2026-05-25 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: The lessons and practices are Claude's; three sources are the same rules restated in Ali's kickoff prompts, so attribution splits between claude and ali.*

**Decision.** Nothing expensive runs on unverified inputs. Before launching a tagging or multi-tool run, the required Docker images are checked present, and on a fresh x86 instance every tool image (mergiraf, refactoring-miner, joern, and the shipped ones) is validated with a live probe. Files are shipped with `cat file | ssh host 'cat > path'` and md5/sha256-verified on both sides before any dependent run — bare scp is not used — and results are collected back the same way, with counts and checksums verified and the change confirmed strictly additive before overwriting local `data/scenarios/`. The round-2 attempt whose scp silently failed was killed, its poisoned output directory wiped, and the run restarted from a fresh migration with the code checksum-verified on the box.

**Why.** "Probe, don't assume": a missing image would silently tag everything `NONE`, and any image built on Apple Silicon without `--platform linux/amd64` dies silently with exec format error on x86 (the gjf incident). A bare scp in the session sandbox can silently degrade to a mangled local cp — which is exactly what happened: ~130 files were recomputed with round-1 code under a round-2 label, invalid data that would have quietly reproduced round-1's numbers. The image check also "protects a ~13-min run from silent all-crash rows".

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-172](#d-172) — other_uid a:fb0fa5c5-32 is cited there: the silently-dead arm64 gjf image and withdrawn local-timeout explanation are the incident that produced the probe-don't-assume rule.

**Cross-theme.** *depends-on* → [D-172](#d-172), [D-261](#d-261) — other_uid a:fb0fa5c5-34's 'validate a scoring environment by reproducing committed canonical numbers' rule is gates-freeze/[D-261](#d-261); the incident entry as in infrastructure:1.

**Source.** `a:e1df1610-14`, `a:8740dbd3-06`, `a:8740dbd3-05`, `a:fb0fa5c5-40`, `a:7b3b2669-05`, `a:7b3b2669-07`, `a:68c24033-06`, `a:fb0fa5c5-32`, `a:fb0fa5c5-34` · Artifacts: `deploy/aws/CLI-DEPLOY.md`, `bundle_sd8.sh`, `provision_sd8.sh`, `merge-tool-comparison/data/scenarios/`

> Probe, don't assume: any image built on Apple Silicon without
>
> — `2026-07-03_8740dbd3.txt:181`

> the first round-2 attempt's file transfer silently failed, so ~130 files were being recomputed with round-1 code under a round-2 label — invalid data that would have quietly reproduced round-1's numbers
>
> — `2026-06-24_fb0fa5c5.txt:2178`

### <a id="d-306"></a>D-306 — Clone blobless with a per-clone timeout, and harden the reuse path instead of predicting cost

`2026-05-26 → 2026-07-08` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: The switch to blobless cloning under a timeout was Ali's directive; the rejected size predictor, the withdrawn attributions and the robustness fixes are Claude's.*

**Decision.** `tools/select_materialize.py` clones with `--filter=blob:none --no-checkout` under a per-clone timeout (120 s default, `CLONE_TIMEOUT`), skipping and logging stragglers, with the candidate list expanded ~20% so failures still yield 60 repos; the stalled Spork job resumed from 21 to 60 on the new code. Predicting clone cost from repo-size metadata is rejected, and the earlier attribution of the slowdown to `lintool/clueweb` is withdrawn (the GitHub API shows it at 2 MB). Reusing blobless clones later required two further fixes: injecting `safe.directory=*` into git subprocess environments rather than changing global git config, and guarding per-file extraction so a transient promisor blob-fetch failure skips and counts that merge for retry on resume instead of raising an uncaught ValueError — with the "dubious ownership" diagnosis of those crashes withdrawn.

**Why.** Only 4 files from 4 commits are read, so fetching every blob and checking out the whole tree is wasted work; and since clone time depends on history depth, blob count, network and throttling — the local Reaper `size` being a stale 2017 source metric that cannot predict renamed/404 repos that hang with no size at all — "a **timeout (bound)** is the reliable fix, and **blobless clone** is the real speedup". The ownership diagnosis was retracted because ownership checked out as the current user and `git show` (which does trigger lazy fetch) succeeded where GitPython's `data_stream` did not; an uncaught ValueError from a transient failure was killing the whole run.

**Status.** adopted. Supersedes: *sequential full git clone with no timeout in select_materialize.py*.

**Source.** `a:e1df1610-22`, `a:e1df1610-23`, `a:e1df1610-24`, `a:92a3e464-09`, `a:92a3e464-10`, `a:92a3e464-11` · Artifacts: `merge-tool-comparison/tools/select_materialize.py`, `8504d74`

> yes, add timeout but expand list for 20% so if a lot of fails we still get 60 repos also switch to blobless/no-checkout cloning
>
> — `2026-05-20_e1df1610.txt:1090`

> which is why a **timeout (bound)** is the reliable fix, and **blobless clone** is the real speedup
>
> — `2026-05-20_e1df1610.txt:1086`

### <a id="d-307"></a>D-307 — Lift the per-strategy triple parse into a shared-CPG component as the one data-demanded refactor

`2026-06-11` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Proposed: hoist the per-strategy base/ours/theirs triple-parse pattern into shared infrastructure — one parse per version, all queries against it — replacing ~15 parses per file, identified as the only structural refactor the Stage-C data demands.

**Why.** Every surviving detector re-implements the same base/ours/theirs capture and re-parses the same three files (five CPG builds per version per file); the refactor is both an architecture cleanup and the ~5× latency win that matters for interactive `git merge` as opposed to CI, and it would make the zero-yield detectors nearly free to keep.

**Status.** superseded. S12 (2026-07-26): declined the same day it was proposed — the adopted skip decision (scope-architecture: [D-023](#d-023), D-023) ruled the rework unnecessary after the pilot came in far under the abort threshold; no shared-CPG component exists and the per-strategy parse pattern remains. Cross-theme superseder, so superseded_by stays null; see cross_theme_resolutions.json extra_edges.

**Cross-theme.** *depended on by* ← [D-098](#d-098) (see the reconciliation note there)

**Cross-theme.** *declined-by* → [D-023](#d-023) — Observed during reconciliation, no flag raised it: the shared-CPG refactor proposal (proposed, 2026-06-11) was considered and skipped the same day on pilot evidence ('far under the abort threshold'). Statuses left untouched — whether the proposal should read abandoned is part of the proposed-residue call for Ali.

**Source.** `a:bfc672b4-25` · Artifacts: `semantic_merge_driver/`

> The natural refactor (and the plan's §8 note) is to lift this into shared infrastructure: one parse per version, all queries against it. That's both an architecture cleanup and the ~5× latency win
>
> — `2026-06-11_bfc672b4.txt:484`

### <a id="d-308"></a>D-308 — Watch runs by process exit and anomalies only, and use the wait to build downstream tooling

`2026-06-11 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Background runs are watched by a harness-tracked waiter that fires on the process's terminal states (completion, timeout, crash) rather than by blind polling or by grepping a log for a completion string — the provision wait-loop that grepped for "provision done" against the actual "provision complete." was killed and replaced with a process-exit monitor. Mid-run monitors are filtered to what warrants attention (control-side flags, UNANALYZABLE verdicts, G0 aborts), with positive-side flags accumulating silently in the cache for end-of-run adjudication from summary.txt; an early-alarm watcher that trips on the first flag lets tuning start before shards complete, and progress is read from shard caches because `tail` pipes buffer until completion. Waiting time is spent writing the deterministic downstream scripts so they are ready the moment results land.

**Why.** A grep-based loop matching the wrong string would never fire. Positive-side flags are the detector doing its job — expected events that only interrupt — so only anomalies warrant eyes mid-run. A harness-tracked waiter notifies on terminal states rather than requiring blind polling, and the early alarm exists so tuning can start before full completion. Writing `taxonomy_g1_eval.py` and `taxonomy_spotcheck_ui.py` during batch processing means results can be evaluated immediately on landing.

**Status.** adopted. Supersedes: *log-string grep wait-loop for provision.sh*.

**Source.** `a:8740dbd3-26`, `a:9e4b6896-34`, `b:82dd479f-14`, `a:bfc672b4-31`, `b:788e483b-02` · Artifacts: `deploy/aws/provision.sh`, `summary.txt`, `taxonomy_g1_eval.py`, `taxonomy_spotcheck_ui.py`, `run.log`

> I'll re-arm it filtered to what actually needs eyes mid-run: control-side flags (R1 damage), UNANALYZABLE verdicts, and G0 aborts.
>
> — `2026-06-11_bfc672b4.txt:451`

> Provisioning monitor rearmed (waits on process exit, not a log string).
>
> — `2026-07-03_8740dbd3.txt:259`

### <a id="d-309"></a>D-309 — Verify HTML deliverables over a localhost static server, and link to them by http not file

`2026-06-20 → 2026-07-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Static HTML deliverables are verified in the preview browser through a static server: a new static-server launch configuration is added for the `full` directory alongside the existing one, serving on localhost:8742. Presentation links to the gate UIs use `http://localhost:8744/8745/8746` URLs matching the repo's existing `.claude/launch.json` server entries instead of `file://` paths, with a pre-talk server command and a zero-setup double-click fallback documented in the slide's speaker notes.

**Why.** The deliverable is a static HTML file, so a static server is needed to preview it. Keynote silently drops `file://` hyperlinks on import, leaving plain text, while it preserves `http://` links (confirmed in the export); ports and directories were matched to launch.json so the links work once the server is up.

**Status.** adopted. Supersedes: *earlier decision to use file:// hyperlinks on slide 4*.

**Source.** `a:0e14484d-14`, `a:16127d04-06`, `a:8740dbd3-19` · Artifacts: `launch.json`, `.claude/launch.json`, `merge-tool-comparison/reports_taxonomy/phase3/adjudication/adjudication_ui.html`

> The deliverable is a static HTML file, so I need a static server. Let me check for an existing launch config and set one up to serve the file.
>
> — `2026-06-20_0e14484d.txt:43`

> Keynote silently drops `file://` hyperlinks on import, leaving plain text. Fixed by switching to `http://` links, which Keynote preserves
>
> — `2026-07-24_16127d04.txt:92`

### <a id="d-310"></a>D-310 — Either run the two remaining Docker P2 configs or document the 3-of-5 partial

`2026-06-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Proposed: complete the P2 whole-driver cost model by running the `driver-git` and `driver-auto` Docker configs, or else explicitly document the 3-of-5 partial run; `driver-auto` remains worth running after the routing flip.

**Why.** The "net −104 weighted cost vs bare Mergiraf" line is the strongest single defensible artifact and deserves a complete table; and post-flip `driver-auto` is not redundant with `driver-mergiraf` because NONE-cluster files still route to git.

**Status.** adopted. S12 (2026-07-26): completed — reports_whole_driver/FINDINGS.md:40-44 shows all five configs including driver-git 'computed (subprocess core/driver.py)' and driver-auto computed at both 843e5f5 (pre-flip) and 9e25b4e (post-flip); no 3-of-5 partial remains.

**Source.** `a:ce56e78d-03` · Artifacts: `merge-tool-comparison/tools/whole_driver_eval.py`, `reports_whole_driver/raw_results.json`

> Run `driver-git` + `driver-auto` (the Docker configs) to complete the cost-model table — *or* explicitly document the 3/5 partial.
>
> — `2026-06-24_ce56e78d.txt:37`

### <a id="d-311"></a>D-311 — Seed each run's cache from the previous run's, invalidating only what changed

`2026-06-25 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Runs reuse prior caches instead of recomputing: the tune runner gains a `--seed-cache` path so the definitive run reuses tune_d2's 243 cached merge reproductions plus the preliminary pass's 117 scored rows for the four untouched lanes, re-executing only the widened lanes; the D2 lane is added to the existing `detector_tune_run.py` LANES (rather than a new harness) and its cache seeded from tune_d1; seed import is filtered to `::__merge__::` keys only; and stale entries are cleared surgically — the 50 `driver-auto` smoke entries predating route capture were deleted while `driver-git` and the bare configs were kept as a resume head start.

**Why.** Merge reproductions are cached lane-independently under `::__merge__::` keys, so an earlier lane's cache can seed a later one; preflight already covers Joern/Docker/images, so seeding avoids re-doing merge work and untouched-lane Joern time. Cache entries that predate a data-capture change (route recording) must be recomputed, which is why only those are cleared.

**Status.** adopted.

**Source.** `a:82dd479f-16`, `a:acf7e1d0-06`, `a:82dd479f-sub-sub-agent-a46641-06`, `a:fb0fa5c5-05` · Artifacts: `merge-tool-comparison/tools/detector_tune_run.py`, `reports_whole_driver/raw_results.json`

> merge reproductions are cached lane-independently (`::__merge__::` keys), so tune_d1's cache can seed the D2 run
>
> — `2026-07-16_acf7e1d0.txt:50`

> tune_d2's cache holds all 243 merge reproductions to seed from. Extending the runner:
>
> — `2026-07-16_82dd479f.txt:121`

### <a id="d-312"></a>D-312 — Run long unattended evaluations on a one-shot x86_64 EC2 instance instead of the laptop

`2026-06-25` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources split between ali (choosing AWS, authorizing the c7i.2xlarge launch), claude (instance architecture) and joint (cancelling the local run). Recorded as joint: Claude put the options and costs, Ali chose and authorized.*

**Decision.** Long unattended runs move to a one-shot AWS EC2 instance rather than a university/lab server or chunked local execution, and the planned local overnight P2 run is cancelled in favour of it. The instance must be Intel x86_64 (`c7i`/`c6i`/`m7i`), never Graviton/arm64; on Ali's go-ahead the assistant creates the key pair and security group and launches a `c7i.2xlarge` (8 vCPU/16 GB, Ubuntu 24.04 x86_64, 80 GB gp3, eu-central-1) via the AWS CLI, and must run a small smoke test on the box before any full run.

**Why.** The binding constraint is Ali's: "i can not run 20h hours too. as i need to be stationary for that long and it will exhaust my laptop" — chunked local execution still loads the machine, and with AWS the laptop need not be tied up at all. Graviton is ruled out because all five Docker images are linux/amd64, so arm64 would re-introduce emulation unless the images were rebuilt multi-arch; c7i.2xlarge is recommended for Joern RAM headroom; and CLI launch is smoother than the console and lets the setup be verified end-to-end.

**Status.** adopted. Supersedes: [D-313](#d-313) — First AWS arrangement: user launches the instance, assistant drives it over SSH; *Local overnight P2 run launched from the Mac*.

**Cross-theme.** *depended on by* ← [D-408](#d-408) (see the reconciliation note there)

**Source.** `b:fb0fa5c5-17`, `a:fb0fa5c5-10`, `a:fb0fa5c5-13`, `b:fb0fa5c5-26` · Artifacts: `deploy/aws/`, `deploy/aws/RUNBOOK.md`, `i-0424514e6763b3c52`, `sg-052531d61c0cfb520`, `p2key`

> problem is that, i can not run 20h hours too. as i need to be stationary for that long and it will exhaust my laptop
>
> — `2026-06-24_fb0fa5c5.txt:455`

> **Native arch** — use a `c7i`/`c6i`/`m7i` (Intel, x86_64) instance, **not Graviton/arm64**. Graviton would re-introduce emulation for the amd64 images unless you rebuild them multi-arch.
>
> — `2026-06-24_fb0fa5c5.txt:427`

### <a id="d-313"></a>D-313 — First AWS arrangement: user launches the instance, assistant drives it over SSH

`2026-06-25` · **superseded** · `[chat]` · corroboration: single-pass · confidence: high · actors: joint

**Decision.** Initial division of labour: Ali creates the AWS account, launches the instance in the console and hands over the public DNS plus the `.pem` path; the assistant then bundles, transfers, provisions, smokes, runs and monitors over SSH from Ali's Mac.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** superseded. Superseded by [D-312](#d-312) — Run long unattended evaluations on a one-shot x86_64 EC2 instance instead of the laptop.

**Source.** `b:fb0fa5c5-25`

> Locked in: **you launch, I drive.**
>
> — `2026-06-24_fb0fa5c5.txt:588`

### <a id="d-314"></a>D-314 — Ship locally-built amd64 images to the instance with docker save/load rather than rebuilding

`2026-06-25` · **superseded** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** The five amd64 tool images are packaged as tarballs with `docker save` and `docker load`ed on the EC2 instance instead of being rebuilt there.

**Why.** The images are already built locally, and rebuilding Spork/Weave from source on a fresh box is the painful part; save/load makes the instance an exact mirror of the local setup.

**Status.** superseded. Superseded by [D-328](#d-328) — Standing rule: always prefer AWS over local for compute runs, with a ≤20-unit local exception.

**Source.** `a:fb0fa5c5-11` · Artifacts: `deploy/aws/bundle.sh`, `deploy/aws/provision.sh`

> So you `docker save` them to tarballs and `docker load` on the instance — **no rebuilding Spork/Weave from source on a fresh box** (that's the painful part).
>
> — `2026-06-24_fb0fa5c5.txt:484`

### <a id="d-315"></a>D-315 — Run the P2 harness sequentially on AWS with no sharding code change

`2026-06-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** No `--shard`/parallelism change is made to `whole_driver_eval.py`: the AWS run is the unchanged sequential harness, unattended — and Ali re-affirmed that choice after learning that parallel sharding would be both faster (~5 h vs ~20 h) and cheaper (~$2–3 vs ~$8–9). It was launched detached under `nohup` logging to `full_run.log`.

**Why.** The binding constraint was "off my laptop, no babysitting" rather than speed, and keeping the harness unchanged carries zero risk to the validated code. No reason is recorded for the re-affirmation after the timing/cost comparison.

**Status.** adopted.

**Source.** `a:fb0fa5c5-12`, `a:fb0fa5c5-18` · Artifacts: `tools/whole_driver_eval.py`, `deploy/aws/RUNBOOK.md`, `reports_whole_driver/full_run.log`

> The harness runs **sequentially, unchanged** — zero risk to the validated code.
>
> — `2026-06-24_fb0fa5c5.txt:541`

> Sequential it is — launching the full run now, **detached under `nohup` and logging to `full_run.log`** so you get the live `tail -f` you wanted.
>
> — `2026-06-24_fb0fa5c5.txt:930`

### <a id="d-316"></a>D-316 — Commit the AWS kit and record each cycle's real commands, costs and lessons in CLI-DEPLOY.md

`2026-06-25 → 2026-07-17` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources split between joint (committing the kit, at Ali's prompting) and claude (the two cost disclosures). Recorded as joint.*

**Decision.** `deploy/aws/` (bundle.sh, provision.sh, RUNBOOK.md) is committed, and `deploy/aws/CLI-DEPLOY.md` records the CLI commands actually run, all resource IDs, a copy-paste teardown block and the native-≈-no-speedup timing finding, with `deploy/.gitignore` excluding the regenerable 611 MB dist/. Subsequent cycles add their real costs and failure modes to the same record: the ~$10-vs-~$2 overrun caused by the instance idling overnight after the SSH watcher died of broken pipe (with three fixes — ServerAliveInterval, fallback wakeup, a `pgrep -f` self-match trap), and the later ~$12–18 cycle whose descriptive derivation-split run (~10 instance-hours, ~$4) was kept despite exceeding the plan's ~$5–10 estimate.

**Why.** The kit was untracked and would be lost on a tree clean; the RUNBOOK documented the console path while the CLI path was actually used; and resource IDs, teardown commands and the timing lesson existed only in the conversation. The overrun is disclosed with "the failure mode and three concrete fixes ... recorded in the CLI-DEPLOY cycle record so it doesn't repeat", and the later overrun is recorded as structural rather than waste — 7-lane × 2-arm, Joern-bound, ~2.4× the Stage-C-shaped cycle the estimate was calibrated on — with the only real spend lever being a plan-specified deliverable.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-408](#d-408) (see the reconciliation note there)

**Source.** `a:fb0fa5c5-19`, `a:8740dbd3-17`, `a:2e726dc0-04` · Artifacts: `12b450d`, `deploy/aws/CLI-DEPLOY.md`, `deploy/aws/RUNBOOK.md`, `deploy/aws/bundle.sh`, `deploy/aws/provision.sh`

> Add **`deploy/aws/CLI-DEPLOY.md`** — the *actual* CLI commands we ran, the resource IDs, the **teardown block**, and the timing finding.
>
> — `2026-06-24_fb0fa5c5.txt:989`

> **Cost overran: ~$10 vs the ~$2 estimate.**
>
> — `2026-07-03_8740dbd3.txt:420`

### <a id="d-317"></a>D-317 — Collect, commit and push results before teardown; then verify the account is empty

`2026-06-26 → 2026-07-03` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources split between claude (the sequence and the interim pull), ali (push-before-teardown, teardown execution, the standing teardown rule) and joint (the interim snapshot). Recorded as joint: Claude proposed the ordering, Ali directed and ratified it.*

**Decision.** The end-of-cycle sequence is fixed: scp results down to the local repo, write FINDINGS and update docs, commit and push to GitHub (including the 42 MB cache), and only then terminate the instance — never the reverse. Mid-run, completed populations' caches, the materialization log and the effective controls list are pulled down incrementally as insurance, and an in-progress snapshot of `raw_results.json` and `full_run.log` is kept locally in a clearly-named backup folder (not in git). Teardown itself is mandatory before ending the cycle: terminate the instance, delete the security group and key pair, then verify no instances or EBS volumes remain and reclaim the local bundle; the instance is never left running unattended after a run completes.

**Why.** The instance's EBS volume is `DeleteOnTermination=true`, so anything not copied back before teardown is gone — and terminating (not stopping) is what ends billing. Each cache entry is ~90 s of compute, making the live cache the irreplaceable artifact, so an incremental local copy means an instance loss costs at most the uncomputed remainder. Pushing to GitHub first backs the results up before the cloud copy is destroyed, leaving them in three places.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-408](#d-408) (see the reconciliation note there)

**Source.** `a:fb0fa5c5-20`, `a:fb0fa5c5-21`, `b:fb0fa5c5-33`, `b:fb0fa5c5-34`, `a:8740dbd3-07`, `a:2e726dc0-09` · Artifacts: `merge-tool-comparison/reports_whole_driver/`, `merge-tool-comparison/reports_whole_driver/aws_interim/`, `deploy/aws/CLI-DEPLOY.md`, `32df839`

> the teardown **deletes the instance and its disk** (the EBS volume is `DeleteOnTermination=true`) — so anything not copied back first is gone.
>
> — `2026-06-24_fb0fa5c5.txt:1152`

> each entry is ~90 s of compute, so it's the irreplaceable part. I'll put it in a clearly-named backup folder so it doesn't clobber your local working files.
>
> — `2026-06-24_fb0fa5c5.txt:1169`

### <a id="d-318"></a>D-318 — Move each compute run to AWS and shrink the bundle so the move is cheap

`2026-07-02 → 2026-07-03` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

*Actors note: Sources split between ali (directing the AWS moves and the tarball rule) and claude (the parity argument, the trimmed bundle, the DRIVER_COMMIT override). Recorded as joint.*

**Decision.** Compute runs are moved onto AWS rather than kept local: the six-tool canonical promotion is produced on the instance alongside the post-flip driver-auto re-run in a single cycle, and the #26 project-level tagging run is executed on AWS against its brief's local-execution instruction (Ali interrupted local environment checks with "execute it in aws"), following the deployment runbook in eu-central-1 under profile claude-p2 with provision/probe/teardown. The bundle is trimmed to make this cheap: only the 15 repos the 50 scenarios actually reference are shipped (604 MB, not the full ~2.1 GB `data/repos/`), Phase-2b scenarios are materialized into a new gitignored `data/scenarios_phase2b/` and shipped as their own tarball because `data/` is not in repo.tar.gz — AppleDouble-clean (`COPYFILE_DISABLE=1`, or delete `._*` after extraction) — and a `DRIVER_COMMIT` environment override is added to detect_validate.py so runs on git-archive deployments with no `.git` still attribute cached verdicts to the right commit sha.

**Why.** Producing the canonical table on AWS "puts it in the same scoring environment as the P2 canonical numbers" per the environment-sensitivity finding, and P4's compute is trivial (~20–40 min) so the cycle is nearly free. Shipping only the referenced repos removes the 2.1 GB objection that had kept the tagging run local. macOS tar ships AppleDouble `._*` files that break JSON loaders, and `data/` cannot ride along inside repo.tar.gz.

**Status.** adopted. Supersedes: [D-320](#d-320) — Run the #26 project-level tagging locally because shipping 2.1 GB of clones is not worth it.

**Cross-theme.** *supersedes* ← [D-173](#d-173) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-104](#d-104) — other_uid a:7b3b2669-02 is cited there: the #26 project-level tagging mode (opt-in flag on rm2_tag.py) is the workload this AWS move executed.

**Source.** `a:7b3b2669-03`, `b:7b3b2669-04`, `a:7b3b2669-04`, `a:fb0fa5c5-31`, `a:8740dbd3-04`, `b:fb0fa5c5-61` · Artifacts: `deploy/aws/bundle.sh`, `data/scenarios_phase2b/`, `tools/detect_validate.py`, `5ed92a2`, `reports/results.csv`

> there's a principled bonus: producing the new canonical table **on AWS puts it in the same scoring environment as the P2 canonical numbers** (the env-sensitivity finding from the review)
>
> — `2026-06-24_fb0fa5c5.txt:1784`

> AWS notes: only the 15 repos the 50 scenarios need were shipped (604 MB, not 2.1 GB)
>
> — `2026-07-03_7b3b2669.txt:114`

### <a id="d-319"></a>D-319 — Do not run P3 and P4 as parallel sessions or worktree agents

`2026-07-02` · **adopted** · `[chat]` · corroboration: single-pass · confidence: high · actors: claude

**Decision.** P3 and P4 are not run as literal parallel sessions or worktree agents. (The position was later narrowed rather than reversed: independent measurement cycles were allowed to run concurrently — see [D-336](#d-336).)

**Why.** For a half-day P3 the merge-the-docs tax probably eats the saving, since both workstreams edit STATUS.md and ISSUES.md.

**Status.** adopted.

**Source.** `b:fb0fa5c5-46` · Artifacts: `STATUS.md`, `ISSUES.md`

> but for a half-day P3 the merge-the-docs tax probably eats the saving
>
> — `2026-06-24_fb0fa5c5.txt:1549`

### <a id="d-320"></a>D-320 — Run the #26 project-level tagging locally because shipping 2.1 GB of clones is not worth it

`2026-07-03` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The #26 project-level RM2 tagging run was specified to run locally, with RefactoringMiner invoked only via its Docker image (never host binaries) and results cached for resumability.

**Why.** Shipping 2.1 GB of repo clones to AWS is not worth it.

**Status.** superseded. Superseded by [D-318](#d-318) — Move each compute run to AWS and shrink the bundle so the move is cheap.

**Source.** `a:fb0fa5c5-45` · Artifacts: `tools/rm2_tag.py`, `ISSUES.md #26`

> Run locally (shipping 2.1 GB of
>
> — `2026-06-24_fb0fa5c5.txt:2328`

### <a id="d-321"></a>D-321 — Rewrite the Phase-2b prompt to run evaluation on AWS and carry the four paid-for lessons

`2026-07-03` · **adopted** · `[chat]` · corroboration: single-pass · confidence: high · actors: joint

*Actors note: One source records Ali directing the change ("change Prompt 2 to run it in aws"), the other Claude specifying the content.*

**Decision.** The Phase-2b session prompt is to be rewritten so recon stays local (web/reading work) while the evaluation compute runs on AWS per deploy/aws/CLI-DEPLOY.md, with mandatory teardown and user go-ahead for spend; and its AWS stage is to encode four lessons explicitly — the AppleDouble tar junk fix (`COPYFILE_DISABLE=1` / delete `._*`), `cat | ssh` transfer plus checksum verification instead of bare scp, the silent arm64 image death and the live-probe requirement, and the `DRIVER_COMMIT` override for git-archive deployments.

**Why.** Keep the laptop free for the compute stage; and write the lessons in "so the fresh session doesn't rediscover them at $0.42/hour".

**Status.** adopted. S12 (2026-07-26): enacted — the Phase-2b session ran recon-local and evaluation on AWS per the runbook, and deploy/aws/CLI-DEPLOY.md carries the lessons (COPYFILE_DISABLE at :139, checksum-before-run at :150) plus the 'Fourth cycle record (Phase-2b detection oracle, 2026-07-04/05)' at :153 documenting cat|ssh + checksum transfers with zero AppleDouble junk. Supersedes: *Phase-2b prompt with evaluation run locally*.

**Source.** `b:fb0fa5c5-67`, `a:fb0fa5c5-46` · Artifacts: `deploy/aws/CLI-DEPLOY.md`

> Recon runs locally; the evaluation compute runs on AWS (keep the laptop free).
>
> — `2026-06-24_fb0fa5c5.txt:2411`

> the four paid-for lessons (AppleDouble tar junk, scp→cp degradation + checksum verification, silent arm64 image death, DRIVER_COMMIT for git-archive deployments) written into the prompt so the fresh session doesn't rediscover them at $0.42/hour.
>
> — `2026-06-24_fb0fa5c5.txt:2495`

### <a id="d-322"></a>D-322 — Trace apparent failures to the wrapper before blaming the run

`2026-07-03 → 2026-07-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** A recurring practice of attributing apparent failures to the tooling around the work rather than the work: a background task's exit code 1 was diagnosed as `tee` failing to open its logfile (with zsh reporting the pipeline status as tee's) and the poller re-launched without `tee`; the Fable-5 xhigh call, run in the background because it can take minutes, was reported "failed" for the same BSD `tee` operand reason while the Python process completed with stop_reason=end_turn; an apparent G1 run hiccup was traced to a status check tailing the wrong log path (run from `~` instead of the repo dir); Keynote's failure to open the built .pptx was attributed to cold-start flakiness once every variant including the full 8-slide deck opened; and count_tokens jitter / truncation-ladder drift was ruled out as the cause of the guard's 13 mismatches because levels were stable across runs.

**Why.** In each case the evidence located the fault outside the run: the Python poller ran its full budget cleanly and persisted all state; the `tee` nonzero exit came from the pipe's tail, not the run; "My earlier status check just tailed the wrong path (ran from `~` instead of the repo dir) — the run itself never hiccupped"; every deck variant opened; and "Levels are deterministic (stable across runs) — so it's not `count_tokens` jitter; the **content** differs at the same level."

**Status.** adopted. Supersedes: *background Phase-1 batch task 'failed with exit code 1'*; *that the G1/scoring run had hiccupped*; *that Keynote's failure to open the deck indicated a problem with the generated .pptx*.

**Source.** `a:788e483b-12`, `a:6296f4f6-21`, `a:8740dbd3-27`, `a:16127d04-21`, `a:9e4b6896-04`

> The exit code 1 is spurious — it's from the `tee` at the very start failing to open its logfile
>
> — `2026-07-09_788e483b.txt:141`

> Levels are deterministic (stable across runs) — so it's not `count_tokens` jitter; the **content** differs at the same level.
>
> — `2026-07-11_9e4b6896.txt:145`

### <a id="d-323"></a>D-323 — Freeze workload models by phase: Opus 4.8 batch for both labeling passes, Fable 5 for consolidation

`2026-07-08 → 2026-07-10` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources split between claude (recommending the allocation and withdrawing the temperature advice) and ali (freezing it and pinning the Phase-2 call). Recorded as joint: Claude put the options, Ali froze the choice.*

**Decision.** Workload models are frozen per phase: `claude-opus-4-8` via the Batch API for the Phase-1 and Phase-3 bulk labeling passes (same model both passes; Sonnet 5 rejected for Phase 3), and `claude-fable-5` interactive for the single Phase-2 consolidation call with `fallbacks=[{"model":"claude-opus-4-8"}]`, betas `["server-side-fallback-2026-06-01"]`, no thinking param and `output_config {"effort":"xhigh"}` — with the full request params, the model that actually served the response and the response id recorded in manifest.json. Haiku 4.5 is not used. A mid-stream workload-model change is a protocol amendment, not a convenience choice. Temperature/top_p/top_k are not used as a determinism lever.

**Why.** Opus 4.8 is the capability-per-dollar tier for bounded per-unit extraction and Batch halves the cost of overnight work; keeping one model across both labeling passes "removes a confound from your pass-1-vs-pass-2 stability check", and a mid-stream change breaks pass-to-pass comparability. Fable 5 is reserved for "the single hardest reasoning step and it's tiny in volume", and can only carry the fallbacks parameter because that parameter is rejected on the Batch API. Haiku is skipped because "a small model produces plausible-wrong mechanisms, the failure mode your protocol most needs to avoid". On these models `temperature`/`top_p`/`top_k` are removed from the API (sending them is a 400), so run-variance is measured by the label-stability metric instead.

**Status.** adopted. Supersedes: *earlier advice to document temperature 0 as a determinism lever*.

**Source.** `a:4c7b0828-11`, `a:4c7b0828-12`, `b:4c7b0828-14`, `a:cfe6365a-06`, `a:6296f4f6-02` · Artifacts: `outputs/taxonomy-protocol.md §9`, `workspace/api_smoke_test.py`, `manifest.json`

> one model across both labeling passes removes a confound from your pass-1-vs-pass-2 stability check.
>
> — `2026-07-06_4c7b0828.txt:675`

> - Workload models FROZEN: claude-opus-4-8 via the Batch API for Phases 1+3
>
> — `2026-07-08_cfe6365a.txt:41`

### <a id="d-324"></a>D-324 — Run bulk labeling through the Batch API from a committed harness, with structured outputs

`2026-07-08 → 2026-07-09` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Bulk labeling runs through committed Python harnesses calling the Anthropic Batch API on a separate pay-as-you-go account (~$100 credits), not by having a Claude Code session iterate over the 500 units interactively. Both batch phases use structured-output mode against committed JSON schemas. The runner polls every 60 s under a 2-hour budget and is resumable across restarts; when a batch ran slow, the poller was re-attached to the same batch via batches.json with a longer (env-configurable, 5.5 h) budget rather than the batch being cancelled and resubmitted. Budget arithmetic (~$50–60 of the $90–110 envelope) assumes only partial prompt-cache hits and reserves headroom for one full sanctioned rerun.

**Why.** The interactive alternative loses the 50% batch discount, hits subscription rate limits, requires an open session for hours, suffers context-window pressure, and has "weaker provenance (the citable claim "labels produced by prompt X on model Y" is cleaner when it's a committed script with a pinned model ID than "a chat session did it")". Structured outputs remove JSON-validity risk from the G0 gate. Phase-1 precedent showed batches can finalize slowly, so the runner must tolerate long waits and be restartable; a resubmit "forfeits ~2h of compute already in flight" while re-attaching costs nothing and avoids double-billing. Opus 4.8's minimum cacheable prefix is 4096 tokens so the Phase-1 static prefix may not cache — assuming partial hits leaves room for one rerun.

**Status.** adopted.

**Source.** `a:4c7b0828-16`, `a:cfe6365a-15`, `a:cfe6365a-18`, `a:506d875b-08`, `a:788e483b-03` · Artifacts: `workspace/api_smoke_test.py`, `tools/taxonomy_phase1.py`, `detector_specs_batch.py`, `merge-tool-comparison/prompts_taxonomy/phase1_output.schema.json`, `merge-tool-comparison/prompts_taxonomy/phase3_output.schema.json`, `reports_taxonomy/phase1/batches.json`

> You *could* skip the API and have a Claude Code session itself loop over the 500 units interactively. But that's strictly worse for this job
>
> — `2026-07-06_4c7b0828.txt:796`

> I can also cancel and resubmit, but I'd advise against it — the batch is progressing without errors and a resubmit forfeits ~2h of compute already in flight.
>
> — `2026-07-09_788e483b.txt:158`

### <a id="d-325"></a>D-325 — Keep the API key in ~/.zshenv and span the two venvs with stdlib-only shared code

`2026-07-08 → 2026-07-10` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Three sources record Claude's decisions; the repo-root-venv instruction comes from Ali's brief.*

**Decision.** `ANTHROPIC_API_KEY` is exported from `~/.zshenv` rather than `~/.zshrc`, kept out of the repo and out of chat; API work runs against the anthropic SDK in the repo-root `.venv`, explicitly not the merge-tool-comparison venv. The shared harness module `tools/taxonomy_common.py` is written stdlib-only so it imports under either venv, and the stratum-B Mergiraf pass reuses the comparator's existing `MergirafTool` (comparator venv + Docker) instead of re-implementing the invocation.

**Why.** "zsh reads `.zshenv` for *every* shell including non-interactive ones (like the ones I spawn), whereas `.zshrc` is only read by interactive shells. That's exactly why I couldn't see it even after sourcing" — and the key must not be pasted into chat because it would be stored in the session transcript. Two venvs split the dependencies (`merge-tool-comparison/.venv` has GitPython, repo-root `.venv` has anthropic), so shared code must run under either; reusing MergirafTool means strata A and B share the identical `merge-tools/mergiraf:0.17.0` invocation.

**Status.** adopted. Supersedes: *earlier instruction to add the export to ~/.zshrc*.

**Source.** `a:4c7b0828-17`, `a:92a3e464-06`, `a:92a3e464-07`, `a:6296f4f6-22` · Artifacts: `~/.zshenv`, `tools/taxonomy_common.py`, `tools/taxonomy_mergiraf.py`

> I'd suggest `~/.zshenv` rather than `~/.zshrc` — zsh reads `.zshenv` for *every* shell including non-interactive ones
>
> — `2026-07-06_4c7b0828.txt:851`

> Two venvs split the deps: `merge-tool-comparison/.venv` has GitPython (Docker/materialization tools), repo-root `.venv` has anthropic (API tools).
>
> — `2026-07-08_92a3e464.txt:94`

### <a id="d-326"></a>D-326 — Harden request assembly and the manifest before G0 as ordinary pre-gate edits

`2026-07-09` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Four pre-G0 fixes to the taxonomy harness: the frozen fixed-12-file T3 becomes a floor plus a fit search that reduces the file cap 12→1 and then truncates individual oversized diffs until the unit fits the 30k budget, with `build_unit_inputs` taking file_cap/diff_line_cap overrides and the effective aggressiveness recorded per unit as a covariate (e.g. T3/cap5, T3/cap1/trunc400); both API `count_fn` implementations tolerate oversized-request errors so an over-large T0 render falls through the ladder; `{UNIT_INPUTS}` is injected with a single-occurrence replace targeting the first (real) slot because the frozen USER template contains the token twice; and the `utcnow` deprecation plus the empty `protocol.frozen_commit` (git log ran with cwd inside merge-tool-comparison/ while the protocol lives at repo-root outputs/) are fixed and the split/manifest regenerated.

**Why.** 18 scored units exceeded the 30k hard cap even at T3 — many-file units (javaparser 59 files → 53k) and few-file-huge-diff units (projectkorra 2 files → 115k) — which fails a G0 criterion, and §5 explicitly sanctions revisiting assembly before Phase 1 as an ordinary pre-G0 edit. The 193-file monster unit could make T0 huge, so the ladder must degrade rather than error. A naive `.replace` would inject the assembled content twice, confirmed by the doubled character count. The manifest is a committed artifact so clean code is worth it, and the seed makes the regenerated split byte-identical, keeping it an ordinary pre-G0 edit.

**Status.** adopted. Supersedes: *frozen T3 with a fixed 12-file cap*.

**Cross-theme.** *supersedes* ← [D-205](#d-205) (see the reconciliation note there)

**Source.** `a:92a3e464-14`, `a:92a3e464-15`, `a:92a3e464-17`, `a:92a3e464-24` · Artifacts: `tools/taxonomy_common.py`, `tools/taxonomy_assemble.py`, `tools/taxonomy_split.py`, `reports_taxonomy/manifest.json`, `302879e`

> §5 explicitly sanctions a pre-G0 assembly revisit as an ordinary edit, so T3 became a *floor* with a fit search (reduce file cap 12→1, then truncate per-diff line counts), guaranteeing ≤30k.
>
> — `2026-07-08_92a3e464.txt:383`

> harden both API `count_fn`s against oversized-request errors (the 193-file monster unit could make T0 huge), so the ladder falls through gracefully
>
> — `2026-07-08_92a3e464.txt:144`

### <a id="d-327"></a>D-327 — Verify the request instrument before submitting and compare artifacts on their bytes

`2026-07-09 → 2026-07-11` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Before G0 the harness dry-constructs a Batch `Request` with the exact frozen parameters without submitting, to confirm the SDK passes `output_config` (effort + json_schema), adaptive thinking and system `cache_control` through rather than dropping them; `custom_id()` is validated for API-validity, uniqueness and invertibility across the whole census (max 64 chars) before rerunning G0, and results are mapped back to merge_ids by inverting the submit-time custom_id map rather than string-splitting the id. The production Phase-1 tool is built by adapting the G0 pilot so request construction is byte-identical to the passed pilot, reusing the exact `assemble_best` path with a resumable multi-batch cache. The assembly integrity guard compares the just-written file's bytes against the committed Phase-1 file's bytes rather than in-memory text against `read_text()`.

**Why.** Dry-construction exists to de-risk the G0 batch by confirming the SDK does not silently drop the frozen parameters. Reusing the pilot's code path byte-identically avoids re-validating assembly, and was verified by the truncation ladder reproducing exactly (T0:118/T1:2/T2:29/T3×15). The guard was fixed because the 13 flagged units contained CRLF line endings and `read_text()` universal-newline-translates CRLF→LF, so the comparison falsely flagged files that were byte-identical on disk — after which "assembly is perfectly reproducible (0 byte-level mismatches across all 165)". No reason is recorded for preferring map inversion over string parsing.

**Status.** adopted. Supersedes: *13 derivation units' Phase-3 assembly differs from committed Phase-1 inputs*.

**Source.** `a:92a3e464-16`, `a:92a3e464-21`, `a:92a3e464-22`, `a:788e483b-01`, `a:9e4b6896-03` · Artifacts: `tools/taxonomy_g0_pilot.py`, `tools/taxonomy_common.py`, `reports_taxonomy/phase1/raw_results.json`, `1b66a13`

> let me de-risk the G0 batch by dry-constructing a Batch `Request` with the exact frozen params (no submission) — to confirm the SDK passes `output_config`/`thinking` through rather than dropping them.
>
> — `2026-07-08_92a3e464.txt:250`

> The guard compared in-memory CRLF text against newline-normalized `read_text()`. Fix: compare the just-written file's bytes to the committed Phase-1 file's bytes.
>
> — `2026-07-11_9e4b6896.txt:149`

### <a id="d-328"></a>D-328 — Standing rule: always prefer AWS over local for compute runs, with a ≤20-unit local exception

`2026-07-15 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: ali

**Decision.** CLAUDE.md gains the standing rule "Always prefer AWS over local for compute runs", with the operational sub-rules the five cycles established: the CLI-DEPLOY.md pattern, a c7i.2xlarge native x86_64 instance, images built on-instance, the environment validated by reproducing a canonical table before scoring, and verified teardown. Unit tests, fixtures and pilots of ≤ ~20 units stay local. The detector plan's S-D5 default runtime becomes an AWS cycle, and later kickoffs restate the rule verbatim — one AWS cycle for the eval battery, local acceptable only for the pre-flight smoke subset.

**Why.** "native x86_64 kills both the Rosetta/QEMU wall-clock tax and the entire *arm64-image-dies-silently* class of scoring bugs that bit P2 v1, and it keeps your Mac free while you write." The ≤20-unit exception is scoped explicitly so "G0-style pilots and GD2 fixture batteries don't trigger pointless deploys".

**Status.** adopted. Supersedes: [D-314](#d-314) — Ship locally-built amd64 images to the instance with docker save/load rather than rebuilding; *detector plan's earlier "local overnight" default for S-D5*.

**Source.** `a:4c7b0828-28`, `b:2e726dc0-04`, `a:6a84a6b3-04` · Artifacts: `CLAUDE.md`, `outputs/detector-cycle-plan.md`, `deploy/aws/CLI-DEPLOY.md`

> always prefer aws over local
>
> — `2026-07-06_4c7b0828.txt:1739`

> I scoped the exception explicitly: unit tests, fixtures, and small pilots (≤ ~20 units) stay local
>
> — `2026-07-06_4c7b0828.txt:1745`

### <a id="d-329"></a>D-329 — Tune-control runs are a documented local exception to the AWS-first rule

`2026-07-15 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** GD2's full-suite runs over the 100 tune-controls inside a build session's iterate-and-fix loop are a documented local exception to the AWS-first standing rule, with the D3 Joern pass's ~1–2 h emulated cost acknowledged in advance. The definitive GD2(iii) tune gate accordingly ran on the laptop, with AWS reserved for S-D5's frozen evaluation battery; offered fallbacks if local load became a problem were throttling to 2 shards (~4 h) or killing and finishing overnight serial, and the shards were left running absent a word from Ali.

**Why.** "Deploying to EC2 per tuning iteration is absurd, but the CLAUDE.md rule as written says local is only for ≤20 units. Needs an explicit documented exception, or every build session starts by violating a standing rule." GD2 is the one place tuning is allowed, so each flag triggers an in-session fix and re-score — on EC2 each iteration would be a redeploy, buying exactly the deploy/build/validate overhead the exception exists to avoid — and that loop already happened once in-session. The usual AWS motivation barely applies here: Joern runs natively, merge reproductions are fully cached, and only short RM2 containers are emulated. Caches make a restart lossless at file granularity.

**Status.** adopted.

**Source.** `a:4c7b0828-29`, `a:82dd479f-14`, `b:82dd479f-06` · Artifacts: `outputs/detector-cycle-plan.md §5 GD2(iii)`, `deploy/aws/CLI-DEPLOY.md`

> tune-control runs are a documented local exception (bounded iterative tuning loops; per-iteration EC2 deploys are absurd)
>
> — `2026-07-06_4c7b0828.txt:1806`

> on EC2 each iteration would be a redeploy
>
> — `2026-07-16_82dd479f.txt:213`

### <a id="d-330"></a>D-330 — Shard long runs into static round-robin shards, re-partitioning stragglers mid-run

`2026-07-16 → 2026-07-18` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The definitive 100-control FULL 7-lane tune run is split into four parallel static shards (61/61/61/60 files) rather than run serially, accepting local load ~20 for roughly 2 h wall time. When static sharding produced a straggler on AWS, the heavy eval-control shards 0/4 and 1/4 were re-partitioned mid-run into modular half-shards (0/8+4/8, 1/8+5/8) with their existing cache files copied into each half, letting the orchestrator exit while the tail (spgroup + scoring) was driven manually.

**Why.** The plan's 1–2 h estimate was wrong for the FULL 7-lane composition (~10 Joern JVM spawns per file → ~6.5 h serial measured), so 4-way sharding brings wall time back to ~2 h. On AWS, static sharding balanced merge counts but not work — shard 0 drew 338 of 832 files and projected 12–17 more hours on one worker while 6 of 8 vCPUs idled; the modular identity makes coverage provably identical (no merge lost or duplicated), cache keys do not mention the shard so nothing recomputes, and `--score` globs all cache files.

**Status.** superseded. Superseded by [D-335](#d-335) — Replace static shards with a 4-worker work queue — deferred out of the frozen run, adopted in S-D7. Supersedes: *plan §5 GD2(iii) estimate that the Joern-bearing D3 tune pass takes ~1–2h*.

**Source.** `a:82dd479f-15`, `a:2e726dc0-08` · Artifacts: `merge-tool-comparison/tools/detector_tune_run.py`

> I sharded it 4-way to get ~2h wall, which is why your laptop is loud right now — load is sitting around 20.
>
> — `2026-07-16_82dd479f.txt:217`

> So shards 2 and 3 finished, and shard 0 alone projected **12–17 more hours** while 6 of 8 vCPUs sat idle.
>
> — `2026-07-16_2e726dc0.txt:356`

### <a id="d-331"></a>D-331 — Adopt the audit fixes to the tune runner: cache-key namespace, exit codes, stale cache, one registry

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Three of five Angle-B audit findings are fixed in the tune runner and detect_validate: the detector cache-key namespace collision with the frozen Stage-C instrument (flag state becomes part of the key), argparse-level exit-code semantics for unknown lanes so rc 2 (bad invocation) stays distinct from rc 1 (gate FAIL), and stale-cache invalidation under uncommitted in-session tuning. The parallel `LANES` and `_SMOKES` dicts are collapsed into a single registry whose rows are `(strategy class, smoke builder)`, so a lane cannot be half-registered, and downstream sessions must use the new row shape. The image-gated test probe helper is rewritten to reuse the production `_run_rm2_pair` via the lane's composed RM2 runner instead of re-inlining a docker invocation.

**Why.** The stale-cache case is "exactly this session's documented workflow" (in-session, uncommitted lane fixes between tune reruns); the key collision would silently serve flag-ON rows to a flag-OFF arm; the exit-code collision would let automation record a spurious GD2 FAIL for a typo'd lane name. The parallel dicts created a three-way string coupling (`--lane` value, `strategy.name`, `_SMOKES` key) whose failure mode is an opaque KeyError after Docker has already started, so a single registry co-locates the class and its smoke fixture. No reason is recorded for routing the test probe through the production runner.

**Status.** adopted. Supersedes: [D-332](#d-332) — Two regressions the multi-lane rewrite introduced: ABORT exit code and a latent lane-key coupling.

**Source.** `a:82dd479f-06`, `a:acf7e1d0-10`, `a:acf7e1d0-11` · Artifacts: `merge-tool-comparison/tools/detector_tune_run.py`, `merge-tool-comparison/tools/detect_validate.py`, `semantic_merge_driver/tests/test_signature_stale_call.py`, `6523ab0`

> two adopted harness fixes (cache-key namespace collision with the frozen Stage-C instrument; argparse exit-code semantics), one adopted robustness fix (stale cache under uncommitted in-session tuning — exactly this session's documented workflow)
>
> — `2026-07-16_82dd479f.txt:173`

> the tune-runner `LANES` registry rows are now `(strategy class, smoke builder)`
>
> — `2026-07-16_acf7e1d0.txt:503`

### <a id="d-332"></a>D-332 — Two regressions the multi-lane rewrite introduced: ABORT exit code and a latent lane-key coupling

`2026-07-16` · **superseded** · `[chat]` · corroboration: single-pass · confidence: medium · actors: claude

**Decision.** The multi-lane tune-runner rewrite deleted `choices=sorted(LANES)` from `--lane`, validating lane names in code and exiting via `sys.exit("ABORT: unknown lane(s) …")` with code 1 — the same code a genuine GD2 gate FAIL returns — instead of argparse's exit code 2 plus usage text. A separate audit reported the resulting three-way string coupling (`--lane` value / `LANES` key / `_SMOKES` key / strategy `.name`) as a low-severity latent finding needing no guard or fix.

**Why.** No reason is recorded for replacing argparse validation. The coupling was left unfixed because all three identifiers currently agree so there is no live bug; the only exposure is a future lane keyed differently from its class's `.name`, which would raise an uncaught KeyError instead of the intended ABORT message.

**Status.** superseded. Superseded by [D-331](#d-331) — Adopt the audit fixes to the tune runner: cache-key namespace, exit codes, stale cache, one registry. Supersedes: *argparse-level --lane validation via choices=sorted(LANES)*.

**Source.** `a:82dd479f-sub-sub-agent-a46641-05`, `b:acf7e1d0-sub-sub-agent-af9ecb-01` · Artifacts: `merge-tool-comparison/tools/detector_tune_run.py:100`, `merge-tool-comparison/tools/detector_tune_run.py:148`

> The deleted `choices=sorted(LANES)` on --lane enforced lane validation at argparse level with exit code 2
>
> — `2026-07-16_82dd479f_sub-agent-a46641.txt:25`

> Currently all three agree, so no live bug.
>
> — `2026-07-16_acf7e1d0_sub-agent-af9ecb.txt:40`

### <a id="d-333"></a>D-333 — Persist the tune-runner cache once per scenario, accepting weaker crash durability

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** The rewritten multi-lane tune runner drops the `save()` after every detector record and persists the cache once per scenario via a `dirty` flag; the old per-result durability is not restored, and this is documented as a deliberate non-fix.

**Why.** Recorded in the code comment as a deliberate coarsening on the grounds that "a crash re-runs ≤1 file's lanes". The accepted cost is explicit: a crash or Ctrl-C mid-scenario loses all of that scenario's completed lane results (up to seven, several of them ~30 s Joern runs) rather than at most one — "a weakening of the old per-result durability invariant".

**Status.** adopted. Supersedes: *old runner's save() immediately after each newly computed detector record*.

**Source.** `a:82dd479f-sub-sub-agent-a46641-03`, `a:82dd479f-07` · Artifacts: `merge-tool-comparison/tools/detector_tune_run.py:167`

> The rewrite persists once per scenario via the `dirty` flag
>
> — `2026-07-16_82dd479f_sub-agent-a46641.txt:31`

> deliberate coarsening, but it is a weakening of the old per-result durability invariant.
>
> — `2026-07-16_82dd479f.txt:154`

### <a id="d-334"></a>D-334 — Move save() out of the per-lane loop (or append JSONL) to stop quadratic cache rewrites

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Recommended: relocate `save()` from inside the per-lane loop in detector_tune_run.py to after the lane loop, or switch the raw_results store to JSONL append, so a FULL run does ~7× fewer full-cache dumps instead of ~1,700 rewrites of a multi-MB cache, with resume semantics staying per-scenario (a mid-scenario crash re-runs at most 6 lane results).

**Why.** The current pattern is quadratic in results — a full `json.dumps` of a cache holding complete merged-file texts after every detector record — but materiality is LOW: 1–2 minutes against hours of Joern/Docker subprocess time. "Worth doing only because the fix is one line moved", and it would grow to tens of minutes on a 500+ file S-D5/S-D6 corpus.

**Status.** adopted. S12 (2026-07-26): landed — detector_tune_run.py:188 calls save() 'once per scenario: a crash re-runs ≤1 file's lanes', and ISSUES.md #31 lists 'per-scenario save batching' among the harness adoptions. The same-day parallel audit that read the runner as already per-scenario is what the adopted [D-333](#d-333) entry records; the code settles both readings the same way.

**Source.** `a:82dd479f-sub-sub-agent-a87c1f-03` · Artifacts: `merge-tool-comparison/tools/detector_tune_run.py`

> Cheaper with identical resume semantics per scenario: move `save()` after the lane loop (7x fewer dumps; a mid-scenario crash re-runs at most 6 lane results), or switch to JSONL append.
>
> — `2026-07-16_82dd479f_sub-agent-a87c1f.txt:31`

### <a id="d-335"></a>D-335 — Replace static shards with a 4-worker work queue — deferred out of the frozen run, adopted in S-D7

`2026-07-17 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** A dynamic work queue replaces static sharding, but not mid-run: the improvement was declined for the running battery and logged in runs.md as an S-D7/S-D8 candidate, then implemented in S-D7 as 4 work-queue workers over 180 positive + 195 control merges (largest merges first) with a recovery sweep and on-instance scoring.

**Why.** A work queue would flatten the straggler tails, "but that's a harness change I won't make mid-run under the freeze discipline". Adopted next cycle because static shards had produced the S-D5 imbalance; the queue balanced claims 94/96/93/92 across the four workers with no straggler shard.

**Status.** adopted. Supersedes: [D-330](#d-330) — Shard long runs into static round-robin shards, re-partitioning stragglers mid-run.

**Source.** `a:2e726dc0-07`, `a:06ec13eb-04` · Artifacts: `runs.md`, `run_sd7.sh`

> but that's a harness change I won't make mid-run under the freeze discipline; it goes in the runs.md notes as an S-D7/S-D8 improvement
>
> — `2026-07-16_2e726dc0.txt:316`

> claims balanced 94/96/93/92 across the 4 workers (the work-queue fixed the S-D5 static-shard imbalance problem — no straggler shard this time).
>
> — `2026-07-22_06ec13eb.txt:142`

### <a id="d-336"></a>D-336 — Run independent cycles concurrently in separate regions, sharing no AWS resource or commit

`2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources split between joint (Ali asking to run in parallel, Claude arguing it safe) and claude (the isolation and coordination rules). Recorded as joint: options were put and Ali chose.*

**Decision.** S-D7 and S-D8 may run concurrently in separate sessions on separate instances, staggered so the second starts while the first grinds on AWS; instead of serializing behind the 8-vCPU regional cap, S-D8 launches in eu-north-1 with its own quota (with a retry loop for the fresh-region PendingVerification delay) and uses its own imported key (`p2key-sd8`) and security group, sharing no resource with S-D7. Coordination rules: do not create or delete a shared key pair or the other session's security group, tear down only your own instance id and SG; treat VcpuLimitExceeded as proof the account cap is 8 vCPUs and fall back to serial; and `git pull` before starting and again before any ISSUES.md/manifest.json close-out edits, committing early and never rebasing away the other session's commits. S-D7 correspondingly left S-D8's resources and files untouched.

**Why.** The two cycles are independent measurements — separate populations, artifact dirs and instances, neither touching detector code and no result feeding the other — and "the plan's serial default is a WIP-discipline choice, and §7 itself allows parallelizing independent steps under calendar pressure". A second region has an independent 8-vCPU quota and nothing in the cycle is region-dependent (images build on-instance, the bundle transfers the same way), so cost is identical and ~10+ hours of waiting are saved; separate keys and SGs are strictly cleaner than the key-reuse pattern the kickoff anticipated. Both sessions will want to edit ISSUES.md and manifest.json at the end, and two sessions committing concurrently in one working tree produce git conflicts.

**Status.** adopted. Supersedes: *kickoff parallel-run note instruction to wait for S-D7's teardown and run serially on VcpuLimitExceeded*; *kickoff instruction to reuse the existing ~/.ssh/p2key.pem for this cycle's instance*.

**Source.** `a:2e726dc0-24`, `a:2e726dc0-25`, `a:68c24033-12`, `a:68c24033-13`, `a:06ec13eb-15` · Artifacts: `df58669`, `i-0006f73fee2019c40`, `sg-02be4b932de464e8f`, `p2key-sd8`, `50d2754`, `4982d18`

> The plan's serial default is a WIP-discipline choice, and §7 itself allows parallelizing independent steps under calendar pressure.
>
> — `2026-07-16_2e726dc0.txt:824`

> But a second region has its own independent 8-vCPU quota, and nothing in the cycle is region-dependent (images build on-instance, bundle transfers the same way).
>
> — `2026-07-22_68c24033.txt:109`

### <a id="d-337"></a>D-337 — Build pinned images on-instance but ship the unpinned ones, and set no _JAVA_OPTIONS

`2026-07-22` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources split between joint, ali and claude for the same split decision: Claude proposed the reproducibility-based split, Ali adopted it in the S-D8 kickoff. Recorded as joint.*

**Decision.** Image provisioning is split by reproducibility rather than by rule text: every pinned image (mergiraf 0.17.0, refactoring-miner 2.4.0, spork 0.5.0 with the legacy dual-tag, weave 0.3.2, google-java-format 1.22.0) is built on-instance per the standing rule, while the two unpinned comparator images (jdime:latest, mastery:latest) are shipped as `docker save` tarballs of the exact local amd64 images. Every image is probed live on-instance and exact reproduction of the canonical six-tool table is required before scoring. The split is recorded in the run notes as a one-sentence reasoned deviation-within-intent, not an amendment. The battery deliberately sets no `_JAVA_OPTIONS`.

**Why.** "the standing rule's intent is killing the silent-arm64 class, not mandating rebuilds for their own sake": jdime and mastery Dockerfiles clone upstream HEAD unpinned (ISSUES #10 retro-pinning TODO), so an on-instance rebuild could drift from the images that produced the committed canonical table and falsely fail the very gate meant to validate the environment; P2/P4 set the docker-save precedent, and the canonical-table reproduction is what makes the shipping path safe. `_JAVA_OPTIONS` is left unset to keep latency comparable with the P2/P3 whole-driver baselines.

**Status.** adopted. Supersedes: [D-314](#d-314) — Ship locally-built amd64 images to the instance with docker save/load rather than rebuilding.

**Source.** `a:2e726dc0-31`, `a:68c24033-05`, `a:68c24033-14` · Artifacts: `ISSUES #10`, `CLAUDE.md standing rule note`, `bundle_sd8.sh`, `provision_sd8.sh`, `run_sd8.sh`

> their Dockerfiles clone upstream HEAD unpinned (ISSUES #10 retro-pinning TODO), so an on-instance rebuild could drift from the images that produced the committed canonical table and falsely fail the gate
>
> — `2026-07-22_68c24033.txt:84`

> **Ship via `docker save`** the unpinned comparator images the canonical table depends on
>
> — `2026-07-16_2e726dc0.txt:971`

### <a id="d-338"></a>D-338 — Proposed v2 model split: Sonnet 5 for extraction, Opus 5 for consolidation and prose, no Haiku

`2026-07-25` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Proposed for the v2 decision-record build, reusing the taxonomy program's validated split: Sonnet 5 for the high-volume, tightly-specified per-session extraction (×2 passes) and Opus 5 for consolidation, supersession logic, provenance discipline and final writing, with Fable 5 an acceptable alternative for consolidation specifically and both phases on Opus 5 (second pass skipped) if cost is not binding. Haiku 4.5 is ruled out for any phase.

**Why.** The v1 misses were coverage failures, not reasoning failures, so a tight schema plus a read-gate suffices for extraction; the subtle judgment lives in consolidation on a small input, and the failure mode that matters most is a confidently-worded rationale nobody said. Haiku is excluded because "Faithfulness is the whole product."

**Status.** superseded. S12 (2026-07-26): the executed v2 instrument chose differently — PROTOCOL.md §8 Amendment 1 pinned claude-opus-5 for extraction (both passes, effort high) and consolidation also ran claude-opus-5 (consolidate_batch.py:36), with the two-pass option kept rather than skipped. Superseded by a recorded decision that is an instrument amendment, not an entry; superseded_by stays null.

**Source.** `a:c4c4d030-10`, `a:c4c4d030-11`

> | **Consolidation + writing** | **Opus 5** | Supersession logic
>
> — `2026-07-25_c4c4d030.txt:93`

> **Haiku 4.5**: no. Faithfulness is the whole product.
>
> — `2026-07-25_c4c4d030.txt:99`

### <a id="d-339"></a>D-339 — v2 orchestration route and the two-pass token budget are left open for Ali

`2026-07-25` · **open** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Two questions are put and deliberately left unresolved: whether v2 runs as multi-session paste-and-go (ten pasted prompts, proven context safety) or as one session fanning extraction out to subagents that write JSON to disk and return one-line summaries (parallel map phase, one prompt, requires explicit opt-in to multi-agent); and whether the ~800k–1M input-token cost of two passes over 15k lines plus subagents (~14–16 extraction sessions) is acceptable, against the stated cheaper alternative of one Opus 5 pass with a hard coverage gate and no stability diff. Either way S0 runs first and separately.

**Why.** The subagent route preserves the artifacts-only handoff discipline because subagents write to disk rather than reporting back through context, but it requires Ali's explicit opt-in to multi-agent; the multi-session route is slower but is the workflow that has actually worked eight times. The two-pass stability diff is a real cost, so the cheaper single-pass option is offered explicitly — "gets you most of the way at half the cost" — rather than the expensive design being assumed.

**Status.** open. Both are explicitly Ali's to settle before kickoff: the orchestration route needs an opt-in to subagents, and the token budget needs confirming. The v2 kickoff prompts would record the answers.

**Cross-theme.** *depends-on* → [D-451](#d-451), [D-366](#d-366) — other_uid b:c4c4d030-15 is cited by the former; the standing artifact-only handoff rule both entries state is the constraint that makes the subagent route acceptable.

**Source.** `a:c4c4d030-20`, `a:c4c4d030-21`, `b:c4c4d030-15` · Artifacts: `#30`

> one Opus 5 pass with a hard coverage gate and no stability diff — gets you most of the way at half the cost.
>
> — `2026-07-25_c4c4d030.txt:168`

> I'd take the subagent route if you're comfortable opting into it, and the multi-session route if you want the same paste-and-go rhythm you've been running all cycle
>
> — `2026-07-25_c4c4d030.txt:211`


## Repository & working conventions

*133 primary source decisions → 34 entries; 7 not promoted (reasons in `docs/decision-record/entries/repo-conventions.json`).*

### <a id="d-340"></a>D-340 — Source of truth is the source code, not the documentation

`2026-04-15 → 2026-06-24` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: The founding declaration and the 2026-05-26 reconciliation instruction are Ali's; the two restatements (scoping the tool-evaluation doc, grounding the 2026-06-24 diagram in the code) are Claude applying the standing rule, which is why two sources record 'claude'.*

**Decision.** The two thesis subprojects (merge-tool-comparison and semantic_merge_driver) live in one private repo, and the declared source of truth for each is the source code in its subfolder plus semantic_merge_driver/initial architecture.md as the target pipeline. Everything derived — plan documents, tool-evaluation write-ups, STATUS/CLAUDE/README/ARCHITECTURE, generated diagrams — is subordinate: when a derived doc disagrees with the code, the code wins and the doc is reconciled to it (commit 6892637 did exactly that for five stale claims), and a review diagram is drawn from the code as it actually runs rather than from the target architecture doc.

**Why.** Declared at repo founding as the per-project source of truth, with all docs to be aligned to it; the tool-evaluation document was then explicitly scoped as non-authoritative because "Source of truth remains source code"; and by 2026-05-26 two stale claims predating the session showed the derived docs had drifted from the code, so they were reconciled with the code kept as source of truth. CLAUDE.md's designation of source code as the authoritative input is what forced the 2026-06-24 architecture diagram to reflect the running code rather than the target spec.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-447](#d-447) — other_uid a:20b53f98-01 landed there: the strongest transcript-era statement of the rule. Mutual links rendered.

**Source.** `preA:pre-commits-01`, `preB:pre-commits-02`, `preB:pre-commits-04`, `preA:pre-tool-evaluation-findings-16`, `a:e1df1610-31`, `a:ce56e78d-01` · Artifacts: `f764605`, `semantic_merge_driver/initial architecture.md`, `CLAUDE.md`, `6892637`, `docs/plans/tool-evaluation-findings.md`

> Source of truth per project:
>
> — `2026-04-15_pre-commits.txt:11`

> So the derived docs had drifted from the code before today; they're now reconciled with STATUS/CLAUDE (and the code remains the source of truth).
>
> — `2026-05-20_e1df1610.txt:1405`

> since CLAUDE.md says source code is the authoritative input.
>
> — `2026-06-24_ce56e78d.txt:5`

### <a id="d-341"></a>D-341 — Gitignore anything regenerable; keep only evidence and irreplaceable binaries

`2026-04-15 → 2026-07-08` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: The policy and the Keynote carve-out are Ali's (2026-04-15 gitignore commits); the five later applications in the transcript era were Claude's calls under it, one explicitly offered back to Ali as overridable.*

**Decision.** Version control excludes anything re-creatable: Python venvs, data/repos/ (~2.1 GB), data/schesch-dataset/ (661 MB), caches, .claude/worktrees/, *.cpg.bin, *.log, the local-only docs/plans/m3.5-review.md review brief, the on-disk scenario tags produced by the R1 tagger, data/scenarios_expanded/ and data/results_expanded/, the seeded scenario data dirs, and the whole top-level /workspace/ scratch tree. Keynote (*.key) files are kept. Committed reports are the exception and stay tracked as evidence.

**Why.** Stated at founding as keeping the repo small, the datasets being re-cloneable from Zenodo, with Keynote files preserved per the user's standing rule. Each later application repeats the same test: the scenario JSONs and their tags are regenerable via load-dataset plus the tagger, the 60 expanded scenarios via select_materialize.py, the scenario dirs from a seed — so the canonical convention (data gitignored, reports/results.* kept) is mirrored, and the call was flagged to Ali as overridable. /workspace/ additionally held a CPG whose `bin1` suffix escaped the existing `*.cpg.bin` pattern and a `mergedataset` clone that is its own git repo (would commit as a broken gitlink) carrying GPL-3.0 content the gitignore already documents as kept out.

**Status.** adopted.

**Source.** `preA:pre-commits-02`, `preA:pre-commits-62`, `a:20b53f98-15`, `a:e1df1610-15`, `a:bfc672b4-19`, `a:5c9bc50d-01`, `a:42acccac-03` · Artifacts: `f764605`, `675bafd`, `0bdf979`, `cbac926`, `7086844`, `b1793e5`, `.gitignore`

> Gitignored to keep repo small:
>
> — `2026-04-15_pre-commits.txt:15`

> I mirrored that: **gitignored `data/scenarios_expanded/` + `data/results_expanded/`**
>
> — `2026-05-20_e1df1610.txt:858`

> added top-level `/workspace/` to [.gitignore](.gitignore). It contained only scratch that must not be committed
>
> — `2026-07-08_5c9bc50d.txt:23`

### <a id="d-342"></a>D-342 — Root-level docs are authoritative; superseded material is archived, never deleted

`2026-04-16 → 2026-07-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: Sources split between 'ali' and 'unclear': the never-delete/archive rule is recorded in the transcript era as a CLAUDE.md standing rule and the 2026-06-24 banner call was Ali's, while the plan-era archive commits record no explicit actor.*

**Decision.** Authoritative documentation lives at repo root — README.md (overview + docs map), ARCHITECTURE.md, STATUS.md, CLAUDE.md, later THREATS_TO_VALIDITY.md — replacing outdated per-project READMEs. Superseded designs and completed working documents are moved to docs/historical/ or kept in place under an explicit marker rather than deleted: the pre-revert RefMerge architecture went to docs/historical/, the obsolete temp-git-repo sketch stayed below an OBSOLETE marker, the finished Stage-C handoff was committed with a COMPLETED banner, execution-sequence.md is to move to docs/historical/ once its four plans complete or are abandoned, and docs/historical/ itself is left untouched by later renames. STATUS and THREATS are maintained as "what is, not what should be".

**Why.** Superseded designs are kept for thesis writing, and keeping the obsolete sketch below a marker preserves M0-reasoning traceability; the Stage-C handoff was committed because its sibling p1-stage-a-handoff.md is already tracked as an audit-trail record, with the banner added so it cannot be misread as live work. docs/historical/ is preserved untouched per a CLAUDE.md standing rule. Only broken duplicates, empty dirs and regenerable Joern temp output were actually deleted.

**Status.** adopted. Supersedes: *semantic_merge_driver/ARCHITECTURE.md as authoritative design*.

**Source.** `preB:pre-commits-05`, `preA:pre-commits-03`, `preA:pre-commits-38`, `preB:pre-commits-38`, `a:fb0fa5c5-47`, `preA:pre-execution-sequence-26`, `a:dc3bc182-sub-sub-agent-a74c7a-10` · Artifacts: `c7fc7e1`, `976e4b0`, `e3094ce`, `docs/historical/ARCHITECTURE-refmerge.md`, `STATUS.md`, `CLAUDE.md`, `THREATS_TO_VALIDITY.md`, `outputs/p1-stage-c-adjudication-handoff.md`

> Adds root-level docs aligned to declared source of truth (source code +
>
> — `2026-04-15_pre-commits.txt:32`

> Archived (superseded designs, kept for thesis writing):
>
> — `2026-04-15_pre-commits.txt:46`

> Its sibling `p1-stage-a-handoff.md` is tracked as an audit-trail record, so committing it is consistent
>
> — `2026-06-24_fb0fa5c5.txt:62`

### <a id="d-343"></a>D-343 — Naming and checklist conventions for adding a strategy

`2026-04-16` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

**Decision.** The RefMerge architecture plan fixes conventions for new detection work: strategies at strategies/<tool>_strategies/<detection_type>.py with classes named <Tool><DetectionType>Strategy, tests at tests/test_<strategy_name>.py with data under tests/data/<category>/, Joern CPG queries in scala_queries/<strategy_name>.sc rather than inline strings in Python; and any new step follows the nine-point §7.4 procedure (read the architecture doc and interfaces, check driver and plugin_loader, implement as a MergeStrategy subclass, add test scenarios, add error handling and timeouts, run the full suite, record metrics and latency, compare against the previous step before proceeding).

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted. S12 (2026-07-26): three of the four conventions demonstrably govern the tree — layout strategies/<tool>_strategies/<detection_type>.py holds for all seven lanes, classes are named <Tool><DetectionType>Strategy (JoernInfiniteLoopStrategy, RM2RenameConflictStrategy, …), tests are tests/test_<strategy>.py. The scala-queries-in-.sc clause did not survive: infinite_loop.sc is unwired (query inline in the lane) and later Joern lanes inline their queries.

**Source.** `preA:pre-architecture-refmerge-21`, `preA:pre-architecture-refmerge-22`, `preA:pre-architecture-refmerge-12` · Artifacts: `scala_queries/`, `strategies/`, `tests/data/`

> ### 7.3 File Naming Conventions
>
> — `2026-04-16_pre-architecture-refmerge.txt:902`

> ### 7.4 When Implementing a New Step
>
> — `2026-04-16_pre-architecture-refmerge.txt:910`

> Move Scala queries from inline strings to `scala_queries/*.sc` files
>
> — `2026-04-16_pre-architecture-refmerge.txt:627`

### <a id="d-344"></a>D-344 — Enabled strategies are configured in YAML, not hardcoded and not env vars

`2026-04-16 → 2026-04-22` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

**Decision.** Strategy selection moves out of driver.py into config/strategies.yaml, which is the single source of truth for enabled strategies and also carries merge backend configuration; it is loaded through a new core/config.py with no environment variables, and the hardcoded `strategies=["JoernInfiniteLoop"]` literal is removed from driver main(). The same Step-0 cleanup also required requirements.txt to list the actual dependencies.

**Why.** The hardcoded strategy list made the second implemented strategy unreachable.

**Status.** adopted. Supersedes: *hardcoded strategies=["JoernInfiniteLoop"] literal in core/driver.py*.

**Cross-theme.** *duplicates* → [D-086](#d-086) — Same decision recorded from two sides (repo convention vs driver implementation). Kept separate, cross-linked; detection's is the implementation record.

**Source.** `preB:pre-architecture-refmerge-21`, `preA:pre-commits-13` · Artifacts: `044051f`, `config/strategies.yaml`, `core/config.py`, `requirements.txt`

> config/strategies.yaml: single source of truth for enabled strategies
>
> — `2026-04-15_pre-commits.txt:128`

> strategies=["JoernInfiniteLoop"] literal that made the second
>
> — `2026-04-15_pre-commits.txt:131`

> - Update `config/strategies.yaml` to include merge backend configuration
>
> — `2026-04-16_pre-architecture-refmerge.txt:404`

### <a id="d-345"></a>D-345 — Each integration phase is one branch and one PR with explicit acceptance criteria

`2026-04-21 → 2026-04-25` · **superseded** · `[recon]` · corroboration: single-pass · confidence: medium · actors: ali

**Decision.** The Mergiraf and Spork integrations are executed as clean tracked incremental steps: each phase is a single branch and a single reviewable commit/PR with explicit acceptance criteria, work stops between phases for re-evaluation, and rollback is `git revert` of the merge commit or dropping the branch (for Spork S2, an env-flag flip with no code change).

**Why.** Big-bang merges had already been rejected once — this is stated as why the prior RefMerge/Mergiraf architecture was reverted.

**Status.** superseded. Superseded by [D-361](#d-361) — Programme work commits directly to main, not on feature branches.

**Source.** `preB:pre-mergiraf-integration-08`, `preA:pre-spork-driver-integration-16` · Artifacts: `CLAUDE.md`, `docs/plans/spork-driver-integration.md`

> **Clean tracked incremental steps.** Each phase is one reviewable commit / PR, not a big-bang merge.
>
> — `2026-04-21_pre-mergiraf-integration.txt:24`

> (This is *why* the prior RefMerge/Mergiraf architecture was reverted;
>
> — `2026-04-21_pre-mergiraf-integration.txt:24`

> Each phase is **one branch, one PR**, with explicit acceptance criteria. Stop between phases; re-evaluate.
>
> — `2026-04-25_pre-spork-driver-integration.txt:97`

### <a id="d-346"></a>D-346 — A new tool adapter phase adds only new files; the evaluation core is untouched

`2026-04-21 → 2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** The first phase of a tool integration (Mergiraf P1, Weave W1) adds only new files — the adapter, its tests, and one config/tools.yaml entry — and must not edit comparator.py, metrics.py, runner.py or plugin_loader.py; rollback is deleting the adapter file and the tools.yaml entry.

**Why.** The plugin loader auto-discovers adapters via `pkgutil.walk_packages()`, so no wiring edits are needed; this is the smallest possible change that produces a new tool row in the current reports, and removing the two additions restores prior behaviour exactly.

**Status.** adopted. S12 (2026-07-26): held — the commit introducing both comparator adapters (e334cb3) adds src/tools/mergiraf.py, src/tools/weave.py, their tests and one config/tools.yaml block, and touches none of comparator.py, metrics.py, runner.py or plugin_loader.py.

**Cross-theme.** *depends-on* → **no counterpart entry exists** — No entry owns the comparator's pkgutil.walk_packages() auto-discovery (searched all themes for plugin_loader/auto-discovery). The nearest architectural statement, scope-architecture/[D-003](#d-003), is driver-side, not the comparator loader. The mechanism lives only in code.

**Source.** `preA:pre-mergiraf-integration-08`, `preA:pre-weave-integration-22` · Artifacts: `merge-tool-comparison/src/tools/mergiraf.py`, `merge-tool-comparison/src/tools/weave.py`, `merge-tool-comparison/config/tools.yaml`

> **Files NOT touched:** `comparator.py`, `metrics.py`, `runner.py`, `plugin_loader.py`. The plugin loader auto-discovers the new adapter via `pkgutil.walk_packages()`.
>
> — `2026-04-21_pre-mergiraf-integration.txt:79`

> Removing `src/tools/weave.py` and the `config/tools.yaml` entry restores prior behaviour exactly.
>
> — `2026-04-25_pre-weave-integration.txt:249`

### <a id="d-347"></a>D-347 — Each plan file is independently gated and owns its components alone

`2026-04-25 → 2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

*Actors note: Sources disagree: the language_detect ownership transfer is recorded as Ali's, the other two plan-era decisions record no actor.*

**Decision.** Plan documents are kept modular: Spork's promotion stays in its own spork-driver-integration.md rather than becoming a Mergiraf P7 or Weave W6 sub-phase; a component has exactly one owning phase (language_detect.py moved from S2 to R4a); and a documentation block that another plan owes is deferred until its gate resolves rather than written speculatively (mergiraf-integration.md's "3b Tier C outcome" subsection waits for ISSUES.md #2 to reach `resolved`).

**Why.** Spork's promotion has different gates (ISSUES.md #2 resolution), different scope (Java-only) and a different dispatch axis (language, not just cluster), so burying it would mix concerns and hide the language-axis decision; language_detect.py was reassigned so it has a single owner; the deferred outcome block is tied to the resolved-status transition, which did not happen.

**Status.** adopted. Supersedes: *language_detect.py owned by S2*; *Phase 3b.5 requirement to append a '3b Tier C outcome' block to mergiraf-integration.md*.

**Source.** `preA:pre-spork-driver-integration-15`, `preB:pre-commits-19`, `preA:pre-comparator-3b-ast-normalize-27` · Artifacts: `docs/plans/spork-driver-integration.md`, `docs/plans/mergiraf-integration.md`, `core/language_detect.py`

> **Why a separate plan file rather than a sub-phase of the Mergiraf or Weave plans?** Because Spork's promotion has different gates (ISSUES.md #2 resolution), different scope (Java-only), and a different dispatch axis (language, not just cluster).
>
> — `2026-04-25_pre-spork-driver-integration.txt:228`

> ownership transferred from S2 to R4a (single owner).
>
> — `2026-04-15_pre-commits.txt:184`

> `mergiraf-integration.md §Phase 3.5` outcome block also deferred — to be added when (and if) ISSUES.md #2 reaches `resolved`.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:530`

### <a id="d-348"></a>D-348 — A commit fixes the docs it stales; wrong claims are retracted, out-of-scope staleness is flagged

`2026-05-06 → 2026-07-02` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Claude drove the updates and corrections; two sources record 'joint' because Ali ruled the P6 ordering and approved the docstring fix, and one plan-era correction records no actor.*

**Decision.** When a change makes a tracked document stale, the same commit updates it (rm2-integration.md's "R1, R2 pending" was corrected inside the R2 commit; the P6 doc-consistency sweep across STATUS, README ×2 and ARCHITECTURE ×3 landed in the #29 closing commit). Claims found to be wrong are retracted explicitly rather than quietly reworded — the recon doc's `-bd` flag claim was withdrawn after verification, the generator docstring's "strict-wins: 6" was corrected to 3, the hardcoded "v1" report header was fixed before the v2 write-ups. Staleness discovered outside the change's scope is flagged rather than fixed in it.

**Why.** The doc "still says 'R1, R2 pending' — stale now", and R3 had already been marked done there the same way; P6 "belongs in the same commit-wave as the #29 close-out ... the natural 'everything is now consistent' pass". The strict-win correction was forced by arithmetic on the committed data (six is impossible when Spork misses only 5 cases, 2 of them shared), and the `-bd` retraction by running RefactoringMiner -h in both images. The STATUS headline-number staleness was flagged instead of fixed because it was genuine but out of scope, and flagging keeps the change scoped rather than expanding it.

**Status.** adopted.

**Source.** `a:20b53f98-28`, `a:20b53f98-17`, `a:fb0fa5c5-41`, `a:3302d287-01`, `a:bfc672b4-42`, `preA:pre-rm2-vs-rm3-differences-04` · Artifacts: `2b95aa3`, `45a87e6`, `5290434`, `docs/plans/rm2-integration.md`, `docs/plans/rm2-integration-recon.md`, `STATUS.md`, `README.md`, `ARCHITECTURE.md`

> But `rm2-integration.md` still says "R1, R2 pending" — stale now. Updating it for consistency (R3 was marked done there the same way).
>
> — `2026-05-18_20b53f98.txt:206`

> I noticed a genuine out-of-scope doc staleness while regenerating the report — flagging it rather than expanding this change.
>
> — `2026-05-18_20b53f98.txt:212`

> Six is impossible: Spork only misses 5 cases total, 2 shared.
>
> — `2026-05-27_3302d287.txt:42`

### <a id="d-349"></a>D-349 — Committed reports_* directories are preserved evidence; new runs get their own directory

`2026-05-06 → 2026-07-03` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Mostly Claude's calls; the FINDINGS.md style requirement was Ali's instruction and one plan-era source records no actor.*

**Decision.** Every experimental run writes into its own reports_* directory and the committed outputs there are treated as preserved evidence rather than build products: the expanded corpus went to data/scenarios_expanded/, data/results_expanded/ and reports_expanded/ leaving the canonical artifacts untouched and reported separately; when results.csv is regenerated, results.json and results.tex are regenerated in the same commit so no tracked report is left stale; the post-3d results.csv was committed as the honest interim state; both the generator and its 1.78 MB standalone HTML output are committed following the pilot pattern; a FINDINGS.md follows the house style of reports_migrate_decl/FINDINGS.md; and committed sample fixtures are not regenerated when regeneration is byte-identical.

**Why.** reports/results.csv is a preserved thesis artifact and the expanded set is deliberately tool-discriminating, so conflating it with the canonical 50 would misreport; results.json and .tex "are also tracked and would be left stale" and ISSUES #23 explicitly covers JSON/LaTeX. The pilot committed both generator and HTML, so that pattern is followed. Re-running the toy fixtures on RM 2.4.0 produced diff-exit-0 identical output, so there was nothing to update. Tier D's results were committed as interim because the transforms are conservative and no semantic-change risk surfaced across 82 tests plus n=50 spot-checks.

**Status.** adopted.

**Source.** `a:e1df1610-11`, `a:20b53f98-16`, `b:7b3b2669-08`, `a:0e14484d-07`, `preA:pre-comparator-3d-extended-ast-transforms-21`, `preA:pre-rm2-vs-rm3-differences-10` · Artifacts: `merge-tool-comparison/reports_expanded/`, `merge-tool-comparison/reports/results.csv`, `merge-tool-comparison/reports/results.json`, `merge-tool-comparison/reports/results.tex`, `merge-tool-comparison/reports_rm2_recall/FINDINGS.md`, `86d8a6c`, `docs/plans/rm2-recon-samples/toy-rename.json`

> outputs to `data/results_expanded/` + `reports_expanded/`, leaving the canonical artifacts untouched
>
> — `2026-05-20_e1df1610.txt:749`

> `results.json` and `.tex` are also tracked and would be left stale (ISSUES #23 explicitly covers JSON/LaTeX too). Regenerating all formats
>
> — `2026-05-18_20b53f98.txt:202`

> `reports/results.csv` post-3d Tier D committed as the current honest interim state.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:430`

### <a id="d-350"></a>D-350 — Findings, deferrals and deviations go into durable artifacts, not just the commit message

`2026-05-14 → 2026-07-22` · **adopted** · `[mixed]` · corroboration: both · confidence: high · actors: ali

*Actors note: Three sources record Ali (the "Doc + commit" decision and both 2026-07-22 run-note instructions); the ISSUES #26 deferral tracker is recorded as joint.*

**Decision.** Anything that would otherwise survive only in a commit message or in chat is written into a durable artifact: the γ diagnostic observations went into docs/plans/stage-gamma-fp-diagnostic.md as well as the commit message; a publishable finding dropped by a scope decision was recorded as ISSUES.md #26 (Low, deferred) with the concrete path to produce it later; and run-time deviations from a plan are recorded in the run notes — the derived-target env-gate replacement as a paste-time patch to the kickoff prompt, the Docker image provisioning split as a one-sentence reasoned deviation-within-intent — with no amendment to the plan document itself.

**Why.** The acceptance wording had said "in the commit message"; the doc was added for permanence per Ali's "Doc + commit" decision. The ISSUES entry was created because R0 recon had designated the recall delta a publishable finding, the scope decision killed it, and no deferral tracker existed anywhere in ISSUES.md or STATUS.md — "a previously-planned publishable finding was silently dropped with no tracker." No reason was recorded for choosing run notes over a plan amendment for the two 2026-07-22 deviations.

**Status.** adopted.

**Source.** `preA:pre-commits-51`, `a:20b53f98-23`, `a:68c24033-04`, `a:68c24033-08` · Artifacts: `10c8a54`, `docs/plans/stage-gamma-fp-diagnostic.md`, `merge-tool-comparison/ISSUES.md`, `eabaddd`, `merge-tool-comparison/reports_detectors/whole_driver_flagon/RUN_NOTES.md`

> A previously-planned publishable finding was silently dropped with no tracker.
>
> — `2026-05-18_20b53f98.txt:253`

> also in stage-gamma-fp-diagnostic.md for permanence per user's "Doc +
>
> — `2026-04-15_pre-commits.txt:888`

> Record the split in your run notes as a one-sentence reasoned deviation-within-intent of the build-on-instance standing rule (drift-risk images shipped, pinned images built). No amendment.
>
> — `2026-07-22_68c24033.txt:86`

### <a id="d-351"></a>D-351 — Work lands as small ordered commits, each reviewable and each leaving the tree green

`2026-05-15 → 2026-06-09` · **adopted** · `[mixed]` · corroboration: both · confidence: high · actors: claude

*Actors note: Two plan-document sources record no actor ('unclear'); the two attributed sources are Claude's.*

**Decision.** Multi-part work is decomposed into small commits landed in order — six for Tier D (3d.1–3d.6), eleven for Tier E — each one reviewable, each leaving the tree in a working state with the full suite re-run per phase. A true bug fix is separated out and lands first, ahead of any new feature commit. An uncommitted working tree is split along work-stream lines rather than committed as one mixed commit (weave / research / presentation).

**Why.** Each phase is one reviewable commit leaving the tree in a working state; the D.1 fix "lands FIRST as a separate small commit, before any new transforms" for easier rollback isolation if the tier has issues, and the D.1 risk mitigation requires re-running the full suite per phase. The three-way split was chosen because the uncommitted work comprised three independent work streams.

**Status.** adopted.

**Source.** `preA:pre-comparator-3d-extended-ast-transforms-16`, `preA:pre-comparator-3e-tier-e-transforms-19`, `preA:pre-comparator-3e-tier-e-transforms-02`, `a:42acccac-01` · Artifacts: `99a5f90`, `9333692`, `ac9114e`, `1eff174`, `9e90b23`, `1c6eb87`, `a86b560`, `8868ec6`, `20b6e45`

> Six small commits, landed in order. Each phase is one reviewable commit; each leaves the tree in a working state.
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:135`

> It lands FIRST as a separate small commit, before any new transforms. Easier rollback isolation if Tier E has issues.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:128`

> Clean scan, clear convention. Three independent work streams — I'll make three commits.
>
> — `2026-06-09_42acccac.txt:17`

### <a id="d-352"></a>D-352 — Test-suite conventions: no redundant integration tests, keep extra coverage, scope collection

`2026-05-15 → 2026-07-03` · **adopted** · `[mixed]` · corroboration: mixed · confidence: medium · actors: claude

*Actors note: One plan-era source (Tier E's test plan) records no actor; the rest are Claude's calls.*

**Decision.** New transform tiers add unit tests only where the contract is not already covered — Tier E shipped 30 unit tests and zero new integration tests because Tier C's 3-test wiring contract plus Tier D's 2 tests already cover it. Tests that the plan said to migrate are kept as-is when that leaves more coverage, even at the cost of overshooting the planned suite size (82 tests versus a 74–80 target, 16 new instead of 23). Logic that is hard to test through `main()` is extracted into a standalone testable function first. Pytest collection is scoped to `tests/` so cloned upstream repositories under data/repos/ and data/schesch-dataset/ stop contributing test files.

**Why.** Tier E's transforms reach `contents_match` via the same Tier 3 path, so the existing wiring tests already cover the contract. The suite overshoot was accepted as "net positive — more coverage retained". Collection scoping was proposed because the cloned corpus produced 16 collection errors that "are noise but mask real failures", and was then executed on 2026-07-03 (commit c9ca9f8) when collection picked up cloned repos' own tests.

**Status.** adopted. Supersedes: *§7 plan that Tier C paren/else-if tests migrate to D.1/D.2 and that Tier D adds 23 unit tests for a 74-80 test suite*.

**Cross-theme.** *depends-on* → [D-450](#d-450) — other_uid a:20b53f98-22 landed there: the clearest instance of the add-a-test-for-what-you-changed convention. Mirror: other:0.

**Source.** `preA:pre-comparator-3e-tier-e-transforms-16`, `preA:pre-comparator-3d-extended-ast-transforms-20`, `a:8740dbd3-25`, `a:ce56e78d-13`, `a:7b3b2669-08` · Artifacts: `merge-tool-comparison/tests/test_ast_normalize.py`, `merge-tool-comparison/tests/test_comparator.py`, `merge-tool-comparison/pyproject.toml`, `merge-tool-comparison/tools/detect_validate.py`, `c9ca9f8`

> already cover Tier E's contract — its transforms reach `contents_match` via the same Tier 3 path.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:283`

> slightly over because some Tier C `strip_redundant_parens` and `flatten_else_if` tests stayed as-is rather than migrating; net positive — more coverage retained
>
> — `2026-05-15_pre-comparator-3d-extended-ast-transforms.txt:419`

> Collection picked up cloned repos' own tests — scope to `tests/`:
>
> — `2026-07-03_7b3b2669.txt:68`

### <a id="d-353"></a>D-353 — Generated diagrams stay scratch unless a file is asked for, then self-contained under docs/

`2026-05-18 → 2026-06-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: the 2026-05-18 refusal to persist the diagram was Claude's, while the file-graph decisions are recorded as joint (Ali asked for a graph, judged html/css the better medium and asked for a browsable path).*

**Decision.** A diagram generated in conversation is not written into any tracked document — the Mermaid project-state diagram went to /tmp only and nothing was committed. When Ali does ask for a browsable file, the artifact is saved as a fully self-contained page with its own light/dark colours and no external assets (docs/driver-file-graph.html), whose nodes are real source files with verbatim snippets and whose edges are actual import/call/data-flow links.

**Why.** CLAUDE.md says never to create or modify docs unless asked, and the request was "generate a diagram", not "add it to X". When the file was asked for, the reason given was that the rendered diagrams are inline chat widgets that do not exist as files, so a standalone self-contained page is what opens directly in any browser.

**Status.** adopted.

**Source.** `a:20b53f98-25`, `a:ce56e78d-16`, `b:ce56e78d-15` · Artifacts: `/tmp/project-state.mmd`, `/tmp/project-state.svg`, `docs/driver-file-graph.html`

> I deliberately did not write it to a document because CLAUDE.md says never to create/modify docs unless you ask
>
> — `2026-05-18_20b53f98.txt:406`

> The diagrams I rendered are inline chat widgets — they don't exist as files yet. Let me save the interactive file-graph as a standalone, self-contained HTML page (its own colors, light + dark) that opens directly in any browser.
>
> — `2026-06-24_ce56e78d.txt:167`

### <a id="d-354"></a>D-354 — The taxonomy is duplicated as a parity-tested copy, not imported across subprojects

`2026-05-18` · **adopted** · `[mixed]` · corroboration: both · confidence: medium · actors: unclear

*Actors note: Sources disagree: the plan-era decision records no actor; the transcript-era restatement of the parity lock is Claude's. The second source is placed primary in another theme and is cited here only as confirmation.*

**Decision.** merge-tool-comparison/src/evaluation/categorizer.py holds its own copy of the driver's cluster taxonomy rather than importing it from semantic_merge_driver/, with tests/test_categorizer.py::test_taxonomy_parity failing on drift; `categorizer.cluster_of` is kept parity-locked to `RefactoringClusterClassifier.cluster(base, ours, theirs)`.

**Why.** So that a "tool X wins in cluster C" result computed offline in the comparison project is directly actionable by the runtime router, which can compute C from the same inputs. No reason was recorded in the plan source for preferring a copy over a cross-project import; the parity test is what guards the duplication.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-255](#d-255) — other_uid a:dc624d63-03 is cited there: the parity-lock is the mechanism that keeps the duplicated taxonomy honest.

**Source.** `preA:pre-rm2-integration-02`, `a:dc624d63-03` · Artifacts: `merge-tool-comparison/src/evaluation/categorizer.py`, `merge-tool-comparison/tests/test_categorizer.py`, `semantic_merge_driver/core/refactoring_classifier.py`

> Taxonomy is a parity-tested copy in `merge-tool-comparison/src/evaluation/categorizer.py` (not a cross-project import).
>
> — `2026-04-22_pre-rm2-integration.txt:6`

> `categorizer.cluster_of` is a parity-locked copy of that exact function (`test_taxonomy_parity` fails on drift).
>
> — `2026-05-18_dc624d63.txt:27`

### <a id="d-355"></a>D-355 — Commit and push only on explicit instruction, and only after a review pass

`2026-05-19 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: Sources disagree: two record Claude stating or applying the standing rule, four record Ali instructing the review or authorising the push. The gate itself is Ali's.*

**Decision.** Claude does not commit or push on its own initiative: readiness questions are answered without committing, finished commits are left local ("ahead N of origin/main") until Ali asks, and the pre-push review belongs to Ali. Before any commit or push, a review pass is run — git state audited (tracked vs ignored, parallel commits), reported numbers re-verified against committed data, tests re-run, and for the S-D1 commits a five-area self-review (list integrity, script re-read, firewall audit, manifest/ISSUES coherence, GD1 number re-derivation from specs.csv). Pushing is preceded by verifying a clean tree and fast-forward status.

**Why.** Stated as the standing rule: "I commit/push only on explicit instruction"; commits were left unpushed because "that wasn't asked" and because "S-D1 precedent: pre-push review is yours". The pre-commit audit is justified by permanence — "this is going to the remote, so let me audit before touching anything permanent" — and numbers were re-verified "so the permanent issue is accurate".

**Status.** adopted.

**Source.** `a:bfc672b4-35`, `b:506d875b-14`, `b:f0d70a59-24`, `b:20b53f98-25`, `a:e1df1610-16`, `b:506d875b-10` · Artifacts: `cbac926`, `2b95aa3`, `eabaddd`, `cf59d37`, `1b99a6a`, `b40d26c`, `d5a202e..c14670a`, `7086844`

> Nothing is committed or pushed yet (you asked a readiness question, and the standing rule is I commit/push only on explicit instruction).
>
> — `2026-06-11_bfc672b4.txt:697`

> Tree clean, not pushed (S-D1 precedent: pre-push review is yours)
>
> — `2026-07-16_f0d70a59.txt:67`

> review you work again before commit and push
>
> — `2026-07-15_506d875b.txt:169`

### <a id="d-356"></a>D-356 — Presentation binaries are tracked, never renamed or deleted, and named by month precedent

`2026-06-09 → 2026-06-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Keynote and PowerPoint binaries are committed to the repo (both extensions are already tracked); a file that looks like a macOS Finder duplicate (`thesis_progress_late_may2026 3.key`) is committed unchanged in place rather than renamed, moved or dropped, with an offer to amend if the name was accidental. A second deck in the same month is named by the existing precedent (`thesis_progress_late_jun2026.pptx`, notes `next_presentation_notes_late_jun2026.md`) rather than rolling to the next month, and the deck build script reuses the previous version's helpers, palette and layout coordinates verbatim.

**Why.** `.key` and `.pptx` are already tracked, so committing new ones follows precedent; the " 3" file has no tracked base version, so it is not a duplicate of anything in the repo and committing it as-is honours the never-delete-`.key` rule. The deck name follows the `may2026`/`late_may2026` precedent, and v4's coordinates are proven to render cleanly, which substitutes for a pixel render that could not be done locally.

**Status.** adopted. Supersedes: *proposed name thesis_progress_jul2026*.

**Source.** `a:42acccac-02`, `a:42acccac-04`, `a:12c77ea5-05`, `a:12c77ea5-04` · Artifacts: `20b6e45`, `merge-tool-comparison/thesis_progress_late_may2026 3.key`, `presentation/thesis_progress_late_jun2026.pptx`, `presentation/build_deck_v5.py`

> `.key` and `.pptx` are both tracked already, so committing the new ones follows precedent.
>
> — `2026-06-09_42acccac.txt:15`

> There's no base `thesis_progress_late_may2026.key` tracked, so it's not a dup of anything in the repo — I committed it as-is (honoring the never-delete-`.key` rule).
>
> — `2026-06-09_42acccac.txt:40`

> Following the `may2026`/`late_may2026` naming precedent, the second June deck is `thesis_progress_late_jun2026.pptx`.
>
> — `2026-06-18_12c77ea5.txt:70`

### <a id="d-357"></a>D-357 — List the calls made without asking when committing on Ali's behalf

`2026-06-09` · **proposed** · `[chat]` · corroboration: single-pass · confidence: medium · actors: claude

**Decision.** When committing on the user's behalf, explicitly enumerate the judgement calls made without asking — here the `research/.DS_Store` exclusion and the spaced `.key` filename — with a stated remedy path ("rename or `git mv` it and I'll amend").

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** proposed. S12 (2026-07-26): not repo-checkable — the practice lives in session commit reports, no CLAUDE.md standing rule exists, and no artifact can settle whether later commits enumerated their unilateral calls. Stays a recommendation about working practice.

**Source.** `a:42acccac-05` · Artifacts: `8868ec6`, `20b6e45`

> Two things I decided rather than asked, flagging for your awareness:
>
> — `2026-06-09_42acccac.txt:37`

### <a id="d-358"></a>D-358 — Unreviewed and draft content is held out of commits and the omission is recorded

`2026-06-11 → 2026-06-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: the Stage-B exclusion was Claude's call, the resolution (review THREATS, exclude the draft, commit and push the rest) was Ali's ruling on options Claude put.*

**Decision.** Content Claude has not reviewed, and content whose labels are proposals rather than Ali's ruling, is excluded from a commit and the exclusion is reported: THREATS_TO_VALIDITY.md was left out of the Stage-B freeze commit because of a 98-line unreviewed pre-session edit, and at the later commit Ali ruled that THREATS be reviewed first and that everything be committed and pushed except hit_adjudications_draft.md, with the commit message recording the omission and ISSUES #29 staying in_progress.

**Why.** Claude would not fold a large pre-session edit it had not reviewed into a commit, so review came first; the adjudication draft is excluded because the labels are proposals, not Ali's ruling. Already-decided content (the ISSUES #28 entry) was allowed to ride along.

**Status.** adopted.

**Source.** `a:bfc672b4-18`, `a:bfc672b4-34` · Artifacts: `843e5f5`, `2354099`, `THREATS_TO_VALIDITY.md`, `hit_adjudications_draft.md`

> **THREATS_TO_VALIDITY.md was left uncommitted** — it has a 98-line pre-session edit I didn't review; worth a look when you're next in there.
>
> — `2026-06-11_bfc672b4.txt:393`

> fix header; commit and push everything but adjudication
>
> — `2026-06-11_bfc672b4.txt:733`

### <a id="d-359"></a>D-359 — STATUS/THREATS disclosure of new work waits for its planned stage gate

`2026-06-12 → 2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** Where a plan schedules when a result becomes public in the self-assessment docs, the docs stay deliberately silent until that gate: STATUS.md and THREATS_TO_VALIDITY.md were left untouched through Stages A and B and updated with measured R1/R2 values only when Stage C triggered it, and STATUS.md says nothing about the new detector lane because that disclosure is scheduled for S-D6.

**Why.** The plan specified Stage C as the trigger for the STATUS/THREATS update, and the S-D plan schedules lane disclosure at S-D6; the Stage-C edit was layered over Ali's uncommitted edits without touching them.

**Status.** adopted. Supersedes: *STATUS/THREATS deliberately left untouched during Stages A and B*.

**Cross-theme.** *depended on by* ← [D-388](#d-388) (see the reconciliation note there)

**Source.** `a:bfc672b4-40`, `b:f0d70a59-23` · Artifacts: `STATUS.md`, `THREATS_TO_VALIDITY.md`, `merge-tool-comparison/ISSUES.md #29`

> Updated per the plan's Stage-C trigger: [STATUS.md](STATUS.md) (strategies table + measured soundness paragraph), [THREATS_TO_VALIDITY.md](THREATS_TO_VALIDITY.md) (constructive-side bullet + new summary row 14 — layered carefully over your uncommitted edits, which I did not touch
>
> — `2026-06-11_bfc672b4.txt:642`

> STATUS.md correctly says nothing yet — that disclosure is scheduled for S-D6 per the plan
>
> — `2026-07-16_f0d70a59.txt:262`

### <a id="d-360"></a>D-360 — Large raw result caches are committed as auditable evidence, once final

`2026-06-16 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: Sources disagree: the originating call is Ali's (Claude put keep-vs-ignore to him and he ruled "keep full/raw_results.json"), while the four later applications are Claude following that precedent, so they record 'claude'.*

**Decision.** Multi-megabyte raw_results.json caches are tracked rather than gitignored: the 9.9 MB reports_detection/full/raw_results.json was kept in the commit on Ali's ruling, and that became the standing precedent — Stage-C's tracked caches are cited when later tune runs and the S-D7 rerun commit their raw JSON caches, excluding only transient queue-claim directories. The timing rule is that only the final cache lands: the 27 MB partial cache was held out of the 2026-06-24 checkpoint commit (which carried durable code plus the 21 KB human-readable partial reports) and the 9.7 MB phase3/inputs directory was deferred to one commit at end of session. The open commit-or-ignore question raised about reports_whole_driver/raw_results.json in the 2026-06-24 review was answered this way the same day.

**Why.** Keeping the cache "makes the post-fix run resumable and the numbers auditable", consistent with the repo policy of keeping reports_* as evidence. Holding a partial cache back is argued from the opposite side of the same test: the current file is a partial cache that the run overwrites/grows, so committing it now "would put a throwaway blob in history"; phase3/inputs is deferred because it is large and regenerates deterministically.

**Status.** adopted.

**Source.** `b:bfc672b4-34`, `a:fb0fa5c5-06`, `a:ce56e78d-14`, `b:f0d70a59-13`, `a:06ec13eb-08`, `a:9e4b6896-06` · Artifacts: `reports_detection/full/raw_results.json`, `reports_whole_driver/raw_results.json`, `0ec0ea3`, `597e535`, `a1f017f`, `9b21914`

> I'd keep it: it makes the post-fix run resumable and the numbers auditable.
>
> — `2026-06-11_bfc672b4.txt:707`

> But the current `raw_results.json` is a **27 MB partial cache** that tonight's run overwrites/grows — committing it now would put a throwaway blob in history.
>
> — `2026-06-24_fb0fa5c5.txt:327`

> S-D5 precedent: caches are tracked. Committing everything except transient queue-claim dirs (logs are gitignored already):
>
> — `2026-07-22_06ec13eb.txt:114`

### <a id="d-361"></a>D-361 — Programme work commits directly to main, not on feature branches

`2026-06-20 → 2026-07-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Work in the ISSUES #29 and #30 programmes is staged and committed directly to `main` in incremental commits referencing the issue number, with unrelated working-tree files (presentation decks, handoff documents) deliberately left alone; input dumps such as phase1/inputs/ are tracked in git.

**Why.** Stated as following the repo's own conventions and precedent: the ISSUES #29 direct-to-main convention, then "the whole #30 program has committed directly to main" and "the entire #30 lineage does", with the brief directing #30-referenced commits; S1 having committed the g0_pilot input dumps is the precedent for tracking phase1/inputs/.

**Status.** adopted. Supersedes: [D-345](#d-345) — Each integration phase is one branch and one PR with explicit acceptance criteria.

**Source.** `a:0e14484d-09`, `a:788e483b-05`, `a:9e4b6896-33` · Artifacts: `86d8a6c`, `3f817b9`, `b604bfc`, `a8734c7`, `merge-tool-comparison/ISSUES.md`

> following the repo's `ISSUES #29` direct-to-main convention; leaving the unrelated `presentation/` and handoff files alone
>
> — `2026-06-20_0e14484d.txt:199`

> S1 committed the g0_pilot input dumps, so tracking `phase1/inputs/` follows precedent, and the whole #30 program has committed directly to `main`
>
> — `2026-07-09_788e483b.txt:206`

> This program commits directly to `main` (the entire #30 lineage does), and the brief directs `#30`-referenced commits.
>
> — `2026-07-11_9e4b6896.txt:117`

### <a id="d-362"></a>D-362 — Review-flagged cleanups batched as one low-risk pass, awaiting a ruling

`2026-06-24 → 2026-07-16` · **proposed** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** The 2026-06-24 project review proposed a batch of low-risk cleanups to run in one pass — delete dead `semantic_merge_driver/strategies/abstract_strategy.py` and the unwired `scala_queries/infinite_loop.sc`, remove debug prints, refresh stale headers (STATUS test count 122→151 plus date, `detect_validate.py` "four strategies"→five) — while decision-bearing items were to be handled separately, and separately proposed a reproducibility manifest mapping each headline claim → command → `reports_*` directory. A later review added the stale `detector_tune_run.py` module docstring to the same queue.

**Why.** The batched items are low-risk and fast and "remove the things a reviewer would flag first", whereas the routing flip and the raw_results.json question carry decisions. The deletions are justified as dead code (abstract_strategy.py is 0 LOC and imported nowhere; the .sc query is superseded by the inline `_QUERY`), the header refreshes because collection now shows 151 tests and all five detectors run, and the docstring fix because a reader adding a fourth lane would trust the stale top-of-file contract and reintroduce the vacuous-run gap the smoke guard exists to prevent.

**Status.** proposed. S12 (2026-07-26): still awaiting the ruling — strategies/abstract_strategy.py and scala_queries/infinite_loop.sc both still exist, and detect_validate.py still says 'four strategies' (:3,:20) — though that last item was separately ruled a frozen-instrument non-fix in ISSUES.md #31, the deletion batch itself was never answered.

**Source.** `a:ce56e78d-15`, `a:ce56e78d-12`, `b:ce56e78d-17`, `a:acf7e1d0-sub-agent-a88268-08`, `a:ce56e78d-05` · Artifacts: `semantic_merge_driver/strategies/abstract_strategy.py`, `scala_queries/infinite_loop.sc`, `STATUS.md`, `merge-tool-comparison/tools/detect_validate.py`, `merge-tool-comparison/tools/detector_tune_run.py`

> Want me to do the safe cleanups (2's debug-print removal, 3, 4, 6) in one pass, and handle 1 and 5 separately since they carry decisions?
>
> — `2026-06-24_ce56e78d.txt:149`

> **Delete** `abstract_strategy.py` (dead) and `scala_queries/infinite_loop.sc` (unwired) — or confirm intent.
>
> — `2026-06-24_ce56e78d.txt:144`

> **Write a reproducibility manifest.** 12 `reports_*` dirs exist; map each headline claim → command → report dir in one file.
>
> — `2026-06-24_ce56e78d.txt:41`

### <a id="d-363"></a>D-363 — Repo reviews inventory only real source and tag every file with one of six verdicts

`2026-06-24 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** A whole-repo state review inventories and sizes only real source files — excluding virtualenvs, worktrees, caches, build artifacts, the metals database and gitignored data such as the 113 workspace/*.cpg.bin Joern scratch dirs — giving ~4,744 LOC for the driver and ~7,736 for the comparator, and classifies every file it reads with one of six verdict tags: solid, partial, dated, dead, stale, dirty.

**Why.** The raw directory listing is dominated by worktrees and venv/build artifacts, which would swamp the primary source picture; the verdict tags are stated as grounded in reading the actual source. No reason was recorded for the six-tag vocabulary itself.

**Status.** adopted.

**Source.** `a:ce56e78d-09`, `a:ce56e78d-10`, `a:dc3bc182-sub-agent-a7bb0f-04` · Artifacts: `semantic_merge_driver/`, `merge-tool-comparison/`

> Verdict tags: **solid** (no action) · **partial** (works, narrow-by-design, documented) · **dated** (inconsistent with its peers) · **dead** (unused) · **stale** (content lag) · **dirty** (uncommitted).
>
> — `2026-06-24_ce56e78d.txt:75`

> let me inventory the actual source files (excluding venvs, worktrees, caches, gitignored data) and size them before reading.
>
> — `2026-06-24_ce56e78d.txt:55`

> The output includes many worktrees. Let me focus on the primary (non-worktree) files.
>
> — `2026-07-18_dc3bc182_sub-agent-a7bb0f.txt:15`

### <a id="d-364"></a>D-364 — Report-directory run.log is force-added despite the global *.log ignore

`2026-07-03` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** A report directory's run.log is force-included in the commit as an exception to the repository-wide `*.log` ignore pattern; logs inside a reports_* directory are treated as artifacts, not noise.

**Why.** The exclusion was noticed as silent, and precedent was checked before overriding: reports_whole_driver already has committed logs.

**Status.** adopted.

**Source.** `a:7b3b2669-10` · Artifacts: `merge-tool-comparison/reports_rm2_recall/`, `b194bb3`

> `run.log` was silently excluded by the global `*.log` ignore. Checking precedent (reports_whole_driver has committed logs):
>
> — `2026-07-03_7b3b2669.txt:102`

### <a id="d-365"></a>D-365 — Commit before running anything that snapshots HEAD

`2026-07-03 → 2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Code is committed before running a tool that captures the commit state: the tagger and its tests are committed before building the AWS deployment bundle, and the detector lane is committed before the tune harness runs.

**Why.** The bundle is built with `git archive HEAD`, so uncommitted files would not ship; committing the lane first makes the tune cache keys carry the true lane commit sha.

**Status.** adopted.

**Source.** `a:7b3b2669-09`, `a:f0d70a59-09` · Artifacts: `c9ca9f8`, `9f871b1`, `merge-tool-comparison/reports_detectors/tune_d1/runs.md`

> Committing the tool + tests so the bundle's `git archive HEAD` includes them.
>
> — `2026-07-03_7b3b2669.txt:70`

> Committing the lane first so the tune cache keys carry the true lane commit, then running.
>
> — `2026-07-16_f0d70a59.txt:53`

### <a id="d-366"></a>D-366 — Sessions hand off through committed artifacts only, never through chat

`2026-07-08 → 2026-07-15` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: One source (the taxonomy brief setting out the handoff rule) is recorded as Ali's; the rest are Claude's applications of it.*

**Decision.** State passes between sessions only through committed artifacts: prompts committed as files with marked slots ({PHASE1_TAGS}, {FROZEN_CODEBOOK}), a per-phase resumable cache keyed by custom_id, scenarios.csv, labels CSV and summary.txt under reports_taxonomy/, plus memory files (MEMORY.md and the per-topic memory notes) carrying non-obvious operational detail for the next stage. At a gate the user brings only summary stats, artifact paths and a ruling, and Claude reads the files from the repo; artifacts produced outside the tree are relocated into the artifacts directory where they belong; the protocol document itself is placed beside its existing precedent at repo-root outputs/. Stage state lives in the ISSUES entry with each session appending its close-out, writing sessions and implementation sessions never mix, and any protocol change after data exists must be a dated sanctioned amendment in the doc, never a silent edit.

**Why.** "Don't hand results back through chat — 500 units of output won't fit in a message and provenance suffers"; committed prompts let the thesis cite "labels produced by prompt X at commit Y with model Z". Tracking state in ISSUES means any future session can regenerate the next kickoff prompt from ISSUES plus the plan file alone, so "this conversation stops being a load-bearing artifact"; and the write-up citing committed FINDINGS means late implementation integrates as one new section without reopening finished chapters. The protocol was placed at repo-root outputs/ because the brief's path pointed at a directory that does not exist and that location sits beside the p1-plan precedent.

**Status.** adopted. Supersedes: *brief path merge-tool-comparison/outputs/taxonomy-protocol.md*.

**Cross-theme.** *depended on by* ← [D-339](#d-339) (see the reconciliation note there)

**Source.** `a:4c7b0828-14`, `a:cfe6365a-08`, `b:4c7b0828-34`, `b:788e483b-12`, `a:92a3e464-25`, `a:cfe6365a-17` · Artifacts: `merge-tool-comparison/reports_taxonomy/`, `merge-tool-comparison/prompts_taxonomy/`, `outputs/taxonomy-protocol.md`, `outputs/detector-cycle-plan.md`, `MEMORY.md`, `ISSUES #31`

> Don't hand results back through chat — 500 units of output won't fit in a message and provenance suffers.
>
> — `2026-07-06_4c7b0828.txt:713`

> **Track state in ISSUES, not in chat.** Open the detector-cycle issue (#31) with the stage checklist; each session appends its close-out there, same as #30 did.
>
> — `2026-07-06_4c7b0828.txt:1645`

> - Handoff between sessions is committed artifacts only: prompts committed as
>
> — `2026-07-08_cfe6365a.txt:49`

### <a id="d-367"></a>D-367 — Review finder agents return at most 6 conclusions as a bare JSON array

`2026-07-16 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

*Actors note: Sources disagree: the agent briefs are Claude's, one report-format brief is recorded as Ali's, and two record no actor.*

**Decision.** Each angle of a multi-angle code review is run by a finder agent under a fixed contract: return at most 6 candidate findings as a JSON array with keys file, line, summary, failure_scenario, and the final message is only the array (an empty array being the expected result when nothing qualifies); report conclusions, not file dumps, with no code excerpt longer than three lines. Angles are given an explicit method (for the removed-behaviour angle: for every line the diff deletes or replaces, name the invariant it enforced and verify the new code re-establishes it, with specific paths enumerated) and an explicit scope — findings must be actionable within the session's constraints, and untracked new files are added to every finder's scope by hand.

**Why.** Untracked files do not appear in `git diff`, so a diff-scoped review would have skipped the new lane and its test file entirely. The actionability scope is argued from the guardrails: the module deliberately avoids importing strategy classes to prevent loader double-registration, and the frozen-plan guardrail forbids changes to existing lanes, so a recommendation requiring those edits cannot be executed.

**Status.** adopted.

**Cross-theme.** *duplicated by* ← [D-457](#d-457) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-462](#d-462) — other_uid a:82dd479f-sub-sub-agent-aca92e-07 landed there: an instance of what the contract produces.

**Source.** `a:82dd479f-sub-sub-agent-a36a1c-02`, `a:82dd479f-sub-sub-agent-a46641-01`, `a:dc3bc182-sub-agent-a7bb0f-02`, `b:acf7e1d0-19`, `a:acf7e1d0-sub-agent-ad3e5a-01` · Artifacts: `scratchpad/sd4_diff.txt`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`

> Return up to 6 candidate findings as a JSON array with keys: file, line, summary, failure_scenario (quote the CLAUDE.md path and rule).
>
> — `2026-07-16_82dd479f_sub-agent-a36a1c.txt:7`

> You are reporting conclusions, not file dumps. No code excerpts longer than 3 lines.
>
> — `2026-07-18_dc3bc182_sub-agent-a7bb0f.txt:11`

> The two new files are untracked, so they don't appear in `git diff` — including them explicitly in every finder's scope.
>
> — `2026-07-16_acf7e1d0.txt:76`

### <a id="d-368"></a>D-368 — A convention violation counts only with the exact rule and the exact line quoted

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** The CLAUDE.md-conventions angle of a review may report a violation only if it can quote both the exact rule text from a CLAUDE.md file and the exact diff line breaking it; style preferences and spirit-of-the-doc inferences are excluded. The applicable rule files are those that both exist and are ancestors of the changed files — repo root, semantic_merge_driver/, merge-tool-comparison/ and ~/.claude/ are all checked, and in practice only the repo-root CLAUDE.md applied.

**Why.** Only clear violations of explicit rules count, and the exact-quote requirement is stated as the bar, with style preferences and spirit-of-the-doc inferences explicitly ruled out. No reason was recorded for restricting rule files to existing ancestors.

**Status.** adopted.

**Source.** `a:82dd479f-sub-sub-agent-a36a1c-01`, `a:acf7e1d0-sub-sub-agent-aaed4d-01`, `a:acf7e1d0-sub-sub-agent-aaed4d-02` · Artifacts: `CLAUDE.md`, `~/.claude/CLAUDE.md`

> Only flag when you can quote the exact rule AND the exact diff line breaking it. No style preferences, no spirit-of-the-doc inferences.
>
> — `2026-07-16_82dd479f_sub-agent-a36a1c.txt:5`

> only apply files that exist and are ancestors of changed files
>
> — `2026-07-16_acf7e1d0_sub-agent-aaed4d.txt:3`

> I reviewed the repo-root `CLAUDE.md` (the only applicable file — no `CLAUDE.md`/`CLAUDE.local.md` exists in `semantic_merge_driver/`, `merge-tool-comparison/`, or `~/.claude/`)
>
> — `2026-07-16_acf7e1d0_sub-agent-aaed4d.txt:23`

### <a id="d-369"></a>D-369 — Duplication is accepted rather than edit a frozen lane or diverge from the ABC

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** In the S-D detector work, duplication and cross-module private access are deliberately left in place rather than refactored: SignatureStaleCallStrategy keeps its own `_inconclusive`, its own `_declared_arities`, and its reaches into other lanes' private members (`self._rm2._run_rm2_pair`, `view._in_excluded`, `view._qualified_or_case`, the `_ipu` helpers); no shared RM2Runner is extracted and no `_FileView` helper is promoted to public. The test-side `_patch_rm2` is classified as a drift risk rather than a removable duplicate. The inherited `base_content: str = None` annotation is left uncorrected.

**Why.** Reusing `self._rm2._inconclusive` would emit the wrong strategy name and message; the existing declaration helpers return booleans with no arity, and adding arity or factoring a shared module-level helper would mean editing the frozen rename/text lanes, which the session guardrail forbids — so the duplication is "unavoidable within constraints, not a finding". The public-ish alternatives also cannot supply what the lane needs (`_rm2_renames` drops Add/Remove-Parameter records; `_FileView.occurrences()` cannot count arity). `_patch_rm2` patches a different method with different signature/return conventions, so it is a genuine near-duplicate rather than a droppable copy. The `base_content` annotation stays because consistency with the project ABC wins and the ABC itself is the offender.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-458](#d-458) — other_uid a:82dd479f-sub-sub-agent-aca92e-01 landed there: the accepted-idiom ruling is the same class of accepted cost.

**Source.** `b:acf7e1d0-13`, `a:acf7e1d0-07`, `a:acf7e1d0-sub-agent-ad3e5a-04`, `a:acf7e1d0-sub-agent-ad3e5a-05`, `a:acf7e1d0-sub-agent-ad3e5a-06`, `a:f0d70a59-17` · Artifacts: `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`, `semantic_merge_driver/strategies/rm2_strategies/rename_conflict.py`, `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`

> Every less-fragile alternative (extract a shared `RM2Runner`, promote `_FileView` scan helpers to public) requires editing the frozen lane files, which the stated constraint forbids this session.
>
> — `2026-07-16_acf7e1d0.txt:203`

> It cannot reuse `self._rm2._inconclusive` (would emit the wrong strategy name/message), and factoring a shared module-level helper would require editing the frozen rename lane. Not actionable under the stated guardrail.
>
> — `2026-07-16_acf7e1d0_sub-agent-ad3e5a.txt:52`

### <a id="d-370"></a>D-370 — Test files should import the docker probe and call the production pair helper

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** Two test-side reuse fixes were recommended for tests/test_signature_stale_call.py: import `_image_available` (or the `needs_image` skipif marker) from tests/test_rename_conflict.py instead of keeping a byte-for-byte copy, and replace the local `_rm2_pair()` helper with a call to the production `strategy._rm2._run_rm2_pair(...)`, which the test can already reach through its own instance. Both are actionable without editing any frozen lane.

**Why.** The two probe copies are identical today, so when the RM2 image tag or docker flags change one copy gets updated and the other silently keeps gating on the old contract, producing divergent CI signal that looks like flakiness; and the docker command line is otherwise maintained in three places, so a change to the invocation would fix production while the "contract pin" integration tests keep exercising a call shape production no longer uses.

**Status.** adopted. S12 (2026-07-26): ruled, one each way — the substantive rec landed: the test's _rm2_pair (:1617) now drives the production runner (SignatureStaleCallStrategy()._rm2._run_rm2_pair, :1623; ISSUES.md #31: 'contract probes now exercise the PRODUCTION RM2 runner'). The _image_available copy (:1605) was deliberately kept: ISSUES.md #31 'per-suite test-helper copies kept (project test idiom … RM2_IMAGE imported from the lane module in both suites so tag bumps propagate)'. Nothing pending.

**Source.** `a:acf7e1d0-sub-agent-ad3e5a-02`, `a:acf7e1d0-sub-agent-ad3e5a-03` · Artifacts: `semantic_merge_driver/tests/test_signature_stale_call.py`, `semantic_merge_driver/tests/test_rename_conflict.py`

> someone updates one copy's probe and the other silently keeps gating on the old contract
>
> — `2026-07-16_acf7e1d0_sub-agent-ad3e5a.txt:29`

> The docker command line is now maintained in three places (production `_run_rm2_pair`, this helper, and note the rename suite inlines it too).
>
> — `2026-07-16_acf7e1d0_sub-agent-ad3e5a.txt:34`

### <a id="d-371"></a>D-371 — Parallel sessions keep hands off the tree and coordinate via the committed prompt

`2026-07-22` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Sources disagree: the read-only commitment is recorded as Claude's, the prompt patch as joint (raised with Ali and agreed).*

**Decision.** While another session owns the working tree, this session makes no commits and no repo edits (read-only checks and Q&A only), with narrow exceptions taken only when the tree is verifiably clean. The parallel-run coordination rules are added to the committed S-D8 kickoff prompt as a dated PARALLEL-RUN NOTE (commit df58669) and pushed with the other session's commit so both sync through origin.

**Why.** So the S-D7 session has the working tree to itself, everything from S-D5/S-D6 already being pushed so it starts from clean, current main; and the parallel-run rules belong in the committed prompt because they did not exist when it was instantiated — the tree was clean at that moment, making a small atomic edit safe for the concurrently running session.

**Status.** adopted.

**Source.** `a:2e726dc0-27`, `a:2e726dc0-26` · Artifacts: `df58669`, `ISSUES.md`

> From this session I'll keep hands off the working tree — no commits, no repo edits — so the S-D7 session has it to itself
>
> — `2026-07-16_2e726dc0.txt:839`

> Yes — the parallel-run rules belong in the committed prompt (they didn't exist when it was instantiated).
>
> — `2026-07-16_2e726dc0.txt:890`

### <a id="d-372"></a>D-372 — DECISIONS.md: methodology included, provenance per entry, coverage stated, not authoritative

`2026-07-25` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Sources disagree: the per-entry provenance labelling is recorded as joint ("as you asked"), the scope, boundary and coverage-section choices as Claude's.*

**Decision.** docs/DECISIONS.md covers design, architecture and methodology decisions grouped into 11 themes with a clickable index, an open-decisions table, and Decision / Why / Status / Source per entry. Every entry carries a provenance tag — [chat] with session id and date where a transcript survives (52 entries), [reconstructed] where it was rebuilt from commit messages and docs/plans/ for the 2026-04-15 → 05-16 window (12 entries). Where an entry overlaps ISSUES.md, STATUS.md, THREATS_TO_VALIDITY.md or docs/plans/, those stay authoritative and the record must not re-derive them. The document states its own reading coverage and names every file not read in full.

**Why.** Git history starts 2026-04-15 with 59 commits (~36% of the project) predating the first surviving transcript, so those decisions exist only in commit messages and docs and must be flagged as reconstructions rather than recorded rationale. The value of the document is the reasoning that exists only in chat, so duplicating what the authoritative docs already state adds nothing and risks divergence. Coverage is stated in the document so the gap is on the record rather than hidden — "Report coverage honestly. An audited 80% beats a claimed 100%."

**Status.** adopted.

**Source.** `a:c4c4d030-02`, `a:c4c4d030-03`, `a:c4c4d030-04`, `b:c4c4d030-20` · Artifacts: `docs/DECISIONS.md`, `docs/plans/`, `docs/historical/`, `ISSUES.md`, `STATUS.md`, `THREATS_TO_VALIDITY.md`

> **Provenance is labelled per entry**, as you asked:
>
> — `2026-07-25_c4c4d030.txt:21`

> those stay authoritative — this is an index and rationale archive, not a replacement.
>
> — `2026-07-25_c4c4d030.txt:32`

> - Report coverage honestly. An audited 80% beats a claimed 100%.
>
> — `2026-07-25_c4c4d030.txt:159`

### <a id="d-373"></a>D-373 — v2 of the decision record should add supersession fields and a JSON sidecar

`2026-07-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** For the next version of the decision record, add explicit Superseded-by / Revises fields to the entry format so a revised or reversed decision records the arc on itself, and emit a machine-readable decisions.json alongside docs/DECISIONS.md mapping decision → date → source file → quote.

**Why.** v1 handled revised decisions inconsistently (the 66.7%→90.7% correction sat inside another entry's notes), and explicit fields make the design-evolution narrative for Ch. 4/8 fall out mechanically; the JSON sidecar is the claims-ledger substrate and makes the Ch. 9 contribution-delineation table a query rather than a writing task.

**Status.** adopted. S12 (2026-07-26): realized by the v2 rebuild — entry.schema.json carries supersedes/superseded_by on every entry, and the machine-readable layer exists as docs/decision-record/entries/*.json (decision → date → sources → verbatim quotes with file:line) plus numbering.json, which is the decisions.json this entry asked for in substance.

**Source.** `a:c4c4d030-15`, `a:c4c4d030-16` · Artifacts: `docs/DECISIONS.md`, `decisions.json`

> **Add a supersession field.** v1 handles revised decisions inconsistently
>
> — `2026-07-25_c4c4d030.txt:164`

> **Emit a machine-readable sidecar** — `decisions.json` alongside the markdown.
>
> — `2026-07-25_c4c4d030.txt:166`


## Thesis framing & reporting

*133 primary source decisions → 72 entries; 0 not promoted (reasons in `docs/decision-record/entries/thesis-framing.json`).*

### <a id="d-374"></a>D-374 — Reframe the thesis around composition-by-abstraction with exit-1 as a third merge outcome

`2026-04-17 → 2026-07-18` · **adopted** · `[mixed]` · corroboration: both · confidence: medium · actors: ali

*Actors note: The 2026-04-17 reframing was Ali's; the 2026-07-18 narrowing was recorded with actors unclear in a sub-agent report. The originating call is Ali's.*

**Decision.** Drop the "merger vs verifier" framing. The thesis claim is composing specialized tools at progressively more concrete abstraction levels, simpler-first, with IVn as motivation only; semantic conflicts surface via exit-1 as a third outcome alongside clean and textual conflict. By 2026-07-18 the constructive success criterion is explicitly narrowed to demonstrating that mechanism (extending Git's two outcomes with a third), not to improving merge quality.

**Why.** IVn is motivation, not the full thesis claim; the contribution is the composition-by-abstraction framing Ali confirmed in conversation. The later narrowing was forced by the measurement: since no tool beats Mergiraf, aim (1) "improve merging via composition" cannot be shown, so the claim is restricted to the mechanism plus the verification layer.

**Status.** adopted. Supersedes: *merger vs verifier framing*.

**Source.** `preA:pre-commits-04`, `a:dc3bc182-sub-sub-agent-a74c7a-04` · Artifacts: `7856a76`, `THREATS_TO_VALIDITY.md`, `STATUS.md`

> Replace the "merger vs verifier" framing with the composition-by-abstraction
>
> — `2026-04-15_pre-commits.txt:58`

> The constructive success criterion is reframed as demonstrating a *mechanism* — extending Git's two outcomes (clean / textual conflict) with a third, "semantic conflict," surfaced via exit-1.
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:25`

### <a id="d-375"></a>D-375 — Report JDime's 96% crash rate as partly intrinsic and harness-scoped, crediting the Passau lineage

`2026-04-17 → 2026-07-22` · **adopted** · `[mixed]` · corroboration: both · confidence: medium · actors: claude

*Actors note: The 2026-04-17 correction is recorded with actors unclear; the 2026-07-22 write-up guidance is Claude's recommendation.*

**Decision.** Describe JDime's 96% crash rate in STATUS.md and CLAUDE.md as partly intrinsic — per Schesch's own "unsuitable for practical use" assessment — rather than a pure Docker/runtime artefact. In the write-up, scope the number strictly as "in this harness, on this corpus", cite Schesch's exclusion as theirs, credit JDime's idea, and present the driver's NONE→git fast-path and crash-fallback as generalising JDime's auto-tuning principle from intra-tool to inter-tool dispatch.

**Why.** Schesch's own assessment calls JDime unsuitable for practical use, so the crash rate cannot be attributed solely to the runtime environment. For the write-up, JDime is a Passau artifact and plausibly the examiners' intellectual home turf, so framing the architecture as extending the Passau principle turns an awkward result into a respectful contribution to their research line.

**Status.** adopted. S12 (2026-07-26): the docs half is in force — CLAUDE.md carries verbatim '96% crash rate intrinsic — Schesch et al. excluded JDime from their own evaluation as unsuitable for practical use' (the 7856a76 correction), and STATUS scopes the number to this harness/corpus. The write-up-application clause awaits a thesis draft. Supersedes: *JDime's 96% crash rate is purely a Docker/runtime artefact*.

**Source.** `preA:pre-commits-05`, `a:dc3bc182-15` · Artifacts: `7856a76`, `STATUS.md`, `CLAUDE.md`

> Also: correct JDime framing in STATUS.md and CLAUDE.md — its 96% crash
>
> — `2026-04-15_pre-commits.txt:64`

> **Handle JDime with precision, not dismissal.** JDime is a Passau artifact and plausibly your examiners' intellectual home turf.
>
> — `2026-07-18_dc3bc182.txt:498`

### <a id="d-376"></a>D-376 — Report Mastery's FP rate with an intrinsic-limitation caveat instead of normalising it away

`2026-04-22 → 2026-05-14` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: claude

*Actors note: The two plan-era sources record actors as unclear; the 2026-05-14 restatement is Claude's. No source attributes the call to Ali.*

**Decision.** Carve Mastery out of the 3e headline treatment: run 3e for it if useful, but do not present normalised numbers as its headline. Instead report an intrinsic-limitation note (systematic content loss — dropped file-header comments and Javadoc) alongside Mastery's FP rate, parallel to the JDime treatment, and confine the 3e-as-headline framing to Spork.

**Why.** All 44/44 Mastery FPs are structural and the eyeballed cases show systematic content loss (71-char output vs 793 expected) because Mastery discards comments and blank-line structure during its AST roundtrip — content diffs, not format diffs, which no amount of canonical formatting can recover. That is the same family weakness Schesch et al. cited when excluding JDime, so Mastery's FPs are partly intrinsic rather than a comparator artefact like Spork's: M3.5 will recover Spork's numbers but not Mastery's.

**Status.** adopted.

**Source.** `preB:pre-execution-sequence-09`, `preA:pre-execution-sequence-09`, `preA:pre-stage-gamma-fp-diagnostic-10` · Artifacts: `docs/plans/stage-gamma-fp-diagnostic.md`

> **For Mastery:** 3e useful but not headline — its limitation goes in the report as an intrinsic-characteristic note alongside the FP rate.
>
> — `2026-04-22_pre-execution-sequence.txt:78`

> 3e (`google-java-format`) is **not the right primary fix for Mastery's FPs.**
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:114`

### <a id="d-377"></a>D-377 — Write up language as a second dispatch axis alongside refactoring cluster

`2026-04-25` · **superseded** · `[recon]` · corroboration: single-pass · confidence: medium · actors: unclear

**Decision.** Phase S4 was to add an ARCHITECTURE.md subsection framing language as a second dispatch axis (router inputs = cluster + language), with matching updates to STATUS.md, tool-evaluation-findings.md §6/§8 and merge-tool-comparison/README.md, and no new files.

**Why.** Framed as the thesis-visible claim that dispatch operates on two axes — refactoring cluster plus language — not just one.

**Status.** superseded. Superseded by [D-396](#d-396) — Reframe the contribution around the routing null result: Mergiraf-only plus fast-path.

**Source.** `preA:pre-spork-driver-integration-19` · Artifacts: `ARCHITECTURE.md`, `STATUS.md`, `tool-evaluation-findings.md`, `merge-tool-comparison/README.md`

> **Purpose:** the thesis-visible claim. Dispatch now operates on two axes — refactoring cluster + language — not just one.
>
> — `2026-04-25_pre-spork-driver-integration.txt:184`

### <a id="d-378"></a>D-378 — Pre-commit to publishing null results as findings rather than tuning toward a signal

`2026-04-25 → 2026-05-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: The two plan-era sources record actors as unclear; the transcript-era restatement is Claude's. No source attributes the commitment to Ali.*

**Decision.** A negative outcome on the taxonomy/granularity experiments does not count as plan failure. A null S3 result is reported as "the PDF's taxonomy claim doesn't hold on this dataset for Java sub-method scenarios" and S1 (standalone backend with explicit selection) ships either way; a negative W3/MIGRATE_DECL result is recorded as a finding that collapses the dispatch branch to Mergiraf-only for that cluster; and a mostly-NONE cluster distribution at n=50 is reported as a publishable negative (scope-tier-options Tier C) rather than a reason to adjust the pipeline.

**Why.** The thesis argument is evidence-first: a negative result refines the PDF's taxonomy against real data rather than accepting it uncritically, so it is itself a contribution. Either W3 outcome is publishable — a signal validates the taxonomy on this dataset, no signal validates the more skeptical "dispatch at the analysis layer, not merger layer" framing. A weak signal at n=50 was anticipated (recon's F-harness saw only ~4/10 scenarios with any refactoring), so it is "not a reason to tune".

**Status.** adopted.

**Source.** `preA:pre-spork-driver-integration-14`, `preA:pre-weave-integration-21`, `b:20b53f98-26` · Artifacts: `docs/plans/tool-evaluation-findings.md`, `docs/plans/scope-tier-options.md`

> **Why S3 can produce a null result without the plan "failing"?** Because the thesis argument is evidence-first.
>
> — `2026-04-25_pre-spork-driver-integration.txt:236`

> **Possible weak/empty signal** — recon F-harness: only ~4/10 scenarios had any refactoring; n=50 may yield mostly `NONE`. That is a *publishable negative* (scope-tier-options Tier C), not a reason to tune. Will report honestly.
>
> — `2026-05-18_20b53f98.txt:145`

### <a id="d-379"></a>D-379 — Do not cite Weave's 31/31 upstream headline without the project's own numbers

`2026-04-25` · **adopted** · `[recon]` · corroboration: both · confidence: medium · actors: unclear

**Decision.** Weave's README-only 31/31 headline result is treated as marketing and must not be cited in the thesis without the project's own measurements.

**Why.** The number is README-only and not peer-reviewed.

**Status.** adopted. S12 (2026-07-26): the bar held — Weave's 31/31 headline is cited nowhere in the repo's docs or reports, and the project's own Weave numbers exist (W3 gate run in reports_migrate_decl/, the six-tool table in reports/results.csv), which is the condition this entry set for ever citing upstream's figure.

**Source.** `preA:pre-weave-integration-20`

> Treat it as marketing; do not cite in the thesis without our own numbers.
>
> — `2026-04-25_pre-weave-integration.txt:241`

### <a id="d-380"></a>D-380 — Restate coverage as "2 strategies, 1 of 7 categories" across all docs

`2026-05-13` · **adopted** · `[recon]` · corroboration: both · confidence: high · actors: unclear

**Decision.** Align phrasing across STATUS, ARCHITECTURE, CLAUDE, root README and the semantic_merge_driver README from "2 of 7 categories" to "2 strategies, 1 of 7 (#5 Loop Semantics)".

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted. Supersedes: *"2 of 7 categories" coverage claim*.

**Source.** `preA:pre-commits-36` · Artifacts: `c4cfe28`, `STATUS.md`, `ARCHITECTURE.md`

> Align "2 of 7 categories" phrasing to "2 strategies, 1 of 7 (#5 Loop
>
> — `2026-04-15_pre-commits.txt:487`

### <a id="d-381"></a>D-381 — Reframe Spork's FP rate as a comparator-ground-truth gap, substantially closed on this corpus

`2026-05-14 → 2026-07-18` · **adopted** · `[mixed]` · corroboration: both · confidence: high · actors: claude

*Actors note: Two plan-era sources record actors as claude, one as unclear, and the 2026-07-18 sub-agent report as unclear. No source attributes the reframing to Ali.*

**Decision.** Write up Spork's false-positive rate as a comparator-ground-truth problem, not a Spork defect, and re-frame ISSUES.md #2 as 'comparator-gap' while keeping its status at `decided — 3e implemented, partial`. Once cumulative recoveries reached 12 against the original §3 floor of 30, the headline moved from 'comparator-gap, partially closed' to 'comparator-gap, substantially closed'. The flagship TP 32 / FP 11 figure must always be cited as "comparator-gap substantially closed on this corpus", never as a property of Spork, and always with the fragility caveat.

**Why.** 15 of 15 stratified samples were AST-equivalent reformatting with no content loss, duplication, method reordering or different-resolution disagreement (≥90% point estimate, Wilson 95% lower bound ≈78%), so under stronger ground truth (3b AST normalize or 3a test-suite execution) these FPs would clear — distinguishing Spork from Mastery (intrinsic content loss) and JDime (intrinsic crash weakness). The move to 'substantially closed' was presented as a significant improvement in defensibility for the thesis discussion. The corpus-scoping and fragility caveat are required because the number clears the bar with literally zero margin, 5 of 32 TPs depend on two lossy transforms, and the comparator was tuned against its own residuals.

**Status.** adopted. Supersedes: *headline framing 'comparator-gap, partially closed'*; *Spork's high FP count on n=50 as evidence of a tool defect*.

**Source.** `preA:pre-mergiraf-integration-15`, `preA:pre-stage-gamma-fp-diagnostic-18`, `preA:pre-comparator-3d-extended-ast-transforms-22`, `a:dc3bc182-sub-sub-agent-a74c7a-06` · Artifacts: `merge-tool-comparison/ISSUES.md #2`, `docs/plans/stage-gamma-fp-diagnostic.md`, `THREATS_TO_VALIDITY.md`

> **Spork's FP rate is a comparator-ground-truth problem, not a Spork bug.**
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:226`

> the docs insist it be cited as "comparator-gap substantially closed *on this corpus*," never as a property of Spork.
>
> — `2026-07-18_dc3bc182_sub-agent-a74c7a.txt:56`

### <a id="d-382"></a>D-382 — Publish the undershooting Tier C numbers as the honest interim state

`2026-05-14` · **adopted** · `[recon]` · corroboration: single-pass · confidence: medium · actors: unclear

**Decision.** reports/results.csv is committed with the post-3b Tier C numbers (Spork TP 7 / FP 36, other tools unchanged) as the current published state, rather than withheld or rolled back to the better-looking M3.5 numbers.

**Why.** Stated as the current honest interim state.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-020](#d-020) (see the reconciliation note there)

**Source.** `preA:pre-comparator-3b-ast-normalize-26` · Artifacts: `merge-tool-comparison/reports/results.csv`

> `reports/results.csv` committed with post-3b Tier C numbers (Spork 7/36, others unchanged) as the current honest interim state.
>
> — `2026-05-14_pre-comparator-3b-ast-normalize.txt:527`

### <a id="d-383"></a>D-383 — Cite upstream Mergiraf numbers and report FP rate under each criterion alongside 3e

`2026-05-14` · **proposed** · `[recon]` · corroboration: both · confidence: medium · actors: claude

**Decision.** On top of 3e as primary, cite upstream Mergiraf numbers (3i) for the Mergiraf row and report the FP rate under each criterion so the reader can pick (3h); both are declared compatible with 3e.

**Why.** 3i is free credibility for the Mergiraf row (captured at M0); 3h lets the reader pick the criterion.

**Status.** proposed. S12 (2026-07-26): 3h is dead (no per-criterion matrix was ever built — see the abandoned extra-report-pivots entry) and the 3i upstream citation appears in no durable text; whether the thesis cites upstream's Mergiraf numbers is settled only by the thesis draft, which does not exist yet.

**Source.** `preA:pre-stage-gamma-fp-diagnostic-06` · Artifacts: `mergiraf-integration.md §Phase 3`

> **Add on top:** option **3i** (cite upstream Mergiraf numbers — free credibility for the Mergiraf row, captured at M0); option **3h** (multi-criteria reporting — show FP rate under each criterion; reader picks).
>
> — `2026-05-14_pre-stage-gamma-fp-diagnostic.txt:87`

### <a id="d-384"></a>D-384 — Maintain a project-level THREATS_TO_VALIDITY.md under the standard empirical-SE taxonomy

`2026-05-16 → 2026-05-20` · **adopted** · `[mixed]` · corroboration: both · confidence: medium · actors: claude

*Actors note: The document's creation is recorded with actors unclear; the §1.5 draft is Claude's. The §1.5 draft itself remained unapplied at the end of that session ("I haven't touched the file yet").*

**Decision.** Add THREATS_TO_VALIDITY.md covering both subprojects under the standard construct/internal/external/conclusion/reliability taxonomy, incorporating the 2026-05-16 adversarial audit findings (textual-not-behavioural oracle; dataset-contingent 3e.2/3e.9 soundness; comparator tuned against its own residuals; zero-margin floor where 5 of 32 Spork TPs ride on the two lossy transforms), and add it to the README docs map. A drafted §1.5 (Construct validity — reconstruction fidelity) documenting merge-base selection vs. git's virtual base, with measured prevalence 1/50 (adangel_pmd 312d4c60c0 / PMD.java), mitigation, residual risk and summary-table row 11, was proposed as an addition.

**Why.** The document is the artefact resolving ISSUES #7, whose status flip was committed in 4db9329. The §1.5 addition was justified because merge-base selection is not covered anywhere in the existing document and the claim was verified as accurate and non-vacuous on this corpus — the stored base genuinely differs from git's reconstructed virtual base by real code on the file under test.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-247](#d-247) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-298](#d-298) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-197](#d-197), [D-164](#d-164) — other_uid b:4f4f0f87-02 is cited by the merge-base entry; the verify-before-adding rule is evaluation-oracles/[D-164](#d-164).

**Source.** `preA:pre-commits-86`, `a:4f4f0f87-03` · Artifacts: `60802e8`, `THREATS_TO_VALIDITY.md`, `ISSUES.md #7`

> docs map. This is the artefact resolving ISSUES #7 (status flip
>
> — `2026-04-15_pre-commits.txt:1705`

> Drafted in the doc's idiom as a new **§1.5** (Construct validity — reconstruction fidelity) plus a summary-table row:
>
> — `2026-05-20_4f4f0f87.txt:66`

### <a id="d-385"></a>D-385 — Report the weak per-cluster signal as suggestive with the hedge attached, not tuned or softened

`2026-05-18` · **adopted** · `[mixed]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: The plan-era source records actors as unclear; the transcript-era source is Claude's.*

**Decision.** R2's outcome — Spork best on INTRA_BODY (F1 0.88), direction-consistent but with per-cluster n of 4–18, below Wilson-CI adequacy — is published as "suggestive, not defensible" rather than tuned into a stronger claim. The cited per-cluster contrasts (Spork INTRA_BODY F1 0.88 vs 0.80, n=16 vs n=8) keep their precise numbers rather than being rewritten as direction-only, with the out-of-context-lifting risk logged.

**Why.** Per-cluster n is 4–18 and sub-Wilson-CI, so the signal cannot support a defensible tool-comparison claim. Keeping the precise numbers is nonetheless defensible because every citation already sits adjacent to the "sub-Wilson-CI / not sufficient" hedge — though direction-only phrasing would be stricter.

**Status.** adopted.

**Source.** `preA:pre-rm2-integration-28`, `b:20b53f98-18` · Artifacts: `merge-tool-comparison/reports/results.csv`, `STATUS.md`, `merge-tool-comparison/ISSUES.md`

> per-cluster n is 4–18, sub-Wilson-CI, so *suggestive, not defensible*; reported
>
> — `2026-04-22_pre-rm2-integration.txt:211`

> Every citation *does* have the "sub-Wilson-CI / not sufficient" hedge adjacent, so it's defensible, but repeating the precise F1 pair invites out-of-context lifting. Direction-only phrasing would be stricter.
>
> — `2026-05-18_20b53f98.txt:258`

### <a id="d-386"></a>D-386 — Keep presentation notes as a standalone markdown file in the slide-by-slide convention

`2026-05-20 → 2026-05-26` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: The file-format choice was Claude's; the Part C content ruling ("All four") was Ali's.*

**Decision.** Add `presentation/next_presentation_notes.md` following the existing slide-by-slide Key points / Visual / Speaker notes convention, not wired into `build_deck_v2.py` and not committed initially, rather than merging into `PRESENTATION_PLAN.md`. Part C (decisions log + slides C1–C5) was later appended including all four borderline items: Mergiraf-is-best-backend, AST-normalizer-is-evaluation-only, the Weave field-loss reliability caveat, and the reproducibility methods (blobless/no-checkout clone, per-clone timeout, multi-base skip).

**Why.** Matching the existing convention was the stated goal — "first let me find where presentation materials live so it matches your existing convention"; the wiring and commit choices were flagged as overridable. No reason was recorded for including all four borderline items; Ali simply ruled "All four — everything goes in."

**Status.** adopted.

**Source.** `a:e1df1610-29`, `a:e1df1610-30` · Artifacts: `presentation/next_presentation_notes.md`, `6892637`

> Convention is clear — slide-by-slide with **Key points** / **Visual** / **Speaker notes**.
>
> — `2026-05-20_e1df1610.txt:456`

> All four — everything goes in.
>
> — `2026-05-20_e1df1610.txt:1343`

### <a id="d-387"></a>D-387 — Bound the "Spork is best nowhere" negative: two clusters untested, taxonomy not Spork-centric

`2026-05-26` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** State explicitly that "Spork is best nowhere" is bounded: CONTAINER_MOVE had 0 cases and HIERARCHY_RESHAPE ≤1 in both samples so Spork's behaviour there is unmeasured, the RM2 cluster taxonomy is driver-centric rather than Spork-centric, selection was by tool outcome not refactoring type, INTRA_BODY was never sub-stratified, and ground truth was exact dev-resolution match. Cross-file cluster testability must be assessed before investing.

**Why.** The clusters with no data are cross-file moves that the file-level scenario model and file-level RM2 may not capture; Spork's design strengths (formatting robustness, import reordering, specific syntactic AST conflicts) do not map onto refactoring clusters and were never defined as a scenario class and tested — so the behaviour is unmeasured, not lost.

**Status.** adopted.

**Source.** `a:e1df1610-32` · Artifacts: `merge-tool-comparison/ISSUES.md #27`

> Spork's behavior on class/package relocation and inheritance reshaping is genuinely **unmeasured** — not "lost."
>
> — `2026-05-20_e1df1610.txt:1425`

### <a id="d-388"></a>D-388 — Surface corrections explicitly and keep refuted designs as named negative results

`2026-06-11 → 2026-06-20` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Evidence corrections are written into the v2 FINDINGS and the Stage-A classification doc as explicit, labelled corrections rather than silent edits. Three refuted detector designs (dropped type-resolution lane, broken (method,name) differential keys, skipped Change-Return-Type) are recorded in FINDINGS with their causes, and each remaining uncovered #6-family miss carries a named limitation. In the same spirit, the aerospike case is characterised as RefactoringMiner correctly reporting a real field rename, with the false positive attributed solely to the downstream var-lane stale-reference scan colliding with a surviving same-named method.

**Why.** Stated as deliberate practice: the correction is "surfaced not buried", kept on the record. Refuted detector designs with named causes are thesis material, and honest coverage requires each miss to carry a named limitation. For the aerospike case, the field genuinely was renamed (isSingleResponse → numExpectedResponses, 6 sites), so blaming RM2's refactoring detection would misattribute the defect.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-359](#d-359) — other_uid a:bfc672b4-40 landed there: the STATUS/THREATS stage-gate disclosure rule is the mechanism by which these corrections reached the project docs.

**Source.** `a:bfc672b4-15`, `a:bfc672b4-16`, `a:0e14484d-13` · Artifacts: `merge-tool-comparison/reports_detection/pilot_v2/FINDINGS.md`, `hit_adjudications.md`

> **One evidence correction, surfaced not buried**
>
> — `2026-06-11_bfc672b4.txt:378`

> One thing worth keeping straight for your write-up: RM2 did **not** hallucinate the rename — the field genuinely was renamed. The false positive is purely the stale-reference scan colliding with a surviving same-named method.
>
> — `2026-06-20_0e14484d.txt:145`

### <a id="d-389"></a>D-389 — Describe the zero-yield category detectors as low-yield cheap coverage, not broken

`2026-06-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** DFI and the two loop strategies are retained and described as "low-yield, cheap, honestly scoped" coverage rather than removed or called broken; the defensible framing is that category base rates, not detector sophistication, determine detection value.

**Why.** G1 proves the DFI pipeline fires 10/10 on real instances when they exist and the v2 loop detector passes every fixture, so they are not broken; their targets barely occur (zero of 23 adjudicated failures were #3/#5) and after the v2 fixes they cost zero false positives, so "useless" overstates it.

**Status.** adopted.

**Source.** `a:bfc672b4-21`

> they are not *broken* — G1 proved the DFI pipeline fires 10/10 on real instances when they exist
>
> — `2026-06-11_bfc672b4.txt:427`

> after the v2 fixes they cost nothing (0 false positives), so "useless" overstates it — "low-yield, cheap, honestly scoped" is the defensible framing
>
> — `2026-06-11_bfc672b4.txt:427`

### <a id="d-390"></a>D-390 — Restate the contribution as the first base-rate measurement of the hypothesized categories

`2026-06-11` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The thesis's central claim shifts from "we built detectors for semantic-conflict categories" to "the first base-rate measurement of the hypothesized categories on a real corpus with test-suite ground truth"; the taxonomy chapter becomes a tested hypothesis space rather than a design spec.

**Why.** The measured distribution inverts the taxonomy's emphasis (categories #1–#5/#7 ≈0%, #6-family ≈62% of attributable mass), and a measured distribution nobody else has produced is worth more than four detectors with two hits; the reading was pre-registered in plan §5, so it is not a post-hoc rescue.

**Status.** adopted. S12 (2026-07-26): the claim shift is the project's stated framing — STATUS.md:238 lists 'the three-outcome model, the base-rate finding, and the evidence-driven repair arc' as the thesis's demonstrated contributions, :121 opens the taxonomy block with 'the first CI-bearing mechanism base rates', and the deck reframing enacted the same shift.

**Source.** `a:bfc672b4-22`

> For a thesis, a measured distribution nobody else has produced is worth more than four detectors with two hits.
>
> — `2026-06-11_bfc672b4.txt:457`

> It stops being a design spec ("we implement these seven") and becomes a tested hypothesis space
>
> — `2026-06-11_bfc672b4.txt:459`

### <a id="d-391"></a>D-391 — Frame the deck around a second pivot: from category-specific detection to generic consistency-checking

`2026-06-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: One source records this as joint (options put, Ali said "sounds good, generate both"), the other as claude. Joint is correct: Claude proposed the reframing and Ali ratified it in the same exchange.*

**Decision.** The July/late-June progress deck's spine is the ISSUES #29 detection-validation double finding: (1) detection adds measurable value (R2 7.3%, R1 2.1%), and (2) the base-rate twist that the #3/#5 detectors are inert. The narrative pivots from category-specific semantic detection to generic refactoring/scope-consistency checking as a clean-merge safety net, with the in-the-wild base rates themselves counted as a contribution plus a labeled validation set.

**Why.** The June 3 deck ended on an open question the project couldn't answer — "how do you know your detection layer works?" — and #29 answers it. Detectors #3 and #5 fired 0 detections and 0 FPs on 443 real files while the entire detection mass came from the #6 rename/declaration family, so the value is carried by generic consistency checking, not taxonomy-driven detection; stating that is honest and defensible.

**Status.** adopted.

**Source.** `a:12c77ea5-01`, `b:12c77ea5-02` · Artifacts: `merge-tool-comparison/reports_detection/full/FINDINGS.md`, `ISSUES #29`, `presentation/thesis_progress_late_jun2026.pptx`

> → This is a clean **second pivot** for the thesis narrative, and it's honest and defensible: *category-specific detection* → *generic consistency-checking as a clean-merge safety net*, with the in-the-wild base rates themselves a contribution
>
> — `2026-06-18_12c77ea5.txt:36`

> sounds good, generate both
>
> — `2026-06-18_12c77ea5.txt:66`

### <a id="d-392"></a>D-392 — Keep the 7-slide spine tight; demote granularity asymmetry, dropped lane and flag table to backups

`2026-06-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The whole-merge-vs-file-level granularity asymmetry, the dropped javasrc2cpg type-resolution lane (an honest negative engineering result), and the 11-flag table go on backup slides rather than in the 7-slide main spine.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Source.** `a:12c77ea5-03` · Artifacts: `presentation/thesis_progress_late_jun2026.pptx`

> **Backup slides:** the whole-merge-vs-file-level **granularity asymmetry** (third independent observation); the **dropped type-resolution lane** (javasrc2cpg version-instability — an honest negative engineering result); the 11-flag table.
>
> — `2026-06-18_12c77ea5.txt:50`

### <a id="d-393"></a>D-393 — Present R2 as provisional rather than rushing adjudication before the talk

`2026-06-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** In the talk and deck, R2 is stated as "12/164 flagged; provisional adjudication all causal-looking, final ruling in progress" instead of claiming the 11 CAUSAL labels as final; the §4.6 adjudication is not to be rushed to completion before the presentation.

**Why.** The §4.6 adjudication of the 15 flags is not done, so the labels aren't final; presenting them as provisional is "honest, safe, and doesn't depend on finishing the adjudication UI before the talk" — don't try to firm it up under time pressure.

**Status.** adopted.

**Source.** `a:12c77ea5-02` · Artifacts: `merge-tool-comparison/reports_detection/full/hit_adjudications_draft.md`, `ISSUES #29`

> My recommendation: **present R2 as "12/164 flagged; provisional adjudication all causal-looking, final ruling in progress"** — honest, safe, and doesn't depend on finishing the adjudication UI before the talk. Don't try to firm it up under time pressure today.
>
> — `2026-06-18_12c77ea5.txt:54`

### <a id="d-394"></a>D-394 — QA every deck build: text-extraction of numbers, then a Keynote PNG render check

`2026-06-18 → 2026-07-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** Slide correctness is verified by text extraction of content, tables and numbers rather than a pixel render, with the user asked to eyeball spacing in Keynote/PowerPoint before presenting. From 2026-07-24 every deck edit is followed by a rebuild, a file validation pass, and a Keynote PNG export render that is visually inspected slide by slide before the change is reported as delivered.

**Why.** At the June build there was no LibreOffice installed to render slides to images, and the layout coordinates were lifted verbatim from v4, which rendered cleanly — so text extraction plus a human eyeball substituted for a render. No reason was recorded for the later validate+render QA loop beyond it being the standing practice.

**Status.** adopted.

**Source.** `a:12c77ea5-06`, `b:16127d04-23` · Artifacts: `presentation/thesis_progress_late_jun2026.pptx`, `workspace/v7_png/`

> I couldn't pixel-render the slides (no LibreOffice installed), so I verified content/tables/numbers via text extraction rather than visually
>
> — `2026-06-18_12c77ea5.txt:101`

> All rewrites in. Rebuilding, validating, rendering, and checking every slide.
>
> — `2026-07-24_16127d04.txt:233`

### <a id="d-395"></a>D-395 — Slides use impersonal voice, speaker notes use first person, bylines keep the name

`2026-06-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

**Decision.** Narrative third-person references to "Ali" are removed: displayed slide text becomes impersonal (slide 7: "the §4.6 ruling on the 15 flags") and speaker notes become first person ("my §4.6 adjudication"). The PRESENTED BY byline, footer attribution, and the build-script docstring mention are left as-is.

**Why.** Ali flagged the line as reading third-person; slides should match the deck's existing impersonal voice (slide 6 already says "hit adjudication in progress" with no name) while the notes are the presenter's own script, and bylines are correct attribution rather than narrative.

**Status.** adopted.

**Source.** `a:12c77ea5-07` · Artifacts: `presentation/build_deck_v5.py`, `presentation/next_presentation_notes_late_jun2026.md`

> this part sound like from 3rd person 
>
> — `2026-06-18_12c77ea5.txt:103`

> I'll make the slide impersonal (matching the deck's voice — slide 6 already says "hit adjudication in progress" with no name) and the notes first-person (they're your speaker notes).
>
> — `2026-06-18_12c77ea5.txt:109`

### <a id="d-396"></a>D-396 — Reframe the contribution around the routing null result: Mergiraf-only plus fast-path

`2026-06-24 → 2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

*Actors note: The 2026-06-24 proposal is Claude's; the two 2026-07-18 sub-agent reports record actors as unclear. No source shows Ali ruling on it.*

**Decision.** Frame the contribution as "single best structured merger (Mergiraf) + a semantic post-merge detector" rather than "adaptive routing", treating the refuted Spork and Weave arms as evidence supporting the null result. By 2026-07-18 the project narrative is rebuilt around "Mergiraf-only-plus-fast-path" as the defensible design, with the multi-arm quality-routing thesis stated as refuted and the driver's claimed contribution restricted to the NONE→git fast-path plus the verification layer.

**Why.** The routing experiment honestly concluded that no specialist backend beats Mergiraf, which is a legitimate publishable finding; leaning into it converts the refuted arms from failures into evidence. Both specialist arms win 0 on their own clusters, so the driver's routing value collapses to a NONE→git fast-path over an always-Mergiraf backbone, and quality-improving routing cannot be claimed.

**Status.** adopted. Supersedes: [D-377](#d-377) — Write up language as a second dispatch axis alongside refactoring cluster; *Aim (1): that a composed pipeline improves merging over any single tool*; *the multi-arm quality-routing thesis (specialist backends improve merge quality on their clusters)*.

**Cross-theme.** *depends-on* → [D-076](#d-076), [D-064](#d-064) — The substantive routing decisions behind the framing. The dispatch-axis reversal the flag asks after is backends-routing/[D-064](#d-064), rendered beside the in-theme supersession of [D-377](#d-377).

**Source.** `a:ce56e78d-06`, `b:dc3bc182-sub-sub-agent-a74c7a-07`, `a:dc3bc182-sub-sub-agent-ab4c4f-06` · Artifacts: `reports_whole_driver/FINDINGS.md`, `THREATS_TO_VALIDITY.md`

> The routing experiment honestly concluded *no specialist backend beats Mergiraf*. That's a legitimate, publishable finding.
>
> — `2026-06-24_ce56e78d.txt:45`

> **The multi-arm quality-routing thesis is refuted.**
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:70`

### <a id="d-397"></a>D-397 — Only deltas and pre-vs-post comparisons are legitimate readings of the enriched corpus

`2026-06-24 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

*Actors note: The 2026-06-24 source is Claude's; the 2026-07-18 sub-agent report records actors as unclear.*

**Decision.** FINDINGS will not claim any backend beats another on absolute cost for this corpus; only the bare→driver deltas and the routing distribution are presented as legitimate comparisons. The six-tool headline table must likewise not be read as a backend ranking, and Weave's top row (F1 1.00, cost 10) is treated as an abstention artifact rather than evidence of quality.

**Why.** Positives are defined as "Mergiraf clean-but-Tests_failed", so Mergiraf-like backends are guaranteed wrong-and-clean (×10) on them while git's conservatism textually-conflicts more (visible ×1) — a selection effect, not "git wins". The headline metric also rewards abstention: Weave conflicts/abstains and its clean merges happen to be correct on Schesch-50, so the beauty-contest ranking contradicts the deeper causal finding that Weave adds nothing over Mergiraf (strict subset + 71% abstention).

**Status.** adopted.

**Source.** `a:fb0fa5c5-08`, `a:dc3bc182-sub-sub-agent-ab4c4f-10` · Artifacts: `reports_whole_driver/FINDINGS.md`, `reports/results.csv`

> absolute cross-backend cost on this corpus is not a fair comparison — only the bare→driver delta and the routing distribution are.
>
> — `2026-06-24_fb0fa5c5.txt:398`

> This is why the FINDINGS insist the corpus is "not a backend beauty contest" and only deltas/pre-vs-post comparisons are legitimate readings.
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:75`

### <a id="d-398"></a>D-398 — Carry the P2 FINDINGS honesty caveats: corroboration framing, ≤33 FPs, route verification, provenance footnotes

`2026-06-26 → 2026-07-02` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** The P2 whole-driver FINDINGS carry four explicit honesty items: the `driver-auto` result is written up as end-to-end corroboration of the already-decided #27/#28 DROP rather than reopening it; the 33 control false positives are presented as "≤33, direction unambiguous" because they are dev-match-scored; the per-file route verification (Spork 79/INTRA_BODY, Weave 47/MIGRATE_DECL, chosen==effective for all 471, zero crash-fallbacks) is folded in as an explicit "routing executed as designed (0 fallbacks)" line; and the run's driver commit is stated as 843e5f5 because the committed summary.txt header records "driver commit unknown".

**Why.** The per-cluster CI work was already decisive on #27/#28, so P2 only adds the end-to-end cost view. The control FPs are dev-match-scored, so per the W3 lesson some may be valid alternative merges even though the direction is unambiguous. The route verification pre-empts the supervisor's obvious question of whether auto genuinely routed to the specialists rather than silently falling back to git. The commit sha must be stated explicitly because the AWS box ran from a git archive with no .git, so driver_commit() could not resolve it.

**Status.** adopted.

**Source.** `a:fb0fa5c5-23`, `a:fb0fa5c5-22`, `b:fb0fa5c5-42`, `a:fb0fa5c5-26` · Artifacts: `reports_whole_driver/FINDINGS.md`, `reports_whole_driver/summary.txt`, `ISSUES.md`, `843e5f5`

> Flag the **33 control FPs honestly** — they're dev-match-scored, so some may be valid-alternative merges (the W3 lesson); I'll present them as "≤33, direction unambiguous" rather than asserting all 33 are true errors.
>
> — `2026-06-24_fb0fa5c5.txt:1222`

> Want me to fold this verification into FINDINGS as an explicit "routing executed as designed (0 fallbacks)" line? It pre-empts exactly this question from your supervisor.
>
> — `2026-06-24_fb0fa5c5.txt:1249`

### <a id="d-399"></a>D-399 — Rewrite FINDINGS as v2 rather than patching, leaving v1 in git history

`2026-07-02` · **adopted** · `[chat]` · corroboration: single-pass · confidence: medium · actors: claude

**Decision.** Replace reports_whole_driver/FINDINGS.md with a v2 rewrite reflecting the repaired-environment scoring and corrected §7a mechanism, relying on git history to preserve v1.

**Why.** v1 stays in git history.

**Status.** adopted.

**Source.** `b:fb0fa5c5-63` · Artifacts: `reports_whole_driver/FINDINGS.md`, `b6ae027`

> Now the FINDINGS v2 rewrite (v1 stays in git history):
>
> — `2026-06-24_fb0fa5c5.txt:2014`

### <a id="d-400"></a>D-400 — Promote the six-tool neutral run to the canonical thesis headline table

`2026-07-02` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

*Actors note: Two sources record Claude; the sub-agent source records unclear. The directive originates in a project-review document rather than a live Ali ruling in this slice.*

**Decision.** Per the P4 directive in outputs/project-review-future-directions-2026-06-10.md, the six-tool neutral run (n=50, git-merge-file/jdime/mastery/spork/mergiraf/weave) replaces the four-tool reports/results.csv as the thesis headline table (legacy archived), with Wilson CI columns added to metrics, a per-scenario pivot export, and a 5-chart pack behind a viz extra; ISSUES #4/#5/#9 close. Weave's precision 1.0 [0.91, 1.0] / cost 10 row carries an explicit caveat that Weave abstains (TN 10) and that on the targeted MIGRATE_DECL gate its correct merges were a strict subset of Mergiraf's.

**Why.** The old canonical table excludes the driver's own backends — mergiraf and weave lived only in reports_neutral/ and expansion sets — so the thesis headline table should be the six-tool neutral run. Weave's row needs the caveat because high precision on an easy corpus is not specialist value; the #28 targeted gate showed its wins were a subset of Mergiraf's.

**Status.** adopted. Supersedes: *4-tool reports/results.csv as canonical*; *Four-tool reports/results.csv as canonical headline (n=50, git/jdime/mastery/spork)*.

**Cross-theme.** *depends-on* → [D-189](#d-189) — The reporting-infrastructure half (Wilson CIs, pivot export, chart pack) has no separate entry; the comparison-design pivot is linked. No dedup needed.

**Source.** `a:fb0fa5c5-35`, `a:fb0fa5c5-36`, `a:fb0fa5c5-sub-sub-agent-a7dbb3-01` · Artifacts: `229a22d`, `reports/results.csv`, `src/evaluation/report.py`, `src/evaluation/metrics.py`, `outputs/project-review-future-directions-2026-06-10.md`, `merge-tool-comparison/reports_neutral/results.csv`

> Six-tool table **promoted to canonical** `reports/results.csv` (legacy archived), with Wilson CIs, per-scenario pivot, 5 charts — legacy tools reproduced exactly (Spork 32/11)
>
> — `2026-06-24_fb0fa5c5.txt:2034`

> High precision on an easy corpus ≠ specialist value; the FINDINGS note will say so.
>
> — `2026-06-24_fb0fa5c5.txt:1965`

### <a id="d-401"></a>D-401 — Footnote driver-mergiraf's med_rt = 0.0 as assembled from Stage C

`2026-07-02` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Add a footnote to FINDINGS explaining that `driver-mergiraf`'s reported median runtime of 0.0 reflects assembly from the Stage-C cache and that its real latency is ~74 s/file.

**Why.** Without the footnote a reader could conclude detection is free on that arm.

**Status.** adopted. S12 (2026-07-26): the footnote exists — reports_whole_driver/FINDINGS.md:142-143: 'driver-mergiraf's med_rt 0.0 is an assembly artifact — its real cost is Stage C's 74 s/merge median.'

**Source.** `a:fb0fa5c5-27` · Artifacts: `reports_whole_driver/FINDINGS.md`

> **4. `driver-mergiraf med_rt = 0.0` is misleading** — it's assembled from Stage C, so its real latency (~74 s/file median, from the Stage-C run) doesn't appear. A reader could think detection is free on that arm. One footnote fixes it.
>
> — `2026-06-24_fb0fa5c5.txt:1353`

### <a id="d-402"></a>D-402 — Produce report charts with matplotlib+seaborn, accepting a pyproject dependency bump

`2026-07-02` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** For issue #4, add matplotlib/seaborn to merge-tool-comparison/pyproject.toml and add chart export functions to report.py (e.g. to_matplotlib_f1_bars(), to_seaborn_heatmap_per_scenario()), following the existing plotting patterns in data/schesch-dataset/src/python/.

**Why.** matplotlib/seaborn are already used in the schesch-dataset utility scripts (merge_analyzer.py, latex_output.py with PGF/PDF output for LaTeX figures), so the integration is already validated in this project ecosystem; any new chart code nevertheless requires a dependency bump since the libs are not declared in pyproject.toml.

**Status.** adopted. S12 (2026-07-26): landed matplotlib-only — pyproject.toml:17 'viz = ["matplotlib>=3.8"]' and report.py:106 to_charts() (headless Agg backend); seaborn was skipped, and no seaborn dependency exists.

**Cross-theme.** *depends-on* → **no counterpart entry exists** — No tooling/reporting entry records the chart-stack choice (searched all themes). Sole owner; stays proposed.

**Source.** `a:fb0fa5c5-sub-sub-agent-a7dbb3-03` · Artifacts: `merge-tool-comparison/pyproject.toml`, `merge-tool-comparison/src/evaluation/report.py`, `merge-tool-comparison/data/schesch-dataset/src/python/latex_output.py`

> matplotlib/seaborn needed in pyproject.toml
>
> — `2026-07-02_fb0fa5c5_sub-agent-a7dbb3.txt:196`

> Example from schesch-dataset shows seaborn + matplotlib integration already validated in this project ecosystem
>
> — `2026-07-02_fb0fa5c5_sub-agent-a7dbb3.txt:198`

### <a id="d-403"></a>D-403 — Frame the n=50 RM2 recall delta as methodology-tightening, citing the pooled number

`2026-07-03` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: joint

*Actors note: The framing decision is recorded as Ali's; the pooled-number citation guidance is Claude's proposed writeup rule. Both parts describe one positioning choice, so joint.*

**Decision.** Position the RM2 recall deliverable as tightening the THREATS §3 routing-coverage limitation and the detection lane's cross-file FN story, explicitly not as a fix to the router; no routing change is in scope. In the writeup, present the pooled 90.7% as the primary statistic with per-axis (ours/theirs) numbers as supporting detail, and keep the caveat that this is a "limitation is small" result rather than a capability gain.

**Why.** Post-flip the router is NONE→git else→Mergiraf, so misclassification stakes are low, making the number a limitation/methodology statement rather than an input to a routing change. The ours-axis CI [68.6, 90.0] still straddles the old Path B/D boundary, so leading with per-axis numbers would overstate uncertainty resolution.

**Status.** adopted.

**Source.** `a:7b3b2669-01`, `a:7b3b2669-14` · Artifacts: `THREATS_TO_VALIDITY.md §3`, `STATUS.md`, `merge-tool-comparison/ISSUES.md #26`

> the detection lane's cross-file FN story), NOT as a routing fix.
>
> — `2026-07-03_7b3b2669.txt:16`

> it's a "limitation is small" result, not a capability gain
>
> — `2026-07-03_7b3b2669.txt:130`

### <a id="d-404"></a>D-404 — Withdraw the "maybe our corpus was unusual" hedge on the base-rate finding

`2026-07-04` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The base-rate finding may no longer be hedged as a corpus artifact: two independent corpora now agree that the taxonomy's covered categories are rare among real interference (spgroup puts 12 of 17 positives in #1/#2, which the driver never implemented). It is recorded as a corroborated finding rather than a caveat.

**Why.** "Two independent corpora now agree: the taxonomy's covered categories are rare among real interference. That's now a corroborated finding, not a caveat."

**Status.** adopted. S12 (2026-07-26): the hedge is gone — no 'unusual corpus' wording exists in STATUS.md or THREATS_TO_VALIDITY.md; STATUS.md:191 states 'the Stage-C base-rate finding corroborated on a second corpus', which is exactly the corroborated framing this entry required. Supersedes: *the base-rate finding softened as "maybe our corpus was unusual"*.

**Cross-theme.** *depended on by* ← [D-022](#d-022) (see the reconciliation note there)

**Source.** `a:8740dbd3-15` · Artifacts: `THREATS_TO_VALIDITY.md`, `STATUS.md`

> You can no longer soften the base-rate finding as "maybe our corpus was unusual."
>
> — `2026-07-03_8740dbd3.txt:351`

> Two independent corpora now agree: the taxonomy's covered categories are rare among real interference. That's now a corroborated finding, not a caveat.
>
> — `2026-07-03_8740dbd3.txt:351`

### <a id="d-405"></a>D-405 — Bar the unqualified "detects semantic conflicts" claim; shift weight to what is measured

`2026-07-04 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

*Actors note: Two sources record Claude; the sub-agent report records unclear. No source shows Ali ruling.*

**Decision.** Thesis and docs must not claim "detects semantic conflicts" unqualified. The wording becomes: detects the rename/declaration (#6) family; screens the rest at zero measured FP cost; measured recall bounds published for everything else. Category #3 phrasing stays at "partial — literal clear→read shape, measured FN on the one benchmark instance outside that shape." The thesis pitch correspondingly shifts weight to the affirmatively measured parts — routing/backend selection, the #6 family (11 CAUSAL hits at 0 FP), and detection-as-free-insurance — and the detection layer is claimed and defended on its zero-false-block record across two independently constructed corpora (0/66 external oracle + 0/193 Stage-C), explicitly accepting bounded recall (0/17, ≤18.4%) rather than trading FPs for coverage.

**Why.** The measured 0/17 recall [0, 18.4] and the concrete missed reassignment-style stale read mean the limit "is no longer hypothetical; it has a concrete measured miss". Only routing, the #6 family and the zero-FP screening are affirmatively measured; detection of the remaining categories requires semantic/behavioral analyses (SDG-, test-, or OA-class) whose published recall on this benchmark is itself ≤0.28. The benchmark's interference mass sits in behavioral/SDG-class shapes the structural layer does not target, so recall is bounded by scope and what distinguishes the layer against a comparable analysis on the same data is its FP cost.

**Status.** adopted. S12 (2026-07-26): the docs carry the qualified formula — STATUS.md:189-191 states the family-scoped claim with measured bounds ('name-binding family … added recall 37.8%', 'Zero adjudicated FPs on 363 control units', '#3 honest scope … the name is aspirational'), CLAUDE.md says 'covers 3 of 7 conflict categories' with the narrow-PoC framing, and no unqualified 'detects semantic conflicts' claim appears in either. Thesis text pending, but the rule governs the docs it named. Supersedes: *STATUS sentence 'per-category FN rates still await the Phase-2b oracle'*; *"per-category FN rates still await the Phase-2b static-semantic-merge oracle" / any unqualified claim that the driver detects data-flow interference*.

**Cross-theme.** *depends-on* → [D-176](#d-176), [D-260](#d-260) — The 0/17 and 0/66 (Phase-2b) and frozen Stage-C numbers behind the claim-wording rules originate in these.

**Source.** `a:8740dbd3-14`, `a:8740dbd3-16`, `a:dc3bc182-sub-sub-agent-a495a0-03` · Artifacts: `STATUS.md`, `THREATS_TO_VALIDITY.md`, `CLAUDE.md`, `merge-tool-comparison/reports_detection/phase2b/FINDINGS.md`

> Don't claim "detects semantic conflicts" unqualified — claim *detects the rename/declaration family; screens the rest at zero cost; measured recall bounds published for everything else*.
>
> — `2026-07-03_8740dbd3.txt:382`

> **The layer's differentiator is its FP cost, not its coverage.**
>
> — `2026-07-18_dc3bc182_sub-agent-a495a0.txt:49`

### <a id="d-406"></a>D-406 — Claim bounded severity of false blocks, not impossibility of false blocks

`2026-07-06` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The defensible claim about false blocks is that they are fail-safe and bounded to cost ×1 (a correct merge surfaced for review), not that they are impossible; R1 = 0% is reported as an empirical result on this corpus with a CI, not a structural guarantee.

**Why.** "Where you should plant your flag is not 'false blocks are impossible' — a reviewer will produce the 4 you already found and you'll lose the point." The severity claim is stronger and more defensible than impossibility because it is about severity, which the design does bound, rather than occurrence, which it doesn't.

**Status.** adopted. Supersedes: *the user's claim that blocking good merges is "not possible by definition of thesis project"*.

**Source.** `a:4c7b0828-05`

> **R1 = 0% is an empirical result on this corpus, not a structural guarantee.**
>
> — `2026-07-06_4c7b0828.txt:295`

> reframe your instinct from *"it can't block good merges"* to *"when it wrongly blocks a good merge, the cost is bounded and recoverable — never an incorrect result."*
>
> — `2026-07-06_4c7b0828.txt:299`

### <a id="d-407"></a>D-407 — Attribute R2 and R1 to their own runs, never to one

`2026-07-06` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** When reporting "R2 6.7%, R1 0%" together, always attribute R2 to the frozen adjudicated Stage-C run (detectors frozen at 843e5f5) and R1 0/193 to the post-fix run, never implying a single run; the frozen run's R1 was 4/193 = 2.1%.

**Why.** They come from two different runs, so presenting them as one would be misleading: "just don't imply they're from a single run — the frozen run had R1 = 2.1%, and the post-fix run confirmed R1 → 0%".

**Status.** adopted.

**Source.** `a:4c7b0828-02` · Artifacts: `ISSUES #29`, `843e5f5`

> They come from **two different runs**, and you should cite them as such:
>
> — `2026-07-06_4c7b0828.txt:245`

> just don't imply they're from a single run — the frozen run had R1 = 2.1%, and the post-fix run confirmed R1 → 0% with zero change to the positive verdicts.
>
> — `2026-07-06_4c7b0828.txt:249`

### <a id="d-408"></a>D-408 — Ship decks without embedded notes and carry an AWS provenance band on the data slides

`2026-07-06 → 2026-07-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: The no-notes rule is Claude's diagnosis and default; the AWS band was Ali's request. Both are recorded in the same deck-build sequence.*

**Decision.** build_deck_v6.py (and later v7) defaults to producing a .pptx with no embedded speaker notes, writing narration to a companion markdown file regenerated from the same source; embedded notes are available only behind WITH_NOTES=1 as a PowerPoint variant and must not be opened in Keynote. Slides 4, 5 and 6 each carry a dark AWS provenance band with a coral "☁ AWS EC2" chip listing instance class (c7i.2xlarge, native x86-64), run hours/cost, build-on-instance discipline, teardown verification, and the slide-specific rigor point.

**Why.** Root cause found: "Keynote silently refuses to open any python-pptx file with embedded notes" (the no-notes file opens fine; both ASCII and rich notes fail), and since Ali uses Keynote the deck must ship without embedded notes. The AWS band was requested by Ali ("also need a highlight on my effort on using aws") with no further reason recorded.

**Status.** adopted. Supersedes: *earlier build that embedded speaker notes in the pptx*.

**Cross-theme.** *depends-on* → [D-312](#d-312), [D-316](#d-316), [D-317](#d-317) — The provenance-band content (instance class, teardown discipline, cost) owners.

**Source.** `a:4c7b0828-04`, `a:4c7b0828-06`, `b:16127d04-02` · Artifacts: `build_deck_v6.py`, `presentation/thesis_progress_jul2026.pptx`, `speaker_notes_jul2026.md`, `presentation/speaker_notes_late_jul2026.md`

> Root cause found: **Keynote silently refuses to open any python-pptx file with embedded notes**
>
> — `2026-07-06_4c7b0828.txt:461`

> enrich slides 4,5,6 with the information from this descriptions. also need a highlight on my effort on using aws
>
> — `2026-07-06_4c7b0828.txt:409`

### <a id="d-409"></a>D-409 — Present the 7-category taxonomy as fixture-derived design apparatus, not a validated classification

`2026-07-08` · **proposed** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Present the 7 categories explicitly as a fixture-derived working taxonomy used as design apparatus; the contribution is the calibrated version (categories + measured base rates + CIs), with an optional regrouped four-family view offered alongside the historical 7.

**Why.** "It was never a validated empirical classification — no systematic literature review behind the specific set of 7, no grounded-theory pass over real conflicts"; the abstraction levels are uneven, it is not exhaustive and not crisply decidable, so presenting it as a classification invites the critique.

**Status.** proposed. S12 (2026-07-26): still pending — the presentation decision is for the thesis taxonomy chapter, which does not exist; STATUS/FINDINGS already carry the calibrated-version substance (measured base rates + CIs, the four-family view as a hypothesis), but the fixture-derived framing as a chapter choice is unmade.

**Source.** `a:4c7b0828-08` · Artifacts: `semantic_merge_driver/ResearchSummary.xml`

> **Reframe it explicitly as a fixture-derived working taxonomy**, not a contribution-grade classification.
>
> — `2026-07-06_4c7b0828.txt:614`

> the 7 categories are a **fixture-derived design taxonomy**: seven directories of hand-written Java examples
>
> — `2026-07-06_4c7b0828.txt:583`

### <a id="d-410"></a>D-410 — Never blend numbers across instruments; state every result per-instrument

`2026-07-11 → 2026-07-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** FINDINGS and the thesis must never present numbers from different instruments in the same claim. Taxonomy base-rate numbers are never combined with Stage-C R1/R2 or Phase-2b numbers; the S-D7 instrument record (R2' 6.7%→22.0%, R1' 0→2/193 with 0 adjudicated FPs) is stated per-instrument and never summed with the S-D5 zero-FP record; the summary table gives one instrument per row with explicit reading rules and no figure combining instruments; the thesis cites the held-out taxonomy instrument's 43.2% family recall as the causal/mechanism claim and the Stage-C 22.0% R2' as the deployment/operational claim; the derivation-split overlap of the 164 positives is annotated as labeled context only, with no S-D5 numbers in derived figures; and every numbers slide in the deck carries a "MEASUREMENT N OF 4" chip so 71.4 / 43.2 / 22.0 / −11.5 are not conflated. Blend-safe comparison requires re-running the original protocol.

**Why.** The instruments have different units, denominators and causal adjudication, so quoting them side by side would be an instrument blend — "don't write 'recall improved from Stage C's 6.7% to X%'". Stage-C semantics are what the driver actually does in deployment, while the held-out taxonomy instrument carries the causal ruling, so each headline belongs on its own instrument. The deck chips keep the four headline numbers from being conflated by the audience.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-262](#d-262), [D-190](#d-190) — One rule stated in three scopes: gate discipline, instrument inventory, framing. All three cross-linked, kept.

**Source.** `a:4c7b0828-22`, `a:06ec13eb-05`, `a:06ec13eb-13`, `b:06ec13eb-13`, `a:16127d04-02` · Artifacts: `reports_taxonomy/FINDINGS.md`, `reports_detectors/FINDINGS.md`, `reports_detectors/stagec_rerun/`

> **Respect the never-blend rule in the obvious temptation:** don't write "recall improved from Stage C's 6.7% to X%" — different instruments and populations.
>
> — `2026-07-06_4c7b0828.txt:1518`

> The S-D5 43.2% is the mechanism claim (causal, family-pooled); the S-D7 22.0% is the operational claim. The thesis needs both, and now has each on its proper instrument.
>
> — `2026-07-22_06ec13eb.txt:243`

### <a id="d-411"></a>D-411 — Start the thesis write-up now and treat detector work as the optional parallel track

`2026-07-15` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Begin the write-up immediately with D1–D3 as a parallel additive track; detector results occupy exactly one optional results section plus one contributions line, and the write-up cites only committed FINDINGS numbers, never numbers from a live session.

**Why.** "The thesis no longer has open empirical dependencies", and "the risk profile is asymmetric: an unfinished thesis with finished detectors is a problem; a finished thesis with the detector section marked 'future work...' is a perfectly defensible document".

**Status.** adopted. S12 (2026-07-26): partially begun at the planning level only — the outline/spine sessions ran (2026-07-18/22/25) and the detector cycle did run as a parallel track, but no chapter draft, spine document or claims ledger exists in the repo, so 'begin the write-up immediately' is not yet evidenced. | Housekeeping PR (2026-08-06): ratified proposed->adopted - the write-up now exists and enacts the decision: thesis/00-spine.md, claims-ledger.md, and merged chapters 1-5 (PRs #3-#9); detector results are cited from committed FINDINGS numbers only.

**Source.** `a:4c7b0828-26`

> If anything, invert the priority you implied: **start the write-up now, let detectors fill slack.**
>
> — `2026-07-06_4c7b0828.txt:1617`

> **Citation discipline is the one coordination rule**: the write-up cites committed numbers from FINDINGS files only — never numbers from a live session.
>
> — `2026-07-06_4c7b0828.txt:1611`

### <a id="d-412"></a>D-412 — Verify cited numbers against the underlying data and artifacts before publishing

`2026-07-15 → 2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Cited FINDINGS numbers are verified against the underlying data before publication — §3.1 Jaccard corrected from 0.92 to 0.942 and §6 secondary prevalence from ~7% to 8.0%. Likewise, when asked where 1994/1784/1579 came from, the actual committed run artifacts (FINDINGS rows, summary.txt, scenarios.csv, predicted_flagoff.csv) are pulled and each total re-derived from the price weights rather than answered from memory.

**Why.** Stated as verifying the cited numbers against the actual data before continuing; and "let me pull the actual run artifacts so the provenance is exact, not from memory" — the per-file rows in scenarios.csv let anyone re-add the columns and get the same totals.

**Status.** adopted.

**Source.** `a:9e4b6896-31`, `a:16127d04-14` · Artifacts: `merge-tool-comparison/reports_taxonomy/FINDINGS.md`, `merge-tool-comparison/reports_whole_driver/FINDINGS.md:57`, `merge-tool-comparison/reports_detectors/whole_driver_flagon/summary.txt`

> Let me verify two numbers I cited in FINDINGS (§3.1 Jaccard and §6 secondary prevalence) against the actual data before continuing.
>
> — `2026-07-11_9e4b6896.txt:1264`

> let me pull the actual run artifacts so the provenance is exact, not from memory.
>
> — `2026-07-24_16127d04.txt:284`

### <a id="d-413"></a>D-413 — Cite the pooled name-binding family number; per-category cells stay bounded, not pinned

`2026-07-16 → 2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** The pooled name-binding family figure is the citable primary number and per-category recall cells are framed as "bounded, not pinned"; the end-of-cycle claim is scoped to "the category's dominant file-local shapes, detected with zero measured FP across three control corpora". CAUSAL rulings are required before calling any flag recall, machine-caught stays any-lane per plan §9 with lane-vs-label attribution descriptive only, and cross-category catches (e.g. D1 catching the vojtechhabarta relocation unit) count in their label's per-category row.

**Why.** n=21 for design and ~14 for held-out per-category measurement give wide Wilson intervals, so per-category cells cannot support a pinned claim; machine-caught ≠ recall until the S-D6 CAUSAL rulings. Category edges are also fuzzy — a relocation executed as an import swap is file-locally an import prune — which is precisely why the pooled number is the one that survives boundary disputes.

**Status.** adopted.

**Source.** `a:f0d70a59-11`, `b:2e726dc0-09`, `a:2e726dc0-20` · Artifacts: `outputs/detector-cycle-plan.md §9`

> The honest claim available at the end of this cycle is "the category's dominant file-local shapes, detected with zero measured FP across three control corpora" — not "the category, solved."
>
> — `2026-07-16_f0d70a59.txt:228`

> That fuzziness at category edges is precisely why the plan makes the pooled number primary and frames per-category rows as bounded, not pinned
>
> — `2026-07-16_2e726dc0.txt:695`

### <a id="d-414"></a>D-414 — Scope literature and prior-art consultations tightly: research-only, cited, compact

`2026-07-16 → 2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: ali

**Decision.** Prior-art and literature consultations are run as bounded research tasks with no code changes. The analyzer prior-art comparison covers exactly four tools (Error Prone, SpotBugs, IntelliJ IDEA, Checkstyle) on unresolved-reference handling and rename propagation, citing a specific doc page/source file/issue URL for each, plus a closing section on prior art for differential/three-way analysis, delivered as a structured markdown report under ~120 lines and nothing else in the final message. The baseline-paper extraction is delivered as compact prose over six requested axes with conclusions only and a hard cap of two short quotes.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-464](#d-464) (see the reconciliation note there)

**Source.** `a:82dd479f-sub-sub-agent-aadfd1-01`, `a:dc3bc182-sub-sub-agent-a71788-02`

> Return a structured markdown report: one section per tool with citations, plus a final "prior art for differential/3-way analysis" section. Keep it under ~120 lines.
>
> — `2026-07-16_82dd479f_sub-agent-aadfd1.txt:14`

> Conclusions only, no long quotes (max 2 short quotes).
>
> — `2026-07-18_dc3bc182_sub-agent-a71788.txt:13`

### <a id="d-415"></a>D-415 — Report the D2 file-local ceiling decomposition as a boundary result, not a detector failure

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Commit to reporting the 0-of-14 ceiling decomposition for D2 in S-D6 alongside Amendment 2's, framing a possible near-zero held-out yield as a measured file-local ceiling result rather than a detector failure.

**Why.** Amendment 2 obliges ceiling reporting; the category's mass sits in cross-file and type-level shapes no merge-driver-local detector can reach, and the two-arm design attributes that cleanly — so it is a boundary result the plan was built to produce.

**Status.** adopted. S12 (2026-07-26): reported as committed — reports_detectors/FINDINGS.md:44 carries 'stale-caller-of-changed-signature (D2's target) | 0/14 = 0% | [0, 21.5]' and :107 the 'D2: 0 held-out flags, 0/14 on its category' framing as a file-local-ceiling result, alongside Amendment 2's decomposition per the S-D6 obligation.

**Source.** `a:acf7e1d0-17`

> S-D5 measures held-out recall and S-D6 must report this ceiling decomposition alongside Amendment 2's.
>
> — `2026-07-16_acf7e1d0.txt:451`

> it's a boundary result the plan was built to produce: *file-local arity-based detection of this category has near-zero yield despite zero FP cost, because the category's mass sits in cross-file and type-level shapes no merge-driver-local detector can reach.*
>
> — `2026-07-16_acf7e1d0.txt:491`

### <a id="d-416"></a>D-416 — Lead the thesis title with the empirical finding, keeping Java/Git and barring collision phrases

`2026-07-18 → 2026-07-18` · **proposed** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Recommend a two-part title leading with the empirical finding — initially titles #4 ('When Clean Merges Break: An Empirical Taxonomy of Silent Merge Failures and a Semantic Safety Net for Git') or #5, with descriptive #1 as conservative fallback; later refined to framing B or an A×B hybrid, working title "Where Merges Break Silently: Measuring and Detecting Semantic Conflicts in Java Git Histories", with routing refutation and comparator methodology demoted to chapters. Constraints on any title: it must contain "Java" or "Git"; it must not put "composition" or "routing" in the main title as a promise; and "evaluation of merge tools" is barred outright. Run the shortlist past the advisor.

**Why.** The thesis's real shape is measurement-first — taxonomy, base rates, refutations — with the driver as the evidence-driven artifact, so the title should put the empirical finding in front while the subtitle promises the artifact; the census and the zero-FP detection record are the two results that are simultaneously novel, positive and gate-hardened. "Java" must stay because external validity is Java-only and the title shouldn't overclaim generality; "composition" and "routing" are barred because the evidence supports them only as questions, not achievements; "evaluation of merge tools" is a direct collision with the Schesch et al. paper title. Title taste is the one axis where the advisor's preference cheaply outranks any argument.

**Status.** proposed. S12 (2026-07-26): still pending — no title has been chosen; the advisor shortlist review has not happened and no thesis title page exists. Supersedes: *Earlier README-derived title recommendation at line 5*; *Earlier title constraints at line 24 (avoid overclaiming verbs; keep Git and merge in title)*.

**Source.** `b:4c7b0828-47`, `a:dc3bc182-03`, `a:dc3bc182-04`, `a:dc3bc182-10`

> B, or an A×B hybrid — e.g. ***Where Merges Break Silently: Measuring and Detecting Semantic Conflicts in Java Git Histories***
>
> — `2026-07-18_dc3bc182.txt:326`

> keep "Java" or "Git" in the title (external validity is Java-only), and don't put "composition" or "routing" in the main title as a promise — the evidence supports them only as questions, not as achievements
>
> — `2026-07-18_dc3bc182.txt:326`

### <a id="d-417"></a>D-417 — Ground thesis framing in the code and measured artifacts, not a single README

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** Framing and title proposals must be derived from an analysis of the actual code and measured artifacts across both subprojects, not from one document (the README), and several distinct framing approaches must be offered rather than one list.

**Why.** Ali objected that the first suggestion set was dictated by one file and did not reflect an understanding of the project's goal.

**Status.** adopted. Supersedes: *Initial title list derived mainly from the README (line 5-24)*.

**Source.** `a:dc3bc182-01`

> dont let one file dictate suggestions analyse and try to understand goal of the project
>
> — `2026-07-18_dc3bc182.txt:26`

> Fair — I'll analyze the actual code and measured artifacts across both subprojects first, then propose distinct framing approaches.
>
> — `2026-07-18_dc3bc182.txt:28`

### <a id="d-418"></a>D-418 — Draft the abstract with Zeller's five moves, labelled blocks and a bracketed pending slot

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: Ali chose the technique; Claude set the drafting conventions.*

**Decision.** The thesis abstract is drafted using Zeller's five-move structure, with one block per move carrying inline labels to be stripped later, numbers quoted rather than adjectives, still-pending results marked in ⟨angle brackets⟩ (the S-D5 held-out eval), and no claim that outruns a frozen report.

**Why.** Ali chose the Zellerisation technique without recording a reason. The conventions were justified on the grounds that labels let each move be checked and every number must trace to the frozen reports, so nothing in a draft outruns a measured result except the explicitly marked pending slot.

**Status.** adopted.

**Source.** `a:dc3bc182-05`, `a:dc3bc182-06` · Artifacts: `reports/`, `reports_whole_driver/`, `reports_taxonomy/`, `reports_detection/`

> generate drafts for thesis abstract. Use zellerisation technique
>
> — `2026-07-18_dc3bc182.txt:328`

> nothing in any draft outruns a measured result except the marked pending slot
>
> — `2026-07-18_dc3bc182.txt:344`

### <a id="d-419"></a>D-419 — The n=50 six-tool table may never be presented as a rival tool ranking

`2026-07-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The six-tool comparator table is restricted to two roles — backend-selection evidence for the driver, and the vehicle for the oracle/comparator-gap finding — and must never be presented as a ranking competing with Schesch's RQ2.

**Why.** At n=50 versus their 6,045 merges the table is not a credible rival ranking; reframing it removes the direct collision.

**Status.** adopted. S12 (2026-07-26): still pending — the claim restriction binds thesis text that does not exist yet; the outline (Ch. 3: 'explicitly not framed as a ranking rivaling Schesch's RQ2') aligns with it, but only a drafted chapter can settle it. | Housekeeping PR (2026-08-06): ratified proposed->adopted - enacted by merged ch.3 (backend-selection reading in RQ1.3; never framed as a ranking rivaling Schesch's RQ2) and by merged ch.5's framing rule citing D-419.

**Source.** `a:dc3bc182-09` · Artifacts: `reports/results.csv`

> At n=50 versus their 6,045, your six-tool table is not a credible rival ranking and must never be presented as one.
>
> — `2026-07-18_dc3bc182.txt:452`

> Its legitimate roles are (a) backend selection evidence for *your* driver and (b) the vehicle for the oracle finding.
>
> — `2026-07-18_dc3bc182.txt:452`

### <a id="d-420"></a>D-420 — Credit Schesch et al. openly with a dedicated relation section, delta table and disjoint RQs

`2026-07-18` · **proposed** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** State the dependencies on Schesch et al. openly — their dataset and test labels as ground truth for census/Stage-C, their simple-beats-complex finding as the thesis premise, IVn as the intellectual ancestor of the router, and the FP×10 weighting as one fixed point of their unknown-k sweep (footnoted). Insert a ~1-page "Relation to Schesch et al." section in the introduction carrying the axis-by-axis delta table (question, tools, oracle, failure analysis, silent failures, composition, scale). Re-pose the thesis RQs so none overlaps their RQ1–RQ4, and fix what each chapter may claim: comparator chapter = oracle finding plus post-paper tool coverage (never a ranking); census chapter = the anatomy their oracle counts but cannot explain; driver chapter = the detector their threats section concedes is missing; routing chapter = refutation of the composition generalisation.

**Why.** Reusing their data is a strength (comparability) provided it is stated, and the honest result that the IVn generalisation failed corroborates their thesis under a different oracle rather than repeating it. The examiner will ask about the overlap, so answer it before they do; and since their questions ask which tool is best, the thesis must occupy the gaps their paper concedes rather than restate their questions. No reason was recorded for the per-chapter claim-hygiene split specifically.

**Status.** proposed. S12 (2026-07-26): still pending — no drafted introduction exists; the delta-table content is prepared in the outline sessions but no section has been written.

**Source.** `a:dc3bc182-11`, `a:dc3bc182-07`, `a:dc3bc182-08`, `a:dc3bc182-12` · Artifacts: `evolution.md`

> ## Where you genuinely depend on them — credit loudly, don't hide
>
> — `2026-07-18_dc3bc182.txt:456`

> **Add a "Relation to Schesch et al." section (~1 page) in the introduction**, with the delta table above. The examiner will ask; answer before they do.
>
> — `2026-07-18_dc3bc182.txt:464`

### <a id="d-421"></a>D-421 — Report the 56.7% escape stratum as a first-class result, not instrument failure

`2026-07-18` · **adopted** · `[chat]` · corroboration: single-pass · confidence: medium · actors: unclear

**Decision.** The 156/275 (56.7%) census units that could not be pinned to a mechanism in the intersecting files are reported as a named escape stratum (none-identified / indeterminate / flaky-suspect) and interpreted as a property of the merge-level test signal rather than unattributed residue or instrument error.

**Why.** The cause for these units sits cross-file, in the build, or in nondeterminism, so it is out of reach of an intersecting-files instrument by construction; attribution is stratum-robust (A 43.3% vs B 43.2%) and does not collapse under input truncation.

**Status.** adopted.

**Cross-theme.** *duplicated by* ← [D-207](#d-207) (see the reconciliation note there)

**Source.** `a:dc3bc182-sub-sub-agent-a495a0-04` · Artifacts: `merge-tool-comparison/reports_taxonomy/FINDINGS.md`, `ISSUES.md #30`

> could not be cleanly pinned to a mechanism in the intersecting files — not instrument failure but a property of the merge-level test signal (cause sits cross-file, in the build, or in nondeterminism)
>
> — `2026-07-18_dc3bc182_sub-agent-a495a0.txt:57`

### <a id="d-422"></a>D-422 — Verify evolution.md is the genuine paper text before using it as a primary source

`2026-07-18` · **adopted** · `[chat]` · corroboration: single-pass · confidence: high · actors: joint

*Actors note: The verification precondition was set by Ali in the sub-agent brief; the verdict and primary-source reporting were Claude's.*

**Decision.** Before treating repo-root `evolution.md` as the text of Schesch et al., ASE 2024, confirm it in chunks; if it is not the paper text, say so clearly and reconstruct the paper's method from the most detailed secondary descriptions in the repo (THREATS_TO_VALIDITY.md, merge-tool-comparison/README.md, docs/plans/, PRESENTATION_PLAN.md), explicitly marked as secondhand. After reading all 1808 lines and confirming title, authors, venue (ASE '24, arXiv:2410.09934v1), all 10 sections and references, the extraction was reported entirely from evolution.md as primary source with line-level citations, and the secondhand fallback was not used.

**Why.** The file only 'reportedly' contains the paper text, so its provenance must be established before its content is used; any fallback material is lower-grade evidence and must be labelled as such. The verification confirmed the genuine full body of the paper (abstract through references, figures as inline text), satisfying the precondition for primary-source reporting.

**Status.** adopted.

**Source.** `a:dc3bc182-sub-sub-agent-a71788-01`, `b:dc3bc182-sub-sub-agent-a71788-02` · Artifacts: `evolution.md`, `THREATS_TO_VALIDITY.md`, `merge-tool-comparison/README.md`, `PRESENTATION_PLAN.md`

> If evolution.md turns out NOT to be the paper text, say so clearly and instead gather what the paper did from the most detailed secondary descriptions in the repo
>
> — `2026-07-18_dc3bc182_sub-agent-a71788.txt:13`

> Confirmed. evolution.md IS the genuine full text of the paper (title, authors, ASE '24, arXiv:2410.09934v1, all 10 sections + references).
>
> — `2026-07-18_dc3bc182_sub-agent-a71788.txt:31`

### <a id="d-423"></a>D-423 — Structure the write-up on the Passau empirical-SE house style, 11 chapters over 60 pages

`2026-07-22` · **superseded** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Adopt an 11-chapter, page-budgeted 60-page structure in the empirical-SE Passau house style: explicit RQs up front, evidence chapters with their own setup/results/interpretation, a dedicated threats chapter, a replication package, and a background chapter presenting the unstructured→semistructured→structured arc as the Passau lineage.

**Why.** It matches the house style of the Passau lineage and is tactically smart because the structured-merge tradition the thesis evaluates originates at Passau (FSTMerge, JDime).

**Status.** superseded. Superseded by [D-424](#d-424) — Revise to 12 chapters, adding methodology/infrastructure and AI-contributions chapters.

**Source.** `a:dc3bc182-13`

> Structure below follows the empirical-SE house style of the Passau lineage (explicit RQs up front, evidence chapters with their own setup/results/interpretation, a real threats chapter, replication package)
>
> — `2026-07-18_dc3bc182.txt:474`

> which is also tactically smart, because the structured-merge tradition your thesis evaluates *originates* at Passau
>
> — `2026-07-18_dc3bc182.txt:474`

### <a id="d-424"></a>D-424 — Revise to 12 chapters, adding methodology/infrastructure and AI-contributions chapters

`2026-07-22` · **proposed** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Revise the 60-page skeleton to 12 chapters: new Ch. 5 "Experimental methodology & infrastructure" (4 pp, absorbing run mechanics from Ch. 3/6/8) and new Ch. 9 "AI and author contributions" (3 pp); Ch. 2 absorbs the old related-work chapter; discussion trimmed to 2 pp.

**Why.** Ali's four additional content requirements slot in cleanly this way while keeping the evidence chapters results-focused.

**Status.** proposed. S12 (2026-07-26): still pending — the outline remains unsigned-off; no spine document exists in the repo, so the 12-chapter skeleton is not yet the operative structure. Supersedes: [D-423](#d-423) — Structure the write-up on the Passau empirical-SE house style, 11 chapters over 60 pages.

**Source.** `a:dc3bc182-18`

> they slot in cleanly if you add two chapters (a methodology/infrastructure chapter and an AI-contribution chapter) and keep the evidence chapters results-focused
>
> — `2026-07-18_dc3bc182.txt:504`

### <a id="d-425"></a>D-425 — Thesis must cover experiment mechanics, AWS deployment, AI-use transparency and adjudication tooling

`2026-07-22` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** Four additional content requirements are mandated for the write-up: how the experiments were performed, how the system was deployed to AWS, transparent accounting of AI use alongside the author's own contribution, and the tools used for adjudication and ruling.

**Why.** Ali states AI's contribution is very large and his own contribution needs to be shown.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-236](#d-236) (see the reconciliation note there)

**Source.** `a:dc3bc182-17`

> 3) I want to be transparent about ai use as it has very big contribution and need to show off my contribution too
>
> — `2026-07-18_dc3bc182.txt:502`

> I would also include information about 1)how experiments performed; 2) how i have deployed it to aws;
>
> — `2026-07-18_dc3bc182.txt:502`

### <a id="d-426"></a>D-426 — Fix a shared evidence-chapter skeleton with execution mechanics and AWS environment in Ch. 5

`2026-07-22` · **proposed** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** State the shared experimental discipline once in Ch. 5 (pre-registered gates, instrument freezes at named commits, firewalled corpora, two-arm flag0/flag1 designs, control materialisation, deterministic caches/shards, Wilson CIs, human adjudication), and give evidence chapters 3, 6, 7 and 8 an identical skeleton: Design & pre-registration → Materials → Execution → Results → Interpretation, with Execution a paragraph pointing at Ch. 5. Ch. 5 also carries a ~1.5-page "Execution environment" section covering c7i.2xlarge native x86_64, Docker-only invocation with pinned tags, on-instance image builds, the environment-validation protocol (reproduce the canonical six-tool table and probe the formatter before any scoring run), teardown with verify-empty and per-cycle cost; full command sequences go to a reproduction-guide appendix and Ch. 11 threats points at this section.

**Why.** The identical skeleton is the Passau/empirical-SE expectation and it turns the project's working practice into visible method rather than buried process. The validation protocol was born from the arm64 google-java-format incident that mis-scored the whole-driver v1 run, so presenting it as lesson-turned-method doubles as the reliability-threat mitigation story.

**Status.** proposed. S12 (2026-07-26): still pending — depends on the unsigned outline; no Ch. 5 draft or spine document exists.

**Cross-theme.** *depended on by* ← [D-236](#d-236) (see the reconciliation note there)

**Source.** `a:dc3bc182-19`, `a:dc3bc182-20` · Artifacts: `843e5f5`, `732d8ff`, `deploy/aws/CLI-DEPLOY.md`

> each evidence chapter (3, 6, 7, 8) uses an identical subsection skeleton — *Design & pre-registration → Materials → Execution → Results → Interpretation*
>
> — `2026-07-18_dc3bc182.txt:527`

> **environment validation protocol** — reproduce the canonical six-tool table and probe the formatter before any scoring run (a protocol *born from* that incident — present it as a lesson-turned-method)
>
> — `2026-07-18_dc3bc182.txt:531`

### <a id="d-427"></a>D-427 — Organise Ch. 9 by three AI roles, with a delineation table and AI-use log started now

`2026-07-22` · **proposed** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Structure Ch. 9 around three distinct AI roles (engineering collaborator, measurement instrument, writing assistant); the LLM closed-coder in the census is treated as method and documented in Ch. 7's method section, with Ch. 9 only cross-referencing it. Include an Artifact/Decision × Author-role × AI-role delineation table, start that table and an AI-use log immediately as running documents, close the chapter with the exhibit that the human gate demonstrably caught AI failures (fabricated-quote instance, incidental-flag rulings, v1 mis-scoring correction), and write the front-matter AI-use declaration to the current FIM/chair rules rather than to the author's own design.

**Why.** The three roles have different scientific status, and the census coder is method, not assistance. Reconstructing who-decided-what months later is the most painful part of that chapter and the log is needed for the formal declaration; the human-gate exhibit converts "AI did a lot" into evidence that the methodology was designed for that risk. The declaration's wording and placement are prescribed by examination regulations, which German universities have been updating frequently.

**Status.** proposed. S12 (2026-07-26): still pending — no AI-use log or delineation table exists as a running document anywhere in the repo (searched), and no Ch. 9 draft exists. The 'start immediately' clause has not been enacted.

**Source.** `a:dc3bc182-21`, `a:dc3bc182-22`, `a:dc3bc182-23` · Artifacts: `THREATS_TO_VALIDITY.md`, `THREATS_TO_VALIDITY.md §4.4`

> **Ch. 9 (the substantive account):** structure it around the three distinct roles AI played, because they have different scientific status:
>
> — `2026-07-18_dc3bc182.txt:539`

> Start the Ch. 9 **delineation table and AI-use log now, as a running document** — reconstructing who-decided-what months later is the single most painful part of that chapter
>
> — `2026-07-18_dc3bc182.txt:571`

### <a id="d-428"></a>D-428 — Enforce one claim, one home: Ch. 5 is how, Ch. 9 is who, neither restates results

`2026-07-22` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Keep the methodology chapter about how and the contributions chapter about who; neither may restate results. Integration is run as separate sweeps — terminology unification (one name per concept, defined once in Ch. 2), a numbers audit against the ledger, cross-references, a "one claim, one home" check (every result stated fully exactly once, referenced elsewhere), then prose polish.

**Why.** The moment either chapter restates results the evidence chapters lose their claim to them, and the page count suffers; the one-claim-one-home check is what keeps Ch. 5/9/10 from leaking results.

**Status.** adopted. S12 (2026-07-26): still pending — a drafting discipline for chapters that do not exist yet; no integration checklist exists. | Housekeeping PR (2026-08-06): ratified proposed->adopted - enacted by merged ch.5 (strictly how; headline results deliberately absent, one instrument per T5.2 row) and the claims-ledger single-home discipline; the integration sweeps themselves remain queued for the assembly round.

**Source.** `a:dc3bc182-25`, `a:dc3bc182-32`

> keep Ch. 5 strictly about *how* and Ch. 9 strictly about *who* — the moment either starts restating results, the evidence chapters lose their claim to them
>
> — `2026-07-18_dc3bc182.txt:551`

> the "one claim, one home" check (every result stated fully exactly once, referenced elsewhere — this is what keeps Ch. 5/9/10 from leaking results)
>
> — `2026-07-18_dc3bc182.txt:575`

### <a id="d-429"></a>D-429 — Write evidence-out in order of frozenness, ugly-but-complete first, polish last

`2026-07-22` · **proposed** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Do not write front-to-back: write the evidence chapters first in order of frozenness (Ch. 7 census → Ch. 8 detection → Ch. 6 routing → Ch. 3 comparator), then artifact/infrastructure chapters, then framing chapters, then polish. A chapter reaches "all claims present, all numbers from macros, figures as placeholders-with-captions" before any sentence is polished, and each chapter opens with a one-paragraph Zeller-style mini-abstract. Do not block Ch. 8 on the pending S-D5 held-out result — write it with a reserved subsection. After the spine, take Ch. 7 to reviewable-draft quality and send it to the supervisor before writing the rest.

**Why.** The results already exist as frozen committed FINDINGS files, so writing is mostly transcription and reframing; interpretation can shift while framing chapters are unwritten, frozen results cannot. Polishing early chapters while late ones don't exist is how 60-page theses stall at page 30. The pre-registered design makes either S-D5 outcome writable — good recall strengthens the story, weak recall becomes an honest FN-ceiling finding. Sending Ch. 7 early sets style, depth and citation-density expectations before five chapters are written in the wrong register; examiners skim, and the mini-abstracts are what they read twice.

**Status.** proposed. S12 (2026-07-26): still pending — no chapter drafts exist, so the writing order has not begun.

**Source.** `a:dc3bc182-26`, `a:dc3bc182-29`, `a:dc3bc182-30`, `a:dc3bc182-31` · Artifacts: `reports_detectors/eval/`

> Don't write front-to-back; write evidence-out.
>
> — `2026-07-18_dc3bc182.txt:555`

> polishing early chapters while late ones don't exist is how 60-page theses stall at page 30
>
> — `2026-07-18_dc3bc182.txt:580`

### <a id="d-430"></a>D-430 — Fix the spine and claims ledger first, get supervisor sign-off before any prose

`2026-07-22` · **proposed** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Before writing prose, fix the title, RQ1–4, contributions list and a one-page bullet skeleton per chapter, and send that spine for supervisor sign-off; the first concrete step is creating the spine document and claims ledger this week. Maintain one file mapping every citable number to its frozen source, define each number once as a LaTeX macro generated from that ledger, and never type a number inline. Track progress by page burn-down against the chapter budget table rather than by "chapter done", with appendices absorbing overflow (full result tables, normalization-tier catalogue, adjudication protocols, fixture batteries, detector specs, reproduction guide) and an over-running chapter cut or moved immediately.

**Why.** A supervisor correcting a skeleton costs an hour; correcting a written chapter costs a week. The ledger-plus-macros discipline kills number-drift across 60 pages, makes the final audit mechanical, turns defence prep into reading one table, and — given the fabricated-quote lesson — acts as the mechanical guard when AI drafts prose from the reports. The budget from the structure is the scope contract.

**Status.** proposed. S12 (2026-07-26): still pending — no spine document and no claims ledger exist in the repo (searched for spine/claims-ledger/macros); supervisor sign-off has not happened.

**Source.** `a:dc3bc182-28`, `a:dc3bc182-27`, `a:dc3bc182-33` · Artifacts: `reports_detection/full/FINDINGS.md`, `843e5f5`

> A supervisor correcting your *skeleton* costs you an hour; correcting a written chapter costs a week.
>
> — `2026-07-18_dc3bc182.txt:559`

> define each number **once** as a LaTeX macro (`\StageCCatch`) generated from that ledger, and never type a number inline.
>
> — `2026-07-18_dc3bc182.txt:561`

### <a id="d-431"></a>D-431 — The chair's formal template overrides the proposed outline's cosmetics

`2026-07-22` · **proposed** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Confirm the chapter skeleton against the supervising chair's template before writing; related-work placement, abstract-language requirements and declaration wording follow the chair, and the outline's chapter content survives any of those variants.

**Why.** Passau FIM chairs differ on related-work placement, German-vs-English abstract requirements and declaration wording.

**Status.** proposed. S12 (2026-07-26): still pending — no evidence the chair's template has been consulted; no template document is in the repo.

**Source.** `a:dc3bc182-16`

> **Follow the chair's formal template, not this outline's cosmetics.**
>
> — `2026-07-18_dc3bc182.txt:500`

### <a id="d-432"></a>D-432 — Use the as-built sq.md architecture figure, not the aspirational pipeline diagram

`2026-07-22` · **proposed** · `[chat]` · corroboration: single-pass · confidence: high · actors: claude

**Decision.** The driver chapter's architecture figure is taken from `core/sq.md` (as-built flow), not from the aspirational `initial architecture.md` pipeline.

**Why.** sq.md documents the as-built flow; the target diagram describes stages (IntelliMerge, GumTree, SafeMerge) that were never built.

**Status.** proposed. S12 (2026-07-26): still pending — core/sq.md exists and the as-built-over-aspirational ruling is adopted, but no driver chapter draft exists, so no figure has been taken from anywhere yet.

**Source.** `a:dc3bc182-14` · Artifacts: `core/sq.md`, `initial architecture.md`

> Architecture figure from `core/sq.md` (as-built, not the aspirational diagram).
>
> — `2026-07-18_dc3bc182.txt:483`

### <a id="d-433"></a>D-433 — Cite S-D7's improved R2' as an instrument comparison, not fresh validation

`2026-07-23` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The S-D7 same-instrument result (R2' 36/164 = 22.0% [16.3, 28.9] vs 6.7%) is citable as a before/after instrument comparison only, not as a fresh recall validation; the held-out S-D5 evaluation remains the primary untainted measurement.

**Why.** "Stage-C positives overlap the taxonomy derivation split, so S-D7's R2 is *tuning-tainted* as a recall claim — it's citable as instrument-comparison, not as fresh validation. That's exactly why the held-out evaluation (S-D5) is the primary and this is the optional echo."

**Status.** adopted.

**Source.** `a:4c7b0828-38` · Artifacts: `reports_detectors/stagec_rerun/`, `reports_detectors/FINDINGS.md`

> Stage-C positives overlap the taxonomy derivation split, so S-D7's R2 is *tuning-tainted* as a recall claim — it's citable as instrument-comparison, not as fresh validation.
>
> — `2026-07-06_4c7b0828.txt:1945`

### <a id="d-434"></a>D-434 — Build the late-July delta deck as v7 in the existing series style

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Create `presentation/thesis_progress_late_jul2026.pptx` via `build_deck_v7.py` with a separate `speaker_notes_late_jul2026.md`, reusing v6's style and palette, with no embedded notes (WITH_NOTES=1 produces a PowerPoint variant instead); QA is validate plus a Keynote PNG export render check.

**Why.** Same series style and palette as v6 for continuity; notes kept out of the file per the Keynote rule.

**Status.** adopted.

**Source.** `a:16127d04-01` · Artifacts: `presentation/thesis_progress_late_jul2026.pptx`, `presentation/build_deck_v7.py`, `presentation/speaker_notes_late_jul2026.md`, `workspace/v7_png/`

> Same series style/palette as v6; 8 slides; verified opening in Keynote and visually QA'd via Keynote PNG export (renders in `workspace/v7_png/`); no embedded notes per the Keynote rule (`WITH_NOTES=1` for a PowerPoint variant).
>
> — `2026-07-24_16127d04.txt:21`

### <a id="d-435"></a>D-435 — State ceilings, unsummed controls and the latency price as first-class numbers on slides

`2026-07-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** The deck states the D2=0 / D3 0-causal-1-FP ceilings explicitly on-slide and reports the zero-FP record as 363 + 193 controls kept separate rather than summed; the runtime cost (79.5 → 87.8 s median per file, +8.3 s, +10.4%) is reported as a first-class number alongside the −11.5% damage improvement rather than a footnote; uncovered patterns on the map slide are labeled "no detector" with Detector 2 marked "honest 0" and the uncovered remainder stated as 12.3% with no piece bigger than 6.5%.

**Why.** The latency figure is "the honest cost of the extra detector passes", uniform across everything. No reason was recorded for the ceiling statements or the unsummed-controls presentation beyond the honesty framing itself.

**Status.** adopted.

**Source.** `a:16127d04-03`, `a:16127d04-20`, `b:16127d04-18` · Artifacts: `presentation/build_deck_v7.py`

> honest ceilings (D2 = 0, D3 0-causal/1-FP) stated on-slide
>
> — `2026-07-24_16127d04.txt:27`

> 79.5 → 87.8 seconds median per file, +10.4%, uniform across everything — the honest cost of the extra detector passes.
>
> — `2026-07-24_16127d04.txt:276`

### <a id="d-436"></a>D-436 — Close the deck with the default-enable switch as an explicit discussion question

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The deck closes with the pending default-enable decision framed as a discussion question with For/Price columns ("11.5% less damage, 10% slower, zero confirmed false alarms — would you switch it on?"), leaving the mapping adjudication as carried-over.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Source.** `a:16127d04-19`

> the pending default-enable decision framed as the discussion question (for/price columns), plus the carried-over mapping adjudication.
>
> — `2026-07-24_16127d04.txt:31`

### <a id="d-437"></a>D-437 — Add a method slide documenting the taxonomy pipeline, tooling and Ali's gate rulings

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: One source records the slide request as Ali's, the other records the A/B wording as joint. The slide exists because Ali asked for it and Claude drafted and verified the content.*

**Decision.** Insert a new slide (slide 4) after the taxonomy results covering the three-phase pipeline, the tooling (Batches API, models, tools/taxonomy_*.py harness, adjudication UIs), and Ali's four gate rulings, with a pre-registration/firewall bottom band; renumber downstream footers. The Phase-3 card states that runs A and B are set up identically (same instructions, locked list, inputs, blind to each other) with the only difference being run-to-run model randomness, framing A/B as a pure repeatability test whose 47 flips are exactly the adjudicated cases.

**Why.** Ali asked for an explanation of how the taxonomy was done, which tools were used and how he ruled it. The A/B wording was verified against the harness — taxonomy_phase3.py builds byte-identical requests for both passes, differing only in the submission id — and "a label that survives two independent rolls isn't luck".

**Status.** adopted.

**Source.** `a:16127d04-05`, `a:16127d04-10` · Artifacts: `presentation/build_deck_v7.py`, `merge-tool-comparison/tools/taxonomy_phase3.py`

> add slide to explain how taxonomy is done which tools where used and how it was ruled by me
>
> — `2026-07-24_16127d04.txt:49`

> That wording is verified against the actual harness ([taxonomy_phase3.py](merge-tool-comparison/tools/taxonomy_phase3.py) builds byte-identical requests for both passes, differing only in the submission id)
>
> — `2026-07-24_16127d04.txt:198`

### <a id="d-438"></a>D-438 — Plain-language register for slides; precision terms stay in FINDINGS

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** Rewrite slide 3, then slide 4, then all remaining slides in plain language — same layout and numbers, jargon translated — while keeping κ, Wilson CIs, category ids, amendment numbering and similar precision terms on the method slide and in FINDINGS only.

**Why.** Ali asked for less jargon and said the simpler style was more understandable; precision terms are kept where precision matters.

**Status.** adopted.

**Source.** `a:16127d04-07` · Artifacts: `presentation/build_deck_v7.py`

> it works. now apply same simple language and easy to understand visuals style from 'step 1  ... ' slide to all others
>
> — `2026-07-24_16127d04.txt:223`

> The technical terms (Wilson CIs, κ, category ids) still live on the method slide and in FINDINGS where precision matters.
>
> — `2026-07-24_16127d04.txt:121`

### <a id="d-439"></a>D-439 — Make denominators explicit: 71% is a share of the 119 visible-cause cases

`2026-07-24` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: joint

*Actors note: One source records the rewording as Claude's proposal, the other records the tree layout as Ali's request; the change arose from Ali's misreading and Claude's fix, ratified by Ali.*

**Decision.** Report the name-change family as "71% of the 119 visible-cause cases (85 cases — 31% of all 275)" so the denominator is unambiguous, and rebuild slide 3 around the exact 275/119/85/34/156 ASCII tree as the hero visual with real connector lines, moving the category table and trust card to the right column so each number's denominator reads off the indentation.

**Why.** Ali misread the 71% as a share of everything; if it tripped him up it will trip the audience up too. The tree makes the 71% visibly hang under the 119, which answers the question he had.

**Status.** adopted.

**Source.** `b:16127d04-09`, `a:16127d04-08` · Artifacts: `presentation/build_deck_v7.py`

> If it tripped you up, it'll trip the audience up too. I'd reword the stat line to make the denominator explicit
>
> — `2026-07-24_16127d04.txt:139`

> so every number's denominator is readable straight off the indentation — the 71% visibly hangs *under* the 119, which answers the question you had.
>
> — `2026-07-24_16127d04.txt:161`

### <a id="d-440"></a>D-440 — Hold all speaker-notes edits until Ali asks at the end

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** Speaker notes are frozen for the rest of the session while slides are edited; the full notes rewrite happens only when Ali requests it, accepting that notes drift out of sync (10 slides vs 9 note sections).

**Why.** Ali explicitly instructed "dont update speaker notes yet. wait for my request at the end to edit notes".

**Status.** adopted.

**Source.** `a:16127d04-09` · Artifacts: `presentation/speaker_notes_late_jul2026.md`

> on PHASE 3 · LABEL ALL, TWICE. describe how phase a and phase b was different. dont update speaker notes yet. wait for my request at the end to edit notes
>
> — `2026-07-24_16127d04.txt:188`

> Speaker notes untouched, as requested — I'll hold all note edits until you ask at the end.
>
> — `2026-07-24_16127d04.txt:200`

### <a id="d-441"></a>D-441 — Publish deck renders to a stable-URL private artifact viewer for phone review

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Publish all slide renders as a private single-column claude.ai artifact page at a fixed URL, re-rendered and republished to the same URL after every deck change, replacing per-edit file attachments.

**Why.** Ali was reviewing from his phone and the file attachments failed to open; the artifact route doesn't depend on mobile file transfer and keeps one refreshable URL.

**Status.** adopted. Supersedes: *sending fresh PNG renders as chat attachments*.

**Source.** `a:16127d04-11` · Artifacts: `https://claude.ai/code/artifact/f1d3125f-94aa-419e-8997-b9952e0fd4b7`

> The earlier file attachments failing was a mobile transfer issue; this route doesn't depend on that.
>
> — `2026-07-24_16127d04.txt:219`

> From now on, whenever I change the deck I'll re-render and republish to this **same URL**, so you can keep that tab open and just refresh after each edit.
>
> — `2026-07-24_16127d04.txt:221`

### <a id="d-442"></a>D-442 — Replace the pricing table with bars and show the cost arithmetic on the slide

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

*Actors note: The bar-chart swap is recorded as Claude's; the on-slide arithmetic was Ali's request. One presentational change made across two turns.*

**Decision.** Replace slide 8's config table with a bar chart (1994 → 1784 → 1579, green winner) under a one-line explanation of the damage score (silent wrong = 10, visible warning = 1, correct = 0), retaining the prediction-gate honesty line; then add the weighted sum inside each bar (e.g. "171 ×10 + 74 ×1 = 1784") and the −207 + 2 = −205 breakdown beneath the bars.

**Why.** Ali asked where the numbers come from and then asked for the calculation on the slide; showing the sums makes every bar a visible weighted sum and the improvement an explicit two-term subtraction, so the slide answers its own provenance question. No reason was recorded for the bars-over-table swap itself.

**Status.** adopted.

**Source.** `a:16127d04-12`, `a:16127d04-13` · Artifacts: `presentation/build_deck_v7.py`, `merge-tool-comparison/reports_detectors/whole_driver_flagon/summary.txt`

> the table became a **bar chart** (1994 → 1784 → 1579, green winner) under a one-line explanation of the damage score
>
> — `2026-07-24_16127d04.txt:248`

> So the slide now answers "where do these numbers come from" by itself: every bar is a visible weighted sum, and the improvement is an explicit two-term subtraction.
>
> — `2026-07-24_16127d04.txt:319`

### <a id="d-443"></a>D-443 — Insert a slide mapping the 2025 guessed categories onto the measured patterns

`2026-07-24` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

**Decision.** Insert a new slide 6 after the detector-build slide mapping the 2025 design's 7 guessed types (as fate chips) onto the 8 measured patterns (share bars) with a 'who watches each' detector column and a score band on coverage (30.9% of all cases, 12.3% uncovered); renumber slides 7–10 and update the two 'slide 6's pair' cross-references.

**Why.** The old→new mapping with detector coverage is a real result already in FINDINGS §4.

**Status.** adopted.

**Source.** `a:16127d04-16` · Artifacts: `presentation/build_deck_v7.py`, `reports_detectors/FINDINGS.md`

> add a slide about old categories vs new with detectors included
>
> — `2026-07-24_16127d04.txt:321`

> Good addition — the old→new mapping with detector coverage is a real result (FINDINGS §4).
>
> — `2026-07-24_16127d04.txt:323`

### <a id="d-444"></a>D-444 — Offer to name the three clean control pools explicitly on slide 7

`2026-07-24` · **proposed** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Proposed edit: replace slide 7's generic "three separate clean pools" with the explicit names of the three pools, including the spgroup mergedataset's 66 human-labeled-clean merges.

**Why.** Offered so the talk can say the zero-false-alarm record survived contact with a second, independently built benchmark.

**Status.** proposed. S12 (2026-07-26): still pending — presentation/build_deck_v7.py slide 7 does not name the three pools (no spgroup/66-clean text in the deck script), and the deck files are not yet committed; the offer remains unanswered.

**Source.** `a:16127d04-18` · Artifacts: `presentation/build_deck_v7.py`

> If you want, I can name the three clean pools explicitly on slide 7 (currently it just says "three separate clean pools") — one small edit.
>
> — `2026-07-24_16127d04.txt:354`

### <a id="d-445"></a>D-445 — Pose four RQs closable by frozen evidence, each with a one-sentence answer preview

`2026-07-25` · **proposed** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Pose exactly four main RQs with sub-questions — RQ1 Measurement/oracle (Ch. 3), RQ2 Routing (Ch. 6), RQ3 Anatomy/census (Ch. 7), RQ4 Detection (Ch. 8) — each mapped to one contribution and one chapter, plus an answers table that becomes the Ch. 12 skeleton and defence cheat-sheet. State each RQ in Ch. 1 together with a one-sentence preview of its answer. Ch. 1 also carries a thesis statement (not an RQ): silent semantic merge failures are dominated by mundane name-binding staleness rather than behavioral interference, a fail-closed static layer blocks a causally-confirmed share at zero measured false-block cost, and specialist per-case tool routing does not survive measurement. Four questions are deliberately excluded from the RQ set: "which merge tool is best" (Schesch's RQ2), "can semantic conflicts be detected" in unbounded form, "is composition the right paradigm", and anything about AI use.

**Why.** One RQ per evidence chapter and contribution, each disjoint from Schesch's RQ1–4 and already answered by frozen evidence — since the thesis is written backwards from results, only questions that can be closed should be posed. Each excluded question is either Schesch's, unanswerable/unfalsifiable as posed (use RQ4's to-what-extent/at-what-cost phrasing; RQ2 is composition's testable projection), or not a research question at all (AI use is methodology transparency in Ch. 9). Answer previews are given because empirical-SE theses aren't mysteries — examiners read the RQs, flip to the conclusion, and judge whether the middle delivers. No reason was recorded for the thesis statement's specific wording.

**Status.** proposed. S12 (2026-07-26): still pending — the RQ set awaits the spine document and supervisor review; neither exists in the repo. Supersedes: *The chapter-aligned RQ set sketched at line 494*.

**Source.** `a:dc3bc182-34`, `a:dc3bc182-35`, `a:dc3bc182-36`, `a:dc3bc182-37` · Artifacts: `reports/`, `reports_whole_driver/`, `reports_taxonomy/`, `reports_detection/`, `reports_detectors/`

> Four main RQs — one per evidence chapter, one per contribution, each disjoint from Schesch's RQ1–4, and each already answered by frozen evidence (you're writing backwards from results, so pose only questions you can close).
>
> — `2026-07-18_dc3bc182.txt:589`

> state each RQ **with a one-sentence preview of its answer** in the contributions list
>
> — `2026-07-18_dc3bc182.txt:633`


## Cross-cutting & meta

*59 primary source decisions → 24 entries; 2 not promoted (reasons in `docs/decision-record/entries/other.json`).*

### <a id="d-446"></a>D-446 — Timebox escape rule: a 2× overrun stops work until a STATUS.md revisit note is written

`2026-04-21 → 2026-05-16` · **adopted** · `[recon]` · corroboration: mixed · confidence: medium · actors: unclear

*Actors note: Sources disagree: one pass attributed the mergiraf-plan statement to Ali, the other two sources record no actor. The plan documents state the rule in a settled voice without naming who set it, so authorship is not on the record.*

**Decision.** Any phase that exceeds its effort estimate by 2× stops, and a revisit note is written to STATUS.md before work continues. Applied concretely to phase 3a (if its infrastructure exceeds 5 days, invoke the escape rule and consider falling back to 3e or 3b) and to Tier E, which is timeboxed to ~4-5 days wall time with a 2× escape budget of 8-10 days.

**Why.** Stated in both plan documents as preventing open-ended phase creep "when 'one more edge case' keeps moving the finish line"; the Tier E budget line records the same 2× multiplier applied to a specific phase estimate without restating the reason.

**Status.** adopted. S12 (2026-07-26): the rule was in force — it is the same 2× escape rule the integration plans adopted (gates-freeze D-240/D-248, both adopted), and the sibling pause-trigger discipline demonstrably fired and was honoured (ISSUES.md #2:84 'Plan §3 pause trigger fires'). No 2×-overrun revisit note exists in STATUS.md, i.e. the timebox branch itself never fired — a rule can be adopted and never triggered.

**Cross-theme.** *duplicates* → [D-240](#d-240), [D-248](#d-248) — The rule's plan statements consolidate as: origin statement (here, proposed), integration-plan adoption, comparator-tier adoption. Kept separate with cross-links rather than merged — merging would move uids across slice boundaries. Mirror: gates-freeze:0.

**Source.** `preA:pre-mergiraf-integration-07`, `preA:pre-rm2-integration-12`, `preB:pre-comparator-3e-tier-e-transforms-19` · Artifacts: `STATUS.md`, `docs/plans/comparator-3e-tier-e-transforms.md`

> **Timebox escape rule.** If any phase exceeds its estimate by 2×, stop and write a revisit note to [`STATUS.md`](../../STATUS.md) before continuing.
>
> — `2026-04-21_pre-mergiraf-integration.txt:28`

> Prevents open-ended phase creep when "one more edge case" keeps moving the finish line.
>
> — `2026-04-21_pre-mergiraf-integration.txt:28`

> ≈ **4-5 days** wall time. Timebox-escape budget: 2× = 8-10 days.
>
> — `2026-05-16_pre-comparator-3e-tier-e-transforms.txt:251`

### <a id="d-447"></a>D-447 — Validate the plan against the code in a Phase 0 memo before entering plan mode

`2026-05-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: ali

*Actors note: The sources disagree: the Phase 0 mandate is Ali's instruction (a:20b53f98-01), while the corollary decision to skip Explore/subagent re-derivation was Claude's own call within that mandate (a:20b53f98-27). Attributed to Ali because the constraint on future work is his.*

**Decision.** Before any code edits or EnterPlanMode, read the authoritative plan docs AND the code they make claims about, answer seven itemized questions from the source, and deliver a written findings memo covering plan-vs-code discrepancies, the recommended approach with deviations, the RM2-cost design decision, and risks/open questions. Because that deep read covered every critical file end-to-end, redundant Explore passes and agent-based re-derivation are then skipped and the plan is written directly.

**Why.** rm2-integration.md is "a hypothesis written 2026-04-24, not ground truth" — in the immediately prior cycle two sibling plan docs were found materially stale against the real code, so the plan must be assumed possibly wrong and validated against the source (CODE wins per CLAUDE.md). The corollary was argued on the strength of the read itself: the Phase 0 deep-read was "stronger than excerpt-level Explore" and had already traced every code path.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-340](#d-340) (see the reconciliation note there)

**Source.** `a:20b53f98-01`, `a:20b53f98-27` · Artifacts: `docs/plans/rm2-integration.md`, `docs/plans/execution-sequence.md`, `merge-tool-comparison/ISSUES.md`

> PHASE 0 — CRITICAL CODE REVIEW & PLAN VALIDATION (mandatory; do this BEFORE
>
> — `2026-05-18_20b53f98.txt:24`

> 2026-04-24, not ground truth — in the immediately prior cycle two sibling plan
>
> — `2026-05-18_20b53f98.txt:6`

> My Phase 0 deep-read already covered every critical file end-to-end (stronger than excerpt-level Explore), so I'll skip redundant exploration.
>
> — `2026-05-18_20b53f98.txt:152`

### <a id="d-448"></a>D-448 — Make MergeScenario.from_dict filter to known fields, accepting a silent-failure cost

`2026-05-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Add a single `refactorings` dict field to MergeScenario, update to_dict, and change from_dict to filter incoming JSON keys to known dataclass fields instead of constructing via cls(**data); round-trip tests stay green. The known downside — a misspelled JSON key such as "catgory" is now silently ignored and the field defaults, where it previously raised TypeError — is accepted and logged rather than mitigated.

**Why.** cls(**data) raises TypeError on any JSON key without a matching dataclass field, so the plan's "backwards-compatible" claim is false unless from_dict is made schema-tolerant; filtering kills that brittleness permanently. The cost was recorded in the same session as a trade rather than pure upside: "from_dict filtering trades a loud failure for a silent one... Forwards-compat win, but I sold it as pure upside."

**Status.** adopted.

**Source.** `a:20b53f98-13`, `b:20b53f98-08` · Artifacts: `merge-tool-comparison/src/core/interfaces.py`, `merge-tool-comparison/tests/test_interfaces.py`, `cbac926`

> make `from_dict` **filter to known fields** (kills the `cls(**data)` brittleness permanently)
>
> — `2026-05-18_20b53f98.txt:128`

> **`from_dict` filtering trades a loud failure for a silent one.** A misspelled JSON key (`"catgory"`) previously raised `TypeError`; now it's silently ignored and `category` defaults. Forwards-compat win, but I sold it as pure upside.
>
> — `2026-05-18_20b53f98.txt:257`

### <a id="d-449"></a>D-449 — Surface doc/data inconsistencies and honesty nuances instead of reconciling them silently

`2026-05-18 → 2026-05-27` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** On finding a doc-vs-data inconsistency, report it and ask whether to fix the docstring or record the discrepancy in ISSUES #27 rather than silently reconciling it. Correspondingly, self-audit findings judged not worth acting on — the from_dict loud→silent trade-off and the repeated tiny-n F1 contrasts — remain logged observations in the conversation rather than triggering code changes or a rewrite of committed history.

**Why.** Reported as following Ali's standing preference against silent reconciliation. For the two nuances, the argument was that every citation already carries an adjacent sub-Wilson-CI hedge so it is defensible, and the remainder is doc/commit-message wording "not worth rewriting committed history, but I'd correct the overstatement if I touch those docs again" — so the items are neither acted on nor hidden.

**Status.** adopted.

**Source.** `a:20b53f98-24`, `a:3302d287-04` · Artifacts: `merge-tool-comparison/ISSUES.md #27`

> Per your standing preference I haven't reconciled it silently.
>
> — `2026-05-27_3302d287.txt:47`

> The two honesty nuances I judged not worth acting on
>
> — `2026-05-18_20b53f98.txt:295`

> not worth rewriting committed history, but I'd correct the overstatement if I touch those docs again
>
> — `2026-05-18_20b53f98.txt:266`

### <a id="d-450"></a>D-450 — Cover the CLI classification wiring with a Docker-free unit test

`2026-05-18` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: joint

**Decision.** Add tests/test_cli.py covering the scenario.refactorings → cluster_of → categories wiring (Extract Method → MIGRATE_DECL; untagged → NONE not unknown; union+precedence → SYMBOL_CASCADE), built from in-memory MergeScenarios and a fake results dict so no Docker is required.

**Why.** The integration changed in R2 had zero test coverage — only cluster_of was tested in isolation, and ISSUES #14 notes no CLI tests exist — so the wiring had been validated only by a manual results.csv regeneration.

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-352](#d-352) — No general 'unit tests must not require Docker' entry exists; the nearest testing-convention owner is linked (mirror: repo-conventions:4).

**Source.** `a:20b53f98-22` · Artifacts: `merge-tool-comparison/tests/test_cli.py`, `eabaddd`

> the integration I changed has zero test coverage.
>
> — `2026-05-18_20b53f98.txt:247`

> New `tests/test_cli.py` covers the `_classify_results` wiring I changed
>
> — `2026-05-18_20b53f98.txt:290`

### <a id="d-451"></a>D-451 — Hand work to fresh sessions with self-contained prompts and artifact-only handoff

`2026-05-26 → 2026-07-25` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

*Actors note: Sources disagree: the Spork-niche handoff was Ali's instruction, the D2 closure and the v2 session split were recommendations Ali accepted, and the artifact-only handoff rule was Claude restating Ali's #30 rule. Recorded as joint because in each case options were put and Ali chose.*

**Decision.** When a session is loaded or a stage is closed, the next piece of work moves to a fresh session carrying a written, self-contained kickoff prompt that points at the current committed docs (ISSUES, STATUS, CLAUDE.md, report dirs, plan §8), lists what is already established as DO-NOT-REDO, names the gaps to attack, and hands over tooling and env knobs. Stage boundaries are declared explicitly (D2's build stage closed at the GD2 PASS stop point, commits 6523ab0 and 83d3a23, with S-D5/S-D6 recorded as scheduled rather than outstanding), and the same seam is used for the decision-record v2 build (S0 instrument, S1..S7 extract, S8 consolidate, S9 audit). No context is carried between sessions: each session commits its artifacts and the next reads from disk.

**Why.** Argued from context limits and grounding: the originating session was "quite loaded", and the prompt points at current docs "so the new session grounds itself rather than trusting a cold summary" instead of leaning on a handoff summary. For v2 the same argument was made quantitatively — one session physically cannot hold the corpus, and in v1 the degradation from reading to grepping happened at the ~60% mark because the remaining budget did not fit the remaining files, so "the grep shortcut was a symptom of running one session, not a separate mistake". Handoff discipline is Ali's own #30 rule: "handoff between sessions is committed artifacts only." Stage closure was justified by every exit criterion in the plan being met and recorded.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-339](#d-339) (see the reconciliation note there)

**Source.** `a:e1df1610-33`, `a:acf7e1d0-19`, `a:c4c4d030-17`, `b:c4c4d030-15` · Artifacts: `merge-tool-comparison/ISSUES.md #27`, `ISSUES #31`, `#30`, `6523ab0`, `83d3a23`, `merge-tool-comparison/tools/select_materialize.py`

> It points at the now-current docs (so the new session grounds itself rather than trusting a cold summary), states what's already ruled out
>
> — `2026-05-20_e1df1610.txt:1438`

> The only D2 items still open are *scheduled* ones, not leftovers
>
> — `2026-07-16_acf7e1d0.txt:501`

> **The grep shortcut was a symptom of running one session, not a separate mistake.**
>
> — `2026-07-25_c4c4d030.txt:176`

> Use your own #30 rule — *"handoff between sessions is committed artifacts only."* Each extraction session commits its JSON; S8 reads from disk.
>
> — `2026-07-25_c4c4d030.txt:195`

### <a id="d-452"></a>D-452 — Keep the empirical clusters as the primary codebook scheme over the four-family view

`2026-07-10` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

*Actors note: Sources disagree (claude, joint, unclear). Recorded as joint because each recommendation was put to Ali with a rationale and Ali ruled — the review table records ACCEPT / "keep (3/4 stay split ✓)" rulings.*

**Decision.** The state / control-flow / data-flow / name-binding four-family view is rejected as the primary organizing scheme and demoted to a secondary axis; the empirical clusters stay primary. Within them, `stale-reference-to-renamed-or-relocated-declaration` (cat 3) and `stale-caller-of-changed-signature` (cat 4) stay separate, decided by the test "does the old name still resolve in the merged code?", with the both-renamed-and-re-signatured case resolved by primary = whichever failure the use trips on first (if the name does not resolve it is cat 3 and the signature mismatch is never evaluated) plus an optional secondary label; and `overlapping-edit-interleaving` (cat 6) is retained unsplit despite spanning compile-time and runtime anchors, with the jdupl moved-declaration-dropped anchor staying there rather than in cat 7.

**Why.** Resolution is the argument throughout: the four-family scheme "would lump 75% into one family" (the 45/60 name-binding units); cats 3 and 4 differ on all three axes that matter for coding — trigger, compiler error and fix — and merging them "makes a single 21-unit bucket (~35% of attributed) that erases a real, decidable line"; the boundary rule keeps the pair decidable in the rare overlap case because the coding arity allows a secondary label; and cat 6 "is coherent as a **mechanism**... which is what the codebook is supposed to cluster on".

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-227](#d-227) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-271](#d-271), [D-029](#d-029) — The codebook definition and freeze owners. The category list is stated once via cross-links; all entries kept.

**Source.** `a:6296f4f6-08`, `a:6296f4f6-13`, `b:6296f4f6-17`, `a:6296f4f6-14` · Artifacts: `reports_taxonomy/phase2/codebook_draft.md`, `reports_taxonomy/phase2/codebook_frozen.md`

> **Four-family view rejected** as a primary scheme (would lump 75% into one family) — kept the empirical clusters.
>
> — `2026-07-10_6296f4f6.txt:161`

> **My recommendation: keep them separate.** They're 7 + 14 = 21 units; merging them makes a single 21-unit bucket (~35% of attributed) that erases a real, decidable line
>
> — `2026-07-10_6296f4f6.txt:304`

> The codebook handles it with the boundary rule (primary = whichever the *use* trips on first — if the name doesn't resolve, it's cat 3; the signature mismatch never even gets evaluated) plus the option of a secondary label.
>
> — `2026-07-10_6296f4f6.txt:306`

> It's coherent as a **mechanism** (the unifying thread is "structured merge interleaves two divergent same-region rewrites"), which is what the codebook is supposed to cluster on.
>
> — `2026-07-10_6296f4f6.txt:329`

### <a id="d-453"></a>D-453 — Rename the two `vs` category ids and record the old→new crosswalk gaps explicitly

`2026-07-10` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: joint

**Decision.** Rename `import-pruning-vs-concurrent-usage` → `stale-usage-of-pruned-import` and `changed-behavior-vs-stale-expectation` → `stale-expectation-of-changed-behavior` so all 8 categories read in one relational style (id + name only, no semantic change). In the old→new mapping, Atomic Updates and Loop Semantics are recorded as having no empirical counterpart; DFI/Stale Read, Control-Flow Interference and Scope Capture get no standalone category (Exception Handling folds into stale-caller-of-changed-signature); Method Rename splits three ways.

**Why.** On naming: "the naming isn't consistent across the 8" — only two ids used an explicit `vs` while the others expressed the same A-meets-B structure relationally, so the change is cosmetic. On the crosswalk: the empty cells are "Consistent with Stage-C's #3/#5 = 0" — those historical categories carried zero mass in the 60 attributed merges.

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-109](#d-109) (see the reconciliation note there)

**Cross-theme.** *depends-on* → [D-219](#d-219) — other_uid a:6296f4f6-12 landed there: the apply-renames-inside-the-freeze-commit ruling governs when these renames took effect.

**Source.** `a:6296f4f6-11`, `b:6296f4f6-09` · Artifacts: `reports_taxonomy/phase2/codebook_draft.md`, `reports_taxonomy/phase2/codebook_frozen.md`

> the naming isn't consistent across the 8.
>
> — `2026-07-10_6296f4f6.txt:267`

> lets rename 'vs's
>
> — `2026-07-10_6296f4f6.txt:273`

> - Old→new: **Atomic Updates & Loop Semantics = no empirical counterpart**; DFI/CFI/Scope-Capture = no standalone category; Method Rename splits three ways.
>
> — `2026-07-10_6296f4f6.txt:160`

### <a id="d-454"></a>D-454 — Withdraw the phantom-unit_id suspicion after a mechanical manifest check

`2026-07-10` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The earlier suspicion that cited unit_ids/SHAs in the draft were hallucinated is withdrawn: the only apparent phantom was the table header row `unit_id`, and all 25 anchor ids plus all 60 coverage ids are genuine derivation units.

**Why.** The suspicion arose from reading only a truncated slice of the manifest; the mechanical check showed the model had transcribed real unit_ids correctly.

**Status.** adopted. Supersedes: *the earlier claim that several cited unit_ids/SHAs may not match the real derivation units*.

**Source.** `a:6296f4f6-07` · Artifacts: `reports_taxonomy/phase2/codebook_draft.md`

> False alarm — the only "phantom" was the table header row `unit_id`.
>
> — `2026-07-10_6296f4f6.txt:116`

> my earlier suspicion came from reading only a truncated slice of the manifest
>
> — `2026-07-10_6296f4f6.txt:116`

### <a id="d-455"></a>D-455 — Open every session prompt with a mandatory ambiguity check that must stop and ask

`2026-07-15 → 2026-07-22` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

*Actors note: Sources disagree: the gate itself is Ali's instruction (a:4c7b0828-34); the S-D5 judgment that no material ambiguity existed, and therefore not to wait, was Claude's (a:06ec13eb-01). Attributed to Ali because the standing constraint is his.*

**Decision.** All six detector-cycle session prompts (S-D1..S-D6) open, after the STATE block, with an ambiguity check: if anything is ambiguous, contradictory or underspecified across plan, repo and prompt, ask Ali concrete questions and WAIT — never improvise. Material resolutions become dated §12 amendments; trivial clarifications go to the session log and close-out. The gate was exercised in S-D5: after reviewing plan §8/§3, ISSUES #31, the frozen instrument, the harness and populations, no material ambiguities were declared and work proceeded without waiting, with four trivial clarifications logged for close-out.

**Why.** "a fresh session that hits ambiguity has only two options, improvise or ask, and the plan should force 'ask.'" The material/trivial split keeps both paths ending in committed artifacts, "keeping the cross-session alignment loop closed". In the S-D5 application the reviewed authority docs, instrument, harness and artifacts were judged to leave no material ambiguity, so the remaining items were recordable in the session log.

**Status.** adopted.

**Source.** `a:4c7b0828-34`, `a:06ec13eb-01` · Artifacts: `outputs/detector-cycle-plan.md §8`, `ISSUES.md #31`

> add for every session prompt to ask questions to validate if anything is causes ambiguity
>
> — `2026-07-06_4c7b0828.txt:1813`

> > **FIRST — AMBIGUITY CHECK:** after reading the authority doc and ISSUES #31, if anything is ambiguous, contradictory, or underspecified
>
> — `2026-07-06_4c7b0828.txt:1819`

> **No material ambiguities — proceeding without waiting.** Trivial clarifications for the session log (close-out will record them):
>
> — `2026-07-22_06ec13eb.txt:32`

### <a id="d-456"></a>D-456 — Serialize the detector cycle at a WIP limit of one while writing has priority

`2026-07-15` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** While the write-up is in the foreground, the detector cycle runs serially — one implementation stage in flight, evaluation batched into a single cycle at the end — with two fixed ~30-60 minute touchpoints per week; parallel builds are explicitly declined.

**Why.** "Parallel builds save calendar time but double your touchpoints; while writing has priority, serialize." The cost is accepted explicitly: "the detector cycle takes ~2–3 calendar weeks instead of one — and costs you roughly two hours of attention per week. That's the trade you want."

**Status.** adopted. S12 (2026-07-26): the cycle ran serially as proposed — S-D0 through S-D8 executed as strictly sequential sessions with one implementation stage in flight (ISSUES.md #31 session records; the S-D7/S-D8 follow-ons likewise serialized), while the write-up planning proceeded in parallel sessions. The two-fixed-touchpoints cadence is not verifiable from the repo.

**Cross-theme.** *depends-on* → [D-027](#d-027) — other_uid a:fb0fa5c5-30 landed there: the same serialization argument one cycle earlier.

**Source.** `a:4c7b0828-41` · Artifacts: `outputs/detector-cycle-plan.md`

> **WIP limit = one implementation stage in flight.**
>
> — `2026-07-06_4c7b0828.txt:1637`

> Parallel builds save calendar time but double your touchpoints; while writing has priority, serialize.
>
> — `2026-07-06_4c7b0828.txt:1637`

### <a id="d-457"></a>D-457 — Brief finder agents on one angle, capped at six findings each with a failure scenario

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: unclear

*Actors note: Sources disagree (some passes recorded ali, others claude). The briefs appear as user-role messages inside subagent transcripts, so the record does not settle whether a brief was authored by Ali or by the orchestrating Claude session; left unclear rather than assigned by majority.*

**Decision.** Each code-review finder subagent is briefed on exactly one angle (cross-file tracer, removed-behavior auditor, simplification, altitude) with the specific paths and questions it must answer, and must return at most 6 candidate findings as a JSON array with keys file, line, summary and failure_scenario (concrete inputs/state → wrong output, or concrete cost); candidates without a nameable failure scenario are not reported, fewer than 6 is explicitly acceptable, and the final message contains only the JSON array. For the removed-behavior angle the method is fixed: for every line the diff deletes or replaces, name the invariant that line enforced and verify the new code re-establishes it, answering pre-set invariant questions (fixture byte-identity, LANES/_SMOKES key-set match, smoke-gate ordering before scoring, behavior change for the pre-existing lane invocation).

**Why.** Only the removed-behavior brief recorded a reason: the D1 smoke fixture's exact content mattered because it was the anti-vacuous-run gate for lane ImportPruneUsage, so the audit is framed around whether each removed line's invariant survives rather than around whether the new code looks correct. The one-angle scoping, the six-candidate cap and the JSON-only output format are stated as instructions without a recorded rationale.

**Status.** adopted.

**Cross-theme.** *duplicates* → [D-367](#d-367), [D-279](#d-279) — The review protocol has one owner (Amendment 3); the brief-side (here) and output-side (repo-conventions) contracts are its two halves. Kept, cross-linked.

**Source.** `a:82dd479f-sub-agent-a9ce95-03`, `a:82dd479f-sub-sub-agent-aca92e-02`, `a:acf7e1d0-sub-agent-a88268-01`, `a:acf7e1d0-sub-sub-agent-ac303e-02`, `a:acf7e1d0-sub-sub-agent-af9ecb-01` · Artifacts: `scratchpad/sd4_diff.txt`, `semantic_merge_driver/core/plugin_loader.py`, `merge-tool-comparison/tools/detector_tune_run.py`, `semantic_merge_driver/config/strategies.yaml`

> Return up to 6 candidate findings, each as: file, line, one-line summary, concrete failure_scenario (inputs/state → wrong output). Only candidates with a nameable failure scenario. If fewer than 6 exist, return fewer.
>
> — `2026-07-16_acf7e1d0_sub-agent-ac303e.txt:13`

> For every deleted/replaced line, name the invariant it enforced and check the new code re-establishes it
>
> — `2026-07-16_acf7e1d0_sub-agent-af9ecb.txt:5`

> Only flag items where a concretely better altitude exists within the stated constraints; name it. Return up to 6 candidates: file, line, summary, failure_scenario = concrete fragility cost. Fewer is fine.
>
> — `2026-07-16_acf7e1d0_sub-agent-a88268.txt:7`

> You are a code-review finder agent (angle: cross-file tracer).
>
> — `2026-07-16_82dd479f_sub-agent-a9ce95.txt:3`

### <a id="d-458"></a>D-458 — Bar style-level and micro-optimization findings from review, and never pad to the cap

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

*Actors note: One source (the efficiency brief, a:acf7e1d0-sub-agent-af6a03-01) was recorded as ali because the brief appears as a user-role message in the subagent transcript; the three review judgments it governs are Claude's. Attributed to Claude with that caveat noted.*

**Decision.** Review angles are scoped to exclude style: the simplification angle may flag only items that plausibly reduce defect risk or represent notable waste, because verbose comment-heavy detector code is accepted project idiom; the efficiency angle must judge against realistic inputs (Java files up to a few thousand lines, 0-3 candidate names per file), must not flag micro-optimizations with no measurable effect at that scale, and must name the cheaper alternative for anything flagged. Applied: the efficiency review returned a single candidate with the rest listed under an explicit "considered and deliberately not flagged" section, and the changed hunks in tools/detector_tune_run.py were held out of scope entirely.

**Why.** "this codebase accepts verbose, comment-heavy detector code as its idiom", so style-level verbosity is not a defect. On the efficiency side the two RM2 Docker runs dominate runtime by ~1000× and the text helpers are already cached, so remaining items fall below the measurability bar and padding the list was declined; detector_tune_run.py is "a one-shot dev/eval tool (each `_smoke_positive` runs Docker once by design); nothing in the diff is a hot path".

**Status.** adopted.

**Cross-theme.** *depended on by* ← [D-369](#d-369) (see the reconciliation note there)

**Source.** `a:82dd479f-sub-sub-agent-aca92e-01`, `a:acf7e1d0-sub-agent-af6a03-01`, `a:acf7e1d0-sub-agent-af6a03-03`, `a:acf7e1d0-sub-agent-af6a03-06` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`, `merge-tool-comparison/tools/detector_tune_run.py`

> Only flag simplifications that plausibly reduce defect risk or notable waste — this codebase accepts verbose, comment-heavy detector code as its idiom.
>
> — `2026-07-16_82dd479f_sub-agent-aca92e.txt:8`

> Judge against realistic inputs: Java files up to a few thousand lines, usually 0–3 candidate names per file. Do NOT flag micro-optimizations with no measurable effect at that scale; name the cheaper alternative for anything you flag.
>
> — `2026-07-16_acf7e1d0_sub-agent-af6a03.txt:5`

> Most remaining items are below the measurability bar at 0–3 candidate names / few-thousand-line files, and I'm declining to pad the list with those.
>
> — `2026-07-16_acf7e1d0_sub-agent-af6a03.txt:15`

> This is a one-shot dev/eval tool (each `_smoke_positive` runs Docker once by design); nothing in the diff is a hot path and I found no efficiency issue worth flagging.
>
> — `2026-07-16_acf7e1d0_sub-agent-af6a03.txt:35`

### <a id="d-459"></a>D-459 — Rank detector review findings false-flag first, then crash, then silent FN

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Candidate findings for the SignatureStaleCall lane are triaged and reported in a fixed severity order: a bug that can produce a FALSE FLAG on legal Java is most severe, a crash/exception in analyze() second, silent false negatives contrary to the documented design third. Findings were returned ordered false-flag first.

**Why.** The detector is FP-averse by design — any uncertainty must suppress the flag (the FN direction) — so bugs that push toward flagging legal Java violate the design contract, whereas FNs are the sanctioned failure direction.

**Status.** adopted.

**Source.** `a:acf7e1d0-sub-sub-agent-ac303e-01` · Artifacts: `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`

> It is FP-averse by design: any uncertainty must suppress the flag (FN direction). A bug that can produce a FALSE FLAG on legal Java is the most severe class; a crash/exception in analyze() is second; silent FNs contrary to the documented design are third.
>
> — `2026-07-16_acf7e1d0_sub-agent-ac303e.txt:9`

> Here are the candidate findings from the line-by-line scan, ordered by severity (false-flag first).
>
> — `2026-07-16_acf7e1d0_sub-agent-ac303e.txt:21`

### <a id="d-460"></a>D-460 — Verify borrowed-helper contracts by running probes, not by reading the code

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Contract verification for borrowed helpers goes beyond the static trace the brief asked for: run the new tests and construct concrete base/ours/theirs probes (label collision, `case FOO, MODE:`, `static class Ev` removal with a retained `Ev cached;`), and mark each reported finding "Empirically confirmed" rather than inferred from reading.

**Why.** Stated as the need to "verify behavior empirically" and to probe contract edge cases rather than rely on the static cross-file trace alone.

**Status.** adopted.

**Source.** `a:82dd479f-sub-agent-a9ce95-04` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`

> Now let me verify behavior empirically — run the new tests and probe a few contract edge cases.
>
> — `2026-07-16_82dd479f_sub-agent-a9ce95.txt:11`

> Empirically confirmed: base declares field 'retry', ours removes it, theirs adds
>
> — `2026-07-16_82dd479f_sub-agent-a9ce95.txt:20`

### <a id="d-461"></a>D-461 — Give cross-lane grammar and predicates a single source of truth

`2026-07-16` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

**Decision.** Four recommendations, one rule: stop copying grammar and classifiers between detector lanes. (1) Delete the private `_method_call_sites` re-implementation in unresolved_reference.py and call `_ssc._call_sites(view, name, False, view.stripped)` instead, since arity is ignored and `_call_sites` keeps arity-None sites. (2) Hoist one module-level type-declaration pattern into import_prune_usage and have `declares_type` and `_declared_type_names` both use it instead of a third/fourth copy. (3) Put the lambda-declared-name alternation in one place — a shared pattern fragment or a small enumerator both lanes call — rather than duplicating rename_conflict._DECL_GUARD as _ARROW_DECL_RE. (4) Extract an `_is_method_decl(s, name_off, after_paren)` predicate in _ssc and have both `_declared_method_names` (D3) and `_declared_arities` use it.

**Why.** Every case is argued as drift surface with a named FP consequence: if D2's `_call_sites` gains a site-classification fix during GD3 tuning, D3's private copy keeps the old semantics and the two lanes classify the same call site differently, producing a control FP; a regex fix landing in `_ipu.declares_type` but not in the copy makes the lane "emit a false 'removed type' flag on a file where the type demonstrably still exists — a zero-FP-gate breach from pure regex drift"; the lambda alternation "exists precisely because it was a measured Stage-C FP fix", so drift reintroduces the var-kind FP class the round-2 fix retired; and divergent method-decl classifiers produce a phantom keeper/remover split that passes the absorption/attribution guards and emits a method-kind FP.

**Status.** adopted. S12 (2026-07-26): ruled and largely landed — unresolved_reference.py imports signature_stale_call as _ssc (:13) and _method_call_sites is now a thin wrapper over _ssc._call_sites (:591-602); the shared tail was factored (finish(), :719); shared grammar (_TYPE_HEADER_RE, _is_decl_tail, _absorbable_spans) is used across lanes. One rec was explicitly declined with a recorded reason: ISSUES.md #31 'regex-copy hoisting — tripwire over touching more gated lanes'. Nothing pending.

**Cross-theme.** *depends-on* → [D-125](#d-125), [D-123](#d-123) — Mirror of detection:10. Whether the refactors landed is not in the record (both proposed); the composition-reuse decision that constrains them is linked.

**Source.** `a:82dd479f-sub-sub-agent-aca92e-03`, `a:82dd479f-sub-sub-agent-aca92e-04`, `a:82dd479f-sub-sub-agent-aca92e-05`, `b:82dd479f-sub-sub-agent-aca92e-08` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py`, `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`, `semantic_merge_driver/strategies/rm2_strategies/rename_conflict.py`

> REUSE: _method_call_sites is a near-verbatim re-implementation of _ssc._call_sites(view, name, is_ctor=False, arity_text) minus the arity computation
>
> — `2026-07-16_82dd479f_sub-agent-aca92e.txt:20`

> the lane emits a false 'removed type' flag on a file where the type demonstrably still exists — a zero-FP-gate breach from pure regex drift.
>
> — `2026-07-16_82dd479f_sub-agent-aca92e.txt:27`

> The grammar itself (`what counts as a lambda-declared name`) should live once, e.g. a shared pattern fragment or a tiny enumerator both lanes call, since that alternation exists precisely because it was a measured Stage-C FP fix.
>
> — `2026-07-16_82dd479f_sub-agent-aca92e.txt:32`

> Extracting a `_is_method_decl(s, name_off, after_paren)` predicate in _ssc and having both call it would keep the two lanes' notion of 'this name(-site is a method declaration' provably identical
>
> — `2026-07-16_82dd479f_sub-agent-aca92e.txt:50`

### <a id="d-462"></a>D-462 — Derive or assert parallel state instead of hand-maintaining it, and drop dead guards

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: medium · actors: claude

**Decision.** Four recommendations making invariants structural rather than copy-maintained: replace the three triplicated per-kind loops in `_widened_issues` with a driver taking (kind, names_by_version, usage_fn, suppressions) so the absorption/attribution/emit tail is written once; in detector_tune_run.py either derive `FULL_SUITE = tuple(LANES)` or assert `set(FULL_SUITE) == set(LANES)` next to it; collapse the parallel `changes`/`sigs` dicts in signature_stale_call.py analyze() into one `sig_lists: Dict[str, Dict[str, List[_SigChange]]]`, deriving the pair-set and representative _SigChange at read time; and reduce `if change.varargs or change.old_arity == change.new_arity: continue` to `if change.varargs: continue`, since `_extract_arity_changes` already skips equal-arity records.

**Why.** Each is argued from a concrete failure of hand-maintained duplication: a semantics fix to the shared loop tail "needs three synchronized edits; missing one... leaves one kind with divergent guard semantics"; a lane registered in LANES but forgotten in FULL_SUITE means `--lane FULL` "silently omits the new lane, the run PASSes, and a vacuous 0-flag result for an untested lane gets recorded in the manifest as gate evidence"; "the two dicts must be kept in lockstep by hand", so a future abstention edit touching one and not the other silently desyncs presence/ambiguity checks; and "the dead check misrepresents the invariant that `_extract_arity_changes` actually enforces", inviting a maintainer to loosen the real guard believing the dead disjunct is the backstop.

**Status.** adopted. S12 (2026-07-26): landed — 'assert set(FULL_SUITE) == set(LANES)' is verbatim at detector_tune_run.py:81, the FP-critical absorption/attribution/emit tail is written once as finish() (unresolved_reference.py:719, 'structural for every kind'), and ISSUES.md #31 records the sig_lists collapse and dead-guard removal for D2.

**Cross-theme.** *depends-on* → [D-126](#d-126), [D-275](#d-275) — The FULL_SUITE/LANES registry duplication is owned by the tune-harness entry; the GD-gate evidence chain it touches by the GD3 gate.

**Cross-theme.** *depended on by* ← [D-367](#d-367) (see the reconciliation note there)

**Source.** `a:82dd479f-sub-sub-agent-aca92e-06`, `a:82dd479f-sub-sub-agent-aca92e-07`, `a:acf7e1d0-sub-agent-afc4ad-02`, `a:acf7e1d0-sub-agent-afc4ad-03` · Artifacts: `semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py:547`, `merge-tool-comparison/tools/detector_tune_run.py:72`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py:210-223`, `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py:244`

> A driver taking (kind, names_by_version, usage_fn, suppressions) would make the invariant 'absorption and attribution are checked identically for every kind' structural instead of copy-maintained.
>
> — `2026-07-16_82dd479f_sub-agent-aca92e.txt:38`

> silently omits the new lane, the run PASSes, and a vacuous 0-flag result for an untested lane gets recorded in the manifest as gate evidence.
>
> — `2026-07-16_82dd479f_sub-agent-aca92e.txt:45`

> the two dicts must be kept in lockstep by hand
>
> — `2026-07-16_acf7e1d0_sub-agent-afc4ad.txt:28`

> The dead check misrepresents the invariant that `_extract_arity_changes` actually enforces.
>
> — `2026-07-16_acf7e1d0_sub-agent-afc4ad.txt:41`

### <a id="d-463"></a>D-463 — Two duplications deliberately kept: coupled helper signature and the tune-tool fixture

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** Documented exceptions to the deduplication line: no refactor is proposed for the redundant `_prev_token(s, name_off)` scan performed both directly and inside `_type_ish_before`, and the hand-rewritten P1 base/ours/theirs/merged Notifier fixture in detector_tune_run.py `_smoke_signature_stale_call` is accepted as intentional duplication of the test file's P1 shape, reported only as a low-confidence watch-item.

**Why.** For `_prev_token`, sharing the pre-computed (kind, tok, idx) would require changing `_type_ish_before`'s signature and coupling two helpers — "Lower priority precisely because sharing it couples two helpers" — a worse trade than one redundant token scan. For the fixture, "This is intentional (the tune tool can't import pytest fixtures), so I'm flagging it as a watch-item, not a defect", with the known cost that if the canonical P1 shape is later adjusted "the smoke copy drifts silently".

**Status.** adopted. S12 (2026-07-26): both acceptances were ruled and recorded — ISSUES.md #31's non-fix list carries '_prev_token double-compute (coupling cost > benefit)' and 'P1 fixture test↔smoke duplication intentional (tune tool cannot import test fixtures)' verbatim.

**Source.** `a:acf7e1d0-sub-agent-afc4ad-04`, `a:acf7e1d0-sub-agent-afc4ad-05` · Artifacts: `semantic_merge_driver/strategies/rm2_strategies/signature_stale_call.py:523-524`, `merge-tool-comparison/tools/detector_tune_run.py:150-207`, `semantic_merge_driver/tests/test_signature_stale_call.py:123-187`

> **Simpler form:** none that's clean without changing `_type_ish_before`'s signature to accept the pre-computed `(kind, tok, idx)`. Lower priority precisely because sharing it couples two helpers.
>
> — `2026-07-16_acf7e1d0_sub-agent-afc4ad.txt:52`

> This is intentional (the tune tool can't import pytest fixtures), so I'm flagging it as a watch-item, not a defect.
>
> — `2026-07-16_acf7e1d0_sub-agent-afc4ad.txt:59`

> if the P1 canonical shape is later adjusted (e.g. to probe a new RM2 rendering), the smoke copy drifts silently
>
> — `2026-07-16_acf7e1d0_sub-agent-afc4ad.txt:61`

### <a id="d-464"></a>D-464 — Review the file standalone against open-source prior art, making no changes

`2026-07-16` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** A second review pass judges import_prune_usage.py as self-contained standalone code with project context deliberately ignored, researching comparable open-source implementations, and making no edits. The companion prior-art consultation is likewise scoped as web+docs research only, covering exactly four tools (Error Prone, SpotBugs, IntelliJ IDEA, Checkstyle) with a specific doc page, source file or issue URL cited for each.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted.

**Cross-theme.** *depends-on* → [D-414](#d-414), [D-030](#d-030) — other_uid a:82dd479f-sub-sub-agent-aadfd1-01 is cited by the former; the consult-not-port boundary is the latter.

**Source.** `a:734e4529-05`, `a:82dd479f-sub-sub-agent-aadfd1-01` · Artifacts: `semantic_merge_driver/strategies/text_strategies/import_prune_usage.py`

> review it independently from project as a sand alone code. Research other similar open source implementation. dont make any changes, review only
>
> — `2026-07-16_734e4529.txt:26`

> Standalone review below — project context deliberately ignored
>
> — `2026-07-16_734e4529.txt:30`

### <a id="d-465"></a>D-465 — Reconstruct the project's identity from four parallel read-only explorations

`2026-07-18` · **adopted** · `[chat]` · corroboration: mixed · confidence: medium · actors: claude

*Actors note: The sources disagree: the fan-out decision is Claude's (a:dc3bc182-02), while the exploration brief was recorded as ali because it appears as a user-role message inside the subagent transcript. Attributed to Claude, who chose the method under Ali's instruction to ground framing in the code.*

**Decision.** Run four read-only sub-agent explorations in parallel — driver code, comparator findings, detection/taxonomy evidence, root self-assessment docs — each briefed to report back in compact prose on headline numbers, the comparator gap, routing refutations and the measured-best config, and anything contradicting the original narrative, with conclusions only and no file dumps; framing options are synthesised only after all four report.

**Why.** Needed to base the framing on the actual code and measured artifacts rather than on documentation, per Ali's instruction; the brief's "conclusions only, no file dumps" constraint is stated without a recorded reason.

**Status.** adopted.

**Source.** `a:dc3bc182-02`, `b:dc3bc182-sub-sub-agent-ab4c4f-11`

> Four explorers are running over the driver code, comparator findings, detection/taxonomy evidence, and root self-assessment docs. I'll synthesize framing approaches once they report back.
>
> — `2026-07-18_dc3bc182.txt:30`

> Conclusions only, no file dumps.
>
> — `2026-07-18_dc3bc182_sub-agent-ab4c4f.txt:12`

### <a id="d-466"></a>D-466 — Run S-D6 in the current session at Ali's direction, overriding the fresh-session rule

`2026-07-22` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: ali

**Decision.** After the rulings CSV was saved to reports_detectors/adjudication/sd6_rulings.csv, Ali directed that S-D6 (applying the rulings, causal recall, FINDINGS, #31 close-out) proceed in the current session rather than as its own fresh session with the §8 kickoff prompt, as had been recommended.

**Why.** *No rationale recorded in the sources — a finding about the record, not an omission of this document.*

**Status.** adopted. Supersedes: *Claude's recommendation that S-D6 run as its own fresh session per plan session discipline*.

**Source.** `a:2e726dc0-21` · Artifacts: `merge-tool-comparison/reports_detectors/adjudication/sd6_rulings.csv`

> is S-D6's job, ideally as its own fresh session with the §8 kickoff prompt.
>
> — `2026-07-16_2e726dc0.txt:709`

> file saved, check it and start S-D6
>
> — `2026-07-16_2e726dc0.txt:712`

### <a id="d-467"></a>D-467 — Distil the transcripts with a deterministic script and spend no model on it

`2026-07-25` · **adopted** · `[chat]` · corroboration: mixed · confidence: high · actors: claude

**Decision.** Build the decision record from a distilled corpus: 32 Claude Code .jsonl sessions (73.7 MB) reduced to 1.52 MB (2.1%) by stripping tool_use, tool_result, thinking blocks and system reminders, keeping only human↔assistant deliberation text, one distilled .txt per session in the scratchpad. The reduction is implemented as a Python script with no model judgment involved.

**Why.** The deliberation text is "the part that actually contains decisions, and it's small enough to read end to end"; and because the reduction is deterministic a model adds nothing — "The 73.7 MB → 1.52 MB step is deterministic. Don't spend a model on it."

**Status.** adopted.

**Source.** `a:c4c4d030-01`, `a:c4c4d030-09` · Artifacts: `~/.claude/projects/-Users-alikarimli-JupyterProjectsOfMine-my-data-project/`

> distilled to 1.52 MB (2.1%) by stripping tool calls, tool results, thinking blocks and system reminders
>
> — `2026-07-25_c4c4d030.txt:25`

> The 73.7 MB → 1.52 MB step is deterministic. Don't spend a model on it.
>
> — `2026-07-25_c4c4d030.txt:91`

### <a id="d-468"></a>D-468 — Withdraw the read-end-to-end claim and put measured 61.5% coverage on the record

`2026-07-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The claim that the distilled corpus was read end to end is withdrawn. Measured coverage is 9,442 of 15,354 lines read in full (61.5%), with 38.5% keyword-grepped only; the unread files are named individually (4c7b0828, 2e726dc0, 9e4b6896 lines 500-1257, acf7e1d0, 82dd479f) and both the audited numbers and the named gaps are stated in the document's coverage section.

**Why.** The judgment that the unread files were non-decision-bearing, made from their user prompts, proved unreliable: spot-checking the two highest-risk files surfaced four decisions the record was missing, so "the gap is on the record rather than hidden".

**Status.** adopted. Supersedes: *the earlier claim that the distilled corpus was read "end to end" (implied 100% reading coverage)*.

**Cross-theme.** *depended on by* ← [D-284](#d-284) (see the reconciliation note there)

**Source.** `a:c4c4d030-05` · Artifacts: `docs/DECISIONS.md`

> I told you I read the distilled corpus "end to end." **That was wrong.**
>
> — `2026-07-25_c4c4d030.txt:56`

> **9,442 of 15,354 lines read in full = 61.5%. 38.5% was keyword-grepped only.**
>
> — `2026-07-25_c4c4d030.txt:58`

> The coverage section states the audited numbers and names every file not read in full, so the gap is on the record rather than hidden.
>
> — `2026-07-25_c4c4d030.txt:73`

### <a id="d-469"></a>D-469 — Run v2 extraction as two independent passes with a frozen decision definition

`2026-07-25` · **adopted** · `[chat]` · corroboration: both · confidence: high · actors: claude

**Decision.** The v2 decision-record instrument: fix the distiller to glob `<session>/subagents/*.jsonl` as well as top-level files (21 files, 5.4 MB never processed) and to stop dropping isSidechain messages, emitting one .txt per session plus a manifest with per-file line counts; extract each session twice independently, diff the two decision lists per session, report an agreement rate and route every disagreement to a review queue for Ali; freeze a definition of "a decision" as anything that constrains future work, explicitly including tool/approach rejections, carve-outs to standing rules, mandated processes, coverage boundaries, accepted known costs and corrections to earlier claims, and explicitly excluding status updates, restatements and results without a choice attached; require date, one-line title, decision, rationale-as-argued, status and at least one verbatim quote per decision, machine-check every quote as a substring of its source file, and say "rationale not recorded" rather than invent one; size batches at ~2,000-2,500 distilled lines and never split a transcript file across batches.

**Why.** The two-pass design "is exactly your own G3 protocol from #30, pointed at a different corpus" and "converts 'did it miss something?' from a question you can't answer into a measured number, and it's the one design that would have caught D-65/D-66/D-67 automatically". The decision definition is set by the v1 misses (Joern rejection, GD2 tune-run carve-out, triple review, coverage boundaries), which were "exactly these non-obvious shapes, stated in prose that no keyword search would find". The quote/rationale discipline addresses the failure mode that matters: "a confidently-worded rationale that nobody said". The distiller fix follows from v1 globbing top-level files only, so 21 subagent transcripts were never processed. Batches must not split a file because "you lose the thread of an argument that spans it".

**Status.** adopted. S12 (2026-07-26): executed in full by the rebuild — the distiller globs subagent transcripts (21 files in the corpus) and keeps isSidechain turns (817), per-file manifest line counts exist, extraction ran twice independently with the agreement rates reported (73.6% / 80.7%), and disagreements went to the union + corroboration tiers rather than silently into the document (PROTOCOL §2, §8 Amendments 1-3; this record's own preflight re-derives it).

**Cross-theme.** *depended on by* ← [D-186](#d-186) (see the reconciliation note there)

**Cross-theme.** *depended on by* ← [D-284](#d-284) (see the reconciliation note there)

**Source.** `a:c4c4d030-06`, `a:c4c4d030-08`, `a:c4c4d030-13`, `a:c4c4d030-14`, `a:c4c4d030-18` · Artifacts: `#30`, `*/subagents/*.jsonl`, `docs/DECISIONS.md`

> **make it a two-pass job with a stability diff** — which is exactly your own G3 protocol from #30, pointed at a different corpus.
>
> — `2026-07-25_c4c4d030.txt:83`

> A DECISION is anything that constrains future work. It includes shapes that do
>
> — `2026-07-25_c4c4d030.txt:126`

> transcript records a decision without one, say "rationale not recorded".
>
> — `2026-07-25_c4c4d030.txt:142`

> the extractor globs top-level `*.jsonl` only, so **21 subagent transcripts (5.4 MB)** under `<session>/subagents/` were never processed
>
> — `2026-07-25_c4c4d030.txt:52`

> never split a transcript file across batches** — you lose the thread of an argument that spans it.
>
> — `2026-07-25_c4c4d030.txt:189`

