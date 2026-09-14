"""S-D8 — whole-driver re-pricing with the experimental detector lanes ON.

P2-style (tools/whole_driver_eval.py — imported, not modified) over the P1
corpus, one config pair that differs ONLY by SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS:

    driver-auto-off   auto routing + default 5-lane detection (flag unset)
    driver-auto-on    auto routing + full 7-lane suite (flag=1: D1 ImportPruneUsage,
                      D2 SignatureStaleCall, D3 widened JoernUnresolvedReference)

Both arms run at the frozen suite commit (reports_detectors/manifest.json
detector_suite_commit = 732d8ff; no driver-code commits after it).

ENV GATE (ratified by Ali 2026-07-22, replacing the kickoff's literal-1779
wording): the measured driver-auto-off arm must match the pre-registered
per-file prediction reports_detectors/whole_driver_flagon/predicted_flagoff.csv
(tools/sd8_predict_flagoff.py — P3 cache + postfix2 known answers; predicted
pooled cost 1784 = 1779 + tcurdt retirement − 4 ctl var-lane fixes).
`--check-gate` performs the reconciliation and exits non-zero on FAIL so the
orchestrator can abort before the flag-on arm burns.

Latency is a FIRST-CLASS result (the enabling-decision price): per-arm
medians plus the paired per-file delta (on − off), split by route and arm.

Usage (on-instance, DRIVER_COMMIT required under git-archive):
    .venv/bin/python tools/whole_driver_flagon.py --configs driver-auto-off
    .venv/bin/python tools/whole_driver_flagon.py --check-gate
    .venv/bin/python tools/whole_driver_flagon.py --configs driver-auto-on
    .venv/bin/python tools/whole_driver_flagon.py --report-only
Smoke:
    .venv/bin/python tools/whole_driver_flagon.py --limit 2
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from whole_driver_eval import (  # noqa: E402
    DRIVER_PY, DRIVER_TIMEOUT_S, SPECIALIST_ROUTING_ENV, _parse_route,
    _reject_reason, load_stage_c, metrics_for, per_merge_three_outcome, preflight,
    score,
)
from detect_validate import (  # noqa: E402
    driver_commit, group_by_merge, load_scenarios, merge_id_of,
)

FLAG_ENV = "SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"
CONFIGS = ["driver-auto-off", "driver-auto-on"]
FLAG_ON = {"driver-auto-off": False, "driver-auto-on": True}

DEFAULT_POS = "data/scenarios_semantic"
DEFAULT_CTL = "data/scenarios_semantic_ctl"
DEFAULT_OUT = "reports_detectors/whole_driver_flagon"
PREDICTED_CSV = "predicted_flagoff.csv"

_FLAG_LINE_RE = re.compile(r"^\[(\w+)\] (\w+): (.*) at line (\S+)$", re.MULTILINE)

COST = {"TP": 0, "FP": 10, "TN": 1, "FN": 1, "CRASH": 1, "TIMEOUT": 1}


def run_driver_flag(scn: dict, flag_on: bool) -> dict:
    """whole_driver_eval.run_driver with explicit flag control + lane capture.

    The flag is set/unset EXPLICITLY per call so an operator-exported value
    can never leak into the wrong arm.
    """
    ext = Path(scn["file_path"]).suffix or ".java"
    t0 = time.monotonic()
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / f"base{ext}"
        cur = Path(td) / f"cur{ext}"
        oth = Path(td) / f"oth{ext}"
        base.write_text(scn["base_content"], encoding="utf-8")
        cur.write_text(scn["ours_content"], encoding="utf-8")
        oth.write_text(scn["theirs_content"], encoding="utf-8")
        env = {**os.environ, "SEMANTIC_MERGE_BACKEND": "auto"}
        env.pop(FLAG_ENV, None)
        if flag_on:
            env[FLAG_ENV] = "1"
        try:
            proc = subprocess.run(
                [sys.executable, str(DRIVER_PY), str(base), str(cur), str(oth)],
                capture_output=True, text=True, env=env, timeout=DRIVER_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            return {"outcome": "timeout", "merged": None, "reject_reason": "timeout",
                    "rt": round(time.monotonic() - t0, 3), "rc": -1, "flags": []}
        rc = proc.returncode
        out = proc.stdout + "\n" + proc.stderr
        merged = cur.read_text(encoding="utf-8", errors="replace")
    rt = round(time.monotonic() - t0, 3)
    route = _parse_route(out)
    flags = [f"{m.group(2)} L{m.group(4)}: {m.group(3)[:100]}"
             for m in _FLAG_LINE_RE.finditer(out)]
    lanes = sorted({m.group(2) for m in _FLAG_LINE_RE.finditer(out)})
    if rc == 0:
        return {"outcome": "clean", "merged": merged, "reject_reason": None,
                "rt": rt, "rc": 0, "route": route, "flags": flags, "lanes": lanes}
    reason = _reject_reason(out)
    outcome = "conflict" if reason in ("textual", "semantic") else "crash"
    return {"outcome": outcome, "merged": None, "reject_reason": reason,
            "rt": rt, "rc": rc, "route": route, "flags": flags, "lanes": lanes}


# --------------------------------------------------------------------------- #
# corpus + cache plumbing
# --------------------------------------------------------------------------- #
def load_work(pos_dir: str, ctl_dir: str, limit: int) -> list[tuple[str, dict]]:
    pos = load_scenarios(ROOT / pos_dir)
    ctl = load_scenarios(ROOT / ctl_dir)
    work: list[tuple[str, dict]] = []
    for arm, scns in (("pos", pos), ("ctl", ctl)):
        groups = group_by_merge(scns)
        mids = sorted(groups)
        if limit:
            mids = mids[:limit]
        for mid in mids:
            for scn in groups[mid]:
                work.append((arm, scn))
    return work


def resolve_commit() -> str:
    commit = os.environ.get("DRIVER_COMMIT") or driver_commit()
    if commit == "unknown":
        sys.exit("ABORT: driver commit unresolved (no .git?) — set DRIVER_COMMIT "
                 "(S-D8 convention: the manifest's detector_suite_commit).")
    return commit


def scored_records(cfg: str, work: list[tuple[str, dict]], cache: dict,
                   sc: dict, commit: str) -> list[dict] | None:
    """Score cached results for one config; None if any file is missing."""
    recs = []
    for arm, scn in work:
        sid = scn["scenario_id"]
        res = cache.get(f"{cfg}::{sid}::{commit}")
        if res is None:
            return None
        ref = sc.get(sid, {}).get("ref_merged")
        cls, oracle = score(arm, res, scn, ref)
        recs.append({
            "arm": arm, "merge_id": merge_id_of(scn), "scenario_id": sid,
            "outcome": res["outcome"], "reject_reason": res.get("reject_reason"),
            "cls": cls, "oracle": oracle, "rt": res.get("rt", 0.0),
            "route": res.get("route"), "lanes": res.get("lanes", []),
            "flags": res.get("flags", []),
        })
    return recs


# --------------------------------------------------------------------------- #
# env gate: reconcile driver-auto-off against the pre-registered prediction
# --------------------------------------------------------------------------- #
def check_gate(out_dir: Path, work: list[tuple[str, dict]], cache: dict,
               sc: dict, commit: str) -> bool:
    pred_path = out_dir / PREDICTED_CSV
    if not pred_path.exists():
        sys.exit(f"ABORT: {pred_path} missing — the pre-registered prediction "
                 "must be committed before the run.")
    pred = {r["scenario_id"]: r for r in csv.DictReader(open(pred_path))}
    recs = scored_records("driver-auto-off", work, cache, sc, commit)
    if recs is None:
        sys.exit("ABORT: driver-auto-off arm incomplete — cannot gate yet.")
    lines = [f"# S-D8 env gate — driver-auto-off @ {commit} vs pre-registered prediction",
             f"# files compared: {len(recs)}"]
    failures, margin_ok, fix_ok = [], [], []
    cost = 0
    for r in recs:
        cost += COST[r["cls"].value]
        p = pred.get(r["scenario_id"])
        if p is None:
            failures.append(f"UNPREDICTED {r['arm']} {r['scenario_id']}")
            continue
        got = (r["outcome"], r["reject_reason"] or "")
        want = (p["predicted_outcome"], p["predicted_reject_reason"])
        if got == want:
            if "postfix2-fix" in p["basis"]:
                fix_ok.append(r["scenario_id"])
            continue
        borderline = "borderline-margin" in p["basis"]
        both_reject = got[0] == "conflict" == want[0] and \
            {got[1], want[1]} <= {"textual", "semantic"}
        if borderline and both_reject:
            margin_ok.append(f"{r['scenario_id']} ({want[1]} -> {got[1]}, cost-identical)")
            continue
        failures.append(f"MISMATCH {r['arm']} {r['scenario_id']}: "
                        f"predicted {want[0]}/{want[1]} got {got[0]}/{got[1]}")
    measured_sids = {r["scenario_id"] for r in recs}
    pred_cost = sum(COST[p["predicted_classification"]] for p in pred.values()
                    if p["scenario_id"] in measured_sids)
    n_fix_expected = sum(1 for p in pred.values()
                         if p["scenario_id"] in measured_sids and "postfix2-fix" in p["basis"])
    lines.append(f"measured pooled cost: {cost}   predicted: {pred_cost}")
    lines.append(f"post-fix deltas confirmed: {len(fix_ok)}/{n_fix_expected} expected "
                 "(full corpus: tcurdt + aerospike + cloudfoundry x2 + mtedone)")
    for m in margin_ok:
        lines.append(f"  margin-ok: {m}")
    for f in failures:
        lines.append(f"  {f}")
    if cost != pred_cost:
        lines.append(f"  COST MISMATCH: measured {cost} != predicted {pred_cost} "
                     "(a same-outcome file scored differently — investigate)")
    ok = not failures and cost == pred_cost
    lines.append(f"ENV GATE: {'PASS' if ok else 'FAIL'}")
    (out_dir / "env_gate.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return ok


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #
def pctl(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    return s[min(len(s) - 1, int(q * len(s)))]


def write_reports(out_dir: Path, scored: dict[str, list[dict]], commit: str) -> str:
    lines: list[str] = []
    p = lines.append
    p("# S-D8 — whole-driver re-pricing, experimental lanes ON (config pair)")
    p(f"# driver commit {commit} (frozen suite); corpus = P1 164 pos / 193 ctl")
    p("# arms differ ONLY by SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS")
    p("# cost unit = per file (Schesch); FP x10, TN/FN x1, CRASH/TIMEOUT x1; hybrid oracle")
    p("")

    for arm_label, arm in (("positives (Tests_failed)", "pos"),
                           ("controls (Tests_passed)", "ctl"), ("POOLED", None)):
        p(f"## Cost-model table — {arm_label}")
        p(f"  {'config':16s} {'n':>4} {'TP':>4} {'FP':>4} {'TN':>4} {'FN':>4} "
          f"{'CR':>3} {'cost':>7} {'cost/n':>7} {'med_rt':>7}")
        for cfg in CONFIGS:
            recs = scored.get(cfg)
            if not recs:
                continue
            sel = [r for r in recs if (arm is None or r["arm"] == arm)]
            m = metrics_for(sel)
            cost = m.weighted_cost()
            rts = [r["rt"] for r in sel if r["rt"] > 0]
            p(f"  {cfg:16s} {m.scenario_count:>4} {m.tp:>4} {m.fp:>4} {m.tn:>4} "
              f"{m.fn:>4} {m.crashes + m.timeouts:>3} {cost:>7.0f} "
              f"{cost / max(1, m.scenario_count):>7.2f} "
              f"{statistics.median(rts) if rts else 0:>7.1f}")
        p("")

    p("## Three-outcome decomposition (per merge, any-file)")
    p(f"  {'config':16s} {'arm':>4} {'merges':>6} {'accept':>7} {'textual':>8} "
      f"{'semantic':>9} {'crash':>6}")
    for cfg in CONFIGS:
        recs = scored.get(cfg)
        if not recs:
            continue
        for arm in ("pos", "ctl"):
            three = per_merge_three_outcome([r for r in recs if r["arm"] == arm])
            c = Counter(three.values())
            p(f"  {cfg:16s} {arm:>4} {len(three):>6} {c['accept']:>7} "
              f"{c['textual']:>8} {c['semantic']:>9} {c['crash']:>6}")
    p("")

    off, on = scored.get("driver-auto-off"), scored.get("driver-auto-on")
    if off and on:
        off_by = {(r["arm"], r["scenario_id"]): r for r in off}
        moved: dict[str, list[dict]] = defaultdict(list)
        d_off = metrics_for(off).weighted_cost()
        d_on = metrics_for(on).weighted_cost()
        for r in on:
            b = off_by.get((r["arm"], r["scenario_id"]))
            if not b:
                continue
            if (b["outcome"], b["reject_reason"]) == (r["outcome"], r["reject_reason"]):
                continue
            key = (f"{b['outcome']}/{b['reject_reason'] or 'accept'}"
                   f" -> {r['outcome']}/{r['reject_reason'] or 'accept'}"
                   f" [{b['cls'].value}->{r['cls'].value}]")
            moved[key].append(r)
        p("## Flag delta — per-file movements off -> on (blocked/broken decomposition)")
        p(f"  pooled weighted cost: off {d_off:.0f} -> on {d_on:.0f} "
          f"(delta {d_on - d_off:+.0f})")
        if not moved:
            p("  (no per-file movements)")
        for key in sorted(moved):
            rows = moved[key]
            p(f"  {key}: {len(rows)}")
            for r in rows:
                lanes = ",".join(r["lanes"]) or "-"
                p(f"    [{r['arm']}] {r['scenario_id'][:64]:64s} lanes={lanes}")
        p("")
        p("## Lane fire counts (on-arm, per file with >=1 flag)")
        lane_counts = Counter(l for r in on for l in r["lanes"])
        for lane, n in lane_counts.most_common():
            p(f"  {lane:28s} {n:>4}")
        p("")
        p("## Latency (FIRST-CLASS — the enabling-decision price; seconds/file)")
        p(f"  {'slice':28s} {'n':>4} {'off_med':>8} {'on_med':>8} "
          f"{'d_med':>7} {'d_mean':>7} {'d_p90':>7}")
        pairs_all: list[tuple[dict, dict]] = []
        for r in on:
            b = off_by.get((r["arm"], r["scenario_id"]))
            if b and b["rt"] > 0 and r["rt"] > 0:
                pairs_all.append((b, r))

        def lat_row(label: str, pairs: list[tuple[dict, dict]]) -> None:
            if not pairs:
                return
            offs = [b["rt"] for b, _ in pairs]
            ons = [r["rt"] for _, r in pairs]
            ds = [r["rt"] - b["rt"] for b, r in pairs]
            p(f"  {label:28s} {len(pairs):>4} {statistics.median(offs):>8.1f} "
              f"{statistics.median(ons):>8.1f} {statistics.median(ds):>7.1f} "
              f"{statistics.mean(ds):>7.1f} {pctl(ds, 0.9):>7.1f}")

        lat_row("all files (paired)", pairs_all)
        for arm in ("pos", "ctl"):
            lat_row(f"arm={arm}", [(b, r) for b, r in pairs_all if r["arm"] == arm])
        for route in ("git", "mergiraf"):
            lat_row(f"route={route}",
                    [(b, r) for b, r in pairs_all
                     if (r.get("route") or {}).get("effective") == route])
        lat_row("on-arm flagged files",
                [(b, r) for b, r in pairs_all if r["lanes"]])
        p("")

    text = "\n".join(lines)
    (out_dir / "summary.txt").write_text(text + "\n")
    with open(out_dir / "scenarios.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["config", "arm", "merge_id", "scenario_id", "outcome",
                    "reject_reason", "classification", "oracle", "rt",
                    "route_effective", "lanes", "flags"])
        for cfg in CONFIGS:
            for r in scored.get(cfg) or []:
                w.writerow([cfg, r["arm"], r["merge_id"], r["scenario_id"],
                            r["outcome"], r["reject_reason"] or "", r["cls"].value,
                            r["oracle"], r["rt"],
                            (r.get("route") or {}).get("effective", ""),
                            ";".join(r["lanes"]), " | ".join(r["flags"])[:500]])
    return text


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pos_dir", nargs="?", default=DEFAULT_POS)
    ap.add_argument("ctl_dir", nargs="?", default=DEFAULT_CTL)
    ap.add_argument("--configs", default=",".join(CONFIGS))
    ap.add_argument("--limit", type=int, default=0, help="smoke: first N merges/arm")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--check-gate", action="store_true",
                    help="reconcile driver-auto-off vs predicted_flagoff.csv; exit 2 on FAIL")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    bad = [c for c in configs if c not in CONFIGS]
    if bad:
        sys.exit(f"ABORT: unknown config(s) {bad}; choose from {CONFIGS}")
    if os.environ.get(SPECIALIST_ROUTING_ENV) == "1":
        sys.exit(f"ABORT: {SPECIALIST_ROUTING_ENV}=1 is set — S-D8 measures the "
                 "post-flip default map; unset it.")
    if os.environ.get(FLAG_ENV):
        sys.exit(f"ABORT: {FLAG_ENV} is exported globally — the harness controls "
                 "it per-arm; unset it.")

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = out_dir / "raw_results.json"
    cache: dict = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    commit = resolve_commit()
    sc = load_stage_c()
    work = load_work(args.pos_dir, args.ctl_dir, args.limit)
    print(f"driver_commit={commit} configs={configs} files={len(work)} out={out_dir}",
          flush=True)

    if args.check_gate:
        sys.exit(0 if check_gate(out_dir, work, cache, sc, commit) else 2)

    if not args.report_only:
        preflight(["driver-auto"])
        n_total = len(work) * len(configs)
        done = 0
        for cfg in configs:
            for arm, scn in work:
                sid = scn["scenario_id"]
                key = f"{cfg}::{sid}::{commit}"
                if key not in cache:
                    cache[key] = run_driver_flag(scn, FLAG_ON[cfg])
                    cache_path.write_text(json.dumps(cache))
                res = cache[key]
                done += 1
                print(f"  [{cfg} {done}/{n_total}] {sid[:52]:52s} {res['outcome']:8s} "
                      f"{res.get('reject_reason') or '':9s} "
                      f"lanes={','.join(res.get('lanes', [])) or '-'} "
                      f"({res.get('rt', 0):.0f}s)", flush=True)

    scored = {}
    for cfg in CONFIGS:
        recs = scored_records(cfg, work, cache, sc, commit)
        if recs is not None:
            scored[cfg] = recs
        else:
            print(f"  ({cfg}: incomplete — omitted from report)", flush=True)
    text = write_reports(out_dir, scored, commit)
    print("\n" + text)
    print(f"\nWrote {out_dir}/summary.txt, scenarios.csv, raw_results.json")


if __name__ == "__main__":
    main()
