from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Optional


class MergeOutcome(Enum):
    CLEAN = "clean"
    CONFLICT = "conflict"
    CRASH = "crash"
    TIMEOUT = "timeout"


@dataclass
class MergeResult:
    outcome: MergeOutcome
    merged_content: Optional[str]
    conflict_count: int
    runtime_seconds: float
    raw_stdout: str = ""
    raw_stderr: str = ""

    @property
    def is_clean(self) -> bool:
        return self.outcome == MergeOutcome.CLEAN


@dataclass
class MergeScenario:
    scenario_id: str
    repo_name: str
    merge_commit: str
    file_path: str
    base_content: str
    ours_content: str
    theirs_content: str
    developer_resolution: str
    category: str = "unknown"
    # RM2-detected refactoring type names per branch axis, file-level.
    # Written by tools/rm2_tag.py (Phase R1): {"ours": [...], "theirs": [...]}.
    # Empty dict = scenario not yet tagged (distinct from a tagged-but-empty axis).
    refactorings: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "repo_name": self.repo_name,
            "merge_commit": self.merge_commit,
            "file_path": self.file_path,
            "base_content": self.base_content,
            "ours_content": self.ours_content,
            "theirs_content": self.theirs_content,
            "developer_resolution": self.developer_resolution,
            "category": self.category,
            "refactorings": self.refactorings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MergeScenario":
        # Filter to known fields: tolerates extra/legacy JSON keys instead of
        # raising TypeError, so schema additions stay backwards-compatible.
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


class MergeTool(ABC):
    """Abstract base for all merge tool adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this tool."""
        ...

    @property
    def docker_image(self) -> Optional[str]:
        """Docker image name, or None if tool runs natively."""
        return None

    @abstractmethod
    def merge(self, base: str, ours: str, theirs: str, timeout: int = 60) -> MergeResult:
        """
        Run three-way merge on file contents.

        Args:
            base: Content of the common ancestor.
            ours: Content of the current branch version.
            theirs: Content of the other branch version.
            timeout: Maximum seconds to wait.

        Returns:
            MergeResult with normalized outcome and content.
        """
        ...
