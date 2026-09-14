"""G2 mechanical evaluation (ISSUES #30, S3, protocol §7 G2 conditions i-iii).

Evaluates the Phase-2 codebook draft against the fixed G2 gate conditions that
can be checked without Ali (i-iii); condition (iv) is Ali's ruling via the
mapping UI and is out of scope here.

  (i)   coverage: >= 90% of attributed derivation units map to a non-residual
        category (residual <= 10% of attributed). Also enforces the FIREWALL +
        completeness invariants the coverage table must satisfy: every cited
        unit_id is a real DERIVATION unit (never held-out, never phantom), and
        the coverage table is exactly the 60 attributed units.
  (ii)  granularity audit: every category ships id/name/mechanism/definition/
        inclusion/exclusion/anchors/boundary (residual-other: anchors optional);
        anchors are derivation-only; a heuristic flags symptom/domain-named ids.
  (iii) old->new mapping complete (all 7 historical categories present) +
        four-family assessment written.

Output: reports_taxonomy/phase2/g2_eval.md   (+ manifest phase2.g2 block)

    ../.venv/bin/python tools/taxonomy_g2_eval.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "reports_taxonomy/phase2/codebook_draft.md"
RAW = ROOT / "reports_taxonomy/phase1/raw_results.json"
SPLIT_CSV = ROOT / "reports_taxonomy/split_assignment.csv"
MANIFEST = ROOT / "reports_taxonomy/manifest.json"
OUT = ROOT / "reports_taxonomy/phase2/g2_eval.md"

REQUIRED_FIELDS = ["name", "mechanism", "definition", "inclusion", "exclusion",
                   "anchors", "boundary"]
# residual-other legitimately has no anchors.
RESIDUAL_EXEMPT = {"residual-other": {"anchors"}}
RESIDUAL_FRAC_MAX = 0.10

HISTORICAL = ["Atomic Updates", "Control Flow Interference", "Data Flow Interference",
              "Exception Handling Divergence", "Loop Semantics Divergence",
              "Method Rename", "Scope Capture"]
# symptom / domain tokens that would make an id a non-mechanism (heuristic).
SYMPTOM_TOKENS = ["test-failure", "compile-error", "exception-thrown", "crash",
                  "npe", "assertion-failure", "wrong-value", "runtime-error"]


def ground_truth() -> tuple[set, set]:
    raw = json.loads(RAW.read_text())
    deriv = set()
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            if r["split"] == "derivation":
                deriv.add(r["merge_id"])
    attributed = {m for m in deriv if raw[m]["parsed"]["verdict"] == "attributed"}
    return deriv, attributed


def parse_categories(txt: str) -> list[dict]:
    """One dict per '### `id`' block up to the '## 3' section."""
    cat_section = txt.split("## 3.")[0]
    parts = re.split(r"\n### ", cat_section)
    cats = []
    for p in parts[1:]:
        m = re.match(r"`([^`]+)`", p.strip())
        if not m:
            continue
        cid = m.group(1)
        fields = {f: bool(re.search(rf"- \*\*{f}:\*\*", p)) for f in REQUIRED_FIELDS}
        anchors = re.findall(r"^  - `([^`]+)` —", p, re.M)
        cats.append({"id": cid, "fields": fields, "anchors": anchors})
    return cats


def parse_coverage(txt: str) -> list[tuple[str, str]]:
    sec = txt.split("## 5.")[-1]
    rows = re.findall(r"^\| (\S[^|]*?) \| ([a-z][a-z0-9-]*) \|", sec, re.M)
    # drop the header row ('unit_id' | 'category') and separator artifacts.
    return [(u.strip(), c.strip()) for u, c in rows if u.strip() != "unit_id"]


def main() -> None:
    if not DRAFT.exists():
        sys.exit(f"no codebook draft at {DRAFT} — run tools/taxonomy_phase2.py first.")
    txt = DRAFT.read_text()
    deriv, attributed = ground_truth()
    cats = parse_categories(txt)
    cov = parse_coverage(txt)
    cat_ids = {c["id"] for c in cats}

    problems: list[str] = []

    # ---- (i) coverage + firewall + completeness -------------------------- #
    cov_ids = [u for u, _ in cov]
    cov_set = set(cov_ids)
    phantom = [u for u in cov_ids if u not in deriv]          # held-out or invented
    dup = [u for u in cov_ids if cov_ids.count(u) > 1]
    missing_attr = sorted(attributed - cov_set)
    extra_nonattr = sorted(cov_set - attributed)
    residual_n = sum(1 for _, c in cov if c == "residual-other")
    n_cov = len(cov_ids)
    residual_frac = residual_n / n_cov if n_cov else 1.0
    unknown_cat = sorted({c for _, c in cov if c not in cat_ids})

    if phantom:
        problems.append(f"(i) FIREWALL: {len(phantom)} coverage unit_id(s) not in the "
                        f"derivation set: {phantom[:5]}")
    if missing_attr:
        problems.append(f"(i) {len(missing_attr)} attributed units missing from coverage: "
                        f"{missing_attr[:5]}")
    if extra_nonattr:
        problems.append(f"(i) {len(extra_nonattr)} coverage units are not attributed: "
                        f"{extra_nonattr[:5]}")
    if dup:
        problems.append(f"(i) duplicate coverage rows: {sorted(set(dup))[:5]}")
    if unknown_cat:
        problems.append(f"(i) coverage cites categories not defined in §2: {unknown_cat}")
    if residual_frac > RESIDUAL_FRAC_MAX:
        problems.append(f"(i) residual {residual_frac:.1%} > {RESIDUAL_FRAC_MAX:.0%} ceiling")
    cond_i = not (phantom or missing_attr or extra_nonattr or dup or unknown_cat
                  or residual_frac > RESIDUAL_FRAC_MAX)

    # ---- (ii) granularity audit ------------------------------------------ #
    field_gaps, anchor_firewall, symptom_ids = [], [], []
    named = [c for c in cats if c["id"] != "residual-other"]
    for c in cats:
        exempt = RESIDUAL_EXEMPT.get(c["id"], set())
        for f in REQUIRED_FIELDS:
            if f in exempt:
                continue
            if not c["fields"][f]:
                field_gaps.append(f"{c['id']}:{f}")
        for a in c["anchors"]:
            if a not in deriv:
                anchor_firewall.append(f"{c['id']}:{a}")
        if any(tok in c["id"] for tok in SYMPTOM_TOKENS):
            symptom_ids.append(c["id"])
    # every named category needs >= 1 anchor.
    no_anchor = [c["id"] for c in named if not c["anchors"]]
    if field_gaps:
        problems.append(f"(ii) missing required fields: {field_gaps[:8]}")
    if anchor_firewall:
        problems.append(f"(ii) FIREWALL: anchors not in derivation set: {anchor_firewall[:5]}")
    if no_anchor:
        problems.append(f"(ii) named categories with no anchor: {no_anchor}")
    if symptom_ids:
        problems.append(f"(ii) category ids look symptom/domain-named (inspect): {symptom_ids}")
    cond_ii = not (field_gaps or anchor_firewall or no_anchor or symptom_ids)

    # ---- (iii) old->new mapping + four-family ---------------------------- #
    map_sec = txt.split("## 3.")[-1].split("## 4.")[0]
    missing_hist = [h for h in HISTORICAL if h not in map_sec]
    ff_sec = txt.split("## 4.")[-1].split("## 5.")[0]
    ff_written = len(ff_sec.strip()) > 200 and (
        "four-family" in ff_sec.lower() or "name-binding" in ff_sec.lower())
    if missing_hist:
        problems.append(f"(iii) historical categories absent from mapping: {missing_hist}")
    if not ff_written:
        problems.append("(iii) four-family assessment missing/too short")
    cond_iii = not missing_hist and ff_written

    machine_pass = cond_i and cond_ii and cond_iii

    # ---- report ---------------------------------------------------------- #
    sizes = {}
    for _, c in cov:
        sizes[c] = sizes.get(c, 0) + 1
    lines = [
        "# G2 machine evaluation — Phase-2 codebook draft (ISSUES #30, §7 G2 i-iii)",
        "",
        f"Draft: `reports_taxonomy/phase2/codebook_draft.md`  |  categories defined: "
        f"{len(cats)} ({len(named)} named + residual-other)",
        f"Ground truth: {len(deriv)} derivation units, {len(attributed)} attributed.",
        "",
        "## Condition (i) — coverage + firewall + completeness",
        f"- coverage rows: {n_cov}  |  attributed: {len(attributed)}  |  "
        f"missing: {len(missing_attr)}  |  extra-non-attributed: {len(extra_nonattr)}  |  "
        f"duplicates: {len(set(dup))}",
        f"- firewall (all coverage ids in derivation set): "
        f"{'OK' if not phantom else 'VIOLATED ' + str(phantom[:5])}",
        f"- residual: {residual_n}/{n_cov} = {residual_frac:.1%}  (ceiling {RESIDUAL_FRAC_MAX:.0%})",
        f"- category sizes: {json.dumps(sizes)}",
        f"- **(i) verdict: {'PASS' if cond_i else 'FAIL'}**",
        "",
        "## Condition (ii) — granularity audit",
        f"- categories with all required fields: "
        f"{len(cats) - len({g.split(':')[0] for g in field_gaps})}/{len(cats)}",
        f"- anchors all derivation-only (firewall): {'OK' if not anchor_firewall else 'VIOLATED'}",
        f"- named categories missing an anchor: {no_anchor or 'none'}",
        f"- symptom/domain-named ids (heuristic): {symptom_ids or 'none'}",
        "- note: 'every category is a mechanism (not a symptom)' is a semantic judgment "
        "for Ali's (iv) ruling; this pass checks structure + the symptom-token heuristic only.",
        f"- **(ii) verdict: {'PASS' if cond_ii else 'FAIL'}**",
        "",
        "## Condition (iii) — old->new mapping + four-family",
        f"- historical categories present in mapping: {7 - len(missing_hist)}/7"
        + (f"  (missing {missing_hist})" if missing_hist else ""),
        f"- four-family assessment written: {'yes' if ff_written else 'no'}",
        f"- **(iii) verdict: {'PASS' if cond_iii else 'FAIL'}**",
        "",
        "## Machine verdict (i-iii)",
        f"**{'PASS' if machine_pass else 'FAIL'}** — "
        + ("all three machine conditions met; hand to Ali for the (iv) ruling via mapping_ui.html."
           if machine_pass else "see problems below; one Fable-5 revision round is sanctioned "
           "pre-freeze (protocol §7 / S3 brief)."),
        "",
        "### Problems" if problems else "### Problems: none",
    ]
    lines += [f"- {p}" for p in problems]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    # ---- manifest -------------------------------------------------------- #
    manifest = json.loads(MANIFEST.read_text())
    manifest.setdefault("phase2", {})["g2"] = {
        "conditions": {
            "i_coverage": {"pass": cond_i, "residual_n": residual_n, "n_cov": n_cov,
                           "residual_frac": round(residual_frac, 4),
                           "firewall_ok": not phantom, "missing_attributed": missing_attr,
                           "extra_non_attributed": extra_nonattr, "duplicates": sorted(set(dup))},
            "ii_granularity": {"pass": cond_ii, "field_gaps": field_gaps,
                               "anchor_firewall_violations": anchor_firewall,
                               "named_without_anchor": no_anchor, "symptom_named_ids": symptom_ids,
                               "n_categories": len(cats), "n_named": len(named)},
            "iii_mapping_four_family": {"pass": cond_iii, "historical_missing": missing_hist,
                                        "four_family_written": ff_written},
        },
        "machine_verdict": "PASS" if machine_pass else "FAIL",
        "category_ids": sorted(cat_ids),
        "category_sizes_provisional": sizes,
        "condition_iv": "PENDING Ali (mapping_ui.html) — freeze commit gated on it",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"\nwrote {OUT.relative_to(ROOT)} + recorded phase2.g2 in manifest.json")


if __name__ == "__main__":
    main()
