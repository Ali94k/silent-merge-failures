```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#000', 'edgeLabelBackground':'#1e1e1e', 'tertiaryColor': '#1e1e1e', 'primaryTextColor': '#fff', 'secondaryTextColor': '#fff', 'lineColor': '#888'}}}%%
graph TD
    %% Input nodes and starting text
    InputStart["Input: base, ours, theirs"]
    InputStart --> A["RefactoringMiner<br/>detect refactors in both branches"]
    A -.-> Anote{{"Pre-merge analysis<br/>Detects renames, extractions,<br/>inlines across branches"}}

    %% Decision structure
    subgraph RefactoringDecision ["Conditional Logic"]
        direction TB
        Decision{"Refactoring detected?"}
        Decision -- Yes --> Intelli["IntelliMerge<br/>(graph-based refactoring-aware merge)"]
        Decision -- No --> JDime["JDime / Spork<br/>(structured AST-level three-way merge)"]
    end
    
    %% Connect input analysis to decision
    A --> Decision

    %% Connect both outcomes to merged file
    Intelli --> Merged
    JDime --> Merged
    Merged["merged file"]

    %% Post-merge analysis steps with notes
    Merged --> GumTree["GumTree Edit Scripts<br/>(3-way AST diff: base->ours, base->theirs<br/>detect overlapping edits)"]
    GumTree -.-> GumTreeNote{{"Structural analysis<br/>Compute edit scripts:<br/>base->ours<br/>base->theirs<br/>Flag overlaps"}}

    GumTree --> Joern["Joern CPG Strategies<br/>(existing + new strategies on Code Property Graph)"]
    Joern -.-> JoernNote{{"Semantic analysis<br/>Dataflow, control flow,<br/>taint analysis on merged"}}

    Joern --> SafeMerge["SafeMerge (optional)<br/>(compositional relational verification via Z3 SMT)"]
    SafeMerge -.-> SafeMergeNote{{"Formal verification<br/>Proves semantic conflict-<br/>freedom mathematically"}}

    %% End state
    SafeMerge --> End["Accept (exit 0) / Reject (exit 1)"]

    %% Styling to make it look dark-mode-like and clear
    classDef box border-width:2px,fill:#1e1e1e,stroke:#fff,color:#fff;
    classDef decision border-width:2px,fill:#1e1e1e,stroke:#fff,color:#fff,shape:diamond;
    classDef note fill:none,stroke:#fff,color:#fff,stroke-dasharray: 5 5;
    classDef title fill:#1e1e1e,stroke:#fff,color:#fff;

    class InputStart,A,Intelli,JDime,Merged,GumTree,Joern,SafeMerge,End box;
    class Decision decision;
    class Anote,GumTreeNote,JoernNote,SafeMergeNote note;
    class RefactoringDecision title;