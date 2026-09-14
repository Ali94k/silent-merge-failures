"""S-D7 Stage-C-protocol rerun — blend-safe before/after (ISSUES #31 follow-on).

Authority: outputs/detector-cycle-plan.md §8 S-D7 stub + §3 freeze (suite
commit 732d8ff) + never-blend; green-lit at S-D6 (2026-07-20). The frozen
Stage-C instrument `detect_validate.py` is NOT edited or executed — this
harness re-runs its PROTOCOL (populations, mergiraf reproduction, unit-level
BLOCKED aggregation incl. fail-closed) with the S-D5 two-arm pattern:

  baseline     — the 5 default lanes, experimental flag OFF. MUST reproduce
                 the frozen post-fix Stage-C verdicts (reports_detection/
                 postfix2/, lanes f964354 == 732d8ff flag-off) — that
                 comparison is this run's known-answer environment gate.
  experimental — the FULL 7-lane suite, flag ON.

Populations — the Stage-C instrument's own, loaded with integrity gates
(scenario_id sets must equal reports_detection/postfix2/scenarios.csv; the
positives are additionally sha256-checked against the taxonomy manifest pins):
  stagec_pos  data/scenarios_semantic      180 merges / 232 files (164 scored)
  stagec_ctl  data/scenarios_semantic_ctl  195 merges / 239 files (193 scored)

Aggregation is the Stage-C rule, NOT the S-D5 machine-caught rule: a merge is
BLOCKED if any scored (clean-merged) file FLAGs (block_reason=flag) or, with
no FLAG, any is UNANALYZABLE (block_reason=fail_closed); merges whose files
all diverge leave the sample. R2' = blocked positives / scored, R1' = blocked
controls / scored, per arm, flag vs fail-closed decomposed, Wilson CIs.

Never blend: numbers produced here are the Stage-C instrument's before/after
only. S-D5/S-D6 held-out, eval-control, and spgroup numbers are a separate
instrument and appear in no derived figure here. (The optional
--crosscheck-sd5 mode compares raw cached VERDICTS on overlapping
(scenario, lane, flag) keys as an environment-consistency check; it writes a
separate file and feeds no number in summary.txt.)

Sharding is a WORK-QUEUE (the S-D5 static-shard imbalance lesson): workers
claim whole merges via O_EXCL claim files in <out>/queue_<pop>/, largest
merges first, and write per-worker caches eval_cache_<pop>_w<K>.json.
A crashed worker's merge is re-queued with --requeue-stale (claims without a
.done marker are deleted; duplicate cache keys are cross-checked at scoring).

Usage:
    .venv/bin/python tools/detector_stagec_rerun.py --smoke
    .venv/bin/python tools/detector_stagec_rerun.py --known-answer 3
    .venv/bin/python tools/detector_stagec_rerun.py --population stagec_pos --worker 0
    .venv/bin/python tools/detector_stagec_rerun.py --requeue-stale
    .venv/bin/python tools/detector_stagec_rerun.py --score
    .venv/bin/python tools/detector_stagec_rerun.py --crosscheck-sd5
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import statistics
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # merge-tool-comparison/
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "tools"))

from detect_validate import (  # noqa: E402
    MERGIRAF_IMAGE, load_scenarios, preflight, reproduce_merge, run_detector,
    fmt_ci,
)
from detector_eval_run import (  # noqa: E402
    ARM_VIEW, BASELINE_LANES, EXECS_BOTH_ARMS, FLAG_ENV, WIDENED_STEM,
    assert_flag_free_lanes, assert_frozen_commit, classify_issue,
    run_known_answer, run_smokes, verdict_from_issues,
)
import detector_tune_run as tune  # noqa: E402

DEFAULT_OUT = "reports_detectors/stagec_rerun"
POSTFIX2 = ROOT / "reports_detection/postfix2"
SD5_EVAL = ROOT / "reports_detectors/eval"

POPULATIONS = {
    "stagec_pos": dict(dir="data/scenarios_semantic", arm_csv="pos",
                       n_merges=180, n_files=232),
    "stagec_ctl": dict(dir="data/scenarios_semantic_ctl", arm_csv="ctl",
                       n_merges=195, n_files=239),
}


# --------------------------------------------------------------------------- #
# population loading + integrity gates
# --------------------------------------------------------------------------- #
def postfix2_expected() -> dict[str, set[str]]:
    """arm -> scenario_id set from the frozen post-fix run's scenarios.csv."""
    out: dict[str, set[str]] = {"pos": set(), "ctl": set()}
    for r in csv.DictReader(open(POSTFIX2 / "scenarios.csv")):
        out[r["arm"]].add(r["scenario_id"])
    return out


def taxonomy_pins() -> dict[str, str]:
    return json.loads((ROOT / "reports_taxonomy/manifest.json").read_text())[
        "scenario_files_sha256"]


def load_population(pop: str) -> list[dict]:
    cfg = POPULATIONS[pop]
    d = ROOT / cfg["dir"]
    scns = load_scenarios(d)
    got = {s["scenario_id"] for s in scns}
    want = postfix2_expected()[cfg["arm_csv"]]
    if got != want:
        sys.exit(f"ABORT: {pop} scenario_id set != frozen postfix2 population "
                 f"(missing {sorted(want - got)[:3]}, extra {sorted(got - want)[:3]}) "
                 f"— the before/after is defined on the ORIGINAL Stage-C units.")
    mids = {s["merge_id"] for s in scns}
    if len(mids) != cfg["n_merges"] or len(scns) != cfg["n_files"]:
        sys.exit(f"ABORT: {pop} expected {cfg['n_merges']} merges / "
                 f"{cfg['n_files']} files, found {len(mids)} / {len(scns)}.")
    if pop == "stagec_pos":
        pins = taxonomy_pins()
        bad = []
        for f in sorted(d.glob("*.json")):
            rel = str(f.relative_to(ROOT))
            if pins.get(rel) != hashlib.sha256(f.read_bytes()).hexdigest():
                bad.append(rel)
        if bad:
            sys.exit(f"ABORT: {len(bad)} stagec_pos files fail the taxonomy "
                     f"sha256 pins (e.g. {bad[:3]}) — rematerialize first.")
    return scns


def group_by_merge(scns: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for s in scns:
        groups.setdefault(s["merge_id"], []).append(s)
    return groups


# --------------------------------------------------------------------------- #
# work-queue execution
# --------------------------------------------------------------------------- #
def run_population_queue(pop: str, out_dir: Path, commit: str, worker: int,
                         limit: int = 0) -> None:
    scns = load_population(pop)
    groups = group_by_merge(scns)
    # largest merges first: the queue self-balances where static shards didn't
    order = sorted(groups, key=lambda m: (-len(groups[m]), m))
    qdir = out_dir / f"queue_{pop}"
    qdir.mkdir(parents=True, exist_ok=True)
    cpath = out_dir / f"eval_cache_{pop}_w{worker}.json"
    cache: dict = json.loads(cpath.read_text()) if cpath.exists() else {}

    def save() -> None:
        cpath.write_text(json.dumps(cache))

    strategies = {ln: tune.LANES[ln][0]() for ln, _ in EXECS_BOTH_ARMS}
    print(f"[{pop} w{worker}] queue of {len(order)} merges / {len(scns)} files "
          f"| execs/file: {len(EXECS_BOTH_ARMS)} | cache {cpath.name}", flush=True)

    t_start, n_claimed = time.time(), 0
    for mid in order:
        if (qdir / f"{mid}.done").exists():
            continue
        try:
            fd = os.open(qdir / f"{mid}.claim", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"w{worker}\n".encode())
            os.close(fd)
        except FileExistsError:
            continue
        for scn in groups[mid]:
            merge_rec = reproduce_merge(scn, cache, save)
            if merge_rec["outcome"] != "clean":
                continue
            dirty = False
            with tempfile.TemporaryDirectory() as td:
                merged_path = Path(td) / Path(scn["file_path"]).name
                written = False
                for lane, flagseg in EXECS_BOTH_ARMS:
                    key = f"{scn['scenario_id']}::{lane}::{commit}::{flagseg}"
                    if key in cache:
                        continue
                    if not written:
                        merged_path.write_text(merge_rec["merged"], encoding="utf-8")
                        written = True
                    os.environ[FLAG_ENV] = "1" if flagseg == "flag1" else "0"
                    cache[key] = run_detector(lane, strategies[lane],
                                              "differential", str(merged_path), scn)
                    dirty = True
            if dirty:
                save()
        (qdir / f"{mid}.done").write_text(f"w{worker}\n")
        n_claimed += 1
        rate = (time.time() - t_start) / n_claimed
        n_done = len(list(qdir.glob("*.done")))
        print(f"  [{pop} w{worker}] {mid} done ({n_claimed} claimed, "
              f"{rate:.0f}s/merge avg; queue {n_done}/{len(order)})", flush=True)
        if limit and n_claimed >= limit:
            print(f"[{pop} w{worker}] --limit {limit} reached, exiting", flush=True)
            break
    save()
    print(f"[{pop} w{worker}] queue drained → {cpath.name}", flush=True)


def requeue_stale(out_dir: Path) -> None:
    for pop in POPULATIONS:
        qdir = out_dir / f"queue_{pop}"
        if not qdir.exists():
            continue
        stale = [c for c in qdir.glob("*.claim")
                 if not (qdir / (c.stem + ".done")).exists()]
        for c in stale:
            print(f"requeue: {pop} {c.stem} (claim without done)")
            c.unlink()
        print(f"[{pop}] {len(stale)} stale claims removed")


# --------------------------------------------------------------------------- #
# scoring — Stage-C aggregation per arm + known-answer gate
# --------------------------------------------------------------------------- #
def load_caches(out_dir: Path, pop: str) -> tuple[dict, list[str]]:
    """Merged per-worker caches + keys whose duplicates disagree (env drift)."""
    merged: dict = {}
    conflicts: list[str] = []
    for f in sorted(out_dir.glob(f"eval_cache_{pop}_w*.json")):
        for k, v in json.loads(f.read_text()).items():
            if k in merged:
                a, b = merged[k], v
                if a.get("verdict") != b.get("verdict") or \
                   a.get("outcome") != b.get("outcome"):
                    conflicts.append(k)
            merged[k] = v
    return merged, conflicts


def file_arm_verdict(frow_lanes: dict, arm: str) -> tuple[str, list]:
    """Stage-C file verdict under one arm's lane view + FLAG lane list."""
    flags, una = [], []
    for lane, flagseg in ARM_VIEW[arm]:
        lrec = frow_lanes.get(f"{lane}::{flagseg}")
        if lrec is None:
            continue
        if lrec["verdict"] == "FLAG":
            flags.append(lane)
        elif lrec["verdict"] == "UNANALYZABLE":
            una.append(lane)
    v = "FLAG" if flags else ("UNANALYZABLE" if una else "CLEAN")
    return v, flags


def score_population(pop: str, out_dir: Path, commit: str):
    scns = load_population(pop)
    groups = group_by_merge(scns)
    cache, conflicts = load_caches(out_dir, pop)
    if not cache:
        return None
    units, drift_rows, missing = [], [], []
    for mid, ss in sorted(groups.items()):
        row = {"merge_id": mid, "n_files": len(ss), "files": {}, "arm": {}}
        n_diverged = 0
        for scn in ss:
            mrec = cache.get(f"{scn['scenario_id']}::__merge__::{MERGIRAF_IMAGE}")
            if mrec is None:
                missing.append(f"{scn['scenario_id']}::__merge__")
                continue
            if mrec["outcome"] != "clean":
                n_diverged += 1
                row["files"][scn["scenario_id"]] = {"merge_outcome": mrec["outcome"]}
                continue
            frow = {"merge_outcome": "clean", "lanes": {}}
            for lane, flagseg in EXECS_BOTH_ARMS:
                key = f"{scn['scenario_id']}::{lane}::{commit}::{flagseg}"
                rec = cache.get(key)
                if rec is None:
                    missing.append(key)
                    continue
                verdict, drift = verdict_from_issues(rec["issues"])
                for d in drift:
                    drift_rows.append({"key": key, "message": d})
                frow["lanes"][f"{lane}::{flagseg}"] = {
                    "verdict": verdict, "issues": rec["issues"],
                    "runtime_s": rec.get("runtime_s", 0.0)}
            row["files"][scn["scenario_id"]] = frow
        row["n_diverged"] = n_diverged
        for arm in ("baseline", "experimental"):
            f_verdicts = {}
            flag_lanes = []
            for fid, frow in row["files"].items():
                if frow.get("merge_outcome") != "clean":
                    continue
                v, flags = file_arm_verdict(frow.get("lanes", {}), arm)
                f_verdicts[fid] = v
                flag_lanes.extend((fid, ln) for ln in flags)
            n_scored = len(f_verdicts)
            if n_scored == 0:
                status, reason = "ALL_DIVERGED", None
            elif "FLAG" in f_verdicts.values():
                status, reason = "BLOCKED", "flag"
            elif "UNANALYZABLE" in f_verdicts.values():
                status, reason = "BLOCKED", "fail_closed"
            else:
                status, reason = "PASSED", None
            row["arm"][arm] = {"status": status, "block_reason": reason,
                               "flag_lanes": flag_lanes,
                               "file_verdicts": f_verdicts}
        units.append(row)
    return {"population": pop, "units": units, "drift": drift_rows,
            "missing": missing, "cache_conflicts": conflicts}


def known_answer_vs_postfix2(results: dict, out_dir: Path, commit: str) -> dict:
    """The S-D7 env gate: the baseline arm must reproduce the frozen post-fix
    Stage-C run (reports_detection/postfix2) verdict-for-verdict."""
    pf = json.loads((POSTFIX2 / "raw_results.json").read_text())
    ref_commits = {k.split("::")[2] for k in pf
                   if "::__merge__::" not in k and "::__sanity__::" not in k}
    if len(ref_commits) != 1:
        sys.exit(f"ABORT: postfix2 cache holds {len(ref_commits)} lane-key "
                 f"commits {sorted(ref_commits)} — expected exactly one.")
    ref_commit = ref_commits.pop()
    flagseg_of = {ln: ("flag0" if ln == "JoernUnresolvedReference" else "flagX")
                  for ln in BASELINE_LANES}

    # completeness targets come from the frozen reference itself
    expect_merge = sum(1 for k in pf if "::__merge__::" in k)
    expect_clean = sum(1 for k, v in pf.items()
                       if "::__merge__::" in k and v["outcome"] == "clean")
    expect_lane = sum(1 for k in pf
                      if "::__merge__::" not in k and "::__sanity__::" not in k)

    stats = Counter()
    mismatches, classifier_div = [], []
    for pop in ("stagec_pos", "stagec_ctl"):
        r = results.get(pop)
        if not r:
            continue
        cache, _ = load_caches(out_dir, pop)
        for scn in load_population(pop):
            sid = scn["scenario_id"]
            mkey = f"{sid}::__merge__::{MERGIRAF_IMAGE}"
            mine, ref = cache.get(mkey), pf.get(mkey)
            if mine is None:
                stats["not_run"] += 1        # incomplete run — totals gate FAILs
                continue
            if ref is None:
                mismatches.append({"key": mkey, "kind": "no_reference_row"})
                continue
            stats["merge_compared"] += 1
            if mine["outcome"] != ref["outcome"]:
                mismatches.append({"key": mkey, "kind": "merge_outcome",
                                   "mine": mine["outcome"], "ref": ref["outcome"]})
                continue
            if mine["outcome"] == "clean":
                h_mine = hashlib.sha256(mine["merged"].encode()).hexdigest()
                h_ref = hashlib.sha256(ref["merged"].encode()).hexdigest()
                stats["merged_content_compared"] += 1
                if h_mine != h_ref:
                    mismatches.append({"key": mkey, "kind": "merged_content"})
                    continue
                for lane in BASELINE_LANES:
                    mine_l = cache.get(f"{sid}::{lane}::{commit}::{flagseg_of[lane]}")
                    ref_l = pf.get(f"{sid}::{lane}::{ref_commit}")
                    if mine_l is None:
                        stats["not_run"] += 1
                        continue
                    if ref_l is None:
                        mismatches.append({"key": f"{sid}::{lane}",
                                           "kind": "no_reference_row"})
                        continue
                    my_v, _ = verdict_from_issues(mine_l["issues"])
                    ref_v_cw, _ = verdict_from_issues(ref_l["issues"])
                    if ref_v_cw != ref_l["verdict"]:
                        classifier_div.append({"key": f"{sid}::{lane}",
                                               "closed_world": ref_v_cw,
                                               "recorded": ref_l["verdict"]})
                    stats["lane_compared"] += 1
                    if my_v != ref_v_cw:
                        mismatches.append({"key": f"{sid}::{lane}",
                                           "kind": "lane_verdict",
                                           "mine": my_v, "ref": ref_v_cw,
                                           "mine_issues": mine_l["issues"],
                                           "ref_issues": ref_l["issues"]})
    complete = (stats["merge_compared"] == expect_merge
                and stats["merged_content_compared"] == expect_clean
                and stats["lane_compared"] == expect_lane)
    gate = {"ref_commit": ref_commit,
            "expected": {"merge": expect_merge, "clean": expect_clean,
                         "lane": expect_lane},
            "merge_compared": stats["merge_compared"],
            "merged_content_compared": stats["merged_content_compared"],
            "lane_compared": stats["lane_compared"],
            "not_run": stats["not_run"],
            "mismatches": mismatches,
            "classifier_divergence": classifier_div,
            "verdict": ("PASS" if complete and not mismatches else
                        "FAIL" if mismatches else "INCOMPLETE")}
    (out_dir / "known_answer.json").write_text(json.dumps(gate, indent=1))
    return gate


def arm_table(units: list[dict], arm: str) -> dict:
    scored = [u for u in units if u["arm"][arm]["status"] != "ALL_DIVERGED"]
    blocked = [u for u in scored if u["arm"][arm]["status"] == "BLOCKED"]
    return {
        "n_materialized": len(units),
        "n_scored": len(scored),
        "blocked": blocked,
        "by_flag": [u for u in blocked if u["arm"][arm]["block_reason"] == "flag"],
        "by_fc": [u for u in blocked if u["arm"][arm]["block_reason"] == "fail_closed"],
    }


def split_assignment() -> dict[str, str]:
    rows = csv.DictReader(open(ROOT / "reports_taxonomy/split_assignment.csv"))
    return {r["merge_id"]: r["split"] for r in rows}


def write_reports(out_dir: Path, commit: str, results: dict, gate: dict) -> str:
    lines: list[str] = []
    p = lines.append
    p(f"# S-D7 Stage-C-protocol rerun — before/after on the Stage-C instrument "
      f"(suite frozen at {commit})")
    p(f"# harness: tools/detector_stagec_rerun.py (detect_validate.py protocol, "
      f"instrument NOT edited) | mergiraf {MERGIRAF_IMAGE}")
    p("# NEVER BLEND: this table is the Stage-C instrument only. S-D5/S-D6")
    p("# held-out / eval-control / spgroup numbers are a separate instrument and")
    p("# appear in no figure here. Stage-C frozen/post-fix history: ISSUES #29.")
    p("")

    drift_total = sum(len(r["drift"]) for r in results.values())
    missing_total = sum(len(r["missing"]) for r in results.values())
    conflict_total = sum(len(r["cache_conflicts"]) for r in results.values())
    if drift_total or missing_total or conflict_total:
        p(f"## *** BLOCKED: drift={drift_total} missing={missing_total} "
          f"cache-conflicts={conflict_total} — resolve before citing numbers ***")
        p("")

    p(f"## Known-answer env gate — baseline arm vs frozen post-fix Stage-C run")
    p(f"   (reports_detection/postfix2, lanes @{gate['ref_commit']}; gate = "
      f"file-level verdict equality, stronger than unit-number equality)")
    e = gate["expected"]
    p(f"  merge outcomes compared : {gate['merge_compared']}/{e['merge']} | "
      f"merged-content sha256 compared: "
      f"{gate['merged_content_compared']}/{e['clean']}")
    p(f"  5-lane baseline verdicts compared: {gate['lane_compared']}/{e['lane']}"
      f" | rows not yet run: {gate['not_run']}")
    p(f"  mismatches: {len(gate['mismatches'])} | classifier divergence on "
      f"postfix2 rows: {len(gate['classifier_divergence'])}")
    p(f"  GATE: {gate['verdict']}")
    p("")

    metric = {"stagec_pos": ("R2'", "positives (mergiraf=Tests_failed)"),
              "stagec_ctl": ("R1'", "controls (mergiraf=Tests_passed)")}
    deltas = {}
    for pop in ("stagec_pos", "stagec_ctl"):
        r = results.get(pop)
        if not r:
            continue
        m, label = metric[pop]
        p(f"## {label} — {m} per arm (unit = merge; BLOCKED = any scored file "
          f"FLAG, else any fail-closed; all-diverged leave the sample)")
        tables = {}
        for arm in ("baseline", "experimental"):
            t = arm_table(r["units"], arm)
            tables[arm] = t
            n = t["n_scored"]
            p(f"  {arm:12s} blocked : {fmt_ci(len(t['blocked']), n)}"
              f"   (via FLAG {len(t['by_flag'])}, via fail-closed only {len(t['by_fc'])})")
        n = tables["baseline"]["n_scored"]
        base_ids = {u["merge_id"] for u in tables["baseline"]["blocked"]}
        exp_ids = {u["merge_id"] for u in tables["experimental"]["blocked"]}
        added = sorted(exp_ids - base_ids)
        lost = sorted(base_ids - exp_ids)
        p(f"  added blocked (experimental-only units): {fmt_ci(len(added), n)}")
        base_flag_ids = {u["merge_id"] for u in tables["baseline"]["by_flag"]}
        exp_flag_ids = {u["merge_id"] for u in tables["experimental"]["by_flag"]}
        p(f"  added FLAG-blocked (experimental-only): "
          f"{fmt_ci(len(exp_flag_ids - base_flag_ids), n)}")
        if lost:
            p(f"  *** NESTEDNESS VIOLATIONS (baseline-only blocked): {lost} — investigate")
        deltas[pop] = {"added": added, "lost": lost}
        for u in sorted(r["units"], key=lambda x: x["merge_id"]):
            a = u["arm"]["experimental"]
            if a["status"] == "BLOCKED":
                tag = "+NEW" if u["merge_id"] in deltas[pop]["added"] else "    "
                lanes = sorted(set(ln for _, ln in a["flag_lanes"]))
                p(f"    {tag} BLOCKED[exp] {u['merge_id']} "
                  f"({a['block_reason']}; lanes {lanes if lanes else '-'})")
        p("")

    # per-lane attribution, file-level FLAG rows (descriptive)
    p("## File-level FLAG rows by arm × lane (attribution descriptive; "
      "unit blocking is any-lane)")
    per_lane: Counter = Counter()
    for pop, r in results.items():
        for u in r["units"]:
            for arm in ("baseline", "experimental"):
                for fid, lane in u["arm"][arm]["flag_lanes"]:
                    lrec = u["files"][fid]["lanes"]
                    for lkey, rec in lrec.items():
                        if not lkey.startswith(f"{lane}::") or rec["verdict"] != "FLAG":
                            continue
                        if lane == "JoernUnresolvedReference":
                            seg = lkey.split("::")[1]
                            if (seg == "flag0") != (arm == "baseline"):
                                continue
                            wid = any(i["message"].startswith(WIDENED_STEM)
                                      for i in rec["issues"]
                                      if classify_issue(i["message"]) == "genuine")
                            joern = any(i["message"].startswith("Unresolved identifier '")
                                        for i in rec["issues"])
                            if wid:
                                per_lane[(pop, arm, f"{lane} [D3-widened]")] += 1
                            if joern:
                                per_lane[(pop, arm, f"{lane} [Joern]")] += 1
                        else:
                            per_lane[(pop, arm, lane)] += 1
    for (pop, arm, lane), k in sorted(per_lane.items()):
        p(f"  {pop:11s} {arm:12s} {lane:45s} {k}")
    p("")

    # per-(lane,flag-state) file breakdown over clean-merged files
    p("## Per-execution breakdown (clean-merged files)")
    p(f"  {'lane::flagstate':45s} {'FLAG':>5} {'UNANALYZ':>9} {'CLEAN':>6} "
      f"{'mean_rt_s':>10} {'median_rt_s':>12}")
    for lane, flagseg in EXECS_BOTH_ARMS:
        recs = []
        for r in results.values():
            for u in r["units"]:
                for frow in u["files"].values():
                    rec = frow.get("lanes", {}).get(f"{lane}::{flagseg}")
                    if rec:
                        recs.append(rec)
        if not recs:
            continue
        cnt = Counter(r["verdict"] for r in recs)
        rts = [r["runtime_s"] for r in recs]
        p(f"  {lane + '::' + flagseg:45s} {cnt['FLAG']:>5} {cnt['UNANALYZABLE']:>9} "
          f"{cnt['CLEAN']:>6} {statistics.mean(rts):>10.1f} "
          f"{statistics.median(rts):>12.1f}")
    p("")

    # taxonomy-split context on the positives (labeled, no S-D5 numbers)
    r = results.get("stagec_pos")
    if r:
        splits = split_assignment()
        p("## Context: taxonomy-split membership of the 164 scored positives")
        p("   (the experimental lanes were DESIGNED on derivation-split units —")
        p("   the derivation row is tuning-tainted for the experimental arm;")
        p("   membership is a corpus fact, no held-out numbers are imported)")
        for split in ("derivation", "heldout"):
            rows = [u for u in r["units"]
                    if splits.get(u["merge_id"]) == split
                    and u["arm"]["baseline"]["status"] != "ALL_DIVERGED"]
            if not rows:
                continue
            cells = " | ".join(
                f"{arm} blocked {fmt_ci(sum(1 for u in rows if u['arm'][arm]['status'] == 'BLOCKED'), len(rows))}"
                for arm in ("baseline", "experimental"))
            p(f"  {split:11s} ({len(rows):3d} units): {cells}")
        unsplit = [u for u in r["units"] if u["merge_id"] not in splits]
        if unsplit:
            p(f"  (unassigned merges: {[u['merge_id'] for u in unsplit]})")
        p("")

    # control-flag surfacing (gates NOTHING automatically — Ali package rule)
    r = results.get("stagec_ctl")
    if r:
        ctl_flags = [u for u in r["units"]
                     if u["arm"]["experimental"]["status"] == "BLOCKED"]
        p(f"## Experimental-arm control blocks (gate NOTHING automatically; any "
          f"FLAG goes to Ali with a package): {len(ctl_flags)}")
        for u in ctl_flags:
            a = u["arm"]["experimental"]
            p(f"  {u['merge_id']} ({a['block_reason']})")
            for fid, lane in a["flag_lanes"]:
                for lkey, rec in u["files"][fid]["lanes"].items():
                    if lkey.startswith(f"{lane}::") and rec["verdict"] == "FLAG":
                        for iss in rec["issues"]:
                            p(f"      {fid[:70]} {lane} L{iss['line']}: "
                              f"{iss['message'][:110]}")
        p("")

    text = "\n".join(lines)
    (out_dir / "summary.txt").write_text(text + "\n")

    # machine-readable artifacts
    flags = []
    for pop, r in results.items():
        for u in r["units"]:
            for arm in ("baseline", "experimental"):
                if u["arm"][arm]["status"] == "BLOCKED":
                    flags.append({
                        "population": pop, "merge_id": u["merge_id"], "arm": arm,
                        "block_reason": u["arm"][arm]["block_reason"],
                        "flag_lanes": u["arm"][arm]["flag_lanes"],
                        "files": u["files"]})
    (out_dir / "flags.json").write_text(json.dumps(flags, indent=1))
    drift = [d for r in results.values() for d in r["drift"]]
    if drift:
        (out_dir / "classifier_drift.json").write_text(json.dumps(drift, indent=1))
    missing = [m for r in results.values() for m in r["missing"]]
    if missing:
        (out_dir / "missing_keys.json").write_text(json.dumps(missing, indent=1))
    for pop, r in results.items():
        with open(out_dir / f"units_{pop}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["merge_id", "n_files", "n_diverged",
                        "baseline_status", "baseline_reason",
                        "experimental_status", "experimental_reason",
                        "experimental_flag_lanes"])
            for u in sorted(r["units"], key=lambda x: x["merge_id"]):
                w.writerow([
                    u["merge_id"], u["n_files"], u["n_diverged"],
                    u["arm"]["baseline"]["status"],
                    u["arm"]["baseline"]["block_reason"] or "",
                    u["arm"]["experimental"]["status"],
                    u["arm"]["experimental"]["block_reason"] or "",
                    ";".join(sorted(set(l for _, l in
                                        u["arm"]["experimental"]["flag_lanes"])))])
    return text


# --------------------------------------------------------------------------- #
# optional S-D5 raw-verdict consistency cross-check (separate file, no numbers
# feed summary.txt — environment consistency only, never a blended figure)
# --------------------------------------------------------------------------- #
def crosscheck_sd5(out_dir: Path, commit: str) -> None:
    sd5: dict = {}
    for f in sorted(SD5_EVAL.glob("eval_cache_heldout*.json")) + \
             sorted(SD5_EVAL.glob("eval_cache_derivation*.json")):
        sd5.update(json.loads(f.read_text()))
    if not sd5:
        print("crosscheck: no S-D5 eval caches present locally — skipped")
        return
    cache, _ = load_caches(out_dir, "stagec_pos")
    same = diff = 0
    diffs = []
    for k, mine in cache.items():
        if "::__merge__::" in k:
            ref = sd5.get(k)
            if ref is not None:
                if ref["outcome"] == mine["outcome"]:
                    same += 1
                else:
                    diff += 1
                    diffs.append({"key": k, "mine": mine["outcome"],
                                  "ref": ref["outcome"]})
            continue
        ref = sd5.get(k)
        if ref is None:
            continue
        mv, _d = verdict_from_issues(mine["issues"])
        rv, _d = verdict_from_issues(ref["issues"])
        if mv == rv:
            same += 1
        else:
            diff += 1
            diffs.append({"key": k, "mine": mv, "ref": rv})
    out = {"overlapping_keys_agree": same, "disagree": diff, "rows": diffs}
    (out_dir / "crosscheck_sd5.json").write_text(json.dumps(out, indent=1))
    print(f"crosscheck vs S-D5 caches: {same} agree / {diff} disagree "
          f"→ crosscheck_sd5.json")


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--population", choices=sorted(POPULATIONS))
    ap.add_argument("--worker", type=int, default=0, help="work-queue worker id")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--known-answer", type=int, default=0, metavar="N",
                    help="tune_d3 env validation on N merges (S-D5 gate)")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop this worker after N claimed merges (pilot use)")
    ap.add_argument("--requeue-stale", action="store_true")
    ap.add_argument("--crosscheck-sd5", action="store_true")
    args = ap.parse_args()

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    commit = assert_frozen_commit()
    assert_flag_free_lanes()

    if args.requeue_stale:
        requeue_stale(out_dir)
        return
    if args.score:
        results = {}
        for pop in POPULATIONS:
            r = score_population(pop, out_dir, commit)
            if r:
                results[pop] = r
        if not results:
            sys.exit("ABORT: no caches found to score.")
        gate = known_answer_vs_postfix2(results, out_dir, commit)
        text = write_reports(out_dir, commit, results, gate)
        print(text)
        return
    if args.crosscheck_sd5:
        crosscheck_sd5(out_dir, commit)
        return
    if args.smoke:
        preflight()
        run_smokes(EXECS_BOTH_ARMS)
        print("smoke gate PASS (all lane × flag-state executions fire)")
        return
    if args.known_answer:
        preflight()
        run_smokes(EXECS_BOTH_ARMS)
        run_known_answer(args.known_answer, commit)
        return
    if not args.population:
        sys.exit("choose --population/--smoke/--known-answer/--score/"
                 "--requeue-stale/--crosscheck-sd5")
    preflight()
    run_population_queue(args.population, out_dir, commit, args.worker,
                         args.limit)


if __name__ == "__main__":
    main()
