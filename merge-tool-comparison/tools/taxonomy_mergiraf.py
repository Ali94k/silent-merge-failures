"""Stratum-B Mergiraf pass (ISSUES #30, S1).

Runs the comparator's ``MergirafTool`` (``merge-tools/mergiraf:0.17.0``,
Docker-only per CLAUDE.md) over every materialized stratum-B file, producing
``reports_taxonomy/mergiraf_hi.json`` — the stratum-B analogue of the Stage-C
``reports_detection/full/raw_results.json`` Mergiraf merges that stratum A
reuses. Keyed by scenario_id; merged content stored for CLEAN files only
(CONFLICT/CRASH files are dropped from their unit per the divergence rule).

Resumable: existing entries are skipped, cache flushed every 10 merges.
Apple-Silicon note: the image is linux/amd64, so each merge runs under
emulation — expect seconds per file.

    .venv/bin/python tools/taxonomy_mergiraf.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.tools.mergiraf import MergirafTool  # noqa: E402

SCEN = ROOT / "data/scenarios_taxonomy_hi"
OUT = ROOT / "reports_taxonomy/mergiraf_hi.json"
TIMEOUT = int(__import__("os").environ.get("MERGE_TIMEOUT", "180"))


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tool = MergirafTool()
    cache = json.loads(OUT.read_text()) if OUT.exists() else {}
    files = sorted(SCEN.glob("*.json"))
    total = len(files)
    print(f"mergiraf_hi: {total} stratum-B files, {len(cache)} already cached, "
          f"image={tool.docker_image} timeout={TIMEOUT}s", flush=True)

    done = 0
    for i, f in enumerate(files):
        s = json.loads(f.read_text())
        sid = s["scenario_id"]
        if sid in cache:
            continue
        r = tool.merge(s["base_content"], s["ours_content"], s["theirs_content"], timeout=TIMEOUT)
        oc = r.outcome.value
        cache[sid] = {
            "outcome": oc,
            "merged": r.merged_content if oc == "clean" else None,
            "conflict_count": r.conflict_count,
            "rt": round(r.runtime_seconds, 2),
        }
        done += 1
        if done % 10 == 0:
            OUT.write_text(json.dumps(cache, indent=2))
            print(f"  [{i + 1}/{total}] {sid[:66]} -> {oc}", flush=True)

    OUT.write_text(json.dumps(cache, indent=2))
    print("DONE mergiraf_hi:", dict(Counter(v["outcome"] for v in cache.values())),
          "| entries", len(cache), flush=True)


if __name__ == "__main__":
    main()
