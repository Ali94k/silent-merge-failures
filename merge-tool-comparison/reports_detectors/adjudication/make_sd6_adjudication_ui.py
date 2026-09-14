"""Generate adjudication_ui.html — standalone browser UI for S-D6 held-out
flag adjudication (detector cycle, ISSUES #31, plan §5 GD4).

One card per HELD-OUT unit the machine flagged (either arm). Ali rules each
flagging LANE CAUSAL / REAL-BUT-INCIDENTAL / DETECTOR-FP with a written
rationale per unit (GD4: per-lane precision; citable unit recall counts a
unit whose ≥1 lane is CAUSAL). Adapted from the Stage-C
reports_detection/full/make_adjudication_ui.py pattern Ali used for §4.6
(localStorage persistence, CSV/clipboard export, no server).

Inputs (all produced by tools/detector_eval_run.py --score):
  ../eval/flags.json                       every unit-level flag, all pops
  ../eval/eval_cache_heldout*.json         merged texts + lane rows
  data/scenarios_semantic + data/scenarios_taxonomy_hi   unit inputs
  reports_taxonomy/labels_final.csv        final taxonomy labels + passes

Line-numbering note (inherited from the Stage-C UI): lane-reported lines are
shown verbatim for provenance, but context windows are RECOMPUTED by
locating the flagged identifier in the actual merged file — RM2 var-lane
lines are stripped-text coordinates and can drift.

Regenerate after any eval re-score:
    ../../.venv/bin/python make_sd6_adjudication_ui.py
"""
from __future__ import annotations

import csv
import glob
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent            # reports_detectors/adjudication
ROOT = HERE.parent.parent                          # merge-tool-comparison
EVAL = HERE.parent / "eval"

MERGE_TOOL = "merge-tools/mergiraf:0.17.0"
CTX = 4
NAME_BINDING_FAMILY = {
    "stale-usage-of-pruned-import",
    "stale-reference-to-removed-declaration",
    "stale-reference-to-renamed-or-relocated-declaration",
    "stale-caller-of-changed-signature",
}

# Draft rulings + rationales (Claude, 2026-07-20) — NOT the answer: the
# starting point Ali accepts ('a' key) or overrides, per the Stage-C §4.6
# DRAFTS pattern. Every draft was probe-verified against the actual unit
# sources (presence tables, JLS import rules, real-repo history where noted).
# CONVENTION (set in the commons-collections card, applied throughout):
# rulings judge the flag's claim about the MERGED ARTIFACT (real,
# merge-induced, compile-breaking); a byte-identical developer resolution is
# noted, never a downgrade — the construct is artifact breakage, not the
# mergiraf-vs-developer delta.
DRAFTS = {
    "ahome-it_lienzo-core__bf4b253816": dict(label="CAUSAL", verify=False,
        why="Field rename innerLayoutContainer→m_innerLayoutContainer (theirs) half-applied: ours-added onShapeResizeEnd keeps 1 bare old-name read; merged declares only m_-name → unresolved = compile error. Consistent with the Stage-C §4.6 CAUSAL ruling on this same merge. Dev-identical; CAUSAL per convention."),
    "apache_commons-collections__15b62fb08d": dict(label="CAUSAL", verify=False,
        why="theirs pruned the iterators.* wildcard; ours concurrently added testPairedIterator using bare PairedIterator; merged keeps the use with no covering import (surviving PairedIterator.PairedItem nested import does not import the enclosing name, JLS 7.5.1) → compile error, the labeled mechanism. CONVENTION: dev file is byte-identical (same human mistake; feature later backed out of mainline) — ruling judges the merged artifact, so dev-identical does not downgrade."),
    "dabsquared_gitlab-plugin__d555b8773d": dict(label="DETECTOR-FP", verify=True,
        why="ours EXTRACTED the nested class GitLabCredentialMatcher to its own same-package file (verified present at the merge commit: connection/GitLabCredentialMatcher.java), keeping the new-site; merged resolves it by same-package lookup. The file-local differential cannot see the extracted file — the lane's documented same-package residual (Amendment-2 ceiling). Merged text compiles; label indeterminate is consistent."),
    "erudika_para__a9e67cc8b3": dict(label="CAUSAL", verify=False,
        why="Variable rename m→method half-applied by interleaved edits; merged keeps 1 bare 'm' read at L109 with no declaration → compile error. Unit label frames the damage as overlapping-edit-interleaving; the flag identifies the concrete break it produced. Consistent with the Stage-C §4.6 CAUSAL ruling on this merge (pilot + full)."),
    "feroult_yawp__1723236a65": dict(label="CAUSAL", verify=False,
        why="theirs removed import endpoint.HttpException with its uses; ours kept 3 uses; merged retains 1 use at L86 with no covering import → compile error, the labeled mechanism. Dev-identical; CAUSAL per convention."),
    "google_truth__2e4a23bebb": dict(label="CAUSAL", verify=False,
        why="ours' side dropped the static org.junit.Assert.fail import path; theirs kept it with 14 uses; merged has 15 bare fail(...) calls and no covering static import → compile errors. Dev-identical; CAUSAL per convention."),
    "javamoney_jsr354-api__6d2356a153": dict(label="CAUSAL", verify=False,
        why="Cleanest shape: ours removed @Ignore usage+import entirely; theirs kept 3 uses; merged keeps 1 use with no import → compile error. Developer resolved by DROPPING the usage (dev=0 uses) — mergiraf-only breakage, no dev-identical caveat needed."),
    "jcabi_jcabi-github__27cc460e3c": dict(label="CAUSAL", verify=False,
        why="theirs renamed static helper gist()→github(); ours added test methods still calling gist(); merged keeps callers (L82 RtGistITCase.gist()) with NO gist() declared (verified: only github() present) → compile error. Dev-identical; CAUSAL per convention."),
    "jenkinsci_credentials-plugin__b9cb5f9d1b": dict(label="CAUSAL", verify=False,
        why="Double prune: ours dropped java.io.ByteArrayOutputStream + io.jenkins...ConfigurationAsCode imports; theirs kept both with uses; merged keeps 4+2 uses uncovered → compile errors. Dev kept the imports (dev≠merged) — mergiraf-only breakage."),
    "jenkinsci_email-ext-plugin__bbf162f5d5": dict(label="CAUSAL", verify=False,
        why="Merge spliced ours' instance-field block (mailAccount writes + getAdminAddress() call) INTO theirs' new static autoConfigure() — instance access in static context = compile errors (Joern: implicit 'this' unresolvable; theirs' own body was descriptor-qualified and clean; verified by body diff). Exactly the labeled insertion-anchored-to-relocated-code damage. Dev-identical; CAUSAL per convention."),
    "jenkinsci_ui-samples-plugin__81bf937a3d": dict(label="CAUSAL", verify=False,
        why="theirs pruned org.kohsuke.stapler.StaplerRequest import+uses; ours kept 3 uses; merged retains 1 use uncovered → compile error. Dev kept the import (dev≠merged) — mergiraf-only breakage."),
    "jnr_jnr-unixsocket__f8f34e5634": dict(label="CAUSAL", verify=False,
        why="theirs' new LibraryLoader uses rode in while the jnr.ffi.* wildcard that covered them was pruned; merged has 2 uses, no cover → compile error. Dev-identical; CAUSAL per convention."),
    "mbosecke_pebble__bb807558a3": dict(label="CAUSAL", verify=False,
        why="ours pruned com...template.EvaluationContext import; theirs kept 3 uses; merged retains 1 use uncovered → compile error. Dev-identical; CAUSAL per convention."),
    "progether_jadventure__e28401af85": dict(label="CAUSAL", verify=False,
        why="ours pruned com.jadventure.game.QueueProvider import+uses; theirs kept 4 uses; merged retains 3 uncovered → compile errors. Dev kept the import (dev≠merged) — mergiraf-only breakage."),
    "sander2798_enderstone__b515bac1b0": dict(label="CAUSAL", verify=False,
        why="theirs pruned org.enderstone.server.EnderLogger import; ours kept 2 uses; merged retains 1 uncovered → compile error. Dev kept the import (dev≠merged) — mergiraf-only. Fork-twin of sandergielisse__b515bac1b0 (same merge SHA, distinct census unit)."),
    "sandergielisse_enderstone__9d0d7b7ba8": dict(label="CAUSAL", verify=False,
        why="Symmetric double prune: RegionSet (ours' import, theirs pruned) + PacketOutPlayerAbilities (theirs' import, ours pruned); merged keeps 3+1 uses with both imports gone → compile errors. Dev kept both (dev≠merged) — mergiraf-only breakage."),
    "sandergielisse_enderstone__b515bac1b0": dict(label="CAUSAL", verify=False,
        why="Same facts as sander2798_enderstone__b515bac1b0 (fork twin): EnderLogger import pruned by theirs, ours' use survives uncovered. Dev≠merged — mergiraf-only. CAUSAL per convention."),
    "scribble_scribble-java__e72f7c9c06": dict(label="DETECTOR-FP", verify=True,
        why="RM2 read theirs' PARTIAL split as a rename, but checkAndAddNoArgUniqueFlag is STILL DECLARED in merged (verified: private void checkAndAddNoArgUniqueFlag(String) present); both names coexist with 4 callers each — code compiles. RM2Rename call-lane misread (name-level granularity limit). Label indeterminate is consistent."),
    "steveice10_mcprotocollib__8a7d7b196b": dict(label="CAUSAL", verify=False,
        why="Unit-level CAUSAL, developer-confirmed: codec file's IntFunction use at L784 is uncovered in merged (no java.util.function.IntFunction import; no project class of that name at the merge commit) and the developer's own NEXT commit touching the file — 'Fix missing imports??' (d5ccf0d2) — adds exactly that import. LongEntityMetadata (test file) likewise cross-package uncovered → real. SUB-FLAG CORRECTION: the MetadataType.java flag is a same-package FP — at the merge commit LongMetadataType.java sits in entity/metadata/, the SAME package as its referencing file, so the bare name resolves import-free and the pruned type.* wildcard never provided it (file-local blind spot, dabsquared-class; feeds the same-package-residual line in FINDINGS). IntFunction message's palette.* provenance clause also imprecise; operative uncovered-name claims verified."),
    "vojtechhabarta_typescript-generator__51835d3c16": dict(label="CAUSAL", verify=False,
        why="theirs migrated JUnit Assert away (relocation — matches the renamed-or-relocated label), pruning org.junit.Assert; ours' kept usage survives at L177 uncovered → compile error. D1 catches the relocation through its import-prune lens — cross-category but the same breakage. Dev-identical; CAUSAL per convention."),
}

# message → (old_identifier, new_identifier|None, is_call) extraction per stem
_PATTERNS = (
    (re.compile(r"^Unresolved identifier '([^']+)'"), None, False),
    (re.compile(r"^Stale reference to a removed/renamed declaration: \S+ '([^']+)'"), None, False),
    (re.compile(r"^Stale usage of pruned import: merged file uses '([^']+)'"), None, False),
    (re.compile(r"^Stale call to '([^']+)'"), None, True),
    (re.compile(r"^Stale caller of renamed identifier: '([^']+)' \(renamed to '([^']+)'\)"), 2, True),
    (re.compile(r"^Stale reference to renamed variable/field: '([^']+)' \(renamed to '([^']+)'\)"), 2, False),
    (re.compile(r"^Potential stale read: collection '([^']+)'"), None, False),
    (re.compile(r"^Potential infinite loop in method '([^']+)'"), None, True),
)


def parse_ident(msg: str):
    for rx, new_grp, is_call in _PATTERNS:
        m = rx.match(msg)
        if m:
            return m.group(1), (m.group(2) if new_grp else None), is_call
    return None, None, False


def count_tok(tok: str, text: str) -> int:
    if not tok:
        return 0
    return len(re.findall(rf"(?<![\w$]){re.escape(tok)}(?![\w$])", text))


def merged_sites(tok: str, lines: list[str]) -> list[int]:
    rx = re.compile(rf"(?<![\w$]){re.escape(tok)}(?![\w$])")
    return [i + 1 for i, l in enumerate(lines) if rx.search(l)]


def windows(sites: list[int], lines: list[str]) -> list[list]:
    """Merge overlapping ±CTX windows; each: [start, [(ln, text, flagged)...]]"""
    if not sites:
        return []
    spans = []
    for s in sites:
        lo, hi = max(1, s - CTX), min(len(lines), s + CTX)
        if spans and lo <= spans[-1][1] + 1:
            spans[-1][1] = hi
        else:
            spans.append([lo, hi])
    out = []
    sset = set(sites)
    for lo, hi in spans[:8]:
        out.append([lo, [(ln, lines[ln - 1], ln in sset)
                         for ln in range(lo, hi + 1)]])
    return out


def load():
    flags = json.loads((EVAL / "flags.json").read_text())
    cache: dict = {}
    for f in sorted(EVAL.glob("eval_cache_heldout*.json")):
        cache.update(json.loads(f.read_text()))
    scns = {}
    for d in ("data/scenarios_semantic", "data/scenarios_taxonomy_hi"):
        for f in glob.glob(str(ROOT / d / "*.json")):
            s = json.loads(Path(f).read_text())
            scns[s["scenario_id"]] = s
    labels = {}
    with open(ROOT / "reports_taxonomy/labels_final.csv") as fh:
        for r in csv.DictReader(fh):
            labels[r["merge_id"]] = r
    return flags, cache, scns, labels


def build():
    flags, cache, scns, labels = load()
    heldout = [f for f in flags if f["population"] == "heldout"]
    by_unit: dict[str, dict] = {}
    for f in heldout:
        u = by_unit.setdefault(f["merge_id"], {"merge_id": f["merge_id"],
                                               "category": f["category"],
                                               "arms": [], "files": f["files"]})
        u["arms"].append(f["arm"])

    cards = []
    for mid, u in sorted(by_unit.items()):
        lab = labels.get(mid, {})
        file_cards = []
        lanes_all = set()
        for sid, frow in u["files"].items():
            if frow.get("merge_outcome") != "clean" or not frow.get("lanes"):
                continue
            flag_lanes = {lk: lr for lk, lr in frow["lanes"].items()
                          if lr["verdict"] == "FLAG"}
            if not flag_lanes:
                continue
            scn = scns.get(sid)
            mrec = cache.get(f"{sid}::__merge__::{MERGE_TOOL}")
            merged = mrec["merged"] if mrec else ""
            mlines = merged.split("\n")
            base = scn["base_content"] if scn else ""
            ours = scn["ours_content"] if scn else ""
            theirs = scn["theirs_content"] if scn else ""
            dev = scn.get("developer_resolution", "") if scn else ""

            idents = []
            raw = []
            for lkey, lrec in sorted(flag_lanes.items()):
                lane = lkey.split("::")[0]
                lanes_all.add(lane)
                for iss in lrec["issues"]:
                    raw.append({"lane": lane, "flagseg": lkey.split("::")[1],
                                "line": iss["line"], "msg": iss["message"]})
                    old, new, is_call = parse_ident(iss["message"])
                    if not old:
                        continue
                    if any(i["old"] == old for i in idents):
                        for i in idents:
                            if i["old"] == old:
                                i["lanes"].add(lane)
                        continue
                    sites = merged_sites(old, mlines)
                    idents.append({
                        "old": old, "new": new, "lanes": {lane}, "is_call": is_call,
                        "presence": {
                            "old": {k: count_tok(old, v) for k, v in
                                    (("base", base), ("ours", ours),
                                     ("theirs", theirs), ("merged", merged),
                                     ("dev", dev))},
                            "new": (None if not new else
                                    {k: count_tok(new, v) for k, v in
                                     (("base", base), ("ours", ours),
                                      ("theirs", theirs), ("merged", merged),
                                      ("dev", dev))}),
                        },
                        "wins": windows(sites, mlines),
                        "n_sites": len(sites),
                    })
            for i in idents:
                i["lanes"] = sorted(i["lanes"])
            file_cards.append({
                "sid": sid,
                "file": scn["file_path"] if scn else sid,
                "idents": idents,
                "raw": sorted(raw, key=lambda r: (r["lane"], r["line"])),
                "src": {"base": base, "ours": ours, "theirs": theirs,
                        "merged": merged, "dev": dev},
            })
        arms = sorted(set(u["arms"]))
        draft = DRAFTS.get(mid, {})
        cards.append({
            "id": mid,
            "category": u["category"],
            "family": u["category"] in NAME_BINDING_FAMILY,
            "stratum": lab.get("stratum", "?"),
            "passes": f"A:{lab.get('pass_a','?')} / B:{lab.get('pass_b','?')} ({lab.get('source','?')})",
            "arms": arms,
            "delta": arms == ["experimental"],
            "lanes": sorted(lanes_all),
            "files": file_cards,
            "draft": draft.get("label", ""),
            "draft_why": draft.get("why", "(no draft)"),
            "draft_verify": draft.get("verify", False),
        })
    # experimental-only (delta) catches first — the cycle's new evidence
    cards.sort(key=lambda c: (not c["delta"], c["id"]))
    return cards


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>S-D6 held-out flag adjudication — ISSUES #31 GD4</title>
<style>
  :root { --red-bg:#fdecec; --red-hl:#f6b4b4; --red-tx:#8f1d1d;
          --grn-bg:#e9f6ec; --grn-hl:#a9dfb4; --grn-tx:#1d5c2e;
          --amb-bg:#fdf3df; --amb-tx:#7a5410;
          --mut:#6b7280; --bd:#d6d3cd; --info-bg:#e8f0fb; --info-tx:#1d4f8f;
          --flag:#fff3cd; --flagbar:#e0a800; }
  * { box-sizing: border-box; }
  body { font-family:-apple-system,"Segoe UI",Roboto,sans-serif; margin:0;
         color:#1f2937; background:#faf9f5; }
  #app { display:flex; height:100vh; }
  #side { width:330px; min-width:330px; border-right:1px solid var(--bd);
          overflow-y:auto; background:#fff; }
  #main { flex:1; overflow-y:auto; padding:16px 22px 80px; }
  .sideItem { padding:8px 12px; border-bottom:1px solid #eee; cursor:pointer; font-size:12.5px; }
  .sideItem:hover { background:#f5f4f0; }
  .sideItem.cur { background:var(--info-bg); }
  .sideItem .mid { font-family:ui-monospace,Menlo,monospace; word-break:break-all; }
  .sideItem .meta { color:var(--mut); font-size:11.5px; margin-top:3px; display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
  .dot { width:9px; height:9px; border-radius:50%; background:#d1d5db; display:inline-block; flex:none; }
  .dot.done { background:#34a35b; }
  .chip { font-size:11px; padding:2px 8px; border-radius:10px; white-space:nowrap; display:inline-block; }
  .c-red { background:var(--red-bg); color:var(--red-tx); }
  .c-grn { background:var(--grn-bg); color:var(--grn-tx); }
  .c-amb { background:var(--amb-bg); color:var(--amb-tx); }
  .c-inf { background:var(--info-bg); color:var(--info-tx); }
  .c-dlt { background:#efe3fb; color:#5b2a86; }
  #head { position:sticky; top:0; background:#fff; border-bottom:1px solid var(--bd);
          padding:10px 12px; z-index:5; font-size:13px; }
  #bar { height:5px; background:#eee; border-radius:3px; margin-top:6px; }
  #barFill { height:5px; background:#2f6fce; border-radius:3px; width:0; }
  button { font:inherit; font-size:12.5px; padding:5px 11px; border:1px solid var(--bd);
           border-radius:7px; background:#fff; cursor:pointer; }
  button:hover { background:#f3f2ee; }
  button.sel-causal { border:1.5px solid var(--grn-tx); background:var(--grn-bg); color:var(--grn-tx); font-weight:600; }
  button.sel-inc { border:1.5px solid var(--amb-tx); background:var(--amb-bg); color:var(--amb-tx); font-weight:600; }
  button.sel-fp { border:1.5px solid var(--red-tx); background:var(--red-bg); color:var(--red-tx); font-weight:600; }
  h2.id { font-family:ui-monospace,Menlo,monospace; font-size:15px; margin:2px 0 2px; word-break:break-all; }
  .sub { color:var(--mut); font-size:12px; margin-bottom:8px; }
  .laneRow { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin:6px 0;
             padding:8px 10px; border:1px solid var(--bd); border-radius:8px; background:#fff; }
  .laneRow .nm { font-family:ui-monospace,Menlo,monospace; font-weight:600; font-size:13px; }
  input[type=text] { width:100%; font:inherit; font-size:13px; padding:7px 10px;
                     border:1px solid var(--bd); border-radius:7px; }
  .sec { margin:18px 0 6px; font-weight:600; font-size:13px; color:#374151;
         border-bottom:1px solid var(--bd); padding-bottom:4px; }
  details { margin:8px 0; }
  details > summary { cursor:pointer; font-size:12.5px; color:var(--info-tx); padding:4px 0; }
  .identCard { border:1px solid var(--bd); border-radius:9px; padding:10px 12px; margin:10px 0; background:#fff; }
  .identHd { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:8px; }
  .nm { font-family:ui-monospace,Menlo,monospace; font-weight:600; font-size:13.5px; }
  table.pres { border-collapse:collapse; font-size:12px; margin:4px 0 8px; }
  table.pres td, table.pres th { border:1px solid var(--bd); padding:3px 9px; text-align:center; font-family:ui-monospace,Menlo,monospace; }
  table.pres th { background:#fafafa; color:var(--mut); font-weight:600; }
  table.pres td.lbl { text-align:left; font-weight:600; background:#fafafa; }
  td.z { color:#bbb; } td.nz { background:#fef6e7; color:#7a5410; font-weight:600; }
  pre.code { margin:6px 0; border:1px solid var(--bd); border-radius:8px; overflow-x:auto;
             font-family:ui-monospace,Menlo,monospace; font-size:11.8px; line-height:1.5; background:#fff; }
  .cl { display:flex; }
  .cl .ln { width:54px; min-width:54px; text-align:right; padding:0 8px; color:#9ca3af;
            user-select:none; border-right:1px solid #eee; background:#fafafa; }
  .cl .tx { padding:0 10px; white-space:pre-wrap; word-break:break-word; flex:1; }
  .cl.flag .tx { background:var(--flag); }
  .cl.flag .ln { background:#fbeec0; border-left:3px solid var(--flagbar); }
  mark.tk-old { background:var(--red-hl); padding:0 1px; border-radius:2px; }
  mark.tk-new { background:var(--grn-hl); padding:0 1px; border-radius:2px; }
  .rawIssue { font-family:ui-monospace,Menlo,monospace; font-size:11.5px; color:#444;
              padding:2px 0; border-bottom:1px dotted #eee; }
  .fileHd { font-family:ui-monospace,Menlo,monospace; font-size:12.5px; color:var(--info-tx);
            margin:14px 0 4px; word-break:break-all; font-weight:600; }
  .nav { display:flex; gap:8px; margin-top:20px; align-items:center; }
  kbd { background:#eee; border-radius:4px; padding:0 5px; font-size:11px; }
  textarea { width:100%; font:inherit; font-size:13px; padding:7px 10px; min-height:60px;
             border:1px solid var(--bd); border-radius:7px; }
</style>
</head>
<body>
<div id="app">
  <div id="side">
    <div id="head">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>S-D6 adjudication (GD4)</strong><span id="prog"></span>
      </div>
      <div id="bar"><div id="barFill"></div></div>
      <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
        <button onclick="exportCsv()">Download CSV</button>
        <button onclick="copyBlock()">Copy rulings for Claude</button>
      </div>
      <div style="margin-top:6px;color:var(--mut);font-size:11px;">
        <kbd>&larr;</kbd><kbd>&rarr;</kbd> unit nav &middot; <kbd>a</kbd> accept draft &middot; <kbd>1</kbd>causal <kbd>2</kbd>incidental <kbd>3</kbd>fp (sets all lanes) &middot; autosaves to localStorage
      </div>
    </div>
    <div id="list"></div>
  </div>
  <div id="main"></div>
</div>
<script>
const DATA = %%DATA%%;
const LABELS = [["CAUSAL","sel-causal","1"],["REAL-BUT-INCIDENTAL","sel-inc","2"],["DETECTOR-FP","sel-fp","3"]];
const LS = "sd6-adjudication-v1";
let st = DATA.map(d => ({lanes: Object.fromEntries(d.lanes.map(l=>[l,null])), note:""}));
try { const saved = JSON.parse(localStorage.getItem(LS) || "{}");
      DATA.forEach((d,i)=>{ if(saved[d.id]) st[i]=saved[d.id]; }); } catch(e) {}
let cur = 0;
function save(){ const o={}; DATA.forEach((d,i)=>o[d.id]=st[i]); localStorage.setItem(LS, JSON.stringify(o)); }
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function reEsc(s){ return s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&"); }
function ruled(i){ return Object.values(st[i].lanes).every(v=>v!==null); }

function hlTokens(line, olds, news){
  const cls={};
  (news||[]).forEach(t=>{ if(t) cls[t]="tk-new"; });
  (olds||[]).forEach(t=>{ if(t) cls[t]="tk-old"; });
  const toks = Object.keys(cls).sort((a,b)=>b.length-a.length);
  if(!toks.length) return esc(line);
  const rx = new RegExp("(?<![\\w$])(" + toks.map(reEsc).join("|") + ")(?![\\w$])","g");
  let out="", last=0, m;
  while((m=rx.exec(line))!==null){
    out += esc(line.slice(last,m.index));
    out += '<mark class="'+cls[m[1]]+'">'+esc(m[1])+'</mark>';
    last = m.index+m[1].length;
  }
  return out+esc(line.slice(last));
}

function renderList(){
  document.getElementById("list").innerHTML = DATA.map((d,i)=>`
    <div class="sideItem ${i===cur?'cur':''}" onclick="go(${i})">
      <div style="display:flex;gap:7px;align-items:center;">
        <span class="dot ${ruled(i)?'done':''}"></span>
        <span class="mid">${esc(d.id)}</span>
      </div>
      <div class="meta">
        ${d.delta?'<span class="chip c-dlt">Δ exp-only</span>':'<span class="chip c-inf">both arms</span>'}
        <span class="chip ${d.family?'c-grn':'c-amb'}">${esc(d.category)}</span>
      </div>
    </div>`).join("");
  const done = st.filter((_,i)=>ruled(i)).length;
  document.getElementById("prog").textContent = done+"/"+DATA.length;
  document.getElementById("barFill").style.width = (DATA.length?100*done/DATA.length:0)+"%";
}

function presTable(p){
  const row = (lbl,o)=>!o?"":`<tr><td class="lbl">${lbl}</td>`+["base","ours","theirs","merged","dev"]
    .map(k=>`<td class="${o[k]? 'nz':'z'}">${o[k]}</td>`).join("")+"</tr>";
  return `<table class="pres"><tr><th></th><th>base</th><th>ours</th><th>theirs</th><th>merged</th><th>dev</th></tr>
    ${row("old",p.old)}${row("new",p.new)}</table>`;
}

function render(){
  const d = DATA[cur], s = st[cur];
  const olds = [], news = [];
  d.files.forEach(f=>f.idents.forEach(x=>{olds.push(x.old); if(x.new) news.push(x.new);}));
  let h = `
    <h2 class="id">${esc(d.id)}</h2>
    <div class="sub">final label <b>${esc(d.category)}</b> (${d.family?"name-binding family":"outside family"})
      &middot; stratum ${esc(d.stratum)} &middot; passes ${esc(d.passes)}
      &middot; caught by: ${d.arms.map(a=>`<span class="chip ${a==='experimental'?'c-dlt':'c-inf'}">${a}</span>`).join(" ")}</div>`;
  if(d.draft){
    const cls = d.draft==="CAUSAL" ? "c-grn" : (d.draft==="DETECTOR-FP" ? "c-red" : "c-amb");
    h += `<div style="background:var(--info-bg);color:var(--info-tx);border-radius:9px;padding:10px 12px;margin:10px 0;font-size:13px;">
      <b>Claude draft</b> <span class="chip ${cls}">${esc(d.draft)}</span>
      ${d.draft_verify?'<span class="chip c-amb">extra scrutiny suggested</span>':''}
      <button style="margin-left:8px;" onclick="acceptDraft()">Accept (a)</button>
      <div style="margin-top:6px;line-height:1.5;">${esc(d.draft_why)}</div></div>`;
  }
  h += `<div class="sec">Ruling per lane (unit is CAUSAL if any lane is CAUSAL)</div>`;
  d.lanes.forEach(l=>{
    h += `<div class="laneRow"><span class="nm">${esc(l)}</span>` +
      LABELS.map(([lab,cls])=>`<button class="${s.lanes[l]===lab?cls:''}"
        onclick="setLane('${esc(l)}','${lab}')">${lab}</button>`).join("") + `</div>`;
  });
  h += `<div style="margin:8px 0;"><input type="text" placeholder="written rationale (required for GD4)"
        value="${esc(s.note||"")}" onchange="st[cur].note=this.value;save();renderList();"></div>`;
  d.files.forEach(f=>{
    h += `<div class="fileHd">${esc(f.file)}</div>`;
    f.idents.forEach(x=>{
      h += `<div class="identCard">
        <div class="identHd"><span class="nm">${esc(x.old)}</span>
          ${x.new?`&rarr; <span class="nm">${esc(x.new)}</span>`:""}
          ${x.lanes.map(l=>`<span class="chip c-inf">${esc(l)}</span>`).join(" ")}
          <span class="chip c-amb">${x.n_sites} site(s) in merged</span></div>
        ${presTable(x.presence)}
        ${x.wins.map(w=>`<pre class="code">${w[1].map(([ln,tx,fl])=>
          `<div class="cl ${fl?'flag':''}"><span class="ln">${ln}</span><span class="tx">${hlTokens(tx,[x.old],[x.new])}</span></div>`).join("")}</pre>`).join("")}
      </div>`;
    });
    h += `<details><summary>verbatim lane output (${f.raw.length})</summary>
      ${f.raw.map(r=>`<div class="rawIssue">[${esc(r.lane)}::${esc(r.flagseg)}] L${r.line}: ${esc(r.msg)}</div>`).join("")}</details>`;
    h += `<details><summary>full sources (base / ours / theirs / merged / developer)</summary>
      ${["base","ours","theirs","merged","dev"].map(k=>`<details style="margin-left:14px;"><summary>${k}</summary>
        <pre class="code">${f.src[k].split("\n").map((tx,j)=>
          `<div class="cl"><span class="ln">${j+1}</span><span class="tx">${hlTokens(tx,olds,news)}</span></div>`).join("")}</pre></details>`).join("")}
    </details>`;
  });
  h += `<div class="nav">
    <button onclick="go(cur-1)">&larr; prev</button>
    <button onclick="go(cur+1)">next &rarr;</button>
  </div>`;
  document.getElementById("main").innerHTML = h;
}

function setLane(l,lab){ st[cur].lanes[l] = (st[cur].lanes[l]===lab? null : lab); save(); render(); renderList(); }
function acceptDraft(){
  const d = DATA[cur];
  if(!d.draft) return;
  Object.keys(st[cur].lanes).forEach(l=>st[cur].lanes[l]=d.draft);
  if(!st[cur].note) st[cur].note = "[accepted Claude draft] " + d.draft_why;
  save(); render(); renderList();
}
function go(i){ if(i<0||i>=DATA.length) return; cur=i; render(); renderList(); document.getElementById("main").scrollTop=0; }
document.addEventListener("keydown",(e)=>{
  if(e.target.tagName==="INPUT"||e.target.tagName==="TEXTAREA") return;
  if(e.key==="ArrowLeft") go(cur-1);
  if(e.key==="ArrowRight") go(cur+1);
  if(e.key==="a") acceptDraft();
  LABELS.forEach(([lab,,key])=>{ if(e.key===key){
    Object.keys(st[cur].lanes).forEach(l=>st[cur].lanes[l]=lab); save(); render(); renderList(); }});
});

function rows(){
  const out=[["merge_id","category","arms","lane","ruling","unit_rollup","rationale"]];
  DATA.forEach((d,i)=>{
    const anyCausal = Object.values(st[i].lanes).some(v=>v==="CAUSAL");
    d.lanes.forEach(l=>out.push([d.id,d.category,d.arms.join("+"),l,
      st[i].lanes[l]||"", anyCausal?"CAUSAL":"", (st[i].note||"").replace(/\n/g," ")]));
  });
  return out;
}
function exportCsv(){
  const csv = rows().map(r=>r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(",")).join("\n");
  const a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download="sd6_rulings.csv"; a.click();
}
function copyBlock(){
  const missing = DATA.filter((_,i)=>!ruled(i)).length;
  const txt = "S-D6 GD4 rulings ("+(missing? missing+" UNRULED — incomplete":"complete")+")\n" +
    rows().slice(1).map(r=>r.join(" | ")).join("\n");
  navigator.clipboard.writeText(txt).then(()=>alert("copied"));
}
go(0);
</script>
</body>
</html>
"""


def main() -> None:
    cards = build()
    html = TEMPLATE.replace("%%DATA%%", json.dumps(cards))
    out = HERE / "adjudication_ui.html"
    out.write_text(html)
    n_delta = sum(1 for c in cards if c["delta"])
    print(f"wrote {out} — {len(cards)} held-out flagged units "
          f"({n_delta} experimental-only)")


if __name__ == "__main__":
    main()
