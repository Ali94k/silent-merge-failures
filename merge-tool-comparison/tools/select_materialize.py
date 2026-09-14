"""Select tool-discriminating merges from the Schesch result table and
materialize them into self-contained scenario JSONs.

Strategy (CLAUDE.md data-expansion plan, decided 2026-05-20):
  1. SELECT rows from results/<corpus>/result_adjusted.csv by CRITERION:
       specialist (default) — gitmerge_ort fails, spork or mergiraf passes
       disagree             — any git/spork/mergiraf disagreement
       spork                — Spork wins (passed where git didn't) OR Spork
                              wrong-merges (Tests_failed)
       semantic             — mergiraf == Tests_failed (clean-but-incorrect
                              positives for the detection-validation pilot)
       semantic_ctl         — mergiraf == Tests_passed (clean-and-correct
                              controls for the same pilot)
     (Schesch has no weave column, so selection uses git/spork/mergiraf only.)

     INTERSECT_MAX (optional) additionally filters on num_intersecting_files
     (keeps rows with a parseable value <= the knob; pilot uses 3).
     INTERSECT_MIN (optional) is the symmetric lower bound (keeps rows with a
     parseable value >= the knob). It is the taxonomy stratum-B complement
     filter (ISSUES #30): CRITERION=semantic INTERSECT_MIN=4 selects the
     `> 3 intersecting files` merges that the <=3 Stage-C pool (INTERSECT_MAX=3)
     left behind. Unparseable counts fail either bound (as with INTERSECT_MAX);
     the frozen census has 0 unparseable `semantic` rows, so `>3` captures all
     of stratum B. Both knobs may be combined for a closed [min, max] band.

     The semantic/semantic_ctl criteria materialize EVERY intersecting Java
     file of a merge (one JSON per file, TARGET counts merges) and record a
     `merge_id` key on each scenario JSON so per-merge aggregation is possible
     downstream (detect_validate.py). Other criteria keep the legacy
     one-file-per-merge behaviour; ALL_FILES=0/1 overrides either default.
  2. DIVERSITY-cap per repo (avoids the alphabetical/2-repo concentration of the
     original 50) and shuffle (seeded, reproducible). The capped pool is far
     larger than the target, so clone failures/timeouts are absorbed — only
     SUCCESSES count toward the target, so we always net `target` scenarios
     unless the failure rate is extreme.
  3. CLONE each repo on demand — BLOBLESS + NO-CHECKOUT (`--filter=blob:none
     --no-checkout`) with a hard per-clone TIMEOUT. We read only 4 files from 4
     commits, so fetching every blob and checking out the whole tree (the real
     cost on big repos) is wasted; needed blobs are fetched on demand. The
     timeout skips giant/renamed/hanging repos so the job can't get stuck.
     MATERIALIZE, SKIPPING any merge with !=1 git merge-base (criss-cross /
     unrelated histories — GitPython's single base would differ from git's
     recursive virtual base).
  4. WRITE scenario JSONs to OUTPUT (default data/scenarios_expanded/), SEPARATE
     from the canonical 50. Resumable: existing JSONs count toward the target.

Then tag with tools/rm2_tag.py and run the comparator over the new dir.

Usage (env-configurable):
    TARGET=60 CAP=3 SEED=42 CRITERION=spork CLONE_TIMEOUT=120 \
      OUTPUT=data/scenarios_spork ./.venv/bin/python tools/select_materialize.py
"""
from __future__ import annotations

import csv
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.interfaces import MergeScenario  # noqa: E402
from src.data.schesch_loader import ScheschDatasetLoader  # noqa: E402
from git import Repo  # noqa: E402

CSV_PATH = PROJECT_ROOT / "data/schesch-dataset/results/reaper/result_adjusted.csv"
DATASET_PATH = PROJECT_ROOT / "data/schesch-dataset/results/reaper"
REPOS_DIR = PROJECT_ROOT / "data/repos"
PASS = "Tests_passed"
DRIVER_TOOLS = ("gitmerge_ort", "spork", "mergiraf")
CLONE_TIMEOUT = int(os.environ.get("CLONE_TIMEOUT", "120"))


def _has_java(row: dict) -> bool:
    return str(row.get("diff contains java file", "")).strip().lower() in ("true", "1", "yes")


def _disagree(row: dict) -> bool:
    return len({row.get(t, "") for t in DRIVER_TOOLS}) > 1


def _specialist_wins(row: dict) -> bool:
    return row.get("gitmerge_ort", "") in ("Merge_failed", "Tests_failed") and (
        row.get("spork", "") == PASS or row.get("mergiraf", "") == PASS
    )


def _spork_focus(row: dict) -> bool:
    """Spork wins (passed where git did not) OR Spork wrong-merges (Tests_failed).

    Yields candidates for both Spork goals from one disjoint pool:
      - spork == Tests_passed and git != Tests_passed  -> "where Spork wins"
      - spork == Tests_failed                          -> "diagnose Spork FPs"
    """
    sp = row.get("spork", "")
    return (sp == PASS and row.get("gitmerge_ort", "") != PASS) or (sp == "Tests_failed")


def _semantic(row: dict) -> bool:
    """Detection-pilot positives: Mergiraf merged cleanly but tests fail."""
    return row.get("mergiraf", "") == "Tests_failed"


def _semantic_ctl(row: dict) -> bool:
    """Detection-pilot controls: Mergiraf merged cleanly and tests pass."""
    return row.get("mergiraf", "") == PASS


def _intersect_ok(
    row: dict, intersect_max: int | None, intersect_min: int | None = None
) -> bool:
    """intersect_min <= num_intersecting_files <= intersect_max.

    Either bound is a no-op when unset. Unparseable/missing values fail the
    filter whenever *either* bound is active: the knobs exist to bound the
    candidate-culprit set, so unknown counts are excluded.
    """
    if intersect_max is None and intersect_min is None:
        return True
    try:
        n = int(float(row.get("num_intersecting_files", "")))
    except (TypeError, ValueError):
        return False
    if intersect_max is not None and n > intersect_max:
        return False
    if intersect_min is not None and n < intersect_min:
        return False
    return True


def _clone_blobless(repo_slug: str, repos_dir: Path, timeout: int):
    """Blobless, no-checkout clone with a hard timeout.

    `--filter=blob:none --no-checkout`: fetch the full commit/tree history but no
    file blobs and no working tree. We read only 4 files from 4 commits, so the
    needed blobs are fetched on demand during extraction; the giant working-tree
    checkout (the real cost on big repos) is skipped entirely.

    Returns (Repo|None, reason) with reason in {reused, cloned, timeout, fail}.
    A timed-out / failed clone leaves no partial directory behind.
    """
    repo_path = repos_dir / repo_slug.replace("/", "_")
    if repo_path.exists():
        try:
            return Repo(repo_path), "reused"
        except Exception:
            shutil.rmtree(repo_path, ignore_errors=True)
    url = f"https://github.com/{repo_slug}.git"
    try:
        subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", "--quiet",
             url, str(repo_path)],
            check=True, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        shutil.rmtree(repo_path, ignore_errors=True)
        return None, "timeout"
    except (subprocess.CalledProcessError, OSError):
        shutil.rmtree(repo_path, ignore_errors=True)
        return None, "fail"
    try:
        return Repo(repo_path), "cloned"
    except Exception:
        shutil.rmtree(repo_path, ignore_errors=True)
        return None, "fail"


def _ensure_commits(repo_path: Path, shas: list[str], timeout: int) -> None:
    """Fetch any of ``shas`` not already present, by SHA, from the promisor remote.

    Merge parents that live on deleted/rebased branches are unreachable from the
    blobless clone's refs, so ``merge-base`` fails ("unresolved"). GitHub serves
    such commits by explicit SHA (``git fetch origin <sha>``), so a targeted
    blobless fetch recovers them. No-op for commits already present.
    """
    for sha in shas:
        if not sha:
            continue
        present = subprocess.run(
            ["git", "-C", str(repo_path), "cat-file", "-e", sha],
            capture_output=True,
        ).returncode == 0
        if present:
            continue
        try:
            subprocess.run(
                ["git", "-C", str(repo_path), "fetch", "--filter=blob:none",
                 "--quiet", "origin", sha],
                check=False, capture_output=True, text=True, timeout=timeout,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass  # leave missing -> merge-base fails -> counted as unresolved


def _extract_all_file_scenarios(repo: Repo, repo_name: str, row: dict) -> list[MergeScenario]:
    """Every intersecting Java file of one merge as its own MergeScenario.

    Mirrors ScheschDatasetLoader._extract_scenario (same commit resolution,
    same diff-intersection, same content checks) but keeps ALL valid files
    instead of the first — the detection pilot scores per merge, any-file-flag,
    so dropping siblings would silently shrink the candidate-culprit set.
    """
    merge_sha = row.get("merge_commit") or row.get("merge", "")
    parent1_sha = row.get("parent_1") or row.get("left", "")
    parent2_sha = row.get("parent_2") or row.get("right", "")
    if not all([merge_sha, parent1_sha, parent2_sha]):
        return []

    try:
        merge_commit = repo.commit(merge_sha)
        parent_ours = repo.commit(parent1_sha)
        parent_theirs = repo.commit(parent2_sha)
        base_shas = repo.merge_base(parent_ours, parent_theirs)
        if not base_shas:
            return []
        merge_base = repo.commit(base_shas[0])
        diff_ours = {
            d.b_path for d in merge_base.diff(parent_ours)
            if d.b_path and d.b_path.endswith(".java")
        }
        diff_theirs = {
            d.b_path for d in merge_base.diff(parent_theirs)
            if d.b_path and d.b_path.endswith(".java")
        }
    except Exception:
        return []

    scenarios = []
    for file_path in sorted(diff_ours & diff_theirs):
        try:
            contents = [
                ScheschDatasetLoader._file_at_commit(c, file_path)
                for c in (merge_base, parent_ours, parent_theirs, merge_commit)
            ]
        except Exception:
            # Blobless clones fetch blobs on demand from the promisor remote;
            # a transient network failure raises here (GitPython mislabels the
            # empty object header "possible dubious ownership"). Abandon the
            # whole merge so it is retried cleanly on the next resume run —
            # partial units would misrepresent the intersecting-file set — and
            # so one bad blob can't crash the entire materialization pass.
            return []
        if not all(contents):
            continue
        scenarios.append(MergeScenario(
            scenario_id=f"{repo_name}__{merge_sha[:10]}__{file_path.replace('/', '_')}",
            repo_name=repo_name,
            merge_commit=merge_sha,
            file_path=file_path,
            base_content=contents[0],
            ours_content=contents[1],
            theirs_content=contents[2],
            developer_resolution=contents[3],
        ))
    return scenarios


def _existing_merge_ids(out_dir: Path) -> set[str]:
    """merge_ids already materialized (resume support for all-files mode)."""
    ids = set()
    for f in out_dir.glob("*.json"):
        try:
            d = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        mid = d.get("merge_id")
        if not mid:  # legacy JSON: derive from scenario_id prefix
            mid = "__".join(d.get("scenario_id", f.stem).split("__")[:2])
        ids.add(mid)
    return ids


def main() -> None:
    target = int(os.environ.get("TARGET", "60"))
    cap = int(os.environ.get("CAP", "3"))
    seed = int(os.environ.get("SEED", "42"))
    criterion = os.environ.get("CRITERION", "specialist")
    intersect_max = (
        int(os.environ["INTERSECT_MAX"]) if os.environ.get("INTERSECT_MAX") else None
    )
    intersect_min = (
        int(os.environ["INTERSECT_MIN"]) if os.environ.get("INTERSECT_MIN") else None
    )
    # all-files mode: default for the detection-pilot criteria, env-overridable.
    if os.environ.get("ALL_FILES") is not None:
        all_files = os.environ["ALL_FILES"] == "1"
    else:
        all_files = criterion in ("semantic", "semantic_ctl")
    out_dir = Path(os.environ.get("OUTPUT", str(PROJECT_ROOT / "data/scenarios_expanded")))
    out_dir.mkdir(parents=True, exist_ok=True)

    keep = {
        "specialist": _specialist_wins,
        "disagree": _disagree,
        "spork": _spork_focus,
        "semantic": _semantic,
        "semantic_ctl": _semantic_ctl,
    }.get(criterion, _specialist_wins)
    rows = list(csv.DictReader(open(CSV_PATH)))
    pool = [
        r for r in rows
        if _has_java(r) and keep(r) and _intersect_ok(r, intersect_max, intersect_min)
    ]
    random.seed(seed)
    random.shuffle(pool)

    # Diversity cap per repo.
    per_repo: dict[str, int] = {}
    candidates = []
    for r in pool:
        repo = r["repository"]
        if per_repo.get(repo, 0) < cap:
            per_repo[repo] = per_repo.get(repo, 0) + 1
            candidates.append(r)

    loader = ScheschDatasetLoader(dataset_path=str(DATASET_PATH), repos_dir=str(REPOS_DIR))

    # resume: all-files mode counts distinct MERGES, legacy mode counts JSONs.
    done_merge_ids = _existing_merge_ids(out_dir) if all_files else set()
    made = len(done_merge_ids) if all_files else len(list(out_dir.glob("*.json")))
    tried = skip_multibase = skip_unresolved = clone_fail = clone_timeout = extract_fail = 0
    buffer_x = len(candidates) / max(target, 1)
    print(
        f"criterion={criterion} target={target} cap={cap} seed={seed} "
        f"intersect_max={intersect_max} intersect_min={intersect_min} all_files={all_files} "
        f"pool={len(pool)} candidates={len(candidates)} (buffer {buffer_x:.1f}x target) "
        f"already_have={made} clone=blobless/no-checkout timeout={CLONE_TIMEOUT}s",
        flush=True,
    )

    for r in candidates:
        if made >= target:
            break
        repo_slug = r["repository"]
        repo_name = repo_slug.replace("/", "_")
        left, right = r.get("left"), r.get("right")
        tried += 1

        if not (REPOS_DIR / repo_name).exists():
            print(f"  cloning {repo_slug} ...", flush=True)
        repo, reason = _clone_blobless(repo_slug, REPOS_DIR, CLONE_TIMEOUT)
        if repo is None:
            if reason == "timeout":
                clone_timeout += 1
                print(f"    timeout (> {CLONE_TIMEOUT}s) — skipped {repo_slug}", flush=True)
            else:
                clone_fail += 1
            continue

        # Recover merges whose parents are unreachable from the clone's refs
        # (deleted/rebased branches) by fetching the exact commits by SHA.
        merge_sha_pre = r.get("merge_commit") or r.get("merge", "")
        _ensure_commits(REPOS_DIR / repo_name, [left, right, merge_sha_pre], CLONE_TIMEOUT)

        # Multi-base SKIP: keep only merges with exactly one merge-base.
        try:
            bases = repo.git.merge_base("--all", left, right).split()
        except Exception:
            skip_unresolved += 1
            continue
        if len(bases) != 1:
            skip_multibase += 1
            continue

        if all_files:
            merge_sha = r.get("merge_commit") or r.get("merge", "")
            merge_id = f"{repo_name}__{merge_sha[:10]}"
            if merge_id in done_merge_ids:
                continue  # merge already materialized in a prior run
            scenarios = _extract_all_file_scenarios(repo, repo_name, r)
            if not scenarios:
                extract_fail += 1
                continue
            for scenario in scenarios:
                dest = out_dir / f"{scenario.scenario_id}.json"
                if dest.exists():
                    continue
                d = scenario.to_dict()
                d["merge_id"] = merge_id
                dest.write_text(json.dumps(d, indent=2))
            done_merge_ids.add(merge_id)
            made += 1
            print(f"  [{made}/{target}] {merge_id} ({len(scenarios)} files)", flush=True)
        else:
            scenario = loader._extract_scenario(repo, repo_name, r)
            if scenario is None:
                extract_fail += 1
                continue

            dest = out_dir / f"{scenario.scenario_id}.json"
            if dest.exists():
                continue  # already materialized in a prior run
            dest.write_text(json.dumps(scenario.to_dict(), indent=2))
            made += 1
            print(f"  [{made}/{target}] {scenario.scenario_id[:70]}", flush=True)

    print(
        f"DONE made={made} tried={tried} multibase_skipped={skip_multibase} "
        f"unresolved={skip_unresolved} clone_fail={clone_fail} clone_timeout={clone_timeout} "
        f"extract_fail={extract_fail} out={out_dir}",
        flush=True,
    )


if __name__ == "__main__":
    main()
