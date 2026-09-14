#!/usr/bin/env python3
"""S10z renderer: entries/ + cross_theme_resolutions.json -> docs/DECISIONS.md.

Deterministic. The finished document is generated output — to change it, edit
the entries JSONs or the resolutions file and re-run this script, then re-run
verify_entries.py. Hand edits to docs/DECISIONS.md will be clobbered.

Numbering: sections in READER_ORDER, entries chronological within a section
(date_from, stable on the consolidation session's original order), numbered
D-001.. sequentially in document order. The assignment is also written to
numbering.json so S11 and later tooling can resolve slug -> number without
parsing the rendered markdown.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
OUT = ROOT / "docs" / "DECISIONS.md"
NUMBERING = HERE / "numbering.json"

READER_ORDER = [
    ("scope-architecture", "Scope & project architecture"),
    ("backends-routing", "Merge backends & routing"),
    ("detection", "Detection layer"),
    ("evaluation-oracles", "Evaluation methodology & oracles"),
    ("corpus-sampling", "Corpora & sampling"),
    ("adjudication", "Adjudication & human oversight"),
    ("gates-freeze", "Gates, freezes & pre-registration"),
    ("infrastructure", "Infrastructure, Docker & compute"),
    ("repo-conventions", "Repository & working conventions"),
    ("thesis-framing", "Thesis framing & reporting"),
    ("other", "Cross-cutting & meta"),
]

PROV_TAG = {"chat": "`[chat]`", "reconstructed": "`[recon]`", "mixed": "`[mixed]`"}


def die(msg: str) -> None:
    print(f"FATAL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load() -> tuple[dict, dict]:
    themes = {}
    for p in sorted((HERE / "entries").glob("*.json")):
        d = json.loads(p.read_text())
        themes[d["theme"]] = d
    res = json.loads((HERE / "cross_theme_resolutions.json").read_text())
    return themes, res


def validate(themes: dict, res: dict) -> None:
    if {t for t, _ in READER_ORDER} != set(themes):
        die(f"READER_ORDER != themes on disk: {sorted(themes)}")
    entry_index = {(t, e["slug"]) for t, d in themes.items() for e in d["entries"]}
    # every flag covered exactly once, ids and slugs consistent
    seen = set()
    for r in res["resolutions"]:
        t, i = r["id"].rsplit(":", 1)
        flags = themes[t].get("cross_theme") or []
        if not i.isdigit() or int(i) >= len(flags):
            die(f"resolution {r['id']}: no such flag")
        f = flags[int(i)]
        if f["slug"] != r["slug"] or f["relation"] != r["relation"]:
            die(f"resolution {r['id']}: slug/relation mismatch with the flag")
        if r["id"] in seen:
            die(f"resolution {r['id']}: duplicated")
        seen.add(r["id"])
        if r["resolution"] not in ("resolved", "no-counterpart"):
            die(f"resolution {r['id']}: bad resolution {r['resolution']!r}")
        if r["resolution"] == "resolved" and not r["targets"]:
            die(f"resolution {r['id']}: resolved but no targets")
        if r["resolution"] == "no-counterpart" and r["targets"]:
            die(f"resolution {r['id']}: no-counterpart yet has targets")
        for tgt in r["targets"]:
            if (tgt["theme"], tgt["slug"]) not in entry_index:
                die(f"resolution {r['id']}: target {tgt} is not an entry")
    for t, d in themes.items():
        n = len(d.get("cross_theme") or [])
        covered = sum(1 for r in res["resolutions"] if r["id"].rsplit(":", 1)[0] == t)
        if n != covered:
            die(f"{t}: {n} flags but {covered} resolutions — silence is not allowed")
    for e in res.get("extra_edges", []):
        for end in (e["from"], e["to"]):
            if (end["theme"], end["slug"]) not in entry_index:
                die(f"extra_edge end {end} is not an entry")


def assign_numbers(themes: dict) -> dict[str, dict]:
    """slug -> {n, theme, title, date}; slugs are globally unique (checked)."""
    numbers: dict[str, dict] = {}
    n = 0
    for theme, _ in READER_ORDER:
        entries = themes[theme]["entries"]
        for e in sorted(entries, key=lambda e: (e["date_from"],
                                                entries.index(e))):
            n += 1
            if e["slug"] in numbers:
                die(f"slug {e['slug']!r} not globally unique")
            numbers[e["slug"]] = {"n": n, "theme": theme,
                                  "title": e["title"], "date": e["date_from"]}
    if len(numbers) != sum(len(d["entries"]) for d in themes.values()):
        die("numbering did not cover every entry exactly once")
    return numbers


def dn(num: int) -> str:
    return f"D-{num:03d}"


def link(slug: str, numbers: dict) -> str:
    n = numbers[slug]["n"]
    return f"[{dn(n)}](#{dn(n).lower()})"


def rewrite_slugs(text: str, numbers: dict, own: str) -> str:
    """Replace exact slug tokens in free text with D-nnn links."""
    if not text:
        return text
    for slug in numbers:
        if slug == own or slug not in text:
            continue
        text = re.sub(rf"(?<![a-z0-9-]){re.escape(slug)}(?![a-z0-9-])",
                      link(slug, numbers), text)
    return text


def quote_block(q: dict) -> str:
    lines = q["text"].split("\n")
    body = "\n".join("> " + ln for ln in lines)
    return f"{body}\n>\n> — `{q['file']}:{q['line']}`"


def build_xrefs(themes: dict, res: dict, numbers: dict) -> dict:
    """(theme, slug) -> list of rendered cross-theme lines."""
    out: dict[tuple, list] = {}
    raiser_targets: dict[tuple, set] = {}
    for r in res["resolutions"]:
        t = r["id"].rsplit(":", 1)[0]
        key = (t, r["slug"])
        raiser_targets.setdefault(key, set()).update(
            (x["theme"], x["slug"]) for x in r["targets"])

    inverse = {"supersedes": "superseded by", "superseded-by": "supersedes",
               "duplicates": "duplicated by", "contradicts": "in tension with",
               "depends-on": "depended on by"}
    for r in res["resolutions"]:
        t = r["id"].rsplit(":", 1)[0]
        key = (t, r["slug"])
        note = rewrite_slugs(r["note"], numbers, r["slug"])
        if r["resolution"] == "no-counterpart":
            out.setdefault(key, []).append(
                f"*{r['relation']}* → **no counterpart entry exists** — {note}")
            continue
        tgts = ", ".join(link(x["slug"], numbers) for x in r["targets"])
        out.setdefault(key, []).append(f"*{r['relation']}* → {tgts} — {note}")
        # reciprocal pointers on targets, unless the target raised its own
        # flag back at this entry (mirror pairs render their own note)
        for x in r["targets"]:
            tkey = (x["theme"], x["slug"])
            if key in [(a, b) for (a, b) in raiser_targets.get(tkey, set())]:
                continue
            out.setdefault(tkey, []).append(
                f"*{inverse[r['relation']]}* ← {link(r['slug'], numbers)} "
                f"(see the reconciliation note there)")
    for e in res.get("extra_edges", []):
        f_, t_ = e["from"], e["to"]
        note = rewrite_slugs(e["note"], numbers, f_["slug"])
        out.setdefault((f_["theme"], f_["slug"]), []).append(
            f"*{e['relation']}* → {link(t_['slug'], numbers)} — {note}")
        out.setdefault((t_["theme"], t_["slug"]), []).append(
            f"*declines* ← {link(f_['slug'], numbers)} — see the note there")
    return out


def render_entry(e: dict, theme: str, numbers: dict, xrefs: dict) -> str:
    num = numbers[e["slug"]]["n"]
    own = e["slug"]
    parts = [f'### <a id="{dn(num).lower()}"></a>{dn(num)} — {e["title"]}\n']

    dates = e["date_from"] + (f" → {e['date_to']}" if e.get("date_to") else "")
    meta = (f"`{dates}` · **{e['status']}** · {PROV_TAG[e['provenance']]} · "
            f"corroboration: {e['corroboration']} · confidence: {e['confidence']} · "
            f"actors: {e['actors']}")
    parts.append(meta + "\n")
    if e.get("actors_note"):
        parts.append(f"*Actors note: {e['actors_note']}*\n")

    parts.append(f"**Decision.** {rewrite_slugs(e['decision'], numbers, own)}\n")
    if e.get("rationale_recorded") and e.get("rationale"):
        parts.append(f"**Why.** {rewrite_slugs(e['rationale'], numbers, own)}\n")
    else:
        parts.append("**Why.** *No rationale recorded in the sources — a finding "
                     "about the record, not an omission of this document.*\n")

    status_bits = [e["status"] + "."]
    if e.get("status_note"):
        status_bits.append(rewrite_slugs(e["status_note"], numbers, own))
    if e.get("superseded_by"):
        sb = e["superseded_by"]
        status_bits.append(f"Superseded by {link(sb, numbers)} — {numbers[sb]['title']}.")
    sup = e.get("supersedes") or []
    sup_r = []
    for s in sup:
        if s in numbers:
            sup_r.append(f"{link(s, numbers)} — {numbers[s]['title']}")
        else:
            sup_r.append(f"*{s}*")
    if sup_r:
        status_bits.append("Supersedes: " + "; ".join(sup_r) + ".")
    parts.append("**Status.** " + " ".join(status_bits) + "\n")

    for line in xrefs.get((theme, own), []):
        parts.append(f"**Cross-theme.** {line}\n")

    src = "`" + "`, `".join(e["sources"]) + "`"
    art = ""
    if e.get("artifacts"):
        art = " · Artifacts: " + ", ".join(f"`{a}`" for a in e["artifacts"])
    parts.append(f"**Source.** {src}{art}\n")
    for q in e.get("evidence") or []:
        parts.append(quote_block(q) + "\n")
    return "\n".join(parts)


def front_matter(themes: dict, res: dict, numbers: dict) -> str:
    all_entries = [e for d in themes.values() for e in d["entries"]]
    st = Counter(e["status"] for e in all_entries)
    pv = Counter(e["provenance"] for e in all_entries)
    cb = Counter(e["corroboration"] for e in all_entries)
    ac = Counter(e["actors"] for e in all_entries)
    cf = Counter(e["confidence"] for e in all_entries)
    quotes = sum(len(e["evidence"]) for e in all_entries)
    np_total = sum(len(d["not_promoted"]) for d in themes.values())
    primary_total = sum(d["slice_primary_total"] for d in themes.values())
    n_res = sum(1 for r in res["resolutions"] if r["resolution"] == "resolved")
    n_noc = sum(1 for r in res["resolutions"] if r["resolution"] == "no-counterpart")
    long_titles = sum(1 for e in all_entries if len(e["title"]) > 90)

    return f"""# Decision Record

Design, architecture and methodology decisions for this thesis project — **v2, rebuilt
2026-07-25** from the complete distilled session corpus plus git history and the plan
documents (statuses resolved against the repo 2026-07-26), under the frozen protocol in
[`docs/decision-record/PROTOCOL.md`](decision-record/PROTOCOL.md). This file is
**generated** by `docs/decision-record/render_decisions.py` from the consolidated
entries in `docs/decision-record/entries/` — edit those and re-render; do not edit
this file by hand. For browsing, an interactive navigator over the same entries
lives at [`docs/decisions_ui.html`](decisions_ui.html) (self-contained, works
offline; regenerate with `make_decisions_ui.py`).

## How to read an entry

Each entry is `D-nnn — title`, then one metadata line, then **Decision**, **Why**,
**Status**, optional **Cross-theme**, and **Source** with verbatim evidence quotes.

- **Date** — when the position was *first* taken (a range when it was argued across
  days). **Status** is the state as of 2026-07-26: `adopted` (in force),
  `superseded` (replaced — the replacing entry is linked), `reversed` (undone, not
  replaced), `open` (live question, no ruling), `proposed` (recommended and still
  genuinely pending), `abandoned` (never enacted, no ruling anywhere). The 96
  entries that were `proposed` at consolidation were resolved against the repo
  on 2026-07-26 (PROTOCOL §8 Amendment 5, Ali's ruling); their status notes
  carry the code evidence, prefixed `S12 (2026-07-26):`. A code-confirmed
  `adopted` is a post-hoc verification against the repo, not a record-visible
  ratification — the prefix keeps that distinction.
- **Provenance** — `[chat]`: every source is a session transcript; the *Why* is
  what was argued at the time, not a later rationalisation. `[recon]`: rebuilt
  from commit messages and planning documents (2026-04-15 → 2026-05-16 has no
  transcripts); faithful to the record, but the deliberation is lost, and a plan
  proves intent, not survival. `[mixed]`: both.
- **Corroboration** — extraction ran twice, independently, over every file.
  `both`: every source decision was found by both passes. `single-pass`: none was
  (weakest evidence tier; the audit samples these preferentially). `mixed`: some
  of each.
- **Actors** — who made the call (`ali` / `claude` / `joint` / `unclear`), for the
  thesis contribution-delineation table. Ali ruled (2026-07-26, PROTOCOL §8
  Amendment 7) that the distribution stands as extracted, with this caveat
  attached wherever it is cited: extraction assigns actors from transcripts in
  which Claude does most of the *writing* even where Ali makes the *call*, and
  most `unclear` entries rest on commit messages, which rarely name a decider.
- **Source** — the union uids this entry consolidates (`a:`/`b:` = transcript
  extraction passes, `preA:`/`preB:` = reconstructed-period passes), then verbatim
  quotes with `file:line` into `docs/decision-record/distilled/`. Every quote is
  machine-verified to be an exact substring of that file starting at that line.

## Coverage — numbers, not adjectives

This rebuild exists because v1 claimed complete coverage on a measured **61.5%**
read. v1 is archived verbatim at
[`docs/historical/DECISIONS-v1.md`](historical/DECISIONS-v1.md) (Ali's ruling,
2026-07-26) — **v1 `D-nn` numbers do not map to v2 numbers.** The v2 chain is
checkable end to end; every figure below is re-derived by
`docs/decision-record/preflight.py`.

| | |
|---|---|
| Corpus | 69 distilled files: 32 session + 21 subagent transcripts (2026-05-18 → 2026-07-25), 15 plan documents + 1 commit log (pre-transcript period, 2026-04-15 → 2026-05-16) |
| Reading coverage | **69/69 files, 100.0%** of 23,934 distilled lines — structural, not asserted: each extraction request contains the whole file (PROTOCOL §8 Amendment 1), and `lines_read == lines_total` is machine-checked on every file |
| Extraction | two independent passes per file; transcript-era agreement **73.6%** of 881 distinct decisions (either pass alone captures only ~86–87% of their union); reconstructed-period agreement **80.7%** of 455 |
| Union | **1,336** source decisions, partitioned into 11 theme slices (167 dual-placed) |
| Consolidation | **{len(all_entries)} entries**; {primary_total - np_total} of {primary_total} primary decisions cited in entries, the other {np_total} individually listed with reasons in `not_promoted` (per-theme JSONs); mean {(primary_total - np_total) / len(all_entries):.1f} primary sources per entry |
| Evidence | **{quotes} quotes**, all machine-verified verbatim at their stated lines |
| Status | {st['adopted']} adopted · {st['proposed']} proposed · {st['superseded']} superseded · {st['open']} open · {st['reversed']} reversed · {st['abandoned']} abandoned |
| Provenance | {pv['chat']} `[chat]` · {pv['reconstructed']} `[recon]` · {pv['mixed']} `[mixed]` |
| Corroboration | {cb['both']} both · {cb['mixed']} mixed · **{cb['single-pass']} single-pass** (weakest tier, flagged for audit) |
| Confidence | {cf['high']} high · {cf['medium']} medium · {cf['low']} low (kept and flagged, not dropped) |
| Actors | {ac['claude']} claude · {ac['joint']} joint · {ac['ali']} ali · {ac['unclear']} unclear — accepted as extracted (Ali, 2026-07-26); cite only with the caveat above |
| Cross-theme reconciliation | 81 flags raised by the per-theme sessions; **{n_res} resolved** to located entries, **{n_noc} have no counterpart entry** (searched, recorded), 0 unaccounted — full rulings in `docs/decision-record/cross_theme_resolutions.json` |

**Known limits, stated rather than smoothed:**

- The consolidation-time `proposed` residue (96 entries) was **resolved against
  the repo on 2026-07-26** (Amendment 5): 53 confirmed adopted on artifact
  evidence, 11 superseded, 7 abandoned, and **{st['proposed']} remain genuinely
  pending** — almost all thesis-writing decisions awaiting a draft. Per-entry
  verdicts and evidence: `docs/decision-record/proposed_resolutions.json`.
- The pre-transcript period is reconstructed: what landed is reliable, *why* is
  thin, and plan-sourced statuses are status-as-of-the-plan unless confirmed by a
  later source (PROTOCOL §8 Amendment 4).
- Two independent extraction passes disagree on roughly a quarter of what counts
  as a decision in conversational text; the union is deliberately inclusive and
  consolidation carries the corroboration tier per entry.
- The residual risk no checker covers: a quote that is verbatim and correctly
  located but attached to the wrong decision. S11 samples for exactly this,
  preferentially in `single-pass` and low-confidence entries.
- {long_titles} titles exceed the 90-character style limit; they are rendered
  verbatim rather than rewritten, because rewriting risks semantic drift.
- Per `CLAUDE.md` and PROTOCOL §7: `ISSUES.md`, `STATUS.md`,
  `THREATS_TO_VALIDITY.md`, `docs/plans/` and the source code remain
  authoritative. This document is an index and a rationale archive — the value is
  the reasoning that exists only in chat.

---
"""


def main() -> int:
    themes, res = load()
    validate(themes, res)
    numbers = assign_numbers(themes)
    xrefs = build_xrefs(themes, res, numbers)

    doc = [front_matter(themes, res, numbers)]

    doc.append("## Index\n")
    for theme, title in READER_ORDER:
        d = themes[theme]
        ordered = sorted(d["entries"],
                         key=lambda e: (e["date_from"], d["entries"].index(e)))
        doc.append(f"### {title}\n")
        doc.append("| # | Decision | Date | Status | Tag |")
        doc.append("|---|---|---|---|---|")
        for e in ordered:
            n = numbers[e["slug"]]["n"]
            doc.append(f"| [{dn(n)}](#{dn(n).lower()}) | {e['title']} "
                       f"| {e['date_from']} | {e['status']} "
                       f"| {PROV_TAG[e['provenance']]} |")
        doc.append("")

    doc.append("---\n")

    for theme, title in READER_ORDER:
        d = themes[theme]
        ordered = sorted(d["entries"],
                         key=lambda e: (e["date_from"], d["entries"].index(e)))
        np_ = d["not_promoted"]
        doc.append(f"## {title}\n")
        doc.append(f"*{d['slice_primary_total']} primary source decisions → "
                   f"{len(d['entries'])} entries; {len(np_)} not promoted "
                   f"(reasons in `docs/decision-record/entries/{theme}.json`).*\n")
        for e in ordered:
            doc.append(render_entry(e, theme, numbers, xrefs))
        doc.append("")

    text = "\n".join(doc)
    OUT.write_text(text)
    NUMBERING.write_text(json.dumps(
        {"assigned": "2026-07-25",
         "rule": "sections in reader order; entries chronological "
                 "(date_from, stable) within a section; D-001.. sequential "
                 "in document order",
         "sections": [t for t, _ in READER_ORDER],
         "numbers": {s: v for s, v in
                     sorted(numbers.items(), key=lambda kv: kv[1]["n"])}},
        indent=1))
    n_ent = len(numbers)
    print(f"rendered {n_ent} entries -> {OUT} ({len(text):,} chars); "
          f"numbering -> {NUMBERING}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
