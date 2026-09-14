"""G2 FREEZE — apply Ali's ruling + freeze the codebook & Phase-3 enum (ISSUES #30, S3, §6/§7 iv).

One-shot: reads the Fable-5 draft + Ali's `g2_codebook_rulings.json` (overall=APPROVE),
applies the rulings (here: 2 RENAME of id+display-name, rest ACCEPT), and writes the two
frozen artifacts of the single freeze commit:

  reports_taxonomy/phase2/codebook_frozen.md          (draft + renames + frozen header)
  prompts_taxonomy/phase3_output.schema.json          (category enum filled, skeleton note removed)

Also records manifest.phase2.freeze. Refuses to run unless overall == APPROVE.

    ../.venv/bin/python tools/taxonomy_freeze.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "reports_taxonomy/phase2/codebook_draft.md"
RULINGS = ROOT / "reports_taxonomy/phase2/g2_codebook_rulings.json"
FROZEN = ROOT / "reports_taxonomy/phase2/codebook_frozen.md"
SCHEMA = ROOT / "prompts_taxonomy/phase3_output.schema.json"
MANIFEST = ROOT / "reports_taxonomy/manifest.json"

# Display-name updates that accompany the two id renames (de-"vs" to match).
NAME_UPDATES = {
    "Import pruning vs. concurrent use": "Stale usage of a pruned import",
    "Runtime-behavior change vs. dependent code": "Stale expectation of changed behavior",
}
ESCAPE = ["none-identified", "indeterminate", "flaky-suspect"]


def main() -> None:
    rul = json.loads(RULINGS.read_text())
    if rul.get("overall") != "APPROVE":
        sys.exit(f"ABORT: overall ruling is {rul.get('overall')!r}, not APPROVE — will not freeze.")

    # ---- build the id-rename map from the ruling (action==RENAME only) ----
    renames: dict[str, str] = {}
    for c in rul["categories"]:
        r = c["ruling"]
        if r["action"] == "RENAME":
            new = r["new_id"].strip()
            if not new:
                sys.exit(f"ABORT: RENAME on {c['id']} has empty new_id.")
            renames[c["id"]] = new
        elif r["action"] != "ACCEPT":
            sys.exit(f"ABORT: unhandled action {r['action']!r} on {c['id']} — this freeze script "
                     f"only handles RENAME/ACCEPT; extend it for merge/split/edit/reject.")
    # collision guard: no two categories may end up with the same id.
    final_ids = [renames.get(c["id"], c["id"]) for c in rul["categories"]]
    if len(set(final_ids)) != len(final_ids):
        sys.exit(f"ABORT: id collision after renames: {final_ids}")

    # ---- apply to the draft body ----
    draft = DRAFT.read_text()
    body = draft.split("## 1. Preamble", 1)[1]
    body = "## 1. Preamble" + body
    for old, new in renames.items():
        if old not in body:
            sys.exit(f"ABORT: rename source id {old!r} not found in draft.")
        body = body.replace(old, new)            # id token is unique; global is safe
    for old_name, new_name in NAME_UPDATES.items():
        body = body.replace(old_name, new_name)

    # verify: old ids fully gone, new ids present as headings
    for old, new in renames.items():
        if old in body:
            sys.exit(f"ABORT: old id {old!r} still present after rename.")
        if f"### `{new}`" not in body:
            sys.exit(f"ABORT: renamed heading '### `{new}`' missing.")

    header = (
        "# Codebook (FROZEN) — Mechanism Categories for Clean-Merge Semantic Breakages\n\n"
        "**Frozen:** 2026-07-11 (Session 3, G2 condition iv). **Ruling:** Ali **APPROVE** via "
        "`mapping_ui.html` (`reports_taxonomy/phase2/g2_codebook_rulings.json`); escape-hatch "
        "stratum framing acknowledged.\n"
        "**Derived from:** `codebook_draft.md` (claude-fable-5, commit `0afaae7`); G2 machine "
        "conditions (i)–(iii) PASS (`phase2/g2_eval.md`).\n"
        "**Rulings applied:** 2 RENAME (id + display name), 7 ACCEPT (incl. `residual-other`); no "
        "merges/splits. `stale-reference-to-renamed-or-relocated-declaration` and "
        "`stale-caller-of-changed-signature` kept separate per Ali. Renames:\n"
        + "".join(f"- `{o}` → `{n}`\n" for o, n in renames.items())
        + "\nThis is the FROZEN instrument for Phase-3 closed coding of the **full census** (both "
        "splits). Post-freeze changes only via a dated protocol §12 amendment + full Phase-3 "
        "relabel. It covers the 60 attributed derivation units; the 105 escape-hatch units are the "
        "first-class not-cleanly-merge-attributable stratum reported in FINDINGS.\n\n---\n\n"
    )
    FROZEN.write_text(header + body)

    # ---- freeze the Phase-3 schema enum from the frozen category headings ----
    frozen_ids = re.findall(r"^### `([^`]+)`", body, re.M)
    named = [i for i in frozen_ids if i != "residual-other"]
    if "residual-other" not in frozen_ids:
        sys.exit("ABORT: residual-other missing from frozen codebook.")
    primary_enum = named + ["residual-other"] + ESCAPE
    secondary_enum = named + ["residual-other"]

    schema = json.loads(SCHEMA.read_text())
    schema.pop("_skeleton_note", None)
    schema["properties"]["primary"]["enum"] = primary_enum
    schema["properties"]["secondary"]["items"]["enum"] = secondary_enum
    SCHEMA.write_text(json.dumps(schema, indent=2) + "\n")

    # ---- record freeze in manifest ----
    manifest = json.loads(MANIFEST.read_text())
    manifest.setdefault("phase2", {})["freeze"] = {
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "overall_ruling": "APPROVE",
        "escape_ack": rul.get("escape_ack"),
        "rulings_file": "reports_taxonomy/phase2/g2_codebook_rulings.json",
        "renames": renames,
        "name_updates": NAME_UPDATES,
        "accepts": [c["id"] for c in rul["categories"] if c["ruling"]["action"] == "ACCEPT"],
        "frozen_codebook": "reports_taxonomy/phase2/codebook_frozen.md",
        "phase3_schema": "prompts_taxonomy/phase3_output.schema.json",
        "frozen_category_ids": named,
        "primary_enum": primary_enum,
        "secondary_enum": secondary_enum,
        "note": "Single freeze commit (this commit). frozen_codebook_commit is pinned in §9 at "
                "Phase-3 time (S4), pointing back to this commit. No Phase-3 request exists yet.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))

    print("FROZEN OK")
    print(f"  renames applied: {renames}")
    print(f"  frozen category ids ({len(named)} named + residual-other): {named}")
    print(f"  primary enum: {primary_enum}")
    print(f"  wrote {FROZEN.relative_to(ROOT)} + {SCHEMA.relative_to(ROOT)} + manifest.phase2.freeze")


if __name__ == "__main__":
    main()
