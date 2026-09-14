"""Detector-cycle control draws (ISSUES #31, S-D1).

Authority: outputs/detector-cycle-plan.md §4 (draw constraints) + §12
Amendment 1 (2026-07-16: viability + spares mechanism; eval pool = the same
`semantic_ctl` pool as tune). Draws are seeded and scripted — no session
ever hand-picks a control unit.

Pool (one pool, both draws): reaper/result_adjusted.csv rows with a Java
diff and mergiraf == Tests_passed (select_materialize's `semantic_ctl`
criterion), restricted to rows with a PARSEABLE num_intersecting_files
(stratification needs it; unparseable rows are counted and excluded),
minus the 195 Stage-C control merges (data/scenarios_semantic_ctl).

Two seeded walks over the shuffled pool, each filling stratum quotas
(~60/40 census file-count mix) under a ≤3-merges-per-repo cap:

  tune  (SEED_TUNE=20260715, 60 ≤3 + 40 >3): Stage-C-style
        draw-with-materialization — a candidate is accepted only when its
        every-intersecting-file scenario set materializes (blobless clone,
        by-SHA parent fetch, exactly-one merge-base, non-empty contents at
        all four commits). The first 100 successes ARE the committed list;
        scenario JSONs land in data/scenarios_detector_tune/ (gitignored,
        regenerable — the committed list + this script are the artifact).
  eval  (SEED_EVAL=20260716, 120 ≤3 + 80 >3, +40 ordered spares 24/16):
        viability check WITHOUT content extraction (§3 firewall: eval
        contents are materialized only in S-D5) — blobless clone + by-SHA
        parent fetch + exactly-one merge-base. Excludes the tune draw's
        accepted merges (mutual disjointness). Spares respect the same
        per-repo cap counting primaries + earlier spares.

S-D5 replacement rule (Amendment 1): a primary that fails materialization
is replaced by the next unused spare of the same stratum that keeps
per-repo ≤3 among effective members; replacements are recorded in the
cycle manifest.

Resume: a tune merge whose JSONs already exist in the output dir is
re-accepted without re-extraction, so an interrupted run replays the same
deterministic walk.

Usage:
    DRY=1 ./.venv/bin/python tools/detector_controls_draw.py   # pool stats only
    ./.venv/bin/python tools/detector_controls_draw.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT))

import select_materialize as sm  # noqa: E402  (clone/extract machinery reused)

SEED_TUNE = 20260715
SEED_EVAL = 20260716
QUOTAS_TUNE = {"le3": 60, "gt3": 40}
QUOTAS_EVAL = {"le3": 120, "gt3": 80}
QUOTAS_EVAL_SPARES = {"le3": 24, "gt3": 16}
PER_REPO_CAP = 3

STAGEC_DIR = ROOT / "data/scenarios_semantic_ctl"
STAGEC_EXPECTED = 195
TUNE_OUT = ROOT / "data/scenarios_detector_tune"
CTRL_DIR = ROOT / "reports_detectors/controls"


def _merge_id(row: dict) -> str:
    sha = row.get("merge_commit") or row.get("merge", "")
    return f"{row['repository'].replace('/', '_')}__{sha[:10]}"


def _stratum(row: dict) -> tuple[str, int] | None:
    try:
        n = int(float(row.get("num_intersecting_files", "")))
    except (TypeError, ValueError):
        return None
    return ("le3" if n <= 3 else "gt3"), n


def _stagec_ids() -> set[str]:
    ids = {"__".join(f.name.split("__")[:2]) for f in STAGEC_DIR.glob("*.json")}
    if len(ids) != STAGEC_EXPECTED:
        sys.exit(f"ABORT: Stage-C exclusion set has {len(ids)} merges, expected {STAGEC_EXPECTED}")
    return ids


def _viable(row: dict):
    """Blobless clone + by-SHA parent fetch + exactly-one merge-base.

    No file contents are read — safe for eval candidates (§3 firewall).
    Returns (Repo|None, reason).
    """
    repo_slug = row["repository"]
    repo, reason = sm._clone_blobless(repo_slug, sm.REPOS_DIR, sm.CLONE_TIMEOUT)
    if repo is None:
        return None, f"clone_{reason}"
    left, right = row.get("left"), row.get("right")
    merge_sha = row.get("merge_commit") or row.get("merge", "")
    sm._ensure_commits(sm.REPOS_DIR / repo_slug.replace("/", "_"),
                       [left, right, merge_sha], sm.CLONE_TIMEOUT)
    try:
        bases = repo.git.merge_base("--all", left, right).split()
    except Exception:
        return None, "unresolved"
    if len(bases) != 1:
        return None, "multibase"
    return repo, "ok"


def _draw(pool: list[dict], seed: int, quotas: dict[str, int],
          spare_quotas: dict[str, int] | None, exclude: set[str],
          materialize_to: Path | None, label: str):
    """One seeded walk. Returns (accepted, spares, log)."""
    cands = [r for r in pool if _merge_id(r) not in exclude]
    rng = random.Random(seed)
    rng.shuffle(cands)

    done_ids = sm._existing_merge_ids(materialize_to) if materialize_to else set()
    accepted: list[dict] = []
    spares: list[dict] = []
    per_repo: Counter = Counter()
    quota_left = dict(quotas)
    spare_left = dict(spare_quotas) if spare_quotas else {}
    log: Counter = Counter()
    t0 = time.time()

    for row in cands:
        if not any(quota_left.values()) and not any(spare_left.values()):
            break
        st, n_files = _stratum(row)  # pool is pre-filtered: never None
        if quota_left.get(st, 0) > 0:
            role = "primary"
        elif spare_left.get(st, 0) > 0:
            role = "spare"
        else:
            log["skip_stratum_full"] += 1
            continue
        if per_repo[row["repository"]] >= PER_REPO_CAP:
            log["skip_repo_cap"] += 1
            continue

        mid = _merge_id(row)
        repo, reason = _viable(row)
        if repo is None:
            log[f"skip_{reason}"] += 1
            print(f"  [{label}] {mid}: {reason} — skipped", flush=True)
            continue

        files_materialized = None
        if materialize_to is not None:
            if mid in done_ids:  # resume: prior run already wrote this merge
                files_materialized = sum(
                    1 for f in materialize_to.glob("*.json")
                    if json.loads(f.read_text()).get("merge_id") == mid)
                log["resumed"] += 1
            else:
                scens = sm._extract_all_file_scenarios(
                    repo, row["repository"].replace("/", "_"), row)
                if not scens:
                    log["skip_extract_fail"] += 1
                    print(f"  [{label}] {mid}: extract_fail — skipped", flush=True)
                    continue
                for s in scens:
                    dest = materialize_to / f"{s.scenario_id}.json"
                    if not dest.exists():
                        d = s.to_dict()
                        d["merge_id"] = mid
                        dest.write_text(json.dumps(d, indent=2))
                files_materialized = len(scens)

        rec = {
            "merge_id": mid,
            "repository": row["repository"],
            "merge_sha": row.get("merge_commit") or row.get("merge", ""),
            "left": row.get("left", ""),
            "right": row.get("right", ""),
            "stratum": st,
            "num_intersecting_files": n_files,
        }
        if files_materialized is not None:
            rec["files_materialized"] = files_materialized
        per_repo[row["repository"]] += 1
        if role == "primary":
            quota_left[st] -= 1
            rec["order"] = len(accepted) + 1
            accepted.append(rec)
        else:
            spare_left[st] -= 1
            rec["spare_order"] = len(spares) + 1
            spares.append(rec)
        got = f"{len(accepted)}/{sum(quotas.values())}"
        sp = f" spares {len(spares)}/{sum(spare_quotas.values())}" if spare_quotas else ""
        print(f"  [{label}] {role} {got}{sp} {st} {mid}", flush=True)

    if any(quota_left.values()) or any(spare_left.values()):
        sys.exit(f"ABORT: {label} pool exhausted with quotas unfilled: "
                 f"{quota_left} spares {spare_left}")
    log["seconds"] = int(time.time() - t0)
    return accepted, spares, dict(log)


def _write_csv(path: Path, rows: list[dict]) -> str:
    cols = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"wrote {path.relative_to(ROOT)}  n={len(rows)}  sha256={digest}", flush=True)
    return digest


def main() -> None:
    CTRL_DIR.mkdir(parents=True, exist_ok=True)
    TUNE_OUT.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(open(sm.CSV_PATH)))
    ctl = [r for r in rows if sm._has_java(r) and r.get("mergiraf", "") == sm.PASS]
    unparseable = [r for r in ctl if _stratum(r) is None]
    pool = [r for r in ctl if _stratum(r) is not None]
    stagec = _stagec_ids()
    in_pool = {_merge_id(r) for r in pool}
    missing = stagec - in_pool
    if missing:
        sys.exit(f"ABORT: {len(missing)} Stage-C control ids not found in pool: "
                 f"{sorted(missing)[:5]}")
    fresh = [r for r in pool if _merge_id(r) not in stagec]
    strata = Counter(_stratum(r)[0] for r in fresh)
    print(f"pool: semantic_ctl={len(ctl)} unparseable_excluded={len(unparseable)} "
          f"stagec_excluded={STAGEC_EXPECTED} fresh={len(fresh)} strata={dict(strata)}",
          flush=True)
    if os.environ.get("DRY") == "1":
        return

    stagec_rows = [{"merge_id": m} for m in sorted(stagec)]
    h_stagec = _write_csv(CTRL_DIR / "stagec_exclusion_195.csv", stagec_rows)

    tune, _, tune_log = _draw(fresh, SEED_TUNE, QUOTAS_TUNE, None,
                              set(), TUNE_OUT, "tune")
    h_tune = _write_csv(CTRL_DIR / "tune_controls.csv", tune)

    tune_ids = {r["merge_id"] for r in tune}
    evalp, spares, eval_log = _draw(fresh, SEED_EVAL, QUOTAS_EVAL,
                                    QUOTAS_EVAL_SPARES, tune_ids, None, "eval")
    h_eval = _write_csv(CTRL_DIR / "eval_controls.csv", evalp)
    h_spares = _write_csv(CTRL_DIR / "eval_controls_spares.csv", spares)

    log = {
        "drawn_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "pool": {"semantic_ctl": len(ctl), "unparseable_excluded": len(unparseable),
                 "stagec_excluded": STAGEC_EXPECTED, "fresh": len(fresh),
                 "strata": dict(strata)},
        "seeds": {"tune": SEED_TUNE, "eval": SEED_EVAL},
        "quotas": {"tune": QUOTAS_TUNE, "eval": QUOTAS_EVAL,
                   "eval_spares": QUOTAS_EVAL_SPARES},
        "per_repo_cap": PER_REPO_CAP,
        "clone_timeout": sm.CLONE_TIMEOUT,
        "tune_walk": tune_log,
        "eval_walk": eval_log,
        "sha256": {"stagec_exclusion_195.csv": h_stagec,
                   "tune_controls.csv": h_tune,
                   "eval_controls.csv": h_eval,
                   "eval_controls_spares.csv": h_spares},
    }
    (CTRL_DIR / "draw_log.json").write_text(json.dumps(log, indent=2))
    print("draw complete; log at reports_detectors/controls/draw_log.json", flush=True)


if __name__ == "__main__":
    main()
