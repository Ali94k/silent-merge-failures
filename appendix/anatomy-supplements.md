# Appendix (candidate): anatomy supplements

Status: created by the ch.7 compression session and extended by the second pass (2026-09-10; A.1 ruled **appendix-candidate** 2026-09-11, and may move to repo-only if the appendix grows too large; source text verbatim from the chapter except the flagged pointer edits) · Every item is marked **appendix-candidate** or **repo-cite (recommended)**; final print-appendix curation is Ali's end-of-wave ruling · Appendix letter assigned at curation · Pointer edits applied to moved text: the ch.5 flatten retargets (§5.3.4 → §5.3, §5.4.x → §5.4, §5.3.2 → §4.1) — each flagged per item; no other wording changed · Narrative: none

**Honest accounting of what a demotion buys.** Moving words from the chapter into a printed appendix does **not** shrink the printed thesis; it only moves pages. Only a **repo-cite** demotion shrinks the printed thesis. Measured on the wave's counting metric, item by item:

- held in this file, remeasured 2026-09-12: **1,269 words** (A.1 835, A.2 254, A.3 103, A.5 77), plus Table T7.2's rows and caption, which the metric never charged to the chapter in the first place.
- **A.1 was ruled appendix-candidate on 2026-09-11**, so of that total only **A.5's 77 words** would leave the printed thesis under the current curation. The remaining 1,192 print, relocated rather than removed.
- that ruling is what keeps three things in print at all: the two-sidedness attribution rule, the escape-hatch rationale and the answer-key exclusion. The chapter's paragraph limits removed all three from §7.1, so A.1 is now their only home in the write-up. **If A.1 later moves to repo-only, they leave the thesis together**, and the chapter stops explaining its own instrument to a reader who does not follow pointers.
- one caveat on A.5: §7.6 states the four families and the ruling, so curating A.5 repo-only removes the two reasons behind the ruling, not the ruling itself.
- one caveat on the chapter-side figure: the chapter fell 6,870 → 4,630 in the first pass and 4,630 → 2,529 in the second, and only part of that is demotion. The rest is compression of text that stayed, less what the verification gates had to add back.

## A.1 The count's protocol rules and execution mechanics — appendix-candidate

Chapter home: §7.1 (which keeps the coverage design, the phases, the split and the pre-registration statement), §7.2 (the population, the strata and the unit of analysis) and §7.3 (the workload list and the rerun). The 2026-09-11 paragraph limits moved the escape-hatch rationale and the answer-key exclusion out of §7.1, so this item is now their only home in the write-up; Table T7.1 still glosses each hatch. Repo record: the committed run manifests, prompts, gate-scoring scripts, and the frozen protocol. Pointer edits flagged: "(§5.3.4)" → "(§5.3)", "(§5.5.4)" and "(§5.5.5)" dropped per rows R7–R9 of `ch5-retarget-map.md`, "(§5.3.2)" → "(§4.1)"; "the machine quote-provenance precheck of §7.1" → an in-item reference (second pass: the two-sentence incident dropped the precheck from §7.4.4, so no chapter section carries it and this item is its only home).

**The rules that discipline every label.** Two govern attribution. First, categories are mechanisms, never symptoms: two units share a category only when the same class of semantic interaction broke the program, however the breakage surfaced. Second, every mechanism claim is two-sided, constructible from the two sides' changes interacting. The strongest causal signal in the inputs is the diff between the merged file and the developer's own resolution, and a frozen prompt rule demotes exactly that signal to supporting evidence. "The developer did it differently" is not a mechanism. A coder anchored on the resolution would read the symptom backwards instead of constructing the interaction.

Closed coding gets three further safeguards.

- **Declining permitted** — the designed-against failure mode is confident invented causality, because a coder required to name a mechanism for every unit would invent one where none is visible. The three escape hatches of Table T7.1 are therefore first-class labels.
- **Frozen label set** — a fixed enum the passes may not extend, with a mandatory `residual-other` catch-all for any attributed unit the codebook cannot place.
- **Answer key excluded** — the frozen codebook document ends with a table listing every attributed derivation unit's category. The closed-coding prompt inlines the definitions and excludes that table, so neither pass can copy known labels instead of coding.
- **Verbatim evidence** — attributed labels require verbatim quotes from the unit's inputs. Open coding backed this rule with a machine precheck that re-locates every quote in the unit's actual input. Closed coding did not, and §7.4.4 reports the one consequence the audit could see.

**What the coder sees.** Each unit's bundle holds four things.

- **Both sides' diffs against base** — what ours changed and what theirs changed, shown separately.
- **The merged files, windowed** — long files as excerpts around the changed regions, short files whole.
- **A compile delta** — the errors the merged file produces that the developer's own file does not.
- **The diff against the developer's resolution** — demoted to supporting evidence by the rule above.

Preparation came in five parts.

- **Scenario rebuild** — stratum B was materialized with the same scenario-building machinery the detection baseline had used, and every scored unit's merged files were reproduced with the pinned Mergiraf image (§7.2).
- **Compile deltas** — the merged file and the developer's file each got a best-effort single-file compile, and only the errors unique to the merged file entered the input bundle. The frozen protocol's caveat is that single-file resolution errors are expected noise. The compiler runs under the container discipline of §4.1, in a pinned image (`eclipse-temurin:17-jdk`).
- **Input bundles** — long inputs are cut to a fixed per-unit token budget by the record's *truncation ladder*, a fixed ladder of progressively deeper cuts. Each unit's level is recorded, so §7.4.1 can check whether attribution depends on it, and every bundle was checked against the budget before submission.
- **The split** — committed before any model request containing unit content (§5.4).
- **The G0 pilot** — ten derivation units through the full assembly and prompt. It passed, and its outputs were discarded, as the gate requires (Table T7.4).

Three ordering checks back the chapter's pre-registration claims.

- **Machine-parsed open coding** — open coding ran as one batch, one request per derivation unit, against the committed prompt and JSON schema, so every response was machine-parsed. Batch results return unordered, keyed by a per-unit submission id, and a committed submission-time map ties each result back to its merge. A resumable cache stores the results, so a rerun submits only missing units. Every unit returned a conforming output.
- **Consolidation ordering** — the consolidation prompt was finalized and committed before any open-coding tags were read, so the git history shows the ordering (§5.4). The call itself was the program's one request outside the batch surface. It ran on the interactive API, and the run manifest records its model, like every model choice in the program (§5.3).
- **Byte-for-byte input revalidation** — before submission, the closed-coding runner revalidated every derivation unit's freshly assembled input byte-for-byte against the input committed during open coding, and would have aborted on any mismatch, under the machine-check discipline of §5.4.

Gate scoring used committed artifacts throughout. The machine quote-provenance precheck named above ran over the attributed drafts before G1 was scored; G1's two machine conditions were scored directly from the committed outputs, and its spot-check through a purpose-built offline review page (§5.3). A committed evaluation script scored G2's machine conditions, and my category-by-category rulings went through a review page of the same kind. The freeze commit fixed the codebook and the closed-coding label set together, and no closed-coding request existed before it. Closed coding ran as two passes, pass a and pass b, each submitted through the resumable cache so a missing unit could be topped up without resubmitting the rest. A committed script computed each stability reading, and the same script scored the rerun. My rulings went through the self-contained review page of §5.3, and the exported rulings are committed.

## A.2 The worked coding example — appendix-candidate

Chapter home: **Table T7.1**, which glosses each hatch, and appendix A.1, which states the designed-against failure mode. The 2026-09-11 paragraph limits removed the rationale from §7.1's prose; §7.1 still points here for the worked examples, which cover the attributed case and all three hatches. Pointer edits flagged: none.

A worked example fixes the coding decision. Suppose ours deletes `import java.util.Optional;` as dead-import cleanup, correct against its own version of the file. Theirs adds a method that uses `Optional`. The merge composes both edits cleanly: the import is gone and the new use is present. This is the same shape the D1 lane of §4.4.3 targets. The repetition is deliberate: §7.6 reports that this category leads the count and that lane D1 targets it. The coder quotes the deletion from ours' diff, the new use from theirs' diff, and the dangling name in the merged file. The unit is *attributed*: its primary label names a mechanism category, here `stale-usage-of-pruned-import` (Table T7.1).

Now suppose instead that the two sides edit disjoint methods, share no names or state, and the merged file compiles. No cross-side interaction is articulable. The unit takes `none-identified`, which is a positive finding of non-interaction, not a failed attribution. If a candidate interaction is nameable but cannot be settled from the shown code, or the code that would settle it sits outside the shown files, the unit takes `indeterminate`.

The third hatch concerns the test signal itself. Some failures are environmental or nondeterministic: timing, network, ports, wall-clock dates, random seeds, resource limits. When the plausible cause is of that kind and not a semantic property of the merged code, the unit takes `flaky-suspect`. The dataset records one pass-or-fail test outcome for the whole merge (§7.2), so a nondeterministic test can fail at the merge commit without the merged code being wrong.

## A.3 The escape-boundary case that split the passes — appendix-candidate

Chapter home: §7.4.4 (the chapter keeps the finding that the instability sat on the escape boundary, and states Amendment 2's rule). Pointer edits flagged: none.

A schematic case shows the boundary that split the passes. Suppose ours edits a parser method, theirs edits a formatter method elsewhere in the file, the diffs share no names, and the merged file compiles. One pass answers `none-identified`, because nothing connects the sides. The other pass notices that both methods read the same buffer field, names that as a candidate interaction, cannot settle it from the shown code, and answers `indeterminate`. Before the amendment, both answers were defensible, and units of this kind split the passes. Under Amendment 2's rule, the schematic unit above takes `indeterminate`, because its candidate interaction is nameable.

## A.4 Table T7.2 — per-category counts and shares — appendix-candidate

Chapter home: §7.4.1 (which states the attributed fraction, the empty catch-all, and the two leading categories, and cites this table). Pre-named on Ali's print-appendix shortlist. Pointer edits flagged: none.

| Category (frozen id) | Family (Table T7.1) | Stratum A (n = 164) | Stratum B (n = 111) | Pooled (n = 275) | Share [Wilson 95%] |
|---|---|--:|--:|--:|---|
| `stale-usage-of-pruned-import` | name-binding | 22 | 13 | 35 | 12.7% [9.3, 17.2] |
| `stale-reference-to-removed-declaration` | name-binding | 4 | 2 | 6 | 2.2% [1.0, 4.7] |
| `stale-reference-to-renamed-or-relocated-declaration` | name-binding | 8 | 8 | 16 | 5.8% [3.6, 9.2] |
| `stale-caller-of-changed-signature` | name-binding | 17 | 11 | 28 | 10.2% [7.1, 14.3] |
| `stale-expectation-of-changed-behavior` | behavioral expectation | 3 | 4 | 7 | 2.5% [1.2, 5.2] |
| `overlapping-edit-interleaving` | tool composition artifact | 11 | 7 | 18 | 6.5% [4.2, 10.1] |
| `insertion-anchored-to-relocated-code` | tool composition artifact | 1 | 2 | 3 | 1.1% [0.4, 3.2] |
| `duplicate-concurrent-addition` | concurrent addition | 5 | 1 | 6 | 2.2% [1.0, 4.7] |
| `residual-other` | catch-all | 0 | 0 | 0 | 0.0% [0.0, 1.4] |
| **attributed subtotal** | | **71** | **48** | **119** | **43.3% [37.5, 49.2]** |
| `none-identified` | escape hatch | 57 | 31 | 88 | 32.0% [26.8, 37.7] |
| `indeterminate` | escape hatch | 34 | 32 | 66 | 24.0% [19.3, 29.4] |
| `flaky-suspect` | escape hatch | 2 | 0 | 2 | 0.7% [0.2, 2.6] |
| **escape subtotal** | | **93** | **63** | **156** | **56.7% [50.8, 62.5]** |
| **total** | | **164** | **111** | **275** | 100% |

*Table T7.2 — per-category counts and shares of the scored population, by size stratum and pooled, with Wilson 95% intervals; families per Table T7.1. Counts and intervals are the frozen full-count record's.* [PerCategoryCounts]

## A.5 The four-family regrouping assessment — repo-cite (recommended)

Chapter home: §7.6, whose prose states the four families and my ruling. The second pass moved the two reasons behind that ruling here, so this item now carries them rather than duplicating them. Repo record: the consolidation-phase written analysis required by gate G2, in `reports_taxonomy/`.

The four-family view groups mechanisms into state, control-flow, data-flow, and name-binding families. It was assessed against the empirical categories when the codebook was consolidated (§7.6). Two reasons decided my ruling. The regrouping would put roughly three quarters of the attributed mass into one family (§7.4.2), and it would split the tool-composition categories, which are defined by how the tool combined edits rather than by where the damage lands. The four-family view remains a descriptive axis.

## Claims used

- PerCategoryCounts
