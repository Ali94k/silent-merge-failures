"""Phase-3 closed-coding DOUBLE batch (ISSUES #30, S4, protocol §3/§6/§7/§9).

Two independent, request-identical passes (``a`` and ``b``) over the FULL scored
census (275 units = 165 derivation + 110 held-out; §4 — labeling held-out with a
frozen instrument is legitimate). Same model/API/assembly as Phase 1 so the §8
stability metric is comparable; the only differences are the SYSTEM prefix (the
frozen closed-coding instrument from ``prompts_taxonomy/phase3_closed_coding.md``)
and the schema (``phase3_output.schema.json``, frozen enum).

Per-unit USER assembly is byte-identical to Phase 1 (``tc.assemble_best`` ->
``tc.render_user``). Integrity guard: for every derivation unit the freshly
assembled text is asserted equal to the committed ``phase1/inputs/`` file.

Resumable (§9): each pass keeps ``reports_taxonomy/phase3/raw_results_{a,b}.json``
(keyed by merge_id) and ``batches_{a,b}.json`` (submit-time {custom_id: merge_id}
maps). A rerun folds in ended batches, then submits a fresh batch for only the
still missing/failed ids. Results recover to merge_id ONLY by inverting the
stored submit-time map (never by string-splitting the custom_id) — §12 Amdt 1.

Run (repo-root .venv — the anthropic SDK is NOT in the mtc venv):

    ../.venv/bin/python tools/taxonomy_phase3.py

Idempotent: re-run to re-attach to in-flight batches, collect, and top up.
Env: PHASE3_WALL_BUDGET (seconds this invocation polls before bailing).
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

P3_DIR = tc.REPORTS / "phase3"
INPUTS_DIR = P3_DIR / "inputs"
P1_INPUTS = tc.REPORTS / "phase1" / "inputs"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
UNITS_CSV = tc.REPORTS / "units.csv"
MANIFEST = tc.REPORTS / "manifest.json"
PROMPT = ROOT / "prompts_taxonomy/phase3_closed_coding.md"
SCHEMA = ROOT / "prompts_taxonomy/phase3_output.schema.json"

MAX_TOKENS = 16000
POLL_SECONDS = 30
WALL_BUDGET = int(os.environ.get("PHASE3_WALL_BUDGET", "7200"))
PASSES = [("a", "p3a"), ("b", "p3b")]
ESCAPE = {"none-identified", "indeterminate", "flaky-suspect"}


# --------------------------------------------------------------------------- #
# Population + instrument loaders.
# --------------------------------------------------------------------------- #

def scored_mids_and_split() -> tuple[list[str], dict[str, str]]:
    mids, split = [], {}
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            mids.append(r["merge_id"])
            split[r["merge_id"]] = r["split"]
    return sorted(mids), split


def load_system() -> str:
    txt = PROMPT.read_text()
    sm = "## SYSTEM (static, cacheable)\n"
    um = "## USER (per unit)\n"
    return txt[txt.index(sm) + len(sm): txt.index(um)].strip("\n")


def load_schema() -> dict:
    return json.loads(SCHEMA.read_text())


def units_csv_levels() -> dict[str, str]:
    out = {}
    with open(UNITS_CSV) as fh:
        for r in csv.DictReader(fh):
            if r["status"] == "scored":
                out[r["merge_id"]] = r["truncation_level"]
    return out


# --------------------------------------------------------------------------- #
# Structural conformance (phase-3 schema).
# --------------------------------------------------------------------------- #

def validate(obj: dict, schema: dict) -> tuple[bool, str]:
    if not isinstance(obj, dict):
        return False, "not an object"
    for k in schema["required"]:
        if k not in obj:
            return False, f"missing key {k}"
    prim_enum = schema["properties"]["primary"]["enum"]
    sec_enum = schema["properties"]["secondary"]["items"]["enum"]
    if obj["primary"] not in prim_enum:
        return False, f"primary {obj['primary']!r} not in enum"
    sec = obj.get("secondary")
    if not isinstance(sec, list):
        return False, "secondary not a list"
    if len(sec) > 2:
        return False, f"secondary has {len(sec)} > 2 items"
    for s in sec:
        if s not in sec_enum:
            return False, f"secondary {s!r} not in enum"
    if obj["confidence"] not in schema["properties"]["confidence"]["enum"]:
        return False, f"confidence {obj['confidence']!r} not in enum"
    if not isinstance(obj.get("evidence"), list):
        return False, "evidence not a list"
    return True, "ok"


def conforming(rec: dict | None) -> bool:
    return bool(rec) and rec.get("result_type") == "succeeded" and rec.get("conforms")


# --------------------------------------------------------------------------- #
# Persistence.
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

    P3_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()

    system = load_system()
    schema = load_schema()
    cc = tc._read_json(tc.COMPILE_CHECKS)

    def count_fn(text: str) -> int:
        try:
            return client.messages.count_tokens(
                model=tc.MODEL, messages=[{"role": "user", "content": text}]).input_tokens
        except anthropic.BadRequestError:
            return 10 ** 9

    # ---- assemble all 275 scored units (identical code path to Phase 1) ----
    mids, split = scored_mids_and_split()
    scored = {u["merge_id"]: u for u in tc.scored_units()}
    missing_scored = [m for m in mids if m not in scored]
    if missing_scored:
        sys.exit(f"ABORT: {len(missing_scored)} scored units absent from scored_units(): "
                 f"{missing_scored[:5]}")

    csv_levels = units_csv_levels()
    assembled: dict[str, dict] = {}
    mismatches, level_drift = [], []
    print(f"assembling {len(mids)} scored units ...", flush=True)
    for i, mid in enumerate(mids, 1):
        level, text, tokens, over = tc.assemble_best(scored[mid], cc, count_fn)
        assembled[mid] = {"level": level, "tokens": tokens, "over_30k": over,
                          "stratum": scored[mid]["stratum"], "split": split[mid], "text": text}
        p3_in = INPUTS_DIR / f"input__{mid}.txt"
        p3_in.write_text(text)
        # Integrity: derivation units must reproduce the committed Phase-1 input.
        # Compare on-disk BYTES (not in-memory text vs read_text): scenario source
        # carries CRLF line endings that read_text universal-normalizes to LF, so a
        # text-vs-read_text compare falsely flags the 13 CR-bearing units. Both files
        # are written through the identical write_text path, so a byte compare is the
        # true reproducibility check.
        if split[mid] == "derivation":
            p1 = P1_INPUTS / f"input__{mid}.txt"
            if p1.exists() and p1.read_bytes() != p3_in.read_bytes():
                mismatches.append(mid)
        if csv_levels.get(mid) and csv_levels[mid] != level:
            level_drift.append((mid, csv_levels[mid], level))
        if i % 50 == 0 or i == len(mids):
            print(f"  assembled {i}/{len(mids)}", flush=True)

    over_units = [m for m, a in assembled.items() if a["over_30k"]]
    if over_units:
        sys.exit(f"ABORT: {len(over_units)} units over the 30k cap: {over_units}")
    if mismatches:
        sys.exit(f"ABORT: {len(mismatches)} derivation units differ from Phase-1 inputs "
                 f"(assembly not reproducible): {mismatches[:5]}")
    if level_drift:
        print(f"WARN: {len(level_drift)} units' truncation level differs from units.csv "
              f"(first: {level_drift[:3]})", flush=True)
    lvl_dist = Counter(a["level"] for a in assembled.values())
    print(f"assembly OK. derivation byte-identity vs Phase-1: {len(mids)-len(mismatches)}/"
          f"{sum(1 for m in mids if split[m]=='derivation')} derivation matched", flush=True)
    print(f"truncation levels: {dict(sorted(lvl_dist.items()))}", flush=True)
    print(f"max unit tokens: {max(a['tokens'] for a in assembled.values())} (cap 30000)", flush=True)

    def build_request(prefix: str, mid: str) -> Request:
        return Request(
            custom_id=tc.custom_id(prefix, mid),
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

    # ---- per-pass resumable state ----
    passes = {}
    for letter, prefix in PASSES:
        passes[letter] = {
            "prefix": prefix,
            "raw_path": P3_DIR / f"raw_results_{letter}.json",
            "batches_path": P3_DIR / f"batches_{letter}.json",
            "raw": _load(P3_DIR / f"raw_results_{letter}.json", {}),
            "batches": _load(P3_DIR / f"batches_{letter}.json", []),
        }

    def collect(st: dict, batch_id: str, cid_to_mid: dict[str, str]) -> int:
        n = 0
        for result in client.messages.batches.results(batch_id):
            mid = cid_to_mid.get(result.custom_id)
            if mid is None:
                print(f"  WARN[{st['prefix']}]: custom_id {result.custom_id} not in submit map — skipped",
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
            rec["split"] = assembled.get(mid, {}).get("split")
            st["raw"][mid] = rec
            n += 1
        _save(st["raw_path"], st["raw"])
        return n

    def missing(st: dict) -> list[str]:
        return [m for m in mids if not conforming(st["raw"].get(m))]

    def step(st: dict) -> None:
        """One fold+submit cycle for a pass (non-blocking)."""
        for b in st["batches"]:
            if b.get("collected"):
                continue
            batch = client.messages.batches.retrieve(b["batch_id"])
            b["status"] = batch.processing_status
            if batch.processing_status == "ended":
                got = collect(st, b["batch_id"], b["cid_to_mid"])
                b["collected"] = True
                b["request_counts"] = dict(batch.request_counts)
                print(f"[{st['prefix']}] collected {got} from {b['batch_id']} "
                      f"({batch.request_counts})", flush=True)
            _save(st["batches_path"], st["batches"])
        miss = missing(st)
        inflight = [b for b in st["batches"] if not b.get("collected")]
        if miss and not inflight:
            reqs = [build_request(st["prefix"], m) for m in miss]
            cid_to_mid = {tc.custom_id(st["prefix"], m): m for m in miss}
            batch = client.messages.batches.create(requests=reqs)
            st["batches"].append({
                "batch_id": batch.id,
                "submitted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "n": len(miss), "mids": miss, "cid_to_mid": cid_to_mid,
                "status": batch.processing_status, "collected": False,
            })
            _save(st["batches_path"], st["batches"])
            print(f"[{st['prefix']}] submitted batch {batch.id} for {len(miss)} units "
                  f"({batch.processing_status})", flush=True)

    # ---- drive both passes concurrently ----
    t0 = time.time()
    while True:
        for st in passes.values():
            step(st)
        remaining = {p: len(missing(st)) for p, st in passes.items()}
        print(f"missing: " + "  ".join(f"{p}={n}" for p, n in remaining.items())
              + f"  (of {len(mids)})", flush=True)
        if all(n == 0 for n in remaining.values()):
            print("both passes complete — all units conforming.", flush=True)
            break
        any_inflight = any(not b.get("collected") for st in passes.values() for b in st["batches"])
        if any_inflight and time.time() - t0 > WALL_BUDGET:
            print(f"batches still processing after {WALL_BUDGET}s — re-run to re-attach.", flush=True)
            break
        if not any_inflight and all(n == 0 for n in remaining.values()):
            break
        time.sleep(POLL_SECONDS)

    _record_manifest(assembled, passes, lvl_dist, mids, split)
    _report(passes, mids)


def _record_manifest(assembled, passes, lvl_dist, mids, split) -> None:
    manifest = json.loads(MANIFEST.read_text())
    p3 = manifest.setdefault("phase3", {})
    all_done = all(conforming(passes[l]["raw"].get(m)) for l, _ in PASSES for m in mids)
    p3["status"] = "complete" if all_done else "partial"
    p3["runs"] = {}
    for letter, prefix in PASSES:
        st = passes[letter]
        done = [m for m in mids if conforming(st["raw"].get(m))]
        tot_in = sum(st["raw"][m]["usage"]["input"] for m in done)
        tot_out = sum(st["raw"][m]["usage"]["output"] for m in done)
        p3["runs"][letter] = {
            "prefix": prefix,
            "n_conforming": len(done),
            "n_units": len(mids),
            "batch_ids": [b["batch_id"] for b in st["batches"]],
            "batches": [{k: b[k] for k in ("batch_id", "submitted_utc", "n", "status",
                                           "collected", "request_counts") if k in b}
                        for b in st["batches"]],
            "tokens": {"input": tot_in, "output": tot_out},
            "est_cost_usd_batch_rate": round(tot_in / 1e6 * 2.50 + tot_out / 1e6 * 12.50, 2),
        }
    p3["truncation_levels"] = dict(sorted(lvl_dist.items()))
    p3["max_unit_tokens"] = max(a["tokens"] for a in assembled.values())
    p3["split_counts"] = dict(Counter(split[m] for m in mids))
    p3["prompt_blob_sha1"] = {
        "phase3_closed_coding.md": tc.git_blob_sha(PROMPT),
        "phase3_output.schema.json": tc.git_blob_sha(SCHEMA),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"recorded phase3 runs in {MANIFEST.relative_to(ROOT)}", flush=True)


def _report(passes, mids) -> None:
    print("\n===== Phase-3 double-batch summary =====")
    for letter, prefix in PASSES:
        st = passes[letter]
        done = [m for m in mids if conforming(st["raw"].get(m))]
        prim = Counter(st["raw"][m]["parsed"]["primary"] for m in done)
        stop = Counter(st["raw"][m].get("stop_reason") for m in done)
        tot_in = sum(st["raw"][m]["usage"]["input"] for m in done)
        tot_out = sum(st["raw"][m]["usage"]["output"] for m in done)
        cost = tot_in / 1e6 * 2.50 + tot_out / 1e6 * 12.50
        print(f"\n-- pass {letter} ({prefix}) : {len(done)}/{len(mids)} conforming --")
        print(f"   primary dist : {dict(sorted(prim.items(), key=lambda kv: -kv[1]))}")
        print(f"   stop reasons : {dict(stop)}")
        print(f"   tokens       : in={tot_in:,} out={tot_out:,}  est ${cost:,.2f} (batch rate)")


if __name__ == "__main__":
    main()
