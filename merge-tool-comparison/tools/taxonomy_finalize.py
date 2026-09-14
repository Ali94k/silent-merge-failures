"""Final labels + FINDINGS statistics (ISSUES #30, S4, protocol §7/§8).

Consumes the two conforming Phase-3 passes + Ali's G3.2 rulings CSV and emits:
  * reports_taxonomy/labels_final.csv — one row per scored census unit (275):
    agreeing units keep their agreed primary (Ali's sampled overrides applied —
    none occurred); disagreeing units take Ali's ruling.
  * reports_taxonomy/phase3/findings_stats.json — every §8 statistic used by
    FINDINGS.md (base rates per stratum + pooled with Wilson 95% CIs, population
    accounting, covariates, secondary co-occurrence, gate numbers).

Stdlib only; deterministic. Run:  python tools/taxonomy_finalize.py
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import taxonomy_common as tc  # noqa: E402

P3 = tc.REPORTS / "phase3"
RULINGS = P3 / "adjudication/phase3_reliability_rulings.csv"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
UNITS_CSV = tc.REPORTS / "units.csv"
OUT_LABELS = tc.REPORTS / "labels_final.csv"
OUT_STATS = P3 / "findings_stats.json"

Z = 1.959963984540054
ESCAPE = ["none-identified", "indeterminate", "flaky-suspect"]
NAMED = ["stale-usage-of-pruned-import", "stale-reference-to-removed-declaration",
         "stale-reference-to-renamed-or-relocated-declaration", "stale-caller-of-changed-signature",
         "stale-expectation-of-changed-behavior", "overlapping-edit-interleaving",
         "insertion-anchored-to-relocated-code", "duplicate-concurrent-addition"]
ALL_PRIMARY = NAMED + ["residual-other"] + ESCAPE
NAME_BINDING = NAMED[:4]          # the four name-binding/typing categories


def wilson(x: int, n: int) -> tuple[float, float, float]:
    if n == 0:
        return 0.0, 0.0, 0.0
    p = x / n
    denom = 1 + Z * Z / n
    center = (p + Z * Z / (2 * n)) / denom
    half = Z / denom * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return p, max(0.0, center - half), min(1.0, center + half)


def load_pass(letter: str) -> dict[str, dict]:
    raw = json.loads((P3 / f"raw_results_{letter}.json").read_text())
    return {m: r["parsed"] for m, r in raw.items()
            if r.get("result_type") == "succeeded" and r.get("conforms")}


def main() -> None:
    A, B = load_pass("a"), load_pass("b")
    meta = {}
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            meta[r["merge_id"]] = (r["split"], r["stratum"])
    mids = sorted(meta)
    assert all(m in A and m in B for m in mids), "non-conforming units"

    rulings = {r["mid"]: r for r in csv.DictReader(open(RULINGS))}
    n_dis_ruled = sum(1 for r in rulings.values() if r["kind"] == "disagree")
    agree_sampled = [r for r in rulings.values() if r["kind"] == "agree"]
    n_acc = sum(1 for r in agree_sampled if r["final"] == r["agreed"])

    # ---- final labels ----
    rows, final = [], {}
    for m in mids:
        la, lb = A[m]["primary"], B[m]["primary"]
        if la == lb:
            src = "agree"
            f = la
            if m in rulings:                      # sampled agreeing unit
                src = "agree-sampled-" + ("accepted" if rulings[m]["final"] == f else "overridden")
                f = rulings[m]["final"]
        else:
            assert m in rulings, f"disagreement {m} lacks a ruling"
            f = rulings[m]["final"]
            src = "ali-ruling"
        final[m] = f
        rows.append({"merge_id": m, "stratum": meta[m][1], "split": meta[m][0],
                     "pass_a": la, "pass_b": lb, "final_primary": f, "source": src,
                     "confidence_a": A[m].get("confidence"), "confidence_b": B[m].get("confidence"),
                     "secondary_a": ";".join(A[m].get("secondary", [])),
                     "secondary_b": ";".join(B[m].get("secondary", []))})
    with open(OUT_LABELS, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- base rates per stratum + pooled ----
    def dist(subset):
        c = Counter(final[m] for m in subset)
        n = len(subset)
        out = {}
        for lab in ALL_PRIMARY:
            x = c.get(lab, 0)
            p, lo, hi = wilson(x, n)
            out[lab] = {"x": x, "n": n, "pct": 100 * p, "ci": [100 * lo, 100 * hi]}
        return out

    A_mids = [m for m in mids if meta[m][1] == "A"]
    B_mids = [m for m in mids if meta[m][1] == "B"]
    base = {"A": dist(A_mids), "B": dist(B_mids), "pooled": dist(mids)}

    def mass(subset, labels):
        x = sum(1 for m in subset if final[m] in labels)
        p, lo, hi = wilson(x, len(subset))
        return {"x": x, "n": len(subset), "pct": 100 * p, "ci": [100 * lo, 100 * hi]}

    masses = {}
    for name, subset in (("A", A_mids), ("B", B_mids), ("pooled", mids)):
        masses[name] = {
            "attributed": mass(subset, set(NAMED) | {"residual-other"}),
            "escape": mass(subset, set(ESCAPE)),
            "name_binding": mass(subset, set(NAME_BINDING)),
        }
    n_attr = masses["pooled"]["attributed"]["x"]
    nb_of_attr = wilson(masses["pooled"]["name_binding"]["x"], n_attr)

    # ---- covariates: verdict-class by truncation level / stratum / file count ----
    ucsv = {r["merge_id"]: r for r in csv.DictReader(open(UNITS_CSV)) if r["status"] == "scored"}
    def vclass(m):
        return "escape" if final[m] in ESCAPE else "attributed"
    cov_trunc = defaultdict(Counter)
    for m in mids:
        lvl = ucsv[m]["truncation_level"].split("/")[0]
        cov_trunc[lvl][vclass(m)] += 1
    cov_files = defaultdict(Counter)
    for m in mids:
        n_f = int(ucsv[m]["files_scored"])
        bucket = "1" if n_f == 1 else ("2-3" if n_f <= 3 else ("4-8" if n_f <= 8 else ">8"))
        cov_files[bucket][vclass(m)] += 1
    cov_stratum = {s: dict(Counter(vclass(m) for m in sub))
                   for s, sub in (("A", A_mids), ("B", B_mids))}

    # ---- secondary co-occurrence (descriptive; union of the two passes per unit) ----
    cooc = defaultdict(Counter)
    for m in mids:
        secs = set(A[m].get("secondary", [])) | set(B[m].get("secondary", []))
        for s in secs:
            if s != final[m]:
                cooc[final[m]][s] += 1
    cooc = {k: dict(v.most_common()) for k, v in cooc.items() if v}

    # ---- gate numbers ----
    stab = json.loads((P3 / "stability.json").read_text())
    rel_p, rel_lo, rel_hi = wilson(n_acc, len(agree_sampled))

    stats = {
        "population": {"census": 308, "census_A": 195, "census_B": 113,
                       "not_materialized_A": 15, "divergence_dropped_A": 16,
                       "not_materialized_B": 2, "divergence_dropped_B": 0,
                       "scored_A": len(A_mids), "scored_B": len(B_mids), "scored": len(mids)},
        "final_distribution": {lab: sum(1 for m in mids if final[m] == lab) for lab in ALL_PRIMARY},
        "base_rates": base,
        "masses": masses,
        "name_binding_share_of_attributed": {"x": masses["pooled"]["name_binding"]["x"],
                                             "n": n_attr, "pct": 100 * nb_of_attr[0],
                                             "ci": [100 * nb_of_attr[1], 100 * nb_of_attr[2]]},
        "labels_source": dict(Counter(r["source"] for r in rows)),
        "covariates": {"truncation": {k: dict(v) for k, v in sorted(cov_trunc.items())},
                       "files_scored": {k: dict(v) for k, v in sorted(cov_files.items())},
                       "stratum": cov_stratum},
        "secondary_cooccurrence": cooc,
        "g3": {
            "stability": {"agreement_x": stab["agree"], "n": stab["n"],
                          "pct": 100 * stab["agreement"],
                          "ci": [100 * c for c in stab["agreement_ci95"]],
                          "kappa": stab["kappa"], "disagreements": stab["disagree"],
                          "verdict": stab["verdict"],
                          "yellow_v1": {"pct": 78.9, "kappa": 0.741, "disagreements": 58}},
            "reliability": {"accepted": n_acc, "sampled_agreeing": len(agree_sampled),
                            "pct": 100 * rel_p, "ci": [100 * rel_lo, 100 * rel_hi],
                            "override_rate_sampled": 0.0 if n_acc == len(agree_sampled) else
                            100 * (1 - n_acc / len(agree_sampled)),
                            "disagreements_ruled": n_dis_ruled,
                            "ruling_sides": dict(Counter(
                                "pass_a" if rulings[m]["final"] == A[m]["primary"] else
                                ("pass_b" if rulings[m]["final"] == B[m]["primary"] else "third")
                                for m in rulings if rulings[m]["kind"] == "disagree")),
                            "verdict": "PASS" if rel_p >= 0.75 else "FAIL"},
        },
    }
    OUT_STATS.write_text(json.dumps(stats, indent=2))
    print(f"wrote {OUT_LABELS.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"wrote {OUT_STATS.relative_to(ROOT)}")
    fd = stats["final_distribution"]
    print("\nfinal primary distribution (pooled):")
    for lab in ALL_PRIMARY:
        if fd[lab]:
            b = base["pooled"][lab]
            print(f"  {lab:52} {fd[lab]:3}  {b['pct']:5.1f}% [{b['ci'][0]:.1f},{b['ci'][1]:.1f}]")
    print(f"\nattributed {masses['pooled']['attributed']['x']}/275 = "
          f"{masses['pooled']['attributed']['pct']:.1f}% "
          f"[{masses['pooled']['attributed']['ci'][0]:.1f},{masses['pooled']['attributed']['ci'][1]:.1f}]"
          f" | escape {masses['pooled']['escape']['x']}/275 = {masses['pooled']['escape']['pct']:.1f}%"
          f" | name-binding {stats['name_binding_share_of_attributed']['pct']:.1f}% of attributed")
    print(f"reliability: {n_acc}/{len(agree_sampled)} = {100*rel_p:.1f}% [{100*rel_lo:.1f},{100*rel_hi:.1f}] -> "
          f"{stats['g3']['reliability']['verdict']}")


if __name__ == "__main__":
    main()
