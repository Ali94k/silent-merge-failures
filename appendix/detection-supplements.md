# Detection supplements

Appendix items of the thesis that are published here rather than printed (end-game step 3, applying the classification ruled 2026-09-13). Each item opens with its printed home, or states that it has none. `§n.m` names a section of the printed thesis and `Table Tn.m` one of its tables; `D-nnn` is an entry of `docs/DECISIONS.md`; a bracketed tag such as `[TierTrajectories]` is a row of `thesis/claims-ledger.md`, listed under *Claims used* at the end of the file. Item identifiers are the ones the working files carried, so an identifier is unambiguous only together with its file name; the printed appendices number their own items (A.1–A.3, B.1–B.2, C.1–C.2), and every printed pointer to this repository names the file.

## B.1 The detector cycle's numeric gate criteria

Printed home: §8.1, which states the gates in one clause and cites the pre-registered criteria; the record is `outputs/detector-cycle-plan.md` §5 and `reports_detectors/FINDINGS.md`.

- **GD1** — machine-readable specs for at least 80% of the target-category derivation units, at least 5 concrete D3 gap shapes, and both control lists committed.
- **GD2** — per build session: unit tests and the full driver suite green, the fixture battery passing, and 0 flags on the 100 tune-controls.
- **GD3** — on the frozen suite, two arms: 0 flags on the 200 eval-controls and on the 66 external labeled-clean units.
- **GD4** — every held-out flag ruled, with no numeric floor.

## B.2 The baseline repair's four defects

Printed home: §8.4.2; the record is `reports_detection/postfix{,2}/`. The fixes went into two separately labeled post-fix runs, not into the frozen suite: the first two defects are the mid-run finds left in place under the freeze, the last two the gaps the first post-fix run surfaced.

- **Missing call-site exclusion** — the variable scan matched a surviving *method* of the renamed variable's name; variables are never callable in Java, so a match followed by a parenthesis should have been skipped.
- **Comment-stripper line-crossing** — a character-literal pattern consumed across newlines on apostrophes inside comments, corrupting the stripped text that the declaration guard reads.
- **Generics wildcard** — a wildcard missing from the guard's type pattern.
- **Lambda parameters** — parameters invisible to the guard.

## B.3 The tcurdt re-ruling

Printed home: §8.4.2, which keeps the verdict and the retirement.

The repair also showed one of the frozen run's positive flags to be defect-dependent, and the record keeps that. The flag sits on the tcurdt repository's merge. The flagged name's only occurrence in the merged file is a method call on a live parameter, exactly the site the missing call-site exclusion should have skipped. Nothing in the file is stale, and it compiles. The merge is a real silent failure, and the flag's claim about the merged file is false. The first post-fix run retired the flag. At that time the causal ruling was left standing for the frozen run. On the later re-read I re-ruled it `DETECTOR-FP`. The post-fix positive side is otherwise unchanged, verified per file.

## B.4 The atam4j re-ruling

Printed home: §8.4.2, which keeps the verdict, and §8.4.8, which keeps the cross-file false negative.

I made both re-rulings on the later re-read of the ruling record. The second has no connection to the repair. That flag sits on the atam4j repository's merge. It does not depend on either repaired defect, and it stays flagged after the repair: the rename detector's caller scan has no declaration guard, and that gap was never fixed. The flagged line is the surviving declaration of the renamed method. Both the old and the new name are declared, the three callers resolve, and the file compiles. The flag's claim about the merged file is false, and I re-ruled it `DETECTOR-FP`. The merge failed for a merge-induced reason, but in a sibling file of the same merge: a class is used there without an import. All five default strategies scored that sibling file clean. That is a measured cross-file false negative on the baseline's own scored files (§8.4.8).

## B.5 The external run's deployment view

Printed home: §8.4.3, whose prose carries the oracle-faithful values; the record is `reports_detection/phase2b/FINDINGS.md`.

The deployment view adds one fact of its own. Re-merged with the pinned backbone, two of the 17 positives stop being silent [ExternalDeploymentView]: they surface as textual conflicts, so a deployed driver would hand them to the developer rather than accept them. Ten of the 66 controls surface the same way [ExternalDeploymentView]. The view's detector scores match the oracle-faithful view's zeros: 0 of the 15 positives and 0 of the 56 controls that stay silent [ExternalDeploymentView].

## B.6 The worked example: D1's guard walk

Printed home: §8.4.4, which keeps the outcome and the ruling.

The unit is a large class file from a major open-source project, and the scored artifact is the developer's own shipped merge, the artifact the benchmark labels. D1, the pruned-import lane, compares the import sets differentially: the union of the two sides' imports, minus the merged file's. Both sides hold an import of a settings type. The merged file has lost it. That loss makes the type a candidate, and the merged file still uses the name, unqualified, at many sites: 8 code uses, and 34 occurrences counting Javadoc [ControlFlagExamples]. The flag is raised only if every guard stays silent (§4.4.3).

- *Wildcard* — no non-static wildcard import survives in the file; when one does, the lane abstains on every type-name candidate, whatever the wildcard's package (§8.4.8).
- *`java.lang`* — the name is not one that needs no import.
- *Same package* — the type is not from the file's own package.
- *Shadowing* — no local declaration shadows the name.
- *Absorption* — neither side used the name without the import, so the breakage, if real, is merge-induced.

Every guard passed, and D1 flagged the developer's own merge on a corpus curated as clean. My ruling followed the standing test of §5.3: the claim is about the scored artifact, and the artifact is genuinely broken. The benchmark's label attests behavioral non-interference, not compile-cleanliness. The project's own history later agreed with the ruling. The developer's next commit restores exactly the dropped imports, with a commit message blaming the merge. Under gate GD3 a ruling of `INCIDENTAL-BUT-TRUE` is recorded and the gate is re-judged, so I re-judged it passed, with the finding kept in the record.

## B.7 Per-detector held-out prose

Printed home: §8.4.5, which keeps the headline and D1's cells; the per-detector record is `reports_detectors/FINDINGS.md`.

- **D1, the pruned-import lane, carries nearly all of the added recall.** It caught 11 of its own category's 12 held-out units, an own-category recall of 91.7% [64.6, 98.5] [DOneCells]. Its unit precision is 12 of 12 [DOneCells]. It also caught one unit outside its category: a library-migration case whose relocation breakage was visible in the import comparison. Its target category is the full count's largest (§7.4.1), so this is the payoff the retargeting was aimed at. (§8.4.4's worked example traced the lane's guards one by one.)
- **D2, the signature lane, measured zero.** It flagged nothing held-out, including none of its own category's 14 units: 0 of 14 [0, 21.5] [DTwoCeiling]. Why the zero was expected is visible in the lane's derivation evidence, cited as design context only. Five of its derivation units break across files, out of a file-local lane's reach by construction [DTwoCeiling]. Four others change a signature without changing arity, the documented miss of its conservative design [DTwoCeiling] (§4.4.3). The category is the full count's second-largest (§7.4.1), so this ceiling is a real coverage loss, not a rounding error. Its fixture battery and its clean control record stand. Its measured held-out recall is zero.
- **D3, the widened declaration differential, added nothing on held-out data.** Its held-out added value is zero causal catches and one false positive [DThreeWidening]: a unit where one side extracted a class to a same-package file the file-local view cannot see. On its own derivation units the widened path had flagged seven [DThreeWidening], but those are the shapes it was built from, tuning-tainted by definition, and the held-out result is the citable one. The same-package shape is now the D1/D3 lane pair's measured residual false-positive class: 2 occurrences across the 20 flagged files of the 18 citable flagged units, one of them a sub-flag inside a unit that stays causal [DThreeWidening].
- **The two default name-binding strategies carry the flag-off catches.** On held-out data the rename detector's flags were 3 of 4 causal and the declaration differential's default path 3 of 3 [PerLaneHeldOut]. Neither strategy is touched by the counting ruling of §8.2, which removed D1 catches only [PerLaneHeldOut].

## B.8 The baseline rerun's split breakdown

Printed home: §8.4.6; the record is `reports_detectors/` §10.

The rise is not confined to the lanes' own design units: the blocked share rose on both the derivation portion and the held-out portion of the positives. On the 98 derivation units it rose from 7 to 22 blocked, a tuning-tainted reading, and on the 66 held-out units from 4 to 14 [BaselineRerunDetail].

## B.9 The lanes' latency components

Printed home: §8.4.7; the record is `reports_detectors/` §11.

The added latency is uniform across the positive and control sides and across both routes. Three components account for it.

- *D2, the signature lane* — its per-side classifier invocations dominate the added time.
- *D1, the pruned-import lane* — text-only.
- *D3, the widened differential* — reuses an existing pass.

## B.10 The five recall ceilings, full statements

Printed home: §8.4.8, which prints each ceiling in compressed form (the wildcard bullet's closing sentence appears in both).

- **Cross-file shapes.** Every strategy and lane is file-local by construction. Failures that break across files sit fully inside the recall denominators of §8.4.5 and out of reach. A measured share of D2's own category breaks this way (§8.4.5). The baseline carries one measured instance of its own. It came from the re-read of a flagged merge's files, not from any scan of the unflagged positives. In the atam4j merge of §8.4.2 the break sits in a sibling file that no default strategy flagged, while the flagged file compiles. That is a cross-file false negative on the baseline's own scored files. The unflagged positives were not re-read, so one instance is a lower bound, not a count. Whether a cross-file view can be added without giving up the zero-false-positive record is an open question (Chapter 12).
- **Same-arity signature changes.** A signature change that keeps its argument count is invisible to D2's conservative arity signal, by documented design (§4.4.3). Closing this needs type resolution, which was built, measured as unreliable on single files, and dropped (§4.4.3).
- **Reassignment-shape stale reads.** The category-#3 strategy's literal-shape limit is now a measured false negative on the external benchmark (§8.4.3), not merely a documented caveat.
- **Same-package resolution.** The D1/D3 lanes cannot see a declaration that moved to another file of the same package. The shape is the lane pair's measured residual false-positive class (§8.4.5) and a recall blind spot at once.
- **Wildcard imports.** The D1 lane abstains on every type-name candidate whenever any non-static wildcard import survives in the merged file, whatever package it names. The guard is broader than the case it protects against. D1's one own-category held-out miss is exactly that guard (§8.4.5).

## Claims used

- BaselineRerunDetail
- ControlFlagExamples
- DOneCells
- DThreeWidening
- DTwoCeiling
- ExternalDeploymentView
- PerLaneHeldOut
