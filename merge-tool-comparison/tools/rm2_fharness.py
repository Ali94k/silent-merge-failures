#!/usr/bin/env python3
"""
RM2 F-harness: file-level vs project-level recall delta.

Phase R0 reconnaissance instrument. Picks N scenarios from `data/scenarios/`,
runs the Dockerized RM2 wrapper two ways per scenario, diffs the refactoring
sets, and reports an aggregate recall ratio.

  file-level    — write `base_content` and `ours_content` to single-file dirs
                  preserving the scenario's `file_path`; run RM2.
  project-level — git-worktree the cloned repo at the merge-base SHA and the
                  ours-side parent SHA; run RM2 on the two full project trees.

The recall ratio answers the load-bearing R0 question: how much does
file-only context lose, relative to full-project context, on this dataset?
That ratio decides Path B/C/D for R1 and bounds R4a's runtime accuracy.

Usage:
    python tools/rm2_fharness.py [N]   # default N=5
"""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SCENARIO_DIR = PROJECT_ROOT / "data" / "scenarios"
REPOS_DIR = PROJECT_ROOT / "data" / "repos"
DOCKER_IMAGE = "merge-tools/refactoring-miner:2.4.0"


def run_rm2(left: Path, right: Path) -> tuple[dict | None, str | None]:
    """Invoke the Dockerized RM2 wrapper on two host directories."""
    res = subprocess.run(
        [
            "docker", "run", "--rm", "--platform", "linux/amd64",
            "-v", f"{left.resolve()}:/data/left:ro",
            "-v", f"{right.resolve()}:/data/right:ro",
            DOCKER_IMAGE,
            "/data/left", "/data/right",
        ],
        capture_output=True, text=True, timeout=300,
    )
    if res.returncode != 0:
        return None, f"docker exit {res.returncode}: {res.stderr[:300]}"
    try:
        return json.loads(res.stdout), None
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {e}; stdout head: {res.stdout[:300]}"


def file_level(scenario: dict) -> tuple[dict | None, str | None]:
    """Single-file dirs at the scenario's file_path, base vs ours contents."""
    file_path = scenario["file_path"]
    with tempfile.TemporaryDirectory() as tmp:
        left = Path(tmp) / "left"
        right = Path(tmp) / "right"
        for d in (left, right):
            (d / Path(file_path).parent).mkdir(parents=True, exist_ok=True)
        (left / file_path).write_text(scenario["base_content"])
        (right / file_path).write_text(scenario["ours_content"])
        return run_rm2(left, right)


def project_level(scenario: dict) -> tuple[dict | None, str | None]:
    """Full project trees via git worktree at the merge-base and ours SHAs."""
    repo = REPOS_DIR / scenario["repo_name"]
    if not repo.exists():
        return None, f"repo not found: {repo}"

    merge_sha = scenario["merge_commit"]

    def git(*args: str) -> str:
        r = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=60,
        )
        return r.stdout.strip()

    ours = git("rev-parse", f"{merge_sha}^1")
    theirs = git("rev-parse", f"{merge_sha}^2")
    if not (ours and theirs):
        return None, f"could not resolve parents of {merge_sha}"
    base = git("merge-base", ours, theirs)
    if not base:
        return None, f"could not resolve merge-base of {ours} {theirs}"

    with tempfile.TemporaryDirectory() as tmp:
        left = Path(tmp) / "left"
        right = Path(tmp) / "right"
        try:
            subprocess.run(
                ["git", "-C", str(repo), "worktree", "add", "--detach", "-f",
                 str(left), base],
                check=True, capture_output=True, timeout=120,
            )
            subprocess.run(
                ["git", "-C", str(repo), "worktree", "add", "--detach", "-f",
                 str(right), ours],
                check=True, capture_output=True, timeout=120,
            )
            return run_rm2(left, right)
        except subprocess.CalledProcessError as e:
            return None, f"git worktree failed: {e.stderr.decode()[:300]}"
        finally:
            subprocess.run(
                ["git", "-C", str(repo), "worktree", "remove", "--force", str(left)],
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "worktree", "remove", "--force", str(right)],
                capture_output=True,
            )


def types_in(json_result: dict | None, file_path_filter: str | None = None) -> set[str]:
    """Return the set of refactoring `type` values.

    If file_path_filter is set, restrict to refactorings whose leftSide or
    rightSide locations reference that file path. R4a only sees the merging
    file at runtime, so for the file-vs-project comparison to be apples-to-
    apples we filter project-level results down to the same file's
    refactorings (mirroring what R4a *could* observe).
    """
    if json_result is None:
        return set()
    out: set[str] = set()
    for r in json_result.get("refactorings", []):
        rtype = r.get("type")
        if file_path_filter is None:
            out.add(rtype)
            continue
        locs = (r.get("leftSideLocations") or []) + (r.get("rightSideLocations") or [])
        if any(loc.get("filePath") == file_path_filter for loc in locs):
            out.add(rtype)
    return out


def main(n: int = 5) -> None:
    scenarios = sorted(SCENARIO_DIR.glob("*.json"))[:n]
    rows: list[dict] = []
    file_total = proj_total = common_total = 0

    for path in scenarios:
        scenario = json.loads(path.read_text())
        sid = scenario["scenario_id"]
        print(f"# {sid[:80]}", file=sys.stderr, flush=True)

        f_result, f_err = file_level(scenario)
        p_result, p_err = project_level(scenario)

        # Project-level filtered to the same file the merge driver would see.
        # This is the apples-to-apples comparison for R4a's runtime question.
        file_path = scenario["file_path"]
        f_types = types_in(f_result)
        p_types_full = types_in(p_result)
        p_types_same_file = types_in(p_result, file_path_filter=file_path)
        common = f_types & p_types_same_file
        only_proj = p_types_same_file - f_types
        only_file = f_types - p_types_same_file

        file_total += len(f_types)
        proj_total += len(p_types_same_file)
        common_total += len(common)

        rows.append({
            "id": sid,
            "file": {"types": sorted(f_types), "err": f_err},
            "proj_same_file": {"types": sorted(p_types_same_file), "err": p_err},
            "proj_full": {"types": sorted(p_types_full)},
            "common": sorted(common),
            "only_proj": sorted(only_proj),
            "only_file": sorted(only_file),
        })

    summary = {
        "n_scenarios": len(scenarios),
        "totals": {
            "file_level_refactoring_types": file_total,
            "project_level_same_file_types": proj_total,
            "common_types": common_total,
        },
        "file_recall_of_proj_same_file_pct": (
            round(100 * common_total / proj_total, 1) if proj_total else None
        ),
        "note": (
            "Recall denominator is project-level results filtered to the "
            "scenario's file_path — matches what R4a could detect at merge time. "
            "Each row's `proj_full` field is the unfiltered project-level set, "
            "kept for inspection."
        ),
        "per_scenario": rows,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
