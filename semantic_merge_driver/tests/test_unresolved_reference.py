"""JoernUnresolvedReferenceStrategy — differential merge-broken resolution.

Live tests run real Joern (skip when joern-parse is absent); fail-closed
tests monkeypatch subprocess (test_fail_closed.py pattern — kept here rather
than in test_fail_closed.py because this strategy abstains without parents,
so the shared no-parents parametrization does not apply).
"""
import shutil
import subprocess

import pytest

from strategies.joern_strategies.unresolved_reference import JoernUnresolvedReferenceStrategy

JOERN = shutil.which("joern-parse") is not None

# Erudika shape: ours renamed m->method everywhere; theirs kept m and added a
# call. Mergiraf output declares `method` but keeps one stale `m` reference.
MERGED_STALE = """\
public class Aspect {
    public void invoke(int mi) {
        int method = mi;
        helper(m);
        helper(method);
    }
    private void helper(int x) {}
}
"""
OURS_RENAMED = """\
public class Aspect {
    public void invoke(int mi) {
        int method = mi;
        helper(method);
    }
    private void helper(int x) {}
}
"""
THEIRS_OLD_NAME = """\
public class Aspect {
    public void invoke(int mi) {
        int m = mi;
        helper(m);
        helper(m);
    }
    private void helper(int x) {}
}
"""

# Inherited-field shape: `logger` resolves in NO version (single-file parse
# cannot see the superclass) -> must not be flagged.
INHERITED = """\
public class Child extends Base {
    public void run() {
        logger.info();
    }
}
"""

# jnr shape: ours resolves Struct via import; merged lost the import.
MERGED_NO_IMPORT = """\
public class N {
    public int getsockopt(int s, Struct data) { return 0; }
}
"""
OURS_WITH_IMPORT = """\
import jnr.ffi.Struct;
public class N {
    public int getsockopt(int s, Struct data) { return 0; }
}
"""
THEIRS_NO_METHOD = """\
public class N {
}
"""


def _write(tmp_path, content):
    p = tmp_path / "Foo.java"
    p.write_text(content, encoding="utf-8")
    return p


def test_abstains_without_parents(tmp_path, monkeypatch):
    """Differential-only: no parents -> clean, and no subprocess at all."""
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append(a))
    merged = _write(tmp_path, MERGED_STALE)
    result = JoernUnresolvedReferenceStrategy().analyze(str(merged))
    assert result.is_clean is True
    assert calls == []


def test_fail_closed_on_subprocess_failure(tmp_path, monkeypatch):
    def raise_cpe(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd="joern-parse")

    monkeypatch.setattr(subprocess, "run", raise_cpe)
    merged = _write(tmp_path, MERGED_STALE)
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(merged), base_content="b", ours_content=OURS_RENAMED, theirs_content=THEIRS_OLD_NAME)
    assert result.is_clean is False
    assert any("inconclusive" in i.message for i in result.issues)


def test_fail_closed_on_query_returncode(tmp_path, monkeypatch):
    def mock_run(*args, **kwargs):
        if kwargs.get("shell"):
            return subprocess.CompletedProcess(args=args[0], returncode=1, stdout="", stderr="boom")
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)
    merged = _write(tmp_path, MERGED_STALE)
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(merged), base_content="b", ours_content=OURS_RENAMED, theirs_content=THEIRS_OLD_NAME)
    assert result.is_clean is False
    assert result.issues[0].severity == "CRITICAL"


@pytest.mark.skipif(not JOERN, reason="joern-parse not on PATH")
def test_flags_merge_induced_unresolved_identifier(tmp_path):
    merged = _write(tmp_path, MERGED_STALE)
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(merged), base_content="b", ours_content=OURS_RENAMED, theirs_content=THEIRS_OLD_NAME)
    assert not result.is_clean
    assert any("'m'" in i.message and "Unresolved identifier" in i.message for i in result.issues)


@pytest.mark.skipif(not JOERN, reason="joern-parse not on PATH")
def test_ignores_identifier_unresolved_in_all_versions(tmp_path):
    """Inherited/same-package names are unresolved everywhere -> clean."""
    merged = _write(tmp_path, INHERITED)
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(merged), base_content="b", ours_content=INHERITED, theirs_content=INHERITED)
    assert result.is_clean is True, [i.message for i in result.issues]


@pytest.mark.skipif(not JOERN, reason="joern-parse not on PATH")
def test_merged_away_import_is_out_of_scope(tmp_path):
    """Import-deletion breakage (jnr pilot shape) is NOT covered: the type
    lane that detected it was dropped after two pilot attempts showed
    javasrc2cpg's type inference is version-unstable on real files (see
    module header). This test documents the abstention — type names are not
    identifiers, so the id lane stays clean."""
    merged = _write(tmp_path, MERGED_NO_IMPORT)
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(merged), base_content="b", ours_content=OURS_WITH_IMPORT, theirs_content=THEIRS_NO_METHOD)
    assert result.is_clean is True


# =========================================================================== #
# D3 widening (ISSUES #31 S-D4) — textual removed/renamed-declaration
# differential. Everything below runs with the experimental flag ON and the
# Joern query stubbed out (the widened pre-pass is pure text; live-Joern
# integration is exercised separately at the end). Fixture shapes are
# reconstructions of the S-D1 gap-inventory derivation units, named in each
# test — derivation data only, per the plan §3 firewall.
# =========================================================================== #
from strategies.joern_strategies import unresolved_reference as _ur  # noqa: E402


def _analyze_widened(tmp_path, monkeypatch, base, ours, theirs, merged,
                     flag=True, joern_ids=(), filename="Foo.java",
                     base_present=True):
    """analyze() with flag control and _run_query stubbed to `joern_ids`."""
    if flag:
        monkeypatch.setenv("SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS", "1")
    else:
        monkeypatch.delenv("SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS", raising=False)
    # `joern_ids` stands in for the MERGED file's unresolved set only; the
    # parent temp files (`…​.ours.java` / `…​.theirs.java`) report empty so
    # the parent-suppression rule stays out of the stub's way.
    monkeypatch.setattr(
        JoernUnresolvedReferenceStrategy, "_run_query",
        lambda self, path: [] if path.endswith((".ours.java", ".theirs.java"))
        else list(joern_ids))
    p = tmp_path / filename
    p.write_text(merged, encoding="utf-8")
    return JoernUnresolvedReferenceStrategy().analyze(
        str(p), base_content=(base if base_present else None),
        ours_content=ours, theirs_content=theirs)


def _stale_msgs(result):
    return [i.message for i in result.issues
            if "Stale reference to a removed/renamed declaration" in i.message]


# --- positives: one per in-reach gap-inventory shape --------------------- #

# S1 (datastax_java-driver__e1535e89ad): ours removed the AtomicBoolean field
# `isShutdown` (a same-named METHOD survives — the declaration guard must be
# kind-strict); theirs added a fresh bare-receiver read.
S1_BASE = """class Pool {
    private final AtomicBoolean isShutdown = new AtomicBoolean();
    public Object borrow() { return null; }
    public boolean isShutdown() { return isShutdown.get(); }
}
"""
S1_OURS = """class Pool {
    private final AtomicReference<Object> shutdownFuture = new AtomicReference<Object>();
    public Object borrow() { return null; }
    public boolean isShutdown() { return shutdownFuture.get() != null; }
}
"""
S1_THEIRS = """class Pool {
    private final AtomicBoolean isShutdown = new AtomicBoolean();
    public Object borrow() {
        if (isShutdown.get()) throw new RuntimeException("down");
        return null;
    }
    public boolean isShutdown() { return isShutdown.get(); }
}
"""
S1_MERGED = """class Pool {
    private final AtomicReference<Object> shutdownFuture = new AtomicReference<Object>();
    public Object borrow() {
        if (isShutdown.get()) throw new RuntimeException("down");
        return null;
    }
    public boolean isShutdown() { return shutdownFuture.get() != null; }
}
"""


def test_widened_flags_removed_field_bare_receiver(tmp_path, monkeypatch):
    result = _analyze_widened(tmp_path, monkeypatch, S1_BASE, S1_OURS, S1_THEIRS, S1_MERGED)
    assert not result.is_clean
    msgs = _stale_msgs(result)
    assert len(msgs) == 1 and "'isShutdown'" in msgs[0]
    assert "variable/field" in msgs[0]
    assert "kept by theirs" in msgs[0] and "removed on ours" in msgs[0]
    assert result.issues[0].line_number == 4


def test_widened_flags_this_qualified_write_under_extends(tmp_path, monkeypatch):
    """S1 (yandex-qatools__6e15a53c7e): `this.processReady = true` — a
    fieldIdentifier in Joern (invisible to the id query, probed 2026-07-16);
    the class extends a supertype, so span suppression would FN — var kind
    deliberately has none (module header records the asymmetry)."""
    base = ("public class P extends AbstractPGProcess {\n"
            "    volatile boolean processReady = false;\n"
            "    public boolean isReady() { return processReady; }\n"
            "    protected void onAfter() { }\n}\n")
    ours = ("public class P extends AbstractPGProcess {\n"
            "    protected void onAfter() { }\n}\n")
    theirs = ("public class P extends AbstractPGProcess {\n"
              "    volatile boolean processReady = false;\n"
              "    public boolean isReady() { return processReady; }\n"
              "    protected void onAfter() { this.processReady = true; }\n}\n")
    merged = ("public class P extends AbstractPGProcess {\n"
              "    protected void onAfter() { this.processReady = true; }\n}\n")
    result = _analyze_widened(tmp_path, monkeypatch, base, ours, theirs, merged)
    msgs = _stale_msgs(result)
    assert len(msgs) == 1 and "'processReady'" in msgs[0]
    assert result.issues[0].line_number == 2


def test_widened_flags_renamed_field_stale_receivers(tmp_path, monkeypatch):
    """S1b (jline_jline2__5acfe59453): rename is removal of the old name's
    declaration — covered without any RM2 involvement."""
    base = ("public class C {\n    private NonBlockingInputStream nonBlockingInput;\n"
            "    void set() { this.nonBlockingInput = null; }\n}\n")
    ours = ("public class C {\n    private NonBlockingInputStream in;\n"
            "    void set() { this.in = null; }\n}\n")
    theirs = ("public class C {\n    private NonBlockingInputStream nonBlockingInput;\n"
              "    void set() { this.nonBlockingInput = null; }\n"
              "    void ic() {\n        if (nonBlockingInput.isNonBlockingEnabled()) {\n"
              "            nonBlockingInput.peek(500);\n        }\n    }\n}\n")
    merged = ("public class C {\n    private NonBlockingInputStream in;\n"
              "    void set() { this.in = null; }\n"
              "    void ic() {\n        if (nonBlockingInput.isNonBlockingEnabled()) {\n"
              "            nonBlockingInput.peek(500);\n        }\n    }\n}\n")
    result = _analyze_widened(tmp_path, monkeypatch, base, ours, theirs, merged)
    msgs = _stale_msgs(result)
    assert len(msgs) == 2 and all("'nonBlockingInput'" in m for m in msgs)


S2_BASE = """public class Decl implements Resolved {
    private Node wrappedNode;
    public Node getWrappedNode() { return wrappedNode; }
    public boolean isField() { return false; }
}
"""
S2_OURS = """public final class Decl {
    public boolean isField() { return false; }
}
"""
S2_THEIRS = """public class Decl implements Resolved {
    private Node wrappedNode;
    public Node getWrappedNode() { return wrappedNode; }
    public boolean isField() { return false; }
    public boolean isVariable() { return getWrappedNode() instanceof Object; }
}
"""
S2_MERGED = """public final class Decl {
    public boolean isField() { return false; }
    public boolean isVariable() { return getWrappedNode() instanceof Object; }
}
"""


def test_widened_flags_removed_method_still_called(tmp_path, monkeypatch):
    """S2 (javaparser__dc6254f1bf): calls are not identifier nodes (probed);
    merged kept ours' supertype-less header, so no absorbable span."""
    result = _analyze_widened(tmp_path, monkeypatch, S2_BASE, S2_OURS, S2_THEIRS, S2_MERGED)
    msgs = _stale_msgs(result)
    assert len(msgs) == 1 and "'getWrappedNode'" in msgs[0] and "method" in msgs[0]


def test_widened_flags_removed_static_helper_called_by_kept_tests(tmp_path, monkeypatch):
    """S2 (jcabi-github__b13d2596ba): a local VARIABLE named `milestones`
    coexists with the removed method — call-form vs var-form must not mix,
    and the remover's qualified `repo.milestones()` must not absorb."""
    base = ("public final class RtM {\n"
            "    public void old() { final Milestones milestones = milestones(); milestones.create(\"x\"); }\n"
            "    private static Milestones milestones() throws Exception { return null; }\n}\n")
    ours = ("public final class RtM {\n"
            "    public void old() { final Milestones milestones = repo.milestones(); milestones.create(\"x\"); }\n}\n")
    theirs = ("public final class RtM {\n"
              "    public void old() { final Milestones milestones = milestones(); milestones.create(\"x\"); }\n"
              "    public void iteratesIssues() { final Milestones milestones = milestones(); }\n"
              "    private static Milestones milestones() throws Exception { return null; }\n}\n")
    merged = ("public final class RtM {\n"
              "    public void old() { final Milestones milestones = repo.milestones(); milestones.create(\"x\"); }\n"
              "    public void iteratesIssues() { final Milestones milestones = milestones(); }\n}\n")
    result = _analyze_widened(tmp_path, monkeypatch, base, ours, theirs, merged)
    msgs = _stale_msgs(result)
    assert len(msgs) == 1 and "'milestones'" in msgs[0]
    assert result.issues[0].line_number == 3


def test_widened_flags_removed_inner_class_new_site(tmp_path, monkeypatch):
    """S3 (gwtbootstrap3__5c0d1eab79): `new SubmitEvent()` under a class that
    extends+implements — type kind has no span suppression (module header);
    ours' surviving references are `FormPanel.SubmitEvent`-qualified and must
    not absorb."""
    base = ("public abstract class F extends FEC implements FPH {\n"
            "    public static class SubmitEvent extends GwtEvent<SubmitHandler> {\n"
            "        public void cancel() { }\n    }\n"
            "    private boolean fire() {\n"
            "        FormPanel.SubmitEvent event = new FormPanel.SubmitEvent();\n"
            "        return true;\n    }\n}\n")
    ours = ("public abstract class F extends FEC implements FPH {\n"
            "    private boolean fire() {\n"
            "        FormPanel.SubmitEvent event = new FormPanel.SubmitEvent();\n"
            "        return true;\n    }\n}\n")
    theirs = ("public abstract class F extends FEC implements FPH {\n"
              "    public static class SubmitEvent extends GwtEvent<SubmitHandler> {\n"
              "        public void cancel() { }\n    }\n"
              "    private boolean fire() {\n"
              "        SubmitEvent event = new SubmitEvent();\n"
              "        fireEvent(event);\n        return true;\n    }\n}\n")
    merged = ("public abstract class F extends FEC implements FPH {\n"
              "    private boolean fire() {\n"
              "        SubmitEvent event = new SubmitEvent();\n"
              "        fireEvent(event);\n        return true;\n    }\n}\n")
    result = _analyze_widened(tmp_path, monkeypatch, base, ours, theirs, merged)
    msgs = _stale_msgs(result)
    assert len(msgs) == 1 and "'SubmitEvent'" in msgs[0] and "type" in msgs[0]


# --- wiring: flag, abstentions, dedupe, fail-closed ---------------------- #

def test_widened_flag_off_is_silent(tmp_path, monkeypatch):
    result = _analyze_widened(tmp_path, monkeypatch, S1_BASE, S1_OURS, S1_THEIRS,
                              S1_MERGED, flag=False)
    assert result.is_clean is True
    assert result.issues == []


def test_widened_without_base_abstains(tmp_path, monkeypatch):
    """No base ⇒ no three-version differential; the Joern flow (stubbed
    empty) proceeds as before."""
    result = _analyze_widened(tmp_path, monkeypatch, S1_BASE, S1_OURS, S1_THEIRS,
                              S1_MERGED, base_present=False)
    assert result.is_clean is True


def test_widened_non_java_abstains(tmp_path, monkeypatch):
    result = _analyze_widened(tmp_path, monkeypatch, S1_BASE, S1_OURS, S1_THEIRS,
                              S1_MERGED, filename="Foo.kt")
    assert result.is_clean is True


def test_widened_conflict_markers_abstain(tmp_path, monkeypatch):
    marked = S1_MERGED + "<<<<<<< ours\nint x;\n=======\nint y;\n>>>>>>> theirs\n"
    result = _analyze_widened(tmp_path, monkeypatch, S1_BASE, S1_OURS, S1_THEIRS, marked)
    assert result.is_clean is True


@pytest.mark.parametrize("side", ["ours", "theirs"])
def test_widened_merged_identical_to_parent_never_flags(tmp_path, monkeypatch, side):
    """Soundness invariant (D1 precedent): a byte-identical wholesale merge
    cannot be merge-induced."""
    parent = S1_OURS if side == "ours" else S1_THEIRS
    result = _analyze_widened(tmp_path, monkeypatch, S1_BASE, S1_OURS, S1_THEIRS, parent)
    assert result.is_clean is True


def test_widened_dedupes_against_joern_findings(tmp_path, monkeypatch):
    """When the Joern differential reports the same name (bare-receiver
    shapes surface both ways — probe record in the module header), the
    widened site wins and the name is reported once."""
    result = _analyze_widened(tmp_path, monkeypatch, S1_BASE, S1_OURS, S1_THEIRS,
                              S1_MERGED, joern_ids=[("borrow", "isShutdown", 4)])
    stale = _stale_msgs(result)
    joern_msgs = [i.message for i in result.issues if "Unresolved identifier" in i.message]
    assert len(stale) == 1 and joern_msgs == []


def test_widened_joern_findings_for_other_names_still_reported(tmp_path, monkeypatch):
    result = _analyze_widened(tmp_path, monkeypatch, S1_BASE, S1_OURS, S1_THEIRS,
                              S1_MERGED, joern_ids=[("borrow", "somethingElse", 9)])
    assert len(_stale_msgs(result)) == 1
    assert any("'somethingElse'" in i.message for i in result.issues)


def test_widened_finding_survives_joern_failure(tmp_path, monkeypatch):
    """Joern breakage fail-closes as before, but a widened textual finding
    rides along — genuine issues win in the Stage-C verdict classifier."""
    monkeypatch.setenv("SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS", "1")

    def boom(self, path):
        raise _ur._JoernError("joern-parse failed: boom")
    monkeypatch.setattr(JoernUnresolvedReferenceStrategy, "_run_query", boom)
    p = tmp_path / "Foo.java"
    p.write_text(S1_MERGED, encoding="utf-8")
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(p), base_content=S1_BASE, ours_content=S1_OURS, theirs_content=S1_THEIRS)
    assert result.is_clean is False
    assert any("inconclusive" in i.message for i in result.issues)
    assert len(_stale_msgs(result)) == 1


def test_flag_off_joern_failure_shape_unchanged(tmp_path, monkeypatch):
    """Regression pin: with the flag off, the fail-closed result is exactly
    the pre-widening single inconclusive Issue."""
    monkeypatch.delenv("SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS", raising=False)

    def boom(self, path):
        raise _ur._JoernError("joern-parse failed: boom")
    monkeypatch.setattr(JoernUnresolvedReferenceStrategy, "_run_query", boom)
    p = tmp_path / "Foo.java"
    p.write_text(S1_MERGED, encoding="utf-8")
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(p), base_content=S1_BASE, ours_content=S1_OURS, theirs_content=S1_THEIRS)
    assert result.is_clean is False
    assert len(result.issues) == 1
    assert "inconclusive" in result.issues[0].message


# --- guard negatives (mirroring the existing lanes' guard patterns) ------ #

def _expect_silent(tmp_path, monkeypatch, base, ours, theirs, merged):
    result = _analyze_widened(tmp_path, monkeypatch, base, ours, theirs, merged)
    assert result.is_clean is True, [i.message for i in result.issues]


def test_widened_removed_by_both_sides_is_silent(tmp_path, monkeypatch):
    """No exactly-one-parent attribution ⇒ abstain (module header: mergiraf-
    dropped declarations kept by both parents are likewise out of scope)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    int f = 1;\n    int a() { return f; }\n}\n",
        "class T {\n    int a() { return 1; }\n}\n",
        "class T {\n    int a() { return 1; }\n    int b() { return f; }\n}\n",
        "class T {\n    int a() { return 1; }\n    int b() { return f; }\n}\n")


def test_widened_surviving_var_declaration_suppresses(tmp_path, monkeypatch):
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    int f = 1;\n    int a() { return f; }\n}\n",
        "class T {\n    int a() { return 1; }\n}\n",
        "class T {\n    int f = 1;\n    int a() { return f; }\n    int b() { return f; }\n}\n",
        "class T {\n    int f = 1;\n    int a() { return 1; }\n    int b() { return f; }\n}\n")


def test_widened_surviving_overload_suppresses_method_kind(tmp_path, monkeypatch):
    """Name-level method granularity: any surviving declaration (or overload)
    of the name absorbs — partial overload removal is a documented FN
    (arity-level matching is SignatureStaleCall's lane)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    void m() { }\n    void m(int x) { }\n    void go() { m(); }\n}\n",
        "class T {\n    void m(int x) { }\n    void go() { }\n}\n",
        "class T {\n    void m() { }\n    void m(int x) { }\n    void go() { m(); }\n    void b() { m(); }\n}\n",
        "class T {\n    void m(int x) { }\n    void go() { }\n    void b() { m(); }\n}\n")


def test_widened_pullup_refactor_absorbed_by_remover_usage(tmp_path, monkeypatch):
    """The remover keeps legal unqualified calls (pull-up/move refactor):
    the name resolves without a local declaration on that side, so nothing
    is merge-induced (the plan §2 'usage resolves in each parent' guard)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class A extends B {\n    void helper() { }\n    void go() { helper(); }\n}\n",
        "class A extends B {\n    void go() { helper(); }\n}\n",
        "class A extends B {\n    void helper() { }\n    void go() { helper(); }\n    void more() { helper(); }\n}\n",
        "class A extends B {\n    void go() { helper(); }\n    void more() { helper(); }\n}\n")


def test_widened_method_site_in_supertyped_body_absorbed(tmp_path, monkeypatch):
    """JLS 15.12.1: an unqualified call inside a supertyped type body may
    bind an inherited member — suppressed (signature_stale_call's span
    guard, method kind only)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class A extends B {\n    void helper() { }\n    void go() { }\n}\n",
        "class A extends B {\n    void go() { }\n}\n",
        "class A extends B {\n    void helper() { }\n    void go() { }\n    void more() { helper(); }\n}\n",
        "class A extends B {\n    void go() { }\n    void more() { helper(); }\n}\n")


def test_widened_keeper_without_usage_unattributable(tmp_path, monkeypatch):
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    int f = 1;\n}\n",
        "class T {\n}\n",
        "class T {\n    int f = 1;\n}\n",
        "class T {\n    int a() { return f; }\n}\n")


def test_widened_static_import_covers_member(tmp_path, monkeypatch):
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    static int LIMIT = 5;\n    int a() { return LIMIT; }\n}\n",
        "class T {\n    int a() { return 5; }\n}\n",
        "class T {\n    static int LIMIT = 5;\n    int a() { return LIMIT; }\n    int b() { return LIMIT + 1; }\n}\n",
        "import static com.cfg.Limits.LIMIT;\nclass T {\n    int a() { return 5; }\n    int b() { return LIMIT + 1; }\n}\n")


def test_widened_static_import_covers_method(tmp_path, monkeypatch):
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    static int calc() { return 1; }\n    int a() { return calc(); }\n}\n",
        "class T {\n    int a() { return 1; }\n}\n",
        "class T {\n    static int calc() { return 1; }\n    int a() { return calc(); }\n    int b() { return calc(); }\n}\n",
        "import static com.cfg.Math2.calc;\nclass T {\n    int a() { return 1; }\n    int b() { return calc(); }\n}\n")


def test_widened_type_import_covers_removed_inner_type(tmp_path, monkeypatch):
    _expect_silent(
        tmp_path, monkeypatch,
        "class F {\n    static class Ev { }\n    void f() { Ev e = new Ev(); }\n}\n",
        "class F {\n    void f() { }\n}\n",
        "class F {\n    static class Ev { }\n    void f() { Ev e = new Ev(); }\n    void g() { Object o = new Ev(); }\n}\n",
        "import com.foo.Ev;\nclass F {\n    void f() { }\n    void g() { Object o = new Ev(); }\n}\n")


def test_widened_java_lang_shadow_type_suppressed(tmp_path, monkeypatch):
    """Removing an inner class that shadows a java.lang type re-binds the
    usage legally (JLS 6.5.5) — never a candidate."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class F {\n    static class Process { }\n    void f() { Object o = new Process(); }\n}\n",
        "class F {\n    void f() { }\n}\n",
        "class F {\n    static class Process { }\n    void f() { Object o = new Process(); }\n    void g() { Object o = new Process(); }\n}\n",
        "class F {\n    void f() { }\n    void g() { Object o = new Process(); }\n}\n")


def test_widened_object_method_names_never_flag(tmp_path, monkeypatch):
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    public String toString() { return \"t\"; }\n    String a() { return toString(); }\n}\n",
        "class T {\n    String a() { return \"t\"; }\n}\n",
        "class T {\n    public String toString() { return \"t\"; }\n    String a() { return toString(); }\n    String b() { return toString(); }\n}\n",
        "class T {\n    String a() { return \"t\"; }\n    String b() { return toString(); }\n}\n")


def test_widened_annotation_element_name_not_a_var_usage(tmp_path, monkeypatch):
    """`timeout` in `@Test(timeout = 500)` is an annotation ELEMENT name,
    not a reference to a same-named removed field."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    long timeout = 5;\n    void a() { long x = timeout; }\n}\n",
        "class T {\n    void a() { long x = 5; }\n}\n",
        "class T {\n    long timeout = 5;\n    void a() { long x = timeout; }\n    @Test(timeout = 500)\n    void b() { }\n}\n",
        "class T {\n    void a() { long x = 5; }\n    @Test(timeout = 500)\n    void b() { }\n}\n")


def test_widened_labels_not_var_usages(tmp_path, monkeypatch):
    """A statement label and its `break`/`continue` references share the
    identifier namespace textually but are not variable reads."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    int retry = 0;\n    void a() { int x = retry; }\n}\n",
        "class T {\n    void a() { int x = 0; }\n}\n",
        "class T {\n    int retry = 0;\n    void a() { int x = retry; }\n    void b() { retry: while (true) { break retry; } }\n}\n",
        "class T {\n    void a() { int x = 0; }\n    void b() { retry: while (true) { break retry; } }\n}\n")


def test_widened_qualified_receivers_not_usages(tmp_path, monkeypatch):
    """`other.f` reads a field of a receiver this file cannot type; only
    bare and `this.`-qualified occurrences count (module header)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    int f = 1;\n    int a() { return f; }\n}\n",
        "class T {\n    int a() { return 1; }\n}\n",
        "class T {\n    int f = 1;\n    int a() { return f; }\n    int b(Other o) { return o.f; }\n}\n",
        "class T {\n    int a() { return 1; }\n    int b(Other o) { return o.f; }\n}\n")


def test_widened_this_qualified_method_call_documented_fn(tmp_path, monkeypatch):
    """`this.m()` reaches inherited members too, but the method kind mirrors
    signature_stale_call's unqualified-only rule — documented FN."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    void m() { }\n    void go() { m(); }\n}\n",
        "class T {\n    void go() { }\n}\n",
        "class T {\n    void m() { }\n    void go() { m(); }\n    void b() { this.m(); }\n}\n",
        "class T {\n    void go() { }\n    void b() { this.m(); }\n}\n")


def test_widened_lambda_parameter_shadows_in_merged(tmp_path, monkeypatch):
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    int request = 1;\n    int a() { return request; }\n}\n",
        "class T {\n    int a() { return 1; }\n}\n",
        "class T {\n    int request = 1;\n    int a() { return request; }\n    void b() { go(request -> request.x()); }\n}\n",
        "class T {\n    int a() { return 1; }\n    void b() { go(request -> request.x()); }\n}\n")


def test_widened_enum_constant_suppresses_var_kind(tmp_path, monkeypatch):
    """An enum constant of the same name survives in merged: `declares_member`
    territory (D1's dedicated constant-list parse)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    static int MODE = 1;\n    int a() { return MODE; }\n}\n",
        "class T {\n    int a() { return 1; }\n}\n",
        "class T {\n    static int MODE = 1;\n    int a() { return MODE; }\n    int b() { return MODE; }\n}\n",
        "class T {\n    enum Kind { MODE, OTHER }\n    int a() { return 1; }\n    int b() { return MODE; }\n}\n")


# --- S-D4 review-found FP vectors (each was execution-verified pre-fix) -- #

def test_widened_second_declarator_of_multi_decl_suppresses(tmp_path, monkeypatch):
    """`int a, b;` — the second declarator is a real declaration of b; the
    merged file compiles and must not flag (review finding A1)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    private int b = 1;\n    int use() { return b; }\n}\n",
        "class T {\n    int use() { return 1; }\n}\n",
        "class T {\n    private int b = 1;\n    int use() { return b; }\n    int m() { int a, b; b = 2; return b; }\n}\n",
        "class T {\n    int use() { return 1; }\n    int m() { int a, b; b = 2; return b; }\n}\n")


def test_widened_c_style_array_declarator_suppresses(tmp_path, monkeypatch):
    """`int b[];` declares b (review finding A1, C-style variant)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    private int b = 1;\n    int use() { return b; }\n}\n",
        "class T {\n    int use() { return 1; }\n}\n",
        "class T {\n    private int b = 1;\n    int use() { return b; }\n    int m() { int b[]; b = null; return 0; }\n}\n",
        "class T {\n    int use() { return 1; }\n    int m() { int b[]; b = null; return 0; }\n}\n")


def test_widened_case_arrow_label_is_not_a_declaration(tmp_path, monkeypatch):
    """`case MODE ->` is a reference; deleting the switch must not read as
    removing a declaration of MODE (review finding A2)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T implements Consts {\n    void s(int k) { switch (k) { case MODE -> go(); default -> stop(); } }\n}\n",
        "class T implements Consts {\n}\n",
        "class T implements Consts {\n    void s(int k) { switch (k) { case MODE -> go(); default -> stop(); } }\n    int g() { return MODE + 1; }\n}\n",
        "class T implements Consts {\n    int g() { return MODE + 1; }\n}\n")


def test_widened_deleted_lambda_param_is_not_a_removed_declaration(tmp_path, monkeypatch):
    """A lambda parameter is scoped: deleting the lambda does not un-declare
    the name file-wide, and an inherited-field read elsewhere must not flag
    (review finding A3 — candidates come from the field tier only)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T extends B {\n    void f(java.util.List<Integer> l) { l.forEach(x -> sink(x)); }\n}\n",
        "class T extends B {\n    void f(java.util.List<Integer> l) { }\n}\n",
        "class T extends B {\n    void f(java.util.List<Integer> l) { l.forEach(x -> sink(x)); }\n    void keep() { int y = x; }\n}\n",
        "class T extends B {\n    void f(java.util.List<Integer> l) { }\n    void keep() { int y = x; }\n}\n")


def test_widened_surviving_type_import_rebinds_receiver(tmp_path, monkeypatch):
    """JLS 6.5.2 obscuring: with the variable gone, `Config.load()` re-binds
    to the imported TYPE Config and compiles (review finding A4)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "import a.b.Config;\nclass T {\n    Config Config = new Config();\n    void go() { Config.load(); }\n}\n",
        "import a.b.Config;\nclass T {\n    void go() { }\n}\n",
        "import a.b.Config;\nclass T {\n    Config Config = new Config();\n    void go() { Config.load(); }\n    void g() { Config.load(); }\n}\n",
        "import a.b.Config;\nclass T {\n    void go() { }\n    void g() { Config.load(); }\n}\n")


def test_widened_label_after_paren_or_else_excluded(tmp_path, monkeypatch):
    """A statement label is legal after `if (…)` / `else`, not only after
    `{`/`}`/`;` (review finding C1)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    int retry = 0;\n    int a() { return retry; }\n}\n",
        "class T {\n    int a() { return 0; }\n}\n",
        "class T {\n    int retry = 0;\n    int a() { return retry; }\n    void b(boolean x) { if (x) retry: while (true) { break retry; } }\n}\n",
        "class T {\n    int a() { return 0; }\n    void b(boolean x) { if (x) retry: while (true) { break retry; } }\n}\n")


def test_widened_multi_label_case_excluded(tmp_path, monkeypatch):
    """`case FOO, MODE:` — non-first labels are still case labels
    (Java 14 multi-labels; review finding C2, fixed in the shared
    _qualified_or_case so D1 inherits the fix)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    static final int MODE = 1;\n    int a() { return MODE; }\n}\n",
        "class T {\n    int a() { return 1; }\n}\n",
        "class T {\n    static final int MODE = 1;\n    int a() { return MODE; }\n    int s(int k) { switch (k) { case FOO, MODE: return 2; } return 0; }\n}\n",
        "class T {\n    int a() { return 1; }\n    int s(int k) { switch (k) { case FOO, MODE: return 2; } return 0; }\n}\n")


def test_widened_remover_bare_type_position_absorbs(tmp_path, monkeypatch):
    """The remover deleted the nested type but kept `Ev cached;` — proof the
    name resolves without the declaration; the broad remover-side matcher
    must see bare positions the anchor-limited merged matcher skips
    (review finding C3)."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class F {\n    static class Ev { }\n    Ev cached;\n    void f() { Ev e = new Ev(); }\n}\n",
        "class F {\n    Ev cached;\n    void f() { }\n}\n",
        "class F {\n    static class Ev { }\n    Ev cached;\n    void f() { Ev e = new Ev(); }\n    void g() { Object o = new Ev(); }\n}\n",
        "class F {\n    Ev cached;\n    void f() { }\n    void g() { Object o = new Ev(); }\n}\n")


def test_type_decl_regexes_agree_with_d1(tmp_path):
    """Drift tripwire (review): _declared_type_names and D1's declares_type
    encode the same type-declaration grammar in separate regexes; if one is
    ever fixed without the other, the merged-side suppression and the
    candidate enumeration part ways — fail loudly here instead."""
    headers = [
        ("class Foo {}", "Foo"),
        ("public final class Bar {}", "Bar"),
        ("interface Baz {}", "Baz"),
        ("enum Kind {}", "Kind"),
        ("record Point(int x) {}", "Point"),
        ("@interface Marker {}", "Marker"),
        ("@ interface Spaced {}", "Spaced"),
    ]
    for text, name in headers:
        view = _ur._ipu._FileView(text)
        assert view.declares_type(name), text
        assert name in _ur._declared_type_names(view.stripped), text


# --- cross-category negatives (other lanes' shapes must not fire here) --- #

def test_widened_silent_on_import_prune_shape(tmp_path, monkeypatch):
    """D1's category: the import is pruned, not a file-local declaration."""
    _expect_silent(
        tmp_path, monkeypatch,
        "import com.foo.Gadget;\nclass T {\n    void f(Gadget g) { }\n}\n",
        "class T {\n    void f() { }\n}\n",
        "import com.foo.Gadget;\nclass T {\n    void f(Gadget g) { }\n    Gadget make() { return new Gadget(); }\n}\n",
        "class T {\n    void f() { }\n    Gadget make() { return new Gadget(); }\n}\n")


def test_widened_silent_on_signature_change_shape(tmp_path, monkeypatch):
    """D2's category: an arity change leaves the name declared — the widened
    lane is name-level by design and must stay silent."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    void send(String h, int p) { }\n    void go() { send(\"h\", 1); }\n}\n",
        "class T {\n    void send(String h, int p, boolean r) { }\n    void go() { send(\"h\", 1, true); }\n}\n",
        "class T {\n    void send(String h, int p) { }\n    void go() { send(\"h\", 1); }\n    void alert() { send(\"a\", 2); }\n}\n",
        "class T {\n    void send(String h, int p, boolean r) { }\n    void go() { send(\"h\", 1, true); }\n    void alert() { send(\"a\", 2); }\n}\n")


def test_widened_silent_on_fully_applied_rename(tmp_path, monkeypatch):
    """A clean rename (all references updated, wholesale ours) has no stale
    site — and is also caught by the merged==parent invariant."""
    base = "class T {\n    int oldF = 1;\n    int a() { return oldF; }\n}\n"
    ours = "class T {\n    int newF = 1;\n    int a() { return newF; }\n}\n"
    _expect_silent(tmp_path, monkeypatch, base, ours, base, ours)


def test_widened_clean_refactor_with_unrelated_edits_silent(tmp_path, monkeypatch):
    """Both sides edit disjoint members, nothing removed-and-referenced."""
    _expect_silent(
        tmp_path, monkeypatch,
        "class T {\n    int a() { return 1; }\n    int b() { return 2; }\n}\n",
        "class T {\n    int a() { return 10; }\n    int b() { return 2; }\n}\n",
        "class T {\n    int a() { return 1; }\n    int b() { return 20; }\n}\n",
        "class T {\n    int a() { return 10; }\n    int b() { return 20; }\n}\n")


# --- live-Joern integration (widened + Joern paths compose) -------------- #

@pytest.mark.skipif(not JOERN, reason="joern-parse not on PATH")
def test_widened_live_joern_union_and_dedupe(tmp_path, monkeypatch):
    """End-to-end with real Joern: the bare-receiver S1 shape is caught by
    BOTH the widened pre-pass and the Joern differential (probe record) —
    the union reports the name once, and the erudika identifier shape keeps
    its Joern flag alongside."""
    monkeypatch.setenv("SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS", "1")
    merged = _write(tmp_path, MERGED_STALE)
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(merged), base_content=OURS_RENAMED, ours_content=OURS_RENAMED,
        theirs_content=THEIRS_OLD_NAME)
    assert not result.is_clean
    assert any("Unresolved identifier 'm'" in i.message for i in result.issues)


@pytest.mark.skipif(not JOERN, reason="joern-parse not on PATH")
def test_widened_live_joern_flag_off_matches_pre_widening(tmp_path, monkeypatch):
    """Regression floor, live: flag off ⇒ the widened pre-pass contributes
    nothing and the Joern verdicts are the lane's old ones."""
    monkeypatch.delenv("SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS", raising=False)
    p = tmp_path / "Pool.java"
    p.write_text(S1_MERGED, encoding="utf-8")
    result = JoernUnresolvedReferenceStrategy().analyze(
        str(p), base_content=S1_BASE, ours_content=S1_OURS, theirs_content=S1_THEIRS)
    assert _stale_msgs(result) == []
