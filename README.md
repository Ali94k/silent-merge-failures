# Textually Clean, Semantically Wrong — evidence record

Repository: `Ali94k/silent-merge-failures`.

This repository is the evidence record for the Master's thesis *Textually Clean, Semantically Wrong: An Anatomy and Detection of Silent Merge Failures*, Universität Passau, 2026.

The printed thesis cites files by path. This repository holds those files: the frozen measurement reports, the plans and pre-registrations, the adjudication exports, the decision record, the claims ledger, the writing contract, the appendix supplements, and a source snapshot of the merge driver and the comparison framework.

It is not the working repository. It has no development history. The data corpora, the session transcripts and the working notes are not published here.

## Version

The files are a snapshot of the working repository at commit `c214977`.

<!-- RELEASE: public commit ________ · release tag ________ · DOI ________ (filled in once the release is archived) -->

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

**Decision numbers.** `D-nnn` is the entry of that number in `docs/DECISIONS.md`, at the anchor `#d-nnn`. For example, D-021 is `docs/DECISIONS.md#d-021`. `docs/DECISIONS.md` is rendered from the entry files under `docs/decision-record/entries/`. `docs/decision-record/numbering.json` gives each number's entry and theme file. `docs/decision-record/PROTOCOL.md` is the protocol the record was built under. `docs/decision-record/render_decisions.py` regenerates `docs/DECISIONS.md` from those inputs.

The entries quote the working sessions they were extracted from. A quote's source line names a session file that is not published. The quote itself is the published evidence.

**Ledger tags.** A bracketed tag such as `[StageCCatch]` is a row of `thesis/claims-ledger.md`. The row's Source column names the file that holds the number. Paths in that column follow the same rules as above. A source that names a published paper rather than a file points outside this repository.

**Issues.** `ISSUES #n`, or `merge-tool-comparison/ISSUES.md` #n, is the section headed "Issue #n" in `merge-tool-comparison/ISSUES.md`. A list such as "ISSUES #27, #28" cites each item.

**Commit identifiers.** A short hash in the thesis or in these files, such as a freeze commit, names a commit of the working repository's history, unless the record labels it upstream. For example, the external benchmark's pin is marked "(upstream repo)". This repository does not carry that history. Each hash dates the state that a record or a number was frozen at.

## Appendix map

<!-- APPENDIX MAP: rewritten by end-game step 3 when the appendix items are curated -->

| Items | File |
|---|---|
| anatomy A.1–A.5 | `appendix/anatomy-supplements.md` |
| attribution C.1–C.11 | `appendix/attribution-supplements.md` |
| background E.1, E.2, E.4 | `appendix/background-supplements.md` |
| comparator A.1–A.9 | `appendix/comparator-supplements.md` |
| detection B.1–B.10 | `appendix/detection-supplements.md` |
| driver D.1–D.5, D.7 | `appendix/driver-supplements.md` |
| methodology A.1–A.4 | `appendix/methodology-supplements.md` |
| routing C.1–C.5 | `appendix/routing-supplements.md` |

<!-- /APPENDIX MAP -->

## Layout

| Directory | Contents |
|---|---|
| `appendix/` | The thesis's appendix supplements, as markdown. |
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

## Running the code

The merge tools run only through their Docker images (see `semantic_merge_driver/README.md` and `merge-tool-comparison/README.md`). The scenario corpora are not included. `merge-tool-comparison/README.md` says where to obtain the public dataset, and the loaders in `merge-tool-comparison/src/data/` and the materialization tools in `merge-tool-comparison/tools/` rebuild the scenarios from it and from the upstream repositories.

## Licence

Code is licensed under the Apache License 2.0 (`LICENSE`). Code means the Python sources, shell scripts, Joern queries, Dockerfiles, Makefiles and configuration files in `semantic_merge_driver/`, `merge-tool-comparison/`, `deploy/` and `docs/decision-record/`, including the scripts kept beside the reports under `reports*/`.

Everything else the project wrote or produced is licensed under Creative Commons Attribution 4.0 International (`LICENSE-docs.md`). That covers the documents, the decision record, the claims ledger, the appendix supplements, the reports and data files under `reports*/`, and the project-written test fixtures.

Third-party material keeps its own licence and is not relicensed here. That covers the open-source Java source carried inside `reports*/`, including the test fixtures that source contains, the merge tools that the Dockerfiles fetch and build, and the cited papers.

Copyright 2026 Ali Karimli.
