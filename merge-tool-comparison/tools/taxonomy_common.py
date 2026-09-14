"""Shared, stdlib-only helpers for the taxonomy-refresh harness (ISSUES #30, S1).

Authoritative protocol: ``outputs/taxonomy-protocol.md`` (frozen 2026-07-09,
commit 9209327). This module:

  * enumerates the frozen 308-merge census from the Schesch table and assigns
    the A/B strata by ``num_intersecting_files`` (protocol §2),
  * resolves every intersecting file's Mergiraf merge from the appropriate
    cache (stratum A: ``reports_detection/full/raw_results.json``; stratum B:
    ``reports_taxonomy/mergiraf_hi.json``),
  * applies the divergence rule (a CONFLICT/CRASH file is not *silent* — it is
    dropped from the unit and counted; a unit that loses every file leaves the
    scored population),
  * assembles the per-unit Phase-1 inputs (protocol §5, items 1-6) and the
    truncation ladder T0-T3, filling the FROZEN prompt template's USER section
    verbatim (``prompts_taxonomy/phase1_open_coding.md``).

No third-party dependencies -> importable under either project venv. Docker
work (Mergiraf, javac) and the API calls (count_tokens, Batches) live in the
sibling tools that import this one.
"""
from __future__ import annotations

import csv
import difflib
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # merge-tool-comparison/
CSV_PATH = ROOT / "data/schesch-dataset/results/reaper/result_adjusted.csv"
SCEN_DIR = {"A": ROOT / "data/scenarios_semantic",
            "B": ROOT / "data/scenarios_taxonomy_hi"}
RAW_A = ROOT / "reports_detection/full/raw_results.json"
MERGIRAF_B = ROOT / "reports_taxonomy/mergiraf_hi.json"
COMPILE_CHECKS = ROOT / "reports_taxonomy/compile_checks.json"
REPORTS = ROOT / "reports_taxonomy"
PROMPT_FILE = ROOT / "prompts_taxonomy/phase1_open_coding.md"
SCHEMA_FILE = ROOT / "prompts_taxonomy/phase1_output.schema.json"

MERGIRAF_TAG = "merge-tools/mergiraf:0.17.0"
MERGE_KEY_SUFFIX = f"::__merge__::{MERGIRAF_TAG}"

# Protocol §5 constants.
MERGED_FULL_MAX_LINES = 700          # full merged body allowed at/below this
WINDOW = 40                          # ±40 lines around regions differing from base
TOKEN_BUDGET = 30_000                # hard per-unit input cap
SEED = 20260709                      # split seed (protocol §4)
DERIVATION_FRACTION = 0.60

MODEL = "claude-opus-4-8"

# ---------------------------------------------------------------------------
# Census (Schesch table) — mirrors select_materialize's semantic predicate.
# ---------------------------------------------------------------------------

def _has_java(row: dict) -> bool:
    return str(row.get("diff contains java file", "")).strip().lower() in ("true", "1", "yes")


def _num_intersecting(row: dict) -> int | None:
    try:
        return int(float(row.get("num_intersecting_files", "")))
    except (TypeError, ValueError):
        return None


def _merge_id(row: dict) -> tuple[str, str, str]:
    """(merge_id, repo_name, merge_sha) matching select_materialize's scheme."""
    sha = row.get("merge_commit") or row.get("merge", "")
    repo = row["repository"].replace("/", "_")
    return f"{repo}__{sha[:10]}", repo, sha


def census() -> list[dict]:
    """The frozen population: has-Java rows with mergiraf == Tests_failed.

    Each entry: merge_id, repo, sha, stratum ('A' if <=3 parseable intersecting
    files else 'B'), num_intersecting_files (None if unparseable -> stratum B).
    """
    out = []
    with open(CSV_PATH) as fh:
        for row in csv.DictReader(fh):
            if not _has_java(row) or row.get("mergiraf", "") != "Tests_failed":
                continue
            mid, repo, sha = _merge_id(row)
            n = _num_intersecting(row)
            stratum = "A" if (n is not None and n <= 3) else "B"
            out.append({"merge_id": mid, "repo": repo, "sha": sha,
                        "stratum": stratum, "num_intersecting_files": n})
    return out


# ---------------------------------------------------------------------------
# Materialized scenarios + Mergiraf merges.
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def load_units() -> dict[str, dict]:
    """merge_id -> {merge_id, stratum, repo, sha, files:[scenario dicts]}.

    Only *materialized* merges (those with scenario JSONs on disk) appear here.
    Files are sorted by path for deterministic ordering.
    """
    units: dict[str, dict] = {}
    for stratum, d in SCEN_DIR.items():
        for f in sorted(Path(d).glob("*.json")):
            s = json.loads(f.read_text())
            mid = s.get("merge_id") or "__".join(s["scenario_id"].split("__")[:2])
            u = units.setdefault(mid, {"merge_id": mid, "stratum": stratum,
                                       "repo": s["repo_name"], "sha": s["merge_commit"],
                                       "files": []})
            u["files"].append(s)
    for u in units.values():
        u["files"].sort(key=lambda s: s["file_path"])
    return units


def mergiraf_index() -> dict[str, dict]:
    """scenario_id -> {outcome, merged} across both strata's Mergiraf caches."""
    idx: dict[str, dict] = {}
    for k, v in _read_json(RAW_A).items():
        if k.endswith(MERGE_KEY_SUFFIX):
            idx[k[: -len(MERGE_KEY_SUFFIX)]] = {"outcome": v.get("outcome"),
                                                "merged": v.get("merged")}
    for sid, v in _read_json(MERGIRAF_B).items():
        idx[sid] = {"outcome": v.get("outcome"), "merged": v.get("merged")}
    return idx


def scored_units(units: dict | None = None, mgi: dict | None = None) -> list[dict]:
    """Apply the divergence rule to every materialized unit.

    Returns unit dicts augmented with:
      scored : [{scenario, merged}]  files with a clean Mergiraf merge (shown)
      dropped: [{path, reason}]      CONFLICT/CRASH/absent files (excluded)
    A unit is *scored* iff its ``scored`` list is non-empty.
    """
    units = units if units is not None else load_units()
    mgi = mgi if mgi is not None else mergiraf_index()
    out = []
    for u in units.values():
        scored, dropped = [], []
        for s in u["files"]:
            m = mgi.get(s["scenario_id"])
            outcome = (m or {}).get("outcome")
            if m and outcome == "clean" and m.get("merged"):
                scored.append({"scenario": s, "merged": m["merged"]})
            else:
                dropped.append({"path": s["file_path"], "reason": outcome or "absent"})
        out.append({**u, "scored": scored, "dropped": dropped})
    return out


# ---------------------------------------------------------------------------
# Compile-delta (protocol §5 compile check) — reads compile_checks.json.
# ---------------------------------------------------------------------------

_LINE_NUM_RE = re.compile(r":\d+:")


def _norm_err(msg: str) -> str:
    """Normalize a javac diagnostic for matching ignoring line numbers/paths."""
    m = _LINE_NUM_RE.sub(":", msg)
    return re.sub(r"\s+", " ", m).strip()


def compile_delta(scenario_id: str, cc: dict) -> str:
    """Merged-only javac errors (present on merged, absent on dev), classified.

    ``(none)`` when the file was not compiled or the delta is empty. Matching
    ignores line numbers per protocol §5.
    """
    e = cc.get(scenario_id)
    if not e:
        return "(none)"
    merged = e.get("merged", {}).get("errors", [])
    dev = e.get("dev", {}).get("errors", [])
    dev_keys = {(x["class"], _norm_err(x["msg"])) for x in dev}
    delta = [x for x in merged if (x["class"], _norm_err(x["msg"])) not in dev_keys]
    if not delta:
        return "(none)"
    return "\n".join(f"[{x['class']}] {x['msg']}" for x in delta)


# ---------------------------------------------------------------------------
# Merged-file windowing (protocol §5 item 3).
# ---------------------------------------------------------------------------

_HEADER_RE = re.compile(r"^\s*(package|import)\b")
_DECL_RE = re.compile(
    r"^\s*(?:@[\w.]+\s*)*"
    r"(?:(?:public|private|protected|static|final|abstract|sealed|non-sealed|"
    r"synchronized|native|strictfp|default|transient|volatile)\s+)*"
    r"(?:class|interface|enum|record|@interface)\b"
)
_METHOD_RE = re.compile(
    r"^\s*(?:@[\w.]+\s*)*"
    r"(?:(?:public|private|protected|static|final|abstract|synchronized|native|"
    r"strictfp|default)\s+)+"
    r"[\w<>\[\],.?\s]+\s+\w+\s*\([^;{]*"
)


def window_merged(base: str, merged: str) -> str:
    """±WINDOW lines around every region differing from base, plus
    package/imports and enclosing type/method signatures; gaps elided."""
    blines = base.splitlines()
    mlines = merged.splitlines()
    keep: set[int] = set()
    for i, line in enumerate(mlines):
        if _HEADER_RE.match(line) or _DECL_RE.match(line) or _METHOD_RE.match(line):
            keep.add(i)
    sm = difflib.SequenceMatcher(a=blines, b=mlines, autojunk=False)
    for tag, _i1, _i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            for j in range(max(0, j1 - WINDOW), min(len(mlines), j2 + WINDOW)):
                keep.add(j)
    if not keep:
        return "(no lines differ from base; body omitted)"
    out, prev = [], -1
    for i in sorted(keep):
        if prev >= 0 and i > prev + 1:
            out.append(f"        // ... {i - prev - 1} lines elided ...")
        out.append(mlines[i])
        prev = i
    if prev < len(mlines) - 1:
        out.append(f"        // ... {len(mlines) - 1 - prev} lines elided ...")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Unified diffs.
# ---------------------------------------------------------------------------

def _udiff(a: str, b: str, fa: str, fb: str, n: int) -> str:
    diff = difflib.unified_diff(a.splitlines(keepends=True), b.splitlines(keepends=True),
                                fromfile=fa, tofile=fb, n=n)
    text = "".join(diff)
    if text and not text.endswith("\n"):
        text += "\n"
    return text or "(no differences)\n"


def _truncate_diff(text: str, line_cap: int | None) -> str:
    """Keep the head and tail of an oversized diff, eliding the middle.

    Used only by the T3 hard-fit path for pathological single-file diffs that
    exceed the 30k budget on their own; the elision is explicit and the
    aggressiveness is recorded as a covariate.
    """
    if line_cap is None:
        return text
    lines = text.splitlines()
    if len(lines) <= line_cap:
        return text
    head = line_cap * 2 // 3
    tail = line_cap - head
    elided = len(lines) - head - tail
    return "\n".join(lines[:head] + [f"        // ... {elided} diff lines elided ..."]
                     + lines[-tail:])


def _diffstat(a: str, b: str) -> str:
    added = removed = 0
    for line in difflib.unified_diff(a.splitlines(), b.splitlines(), n=0):
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return f"+{added} -{removed}"


# ---------------------------------------------------------------------------
# Per-unit input assembly (truncation ladder).
# ---------------------------------------------------------------------------

# Each level: (diff_context_n, merged_mode, file_cap)
#   merged_mode: "full" (full if <=700 lines else windowed), "window", "omit"
LEVELS = {
    "T0": (8, "full", None),
    "T1": (8, "window", None),
    "T2": (8, "omit", None),
    "T3": (3, "omit", 12),
}
TRUNC_NOTE = {
    "T0": "(full inputs)",
    "T1": "(merged files windowed ±40 around base-differing regions)",
    "T2": "(merged bodies omitted; diffs + dev-diff + compile delta only)",
    "T3": "(diffs at -U3; merged bodies omitted; files capped at 12 largest merged-vs-dev diffs)",
}


def _file_block(idx: int, n: int, entry: dict, cc: dict, ctx_n: int, merged_mode: str,
                diff_line_cap: int | None = None) -> str:
    s = entry["scenario"]
    merged = entry["merged"]
    path = s["file_path"]

    def d(a, b, fa, fb):
        return _truncate_diff(_udiff(a, b, fa, fb, ctx_n).rstrip("\n"), diff_line_cap)

    parts = [f"=== FILE {idx}/{n}: {path} ==="]
    parts.append("--- OURS vs BASE (unified diff, -U%d) ---" % ctx_n)
    parts.append(d(s["base_content"], s["ours_content"], "base", "ours"))
    parts.append("--- THEIRS vs BASE (unified diff, -U%d) ---" % ctx_n)
    parts.append(d(s["base_content"], s["theirs_content"], "base", "theirs"))
    if merged_mode != "omit":
        n_lines = merged.count("\n") + 1
        if merged_mode == "full" and n_lines <= MERGED_FULL_MAX_LINES:
            body = merged.rstrip("\n")
            hdr = "--- MERGED RESULT (mergiraf; full) ---"
        else:
            body = window_merged(s["base_content"], merged)
            hdr = "--- MERGED RESULT (mergiraf; windowed ±40 around base-differing regions + package/imports/signatures) ---"
        parts.append(hdr)
        parts.append(body)
    parts.append("--- MERGED vs DEVELOPER RESOLUTION (unified diff, -U%d) ---" % ctx_n)
    parts.append(d(merged, s["developer_resolution"], "merged", "developer"))
    parts.append("--- COMPILE DELTA (javac, single-file, eclipse-temurin:17-jdk; PARSE/RESOLVE/OTHER) ---")
    parts.append(compile_delta(s["scenario_id"], cc))
    return "\n".join(parts)


def build_unit_inputs(unit: dict, cc: dict, level: str,
                      file_cap: int | None = None, diff_line_cap: int | None = None) -> str:
    """The {UNIT_INPUTS} body for a scored unit at a given truncation level.

    ``file_cap`` overrides the level's default cap (the T3 hard-fit path lowers
    it below 12 when 12 files still exceed budget). ``diff_line_cap`` caps each
    diff section's line count (T3 hard-fit for single huge diffs).
    """
    ctx_n, merged_mode, level_cap = LEVELS[level]
    cap = file_cap if file_cap is not None else level_cap
    scored = unit["scored"]
    shown = scored
    tail = ""
    if cap is not None and len(scored) > cap:
        ranked = sorted(scored, key=lambda e: len(_udiff(
            e["merged"], e["scenario"]["developer_resolution"], "m", "d", 0)), reverse=True)
        shown = ranked[:cap]
        rest = ranked[cap:]
        lines = [f"  {e['scenario']['file_path']}  (merged-vs-dev {_diffstat(e['merged'], e['scenario']['developer_resolution'])})"
                 for e in rest]
        tail = ("\n\n=== REMAINING %d FILES (elided at truncation %s; listed by path + merged-vs-dev diffstat) ===\n"
                % (len(rest), level)) + "\n".join(lines)
    blocks = [_file_block(i + 1, len(scored), e, cc, ctx_n, merged_mode, diff_line_cap)
              for i, e in enumerate(shown)]
    return "\n\n".join(blocks) + tail


# ---------------------------------------------------------------------------
# Frozen prompt template (SYSTEM / USER split).
# ---------------------------------------------------------------------------

def load_prompt() -> tuple[str, str]:
    """(system_text, user_template) extracted verbatim from the frozen file."""
    txt = PROMPT_FILE.read_text()
    sys_marker = "## SYSTEM (static, cacheable)\n"
    usr_marker = "## USER (per unit)\n"
    si = txt.index(sys_marker) + len(sys_marker)
    ui = txt.index(usr_marker)
    system = txt[si:ui].strip("\n")
    user = txt[ui + len(usr_marker):].strip("\n")
    return system, user


def _level_label(level: str, file_cap: int | None, diff_line_cap: int | None) -> tuple[str, str]:
    """(display label, note) reflecting the T3 hard-fit aggressiveness."""
    if file_cap is None and diff_line_cap is None:
        return level, TRUNC_NOTE[level]
    bits = []
    if file_cap is not None:
        bits.append(f"cap{file_cap}")
    if diff_line_cap is not None:
        bits.append(f"trunc{diff_line_cap}")
    label = f"{level}/" + "/".join(bits)
    note = ("(diffs at -U3; merged bodies omitted; hard-fit to the 30k budget: "
            + ", ".join(
                ([f"files capped at {file_cap} largest merged-vs-dev diffs"] if file_cap is not None else [])
                + ([f"each diff section truncated to {diff_line_cap} lines"] if diff_line_cap is not None else []))
            + ")")
    return label, note


def render_user(unit: dict, cc: dict, level: str,
                file_cap: int | None = None, diff_line_cap: int | None = None) -> str:
    """Fill the frozen USER template's slots for one scored unit."""
    _system, template = load_prompt()
    dropped = ", ".join(d["path"] for d in unit["dropped"]) or "(none)"
    body = build_unit_inputs(unit, cc, level, file_cap=file_cap, diff_line_cap=diff_line_cap)
    label, note = _level_label(level, file_cap, diff_line_cap)
    filled = (template
              .replace("{MERGE_ID}", unit["merge_id"])
              .replace("{REPO}", unit["repo"])
              .replace("{MERGE_SHA}", unit["sha"])
              .replace("{STRATUM}", unit["stratum"])
              .replace("{N_FILES_SHOWN}", str(len(unit["scored"])))
              .replace("{N_FILES_TOTAL}", str(len(unit["files"])))
              .replace("{DROPPED_FILE_PATHS}", dropped)
              .replace("{TRUNCATION_LEVEL}", label)
              .replace("{TRUNCATION_NOTE}", note)
              # The {UNIT_INPUTS} token occurs twice — the real slot (first) and
              # inside the trailing legend comment. Fill only the slot; the
              # comment keeps its literal token as documentation for the model.
              .replace("{UNIT_INPUTS}", body, 1))
    return filled


def load_schema() -> dict:
    return json.loads(SCHEMA_FILE.read_text())


# T3 hard-fit search: progressively smaller file caps, then per-diff line caps.
# Guarantees the 30k hard cap for pathological units (many files, or a single
# huge diff) that the fixed T3 (12 files, -U3) cannot. Sanctioned pre-G0
# assembly revisit (protocol §5); aggressiveness is recorded as a covariate.
_T3_FILE_CAPS = (12, 10, 8, 6, 5, 4, 3, 2, 1)
_T3_DIFF_LINE_CAPS = (400, 250, 150, 80, 40)


def assemble_best(unit: dict, cc: dict, count_fn) -> tuple[str, str, int, bool]:
    """Walk the ladder T0->T3, stopping at the first level within TOKEN_BUDGET.

    T3 is a floor with a hard-fit search: reduce the file cap, then truncate
    per-diff line counts, until the unit is under budget. ``count_fn(text) ->
    int`` is injected so this module stays stdlib-only. Returns
    (level_label, user_text, token_count, over_budget).
    """
    for level in ("T0", "T1", "T2"):
        text = render_user(unit, cc, level)
        tokens = count_fn(text)
        if tokens <= TOKEN_BUDGET:
            return level, text, tokens, False

    # T3 with decreasing file cap.
    text = tokens = label = None
    for cap in _T3_FILE_CAPS:
        text = render_user(unit, cc, "T3", file_cap=cap)
        tokens = count_fn(text)
        label = _level_label("T3", cap if cap != 12 else None, None)[0]
        if tokens <= TOKEN_BUDGET:
            return label, text, tokens, False

    # Single kept file still over budget -> truncate its diff sections.
    for lc in _T3_DIFF_LINE_CAPS:
        text = render_user(unit, cc, "T3", file_cap=1, diff_line_cap=lc)
        tokens = count_fn(text)
        if tokens <= TOKEN_BUDGET:
            return _level_label("T3", 1, lc)[0], text, tokens, False
    return _level_label("T3", 1, _T3_DIFF_LINE_CAPS[-1])[0], text, tokens, tokens > TOKEN_BUDGET


# ---------------------------------------------------------------------------
# Hashing (manifest §9).
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# custom_id wire-encoding (protocol §9 + §12 Amendment 1).
# ---------------------------------------------------------------------------
# The §9 notation p1::<merge_id> uses ':' which the Message Batches API
# custom_id pattern ^[a-zA-Z0-9_-]{1,64}$ forbids; the longest merge_id (61
# chars) plus a p3a-/p3b- prefix also exceeds 64, and one merge_id contains a
# '.'. The LOGICAL per-phase per-merge key is unchanged; on the wire it is
# encoded API-safe and recovered to merge_id by inverting the deterministic
# submit-time map (never by string-splitting the id).
CUSTOM_ID_SCHEME = ("logical p1::/p3a::/p3b::<merge_id> (§9); wire-encoded as "
                    "<phase>-<sanitized merge_id>, out-of-charset chars -> '-', "
                    "truncated + <sha1[:8]>-suffixed to <=64 chars when needed. "
                    "Recovered via the submit-time {custom_id: merge_id} map.")


def custom_id(phase: str, merge_id: str) -> str:
    """API-safe, deterministic custom_id for a (phase, merge_id) pair."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "-", merge_id)
    cid = f"{phase}-{safe}"
    if len(cid) <= 64 and re.fullmatch(r"[A-Za-z0-9_-]+", merge_id):
        return cid
    h = hashlib.sha1(merge_id.encode()).hexdigest()[:8]
    keep = 64 - len(phase) - 1 - 1 - 8            # phase + '-' + safe + '-' + hash
    return f"{phase}-{safe[:keep]}-{h}"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    """git hash-object equivalent (blob SHA-1) without shelling out."""
    data = Path(path).read_bytes()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()
