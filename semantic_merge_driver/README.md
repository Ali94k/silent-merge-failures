# semantic_merge_driver

A custom Git merge driver that extends merging with post-merge **semantic analysis**. It runs a pluggable three-way merge backend (default: `auto` — RM2 cluster classifier routes to Mergiraf via Docker, with `git merge-file` as a single-shot fallback on Mergiraf crash; explicit `mergiraf` and `git` modes also available via env flag) and then runs a strategy pipeline on the merged result, rejecting the merge (exit 1) if any strategy flags a critical issue.

For thesis context and the unified pipeline design, see [`../README.md`](../README.md) and [`../ARCHITECTURE.md`](../ARCHITECTURE.md). For implementation status, see [`../STATUS.md`](../STATUS.md).

## Why

Text merges can succeed while introducing semantic bugs (stale reads, infinite loops, variable capture, method-rename staleness). This driver treats text merging as the fast path and adds static analysis as a gate: if the merged code fails a strategy's check, the merge is rejected so a human reviews it.

Seven semantic-conflict categories motivate the work — see [`ResearchSummary.xml`](ResearchSummary.xml):

1. Atomic Updates
2. Control Flow Interference (short circuit)
3. Data Flow Interference (stale read)
4. Exception Handling Divergence
5. Loop Semantics Divergence ← **only category with detection today** (2 strategies)
6. Method Rename
7. Scope Capture (variable shadowing)

## Target pipeline

The authoritative target design is in [`initial architecture.md`](initial%20architecture.md):

```
Input: base, ours, theirs
  → RefactoringMiner (refactor detection across branches)
  → Decision: refactor? → IntelliMerge : JDime/Spork (structured merge)
  → merged file
  → GumTree Edit Scripts (3-way AST diff)
  → Joern CPG Strategies
  → SafeMerge (optional Z3)
  → Accept / Reject
```

The runtime sequence for what is currently built is in [`core/sq.md`](core/sq.md).

## What is currently built

Out of the 7 target stages, 3 are implemented end-to-end and 2 are partial (Joern strategies and RM2 verification-side):

| Stage | Status | Code |
|---|---|---|
| Three-way merge backend (`auto` default; `mergiraf` / `git` via env) | ✅ | `core/backends/`, `core/driver.py` |
| RefactoringMiner runtime classifier (Cluster + language) | ✅ wired via `AutoBackend` (R4b) | `core/refactoring_classifier.py`, `core/language_detect.py`, `core/backends/auto_backend.py` |
| IntelliMerge / JDime / Spork switch | ⚠️ skeleton present — every cluster currently routes to Mergiraf; W5 (Weave) and S2 (Spork) will add per-cluster elif arms with their own evidence gates | `core/backends/auto_backend.py` |
| GumTree Edit Scripts | ✗ | — |
| Joern CPG Strategies | ⚠️ 2 strategies, category #5 Loop Semantics | `strategies/joern_strategies/` |
| RM2 verification-side strategy (R3) | ✅ 1 strategy, category #6 Method Rename | `strategies/rm2_strategies/rename_conflict.py` |
| SafeMerge / Z3 | ✗ | — |
| Accept / Reject | ✅ | `core/driver.py:run_merge` |

See [`../STATUS.md`](../STATUS.md) for detail on known bugs (β.1: fail-silent on shell-piped Joern queries — distinct from the prior fail-open and hardcoded-strategy bugs, both fixed in commit `044051f`).

## Requirements

- Python 3.10+
- [Joern](https://joern.io) on `PATH` — the strategies shell out to `joern-parse` and `joern`.
- Git (the driver is invoked by `git merge`).
- **Docker** — required by the default Mergiraf backend; the driver invokes `docker run merge-tools/mergiraf:0.17.0`. Build the image once: `cd ../merge-tool-comparison && make docker-build`. Per project rule ([`../CLAUDE.md`](../CLAUDE.md) standing rules), merge tools are accessed via Docker only — no host-PATH `mergiraf` binary. If Docker is unavailable, use the git-merge-file backend instead (see "Choosing a merge backend" below).

## Install

```bash
cd semantic_merge_driver
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Use as a git merge driver

Register the driver in your project's `.git/config`:

```ini
[merge "semantic-driver"]
    name = Semantic merge driver
    driver = /absolute/path/to/semantic_merge_driver/venv/bin/python /absolute/path/to/semantic_merge_driver/core/driver.py %O %A %B
```

(The `driver = …` value must be a single physical line. Backslash line continuation is not safe in unquoted git-config values.)

And enable it for Java files in `.gitattributes`:

```
*.java  merge=semantic-driver
```

Git will call `driver.py %O %A %B`, passing paths for ancestor / ours / theirs. The driver performs a text merge on the ours-side file in place, runs strategies, and returns exit 0 (accept) or 1 (reject).

## Run standalone

```bash
python core/driver.py <ancestor> <ours> <theirs>
```

Exit code 0 means both the merge succeeded and all strategies returned clean. Exit code 1 means either the merge produced textual conflicts, a strategy flagged a critical issue, or the backend itself crashed (fail-closed).

### Choosing a merge backend

The three-way merge step is performed by a `MergeBackend` implementation, selected at run-time via the `SEMANTIC_MERGE_BACKEND` environment variable:

| Value | Backend | What it is |
|---|---|---|
| `auto` (default) | `AutoBackend` | invokes the RM2 cluster classifier, logs `cluster=X language=Y → backend` to stderr, routes every cluster to Mergiraf today (W5/S2 will add per-cluster elif arms), and falls back once to `git merge-file` if Mergiraf crashes |
| `mergiraf` | `MergirafBackend` | `docker run merge-tools/mergiraf:0.17.0` — syntax-aware Rust merger, multi-language; bypasses the classifier |
| `git` | `GitMergeFileBackend` | inline `git merge-file` — line-based, universally available, fast, no Docker required; bypasses the classifier |

Examples:

```bash
# default — auto mode: classifier → Mergiraf, with git fallback on Mergiraf crash
python core/driver.py base.java ours.java theirs.java

# explicit mergiraf (skips the classifier; latency-sensitive workflows)
SEMANTIC_MERGE_BACKEND=mergiraf python core/driver.py base.java ours.java theirs.java

# explicit git-merge-file (recovers pre-M6-lite behaviour; no Docker required)
SEMANTIC_MERGE_BACKEND=git python core/driver.py base.java ours.java theirs.java
```

If the chosen backend fails (subprocess crash, missing Docker, missing image), the driver fails closed (exit 1) — never a silent accept. In `auto` mode, a Mergiraf CRASH triggers a one-shot fallback to `git merge-file`; if that also crashes, the driver fails closed. To use a non-default backend with `git merge`, set the env in the merge-driver wrapper or shell session before invoking git.

**Honest caveat:** until W5 / S2 add per-cluster elifs against the `AutoBackend` skeleton, `auto` mode is functionally identical to `mergiraf` mode plus a fallback line. The mechanism is real plumbing + per-merge classifier dispatch + cluster logging — the value is having the dispatch infrastructure in place so W5/S2 are pure additions, plus early classifier-correctness signal from production-style usage.

**Latency note:** `auto` invokes the RM2 classifier on every merge (two `docker run merge-tools/refactoring-miner:2.4.0` calls per merge, since RM2's API is pairwise — see [`../docs/plans/rm2-integration.md §1.1`](../docs/plans/rm2-integration.md)). Measured ~5.3s end-to-end on Apple Silicon (`--platform linux/amd64` via Rosetta/QEMU); native linux/amd64 is faster. For latency-sensitive workflows that don't need the classifier signal, set `SEMANTIC_MERGE_BACKEND=mergiraf` (or `=git`) to bypass the classifier entirely.

## Strategies

A strategy is a `MergeStrategy` subclass (see `core/interfaces.py`) that implements `analyze(file_path) -> AnalysisResult`. `AnalysisResult` has `is_clean: bool` and `issues: List[Issue]`; the driver rejects the merge if any strategy reports `is_clean=False` with any issue of severity `CRITICAL`.

### Implemented

| Strategy | File | What it detects | Maps to category |
|---|---|---|---|
| `JoernInfiniteLoopStrategy` | `strategies/joern_strategies/infinite_loop.py` | `while(true)` / `for(;;)` — constant-truthy loop headers in the merged file | #5 Loop Semantics Divergence |
| `JoernInvalidLoopBoundsStrategy` | `strategies/joern_strategies/invalid_loop_bounds.py` | Dead-loop headers where initializer > terminal condition (e.g., `for(i=15; i<10; i++)`) | #5 Loop Semantics Divergence |
| `RM2RenameConflictStrategy` (R3) | `strategies/rm2_strategies/rename_conflict.py` | RM2 on (base, merged): for each `Rename Method` / `Rename Class`, regex-scans the merged file for stale `\b<old_name>\s*\(` callers | #6 Method Rename |

The Joern strategies use Joern: `joern-parse` builds a `.cpg.bin` from the merged file, then a Scala script (inlined or generated on-the-fly) is piped into the `joern` REPL to query the CPG. The R3 strategy uses `docker run merge-tools/refactoring-miner:2.4.0` instead — one Docker call per merge, file-level. Within-file scope only; cross-file stale callers are out of scope for this MVP.

### Empty stubs (present but not implemented)

- `strategies/abstract_strategy.py` — intended base class; current strategies inherit directly from `core.interfaces.MergeStrategy` instead.
- `scala_queries/infinite_loop.sc` — intended external Scala query; currently the query is inlined in `infinite_loop.py`.

## Plugin loader

`core/plugin_loader.py` walks the `strategies/` package with `pkgutil`, finds every `MergeStrategy` subclass, and instantiates each one whose name appears in the optional `enabled_strategies` list (or all if no list is supplied). To add a new strategy:

1. Create `strategies/my_group/my_check.py` with a subclass of `MergeStrategy`.
2. Implement `analyze(file_path: str) -> AnalysisResult`.
3. Add the strategy's `name` to `config/strategies.yaml` under `enabled:`. Omit the file (or set `enabled: null`) to auto-load all discovered strategies.

No registration code required — discovery is automatic.

## Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

- [`tests/test_driver.py`](tests/test_driver.py) — driver orchestration, Python fixtures in `tests/data/ancestor.py` / `ours.py` / `theirs.py` reproducing an infinite-loop merge scenario. Tests inject `GitMergeFileBackend` explicitly.
- [`tests/test_invalid_loop.py`](tests/test_invalid_loop.py) — Java fixtures in `tests/data/loop_bounds/` reproducing a dead-loop merge (`for(i=15; i<10; i++)`).
- [`tests/test_fail_closed.py`](tests/test_fail_closed.py) — fail-closed behaviour of both Joern strategies under monkeypatched subprocess failures (β commit `044051f`).
- [`tests/test_strategy_config.py`](tests/test_strategy_config.py) — YAML config parsing in `core/config.py` + `StrategyLoader` filtering by enabled list (β commit `044051f`).
- [`tests/test_git_merge_file_backend.py`](tests/test_git_merge_file_backend.py) — `GitMergeFileBackend` contract: clean merge, conflict markers, fail-closed on missing `git`.
- [`tests/test_mergiraf_backend.py`](tests/test_mergiraf_backend.py) — `MergirafBackend` contract: clean merge, conflict markers, fail-closed on missing `docker`. Clean and conflict tests skip if Docker or the `merge-tools/mergiraf:0.17.0` image aren't available.
- [`tests/test_cluster_classifier.py`](tests/test_cluster_classifier.py) — `RefactoringClusterClassifier` contract: 98-entry table drift-detection, precedence resolution, fail-closed paths, plus one image-gated integration against `merge-tools/refactoring-miner:2.4.0`.
- [`tests/test_language_detect.py`](tests/test_language_detect.py) — `language_of()` extension mapping.
- [`tests/test_auto_backend.py`](tests/test_auto_backend.py) — `AutoBackend` dispatch contract with mocked classifier + sub-backends: every cluster routes to primary, CLEAN / CONFLICT outcomes propagate, primary-CRASH triggers single-shot fallback, double-CRASH propagates, classifier-exception is treated as NONE, stderr log format.
- [`tests/test_driver_dispatch.py`](tests/test_driver_dispatch.py) — `driver.main()` env handling: default is `auto`, all three modes resolvable, unknown name exits 1.
- [`tests/test_rename_conflict.py`](tests/test_rename_conflict.py) — `RM2RenameConflictStrategy` (R3): identifier extraction, stale-caller detection (single / multi-caller / multi-rename), qualified-caller (`this.foo()`) flagged but method-reference (`Foo::foo`) not, clean-when-no-renames / clean-when-no-callers, six fail-closed paths, plus one image-gated integration against `merge-tools/refactoring-miner:2.4.0`.

**Strategy detection** coverage is categories 5 + 6; categories 1, 2, 3, 4, 7 have no detection tests. The fail-closed, YAML-config, backend, classifier, language, dispatch, AutoBackend, and rename-conflict tests are infrastructure or per-strategy coverage, not additional category coverage.

## Project layout

```
semantic_merge_driver/
├── core/
│   ├── driver.py                   entry point; invoked by git
│   ├── interfaces.py               MergeStrategy ABC, AnalysisResult, Issue
│   ├── plugin_loader.py            auto-discovers MergeStrategy subclasses
│   ├── config.py                   reads config/strategies.yaml (enabled list)
│   ├── backends/                   MergeBackend implementations (3-way merge step)
│   │   ├── base.py                 MergeBackend ABC + MergeOutcome enum
│   │   ├── git_merge_file_backend.py    wraps `git merge-file`
│   │   ├── mergiraf_backend.py     invokes merge-tools/mergiraf:0.17.0 Docker image
│   │   └── auto_backend.py         R4b — classifier-driven dispatch + git fallback on crash
│   ├── refactoring_classifier.py   R4a — RM2 cluster classifier (`merge-tools/refactoring-miner:2.4.0`)
│   ├── language_detect.py          R4a — extension→Language enum
│   └── sq.md                       runtime sequence diagram
├── strategies/
│   ├── abstract_strategy.py        (empty stub)
│   ├── joern_strategies/
│   │   ├── infinite_loop.py        detects while(true) / for(;;)
│   │   ├── invalid_loop_bounds.py  detects dead-loop headers
│   │   └── taint_check.py          detects stale reads (clear-then-read, category #3)
│   └── rm2_strategies/
│       └── rename_conflict.py      R3 — RM2 stale-caller detector (category #6)
├── scala_queries/
│   └── infinite_loop.sc            (empty stub)
├── config/
│   └── strategies.yaml             enabled-strategies list (YAML)
├── tests/
│   ├── test_driver.py                       3 tests, driver orchestration
│   ├── test_invalid_loop.py                 2 tests, Java fixtures
│   ├── test_fail_closed.py                  4 cases, Joern strategy fail-safety
│   ├── test_strategy_config.py              9 tests, YAML config + loader filter
│   ├── test_git_merge_file_backend.py       3 tests, GitMergeFileBackend contract
│   ├── test_mergiraf_backend.py             3 tests, MergirafBackend contract (2 skip if no Docker)
│   ├── test_cluster_classifier.py           17 functions / 27 cases, classifier (1 image-gated)
│   ├── test_language_detect.py              1 function / 13 cases, language_of mapping
│   ├── test_auto_backend.py                 11 functions / 17 cases, AutoBackend dispatch (mocked)
│   ├── test_driver_dispatch.py              5 functions / 7 cases, env→backend wiring
│   ├── test_rename_conflict.py              17 functions / 21 cases, R3 strategy (1 image-gated)
│   └── data/                                fixtures (.py and Java)
├── initial architecture.md         **authoritative target pipeline**
├── ResearchSummary.xml             7-category taxonomy with worked Java examples
└── requirements.txt
```

## References

- [Joern](https://joern.io) — Code Property Graph static-analysis engine.
- [RefactoringMiner](https://github.com/tsantalis/RefactoringMiner) — Tsantalis et al.; target for the pre-merge stage.
- GumTree — Falleri et al., "Fine-grained and Accurate Source Code Differencing."
- IntelliMerge — Shen et al., 2019.
- JDime — Apel et al. 2011, Seibt et al. 2022.
- Spork — ASSERT-KTH.
- SafeMerge — target for the optional Z3 verification stage.
