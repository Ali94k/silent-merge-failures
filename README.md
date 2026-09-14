# Textually Clean, Semantically Wrong — evidence record

Repository: `Ali94k/silent-merge-failures`.

This repository is the evidence record for the Master's thesis *Textually Clean, Semantically Wrong: An Anatomy and Detection of Silent Merge Failures*, Universität Passau, 2026.

The printed thesis cites files by path. This repository holds those files: the frozen measurement reports, the plans and pre-registrations, the adjudication exports, the decision record, the claims ledger, the writing contract, the appendix items that left print, and a source snapshot of the merge driver and the comparison framework.

It is not the working repository. It has no development history. The data corpora, the session transcripts and the working notes are not published here.

## Version

The files are a snapshot of the working repository at commit `2e10f41`.

<!-- RELEASE: public commit ________ · release tag v1.0.0 · DOI ________ (filled in once the release is archived) -->

## Resolving a thesis citation

**Paths.** Every path the thesis prints is relative to this repository's root, apart from the shorthand forms below. They also apply to the Source column of the claims ledger.

- **Reports.** A path that begins with `reports` is inside `merge-tool-comparison/`. For example, `reports_detectors/FINDINGS.md` is `merge-tool-comparison/reports_detectors/FINDINGS.md`. `reports*/` means all of those directories.
- **Strategies.** A path that begins with `strategies/` is inside `semantic_merge_driver/`.
- **Ledger cells.** The Source column also uses `config/` and `src/` for directories inside `merge-tool-comparison/`.
- **A directory with a section number.** "`reports_detectors/` §11" is section 11 of that directory's `FINDINGS.md`.
- **Names after a path.** A bare file name or a partial path printed after a path in the same sentence or cell is in that path's directory or the nearest directory above it. For example:
  - "`…/reports_taxonomy/phase3/adjudication/adjudication_record.md`; FINDINGS.md §3.2" means `merge-tool-comparison/reports_taxonomy/FINDINGS.md`.
  - "`reports_detection/full/`, `postfix{,2}/`" means `merge-tool-comparison/reports_detection/postfix{,2}/`.
  - A name that begins with a hyphen shares the stem of the path before it: "`docs/plans/comparator-3b-ast-normalize.md`, `-3d-extended-ast-transforms.md`" means `docs/plans/comparator-3d-extended-ast-transforms.md`.
- **Other bare file names.** A bare file name printed on its own, such as `ResearchSummary.xml` or `00-spine.md`, is the one file of that name in the repository. There are two exceptions. `adjudication_ui.html` exists in three places, one per annotation round. `hit_adjudications.md` exists in `reports_detection/full/` (the cited baseline) and `reports_detection/pilot_v2/`.
- **Braces.** Braces list alternatives: `postfix{,2}/` is `postfix/` and `postfix2/`.

**Section and table numbers.** The printed thesis numbers sections and tables sequentially. This repository's records, the appendix items and the claims ledger keep the draft identifiers, in which the numbers of withdrawn sections and tables stay unassigned, so the draft numbering has gaps that the print closes. Where the two differ: draft sections 4.4.2 and 4.4.3 are the print's 4.4.1 and 4.4.2; 6.4.4 is 6.4.3; 7.6 is 7.5; 8.4 is 8.3, 8.4.1 to 8.4.8 are 8.3.1 to 8.3.8, and 8.5 is 8.4; 9.5 and 9.6 are 9.4 and 9.5; 10.4 is 10.3. Draft table T3.2 is the print's Table 3.1, T6.5 is 6.1, T6.4 is 6.2, T7.8 is 7.2, T8.4 is 8.2, T8.8 is 8.3; T5.1 to T5.3 are A.1 to A.3; T7.2 is B.1. A printed number can also be a draft identifier with another meaning: printed 4.4.2, 8.4, 9.5 and Table 7.2 are the draft's 4.4.3, 8.5, 9.6 and T7.8. Figure numbers are the same in both. The same paragraph opens the printed Appendix A.

**Decision numbers.** `D-nnn` is the entry of that number in `docs/DECISIONS.md`, at the anchor `#d-nnn`. For example, D-021 is `docs/DECISIONS.md#d-021`. `docs/DECISIONS.md` is rendered from the entry files under `docs/decision-record/entries/`. `docs/decision-record/numbering.json` gives each number's entry and theme file. `docs/decision-record/PROTOCOL.md` is the protocol the record was built under. `docs/decision-record/render_decisions.py` regenerates `docs/DECISIONS.md` from those inputs.

The entries quote the working sessions they were extracted from. A quote's source line names a session file that is not published. The quote itself is the published evidence.

**Ledger tags.** A bracketed tag such as `[StageCCatch]` is a row of `thesis/claims-ledger.md`. The row's Source column names the file that holds the number. Paths in that column follow the same rules as above. A source that names a published paper rather than a file points outside this repository.

**Issues.** `ISSUES #n`, or `merge-tool-comparison/ISSUES.md` #n, is the section headed "Issue #n" in `merge-tool-comparison/ISSUES.md`. A list such as "ISSUES #27, #28" cites each item.

**Commit identifiers.** A short hash in the thesis or in these files, such as a freeze commit, names a commit of the working repository's history, unless the record labels it upstream. For example, the external benchmark's pin is marked "(upstream repo)". This repository does not carry that history. Each hash dates the state that a record or a number was frozen at.

## Appendix map

<!-- APPENDIX MAP: written by end-game step 3 (2026-09-14) from the curated files -->

The printed thesis keeps five appendices: A the methodology inventories (Tables T5.1, T5.2, T5.3), B the anatomy supplements (the count's protocol in summary, Table T7.2), C the comparator supplements (the transform catalogue, the per-tier trajectories), and the two generated listings D (decisions cited) and E (ledger rows cited). The 47 items below left print. Each opens with its printed home, the section of the thesis that keeps its claim, or states that it has none. The item identifiers are the ones the working files carried, so a thesis pointer such as "`appendix/anatomy-supplements.md`, A.3" names the file and the item.

| Item | Title | File and anchor |
|---|---|---|
| anatomy A.1 | The count's protocol rules and execution mechanics | `appendix/anatomy-supplements.md#a1-the-counts-protocol-rules-and-execution-mechanics` |
| anatomy A.2 | The worked coding example | `appendix/anatomy-supplements.md#a2-the-worked-coding-example` |
| anatomy A.3 | The escape-boundary case that split the passes | `appendix/anatomy-supplements.md#a3-the-escape-boundary-case-that-split-the-passes` |
| anatomy A.5 | The four-family regrouping assessment | `appendix/anatomy-supplements.md#a5-the-four-family-regrouping-assessment` |
| attribution C.1 | The draft-ruling audit's verification procedure | `appendix/attribution-supplements.md#c1-the-draft-ruling-audits-verification-procedure` |
| attribution C.2 | The exported adjudication record | `appendix/attribution-supplements.md#c2-the-exported-adjudication-record` |
| attribution C.3 | The two held-out population defects, itemized | `appendix/attribution-supplements.md#c3-the-two-held-out-population-defects-itemized` |
| attribution C.4 | The decision record's extraction-protocol detail | `appendix/attribution-supplements.md#c4-the-decision-records-extraction-protocol-detail` |
| attribution C.5 | What the pre-transcript commits cover | `appendix/attribution-supplements.md#c5-what-the-pre-transcript-commits-cover` |
| attribution C.6 | §9.3's ruling-groups breakdown | `appendix/attribution-supplements.md#c6-93s-ruling-groups-breakdown` |
| attribution C.7 | The reading discipline for this chapter | `appendix/attribution-supplements.md#c7-the-reading-discipline-for-this-chapter` |
| attribution C.8 | The review flow's branch mechanics and the ruled-text rule | `appendix/attribution-supplements.md#c8-the-review-flows-branch-mechanics-and-the-ruled-text-rule` |
| attribution C.9 | The full-count labeling pass's own name | `appendix/attribution-supplements.md#c9-the-full-count-labeling-passs-own-name` |
| attribution C.10 | The mis-scored run's second error | `appendix/attribution-supplements.md#c10-the-mis-scored-runs-second-error` |
| attribution C.11 | The ruling audit's scope bound | `appendix/attribution-supplements.md#c11-the-ruling-audits-scope-bound` |
| background E.1 | The six evaluated tools | `appendix/background-supplements.md#e1-the-six-evaluated-tools` |
| background E.2 | The seven-category starting taxonomy | `appendix/background-supplements.md#e2-the-seven-category-starting-taxonomy` |
| background E.4 | Detection-side approaches not carried in print | `appendix/background-supplements.md#e4-detection-side-approaches-not-carried-in-print` |
| comparator A.1 | The naive-FP bucket diagnostic | `appendix/comparator-supplements.md#a1-the-naive-fp-bucket-diagnostic` |
| comparator A.2 | The stratified labelling sample's recurring patterns | `appendix/comparator-supplements.md#a2-the-stratified-labelling-samples-recurring-patterns` |
| comparator A.5 | The three re-diagnoses' findings | `appendix/comparator-supplements.md#a5-the-three-re-diagnoses-findings` |
| comparator A.6 | Mastery's movement under the pipeline | `appendix/comparator-supplements.md#a6-masterys-movement-under-the-pipeline` |
| comparator A.7 | The Weave abstention mechanism | `appendix/comparator-supplements.md#a7-the-weave-abstention-mechanism` |
| comparator A.8 | The residual Spork FP patterns | `appendix/comparator-supplements.md#a8-the-residual-spork-fp-patterns` |
| comparator A.9 | The materials-flow figure | `appendix/comparator-supplements.md#a9-the-materials-flow-figure` |
| detection B.1 | The detector cycle's numeric gate criteria | `appendix/detection-supplements.md#b1-the-detector-cycles-numeric-gate-criteria` |
| detection B.2 | The baseline repair's four defects | `appendix/detection-supplements.md#b2-the-baseline-repairs-four-defects` |
| detection B.3 | The tcurdt re-ruling | `appendix/detection-supplements.md#b3-the-tcurdt-re-ruling` |
| detection B.4 | The atam4j re-ruling | `appendix/detection-supplements.md#b4-the-atam4j-re-ruling` |
| detection B.5 | The external run's deployment view | `appendix/detection-supplements.md#b5-the-external-runs-deployment-view` |
| detection B.6 | The worked example: D1's guard walk | `appendix/detection-supplements.md#b6-the-worked-example-d1s-guard-walk` |
| detection B.7 | Per-detector held-out prose | `appendix/detection-supplements.md#b7-per-detector-held-out-prose` |
| detection B.8 | The baseline rerun's split breakdown | `appendix/detection-supplements.md#b8-the-baseline-reruns-split-breakdown` |
| detection B.9 | The lanes' latency components | `appendix/detection-supplements.md#b9-the-lanes-latency-components` |
| detection B.10 | The five recall ceilings, full statements | `appendix/detection-supplements.md#b10-the-five-recall-ceilings-full-statements` |
| driver D.1 | The default strategies' documented limits | `appendix/driver-supplements.md#d1-the-default-strategies-documented-limits` |
| driver D.2 | `JoernUnresolvedReference`'s two parser quirks | `appendix/driver-supplements.md#d2-joernunresolvedreferences-two-parser-quirks` |
| driver D.3 | The D1 lane's five guards | `appendix/driver-supplements.md#d3-the-d1-lanes-five-guards` |
| driver D.4 | The D2 lane's four guards | `appendix/driver-supplements.md#d4-the-d2-lanes-four-guards` |
| driver D.5 | The lanes' worked shapes | `appendix/driver-supplements.md#d5-the-lanes-worked-shapes` |
| driver D.7 | The as-built flow, step by step | `appendix/driver-supplements.md#d7-the-as-built-flow-step-by-step` |
| methodology A.4 | Annotation review interface (screenshot placeholder) | `appendix/methodology-supplements.md#a4-annotation-review-interface-screenshot-placeholder` |
| routing C.1 | The arms' rationale and the worked dispatch example | `appendix/routing-supplements.md#c1-the-arms-rationale-and-the-worked-dispatch-example` |
| routing C.2 | The mapping document's history | `appendix/routing-supplements.md#c2-the-mapping-documents-history` |
| routing C.3 | The tools' own records, read after the verdicts | `appendix/routing-supplements.md#c3-the-tools-own-records-read-after-the-verdicts` |
| routing C.4 | The whole-driver runs' scoring detail | `appendix/routing-supplements.md#c4-the-whole-driver-runs-scoring-detail` |
| routing C.5 | The method-body gate's two-layer pre-registration | `appendix/routing-supplements.md#c5-the-method-body-gates-two-layer-pre-registration` |

<!-- /APPENDIX MAP -->

## Layout

| Directory | Contents |
|---|---|
| `appendix/` | The 47 appendix items that left the printed thesis, as markdown in eight files (the map above). |
| `deploy/` | The cloud run procedure, its runbook, and the per-cycle provision, bundle and run scripts. |
| `docs/` | The decision record (`DECISIONS.md`, `decision-record/`), five plans (`plans/`), and archived documents, including the decision record's first version (`historical/`). |
| `merge-tool-comparison/` | The comparison framework: source, tests, tools, prompts, `ISSUES.md`, and the frozen reports in `reports*/`. |
| `outputs/` | The detector-cycle plan, the full count's protocol, and the detection-validation plan. |
| `research/` | Two reconnaissance notes that a findings file and the threats register cite. |
| `semantic_merge_driver/` | The merge driver: backends, strategies, tests. |
| `thesis/` | The claims ledger, the writing contract (`WORKFLOW.md`), and the thesis spine. |
| `CLAUDE.md` | The project's standing rules: the written contract that Chapter 9 cites. |
| `THREATS_TO_VALIDITY.md` | The project's threats register, a ledger source. |
| `LICENSE`, `LICENSE-docs.md` | The licence texts. |
| `CITATION.cff`, `.zenodo.json` | Citation metadata for the release archive. |

## Running the code

The merge tools run only through their Docker images (see `semantic_merge_driver/README.md` and `merge-tool-comparison/README.md`). The scenario corpora are not included. `merge-tool-comparison/README.md` says where to obtain the public dataset, and the loaders in `merge-tool-comparison/src/data/` and the materialization tools in `merge-tool-comparison/tools/` rebuild the scenarios from it and from the upstream repositories.

## Licence

Code is licensed under the Apache License 2.0 (`LICENSE`). Code means the Python sources, shell scripts, Joern queries, Dockerfiles, Makefiles and configuration files in `semantic_merge_driver/`, `merge-tool-comparison/`, `deploy/` and `docs/decision-record/`, including the scripts kept beside the reports under `reports*/`.

Everything else the project wrote or produced is licensed under Creative Commons Attribution 4.0 International (`LICENSE-docs.md`). That covers the documents, the decision record, the claims ledger, the appendix supplements, the reports and data files under `reports*/`, and the project-written test fixtures.

Third-party material keeps its own licence and is not relicensed here. That covers the open-source Java source carried inside `reports*/`, including the test fixtures that source contains, the merge tools that the Dockerfiles fetch and build, and the cited papers.

Copyright 2026 Ali Karimli.
