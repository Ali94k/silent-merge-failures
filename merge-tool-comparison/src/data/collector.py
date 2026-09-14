import json
import logging
from pathlib import Path

import yaml
from git import Repo, GitCommandError

from src.core.interfaces import MergeScenario

logger = logging.getLogger(__name__)


def collect_scenarios(
    repos_config_path: str,
    output_dir: str = "data/scenarios",
    repos_dir: str = "data/repos",
    max_scenarios: int | None = None,
) -> list[MergeScenario]:
    """
    Extract merge scenarios from real-world Java repos.

    For each merge commit:
    1. Identify the two parents and compute the merge base.
    2. For each .java file changed in both parents relative to base,
       extract base/ours/theirs/developer_resolution.
    3. Save each scenario as a JSON file.
    """
    config = yaml.safe_load(Path(repos_config_path).read_text())
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    repos_path = Path(repos_dir)
    repos_path.mkdir(parents=True, exist_ok=True)

    all_scenarios: list[MergeScenario] = []

    for repo_config in config["repos"]:
        repo_name = repo_config["name"]
        url = repo_config["url"]
        repo_max = repo_config.get("max_scenarios", 50)
        if max_scenarios is not None:
            repo_max = min(repo_max, max_scenarios)

        logger.info(f"Processing repo: {repo_name}")
        repo_path = repos_path / repo_name

        # Clone or open
        if repo_path.exists():
            repo = Repo(repo_path)
            logger.info(f"Using existing clone at {repo_path}")
        else:
            logger.info(f"Cloning {url} to {repo_path}")
            repo = Repo.clone_from(url, repo_path)

        # Find merge commits
        merge_commits = repo_config.get("merge_commits")
        if merge_commits:
            commits = [repo.commit(sha) for sha in merge_commits]
        else:
            commits = _find_merge_commits(repo, limit=max(repo_max * 100, 500))

        scenario_count = 0
        for commit in commits:
            if scenario_count >= repo_max:
                break

            if len(commit.parents) < 2:
                continue

            parent_ours = commit.parents[0]
            parent_theirs = commit.parents[1]

            try:
                merge_base_shas = repo.merge_base(parent_ours, parent_theirs)
                if not merge_base_shas:
                    continue
                merge_base = repo.commit(merge_base_shas[0])
            except GitCommandError:
                logger.warning(f"Could not find merge base for {commit.hexsha}")
                continue

            # Find Java files changed in both parents relative to base
            try:
                diff_ours = {
                    d.b_path for d in merge_base.diff(parent_ours)
                    if d.b_path and d.b_path.endswith(".java")
                }
                diff_theirs = {
                    d.b_path for d in merge_base.diff(parent_theirs)
                    if d.b_path and d.b_path.endswith(".java")
                }
            except Exception as e:
                logger.warning(f"Error diffing {commit.hexsha}: {e}")
                continue

            both_changed = diff_ours & diff_theirs

            for file_path in both_changed:
                if scenario_count >= repo_max:
                    break

                try:
                    base_content = _get_file_content(merge_base, file_path)
                    ours_content = _get_file_content(parent_ours, file_path)
                    theirs_content = _get_file_content(parent_theirs, file_path)
                    dev_resolution = _get_file_content(commit, file_path)
                except (KeyError, GitCommandError):
                    continue

                if not all([base_content, ours_content, theirs_content, dev_resolution]):
                    continue

                scenario_id = f"{repo_name}__{commit.hexsha[:10]}__{file_path.replace('/', '_')}"
                scenario = MergeScenario(
                    scenario_id=scenario_id,
                    repo_name=repo_name,
                    merge_commit=commit.hexsha,
                    file_path=file_path,
                    base_content=base_content,
                    ours_content=ours_content,
                    theirs_content=theirs_content,
                    developer_resolution=dev_resolution,
                )

                # Save to disk
                scenario_file = output_path / f"{scenario_id}.json"
                scenario_file.write_text(json.dumps(scenario.to_dict(), indent=2))
                all_scenarios.append(scenario)
                scenario_count += 1
                logger.info(f"  Collected scenario {scenario_count}/{repo_max}: {scenario_id}")

        logger.info(f"Collected {scenario_count} scenarios from {repo_name}")

    return all_scenarios


def load_scenarios(scenarios_dir: str = "data/scenarios") -> list[MergeScenario]:
    """Load previously collected scenarios from disk."""
    path = Path(scenarios_dir)
    scenarios = []
    for f in sorted(path.glob("*.json")):
        data = json.loads(f.read_text())
        scenarios.append(MergeScenario.from_dict(data))
    return scenarios


def _find_merge_commits(repo: Repo, limit: int = 250) -> list:
    """Find merge commits in the repo (most recent first)."""
    merges = []
    for commit in repo.iter_commits(max_count=limit):
        if len(commit.parents) >= 2:
            merges.append(commit)
    return merges


def _get_file_content(commit, file_path: str) -> str | None:
    """Get file content at a specific commit."""
    try:
        blob = commit.tree / file_path
        return blob.data_stream.read().decode("utf-8", errors="replace")
    except (KeyError, TypeError):
        return None
