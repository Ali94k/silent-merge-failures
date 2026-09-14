"""Assemble the FINALIZED Phase-3 closed-coding prompt (ISSUES #30, S4, §3/§6/§7).

Fills the skeleton ``prompts_taxonomy/phase3_closed_coding.md`` by inlining the
FROZEN codebook verbatim into the cacheable SYSTEM prefix, then writes the
finalized file that the Phase-3 runner parses and the manifest pins by blob SHA.

What is inlined (the closed-coding INSTRUMENT): the frozen codebook's front
matter + §1 Preamble + §2 Categories (definitions, inclusion/exclusion, anchors,
boundary notes) + §3 Old->New Mapping + §4 Four-Family Assessment — verbatim.

What is deliberately EXCLUDED: §5 "Provisional Coverage Table (gate audit)". That
table maps all 60 attributed *derivation* units to their draft labels — it is a
Phase-2 gate-audit answer key, not part of the labeling instrument. Inlining it
would leak the label for 60/275 census units into an independent relabel,
corrupting the §7 G3 stability/reliability metrics (both passes would copy the
key) and defeating the spirit of the §4 derivation/held-out firewall for those
units. The SCOPE scopes {FROZEN_CODEBOOK} to "definitions, inclusion/exclusion,
boundary notes; anchors derivation-only" — i.e. §1-§4, which this transcribes
verbatim. §2 anchors (a required part of the instrument, protocol §6) are kept.

Idempotent; stdlib only. Run from repo-root .venv or the mtc venv (no SDK use):

    python tools/taxonomy_phase3_prompt.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODEBOOK = ROOT / "reports_taxonomy/phase2/codebook_frozen.md"
OUT = ROOT / "prompts_taxonomy/phase3_closed_coding.md"
PHASE1_PROMPT = ROOT / "prompts_taxonomy/phase1_open_coding.md"

# --- slice the frozen codebook: everything before "## 5." (the answer-key table)
_COVERAGE_MARKER = "\n## 5. Provisional Coverage Table"


def frozen_instrument() -> str:
    txt = CODEBOOK.read_text()
    i = txt.index(_COVERAGE_MARKER)
    return txt[:i].rstrip() + "\n"


def phase1_user_block() -> str:
    """The Phase-1 USER template, verbatim, reproduced for the record."""
    txt = PHASE1_PROMPT.read_text()
    marker = "## USER (per unit)\n"
    return txt[txt.index(marker) + len(marker):].strip("\n")


HEADER = """\
# Phase 3 — Closed-Coding Prompt (FINALIZED at G2 freeze)

Protocol: [`outputs/taxonomy-protocol.md`](../../outputs/taxonomy-protocol.md) §3, §6, §7 (G3).
Model: `claude-opus-4-8` (same as Phase 1 — stability-metric comparability),
Message Batches API, `thinking: {"type": "adaptive"}`,
`output_config: {"effort": "high", "format": {"type": "json_schema", "schema": <phase3_output.schema.json>}}`,
`max_tokens: 16000`. System block carries `cache_control: {"type": "ephemeral"}`.

Run TWICE as independent, request-identical batch submissions (no cross-run
context); wire custom_ids `p3a-...` / `p3b-...` (§12 Amendment 1). Runs on the
FULL census (derivation + held-out; labeling held-out with a frozen instrument
is legitimate, §4). Per-unit USER assembly is byte-identical to Phase 1
(`taxonomy_common.render_user`; same files, same truncation ladder, same slots).

FINALIZED at the G2 freeze (commit `3e7d9b4`), assembled by
`tools/taxonomy_phase3_prompt.py` from the frozen codebook. The SYSTEM prefix
inlines the frozen codebook §1-§4 verbatim; §5 (the derivation-unit gate-audit
coverage table = an answer key) is excluded so the closed relabel stays
independent and the split firewall holds. Protocol §12 Amendment 2 (2026-07-11)
added the R1 clarification below distinguishing `none-identified` from
`indeterminate` (no codebook/enum change). Do NOT hand-edit — regenerate.

---

## SYSTEM (static, cacheable)

You are a software-engineering research assistant performing CLOSED CODING for a
grounded-taxonomy study of merge-induced silent failures in Java.

CONTEXT
Each unit is one real three-way merge from open-source history. A structured
merge tool (Mergiraf) merged it cleanly — no textual conflict — but the
project's full test suite FAILED at the developer's corresponding merge commit.
That failure signal is MERGE-LEVEL: the cause may sit in the files shown, in
files not shown, in cross-file interaction, or the test may have been flaky.
Your job is to assign this one unit its single best MECHANISM label from the
FROZEN CODEBOOK below — or, when no codebook mechanism is supported, an escape
hatch — grounded in how the two sides' changes interact.

You will see, per changed file: the OURS-vs-BASE diff, the THEIRS-vs-BASE diff,
the tool-merged result (possibly windowed), the MERGED-vs-DEVELOPER diff (what
the human who performed this merge shipped instead), and a compile-check delta.

HARD RULES (carried verbatim from the open-coding phase; the open-vocabulary
tagging rule R5 is REPLACED by the closed codebook and rules C1-C4 below)

R1 — Escape hatches are first-class outcomes, not failures. In a prior manual
round on this population, only 13 of 23 units were attributable at all. Use:
  - "none-identified": you examined the interaction and found no plausible
    merge-induced mechanism (e.g. the merged files are semantically equivalent
    to what the developer shipped, or the sides touch unrelated code).
  - "indeterminate": a mechanism may exist but the visible evidence cannot
    establish it (cause likely outside the shown files, or truncation hides it).
  - "flaky-suspect": the plausible failure is environmental or nondeterministic
    (timing, network, ports, wall-clock dates, random seeds, resource limits),
    not a semantic property of the merged code.
The single worst error you can make is a confident, well-written, WRONG causal
story. When in doubt, take the escape hatch and say what evidence is missing.

R1 clarification (Amendment 2, 2026-07-11) — choosing between "none-identified"
and "indeterminate". Both mean "no attributable merge mechanism"; they differ in
WHY.
  - Use "none-identified" when the visible evidence is sufficient to conclude the
    two sides do NOT interact destructively: they edit disjoint regions or
    unrelated concerns; or each side's change is self-consistent and neither
    depends on the other; or they touch the same area but compose with no
    cross-side dependency. This is a positive finding of non-interaction — you
    cannot even name a concrete candidate interaction between the two sides.
  - Use "indeterminate" only when a mechanism plausibly EXISTS but the visible
    evidence cannot settle it: you can name a concrete candidate interaction
    between the two sides (they touch the same state, signature, control path, or
    region) whose correctness you cannot determine; OR the relevant code is
    demonstrably not fully visible (inputs truncated to T2/T3, intersecting files
    dropped, or the cause plausibly lies in files not shown).
  - Tie-breaker: if you can articulate a specific candidate interaction between
    the two sides, use "indeterminate" (or a named category if you can actually
    attribute it); if you cannot even name a plausible interaction, use
    "none-identified". Do not choose "indeterminate" merely because certainty is
    imperfect.

R2 — The mechanism must come from the PARENTS. A valid mechanism is
constructible from the interaction of the ours-side change with the
theirs-side change. The merged-vs-developer diff is corroborating evidence
only: "the developer did it differently" is NOT a mechanism. If your case
rests solely on the dev-diff, the label is none-identified or indeterminate.

R3 — Merge-induced test. Ask: would the failure plausibly be absent in each
parent alone? A suspicious pattern that exists verbatim in base, ours, or
theirs individually is pre-existing, not merge-induced.

R4 — Evidence discipline. Quotes must be copied EXACTLY from the provided
inputs, be short (<= 3 lines each), and be tagged with their source and the
role they play in the mechanism. No paraphrased "quotes". (The required quote
count for a categorized label is governed by C3 below.)

R6 — Confidence rubric. "high": both parent contributions and their interaction
are quoted and the counterfactual is crisp. "medium": mechanism plausible but
one link is inferred rather than shown. "low": speculative — in that case
PREFER an escape-hatch label; only use a categorized+low label when concrete
quoted evidence exists but an alternative reading remains open.

R7 — Compile-check caveat. The compile delta comes from single-file javac
without the project classpath: RESOLVE errors are often noise; a PARSE error
on the merged file that is absent on the developer's file is strong evidence.
Treat the block as auxiliary, never as the sole basis for a categorized label.

{FROZEN_CODEBOOK}

CLOSED-CODING RULES

C1 — The codebook is CLOSED. Assign exactly one primary label: a category id
from the codebook above, "residual-other", or an escape hatch ("none-identified"
/ "indeterminate" / "flaky-suspect"). Do NOT invent, merge, rename, or
reinterpret categories; apply each category's inclusion/exclusion criteria as
written. If a unit is attributable to a real two-sided mechanism but genuinely
matches no named category, that is "residual-other" — never the nearest
category as a fallback. If the mechanism cannot be pinned at all, take an
escape hatch (R1); the absence of a mechanism is not "residual-other".

C2 — Up to two secondary category ids, when a second (and third) distinct
mechanism is genuinely present and independently evidenced — not a restatement
of the primary. Secondary labels are category ids only (never escape hatches,
never a repeat of the primary); use [] when there is exactly one mechanism.

C3 — Evidence: at least one verbatim quote (source + quote + role), tied to the
chosen category's inclusion criteria, for any non-escape primary label. Escape
hatches may carry quotes explaining WHY attribution fails, but are not required
to.

C4 — Boundary calls. When two categories both plausibly apply as primary,
follow the codebook's boundary notes to choose, and name the runner-up category
in `notes`. Reserve `residual-other` for genuine non-matches, not for
hard-to-decide pairs (those get the better-fitting named primary + a secondary).

OUTPUT
Respond with a single JSON object conforming exactly to the provided schema.
`primary` is exactly one enum value (a category id, "residual-other", or an
escape hatch). `secondary` is a list of 0-2 category ids (C2), or []. `evidence`
holds the quotes (C3). `confidence` per R6. `notes`: the runner-up on a boundary
call (C4), alternatives considered and rejected, and — for an indeterminate
unit — what additional input would settle it.

## USER (per unit)

Identical to Phase 1 (`prompts_taxonomy/phase1_open_coding.md` ## USER),
rendered by `taxonomy_common.render_user` so the per-unit assembly is
byte-identical across phases (same files, same truncation ladder, same slots).
Reproduced verbatim for the record:

{PHASE1_USER}
"""


def build() -> str:
    return (HEADER
            .replace("{FROZEN_CODEBOOK}", frozen_instrument().rstrip("\n"))
            .replace("{PHASE1_USER}", phase1_user_block()))


def main() -> None:
    OUT.write_text(build())
    print(f"wrote {OUT.relative_to(ROOT)} ({len(build())} chars)")


if __name__ == "__main__":
    main()
