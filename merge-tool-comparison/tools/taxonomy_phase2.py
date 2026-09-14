"""Phase-2 consolidation call (ISSUES #30, S3, protocol §3/§6/§9).

Assembles the two data slots of the FINALIZED Phase-2 prompt and makes ONE
interactive Fable-5 call to draft the codebook:

  {PHASE1_TAGS}  = ALL 165 derivation-split Phase-1 outputs, restricted to
                   unit_id, stratum, verdict, confidence, tags,
                   mechanism.summary, interaction_point (§4 firewall — held-out
                   units are never loaded; the derivation split is read from
                   split_assignment.csv, not from the raw_results file blindly).
  {OLD_TAXONOMY} = the 7 historical categories from
                   semantic_merge_driver/ResearchSummary.xml.

Workload (pinned by the S3 brief + the prompt header):
  model=claude-fable-5, interactive beta.messages.stream (NOT batch),
  betas=["server-side-fallback-2026-06-01"], fallbacks=[{"model":"claude-opus-4-8"}],
  NO thinking param (Fable 5: always on), output_config={"effort":"xhigh"}.
  Streamed so the long high-effort turn does not hit the non-streaming timeout guard.

Output: reports_taxonomy/phase2/codebook_draft.md
Manifest: reports_taxonomy/manifest.json  ->  phase2 block (full request params,
served model / fallback detection, response id, usage).

Run (repo-root .venv — the anthropic SDK is NOT in the merge-tool-comparison venv):

    ../.venv/bin/python tools/taxonomy_phase2.py
"""
from __future__ import annotations

import csv
import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent            # merge-tool-comparison/
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "tools"))
import taxonomy_common as tc  # noqa: E402  (git_blob_sha helper)

PROMPT_FILE = ROOT / "prompts_taxonomy/phase2_consolidation.md"
RAW = ROOT / "reports_taxonomy/phase1/raw_results.json"
SPLIT_CSV = ROOT / "reports_taxonomy/split_assignment.csv"
OLD_TAX_XML = REPO_ROOT / "semantic_merge_driver/ResearchSummary.xml"
MANIFEST = ROOT / "reports_taxonomy/manifest.json"
OUT_DIR = ROOT / "reports_taxonomy/phase2"
OUT_MD = OUT_DIR / "codebook_draft.md"
ASSEMBLED_TXT = OUT_DIR / "phase2_input.txt"        # the exact user block sent

MODEL = "claude-fable-5"
FALLBACK_MODEL = "claude-opus-4-8"
BETAS = ["server-side-fallback-2026-06-01"]
EFFORT = "xhigh"
MAX_TOKENS = 32000


# --------------------------------------------------------------------------- #
# Slot assembly.
# --------------------------------------------------------------------------- #

def derivation_rows() -> list[dict]:
    """(merge_id, stratum) for derivation units only — the §4 firewall gate."""
    out = []
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            if r["split"] == "derivation":
                out.append({"merge_id": r["merge_id"], "stratum": r["stratum"]})
    return sorted(out, key=lambda d: d["merge_id"])


def build_phase1_tags() -> tuple[str, dict]:
    raw = json.loads(RAW.read_text())
    deriv = derivation_rows()
    deriv_ids = {d["merge_id"] for d in deriv}

    # Firewall assertions: every derivation unit present & conforming; nothing else.
    missing = [d["merge_id"] for d in deriv if d["merge_id"] not in raw]
    if missing:
        sys.exit(f"ABORT: {len(missing)} derivation units absent from raw_results: {missing[:5]}")
    non_deriv = [mid for mid in raw if mid not in deriv_ids]
    if non_deriv:
        sys.exit(f"ABORT (firewall): raw_results contains {len(non_deriv)} non-derivation ids: "
                 f"{non_deriv[:5]}")

    verdicts: dict[str, int] = {}
    attributed = 0
    blocks = []
    for d in deriv:
        mid = d["merge_id"]
        rec = raw[mid]
        if not (rec.get("result_type") == "succeeded" and rec.get("conforms")):
            sys.exit(f"ABORT: derivation unit {mid} is not a conforming success")
        p = rec["parsed"]
        verdict = p["verdict"]
        conf = p["confidence"]
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        if verdict == "attributed":
            attributed += 1
        mech = p.get("mechanism", {}) or {}
        tags = mech.get("tags", []) or []
        summary = (mech.get("summary", "") or "").strip()
        ip = (p.get("interaction_point", "") or "").strip()
        # DERIVATION-ONLY, restricted-field row. No per_side_changes, no evidence
        # quotes, no counterfactual — only the seven fields the slot names.
        lines = [f"### {mid}  [stratum {d['stratum']} | verdict {verdict} | confidence {conf}]"]
        lines.append(f"interaction_point: {ip or '(none)'}")
        lines.append(f"tags: {', '.join(tags) if tags else '(none)'}")
        lines.append(f"mechanism: {summary or '(none — escape hatch)'}")
        blocks.append("\n".join(lines))

    header = (f"Total derivation units: {len(deriv)} "
              f"(attributed {attributed}; escape-hatch {len(deriv) - attributed}).\n"
              f"Verdict distribution: "
              f"{', '.join(f'{k}={v}' for k, v in sorted(verdicts.items()))}.\n")
    table = header + "\n" + "\n\n".join(blocks)
    stats = {"n_derivation": len(deriv), "n_attributed": attributed,
             "verdict_distribution": verdicts}
    return table, stats


def build_old_taxonomy() -> str:
    tree = ET.parse(OLD_TAX_XML)
    root = tree.getroot()
    cats = root.findall(".//SemanticConflictCategories/Category")
    lines = []
    for i, c in enumerate(cats, 1):
        name = c.get("name")
        conflict = (c.findtext("Conflict") or "").strip()
        conflict = " ".join(conflict.split())          # collapse whitespace
        lines.append(f"{i}. {name} — {conflict}")
    if len(lines) != 7:
        sys.exit(f"ABORT: expected 7 historical categories, parsed {len(lines)}")
    return "\n".join(lines)


def load_prompt() -> tuple[str, str]:
    txt = PROMPT_FILE.read_text()
    sys_marker = "## SYSTEM (static)\n"
    usr_marker = "## USER (data)\n"
    si = txt.index(sys_marker) + len(sys_marker)
    ui = txt.index(usr_marker)
    system = txt[si:ui].strip("\n")
    user = txt[ui + len(usr_marker):].strip("\n")
    return system, user


# --------------------------------------------------------------------------- #
# Main.
# --------------------------------------------------------------------------- #

def main() -> None:
    import anthropic

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()

    system, user_template = load_prompt()
    phase1_tags, stats = build_phase1_tags()
    old_tax = build_old_taxonomy()
    user = (user_template
            .replace("{OLD_TAXONOMY}", old_tax)
            .replace("{PHASE1_TAGS}", phase1_tags))
    ASSEMBLED_TXT.write_text(user)

    # Token sanity (best-effort; not gated for Phase 2).
    try:
        n_in = client.messages.count_tokens(
            model=MODEL,
            system=system,
            messages=[{"role": "user", "content": user}],
        ).input_tokens
    except Exception as e:                              # noqa: BLE001
        n_in = None
        print(f"count_tokens skipped: {e}", flush=True)

    print(f"derivation units: {stats['n_derivation']} "
          f"(attributed {stats['n_attributed']}); verdicts {stats['verdict_distribution']}",
          flush=True)
    print(f"input tokens (fable-5 count_tokens): {n_in}", flush=True)
    print(f"calling {MODEL} (effort={EFFORT}, fallback={FALLBACK_MODEL}) — streamed ...",
          flush=True)

    t0 = time.time()
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        betas=BETAS,
        fallbacks=[{"model": FALLBACK_MODEL}],
        output_config={"effort": EFFORT},              # NO thinking param (Fable 5)
        system=system,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        msg = stream.get_final_message()
    dt = time.time() - t0

    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    stop_reason = msg.stop_reason

    # Served-model / fallback detection (skill: server-side fallbacks).
    fallback_blocks = [b for b in msg.content if getattr(b, "type", None) == "fallback"]
    iterations = getattr(msg.usage, "iterations", None) or []
    fallback_ran = any(getattr(e, "type", None) == "fallback_message" for e in iterations)
    served_model = msg.model

    print(f"\ncompleted in {dt:.0f}s | stop_reason={stop_reason} | served_model={served_model} "
          f"| fallback_ran={fallback_ran} | id={msg.id}", flush=True)

    if stop_reason == "refusal":
        (OUT_DIR / "REFUSAL.txt").write_text(str(getattr(msg, "stop_details", "")))
        sys.exit("ABORT: whole chain refused — see phase2/REFUSAL.txt; no codebook written")
    if stop_reason != "end_turn":
        print(f"WARNING: stop_reason={stop_reason} (not end_turn) — output may be truncated; "
              f"raising max_tokens or re-running may be needed.", flush=True)

    OUT_MD.write_text(text)
    print(f"wrote {OUT_MD.relative_to(ROOT)} ({len(text)} chars)", flush=True)

    _record_manifest(msg, served_model, fallback_ran, fallback_blocks, iterations,
                     n_in, stats, dt)


def _record_manifest(msg, served_model, fallback_ran, fallback_blocks, iterations,
                     n_in, stats, dt) -> None:
    manifest = json.loads(MANIFEST.read_text())
    u = msg.usage
    manifest["phase2"] = {
        "status": "codebook_draft_produced (pending Ali G2 ruling + freeze)",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_requested": MODEL,
        "api": "interactive beta.messages.stream (NOT batch)",
        "request_params": {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "betas": BETAS,
            "fallbacks": [{"model": FALLBACK_MODEL}],
            "output_config": {"effort": EFFORT},
            "thinking": "omitted (Fable 5: always on; explicit config 400s)",
            "streamed": True,
        },
        "response": {
            "id": msg.id,
            "served_model": served_model,
            "fallback_ran": fallback_ran,
            "n_fallback_blocks": len(fallback_blocks),
            "iteration_types": [getattr(e, "type", None) for e in iterations],
            "stop_reason": msg.stop_reason,
            "usage": {
                "input_tokens": getattr(u, "input_tokens", None),
                "output_tokens": getattr(u, "output_tokens", None),
                "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", None),
                "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", None),
            },
            "wall_seconds": round(dt, 1),
        },
        "input": {
            "count_tokens_fable5": n_in,
            "n_derivation_units": stats["n_derivation"],
            "n_attributed": stats["n_attributed"],
            "verdict_distribution": stats["verdict_distribution"],
            "split": "derivation-only (§4 firewall)",
        },
        "prompt_blob_sha1": tc.git_blob_sha(PROMPT_FILE),
        "output": "reports_taxonomy/phase2/codebook_draft.md",
        "note": "Prompt wording finalized + committed BEFORE the {PHASE1_TAGS} slot was "
                "assembled (S3 ordering). Codebook is DRAFT — frozen only after Ali's G2 "
                "ruling in the freeze commit; no Phase-3 request may exist before then.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"recorded phase2 in {MANIFEST.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
