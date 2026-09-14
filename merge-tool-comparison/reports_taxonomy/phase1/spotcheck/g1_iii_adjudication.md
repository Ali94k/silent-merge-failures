# G1 condition (iii) — Ali spot-check adjudication

**Ruled by Ali, 2026-07-10.** ISSUES #30 S2. Protocol [`outputs/taxonomy-protocol.md`](../../../../outputs/taxonomy-protocol.md) §7 condition (iii).

Instrument: `spotcheck_ui.html` (seeded draw 20260709, 5 high / 5 medium / 5 low-or-escape). Rulings: `spotcheck_rulings.csv`.

## Rulings

| # | draft | bucket | verdict | ruling | reason |
|---|---|---|---|---|---|
| 1 | jacquesberger_jsonparsingexample | high | attributed | ACCEPT | |
| 2 | kaazing_robot | high | attributed | ACCEPT | |
| 3 | jdupl_lancoder | high | attributed | ACCEPT | |
| 4 | sandergielisse_enderstone | high | attributed | ACCEPT | |
| 5 | jline_jline2 | high | attributed | ACCEPT | |
| 6 | segmentio_analytics-java | medium | attributed | ACCEPT | |
| 7 | jmetal_jmetal | medium | attributed | ACCEPT | |
| 8 | mercadopago_sdk-java | medium | attributed | ACCEPT | |
| 9 | cternes_openkeepass | medium | attributed | ACCEPT | |
| 10 | movsim_movsim | medium | attributed | ACCEPT | |
| 11 | glowroot_glowroot | low_or_escape | indeterminate | REJECT-UNSUPPORTED | "not a good representation of the silent merge conflicts" |
| 12 | j256_ormlite-core | low_or_escape | indeterminate | REJECT-UNSUPPORTED | "not a good representation of the silent merge conflicts" |
| 13 | garbagemule_mobarena | low_or_escape | none-identified | REJECT-UNSUPPORTED | "not a good representation of the silent merge conflicts" |
| 14 | javaparser_javaparser | low_or_escape | indeterminate | REJECT-UNSUPPORTED | "not a good representation of the silent merge conflicts" |
| 15 | jdeparser_jdeparser2 | low_or_escape | indeterminate | ACCEPT | |

Raw tally: **11 ACCEPT, 4 REJECT-UNSUPPORTED.**

## Scoring adjudication (marked decision)

The pre-registered gate (§7 iii) reads: *"Pass: ≤ 3/15 rejected **as hallucinated or unsupported-by-quotes**."* The rejection reason is part of the criterion, so the gate is scored **by qualifying rejections**, not by raw button clicks.

All 4 rejections are **escape-hatch verdicts** (3 `indeterminate` + 1 `none-identified`) — the model claimed **no** mechanism for any of them, so there is no causal story to be hallucinated or unsupported-by-quotes. The stated reason — *"not a good representation of the silent merge conflicts"* — is a **population/selection** objection that in fact **agrees** with the model's escape-hatch call; it is not the labeling-quality failure the gate targets. Meanwhile **0 of the 11 mechanism-claiming drafts** (10 attributed + 1 accepted escape) were rejected — the confident-hallucinated-causality failure mode the gate exists to catch **did not fire**.

**Ali's ruling (2026-07-10):** score criterion-scoped → **0/15 qualifying rejections → condition (iii) PASS.** A full Phase-1 rerun (the literal-fail remedy) would only reproduce the same correctly-taken escape-hatches and is not warranted.

This is an **application of the gate as written** (the criterion already scopes rejections by reason), ruled by Ali — not a change to the gate, so no §12 amendment is required. Recorded here in full for pre-registration transparency; the raw button count (4) is preserved above and not hidden.

## G1 verdict

- (i) attribution floor: **PASS** (60/165 = 36.4% ≥ 35%)
- (ii) escape-hatch band: **PASS** (105/165 = 63.6% ∈ [15%, 65%])
- (iii) Ali spot-check: **PASS** (criterion-scoped; 0 qualifying rejections)
- **G1 overall: PASS** → S3 (Phase-2 consolidation) proceeds.

## Population concern — carried to Phase-2 (marked)

Ali's "not a good representation" objection on 4/5 escape-bucket drafts is a **first-class signal about the population**, not a labeling defect: a substantial share of the frozen `mergiraf == Tests_failed` census is **not cleanly attributable to a merge-induced mechanism** from the shown files (the measured escape-hatch fraction is **63.6% [56.1, 70.6]**). Phase-2 and FINDINGS must foreground this — treat `indeterminate` / `none-identified` / `flaky-suspect` as a reported "not-cleanly-merge-attributable" stratum in the honest-coverage accounting, and note the threat that the whole-merge `Tests_failed` label admits failures whose cause sits outside the intersecting files or is nondeterministic. This does **not** reopen the frozen §2 population; it is guidance for how the escape-hatch mass is framed downstream.
