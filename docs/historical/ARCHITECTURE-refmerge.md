# Semantic Merge Driver — Architecture & Implementation Roadmap

## 1. Project Overview

### 1.1 Problem Statement

Standard Git merge tools (e.g., `git merge-file`, `diff3`) operate at the textual/line level. When two branches modify different lines, the merge succeeds — even if the combined changes introduce **semantic bugs**. These are called **semantic merge conflicts**: merges that are textually clean but logically broken.

Refactoring operations are implicated in up to 22% of all merge conflicts and tend to produce substantially larger and more complex conflict blocks. Textual merge tools are entirely agnostic to the syntactic structures and semantic behaviors of programming languages, so when developers execute structural transformations — renaming methods, extracting classes, or moving fields — concurrently with independent edits to the same logical blocks, textual merging tools inevitably fail. This failure manifests as false positive conflicts (semantically compatible changes flagged as conflicts) and, more dangerously, false negative conflicts (silent merges that introduce compilation failures, broken tests, or runtime regressions).

### 1.2 Research Goal

Build a **pluggable, multi-layered Git merge driver** that combines tree-sitter-based structural merging, refactoring-aware operation-based merging (via RefactoringMiner 3.0 and RefMerge), and Code Property Graph semantic analysis (via Joern) to detect and reject semantic merge conflicts that textual tools miss.

### 1.3 Conflict Categories (Dataset)

The project defines 7 categories of semantic merge conflicts, each with Java test cases:

| # | Category | Directory | Description |
|---|----------|-----------|-------------|
| 1 | Atomic Updates | `atomic_updates` | Concurrent changes violate invariant (e.g., min > max) |
| 2 | Control Flow Interference | `cfi_short_circuit` | Early return bypasses newly added audit logic |
| 3 | Data Flow Interference (Stale Read) | `dfi_stale_read` | One branch clears a list; the other iterates it |
| 4 | Exception Handling Divergence | `exception_handling` | Narrowed catch block misses new exception type |
| 5 | Loop Semantics Divergence | `loop_semantics_divergence` | Merged changes create infinite loop |
| 6 | Method Rename | `method_rename` | Dangling reference after rename + new caller |
| 7 | Scope Capture (Variable Shadowing) | `scope_capture` | Local variable shadows field, breaking validation |

### 1.4 Design Principles

The architecture is guided by four principles derived from empirical evaluation of existing merge architectures:

1. **Eliminate redundancy.** Do not run separate tools for AST differencing and refactoring detection when a single tool (RefactoringMiner 3.0 / RM-ASTDiff) unifies both with superior precision.
2. **Prefer operation-based over graph-based merging.** Empirical evidence from 2,001 merge scenarios across 20 open-source projects demonstrates that operation-based refactoring-aware merging (RefMerge) nearly doubles the resolution rate of graph-based approaches (IntelliMerge) while completely eliminating false negatives.
3. **Syntax-aware by default.** Replace the textual baseline with a tree-sitter-backed structural merge engine that understands language grammar, eliminating formatting and ordering conflicts at the merge level.
4. **Mandatory semantic verification.** Joern CPG analysis is a required stage of the pipeline, not an optional or deferred step. Semantic conflicts (stale reads, infinite loops, scope capture) can only be detected through dataflow and control flow analysis on the merged result.

---

## 2. Current Architecture (Baseline — Step 0)

### 2.1 Components

```
┌────────────────────────────────────────────────────────┐
│                  SemanticMergeDriver                   │
│                   (core/driver.py)                     │
│                                                        │
│  1. git merge-file (textual 3-way merge)              │
│  2. StrategyLoader → loads MergeStrategy plugins      │
│  3. Run each strategy's analyze() on merged file      │
│  4. Accept (exit 0) or Reject (exit 1)                │
└────────────────────────────────────────────────────────┘
```

### 2.2 File Structure

```
semantic_merge_driver/
├── core/
│   ├── __init__.py
│   ├── driver.py              # Entry point, orchestrates merge + analysis
│   ├── interfaces.py          # MergeStrategy ABC, Issue, AnalysisResult
│   └── plugin_loader.py       # Dynamic strategy discovery
├── strategies/
│   ├── __init__.py
│   ├── abstract_strategy.py
│   └── joern_strategies/
│       ├── __init__.py
│       ├── infinite_loop.py       # Detects while(true)/for(;;) via CPG
│       ├── invalid_loop_bounds.py # Detects dead loops via CPG
│       └── taint_check.py         # Placeholder
├── scala_queries/
│   └── infinite_loop.sc
├── config/
│   └── strategies.yaml
├── tests/
│   ├── data/
│   ├── test_driver.py
│   └── test_invalid_loop.py
└── workspace/
```

### 2.3 Plugin Interface

```python
# core/interfaces.py
class MergeStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def analyze(self, file_path: str, base_content: str = None) -> AnalysisResult: ...

@dataclass
class AnalysisResult:
    is_clean: bool
    issues: List[Issue]

@dataclass
class Issue:
    line_number: int
    severity: str       # 'CRITICAL', 'WARNING'
    message: str
    strategy_name: str
```

### 2.4 Baseline Capabilities

| Conflict Category | Detected? | Strategy |
|-------------------|-----------|----------|
| Infinite Loop | Yes | JoernInfiniteLoop |
| Invalid Loop Bounds | Yes | JoernInvalidLoopBounds |
| Atomic Updates | No | — |
| Control Flow Interference | No | — |
| Data Flow Interference | No | — |
| Exception Handling | No | — |
| Method Rename | No | — |
| Scope Capture | No | — |

### 2.5 Known Limitations of the Baseline

The current baseline has several operational issues that will be addressed across subsequent steps:

- `requirements.txt` is empty; external dependencies (Joern, Git) are undocumented
- `strategies.yaml` is empty; strategy selection is hardcoded in `driver.py`
- `taint_check.py` and `abstract_strategy.py` are empty placeholders
- Joern Scala queries are built as inline strings rather than using dedicated `.sc` files
- Strategies fail open (return `is_clean=True` on errors) — must be changed to fail closed
- Error handling and timeout management are absent

---

## 3. Target Architecture (Final Pipeline)

### 3.1 Full Pipeline Diagram

```
                     Input: base, ours, theirs
                              │
                    ┌─────────▼──────────┐
                    │  RM-ASTDiff        │   Pre-merge analysis
                    │  (RefactoringMiner │   Unified AST differencing +
                    │   3.0)             │   refactoring detection
                    │                    │   100+ refactoring types
                    │  Detects: renames, │   Multi-mapping support
                    │  extractions,      │   (1-to-n, n-to-1)
                    │  inlines, moves    │
                    └────────┬───────────┘
                             │
              ┌──────────────┴──────────────┐
              │ Refactoring detected?       │
         Yes  │                        No   │
    ┌─────────▼──────────┐    ┌─────────────▼──────────┐
    │  RefMerge           │    │  Mergiraf              │
    │  (operation-based   │    │  (tree-sitter-backed   │
    │   refactoring-aware │    │   structural merge)    │
    │   merge via invert, │    │                        │
    │   merge, replay)    │    │  Syntax-aware, fast,   │
    └─────────┬───────────┘    │  handles ordering &    │
              │                │  formatting conflicts  │
              │                └─────────────┬──────────┘
              └──────────────┬───────────────┘
                             │  merged file
              ┌──────────────▼──────────────┐
              │  Joern CPG Analysis         │   Mandatory semantic
              │  (Code Property Graph)      │   verification stage
              │                             │
              │  Strategies:                │
              │  - Infinite loop detection  │
              │  - Invalid loop bounds      │
              │  - Dataflow interference    │
              │  - Control flow analysis    │
              │  - Scope capture detection  │
              │  - Taint analysis           │
              └──────────────┬──────────────┘
                             │
                     Accept (exit 0) / Reject (exit 1)
```

### 3.2 Tool Summary

| Layer | Tool | Language | Invocation | Purpose |
|-------|------|----------|------------|---------|
| Pre-merge | RefactoringMiner 3.0 (RM-ASTDiff) | Java | CLI / Java API | Unified AST differencing + refactoring detection (100+ types, 99.6% precision) |
| Merge (refactoring) | RefMerge | Java | CLI | Operation-based refactoring-aware merge (invert → merge → replay) |
| Merge (standard) | Mergiraf | Rust | CLI (`mergiraf merge`) | Tree-sitter-backed structural merge, syntax-aware conflict resolution |
| Analysis (semantic) | Joern | Scala/Java | CLI (`joern-parse`, `joern`) | CPG generation + dataflow/control flow/taint analysis |

### 3.3 Architectural Rationale

**Why RM-ASTDiff instead of GumTree + RefactoringMiner 2.0:**
RefactoringMiner 3.0 (also known as RM-ASTDiff) unifies AST differencing and refactoring detection into a single tool. It breaks the strict one-to-one mapping constraint enforced by GumTree, natively supporting one-to-many and many-to-one mappings. By leveraging language-specific semantic clues (such as method call injection to locate extracted method bodies), it achieves flawless 100% precision in inter-file mapping. Running GumTree for AST differencing and then a separate RefactoringMiner pass for refactoring detection is computationally wasteful when RM-ASTDiff does both, better, in one pass. RM-ASTDiff also expands support to over 100 refactoring types (vs. 40 in RM 2.0) and natively supports Python and Kotlin in addition to Java.

**Why RefMerge instead of IntelliMerge:**
Empirical evidence from a rigorous study of 2,001 merge scenarios across 20 open-source projects demonstrates that IntelliMerge's graph-based approach is fundamentally flawed at scale. IntelliMerge completely resolved only 4% of refactoring-related conflicts while actively *increasing* conflicting lines of code in 30% of scenarios (median increase of 169%). In a 50-scenario qualitative sample, IntelliMerge introduced 707 false positive conflict blocks (a 192% increase over standard Git) and 71 false negatives (a 1,320% increase in dangerous semantic conflicts). RefMerge, using the operation-based paradigm, nearly doubled IntelliMerge's resolution rate (7% vs 4%), reduced false positives by 23% compared to Git, and completely eliminated false negatives. RefMerge's invert-merge-replay approach treats refactorings as discrete mathematical operations that can be inverted and replayed, eliminating the threshold-induced graph matching failures that plague IntelliMerge.

**Why Mergiraf instead of JDime/Spork:**
JDime and Spork are strictly and exclusively engineered for the Java programming language. JDime relies on an extensible Java compiler; Spork relies on the Spoon library for AST representation, which is entirely Java-dependent. While this project focuses on Java, Mergiraf provides a production-ready, tree-sitter-backed structural merge engine written in Rust that understands Java syntax through declarative grammar definitions. Mergiraf operates on a hybrid methodology: it defaults to fast line-based merging and only engages its tree-aware matching engine when a conflict occurs. It requires no complex threshold tuning, understands language-specific commutativity semantics (e.g., import ordering), and employs strict safety heuristics — falling back to conflict markers when uncertain. This makes it suitable for use as a direct replacement for the default Git merge driver with negligible latency overhead.

**Why Joern CPG as mandatory:**
Semantic conflicts — stale reads, infinite loops, scope capture, control flow interference — can only be detected through dataflow and control flow analysis on the merged result. No amount of structural merging or refactoring detection can substitute for analyzing how the merged code actually behaves. Joern's Code Property Graph unifies the AST, Control Flow Graph (CFG), and Program Dependence Graph (PDG) into a single queryable structure, making it the appropriate tool for this class of analysis. While CPG generation introduces latency, this cost is justified because the entire purpose of the project is to catch semantic conflicts that all other layers miss.

### 3.4 Extended Strategy Interface

The `MergeStrategy` interface is extended to receive merge context (refactoring metadata, branch information) in addition to the merged file:

```python
# core/interfaces.py (extended)
@dataclass
class MergeContext:
    base_path: str
    ours_path: str
    theirs_path: str
    merged_path: str
    refactorings_ours: List[dict]    # RM-ASTDiff output for base→ours
    refactorings_theirs: List[dict]  # RM-ASTDiff output for base→theirs
    merge_backend_used: str          # "mergiraf" | "refmerge" | "git"

class MergeStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def analyze(self, context: MergeContext) -> AnalysisResult: ...

@dataclass
class AnalysisResult:
    is_clean: bool
    issues: List[Issue]

@dataclass
class Issue:
    line_number: int
    severity: str       # 'CRITICAL', 'WARNING'
    message: str
    strategy_name: str
```

### 3.5 Strategy Directory Structure

```
strategies/
├── joern_strategies/
│   ├── __init__.py
│   ├── infinite_loop.py           # CPG: while(true)/for(;;)
│   ├── invalid_loop_bounds.py     # CPG: dead loops (start > end)
│   ├── dataflow_interference.py   # CPG: stale reads, cleared collections
│   ├── control_flow_analysis.py   # CPG: early return bypassing new logic
│   ├── scope_capture.py           # CPG: variable shadowing across branches
│   └── taint_analysis.py          # CPG: taint propagation through merge
├── refactoring_strategies/
│   ├── __init__.py
│   └── refactoring_conflict.py    # RM-ASTDiff: dangling refs, lost changes
└── structural_strategies/
    ├── __init__.py
    └── atomic_update_check.py     # Structural: invariant violation detection
```

### 3.6 Driver Architecture

```python
# Proposed driver flow (pseudocode)
class SemanticMergeDriver:
    def __init__(self, config: dict):
        self.rm_astdiff = RMASTDiffAnalyzer()
        self.merge_router = MergeRouter()
        self.loader = StrategyLoader(config)

    def run_merge(self, base: str, ours: str, theirs: str) -> int:
        # Phase 1: Pre-merge refactoring analysis (RM-ASTDiff)
        refactorings = self.rm_astdiff.analyze(base, ours, theirs)

        # Phase 2: Select and execute merge backend
        backend = self.merge_router.select(refactorings)
        merged = backend.merge(base, ours, theirs)

        # Phase 3: Build context for downstream strategies
        context = MergeContext(
            base_path=base,
            ours_path=ours,
            theirs_path=theirs,
            merged_path=merged,
            refactorings_ours=refactorings.ours,
            refactorings_theirs=refactorings.theirs,
            merge_backend_used=backend.name
        )

        # Phase 4: Run all analysis strategies (including mandatory Joern CPG)
        strategies = self.loader.load_strategies()
        all_issues = []
        for strategy in strategies:
            result = strategy.analyze(context)
            all_issues.extend(result.issues)

        # Phase 5: Verdict
        critical_issues = [i for i in all_issues if i.severity == 'CRITICAL']
        if critical_issues:
            self._report_issues(critical_issues)
            return 1  # Reject
        return 0  # Accept
```

### 3.7 Merge Backend Abstraction

```python
# core/merge_backends.py
class MergeBackend(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def merge(self, base: str, ours: str, theirs: str) -> MergeResult: ...

@dataclass
class MergeResult:
    success: bool
    merged_path: str
    conflicts: List[str]    # Unresolved conflict regions, if any

class GitMergeBackend(MergeBackend):
    """Baseline textual 3-way merge via git merge-file."""
    name = "git"
    def merge(self, base, ours, theirs):
        result = subprocess.run(["git", "merge-file", ours, base, theirs], ...)
        return MergeResult(success=result.returncode == 0, merged_path=ours)

class MergirafBackend(MergeBackend):
    """Tree-sitter-backed structural merge via Mergiraf."""
    name = "mergiraf"
    def merge(self, base, ours, theirs):
        # mergiraf merge <base> <ours> <theirs> --output <merged>
        ...

class RefMergeBackend(MergeBackend):
    """Operation-based refactoring-aware merge.
    Uses RefMerge's invert-merge-replay pipeline:
    1. Detect refactorings on both branches (via RM-ASTDiff)
    2. Simplify: collapse transitive refactoring chains
    3. Invert refactorings to produce refactoring-free code
    4. Run textual merge on purified code
    5. Check refactoring conflict matrix (commutative vs conflicting)
    6. Replay valid refactorings sequentially onto merged code
    """
    name = "refmerge"
    def merge(self, base, ours, theirs):
        ...

class MergeRouter:
    """Routes to RefMerge if refactorings detected, Mergiraf otherwise."""
    def select(self, refactorings) -> MergeBackend:
        has_refactorings = (
            len(refactorings.ours) > 0 or len(refactorings.theirs) > 0
        )
        if has_refactorings:
            return RefMergeBackend()
        return MergirafBackend()
```

---

## 4. Implementation Roadmap (Step-by-Step)

Each step adds one major capability. Each step is independently testable. Results from each step are compared against the previous step using the same 7 conflict categories.

### 4.0 Step 0 — Establish Baseline (Current State)

**Status**: Done

**Architecture**:
```
git merge-file ──► Joern strategies ──► Accept/Reject
```

**Tasks**:
- [ ] Create a standardized test suite with all 7 conflict categories as merge scenarios
- [ ] Run each scenario through the current driver
- [ ] Record baseline metrics: TP, FP, FN per category
- [ ] Document which categories are detected and which are missed
- [ ] Fix fail-open behavior: strategies must fail closed (reject on error, not accept)
- [ ] Populate `requirements.txt` with actual dependencies
- [ ] Move inline Scala queries to dedicated `.sc` files in `scala_queries/`

**Expected detection**: Only infinite loop and invalid loop bounds (2 of 7 categories).

---

### 4.1 Step 1 — Replace Textual Merge with Mergiraf (Tree-Sitter Structural Merge)

**Architecture**:
```
Mergiraf (tree-sitter) ──► Joern strategies ──► Accept/Reject
```

**What changes**:
- Modify `core/driver.py` to support configurable merge backends
- New file: `core/merge_backends.py` with `MergeBackend` ABC, `GitMergeBackend`, `MergirafBackend`
- Update `config/strategies.yaml` to include merge backend configuration

**Implementation**:
```python
class MergirafBackend(MergeBackend):
    """
    Tree-sitter-backed structural merge via Mergiraf.

    Mergiraf operates on a hybrid methodology:
    1. Defaults to fast line-based merging
    2. When a textual conflict is detected, engages tree-aware matching
    3. Parses conflict regions using tree-sitter Java grammar
    4. Attempts structural reconciliation of divergent AST subtrees
    5. Falls back to conflict markers if structural merge is uncertain

    Mergiraf understands Java-specific commutativity:
    - Import statement ordering does not matter
    - Annotation ordering on methods/classes does not matter

    Invocation:
        mergiraf merge <base> <ours> <theirs> -o <output>

    Safety: If the syntax-aware merge appears too optimistic or encounters
    a suspicious structural anomaly, Mergiraf immediately falls back to
    inserting conflict markers, prioritizing safety over automated guesswork.
    """
    name = "mergiraf"

    def merge(self, base, ours, theirs):
        output = tempfile.mktemp(suffix=".java")
        result = subprocess.run(
            ["mergiraf", "merge", base, ours, theirs, "-o", output],
            capture_output=True, text=True, timeout=30
        )
        return MergeResult(
            success=result.returncode == 0,
            merged_path=output,
            conflicts=self._extract_conflicts(result.stdout)
        )
```

**Requires**:
- Mergiraf installed (Rust binary, available via cargo or GitHub releases)
- Tree-sitter Java grammar (bundled with Mergiraf)

**Evaluation**:
- Run all 7 categories through Step 0 (git merge-file) and Step 1 (Mergiraf)
- Compare: does Mergiraf produce cleaner merged output for Joern to analyze?
- Compare: does Mergiraf resolve any textual conflicts that `git merge-file` generates?
- Measure latency overhead of Mergiraf vs `git merge-file`
- Expected: fewer false positives from Joern due to cleaner merged output; resolution of import/formatting conflicts that confuse textual merge

**Key references**:
- Mergiraf documentation and GitHub repository
- ThoughtWorks Technology Radar entry for Mergiraf

---

### 4.2 Step 2 — Add RM-ASTDiff + RefMerge (Refactoring-Aware Merge Layer)

**Architecture**:
```
RM-ASTDiff (pre-merge) ─┬─ refactoring found ──► RefMerge ───────┐
                         └─ no refactoring ─────► Mergiraf ───────┤
                                                                   ▼
                                                          Joern CPG Analysis
                                                                   │
                                                           Accept / Reject
```

**What changes**:
- New file: `core/rm_astdiff.py` — RM-ASTDiff integration for pre-merge analysis
- New file: `core/merge_backends.py` — add `RefMergeBackend`
- New file: `core/merge_router.py` — routing logic based on RM-ASTDiff output
- New file: `strategies/refactoring_strategies/__init__.py`
- New file: `strategies/refactoring_strategies/refactoring_conflict.py`
- Modify `core/driver.py` — integrate pre-merge analysis and routing
- Modify `core/interfaces.py` — add `MergeContext` dataclass

**RM-ASTDiff Integration**:
```python
class RMASTDiffAnalyzer:
    """
    Runs RefactoringMiner 3.0 (RM-ASTDiff) on both branches to perform
    unified AST differencing and refactoring detection in a single pass.

    Key advantages over GumTree + RefactoringMiner 2.0:
    - Supports 100+ refactoring types (vs 40 in RM 2.0)
    - Multi-mapping support: one-to-many and many-to-one AST node mappings
    - No arbitrary similarity thresholds (threshold-less detection)
    - Uses language-specific semantic clues for precise mapping
    - Natively supports Java, Python, and Kotlin

    Invocation:
        java -jar RefactoringMiner.jar -c <repo_path> <commit_hash>
        OR for file-level comparison:
        java -jar RefactoringMiner.jar -bf <base_file> <changed_file>

    Output: JSON listing detected refactorings with:
        - type (e.g., "Rename Method", "Extract Method", "Inline Method")
        - source location (file, class, method, line range)
        - target location
        - AST edit script (node mappings)
    """
    def analyze(self, base, ours, theirs) -> RefactoringResult:
        # 1. Run RM-ASTDiff on base→ours
        ours_refactorings = self._detect(base, ours)
        # 2. Run RM-ASTDiff on base→theirs
        theirs_refactorings = self._detect(base, theirs)
        return RefactoringResult(ours=ours_refactorings, theirs=theirs_refactorings)

    def _detect(self, file_a, file_b) -> List[dict]:
        result = subprocess.run(
            ["java", "-jar", "RefactoringMiner.jar", "-bf", file_a, file_b],
            capture_output=True, text=True, timeout=60
        )
        return json.loads(result.stdout)
```

**RefMerge Integration**:
```python
class RefMergeBackend(MergeBackend):
    """
    Operation-based refactoring-aware merge using RefMerge's pipeline.

    RefMerge operates in five precise steps:
    1. DETECT: Use RM-ASTDiff to detect refactorings on both branches
    2. SIMPLIFY: Collapse transitive refactoring chains
       (e.g., A→B then B→C becomes A→C)
       Also tracks cross-element refactoring chains
       (e.g., method rename tracked through parent class rename)
    3. INVERT: Reverse refactorings top-down to produce
       "refactoring-free" versions of both branches
    4. MERGE: Run textual merge on the purified (refactoring-free) code
    5. CHECK & REPLAY:
       - Build refactoring conflict matrix (commutative vs conflicting)
       - If Branch A renames X→Z and Branch B extracts new method Z
         in same hierarchy → CONFLICT (accidental override)
       - If no conflicts → replay valid refactorings sequentially
         (bottom-up order) onto the merged code, updating all references

    Key insight: An Extract Method is perfectly inverted by executing
    an Inline Method operation on the extracted code block, allowing
    the textual merge to process the original unextracted logic before
    replaying the extraction on the newly merged code.

    Invocation:
        java -jar RefMerge.jar -b <base> -l <left> -r <right> -o <output>
    """
    name = "refmerge"

    def merge(self, base, ours, theirs):
        ...
```

**Refactoring Conflict Strategy**:
```python
class RefactoringConflictStrategy(MergeStrategy):
    """
    Uses RM-ASTDiff refactoring metadata from MergeContext to detect
    semantic conflicts that survive the merge:

    - Branch A renames method X→Y, Branch B adds call to X → dangling reference
    - Branch A extracts method M, Branch B modifies code in M → lost changes
    - Branch A moves class to new package, Branch B adds import of old location
    - Both branches rename same method to different names → naming conflict
    - Branch A inlines method, Branch B adds new call to it → dangling reference

    This strategy operates on the refactoring metadata, not on the merged
    file itself. It cross-references the detected refactorings on both
    branches to identify conflicting operations.
    """
    @property
    def name(self): return "RefactoringConflict"

    def analyze(self, context: MergeContext) -> AnalysisResult:
        issues = []
        for ref_ours in context.refactorings_ours:
            for ref_theirs in context.refactorings_theirs:
                conflict = self._check_conflict(ref_ours, ref_theirs)
                if conflict:
                    issues.append(conflict)
        return AnalysisResult(
            is_clean=len(issues) == 0,
            issues=issues
        )
```

**Evaluation**:
- Run all 7 categories through Step 1 and Step 2
- Key question: does the refactoring-aware path correctly handle method rename conflicts?
- Key question: does RefMerge's invert-merge-replay produce fewer false positives than direct structural merge?
- Expected new detections: **method rename** (directly from refactoring metadata), improved handling of **scope capture** involving renamed/extracted elements
- Measure latency: RM-ASTDiff + RefMerge vs Mergiraf-only path

**Key references**:
- Tsantalis et al. 2020, "RefactoringMiner 2.0" (foundational algorithm)
- Pourya Fard et al. 2024, "RM-ASTDiff / RefactoringMiner 3.0" (unified AST diff + refactoring)
- Ellis et al. 2022, "Operation-based Refactoring-aware Merging" (RefMerge)
- Shen et al. 2019, "IntelliMerge" (graph-based comparison baseline)

---

### 4.3 Step 3 — Expand Joern CPG Strategy Coverage

**Architecture**:
```
RM-ASTDiff ─┬─ refactoring ──► RefMerge ──┐
             └─ none ─────────► Mergiraf ──┤
                                            ▼
                                   Joern CPG Analysis
                                   (full strategy suite)
                                            │
                                    Accept / Reject
```

**What changes**:
- New file: `strategies/joern_strategies/dataflow_interference.py`
- New file: `strategies/joern_strategies/control_flow_analysis.py`
- New file: `strategies/joern_strategies/scope_capture.py`
- New file: `strategies/joern_strategies/taint_analysis.py`
- New file: `strategies/structural_strategies/__init__.py`
- New file: `strategies/structural_strategies/atomic_update_check.py`
- Move Scala queries from inline strings to `scala_queries/*.sc` files
- Update `config/strategies.yaml` with full strategy configuration and timeouts

**New Joern Strategies**:

```python
class JoernDataflowInterferenceStrategy(MergeStrategy):
    """
    Detects stale read conflicts using Joern's PDG (Program Dependence Graph).

    Pattern: Branch A clears/modifies a data structure, Branch B reads from it.
    The merged code reads from a cleared structure → runtime failure.

    CPG Query approach:
    1. Identify data-modifying operations (clear, remove, reassign)
       introduced by one branch
    2. Identify read operations (get, iterate, access) introduced by
       the other branch
    3. Check if there exists a data dependence path from the modification
       to the read without an intervening re-initialization

    Scala query:
        cpg.call.name("clear|remove|removeAll")
           .reachableByFlows(cpg.call.name("get|iterator|forEach|size"))
           .l
    """
    @property
    def name(self): return "JoernDataflowInterference"
    ...

class JoernControlFlowAnalysisStrategy(MergeStrategy):
    """
    Detects control flow interference conflicts using Joern's CFG.

    Pattern: Branch A adds an early return/throw/break, Branch B adds
    logic that assumes execution continues past that point.

    CPG Query approach:
    1. Identify new control flow exits (return, throw, break, continue)
       introduced by one branch
    2. Identify new logic (method calls, assignments) introduced by the
       other branch that appears after the exit point in control flow
    3. If the new exit dominates the new logic (in CFG dominator tree),
       the new logic is unreachable → semantic conflict

    Scala query:
        cpg.method.name("<merged_method>")
           .controlStructure.controlStructureType("IF")
           .astChildren.isReturn
           .dominates(cpg.call.lineNumber(<new_logic_line>))
           .l
    """
    @property
    def name(self): return "JoernControlFlowAnalysis"
    ...

class JoernScopeCaptureStrategy(MergeStrategy):
    """
    Detects variable shadowing conflicts using Joern's scope analysis.

    Pattern: Branch A introduces a local variable with the same name as
    a field that Branch B's new code references. The merged code
    silently reads the local instead of the field → wrong value.

    CPG Query approach:
    1. Identify new local variable declarations from one branch
    2. Identify new field references from the other branch
    3. Check if any local declaration shadows a field reference
       within the same scope

    Scala query:
        cpg.local.name("<var>")
           .method.fieldAccess.fieldIdentifier.canonicalName("<var>")
           .l
    """
    @property
    def name(self): return "JoernScopeCapture"
    ...

class JoernTaintAnalysisStrategy(MergeStrategy):
    """
    Detects taint propagation conflicts through merged code.

    Pattern: Branch A introduces a new data source (user input, network),
    Branch B introduces a new sink (database query, command execution).
    The merged code creates an unvalidated taint path → security vulnerability.

    CPG Query approach:
    1. Identify new sources introduced by either branch
    2. Identify new sinks introduced by either branch
    3. Check for taint paths between new sources and new sinks
       without intervening sanitization

    Scala query:
        val sources = cpg.call.name("getParameter|readLine|getInput")
        val sinks = cpg.call.name("executeQuery|exec|write")
        sinks.reachableByFlows(sources).l
    """
    @property
    def name(self): return "JoernTaintAnalysis"
    ...
```

**Structural Strategy**:
```python
class AtomicUpdateCheckStrategy(MergeStrategy):
    """
    Detects invariant violations from concurrent modifications.

    Pattern: An object has fields with an invariant relationship
    (e.g., min <= max, start < end). Branch A modifies one field,
    Branch B modifies the other. The merged code violates the invariant.

    This strategy uses a combination of RM-ASTDiff edit information
    (to identify which fields were modified by which branch) and
    Joern CPG analysis (to detect assertion/validation methods that
    enforce the invariant).
    """
    @property
    def name(self): return "AtomicUpdateCheck"
    ...
```

**Evaluation**:
- Run all 7 categories through Step 2 and Step 3
- This step should achieve detection of all 7 categories
- Key question: what is the false positive rate of the new Joern strategies?
- Key question: does the refactoring metadata from RM-ASTDiff help reduce false positives in Joern analysis (by knowing which changes are intentional refactorings vs semantic modifications)?
- Measure end-to-end pipeline latency with all strategies active

**Expected detection coverage**:

| Conflict Category | Detected By |
|-------------------|-------------|
| Infinite Loop | JoernInfiniteLoop |
| Invalid Loop Bounds | JoernInvalidLoopBounds |
| Atomic Updates | AtomicUpdateCheck |
| Control Flow Interference | JoernControlFlowAnalysis |
| Data Flow Interference | JoernDataflowInterference |
| Exception Handling | JoernControlFlowAnalysis (exception paths) |
| Method Rename | RefactoringConflict (from RM-ASTDiff metadata) |
| Scope Capture | JoernScopeCapture |

---

## 5. Evaluation Framework

### 5.1 Metrics (recorded at every step)

| Metric | Definition |
|--------|------------|
| **True Positive (TP)** | Semantic conflict correctly rejected |
| **False Negative (FN)** | Semantic conflict missed (merge accepted but buggy) |
| **False Positive (FP)** | Clean merge incorrectly rejected |
| **True Negative (TN)** | Clean merge correctly accepted |
| **Precision** | TP / (TP + FP) |
| **Recall** | TP / (TP + FN) |
| **F1 Score** | 2 * (Precision * Recall) / (Precision + Recall) |
| **Categories Covered** | Count of 7 conflict categories detected |
| **Runtime (merge)** | Seconds for merge phase only |
| **Runtime (analysis)** | Seconds for Joern CPG + strategy analysis |
| **Runtime (total)** | End-to-end seconds per merge scenario |

### 5.2 Comparison Table Template

| Step | Merge Backend | Analysis Layers | TP | FN | FP | Precision | Recall | F1 | Categories | Runtime |
|------|---------------|-----------------|----|----|----|-----------|---------|----|------------|---------|
| 0 | git merge-file | Joern (2 strategies) | ? | ? | ? | ? | ? | ? | 2/7 | ? |
| 1 | Mergiraf | Joern (2 strategies) | ? | ? | ? | ? | ? | ? | ?/7 | ? |
| 2 | Mergiraf + RefMerge | Joern + RefactoringConflict | ? | ? | ? | ? | ? | ? | ?/7 | ? |
| 3 | Mergiraf + RefMerge | Joern (full suite) + RefactoringConflict + AtomicUpdate | ? | ? | ? | ? | ? | ? | 7/7 | ? |

### 5.3 Test Scenarios Per Category

Each conflict category requires **at minimum**:
- 1 positive scenario (merge contains the semantic conflict — should be rejected)
- 1 negative scenario (clean merge of same structure — should be accepted)

Test data lives in `tests/data/<category>/` with files: `base.java`, `ours.java`, `theirs.java`, `expected_result.txt`.

### 5.4 Latency Benchmarks

In addition to detection metrics, each step must record latency benchmarks on a standardized hardware profile:

| Phase | Step 0 | Step 1 | Step 2 | Step 3 |
|-------|--------|--------|--------|--------|
| Merge phase (ms) | ? | ? | ? | ? |
| CPG generation (ms) | ? | ? | ? | ? |
| Strategy analysis (ms) | ? | ? | ? | ? |
| RM-ASTDiff (ms) | N/A | N/A | ? | ? |
| Total (ms) | ? | ? | ? | ? |

---

## 6. Research Paper References (Grouped)

### Group 1: Program Dependence Graphs and Slicing
- Weiser 1984 — foundational PDGs
- Horwitz, Reps, Binkley 1990 — interprocedural slicing (SDGs)
- Binkley 1995 — executable slices
- Ranganath & Hatcliff 2007 — concurrent Java slicing (Indus/Kaveri)
- Pauck & Wehrheim 2023 — Android slicing (Jicer)

### Group 2: Semantics-Based Program Integration
- Horwitz, Prins, Reps 1989 — foundational semantic merge (Algorithm Integrate)
- Binkley, Horwitz, Reps 1995 — extension to procedure calls
- Yang, Horwitz, Reps 1992 — accommodating semantics-preserving transformations
- Horwitz 1990 — identifying semantic vs textual differences

### Group 3: AST Differencing and Refactoring Detection
- Fluri et al. 2007 — ChangeDistiller
- Falleri et al. 2014 — GumTree (original AST diff algorithm)
- Le Dilavrec et al. 2022 — HyperAST
- Tsantalis et al. 2020 — RefactoringMiner 2.0 (99.6% precision, 94% recall, 40 types)
- Pourya Fard et al. 2024 — RefactoringMiner 3.0 / RM-ASTDiff (unified AST diff + refactoring detection, 100+ types, multi-mapping)

### Group 4: Merge Strategies
- Seibt et al. 2022 — structured merge empirical study (JDime)
- Cavalcanti et al. 2017 — semistructured merge evaluation
- Brindescu et al. 2019 — merge conflicts and software quality
- Schesch et al. 2024 — merge tool evaluation

### Group 5: Refactoring-Aware Merging
- Shen et al. 2019 — IntelliMerge (graph-based, used as comparison baseline)
- Ellis et al. 2022 — RefMerge (operation-based, empirically superior)
- Dig et al. 2006 — MolhadoRef (foundational operation-based approach)

### Group 6: Tree-Sitter and Structural Merge
- Mergiraf — production-ready tree-sitter-backed Git merge driver (Rust)
- Tree-sitter — incremental parsing framework supporting 30+ languages

### Group 7: Code Property Graphs
- Yamaguchi et al. 2014 — CPG for vulnerability discovery (Joern foundation)
- Seidel et al. 2023 — CodeTIDAL5 type inference for Joern

### Group 8: Empirical Studies
- Microsoft Research 2018 — "Safe program merges at scale" (industry perspective)
- Ellis et al. 2022 — 2,001 merge scenario study (IntelliMerge vs RefMerge comparison)

---

## 7. Implementation Notes for AI Coding Tools

### 7.1 Key Constraints

- **Language**: Python driver, calling Java/Scala/Rust tools via subprocess
- **No LLM approaches**: Research must use classic program analysis techniques only
- **Plugin architecture**: All new analysis tools are added as `MergeStrategy` subclasses
- **Incremental**: Each step must be independently testable before proceeding
- **Java focus**: Test cases and merge scenarios are in Java
- **Fail closed**: All strategies must reject (report issue) on internal errors, never silently accept
- **Timeout management**: All external tool invocations must have configurable timeouts

### 7.2 External Tool Installation

```bash
# Mergiraf (Step 1)
# Install via cargo: cargo install mergiraf
# Or download from: https://mergiraf.org
# Usage: mergiraf merge <base> <ours> <theirs> -o <output>

# RefactoringMiner 3.0 / RM-ASTDiff (Step 2)
# Download from: https://github.com/tsantalis/RefactoringMiner/releases
# Usage: java -jar RefactoringMiner.jar -bf <base_file> <changed_file>
# Note: Requires Java 17+

# RefMerge (Step 2)
# Clone from: https://github.com/ualberta-smr/RefMerge
# Usage: java -jar RefMerge.jar -b <base> -l <left> -r <right> -o <output>

# Joern (already in use)
# joern-parse <file> --output <cpg.bin>
# joern --script <query.sc> --param cpgFile=<cpg.bin>
```

### 7.3 File Naming Conventions

- Strategy files: `strategies/<tool>_strategies/<detection_type>.py`
- Strategy classes: `<Tool><DetectionType>Strategy` (e.g., `JoernDataflowInterferenceStrategy`)
- Test files: `tests/test_<strategy_name>.py`
- Test data: `tests/data/<category>/base.java`, `ours.java`, `theirs.java`
- Scala queries: `scala_queries/<strategy_name>.sc`

### 7.4 When Implementing a New Step

1. Read this document and the current `core/interfaces.py` for the strategy interface
2. Check `core/driver.py` for how strategies are invoked
3. Check `core/plugin_loader.py` for how strategies are discovered
4. Create the new strategy as a `MergeStrategy` subclass
5. Add test scenarios for the conflict categories the new strategy targets
6. Ensure all external tool calls have proper error handling and timeouts
7. Run the full test suite and record metrics in the comparison table (Section 5.2)
8. Record latency benchmarks in the latency table (Section 5.4)
9. Compare results against the previous step before proceeding
