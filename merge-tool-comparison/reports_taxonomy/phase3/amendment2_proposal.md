# Proposed Amendment 2 — escape-hatch boundary clarification (G3 yellow band)

**Status:** DRAFT — awaiting Ali's ruling. Nothing applied; frozen artifacts untouched.
**Trigger:** G3 condition 1 (stability) returned **YELLOW** (protocol §7.G3.1).

## The stability result

Two independent closed-coding passes (p3a / p3b, `claude-opus-4-8`, identical
requests) over all 275 scored census units:

| metric | value | gate | pass? |
|---|---|---|---|
| exact primary agreement | **217/275 = 78.9%** [73.7, 83.3] | ≥ 80% | ❌ (−1.1 pt) |
| Cohen's κ | **0.741** | ≥ 0.70 | ✅ |
| disagreements | **58** | ≤ 60 | ✅ |

Point estimate 78.9% < 80% → **yellow band** per the pre-registered gate (the CI
covering 80% does not change the gate; pre-registration means no post-hoc
"close enough"). Yellow band ⇒ exactly one sanctioned codebook-clarification
amendment, then **both passes rerun** (§7.G3.1).

## Where the instability lives — it is NOT the mechanism taxonomy

The 58 disagreements decompose as:

| disagreement type | count | note |
|---|--:|---|
| `none-identified` ↔ `indeterminate` | **35** | both escape hatches; the dominant confusion (60%) |
| escape ↔ named category | 18 | one pass attributed, the other escaped |
| escape ↔ escape (other) | 2 | flaky-suspect vs another escape |
| **named category ↔ named category** | **3** | idiosyncratic one-offs (3 different pairs) |

The **named mechanism categories are essentially perfectly stable**: only 3 of
275 units flip between two named categories, and each is a distinct one-off
boundary call (`duplicate-concurrent-addition`/`overlapping-edit-interleaving`;
`stale-usage-of-pruned-import`/`stale-expectation-of-changed-behavior`;
`stale-reference-to-renamed-or-relocated-declaration`/`overlapping-edit-interleaving`)
— unavoidable residual noise, not a systematic ambiguity a rule could remove.
κ = 0.741 already clears its floor. **The scientific deliverable — the taxonomy of
attributable mechanisms — is reliable.** The sub-80% is driven almost entirely by
one under-specified boundary: which of the two "no-mechanism" escape hatches to
use.

## Why the two escapes are confused

Reading both passes' notes on the 35 flip units, they **agree on the substance**
every time — the two sides edit disjoint regions or are each self-consistent, the
merge composes cleanly, the compile delta is empty — and split only on the label:
one pass says *"no merge-induced mechanism"* (`none-identified`), the other says
*"a mechanism may exist but I can't establish it"* (`indeterminate`). The current
instrument (carried rule R1) defines both but gives no operational test to choose
between them, so a coder on the fence goes either way.

(Note: `merged == developer-resolution` is **not** a usable tie-breaker — it is the
normal case here, true in 144/275 units, and 36 of those carry real named-category
mechanisms. The developer's merge commit is itself the failing commit; Mergiraf
reproducing it exactly says nothing about whether a mechanism is present. R2 also
forbids leaning on the dev-diff. So the clarification below keys on the *visibility
of a cross-side interaction*, which is what actually separates the flip cases.)

## Proposed Amendment 2 (exact text to add to the instrument)

Added to the Phase-3 SYSTEM prefix as a clarification of rule R1 (escape hatches);
it does **not** invent, merge, split, rename, or redefine any named mechanism
category, and does not change the attributed-vs-escape threshold or any inclusion
criterion. It sharpens only the boundary *between the two no-mechanism escapes*:

> **R1 clarification — choosing between `none-identified` and `indeterminate`.**
> Both mean "no attributable merge mechanism"; they differ in *why*.
> - Use **`none-identified`** when the visible evidence is sufficient to conclude
>   the two sides do **not** interact destructively: they edit disjoint regions or
>   unrelated concerns; or each side's change is self-consistent and neither
>   depends on the other; or they touch the same area but compose with no cross-side
>   dependency. This is a positive finding of non-interaction — you cannot even name
>   a concrete candidate interaction between the two sides' changes.
> - Use **`indeterminate`** only when a mechanism plausibly **exists** but the
>   visible evidence cannot settle it: you can name a concrete candidate interaction
>   between the two sides (they touch the same state, signature, control path, or
>   region) whose correctness you cannot determine; **or** the relevant code is
>   demonstrably not fully visible (inputs truncated to T2/T3, intersecting files
>   dropped, or the cause plausibly lies in files not shown).
> - **Tie-breaker:** if you can articulate a specific candidate interaction between
>   the two sides, use `indeterminate` (or a named category if you can actually
>   attribute it); if you cannot even name a plausible interaction, use
>   `none-identified`. Do not choose `indeterminate` merely because certainty is
>   imperfect.

## Expected effect

Grounded, not guaranteed: 31 of the 35 `ni↔ind` flips (and several of the 18
escape↔category flips) are exactly the "disjoint / self-consistent, no nameable
interaction" shape the rule routes to `none-identified`. If the rerun resolves even
~half of the 35, agreement clears 80% comfortably (resolving 15 → ~84%, 25 → ~88%).
This is the one sanctioned shot; if the rerun still lands yellow/below, the
protocol path is a return to Phase 2 as a documented outcome.

## What happens on approval

1. Record this as **protocol §12 Amendment 2** (dated 2026-07-11), and add the R1
   clarification block to `prompts_taxonomy/phase3_closed_coding.md` (regenerated
   via the assembler) — the frozen **codebook** file and category **enum** are
   unchanged; only the escape-hatch decision rule in the prompt is clarified.
2. Per §9, the prompt change **invalidates the Phase-3 cache wholesale** →
   `raw_results_{a,b}.json` are archived and **both passes are resubmitted** as
   fresh batches on the amended instrument.
3. Re-run G3 stability on the new passes; if PASS, proceed to G3 condition 2
   (your reliability adjudication).

**No categories change. No base-rate definition changes. This is a one-time
clarification of the escape-hatch decision procedure, as the yellow band permits.**
