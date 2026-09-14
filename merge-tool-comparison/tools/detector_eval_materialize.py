"""S-D5 eval-controls materialization under the Amendment-1 replacement rule.

Authority: outputs/detector-cycle-plan.md §4 + §12 Amendment 1 +
reports_detectors/controls/README.md. Executes ONLY in S-D5, after the
detector-suite freeze: materializes the 200 committed eval-control primaries
(reports_detectors/controls/eval_controls.csv) into
data/scenarios_detector_eval/ (gitignored, regenerable); a primary that
fails materialization is replaced by the NEXT UNUSED SPARE of the SAME
STRATUM in eval_controls_spares.csv order that keeps per-repo ≤3 among
effective members — deterministic, no hand-picking. Every replacement event
is recorded in <out>/materialize_log.json and belongs in the cycle manifest.

The S-D1 draw already capped per-repo ≤3 over primaries+spares JOINTLY, so
any replacement preserves the cap; the check here is a tripwire, not a
choice point. Stratum quotas (120 ≤3 / 80 >3) are preserved by same-stratum
replacement by construction.

Failure ≡ any of: clone timeout/fail, unresolvable parents, ≠1 merge-base,
zero extractable intersecting files (the draw's own success criterion).

Usage:
    .venv/bin/python tools/detector_eval_materialize.py
    .venv/bin/python tools/detector_eval_materialize.py --out reports_detectors/eval
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT))

import select_materialize as sm  # noqa: E402

CTRL_DIR = ROOT / "reports_detectors/controls"
OUT_DIR = ROOT / "data/scenarios_detector_eval"
PER_REPO_CAP = 3


def _row_for_extract(r: dict) -> dict:
    return {"repository": r["repository"], "left": r["left"], "right": r["right"],
            "merge_commit": r["merge_sha"]}


def _materialize(r: dict, done_ids: set[str]) -> tuple[int | None, str]:
    """(files_materialized|None, reason). Mirrors the S-D1 tune-draw success
    criterion: viable clone + exactly-one merge-base + ≥1 extracted file."""
    mid = r["merge_id"]
    if mid in done_ids:  # resume: a prior run already wrote this merge
        n = sum(1 for f in OUT_DIR.glob(f"{mid}__*.json"))
        return (n or None), "resumed"
    repo_slug = r["repository"]
    repo, reason = sm._clone_blobless(repo_slug, sm.REPOS_DIR, sm.CLONE_TIMEOUT)
    if repo is None:
        return None, f"clone_{reason}"
    repo_path = sm.REPOS_DIR / repo_slug.replace("/", "_")
    sm._ensure_commits(repo_path, [r["left"], r["right"], r["merge_sha"]],
                       sm.CLONE_TIMEOUT)
    try:
        bases = repo.git.merge_base("--all", r["left"], r["right"]).split()
    except Exception:
        return None, "unresolved"
    if len(bases) != 1:
        return None, "multibase"
    scens = sm._extract_all_file_scenarios(
        repo, repo_slug.replace("/", "_"), _row_for_extract(r))
    if not scens:
        return None, "extract_fail"
    for s in scens:
        dest = OUT_DIR / f"{s.scenario_id}.json"
        if not dest.exists():
            d = s.to_dict()
            d["merge_id"] = mid
            dest.write_text(json.dumps(d, indent=2))
    return len(scens), "ok"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports_detectors/eval")
    args = ap.parse_args()
    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    primaries = list(csv.DictReader(open(CTRL_DIR / "eval_controls.csv")))
    spares = list(csv.DictReader(open(CTRL_DIR / "eval_controls_spares.csv")))
    assert len(primaries) == 200 and len(spares) == 40, "committed lists changed size"

    done_ids = sm._existing_merge_ids(OUT_DIR)
    effective: list[dict] = []
    events: list[dict] = []
    used_spares: set[str] = set()
    per_repo: Counter = Counter()
    t0 = time.time()

    def try_accept(r: dict, role: str) -> bool:
        n, reason = _materialize(r, done_ids)
        if n is None:
            events.append({"event": f"{role}_failed", "merge_id": r["merge_id"],
                           "stratum": r["stratum"], "reason": reason})
            print(f"  {role} FAILED {r['merge_id']} ({reason})", flush=True)
            return False
        per_repo[r["repository"]] += 1
        if per_repo[r["repository"]] > PER_REPO_CAP:
            sys.exit(f"ABORT: per-repo cap exceeded for {r['repository']} — "
                     f"the S-D1 joint-cap invariant broke; investigate.")
        effective.append({**r, "files_materialized": n, "role": role})
        return True

    for i, r in enumerate(primaries, 1):
        if try_accept(r, "primary"):
            pass
        else:
            replaced = False
            for s in spares:
                if s["merge_id"] in used_spares or s["stratum"] != r["stratum"]:
                    continue
                if per_repo[s["repository"]] >= PER_REPO_CAP:
                    continue  # unreachable given the joint cap; kept as tripwire
                used_spares.add(s["merge_id"])
                if try_accept(s, "spare"):
                    events.append({"event": "replacement",
                                   "primary": r["merge_id"],
                                   "spare": s["merge_id"],
                                   "stratum": r["stratum"],
                                   "spare_order": s["spare_order"]})
                    replaced = True
                    break
            if not replaced:
                sys.exit(f"ABORT: no usable spare left for stratum {r['stratum']} "
                         f"(primary {r['merge_id']}) — Amendment-1 mechanism "
                         f"exhausted; this needs Ali.")
        if i % 10 == 0 or i == len(primaries):
            print(f"[{i}/200] effective={len(effective)} "
                  f"({int(time.time() - t0)}s)", flush=True)

    strata = Counter(r["stratum"] for r in effective)
    files_total = sum(r["files_materialized"] for r in effective)
    assert len(effective) == 200 and strata == Counter({"le3": 120, "gt3": 80}), \
        f"effective list broke quotas: {dict(strata)}"

    eff_path = out_dir / "eval_controls_effective.csv"
    # ordered union of keys: spare rows carry spare_order, primaries carry order
    cols = list(dict.fromkeys(k for r in effective for k in r))
    with eff_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval="")
        w.writeheader()
        w.writerows(effective)
    digest = hashlib.sha256(eff_path.read_bytes()).hexdigest()

    log = {
        "materialized_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "merges": len(effective),
        "files": files_total,
        "strata": dict(strata),
        "replacement_events": [e for e in events if e["event"] == "replacement"],
        "failure_events": [e for e in events if e["event"] != "replacement"],
        "effective_list": str(eff_path.relative_to(ROOT)),
        "effective_sha256": digest,
        "dir": str(OUT_DIR.relative_to(ROOT)) + "/ (gitignored, regenerable)",
        "seconds": int(time.time() - t0),
    }
    (out_dir / "materialize_log.json").write_text(json.dumps(log, indent=2))
    print(f"\nmaterialized {len(effective)} merges / {files_total} files; "
          f"{len(log['replacement_events'])} replacement(s); "
          f"log → {out_dir / 'materialize_log.json'}", flush=True)


if __name__ == "__main__":
    main()
