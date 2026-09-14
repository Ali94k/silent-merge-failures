"""G0 calibration pilot (ISSUES #30, S1, protocol §7).

Runs 10 derivation units (7 A / 3 B) through the full assembly + the FROZEN
Phase-1 prompt on the Message Batches API with structured outputs, to exercise
the production plumbing end-to-end before the real Phase-1 batch (S2). Pilot
outputs are DISCARDED — the 10 units are relabeled in the real run — and that
is recorded in the manifest.

G0 PASS (all required):
  * 10/10 parseable outputs conforming to phase1_output.schema.json
  * no unit over the 30k hard cap
  * truncation-level distribution acceptable (>25% of stratum-B units at T3 is
    a pre-G0 assembly-revisit trigger — measured over the full units.csv)
  * escape-hatch plumbing verified end-to-end (verdict enum incl. escape hatches)

Requires the anthropic SDK (repo-root .venv):
    ../.venv/bin/python tools/taxonomy_g0_pilot.py
Re-attaches to an in-flight batch via reports_taxonomy/g0_pilot/batch_id.txt.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import taxonomy_common as tc  # noqa: E402

G0_DIR = tc.REPORTS / "g0_pilot"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
MANIFEST = tc.REPORTS / "manifest.json"
N_A, N_B = 7, 3
POLL_SECONDS = 20
POLL_TIMEOUT = 3600


def select_units() -> list[str]:
    deriv = {"A": [], "B": []}
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            if r["split"] == "derivation":
                deriv[r["stratum"]].append(r["merge_id"])
    a = sorted(deriv["A"])[:N_A]
    b = sorted(deriv["B"])[:N_B]
    if len(a) < N_A or len(b) < N_B:
        sys.exit(f"ABORT: derivation split too small for G0 (A={len(deriv['A'])} B={len(deriv['B'])}).")
    return a + b


def validate(obj: dict, schema: dict) -> tuple[bool, str]:
    """Structural conformance to phase1_output.schema.json (stdlib-only check)."""
    if not isinstance(obj, dict):
        return False, "not an object"
    for k in schema["required"]:
        if k not in obj:
            return False, f"missing key {k}"
    verdict_enum = schema["properties"]["verdict"]["enum"]
    conf_enum = schema["properties"]["confidence"]["enum"]
    if obj["verdict"] not in verdict_enum:
        return False, f"verdict {obj['verdict']!r} not in enum"
    if obj["confidence"] not in conf_enum:
        return False, f"confidence {obj['confidence']!r} not in enum"
    mech = obj.get("mechanism")
    if not isinstance(mech, dict) or "tags" not in mech or "merge_induced" not in mech:
        return False, "mechanism malformed"
    if not isinstance(obj.get("evidence"), list):
        return False, "evidence not a list"
    return True, "ok"


def main() -> None:
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    G0_DIR.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()

    system, _ = tc.load_prompt()
    schema = tc.load_schema()
    cc = tc._read_json(tc.COMPILE_CHECKS)

    def count_fn(text: str) -> int:
        try:
            return client.messages.count_tokens(
                model=tc.MODEL, messages=[{"role": "user", "content": text}]).input_tokens
        except anthropic.BadRequestError:
            return 10 ** 9

    # ---- assemble the 10 pilot units ----
    mids = select_units()
    scored = {u["merge_id"]: u for u in tc.scored_units()}
    assembled = {}   # mid -> (level, text, tokens, over)
    requests = []
    for mid in mids:
        level, text, tokens, over = tc.assemble_best(scored[mid], cc, count_fn)
        assembled[mid] = {"level": level, "tokens": tokens, "over_30k": over,
                          "stratum": scored[mid]["stratum"]}
        (G0_DIR / f"input__{mid}.txt").write_text(text)
        requests.append(Request(
            custom_id=tc.custom_id("p1", mid),
            params=MessageCreateParamsNonStreaming(
                model=tc.MODEL,
                max_tokens=16000,
                thinking={"type": "adaptive"},
                output_config={"effort": "high",
                               "format": {"type": "json_schema", "schema": schema}},
                system=[{"type": "text", "text": system,
                         "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": text}],
            ),
        ))
    print("assembled 10 pilot units:", {m: (a["stratum"], a["level"], a["tokens"])
                                        for m, a in assembled.items()}, flush=True)

    # ---- submit (or re-attach) ----
    id_file = G0_DIR / "batch_id.txt"
    if id_file.exists():
        batch_id = id_file.read_text().strip()
        print(f"re-attaching to batch {batch_id}", flush=True)
    else:
        batch = client.messages.batches.create(requests=requests)
        batch_id = batch.id
        id_file.write_text(batch_id)
        print(f"submitted batch {batch_id} ({batch.processing_status})", flush=True)

    # ---- poll ----
    t0 = time.time()
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            break
        if time.time() - t0 > POLL_TIMEOUT:
            sys.exit(f"batch still processing after {POLL_TIMEOUT}s — re-run to re-attach.")
        time.sleep(POLL_SECONDS)
    print(f"batch ended after {time.time()-t0:.0f}s: {batch.request_counts}", flush=True)

    # ---- collect + evaluate ----
    cid_to_mid = {tc.custom_id("p1", m): m for m in mids}
    raw = {}
    for result in client.messages.batches.results(batch_id):
        mid = cid_to_mid.get(result.custom_id, result.custom_id)
        rec = {"result_type": result.result.type}
        if result.result.type == "succeeded":
            msg = result.result.message
            rec["stop_reason"] = msg.stop_reason
            text = next((b.text for b in msg.content if b.type == "text"), "")
            rec["raw_text"] = text
            try:
                obj = json.loads(text)
                ok, why = validate(obj, schema)
                rec.update(parsed=obj, conforms=ok, reason=why)
            except json.JSONDecodeError as e:
                rec.update(conforms=False, reason=f"json error: {e}")
            rec["usage"] = {"input": msg.usage.input_tokens, "output": msg.usage.output_tokens}
        raw[mid] = rec
    (G0_DIR / "raw_results.json").write_text(json.dumps(raw, indent=2))

    parseable = sum(1 for r in raw.values() if r.get("conforms"))
    stop_reasons = Counter(r.get("stop_reason") for r in raw.values())
    verdicts = Counter(r.get("parsed", {}).get("verdict") for r in raw.values() if r.get("conforms"))
    max_tokens = max(a["tokens"] for a in assembled.values())
    over = sum(1 for a in assembled.values() if a["over_30k"])
    lvl = Counter(a["level"] for a in assembled.values())

    escape = {"none-identified", "indeterminate", "flaky-suspect"}
    escape_enum_ok = escape.issubset(set(schema["properties"]["verdict"]["enum"]))

    passed = (parseable == 10 and over == 0 and escape_enum_ok)

    print("\n===== G0 evaluation =====")
    print(f"parseable/conforming : {parseable}/10")
    print(f"stop reasons         : {dict(stop_reasons)}")
    print(f"verdict distribution : {dict(verdicts)}")
    print(f"truncation levels    : {dict(sorted(lvl.items()))}")
    print(f"max unit tokens      : {max_tokens} (cap 30000) | over-cap units: {over}")
    print(f"escape-hatch plumbing: enum has escape hatches = {escape_enum_ok}")
    print(f"VERDICT              : {'PASS' if passed else 'FAIL'}")

    # ---- record in manifest (pilot outputs discarded) ----
    manifest = json.loads(MANIFEST.read_text())
    # §12 Amendment 1: custom_id wire-encoding (Batches API pattern constraint).
    manifest.setdefault("conventions", {})["custom_id"] = tc.CUSTOM_ID_SCHEME
    manifest.setdefault("phase1", {})["custom_id_scheme"] = tc.CUSTOM_ID_SCHEME
    manifest["g0_pilot"] = {
        "status": "complete",
        "batch_id": batch_id,
        "model": tc.MODEL,
        "api": "Message Batches",
        "n_units": 10, "n_A": N_A, "n_B": N_B,
        "units": mids,
        "parseable": parseable,
        "stop_reasons": {str(k): v for k, v in stop_reasons.items()},
        "verdict_distribution": {str(k): v for k, v in verdicts.items()},
        "truncation_levels": dict(sorted(lvl.items())),
        "max_unit_tokens": max_tokens,
        "units_over_30k": over,
        "escape_hatch_plumbing_ok": escape_enum_ok,
        "g0_verdict": "PASS" if passed else "FAIL",
        "outputs_discarded": True,
        "relabeled_in_real_run": True,
        "note": "Pilot exercises production plumbing; labels are NOT used. "
                "The 10 units are relabeled in the S2 Phase-1 batch.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"\nrecorded g0 verdict in {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
