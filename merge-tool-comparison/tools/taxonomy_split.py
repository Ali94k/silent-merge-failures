"""Derivation/held-out split + manifest bootstrap (ISSUES #30, S1, protocol §4/§9).

Computes the scored unit population (census -> materialized -> Mergiraf-clean
divergence rule), draws the seeded 60% derivation split stratified by A/B
(SEED=20260709), and writes:

  * reports_taxonomy/split_assignment.csv   (merge_id, stratum, split)
  * reports_taxonomy/manifest.json          (every §9 pinning field known so far)

The split MUST be committed before the first content-bearing API request
(count_tokens / Batches) — this tool makes no network/API calls. It refuses to
run until the stratum-B Mergiraf cache covers every materialized B file, so the
scored population is final before the split is drawn.

    .venv/bin/python tools/taxonomy_split.py
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import taxonomy_common as tc  # noqa: E402

SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
MANIFEST = tc.REPORTS / "manifest.json"
PROMPT_FILES = [
    "phase1_open_coding.md", "phase1_output.schema.json",
    "phase2_consolidation.md", "phase3_closed_coding.md", "phase3_output.schema.json",
]


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _docker_image_id(ref: str) -> str:
    try:
        return subprocess.check_output(
            ["docker", "image", "inspect", ref, "--format", "{{.Id}}"],
            text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable"


def _check_prereqs(units: dict) -> None:
    """Every materialized stratum-B file must have a Mergiraf outcome cached."""
    mgi = tc.mergiraf_index()
    missing = []
    for u in units.values():
        if u["stratum"] != "B":
            continue
        for s in u["files"]:
            if s["scenario_id"] not in mgi:
                missing.append(s["scenario_id"])
    if missing:
        sys.exit(f"ABORT: {len(missing)} stratum-B files lack a Mergiraf outcome. "
                 f"Run tools/taxonomy_mergiraf.py first (e.g. missing: {missing[:2]}).")


def main() -> None:
    tc.REPORTS.mkdir(parents=True, exist_ok=True)
    if SPLIT_CSV.exists():
        sys.exit(f"ABORT: {SPLIT_CSV} already exists — the split is committed and "
                 f"frozen. Refusing to overwrite (amend via protocol §12 only).")

    census = tc.census()
    census_by_id = {c["merge_id"]: c for c in census}
    units = tc.load_units()
    scored = tc.scored_units(units)
    _check_prereqs(units)

    scored_by_stratum = {"A": [], "B": []}
    for u in scored:
        if u["scored"]:
            scored_by_stratum[u["stratum"]].append(u["merge_id"])

    # Seeded 60% derivation, stratified A then B (single RNG, fixed order).
    rng = random.Random(tc.SEED)
    derivation: set[str] = set()
    for st in ("A", "B"):
        ids = sorted(scored_by_stratum[st])
        rng.shuffle(ids)
        k = round(tc.DERIVATION_FRACTION * len(ids))
        derivation.update(ids[:k])

    rows = []
    for st in ("A", "B"):
        for mid in sorted(scored_by_stratum[st]):
            rows.append((mid, st, "derivation" if mid in derivation else "heldout"))

    with open(SPLIT_CSV, "w", newline="") as fh:
        import csv
        w = csv.writer(fh)
        w.writerow(["merge_id", "stratum", "split"])
        w.writerows(rows)

    # ------- manifest (§9), everything known before any API request -------
    scenario_hashes = {}
    for st, d in tc.SCEN_DIR.items():
        for f in sorted(Path(d).glob("*.json")):
            scenario_hashes[str(f.relative_to(ROOT))] = tc.sha256_file(f)

    n_scoredA, n_scoredB = len(scored_by_stratum["A"]), len(scored_by_stratum["B"])
    n_derivA = sum(1 for m, st, sp in rows if st == "A" and sp == "derivation")
    n_derivB = sum(1 for m, st, sp in rows if st == "B" and sp == "derivation")
    census_A = sum(1 for c in census if c["stratum"] == "A")
    census_B = sum(1 for c in census if c["stratum"] == "B")
    materialized = {"A": 0, "B": 0}
    for u in units.values():
        materialized[u["stratum"]] += 1

    manifest = {
        "program": "taxonomy-refresh (ISSUES #30)",
        "session": "S1",
        "generated_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "protocol": {
            "file": "outputs/taxonomy-protocol.md",
            # protocol lives at repo-root outputs/, i.e. ../ from cwd (comparator dir)
            "frozen_commit": _git("log", "-1", "--format=%H", "--", "../outputs/taxonomy-protocol.md"),
        },
        "repo_commit": _git("rev-parse", "HEAD"),
        "prompt_blob_sha1": {
            f: tc.git_blob_sha(ROOT / "prompts_taxonomy" / f) for f in PROMPT_FILES
        },
        "mergiraf_image_tag": tc.MERGIRAF_TAG,
        "mergiraf_image_id": _docker_image_id(tc.MERGIRAF_TAG),
        "javac_image": "eclipse-temurin:17-jdk",
        "javac_image_id": _docker_image_id("eclipse-temurin:17-jdk"),
        "split": {
            "seed": tc.SEED,
            "derivation_fraction": tc.DERIVATION_FRACTION,
            "file": "reports_taxonomy/split_assignment.csv",
            "file_sha256": tc.sha256_file(SPLIT_CSV),
            "stratified_by": "A/B",
            "order": "A then B, single random.Random(SEED)",
        },
        "population": {
            "census_total": len(census), "census_A": census_A, "census_B": census_B,
            "materialized_A": materialized["A"], "materialized_B": materialized["B"],
            "scored_A": n_scoredA, "scored_B": n_scoredB, "scored_total": n_scoredA + n_scoredB,
            "derivation_A": n_derivA, "derivation_B": n_derivB,
            "heldout_A": n_scoredA - n_derivA, "heldout_B": n_scoredB - n_derivB,
        },
        "scenario_files_sha256": scenario_hashes,
        "phase1": {
            "model": tc.MODEL,
            "api": "Message Batches",
            "request_params": {
                "max_tokens": 16000,
                "thinking": {"type": "adaptive"},
                "output_config": {"effort": "high",
                                  "format": {"type": "json_schema",
                                             "schema": "prompts_taxonomy/phase1_output.schema.json"}},
                "system_cache_control": {"type": "ephemeral"},
            },
            "custom_id_scheme": tc.CUSTOM_ID_SCHEME,
            "token_budget_per_unit": tc.TOKEN_BUDGET,
            "count_tokens_model": tc.MODEL,
        },
        "conventions": {
            "custom_id": tc.CUSTOM_ID_SCHEME,
            "resumable_cache": "per-phase raw_results.json keyed by custom_id",
            "divergence_rule": "CONFLICT/CRASH Mergiraf file dropped from unit and counted; "
                               "all-files-dropped unit leaves the scored population",
        },
        "phase2": {"status": "pending (S3)"},
        "phase3": {"status": "pending (S4)"},
        "g0_pilot": {"status": "pending (this session)"},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))

    print(f"census={len(census)} (A={census_A} B={census_B}) | "
          f"materialized A={materialized['A']} B={materialized['B']} | "
          f"scored A={n_scoredA} B={n_scoredB} (total {n_scoredA+n_scoredB})")
    print(f"derivation A={n_derivA} B={n_derivB} | heldout A={n_scoredA-n_derivA} B={n_scoredB-n_derivB}")
    print(f"wrote {SPLIT_CSV.relative_to(ROOT)} (sha256 {manifest['split']['file_sha256'][:12]}…)")
    print(f"wrote {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
