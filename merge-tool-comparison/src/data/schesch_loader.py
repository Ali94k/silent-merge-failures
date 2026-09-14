"""
Loader for the Schesch et al. (ASE 2024) merge scenario dataset.

The dataset stores merge scenarios as git references (repo slug + commit SHAs),
not inline file contents. This loader:
1. Reads merge CSVs from the dataset
2. Clones referenced repos
3. Checks out base/ours/theirs/resolution from git
4. Outputs MergeScenario objects compatible with the existing pipeline

Dataset sources:
- Zenodo: https://zenodo.org/records/13366866
- GitHub: https://github.com/benedikt-schesch/AST-Merging-Evaluation
"""

import csv
import json
import logging
from pathlib import Path
from typing import Optional

from git import Repo, GitCommandError

from src.core.interfaces import MergeScenario

logger = logging.getLogger(__name__)


class ScheschDatasetLoader:
    """Load merge scenarios from Schesch et al. (ASE 2024) dataset."""

    def __init__(
        self,
        dataset_path: str,
        repos_dir: str = "data/repos",
    ):
        self.dataset_path = Path(dataset_path)
        self.repos_dir = Path(repos_dir)
        self.repos_dir.mkdir(parents=True, exist_ok=True)

    def load(
        self,
        max_scenarios: Optional[int] = None,
        filter_repos: Optional[list[str]] = None,
    ) -> list[MergeScenario]:
        """Load scenarios from CSV merge files.

        Args:
            max_scenarios: Maximum total scenarios to load.
            filter_repos: Only load from these repo slugs (e.g. ["google/guava"]).

        Returns:
            List of MergeScenario objects with file contents extracted from git.
        """
        merge_csvs = self._find_merge_csvs()
        if not merge_csvs:
            logger.error(f"No merge CSV files found in {self.dataset_path}")
            return []

        scenarios: list[MergeScenario] = []

        for csv_path in merge_csvs:
            if max_scenarios and len(scenarios) >= max_scenarios:
                break

            repo_slug = self._repo_slug_from_path(csv_path)
            if filter_repos and repo_slug not in filter_repos:
                continue

            repo_name = repo_slug.replace("/", "_")
            logger.info(f"Processing {repo_slug}")

            rows = self._read_merge_csv(csv_path)
            repo = self._clone_or_open(repo_slug)
            if not repo:
                continue

            for row in rows:
                if max_scenarios and len(scenarios) >= max_scenarios:
                    break

                scenario = self._extract_scenario(repo, repo_name, row)
                if scenario:
                    scenarios.append(scenario)

        logger.info(f"Loaded {len(scenarios)} scenarios total")
        return scenarios

    def _find_merge_csvs(self) -> list[Path]:
        """Find merge CSV files in the dataset directory.

        Supports multiple dataset layouts:
        - merges/{owner}/{repo}.csv (raw merge discovery output)
        - merges_tested/{owner}/{repo}.csv (with test results)
        - result_adjusted.csv (single aggregated file)
        - *.csv at top level
        """
        # Prefer merges/ directory structure
        for subdir in ["merges_tested", "merges_analyzed", "merges"]:
            pattern_dir = self.dataset_path / subdir
            if pattern_dir.exists():
                csvs = sorted(pattern_dir.rglob("*.csv"))
                if csvs:
                    return csvs

        # Fallback: aggregated CSV or top-level CSVs
        agg = self.dataset_path / "result_adjusted.csv"
        if agg.exists():
            return [agg]

        return sorted(self.dataset_path.glob("*.csv"))

    def _repo_slug_from_path(self, csv_path: Path) -> str:
        """Extract repo slug (owner/name) from CSV path."""
        # For merges/{owner}/{repo}.csv -> owner/repo
        parts = csv_path.relative_to(self.dataset_path).parts
        if len(parts) >= 3:
            return f"{parts[-2]}/{csv_path.stem}"
        return csv_path.stem

    def _read_merge_csv(self, csv_path: Path) -> list[dict]:
        """Read a merge CSV and return rows as dicts."""
        rows = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip trivial merges
                if row.get("notes") == "a parent is the base":
                    continue
                rows.append(row)
        return rows

    def _clone_or_open(self, repo_slug: str) -> Optional[Repo]:
        """Clone repo from GitHub or open existing clone."""
        repo_path = self.repos_dir / repo_slug.replace("/", "_")
        url = f"https://github.com/{repo_slug}.git"

        if repo_path.exists():
            try:
                return Repo(repo_path)
            except Exception:
                logger.warning(f"Invalid repo at {repo_path}, re-cloning")

        try:
            logger.info(f"Cloning {url}")
            return Repo.clone_from(url, repo_path)
        except GitCommandError as e:
            logger.error(f"Failed to clone {url}: {e}")
            return None

    def _extract_scenario(
        self, repo: Repo, repo_name: str, row: dict,
    ) -> Optional[MergeScenario]:
        """Extract a single merge scenario from a CSV row.

        Finds Java files changed in both parents relative to merge base,
        picks the first one, and extracts base/ours/theirs/resolution.
        """
        # Map column names (dataset uses parent_1/parent_2 or left/right)
        merge_sha = row.get("merge_commit") or row.get("merge", "")
        parent1_sha = row.get("parent_1") or row.get("left", "")
        parent2_sha = row.get("parent_2") or row.get("right", "")

        if not all([merge_sha, parent1_sha, parent2_sha]):
            return None

        try:
            merge_commit = repo.commit(merge_sha)
            parent_ours = repo.commit(parent1_sha)
            parent_theirs = repo.commit(parent2_sha)
        except Exception as e:
            logger.debug(f"Could not resolve commits for {merge_sha}: {e}")
            return None

        # Compute merge base
        try:
            base_shas = repo.merge_base(parent_ours, parent_theirs)
            if not base_shas:
                return None
            merge_base = repo.commit(base_shas[0])
        except GitCommandError:
            return None

        # Find Java files changed in both parents
        try:
            diff_ours = {
                d.b_path for d in merge_base.diff(parent_ours)
                if d.b_path and d.b_path.endswith(".java")
            }
            diff_theirs = {
                d.b_path for d in merge_base.diff(parent_theirs)
                if d.b_path and d.b_path.endswith(".java")
            }
        except Exception:
            return None

        both_changed = diff_ours & diff_theirs
        if not both_changed:
            return None

        # Extract first file with valid contents
        for file_path in sorted(both_changed):
            try:
                base_content = self._file_at_commit(merge_base, file_path)
                ours_content = self._file_at_commit(parent_ours, file_path)
                theirs_content = self._file_at_commit(parent_theirs, file_path)
                dev_resolution = self._file_at_commit(merge_commit, file_path)
            except (KeyError, GitCommandError):
                continue

            if not all([base_content, ours_content, theirs_content, dev_resolution]):
                continue

            scenario_id = (
                f"{repo_name}__{merge_sha[:10]}__{file_path.replace('/', '_')}"
            )
            return MergeScenario(
                scenario_id=scenario_id,
                repo_name=repo_name,
                merge_commit=merge_sha,
                file_path=file_path,
                base_content=base_content,
                ours_content=ours_content,
                theirs_content=theirs_content,
                developer_resolution=dev_resolution,
            )

        return None

    @staticmethod
    def _file_at_commit(commit, file_path: str) -> Optional[str]:
        """Get file content at a specific commit."""
        try:
            blob = commit.tree / file_path
            return blob.data_stream.read().decode("utf-8", errors="replace")
        except (KeyError, TypeError):
            return None
