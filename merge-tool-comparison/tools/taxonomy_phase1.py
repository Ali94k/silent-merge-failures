"""Phase-1 open-coding production batch (ISSUES #30, S2, protocol §3/§5/§9).

Runs the FROZEN Phase-1 prompt over the **165 derivation-split units only**
(§4 firewall — held-out units get NO Phase-1 request) on the Message Batches
API with structured outputs. Same assembly code path as the G0 pilot
(``taxonomy_common.assemble_best``) so the text is byte-identical to what G0
exercised; the G0 pilot's 10 units are relabeled here like everything else.

Resumable (protocol §9): ``reports_taxonomy/phase1/raw_results.json`` is keyed
by merge_id; ``reports_taxonomy/phase1/batches.json`` records every submitted
batch with its submit-time ``{custom_id: merge_id}`` map. A rerun folds in any
ended batch, then submits a NEW batch for only the still-missing/failed ids.
Results are recovered to merge_id ONLY by inverting the stored submit-time map
(never by string-splitting the custom_id) — §12 Amendment 1.

Run (repo-root .venv — the anthropic SDK is NOT in the merge-tool-comparison
venv; S1 two-venv gotcha):

    ../.venv/bin/python tools/taxonomy_phase1.py

Idempotent: re-run to re-attach to an in-flight batch, collect, and top up.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import taxonomy_common as tc  # noqa: E402

P1_DIR = tc.REPORTS / "phase1"
INPUTS_DIR = P1_DIR / "inputs"
RAW = P1_DIR / "raw_results.json"
BATCHES = P1_DIR / "batches.json"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
MANIFEST = tc.REPORTS / "manifest.json"

MAX_TOKENS = 16000
POLL_SECONDS = 30
# Seconds this invocation will poll before bailing (state is persisted; a rerun
# re-attaches). Override with PHASE1_WALL_BUDGET for a long unattended ride.
WALL_BUDGET = int(os.environ.get("PHASE1_WALL_BUDGET", "7200"))
ESCAPE = {"none-identified", "indeterminate", "flaky-suspect"}


# --------------------------------------------------------------------------- #
# Unit selection — derivation split only.
# --------------------------------------------------------------------------- #

def derivation_mids() -> list[str]:
    mids = []
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            if r["split"] == "derivation":
                mids.append(r["merge_id"])
    return sorted(mids)


# --------------------------------------------------------------------------- #
# Structural conformance check (stdlib; mirrors the pilot's).
# --------------------------------------------------------------------------- #

def validate(obj: dict, schema: dict) -> tuple[bool, str]:
    if not isinstance(obj, dict):
        return False, "not an object"
    for k in schema["required"]:
        if k not in obj:
            return False, f"missing key {k}"
    if obj["verdict"] not in schema["properties"]["verdict"]["enum"]:
        return False, f"verdict {obj['verdict']!r} not in enum"
    if obj["confidence"] not in schema["properties"]["confidence"]["enum"]:
        return False, f"confidence {obj['confidence']!r} not in enum"
    mech = obj.get("mechanism")
    if not isinstance(mech, dict) or "tags" not in mech or "merge_induced" not in mech:
        return False, "mechanism malformed"
    if not isinstance(obj.get("evidence"), list):
        return False, "evidence not a list"
    return True, "ok"


def conforming(rec: dict | None) -> bool:
    return bool(rec) and rec.get("result_type") == "succeeded" and rec.get("conforms")


# --------------------------------------------------------------------------- #
# Persistence helpers.
# --------------------------------------------------------------------------- #

def _load(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def _save(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2))


# --------------------------------------------------------------------------- #
# Main.
# --------------------------------------------------------------------------- #

def main() -> None:
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    P1_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
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

    # ---- assemble all 165 derivation units (identical code path to G0) ----
    mids = derivation_mids()
    scored = {u["merge_id"]: u for u in tc.scored_units()}
    missing_scored = [m for m in mids if m not in scored]
    if missing_scored:
        sys.exit(f"ABORT: {len(missing_scored)} derivation units absent from scored_units: "
                 f"{missing_scored[:5]}")

    assembled: dict[str, dict] = {}          # mid -> {level, tokens, over_30k, text}
    print(f"assembling {len(mids)} derivation units ...", flush=True)
    for i, mid in enumerate(mids, 1):
        level, text, tokens, over = tc.assemble_best(scored[mid], cc, count_fn)
        assembled[mid] = {"level": level, "tokens": tokens, "over_30k": over,
                          "stratum": scored[mid]["stratum"], "text": text}
        (INPUTS_DIR / f"input__{mid}.txt").write_text(text)
        if i % 25 == 0 or i == len(mids):
            print(f"  assembled {i}/{len(mids)}", flush=True)
    over_units = [m for m, a in assembled.items() if a["over_30k"]]
    if over_units:
        sys.exit(f"ABORT: {len(over_units)} units over the 30k cap: {over_units}")
    lvl_dist = Counter(a["level"] for a in assembled.values())
    print(f"truncation levels: {dict(sorted(lvl_dist.items()))}", flush=True)
    print(f"max unit tokens: {max(a['tokens'] for a in assembled.values())} (cap 30000)", flush=True)

    def build_request(mid: str) -> Request:
        return Request(
            custom_id=tc.custom_id("p1", mid),
            params=MessageCreateParamsNonStreaming(
                model=tc.MODEL,
                max_tokens=MAX_TOKENS,
                thinking={"type": "adaptive"},
                output_config={"effort": "high",
                               "format": {"type": "json_schema", "schema": schema}},
                system=[{"type": "text", "text": system,
                         "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": assembled[mid]["text"]}],
            ),
        )

    # ---- resumable state ----
    raw: dict[str, dict] = _load(RAW, {})
    batches: list[dict] = _load(BATCHES, [])

    def collect(batch_id: str, cid_to_mid: dict[str, str]) -> int:
        n = 0
        for result in client.messages.batches.results(batch_id):
            mid = cid_to_mid.get(result.custom_id)
            if mid is None:                       # recover ONLY via submit-time map
                print(f"  WARN: custom_id {result.custom_id} not in submit map — skipped", flush=True)
                continue
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
                rec["usage"] = {"input": msg.usage.input_tokens,
                                "output": msg.usage.output_tokens}
            else:
                rec["error"] = str(getattr(result.result, "error", "")) or result.result.type
            rec["level"] = assembled.get(mid, {}).get("level")
            rec["stratum"] = assembled.get(mid, {}).get("stratum")
            raw[mid] = rec
            n += 1
        _save(RAW, raw)
        return n

    def missing() -> list[str]:
        return [m for m in mids if not conforming(raw.get(m))]

    t0 = time.time()
    while True:
        # 1. fold in any ended-but-uncollected batch.
        for b in batches:
            if b.get("collected"):
                continue
            batch = client.messages.batches.retrieve(b["batch_id"])
            b["status"] = batch.processing_status
            if batch.processing_status == "ended":
                got = collect(b["batch_id"], b["cid_to_mid"])
                b["collected"] = True
                b["request_counts"] = dict(batch.request_counts)
                print(f"collected {got} results from {b['batch_id']} ({batch.request_counts})",
                      flush=True)
            _save(BATCHES, batches)

        miss = missing()
        print(f"missing/failed: {len(miss)}/{len(mids)}", flush=True)
        if not miss:
            print("all derivation units conforming — done.", flush=True)
            break

        inflight = [b for b in batches if not b.get("collected")]
        if inflight:
            if time.time() - t0 > WALL_BUDGET:
                print(f"batch(es) still processing after {WALL_BUDGET}s — re-run to re-attach.",
                      flush=True)
                break
            time.sleep(POLL_SECONDS)
            continue

        # 2. no in-flight batch and units still missing -> submit a fresh batch.
        requests = [build_request(m) for m in miss]
        cid_to_mid = {tc.custom_id("p1", m): m for m in miss}
        batch = client.messages.batches.create(requests=requests)
        batches.append({
            "batch_id": batch.id,
            "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "n": len(miss),
            "mids": miss,
            "cid_to_mid": cid_to_mid,
            "status": batch.processing_status,
            "collected": False,
        })
        _save(BATCHES, batches)
        print(f"submitted batch {batch.id} for {len(miss)} units ({batch.processing_status})",
              flush=True)

    # ---- record in manifest ----
    _record_manifest(assembled, batches, raw, lvl_dist)
    _report(raw, assembled)


def _record_manifest(assembled: dict, batches: list, raw: dict, lvl_dist: Counter) -> None:
    manifest = json.loads(MANIFEST.read_text())
    p1 = manifest.setdefault("phase1", {})
    p1["run"] = {
        "status": "complete" if all(conforming(raw.get(m)) for m in assembled) else "partial",
        "n_units": len(assembled),
        "split": "derivation-only",
        "model": tc.MODEL,
        "api": "Message Batches",
        "max_tokens": MAX_TOKENS,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "high",
                          "format": {"type": "json_schema",
                                     "schema": "prompts_taxonomy/phase1_output.schema.json"}},
        "system_cache_control": {"type": "ephemeral"},
        "batch_ids": [b["batch_id"] for b in batches],
        "batches": [{k: b[k] for k in ("batch_id", "submitted_utc", "n", "status",
                                       "collected", "request_counts")
                     if k in b} for b in batches],
        "truncation_levels": dict(sorted(lvl_dist.items())),
        "max_unit_tokens": max(a["tokens"] for a in assembled.values()),
        "prompt_blob_sha1": tc.git_blob_sha(tc.PROMPT_FILE),
        "schema_blob_sha1": tc.git_blob_sha(tc.SCHEMA_FILE),
        "note": "Derivation split only (§4 firewall). Same assembly code path as G0; "
                "the 10 G0 pilot units are relabeled here. Results recovered via the "
                "submit-time {custom_id: merge_id} map per §12 Amendment 1.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"recorded phase1 run in {MANIFEST.relative_to(ROOT)}", flush=True)


def _report(raw: dict, assembled: dict) -> None:
    done = [m for m in assembled if conforming(raw.get(m))]
    verdicts = Counter(raw[m]["parsed"]["verdict"] for m in done)
    stop = Counter(raw[m].get("stop_reason") for m in done)
    print("\n===== Phase-1 run summary =====")
    print(f"conforming/total : {len(done)}/{len(assembled)}")
    print(f"verdict dist     : {dict(verdicts)}")
    print(f"stop reasons     : {dict(stop)}")
    tot_in = sum(raw[m]["usage"]["input"] for m in done)
    tot_out = sum(raw[m]["usage"]["output"] for m in done)
    # Opus 4.8 batch rates: $2.50/MTok in, $12.50/MTok out (50% of standard).
    cost = tot_in / 1e6 * 2.50 + tot_out / 1e6 * 12.50
    print(f"tokens           : in={tot_in:,} out={tot_out:,}  est cost ${cost:,.2f} (batch rate)")


if __name__ == "__main__":
    main()
