"""S-D5 two-arm evaluation battery (GD3) — detector cycle ISSUES #31.

Authority: outputs/detector-cycle-plan.md §5 GD3 + §9; runs only AFTER the
detector-suite freeze is recorded in reports_detectors/manifest.json
(detector_suite_commit) — this harness ABORTS if the recorded freeze commit
does not match the driver commit it is about to score, or if the driver
working tree is dirty (post-freeze detector edits are forbidden, plan §3).

Two arms per plan §5 GD3:
  baseline     — the 5 default lanes (the Stage-C DETECTORS set), experimental
                 flag OFF: JoernDataFlowInterference, JoernUnresolvedReference,
                 JoernInfiniteLoop, JoernInvalidLoopBounds, RM2RenameConflict.
  experimental — the FULL 7-lane suite (detector_tune_run.FULL_SUITE), flag ON.

Execution plan per file (both arms in one pass; arm = a VIEW over lane rows):
  4 lanes never read SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS (verified by a
  source-scan tripwire at import): DFI, InfiniteLoop, InvalidLoopBounds,
  RM2RenameConflict — executed once under flag=0, keyed ::flagX, and shared
  by both arms (a paired design: the arms differ ONLY through flag-sensitive
  lanes, so the added-recall contrast carries no Joern re-run noise).
  JoernUnresolvedReference runs twice (::flag0 baseline / ::flag1 widened);
  ImportPruneUsage + SignatureStaleCall run once (::flag1, experimental-only).

Verdict classification (S-D3/S-D4 close-out notes): detect_validate's
"inconclusive" SUBSTRING sentinel can collide with a genuine flag quoting a
Java identifier. Here every Issue message must match a closed world of
prefix stems — genuine stems or fail-closed stems, enumerated from the lane
sources at the freeze commit. An unmatched message is classified fail-closed
AND recorded in classifier_drift; scoring refuses a PASS verdict while drift
rows exist. Classification happens at SCORING time from cached raw issues,
so a classifier fix never re-runs lanes.

Attribution (report only — machine-caught is any-lane FLAG, plan §9):
D3-widened findings are recognized inside JoernUnresolvedReference rows by
the message stem "Stale reference to a removed/renamed declaration:".

Populations (unit = merge; any-file-flag; machine-caught = ≥1 lane FLAG):
  heldout     110 taxonomy held-out units — the S1-materialized scenario JSONs
              (data/scenarios_semantic + data/scenarios_taxonomy_hi), selected
              by reports_taxonomy/split_assignment.csv and integrity-checked
              against the taxonomy manifest's committed sha256 pins.
  derivation  165 derivation units — descriptive only, TUNING-TAINTED.
  evalctl     the 200 eval-controls (materialized by
              tools/detector_eval_materialize.py under Amendment 1).
  spgroup_ctl / spgroup_pos — the Phase-2b spgroup JSONs, developer-merged
              source (the phase2b harness pattern), EXPERIMENTAL ARM ONLY.

Vacuous-run guard: before scoring, every (lane, flag-state) execution in the
plan must FLAG on an embedded positive micro-fixture under that exact flag
state (the tune-runner pattern; the baseline-arm JoernUnresolvedReference
smoke is an OLD-lane live-Joern positive, not the widened-path one).

Known-answer env validation (--known-answer N): re-scores the first N tune
merges with the FULL suite and compares every file×lane verdict to the
committed GD2(iii) cache (reports_detectors/tune_d3/raw_results.json, keys
"<sid>::<lane>::732d8ff::exp1") — the detector-cycle analogue of the
canonical-table environment validation from CLI-DEPLOY.md.

Resumable: results cache per (scenario, lane, freeze-commit, flag-state) in
<out>/eval_cache_<population>[_shardK_N].json; merge reproductions cached
under the detect_validate ::__merge__:: keys. --shard K/N partitions merges
deterministically (sorted merge_id, index % N == K); --score aggregates all
shard caches without running anything.

Usage (repo-local smoke uses tune-controls only — held-out stays eval-side):
    .venv/bin/python tools/detector_eval_run.py --smoke
    .venv/bin/python tools/detector_eval_run.py --known-answer 3
    .venv/bin/python tools/detector_eval_run.py --population heldout [--shard 0/4]
    .venv/bin/python tools/detector_eval_run.py --score
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # merge-tool-comparison/
DRIVER_ROOT = ROOT.parent / "semantic_merge_driver"
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "tools"))

from detect_validate import (  # noqa: E402
    MERGIRAF_IMAGE, driver_commit, load_scenarios, preflight, reproduce_merge,
    run_detector, wilson, fmt_ci,
)
import detector_tune_run as tune  # noqa: E402  (LANES + smoke builders; its
# import-time flag export is overridden per-execution below)

FLAG_ENV = "SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"
DEFAULT_OUT = "reports_detectors/eval"

BASELINE_LANES = (
    "JoernDataFlowInterference", "JoernUnresolvedReference",
    "JoernInfiniteLoop", "JoernInvalidLoopBounds", "RM2RenameConflict",
)
EXPERIMENTAL_LANES = tune.FULL_SUITE                    # all 7
FLAG_SENSITIVE = frozenset(
    {"JoernUnresolvedReference", "ImportPruneUsage", "SignatureStaleCall"})

# (lane, flag-state) execution rows per file. flagX = lane provably never
# reads the flag (shared by both arms); flag0/flag1 = explicit arm state.
EXECS_BOTH_ARMS = (
    ("JoernDataFlowInterference", "flagX"),
    ("JoernInfiniteLoop", "flagX"),
    ("JoernInvalidLoopBounds", "flagX"),
    ("RM2RenameConflict", "flagX"),
    ("JoernUnresolvedReference", "flag0"),
    ("JoernUnresolvedReference", "flag1"),
    ("ImportPruneUsage", "flag1"),
    ("SignatureStaleCall", "flag1"),
)
EXECS_EXPERIMENTAL_ONLY = tuple(
    (ln, fs) for ln, fs in EXECS_BOTH_ARMS if (ln, fs) != ("JoernUnresolvedReference", "flag0"))

ARM_VIEW = {
    "baseline": (("JoernDataFlowInterference", "flagX"), ("JoernInfiniteLoop", "flagX"),
                 ("JoernInvalidLoopBounds", "flagX"), ("RM2RenameConflict", "flagX"),
                 ("JoernUnresolvedReference", "flag0")),
    "experimental": (("JoernDataFlowInterference", "flagX"), ("JoernInfiniteLoop", "flagX"),
                     ("JoernInvalidLoopBounds", "flagX"), ("RM2RenameConflict", "flagX"),
                     ("JoernUnresolvedReference", "flag1"), ("ImportPruneUsage", "flag1"),
                     ("SignatureStaleCall", "flag1")),
}

NAME_BINDING_FAMILY = frozenset({
    "stale-usage-of-pruned-import",
    "stale-reference-to-removed-declaration",
    "stale-reference-to-renamed-or-relocated-declaration",
    "stale-caller-of-changed-signature",
})

# --------------------------------------------------------------------------- #
# closed-world message classification (stems verified against lane sources
# at the freeze commit 732d8ff; the source-scan tripwire below guards drift)
# --------------------------------------------------------------------------- #
GENUINE_STEMS = (
    "Potential infinite loop in method",            # JoernInfiniteLoop
    "Unresolved identifier '",                      # JoernUnresolvedReference (Joern)
    "Stale reference to a removed/renamed declaration:",  # UnresolvedReference (D3 widened)
    "Potential stale read: collection",             # JoernDataFlowInterference
    "Dead Loop Detected:",                          # JoernInvalidLoopBounds
    "Stale caller of renamed identifier:",          # RM2RenameConflict (call lane)
    "Stale reference to renamed variable/field:",   # RM2RenameConflict (var lane)
    "Stale usage of pruned import:",                # ImportPruneUsage
    "Stale call to '",                              # SignatureStaleCall
)
FAIL_CLOSED_STEMS = (
    "merged analysis inconclusive:",                # Joern lanes, merged parse
    "ours analysis inconclusive:",                  # Joern lanes, parent parse
    "theirs analysis inconclusive:",
    "Joern analysis inconclusive:",                 # Joern lanes, query wrapper
    "Joern query exited rc=",                       # JoernInvalidLoopBounds
    "Joern subprocess failed; analysis inconclusive:",
    "RM2RenameConflict analysis inconclusive:",
    "SignatureStaleCall analysis inconclusive:",
    "harness: strategy raised",                     # run_detector exception wrap
)
WIDENED_STEM = "Stale reference to a removed/renamed declaration:"


def classify_issue(message: str) -> str:
    """'genuine' | 'fail_closed' | 'drift' (drift = unmatched, treated as
    fail-closed for verdicts but blocks a PASS until adjudicated)."""
    if message.startswith(GENUINE_STEMS):
        return "genuine"
    if message.startswith(FAIL_CLOSED_STEMS):
        return "fail_closed"
    return "drift"


def verdict_from_issues(issues: list[dict]) -> tuple[str, list[str]]:
    """(CLEAN | FLAG | UNANALYZABLE, drift messages). Genuine wins mixes —
    both block in deployment, only FLAG enters adjudication (Stage-C rule);
    a Joern-env failure with a widened finding is deliberately a FLAG
    (S-D4 close-out note)."""
    kinds = [(classify_issue(i["message"]), i["message"]) for i in issues]
    drift = [m for k, m in kinds if k == "drift"]
    if any(k == "genuine" for k, _ in kinds):
        return "FLAG", drift
    if kinds:
        return "UNANALYZABLE", drift
    return "CLEAN", drift


# --------------------------------------------------------------------------- #
# freeze + flag-free tripwires
# --------------------------------------------------------------------------- #
def _manifest() -> dict:
    return json.loads((ROOT / "reports_detectors/manifest.json").read_text())


def assert_frozen_commit() -> str:
    frozen = _manifest().get("detector_suite_commit")
    if not frozen:
        sys.exit("ABORT: detector_suite_commit not recorded in the cycle manifest "
                 "— the plan §3 freeze must land before any evaluation run.")
    commit = driver_commit()
    if commit != frozen:
        sys.exit(f"ABORT: driver commit {commit!r} != frozen suite commit "
                 f"{frozen!r} — post-freeze detector changes require a dated "
                 f"§12 amendment + full S-D5 rerun (plan §3).")
    if not os.environ.get("DRIVER_COMMIT"):      # git checkout (not an archive)
        dirty = subprocess.run(
            ["git", "-C", str(ROOT.parent), "diff", "HEAD", "--",
             "semantic_merge_driver"], capture_output=True, text=True).stdout
        if dirty:
            sys.exit("ABORT: semantic_merge_driver working tree is dirty — "
                     "post-freeze detector edits are forbidden (plan §3).")
    return commit


def assert_flag_free_lanes() -> None:
    """flagX sharing is sound only while those 4 lanes never read the flag."""
    import importlib
    for lane in ("JoernDataFlowInterference", "JoernInfiniteLoop",
                 "JoernInvalidLoopBounds", "RM2RenameConflict"):
        cls = tune.LANES[lane][0]
        src = Path(importlib.import_module(cls.__module__).__file__).read_text()
        if FLAG_ENV in src:
            sys.exit(f"ABORT: lane {lane} source mentions {FLAG_ENV} — the "
                     f"::flagX shared-execution assumption no longer holds; "
                     f"rekey per-arm before scoring.")


# --------------------------------------------------------------------------- #
# populations
# --------------------------------------------------------------------------- #
TAXONOMY_DIRS = ("data/scenarios_semantic", "data/scenarios_taxonomy_hi")
POPULATIONS = {
    "heldout":     dict(source="mergiraf", execs=EXECS_BOTH_ARMS, split="heldout"),
    "derivation":  dict(source="mergiraf", execs=EXECS_BOTH_ARMS, split="derivation"),
    "evalctl":     dict(source="mergiraf", execs=EXECS_BOTH_ARMS, split=None,
                        dirs=("data/scenarios_detector_eval",)),
    "spgroup_ctl": dict(source="developer", execs=EXECS_EXPERIMENTAL_ONLY, split=None,
                        dirs=("data/scenarios_phase2b_ctl",)),
    "spgroup_pos": dict(source="developer", execs=EXECS_EXPERIMENTAL_ONLY, split=None,
                        dirs=("data/scenarios_phase2b",)),
}


def split_ids(split: str) -> set[str]:
    rows = csv.DictReader(open(ROOT / "reports_taxonomy/split_assignment.csv"))
    return {r["merge_id"] for r in rows if r["split"] == split}


def final_labels() -> dict[str, str]:
    rows = csv.DictReader(open(ROOT / "reports_taxonomy/labels_final.csv"))
    return {r["merge_id"]: r["final_primary"] for r in rows}


def taxonomy_pins() -> dict[str, str]:
    return json.loads((ROOT / "reports_taxonomy/manifest.json").read_text())[
        "scenario_files_sha256"]


def load_population(pop: str) -> list[dict]:
    cfg = POPULATIONS[pop]
    if cfg["split"]:
        ids = split_ids(cfg["split"])
        pins = taxonomy_pins()
        scns, missing, bad = [], [], []
        for d in TAXONOMY_DIRS:
            for f in sorted(glob.glob(str(ROOT / d / "*.json"))):
                rel = str(Path(f).relative_to(ROOT))
                scn = json.load(open(f))
                if scn.get("merge_id") not in ids:
                    continue
                if rel not in pins:
                    missing.append(rel)
                    continue
                if hashlib.sha256(Path(f).read_bytes()).hexdigest() != pins[rel]:
                    bad.append(rel)
                    continue
                scns.append(scn)
        if missing or bad:
            sys.exit(f"ABORT: {pop} integrity check failed — "
                     f"{len(missing)} unpinned, {len(bad)} hash-mismatched "
                     f"(e.g. {(missing + bad)[:3]}); rematerialize before scoring.")
        got = {s["merge_id"] for s in scns}
        if got != ids:
            sys.exit(f"ABORT: {pop} expected {len(ids)} units, found scenario "
                     f"files for {len(got)} (missing: {sorted(ids - got)[:5]}).")
        return scns
    scns = []
    for d in cfg["dirs"]:
        scns.extend(load_scenarios(ROOT / d))
    if not scns:
        sys.exit(f"ABORT: population {pop} is empty — materialize {cfg['dirs']} first.")
    if pop == "evalctl":
        # Post-run guard (2026-07-18, runs.md incident 3): scoring evalctl
        # against a PARTIAL local materialization silently shrinks the GD3(ii)
        # denominator. The effective list is the authority.
        eff = ROOT / "reports_detectors/eval/eval_controls_effective.csv"
        if eff.exists():
            want = {r["merge_id"] for r in csv.DictReader(open(eff))}
            got = {s["merge_id"] for s in scns}
            if got != want:
                sys.exit(f"ABORT: evalctl scenario dir holds {len(got)} of the "
                         f"{len(want)} effective merges (missing e.g. "
                         f"{sorted(want - got)[:3]}) — rematerialize before "
                         f"scoring; the committed instance-run artifacts are "
                         f"the authoritative score.")
    return scns


# --------------------------------------------------------------------------- #
# smoke gate (vacuous-run guard, per (lane, flag-state) execution row)
# --------------------------------------------------------------------------- #
def _smoke_unresolved_reference_oldlane():
    """OLD-lane (flag OFF) positive: variable rename m→method half-applied —
    the erudika shape from test_unresolved_reference.py, which the Joern
    differential flags without the widened path (live Joern required)."""
    base = "public class Aspect {\n    public void invoke(int mi) {\n        int m = mi;\n        helper(m);\n    }\n    private void helper(int x) {}\n}\n"
    ours = "public class Aspect {\n    public void invoke(int mi) {\n        int method = mi;\n        helper(method);\n    }\n    private void helper(int x) {}\n}\n"
    theirs = "public class Aspect {\n    public void invoke(int mi) {\n        int m = mi;\n        helper(m);\n        helper(m);\n    }\n    private void helper(int x) {}\n}\n"
    merged = "public class Aspect {\n    public void invoke(int mi) {\n        int method = mi;\n        helper(m);\n        helper(method);\n    }\n    private void helper(int x) {}\n}\n"
    return base, ours, theirs, merged, "Aspect.java"


def run_smokes(execs: tuple) -> None:
    strategies = {ln: tune.LANES[ln][0]() for ln, _ in execs}
    for lane, flagseg in execs:
        if (lane, flagseg) == ("JoernUnresolvedReference", "flag0"):
            builder = _smoke_unresolved_reference_oldlane
        else:
            builder = tune.LANES[lane][1]
        os.environ[FLAG_ENV] = "1" if flagseg == "flag1" else "0"
        base, ours, theirs, merged, filename = builder()
        scn = {"base_content": base, "ours_content": ours, "theirs_content": theirs}
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / filename
            p.write_text(merged, encoding="utf-8")
            rec = run_detector("smoke", strategies[lane], "differential", str(p), scn)
        verdict, _ = verdict_from_issues(rec["issues"])
        if verdict != "FLAG":
            sys.exit(f"ABORT: smoke {lane}::{flagseg} did not FLAG (got {verdict}) "
                     f"— flag wiring or lane regression; a 0-flag run would be vacuous.")
        print(f"smoke positive: FLAG ok | {lane}::{flagseg}", flush=True)


# --------------------------------------------------------------------------- #
# known-answer env validation vs the committed GD2(iii) cache
# --------------------------------------------------------------------------- #
def run_known_answer(n_merges: int, commit: str) -> None:
    tune_cache = json.loads(
        (ROOT / "reports_detectors/tune_d3/raw_results.json").read_text())
    scns = load_scenarios(ROOT / "data/scenarios_detector_tune")
    groups: dict[str, list[dict]] = {}
    for s in scns:
        groups.setdefault(s["merge_id"], []).append(s)
    chosen = sorted(groups)[:n_merges]
    strategies = {ln: tune.LANES[ln][0]() for ln in EXPERIMENTAL_LANES}
    cache: dict = {}
    mism = []
    checked = 0
    for mid in chosen:
        for scn in groups[mid]:
            merge_rec = reproduce_merge(scn, cache, lambda: None)
            ref_merge = tune_cache.get(
                f"{scn['scenario_id']}::__merge__::{MERGIRAF_IMAGE}")
            if ref_merge and ref_merge["outcome"] != merge_rec["outcome"]:
                mism.append((scn["scenario_id"], "__merge__",
                             f"{merge_rec['outcome']} != tune {ref_merge['outcome']}"))
            for lane in EXPERIMENTAL_LANES:
                ref = tune_cache.get(f"{scn['scenario_id']}::{lane}::{commit}::exp1")
                if merge_rec["outcome"] != "clean":
                    continue     # tune recorded DIVERGED rows outside lane keys
                if ref is None:
                    mism.append((scn["scenario_id"], lane, "no tune reference row"))
                    continue
                os.environ[FLAG_ENV] = "1"
                with tempfile.TemporaryDirectory() as td:
                    p = Path(td) / Path(scn["file_path"]).name
                    p.write_text(merge_rec["merged"], encoding="utf-8")
                    rec = run_detector(lane, strategies[lane], "differential",
                                       str(p), scn)
                got, _ = verdict_from_issues(rec["issues"])
                want, _ = verdict_from_issues(ref["issues"])
                checked += 1
                if got != want:
                    mism.append((scn["scenario_id"], lane, f"{got} != tune {want}"))
        print(f"known-answer: merge {mid} done", flush=True)
    if mism:
        for row in mism:
            print(f"  MISMATCH {row}", flush=True)
        sys.exit(f"ABORT: known-answer validation failed on {len(mism)} rows — "
                 f"environment does not reproduce the committed GD2(iii) verdicts.")
    print(f"known-answer validation PASS: {checked} file×lane verdicts match "
          f"the committed tune_d3 cache over {len(chosen)} merges.", flush=True)


# --------------------------------------------------------------------------- #
# execution
# --------------------------------------------------------------------------- #
def cache_path(out_dir: Path, pop: str, shard: str | None) -> Path:
    suffix = f"_shard{shard.replace('/', '_')}" if shard else ""
    return out_dir / f"eval_cache_{pop}{suffix}.json"


def run_population(pop: str, out_dir: Path, commit: str, shard: str | None) -> None:
    cfg = POPULATIONS[pop]
    scns = load_population(pop)
    groups: dict[str, list[dict]] = {}
    for s in scns:
        groups.setdefault(s["merge_id"], []).append(s)
    mids = sorted(groups)
    if shard:
        k, n = (int(x) for x in shard.split("/"))
        mids = [m for i, m in enumerate(mids) if i % n == k]
    cpath = cache_path(out_dir, pop, shard)
    cache: dict = json.loads(cpath.read_text()) if cpath.exists() else {}

    def save() -> None:
        cpath.write_text(json.dumps(cache))

    strategies = {ln: tune.LANES[ln][0]() for ln, _ in cfg["execs"]}
    print(f"[{pop}] {len(mids)} merges / "
          f"{sum(len(groups[m]) for m in mids)} files | execs/file: "
          f"{len(cfg['execs'])} | cache {cpath.name}", flush=True)

    t_start = time.time()
    for i, mid in enumerate(mids, 1):
        for scn in groups[mid]:
            merge_rec = reproduce_merge(scn, cache, save, cfg["source"])
            if merge_rec["outcome"] != "clean":
                continue
            dirty = False
            with tempfile.TemporaryDirectory() as td:
                merged_path = Path(td) / Path(scn["file_path"]).name
                written = False
                for lane, flagseg in cfg["execs"]:
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
        if i % 5 == 0 or i == len(mids):
            rate = (time.time() - t_start) / i
            print(f"  [{pop}{' ' + shard if shard else ''}] {i}/{len(mids)} merges "
                  f"({rate:.0f}s/merge avg)", flush=True)
    save()
    print(f"[{pop}] run complete → {cpath.name}", flush=True)


# --------------------------------------------------------------------------- #
# scoring
# --------------------------------------------------------------------------- #
def load_caches(out_dir: Path, pop: str) -> dict:
    merged: dict = {}
    for f in sorted(out_dir.glob(f"eval_cache_{pop}*.json")):
        merged.update(json.loads(f.read_text()))
    return merged


def score_population(pop: str, out_dir: Path, commit: str,
                     labels: dict[str, str]) -> dict | None:
    cfg = POPULATIONS[pop]
    try:
        scns = load_population(pop)
    except SystemExit:
        return None                                  # population not materialized
    cache = load_caches(out_dir, pop)
    if not cache:
        return None
    groups: dict[str, list[dict]] = {}
    for s in scns:
        groups.setdefault(s["merge_id"], []).append(s)

    arms = ("experimental",) if cfg["execs"] is EXECS_EXPERIMENTAL_ONLY \
        else ("baseline", "experimental")
    units, drift_rows, missing = [], [], []
    for mid, ss in sorted(groups.items()):
        row = {"merge_id": mid, "n_files": len(ss),
               "category": (labels.get(mid) if cfg["split"] else
                            ss[0].get("category", "unknown")),
               "files": {}, "arm": {}}
        n_diverged = 0
        for scn in ss:
            mkey = (f"{scn['scenario_id']}::__merge__::developer"
                    if cfg["source"] == "developer"
                    else f"{scn['scenario_id']}::__merge__::{MERGIRAF_IMAGE}")
            mrec = cache.get(mkey)
            if mrec is None:
                missing.append(mkey)
                continue
            if mrec["outcome"] != "clean":
                n_diverged += 1
                row["files"][scn["scenario_id"]] = {"merge_outcome": mrec["outcome"]}
                continue
            frow = {"merge_outcome": "clean", "lanes": {}}
            for lane, flagseg in cfg["execs"]:
                key = f"{scn['scenario_id']}::{lane}::{commit}::{flagseg}"
                rec = cache.get(key)
                if rec is None:
                    missing.append(key)
                    continue
                verdict, drift = verdict_from_issues(rec["issues"])
                for d in drift:
                    drift_rows.append({"key": key, "message": d})
                frow["lanes"][f"{lane}::{flagseg}"] = {
                    "verdict": verdict,
                    "issues": rec["issues"],
                    "runtime_s": rec.get("runtime_s", 0.0),
                }
            row["files"][scn["scenario_id"]] = frow
        row["n_diverged"] = n_diverged
        for arm in arms:
            flag_lanes, una = [], []
            for fid, frow in row["files"].items():
                if frow.get("merge_outcome") != "clean":
                    continue
                for lane, flagseg in ARM_VIEW[arm]:
                    lrec = frow.get("lanes", {}).get(f"{lane}::{flagseg}")
                    if not lrec:
                        continue
                    if lrec["verdict"] == "FLAG":
                        flag_lanes.append((fid, lane))
                    elif lrec["verdict"] == "UNANALYZABLE":
                        una.append((fid, lane))
            n_scored = sum(1 for f in row["files"].values()
                           if f.get("merge_outcome") == "clean")
            row["arm"][arm] = {
                "caught": bool(flag_lanes),
                "flag_lanes": flag_lanes,
                "unanalyzable": una,
                "status": ("ALL_DIVERGED" if n_scored == 0 else
                           "FLAG" if flag_lanes else
                           "UNANALYZABLE" if una else "CLEAN"),
            }
        units.append(row)
    return {"population": pop, "units": units, "arms": arms,
            "drift": drift_rows, "missing": missing}


def recall_block(p, scored: list[dict], arms, tainted: bool) -> None:
    tag = "TUNING-TAINTED " if tainted else ""
    n = len(scored)
    per_arm_catch = {}
    for arm in arms:
        k = sum(1 for u in scored if u["arm"][arm]["caught"])
        per_arm_catch[arm] = k
        p(f"  {tag}{arm:12s} machine-caught: {fmt_ci(k, n)}")
        una = sum(1 for u in scored if u["arm"][arm]["status"] == "UNANALYZABLE")
        if una:
            p(f"  {tag}{arm:12s} additionally UNANALYZABLE-only units: {una}")
    if len(arms) == 2:
        exp_only = [u for u in scored
                    if u["arm"]["experimental"]["caught"] and not u["arm"]["baseline"]["caught"]]
        violations = [u for u in scored
                      if u["arm"]["baseline"]["caught"] and not u["arm"]["experimental"]["caught"]]
        p(f"  {tag}added recall (experimental-only catches): {fmt_ci(len(exp_only), n)}")
        if violations:
            p(f"  {tag}*** NESTEDNESS VIOLATIONS (baseline-only catches): "
              f"{[u['merge_id'] for u in violations]} — investigate")
    cats = Counter(u["category"] for u in scored)
    p(f"  {tag}per final-label category (unit counts small — bounded, not pinned):")
    for cat in sorted(cats):
        rows = [u for u in scored if u["category"] == cat]
        cells = " | ".join(
            f"{arm} {fmt_ci(sum(1 for u in rows if u['arm'][arm]['caught']), len(rows))}"
            for arm in arms)
        p(f"    {tag}{cat:55s} {cells}")
    fam = [u for u in scored if u["category"] in NAME_BINDING_FAMILY]
    if fam:
        cells = " | ".join(
            f"{arm} {fmt_ci(sum(1 for u in fam if u['arm'][arm]['caught']), len(fam))}"
            for arm in arms)
        p(f"  {tag}POOLED name-binding family (primary citable): {cells}")
        if len(arms) == 2:
            k = sum(1 for u in fam if u["arm"]["experimental"]["caught"]
                    and not u["arm"]["baseline"]["caught"])
            p(f"  {tag}POOLED family added recall: {fmt_ci(k, len(fam))}")


def lane_attribution(p, scored: list[dict], arms) -> None:
    per_lane: Counter = Counter()
    for u in scored:
        for arm in arms:
            for fid, lane in u["arm"][arm]["flag_lanes"]:
                frow = u["files"][fid]
                for lkey, lrec in frow["lanes"].items():
                    if not lkey.startswith(f"{lane}::") or lrec["verdict"] != "FLAG":
                        continue
                    if lane == "JoernUnresolvedReference":
                        wid = any(i["message"].startswith(WIDENED_STEM)
                                  for i in lrec["issues"]
                                  if classify_issue(i["message"]) == "genuine")
                        joern = any(i["message"].startswith("Unresolved identifier '")
                                    for i in lrec["issues"])
                        if wid:
                            per_lane[(arm, f"{lane} [D3-widened]")] += 1
                        if joern:
                            per_lane[(arm, f"{lane} [Joern]")] += 1
                    else:
                        per_lane[(arm, lane)] += 1
    if per_lane:
        p("  file-level FLAG rows by arm × lane (attribution is descriptive; "
          "machine-caught is any-lane):")
        for (arm, lane), k in sorted(per_lane.items()):
            p(f"    {arm:12s} {lane:45s} {k}")


def write_reports(out_dir: Path, commit: str, results: dict[str, dict]) -> str:
    labels_present = bool(results.get("heldout") or results.get("derivation"))
    lines: list[str] = []
    p = lines.append
    p(f"# S-D5 two-arm evaluation battery (GD3) — detector suite frozen at {commit}")
    p(f"# plan: outputs/detector-cycle-plan.md §5 GD3 + §9 | mergiraf {MERGIRAF_IMAGE}")
    p("# NEVER BLEND: detector-cycle numbers are a fourth instrument — separate from")
    p("# taxonomy base rates, Stage-C R1/R2, and Phase-2b recall.")
    p("")

    drift_total = sum(len(r["drift"]) for r in results.values())
    missing_total = sum(len(r["missing"]) for r in results.values())
    if drift_total:
        p(f"## *** CLASSIFIER DRIFT: {drift_total} unmatched messages — no gate can "
          f"PASS until adjudicated (see classifier_drift.json) ***")
    if missing_total:
        p(f"## *** INCOMPLETE CACHES: {missing_total} missing rows — run the missing "
          f"shards/populations before citing numbers (see missing_keys.json) ***")
    if drift_total or missing_total:
        p("")

    if results.get("heldout"):
        r = results["heldout"]
        scored = [u for u in r["units"]
                  if any(a["status"] != "ALL_DIVERGED" for a in u["arm"].values())]
        p(f"## Held-out recall (PRIMARY) — {len(scored)} units scored of "
          f"{len(r['units'])} (unit = merge, any-file-flag; machine-caught = any lane FLAG)")
        recall_block(p, scored, r["arms"], tainted=False)
        lane_attribution(p, scored, r["arms"])
        p("")

    if results.get("derivation"):
        r = results["derivation"]
        scored = [u for u in r["units"]
                  if any(a["status"] != "ALL_DIVERGED" for a in u["arm"].values())]
        p(f"## TUNING-TAINTED derivation-split numbers (descriptive only, never "
          f"citable as recall) — {len(scored)} units scored of {len(r['units'])}")
        recall_block(p, scored, r["arms"], tainted=True)
        p("")

    for pop, gate in (("evalctl", "GD3(ii) — 0 flags on the 200 eval-controls"),
                      ("spgroup_ctl", "GD3(iii) — 0 flags on spgroup labeled-clean (66)"),
                      ("spgroup_pos", "spgroup labeled-positive (17) — descriptive")):
        r = results.get(pop)
        if not r:
            continue
        p(f"## {gate}")
        for arm in r["arms"]:
            flagged = [u for u in r["units"] if u["arm"][arm]["caught"]]
            una = [u for u in r["units"] if u["arm"][arm]["status"] == "UNANALYZABLE"]
            div = [u for u in r["units"] if u["arm"][arm]["status"] == "ALL_DIVERGED"]
            n_scored = len(r["units"]) - len(div)
            p(f"  {arm:12s} units flagged: {fmt_ci(len(flagged), n_scored)}"
              f"{' | all-diverged: ' + str(len(div)) if div else ''}"
              f"{' | UNANALYZABLE-only: ' + str(len(una)) if una else ''}")
            for u in flagged:
                p(f"    FLAG {u['merge_id']} [{arm}] "
                  f"lanes={sorted(set(l for _, l in u['arm'][arm]['flag_lanes']))} "
                  f"category={u['category']}")
        if pop == "spgroup_pos":
            scored = [u for u in r["units"]
                      if u["arm"]["experimental"]["status"] != "ALL_DIVERGED"]
            cats = Counter(u["category"] for u in scored)
            for cat in sorted(cats):
                rows = [u for u in scored if u["category"] == cat]
                k = sum(1 for u in rows if u["arm"]["experimental"]["caught"])
                p(f"    category {cat:24s} {fmt_ci(k, len(rows))}")
        p("")

    p("## Gate verdicts")
    gates = gate_verdicts(results, drift_total, missing_total)
    for k, v in gates.items():
        p(f"  {k}: {v}")
    text = "\n".join(lines)
    (out_dir / "summary.txt").write_text(text + "\n")

    flags = []
    for pop, r in results.items():
        for u in r["units"]:
            for arm in r["arms"]:
                if u["arm"][arm]["caught"]:
                    flags.append({
                        "population": pop, "merge_id": u["merge_id"], "arm": arm,
                        "category": u["category"],
                        "flag_lanes": u["arm"][arm]["flag_lanes"],
                        "files": {fid: f for fid, f in u["files"].items()},
                    })
    (out_dir / "flags.json").write_text(json.dumps(flags, indent=1))
    drift = [d for r in results.values() for d in r["drift"]]
    if drift:
        (out_dir / "classifier_drift.json").write_text(json.dumps(drift, indent=1))
    missing = [m for r in results.values() for m in r["missing"]]
    if missing:
        (out_dir / "missing_keys.json").write_text(json.dumps(missing, indent=1))
    (out_dir / "gd3.json").write_text(json.dumps(gates, indent=1))

    for pop, r in results.items():
        with open(out_dir / f"units_{pop}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["merge_id", "category", "n_files", "n_diverged",
                        *(f"{a}_status" for a in r["arms"]),
                        *(f"{a}_flag_lanes" for a in r["arms"])])
            for u in sorted(r["units"], key=lambda x: x["merge_id"]):
                w.writerow([
                    u["merge_id"], u["category"], u["n_files"], u["n_diverged"],
                    *(u["arm"][a]["status"] for a in r["arms"]),
                    *(";".join(sorted(set(l for _, l in u["arm"][a]["flag_lanes"])))
                      for a in r["arms"]),
                ])
    return text


def gate_verdicts(results, drift_total, missing_total) -> dict:
    gates = {}
    blocked = drift_total or missing_total
    r = results.get("evalctl")
    if r:
        k = sum(1 for u in r["units"] if u["arm"]["experimental"]["caught"])
        kb = sum(1 for u in r["units"] if u["arm"]["baseline"]["caught"])
        gates["GD3(ii) eval-controls experimental flags"] = k
        gates["GD3(ii) eval-controls baseline flags (reported)"] = kb
        gates["GD3(ii)"] = ("BLOCKED (drift/missing rows)" if blocked else
                            "PASS" if k == 0 else "FAIL — STOP, package for Ali")
    r = results.get("spgroup_ctl")
    if r:
        k = sum(1 for u in r["units"] if u["arm"]["experimental"]["caught"])
        gates["GD3(iii) spgroup-clean experimental flags"] = k
        gates["GD3(iii)"] = ("BLOCKED (drift/missing rows)" if blocked else
                             "PASS" if k == 0 else "FAIL — STOP, package for Ali")
    return gates


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--population", choices=sorted(POPULATIONS))
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--shard", default=None, help="K/N deterministic merge split")
    ap.add_argument("--score", action="store_true", help="aggregate caches only")
    ap.add_argument("--smoke", action="store_true", help="run smoke gate only")
    ap.add_argument("--known-answer", type=int, default=0, metavar="N",
                    help="env validation vs committed tune_d3 cache on N merges")
    args = ap.parse_args()

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    commit = assert_frozen_commit()
    assert_flag_free_lanes()

    if args.score:
        labels = final_labels()
        results = {}
        for pop in POPULATIONS:
            r = score_population(pop, out_dir, commit, labels)
            if r:
                results[pop] = r
        if not results:
            sys.exit("ABORT: no caches found to score.")
        text = write_reports(out_dir, commit, results)
        print(text)
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
        sys.exit("choose --population/--smoke/--known-answer/--score")
    cfg = POPULATIONS[args.population]
    preflight(cfg["source"])
    run_smokes(cfg["execs"])
    run_population(args.population, out_dir, commit, args.shard)


if __name__ == "__main__":
    main()
