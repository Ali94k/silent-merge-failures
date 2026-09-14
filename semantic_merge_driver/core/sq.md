```mermaid
sequenceDiagram
    participant User
    participant Git as Git Process
    participant Driver as Python Driver (driver.py)
    participant Backend as MergeBackend (auto default)
    participant Classifier as RM2 Classifier (in AutoBackend)
    participant Loader as Plugin Loader
    participant Strategy as Strategy (InfiniteLoop)
    participant Joern as Joern CLI / JVM

    User->>Git: git merge feature-branch
    Note over Git: Git checks .gitattributes<br/>Found "merge=semantic-driver"

    Git->>Driver: Execute driver.py %O %A %B
    Note right of Git: Passes Ancestor, Ours, Theirs paths

    activate Driver

    Driver->>Backend: merge(base, ours, theirs)
    Note right of Driver: Three-way merge step;<br/>backend chosen via SEMANTIC_MERGE_BACKEND<br/>(auto default; mergiraf / git for explicit bypass)

    alt Backend is AutoBackend (default)
        Backend->>Classifier: cluster(base, ours, theirs)
        Note right of Backend: docker run<br/>merge-tools/refactoring-miner:2.4.0<br/>twice (base→ours, base→theirs)
        Classifier-->>Backend: Cluster label (NONE if RM2 fails)
        Note right of Backend: Logs cluster=X language=Y → backend;<br/>routes every cluster to Mergiraf today;<br/>falls back to git merge-file once on CRASH
    end

    Backend-->>Driver: MergeOutcome (CLEAN / CONFLICT / CRASH)

    Driver->>Loader: load_strategies()
    activate Loader
    Loader-->>Driver: Returns list [InfiniteLoopStrategy, ...]
    deactivate Loader

    loop For each Strategy
        Driver->>Strategy: analyze(merged_file_path, base_content)
        activate Strategy

        Strategy->>Joern: joern-parse merged_file
        Note right of Strategy: Generates CPG (Graph)

        Strategy->>Joern: joern --script infinite_loop.sc
        activate Joern
        Joern-->>Strategy: Output JSON (e.g., {"line": 10, "msg": "Loop detected"})
        deactivate Joern

        Strategy-->>Driver: AnalysisResult(is_clean=False, issues=...)
        deactivate Strategy
    end

    alt Critical Issues Found
        Driver->>User: Print "Semantic Merge Rejected: Infinite Loop at line 10"
        Driver-->>Git: Exit Code 1 (Failure)
        Git->>User: "Automatic merge failed, fix conflicts and then commit result."
    else No Issues Found
        Driver-->>Git: Exit Code 0 (Success)
        Git->>User: Merge completed successfully
    end

    deactivate Driver
```