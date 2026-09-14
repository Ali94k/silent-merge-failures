"""Generate a synthetic, Spork-favorable 3-way-merge suite as scenario JSONs.

Purpose
-------
A hand-built battery targeting Spork's *documented* strengths (Larsén et al.,
IEEE TSE 2023: Spoon AST + 3DM merge + original-token caching for formatting
preservation; structured conflict reduction vs line-based git). Each case is a
clean-mergeable scenario whose `developer_resolution` is the semantically correct
merge, so the comparator scores every tool against the same ground truth.

These are CAPABILITY demonstrations, not field-frequency evidence: per the
`routing-two-phase` memory and ISSUES #27, synthetic data is Phase-1 routing
coverage, NOT Phase-2 routing evidence. They do not justify the `INTRA_BODY ->
Spork` (S2) routing arm.

Empirical outcome when run through git / mergiraf / spork (2026-05-26, canonical
`contents_match` oracle):
  - Spork beats git (line-based) on the structured families (1-5) — its real niche.
  - Spork strict-wins over Mergiraf: 0/16.
  - Mergiraf strict-wins over Spork: 3 — concurrent annotations, records, and
    switch-patterns (Spork-0.5.0 Spoon conflicts/chokes; Mergiraf's tree-sitter
    merges cleanly).
  - The 3 comment cases (14-16) score TP for *both*: the canonical oracle's AST
    tier strips comments before comparing (see comparator.contents_match), so
    Spork's body reformatting / one-line-Javadoc expansion / trailing-comment
    move is neutralized rather than counted against it. They would favor Mergiraf
    only under a raw byte oracle (Mergiraf is byte-exact there) — which is NOT the
    oracle these numbers use.
  - H_enum / I_throws: both tools conflict (neither treats the construct as
    commutative at a shared insertion point).
Caveat: tiny files; Spork's formatting-preservation is measured on large real
files via token reuse, so this is not a general claim about Spork's formatter.

Families: 1 imports, 2 members, 3 move+edit, 4 sub-expression, 5 reformat,
6 modern-syntax / commutative-edge, 7 comment/formatting preservation.

Usage:
    OUTPUT=data/scenarios_synthetic ./.venv/bin/python tools/make_synthetic_spork_cases.py
Then:
    ./.venv/bin/python -m src.cli run    --scenarios-dir data/scenarios_synthetic --results-dir data/results_synthetic
    ./.venv/bin/python -m src.cli report --scenarios-dir data/scenarios_synthetic --results-dir data/results_synthetic \
        --format console --format csv --output-dir reports_synthetic
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.core.interfaces import MergeScenario  # noqa: E402

# Each case: (name, family, base, ours, theirs, developer_resolution).
CASES: list[tuple[str, str, str, str, str, str]] = [
    ("move_plus_edit", "3-move",
     "package p;\nclass C {\n    int foo(){ return 1; }\n    int bar(){ return 2; }\n}\n",
     "package p;\nclass C {\n    int bar(){ return 2; }\n    int foo(){ return 1; }\n}\n",
     "package p;\nclass C {\n    int foo(){ return 10; }\n    int bar(){ return 2; }\n}\n",
     "package p;\nclass C {\n    int bar(){ return 2; }\n    int foo(){ return 10; }\n}\n"),
    ("dual_rename_shared_line", "4-subexpr",
     "package p;\nclass C {\n    int alpha=1;\n    int gamma=2;\n    int m(){ return alpha*gamma; }\n}\n",
     "package p;\nclass C {\n    int alpha2=1;\n    int gamma=2;\n    int m(){ return alpha2*gamma; }\n}\n",
     "package p;\nclass C {\n    int alpha=1;\n    int gamma2=2;\n    int m(){ return alpha*gamma2; }\n}\n",
     "package p;\nclass C {\n    int alpha2=1;\n    int gamma2=2;\n    int m(){ return alpha2*gamma2; }\n}\n"),
    ("imports_add_different", "1-imports",
     "package p;\nimport java.util.List;\nimport java.util.Map;\nclass C { List<String> a; Map<String,String> b; }\n",
     "package p;\nimport java.util.List;\nimport java.util.Map;\nimport java.util.Set;\nclass C { List<String> a; Map<String,String> b; }\n",
     "package p;\nimport java.io.IOException;\nimport java.util.List;\nimport java.util.Map;\nclass C { List<String> a; Map<String,String> b; }\n",
     "package p;\nimport java.io.IOException;\nimport java.util.List;\nimport java.util.Map;\nimport java.util.Set;\nclass C { List<String> a; Map<String,String> b; }\n"),
    ("methods_add_different", "2-members",
     "package p;\nclass C {\n    int base(){ return 0; }\n}\n",
     "package p;\nclass C {\n    int base(){ return 0; }\n    int a(){ return 1; }\n}\n",
     "package p;\nclass C {\n    int base(){ return 0; }\n    int b(){ return 2; }\n}\n",
     "package p;\nclass C {\n    int base(){ return 0; }\n    int a(){ return 1; }\n    int b(){ return 2; }\n}\n"),
    ("fields_add_different", "2-members",
     "package p;\nclass C {\n    int base=0;\n}\n",
     "package p;\nclass C {\n    int base=0;\n    int a=1;\n}\n",
     "package p;\nclass C {\n    int base=0;\n    int b=2;\n}\n",
     "package p;\nclass C {\n    int base=0;\n    int a=1;\n    int b=2;\n}\n"),
    ("two_stmt_same_method", "4-subexpr",
     "package p;\nclass C {\n    void m(){\n        int x=1;\n        int y=2;\n    }\n}\n",
     "package p;\nclass C {\n    void m(){\n        int x=10;\n        int y=2;\n    }\n}\n",
     "package p;\nclass C {\n    void m(){\n        int x=1;\n        int y=20;\n    }\n}\n",
     "package p;\nclass C {\n    void m(){\n        int x=10;\n        int y=20;\n    }\n}\n"),
    ("reformat_plus_edit", "5-reformat",
     "package p;\nclass C {\n    int m(){\n        int a=1;\n        return a;\n    }\n}\n",
     "package p;\nclass C {\n    int m(){ int a=1; return a; }\n}\n",
     "package p;\nclass C {\n    int m(){\n        int a=5;\n        return a;\n    }\n}\n",
     "package p;\nclass C {\n    int m(){\n        int a=5;\n        return a;\n    }\n}\n"),
    ("enum_add_constants", "6-edge",
     "package p;\nenum E { A, B }\n", "package p;\nenum E { A, B, C }\n",
     "package p;\nenum E { A, B, D }\n", "package p;\nenum E { A, B, C, D }\n"),
    ("throws_add_different", "6-edge",
     "package p;\nclass C {\n    void m() throws java.io.IOException {}\n}\n",
     "package p;\nclass C {\n    void m() throws java.io.IOException, java.sql.SQLException {}\n}\n",
     "package p;\nclass C {\n    void m() throws java.io.IOException, InterruptedException {}\n}\n",
     "package p;\nclass C {\n    void m() throws java.io.IOException, java.sql.SQLException, InterruptedException {}\n}\n"),
    ("annotations_add_different", "6-edge",
     "package p;\nclass C {\n    @Override\n    public String toString(){ return \"x\"; }\n}\n",
     "package p;\nclass C {\n    @Deprecated\n    @Override\n    public String toString(){ return \"x\"; }\n}\n",
     "package p;\nclass C {\n    @SuppressWarnings(\"unused\")\n    @Override\n    public String toString(){ return \"x\"; }\n}\n",
     "package p;\nclass C {\n    @Deprecated\n    @SuppressWarnings(\"unused\")\n    @Override\n    public String toString(){ return \"x\"; }\n}\n"),
    ("record_edit_plus_add", "6-edge",
     "package p;\nrecord R(int x, int y) {\n    int sum(){ return x + y; }\n}\n",
     "package p;\nrecord R(int x, int y) {\n    int sum(){ return x * y; }\n}\n",
     "package p;\nrecord R(int x, int y) {\n    int sum(){ return x + y; }\n    int diff(){ return x - y; }\n}\n",
     "package p;\nrecord R(int x, int y) {\n    int sum(){ return x * y; }\n    int diff(){ return x - y; }\n}\n"),
    ("switch_pattern_add_case", "6-edge",
     "package p;\nclass C {\n    String f(Object o){\n        return switch(o){\n            case Integer i -> \"int\";\n            default -> \"other\";\n        };\n    }\n}\n",
     "package p;\nclass C {\n    String f(Object o){\n        return switch(o){\n            case Integer i -> \"int\";\n            case String s -> \"str\";\n            default -> \"other\";\n        };\n    }\n}\n",
     "package p;\nclass C {\n    String f(Object o){\n        return switch(o){\n            case Integer i -> \"int\";\n            default -> \"unknown\";\n        };\n    }\n}\n",
     "package p;\nclass C {\n    String f(Object o){\n        return switch(o){\n            case Integer i -> \"int\";\n            case String s -> \"str\";\n            default -> \"unknown\";\n        };\n    }\n}\n"),
    ("textblock_surrounding_edit", "6-edge",
     "package p;\nclass C {\n    String s = \"\"\"\n        hello\n        \"\"\";\n    int n = 1;\n}\n",
     "package p;\nclass C {\n    String s = \"\"\"\n        hello\n        \"\"\";\n    int n = 2;\n}\n",
     "package p;\nclass C {\n    String s = \"\"\"\n        hello\n        \"\"\";\n    int n = 1;\n    int m = 3;\n}\n",
     "package p;\nclass C {\n    String s = \"\"\"\n        hello\n        \"\"\";\n    int n = 2;\n    int m = 3;\n}\n"),
    ("comment_move_with_method", "7-comment",
     "package p;\nclass C {\n    /** does foo */\n    int foo(){ return 1; }\n    int bar(){ return 2; }\n}\n",
     "package p;\nclass C {\n    int bar(){ return 2; }\n    /** does foo */\n    int foo(){ return 1; }\n}\n",
     "package p;\nclass C {\n    /** does foo */\n    int foo(){ return 10; }\n    int bar(){ return 2; }\n}\n",
     "package p;\nclass C {\n    int bar(){ return 2; }\n    /** does foo */\n    int foo(){ return 10; }\n}\n"),
    ("javadoc_edit_plus_signature", "7-comment",
     "package p;\nclass C {\n    /** old doc */\n    int m(int a){ return a; }\n}\n",
     "package p;\nclass C {\n    /** new doc */\n    int m(int a){ return a; }\n}\n",
     "package p;\nclass C {\n    /** old doc */\n    int m(int a, int b){ return a; }\n}\n",
     "package p;\nclass C {\n    /** new doc */\n    int m(int a, int b){ return a; }\n}\n"),
    ("inline_trailing_comment", "7-comment",
     "package p;\nclass C {\n    int m(){\n        int a = 1;\n        return a;\n    }\n}\n",
     "package p;\nclass C {\n    int m(){\n        int a = 1; // initialize\n        return a;\n    }\n}\n",
     "package p;\nclass C {\n    int m(){\n        int a = 1;\n        return a * 2;\n    }\n}\n",
     "package p;\nclass C {\n    int m(){\n        int a = 1; // initialize\n        return a * 2;\n    }\n}\n"),
]


def main() -> None:
    out_dir = Path(os.environ.get("OUTPUT", str(PROJECT_ROOT / "data/scenarios_synthetic")))
    out_dir.mkdir(parents=True, exist_ok=True)
    made = 0
    for idx, (name, family, base, ours, theirs, dev) in enumerate(CASES, 1):
        sid = f"synthetic__{idx:02d}_{name}"
        scenario = MergeScenario(
            scenario_id=sid,
            repo_name="synthetic",
            merge_commit="synthetic",
            file_path=f"{family}/{name}.java",
            base_content=base,
            ours_content=ours,
            theirs_content=theirs,
            developer_resolution=dev,
            category="synthetic",
            refactorings={"ours": [], "theirs": []},
        )
        (out_dir / f"{sid}.json").write_text(json.dumps(scenario.to_dict(), indent=2))
        made += 1
        print(f"  [{made}/{len(CASES)}] {sid}  (family {family})")
    print(f"DONE made={made} out={out_dir}")


if __name__ == "__main__":
    main()
