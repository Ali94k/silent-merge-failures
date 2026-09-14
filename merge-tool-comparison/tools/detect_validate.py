"""Detection-validation pilot harness — Stage A of the P1 plan.

Runs the semantic_merge_driver's four detection strategies, driver-faithfully
and unmodified (v1), over Mergiraf-reproduced merged files of the
`semantic` (mergiraf == Tests_failed, positives) and `semantic_ctl`
(Tests_passed, controls) scenario pools, and reports:

  R1 — blocked controls / n   (false-alarm + fail-closed cost per good merge)
  R2 — blocked positives / n  (detection rate on real silent failures)

both with Wilson 95% CIs, per-detector breakdowns, and the G0 calibration
stats (median per-merge runtime, UNANALYZABLE file fraction). Spec:
outputs/p1-detection-validation-plan.md §4–§5.

Per scenario file:
  1. Reproduce the merged file with the comparator's Mergiraf adapter
     (merge-tools/mergiraf:0.17.0 — same image as the driver backend).
     File-level CONFLICT/CRASH/TIMEOUT -> MERGE_DIVERGED, detectors skipped
     (a textual conflict is not a silent merge; the driver would surface it).
  2. Run the four strategies exactly as the driver invokes them:
       JoernDataFlowInterference.analyze(merged, base, ours, theirs)  [differential]
       JoernInfiniteLoop.analyze(merged)
       JoernInvalidLoopBounds.analyze(merged)
       RM2RenameConflict.analyze(merged, base)
  3. Verdict per detector: CLEAN / FLAG (genuine issues) / UNANALYZABLE
     (fail-closed "inconclusive" result or a raised exception — counts as a
     BLOCK, matching deployment semantics).
Aggregation is per merge, any-file-flag (plan §3): a merge is BLOCKED if any
of its non-diverged files FLAGs or is UNANALYZABLE; a merge whose files all
diverged leaves the sample (counted + reported — itself a granularity finding).

G0 abort thresholds (plan §5), checked after every completed merge once >=5
merges are scored: median per-merge runtime > 20 min OR UNANALYZABLE file
fraction > 30% -> write partial reports, exit 2.

G1 harness sanity (--inject-sanity): splice the canonical clear->read pattern
from semantic_merge_driver/tests/data/dfi_stale_read/ into 10 control
merged-files and require the differential DFI detector to fire 10/10. Scoring
refuses to run until sanity.json records a pass (override: SKIP_SANITY=1).

Resumable: every Mergiraf merge and detector result is cached in
<out>/raw_results.json keyed (scenario_id, step, driver_commit); a Docker +
Joern preflight aborts BEFORE running anything so a down daemon cannot poison
the cache. Detectors are read-only here — no driver code is touched (Stage B).

Phase-2b (research/outputs/phase2b-recon.md): --merged-source developer scores
the shipped developer_resolution instead of a Mergiraf re-merge (oracle-faithful
for externally labeled benchmarks); scenario `category` fields feed a
per-category recall section. One --out dir == one merged-source (guarded).

Usage:
    .venv/bin/python tools/detect_validate.py --inject-sanity
    .venv/bin/python tools/detect_validate.py data/scenarios_semantic data/scenarios_semantic_ctl
    .venv/bin/python tools/detect_validate.py data/scenarios_phase2b data/scenarios_phase2b_ctl \
        --merged-source developer --out reports_detection/phase2b/dev
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import glob
import io
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # merge-tool-comparison/
DRIVER_ROOT = ROOT.parent / "semantic_merge_driver"
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(DRIVER_ROOT))                   # after ROOT: comparator's
                                                       # `tests` pkg must win

from src.core.interfaces import MergeOutcome  # noqa: E402
from src.tools.mergiraf import MergirafTool  # noqa: E402
from strategies.joern_strategies.infinite_loop import JoernInfiniteLoopStrategy  # noqa: E402
from strategies.joern_strategies.invalid_loop_bounds import JoernInvalidLoopBoundsStrategy  # noqa: E402
from strategies.joern_strategies.taint_check import JoernDataFlowInterferenceStrategy  # noqa: E402
from strategies.joern_strategies.unresolved_reference import JoernUnresolvedReferenceStrategy  # noqa: E402
from strategies.rm2_strategies.rename_conflict import RM2RenameConflictStrategy  # noqa: E402

MERGIRAF_IMAGE = "merge-tools/mergiraf:0.17.0"
RM2_IMAGE = "merge-tools/refactoring-miner:2.4.0"
DEFAULT_POS = "data/scenarios_semantic"
DEFAULT_CTL = "data/scenarios_semantic_ctl"
DEFAULT_OUT = "reports_detection/pilot"

G0_MIN_MERGES = 5            # don't evaluate abort thresholds on tiny samples
G0_MEDIAN_RUNTIME_S = 20 * 60
G0_UNANALYZABLE_FRAC = 0.30
SANITY_N = 10

# invocation mode per detector — exactly how core/driver.py calls them.
# Since Stage B (v2) every driver strategy receives base+ours+theirs (the
# driver always passed them; v2 strategies actually use them), so every mode
# is "differential". The merged_only/base_merged branches remain for tests.
DETECTORS = (
    ("JoernDataFlowInterference", JoernDataFlowInterferenceStrategy(), "differential"),
    ("JoernUnresolvedReference", JoernUnresolvedReferenceStrategy(), "differential"),
    ("JoernInfiniteLoop", JoernInfiniteLoopStrategy(), "differential"),
    ("JoernInvalidLoopBounds", JoernInvalidLoopBoundsStrategy(), "differential"),
    ("RM2RenameConflict", RM2RenameConflictStrategy(), "differential"),
)

# Canonical clear->read pattern (tests/data/dfi_stale_read/ merged shape) as a
# self-contained package-private class, appendable to any control merged-file.
# The (method, collection) pair exists in neither parent, so the differential
# detector must flag it as merge-induced.
SANITY_SNIPPET = """
class MergeSanityStaleReadProbe {
    private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

    public void run() {
        pendingTasks.add("init");
        pendingTasks.clear();
        for (String task : pendingTasks) {
            System.out.println("Processing " + task);
        }
    }
}
"""


# --------------------------------------------------------------------------- #
# statistics (Wilson helper pattern from tools/migrate_decl_w3.py)
# --------------------------------------------------------------------------- #
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
    return f"{k}/{n} = {p:.3f} [{lo:.3f}, {hi:.3f}]"


# --------------------------------------------------------------------------- #
# scenario loading / grouping
# --------------------------------------------------------------------------- #
def merge_id_of(scn: dict) -> str:
    return scn.get("merge_id") or f"{scn['repo_name']}__{scn['merge_commit'][:10]}"


def load_scenarios(d: Path) -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(d / "*.json"))):
        out.append(json.load(open(f)))
    return out


def group_by_merge(scns: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for s in scns:
        groups.setdefault(merge_id_of(s), []).append(s)
    return groups


# --------------------------------------------------------------------------- #
# merge reproduction + detector execution
# --------------------------------------------------------------------------- #
def driver_commit() -> str:
    """Last commit touching the driver — the detector-freeze cache key (G2).

    DRIVER_COMMIT env overrides (git-archive deployments have no .git —
    same convention as tools/whole_driver_eval.py)."""
    override = os.environ.get("DRIVER_COMMIT")
    if override:
        return override
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT.parent), "log", "-1", "--format=%h",
             "--", "semantic_merge_driver"],
            capture_output=True, text=True, check=True,
        ).stdout.strip() or "unknown"
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def reproduce_merge(scn: dict, cache: dict, save, source: str = "mergiraf") -> dict:
    """Merged-file provider, cached. Returns {outcome, merged, rt}.

    source="mergiraf"  — file-level re-merge with the driver's default backend
                         (deployment-faithful; CONFLICT/CRASH -> diverged).
    source="developer" — the scenario's shipped developer_resolution
                         (oracle-faithful: what externally labeled benchmarks
                         describe; always "clean", no Docker call).
    """
    if source == "developer":
        key = f"{scn['scenario_id']}::__merge__::developer"
        if key not in cache:
            cache[key] = {"outcome": "clean",
                          "merged": scn["developer_resolution"], "rt": 0.0}
            save()
        return cache[key]
    key = f"{scn['scenario_id']}::__merge__::{MERGIRAF_IMAGE}"
    if key not in cache:
        res = MergirafTool().merge(
            scn["base_content"], scn["ours_content"], scn["theirs_content"],
            timeout=120,
        )
        cache[key] = {
            "outcome": res.outcome.value,
            "merged": res.merged_content if res.outcome == MergeOutcome.CLEAN else None,
            "rt": round(res.runtime_seconds, 3),
        }
        save()
    return cache[key]


def verdict_of(result) -> str:
    """CLEAN / FLAG / UNANALYZABLE from a driver AnalysisResult.

    All four strategies mark their fail-closed paths with "inconclusive" in
    the Issue message (see test_fail_closed.py); a result with only such
    issues is a harness/parse failure, not a detection. Genuine issues win if
    ever mixed — both verdicts block, but only FLAG enters adjudication.
    """
    if result.is_clean:
        return "CLEAN"
    genuine = [i for i in result.issues if "inconclusive" not in i.message]
    return "FLAG" if genuine else "UNANALYZABLE"


def run_detector(name: str, strategy, mode: str, merged_path: str, scn: dict) -> dict:
    """One strategy on one merged file, driver-faithful. Never raises."""
    t0 = time.monotonic()
    try:
        # invalid_loop_bounds print()s raw Joern output; keep our log readable.
        with contextlib.redirect_stdout(io.StringIO()):
            if mode == "differential":
                result = strategy.analyze(
                    merged_path,
                    base_content=scn["base_content"],
                    ours_content=scn["ours_content"],
                    theirs_content=scn["theirs_content"],
                )
            elif mode == "base_merged":
                result = strategy.analyze(merged_path, base_content=scn["base_content"])
            else:
                result = strategy.analyze(merged_path)
    except Exception as e:  # noqa: BLE001 — any escape is a fail-closed block
        return {
            "verdict": "UNANALYZABLE",
            "issues": [{"line": 0, "severity": "CRITICAL",
                        "message": f"harness: strategy raised {e!r}"}],
            "runtime_s": round(time.monotonic() - t0, 3),
        }
    return {
        "verdict": verdict_of(result),
        "issues": [{"line": i.line_number, "severity": i.severity, "message": i.message}
                   for i in result.issues],
        "runtime_s": round(time.monotonic() - t0, 3),
    }


def analyze_file(scn: dict, merged_content: str, cache: dict, save, commit: str) -> dict:
    """All four detectors on one reproduced merged file (cached per detector)."""
    detectors = {}
    with tempfile.TemporaryDirectory() as td:
        merged_path = Path(td) / Path(scn["file_path"]).name
        merged_path.write_text(merged_content, encoding="utf-8")
        for name, strategy, mode in DETECTORS:
            key = f"{scn['scenario_id']}::{name}::{commit}"
            if key not in cache:
                cache[key] = run_detector(name, strategy, mode, str(merged_path), scn)
                save()
            detectors[name] = cache[key]
    return detectors


def file_verdict(detectors: dict) -> str:
    verdicts = {d["verdict"] for d in detectors.values()}
    if "FLAG" in verdicts:
        return "FLAG"
    if "UNANALYZABLE" in verdicts:
        return "UNANALYZABLE"
    return "CLEAN"


# --------------------------------------------------------------------------- #
# per-merge aggregation (plan §3: any-file-flag, diverged files drop out)
# --------------------------------------------------------------------------- #
def aggregate_merges(file_records: list[dict]) -> list[dict]:
    """Collapse per-file records into per-merge rows.

    status: BLOCKED   — any scored file FLAGs or is UNANALYZABLE
            PASSED    — all scored files CLEAN
            ALL_DIVERGED — every file diverged at the merge step (leaves the
                           sample; reported, not scored)
    block_reason: "flag" if any file FLAGged, else "fail_closed".
    """
    merges: dict[str, list[dict]] = {}
    for fr in file_records:
        merges.setdefault(fr["merge_id"], []).append(fr)

    out = []
    for mid, frs in merges.items():
        scored = [f for f in frs if f["merge_outcome"] == "clean"]
        diverged = [f for f in frs if f["merge_outcome"] != "clean"]
        runtime = round(sum(f["runtime_s"] for f in frs), 3)
        if not scored:
            status, reason = "ALL_DIVERGED", None
        else:
            verdicts = [f["file_verdict"] for f in scored]
            if "FLAG" in verdicts:
                status, reason = "BLOCKED", "flag"
            elif "UNANALYZABLE" in verdicts:
                status, reason = "BLOCKED", "fail_closed"
            else:
                status, reason = "PASSED", None
        out.append({
            "merge_id": mid,
            "arm": frs[0]["arm"],
            "category": frs[0].get("category", "unknown"),
            "n_files": len(frs),
            "n_diverged": len(diverged),
            "n_scored": len(scored),
            "status": status,
            "block_reason": reason,
            "runtime_s": runtime,
        })
    return out


def g0_violation(merge_rows: list[dict], file_records: list[dict]) -> str | None:
    """Abort-threshold check (plan §5 G0). Returns a reason string or None."""
    if len(merge_rows) < G0_MIN_MERGES:
        return None
    med = statistics.median(m["runtime_s"] for m in merge_rows)
    if med > G0_MEDIAN_RUNTIME_S:
        return (f"median per-merge runtime {med:.0f}s > {G0_MEDIAN_RUNTIME_S}s "
                f"over {len(merge_rows)} merges")
    analyzed = [f for f in file_records if f["merge_outcome"] == "clean"]
    if len(analyzed) >= 10:
        unanalyzable = sum(
            1 for f in analyzed
            if any(d["verdict"] == "UNANALYZABLE" for d in f["detectors"].values())
        )
        frac = unanalyzable / len(analyzed)
        if frac > G0_UNANALYZABLE_FRAC:
            return (f"UNANALYZABLE file fraction {frac:.2f} "
                    f"({unanalyzable}/{len(analyzed)}) > {G0_UNANALYZABLE_FRAC}")
    return None


def guard_out_dir_mode(out_dir: Path, source: str) -> None:
    """One out-dir == one merged-source: a cache written under the other mode
    would silently mix merged contents under the same detector keys."""
    meta_path = out_dir / "meta.json"
    if meta_path.exists():
        prior = json.loads(meta_path.read_text()).get("merged_source")
        if prior != source:
            sys.exit(f"ABORT: {out_dir} was populated with --merged-source={prior}; "
                     f"use a fresh --out for --merged-source={source}.")
    else:
        meta_path.write_text(json.dumps({"merged_source": source}))


# --------------------------------------------------------------------------- #
# preflight (migrate_decl_w3 pattern: abort before anything can poison cache)
# --------------------------------------------------------------------------- #
def preflight(source: str = "mergiraf") -> None:
    if shutil.which("joern-parse") is None or shutil.which("joern") is None:
        sys.exit("ABORT: joern-parse / joern not on PATH (Joern strategies need them).")
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=30, check=True)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ABORT: Docker not available — start Docker Desktop, then re-run.\n  ({str(e)[:160]})")
    have = subprocess.run(
        ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
        capture_output=True, text=True,
    ).stdout
    needed = (RM2_IMAGE,) if source == "developer" else (MERGIRAF_IMAGE, RM2_IMAGE)
    missing = [im for im in needed if im not in have]
    if missing:
        sys.exit("ABORT: missing Docker images:\n  " + "\n  ".join(missing))


# --------------------------------------------------------------------------- #
# G1 — inject-sanity (positive control)
# --------------------------------------------------------------------------- #
def inject_snippet(merged_content: str) -> str:
    sep = "" if merged_content.endswith("\n") else "\n"
    return merged_content + sep + SANITY_SNIPPET


def run_sanity(ctl_scns: list[dict], cache: dict, save, out_dir: Path, commit: str,
               source: str = "mergiraf") -> bool:
    """Splice the canonical pattern into SANITY_N control merged-files; the
    differential DFI detector must fire on every one (10/10)."""
    taint = DETECTORS[0]
    assert taint[0] == "JoernDataFlowInterference"
    candidates = []
    for scn in ctl_scns:
        rec = reproduce_merge(scn, cache, save, source)
        if rec["outcome"] == "clean":
            candidates.append((scn, rec["merged"]))
        if len(candidates) >= SANITY_N:
            break
    if len(candidates) < SANITY_N:
        print(f"G1 FAIL: only {len(candidates)} clean control merged-files available "
              f"(need {SANITY_N}).")
        return False

    details = []
    fired = 0
    for i, (scn, merged) in enumerate(candidates, 1):
        key = f"{scn['scenario_id']}::__sanity__::{commit}"
        if key not in cache:
            with tempfile.TemporaryDirectory() as td:
                p = Path(td) / Path(scn["file_path"]).name
                p.write_text(inject_snippet(merged), encoding="utf-8")
                cache[key] = run_detector(taint[0], taint[1], taint[2], str(p), scn)
            save()
        rec = cache[key]
        hit = rec["verdict"] == "FLAG" and any(
            "stale read" in i_["message"].lower() for i_ in rec["issues"]
        )
        fired += hit
        details.append({"scenario_id": scn["scenario_id"], "verdict": rec["verdict"],
                        "fired": hit})
        print(f"  [sanity {i}/{SANITY_N}] {'FIRED' if hit else 'MISSED ('+rec['verdict']+')'}"
              f"  {scn['scenario_id'][:60]}", flush=True)

    passed = fired == SANITY_N
    (out_dir / "sanity.json").write_text(json.dumps(
        {"pass": passed, "fired": fired, "n": SANITY_N,
         "driver_commit": commit, "details": details}, indent=2))
    print(f"G1 sanity: {fired}/{SANITY_N} fired -> {'PASS' if passed else 'FAIL'}")
    return passed


# --------------------------------------------------------------------------- #
# reports
# --------------------------------------------------------------------------- #
def write_reports(out_dir: Path, file_records: list[dict], merge_rows: list[dict],
                  commit: str, aborted: str | None,
                  merged_source: str = "mergiraf") -> str:
    det_names = [d[0] for d in DETECTORS]

    with open(out_dir / "scenarios.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "merge_id", "scenario_id", "file_path", "merge_outcome",
                    "category", *det_names, "file_verdict", "runtime_s"])
        for fr in file_records:
            w.writerow([
                fr["arm"], fr["merge_id"], fr["scenario_id"], fr["file_path"],
                fr["merge_outcome"], fr.get("category", "unknown"),
                *[fr["detectors"].get(n, {}).get("verdict", "") for n in det_names],
                fr["file_verdict"], fr["runtime_s"],
            ])

    # misses_to_classify.csv — unblocked positives; adjudication is MANUAL
    # (plan §4.7), the label columns stay empty here by design.
    misses = [m for m in merge_rows if m["arm"] == "pos" and m["status"] == "PASSED"]
    files_by_merge: dict[str, list[dict]] = {}
    for fr in file_records:
        files_by_merge.setdefault(fr["merge_id"], []).append(fr)
    with open(out_dir / "misses_to_classify.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["merge_id", "n_files", "n_diverged", "file_paths",
                    "suspected_category(1-7|none)", "rationale"])
        for m in misses:
            paths = ";".join(f["file_path"] for f in files_by_merge[m["merge_id"]])
            w.writerow([m["merge_id"], m["n_files"], m["n_diverged"], paths, "", ""])

    lines: list[str] = []
    p = lines.append
    p(f"# Detection-validation pilot (detectors at driver commit {commit}; "
      f"NOTE: an uncommitted working tree still reports the last commit)")
    p(f"# spec: outputs/p1-detection-validation-plan.md §4–§5"
      f" | merged_source={merged_source}")
    if aborted:
        p("")
        p(f"## *** G0 ABORT: {aborted} ***")
        p("## Results below are PARTIAL — fix harness/scope before scaling (plan §8:")
        p("## shared-CPG is the sanctioned fallback; document the deviation if used).")
    p("")

    if merged_source == "developer":
        arm_labels = (("pos", "positives (externally labeled interference)"),
                      ("ctl", "controls (externally labeled interference-free)"))
    else:
        arm_labels = (("pos", "positives (mergiraf=Tests_failed)"),
                      ("ctl", "controls (mergiraf=Tests_passed)"))
    for arm, label in arm_labels:
        rows = [m for m in merge_rows if m["arm"] == arm]
        frs = [f for f in file_records if f["arm"] == arm]
        if not rows:
            continue
        n_all = len(rows)
        left = [m for m in rows if m["status"] == "ALL_DIVERGED"]
        scored = [m for m in rows if m["status"] != "ALL_DIVERGED"]
        blocked = [m for m in scored if m["status"] == "BLOCKED"]
        by_flag = [m for m in blocked if m["block_reason"] == "flag"]
        by_fc = [m for m in blocked if m["block_reason"] == "fail_closed"]
        div_files = Counter(f["merge_outcome"] for f in frs if f["merge_outcome"] != "clean")
        metric = "R2 (detection rate)" if arm == "pos" else "R1 (block rate on good merges)"
        p(f"## {label} — {metric}")
        p(f"  merges materialized      : {n_all}  ({len(frs)} files)")
        p(f"  files MERGE_DIVERGED     : {sum(div_files.values())}  {dict(div_files) or ''}")
        p(f"  merges all-files-diverged: {len(left)} (leave the sample — granularity finding)")
        p(f"  merges scored            : {len(scored)}")
        p(f"  blocked                  : {fmt_ci(len(blocked), len(scored))}")
        p(f"    via detector FLAG      : {len(by_flag)}")
        p(f"    via fail-closed only   : {len(by_fc)}")
        p("")

    # Per-category recall — only meaningful when scenarios carry categories
    # (Phase-2b labeled pools; legacy Schesch pools are all "unknown").
    pos_rows = [m for m in merge_rows if m["arm"] == "pos"
                and m["status"] != "ALL_DIVERGED"]
    if any(m["category"] not in ("unknown",) for m in pos_rows):
        p("## Per-category recall (positives, unit-level)")
        cats = Counter(m["category"] for m in pos_rows)
        for cat in sorted(cats):
            rows = [m for m in pos_rows if m["category"] == cat]
            hit = [m for m in rows if m["status"] == "BLOCKED"]
            by_flag = sum(1 for m in hit if m["block_reason"] == "flag")
            p(f"  {cat:24s} recall {fmt_ci(len(hit), len(rows))} "
              f"(flag {by_flag}, fail-closed {len(hit) - by_flag})")
        p("")

    p("## Per-detector breakdown (clean-merged files only)")
    analyzed = [f for f in file_records if f["merge_outcome"] == "clean"]
    p(f"  {'detector':28s} {'FLAG':>5} {'UNANALYZ':>9} {'CLEAN':>6} {'mean_rt_s':>10} {'median_rt_s':>12}")
    for name in det_names:
        recs = [f["detectors"][name] for f in analyzed if name in f["detectors"]]
        if not recs:
            continue
        cnt = Counter(r["verdict"] for r in recs)
        rts = [r["runtime_s"] for r in recs]
        p(f"  {name:28s} {cnt['FLAG']:>5} {cnt['UNANALYZABLE']:>9} {cnt['CLEAN']:>6} "
          f"{statistics.mean(rts):>10.1f} {statistics.median(rts):>12.1f}")
    p("")

    p("## G0 calibration")
    if merge_rows:
        med = statistics.median(m["runtime_s"] for m in merge_rows)
        p(f"  median per-merge runtime : {med:.0f}s (abort threshold {G0_MEDIAN_RUNTIME_S}s)")
    if analyzed:
        una = sum(1 for f in analyzed
                  if any(d["verdict"] == "UNANALYZABLE" for d in f["detectors"].values()))
        p(f"  UNANALYZABLE file frac   : {una}/{len(analyzed)} = {una/len(analyzed):.2f} "
          f"(abort threshold {G0_UNANALYZABLE_FRAC})")
    p("")

    flags = [f for f in analyzed if f["file_verdict"] == "FLAG"]
    p(f"## FLAGged files — adjudicate every one, written rationale (plan §4.6): {len(flags)}")
    for f in flags:
        p(f"  [{f['arm']}] {f['scenario_id']}")
        for name in det_names:
            rec = f["detectors"].get(name, {})
            if rec.get("verdict") == "FLAG":
                for i_ in rec["issues"]:
                    p(f"      {name} L{i_['line']}: {i_['message'][:120]}")
    p("")

    text = "\n".join(lines)
    (out_dir / "summary.txt").write_text(text + "\n")
    return text


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pos_dir", nargs="?", default=DEFAULT_POS)
    ap.add_argument("ctl_dir", nargs="?", default=DEFAULT_CTL)
    ap.add_argument("--inject-sanity", action="store_true",
                    help="G1 positive control only; run before scoring")
    ap.add_argument("--merged-source", choices=("mergiraf", "developer"),
                    default="mergiraf",
                    help="mergiraf: re-merge (deployment-faithful); developer: "
                         "score the shipped developer_resolution (oracle-faithful, "
                         "Phase-2b labeled benchmarks)")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = out_dir / "raw_results.json"
    cache: dict = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    guard_out_dir_mode(out_dir, args.merged_source)

    def save() -> None:
        cache_path.write_text(json.dumps(cache))

    commit = driver_commit()
    preflight(args.merged_source)
    print(f"driver_commit={commit} merged_source={args.merged_source} out={out_dir}",
          flush=True)

    ctl_scns = load_scenarios(ROOT / args.ctl_dir)
    if args.inject_sanity:
        ok = run_sanity(ctl_scns, cache, save, out_dir, commit, args.merged_source)
        sys.exit(0 if ok else 1)

    # G1 gate: scoring without a passed sanity run can't distinguish
    # "detectors blind" from "harness broken".
    sanity_file = out_dir / "sanity.json"
    if os.environ.get("SKIP_SANITY") != "1":
        if not sanity_file.exists() or not json.loads(sanity_file.read_text()).get("pass"):
            sys.exit("ABORT: G1 sanity not passed — run --inject-sanity first "
                     "(or SKIP_SANITY=1 to override).")

    pos_scns = load_scenarios(ROOT / args.pos_dir)
    arms = [("pos", group_by_merge(pos_scns)), ("ctl", group_by_merge(ctl_scns))]
    n_merges = sum(len(g) for _, g in arms)
    print(f"positives: {len(pos_scns)} files / {len(arms[0][1])} merges; "
          f"controls: {len(ctl_scns)} files / {len(arms[1][1])} merges", flush=True)

    file_records: list[dict] = []
    merge_rows: list[dict] = []
    done = 0
    aborted: str | None = None
    for arm, groups in arms:
        if aborted:
            break
        for mid, scns in sorted(groups.items()):
            batch = []
            for scn in scns:
                merge_rec = reproduce_merge(scn, cache, save, args.merged_source)
                if merge_rec["outcome"] == "clean":
                    detectors = analyze_file(scn, merge_rec["merged"], cache, save, commit)
                    fv = file_verdict(detectors)
                else:
                    detectors, fv = {}, "DIVERGED"
                rt = round(merge_rec["rt"] + sum(d["runtime_s"] for d in detectors.values()), 3)
                batch.append({
                    "arm": arm, "merge_id": mid, "scenario_id": scn["scenario_id"],
                    "file_path": scn["file_path"], "merge_outcome": merge_rec["outcome"],
                    "category": scn.get("category", "unknown"),
                    "detectors": detectors, "file_verdict": fv, "runtime_s": rt,
                })
                d_str = " ".join(f"{n[:4]}={d['verdict'][:5]}" for n, d in detectors.items())
                print(f"  [{arm} {done+1}/{n_merges}] {scn['scenario_id'][:55]:55s} "
                      f"{merge_rec['outcome']:8s} {d_str} ({rt:.0f}s)", flush=True)
            file_records.extend(batch)
            done += 1
            merge_rows = aggregate_merges(file_records)
            aborted = g0_violation(merge_rows, file_records)
            if aborted:
                print(f"\n*** G0 ABORT after {done}/{n_merges} merges: {aborted}", flush=True)
                break

    text = write_reports(out_dir, file_records, merge_rows, commit, aborted,
                         args.merged_source)
    print("\n" + text)
    print(f"Wrote {out_dir}/summary.txt, scenarios.csv, misses_to_classify.csv")
    sys.exit(2 if aborted else 0)


if __name__ == "__main__":
    main()
