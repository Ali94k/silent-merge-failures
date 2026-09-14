"""P2 — whole-driver end-to-end cost-model evaluation.

Scores the *whole* semantic_merge_driver (backend + detection + accept/reject),
not just the detectors, against the Schesch cost model on the P1 corpus
(164 positives = mergiraf clean-but-Tests_failed, 193 controls = Tests_passed).
Five configs:

    bare-git        git-merge-file backend only   (native, no Docker)
    bare-mergiraf   mergiraf backend only         (reused from Stage C — no Docker)
    driver-git      git backend + detection       (subprocess core/driver.py; Joern+RM2)
    driver-mergiraf mergiraf backend + detection   (reused from Stage C — no Docker)
    driver-auto     auto routing + detection       (subprocess; Joern+RM2+mergiraf;
                    post-flip default NONE→git else→Mergiraf — Spork/Weave only
                    under SEMANTIC_MERGE_SPECIALIST_ROUTING=1, the refuted arms)

Plan: outputs/p1-detection-validation-plan.md is P1; this is P2 in
.claude/plans/lexical-tinkering-plum.md. Reuses detect_validate's loaders +
the comparator's classify_result / cost model.

HYBRID ORACLE (decided 2026-06-24): on the CLEAN (accept) branch, if a config's
accepted output equals the Mergiraf reference (contents_match), the Schesch
test label applies — positives = Tests_failed = silent-WRONG = FP (cost x10);
controls = Tests_passed = correct = TP (cost 0). Outputs that diverge from the
Mergiraf reference fall back to dev-match (comparator.classify_result). REJECTs
(textual / semantic / crash) are visible conflicts → cost x1 via the CONFLICT
branch. The Mergiraf reference for every scenario is read from Stage C's cache
(reports_detection/full/raw_results.json) — no re-merge needed.

COST UNIT is per file (the canonical Schesch unit, matching reports/results.csv).
Unlike P1's R1/R2 (which drop file-level-diverged merges), P2 scores a backend
CONFLICT as a real cost-x1 visible outcome — diverged files are NOT dropped.
The Stage-C-compatible per-merge R1/R2 is recomputed separately as a cross-check.

Resumable: per-(config, scenario) results cached in <out>/raw_results.json.
Configs are independent — run the no-Docker three first, the Docker two later;
the report renders whatever is cached.

Usage:
    .venv/bin/python tools/whole_driver_eval.py --configs bare-git,bare-mergiraf,driver-mergiraf
    .venv/bin/python tools/whole_driver_eval.py --configs driver-git,driver-auto
    .venv/bin/python tools/whole_driver_eval.py            # all five
    .venv/bin/python tools/whole_driver_eval.py --limit 5  # smoke run
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # merge-tool-comparison/tools
ROOT = HERE.parent                                     # merge-tool-comparison/
DRIVER_ROOT = ROOT.parent / "semantic_merge_driver"
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(DRIVER_ROOT))
sys.path.insert(2, str(HERE))                          # sibling: detect_validate

from src.core.interfaces import MergeOutcome, MergeResult  # noqa: E402
from src.evaluation.comparator import (  # noqa: E402
    Classification, classify_result, contents_match,
)
from src.evaluation.metrics import ToolMetrics  # noqa: E402
from src.tools.git_merge_file import GitMergeFileTool  # noqa: E402

from detect_validate import (  # noqa: E402  (sibling module in tools/)
    MERGIRAF_IMAGE, RM2_IMAGE, driver_commit, fmt_ci, group_by_merge,
    load_scenarios, merge_id_of, wilson,
)

SPORK_IMAGE = "merge-tools/spork:0.5.0"
WEAVE_IMAGE = "merge-tools/weave:0.3.2"
DRIVER_PY = DRIVER_ROOT / "core" / "driver.py"
DRIVER_TIMEOUT_S = 900

STAGE_C_DIR = ROOT / "reports_detection" / "full"

ALL_CONFIGS = ["bare-git", "bare-mergiraf", "driver-git", "driver-mergiraf", "driver-auto"]
DRIVER_ENV = {"driver-git": "git", "driver-mergiraf": "mergiraf", "driver-auto": "auto"}
# configs that shell out to Joern/Docker (preflight only gates these).
# These execute driver *code*, so their cache keys embed the driver commit —
# a re-run after a driver change recomputes instead of silently serving stale
# results (post-P2-review fix; the P2 run itself used un-suffixed keys and is
# preserved as the committed pre-flip artifact).
DOCKER_CONFIGS = {"driver-git", "driver-auto"}
SPECIALIST_ROUTING_ENV = "SEMANTIC_MERGE_SPECIALIST_ROUTING"  # mirrors auto_backend

DEFAULT_POS = "data/scenarios_semantic"
DEFAULT_CTL = "data/scenarios_semantic_ctl"
DEFAULT_OUT = "reports_whole_driver"

# Stage-C ground truth for the cross-check assertion (FINDINGS.md headline).
STAGE_C_R2 = (12, 164)   # blocked positives / scored
STAGE_C_R1 = (4, 193)    # blocked controls / scored


# --------------------------------------------------------------------------- #
# scoring (hybrid oracle)
# --------------------------------------------------------------------------- #
def _mr(outcome: str, merged: str | None) -> MergeResult:
    om = MergeOutcome(outcome)
    return MergeResult(outcome=om, merged_content=merged,
                       conflict_count=0 if om == MergeOutcome.CLEAN else 1,
                       runtime_seconds=0.0)


def score(arm: str, res: dict, scn: dict, mergiraf_ref: str | None) -> tuple[Classification, str]:
    """(cost-model Classification, oracle_used) for one file under one config.

    Hybrid oracle on the CLEAN branch; dev-match elsewhere.
    """
    outcome = res["outcome"]
    if outcome == "crash":
        return Classification.CRASH, "n/a"
    if outcome == "timeout":
        return Classification.TIMEOUT, "n/a"

    if outcome == "clean":
        merged = res.get("merged")
        if mergiraf_ref is not None and merged is not None and contents_match(merged, mergiraf_ref):
            # accepted output == Mergiraf reference → Schesch test label is truth
            return (Classification.FALSE_POSITIVE if arm == "pos"
                    else Classification.TRUE_POSITIVE), "test-label"
        cls = classify_result(_mr("clean", merged), scn["developer_resolution"],
                              scn["base_content"], scn["ours_content"], scn["theirs_content"])
        return cls, "dev-match"

    # CONFLICT (reject) — visible, cost x1; FN/TN split via dev-match
    cls = classify_result(_mr("conflict", None), scn["developer_resolution"],
                          scn["base_content"], scn["ours_content"], scn["theirs_content"])
    return cls, "dev-match"


# --------------------------------------------------------------------------- #
# backend / driver execution (per file)
# --------------------------------------------------------------------------- #
def run_bare_git(scn: dict) -> dict:
    res = GitMergeFileTool().merge(scn["base_content"], scn["ours_content"],
                                   scn["theirs_content"])
    clean = res.outcome == MergeOutcome.CLEAN
    return {"outcome": res.outcome.value,
            "merged": res.merged_content if clean else None,
            "reject_reason": None if clean else (
                "crash" if res.outcome in (MergeOutcome.CRASH, MergeOutcome.TIMEOUT)
                else "textual"),
            "rt": round(res.runtime_seconds, 3)}


def _reject_reason(out: str) -> str:
    if "crashed; rejecting" in out:
        return "crash"
    if "Semantic Merge Rejected" in out:
        return "semantic"
    if "Textual Merge Conflicts Exist" in out:
        return "textual"
    return "error"


_ROUTE_RE = re.compile(r"AutoBackend: cluster=(\S+) language=(\S+) → (\S+)")
_FALLBACK_RE = re.compile(r"AutoBackend: (\S+) crashed; falling back to (\S+)")


def _parse_route(out: str) -> dict | None:
    """Extract the AutoBackend routing decision from driver stderr (auto only).

    Returns {cluster, language, chosen, fell_back, effective} or None when the
    line is absent (non-auto backends, or auto's own log not emitted).
    """
    m = _ROUTE_RE.search(out)
    if not m:
        return None
    cluster, language, chosen = m.group(1), m.group(2), m.group(3)
    fb = _FALLBACK_RE.search(out)
    return {"cluster": cluster, "language": language, "chosen": chosen,
            "fell_back": bool(fb), "effective": fb.group(2) if fb else chosen}


def run_driver(backend_env: str, scn: dict) -> dict:
    """Invoke core/driver.py as a subprocess on one file, driver-faithful.

    Returns outcome in {clean, conflict, crash, timeout}, the merged content on
    accept (read back from the in-place-mutated `current`), and the reject reason.
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
        env = {**os.environ, "SEMANTIC_MERGE_BACKEND": backend_env}
        try:
            proc = subprocess.run(
                [sys.executable, str(DRIVER_PY), str(base), str(cur), str(oth)],
                capture_output=True, text=True, env=env, timeout=DRIVER_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            return {"outcome": "timeout", "merged": None, "reject_reason": "timeout",
                    "rt": round(time.monotonic() - t0, 3), "rc": -1}
        rc = proc.returncode
        out = proc.stdout + "\n" + proc.stderr
        merged = cur.read_text(encoding="utf-8", errors="replace")
    rt = round(time.monotonic() - t0, 3)
    route = _parse_route(out)  # populated for backend_env == "auto"
    if rc == 0:
        return {"outcome": "clean", "merged": merged, "reject_reason": None,
                "rt": rt, "rc": 0, "route": route}
    reason = _reject_reason(out)
    outcome = "conflict" if reason in ("textual", "semantic") else "crash"
    return {"outcome": outcome, "merged": None, "reject_reason": reason,
            "rt": rt, "rc": rc, "route": route}


# --------------------------------------------------------------------------- #
# Stage-C reuse (bare-mergiraf, driver-mergiraf, the Mergiraf reference)
# --------------------------------------------------------------------------- #
def load_stage_c() -> dict[str, dict]:
    """{scenario_id: {file_verdict, merge_outcome, ref_merged}} from Stage C."""
    csv_path = STAGE_C_DIR / "scenarios.csv"
    cache_path = STAGE_C_DIR / "raw_results.json"
    if not csv_path.exists() or not cache_path.exists():
        sys.exit(f"ABORT: Stage-C artifacts missing under {STAGE_C_DIR} — "
                 "bare-mergiraf / driver-mergiraf / the oracle reference need them.")
    rows = {r["scenario_id"]: r for r in csv.DictReader(open(csv_path))}
    cache = json.loads(cache_path.read_text())
    out = {}
    for sid, r in rows.items():
        ref = cache.get(f"{sid}::__merge__::{MERGIRAF_IMAGE}", {}).get("merged")
        out[sid] = {"file_verdict": r["file_verdict"],
                    "merge_outcome": r["merge_outcome"], "ref_merged": ref}
    return out


def bare_mergiraf_result(scn: dict, sc: dict) -> dict | None:
    rec = sc.get(scn["scenario_id"])
    if rec is None:
        return None
    if rec["merge_outcome"] != "clean":
        return {"outcome": "conflict", "merged": None, "reject_reason": "textual",
                "rt": 0.0, "reused": True}
    return {"outcome": "clean", "merged": rec["ref_merged"], "reject_reason": None,
            "rt": 0.0, "reused": True}


def driver_mergiraf_result(scn: dict, sc: dict) -> dict | None:
    """Assemble the driver-mergiraf accept/reject from Stage C verdicts."""
    rec = sc.get(scn["scenario_id"])
    if rec is None:
        return None
    fv, mo = rec["file_verdict"], rec["merge_outcome"]
    if mo != "clean":  # mergiraf backend itself conflicted → driver textual-reject
        return {"outcome": "conflict", "merged": None, "reject_reason": "textual",
                "rt": 0.0, "reused": True}
    if fv == "CLEAN":  # all detectors clean → driver accepts mergiraf's output
        return {"outcome": "clean", "merged": rec["ref_merged"], "reject_reason": None,
                "rt": 0.0, "reused": True}
    if fv == "FLAG":   # detector flagged → semantic reject
        return {"outcome": "conflict", "merged": None, "reject_reason": "semantic",
                "rt": 0.0, "reused": True}
    # UNANALYZABLE → fail-closed reject
    return {"outcome": "crash", "merged": None, "reject_reason": "crash",
            "rt": 0.0, "reused": True}


# --------------------------------------------------------------------------- #
# dispatch one (config, scenario) → result dict (cached)
# --------------------------------------------------------------------------- #
def eval_one(config: str, scn: dict, sc: dict) -> dict:
    if config == "bare-git":
        return run_bare_git(scn)
    if config == "bare-mergiraf":
        return bare_mergiraf_result(scn, sc)
    if config == "driver-mergiraf":
        return driver_mergiraf_result(scn, sc)
    if config in ("driver-git", "driver-auto"):
        return run_driver(DRIVER_ENV[config], scn)
    raise ValueError(f"unknown config {config!r}")


# --------------------------------------------------------------------------- #
# preflight (only when a Docker config is selected)
# --------------------------------------------------------------------------- #
def preflight(configs: list[str]) -> None:
    if not (set(configs) & DOCKER_CONFIGS):
        return
    if shutil.which("joern-parse") is None or shutil.which("joern") is None:
        sys.exit("ABORT: joern-parse / joern not on PATH (driver detection needs them).")
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=30, check=True)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ABORT: Docker not available — start Docker Desktop, then re-run.\n  ({str(e)[:160]})")
    have = subprocess.run(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
                          capture_output=True, text=True).stdout
    need = {MERGIRAF_IMAGE, RM2_IMAGE}
    if "driver-auto" in configs and os.environ.get(SPECIALIST_ROUTING_ENV) == "1":
        # Post-flip (#27/#28), auto only routes to git/Mergiraf by default; the
        # refuted Spork/Weave arms run only under the opt-in flag — and then a
        # missing image would silently crash-fallback to git and confound the arm.
        need |= {SPORK_IMAGE, WEAVE_IMAGE}
    missing = [im for im in sorted(need) if im not in have]
    if missing:
        sys.exit("ABORT: missing Docker images (needed by the selected driver configs):\n  "
                 + "\n  ".join(missing))


# --------------------------------------------------------------------------- #
# aggregation + reporting
# --------------------------------------------------------------------------- #
def per_merge_three_outcome(records: list[dict]) -> dict[str, str]:
    """merge_id → {accept, textual, semantic, crash} (any-file priority)."""
    by_merge: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_merge[r["merge_id"]].append(r)
    out = {}
    for mid, frs in by_merge.items():
        reasons = {f["reject_reason"] for f in frs}
        if "semantic" in reasons:
            out[mid] = "semantic"
        elif "textual" in reasons:
            out[mid] = "textual"
        elif "crash" in reasons or "timeout" in reasons:
            out[mid] = "crash"
        else:
            out[mid] = "accept"
    return out


def stage_c_style_r(records: list[dict]) -> tuple[int, int]:
    """(blocked, scored) per-merge, Stage-C definition: drop all-diverged merges,
    blocked = any clean file rejected (semantic or fail-closed)."""
    by_merge: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_merge[r["merge_id"]].append(r)
    blocked = scored = 0
    for frs in by_merge.values():
        # a file is "scored" if mergiraf produced a clean merge (not diverged);
        # for driver-mergiraf, diverged==textual-reject reason on a conflict outcome
        clean_or_flagged = [f for f in frs if not (f["outcome"] == "conflict"
                                                   and f["reject_reason"] == "textual")]
        if not clean_or_flagged:
            continue  # all files diverged → leaves the sample
        scored += 1
        if any(f["reject_reason"] in ("semantic", "crash") for f in clean_or_flagged):
            blocked += 1
    return blocked, scored


def metrics_for(records: list[dict]) -> ToolMetrics:
    m = ToolMetrics(tool_name="x")
    for r in records:
        m.add_classification(r["cls"], r["rt"])
    return m


def write_reports(out_dir: Path, scored: dict[str, list[dict]], commit: str,
                  configs_run: list[str]) -> str:
    lines: list[str] = []
    p = lines.append
    p("# P2 — Whole-Driver End-to-End Cost-Model Evaluation")
    p(f"# detectors frozen at driver commit {commit}; corpus = P1 164 pos / 193 ctl")
    p(f"# configs scored: {', '.join(configs_run)}")
    p("# cost unit = per file (Schesch); FP x10, FN/TN x1, CRASH/TIMEOUT x1")
    p("# oracle = hybrid (test-label when output==Mergiraf ref; else dev-match)")
    p("")

    # ---- 1. cost-model table (per file), per arm + pooled ----
    for arm_label, arm in (("positives (Tests_failed)", "pos"),
                           ("controls (Tests_passed)", "ctl"),
                           ("POOLED", None)):
        p(f"## Cost-model table — {arm_label}")
        p(f"  {'config':16s} {'n':>4} {'TP':>4} {'FP':>4} {'TN':>4} {'FN':>4} "
          f"{'CR':>3} {'cost':>7} {'cost/n':>7} {'med_rt':>7}")
        for cfg in ALL_CONFIGS:
            recs = scored.get(cfg)
            if not recs:
                continue
            sel = [r for r in recs if (arm is None or r["arm"] == arm)]
            if not sel:
                continue
            m = metrics_for(sel)
            cost = m.weighted_cost()
            rts = [r["rt"] for r in sel if r["rt"] > 0]
            med = statistics.median(rts) if rts else 0.0
            p(f"  {cfg:16s} {m.scenario_count:>4} {m.tp:>4} {m.fp:>4} {m.tn:>4} "
              f"{m.fn:>4} {m.crashes + m.timeouts:>3} {cost:>7.0f} "
              f"{cost / m.scenario_count:>7.2f} {med:>7.1f}")
        p("")

    # ---- 2. three-outcome decomposition (per merge, any-file) ----
    p("## Three-outcome decomposition (per merge, any-file)")
    p(f"  {'config':16s} {'arm':>4} {'merges':>6} {'accept':>7} {'textual':>8} "
      f"{'semantic':>9} {'crash':>6}")
    for cfg in ALL_CONFIGS:
        recs = scored.get(cfg)
        if not recs:
            continue
        for arm in ("pos", "ctl"):
            sel = [r for r in recs if r["arm"] == arm]
            if not sel:
                continue
            three = per_merge_three_outcome(sel)
            c = Counter(three.values())
            n = len(three)
            p(f"  {cfg:16s} {arm:>4} {n:>6} {c['accept']:>7} {c['textual']:>8} "
              f"{c['semantic']:>9} {c['crash']:>6}")
    p("")

    # ---- 2b. routing distribution (driver-auto only) ----
    auto = scored.get("driver-auto")
    if auto:
        routed = [r for r in auto if r.get("route")]
        p("## Routing distribution — driver-auto (cluster → effective backend, per file)")
        if not routed:
            p("  (no AutoBackend routing lines captured — cache predates route capture; "
              "re-run driver-auto to populate)")
        else:
            by_cluster = Counter(r["route"]["cluster"] for r in routed)
            by_chosen = Counter(r["route"]["chosen"] for r in routed)
            by_effective = Counter(r["route"]["effective"] for r in routed)
            fell_back = sum(1 for r in routed if r["route"]["fell_back"])
            p(f"  files with a routing line : {len(routed)}/{len(auto)}")
            p(f"  cluster      : {dict(by_cluster)}")
            p(f"  chosen route : {dict(by_chosen)}")
            p(f"  effective    : {dict(by_effective)}  (after crash-fallback)")
            p(f"  crash-fell-back to git    : {fell_back}")
            # FP rate per effective backend — the #27/#28 end-to-end signal
            p("  FP (silent-wrong) by effective backend:")
            for be in sorted(by_effective):
                sub = [r for r in routed if r["route"]["effective"] == be]
                fp = sum(1 for r in sub if r["cls"] == Classification.FALSE_POSITIVE)
                p(f"    {be:18s} {fp:>3} FP / {len(sub):>3}")
        p("")

    # ---- 3. detection delta (bare → driver, same backend) ----
    p("## Detection delta — what the detection layer adds (per file)")
    for bare, drv in (("bare-mergiraf", "driver-mergiraf"), ("bare-git", "driver-git")):
        if bare not in scored or drv not in scored:
            continue
        bare_by = {(r["arm"], r["scenario_id"]): r for r in scored[bare]}
        moved_fp = moved_tp = 0  # FP→visible (good), TP→visible (R1 cost)
        for r in scored[drv]:
            b = bare_by.get((r["arm"], r["scenario_id"]))
            if not b:
                continue
            # a bare-clean file the driver now surfaces (semantic/textual/fail-closed)
            surfaced = r["outcome"] != "clean"
            if b["cls"] == Classification.FALSE_POSITIVE and surfaced:
                moved_fp += 1
            if b["cls"] == Classification.TRUE_POSITIVE and surfaced:
                moved_tp += 1
        dcost = metrics_for(scored[bare]).weighted_cost() - metrics_for(scored[drv]).weighted_cost()
        p(f"  {bare} → {drv}:")
        p(f"    silent-wrong (FP x10) converted to visible (x1): {moved_fp}  "
          f"(cost saved ≈ {moved_fp * 9})")
        p(f"    correct (TP) wrongly rejected (x0→x1, the R1 cost): {moved_tp}  "
          f"(cost added {moved_tp})")
        p(f"    net weighted-cost improvement (bare − driver): {dcost:.0f}")
    p("")

    # ---- 4. cross-check: driver-mergiraf reproduces Stage C R1/R2 ----
    p("## Cross-check — driver-mergiraf reproduces Stage C (Stage-C R-definition)")
    if "driver-mergiraf" in scored:
        recs = scored["driver-mergiraf"]
        b2, n2 = stage_c_style_r([r for r in recs if r["arm"] == "pos"])
        b1, n1 = stage_c_style_r([r for r in recs if r["arm"] == "ctl"])
        ok2 = (b2, n2) == STAGE_C_R2
        ok1 = (b1, n1) == STAGE_C_R1
        p(f"  R2 (positives blocked/scored): {fmt_ci(b2, n2)}  "
          f"[Stage C {STAGE_C_R2[0]}/{STAGE_C_R2[1]}: {'MATCH' if ok2 else '*** MISMATCH ***'}]")
        p(f"  R1 (controls blocked/scored) : {fmt_ci(b1, n1)}  "
          f"[Stage C {STAGE_C_R1[0]}/{STAGE_C_R1[1]}: {'MATCH' if ok1 else '*** MISMATCH ***'}]")
    else:
        p("  (driver-mergiraf not scored this run)")
    p("")

    text = "\n".join(lines)
    (out_dir / "summary.txt").write_text(text + "\n")

    # per-file CSV
    with open(out_dir / "scenarios.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["config", "arm", "merge_id", "scenario_id", "outcome",
                    "reject_reason", "classification", "oracle", "rt"])
        for cfg in ALL_CONFIGS:
            for r in scored.get(cfg, []):
                w.writerow([cfg, r["arm"], r["merge_id"], r["scenario_id"], r["outcome"],
                            r["reject_reason"] or "", r["cls"].value, r["oracle"], r["rt"]])
    return text


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pos_dir", nargs="?", default=DEFAULT_POS)
    ap.add_argument("ctl_dir", nargs="?", default=DEFAULT_CTL)
    ap.add_argument("--configs", default=",".join(ALL_CONFIGS),
                    help="comma-separated subset of " + ",".join(ALL_CONFIGS))
    ap.add_argument("--limit", type=int, default=0, help="smoke run: first N merges/arm")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    bad = [c for c in configs if c not in ALL_CONFIGS]
    if bad:
        sys.exit(f"ABORT: unknown config(s) {bad}; choose from {ALL_CONFIGS}")

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = out_dir / "raw_results.json"
    cache: dict = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    def save() -> None:
        cache_path.write_text(json.dumps(cache))

    # DRIVER_COMMIT env override: a git-archive deployment (e.g. the AWS box)
    # has no .git, so driver_commit() returns "unknown" — the operator must
    # state the shipped commit explicitly rather than run un-attributable.
    commit = os.environ.get("DRIVER_COMMIT") or driver_commit()
    if commit == "unknown" and (set(configs) & DOCKER_CONFIGS):
        sys.exit("ABORT: driver commit unresolved (no .git?) but a driver-executing "
                 "config is selected — set DRIVER_COMMIT=<short-sha> so cache keys "
                 "and reports are attributable.")
    preflight(configs)
    sc = load_stage_c()

    pos = load_scenarios(ROOT / args.pos_dir)
    ctl = load_scenarios(ROOT / args.ctl_dir)
    arms = [("pos", group_by_merge(pos)), ("ctl", group_by_merge(ctl))]
    print(f"driver_commit={commit} configs={configs} out={out_dir}", flush=True)
    print(f"positives: {len(pos)} files / {len(arms[0][1])} merges; "
          f"controls: {len(ctl)} files / {len(arms[1][1])} merges", flush=True)

    # flatten scenarios, honoring --limit per arm
    work: list[tuple[str, dict]] = []
    for arm, groups in arms:
        mids = sorted(groups)
        if args.limit:
            mids = mids[:args.limit]
        for mid in mids:
            for scn in groups[mid]:
                work.append((arm, scn))

    scored: dict[str, list[dict]] = {c: [] for c in configs}
    n_total = len(work) * len(configs)
    done = 0
    for cfg in configs:
        for arm, scn in work:
            sid = scn["scenario_id"]
            # Driver-executing configs are keyed by driver commit (stale-cache
            # guard); assembled/bare configs are driver-independent.
            key = f"{cfg}::{sid}::{commit}" if cfg in DOCKER_CONFIGS else f"{cfg}::{sid}"
            if key not in cache:
                res = eval_one(cfg, scn, sc)
                if res is None:
                    print(f"  WARN {cfg} {sid[:50]}: no Stage-C record, skipped", flush=True)
                    done += 1
                    continue
                cache[key] = res
                save()
            res = cache[key]
            ref = sc.get(sid, {}).get("ref_merged")
            cls, oracle = score(arm, res, scn, ref)
            scored[cfg].append({
                "arm": arm, "merge_id": merge_id_of(scn), "scenario_id": sid,
                "outcome": res["outcome"], "reject_reason": res.get("reject_reason"),
                "merged": res.get("merged"), "cls": cls, "oracle": oracle,
                "rt": res.get("rt", 0.0), "route": res.get("route"),
            })
            done += 1
            if cfg in DOCKER_CONFIGS:
                print(f"  [{cfg} {done}/{n_total}] {sid[:52]:52s} {res['outcome']:8s} "
                      f"{res.get('reject_reason') or '':9s} {cls.value:4s} ({res.get('rt',0):.0f}s)",
                      flush=True)

    text = write_reports(out_dir, scored, commit, configs)
    print("\n" + text)
    print(f"\nWrote {out_dir}/summary.txt, scenarios.csv, raw_results.json")


if __name__ == "__main__":
    main()
