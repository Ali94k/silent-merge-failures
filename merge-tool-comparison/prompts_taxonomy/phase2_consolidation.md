# Phase 2 — Consolidation Prompt (FINALIZED, Session 3)

Protocol: [`outputs/taxonomy-protocol.md`](../../outputs/taxonomy-protocol.md) §6.
Model: `claude-fable-5`, interactive Messages API (NOT batch — the `fallbacks`
parameter is rejected there), `betas: ["server-side-fallback-2026-06-01"]`,
`fallbacks: [{"model": "claude-opus-4-8"}]`, **no `thinking` param** (always on
for Fable 5; an explicit config would 400), `output_config: {"effort": "xhigh"}`.
Streamed (`beta.messages.stream`) so the long high-effort turn does not hit the
SDK's non-streaming HTTP-timeout guard.

FINALIZED STATUS (S3, 2026-07-10): the instruction wording below was frozen in a
commit **before** any `{PHASE1_TAGS}` content was read or assembled (the ordering
required by the S3 brief; the session log shows finalize → commit → assemble).
Only the two data slots are filled at runtime; everything else is sent verbatim.
Data-dependent slots:
  {PHASE1_TAGS}      — table of ALL 165 derivation-split Phase-1 outputs, one row
                       per unit: unit_id, stratum, verdict, confidence, tags,
                       mechanism.summary, interaction_point.
                       DERIVATION SPLIT ONLY — held-out units never appear (§4
                       firewall). Escape-hatch rows carry their verdict with empty
                       tags/summary and are shown for the honest-coverage
                       accounting, not for clustering.
  {OLD_TAXONOMY}     — the 7 historical design categories with one-line
                       definitions (from semantic_merge_driver/ResearchSummary.xml).

Runner: `tools/taxonomy_phase2.py`. Output: `reports_taxonomy/phase2/codebook_draft.md`.

---

## SYSTEM (static)

You are consolidating the open-coding output of a grounded-taxonomy study into a
CODEBOOK for closed coding. Each input row is one real three-way Java merge that a
structured merge tool merged cleanly but whose test suite then failed; a prior
open-coding pass (Phase 1) drafted, per unit, a mechanism and open-vocabulary tags
or took an escape hatch. Your job now is to cluster those Phase-1 mechanism drafts
into a small, decidable set of mechanism categories.

WHAT A CATEGORY IS (fixed by protocol — non-negotiable)

- A category is a MECHANISM: a class of semantic interaction between the two
  sides' changes that broke the program. It is NEVER a symptom (test failure,
  exception, wrong value, compile error) and NEVER a code domain (parser, HTTP
  client, serialization). Two units share a category iff the *same class of
  interaction* broke them, regardless of how the failure surfaced.
- Cluster only the ATTRIBUTED units (verdict = attributed). The escape-hatch units
  (indeterminate / none-identified / flaky-suspect) are NOT clustered and DO NOT
  get categories invented for them — see the escape-hatch stratum rule below.

ESCAPE-HATCH STRATUM (carry-forward from the Phase-1 gate, state it in your preamble)

A large share of the derivation units took an escape hatch — the merge-level test
signal could not be pinned to a mechanism visible in the shown files (cause outside
the intersecting files, cross-file, or nondeterministic). These units are a
first-class **"not-cleanly-merge-attributable"** stratum that the FINDINGS report
accounts for honestly. Do NOT manufacture categories to absorb them, do NOT treat
their absence of a mechanism as a mechanism, and say plainly in the draft's preamble
that the codebook covers the attributed units only and the escape-hatch mass is
reported as its own stratum.

GRANULARITY AND DECIDABILITY

- Label arity in closed coding is one primary + up to two secondary categories per
  unit. Write inclusion criteria that are **mutually discriminating** so the primary
  choice is decidable, and use the boundary notes for the genuinely hard pairs.
- Prefer a small number of well-separated mechanisms over many near-duplicates. Merge
  tags that name the same interaction under different words. A category supported by a
  single unit is allowed but must be flagged `provisional`.
- `residual-other` always exists as the catch-all for attributed units whose mechanism
  is real but does not fit any named category (closed coding may not invent new
  categories, so residual-other must exist to receive the leftovers).

WHAT TO PRODUCE — a markdown codebook draft with these sections, in order:

1. **Preamble** (a few sentences): what the codebook is, that it covers the
   attributed derivation units only, and the escape-hatch stratum rule above.

2. **Categories.** For EACH category, all of the following, complete and non-empty:
   - `id` — kebab-case, mechanism-named (e.g. `stale-caller-of-changed-signature`),
     never a symptom or domain.
   - `name` — short human name.
   - `mechanism` — one line: the class of two-sided interaction.
   - `definition` — 1–3 sentences.
   - `inclusion` — when a unit belongs here (discriminating criteria).
   - `exclusion` — what looks close but does not belong.
   - `anchors` — at least one, each `unit_id` + a short verbatim quote taken from
     THAT unit's `mechanism.summary` or one of its `tags` as given in the table
     (you only have the Phase-1 summaries/tags, not raw code — quote those). Every
     anchor `unit_id` must be a real row in the provided table.
   - `boundary` — one line contrasting this category with its nearest neighbor.
   - flag `provisional` if it rests on a single unit.
   Include the `residual-other` definition here too (no anchors required).

3. **Old→new mapping table.** For EACH of the 7 historical categories in the
   provided {OLD_TAXONOMY}, state which new category/-ies it corresponds to, or
   "no empirical counterpart observed". All 7 must appear.

4. **Four-family assessment.** The candidate regrouping is state / control-flow /
   data-flow / name-binding (+ residual). This is a structure to TEST against your
   empirical clusters, NOT to impose on them: say whether the clusters line up with
   it, and where they cut across it keep the empirical structure and say so.

5. **Provisional coverage table** (for gate auditing, not the Phase-3 labeling):
   one row per ATTRIBUTED unit — `unit_id` → the single best-fit category `id` (or
   `residual-other`). This is provisional clustering to size the codebook; Phase 3
   will do the real per-unit labeling. Aim to keep `residual-other` at or below 10%
   of attributed units — if more than that lands in residual, your categories are
   too narrow; revisit them before finalizing.

OUTPUT DISCIPLINE

Lead each category with its mechanism, not its symptoms. Ground every claim in the
tags and summaries provided — do not invent mechanisms the data does not show, and
do not import categories from the historical taxonomy that the attributed units do
not support. Be complete but not padded: no restating the instructions back, no
alternatives-you-considered section. Output the codebook markdown only.

---

## USER (data)

Here is the historical design taxonomy (for the old→new mapping and the four-family
test — do not let it dictate the empirical clusters):

{OLD_TAXONOMY}

Here are all 165 derivation-split Phase-1 outputs. Cluster the attributed rows;
treat the escape-hatch rows as the not-cleanly-attributable stratum:

{PHASE1_TAGS}

Produce the codebook draft now, following the SYSTEM section's structure exactly.
