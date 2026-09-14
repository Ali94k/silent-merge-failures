#!/usr/bin/env python3
"""RM2 file-level vs project-level recall delta on the Schesch n=50 (ISSUES #26).

Consumes the tags produced by `tools/rm2_tag.py` (file-level `refactorings`,
R1) and `tools/rm2_tag.py --project-level` (`refactorings_project` — project
trees, same-file filtered; `refactorings_project_full` — unfiltered, kept for
inspection). Produces the R0-promised finding (rm2-integration-recon.md §5–§6):
the tightened n=50 version of the n=10 "file-level recall is 66.7% of
project-level" measurement.

Methodology mirrors R0 exactly:
  * Recall denominator = project-level types filtered to the scenario's
    `file_path` (what R4a *could* observe at merge time) — NOT the whole
    project. Totals are type-occurrence counts (sums of per-scenario-axis
    type-set sizes), the same aggregation R0 used.
  * Each project-level type-occurrence is one Bernoulli trial ("did file-level
    detect it?") → Wilson 95% CI on the pooled and per-axis recall.
  * Cluster impact: `cluster_of` (the comparator's parity-tested copy of the
    driver's classifier mapping) on file-level vs project-level tags per
    scenario; a NONE→X flip is the routing-visible kind post-flip
    (NONE→git fast-path vs Mergiraf).

No Docker, no cache — pure aggregation over the tagged scenario JSONs.
Writes reports_rm2_recall/{summary.txt,scenarios.csv,raw_results.json}.

Usage:
    python3 tools/rm2_recall_delta.py [--scenarios-dir data/scenarios]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.evaluation.categorizer import cluster_of  # noqa: E402

AXES = ("ours", "theirs")
OUT_DIR = ROOT / "reports_rm2_recall"


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """(point, lo, hi) Wilson score interval for k successes in n trials."""
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / den
    return (p, max(0.0, center - half), min(1.0, center + half))


def fmt_ci(k: int, n: int) -> str:
    p, lo, hi = wilson(k, n)
    return f"{k}/{n} = {100*p:.1f}% [{100*lo:.1f}, {100*hi:.1f}]"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenarios-dir", default=str(ROOT / "data" / "scenarios"))
    args = parser.parse_args()

    paths = sorted(Path(args.scenarios_dir).glob("*.json"))
    rows: list[dict] = []
    common = Counter()   # per axis: |file ∩ proj_same_file|
    proj = Counter()     # per axis: |proj_same_file|
    file_ = Counter()    # per axis: |file|
    only_file = Counter()
    missed_types = Counter()   # project-level types file-level missed
    spurious_types = Counter() # file-level types project-level lacks
    cluster_flips = Counter()  # (file_cluster, proj_cluster) where they differ

    for path in paths:
        s = json.loads(path.read_text())
        refs_f = s.get("refactorings")
        refs_p = s.get("refactorings_project")
        if not (isinstance(refs_f, dict) and isinstance(refs_p, dict)):
            sys.exit(f"ERROR: {path.name} lacks file-level or project-level tags — "
                     "run rm2_tag.py (and --project-level) first.")
        row = {"scenario_id": s["scenario_id"], "repo": s["repo_name"]}
        for axis in AXES:
            f = set(refs_f.get(axis, []))
            p = set(refs_p.get(axis, []))
            c = f & p
            common[axis] += len(c)
            proj[axis] += len(p)
            file_[axis] += len(f)
            only_file[axis] += len(f - p)
            for t in p - f:
                missed_types[t] += 1
            for t in f - p:
                spurious_types[t] += 1
            row[f"file_{axis}"] = ";".join(sorted(f))
            row[f"proj_{axis}"] = ";".join(sorted(p))
            row[f"only_proj_{axis}"] = ";".join(sorted(p - f))
            row[f"only_file_{axis}"] = ";".join(sorted(f - p))
        row["cluster_file"] = cluster_of(refs_f.get("ours", []), refs_f.get("theirs", []))
        row["cluster_proj"] = cluster_of(refs_p.get("ours", []), refs_p.get("theirs", []))
        full = s.get("refactorings_project_full", {})
        row["cluster_proj_full"] = cluster_of(full.get("ours", []), full.get("theirs", []))
        if row["cluster_file"] != row["cluster_proj"]:
            cluster_flips[(row["cluster_file"], row["cluster_proj"])] += 1
        rows.append(row)

    n = len(rows)
    pooled_common = sum(common.values())
    pooled_proj = sum(proj.values())
    active = sum(1 for r in rows if any(r[f"proj_{a}"] or r[f"file_{a}"] for a in AXES))
    flips_total = sum(cluster_flips.values())
    none_flips = sum(v for (fc, pc), v in cluster_flips.items() if fc == "NONE")

    lines = []
    add = lines.append
    add(f"RM2 file-level vs project-level recall delta — n={n} scenarios "
        f"({active} active: any types either level)")
    add("")
    add("Recall = file-level detected type-occurrences / project-level (same-file"
        " filter) type-occurrences, Wilson 95% CI:")
    for axis in AXES:
        add(f"  {axis:6s}: {fmt_ci(common[axis], proj[axis])}"
            f"   (file total {file_[axis]}, only-file {only_file[axis]})")
    add(f"  pooled: {fmt_ci(pooled_common, pooled_proj)}")
    add("")
    add(f"Cluster assignment (cluster_of on ours+theirs tags): "
        f"{flips_total}/{n} scenarios classify differently at project level; "
        f"{none_flips} of those are NONE→X flips (the routing-visible kind "
        f"post-flip: NONE→git fast-path vs Mergiraf).")
    for (fc, pc), v in sorted(cluster_flips.items(), key=lambda kv: -kv[1]):
        add(f"    {fc} → {pc}: {v}")
    add("")
    add("Project-level types file-level missed (occurrences across scenario-axes):")
    for t, v in missed_types.most_common():
        add(f"    {v:3d}  {t}")
    if spurious_types:
        add("")
        add("File-level types absent at project level (same-file filter) — "
            "file-level-only detections:")
        for t, v in spurious_types.most_common():
            add(f"    {v:3d}  {t}")

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "summary.txt").write_text("\n".join(lines) + "\n")
    (OUT_DIR / "raw_results.json").write_text(json.dumps({
        "n_scenarios": n,
        "active_scenarios": active,
        "recall": {
            **{a: {"common": common[a], "proj": proj[a], "file": file_[a],
                   "only_file": only_file[a],
                   "wilson": wilson(common[a], proj[a])} for a in AXES},
            "pooled": {"common": pooled_common, "proj": pooled_proj,
                       "wilson": wilson(pooled_common, pooled_proj)},
        },
        "cluster_flips": {f"{fc}->{pc}": v for (fc, pc), v in cluster_flips.items()},
        "missed_types": dict(missed_types),
        "spurious_types": dict(spurious_types),
        "per_scenario": rows,
    }, indent=2))
    with (OUT_DIR / "scenarios.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\n".join(lines))
    print(f"\nwrote {OUT_DIR}/summary.txt, scenarios.csv, raw_results.json")


if __name__ == "__main__":
    main()
