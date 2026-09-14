"""AutoBackend — unit tests with mocked classifier + mocked sub-backends.

No Docker required. The classifier and all four sub-backends (primary,
fallback, spork, weave) are injected via the constructor; tests construct
AutoBackend with stubs that return controlled cluster labels and outcomes.

Live integration of the dispatch path (real classifier + real backends) is
covered by the image-gated classifier/backend tests and the end-to-end
auto-routing harness. AutoBackend itself is plumbing — the appropriate unit
boundary is mocked.

Routing contract under test — post-flip default (#27/#28 DROP, 2026-06-27):
    NONE                         → git-merge-file (fallback instance)
    everything else              → Mergiraf (primary)
    any routed backend CRASH     → git-merge-file (fallback)

Refuted specialist arms, opt-in via SEMANTIC_MERGE_SPECIALIST_ROUTING=1
(kept as apparatus; reproduces the P2 pre-flip behavior):
    MIGRATE_DECL                 → Weave
    INTRA_BODY + language=JAVA   → Spork
    INTRA_BODY + non-Java        → Mergiraf (language gate fallthrough)
"""
import pytest

from core.backends.auto_backend import SPECIALIST_ROUTING_ENV, AutoBackend
from core.backends.base import MergeBackend, MergeOutcome
from core.refactoring_classifier import Cluster


@pytest.fixture(autouse=True)
def _specialist_flag_off(monkeypatch):
    """Default tests run with the refuted-arms flag unset, regardless of the
    ambient environment. Flag-on tests set it explicitly."""
    monkeypatch.delenv(SPECIALIST_ROUTING_ENV, raising=False)


class _StubClassifier:
    def __init__(self, cluster: Cluster):
        self._cluster = cluster
        self.calls = 0

    def cluster(self, base_path, ours_path, theirs_path):
        self.calls += 1
        return self._cluster


class _RaisingClassifier:
    def cluster(self, base_path, ours_path, theirs_path):
        raise RuntimeError("classifier exploded")


class _StubBackend(MergeBackend):
    def __init__(self, name: str, outcome: MergeOutcome):
        self._name = name
        self._outcome = outcome
        self.calls = 0

    @property
    def name(self):
        return self._name

    def merge(self, base_path, ours_path, theirs_path):
        self.calls += 1
        return self._outcome


def _make_backend(cluster=Cluster.NONE,
                  primary_outcome=MergeOutcome.CLEAN,
                  fallback_outcome=MergeOutcome.CLEAN,
                  spork_outcome=MergeOutcome.CLEAN,
                  weave_outcome=MergeOutcome.CLEAN,
                  classifier=None):
    primary = _StubBackend("mergiraf", primary_outcome)
    fallback = _StubBackend("git", fallback_outcome)
    spork = _StubBackend("spork", spork_outcome)
    weave = _StubBackend("weave", weave_outcome)
    classifier = classifier or _StubClassifier(cluster)
    auto = AutoBackend(classifier=classifier, primary=primary,
                       fallback=fallback, spork=spork, weave=weave)
    return auto, classifier, primary, fallback, spork, weave


def _write_trio(tmp_path, ext=".java"):
    base = tmp_path / f"base{ext}"; base.write_text("a")
    ours = tmp_path / f"ours{ext}"; ours.write_text("a")
    theirs = tmp_path / f"theirs{ext}"; theirs.write_text("a")
    return str(base), str(ours), str(theirs)


def test_name_is_auto():
    auto, *_ = _make_backend()
    assert auto.name == "auto"


# (cluster, file-extension, expected backend role) — DEFAULT map (flag off:
# NONE→git, everything else→Mergiraf). Module-level so the completeness test
# below can assert every Cluster enum member is covered.
ROUTING_CASES = [
    (Cluster.NONE, ".java", "fallback"),
    (Cluster.MIGRATE_DECL, ".java", "primary"),   # refuted Weave arm OFF by default
    (Cluster.INTRA_BODY, ".java", "primary"),     # refuted Spork arm OFF by default
    (Cluster.INTRA_BODY, ".py", "primary"),
    (Cluster.SYMBOL_CASCADE, ".java", "primary"),
    (Cluster.CONTAINER_MOVE, ".java", "primary"),
    (Cluster.HIERARCHY_RESHAPE, ".java", "primary"),
    (Cluster.LOCAL_DECL_EDIT, ".java", "primary"),
]

# Same shape, with SEMANTIC_MERGE_SPECIALIST_ROUTING=1 — the refuted arms
# (pre-flip P2 behavior) must be reproducible on demand.
SPECIALIST_ROUTING_CASES = [
    (Cluster.NONE, ".java", "fallback"),          # flag does not affect NONE
    (Cluster.MIGRATE_DECL, ".java", "weave"),
    (Cluster.INTRA_BODY, ".java", "spork"),
    (Cluster.INTRA_BODY, ".py", "primary"),       # language gate: non-Java → Mergiraf
    (Cluster.SYMBOL_CASCADE, ".java", "primary"),
]


def _assert_routes(cluster, ext, expected, tmp_path):
    auto, classifier, primary, fallback, spork, weave = _make_backend(cluster=cluster)
    outcome = auto.merge(*_write_trio(tmp_path, ext))

    assert outcome == MergeOutcome.CLEAN
    assert classifier.calls == 1
    backends = {"primary": primary, "fallback": fallback,
                "spork": spork, "weave": weave}
    chosen = backends.pop(expected)
    assert chosen.calls == 1, f"{cluster.value}/{ext} should route to {expected}"
    for nm, b in backends.items():
        assert b.calls == 0, f"{cluster.value}/{ext} unexpectedly called {nm}"


@pytest.mark.parametrize("cluster,ext,expected", ROUTING_CASES)
def test_routing_map(cluster, ext, expected, tmp_path):
    _assert_routes(cluster, ext, expected, tmp_path)


@pytest.mark.parametrize("cluster,ext,expected", SPECIALIST_ROUTING_CASES)
def test_routing_map_specialist_flag_on(cluster, ext, expected, tmp_path, monkeypatch):
    monkeypatch.setenv(SPECIALIST_ROUTING_ENV, "1")
    _assert_routes(cluster, ext, expected, tmp_path)


def test_flag_value_other_than_1_stays_default(tmp_path, monkeypatch):
    """Only the literal "1" enables the refuted arms — "true"/"on"/etc. do not."""
    monkeypatch.setenv(SPECIALIST_ROUTING_ENV, "true")
    _assert_routes(Cluster.MIGRATE_DECL, ".java", "primary", tmp_path)


def test_routing_map_covers_every_cluster():
    """Completeness guard: every Cluster enum member must have an explicit
    routing case above. Without this, adding a new Cluster value would
    silently fall through `_route`'s `else` to Mergiraf with no test
    flagging that the routing decision was never made deliberately.
    """
    covered = {cluster for (cluster, _ext, _expected) in ROUTING_CASES}
    missing = set(Cluster) - covered
    assert not missing, (
        f"Cluster value(s) with no explicit routing-map test case: "
        f"{sorted(c.value for c in missing)}. Add a case to ROUTING_CASES "
        f"(and a routing decision in AutoBackend._route) before merging."
    )


def test_primary_clean_returned_as_is(tmp_path):
    auto, _, primary, fallback, _, _ = _make_backend(
        cluster=Cluster.SYMBOL_CASCADE, primary_outcome=MergeOutcome.CLEAN)
    outcome = auto.merge(*_write_trio(tmp_path))
    assert outcome == MergeOutcome.CLEAN
    assert primary.calls == 1
    assert fallback.calls == 0


def test_primary_conflict_returned_without_fallback(tmp_path):
    """CONFLICT is a valid outcome with markers, not a crash. No fallback."""
    auto, _, primary, fallback, _, _ = _make_backend(
        cluster=Cluster.SYMBOL_CASCADE, primary_outcome=MergeOutcome.CONFLICT)
    outcome = auto.merge(*_write_trio(tmp_path))
    assert outcome == MergeOutcome.CONFLICT
    assert primary.calls == 1
    assert fallback.calls == 0


def test_primary_crash_falls_back_to_git(tmp_path):
    auto, _, primary, fallback, _, _ = _make_backend(
        cluster=Cluster.SYMBOL_CASCADE,
        primary_outcome=MergeOutcome.CRASH,
        fallback_outcome=MergeOutcome.CLEAN,
    )
    outcome = auto.merge(*_write_trio(tmp_path))
    assert outcome == MergeOutcome.CLEAN
    assert primary.calls == 1
    assert fallback.calls == 1


def test_specialist_crash_falls_back_to_git(tmp_path, monkeypatch):
    """A specialist (Weave on MIGRATE_DECL, flag on) crashing → git fallback.
    Keeps the specialist-crash-fallback path exercised now that the arms are
    opt-in (#27/#28)."""
    monkeypatch.setenv(SPECIALIST_ROUTING_ENV, "1")
    auto, _, primary, fallback, spork, weave = _make_backend(
        cluster=Cluster.MIGRATE_DECL,
        weave_outcome=MergeOutcome.CRASH,
        fallback_outcome=MergeOutcome.CLEAN,
    )
    outcome = auto.merge(*_write_trio(tmp_path))
    assert outcome == MergeOutcome.CLEAN
    assert weave.calls == 1
    assert fallback.calls == 1
    assert primary.calls == 0


def test_double_crash_returns_crash(tmp_path):
    auto, _, primary, fallback, _, _ = _make_backend(
        cluster=Cluster.SYMBOL_CASCADE,
        primary_outcome=MergeOutcome.CRASH,
        fallback_outcome=MergeOutcome.CRASH,
    )
    outcome = auto.merge(*_write_trio(tmp_path))
    assert outcome == MergeOutcome.CRASH
    assert primary.calls == 1
    assert fallback.calls == 1


def test_none_routes_to_git_no_double_fallback(tmp_path):
    """NONE → git (fallback instance). If git itself crashes there is nothing
    better to try: CRASH is returned, fallback is not invoked twice."""
    auto, _, primary, fallback, _, _ = _make_backend(
        cluster=Cluster.NONE, fallback_outcome=MergeOutcome.CRASH)
    outcome = auto.merge(*_write_trio(tmp_path))
    assert outcome == MergeOutcome.CRASH
    assert fallback.calls == 1
    assert primary.calls == 0


def test_classifier_exception_treated_as_none(tmp_path):
    """Defensive: classifier *should* fail-closed → NONE, but if it raises
    anyway, AutoBackend honours must-not-raise and routes NONE → git."""
    auto, _, primary, fallback, _, _ = _make_backend(
        fallback_outcome=MergeOutcome.CLEAN,
        classifier=_RaisingClassifier(),
    )
    outcome = auto.merge(*_write_trio(tmp_path))
    assert outcome == MergeOutcome.CLEAN
    assert fallback.calls == 1
    assert primary.calls == 0


def test_dispatch_log_shape(tmp_path, capsys):
    auto, *_ = _make_backend(cluster=Cluster.SYMBOL_CASCADE)
    auto.merge(*_write_trio(tmp_path))
    err = capsys.readouterr().err
    assert "cluster=SYMBOL_CASCADE" in err
    assert "language=java" in err
    assert "→ mergiraf" in err


def test_migrate_decl_routes_to_mergiraf_by_default(tmp_path, capsys):
    """Post-flip default: the refuted Weave arm is off — MIGRATE_DECL → Mergiraf."""
    auto, *_ = _make_backend(cluster=Cluster.MIGRATE_DECL)
    auto.merge(*_write_trio(tmp_path))
    err = capsys.readouterr().err
    assert "cluster=MIGRATE_DECL" in err
    assert "→ mergiraf" in err


def test_specialist_dispatch_log_shape(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv(SPECIALIST_ROUTING_ENV, "1")
    auto, *_ = _make_backend(cluster=Cluster.MIGRATE_DECL)
    auto.merge(*_write_trio(tmp_path))
    err = capsys.readouterr().err
    assert "cluster=MIGRATE_DECL" in err
    assert "→ weave" in err


def test_fallback_log_shape(tmp_path, capsys):
    auto, *_ = _make_backend(
        cluster=Cluster.SYMBOL_CASCADE,
        primary_outcome=MergeOutcome.CRASH,
        fallback_outcome=MergeOutcome.CLEAN,
    )
    auto.merge(*_write_trio(tmp_path))
    err = capsys.readouterr().err
    assert "mergiraf crashed" in err
    assert "falling back to git" in err


def test_unknown_language_does_not_break_log(tmp_path, capsys):
    """Unrecognized extension → language=UNKNOWN; NONE still routes to git."""
    auto, _, primary, fallback, _, _ = _make_backend(cluster=Cluster.NONE)
    f = tmp_path / "ours.xyz"; f.write_text("a")
    outcome = auto.merge(str(f), str(f), str(f))
    assert outcome == MergeOutcome.CLEAN
    assert fallback.calls == 1
    assert "language=unknown" in capsys.readouterr().err


def test_default_construction_uses_real_components():
    """Smoke check: bare AutoBackend() composes real classifier + all four
    sub-backends (classifier, Mergiraf, git, Spork, Weave). Doesn't invoke
    .merge() — that would require Docker. Confirms the no-arg constructor
    works (no missing imports, no typos in the class refs).
    """
    auto = AutoBackend()
    assert auto.name == "auto"
