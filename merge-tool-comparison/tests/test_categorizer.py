"""Tests for the R2 scenario categorizer, incl. the cross-project parity guard.

`test_taxonomy_parity` is the safety net for the deliberate decision to *copy*
(not cross-project-import) the RM2 type→cluster taxonomy: it imports the single
source of truth — `semantic_merge_driver/core/refactoring_classifier.py` — by
file path and asserts byte-equivalence of the enum, precedence, and mapping.
If the driver's taxonomy ever changes without the copy being updated, this
fails loudly.
"""
import importlib.util
from pathlib import Path

import pytest

from src.evaluation.categorizer import (
    PRECEDENCE,
    TYPE_TO_CLUSTERS,
    Cluster,
    cluster_of,
)

DRIVER_CLASSIFIER = (
    Path(__file__).resolve().parents[2]
    / "semantic_merge_driver"
    / "core"
    / "refactoring_classifier.py"
)


def _load_driver_module():
    spec = importlib.util.spec_from_file_location(
        "_driver_refactoring_classifier", DRIVER_CLASSIFIER
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_taxonomy_parity():
    """Copy must stay byte-equivalent to the R4a single source of truth.

    Skip — do not fail — when the driver source is absent (e.g.
    merge-tool-comparison checked out without its sibling project). Absence
    means parity is *unverifiable*, not *violated*; only an actual drift
    while the source is present should redden this suite.
    """
    if not DRIVER_CLASSIFIER.is_file():
        pytest.skip(f"driver source absent ({DRIVER_CLASSIFIER}); parity unverifiable")
    driver = _load_driver_module()

    # Cluster value set identical.
    assert {c.value for c in Cluster} == {c.value for c in driver.Cluster}

    # Precedence order identical (compared by value — distinct enum classes).
    assert [c.value for c in PRECEDENCE] == [c.value for c in driver.PRECEDENCE]

    # Mapping identical: same keys, same cluster-value sets per key.
    def norm(table):
        return {k: sorted(c.value for c in v) for k, v in table.items()}

    assert norm(TYPE_TO_CLUSTERS) == norm(driver.TYPE_TO_CLUSTERS)
    assert len(TYPE_TO_CLUSTERS) == 98


def test_empty_tags_is_none():
    assert cluster_of([], []) == "NONE"


def test_unknown_type_is_none():
    assert cluster_of(["Totally Made Up Refactoring"], []) == "NONE"


@pytest.mark.parametrize(
    "rtype,expected",
    [
        ("Extract Method", "MIGRATE_DECL"),
        ("Rename Variable", "INTRA_BODY"),
        ("Rename Method", "SYMBOL_CASCADE"),
        ("Move Class", "CONTAINER_MOVE"),
        ("Collapse Hierarchy", "HIERARCHY_RESHAPE"),
        ("Add Method Annotation", "LOCAL_DECL_EDIT"),
    ],
)
def test_single_type_maps_to_cluster(rtype, expected):
    assert cluster_of([rtype], []) == expected


def test_precedence_picks_hardest_for_line_merge():
    # MIGRATE_DECL outranks INTRA_BODY when both present across the union.
    assert cluster_of(["Extract Method"], ["Rename Variable"]) == "MIGRATE_DECL"
    # SYMBOL_CASCADE outranks CONTAINER_MOVE.
    assert cluster_of(["Rename Method", "Move Class"], []) == "SYMBOL_CASCADE"


def test_union_across_both_axes():
    # A type on theirs only still contributes to the union.
    assert cluster_of([], ["Extract Method"]) == "MIGRATE_DECL"


def test_compound_type_resolves_via_precedence():
    # "Move And Rename Method" → {MIGRATE_DECL, SYMBOL_CASCADE} → MIGRATE_DECL.
    assert cluster_of(["Move And Rename Method"], []) == "MIGRATE_DECL"
