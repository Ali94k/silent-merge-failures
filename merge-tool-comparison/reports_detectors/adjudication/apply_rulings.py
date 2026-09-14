"""S-D6: apply Ali's GD4 rulings to the S-D5 machine numbers (ISSUES #31).

Joins sd6_rulings.csv (unit × lane rulings) with the eval units tables and
labels to produce the citable numbers per plan §9: causal recall counts a
unit with ≥1 CAUSAL lane; machine flag rates reported beside, labeled;
per-lane precision = causal-units / flagged-units for that lane; Wilson CIs
everywhere. Derivation-split numbers stay MACHINE-caught (no adjudication
there) and are TUNING-TAINTED wherever shown.

Output: causal_numbers.json (consumed by FINDINGS.md; committed).
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from detect_validate import wilson  # noqa: E402

NAME_BINDING_FAMILY = {
    "stale-usage-of-pruned-import",
    "stale-reference-to-removed-declaration",
    "stale-reference-to-renamed-or-relocated-declaration",
    "stale-caller-of-changed-signature",
}
N_HELDOUT = 110


def ci(k, n):
    p, lo, hi = wilson(k, n)
    return {"k": k, "n": n, "pct": round(100 * p, 1),
            "lo": round(100 * lo, 1), "hi": round(100 * hi, 1)}


def main() -> None:
    rulings = list(csv.DictReader(open(HERE / "sd6_rulings.csv")))
    units_rows = list(csv.DictReader(open(HERE.parent / "eval/units_heldout.csv")))
    assert len(units_rows) == N_HELDOUT

    by_unit: dict[str, dict] = {}
    for r in rulings:
        u = by_unit.setdefault(r["merge_id"], {"lanes": {}, "category": r["category"],
                                               "arms": r["arms"]})
        u["lanes"][r["lane"]] = r["ruling"]
    assert len(by_unit) == 20 and all(
        all(v in ("CAUSAL", "REAL-BUT-INCIDENTAL", "DETECTOR-FP") for v in u["lanes"].values())
        for u in by_unit.values()), "rulings incomplete"

    causal_units = {m for m, u in by_unit.items()
                    if any(v == "CAUSAL" for v in u["lanes"].values())}
    # arm-level flag sets from the machine table
    exp_flagged = {r["merge_id"] for r in units_rows if r["experimental_status"] == "FLAG"}
    base_flagged = {r["merge_id"] for r in units_rows if r["baseline_status"] == "FLAG"}
    assert exp_flagged == set(by_unit), "rulings do not cover exactly the flagged units"
    cat_of = {r["merge_id"]: r["category"] for r in units_rows}
    fam_units = {m for m, c in cat_of.items() if c in NAME_BINDING_FAMILY}
    n_fam = len(fam_units)

    exp_causal = causal_units                       # rulings cover experimental flags
    base_causal = causal_units & base_flagged       # baseline flags ⊂ experimental flags

    out = {
        "heldout": {
            "machine": {
                "experimental": ci(len(exp_flagged), N_HELDOUT),
                "baseline": ci(len(base_flagged), N_HELDOUT),
            },
            "causal": {
                "experimental": ci(len(exp_causal), N_HELDOUT),
                "baseline": ci(len(base_causal), N_HELDOUT),
                "added": ci(len(exp_causal - base_causal), N_HELDOUT),
            },
            "family": {
                "n": n_fam,
                "machine_experimental": ci(len(exp_flagged & fam_units), n_fam),
                "causal_experimental": ci(len(exp_causal & fam_units), n_fam),
                "causal_baseline": ci(len(base_causal & fam_units), n_fam),
                "causal_added": ci(len((exp_causal - base_causal) & fam_units), n_fam),
            },
            "fp_units": sorted(set(by_unit) - causal_units),
        },
        "per_category_causal_experimental": {},
        "per_lane_precision_units": {},
    }

    cats = Counter(cat_of.values())
    for cat in sorted(cats):
        members = {m for m, c in cat_of.items() if c == cat}
        out["per_category_causal_experimental"][cat] = ci(
            len(exp_causal & members), len(members))

    lane_flagged: dict[str, set] = {}
    lane_causal: dict[str, set] = {}
    for m, u in by_unit.items():
        for lane, ruling in u["lanes"].items():
            lane_flagged.setdefault(lane, set()).add(m)
            if ruling == "CAUSAL":
                lane_causal.setdefault(lane, set()).add(m)
    # D3-widened vs Joern mechanism split inside JoernUnresolvedReference:
    # dabsquared (widened path, ruled FP) vs the three Joern-native causal units.
    for lane in sorted(lane_flagged):
        k = len(lane_causal.get(lane, set()))
        n = len(lane_flagged[lane])
        out["per_lane_precision_units"][lane] = {**ci(k, n),
                                                 "flagged": sorted(lane_flagged[lane])}
    (HERE / "causal_numbers.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
