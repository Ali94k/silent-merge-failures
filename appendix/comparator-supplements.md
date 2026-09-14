# Appendix (candidate): comparator supplements

Status: skeleton created by the ch.3 compression session (2026-09-10; source text from merged draft-r3, except where an item is marked NEW below) · Every item is marked **appendix-candidate** or **repo-cite (recommended)**; final print-appendix curation is Ali's end-of-wave ruling · Appendix letter assigned at curation · Pointer edits applied to moved text are flagged per item · **NEW (not in the merged draft, each value ledger-backed):** A.3's Tier E enumeration, transcribed from `merge-tool-comparison/ISSUES.md` #2 phases 3e.0-3e.10; A.4's table and caption; A.8's 2 / 2 / 7 counts; A.9 in full · Narrative: none

**Ruled shortlist (Ali):** the promoted six-tool table and the condensed tier catalogue are both on the print-appendix shortlist. Items A.3 and A.4 below are that catalogue and must not be curated to repo-only. The promoted six-tool table itself stays in the chapter as Table T3.2.

## A.1 The naive-FP bucket diagnostic — repo-cite (recommended)

Chapter home: §3.2 (the claim and the tag stay in print: "put nearly the entire naive FP mass in one bucket of structural differences [SporkFPBuckets]"). Repo record: `docs/plans/stage-gamma-fp-diagnostic.md` §2–3.

The first diagnostic pass bucketed Spork's 42 naive false positives by mechanical shape: 39 structural, 1 whitespace-only, 2 imports-plus-whitespace [SporkFPBuckets]. The initial manual inspection that read the structural bucket as pure reformatting covered 3 size-stratified diffs. That inspection is what motivated trying the formatter roundtrip first, and it is what failed to generalize.

## A.2 The stratified labelling sample's recurring patterns — appendix-candidate

Chapter home: §3.2 (the pass, its finding, its tag and its attribution stay in print). Repo record: `docs/plans/stage-gamma-fp-diagnostic.md`; ISSUES #2; commit `caf33e2`.

The second diagnostic pass drew residual cases across file-size quintiles, 3 per quintile, and labelled each from its raw, pre-formatter diff. All 15 were ruled AST-equivalent reformatting [StratifiedLabelling]. The recurring patterns in that sample were extra parentheses around casts, fully-qualified names expanded from `java.lang`, comment placement, and `} else { if }` restructuring. The AI assistant performed the pass. I ruled the attribution on 2026-08-06 (D-212), and Chapter 9 records it.

## A.3 The AST transform catalogue — appendix-candidate (ruled shortlist)

Chapter home: §3.3 ("unit-tested tree-sitter transforms designed to be semantics-preserving and condensed in the comparator supplement's catalogue") and §3.4.1. Repo record: `merge-tool-comparison/ISSUES.md` #2.

- **Tier C — five transforms.** Comment stripping, blank-line stripping, `else`-`if` flattening, redundant paren-around-paren removal, and `java.lang` qualifier stripping.
- **Tier D — six broader transforms.** Single-statement block unwrapping, four parenthesis strips (around primaries, around casts, and two binary-expression families under precedence guards), and a token-canonical fold that ends line-breaking artifacts.
- **Tier E — a bug fix plus ten transforms.** Unary `!` and `~` paren strip, `new T[]{}` array shorthand, same-operator left-associative paren strip for `+`, `-`, `*`, `/` and `%` in left position, `instanceof` paren strip, enum trailing `;`, an expanded safe-binary-paren parent set, array-initializer trailing comma, assignment paren strip, float `d`/`D`/`f`/`F` suffix normalization, and hex-case lowercasing.

## A.4 The per-tier trajectories — appendix-candidate (ruled shortlist)

Chapter home: §3.4.1 (the tag, the landing point and the floor verdict stay in print). Repo record: `merge-tool-comparison/ISSUES.md` tier tables; `reports/results.csv`.

Counts at each oracle stage, naive through Tier E [TierTrajectories]:

| Tool | naive | formatter | Tier C | Tier D | Tier E |
|---|---|---|---|---|---|
| Spork | 1 TP / 42 FP | 2 / 41 | 7 / 36 | 14 / 29 | 32 / 11 |
| Mastery | 0 TP / 44 FP | 0 / 44 | 0 / 44 | 10 / 34 | 12 / 32 |
| JDime | 0 TP / 2 FP | 0 / 2 | 0 / 2 | 1 / 1 | 1 / 1 |

*Table A.1 — Spork's per-tier recoveries are +1, +5, +7 and +18 [TierTrajectories].*

The floor is defined over false positives recovered above the post-formatter baseline [PreRegFloor]. Spork's clean-merge total is 43 at every tier, so the TP and FP bases agree: 41 − 11 = 30, and 32 − 2 = 30. The plan writes that cumulative recovery as X_total, and 30 meets the floor X ≥ 30 exactly.

## A.5 The three re-diagnoses' findings — repo-cite (recommended)

Chapter home: none. The second compression pass deleted the re-diagnosis sentence, so this item has no chapter anchor. Repo record: `merge-tool-comparison/ISSUES.md` #2; `docs/plans/comparator-3b-ast-normalize.md`.

**Demoted on Ali's ruling of 2026-09-10 (compression option P4). On the repo-cite recommendation this item leaves print entirely, as does A.1.**

- **Re-diagnosis one, after the formatter tier recovered almost nothing.** It triggered the stratified re-annotation of A.2.
- **Re-diagnosis two, mandated when Tier C's recovery fired the pause threshold.** It produced the cycle's key methodological finding: the residual diff *after* formatter normalization is dominated by different patterns than the raw diff that was annotated. "AST-equivalent" does not imply "recoverable by any particular transform set".
- **Re-diagnosis three, on the residuals left after Tier D.** It found that Tier D's block-unwrap transform carried an identity-comparison defect that had been corrupting its interaction with the token fold. It also found that the dominant residual patterns again differed from what the plan brief expected. Tier E carries the fix.

## A.6 Mastery's movement under the pipeline — appendix-candidate

Chapter home: §3.4.2 (the discrimination claim and the unmoved core stay in print; the comment-only reading and the one non-comment recovery left print in the second compression pass). The chapter's pointer to this item sits in §3.4.4, Table T3.2's Mastery row.

The bulk of Mastery's movement arrived at Tier D, when the token fold began closing comment-only cases. The project's records call that movement a surprise. The last arrivals came at Tier E: a comment-only case revealed by the block-unwrap bug fix, and a single array-initializer trailing-comma case, which is the one non-comment recovery. File headers and Javadoc blocks count as comments for this purpose. JDime's tiny non-crash remainder moved by one case at Tier D and then held.

## A.7 The Weave abstention mechanism — appendix-candidate

Chapter home: §3.4.4 (the artifact reading and the tag stay in print, and Table T3.2's Weave row states the one-point charge).

Weave merges at entity granularity. When both sides edit the same entity in interfering ways, it abstains and reports a conflict (§2.2). Each abstention is charged the one-point cost of a surfaced conflict, and Weave's entire weighted cost [WeaveTable] consists of exactly those charges. Abstention is never charged the ten-point silent-error weight, and it cannot lower precision. It can lower F1 only through an abstention on a trivial merge, which is a false negative, and Weave's perfect F1 [WeaveTable] entails that it recorded none. Merging power is a different question. On the cluster where a Weave specialist was later hypothesized, Weave's correct merges proved a strict subset of Mergiraf's; Chapter 6 carries the numbers.

*Pointer edit applied:* the merged text's forward pointer "§3.4.6 gives the reason" is now the chapter's own "The comparator supplement works the abstention mechanism through", in §3.4.4. The second compression pass made that wording route-neutral, so it needs no rewording if this item is curated to repo-only.

## A.8 The residual Spork FP patterns — appendix-candidate

Chapter home: §3.4.4, Table T3.2's Spork row (the three-class split, its counts and its tag stay in print). §3.4.6 was withdrawn by the second compression pass.

The 11 residual false positives split three ways [SporkResiduals]:

- **2 formatter parse failures.** `google-java-format` cannot parse these files, so the canonicalizing pipeline never engages. This is a measurement boundary, not a Spork error.
- **2 content disagreements.** In one, Spork dropped an import the developer kept. In the other, it retained a debug print statement the developer deleted. These are real content divergences.
- **7 long-tail equivalences.** Four are single-pattern scenarios showing, respectively, a multi-declarator split, a fully-qualified name outside `java.lang`, numeric underscore literals, and a redundant `abstract` modifier. The remaining three mix several patterns at once.

## A.9 The materials-flow figure — deleted, no home

The merged draft carried a Mermaid figure F3.1 showing dataset → file triples with the developer's resolution → fixed sample → six tools → comparator. It had zero inbound references and restated §3.3's first two paragraphs, so the compression pass deleted it. The former F3.2 (comparator layers) became F3.1 and the former F3.3 (tier-recovery chart) became F3.2. The second compression pass then deleted both, so the chapter carries no figure. Recorded here so the deck session can pick up the change.
