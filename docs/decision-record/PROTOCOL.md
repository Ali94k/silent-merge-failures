# Decision-record rebuild — protocol

**Status:** FROZEN at S0 close-out, 2026-07-25.
**Owner:** Ali.
**Produces:** a rebuilt `docs/DECISIONS.md` with audited coverage.
**Supersedes:** the v1 pass that produced the current `docs/DECISIONS.md` — a
single-session run that read 61.5% of the corpus while reporting complete coverage.

Changes to §1–§7 after extraction begins require a dated §8 amendment. Never a
silent edit.

---

## 1. Why this exists

`docs/DECISIONS.md` v1 was built in one session. It missed 38.5% of the corpus,
and a spot-check of two skipped transcripts recovered three real decisions
(v1 D-65/D-66/D-67, archived at `docs/historical/DECISIONS-v1.md`; their v2
entries are D-110, D-279 and D-118) plus a carve-out to a standing rule. The root cause was not a
bad prompt — it was **no mechanical coverage gate**, so triage decisions taken
under context pressure went unrecorded and the coverage claim was optimistic.

Three design consequences, each aimed at that failure:

1. **The corpus exceeds one context window** (~430k tokens). Split the work, do
   not compress it.
2. **Coverage is asserted mechanically**, not narrated. `lines_read` must equal
   `lines_total`, and a checker enforces it before commit.
3. **Grep is not reading.** Design rationale is stated in ordinary prose that
   contains none of the words you would search for. The single clearest example
   in this corpus is a rejection of Joern argued as *"import and name binding are
   a frontend concern"* — no keyword search finds that.

## 2. Corpus

Produced by `distil_transcripts.py`, committed under `distilled/`.

| | |
|---|---|
| Source | 32 session + 21 subagent transcripts, 82.1 MB |
| Distilled | 53 files, **16,972 lines / 1.74 MB (2.12%)** |
| Window | 2026-05-18 → 2026-07-25 |
| Parse failures | 0 |

The distiller drops tool calls, tool results, thinking blocks and harness
wrapper tags, and **counts every drop by category** in `manifest.json`. Two v1
bugs are fixed: subagent transcripts are now included, and `isSidechain` turns
are kept (817 of them). Image and document attachments become explicit
placeholders rather than vanishing.

**The distilled corpus is committed**, which is a deliberate deviation from the
repo's usual "regenerable data is gitignored" rule (v1 D-57, archived at
`docs/historical/DECISIONS-v1.md`; v2 D-341). The
source transcripts live outside git, on one machine, and rotate. Committing the
distillation is what makes every quote in the finished record independently
checkable by someone who does not have that laptop.

**Coverage limit, unchanged from v1 and not fixable here:** 59 commits predate
2026-05-18 and have no transcript. That period is reconstructed from git and
`docs/plans/` at consolidation, and tagged `[reconstructed]`.

## 3. Instruments (frozen)

| File | Role |
|---|---|
| `distil_transcripts.py` | corpus + manifest + batch plan |
| `extraction.schema.json` | per-transcript output contract |
| `extract_prompt.md` | the extraction session kickoff |
| `verify_extractions.py` | quote / line / coverage / schema checker |
| `extractions/pilot/` | the S0 calibration set — 3 files, 12 decisions |

Extraction sessions adapt to the schema; the schema does not adapt to them.

## 4. Sessions

| Session | Job | Reads |
|---|---|---|
| **S0** | this document, the instruments, the pilot | 3 files |
| **S1–S9** | extract decisions per batch → JSON | its batch only |
| **S10** | consolidate: dedupe, resolve supersession, backfill pre-transcript period, write `docs/DECISIONS.md` | the JSONs, not the corpus |
| **S11** | audit: re-verify, spot-check ~10 entries against source, report residual risk | samples |

**Handoff is committed artifacts only.** No context carried between sessions, no
summary handoff, no cold session trusting its predecessor's memory. This is the
same rule the #30 and #31 programs ran on.

### Batch assignment

File-atomic — a transcript is never split, because an argument that spans one
must be read as one. Target 2,500 distilled lines per session.

| Batch | Lines | Files | Window | Content |
|---|---:|---:|---|---|
| S1 | 2222 | 6 | 2026-05-18 → 06-09 | sessions |
| S2 | 1183 | 3 | 2026-06-11 → 06-20 | sessions |
| S3 | 2495 | 1 | 2026-06-24 → 07-03 | one large session |
| S4 | 1000 | 4 | 2026-06-24 → 07-05 | mixed |
| S5 | 2216 | 3 | 2026-07-06 → 07-23 | sessions |
| S6 | 2463 | 4 | 2026-07-08 → 07-15 | sessions |
| S7 | 2194 | 21 | 2026-07-15 → 07-16 | mixed |
| S8 | 2335 | 8 | 2026-07-16 → 07-25 | mixed |
| S9 | 864 | 3 | 2026-07-22 → 07-25 | sessions |

Authoritative assignment is `distilled/manifest.json` → `batching.batches`.

## 5. Gates

**G-COV — coverage.** Every extraction file has `lines_read == lines_total` and
`coverage_complete: true`. Enforced by `verify_extractions.py`. A session that
cannot meet it says so and stops; it does not round up.

**G-QUOTE — provenance.** Every decision carries ≥1 quote that is an exact
substring of its source at the stated line. Enforced mechanically. This gate
exists because this project has already caught a fabricated quote inside an
LLM-coded instrument (`THREATS_TO_VALIDITY.md` §4.4.9) — the same failure mode,
the same guard.

**G-CAL — calibration.** Pilot density was **1 decision per 53–60 lines** across
a high-density architecture session, a low-density presentation session, and the
review session v1 missed entirely. A batch landing far outside that range is not
automatically wrong, but must be explained in `notes`.

**G-AUDIT — S11.** Re-run the checker over everything, spot-check ~10 entries
against source, and report the residual-risk estimate. Coverage is stated in the
finished document as a number, never as an adjective.

## 6. Optional: two-pass stability

If maximum recall is wanted, run S1–S9 twice independently and diff the decision
lists per file. Agreement rate is the recall statistic; disagreements go to a
review queue for Ali rather than silently into the document. This is `#30`'s G3
stability check pointed at a different corpus.

Cost: doubles the extraction phase (~18 sessions). The single-pass alternative —
one careful pass with G-COV and G-QUOTE enforced — is what this protocol assumes
by default, because the v1 failure was coverage, not judgment: the decisions that
were missed were in files that were never read, not in files that were read and
misjudged.

## 7. Standing constraints

- `ISSUES.md`, `STATUS.md`, `THREATS_TO_VALIDITY.md` and `docs/plans/` remain
  authoritative. This record is an index and a rationale archive.
- The value is the reasoning that exists **only** in chat. Do not re-derive what
  those documents already state.
- Extraction sessions must not read `docs/DECISIONS.md` v1 — it is partial and
  known-lossy, and anchoring on it defeats the rebuild.
- Report coverage honestly. **An audited 80% beats a claimed 100%.**

## 8. Amendments

Add dated entries here; never edit §1–§7 in place once S1 has started.

### Amendment 1 — 2026-07-25: extraction runs on the Batch API

Adopted before S1 started. Affects **§4** (session structure) and **how §5's G-COV
is enforced**. §1–§3, §6, §7 unchanged.

**What changes.** S1–S9 were nine interactive extraction sessions, each reading a
batch of files and asserting its own coverage. They are replaced by **53 Message
Batches requests, one per distilled file**, submitted and collected by
`extract_batch.py`. §4's batch table is superseded and kept as record only — the
batching existed to fit a session's context budget, which no longer binds.

**Why.** v1's failure was that an interactive session chooses how much to read, so
`lines_read == lines_total` was a claim the model made about its own behaviour
(§1). In a batch request the whole file is in the prompt; there is no triage step
left to fail. G-COV stops being asserted and becomes structural.

Each consequence below is a deviation, recorded as one:

1. **G-COV is now a runner invariant, not a model assertion.** `file`,
   `lines_total`, `lines_read` and `coverage_complete` are written by
   `extract_batch.py` from `manifest.json` at collection. The request schema is
   `extraction.schema.json` minus those four fields — the model is not asked to
   attest to something it no longer controls. `verify_extractions.py` is unchanged
   and still runs, so the on-disk contract is identical.

2. **Transcripts are line-numbered in the prompt** (`NNNN| ` prefix), so quote line
   numbers are read off rather than counted. This targets the one defect the
   checker caught in the S0 pilot. The collector strips a leading line-number
   prefix from quote text if and only if the raw text is absent from the source and
   the stripped text is present; the repair count is reported. Quote text is never
   otherwise altered — G-QUOTE is unchanged and still the gate.

3. **`extract_prompt.md` stays frozen and is sent verbatim, minus its
   harness-mechanics sections.** The runner slices the named judgment sections out
   of the frozen file and records its blob SHA. Excluded, because the runner now
   owns that I/O: AUTHORITY, STATE, YOUR BATCH, SCOPE, GUARDRAILS, BEFORE YOU
   COMMIT, EXIT. Included verbatim: THE GATE, WHAT COUNTS AS A DECISION, STATUS
   WHEN NOTHING WAS RATIFIED, GRANULARITY, DENSITY AS A SELF-CHECK, RATIONALE
   DISCIPLINE, QUOTES, ACTORS, NEAR MISSES. The runner adds a short preamble
   stating the task, the line-number convention and the JSON-only output contract;
   that preamble lives in the runner source and is frozen with it from S1 on.

4. **Model is `claude-opus-5`**, adaptive thinking, `effort: high`, structured
   output against the reduced schema. The #30 taxonomy program ran the same
   settings on `claude-opus-4-8`; the difference is recorded so the two instruments
   are never reported as one.

5. **Two-pass stability (§6) becomes cheap** — a second submission and a diff
   rather than nine more sessions. Single-vs-two-pass remains **Ali's open call**;
   the runner takes `--pass a|b` either way.

**Validation gate on this amendment.** The three S0 pilot files run through the
runner first and are diffed against the hand-extracted `extractions/pilot/` JSONs.
That is a direct agreement measure between the S0 method and this one, against
ground truth that already exists. The other 50 files do not go out until that diff
has been read.

**Gate result, 2026-07-25** (`extractions/pilotA`, batch `msgbatch_017GX95RXtiop`):
PASSED on recall, at a materially lower threshold.

| | |
|---|---|
| Mechanics | 3/3 succeeded, no truncation; **91/91 quotes verbatim and correctly numbered**, 0 prefix repairs — consequence (2) works |
| Recall vs the hand set | **12 matched, 0 missed** — a strict superset |
| Threshold | 50 decisions vs the hand pass's 12; agreement 24%, entirely from 38 batch-only entries |
| Cost | $0.41 / 692 lines → ~$10 per corpus pass; `cache_read` 0 (concurrent requests cannot read each other's cache write) |

The 38 extras are three different things: decisions the hand pass genuinely
missed (the Spoon/JavaParser/CodeQL/Semgrep rejection, the assertj-shape FN
boundary, the SE-17 scope boundary); splits where the hand pass merged (the
tree-sitter and ecj rungs); and items the hand pass **explicitly listed in
`near_misses` with reasons** (deck naming, the 7-slide spine, the second-pivot
framing) — a documented threshold disagreement, not an error.

**Root cause is a tension inside the frozen prompt**, not a runner defect:
GRANULARITY says extract finer and cites 8-from-465-lines; DENSITY says ~1/50–60
and warns that ~1/15 means recording status updates. The model followed
GRANULARITY, landed at 1/13, and self-reported the deviation in `notes` on all
three files — which is what DENSITY asks of it. **Left unresolved deliberately**;
recall is what v1 failed at, and the near_misses lists let S10 audit the threshold
in both directions.

**Open, and Ali's to close:** (a) whether to keep this threshold or tighten it,
and (b) the S10 consequence — 1/13 projects to ~1,226 raw decisions / ~457k tokens
of extraction JSON, against the S0 appendix's ~300, so consolidation will not fit
one session. Sequenced after extraction, since neither changes what gets extracted.

**One pre-S1 revision to the runner preamble**, recorded rather than made
silently: `title` length is now stated in the preamble, because the schema's
`maxLength: 90` cannot survive the structured-output subset and 8 of the 50 pilot
titles overran it. `extractions/pilotA` was produced *before* this revision.

### Amendment 2 — 2026-07-25: quotes may span a line break

Ruled by Ali after the pass-`a` extraction. Amends **§5 G-QUOTE**.

**What changes.** A quote is no longer required to sit on one line. It must be a
verbatim substring of the distilled file, and `line` must be the line it *starts*
on. `verify_extractions.py` checks exactly that; a repeated quote is valid at any
of its occurrences.

**Why.** The one-line rule was a simplification that collides with the corpus:
the distilled transcripts are hard-wrapped, so a sentence of argument routinely
crosses a break. It cost real evidence — 30 of pass `a`'s 35 residual failures
were quotes that were *verbatim* and rejected only for spanning a wrap. Requiring
one line would have forced either truncated evidence or a re-extraction, both
worse than relaxing a rule that was never load-bearing. The fabrication guard is
untouched: the text must still be present in the source, character for character.

**Repairs applied to pass `a`** (`repair_quotes.py`, log in
`batch_state/repairs_a.json`; model output is preserved unmodified in
`batch_state/raw_a.json`, so every one is reversible):

| | n | |
|---|---:|---|
| Line moved to the quote's start line | 29 | text already verbatim |
| List enumerator restored | 6 | `**Header says…` → `**3. Header says…` |
| Line-wrap whitespace restored | 4 | `foo bar` → `foo\n   bar`, from the source |
| One-token slips | 5 | adjudicated individually — see below |
| `rationale_recorded` cleared | 1 | claimed a rationale, supplied none |

The five slips, each repaired to the source text and verified by exact match:
`paper over it`→`them`; `design is third`→`are`; `the line-74 comment`→`The`; a
stray `)` after `row 14`; a leading `**` that opened earlier in the source line.

**Final state: 1,323 quotes, all verbatim, all line numbers correct, 53/53 files
coverage-complete.**

**Two things recorded rather than fixed:**

1. **100 of 760 titles exceed 90 characters** (87% compliance). The limit moved
   from the schema to the prompt when `maxLength` was stripped for the
   structured-output subset, and a prompt constraint is softer than a schema one.
   The checker warns rather than fails, and S10 rewrites titles for the finished
   document, so this is cosmetic — but it is the measured cost of that stripping.

2. **Automated fuzzy quote repair was attempted and abandoned.** Four successive
   matchers each produced a *new* silent corruption — truncating `them` to `th`,
   deleting it outright, stripping a leading `**` and leaving unbalanced markdown.
   The cause is structural, not a bad threshold: similarity scoring prefers
   deleting the differing token to restoring it (`"…paper over "` scores 0.986
   against the claim; the correct `"…paper over them"` scores 0.959). The design
   that shipped applies **only deterministic single-candidate transforms verified
   by exact substring match**, and routes everything else to a human queue. Worth
   remembering the next time a repair looks automatable.

### Amendment 3 — 2026-07-25: §6 two-pass run, and its result

Ali elected the two-pass option. Pass `b` ran the same instrument, model
(`claude-opus-5`), effort and schema over the same 53 files. **Not
request-identical**, unlike #30's Phase-3 double batch: `max_tokens` differed
(pass `a` flat 32,000 with a re-run at 100,416 for the one file that truncated;
pass `b` scaled 32,000–119,760). The ceiling is non-binding in both — nothing
truncated in either pass's final data — but the §6 metric must not be reported
as request-identical.

**Result.** 769 decisions vs `a`'s 760; 1,306 quotes vs 1,323; all verbatim,
coverage complete on both.

| | |
|---|---:|
| Matched (same decision, overlapping evidence) | 648 |
| Only in `a` | 112 |
| Only in `b` | 121 |
| **Agreement** | **73.6%** of 881 distinct |

**Below §6's ≥80% band, and the shortfall is real rather than an artefact of the
matcher.** Pairing is anchored on quoted-line overlap within ±3 lines; widening
that window to ±8 / ±15 / ±30 moves agreement only to 75.5% / 77.8% / 79.2%, and
±30 is already generous enough to risk false pairings. Two independent passes
genuinely disagree on roughly a quarter of what they find.

**What that buys, and why it was worth $7.65.** The disagreement is near
symmetric (112 vs 121), so neither pass is systematically better — this is
threshold noise on a corpus where "what counts as a decision" is a judgment.
The consequence is the recall argument, quantified: **either pass alone captures
only ~86–87% of the union.** A single pass would have missed roughly one decision
in seven that a second pass found. That is the same failure v1 had, one order
smaller.

**Consequence for S10.** Consolidation should read the **union (881)** and use
the pairing as a confidence signal, not read one pass. A decision found
independently by both passes is corroborated; a single-pass decision is a
candidate that needs the transcript checked. The full unmatched list is
`batch_state/stability_ab.txt` (2,525 lines) — §6's review queue, and Ali's, not
a script's, because "the other pass missed it" and "this pass over-extracted"
are indistinguishable mechanically.

### Amendment 4 — 2026-07-25: the pre-transcript period joins the pipeline

Ali's ruling: reconstruct that period from **commit logs *and* the plan/historical
documents**, because "pre-transcript commit messages are not good enough to
reason" — they record what landed but compress away why, and the plan documents
carry the argument a transcript would otherwise have held.

**It is not a special case.** §2's 59 commits and the 15 documents first committed
before 2026-05-18 become **16 distilled source files** (`build_pretranscript.py`,
6,962 lines, 259k tokens) and run through the existing instruments: extract,
verify, repair, classify, slice, consolidate. Quotes stay verbatim substrings of
real files with real line numbers, so **G-QUOTE is restored rather than waived** —
which also dissolves the `entry.schema.json` defect noted below, since these
entries have real `sources` and real `evidence`.

Three changes this forced:

1. **The frozen id pattern** now also accepts `pre-<slug>-NN` alongside
   `<session8>-NN`; a reconstructed source has no session id. `pre--01` and
   `Bad-01` still fail.
2. **The runner tells the extractor its source type**, because the two need
   opposite defaults. `commits`: written after the fact, records what *landed*, so
   ratified unless the message says otherwise; actors normally `ali`. `plan`:
   written *before* the work, default `status=proposed`.
3. **`extract_batch.py --pre`** selects by manifest `kind`.

**Result.** preA 409 decisions, preB 413, **agreement 80.7%** of 455 distinct —
*above* §6's ≥80% band, where the transcripts managed 73.6%. A plan states its
decisions explicitly so two passes agree on what counts; a conversation does not.
Note the two axes: these sources are **weaker evidence** (post-hoc,
non-deliberative, sometimes stale) but **more stable to extract from**. The
stability number says nothing about the first fact — `provenance: reconstructed`
carries it.

**A period v1 covered with 8 entries yielded 409 raw decisions.** v1's
reconstructed half was missing proportionally more than its transcript half.

**The instruction that did not take, and where it moved to.** The runner told the
extractor to default plan documents to `status=proposed`. It did not: plan-doc
decisions came back **217 adopted / 90 proposed** in pass A and **219 / 94** in
pass B — two independent passes within two decisions of each other, so this is a
property of the documents, not a slip. A plan states its decisions in a settled
voice, and at the time of writing they often genuinely were settled; what a plan
cannot evidence is that they *survived*.

Rather than redefine `proposed` for one source type, the ruling moved to
`consolidate_prompt.md`, which now carries **PLAN-SOURCED DECISIONS ARE
STATUS-AS-OF-THE-PLAN**: before an entry built from a `pre-` source is adopted, it
must be confirmed by a `pre-commits-` source showing the thing landed or by a
transcript-era source in the same slice; otherwise `proposed` with a status_note,
or `superseded` where a later source overrides it. That is the one place a
consolidation session may downgrade a status extraction gave it. The check is put
where the evidence is — a single-document extractor cannot know what happened
afterwards, and the slices contain both.

**Slip repairs: 2 in preA, 3 in preB**, adjudicated per pass. A new systematic
pattern, same family as the elided list enumerator: markdown structure normalised
away while quoting — an ASCII `|` for a box-drawing `│`, a leading box gutter, an
elided `- [ ] ` checkbox, backticks added around a filename. The model renders
markdown as it reads rather than as it is written.

**Sizing consequence.** The corpus becomes ~1,336 decisions and the union ~764k
tokens. The thematic split was already necessary; `detection` grows from 94k to
roughly 140k, still comfortable for one session.

---

**Slip repairs in pass `b`: 7**, adjudicated separately (`SLIP_FIXES` is keyed by
pass — decision ids are minted per pass, so `a`'s rulings must not leak across).
Three are **independent reproductions of `a`'s slips on the same source spans**:
the stray `)` after `row 14`, the spurious leading `**`, the lowercased `The`.
The new ones are of the same kind — `behaviour`→`behavior`, `**only** the` for
`**only the`, a dropped Oxford comma, `;` for an em-dash. The failure mode is a
systematic property of how the model excerpts hard-wrapped markdown, not random
noise, which is why the exact-substring gate is load-bearing rather than
belt-and-braces.

**Unchanged:** `extraction.schema.json`, G-QUOTE, G-CAL, G-AUDIT, §7's standing
constraints, and S10/S11 remaining interactive sessions.

### Amendment 5 — 2026-07-26: S12 resolves the proposed residue against the repo

Ali's ruling, closing open call 1 from the S10z close-out: **"resolve the 96
proposed entries against the code."** A new pass (S12, interactive, same session
as S10z/S11 at Ali's direction) checked every `status: proposed` entry against
the working tree at `2b53b91` — following each entry's own `status_note` pointer
into source files, git history, plans and report artifacts.

**Result: 53 adopted · 25 still proposed · 11 superseded · 7 abandoned.**
Per-entry verdicts with file:line / commit evidence: `proposed_resolutions.json`.
The 25 that stay proposed are genuinely pending — almost all thesis-writing
decisions awaiting a draft (no chapter, spine or claims ledger exists in the
repo), plus the still-open default-enable preconditions and two items that are
not repo-checkable.

Deviations, each recorded rather than made silently:

1. **`status_note` is now non-null on resolved entries**, carrying the evidence
   line prefixed `S12 (2026-07-26):`. The schema's description said "Null
   otherwise"; the checker never enforced that and is unchanged. The prefix is
   load-bearing: a code-confirmed `adopted` is a **post-hoc verification against
   the repo**, not a record-visible ratification, and the note keeps that
   distinction inspectable per entry.
2. **Three superseded entries carry no `superseded_by` pointer** because the
   superseder is cross-theme or not an entry at all:
   `shared-cpg-refactor-proposal` (declined by scope-architecture D-023),
   `v2-model-split-sonnet-opus` (superseded by this protocol's own Amendment 1),
   `empty-merger-slot-no-dispatcher-diamond` (overtaken by the backends-routing
   dispatch arc D-049 → D-076). `verify_entries.py` reports exactly these three
   as warnings; accepted.
3. **Mixed-outcome convention.** Where a proposal received an explicit recorded
   ruling adopting some parts and declining others *with reasons* (the ISSUES
   #31 review-record pattern), the verdict is `adopted` and the note carries the
   per-part disposition — nothing is left pending. A recorded decline is a
   ruling, not an abandonment.
4. **"Status as of" moves to 2026-07-26** for exactly these 96 entries; no
   other entry field was touched, so every derived field the checker recomputes
   (corroboration, provenance, dates, actors) is unaffected.
5. The adoption bar was deliberately asymmetric, per the consolidation prompt's
   own rule that a wrong `adopted` is the worst available error: `adopted` only
   on concrete artifact evidence; anything ambiguous stayed `proposed` with the
   check recorded.

### Amendment 6 — 2026-07-26: Ali closes open calls 2 and 3

**Call 2 — v1's fate.** Ruled: v1 is kept as
`docs/historical/DECISIONS-v1.md` (byte-verbatim copy of the `bca6f85` blob
under a dated archive banner) and the stale references are fixed. The three v1
`D-nn` citations in this document's frozen sections (§1's D-65/D-66/D-67, §2's
D-57, the appendix's D-63) were retargeted in place to name the archived file
and the corresponding v2 entries — an editorial change to §1–§7, recorded here
per the never-a-silent-edit rule; no semantic content changed. No other v1
D-number references exist in the repo or the memory stores (grepped).
`docs/DECISIONS.md` v2's front matter now points at the archive.

**Call 3 — record vs index.** Ruled: the 469-entry granularity stands;
nothing about the consolidation is changed.

### Amendment 7 — 2026-07-26: Ali closes call 4 — no actors hand check

Ruled: the actors hand check is not needed. The distribution stands as
extracted (claude 229 / joint 90 / ali 41 / unclear 109). The provenance
caveat is not removed by this ruling and travels with the numbers wherever
they are cited: extraction assigns actors from transcripts in which Claude
does most of the *writing* even where Ali makes the *call*, and most
`unclear` entries rest on commit messages, which rarely name a decider.

**All four S10z open calls are now closed** (1: S12/Amendment 5;
2 and 3: Amendment 6; 4: here). The rebuild has no open questions.

---

## Appendix — S0 close-out

**Built and verified:**

- Distiller rewritten. Recovers **+1,618 lines (+10.5%)** over v1: 21 subagent
  transcripts (1,352 lines) plus 817 retained `isSidechain` turns. Drop
  accounting is complete and every dropped record type is named. 0 parse failures.
- Schema frozen. Fields chosen against v1's specific failures: the coverage gate,
  a `shape` enum that operationally *defines* "decision", `rationale_recorded` as
  a fabrication guard, `supersedes` / `revises_claim` for decision arcs that v1
  handled inconsistently, and `actors` — which v1 lacked entirely and which feeds
  the thesis contribution-delineation table (v1 D-63, archived at
  `docs/historical/DECISIONS-v1.md`; the v2 entries are D-424/D-427).
- Extraction prompt frozen, with the six decision shapes that "do not look like
  decisions" written in as worked examples drawn from real misses.
- Checker written. **It failed the S0 pilot on first run** — a wrong line number
  in one of the twelve pilot decisions — and passed after the fix. A gate that
  has never rejected anything has not been tested.

**Pilot calibration** (`extractions/pilot/`, 3 files, 12 decisions, verifier green):

| File | Lines | Decisions | Density | Why this file |
|---|---:|---:|---|---|
| `2026-05-18_20b53f98` | 465 | 8 | 1/58 | high-density architecture; known ground truth |
| `2026-06-18_12c77ea5` | 120 | 2 | 1/60 | low-density presentation; false-positive discipline |
| `2026-07-16_734e4529` | 107 | 2 | 1/53 | **the file v1 skipped entirely** |

Six of eight `shape` values and three of four `actors` values were exercised;
`carve-out`, `reversal` and `unclear` were not, which is expected at n=3.

**The result that matters:** the third pilot file recovers the Joern rejection
and the JDK-set finding — the decisions v1's grep-based triage missed. The
instrument catches what the v1 method could not.

**Projection:** at the pilot density, 16,972 lines implies roughly **300 raw
extracted decisions**, consolidating to an estimated 90–130 entries. v1 produced
67 from a 61.5% read with no subagent coverage.

**Open call for Ali:** single-pass (default, ~11 sessions) or two-pass with the
stability diff (~20 sessions). §6 has the trade-off.
