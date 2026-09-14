#!/usr/bin/env python3
"""
RM2 scenario tagger (Phase R1 of docs/plans/rm2-integration.md).

Walks `data/scenarios/*.json` and records, per scenario, the RefactoringMiner 2
type names detected file-level on each branch axis:

    "refactorings": {"ours": [<type>...], "theirs": [<type>...]}

Two RM2 runs per scenario — `(base, ours)` and `(base, theirs)`, file-level —
mirroring `semantic_merge_driver/core/refactoring_classifier.py`
`RefactoringClusterClassifier._detect_pair` exactly (basename-only staging in
two single-file dirs). Mirroring matters: the empirical cluster R2 pivots on
must equal the cluster the runtime dispatcher would assign for the same inputs.
The `resolution` axis is deliberately out of scope here (see the approved R1
plan).

Project-level mode (`--project-level`, ISSUES #26): tags the same two axes with
RM2 run on full project trees instead of single files — `git worktree` the
cloned repo at the merge-base and the side parent (`merge_commit^1`/`^2`),
mirroring `tools/rm2_fharness.py` `project_level()`. Results are filtered to
refactorings touching the scenario's `file_path` (the fharness same-file
`types_in` filter — the apples-to-apples comparison for the file-level R4a
question) and recorded under a *separate* key, never touching the R1
`refactorings` tags:

    "refactorings_project":      {"ours": [<type>...], "theirs": [<type>...]}
    "refactorings_project_full": {"ours": [<type>...], "theirs": [<type>...]}

`_full` is the unfiltered project-wide set, kept for inspection (R0 practice).
Needs the gitignored `data/repos/` clones. Caching/fail-closed semantics match
file-level mode, keyed on `refactorings_project`.

Caching mirrors `load-dataset` (cli.py): a scenario whose JSON already carries a
`refactorings` dict with both axes is skipped unless `--force`. A tagged-but-
empty axis (`[]`) is a real, cached result (RM2 ran, found nothing) — distinct
from an untagged scenario (no `refactorings` key).

Fail-closed (rm2-integration.md §1.3): any RM2 failure for an axis records `[]`
for that axis and logs to stderr — never aborts the run. Same posture as the
runtime classifier returning the empty set on failure.

Usage:
    python tools/rm2_tag.py [--force] [--scenarios-dir data/scenarios]
    python tools/rm2_tag.py --project-level [--repos-dir data/repos] [--force]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_SCENARIO_DIR = PROJECT_ROOT / "data" / "scenarios"
DEFAULT_REPOS_DIR = PROJECT_ROOT / "data" / "repos"
DOCKER_IMAGE = "merge-tools/refactoring-miner:2.4.0"
# Match the runtime classifier's timeout
# (semantic_merge_driver/core/refactoring_classifier.py RM2_TIMEOUT_SECONDS).
# The empirical cluster R2 pivots on must equal the cluster the runtime
# dispatcher would assign; a different timeout could diverge on a slow file.
# File-level single-file RM2 is ~2s warm, so 120s is ample (n=50: 0 errors).
RM2_TIMEOUT_SECONDS = 120
# Project-level runs RM2 on full trees (adangel_pmd's worktree is thousands of
# files) — R0 measured ~3× file-level cost, but the tail is long; be generous.
PROJECT_RM2_TIMEOUT_SECONDS = 900
GIT_WORKTREE_TIMEOUT_SECONDS = 240

AXES = ("ours", "theirs")
PROJECT_KEY = "refactorings_project"
PROJECT_FULL_KEY = "refactorings_project_full"


def run_rm2_raw(
    left: Path,
    right: Path,
    image: str = DOCKER_IMAGE,
    timeout: int = RM2_TIMEOUT_SECONDS,
) -> tuple[dict | None, str | None]:
    """Invoke the Dockerized RM2 wrapper; return the raw JSON payload.

    Returns (payload dict, error string or None). Fail-closed: any failure
    yields (None, error).
    """
    try:
        res = subprocess.run(
            [
                "docker", "run", "--rm", "--platform", "linux/amd64",
                "-v", f"{left.resolve()}:/data/left:ro",
                "-v", f"{right.resolve()}:/data/right:ro",
                image,
                "/data/left", "/data/right",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
        return None, f"subprocess error: {e}"

    if res.returncode != 0:
        return None, f"docker exit {res.returncode}: {(res.stderr or '').strip()[:300]}"

    try:
        return json.loads(res.stdout), None
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {e}; stdout head: {res.stdout[:200]!r}"


def run_rm2(left: Path, right: Path, image: str = DOCKER_IMAGE) -> tuple[set[str], str | None]:
    """Invoke the Dockerized RM2 wrapper on two host directories.

    Returns (detected type-name set, error string or None). Fail-closed: any
    failure yields (empty set, error) — the caller records `[]` for that axis.
    """
    payload, err = run_rm2_raw(left, right, image=image)
    if payload is None:
        return set(), err
    return types_in(payload), None


def types_in(payload: dict | None, file_path_filter: str | None = None) -> set[str]:
    """Return the set of refactoring `type` values in an RM2 payload.

    If file_path_filter is set, restrict to refactorings whose leftSide or
    rightSide locations reference that file path — mirrors rm2_fharness.py:
    R4a only sees the merging file at runtime, so the file-vs-project
    comparison is apples-to-apples only on the same file's refactorings.
    """
    if payload is None:
        return set()
    out: set[str] = set()
    for r in payload.get("refactorings", []):
        rtype = r.get("type")
        if rtype is None:
            continue
        if file_path_filter is None:
            out.add(rtype)
            continue
        locs = (r.get("leftSideLocations") or []) + (r.get("rightSideLocations") or [])
        if any(loc.get("filePath") == file_path_filter for loc in locs):
            out.add(rtype)
    return out


def detect_axis(
    file_path: str,
    base_content: str,
    side_content: str,
    runner=run_rm2,
) -> tuple[list[str], str | None]:
    """RM2 types for one (base, side) pair, file-level, basename-only staging.

    Basename-only staging in `left/`+`right/` single-file dirs mirrors R4a's
    `_detect_pair` so the empirical detection equals the runtime one.
    """
    basename = Path(file_path).name
    with tempfile.TemporaryDirectory() as tmp:
        left_dir = Path(tmp) / "left"
        right_dir = Path(tmp) / "right"
        left_dir.mkdir()
        right_dir.mkdir()
        try:
            (left_dir / basename).write_text(base_content, encoding="utf-8")
            (right_dir / basename).write_text(side_content, encoding="utf-8")
        except OSError as e:
            return [], f"staging failed: {e}"
        types, err = runner(left_dir, right_dir)
        return sorted(types), err


def tag_scenario(scenario: dict, runner=run_rm2) -> tuple[dict, dict[str, str]]:
    """Return (scenario with `refactorings` populated, {axis: error}).

    `runner` is injectable for Docker-free tests.
    """
    errors: dict[str, str] = {}
    refs: dict[str, list[str]] = {}
    file_path = scenario["file_path"]
    base = scenario["base_content"]
    side_by_axis = {"ours": scenario["ours_content"], "theirs": scenario["theirs_content"]}
    for axis in AXES:
        types, err = detect_axis(file_path, base, side_by_axis[axis], runner=runner)
        refs[axis] = types
        if err is not None:
            errors[axis] = err
    scenario["refactorings"] = refs
    return scenario, errors


def _git(repo: Path, *args: str, timeout: int = 60) -> tuple[str | None, str | None]:
    """Run git in `repo`; return (stdout, None) or (None, error)."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return None, f"git {' '.join(args[:2])}: {e}"
    if r.returncode != 0:
        return None, f"git {' '.join(args[:2])} exit {r.returncode}: {r.stderr.strip()[:300]}"
    return r.stdout.strip(), None


def resolve_merge_shas(repo: Path, merge_sha: str) -> tuple[dict | None, str | None]:
    """Resolve base/ours/theirs SHAs for a merge commit (fharness logic)."""
    ours, err = _git(repo, "rev-parse", f"{merge_sha}^1")
    if err:
        return None, err
    theirs, err = _git(repo, "rev-parse", f"{merge_sha}^2")
    if err:
        return None, err
    base, err = _git(repo, "merge-base", ours, theirs)
    if err:
        return None, err
    return {"base": base, "ours": ours, "theirs": theirs}, None


def _worktree_add(repo: Path, dest: Path, sha: str) -> str | None:
    out, err = _git(
        repo, "worktree", "add", "--detach", "-f", str(dest), sha,
        timeout=GIT_WORKTREE_TIMEOUT_SECONDS,
    )
    return err


def _worktree_remove(repo: Path, dest: Path) -> None:
    _git(repo, "worktree", "remove", "--force", str(dest),
         timeout=GIT_WORKTREE_TIMEOUT_SECONDS)


def tag_scenario_project(
    scenario: dict,
    repos_dir: Path = DEFAULT_REPOS_DIR,
    raw_runner=run_rm2_raw,
) -> tuple[dict, dict[str, str]]:
    """Populate PROJECT_KEY (+PROJECT_FULL_KEY) via project-level RM2.

    One shared base worktree + one worktree per side parent; RM2 runs on the
    full trees, then results are filtered to the scenario's `file_path`
    (see module docstring). Fail-closed per axis, like `tag_scenario`.
    `raw_runner` is injectable for Docker-free tests.
    """
    errors: dict[str, str] = {}
    filtered: dict[str, list[str]] = {axis: [] for axis in AXES}
    full: dict[str, list[str]] = {axis: [] for axis in AXES}
    file_path = scenario["file_path"]
    repo = repos_dir / scenario["repo_name"]

    def fail_all(msg: str) -> tuple[dict, dict[str, str]]:
        for axis in AXES:
            errors[axis] = msg
        scenario[PROJECT_KEY] = filtered
        scenario[PROJECT_FULL_KEY] = full
        return scenario, errors

    if not repo.exists():
        return fail_all(f"repo not found: {repo}")

    shas, err = resolve_merge_shas(repo, scenario["merge_commit"])
    if err:
        return fail_all(err)

    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp) / "base"
        err = _worktree_add(repo, base_dir, shas["base"])
        if err:
            return fail_all(err)
        try:
            for axis in AXES:
                side_dir = Path(tmp) / axis
                err = _worktree_add(repo, side_dir, shas[axis])
                if err:
                    errors[axis] = err
                    continue
                try:
                    payload, err = raw_runner(
                        base_dir, side_dir, timeout=PROJECT_RM2_TIMEOUT_SECONDS
                    )
                    if err:
                        errors[axis] = err
                        continue
                    filtered[axis] = sorted(types_in(payload, file_path_filter=file_path))
                    full[axis] = sorted(types_in(payload))
                finally:
                    _worktree_remove(repo, side_dir)
        finally:
            _worktree_remove(repo, base_dir)

    scenario[PROJECT_KEY] = filtered
    scenario[PROJECT_FULL_KEY] = full
    return scenario, errors


def _is_tagged(scenario: dict) -> bool:
    """True iff both axes are already recorded (empty lists count as tagged)."""
    refs = scenario.get("refactorings")
    return isinstance(refs, dict) and all(axis in refs for axis in AXES)


def _is_project_tagged(scenario: dict) -> bool:
    """True iff both project-level axes are already recorded."""
    refs = scenario.get(PROJECT_KEY)
    return isinstance(refs, dict) and all(axis in refs for axis in AXES)


def process_scenarios(
    scenario_dir: Path,
    force: bool = False,
    runner=run_rm2,
) -> dict:
    """Tag every scenario JSON in `scenario_dir`. Returns a summary dict."""
    paths = sorted(scenario_dir.glob("*.json"))
    summary = {
        "total": len(paths),
        "tagged": 0,
        "skipped_cached": 0,
        "nonempty_ours": 0,
        "nonempty_theirs": 0,
        "both_empty": 0,
        "axis_diverged": 0,  # ours type-set != theirs type-set
        "errored_scenarios": 0,
        "errors": {},
    }

    for path in paths:
        scenario = json.loads(path.read_text())
        sid = scenario.get("scenario_id", path.stem)

        if _is_tagged(scenario) and not force:
            summary["skipped_cached"] += 1
            refs = scenario["refactorings"]
        else:
            print(f"# tagging {sid[:80]}", file=sys.stderr, flush=True)
            scenario, errors = tag_scenario(scenario, runner=runner)
            path.write_text(json.dumps(scenario, indent=2))
            summary["tagged"] += 1
            if errors:
                summary["errored_scenarios"] += 1
                summary["errors"][sid] = errors
            refs = scenario["refactorings"]

        ours, theirs = refs.get("ours", []), refs.get("theirs", [])
        if ours:
            summary["nonempty_ours"] += 1
        if theirs:
            summary["nonempty_theirs"] += 1
        if not ours and not theirs:
            summary["both_empty"] += 1
        if set(ours) != set(theirs):
            summary["axis_diverged"] += 1

    return summary


def process_scenarios_project(
    scenario_dir: Path,
    repos_dir: Path = DEFAULT_REPOS_DIR,
    force: bool = False,
    raw_runner=run_rm2_raw,
) -> dict:
    """Project-level tagging pass over `scenario_dir`. Returns a summary dict.

    Separate from `process_scenarios` on purpose: the R1 file-level path is
    frozen (its tags are the load-bearing cluster pivot) and stays byte-
    identical. Counters here describe the same-file-filtered project tags.
    """
    paths = sorted(scenario_dir.glob("*.json"))
    summary = {
        "mode": "project-level",
        "total": len(paths),
        "tagged": 0,
        "skipped_cached": 0,
        "nonempty_ours": 0,
        "nonempty_theirs": 0,
        "both_empty": 0,
        "axis_diverged": 0,
        "errored_scenarios": 0,
        "errors": {},
    }

    for path in paths:
        scenario = json.loads(path.read_text())
        sid = scenario.get("scenario_id", path.stem)

        if _is_project_tagged(scenario) and not force:
            summary["skipped_cached"] += 1
            refs = scenario[PROJECT_KEY]
        else:
            print(f"# project-tagging {sid[:80]}", file=sys.stderr, flush=True)
            scenario, errors = tag_scenario_project(
                scenario, repos_dir=repos_dir, raw_runner=raw_runner
            )
            path.write_text(json.dumps(scenario, indent=2))
            summary["tagged"] += 1
            if errors:
                summary["errored_scenarios"] += 1
                summary["errors"][sid] = errors
            refs = scenario[PROJECT_KEY]

        ours, theirs = refs.get("ours", []), refs.get("theirs", [])
        if ours:
            summary["nonempty_ours"] += 1
        if theirs:
            summary["nonempty_theirs"] += 1
        if not ours and not theirs:
            summary["both_empty"] += 1
        if set(ours) != set(theirs):
            summary["axis_diverged"] += 1

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="RM2 scenario tagger (Phase R1).")
    parser.add_argument(
        "--scenarios-dir",
        default=str(DEFAULT_SCENARIO_DIR),
        help="Directory of scenario JSON files (default: data/scenarios).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-extract even for scenarios already carrying a refactorings tag.",
    )
    parser.add_argument(
        "--project-level",
        action="store_true",
        help="Tag refactorings_project via git-worktree full trees (ISSUES #26); "
             "needs data/repos clones. File-level tags are left untouched.",
    )
    parser.add_argument(
        "--repos-dir",
        default=str(DEFAULT_REPOS_DIR),
        help="Directory of cloned repos for --project-level (default: data/repos).",
    )
    args = parser.parse_args()

    if args.project_level:
        summary = process_scenarios_project(
            Path(args.scenarios_dir), repos_dir=Path(args.repos_dir), force=args.force
        )
    else:
        summary = process_scenarios(Path(args.scenarios_dir), force=args.force)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
