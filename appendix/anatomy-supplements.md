# Anatomy supplements

Appendix items of the thesis that are published here rather than printed (end-game step 3, applying the classification ruled 2026-09-13). Each item opens with its printed home, or states that it has none. `§n.m` names a section of the printed thesis and `Table Tn.m` one of its tables; `D-nnn` is an entry of `docs/DECISIONS.md`; a bracketed tag such as `[TierTrajectories]` is a row of `thesis/claims-ledger.md`, listed under *Claims used* at the end of the file. Item identifiers are the ones the working files carried, so an identifier is unambiguous only together with its file name; the printed appendices number their own items (A.1–A.3, B.1–B.2, C.1–C.2), and every printed pointer to this repository names the file.

## A.1 The count's protocol rules and execution mechanics

Printed home: §7.1 (the coverage design, the phases, the split and the pre-registration statement), §7.2 (the population, the strata and the unit of analysis) and §7.3 (the workload and the rerun); the printed Appendix B.1 summarizes this item.

**The rules that discipline every label.** Two govern attribution. First, categories are mechanisms, never symptoms: two units share a category only when the same class of semantic interaction broke the program, however the breakage surfaced. Second, every mechanism claim is two-sided, constructible from the two sides' changes interacting. The strongest causal signal in the inputs is the diff between the merged file and the developer's own resolution, and a frozen prompt rule demotes exactly that signal to supporting evidence. "The developer did it differently" is not a mechanism. A coder anchored on the resolution would read the symptom backwards instead of constructing the interaction.

Closed coding gets four further safeguards.

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

## A.2 The worked coding example

Printed home: §7.1, which points here for the worked examples, and Table T7.1, which glosses each hatch.

A worked example fixes the coding decision. Suppose ours deletes `import java.util.Optional;` as dead-import cleanup, correct against its own version of the file. Theirs adds a method that uses `Optional`. The merge composes both edits cleanly: the import is gone and the new use is present. This is the same shape the D1 lane of §4.4.3 targets. The repetition is deliberate: §7.6 reports that this category leads the count and that lane D1 targets it. The coder quotes the deletion from ours' diff, the new use from theirs' diff, and the dangling name in the merged file. The unit is *attributed*: its primary label names a mechanism category, here `stale-usage-of-pruned-import` (Table T7.1).

Now suppose instead that the two sides edit disjoint methods, share no names or state, and the merged file compiles. No cross-side interaction is articulable. The unit takes `none-identified`, which is a positive finding of non-interaction, not a failed attribution. If a candidate interaction is nameable but cannot be settled from the shown code, or the code that would settle it sits outside the shown files, the unit takes `indeterminate`.

The third hatch concerns the test signal itself. Some failures are environmental or nondeterministic: timing, network, ports, wall-clock dates, random seeds, resource limits. When the plausible cause is of that kind and not a semantic property of the merged code, the unit takes `flaky-suspect`. The dataset records one pass-or-fail test outcome for the whole merge (§7.2), so a nondeterministic test can fail at the merge commit without the merged code being wrong.

## A.3 The escape-boundary case that split the passes

Printed home: §7.4.4, which states the finding and Amendment 2's rule.

A schematic case shows the boundary that split the passes. Suppose ours edits a parser method, theirs edits a formatter method elsewhere in the file, the diffs share no names, and the merged file compiles. One pass answers `none-identified`, because nothing connects the sides. The other pass notices that both methods read the same buffer field, names that as a candidate interaction, cannot settle it from the shown code, and answers `indeterminate`. Before the amendment, both answers were defensible, and units of this kind split the passes. Under Amendment 2's rule, the schematic unit above takes `indeterminate`, because its candidate interaction is nameable.

## A.5 The four-family regrouping assessment

Printed home: §7.6, which states the four families and the ruling; the consolidation-phase written analysis required by gate G2 is in `reports_taxonomy/`.

The four-family view groups mechanisms into state, control-flow, data-flow, and name-binding families. It was assessed against the empirical categories when the codebook was consolidated (§7.6). Two reasons decided my ruling. The regrouping would put roughly three quarters of the attributed mass into one family (§7.4.2), and it would split the tool-composition categories, which are defined by how the tool combined edits rather than by where the damage lands. The four-family view remains a descriptive axis.

## Claims used

None. The items carry citations but no ledger-tagged value.
