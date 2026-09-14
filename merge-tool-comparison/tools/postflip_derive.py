"""Derive the predicted post-flip driver-auto table from committed P2 data.

Routing identity: post-flip `auto` (default map NONE→git, else→Mergiraf; the
refuted #27/#28 specialist arms off) merges each file with exactly the backend
whose driver-arm P2 already measured:

    cluster == NONE  →  the file's `driver-git` P2 result
    cluster != NONE  →  the file's `driver-mergiraf` result (Stage-C assembly)

Clusters come from the 471 per-file route records the P2 `driver-auto` run
logged (`raw_results.json`, committed at 32df839). The RM2 classifier and the
detection strategies are untouched by the flip commit, so per-file results at
`843e5f5` carry over exactly; the derivation is a *prediction* the measured
post-flip AWS re-run must match file-for-file (P3 verification step).

Outputs (into --out, default reports_whole_driver/):
    postflip_derived.md   — predicted cost table + before/after comparison
    postflip_derived.csv  — per-file predictions (the measured==derived join key)

Usage:
    .venv/bin/python tools/postflip_derive.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(2, str(HERE))

from detect_validate import load_scenarios, merge_id_of  # noqa: E402
from whole_driver_eval import (  # noqa: E402
    DEFAULT_CTL, DEFAULT_POS, Classification, driver_mergiraf_result, fmt_ci,
    load_stage_c, metrics_for, per_merge_three_outcome, score,
)

P2_CACHE = ROOT / "reports_whole_driver" / "raw_results.json"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports_whole_driver")
    args = ap.parse_args()
    out_dir = ROOT / args.out

    cache = json.loads(P2_CACHE.read_text())
    sc = load_stage_c()
    scns = [("pos", s) for s in load_scenarios(ROOT / DEFAULT_POS)] + \
           [("ctl", s) for s in load_scenarios(ROOT / DEFAULT_CTL)]

    derived, preflip = [], []
    missing_route = missing_git = 0
    by_cluster: Counter = Counter()
    for arm, scn in scns:
        sid = scn["scenario_id"]
        auto_rec = cache.get(f"driver-auto::{sid}")          # pre-flip P2 keys
        if not auto_rec or not auto_rec.get("route"):
            missing_route += 1
            continue
        cluster = auto_rec["route"]["cluster"]
        by_cluster[cluster] += 1

        if cluster == "NONE":
            res = cache.get(f"driver-git::{sid}")
            if res is None:
                missing_git += 1
                continue
            source = "driver-git"
        else:
            res = driver_mergiraf_result(scn, sc)
            source = "driver-mergiraf"

        ref = sc.get(sid, {}).get("ref_merged")
        for bucket, rec in ((derived, res), (preflip, auto_rec)):
            cls, oracle = score(arm, rec, scn, ref)
            bucket.append({
                "arm": arm, "merge_id": merge_id_of(scn), "scenario_id": sid,
                "outcome": rec["outcome"], "reject_reason": rec.get("reject_reason"),
                "cls": cls, "oracle": oracle, "rt": rec.get("rt", 0.0),
                "source": source if bucket is derived else "measured-preflip",
            })

    if missing_route or missing_git:
        sys.exit(f"ABORT: incomplete P2 artifact — {missing_route} files without "
                 f"route records, {missing_git} without driver-git results.")

    lines: list[str] = []
    p = lines.append
    p("# Post-flip driver-auto — DERIVED prediction (from committed P2 data)")
    p("")
    p(f"Basis: P2 `raw_results.json` (pre-flip run @ driver `843e5f5`); "
      f"{len(derived)} files; clusters {dict(by_cluster)}.")
    p("Identity: NONE→driver-git rows; else→driver-mergiraf rows. The flip commit")
    p("touches only `auto_backend._route`, so per-file results carry over exactly.")
    p("**The measured post-flip AWS re-run must match this file-for-file on**")
    p("**`outcome` + `reject_reason`** (environment-independent). The cost/`cls`")
    p("columns here are scored in the *local* environment — divergent outputs are")
    p("dev-match-scored, which is normalization-sensitive (FINDINGS §7a): e.g. the")
    p("pre-flip control-FP count re-scores locally as 21 vs 33 on AWS. Citable")
    p("post-flip cost tables come from the AWS-scored measured run; the")
    p("before/after below is internally consistent (both sides local-scored).")
    p("")
    for label, rows in (("derived post-flip driver-auto", derived),
                        ("measured PRE-flip driver-auto (P2)", preflip)):
        p(f"## {label}")
        p(f"  {'arm':6s} {'n':>4} {'TP':>4} {'FP':>4} {'TN':>4} {'FN':>4} {'CR':>3} "
          f"{'cost':>7} {'cost/n':>7}")
        for arm in ("pos", "ctl", None):
            sel = [r for r in rows if (arm is None or r["arm"] == arm)]
            m = metrics_for(sel)
            cost = m.weighted_cost()
            p(f"  {arm or 'ALL':6s} {m.scenario_count:>4} {m.tp:>4} {m.fp:>4} "
              f"{m.tn:>4} {m.fn:>4} {m.crashes + m.timeouts:>3} {cost:>7.0f} "
              f"{cost / m.scenario_count:>7.2f}")
        three = Counter()
        for arm in ("pos", "ctl"):
            sub = per_merge_three_outcome([r for r in rows if r["arm"] == arm])
            three[arm] = Counter(sub.values())
        p(f"  three-outcome pos: {dict(three['pos'])}")
        p(f"  three-outcome ctl: {dict(three['ctl'])}")
        p("")

    d_ctl_fp = sum(1 for r in derived if r["arm"] == "ctl"
                   and r["cls"] == Classification.FALSE_POSITIVE)
    b_ctl_fp = sum(1 for r in preflip if r["arm"] == "ctl"
                   and r["cls"] == Classification.FALSE_POSITIVE)
    dcost = metrics_for(preflip).weighted_cost() - metrics_for(derived).weighted_cost()
    p("## Before/after (the flip's predicted effect)")
    p(f"  control FPs from routing: {b_ctl_fp} → {d_ctl_fp}")
    p(f"  pooled weighted cost improvement (pre − post): {dcost:.0f}")
    p("")

    text = "\n".join(lines)
    (out_dir / "postflip_derived.md").write_text(text + "\n")
    with open(out_dir / "postflip_derived.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "merge_id", "scenario_id", "outcome", "reject_reason",
                    "classification", "oracle", "source"])
        for r in derived:
            w.writerow([r["arm"], r["merge_id"], r["scenario_id"], r["outcome"],
                        r["reject_reason"] or "", r["cls"].value, r["oracle"],
                        r["source"]])
    print(text)
    print(f"Wrote {out_dir}/postflip_derived.md, postflip_derived.csv")


if __name__ == "__main__":
    main()
