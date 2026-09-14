"""RefactoringClusterClassifier — unit + image-gated integration tests.

Unit tests bypass Docker by monkeypatching `_detect_pair`. They cover:
- one cluster per representative refactoring type,
- precedence on multi-cluster scenarios,
- empty-refactoring fallthrough → NONE,
- fail-closed paths: subprocess error, missing image, non-zero rc, malformed
  JSON, timeout — all return NONE without raising.

The integration test runs the real Docker image against a toy Rename Method
fixture; it skips cleanly when Docker or `merge-tools/refactoring-miner:2.4.0`
aren't available.

The map-completeness test asserts the 98-entry RM2 2.4.0 enum is fully
covered by TYPE_TO_CLUSTERS — drift-detection in case RM2 grows the enum.
"""
from __future__ import annotations

import json
import subprocess

import pytest

from core.refactoring_classifier import (
    PRECEDENCE,
    RM2_IMAGE,
    Cluster,
    RefactoringClusterClassifier,
    TYPE_TO_CLUSTERS,
    _resolve_precedence,
)


# --- Pure-mapping tests (no subprocess) ---

def test_type_map_has_98_entries():
    """Drift-detection: RM2 2.4.0 ships 98 RefactoringType enum constants;
    every one must be classified. If RM2 grows the enum, this test fires."""
    assert len(TYPE_TO_CLUSTERS) == 98


def test_every_mapping_value_is_nonempty_frozenset_of_clusters():
    for rtype, clusters in TYPE_TO_CLUSTERS.items():
        assert isinstance(clusters, frozenset), rtype
        assert clusters, f"{rtype} maps to empty set"
        for c in clusters:
            assert isinstance(c, Cluster), f"{rtype} → non-Cluster {c!r}"


def test_precedence_covers_all_clusters_exactly_once():
    assert set(PRECEDENCE) == set(Cluster)
    assert len(PRECEDENCE) == len(Cluster)


@pytest.mark.parametrize("clusters,expected", [
    ({Cluster.LOCAL_DECL_EDIT}, Cluster.LOCAL_DECL_EDIT),
    ({Cluster.HIERARCHY_RESHAPE, Cluster.LOCAL_DECL_EDIT}, Cluster.HIERARCHY_RESHAPE),
    ({Cluster.MIGRATE_DECL, Cluster.SYMBOL_CASCADE}, Cluster.MIGRATE_DECL),
    ({Cluster.INTRA_BODY, Cluster.SYMBOL_CASCADE}, Cluster.INTRA_BODY),
    ({Cluster.CONTAINER_MOVE, Cluster.SYMBOL_CASCADE}, Cluster.SYMBOL_CASCADE),
    ({Cluster.NONE}, Cluster.NONE),
])
def test_resolve_precedence(clusters, expected):
    assert _resolve_precedence(clusters) is expected


# --- Synthetic-output classifier tests (mock _detect_pair) ---

def _classifier_with_pairs(ours_types: set[str], theirs_types: set[str], monkeypatch):
    """Build a classifier whose two _detect_pair calls return the given sets."""
    classifier = RefactoringClusterClassifier()
    calls = {"n": 0}

    def fake_detect(left, right):
        calls["n"] += 1
        return ours_types if calls["n"] == 1 else theirs_types

    monkeypatch.setattr(classifier, "_detect_pair", fake_detect)
    return classifier


@pytest.mark.parametrize("rtype,expected", [
    ("Extract Method", Cluster.MIGRATE_DECL),
    ("Inline Variable", Cluster.INTRA_BODY),
    ("Rename Method", Cluster.SYMBOL_CASCADE),
    ("Move Class", Cluster.CONTAINER_MOVE),
    ("Collapse Hierarchy", Cluster.HIERARCHY_RESHAPE),
    ("Add Method Annotation", Cluster.LOCAL_DECL_EDIT),
])
def test_single_type_per_cluster(rtype, expected, monkeypatch):
    classifier = _classifier_with_pairs({rtype}, set(), monkeypatch)
    assert classifier.cluster("/b", "/o", "/t") is expected


def test_empty_branches_return_none(monkeypatch):
    classifier = _classifier_with_pairs(set(), set(), monkeypatch)
    assert classifier.cluster("/b", "/o", "/t") is Cluster.NONE


def test_unknown_type_alone_returns_none(monkeypatch):
    """A future RM2 type not in TYPE_TO_CLUSTERS contributes Cluster.NONE only;
    if it's the only signal, the result is NONE."""
    classifier = _classifier_with_pairs({"Some Future Refactoring"}, set(), monkeypatch)
    assert classifier.cluster("/b", "/o", "/t") is Cluster.NONE


def test_unknown_type_dominated_by_known(monkeypatch):
    """An unknown type contributes Cluster.NONE; when paired with a known type
    of higher precedence, the known type's cluster wins. Verifies that future
    RM2 enum growth degrades gracefully — unknown types are silently absorbed
    rather than poisoning a real classification."""
    classifier = _classifier_with_pairs(
        {"Some Future Refactoring", "Extract Method"}, set(), monkeypatch,
    )
    assert classifier.cluster("/b", "/o", "/t") is Cluster.MIGRATE_DECL


def test_precedence_across_branches(monkeypatch):
    """Ours has a SYMBOL_CASCADE rename; theirs has a MIGRATE_DECL extract.
    Precedence picks MIGRATE_DECL."""
    classifier = _classifier_with_pairs(
        {"Rename Method"}, {"Extract Method"}, monkeypatch,
    )
    assert classifier.cluster("/b", "/o", "/t") is Cluster.MIGRATE_DECL


def test_compound_type_resolved_by_precedence(monkeypatch):
    """A single compound type (Move And Rename Method → {MIGRATE_DECL,
    SYMBOL_CASCADE}) resolves to MIGRATE_DECL alone."""
    classifier = _classifier_with_pairs({"Move And Rename Method"}, set(), monkeypatch)
    assert classifier.cluster("/b", "/o", "/t") is Cluster.MIGRATE_DECL


def test_local_decl_edit_alone_returns_local(monkeypatch):
    classifier = _classifier_with_pairs(
        {"Add Method Annotation", "Remove Class Annotation"}, set(), monkeypatch,
    )
    assert classifier.cluster("/b", "/o", "/t") is Cluster.LOCAL_DECL_EDIT


# --- Fail-closed tests for _detect_pair (real method, mocked subprocess) ---

def _stage(tmp_path):
    base = tmp_path / "base.java"
    ours = tmp_path / "ours.java"
    theirs = tmp_path / "theirs.java"
    for p in (base, ours, theirs):
        p.write_text("class A {}\n")
    return str(base), str(ours), str(theirs)


def test_fail_closed_on_missing_docker(tmp_path, monkeypatch):
    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("docker: not found")

    monkeypatch.setattr(subprocess, "run", raise_file_not_found)
    base, ours, theirs = _stage(tmp_path)

    assert RefactoringClusterClassifier().cluster(base, ours, theirs) is Cluster.NONE


def test_fail_closed_on_nonzero_rc(tmp_path, monkeypatch):
    """Docker exits non-zero (e.g., image missing). Classifier returns NONE."""
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0], returncode=125, stdout="", stderr="image not found",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    base, ours, theirs = _stage(tmp_path)

    assert RefactoringClusterClassifier().cluster(base, ours, theirs) is Cluster.NONE


def test_fail_closed_on_malformed_json(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0], returncode=0, stdout="not valid json {[", stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    base, ours, theirs = _stage(tmp_path)

    assert RefactoringClusterClassifier().cluster(base, ours, theirs) is Cluster.NONE


def test_fail_closed_on_timeout(tmp_path, monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="docker", timeout=1)

    monkeypatch.setattr(subprocess, "run", raise_timeout)
    base, ours, theirs = _stage(tmp_path)

    assert RefactoringClusterClassifier().cluster(base, ours, theirs) is Cluster.NONE


def test_detect_pair_parses_real_rm2_json_shape(tmp_path, monkeypatch):
    """End-to-end through _detect_pair with a synthetic RM2-shaped payload."""
    payload = {
        "directories": {"left": "/data/left", "right": "/data/right"},
        "refactorings": [
            {"type": "Rename Method", "description": "..."},
            {"type": "Extract Method", "description": "..."},
        ],
    }

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0], returncode=0, stdout=json.dumps(payload), stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    base, ours, theirs = _stage(tmp_path)

    # Both pair calls return the same 2 types. Union → {Rename Method,
    # Extract Method} → contributions {SYMBOL_CASCADE, MIGRATE_DECL} →
    # precedence picks MIGRATE_DECL.
    assert RefactoringClusterClassifier().cluster(base, ours, theirs) is Cluster.MIGRATE_DECL


# --- Integration test: real Docker, real image, toy fixture ---

def _docker_image_available():
    try:
        subprocess.run(
            ["docker", "image", "inspect", RM2_IMAGE],
            capture_output=True, check=True,
        )
        return True
    except (FileNotFoundError, OSError, subprocess.CalledProcessError):
        return False


REQUIRES_RM2_IMAGE = pytest.mark.skipif(
    not _docker_image_available(),
    reason=f"Docker or {RM2_IMAGE} image not available; "
           f"build via `cd merge-tool-comparison && docker build -t {RM2_IMAGE} docker/refactoring_miner/`",
)


@REQUIRES_RM2_IMAGE
def test_integration_rename_method_detected_as_symbol_cascade(tmp_path):
    """Real RM2 against a toy Rename Method fixture should yield SYMBOL_CASCADE.

    Three files (base, ours, theirs) — only `ours` renames the method, so
    the classifier sees Rename Method on the (base, ours) pair and an empty
    set on (base, theirs). Union → {Rename Method} → SYMBOL_CASCADE.
    """
    base = tmp_path / "Foo.java"
    ours = tmp_path / "Foo_ours.java"
    theirs = tmp_path / "Foo_theirs.java"

    base.write_text(
        "package com.example;\n"
        "public class Foo {\n"
        "  public int oldName(int a, int b) { return a + b; }\n"
        "}\n"
    )
    ours.write_text(
        "package com.example;\n"
        "public class Foo {\n"
        "  public int newName(int a, int b) { return a + b; }\n"
        "}\n"
    )
    theirs.write_text(base.read_text())

    result = RefactoringClusterClassifier().cluster(str(base), str(ours), str(theirs))

    assert result is Cluster.SYMBOL_CASCADE
