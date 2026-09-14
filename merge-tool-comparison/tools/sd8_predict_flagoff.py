"""S-D8 — pre-registered per-file prediction of the flag-OFF arm @ HEAD.

The S-D8 env gate (ratified by Ali 2026-07-22, replacing the kickoff's
literal-1779 wording): the measured driver-auto flag-OFF arm at the frozen
suite HEAD must match THIS table file-for-file, with every difference
attributable to the #29 post-fix commits (5ed92a2 + f964354) or the known
2/471 textual<->semantic nondeterminism margin (datastax 725b790a79,
graphity 2a8e8c75e9 — cost-identical either way).

Derivation (committed artifacts only, run BEFORE the AWS cycle):
  - P3 post-flip measured run @ 9e25b4e:  reports_whole_driver/raw_results.json
    (routes) + postflip_scenarios.csv (per-file outcome + classification)
  - post-fix known answers @ f964354 (== frozen HEAD default lanes) on
    Mergiraf outputs: reports_detection/postfix2/scenarios.csv
  - Mergiraf-routed files reuse postfix2 verdicts directly (identical merged
    content); git-routed files carry the P3 result (the fixes only remove
    flag patterns; any git-routed semantic reject is listed for local
    pre-launch verification at HEAD).

Output: reports_detectors/whole_driver_flagon/predicted_flagoff.csv + .md
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

P3_CACHE = ROOT / "reports_whole_driver" / "raw_results.json"
P3_CSV = ROOT / "reports_whole_driver" / "postflip_scenarios.csv"
PF2_CSV = ROOT / "reports_detection" / "postfix2" / "scenarios.csv"
OUT_DIR = ROOT / "reports_detectors" / "whole_driver_flagon"

P3_COMMIT = "9e25b4e"
FIX_COMMITS = "5ed92a2+f964354"
# The two files P2/P3 FINDINGS §7(d) records as textual<->semantic borderline.
BORDERLINE = {
    "datastax_java-driver__725b790a79__driver-core_src_main_java_com_datastax_driver_core_Cluster.java",
    "graphity_graphity-client__2a8e8c75e9__src_main_java_org_graphity_util_XSLTBuilder.java",
}

COST = {"TP": 0, "FP": 10, "TN": 1, "FN": 1, "CRASH": 1, "TIMEOUT": 1}


def main() -> None:
    p3_rows = [r for r in csv.DictReader(open(P3_CSV)) if r["config"] == "driver-auto"]
    cache = json.loads(P3_CACHE.read_text())
    routes = {}
    for k, v in cache.items():
        parts = k.split("::")
        if parts[0] == "driver-auto" and len(parts) == 3 and parts[2] == P3_COMMIT:
            route = v.get("route") or {}
            routes[parts[1]] = route.get("effective", "unknown")
    pf2 = {r["scenario_id"]: r for r in csv.DictReader(open(PF2_CSV))}

    out_rows: list[dict] = []
    verify_local: list[str] = []
    changed: list[dict] = []
    for r in p3_rows:
        sid = r["scenario_id"]
        route = routes.get(sid, "unknown")
        p3_outcome, p3_reason, p3_cls = r["outcome"], r["reject_reason"], r["classification"]
        pred_outcome, pred_reason, pred_cls = p3_outcome, p3_reason, p3_cls
        basis = "unchanged"

        pf = pf2.get(sid)
        if route == "mergiraf" and pf is not None:
            if pf["merge_outcome"] != "clean":
                pred_outcome, pred_reason = "conflict", "textual"
                # backend conflict is deterministic; cls unchanged (both reject paths
                # score dev-match on a conflict) — cost identical.
                if p3_outcome != "conflict":
                    basis = "postfix2-divergence-MISMATCH"  # should not happen
            elif pf["file_verdict"] == "FLAG":
                pred_outcome, pred_reason = "conflict", "semantic"
                if p3_reason != "semantic":
                    basis = "postfix2-new-flag-MISMATCH"    # should not happen
            elif pf["file_verdict"] == "CLEAN" and p3_reason == "semantic":
                # flag present @ 9e25b4e, absent @ f964354 → the post-fix delta
                pred_outcome, pred_reason = "clean", ""
                pred_cls = "FP" if r["arm"] == "pos" else "TP"  # hybrid: output == mergiraf ref
                basis = f"postfix2-fix ({FIX_COMMITS})"
        elif route != "mergiraf" and p3_reason == "semantic":
            verify_local.append(sid)
            basis = "git-routed-flag (verify locally pre-launch)"

        if sid in BORDERLINE:
            basis += " | borderline-margin (textual<->semantic, cost-identical)"

        if (pred_outcome, pred_reason) != (p3_outcome, p3_reason):
            changed.append({"arm": r["arm"], "sid": sid, "from": f"{p3_outcome}/{p3_reason}/{p3_cls}",
                            "to": f"{pred_outcome}/{pred_reason}/{pred_cls}", "basis": basis})
        out_rows.append({
            "arm": r["arm"], "merge_id": r["merge_id"], "scenario_id": sid,
            "route_p3": route, "p3_outcome": p3_outcome, "p3_reject_reason": p3_reason,
            "p3_classification": p3_cls, "predicted_outcome": pred_outcome,
            "predicted_reject_reason": pred_reason, "predicted_classification": pred_cls,
            "basis": basis,
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "predicted_flagoff.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    def cost_of(rows: list[dict], key: str) -> int:
        return sum(COST[r[key]] for r in rows)

    p3_cost = cost_of(out_rows, "p3_classification")
    pred_cost = cost_of(out_rows, "predicted_classification")
    by_arm = {arm: [r for r in out_rows if r["arm"] == arm] for arm in ("pos", "ctl")}

    lines = [
        "# S-D8 pre-registered flag-OFF prediction (env-gate reference)",
        "",
        f"Derived from the committed P3 post-flip run @ `{P3_COMMIT}` plus the",
        f"post-fix known answers @ `f964354` (reports_detection/postfix2/) — the",
        "frozen-suite HEAD's default lanes. Committed BEFORE the S-D8 AWS cycle.",
        "",
        f"- files: {len(out_rows)} (pos {len(by_arm['pos'])} / ctl {len(by_arm['ctl'])})",
        f"- P3 measured pooled cost @ {P3_COMMIT}: **{p3_cost}**",
        f"- predicted flag-OFF pooled cost @ HEAD: **{pred_cost}**"
        f"  (pos {cost_of(by_arm['pos'], 'predicted_classification')}"
        f" / ctl {cost_of(by_arm['ctl'], 'predicted_classification')})",
        f"- predicted changes vs P3: {len(changed)}",
        "",
        "| arm | scenario | P3 → predicted | basis |",
        "|---|---|---|---|",
    ]
    for c in changed:
        lines.append(f"| {c['arm']} | {c['sid'][:60]} | {c['from']} → {c['to']} | {c['basis']} |")
    lines += [
        "",
        "Gate at scoring time: every measured flag-OFF file must match",
        "`predicted_outcome`/`predicted_reject_reason` (reject-reason flips inside",
        "the borderline-margin rows are allowed — cost-identical); any other",
        "difference fails the gate unless attributable to the fix commits with a",
        "written per-file rationale.",
    ]
    if verify_local:
        lines += ["", "Git-routed semantic flags needing local pre-launch verification @ HEAD:"]
        lines += [f"- {s}" for s in verify_local]
    (OUT_DIR / "predicted_flagoff.md").write_text("\n".join(lines) + "\n")

    print(f"rows={len(out_rows)} p3_cost={p3_cost} predicted_cost={pred_cost}")
    print(f"changed={len(changed)} verify_local={len(verify_local)}")
    for c in changed:
        print(f"  {c['arm']} {c['sid'][:64]} {c['from']} -> {c['to']}  [{c['basis']}]")
    mism = [c for c in changed if "MISMATCH" in c["basis"]]
    print("route distribution:", dict(Counter(r["route_p3"] for r in out_rows)))
    if mism:
        raise SystemExit(f"ABORT: {len(mism)} inconsistent predictions — investigate before launch")


if __name__ == "__main__":
    main()
