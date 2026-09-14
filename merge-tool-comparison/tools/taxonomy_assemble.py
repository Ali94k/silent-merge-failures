"""Per-unit input assembly + truncation-ladder measurement (ISSUES #30, S1, §5).

For every scored census unit, assembles the frozen Phase-1 USER block, walks
the truncation ladder T0->T3 measuring each level with count_tokens against
claude-opus-4-8, and records the chosen level + token count. Writes
``reports_taxonomy/units.csv`` covering the FULL census (308 rows): scored
units, divergence-dropped units, and materialization losses alike.

count_tokens sends unit content to the API, so this is a content-bearing
request: the derivation/held-out split MUST already be committed (protocol §4
firewall). The tool refuses to run if split_assignment.csv is absent.

Requires the anthropic SDK (repo-root .venv):
    ../.venv/bin/python tools/taxonomy_assemble.py
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import taxonomy_common as tc  # noqa: E402

UNITS_CSV = tc.REPORTS / "units.csv"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"


def _load_split() -> dict[str, str]:
    out = {}
    if SPLIT_CSV.exists():
        with open(SPLIT_CSV) as fh:
            for r in csv.DictReader(fh):
                out[r["merge_id"]] = r["split"]
    return out


def main() -> None:
    if not SPLIT_CSV.exists():
        sys.exit("ABORT: split_assignment.csv missing. Commit the split first "
                 "(tools/taxonomy_split.py) — count_tokens is a content-bearing "
                 "API call and must follow the split (protocol §4 firewall).")

    import anthropic
    client = anthropic.Anthropic()

    def count_fn(text: str) -> int:
        try:
            return client.messages.count_tokens(
                model=tc.MODEL, messages=[{"role": "user", "content": text}]).input_tokens
        except anthropic.BadRequestError:
            # Oversized request (e.g. the 193-file monster at T0) — treat as
            # far over budget so the ladder falls through to a smaller level.
            return 10 ** 9

    census = tc.census()
    census_by_id = {c["merge_id"]: c for c in census}
    units = tc.load_units()
    scored = {u["merge_id"]: u for u in tc.scored_units(units)}
    cc = tc._read_json(tc.COMPILE_CHECKS)
    split = _load_split()

    if not cc:
        print("WARN: compile_checks.json is empty — compile deltas will render "
              "'(none)'. Run tools/taxonomy_compile_checks.py before the final "
              "assembly so token counts include the delta blocks.", flush=True)

    rows = []
    n_scored = sum(1 for u in scored.values() if u["scored"])
    done = 0
    for c in census:
        mid = c["merge_id"]
        row = {"merge_id": mid, "stratum": c["stratum"],
               "num_intersecting_csv": c["num_intersecting_files"],
               "files_materialized": "", "files_scored": "", "files_dropped": "",
               "dropped_reasons": "", "status": "", "split": split.get(mid, ""),
               "truncation_level": "", "unit_tokens": "", "over_30k": ""}
        u = scored.get(mid)
        if u is None:
            row["status"] = "materialization_loss"
        else:
            n_mat = len(u["files"])
            n_sc = len(u["scored"])
            n_dr = len(u["dropped"])
            row.update(files_materialized=n_mat, files_scored=n_sc, files_dropped=n_dr,
                       dropped_reasons=";".join(sorted({d["reason"] for d in u["dropped"]})) or "")
            if n_sc == 0:
                row["status"] = "dropped_divergence"
            else:
                row["status"] = "scored"
                level, _text, tokens, over = tc.assemble_best(u, cc, count_fn)
                row.update(truncation_level=level, unit_tokens=tokens,
                           over_30k=int(over))
                done += 1
                if done % 25 == 0 or done == n_scored:
                    print(f"  assembled {done}/{n_scored} scored units", flush=True)
        rows.append(row)

    cols = ["merge_id", "stratum", "num_intersecting_csv", "status", "split",
            "files_materialized", "files_scored", "files_dropped", "dropped_reasons",
            "truncation_level", "unit_tokens", "over_30k"]
    with open(UNITS_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    # ---- record the assembly outcome in the manifest (§9) ----
    scored_rows_m = [r for r in rows if r["status"] == "scored"]
    lvl_all = Counter(r["truncation_level"] for r in scored_rows_m)
    lvlB_all = Counter(r["truncation_level"] for r in scored_rows_m if r["stratum"] == "B")
    base_lvl = Counter(str(r["truncation_level"]).split("/")[0] for r in scored_rows_m)
    manifest_path = tc.REPORTS / "manifest.json"
    if manifest_path.exists():
        import json
        manifest = json.loads(manifest_path.read_text())
        nB_ = sum(1 for r in scored_rows_m if r["stratum"] == "B")
        t3B_ = sum(1 for r in scored_rows_m
                   if r["stratum"] == "B" and str(r["truncation_level"]).startswith("T3"))
        manifest["assembly"] = {
            "units_csv": "reports_taxonomy/units.csv",
            "units_csv_sha256": tc.sha256_file(UNITS_CSV),
            "compile_checks_sha256": tc.sha256_file(tc.COMPILE_CHECKS) if tc.COMPILE_CHECKS.exists() else None,
            "token_budget": tc.TOKEN_BUDGET,
            "count_tokens_model": tc.MODEL,
            "truncation_base_levels": dict(sorted(base_lvl.items())),
            "truncation_levels_detailed": dict(sorted(lvl_all.items())),
            "stratum_B_T3_fraction": f"{t3B_}/{nB_}",
            "units_over_30k": sum(1 for r in scored_rows_m if r["over_30k"] == 1),
            "t3_hard_fit": {
                "note": "Pre-G0 assembly revisit (protocol §5): the frozen T3 (fixed 12-file "
                        "cap, -U3) cannot guarantee the 30k hard cap for pathological units "
                        "(many files, or a single huge diff). T3 is strengthened to a floor "
                        "with a hard-fit search — reduce the file cap (12->1), then truncate "
                        "per-diff line counts (400->40) — until under budget. Aggressiveness "
                        "is recorded in units.csv truncation_level (e.g. T3/cap5, T3/cap1/trunc400) "
                        "as an analysis covariate. No §12 amendment (pre-first-G0 = ordinary edit).",
                "file_caps": list(tc._T3_FILE_CAPS),
                "diff_line_caps": list(tc._T3_DIFF_LINE_CAPS),
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2))

    # ---- summary + pre-G0 truncation-distribution gate (protocol §5/§7) ----
    scored_rows = [r for r in rows if r["status"] == "scored"]
    lvl = Counter(r["truncation_level"] for r in scored_rows)
    lvlB = Counter(r["truncation_level"] for r in scored_rows if r["stratum"] == "B")
    over = sum(1 for r in scored_rows if r["over_30k"] == 1)
    status = Counter(r["status"] for r in rows)
    print(f"\nwrote {UNITS_CSV.relative_to(ROOT)}  ({len(rows)} census rows)")
    print("status:", dict(status))
    print("truncation (all scored):", dict(sorted(lvl.items())))
    print("truncation (stratum B):", dict(sorted(lvlB.items())))
    nB = sum(lvlB.values())
    # "at T3" = the T3 floor incl. its hard-fit variants (T3/cap*, T3/*/trunc*)
    t3B = sum(v for k, v in lvlB.items() if str(k).startswith("T3"))
    print(f"stratum-B T3 fraction: {t3B}/{nB} = {(t3B/nB if nB else 0):.1%} "
          f"(pre-G0 gate: revisit assembly if > 25%)")
    print(f"units over 30k hard cap: {over} (must be 0 for G0)")


if __name__ == "__main__":
    main()
