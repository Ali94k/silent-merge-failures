from src.core.interfaces import MergeResult, MergeOutcome
from src.evaluation import comparator as comparator_mod
from src.evaluation.comparator import (
    Classification,
    classify_result,
    contents_match,
    normalize_content,
)


def test_normalize_content():
    assert normalize_content("foo  \nbar\n\n") == "foo\nbar"
    assert normalize_content("foo\r\nbar") == "foo\nbar"


def test_contents_match():
    assert contents_match("foo\n", "foo  \n")
    assert not contents_match("foo", "bar")


def test_contents_match_formatter_off_does_not_invoke_docker(monkeypatch):
    """With MERGE_COMPARATOR_FORMATTER=off, two texts that differ at the
    whitespace-normalization level must short-circuit to False — never reach
    the formatter. Guards against a regression where conftest's env var stops
    being honored."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "off")
    calls: list[str] = []
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: calls.append(c) or None)
    assert not contents_match("class A {}", "class B {}")
    assert calls == []


def test_contents_match_formatter_collapses_ast_equivalent(monkeypatch):
    """With the formatter enabled and mocked to canonicalise both inputs, two
    AST-equivalent textual variants should match. This is the stage γ Spork
    diagnostic pattern in miniature: brace-style + paren differences that
    google-java-format would erase."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "on")
    monkeypatch.setattr(comparator_mod, "_format_cache", {})
    canonical = "class A {\n  int x = 1;\n}\n"
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: canonical)
    a = "class A { int x = 1; }"
    b = "class A {\nint x=1;\n}"
    assert contents_match(a, b)


def test_contents_match_formatter_unavailable_returns_false(monkeypatch):
    """If the formatter is enabled but Docker / image is unavailable
    (`_format_java` returns None), comparator must conservatively report
    "different" rather than masking real disagreement as a match."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "on")
    monkeypatch.setattr(comparator_mod, "_format_cache", {})
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: None)
    assert not contents_match("class A {}", "class B {}")


def test_contents_match_formatter_invoked_only_on_whitespace_mismatch(monkeypatch):
    """Tier-1 (whitespace) match should short-circuit — formatter is not
    invoked when the cheap check already agrees. Performance-critical
    invariant: n=50 evaluation depends on it."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "on")
    monkeypatch.setattr(comparator_mod, "_format_cache", {})
    calls: list[str] = []
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: calls.append(c) or "")
    assert contents_match("foo\n", "foo  \n")
    assert calls == []


def test_contents_match_tier3_recovers_comment_diff(monkeypatch):
    """Tier 3 collapses a standalone-comment diff when gjf preserves both
    sides verbatim. Mirrors the §9 finding that gjf is minimally opinionated
    about source-given comment/blank-line style — Tier 3 strips the
    comment, then `strip_blank_lines` collapses the resulting empty line."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "on")
    monkeypatch.setenv(comparator_mod.AST_NORMALIZE_ENV, "on")
    monkeypatch.setattr(comparator_mod, "_format_cache", {})
    monkeypatch.setattr(comparator_mod, "_ast_cache", {})
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: c)
    a = "class A {\n    // doc\n    int x = 1;\n}\n"
    b = "class A {\n    int x = 1;\n}\n"
    assert contents_match(a, b)


def test_contents_match_tier3_off_short_circuits(monkeypatch):
    """With AST_NORMALIZE=off and Tier 2 disagreeing, Tier 3 must not be
    invoked. Guards against a regression where the env var stops being
    honored."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "on")
    monkeypatch.setenv(comparator_mod.AST_NORMALIZE_ENV, "off")
    monkeypatch.setattr(comparator_mod, "_format_cache", {})
    monkeypatch.setattr(comparator_mod, "_ast_cache", {})
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: c)
    calls: list[str] = []
    monkeypatch.setattr(comparator_mod, "_ast_normalize", lambda c: calls.append(c) or None)
    a = "class A {\n    // doc\n    int x = 1;\n}\n"
    b = "class A {\n    int x = 1;\n}\n"
    assert not contents_match(a, b)
    assert calls == []


def test_contents_match_tier3_parse_fail_falls_through(monkeypatch):
    """When Tier 3's tree-sitter parse fails on either side (e.g. residual
    conflict markers somehow survived gjf and reached Tier 3), contents_match
    returns False without raising — the Tier 2 verdict (already disagreement)
    stands."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "on")
    monkeypatch.setenv(comparator_mod.AST_NORMALIZE_ENV, "on")
    monkeypatch.setattr(comparator_mod, "_format_cache", {})
    monkeypatch.setattr(comparator_mod, "_ast_cache", {})
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: c)
    a = "class A {\n<<<<<<<\nint x;\n=======\nint y;\n>>>>>>>\n}\n"
    b = "class B {\n<<<<<<<\nint x;\n=======\nint y;\n>>>>>>>\n}\n"
    assert not contents_match(a, b)


def test_contents_match_d2_syntactic_paren_guard_end_to_end(monkeypatch):
    """D.2's syntactic-paren guard preserves the `if (cond)` paren so the
    Tier-3 canonical output remains valid Java. The pair below — two forms
    of the same `if (x > 0) y();`, with Spork's typical brace + dev's
    inlined form — canonicalises to the same shape via D.1 (consequence
    unwrap) + D.2 (paren around primary x.f stripped, but the if's
    condition paren retained)."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "on")
    monkeypatch.setenv(comparator_mod.AST_NORMALIZE_ENV, "on")
    monkeypatch.setattr(comparator_mod, "_format_cache", {})
    monkeypatch.setattr(comparator_mod, "_ast_cache", {})
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: c)
    a = "class A {\n    void m(int x) { if (x > 0) { y(); } }\n    void y() {}\n}\n"
    b = "class A {\n    void m(int x) { if (x > 0) y(); }\n    void y() {}\n}\n"
    assert contents_match(a, b)


def test_contents_match_d6_line_wrap_recovers_end_to_end(monkeypatch):
    """D.6 token-canonical fold closes pure-line-wrap differences. The two
    fixtures below differ only in newline placement within the method body —
    no AST-level transform fires, but the token-fold yields the same
    canonical form, so `contents_match` returns True."""
    monkeypatch.setenv(comparator_mod.FORMATTER_ENV, "on")
    monkeypatch.setenv(comparator_mod.AST_NORMALIZE_ENV, "on")
    monkeypatch.setattr(comparator_mod, "_format_cache", {})
    monkeypatch.setattr(comparator_mod, "_ast_cache", {})
    monkeypatch.setattr(comparator_mod, "_format_java", lambda c: c)
    a = ("class A {\n  void m() {\n    longMethodName(\n      argument);\n  }\n"
         "  void longMethodName(int x) {}\n}\n")
    b = ("class A {\n  void m() {\n    longMethodName(argument);\n  }\n"
         "  void longMethodName(int x) {}\n}\n")
    # Note: `argument` is undeclared here, but that's fine — tree-sitter
    # parses syntax, not semantics. Both fixtures parse identically.
    assert contents_match(a, b)


def test_classify_clean_match():
    result = MergeResult(
        outcome=MergeOutcome.CLEAN,
        merged_content="merged content",
        conflict_count=0,
        runtime_seconds=0.1,
    )
    cls = classify_result(
        result=result,
        developer_resolution="merged content",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
    )
    assert cls == Classification.TRUE_POSITIVE


def test_classify_clean_mismatch():
    result = MergeResult(
        outcome=MergeOutcome.CLEAN,
        merged_content="wrong merge",
        conflict_count=0,
        runtime_seconds=0.1,
    )
    cls = classify_result(
        result=result,
        developer_resolution="correct merge",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
    )
    assert cls == Classification.FALSE_POSITIVE


def test_classify_conflict_real():
    result = MergeResult(
        outcome=MergeOutcome.CONFLICT,
        merged_content="<<<<<<< ...",
        conflict_count=1,
        runtime_seconds=0.1,
    )
    cls = classify_result(
        result=result,
        developer_resolution="manually resolved",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
    )
    assert cls == Classification.TRUE_NEGATIVE


def test_classify_conflict_both_sides_changed_dev_picks_side():
    """Both parents differ from base — real conflict, dev picked one side."""
    result = MergeResult(
        outcome=MergeOutcome.CONFLICT,
        merged_content="<<<<<<< ...",
        conflict_count=1,
        runtime_seconds=0.1,
    )
    cls = classify_result(
        result=result,
        developer_resolution="ours",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
    )
    assert cls == Classification.TRUE_NEGATIVE


def test_classify_conflict_one_side_changed():
    """Only ours changed from base — conflict was unnecessary (false alarm)."""
    result = MergeResult(
        outcome=MergeOutcome.CONFLICT,
        merged_content="<<<<<<< ...",
        conflict_count=1,
        runtime_seconds=0.1,
    )
    cls = classify_result(
        result=result,
        developer_resolution="ours",
        base_content="base",
        ours_content="ours",
        theirs_content="base",  # theirs == base, only ours changed
    )
    assert cls == Classification.FALSE_NEGATIVE


def test_classify_conflict_dev_reverts_to_base():
    """Developer reverted to base — conflict was a false alarm."""
    result = MergeResult(
        outcome=MergeOutcome.CONFLICT,
        merged_content="<<<<<<< ...",
        conflict_count=1,
        runtime_seconds=0.1,
    )
    cls = classify_result(
        result=result,
        developer_resolution="base",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
    )
    assert cls == Classification.FALSE_NEGATIVE


def test_classify_crash():
    result = MergeResult(
        outcome=MergeOutcome.CRASH,
        merged_content=None,
        conflict_count=0,
        runtime_seconds=0.1,
    )
    cls = classify_result(
        result=result,
        developer_resolution="any",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
    )
    assert cls == Classification.CRASH


def test_classify_timeout():
    result = MergeResult(
        outcome=MergeOutcome.TIMEOUT,
        merged_content=None,
        conflict_count=0,
        runtime_seconds=60.0,
    )
    cls = classify_result(
        result=result,
        developer_resolution="any",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
    )
    assert cls == Classification.TIMEOUT
