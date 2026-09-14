"""MergeBackend ABC + MergeOutcome enum.

Backends perform the three-way merge step: given paths to base, ours, and
theirs, they produce a merged file by mutating `ours_path` in place.
Strategies (separate ABC at core/interfaces.py:MergeStrategy) inspect the
merged file afterwards; the two abstractions are intentionally disjoint —
backends merge, strategies analyse.

Fail-closed contract: implementations must NOT raise on subprocess errors,
missing binaries, or other expected failures. Return MergeOutcome.CRASH
so the driver can reject the merge.
"""
from abc import ABC, abstractmethod
from enum import Enum


class MergeOutcome(str, Enum):
    """Result of a three-way merge attempt."""

    CLEAN = "clean"
    """Merged successfully; no conflict markers in output."""

    CONFLICT = "conflict"
    """Output was written but contains conflict markers (e.g., <<<<<<<).
    Caller treats this as a rejected merge."""

    CRASH = "crash"
    """Backend itself failed (subprocess error, missing tool, etc.).
    Caller fail-closes and rejects the merge."""


class MergeBackend(ABC):
    """Contract for three-way merge implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this backend (e.g., 'git', 'mergiraf')."""

    @abstractmethod
    def merge(
        self, base_path: str, ours_path: str, theirs_path: str
    ) -> MergeOutcome:
        """Three-way merge: combine base + ours + theirs into a single file.

        Mutates `ours_path` in place with the merged content.

        Args:
            base_path: path to the common-ancestor revision.
            ours_path: path to the current-branch revision; mutated in place.
            theirs_path: path to the incoming revision.

        Returns:
            MergeOutcome.CLEAN — merged successfully, no conflict markers.
            MergeOutcome.CONFLICT — output written but contains markers.
            MergeOutcome.CRASH — backend failed (e.g., subprocess error).

        Must NOT raise. Implementations catch expected exceptions and
        return CRASH so the caller can fail-closed.
        """
