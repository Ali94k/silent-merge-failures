"""G3 condition 1 — Phase-3 STABILITY (ISSUES #30, S4, protocol §7/§8).

Compares the two independent closed-coding passes (a vs b) over all 275 scored
census units on the PRIMARY label (escape hatches count as labels). Emits:
  * exact primary-label agreement % + Wilson 95% CI,
  * Cohen's kappa,
  * disagreement count,
  * per-category confusion (descriptive),
  * secondary-label Jaccard (descriptive, not gated),
into ``reports_taxonomy/phase3/stability.md`` and ``stability.json``.

Gate (§7.G3.1): PASS iff agreement >= 80% AND kappa >= 0.70 AND disagreements
<= 60. Yellow band (agreement 60-80% or kappa 0.50-0.70): STOP — one sanctioned
codebook-clarification amendment then rerun BOTH passes (propose + wait for
Ali). Below the band: return to Phase 2 (documented failure).

Stdlib only. Run:  python tools/taxonomy_g3_stability.py
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import taxonomy_common as tc  # noqa: E402

P3 = tc.REPORTS / "phase3"
RAW_A = P3 / "raw_results_a.json"
RAW_B = P3 / "raw_results_b.json"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
OUT_MD = P3 / "stability.md"
OUT_JSON = P3 / "stability.json"

Z = 1.959963984540054  # 95%

PRIMARY_ENUM = [
    "stale-usage-of-pruned-import", "stale-reference-to-removed-declaration",
    "stale-reference-to-renamed-or-relocated-declaration", "stale-caller-of-changed-signature",
    "stale-expectation-of-changed-behavior", "overlapping-edit-interleaving",
    "insertion-anchored-to-relocated-code", "duplicate-concurrent-addition",
    "residual-other", "none-identified", "indeterminate", "flaky-suspect",
]
ESCAPE = {"none-identified", "indeterminate", "flaky-suspect"}


def wilson(x: int, n: int) -> tuple[float, float, float]:
    if n == 0:
        return 0.0, 0.0, 0.0
    p = x / n
    denom = 1 + Z * Z / n
    center = (p + Z * Z / (2 * n)) / denom
    half = Z / denom * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return p, max(0.0, center - half), min(1.0, center + half)


def cohen_kappa(a: list[str], b: list[str], labels: list[str]) -> float:
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca = Counter(a)
    cb = Counter(b)
    pe = sum((ca.get(k, 0) / n) * (cb.get(k, 0) / n) for k in labels)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def load_pass(path: Path) -> dict[str, dict]:
    raw = json.loads(path.read_text())
    return {mid: rec for mid, rec in raw.items()
            if rec.get("result_type") == "succeeded" and rec.get("conforms")}


def scored_mids() -> tuple[list[str], dict]:
    import csv
    mids, split = [], {}
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            mids.append(r["merge_id"])
            split[r["merge_id"]] = (r["split"], r["stratum"])
    return sorted(mids), split


def main() -> None:
    mids, split = scored_mids()
    A, B = load_pass(RAW_A), load_pass(RAW_B)
    miss_a = [m for m in mids if m not in A]
    miss_b = [m for m in mids if m not in B]
    if miss_a or miss_b:
        sys.exit(f"ABORT: non-conforming/missing units — a:{len(miss_a)} b:{len(miss_b)} "
                 f"(need all {len(mids)} conforming in both passes). First a:{miss_a[:3]} b:{miss_b[:3]}")

    pa = [A[m]["parsed"]["primary"] for m in mids]
    pb = [B[m]["parsed"]["primary"] for m in mids]
    n = len(mids)
    agree = sum(1 for x, y in zip(pa, pb) if x == y)
    disagree = n - agree
    p, lo, hi = wilson(agree, n)
    kappa = cohen_kappa(pa, pb, PRIMARY_ENUM)

    # Gate logic (§7.G3.1).
    pass_all = (p >= 0.80) and (kappa >= 0.70) and (disagree <= 60)
    yellow = (0.60 <= p < 0.80) or (0.50 <= kappa < 0.70)
    if pass_all:
        verdict = "PASS"
    elif yellow:
        verdict = "YELLOW"
    else:
        verdict = "FAIL"
    # Disagreement cap can force below-band even with high %/kappa.
    if not pass_all and not yellow and disagree > 60 and p >= 0.60 and kappa >= 0.50:
        verdict = "YELLOW"  # driven by the cap only; still a clarification-amendment case

    # Confusion (pass a rows x pass b cols), only off-diagonal reported in prose.
    confusion = defaultdict(Counter)
    disagreements = []
    for m in mids:
        la, lb = A[m]["parsed"]["primary"], B[m]["parsed"]["primary"]
        confusion[la][lb] += 1
        if la != lb:
            disagreements.append({"merge_id": m, "split": split[m][0], "stratum": split[m][1],
                                  "a": la, "b": lb,
                                  "a_conf": A[m]["parsed"].get("confidence"),
                                  "b_conf": B[m]["parsed"].get("confidence")})

    # Secondary Jaccard (descriptive).
    jac = []
    for m in mids:
        sa, sb = set(A[m]["parsed"].get("secondary", [])), set(B[m]["parsed"].get("secondary", []))
        u = sa | sb
        jac.append(1.0 if not u else len(sa & sb) / len(u))
    mean_jac = sum(jac) / len(jac)

    dist_a = Counter(pa)
    dist_b = Counter(pb)

    result = {
        "n": n, "agree": agree, "disagree": disagree,
        "agreement": p, "agreement_ci95": [lo, hi], "kappa": kappa,
        "mean_secondary_jaccard": mean_jac,
        "verdict": verdict,
        "gate": {"agreement_floor": 0.80, "kappa_floor": 0.70, "disagree_cap": 60,
                 "agreement_pass": p >= 0.80, "kappa_pass": kappa >= 0.70,
                 "disagree_pass": disagree <= 60},
        "primary_dist_a": dict(dist_a), "primary_dist_b": dict(dist_b),
        "disagreements": disagreements,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2))

    # ---- Markdown report ----
    L = []
    L.append("# G3 Condition 1 — Phase-3 Stability (pass a vs pass b)\n")
    L.append(f"**Generated over all {n} scored census units** (protocol §7 G3.1 / §8). "
             "Primary label, escape hatches counted as labels. NEW labeled evaluation — "
             "never blended with Stage-C R1/R2 or Phase-2b.\n")
    L.append(f"- Exact primary-label agreement: **{agree}/{n} = {p*100:.1f}%** "
             f"(Wilson 95% CI [{lo*100:.1f}, {hi*100:.1f}])")
    L.append(f"- Cohen's κ: **{kappa:.3f}**")
    L.append(f"- Disagreements: **{disagree}** (cap 60)")
    L.append(f"- Mean secondary-label Jaccard (descriptive): {mean_jac:.3f}\n")
    L.append("## Gate\n")
    L.append("| criterion | threshold | value | pass |")
    L.append("|---|---|---|---|")
    L.append(f"| agreement | ≥ 80% | {p*100:.1f}% | {'✅' if p>=0.80 else '❌'} |")
    L.append(f"| Cohen's κ | ≥ 0.70 | {kappa:.3f} | {'✅' if kappa>=0.70 else '❌'} |")
    L.append(f"| disagreements | ≤ 60 | {disagree} | {'✅' if disagree<=60 else '❌'} |")
    L.append(f"\n**Verdict: {verdict}**  "
             + {"PASS": "(→ proceed to G3 condition 2, Ali reliability adjudication)",
                "YELLOW": "(60–80% or κ 0.50–0.70, or cap-only miss → STOP: one sanctioned "
                          "codebook-clarification amendment, then rerun BOTH passes — propose + wait for Ali)",
                "FAIL": "(below band → return to Phase 2, documented failure)"}[verdict] + "\n")

    L.append("## Primary-label distributions\n")
    L.append("| category | pass a | pass b |")
    L.append("|---|--:|--:|")
    for k in PRIMARY_ENUM:
        L.append(f"| `{k}` | {dist_a.get(k,0)} | {dist_b.get(k,0)} |")

    L.append("\n## Disagreements (pass a → pass b)\n")
    if not disagreements:
        L.append("_None._")
    else:
        L.append(f"{len(disagreements)} of {n}. Contents of held-out units are NOT quoted here "
                 "(labels only, §4 firewall).\n")
        L.append("| merge_id | split | stratum | pass a | pass b | a conf | b conf |")
        L.append("|---|---|---|---|---|---|---|")
        for d in sorted(disagreements, key=lambda x: (x["a"], x["b"])):
            L.append(f"| `{d['merge_id']}` | {d['split']} | {d['stratum']} | "
                     f"`{d['a']}` | `{d['b']}` | {d['a_conf']} | {d['b_conf']} |")

    L.append("\n## Off-diagonal confusion (pass a row → pass b col; nonzero only)\n")
    for la in PRIMARY_ENUM:
        offs = {lb: c for lb, c in confusion[la].items() if lb != la and c}
        if offs:
            L.append(f"- `{la}` → " + ", ".join(f"`{lb}`×{c}" for lb, c in
                     sorted(offs.items(), key=lambda kv: -kv[1])))

    OUT_MD.write_text("\n".join(L) + "\n")
    print(f"agreement {agree}/{n} = {p*100:.1f}% [{lo*100:.1f},{hi*100:.1f}]  "
          f"kappa {kappa:.3f}  disagree {disagree}  -> {verdict}")
    print(f"wrote {OUT_MD.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
