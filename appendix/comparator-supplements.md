# Comparator supplements

Appendix items of the thesis that are published here rather than printed (end-game step 3, applying the classification ruled 2026-09-13). Each item opens with its printed home, or states that it has none. `§n.m` names a section of the printed thesis and `Table Tn.m` one of its tables; `D-nnn` is an entry of `docs/DECISIONS.md`; a bracketed tag such as `[TierTrajectories]` is a row of `thesis/claims-ledger.md`, listed under *Claims used* at the end of the file. Item identifiers are the ones the working files carried, so an identifier is unambiguous only together with its file name; the printed appendices number their own items (A.1–A.3, B.1–B.2, C.1–C.2), and every printed pointer to this repository names the file.

## A.1 The naive-FP bucket diagnostic

Printed home: §3.2, which keeps the claim and its tag; the record is `docs/plans/stage-gamma-fp-diagnostic.md` §2–3.

The first diagnostic pass bucketed Spork's 42 naive false positives by mechanical shape: 39 structural, 1 whitespace-only, 2 imports-plus-whitespace [SporkFPBuckets]. The initial manual inspection that read the structural bucket as pure reformatting covered 3 size-stratified diffs. That inspection is what motivated trying the formatter roundtrip first, and it is what failed to generalize.

## A.2 The stratified labelling sample's recurring patterns

Printed home: §3.2, which keeps the pass, its finding, its tag and its attribution; the record is `docs/plans/stage-gamma-fp-diagnostic.md`, ISSUES #2 and commit `caf33e2`.

The second diagnostic pass drew residual cases across file-size quintiles, 3 per quintile, and labelled each from its raw, pre-formatter diff. All 15 were ruled AST-equivalent reformatting [StratifiedLabelling]. The recurring patterns in that sample were extra parentheses around casts, fully-qualified names expanded from `java.lang`, comment placement, and `} else { if }` restructuring. The AI assistant performed the pass. I ruled the attribution on 2026-08-06 (D-212), and Chapter 9 records it.

## A.5 The three re-diagnoses' findings

Printed home: none; the second compression pass deleted the re-diagnosis sentence. The record is `merge-tool-comparison/ISSUES.md` #2 and `docs/plans/comparator-3b-ast-normalize.md`.

- **Re-diagnosis one, after the formatter tier recovered almost nothing.** It triggered the stratified re-annotation of A.2.
- **Re-diagnosis two, mandated when Tier C's recovery fired the pause threshold.** It produced the cycle's key methodological finding: the residual diff *after* formatter normalization is dominated by different patterns than the raw diff that was annotated. "AST-equivalent" does not imply "recoverable by any particular transform set".
- **Re-diagnosis three, on the residuals left after Tier D.** It found that Tier D's block-unwrap transform carried an identity-comparison defect that had been corrupting its interaction with the token fold. It also found that the dominant residual patterns again differed from what the plan brief expected. Tier E carries the fix.

## A.6 Mastery's movement under the pipeline

Printed home: §3.4.2, which keeps the discrimination claim and the unmoved core, and Table T3.2's Mastery row, which points here.

The bulk of Mastery's movement arrived at Tier D, when the token fold began closing comment-only cases. The project's records call that movement a surprise. The last arrivals came at Tier E: a comment-only case revealed by the block-unwrap bug fix, and a single array-initializer trailing-comma case, which is the one non-comment recovery. File headers and Javadoc blocks count as comments for this purpose. JDime's tiny non-crash remainder moved by one case at Tier D and then held.

## A.7 The Weave abstention mechanism

Printed home: §3.4.4, which keeps the artifact reading and the tag; Table T3.2's Weave row states the one-point charge.

Weave merges at entity granularity. When both sides edit the same entity in interfering ways, it abstains and reports a conflict (§2.2). Each abstention is charged the one-point cost of a surfaced conflict, and Weave's entire weighted cost [WeaveTable] consists of exactly those charges. Abstention is never charged the ten-point silent-error weight, and it cannot lower precision. It can lower F1 only through an abstention on a trivial merge, which is a false negative, and Weave's perfect F1 [WeaveTable] entails that it recorded none. Merging power is a different question. On the cluster where a Weave specialist was later hypothesized, Weave's correct merges proved a strict subset of Mergiraf's; Chapter 6 carries the numbers.

## A.8 The residual Spork FP patterns

Printed home: §3.4.4, Table T3.2's Spork row, which keeps the three-class split, its counts and its tag.

The 11 residual false positives split three ways [SporkResiduals]:

- **2 formatter parse failures.** `google-java-format` cannot parse these files, so the canonicalizing pipeline never engages. This is a measurement boundary, not a Spork error.
- **2 content disagreements.** In one, Spork dropped an import the developer kept. In the other, it retained a debug print statement the developer deleted. These are real content divergences.
- **7 long-tail equivalences.** Four are single-pattern scenarios showing, respectively, a multi-declarator split, a fully-qualified name outside `java.lang`, numeric underscore literals, and a redundant `abstract` modifier. The remaining three mix several patterns at once.

## A.9 The materials-flow figure

Printed home: none; this is the record of a deleted figure.

The merged draft carried a Mermaid figure F3.1 showing dataset → file triples with the developer's resolution → fixed sample → six tools → comparator. It had zero inbound references and restated §3.3's first two paragraphs, so the compression pass deleted it. The former F3.2 (comparator layers) became F3.1 and the former F3.3 (tier-recovery chart) became F3.2. The second compression pass then deleted both, so the chapter carries no figure. Recorded here so the deck session can pick up the change.

## Claims used

- SporkFPBuckets
- SporkResiduals
- StratifiedLabelling
- WeaveTable
