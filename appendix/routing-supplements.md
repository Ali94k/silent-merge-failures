# Routing supplements

Appendix items of the thesis that are published here rather than printed (end-game step 3, applying the classification ruled 2026-09-13). Each item opens with its printed home, or states that it has none. `§n.m` names a section of the printed thesis and `Table Tn.m` one of its tables; `D-nnn` is an entry of `docs/DECISIONS.md`; a bracketed tag such as `[TierTrajectories]` is a row of `thesis/claims-ledger.md`, listed under *Claims used* at the end of the file. Item identifiers are the ones the working files carried, so an identifier is unambiguous only together with its file name; the printed appendices number their own items (A.1–A.3, B.1–B.2, C.1–C.2), and every printed pointer to this repository names the file.

## C.1 The arms' rationale and the worked dispatch example

Printed home: §6.1, which states each arm's cluster, its specialist, its unit of composition and its gate criterion; the comparative form of each hypothesis survives only here.

**The hypothesis in full.** The routing hypothesis behind the dispatch layer is intuitive. No single merge tool is strongest on every input shape. A classifier that predicts each merge's difficulty should therefore be able to dispatch every merge to the tool best suited for merges of its kind. The idea has precedent in JDime's auto-tuning, which escalates from cheap line-based merge to expensive structured merge exactly where text conflicts (§2.2). [CITE: apel2012autotuning]

In Chapter 2 I promised that this chapter would measure that principle's limits at whole-tool granularity, not to question the principle itself.

**Units of composition.** I instantiated the hypothesis in two arms. The pairing logic behind both is the same, and I fixed it in the integration plans before any per-cluster measurement existed. Each backend merges at a characteristic unit of composition (§2.2).

- *git merge-file* — composes lines.
- *Mergiraf* — composes AST subtrees.
- *Spork* — composes a full Java AST down to sub-method granularity.
- *Weave* — composes whole declarations.

Each cluster of Table T4.1 names a failure shape for a line-based merger. An arm pairs a cluster's failure shape with the specialist whose unit of composition matches it.

**The method-body specialist hypothesis** claims that Java merges in the `INTRA_BODY` cluster merge better under Spork. That cluster's failure shape is sub-method restructuring: overlapping edits confined inside one method body, exactly where a line-based merger reports the whole region as a conflict. The plan's stated ground is granularity. Spork parses Java into Spoon ASTs, and my mapping ranked Spoon's sub-method structure finer than the tree-sitter grammars behind the backbone. That comparison was asserted in my mapping and never measured. [CITE: larsen2023spork]

**The declaration-migration specialist hypothesis** claims that merges in the `MIGRATE_DECL` cluster merge better under Weave. That cluster's failure shape is whole-declaration relocation: a declaration moves or is extracted across containers, and line merge sees only a deletion and an insertion it cannot reconcile. The plan states the mechanism: when both branches extract methods independently, the backbone's subtree matching can raise spurious conflicts from spatial proximity, while an entity-level merger should follow the moved declaration and compose declarations as unordered units. Composing declarations as unordered units has precedent in semistructured merge (§2.2). [CITE: apel2011semistructured]

**The worked dispatch example.** A schematic example traces the mechanism once. Take a merge where ours extracts a local variable inside a method and theirs inverts a condition in the same method. The dispatcher runs RM2 on (base, ours) and on (base, theirs). Both reported refactoring types map to `INTRA_BODY`, so the merge is assigned that cluster. Under the pre-flip map with the arms live, the dispatcher sends this Java merge to Spork. Spork performs the three-way merge at AST level. If it reports a clean result, the verification layer still runs, and the merge is accepted only when every strategy is clean (Figure F4.1). Whether Spork's clean results on this cluster deserve that trust is exactly what the method-body gate measures. Under the post-flip map, the same merge goes to Mergiraf. A merge with no detected refactoring on either side would instead classify as `NONE` and take the fast path to git-merge-file.

## C.2 The mapping document's history

Printed home: §6.1, which keeps the provenance fact itself (I built the pairing myself, using a separate AI analysis tool, and recorded it in a dated mapping document; Chapter 9 accounts for the AI assistance); the record is the archived mapping document in `docs/historical/` and the committed integration plans that reference it.

I had built the pairing itself earlier, before the plans existed, using a separate AI analysis tool: it mapped the refactoring clusters onto the candidate merge tools by algorithmic paradigm, and I recorded the result in a dated mapping document. Chapter 9 accounts for this AI assistance along with the rest of the thesis's AI use. A mapping produced this way is a conjecture, not evidence. I therefore adopted my own mapping's pairings as hypotheses to confirm or refute, not as settled truth. The integration plan states the discipline in its own words: wiring a route without evidence would be "adding a tool because it seems nice", the move this thesis argues against.

In Chapter 3 I kept both tools selectable as unproven specialists. Neither arm rested on a measured weakness of the backbone: no comparator measurement of Mergiraf existed when I planned the arms. I ruled the one early per-cluster signal in Spork's favor suggestive only. The counts were far too small to carry a routing decision.

## C.3 The tools' own records, read after the verdicts

Printed home: §6.5, which states the two findings behind the verdicts; the tools'-own-records reading and its three citations survive only here.

The tools' own records, read after the verdicts, support the same conclusion. Spork's paper claims formatting preservation and fewer conflicts than other structured tools. It does not claim strength on edits inside method bodies. For the conflict shapes such edits produce, the paper describes a fallback: Spork merges the affected region line by line. [CITE: larsen2023spork]

Weave's own documentation contradicts the declaration-migration arm's assumption the same way. Weave identifies an entity by its name, its kind, and its enclosing scope. A declaration migrated across containers changes its scope, so it takes a new identity. The tool then sees a deletion plus an addition, not a move. The semistructured-merge literature had measured that misreading for renamed declarations years earlier. The capability the arm attributed to Weave is absent from Weave's own record. [CITE: weave] [CITE: cavalcanti2017evaluating]

These readings share a pattern. My mapping chose tools by two properties: how a tool represents code, and what unit it composes. The gates showed that behavior on hard merges depends on two other properties: how a tool matches elements across versions, and what it does when they conflict. Spork represents statements in full detail, and still merges them line by line when they conflict. Weave composes whole declarations, and loses track of a declaration when it moves. The hypotheses were reasonable at the time. The specialist tools' own evaluations, surveyed in §2.6, reported gains on refactoring-bearing merges. But each arm assumed a capability that its tool's own record does not claim, and a closer reading of the primary sources could have raised this before any gate ran. I record that as a lesson for building hypotheses, next to the oracle artifact of the second finding. A future routing hypothesis should start from how tools match and resolve conflicts, not from how they represent code.

## C.4 The whole-driver runs' scoring detail

Printed home: §6.4.4, whose prose carries the shared-oracle rule, and Table T6.4's caption, which carries the deltas-only rule; the routing-verification statement survives only here and in the record, `merge-tool-comparison/reports_whole_driver/FINDINGS.md`.

The pre-flip run executed the router with both specialist arms live, before any route had changed. The run's logs verify the routing as genuine: for every file, the backend the dispatcher chose was the backend that actually ran, with no crash fallbacks.

I read these counts under the whole-driver runs' hybrid oracle (T5.2), whose fallback for outputs that diverge from the Mergiraf reference is canonicalized dev-match. Dev-match over-counts wrong output, so false-positive counts on divergent outputs are upper bounds. Both sides of every comparison here are scored under the same oracle, so the over-count inflates both sides equally and the comparisons stand.

## C.5 The method-body gate's two-layer pre-registration

Printed home: §6.1, which states both gate criteria and that the method-body gate's second requirement was committed before the decisive run; the two-layer history survives only here.

The two gates have different pre-registration histories. I disclose the difference rather than hide it. I fixed the declaration-migration gate in the Weave integration plan at planning time, weeks before the arm was wired. It stayed unread until its dedicated run.

The method-body gate has two layers. The integration plan carried a retention criterion from before any sample existed: Spork had to beat Mergiraf with non-overlapping intervals, or the route would revert. Two small early samples then contradicted the arm. Those samples were selection-biased. So, as they arrived, I fixed a further evidence bar in the issue record: the route could change only on a cluster-stratified sample with Wilson intervals. I committed both layers before the decisive run (§5.4).

## Claims used

None. The items carry citations but no ledger-tagged value.
