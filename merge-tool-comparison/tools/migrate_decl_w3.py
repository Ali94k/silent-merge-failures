"""MIGRATE_DECL W3 evidence gate — Weave vs Mergiraf (vs git) head-to-head.

The deferred W3/W5 gate (docs/plans/weave-integration.md §W5) asks: does Weave
*strictly outperform* Mergiraf on the MIGRATE_DECL cluster it is meant to own in
the driver's `auto` routing? The existing reports carry only incidental n=19
slices of MIGRATE_DECL from samples selected for other purposes. This harness
runs the targeted comparison the gate actually requires:

  * POOL every distinct, already-materialized + RM2-tagged scenario across
    data/scenarios{,_ci,_expanded,_spork}, recompute its cluster with the
    comparator's own `cluster_of`, and keep CLUSTER (default MIGRATE_DECL). No
    new cloning — these are cached on disk (n≈38, ~2x any single report).
  * Run git-merge-file / mergiraf / weave through the REAL adapters and classify
    each with the comparator's own `classify_result`, so outcomes are
    consistent-by-construction with reports_ci (not a re-implementation).
  * Classify under BOTH oracle modes: `normalized` (google-java-format + AST,
    the canonical oracle) and `raw` (whitespace only). The raw column exposes
    FPs that normalization masks — notably Weave's known field-declaration-loss.
  * Join the Schesch TEST-SUITE label for Mergiraf from result_adjusted.csv.
    The CSV has NO weave column, so Weave has no test-suite label — a documented
    asymmetry (see FINDINGS). The Mergiraf label calibrates how many of its
    dev-mismatch "FPs" are real test failures vs valid-alternative comparator-gap.
  * Report Wilson 95% CIs on precision and clean-correct rate, a paired McNemar
    exact test on clean-correct outcomes, and the decision cross-tabs.

No commit, no push, writes only under reports_migrate_decl/. Resumable: tool
outputs are cached in raw_results.json keyed by (scenario_id, tool); a Docker
preflight aborts BEFORE running anything so a down daemon cannot poison the cache.

Usage:
    ./.venv/bin/python tools/migrate_decl_w3.py            # full run (needs Docker)
    DRYRUN=1 ./.venv/bin/python tools/migrate_decl_w3.py   # selection + stats self-test, no Docker
    CLUSTER=INTRA_BODY ./.venv/bin/python tools/migrate_decl_w3.py
"""
from __future__ import annotations

import csv
import glob
import json
import math
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.core.interfaces import MergeOutcome, MergeResult  # noqa: E402
from src.evaluation.categorizer import cluster_of  # noqa: E402
from src.evaluation.comparator import classify_result  # noqa: E402
from src.tools.git_merge_file import GitMergeFileTool  # noqa: E402
from src.tools.mergiraf import MergirafTool  # noqa: E402
from src.tools.weave import WeaveTool  # noqa: E402

CLUSTER = os.environ.get("CLUSTER", "MIGRATE_DECL")
POOLS = os.environ.get(
    "POOLS",
    "data/scenarios,data/scenarios_ci,data/scenarios_expanded,data/scenarios_spork",
).split(",")
CSV_PATH = ROOT / "data/schesch-dataset/results/reaper/result_adjusted.csv"
OUT = ROOT / "reports_migrate_decl"
CACHE = OUT / "raw_results.json"
TOOLS = [GitMergeFileTool(), MergirafTool(), WeaveTool()]
REQUIRED_IMAGES = [
    "merge-tools/mergiraf:0.17.0",
    "merge-tools/weave:0.3.2",
    "merge-tools/google-java-format:1.22.0",  # tier-2 of contents_match
]


# --------------------------------------------------------------------------- #
# selection + join
# --------------------------------------------------------------------------- #
def load_scenarios() -> list[dict]:
    seen: dict[str, dict] = {}
    for d in POOLS:
        for f in sorted(glob.glob(str(ROOT / d.strip() / "*.json"))):
            s = json.load(open(f))
            sid = s["scenario_id"]
            if sid in seen:
                continue
            refs = s.get("refactorings", {})
            cl = cluster_of(refs.get("ours", []), refs.get("theirs", [])) if refs else "NONE"
            if cl == CLUSTER:
                seen[sid] = s
    return [seen[k] for k in sorted(seen)]


def build_csv_index() -> dict[tuple[str, str], dict]:
    csv.field_size_limit(10 ** 8)
    idx: dict[tuple[str, str], dict] = {}
    with open(CSV_PATH) as fh:
        for r in csv.DictReader(fh):
            idx[(r["repository"].replace("/", "_"), r["merge"])] = r
    return idx


def csv_lookup(idx: dict, scn: dict) -> dict | None:
    key = (scn["repo_name"], scn["merge_commit"])
    if key in idx:
        return idx[key]
    for (rp, mg), r in idx.items():  # prefix tolerance on short SHAs
        if rp == scn["repo_name"] and (mg.startswith(scn["merge_commit"]) or scn["merge_commit"].startswith(mg)):
            return r
    return None


# --------------------------------------------------------------------------- #
# statistics
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


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar (binomial sign test on discordant pairs b, c)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


# --------------------------------------------------------------------------- #
# run + classify
# --------------------------------------------------------------------------- #
def preflight() -> None:
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=30, check=True)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ABORT: Docker not available — start Docker Desktop, then re-run.\n  ({str(e)[:160]})")
    have = subprocess.run(
        ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
        capture_output=True, text=True,
    ).stdout
    missing = [im for im in REQUIRED_IMAGES if im not in have]
    if missing:
        sys.exit(
            "ABORT: missing Docker images required for a valid normalized oracle:\n  "
            + "\n  ".join(missing)
            + "\nBuild them from merge-tool-comparison/docker/<tool>/Dockerfile first."
        )


def to_result(c: dict) -> MergeResult:
    return MergeResult(
        outcome=MergeOutcome(c["outcome"]),
        merged_content=c.get("merged"),
        conflict_count=0,
        runtime_seconds=c.get("rt", 0.0),
    )


def classify_mode(c: dict, scn: dict, mode: str) -> str:
    if mode == "raw":
        os.environ["MERGE_COMPARATOR_FORMATTER"] = "off"
        os.environ["MERGE_COMPARATOR_AST_NORMALIZE"] = "off"
    else:
        os.environ["MERGE_COMPARATOR_FORMATTER"] = "on"
        os.environ["MERGE_COMPARATOR_AST_NORMALIZE"] = "on"
    return classify_result(
        to_result(c),
        scn["developer_resolution"],
        scn["base_content"],
        scn["ours_content"],
        scn["theirs_content"],
    ).value


def run_tools(scns: list[dict]) -> dict:
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    for i, scn in enumerate(scns, 1):
        sid = scn["scenario_id"]
        for tool in TOOLS:
            ck = f"{sid}::{tool.name}"
            if ck in cache:
                continue
            try:
                res = tool.merge(
                    scn["base_content"], scn["ours_content"], scn["theirs_content"], timeout=120
                )
                cache[ck] = {
                    "outcome": res.outcome.value,
                    "merged": res.merged_content,
                    "rt": round(res.runtime_seconds, 3),
                }
            except Exception as e:  # noqa: BLE001
                cache[ck] = {"outcome": "crash", "merged": None, "rt": 0.0, "err": str(e)[:200]}
            CACHE.write_text(json.dumps(cache))
            print(f"  [{i}/{len(scns)}] {tool.name:14s} {cache[ck]['outcome']:8s} {sid[:46]}", flush=True)
    return cache


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #
def fmt_ci(k: int, n: int) -> str:
    p, lo, hi = wilson(k, n)
    return f"{p:.3f} [{lo:.3f}, {hi:.3f}]"


def report(scns: list[dict], cache: dict, idx: dict) -> None:
    toolnames = [t.name for t in TOOLS]
    # per (scenario, tool, mode) classification
    cls = defaultdict(dict)  # sid -> {(tool,mode): class}
    for scn in scns:
        sid = scn["scenario_id"]
        for tn in toolnames:
            c = cache.get(f"{sid}::{tn}")
            if not c:
                continue
            for mode in ("normalized", "raw"):
                cls[sid][(tn, mode)] = classify_mode(c, scn, mode)

    lines: list[str] = []
    p = lines.append
    n = len(scns)
    p(f"# MIGRATE_DECL W3 gate — Weave vs Mergiraf vs git   (n={n} distinct scenarios)")
    p(f"# pools: {', '.join(POOLS)}")
    p("")

    # ---- aggregate per tool per mode ----
    for mode in ("normalized", "raw"):
        p(f"## Aggregate — oracle={mode}")
        p(f"{'tool':16s} {'TP':>3} {'FP':>3} {'TN':>3} {'FN':>3} {'CR':>3}  "
          f"{'precision (Wilson95)':>24}  {'clean-correct rate':>22}  {'mean_rt_s':>9}")
        for tn in toolnames:
            cnt = Counter(cls[sid].get((tn, mode)) for sid in cls)
            tp, fp, tn_, fn, cr = cnt["TP"], cnt["FP"], cnt["TN"], cnt["FN"], cnt["CRASH"]
            rts = [cache[f"{sid}::{tn}"]["rt"] for sid in cls if f"{sid}::{tn}" in cache]
            mean_rt = sum(rts) / len(rts) if rts else 0.0
            prec = fmt_ci(tp, tp + fp) if (tp + fp) else "   n/a (no clean)"
            ccr = fmt_ci(tp, n)
            p(f"{tn:16s} {tp:>3} {fp:>3} {tn_:>3} {fn:>3} {cr:>3}  {prec:>24}  {ccr:>22}  {mean_rt:>9.2f}")
        p("")

    # ---- paired Weave vs Mergiraf on clean-correct (normalized) ----
    p("## Paired Weave vs Mergiraf — clean-correct (TP) outcomes, normalized oracle")
    both_tp = mg_only = wv_only = neither = 0
    for sid in cls:
        mg = cls[sid].get(("mergiraf", "normalized"))
        wv = cls[sid].get(("weave", "normalized"))
        mg_ok, wv_ok = mg == "TP", wv == "TP"
        both_tp += mg_ok and wv_ok
        mg_only += mg_ok and not wv_ok
        wv_only += wv_ok and not mg_ok
        neither += not mg_ok and not wv_ok
    p(f"  both correct           : {both_tp}")
    p(f"  Mergiraf only correct  : {mg_only}   (Weave failed to clean-merge these)")
    p(f"  Weave only correct     : {wv_only}   (the W3 win cell — Weave beats Mergiraf here)")
    p(f"  neither correct        : {neither}")
    p(f"  McNemar exact p (discordant {mg_only} vs {wv_only}) = {mcnemar_exact(mg_only, wv_only):.4f}")
    p("")

    # ---- decision cross-tab: Mergiraf-class x Weave-class (normalized) ----
    p("## Cross-tab — Mergiraf class (rows) x Weave class (cols), normalized")
    classes = ["TP", "FP", "TN", "FN", "CRASH"]
    mat = Counter()
    for sid in cls:
        mat[(cls[sid].get(("mergiraf", "normalized")), cls[sid].get(("weave", "normalized")))] += 1
    p(f"  {'mg\\wv':8s}" + "".join(f"{c:>6}" for c in classes))
    for r in classes:
        p(f"  {r:8s}" + "".join(f"{mat[(r, c)]:>6}" for c in classes))
    p("  (note: Weave TN = entity-level conflict / abstention, not a wrong merge)")
    p("")

    # ---- comparator-gap calibration: Mergiraf dev-class x Schesch test label ----
    p("## Comparator-gap calibration — Mergiraf dev-class (normalized) x Schesch test-suite label")
    p("   (test label is WHOLE-MERGE Mergiraf from result_adjusted.csv; single-file proxy caveat noted by num_diff_files)")
    gap = Counter()
    miss = 0
    for scn in scns:
        sid = scn["scenario_id"]
        row = csv_lookup(idx, scn)
        if row is None:
            miss += 1
            continue
        gap[(cls[sid].get(("mergiraf", "normalized")), row["mergiraf"])] += 1
    labels = ["Tests_passed", "Tests_failed", "Merge_failed"]
    p(f"  {'mg-class':10s}" + "".join(f"{l:>14}" for l in labels))
    for r in ["TP", "FP", "TN", "FN", "CRASH"]:
        if any(gap[(r, l)] for l in labels):
            p(f"  {r:10s}" + "".join(f"{gap[(r, l)]:>14}" for l in labels))
    p(f"  unjoined scenarios: {miss}")
    fp_fail = gap[("FP", "Tests_failed")]
    fp_pass = gap[("FP", "Tests_passed")]
    fp_mf = gap[("FP", "Merge_failed")]
    p(f"  -> of Mergiraf dev-FPs: {fp_fail} truly fail tests (real silent errors), "
      f"{fp_pass} pass tests (valid-alt comparator-gap), {fp_mf} whole-merge Merge_failed (granularity).")
    p("")

    # ---- the money list: every scenario where the tools disagree on clean-correct ----
    p("## Discordant scenarios (Mergiraf vs Weave clean-correct differ, normalized)")
    p(f"  {'scenario':50s} {'mg':>4} {'wv':>4} {'git':>4} {'mg_test':>13} {'nfiles':>6}")
    for scn in sorted(scns, key=lambda s: s["scenario_id"]):
        sid = scn["scenario_id"]
        mg = cls[sid].get(("mergiraf", "normalized"))
        wv = cls[sid].get(("weave", "normalized"))
        if (mg == "TP") == (wv == "TP"):
            continue
        gt = cls[sid].get(("git-merge-file", "normalized"))
        row = csv_lookup(idx, scn)
        p(f"  {sid[:50]:50s} {mg:>4} {wv:>4} {gt:>4} "
          f"{(row['mergiraf'] if row else '?'):>13} {(row['num_diff_files'] if row else '?'):>6}")
    p("")

    # ---- per-scenario CSV ----
    csv_path = OUT / "scenarios.csv"
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["scenario_id", "repo", "file_path", "num_diff_files", "num_diff_hunks",
             "imports_involved", "mergiraf_test_label", "spork_test_label", "gitmerge_ort_test_label"]
            + [f"{t}_{m}" for t in toolnames for m in ("norm", "raw")]
            + [f"{t}_rt" for t in toolnames]
        )
        for scn in sorted(scns, key=lambda s: s["scenario_id"]):
            sid = scn["scenario_id"]
            row = csv_lookup(idx, scn) or {}
            w.writerow(
                [sid, scn["repo_name"], scn["file_path"], row.get("num_diff_files", ""),
                 row.get("num_diff_hunks", ""), row.get("imports_involved", ""),
                 row.get("mergiraf", ""), row.get("spork", ""), row.get("gitmerge_ort", "")]
                + [cls[sid].get((t, "normalized" if m == "norm" else "raw"), "")
                   for t in toolnames for m in ("norm", "raw")]
                + [cache.get(f"{sid}::{t}", {}).get("rt", "") for t in toolnames]
            )

    text = "\n".join(lines)
    (OUT / "summary.txt").write_text(text + "\n")
    print("\n" + text)
    print(f"\nWrote {OUT/'summary.txt'} and {csv_path}")


# --------------------------------------------------------------------------- #
def main() -> None:
    OUT.mkdir(exist_ok=True)
    scns = load_scenarios()
    idx = build_csv_index()
    joined = sum(csv_lookup(idx, s) is not None for s in scns)
    print(f"cluster={CLUSTER} scenarios={len(scns)} csv_join={joined}/{len(scns)}", flush=True)

    if os.environ.get("DRYRUN"):
        # stats self-test on textbook values; no Docker.
        assert abs(wilson(7, 13)[0] - 0.5385) < 1e-3
        lo, hi = wilson(2, 2)[1], wilson(2, 2)[2]
        assert 0.0 <= lo < hi <= 1.0
        assert abs(mcnemar_exact(0, 6) - 2 * (1 / 64)) < 1e-9  # one-sided 6:0 -> 2*(1/2^6)
        assert mcnemar_exact(0, 0) == 1.0
        by_repo = Counter(s["repo_name"] for s in scns)
        print("DRYRUN ok — stats self-test passed.")
        print(f"distinct repos: {len(by_repo)}; top: {by_repo.most_common(5)}")
        return

    preflight()
    cache = run_tools(scns)
    report(scns, cache, idx)


if __name__ == "__main__":
    main()
