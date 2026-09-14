# Appendix (candidate): background supplements

Status: skeleton created by the ch.2 compression session (2026-09-10) · Source text verbatim from merged draft-r3 except where an item is marked NEW or notes a pointer edit · Every item is marked **appendix-candidate** or **repo-cite (recommended)**; final print-appendix curation is Ali's end-of-wave ruling · Appendix letter assigned at curation · Narrative: none

**Why this file exists.** The ch.2 ceiling of 797 words is below the chapter's measured anchor floor (~995 words of content that another chapter's §-pointer or a ledger tag depends on). Ali ruled on 2026-09-10 that the ceiling binds. Everything below therefore left print rather than being deleted, because deleting it would have removed cited scholarship from the thesis's only related-work chapter. Items E.1, E.2 and E.4 are **strong print-appendix candidates**: each is the last home of a work or a fact the chapter previously carried in print. Ali ruled the curation on 2026-09-10: the cost-model item was deleted (ch.3 §3.1 and ch.12 §12.3 are its print homes) and the deleted-figures item was sent to repo-cite (the record is in `thesis/audits/ch2-retarget-map.md`).

## E.1 The six evaluated tools — appendix-candidate (strong)

Chapter home: §2.2 (the six names, their one-line identities, and Weave's abstention stay in print; ch.3 §3.3 cites §2.2 as the place all six are introduced).

- **`git merge-file`** is the line-based baseline. It is a standalone three-way merge over file triples, with no notion of syntax.
- **JDime** is the reference structured merge for Java, with the auto-tuned line/structure switch [CITE: apel2012autotuning, seibt2022leveraging]. Its practical standing is poor. Schesch et al. excluded it from their own evaluation [CITE: schesch2024evaluation]. They report that it discards comments and file headers, reorders declarations, runs slowly, and does not handle the full syntax of Java 8. It is retained here as a baseline for a specific reason. One family of its defects is content loss during AST round-trips. That family recurs in other tools.
- **Spork** is a Java merge tool from KTH. It maps files onto Spoon ASTs and applies a 3DM-style tree merge [CITE: larsen2023spork]. The tree merge gives it genuine support for moved code. Spork prints its result from its own AST. Its output can therefore differ textually from both parents even when it is semantically faithful. That is a pretty-printer characteristic, not a defect. The property is central to the oracle problem of Chapter 3. A naive textual comparison charges Spork for every reformatting.
- **Mastery** is a structured merge algorithm designed to handle code shifted between versions [CITE: zhu2022mastery]. In this thesis it serves as a non-driver baseline. Chapter 3 reports that its divergences from developer resolutions differ in character from Spork's. That contrast is what makes the pair a useful discrimination test for any oracle.
- **Mergiraf** is a recent syntax-aware merge tool built on tree-sitter grammars [CITE: mergiraf]. It is implemented in Rust and supports many languages. It is designed to be installed as an ordinary Git merge driver. It is fast enough for interactive use. In this thesis it emerges as the strongest structured tool under the repaired oracle (Chapter 3). It then becomes the backbone of the driver (Chapter 4).
- **Weave** merges at *entity* granularity: declarations are the unit of composition [CITE: weave]. Its abstention on interfering edits, stated in §2.2, makes it conservative by construction. That is an important contrast case when Chapter 3 discusses why a high-precision row in a results table is not by itself evidence of merging skill. Weave is a young open-source tool, first released in 2026 with no accompanying publication. Its upstream replay benchmark does not cover Java. To our knowledge, no independent published evaluation of Weave exists. I evaluate it as a backend and comparator baseline in Chapters 3 and 6.

**Merge-technique spectrum.** Merge techniques span a spectrum from unstructured (plain text) to fully structured (abstract syntax trees) [CITE: mens2002survey]. Files under semistructured merge are parsed to the granularity of declarations, and declarations are merged structurally by superimposition [CITE: apel2011semistructured]. The approach was later evaluated and refined empirically [CITE: cavalcanti2017evaluating]. Fully structured merge operates on ASTs throughout, at higher cost.

**The auto-tuning precedent.** JDime's principle is to spend precision only where the cheap path fails. The routing hypothesis this thesis examines has precedent in it. Chapter 6 tests the same idea at whole-tool granularity, routing entire merge cases to specialist tools by predicted difficulty. That test measures the principle's limits at that granularity. It does not question the principle itself.

## E.2 The seven-category starting taxonomy — appendix-candidate (strong)

Chapter home: §2.3, which prints the seven category names, the design-phase provenance record, and the working-hypothesis framing. This item carries the mechanisms and the worked-example pointers. Table T4.2 (ch.4) and Table T7.3 (ch.7) both print the seven category names in their own left-hand columns.

1. atomic updates split across branches;
2. control-flow interference, e.g. a short-circuit introduced around a call the other side made effectful;
3. data-flow interference, e.g. a stale read from a collection the other side cleared;
4. exception-handling divergence;
5. loop-semantics divergence, e.g. merged bounds that never terminate or never run;
6. method rename interference, a caller left referring to a name the other side renamed;
7. scope capture through variable shadowing.

**Provenance.** I compiled the taxonomy with worked Java examples in the design phase before this project's measurement program, with AI assistance (§9.1, §10.4). The examples live in a worked-example dataset outside this repository. The project's `ResearchSummary.xml` is an AI-generated summary of that dataset and of the prototype driver. It is the pointer Chapter 2 cites for the examples (§9.1).

**Framing.** The taxonomy was assembled from the literature and from constructed examples, not from field data. It shaped which detectors I built first (Chapters 4 and 8). Whether real histories distribute their silent failures the way the taxonomy suggests is an empirical question, answered in Chapter 7 with a full-population count over real merges.

**Foundations.** Program-integration research defined *interference* over program dependence representations [CITE: horwitz1989integrating]. That work showed that integrating noninterfering versions is possible in principle. It also showed that establishing noninterference is undecidable in general. Brun et al. observed clean merges that fail to build or test, and argued for proactive detection [CITE: brun2011proactive].


## E.4 Detection-side approaches not carried in print — appendix-candidate (strong)

Chapter home: §2.6 (the overriding-assignment operating point and IntelliMerge stay in print, because ch.8 §8.5 and ch.10 §10.4 cite them). This item is the last home of two works: RefMerge and MergeBERT. The Accioly conflict-pattern taxonomy returned to print in §2.6 on Ali's 2026-09-10 curation ruling.

- **Proactive approaches** merge continuously in the background and surface build or test breakage early [CITE: brun2011proactive].
- **SMAT** detects behavioral interference by generating unit tests targeted at merged regions [CITE: dasilva2020behavior].
- **RefMerge** inverts refactorings before merging and replays them afterwards [CITE: ellis2023refmerge]. It rests on the same specialist premise Chapter 6 measures.
- **MergeBERT** resolves *surfaced* textual conflicts with a neural model [CITE: svyatkovskiy2022mergebert]. It addresses the visible half of the problem. By construction it says nothing about merges that never surface, so it is out of scope here.

**The IntelliMerge gate.** The project's own tool survey reached the same conclusion as the external evidence. IntelliMerge occupies a box in this project's historical target pipeline, and I kept it out before integration. The omission was evidence-gated, not accidental. Chapter 6 applies the same gate logic to the specialist arms that *were* built.

