from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Issue:
    line_number: int
    severity: str  # 'CRITICAL', 'WARNING'
    message: str
    strategy_name: str

@dataclass
class AnalysisResult:
    is_clean: bool
    issues: List[Issue]

class MergeStrategy(ABC):
    """
    The Interface that all analysis strategies must implement.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the strategy."""
        pass

    @abstractmethod
    def analyze(self, file_path: str, base_content: str = None,
                ours_content: str = None, theirs_content: str = None) -> AnalysisResult:
        """
        Analyze the proposed merged file for specific defects.

        Args:
            file_path: Path to the temporary merged file on disk (Git's %A).
            base_content: Optional content of the ancestor for comparison.
            ours_content: Optional content of the "ours" side (Git's %A before
                the backend overwrote it). Enables 3-way / merge-induced checks.
            theirs_content: Optional content of the "theirs" side (Git's %B).

        Strategies that only need the merged file may ignore base/ours/theirs.

        Returns:
            AnalysisResult object containing found issues.
        """
        pass