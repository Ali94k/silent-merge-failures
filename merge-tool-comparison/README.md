# merge-tool-comparison

Empirical evaluation framework replicating **Schesch et al., "Evaluation of Version Control Merge Tools" (ASE 2024).** Runs multiple 3-way merge tools on Java merge scenarios and classifies their outputs (TP/FP/TN/FN/CRASH/TIMEOUT) against the developer's actual resolution as ground truth.

For thesis context, see [`../README.md`](../README.md) and [`../ARCHITECTURE.md`](../ARCHITECTURE.md). For implementation status and known bugs, see [`../STATUS.md`](../STATUS.md) and [`ISSUES.md`](ISSUES.md).

## Tools under evaluation

| Tool | Type | Invocation | Reference |
|---|---|---|---|
| `git merge-file` | textual | native | baseline |
| **JDime** | structured (AST) | Docker | Apel et al. 2011 / Seibt et al. 2022 |
| **Spork** | structured + move support | Docker | ASSERT-KTH |
| **Mastery** | structured (shifted-code-aware) | Docker | Zhu et al., SETTA 2022 |

Adding a fifth tool requires one Python adapter, one Dockerfile, and one `config/tools.yaml` entry — see [Adding a new merge tool](#adding-a-new-merge-tool).

## Requirements

- Python 3.10+
- Docker (with `linux/amd64` support; Rosetta on Apple Silicon works but is slow)
- Git

## Install

```bash
cd merge-tool-comparison
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run the full pipeline

```bash
# Default: Schesch et al. dataset as input, all 4 tools, all 4 report formats
make all

# Or step by step:
make docker-build      # build JDime/Spork/Mastery images
make load-dataset      # load scenarios from data/schesch-dataset/
make run               # run all tools on all scenarios
make evaluate          # classify results against developer resolutions
make report            # write reports/{results.csv, results.json, results.tex}
```

CLI equivalents (from `src/cli.py`):

```bash
python -m src.cli all --source dataset --max-scenarios 50
python -m src.cli load-dataset
python -m src.cli collect            # legacy: mine from config/repos.yaml
python -m src.cli run
python -m src.cli evaluate
python -m src.cli report --format console --format csv --format json --format latex
```

Scenario- and result-level caching is automatic. Re-running `run` skips already-computed (scenario × tool) pairs; re-running `load-dataset` skips already-extracted scenarios (use `--force` to re-extract).

## Data sources

### Schesch dataset (default)

External dataset from the ASE 2024 paper, downloaded from the [Zenodo record](https://zenodo.org/records/13366866) or [the paper's GitHub repo](https://github.com/benedikt-schesch/AST-Merging-Evaluation), placed at `data/schesch-dataset/` (gitignored; ~661 MB).

Loader: [`src/data/schesch_loader.py`](src/data/schesch_loader.py). Config: [`config/datasets.yaml`](config/datasets.yaml).

### Legacy github-mining path

Clone target repos listed in [`config/repos.yaml`](config/repos.yaml), find merge commits, extract (base, ours, theirs, developer_resolution) per file. Biased toward recent, simpler merges (see [`ISSUES.md`](ISSUES.md) #6).

Collector: [`src/data/collector.py`](src/data/collector.py).

## Architecture (inside this project)

```
config/{datasets,repos}.yaml
        │
        ▼
  schesch_loader.py / collector.py
        │
        ▼
  data/scenarios/*.json              (MergeScenario JSON)
        │
        ▼
  core/runner.py (ComparisonRunner)
        │   per (scenario × tool): cache-aware
        ▼
  data/results/{scenario_id}/{tool}.json
        │
        ▼
  evaluation/comparator.py
        │   classify → TP/FP/TN/FN/CRASH/TIMEOUT
        ▼
  evaluation/metrics.py
        │   precision, recall, F1, weighted cost
        ▼
  evaluation/report.py
        │
        ▼
  reports/results.{csv, json, tex}
```

Key abstractions live in [`src/core/interfaces.py`](src/core/interfaces.py):

- **`MergeScenario`** — one file-level merge: `base_content`, `ours_content`, `theirs_content`, `developer_resolution`, plus metadata.
- **`MergeResult`** — tool output: `outcome` (`CLEAN`/`CONFLICT`/`CRASH`/`TIMEOUT`), `merged_content`, `conflict_count`, `runtime_seconds`.
- **`MergeTool`** (ABC) — tool adapter contract: `.name`, `.docker_image`, `.merge(base, ours, theirs, timeout)`.

## Classification rules

From [`src/evaluation/comparator.py`](src/evaluation/comparator.py):

| Tool output | Condition | Label |
|---|---|---|
| CLEAN | matches dev resolution | **TP** |
| CLEAN | differs from dev resolution | **FP** — silent wrong merge (worst case) |
| CONFLICT | dev reverted to base | **FN** — false alarm |
| CONFLICT | dev picked a side, both changed | **TN** — real conflict |
| CONFLICT | dev picked a side, only one changed | **FN** — false alarm |
| CONFLICT | dev wrote a novel resolution | **TN** — real conflict |
| CRASH / TIMEOUT | — | tracked separately |

Content equality uses `normalize_content()` (strips trailing whitespace, normalizes line endings, drops trailing blank lines). **This is the known FP-inflation risk** for AST-reformatting tools; see [`ISSUES.md`](ISSUES.md) #2.

## Metrics

From [`src/evaluation/metrics.py`](src/evaluation/metrics.py):

- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **F1** = 2·P·R / (P + R)
- **Incorrect merge rate** = FP / (TP + FP)
- **Weighted cost (Schesch model)** = TP·0 + FP·10 + (FN+TN)·1 + (CRASH+TIMEOUT)·1

## Project layout

`tools/rm2_fharness.py` and `docker/refactoring_miner/` are R0 reconnaissance instruments for the upcoming RM2 integration ([../docs/plans/rm2-integration-recon.md](../docs/plans/rm2-integration-recon.md)) — not part of the 4-tool comparison.

```
merge-tool-comparison/
├── src/
│   ├── cli.py                      Click CLI entry point
│   ├── core/
│   │   ├── interfaces.py           MergeTool ABC, MergeResult, MergeScenario
│   │   ├── runner.py               ComparisonRunner (orchestration + caching)
│   │   ├── docker_runner.py        docker run wrapper + workspace helpers
│   │   └── plugin_loader.py        dynamic tool discovery via pkgutil
│   ├── tools/
│   │   ├── git_merge_file.py       native
│   │   ├── jdime.py                Docker
│   │   ├── spork.py                Docker
│   │   └── mastery.py              Docker
│   ├── data/
│   │   ├── schesch_loader.py       default data source
│   │   └── collector.py            legacy github-mining path
│   └── evaluation/
│       ├── comparator.py           classify TP/FP/TN/FN/CRASH/TIMEOUT
│       ├── metrics.py              precision/recall/F1/weighted-cost
│       └── report.py               console/CSV/JSON/LaTeX writers
├── config/
│   ├── datasets.yaml               Schesch dataset path + filters
│   ├── repos.yaml                  GitHub repos for legacy collection
│   └── tools.yaml                  tool registry
├── docker/
│   ├── git-merge-file/Dockerfile
│   ├── jdime/Dockerfile
│   ├── spork/Dockerfile
│   ├── mastery/Dockerfile
│   └── refactoring_miner/          RM 2.4.0 image (Dockerfile + DirPairMain.java wrapper) — R0 reconnaissance
├── tools/
│   └── rm2_fharness.py             R0 file-vs-project recall delta harness
├── tests/                          37 tests (pytest)
├── reports/                        generated output (results.{csv,json,tex} tracked; other artefacts gitignored)
├── data/                           gitignored runtime data
│   ├── repos/                      cloned Java sources (legacy path)
│   ├── schesch-dataset/            Schesch et al. Zenodo dataset
│   ├── scenarios/                  extracted scenario JSONs
│   └── results/                    cached tool outputs
├── ISSUES.md                       live issue tracker (24 items; 3 resolved)
├── PRESENTATION_PLAN.md            deck outline
├── Makefile
└── pyproject.toml
```

## Adding a new merge tool

1. Create `src/tools/my_tool.py`:

   ```python
   from src.core.interfaces import MergeTool, MergeResult, MergeOutcome
   from src.core.docker_runner import run_in_docker, write_workspace_files

   class MyTool(MergeTool):
       @property
       def name(self): return "my-tool"

       @property
       def docker_image(self): return "merge-tools/my-tool"

       def merge(self, base, ours, theirs, timeout=60) -> MergeResult:
           ...  # write workspace, run, read output, count conflict markers
   ```

2. Create `docker/my-tool/Dockerfile`.

3. Add to `config/tools.yaml`:

   ```yaml
   - name: my-tool
     adapter: my_tool
     docker_image: merge-tools/my-tool
     timeout: 120
     enabled: true
   ```

`plugin_loader.py` auto-discovers subclasses of `MergeTool` — no registration code needed.

## Testing

```bash
source .venv/bin/activate
pytest tests/ -v
```

Tested: `comparator`, `metrics`, `interfaces`, `git_merge_file`, `mastery`, `schesch_loader` (including CLI caching).
Not tested: `jdime`, `spork`, `docker_runner`, `plugin_loader`, `cli` (non-load-dataset commands), `collector`. See [`ISSUES.md`](ISSUES.md) #14.

## Current headline numbers

From `reports/results.csv` at n=50:

| Tool | TP | FP | TN | FN | CRASH | F1 | Weighted cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| git-merge-file | 39 | 0 | 10 | 1 | 0 | 0.987 | 11 |
| JDime | 0 | 2 | 0 | 0 | 48 | 0.000 | 68 |
| Mastery | 0 | 44 | 6 | 0 | 0 | 0.000 | 446 |
| Spork | 1 | 42 | 6 | 1 | 0 | 0.044 | 427 |

**Caveat:** the JDime crash rate and the Spork/Mastery FP counts are almost certainly partly measurement artefacts (Docker build failures and textual-normalization limits respectively). Before citing, resolve [`ISSUES.md`](ISSUES.md) #2.

## References

- **Schesch et al. 2024 (ASE)** — *Evaluation of Version Control Merge Tools.* [Zenodo](https://zenodo.org/records/13366866) · [GitHub](https://github.com/benedikt-schesch/AST-Merging-Evaluation)
- Apel et al. 2011, Seibt et al. 2022 — JDime
- ASSERT-KTH — Spork
- Zhu et al. 2022 (SETTA) — Mastery
- Cavalcanti et al. 2017 — *Evaluating and Improving Semistructured Merge*
