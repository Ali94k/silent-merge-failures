"""GD2(iii) tune-control run for one detector-cycle lane (ISSUES #31).

Runs a single experimental lane over the materialized tune-controls
(`data/scenarios_detector_tune/`, n=100 merges — committed list
`reports_detectors/controls/tune_controls.csv`) and reports every FLAG /
UNANALYZABLE file. Gate: **0 flags**; any flag is fixed in-session (plan §5
GD2 — tuning is allowed here and only here). Local execution is the plan's
documented exception to the AWS-over-local rule (bounded iterative tuning).

Reuses the Stage-C harness machinery (tools/detect_validate.py): the same
Mergiraf image reproduces each merged file (CONFLICT/CRASH files are
MERGE_DIVERGED and skipped — a textual conflict is not a silent merge), the
same cache/verdict conventions apply. Results cache per (scenario, lane,
driver-commit) in <out>/raw_results.json — reruns after a lane fix rescore
detectors without re-merging.

A vacuous run cannot pass silently: every lane's LANES registry row carries
an embedded positive micro-fixture (the P1 shape from that lane's test
file), exercised before scoring — the run ABORTs unless it FLAGs. This
catches a missing experimental-flag env or a lane that stopped firing.

Usage:
    .venv/bin/python tools/detector_tune_run.py --lane ImportPruneUsage \
        --out reports_detectors/tune_d1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from collections import Counter
from pathlib import Path

os.environ["SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"] = "1"  # before lane import

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT / "tools"))  # detect_validate is a script, not a pkg

from detect_validate import (  # noqa: E402
    MERGIRAF_IMAGE, driver_commit, group_by_merge, load_scenarios, preflight,
    reproduce_merge, run_detector,
)
from strategies.joern_strategies.infinite_loop import JoernInfiniteLoopStrategy  # noqa: E402
from strategies.joern_strategies.invalid_loop_bounds import JoernInvalidLoopBoundsStrategy  # noqa: E402
from strategies.joern_strategies.taint_check import JoernDataFlowInterferenceStrategy  # noqa: E402
from strategies.joern_strategies.unresolved_reference import JoernUnresolvedReferenceStrategy  # noqa: E402
from strategies.rm2_strategies.rename_conflict import RM2RenameConflictStrategy  # noqa: E402
from strategies.rm2_strategies.signature_stale_call import SignatureStaleCallStrategy  # noqa: E402
from strategies.text_strategies.import_prune_usage import ImportPruneUsageStrategy  # noqa: E402

# One registry row per lane: (strategy class, smoke-fixture builder). The key
# is the --lane CLI value AND must equal the strategy's .name property (the
# cache key and report labels use it). Co-locating the smoke builder makes a
# half-registered lane impossible. S-D4 added the five default lanes so
# GD2(iii) can run the FULL S-D5 experimental-arm composition ("interactions
# count") — their smoke shapes come from each lane's own test file.
LANES = {
    "ImportPruneUsage": (ImportPruneUsageStrategy, lambda: _smoke_import_prune()),
    "SignatureStaleCall": (SignatureStaleCallStrategy, lambda: _smoke_signature_stale_call()),
    "JoernUnresolvedReference": (JoernUnresolvedReferenceStrategy, lambda: _smoke_unresolved_reference()),
    "RM2RenameConflict": (RM2RenameConflictStrategy, lambda: _smoke_rename_conflict()),
    "JoernDataFlowInterference": (JoernDataFlowInterferenceStrategy, lambda: _smoke_dataflow_interference()),
    "JoernInfiniteLoop": (JoernInfiniteLoopStrategy, lambda: _smoke_infinite_loop()),
    "JoernInvalidLoopBounds": (JoernInvalidLoopBoundsStrategy, lambda: _smoke_invalid_loop_bounds()),
}
# The S-D5 experimental-arm composition (plan §5 GD3): every default lane
# plus the detector-cycle experimental lanes, flag ON. Kept as an explicit
# ordered tuple; the assert makes a half-registered composition impossible
# (a lane added to LANES but not here, or vice versa, aborts at import).
FULL_SUITE = (
    "JoernDataFlowInterference", "JoernUnresolvedReference", "JoernInfiniteLoop",
    "JoernInvalidLoopBounds", "RM2RenameConflict",
    "ImportPruneUsage", "SignatureStaleCall",
)
assert set(FULL_SUITE) == set(LANES), "FULL_SUITE and LANES drifted apart"
DEFAULT_DIR = "data/scenarios_detector_tune"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lane", required=True,
                    help="lane name, comma-separated lane names, or FULL "
                         "(the S-D5 experimental-arm composition)")
    ap.add_argument("--scenarios", default=DEFAULT_DIR)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed-cache", default=None,
                    help="path to a prior tune run's raw_results.json; its "
                         "lane-independent ::__merge__:: entries are copied "
                         "into this run's cache (skips re-merging)")
    args = ap.parse_args()

    lane_names = list(FULL_SUITE) if args.lane == "FULL" else [
        s.strip() for s in args.lane.split(",") if s.strip()]
    unknown = [ln for ln in lane_names if ln not in LANES]
    if unknown:
        # argparse-error semantics (rc 2 + usage), matching the old
        # choices=-based validation: a typo'd lane must not read as a
        # gate FAIL (rc 1) to any wrapper that distinguishes the two.
        ap.error(f"unknown lane(s) {unknown}; known: {sorted(LANES)} or FULL")

    out_dir = ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = out_dir / "raw_results.json"
    cache: dict = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    if args.seed_cache:
        seed = json.loads((ROOT / args.seed_cache).read_text())
        merged_keys = [k for k in seed if "::__merge__::" in k and k not in cache]
        cache.update({k: seed[k] for k in merged_keys})
        print(f"seeded {len(merged_keys)} merge reproductions from {args.seed_cache}",
              flush=True)

    def save() -> None:
        cache_path.write_text(json.dumps(cache))

    commit = driver_commit()
    # Two tune-side cache-key hardenings (S-D4 review):
    # (1) driver_commit() is the last COMMIT touching the driver — blind to
    #     the uncommitted in-session edits that GD2 tuning explicitly allows.
    #     Suffix a digest of the working-tree diff so a lane fix invalidates
    #     stale verdicts instead of serving the pre-fix FLAG verbatim.
    # (2) "::exp1" namespaces these flag-ON rows away from the frozen Stage-C
    #     harness's flag-OFF keys (byte-identical format otherwise): the
    #     widened lanes verdict differently per flag state, so the key spaces
    #     must not be mergeable by accident.
    dirty = subprocess.run(
        ["git", "-C", str(ROOT.parent), "diff", "HEAD", "--",
         "semantic_merge_driver"], capture_output=True, text=True).stdout
    if dirty:
        commit = f"{commit}+dirty.{hashlib.sha1(dirty.encode()).hexdigest()[:8]}"
    commit = f"{commit}::exp1"
    preflight()  # Joern on PATH + Docker + images — all lanes need the trio here

    # ---- vacuous-run guard: every lane must fire on a known positive -------
    strategies = {}
    for lane in lane_names:
        strategy_cls, smoke_builder = LANES[lane]
        strategies[lane] = strategy_cls()
        # Registry-key invariant the LANES comment promises: the key IS the
        # strategy's .name (cache keys and report labels depend on it).
        if strategies[lane].name != lane:
            sys.exit(f"ABORT: LANES key {lane!r} != strategy .name "
                     f"{strategies[lane].name!r} — registry drift.")
        smoke = _smoke_positive(strategies[lane], smoke_builder)
        if smoke["verdict"] != "FLAG":
            sys.exit(f"ABORT: lane {lane} did not fire on the embedded positive "
                     f"micro-fixture (got {smoke['verdict']}) — flag wiring or lane "
                     f"regression; a 0-flag run would be vacuous.")
        print(f"smoke positive: FLAG ok | lane={lane}", flush=True)
    print(f"driver_commit={commit} | lanes: {', '.join(lane_names)}", flush=True)

    scns = load_scenarios(ROOT / args.scenarios)
    groups = group_by_merge(scns)
    print(f"tune-controls: {len(scns)} files / {len(groups)} merges", flush=True)

    file_rows = []
    for i, (mid, ss) in enumerate(sorted(groups.items()), 1):
        for scn in ss:
            merge_rec = reproduce_merge(scn, cache, save)
            if merge_rec["outcome"] != "clean":
                for lane in lane_names:
                    file_rows.append({"merge_id": mid, "scenario_id": scn["scenario_id"],
                                      "lane": lane, "verdict": "DIVERGED", "issues": []})
                continue
            with tempfile.TemporaryDirectory() as td:
                merged_path = Path(td) / Path(scn["file_path"]).name
                merged_written = False
                dirty = False
                for lane in lane_names:
                    key = f"{scn['scenario_id']}::{lane}::{commit}"
                    if key not in cache:
                        if not merged_written:
                            merged_path.write_text(merge_rec["merged"], encoding="utf-8")
                            merged_written = True
                        cache[key] = run_detector(lane, strategies[lane],
                                                  "differential", str(merged_path), scn)
                        dirty = True
                    rec = cache[key]
                    file_rows.append({"merge_id": mid, "scenario_id": scn["scenario_id"],
                                      "lane": lane, "verdict": rec["verdict"],
                                      "issues": rec["issues"]})
                if dirty:
                    save()  # once per scenario: a crash re-runs ≤1 file's lanes
        if i % 10 == 0 or i == len(groups):
            print(f"  [{i}/{len(groups)}] merges done", flush=True)

    counts = Counter(r["verdict"] for r in file_rows)
    flags = [r for r in file_rows if r["verdict"] == "FLAG"]
    unanalyzable = [r for r in file_rows if r["verdict"] == "UNANALYZABLE"]
    flagged_merges = sorted({r["merge_id"] for r in flags})

    lines = [
        f"# GD2(iii) tune-control run — lane(s) {', '.join(lane_names)} @ driver commit {commit}",
        f"# scenarios {args.scenarios} (committed list: "
        f"reports_detectors/controls/tune_controls.csv) | mergiraf {MERGIRAF_IMAGE}",
        "",
        f"merges: {len(groups)} | files×lanes: {len(file_rows)} | "
        f"verdicts: {dict(counts)}",
        f"flagged merges: {len(flagged_merges)} (gate: 0)",
        f"UNANALYZABLE file×lane rows: {len(unanalyzable)} (target: 0)",
        "",
        "per-lane verdicts:",
    ]
    for lane in lane_names:
        lane_counts = Counter(r["verdict"] for r in file_rows if r["lane"] == lane)
        lines.append(f"  {lane}: {dict(lane_counts)}")
    lines.append("")
    for r in flags:
        lines.append(f"FLAG {r['scenario_id']} [{r['lane']}]")
        for i_ in r["issues"]:
            lines.append(f"    L{i_['line']}: {i_['message']}")
    for r in unanalyzable:
        lines.append(f"UNANALYZABLE {r['scenario_id']} [{r['lane']}]")
        for i_ in r["issues"]:
            lines.append(f"    {i_['message'][:200]}")
    verdict = "PASS" if not flags and not unanalyzable else "FAIL"
    lines += ["", f"GD2(iii) verdict: {verdict}"]

    text = "\n".join(lines)
    (out_dir / "summary.txt").write_text(text + "\n")
    print("\n" + text)
    sys.exit(0 if verdict == "PASS" else 1)


def _smoke_positive(strategy, smoke_builder) -> dict:
    """Per-lane embedded positive micro-fixture (P1 shape from the lane's
    test file), supplied by the lane's LANES registry row. D1's is
    pure-text; D2's needs the real RM2 image — the run requires Docker
    regardless."""
    base, ours, theirs, merged, filename = smoke_builder()
    scn = {"base_content": base, "ours_content": ours, "theirs_content": theirs}
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / filename
        p.write_text(merged, encoding="utf-8")
        return run_detector("smoke", strategy, "differential", str(p), scn)


def _smoke_import_prune():
    base = textwrap.dedent("""\
        package p;
        import com.foo.Gadget;
        public class T {
            public void f(Gadget g) {}
        }
        """)
    ours = textwrap.dedent("""\
        package p;
        public class T {
            public void f() {}
        }
        """)
    theirs = textwrap.dedent("""\
        package p;
        import com.foo.Gadget;
        public class T {
            public void f(Gadget g) {}
            public Gadget make() { return new Gadget(); }
        }
        """)
    merged = textwrap.dedent("""\
        package p;
        public class T {
            public void f() {}
            public Gadget make() { return new Gadget(); }
        }
        """)
    return base, ours, theirs, merged, "T.java"


def _smoke_unresolved_reference():
    """Widened-path positive (S-D4 jcabi shape from test_unresolved_reference):
    one side removed a private static helper the other side's kept tests still
    call. Pure-text detection, so the smoke also survives a broken-Joern env
    (the fail-closed inconclusive Issue rides with the genuine one)."""
    base = textwrap.dedent("""\
        public final class RtM {
            public void old() { final Milestones milestones = milestones(); milestones.create("x"); }
            private static Milestones milestones() throws Exception { return null; }
        }
        """)
    ours = textwrap.dedent("""\
        public final class RtM {
            public void old() { final Milestones milestones = repo.milestones(); milestones.create("x"); }
        }
        """)
    theirs = textwrap.dedent("""\
        public final class RtM {
            public void old() { final Milestones milestones = milestones(); milestones.create("x"); }
            public void iteratesIssues() { final Milestones milestones = milestones(); }
            private static Milestones milestones() throws Exception { return null; }
        }
        """)
    merged = textwrap.dedent("""\
        public final class RtM {
            public void old() { final Milestones milestones = repo.milestones(); milestones.create("x"); }
            public void iteratesIssues() { final Milestones milestones = milestones(); }
        }
        """)
    return base, ours, theirs, merged, "RtM.java"


def _smoke_rename_conflict():
    """Rename Method + stale caller (test_rename_conflict integration shape);
    needs the real RM2 image — the run requires Docker regardless."""
    base = textwrap.dedent("""\
        package com.example;
        public class Foo {
            public int oldName(int a, int b) { return a + b; }
            public int caller() { return oldName(1, 2); }
        }
        """)
    ours = textwrap.dedent("""\
        package com.example;
        public class Foo {
            public int newName(int a, int b) { return a + b; }
            public int caller() { return newName(1, 2); }
        }
        """)
    theirs = textwrap.dedent("""\
        package com.example;
        public class Foo {
            public int oldName(int a, int b) { return a + b; }
            public int caller() { return oldName(1, 2); }
            public int extra() { return oldName(3, 4); }
        }
        """)
    merged = textwrap.dedent("""\
        package com.example;
        public class Foo {
            public int newName(int a, int b) { return a + b; }
            public int caller() { return newName(1, 2); }
            public int extra() { return oldName(3, 4); }
        }
        """)
    return base, ours, theirs, merged, "Foo.java"


def _smoke_dataflow_interference():
    """Canonical clear→read pattern (test_dataflow_interference shapes):
    ours adds the clear, theirs adds the read, neither parent alone is stale."""
    base = textwrap.dedent("""\
        public class TaskManager {
            private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

            public void run() {
                pendingTasks.add("init");
            }
        }
        """)
    ours = textwrap.dedent("""\
        public class TaskManager {
            private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

            public void run() {
                pendingTasks.add("init");
                pendingTasks.clear();
            }
        }
        """)
    theirs = textwrap.dedent("""\
        public class TaskManager {
            private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

            public void run() {
                pendingTasks.add("init");
                for (String task : pendingTasks) {
                    System.out.println("Processing " + task);
                }
            }
        }
        """)
    merged = textwrap.dedent("""\
        public class TaskManager {
            private java.util.List<String> pendingTasks = new java.util.ArrayList<>();

            public void run() {
                pendingTasks.add("init");
                pendingTasks.clear();
                for (String task : pendingTasks) {
                    System.out.println("Processing " + task);
                }
            }
        }
        """)
    return base, ours, theirs, merged, "TaskManager.java"


def _smoke_infinite_loop():
    """Merge-induced no-exit loop (test_infinite_loop SPIN shape)."""
    calm = textwrap.dedent("""\
        public class Loops {
            private int count = 0;
            public void calm() { count++; }
        }
        """)
    merged = textwrap.dedent("""\
        public class Loops {
            private int count = 0;
            public void spin() {
                while (true) { count++; }
            }
        }
        """)
    return calm, calm, calm, merged, "Loops.java"


def _smoke_invalid_loop_bounds():
    """Dead loop start>end (test_invalid_loop shape; merged-only detection)."""
    calm = textwrap.dedent("""\
        public class BatchProcessor {
            public void processItems() {
            }
        }
        """)
    merged = textwrap.dedent("""\
        public class BatchProcessor {
            public void processItems() {
                for (int i = 15; i < 10; i++) {
                    System.out.println(i);
                }
            }
        }
        """)
    return calm, calm, calm, merged, "BatchProcessor.java"


def _smoke_signature_stale_call():
    base = textwrap.dedent("""\
        package p;
        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }
            public void go() {
                send("h", 1);
            }
        }
        """)
    ours = textwrap.dedent("""\
        package p;
        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }
            public void go() {
                send("h", 1, true);
            }
        }
        """)
    theirs = textwrap.dedent("""\
        package p;
        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }
            public void go() {
                send("h", 1);
            }
            public void alert() {
                send("alert.example", 9090);
            }
        }
        """)
    merged = textwrap.dedent("""\
        package p;
        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }
            public void go() {
                send("h", 1, true);
            }
            public void alert() {
                send("alert.example", 9090);
            }
        }
        """)
    return base, ours, theirs, merged, "Notifier.java"




if __name__ == "__main__":
    main()
