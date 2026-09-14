# CLAUDE.md

Notes for future Claude sessions working in this repo.

## Source of truth

For any architectural or design question, the authoritative inputs are:

1. **Source code** in `merge-tool-comparison/` and `semantic_merge_driver/`.
2. **`semantic_merge_driver/initial architecture.md`** — the target pipeline for the merge driver.

Anything else (README narratives, `STATUS.md`, memory files) is derived from these and may lag behind.

Historical design documents that **do not reflect the current target** live in [`docs/historical/`](docs/historical/). Do not cite those as current design.

**Thesis work starts at [`thesis/HANDOFF.md`](thesis/HANDOFF.md)** — current state, open rulings, what is queued, and how coordinator and worker sessions divide the work. Its companions are [`thesis/audits/compression-levers.md`](thesis/audits/compression-levers.md) (the wave's measured compression method) and [`thesis/WORKFLOW.md`](thesis/WORKFLOW.md) (rules R1–R13). A snapshot of the Claude auto-memory store, with restore instructions, is in [`docs/session-memory/`](docs/session-memory/).

## Standing rules from the user

- **Never delete `*.key` files** (Keynote presentations). They stay in the repo even if seemingly stale.
- **Ask before destructive actions.** This repo is not git-backed locally in a way that makes `rm -rf` undoable — check with the user before removing files or folders outside `data/`, caches, or `workspace/` scratch dirs.
- **Keep prose terse.** No "Let me..." preambles, no trailing summaries.
- **Always prefer AWS over local for compute runs** (decided 2026-07-15). Evaluation batteries, corpus runs, and anything Docker-emulation-bound go to an EC2 cycle per `deploy/aws/CLI-DEPLOY.md` (repo root; c7i.2xlarge native x86_64 pattern; 8 runs proven — 7 runbook-numbered cycles + 1 unnumbered short run, ~$5–10 each) rather than local overnight runs on the Apple-Silicon Mac. Rationale: native x86_64 avoids the Rosetta/QEMU tax and the arm64-image-dies-silently class of scoring bugs; keeps the Mac free. Standing sub-rules: build images on-instance, validate the env by reproducing a canonical table before scoring, tear down + verify empty. Local runs remain fine for unit tests, fixtures, and small pilots (≤ ~20 units).
- **Merge tools invoked via Docker only.** All evaluated/integrated tools (Mergiraf, JDime, Spork, Mastery, Weave, RefactoringMiner) must be invoked through their Docker images in the `merge-tools/<name>` namespace, never via host PATH binaries. Host installations (e.g., `brew install mergiraf`) are dev convenience for ad-hoc CLI use only — not runtime dependencies. Applies to both `merge-tool-comparison/` and `semantic_merge_driver/`. Exception: `git` itself. This rule **overrode the now-stale `weave-integration.md` "native, no Docker" W1 decision** when Weave was integrated 2026-05-18. Version-pinning of image tags (`merge-tools/<name>:<version>`) is best-practice and in place for `mergiraf:0.17.0`, `spork:0.5.0`, and `weave:0.3.2` (the latter two pinned 2026-05-18 for the constructive backends; the empirical Spork adapter still uses the legacy untagged `merge-tools/spork`, dual-tagged from the same build); refactoring-miner is pinned (`merge-tools/refactoring-miner:2.4.0` in `core/refactoring_classifier.py`); retroactive pinning of jdime/mastery remains a future-work TODO.
- **Driver is the primary deliverable; the comparator tracks the driver's backends.** The empirical `merge-tool-comparison` toolset should cover the `semantic_merge_driver` backends (git-merge-file, mergiraf, spork, weave) so the comparison justifies the driver's routing — not stand alone. **2026-05-20 (decided with the user):** added comparator adapters `src/tools/mergiraf.py` (`merge-tools/mergiraf:0.17.0`) and `src/tools/weave.py` (`merge-tools/weave:0.3.2`), both enabled in `config/tools.yaml` and mirroring the driver backends' Docker invocations. jdime + mastery stay enabled as **non-driver baselines** (their prior empirical findings remain valid but are no longer the focus). Adapters are wired but **not yet run on the corpus** — a tagging/run pass is still pending.

## Repo layout

```
my-data-project/                   (git root; remote: github.com/Ali94k/thesis-projects, private)
├── README.md                      overview of both projects
├── ARCHITECTURE.md                unified technical design (both pipelines)
├── STATUS.md                      honest snapshot: implemented vs. planned vs. broken
├── CLAUDE.md                      this file
├── docs/historical/               superseded designs kept for thesis-writing context
├── docs/plans/                    in-flight integration plans (RM2, mergiraf, weave, spork-driver, etc.)
├── merge-tool-comparison/         empirical: replicates Schesch et al. ASE 2024
│   ├── README.md                  project-specific docs
│   └── ISSUES.md                  31 tracked issues; 9 resolved in headings
└── semantic_merge_driver/
    ├── README.md                  project-specific docs
    ├── initial architecture.md    **authoritative target pipeline**
    └── core/sq.md                 runtime sequence diagram
```

## Practical setup

- **Python:** 3.10+ (merge-tool-comparison), 3.14 venv present (semantic_merge_driver).
- **Credentials:** macOS Keychain (`osxkeychain` git helper). `git push` Just Works.
- **`gh` CLI is installed and authenticated as Ali94k.** Used for the thesis PR review flow (see `thesis/WORKFLOW.md`).
- **Docker:** required for merge-tool-comparison (JDime, Spork, Mastery) **and** for semantic_merge_driver's default Mergiraf backend (`merge-tools/mergiraf:0.17.0` image; `SEMANTIC_MERGE_BACKEND=git` env var falls back to inline `git merge-file`). Hardcoded to `--platform linux/amd64` — slow on Apple Silicon via Rosetta/QEMU.
- **Joern:** required for semantic_merge_driver strategies. Invoked via `joern-parse` and `joern --cpg …` subprocesses.

## Gitignored (re-cloneable / regenerable)

- `merge-tool-comparison/data/repos/` (~2.1 GB cloned Java source)
- `merge-tool-comparison/data/schesch-dataset/` (661 MB, own git repo, re-cloneable from Zenodo)
- `.venv/`, `venv/` (three Python virtualenvs)
- `.pytest_cache/`, `.metals/`, `__pycache__/`, `.DS_Store`
- `**/.claude/worktrees/` (abandoned Claude worktrees; exist on disk, not tracked)
- `*.cpg.bin`, `*.log`
- Result artifacts in `merge-tool-comparison/reports/` are **explicitly unignored** (preserved for thesis reference).

## Known live caveats (more detail in [STATUS.md](STATUS.md))

- **`merge-tool-comparison` headline numbers — Spork comparator-gap CLOSED post-3e Tier E.** Post-3e Tier E (2026-05-15): Spork 11 FP / 32 TP (was 29/14 post-3d; 36/7 post-3b; 41/2 post-M3.5; 42/1 pre-M3.5). 3e Tier E (D.1 identity-bug fix + 10 new transforms: unary `!`/`~` paren strip, `new T[]{}` array shorthand, `+`/`-`/`*` same-op left-assoc paren strip, instanceof paren, enum trailing `;`, expanded SAFE_BINARY_PAREN_PARENTS with assert_statement + array_access, array_initializer trailing comma, assignment paren, float `d`/`D`/`f`/`F` suffix normalize, hex case lowercase) recovered 18 additional Spork residuals (X_total = 30, **HITS** the original 3b plan §3 floor of X ≥ 30 exactly). **ISSUES.md #2 moves `decided → resolved`.** Mastery 10→12 TP / 34→32 FP — bonus +2 from D.1 fix + array trailing comma strip. Remaining 32 Mastery FPs are genuine code-content loss — recoverable only via test-suite ground truth (3a), if at all. JDime unchanged at 1/1 (96% crash rate intrinsic — Schesch et al. excluded JDime from their own evaluation as "unsuitable for practical use"). git-merge-file unchanged at 39/0. The 11 remaining Spork FPs are dominated by truly irrecoverable cases: 2 gjf parse-fail, 2 content disagreements (Spork dropped 1 import; Spork kept a debug `println`), plus 7 long-tail patterns (multi-decl split, FQN scope, numeric underscore, redundant `abstract`) deferred to Tier F or 3a. Cite these numbers as final for thesis defense with the methodological caveat that the comparator-gap framing required four tiers (M3.5 + 3b + 3d + 3e) to close.
- **`semantic_merge_driver` covers 3 of 7 conflict categories** (5 strategies since Stage-B v2): #3 Data Flow Interference / Stale Read (Joern detector `JoernDataFlowInterference` at `strategies/joern_strategies/taint_check.py` — flags a collection cleared then read without repopulation; differential 3-way, merge-induced only. **Narrow PoC:** literal `.clear()` only, method-name matching without types, line-ordering not flow-sensitive, intra-method/intra-file), #5 Loop Semantics Divergence (infinite loop + invalid bounds, Joern-based) and the #6 rename/declaration family (`RM2RenameConflict` v2 + differential `JoernUnresolvedReference`). **Detector cycle D1–D3 DONE (ISSUES #31 resolved 2026-07-20, suite frozen `732d8ff` — a FOURTH instrument, never blend):** two new flag-gated lanes (`ImportPruneUsage` D1, `SignatureStaleCall` D2) + a flag-gated textual widening of `JoernUnresolvedReference` (D3), all behind `SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1` (default behavior unchanged; default-enabling deferred). Held-out causal recall (Ali-adjudicated): name-binding family 5.7% → **40.0% [25.6, 56.4]** (14/35 after the 2026-09-05 ruling: one unit per distinct merge, design-spec fork twin excluded; as run 16/37 = 43.2%; added 34.3%), D1 own-category 11/12 at 12/12 precision; **0 ruled FPs / 363 controls** (2 flags ruled incidental-but-true incl. jOOQ "Grr Git"); D2 honest 0 (file-local ceiling); D3 widening 0-causal/1-FP unseen (same-package residual). `merge-tool-comparison/reports_detectors/FINDINGS.md`. The other 4 categories have no detection logic. **Detection is MEASURED on real data (ISSUES #29, resolved 2026-07-03):** frozen Stage-C R2 = 11 flags of 164 = 6.7% [3.8, 11.6] — **9 CAUSAL = 5.5% [2.9, 10.1] after the 2026-09-04 audit** (atam4j + tcurdt re-ruled DETECTOR-FP by Ali; `reports_detection/full/audit_2026-09-04.md`; the atam4j sibling file is a measured cross-file FN) / R1 = 2.1%; post-fix (two labeled rounds) R1 = 0/193 = 0.0% [0, 2.0], R2 = 11/164; **all detection mass is the #6 family — categories #3/#5 fired zero times on 443 real files** (base-rate finding). **Phase-2b external oracle MEASURED (2026-07-05, spgroup mergedataset @ `04a18017`, detectors @ `f964354`, `reports_detection/phase2b/FINDINGS.md`):** recall on 17 externally labeled interference units **0/17 [0, 18.4]** (per-category #3 = 0/1 — a reassignment-shape stale read missed exactly as the frozen pre-run mapping predicted; the literal-`.clear()` limit is now a measured FN); FP **0/66 [0, 5.5]** on labeled-clean units (zero-FP record extends to a second independent corpus); G1 10/10 both arms; 12/17 of the benchmark's interference sits in uncovered #1/#2, zero #4/#5/#7 instances (base-rate finding corroborated); category mapping RULED by Ali 2026-07-27 (17/17 confirm the frozen draft, 0 overrides — per-category table final); NEW labeled evaluation — never blend with Stage C. The driver's three-way merge step is backend-pluggable as of M6-lite (`3fef834`): `MergeBackend` ABC at `core/backends/base.py`; default is `auto` (R4b — `AutoBackend` invokes the RM2 classifier, logs cluster + language; **post-flip default map: `NONE`→git-merge-file, everything else→Mergiraf**; any chosen backend returning CRASH falls back to `GitMergeFileBackend`). `SEMANTIC_MERGE_BACKEND=mergiraf`, `=git`, `=spork`, and `=weave` are all selectable for explicit-bypass workflows. **Backends-only cycle (2026-05-18):** `SporkBackend` (`merge-tools/spork:0.5.0`) and `WeaveBackend` (`merge-tools/weave:0.3.2`, newly Dockerized) shipped as selectable backends registered in the `driver.py` `BACKENDS` dict. **Routing Phase 1 (`c0a32f5`) wired the S2/W5 elifs; both evidence gates subsequently REFUTED the arms and the flip landed (see below)** — post-flip, Spork/Weave route only under `SEMANTIC_MERGE_SPECIALIST_ROUTING=1`. Weave's v0.3.2 CLI was confirmed against the built image: `WeaveBackend` uses the `-o <output>` form because the positional/git-driver form *empties the ours file* on a whole-entity conflict (silent data loss). Weave is entity-level — on conflict it returns rc 1 with a summary and **no `<<<<<<<` marker file**; the backend keys CONFLICT off rc 1 and never blanks ours_path. Full suite 122/122 green with all three backend images built. **Comparator now tracks these backends + first Phase-2 routing evidence (2026-05-26):** mergiraf/weave comparator adapters added (see standing rule above); `tools/select_materialize.py` scales the corpus (tool-outcome selection, blobless+`--no-checkout` clone with per-clone timeout, multi-base skip). Across 3 file-level samples (n=6 + n=10 + n=43 `INTRA_BODY`) + the full 5,405-merge table + a Spork-rigged synthetic battery, Mergiraf beats Spork in **every** cluster. **CI-grade → DROP decided (2026-05-27, ISSUES #27):** pooled INTRA_BODY precision + Wilson 95% CI Spork 0.49 [0.37, 0.60] vs Mergiraf 0.78 [0.66, 0.86] (non-overlapping); Spork is also ~14× slower (faster in 0/146 both-clean cases) and scored **0 strict-wins** over Mergiraf on 16 cases hand-built to favor it. The S2 (`INTRA_BODY`→Spork) arm was **refuted** — route to Mergiraf, keep Spork selectable + as a comparator baseline. Spork's FPs are mostly comparator-gap (genuine ≈27%), **but Mergiraf wins under the *same* normalization, so the gap is not the driver.** (#27 resolved with the flip — see below.) **MIGRATE_DECL→Weave (W5) likewise refuted — DROP decided (2026-06-01, ISSUES #28):** a targeted W3 run (`tools/migrate_decl_w3.py`, n=38 pooled MIGRATE_DECL scenarios → `merge-tool-comparison/reports_migrate_decl/FINDINGS.md`) found Weave wins **0** scenarios over Mergiraf (paired McNemar p=0.0078; its correct merges are a strict subset of Mergiraf's, and it abstains on all 7 Mergiraf dev-FPs), and the cluster is **not** a Mergiraf weakness under the test-suite oracle (0/7 Mergiraf dev-FPs fail tests — the dev-match FP was comparator-gap). **Both specialist arms (Spork/Weave) are refuted and the flip is LANDED (2026-06-27, #27/#28 resolved)**: default `auto` map is `NONE→git, everything-else→Mergiraf`; the refuted arms stay in code behind opt-in `SEMANTIC_MERGE_SPECIALIST_ROUTING=1` (apparatus — reproduces the pre-flip P2 behavior; `workspace/e2e_routing.sh` runs flag-on). P2 (2026-06-26, AWS) corroborated the DROP in vivo before the flip: pre-flip auto cost 1925 vs always-Mergiraf 1994, 21/239 good merges silently broken by the specialist arms vs 0 (v2 rescore per `merge-tool-comparison/reports_whole_driver/FINDINGS.md`; the earlier v1 figures 2055 / 33/239 are superseded).

## Memory

Auto-memory for sessions launched at the repo root lives at `~/.claude/projects/-Users-alikarimli-JupyterProjectsOfMine-my-data-project/memory/`. An older store from sessions launched inside the subproject sits at `~/.claude/projects/-Users-alikarimli-JupyterProjectsOfMine-my-data-project-merge-tool-comparison/memory/` and includes:

- `user_profile.md` — Ali's background, working style, prior presentations.
- `project_thesis_landscape.md` — how the two subprojects relate and their thesis role.
- `repo_layout.md` — gitignore rules, credential setup, safety backups.

Each store has its own `MEMORY.md` index. Update the active (top-level) store when the picture changes; consolidate from the subproject store if anything there is still load-bearing.
