"""G1 machine-condition evaluation (ISSUES #30, S2, protocol §7).

Reads the Phase-1 derivation-split outputs (``reports_taxonomy/phase1/
raw_results.json``) and computes the two machine conditions of gate G1:

  (i)  attribution-rate floor  : ``attributed`` fraction >= 35% of scored
       derivation units;
  (ii) escape-hatch sanity band: combined (none-identified + indeterminate +
       flaky-suspect) fraction within [15%, 65%].

Both per stratum (A/B) and pooled, with Wilson 95% CIs (§8). Also reports the
verdict distribution, confidence distribution, open-vocabulary tag inventory,
and the §8 covariate crosstabs (truncation level x verdict, stratum x verdict)
to check attribution does not collapse on truncated / stratum-B units.

Writes ``reports_taxonomy/phase1/summary.txt``. Condition (iii) — Ali's
15-draft spot-check — is evaluated separately via the spot-check UI.

    ../.venv/bin/python tools/taxonomy_g1_eval.py
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

P1_DIR = tc.REPORTS / "phase1"
RAW = P1_DIR / "raw_results.json"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
SUMMARY = P1_DIR / "summary.txt"

ESCAPE = ("none-identified", "indeterminate", "flaky-suspect")
VERDICTS = ("attributed",) + ESCAPE
ATTR_FLOOR = 0.35
ESCAPE_BAND = (0.15, 0.65)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def pct(k: int, n: int) -> str:
    if n == 0:
        return "n/a"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100*k/n:5.1f}%  [{100*lo:4.1f}, {100*hi:4.1f}]"


def load() -> list[dict]:
    raw = json.loads(RAW.read_text())
    split = {}
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            split[r["merge_id"]] = (r["split"], r["stratum"])

    units = []
    for mid, rec in raw.items():
        if split.get(mid, (None, None))[0] != "derivation":
            continue
        if not (rec.get("result_type") == "succeeded" and rec.get("conforms")):
            units.append({"mid": mid, "stratum": split[mid][1], "conforms": False})
            continue
        obj = rec["parsed"]
        units.append({
            "mid": mid,
            "stratum": rec.get("stratum") or split[mid][1],
            "conforms": True,
            "verdict": obj["verdict"],
            "confidence": obj["confidence"],
            "tags": obj["mechanism"].get("tags", []),
            "merge_induced": obj["mechanism"].get("merge_induced"),
            "level": rec.get("level", "?"),
            "n_evidence": len(obj.get("evidence", [])),
        })
    return units


def _base_level(lvl: str) -> str:
    """Collapse 'T3/cap5', 'T3/cap1/trunc400' -> 'T3' for the covariate crosstab."""
    return (lvl or "?").split("/")[0]


def section_condition(units: list[dict], out: list[str]) -> dict:
    ok = [u for u in units if u["conforms"]]
    verdict = {u["mid"]: u["verdict"] for u in ok}

    def frac(sub, pred):
        n = len(sub)
        k = sum(1 for u in sub if pred(u))
        return k, n

    result = {}
    strata = {"A": [u for u in ok if u["stratum"] == "A"],
              "B": [u for u in ok if u["stratum"] == "B"],
              "pooled": ok}

    out.append("=" * 72)
    out.append("G1 MACHINE CONDITIONS (protocol §7)")
    out.append("=" * 72)
    out.append(f"scored derivation units returned & conforming: {len(ok)}/{len(units)}")
    non = [u["mid"] for u in units if not u["conforms"]]
    if non:
        out.append(f"NON-CONFORMING / MISSING (excluded from rates): {non}")
    out.append("")

    out.append("(i)  Attribution-rate floor  — attributed fraction >= 35.0%")
    for name in ("A", "B", "pooled"):
        k, n = frac(strata[name], lambda u: u["verdict"] == "attributed")
        result[f"attr_{name}"] = (k, n)
        out.append(f"     {name:7s}: {pct(k, n)}")
    ka, na = result["attr_pooled"]
    pass_i = na > 0 and ka / na >= ATTR_FLOOR
    out.append(f"     -> pooled {'PASS' if pass_i else 'FAIL'} "
               f"(floor {ATTR_FLOOR:.0%}; observed {100*ka/na:.1f}%)")
    out.append("")

    out.append("(ii) Escape-hatch sanity band — combined escape fraction in [15%, 65%]")
    for name in ("A", "B", "pooled"):
        k, n = frac(strata[name], lambda u: u["verdict"] in ESCAPE)
        result[f"esc_{name}"] = (k, n)
        out.append(f"     {name:7s}: {pct(k, n)}")
    ke, ne = result["esc_pooled"]
    frac_e = ke / ne if ne else 0
    pass_ii = ESCAPE_BAND[0] <= frac_e <= ESCAPE_BAND[1]
    out.append(f"     -> pooled {'PASS' if pass_ii else 'FAIL'} "
               f"(band [{ESCAPE_BAND[0]:.0%}, {ESCAPE_BAND[1]:.0%}]; observed {100*frac_e:.1f}%)")
    out.append("")
    result["pass_i"] = pass_i
    result["pass_ii"] = pass_ii
    return result


def section_distributions(units: list[dict], out: list[str]) -> None:
    ok = [u for u in units if u["conforms"]]
    out.append("=" * 72)
    out.append("VERDICT DISTRIBUTION (per stratum + pooled)")
    out.append("=" * 72)
    header = f"{'verdict':18s} " + " ".join(f"{s:>16s}" for s in ("A", "B", "pooled"))
    out.append(header)
    for v in VERDICTS:
        row = f"{v:18s} "
        for name in ("A", "B", "pooled"):
            sub = ok if name == "pooled" else [u for u in ok if u["stratum"] == name]
            k = sum(1 for u in sub if u["verdict"] == v)
            row += f"{k:>3d}/{len(sub):<3d}({100*k/len(sub):4.1f}%) " if sub else "   n/a   "
        out.append(row)
    out.append("")

    out.append("CONFIDENCE DISTRIBUTION (conforming units)")
    conf = Counter(u["confidence"] for u in ok)
    for c in ("high", "medium", "low"):
        out.append(f"  {c:8s}: {conf.get(c,0):3d}  ({100*conf.get(c,0)/len(ok):.1f}%)")
    out.append("")
    out.append("  confidence x verdict:")
    for c in ("high", "medium", "low"):
        cc = Counter(u["verdict"] for u in ok if u["confidence"] == c)
        out.append(f"    {c:8s}: " + ", ".join(f"{v}={cc.get(v,0)}" for v in VERDICTS))
    out.append("")

    out.append("MERGE-INDUCED FLAG (conforming units)")
    mi = Counter(u["merge_induced"] for u in ok)
    out.append("  " + ", ".join(f"{k}={v}" for k, v in mi.most_common()))
    out.append("")


def section_covariate(units: list[dict], out: list[str]) -> None:
    ok = [u for u in units if u["conforms"]]
    out.append("=" * 72)
    out.append("§8 COVARIATE — TRUNCATION LEVEL x VERDICT")
    out.append("(does attribution collapse on truncated / stratum-B units?)")
    out.append("=" * 72)
    by_lvl = defaultdict(list)
    for u in ok:
        by_lvl[_base_level(u["level"])].append(u)
    out.append(f"{'level':8s} {'n':>4s}  {'attributed':>18s}  {'escape':>18s}")
    for lvl in sorted(by_lvl):
        sub = by_lvl[lvl]
        ka = sum(1 for u in sub if u["verdict"] == "attributed")
        ke = sum(1 for u in sub if u["verdict"] in ESCAPE)
        out.append(f"{lvl:8s} {len(sub):>4d}  {pct(ka,len(sub)):>18s}  {pct(ke,len(sub)):>18s}")
    out.append("")
    out.append("  (T2/T3 = merged bodies omitted / hard-fit; watch for attribution drop-off)")
    out.append("")


def section_tags(units: list[dict], out: list[str]) -> None:
    ok = [u for u in units if u["conforms"]]
    tagc = Counter()
    for u in ok:
        for t in u["tags"]:
            tagc[t] += 1
    n_attr = sum(1 for u in ok if u["verdict"] == "attributed")
    out.append("=" * 72)
    out.append(f"OPEN-VOCABULARY TAG INVENTORY  ({len(tagc)} distinct tags across "
               f"{n_attr} attributed units)")
    out.append("(feeds Phase-2 consolidation — not gated here)")
    out.append("=" * 72)
    for t, c in tagc.most_common():
        out.append(f"  {c:3d}  {t}")
    out.append("")


def main() -> None:
    if not RAW.exists():
        sys.exit(f"no raw results at {RAW} — run tools/taxonomy_phase1.py first.")
    units = load()
    out: list[str] = []
    out.append("Phase-1 G1 evaluation — ISSUES #30 S2 — derivation split (165 units)")
    out.append("")
    result = section_condition(units, out)
    section_distributions(units, out)
    section_covariate(units, out)
    section_tags(units, out)

    out.append("=" * 72)
    out.append("G1 MACHINE VERDICT (conditions i + ii; condition iii = Ali spot-check)")
    out.append("=" * 72)
    out.append(f"  (i)  attribution floor : {'PASS' if result['pass_i'] else 'FAIL'}")
    out.append(f"  (ii) escape-hatch band : {'PASS' if result['pass_ii'] else 'FAIL'}")
    machine = result["pass_i"] and result["pass_ii"]
    out.append(f"  machine (i+ii)         : {'PASS' if machine else 'FAIL'}")
    out.append("  (iii) Ali spot-check   : PENDING (see phase1/spotcheck/spotcheck_ui.html)")
    out.append("")

    text = "\n".join(out)
    SUMMARY.write_text(text + "\n")
    print(text)
    print(f"\nwrote {SUMMARY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
