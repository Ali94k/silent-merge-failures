"""Detector-cycle spec-extraction batch (ISSUES #31, S-D1) — the cycle's
ONLY LLM use (plan §2 rule N1: development tooling on derivation data).

Extracts machine-readable detector specs from the 48 ATTRIBUTED DERIVATION
units whose frozen final primary label is a target category:
  D1  stale-usage-of-pruned-import                      (21)
  D2  stale-caller-of-changed-signature                 (14)
  D3  stale-reference-to-removed-declaration            (6)
      + stale-reference-to-renamed-or-relocated-declaration (7)

Inputs are the committed Phase-3 per-unit texts
(reports_taxonomy/phase3/inputs/input__<mid>.txt — byte-identical to what
the labeling passes saw). No held-out, eval-control, or spgroup content is
ever requested (§3 firewall; the runner asserts derivation-split ids).

Model/params mirror the proven taxonomy pattern: claude-opus-4-8 via the
Batch API, adaptive thinking, effort high, structured outputs against
prompts_detectors/spec_output.schema.json, cached system prefix, recovery
strictly via the submit-time {custom_id: merge_id} map.

Modes:
    run     submit-if-needed -> poll -> collect -> resubmit missing
            (resumable; state in reports_detectors/specs/)
    report  raw_results.json -> specs.csv + spec_table.md + gd1_machine.json
            (quote-provenance grading + GD1 usable-spec machine check)

Usage (repo-root venv has the anthropic SDK, plan §6):
    ../.venv/bin/python tools/detector_specs_batch.py run
    ../.venv/bin/python tools/detector_specs_batch.py report
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports_detectors"
SPECS = REPORTS / "specs"
LABELS = ROOT / "reports_taxonomy/labels_final.csv"
INPUTS = ROOT / "reports_taxonomy/phase3/inputs"
PROMPT_FILE = ROOT / "prompts_detectors/spec_extraction.md"
SCHEMA_FILE = ROOT / "prompts_detectors/spec_output.schema.json"
BATCHES = SPECS / "batches.json"
RAW = SPECS / "raw_results.json"

MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000
WALL_BUDGET = int(os.environ.get("WALL_BUDGET", "7200"))
POLL_SECONDS = 60

D1 = "stale-usage-of-pruned-import"
D2 = "stale-caller-of-changed-signature"
D3A = "stale-reference-to-removed-declaration"
D3B = "stale-reference-to-renamed-or-relocated-declaration"
DETECTOR = {D1: "D1", D2: "D2", D3A: "D3", D3B: "D3"}


def target_units() -> list[dict]:
    """The 48 attributed derivation units in the four target categories."""
    units = []
    with LABELS.open() as fh:
        for r in csv.DictReader(fh):
            if r["split"] == "derivation" and r["final_primary"] in DETECTOR:
                units.append({"merge_id": r["merge_id"], "stratum": r["stratum"],
                              "category": r["final_primary"],
                              "detector": DETECTOR[r["final_primary"]]})
    if not units:
        sys.exit("ABORT: no target units found — check labels_final.csv")
    # §3 firewall cross-check: every batched unit must be derivation-split
    # in the independent split_assignment.csv too, not only in labels_final.
    split = {r["merge_id"]: r["split"]
             for r in csv.DictReader((ROOT / "reports_taxonomy/split_assignment.csv").open())}
    leak = [u["merge_id"] for u in units if split.get(u["merge_id"]) != "derivation"]
    if leak:
        sys.exit(f"ABORT: non-derivation unit(s) in batch set: {leak[:5]}")
    return sorted(units, key=lambda u: u["merge_id"])


def load_system() -> str:
    text = PROMPT_FILE.read_text()
    if "## SYSTEM" not in text:
        sys.exit("ABORT: prompt file missing '## SYSTEM' marker")
    return text.split("## SYSTEM", 1)[1].strip()


def unit_text(mid: str) -> str:
    p = INPUTS / f"input__{mid}.txt"
    if not p.exists():
        sys.exit(f"ABORT: missing committed phase-3 input for {mid}")
    return p.read_text()


def build_user(u: dict) -> str:
    return (f"UNIT: {u['merge_id']}\n"
            f"PRIMARY CATEGORY (frozen final label): {u['category']}\n"
            f"DETECTOR: {u['detector']}\n\n"
            f"--- UNIT INPUT (exactly as seen by the labeling passes) ---\n"
            f"{unit_text(u['merge_id'])}")


def custom_id(mid: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]", "-", mid)
    cid = f"spec-{safe}"
    if len(cid) <= 64 and re.fullmatch(r"[A-Za-z0-9_-]+", mid):
        return cid
    h = hashlib.sha1(mid.encode()).hexdigest()[:8]
    return f"spec-{safe[:64 - 5 - 1 - 8]}-{h}"


def validate(obj) -> tuple[bool, str]:
    """Shallow conformance net (structured outputs enforce the full schema)."""
    if not isinstance(obj, dict):
        return False, "not an object"
    for k in ("unit_id", "category", "extraction_status", "cannot_extract",
              "d1", "d2", "d3", "notes"):
        if k not in obj:
            return False, f"missing key {k}"
    if obj["extraction_status"] not in ("ok", "partial", "cannot_extract"):
        return False, f"bad extraction_status {obj['extraction_status']!r}"
    return True, "ok"


def conforming(rec) -> bool:
    return bool(rec) and rec.get("result_type") == "succeeded" and rec.get("conforms")


def _load(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def _save(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2))


# --------------------------------------------------------------------------- #
# run: submit -> poll -> collect (resumable, phase-1 pattern)
# --------------------------------------------------------------------------- #

def run() -> None:
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    SPECS.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()
    system = load_system()
    schema = json.loads(SCHEMA_FILE.read_text())
    units = target_units()
    by_mid = {u["merge_id"]: u for u in units}
    print(f"target units: {len(units)} "
          f"({Counter(u['detector'] for u in units)})", flush=True)

    def build_request(mid: str) -> Request:
        return Request(
            custom_id=custom_id(mid),
            params=MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                thinking={"type": "adaptive"},
                output_config={"effort": "high",
                               "format": {"type": "json_schema", "schema": schema}},
                system=[{"type": "text", "text": system,
                         "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": build_user(by_mid[mid])}],
            ),
        )

    raw: dict[str, dict] = _load(RAW, {})
    batches: list[dict] = _load(BATCHES, [])

    def collect(batch_id: str, cid_to_mid: dict[str, str]) -> int:
        n = 0
        for result in client.messages.batches.results(batch_id):
            mid = cid_to_mid.get(result.custom_id)
            if mid is None:
                print(f"  WARN: custom_id {result.custom_id} not in submit map — skipped",
                      flush=True)
                continue
            rec = {"result_type": result.result.type}
            if result.result.type == "succeeded":
                msg = result.result.message
                rec["stop_reason"] = msg.stop_reason
                text = next((b.text for b in msg.content if b.type == "text"), "")
                rec["raw_text"] = text
                try:
                    obj = json.loads(text)
                    ok, why = validate(obj)
                    rec.update(parsed=obj, conforms=ok, reason=why)
                except json.JSONDecodeError as e:
                    rec.update(conforms=False, reason=f"json error: {e}")
                rec["usage"] = {"input": msg.usage.input_tokens,
                                "output": msg.usage.output_tokens}
            else:
                rec["error"] = str(getattr(result.result, "error", "")) or result.result.type
            rec["category"] = by_mid[mid]["category"]
            rec["detector"] = by_mid[mid]["detector"]
            raw[mid] = rec
            n += 1
        _save(RAW, raw)
        return n

    def missing() -> list[str]:
        return [u["merge_id"] for u in units if not conforming(raw.get(u["merge_id"]))]

    t0 = time.time()
    while True:
        for b in batches:
            if b.get("collected"):
                continue
            batch = client.messages.batches.retrieve(b["batch_id"])
            b["status"] = batch.processing_status
            if batch.processing_status == "ended":
                got = collect(b["batch_id"], b["cid_to_mid"])
                b["collected"] = True
                b["request_counts"] = dict(batch.request_counts)
                print(f"collected {got} results from {b['batch_id']} "
                      f"({batch.request_counts})", flush=True)
            _save(BATCHES, batches)

        miss = missing()
        print(f"missing/failed: {len(miss)}/{len(units)}", flush=True)
        if not miss:
            tot_in = sum(r.get("usage", {}).get("input", 0) for r in raw.values())
            tot_out = sum(r.get("usage", {}).get("output", 0) for r in raw.values())
            print(f"all target units conforming — done. usage in={tot_in} out={tot_out}",
                  flush=True)
            break

        inflight = [b for b in batches if not b.get("collected")]
        if inflight:
            if time.time() - t0 > WALL_BUDGET:
                print(f"batch(es) still processing after {WALL_BUDGET}s — "
                      f"re-run to re-attach.", flush=True)
                break
            time.sleep(POLL_SECONDS)
            continue

        reqs = [build_request(m) for m in miss]
        cid_to_mid = {custom_id(m): m for m in miss}
        batch = client.messages.batches.create(requests=reqs)
        batches.append({"batch_id": batch.id, "cid_to_mid": cid_to_mid,
                        "status": batch.processing_status, "collected": False,
                        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "n_requests": len(reqs)})
        _save(BATCHES, batches)
        print(f"submitted batch {batch.id} for {len(reqs)} units "
              f"({batch.processing_status})", flush=True)


# --------------------------------------------------------------------------- #
# report: quote grading + GD1 machine check + Ali's spec table
# --------------------------------------------------------------------------- #

def _haystacks(text: str) -> tuple[str, set[str]]:
    """(raw text, set of whitespace-collapsed line variants w/ and w/o gutter)."""
    hay = set()
    for line in text.split("\n"):
        for v in (line, line[1:] if line[:1] in "+- " else line):
            c = re.sub(r"\s+", " ", v).strip()
            if c:
                hay.add(c)
    return text, hay


def _grade_quote(quote: str, raw_text: str, hay: set[str]) -> str:
    q = quote.strip()
    if not q:
        return "empty"
    if q in raw_text:
        return "exact"
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in q.split("\n")]
    lines = [ln for ln in lines if ln]
    if lines and all(ln in hay for ln in lines):
        return "normalized"
    return "absent"


def _usable(rec: dict, raw_text: str, hay: set[str]) -> tuple[bool, str, list[str]]:
    """GD1 usable-spec rule per detector. Returns (usable, why, grades)."""
    obj = rec["parsed"]
    det = rec["detector"]
    grades: list[str] = []

    def g(site) -> str:
        gr = _grade_quote(site.get("quote", ""), raw_text, hay)
        grades.append(gr)
        return gr

    if det == "D1":
        d = obj["d1"]
        imp_ok = g(d["pruned_import_statement"]) in ("exact", "normalized")
        sites_ok = any(g(s) in ("exact", "normalized") for s in d["stale_usage_sites"]) \
            if d["stale_usage_sites"] else False
        sym_ok = bool(d["pruned_symbol"].strip())
        ok = imp_ok and sites_ok and sym_ok
        why = ("ok" if ok else
               f"import_quote={'ok' if imp_ok else 'missing/absent'} "
               f"symbol={'ok' if sym_ok else 'empty'} "
               f"usage_sites={'ok' if sites_ok else 'none-verify'}")
    elif det == "D2":
        d = obj["d2"]
        old_ok = g(d["old_signature"]) in ("exact", "normalized")
        new_ok = g(d["new_signature"]) in ("exact", "normalized")
        sites_ok = any(g(s) in ("exact", "normalized") for s in d["stale_call_sites"]) \
            if d["stale_call_sites"] else False
        ok = old_ok and new_ok and sites_ok
        why = ("ok" if ok else
               f"old_sig={'ok' if old_ok else 'missing/absent'} "
               f"new_sig={'ok' if new_ok else 'missing/absent'} "
               f"call_sites={'ok' if sites_ok else 'none-verify'}")
    else:
        d = obj["d3"]
        decl_ok = g(d["old_declaration"]) in ("exact", "normalized")
        sites_ok = any(g(s) in ("exact", "normalized") for s in d["stale_reference_sites"]) \
            if d["stale_reference_sites"] else False
        v1, v2 = d["rm2_would_fire"]["verdict"], d["joern_would_fire"]["verdict"]
        verdicts_ok = v1 in ("yes", "no", "uncertain") and v2 in ("yes", "no", "uncertain")
        shape_ok = (v1 != "no" or v2 != "no") or bool(d["missed_shape"].strip())
        ok = decl_ok and sites_ok and verdicts_ok and shape_ok
        why = ("ok" if ok else
               f"decl={'ok' if decl_ok else 'missing/absent'} "
               f"refs={'ok' if sites_ok else 'none-verify'} "
               f"verdicts={'ok' if verdicts_ok else 'incomplete'} "
               f"missed_shape={'ok' if shape_ok else 'required-but-empty'}")
    return ok, why, grades


def report() -> None:
    raw = _load(RAW, {})
    units = target_units()
    rows, gd1 = [], {"per_detector": {}}
    grade_counter: Counter = Counter()

    for u in units:
        mid = u["merge_id"]
        rec = raw.get(mid)
        if not conforming(rec):
            rows.append({"unit_id": mid, "detector": u["detector"],
                         "category": u["category"], "extraction_status": "MISSING",
                         "usable": False, "why": "no conforming result",
                         "summary": "", "n_sites": 0, "quote_grades": "",
                         "cannot_extract": "", "missed_shape": "", "notes": ""})
            continue
        obj = rec["parsed"]
        raw_text, hay = _haystacks(unit_text(mid))
        ok, why, grades = _usable(rec, raw_text, hay)
        grade_counter.update(grades)
        det = rec["detector"]
        if det == "D1":
            d = obj["d1"]
            summary = (f"import `{d['pruned_symbol']}` {d['import_change_kind'] or '?'} "
                       f"by {d['pruning_side'] or '?'}; "
                       f"{len(d['stale_usage_sites'])} usage site(s), "
                       f"added by {d['usage_added_by'] or '?'}")
            n_sites = len(d["stale_usage_sites"])
        elif det == "D2":
            d = obj["d2"]
            summary = (f"{'+'.join(d['change_kinds']) or '?'}; arity_changed="
                       f"{d['arity_changed'] or '?'} by {d['changing_side'] or '?'}; "
                       f"decl_visible={d['declaration_visible_in_unit'] or '?'}; "
                       f"{len(d['stale_call_sites'])} call site(s); "
                       f"{d['mismatch_statement'][:90]}")
            n_sites = len(d["stale_call_sites"])
        else:
            d = obj["d3"]
            summary = (f"{d['declaration_kind'] or '?'} {d['change_kind'] or '?'} "
                       f"by {d['changing_side'] or '?'}; "
                       f"{len(d['stale_reference_sites'])} ref site(s); "
                       f"rm2={d['rm2_would_fire']['verdict'] or '?'} "
                       f"joern={d['joern_would_fire']['verdict'] or '?'}")
            n_sites = len(d["stale_reference_sites"])
        rows.append({
            "unit_id": mid, "detector": det, "category": rec["category"],
            "extraction_status": obj["extraction_status"], "usable": ok,
            "why": why, "summary": summary, "n_sites": n_sites,
            "quote_grades": "/".join(grades),
            "cannot_extract": "; ".join(f"{c['field']}: {c['reason']}"
                                        for c in obj["cannot_extract"]),
            "missed_shape": obj["d3"]["missed_shape"] if det == "D3" else "",
            "notes": obj["notes"],
        })

    SPECS.mkdir(parents=True, exist_ok=True)
    with (SPECS / "specs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    for det in ("D1", "D2", "D3"):
        sub = [r for r in rows if r["detector"] == det]
        gd1["per_detector"][det] = {
            "units": len(sub), "usable": sum(r["usable"] for r in sub)}
    n_all = len(rows)
    n_usable = sum(r["usable"] for r in rows)
    gd1.update(pooled={"units": n_all, "usable": n_usable,
                       "fraction": round(n_usable / n_all, 4)},
               threshold=0.80,
               machine_pass=bool(n_usable / n_all >= 0.80),
               quote_grade_distribution=dict(grade_counter))
    # Adjudication blocks (unusable decomposition, amendment rulings) are
    # recorded by hand after Ali rules — a rerun must never wipe them.
    prev = _load(SPECS / "gd1_machine.json", {})
    for k in ("unusable_decomposition", "amendment2_ruling"):
        if k in prev:
            gd1[k] = prev[k]
    _save(SPECS / "gd1_machine.json", gd1)

    lines = [
        "# S-D1 Spec Table — Ali's GD1 eyeball",
        "",
        f"Pooled usable specs: **{n_usable}/{n_all} = {n_usable / n_all:.1%}** "
        f"(GD1 machine threshold 80%: "
        f"{'PASS' if gd1['machine_pass'] else 'FAIL'})",
        "",
    ]
    ruling = gd1.get("amendment2_ruling")
    if ruling:
        rs = ruling.get("rescored", {})
        lines += [
            f"> **Final GD1 verdict: {ruling.get('verdict', '?')}** — plan §12 "
            f"Amendment 2 ({ruling.get('ruled_by', '?')}, {ruling.get('date', '?')}, "
            f"failure-path option b): design targets reduced to "
            f"{ruling.get('target_set', '?')}; re-scored "
            f"**{rs.get('usable', '?')}/{rs.get('units', '?')}**. "
            f"Decomposition + ids: `gd1_machine.json`.",
            "",
        ]
    lines += [
        "| detector | units | usable |",
        "|---|---|---|",
    ]
    for det, v in gd1["per_detector"].items():
        lines.append(f"| {det} | {v['units']} | {v['usable']} |")
    lines += ["", f"Quote-provenance grades over all checked sites: "
                  f"{dict(grade_counter)}", "",
              "| unit | det | status | usable | extraction summary |",
              "|---|---|---|---|---|"]
    for r in rows:
        mark = "✓" if r["usable"] else "✗"
        lines.append(f"| `{r['unit_id']}` | {r['detector']} | "
                     f"{r['extraction_status']} | {mark} {'' if r['usable'] else r['why']} | "
                     f"{r['summary']} |")
    (SPECS / "spec_table.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(gd1, indent=2))
    print(f"wrote {SPECS / 'specs.csv'}, spec_table.md, gd1_machine.json", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"run": run, "report": report}[mode]()
