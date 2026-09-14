"""Generate adjudication_ui.html — standalone browser UI for Stage-C §4.6 hit
adjudication (ISSUES #29). 15 detector FLAGs (11 positives, 4 controls); per
flag Ali rules CAUSAL / REAL-BUT-INCIDENTAL / DETECTOR-FP with written reasoning.
Adapted from ../pilot/make_review_ui.py (the miss-review UI Ali liked).

All evidence is precomputed here and embedded as JSON — no server, no network;
localStorage persistence + CSV/clipboard export. Regenerate after any draft edit:

    ../../.venv/bin/python make_adjudication_ui.py        (from this directory)

Line-numbering note (why the UI re-locates flagged identifiers in the merged
file rather than trusting the detector's reported line):
  - JoernUnresolvedReference and RM2 *call*-lane line numbers ARE merged-file
    coordinates (Joern reads the CPG; `_scan_stale_callers` indexes merged_text).
  - RM2 *var*-lane line numbers are computed on COMMENT/STRING-STRIPPED text
    (`_scan_stale_var_refs` indexes `_strip_comments_and_strings(merged)`), whose
    char-literal regex can eat newlines and shift line numbers (the mtedone FP:
    reported "L1538" is a Javadoc line; the real `mapType` sites are L2459+).
  So the detector's verbatim output is shown for provenance, but the context
  windows + parent-presence table are recomputed against the actual merged file.
"""
from __future__ import annotations

import csv
import difflib
import glob
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent          # reports_detection/full
ROOT = HERE.parent.parent                        # merge-tool-comparison
COMMIT = "843e5f5"
MERGE_TOOL = "merge-tools/mergiraf:0.17.0"
DETECTORS = ["JoernDataFlowInterference", "JoernUnresolvedReference",
             "JoernInfiniteLoop", "JoernInvalidLoopBounds", "RM2RenameConflict"]
CTX = 4           # context lines around each flagged site
COLLAPSE_MIN = 8  # equal runs longer than this collapse in the dev/mergiraf diff

csv.field_size_limit(10 ** 8)

# Draft labels + rationale, transcribed from hit_adjudications_draft.md (NOT the
# answer — the starting point Ali accepts/overrides). `verify` raises the two
# cases the draft flagged for extra scrutiny.
DRAFTS = {
    "ahome-it_lienzo-core__bf4b253816__src_main_java_com_ait_lienzo_client_core_shape_wires_WiresShape.java": dict(
        label="CAUSAL", verify=False,
        why="field rename innerLayoutContainer→m_innerLayoutContainer half-applied; the bare reference is unresolved = compile error. Joern + RM2 var-lane agree on the same site."),
    "atam4j_atam4j__71fcecb071__acceptance-tests_src_test_java_me_atam_atam4jsampleapp_testsupport_AcceptanceTest.java": dict(
        label="CAUSAL", verify=False,
        why="method rename getTestRunResultFromServer→getCriticalTestRunResultFromServer; 4 stale callers of the old name = compile error."),
    "comatoes_ftl-profile-editor__e87fe65818__src_main_java_net_blerf_ftl_parser_SavedGameParser.java": dict(
        label="CAUSAL", verify=True,
        why="VERIFY the RM2 rename pairing. Unresolved 'gameState' (Joern) is solid and stands on its own. But RM2's setReservePowerCapacity→setSectorNumber pairing looks like RM2 matching two dissimilar methods — setReservePowerCapacity persists in every parent AND in the developer resolution, so it is not actually a rename. Likely keep the merge CAUSAL via the Joern lane, mark the RM2 lane REAL-BUT-INCIDENTAL/FP in the notes."),
    "datastax_java-driver__e1535e89ad__driver-core_src_main_java_com_datastax_driver_core_HostConnectionPool.java": dict(
        label="CAUSAL", verify=False,
        why="unresolved 'isShutdown' in borrowConnection — referenced in merged, resolvable in neither parent."),
    "erudika_para__a9e67cc8b3__para-server_src_main_java_com_erudika_para_aop_IndexAndCacheAspect.java": dict(
        label="CAUSAL", verify=False,
        why="variable rename m→method half-applied; bare 'm' unresolved at L109. Pilot hit reconfirmed (adjudicated in pilot_v2)."),
    "jacquesberger_jsonparsingexample__ac521954c2__src_main_java_org_jberger_jsonparsingexample_json_JSON.java": dict(
        label="CAUSAL", verify=False,
        why="unresolved 'bookTitleList' and 'outputList' (Joern ×2). Pilot hit reconfirmed."),
    "jcabi_jcabi-github__27cc460e3c__src_test_java_com_jcabi_github_RtGistITCase.java": dict(
        label="CAUSAL", verify=False,
        why="stale caller gist( after rename to github = compile error."),
    "jcabi_jcabi-github__e18a8ffd16__src_test_java_com_jcabi_github_RtHooksITCase.java": dict(
        label="CAUSAL", verify=False,
        why="stale callers repo( after rename to repos (4 sites) = compile error."),
    "jdupl_lancoder__407742ea19__src_main_java_org_lancoder_master_api_web_ApiServer.java": dict(
        label="CAUSAL", verify=False,
        why="unresolved 'ctxApi' in run — referenced in merged, resolvable in neither parent."),
    "softinstigate_restheart__98dda32101__graphql_src_main_java_org_restheart_graphql_GraphQLService.java": dict(
        label="CAUSAL", verify=False,
        why="request→req / response→res half-applied, 7 stale sites, dual-lane (Joern + RM2 var) agreement."),
    "tcurdt_jdeb__77d052996a__src_main_java_org_vafer_jdeb_DataBuilder.java": dict(
        label="CAUSAL", verify=True,
        why="VERIFY: field rename compression→options; single site at L95. Confirm 'compression' is no longer declared in merged (only the one bare use should remain; 'options' is the surviving declaration at L87)."),
    # controls — proposed DETECTOR-FP
    "aerospike_aerospike-client-java__b77316ac92__proxy_src_com_aerospike_client_proxy_grpc_GrpcStreamingCall.java": dict(
        label="DETECTOR-FP", verify=False,
        why="var-lane matched the METHOD isSingleResponse() — declared & live at L210 (public boolean isSingleResponse()). Missing '('-exclusion in the var-lane scan. Control merge passes tests."),
    "cloudfoundry_cf-java-client__0d588aa1e7__cloudfoundry-client-reactor_src_main_java_org_cloudfoundry_reactor_util_Operator.java": dict(
        label="DETECTOR-FP", verify=False,
        why="var-lane matched the METHOD request(HttpMethod) and a lambda param 'request' — not a stale variable. Same missing '('-exclusion. Control merge passes tests."),
    "cloudfoundry_cf-java-client__f994a25985__cloudfoundry-client-reactor_src_main_java_org_cloudfoundry_reactor_util_Operator.java": dict(
        label="DETECTOR-FP", verify=False,
        why="identical to the other cf-java-client Operator FP: method request(...) / lambda param matched by the var-lane; missing '('-exclusion. Control merge passes tests."),
    "mtedone_podam__1075ffea79__src_main_java_uk_co_jemos_podam_api_PodamFactoryImpl.java": dict(
        label="DETECTOR-FP", verify=False,
        why="comment-stripper newline bug: 'mapType' IS still declared & used (L2459 'Class<? extends Map<?,?>> mapType =', L2746 param). The reported lines (1538–1763) are stripped-text coordinates that land on Javadoc; the decl-guard was blinded by corrupted stripped text. Control merge passes tests."),
}

RE_VAR = re.compile(r"renamed variable/field: '([^']+)' \(renamed to '([^']+)'\)")
RE_CALL = re.compile(r"renamed identifier: '([^']+)' \(renamed to '([^']+)'\)")
RE_JOERN = re.compile(r"identifier '([^']+)'")


def parse_issue(det: str, msg: str):
    """-> (old_name, new_name|None, lane) ; lane in {call,var,joern,?}."""
    if det == "RM2RenameConflict":
        m = RE_VAR.search(msg)
        if m:
            return m.group(1), m.group(2), "var"
        m = RE_CALL.search(msg)
        if m:
            return m.group(1), m.group(2), "call"
    m = RE_JOERN.search(msg)
    if m:
        return m.group(1), None, "joern"
    return None, None, "?"


def count_tok(tok: str, text: str) -> int:
    if not tok:
        return 0
    return len(re.findall(rf"\b{re.escape(tok)}\b", text))


def merged_sites(old: str, is_call: bool, lines: list[str]) -> list[int]:
    pat = re.compile(rf"\b{re.escape(old)}\s*\(") if is_call else re.compile(rf"\b{re.escape(old)}\b")
    return [i + 1 for i, l in enumerate(lines) if pat.search(l)]


def windows(sites: list[int], lines: list[str]) -> list[list]:
    """Merge per-site ±CTX windows; -> [[ [lineno, text, flagged], ... ], ...]."""
    if not sites:
        return []
    flagged = set(sites)
    spans = []
    for s in sites:
        lo, hi = max(1, s - CTX), min(len(lines), s + CTX)
        if spans and lo <= spans[-1][1] + 1:
            spans[-1][1] = max(spans[-1][1], hi)
        else:
            spans.append([lo, hi])
    out = []
    for lo, hi in spans:
        out.append([[n, lines[n - 1].rstrip("\n"), n in flagged] for n in range(lo, hi + 1)])
    return out


def inline_segs(a: str, b: str):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    left, right = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            left.append([a[i1:i2], 0])
            right.append([b[j1:j2], 0])
        else:
            if i2 > i1:
                left.append([a[i1:i2], 1])
            if j2 > j1:
                right.append([b[j1:j2], 1])
    return left, right


def align(dev: str, mg: str):
    a = [l.rstrip() for l in dev.split("\n")]
    b = [l.rstrip() for l in mg.split("\n")]
    rows = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            run = [["e", a[i1 + k], i1 + k + 1, j1 + k + 1] for k in range(i2 - i1)]
            if len(run) > COLLAPSE_MIN + 2 * CTX:
                rows.extend(run[:CTX])
                rows.append(["s", run[CTX:-CTX]])
                rows.extend(run[-CTX:])
            else:
                rows.extend(run)
        elif op == "replace":
            n = min(i2 - i1, j2 - j1)
            for k in range(n):
                ls, rs = inline_segs(a[i1 + k], b[j1 + k])
                rows.append(["r", ls, rs, i1 + k + 1, j1 + k + 1])
            for k in range(i1 + n, i2):
                rows.append(["d", a[k], k + 1])
            for k in range(j1 + n, j2):
                rows.append(["i", b[k], k + 1])
        elif op == "delete":
            for k in range(i1, i2):
                rows.append(["d", a[k], k + 1])
        else:
            for k in range(j1, j2):
                rows.append(["i", b[k], k + 1])
    return rows


def load():
    cache = json.loads((HERE / "raw_results.json").read_text())
    scns = {}
    for arm, d in (("pos", "scenarios_semantic"), ("ctl", "scenarios_semantic_ctl")):
        for f in glob.glob(str(ROOT / "data" / d / "*.json")):
            s = json.loads(Path(f).read_text())
            s["__arm__"] = arm
            scns[s["scenario_id"]] = s
    idx = {}
    rpath = ROOT / "data/schesch-dataset/results/reaper/result_adjusted.csv"
    if rpath.exists():
        with open(rpath) as fh:
            for r in csv.DictReader(fh):
                idx[(r["repository"].replace("/", "_"), r["merge"][:10])] = r
    return cache, scns, idx


def build():
    cache, scns, idx = load()
    flags = []
    for sid, s in scns.items():
        lanes = {}
        for det in DETECTORS:
            k = f"{sid}::{det}::{COMMIT}"
            rec = cache.get(k)
            if rec and rec.get("verdict") == "FLAG":
                lanes[det] = rec["issues"]
        if not lanes:
            continue

        rec = cache[f"{sid}::__merge__::{MERGE_TOOL}"]
        merged = rec["merged"]
        mlines = merged.split("\n")
        base, ours, theirs = s["base_content"], s["ours_content"], s["theirs_content"]
        dev = s["developer_resolution"]

        # group flagged issues by old identifier
        groups: dict[str, dict] = {}
        for det, issues in lanes.items():
            for iss in issues:
                old, new, lane = parse_issue(det, iss["message"])
                if not old:
                    continue
                g = groups.setdefault(old, {"old": old, "new": None, "lanes": set(),
                                            "is_call": False, "raw": []})
                if new and not g["new"]:
                    g["new"] = new
                g["lanes"].add(det)
                if lane == "call":
                    g["is_call"] = True
                coord = "stripped" if (det == "RM2RenameConflict" and lane == "var") else "merged"
                g["raw"].append({"det": det, "line": iss["line"],
                                 "msg": iss["message"], "coord": coord})

        idents = []
        for old, g in groups.items():
            new = g["new"]
            sites = merged_sites(old, g["is_call"], mlines)
            idents.append({
                "old": old, "new": new,
                "lanes": sorted(g["lanes"]),
                "is_call": g["is_call"],
                "presence": {
                    "old": {"base": count_tok(old, base), "ours": count_tok(old, ours),
                            "theirs": count_tok(old, theirs), "merged": count_tok(old, merged),
                            "dev": count_tok(old, dev)},
                    "new": (None if not new else
                            {"base": count_tok(new, base), "ours": count_tok(new, ours),
                             "theirs": count_tok(new, theirs), "merged": count_tok(new, merged),
                             "dev": count_tok(new, dev)}),
                },
                "wins": windows(sites, mlines),
                "n_sites": len(sites),
                "raw": sorted(g["raw"], key=lambda r: (r["det"], r["line"])),
            })
        idents.sort(key=lambda x: (-len(x["lanes"]), x["old"]))

        row = idx.get((s["repo_name"], s["merge_commit"][:10]), {})
        dev_eq = ([l.rstrip() for l in dev.split("\n") if l.strip()]
                  == [l.rstrip() for l in merged.split("\n") if l.strip()])
        draft = DRAFTS.get(sid, {"label": "", "why": "(no draft)", "verify": False})

        lane_counts = {det: len(iss) for det, iss in lanes.items()}
        highlights = sorted({i["old"] for i in idents}
                            | {i["new"] for i in idents if i["new"]})

        flags.append({
            "id": sid,
            "repo": s["repo_name"],
            "file": s["file_path"],
            "arm": s["__arm__"],
            "schesch": "Tests_failed" if s["__arm__"] == "pos" else "Tests_passed",
            "git": row.get("gitmerge_ort", "?"),
            "spork": row.get("spork", "?"),
            "lanes": lane_counts,
            "idents": idents,
            "diff": align(dev, merged),
            "dev_eq": dev_eq,
            "src": {"base": base, "ours": ours, "theirs": theirs,
                    "merged": merged, "dev": dev},
            "hl": highlights,
            "draft": draft["label"], "why": draft["why"], "verify": draft["verify"],
        })

    # positives first, then controls; stable by id within arm
    flags.sort(key=lambda f: (f["arm"] != "pos", f["id"]))
    return flags


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Stage-C hit adjudication — ISSUES #29 §4.6</title>
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
  #side { width:320px; min-width:320px; border-right:1px solid var(--bd);
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
  .c-pos { background:#efe3fb; color:#5b2a86; }
  .c-ctl { background:#e3eef0; color:#27606b; }
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
  .sub { color:var(--mut); font-size:12px; font-family:ui-monospace,Menlo,monospace; margin-bottom:8px; word-break:break-all; }
  .draftBox { background:var(--info-bg); color:var(--info-tx); border-radius:9px;
              padding:10px 12px; margin:10px 0; display:flex; gap:12px; align-items:flex-start; font-size:13px; }
  .verifyBox { background:#fff7e6; color:#8a5a00; border:1px solid #f0c674; border-radius:9px;
               padding:9px 12px; margin:10px 0; font-size:12.5px; }
  .labels { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0 8px; align-items:center; }
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
  .rawIssue .pill { font-size:10px; padding:1px 6px; border-radius:8px; margin-right:6px; }
  .pill.merged { background:var(--grn-bg); color:var(--grn-tx); }
  .pill.stripped { background:var(--amb-bg); color:var(--amb-tx); }
  table.diff { width:100%; border-collapse:collapse; table-layout:fixed;
               font-family:ui-monospace,Menlo,monospace; font-size:11.6px; line-height:1.45;
               border:1px solid var(--bd); border-radius:8px; }
  table.diff td { vertical-align:top; padding:0 6px; white-space:pre-wrap; word-break:break-all; }
  td.dln { width:42px; text-align:right; color:#9ca3af; user-select:none; border-right:1px solid #eee; background:#fafafa; }
  td.lc { width:calc(50% - 42px); }
  td.lc.del { background:var(--red-bg); } td.lc.ins { background:var(--grn-bg); } td.lc.empty { background:#f3f4f6; }
  mark.del { background:var(--red-hl); } mark.ins { background:var(--grn-hl); }
  tr.skip td { background:#f0f6ff; color:var(--info-tx); text-align:center; cursor:pointer; padding:3px; font-size:11.5px; }
  .colHead td { font-size:12px; font-weight:600; color:var(--mut); background:#fafafa; padding:4px 6px; border-bottom:1px solid var(--bd); }
  .tabs { display:flex; gap:4px; margin:6px 0; flex-wrap:wrap; }
  .tabs button.act { border:1.5px solid #2f6fce; background:var(--info-bg); color:var(--info-tx); }
  .nav { display:flex; gap:8px; margin-top:20px; align-items:center; }
  kbd { background:#eee; border-radius:4px; padding:0 5px; font-size:11px; }
  .why { font-size:12.5px; line-height:1.5; }
</style>
</head>
<body>
<div id="app">
  <div id="side">
    <div id="head">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>Stage-C adjudication</strong><span id="prog"></span>
      </div>
      <div id="bar"><div id="barFill"></div></div>
      <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
        <button onclick="exportCsv()">Download CSV</button>
        <button onclick="copyBlock()">Copy rulings for Claude</button>
      </div>
      <div style="margin-top:6px;color:var(--mut);font-size:11px;">
        <kbd>&larr;</kbd><kbd>&rarr;</kbd> nav &middot; <kbd>a</kbd> accept &middot; <kbd>1</kbd>causal <kbd>2</kbd>incidental <kbd>3</kbd>fp &middot; localStorage
      </div>
    </div>
    <div id="list"></div>
  </div>
  <div id="main"></div>
</div>
<script>
const DATA = %%DATA%%;
const LABELS = [["CAUSAL","sel-causal","1"],["REAL-BUT-INCIDENTAL","sel-inc","2"],["DETECTOR-FP","sel-fp","3"]];
const LS = "stage-c-adjudication-v1";
let st = DATA.map(() => ({label:null, note:""}));
try { const saved = JSON.parse(localStorage.getItem(LS) || "{}");
      DATA.forEach((d,i)=>{ if(saved[d.id]) st[i]=saved[d.id]; }); } catch(e) {}
let cur = 0;
function save(){ const o={}; DATA.forEach((d,i)=>o[d.id]=st[i]); localStorage.setItem(LS, JSON.stringify(o)); }
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function reEsc(s){ return s.replace(/[.*+?^${}()|[\]\\]/g,"\\$&"); }

function hlTokens(line, olds, news){
  // match whole-word old/new tokens on the RAW line, escape the pieces between.
  const cls={};
  (news||[]).forEach(t=>{ if(t) cls[t]="tk-new"; });
  (olds||[]).forEach(t=>{ if(t) cls[t]="tk-old"; });   // old wins on overlap
  const toks=Object.keys(cls);
  if(!toks.length) return esc(line);
  const re=new RegExp("\\b("+toks.map(reEsc).join("|")+")\\b","g");
  let out="", last=0, m;
  while((m=re.exec(line))!==null){
    out+=esc(line.slice(last,m.index));
    out+=`<mark class="${cls[m[0]]}">`+esc(m[0])+`</mark>`;
    last=m.index+m[0].length;
  }
  return out+esc(line.slice(last));
}
function codeBlock(rows, olds, news){
  // rows: [lineno, text, flagged]
  return `<pre class="code">` + rows.map(r =>
    `<div class="cl ${r[2]?"flag":""}"><span class="ln">${r[0]}</span><span class="tx">${hlTokens(r[1],olds,news)}</span></div>`
  ).join("") + `</pre>`;
}
function presTable(p){
  const cols=["base","ours","theirs","merged","dev"];
  const cell=(o)=>cols.map(c=>{const v=o[c];return `<td class="${v?"nz":"z"}">${v}</td>`;}).join("");
  let h=`<table class="pres"><tr><th>identifier</th>${cols.map(c=>`<th>${c}</th>`).join("")}</tr>`;
  h+=`<tr><td class="lbl">old: ${esc(p.old.__nm)}</td>${cell(p.old)}</tr>`;
  if(p.new) h+=`<tr><td class="lbl">new: ${esc(p.new.__nm)}</td>${cell(p.new)}</tr>`;
  return h+`</table>`;
}
function laneChips(lanes){
  return Object.entries(lanes).map(([d,n])=>{
    const short=d.replace("Joern","").replace("RM2","RM2 ");
    return `<span class="chip c-inf">${short}${n>1?" ×"+n:""}</span>`;
  }).join(" ");
}
function diffRowHtml(r){
  if(r[0]==="e") return `<tr><td class="dln">${r[2]}</td><td class="lc">${esc(r[1])}</td><td class="dln">${r[3]}</td><td class="lc">${esc(r[1])}</td></tr>`;
  if(r[0]==="r") return `<tr><td class="dln">${r[3]}</td><td class="lc del">${segHtml(r[1],"del")}</td><td class="dln">${r[4]}</td><td class="lc ins">${segHtml(r[2],"ins")}</td></tr>`;
  if(r[0]==="d") return `<tr><td class="dln">${r[2]}</td><td class="lc del">${esc(r[1])}</td><td class="dln"></td><td class="lc empty"></td></tr>`;
  if(r[0]==="i") return `<tr><td class="dln"></td><td class="lc empty"></td><td class="dln">${r[2]}</td><td class="lc ins">${esc(r[1])}</td></tr>`;
}
function segHtml(segs, cls){ return segs.map(([t,h]) => h?`<mark class="${cls}">${esc(t)}</mark>`:esc(t)).join(""); }

function renderList(){
  document.getElementById("list").innerHTML = DATA.map((d,i)=>{
    const s=st[i];
    return `<div class="sideItem ${i===cur?"cur":""}" onclick="go(${i})">
      <div class="mid">${i+1}. ${d.repo}</div>
      <div class="meta"><span class="dot ${s.label?"done":""}"></span>
        <span class="chip ${d.arm==="pos"?"c-pos":"c-ctl"}">${d.arm}</span>
        <span>draft: ${d.draft}</span>${s.label?`<span>&rarr; <strong>${s.label}</strong></span>`:""}
        ${d.verify?'<span class="chip c-amb">verify</span>':""}</div></div>`;
  }).join("");
  const n = st.filter(x=>x.label).length;
  document.getElementById("prog").textContent = n+" / "+DATA.length;
  document.getElementById("barFill").style.width = Math.round(100*n/DATA.length)+"%";
}
function renderMain(){
  const d=DATA[cur], s=st[cur];
  const olds=d.hl.filter(x=>d.idents.some(it=>it.old===x));
  const news=d.hl.filter(x=>d.idents.some(it=>it.new===x));
  let h=`<h2 class="id">${d.repo}</h2><div class="sub">${d.file}</div>
    <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
      <span class="chip ${d.arm==="pos"?"c-pos":"c-ctl"}">${d.arm==="pos"?"POSITIVE":"CONTROL"}</span>
      <span class="chip ${d.schesch==="Tests_failed"?"c-red":"c-grn"}">schesch: ${d.schesch}</span>
      <span class="chip ${d.git==="Tests_failed"?"c-red":(d.git==="Tests_passed"?"c-grn":"c-amb")}">git: ${d.git}</span>
      <span class="chip ${d.spork==="Tests_failed"?"c-red":(d.spork==="Tests_passed"?"c-grn":"c-amb")}">spork: ${d.spork}</span>
      ${laneChips(d.lanes)}</div>`;

  h+=`<div class="draftBox"><div style="flex:1;">
      <div style="font-weight:600;">Claude draft: ${d.draft}</div>
      <div class="why">${esc(d.why)}</div></div>
      <button onclick="accept()">&#10003; Accept draft</button></div>`;
  if(d.verify) h+=`<div class="verifyBox"><strong>&#9888; Verify case.</strong> The draft asks you to confirm a specific point before citing it — see the rationale above and the parent-presence table / source viewer below.</div>`;

  h+=`<div class="labels"><span style="color:var(--mut);font-size:12px;">Ruling:</span>`+
     LABELS.map(([v,cls,k])=>`<button class="${s.label===v?cls:""}" onclick="setLabel('${v}')">${v} <span style="opacity:.5">[${k}]</span></button>`).join("")+`</div>`;
  h+=`<input type="text" placeholder="Reasoning / override note (recorded as the audit trail)" value="${esc(s.note||"").replace(/"/g,"&quot;")}" oninput="st[${cur}].note=this.value;save()">`;

  // --- flagged identifiers ---
  h+=`<div class="sec">Flagged identifiers &mdash; present? (Q1) &middot; merge-induced? (Q2)</div>`;
  d.idents.forEach((it,ii)=>{
    h+=`<div class="identCard"><div class="identHd">
      <span class="nm">${esc(it.old)}</span>${it.new?`<span style="color:var(--mut)">&rarr;</span><span class="nm" style="color:var(--grn-tx)">${esc(it.new)}</span>`:""}
      ${it.lanes.map(l=>`<span class="chip c-inf">${l.replace("Joern","").replace("RM2RenameConflict","RM2 var/call")}</span>`).join("")}
      <span class="chip c-amb">${it.n_sites} site${it.n_sites!==1?"s":""} in merged</span></div>`;
    const pres={old:Object.assign({__nm:it.old},it.presence.old)};
    if(it.presence.new) pres.new=Object.assign({__nm:it.new},it.presence.new);
    h+=presTable(pres);
    // merged context windows
    if(it.wins.length){
      it.wins.forEach(w=> h+=codeBlock(w,[it.old],it.new?[it.new]:[]));
    } else {
      h+=`<div style="color:var(--mut);font-size:12px;">No occurrence of <code>${esc(it.old)}</code> found in the merged file by the re-scan (var-lane line number is stripped-text coordinate — see verbatim output).</div>`;
    }
    // verbatim detector output
    h+=`<details><summary>Detector output (verbatim, as reported)</summary>`+
       it.raw.map(r=>`<div class="rawIssue"><span class="pill ${r.coord}">${r.coord==="stripped"?"stripped-coord":"merged-coord"}</span>${r.det} L${r.line}: ${esc(r.msg)}</div>`).join("")+
       `</details></div>`;
  });

  // --- dev vs mergiraf diff ---
  h+=`<div class="sec">Causality (Q3) &mdash; developer resolution vs Mergiraf output</div>`;
  h+=`<details ${d.idents.length?"":"open"}><summary>${d.dev_eq?"&#8801; dev resolution matches mergiraf (ws-normalized) &mdash; show diff":"side-by-side diff (what the developer did differently)"}</summary>`;
  h+=`<table class="diff"><tr class="colHead"><td colspan="2">developer resolution</td><td colspan="2">mergiraf output</td></tr>`;
  d.diff.forEach((r,ri)=>{
    if(r[0]==="s") h+=`<tr class="skip" id="sk-${ri}" onclick="expand(${ri})"><td colspan="4">&#8943; ${r[1].length} unchanged lines &mdash; click to expand</td></tr>`;
    else h+=diffRowHtml(r);
  });
  h+=`</table></details>`;

  // --- source viewer ---
  h+=`<div class="sec">Source viewer &mdash; full files (flagged identifiers highlighted)</div>`;
  h+=`<div class="tabs" id="tabs">`+["base","ours","theirs","merged","dev"].map((t,ti)=>
     `<button class="${ti===0?"act":""}" onclick="showSrc('${t}',this)">${t}</button>`).join("")+
     `<span style="color:var(--mut);font-size:11.5px;align-self:center;">&nbsp;old=<mark class="tk-old">red</mark> new=<mark class="tk-new">green</mark></span></div>`;
  h+=`<div id="srcView"></div>`;

  h+=`<div class="nav"><button onclick="go(cur-1)">&larr; Prev</button>
      <button onclick="go(cur+1)">Next &rarr;</button>
      <span style="color:var(--mut);font-size:12px;" id="tally"></span></div>`;
  document.getElementById("main").innerHTML=h;
  showSrc("base", document.querySelector("#tabs button"));
  const t={}; st.forEach(x=>{ if(x.label) t[x.label]=(t[x.label]||0)+1; });
  document.getElementById("tally").textContent=Object.entries(t).map(([k,v])=>k+": "+v).join("   ");
}
function showSrc(which, btn){
  const d=DATA[cur];
  const olds=d.hl.filter(x=>d.idents.some(it=>it.old===x));
  const news=d.hl.filter(x=>d.idents.some(it=>it.new===x));
  const rows=d.src[which].split("\n").map((l,i)=>[i+1,l,false]);
  document.getElementById("srcView").innerHTML=codeBlock(rows,olds,news);
  if(btn){ document.querySelectorAll("#tabs button").forEach(b=>b.classList.remove("act")); btn.classList.add("act"); }
}
function expand(ri){
  const tr=document.getElementById(`sk-${ri}`);
  tr.outerHTML=DATA[cur].diff[ri][1].map(diffRowHtml).join("");
}
function render(){ renderList(); renderMain(); }
function go(i){ if(i<0||i>=DATA.length) return; cur=i; render(); document.getElementById("main").scrollTop=0; }
function setLabel(v){ st[cur].label=(st[cur].label===v?null:v); save(); render(); }
function accept(){ st[cur].label=DATA[cur].draft; save(); if(cur<DATA.length-1) cur++; render(); }
function lines(){ return DATA.map((d,i)=>`${d.id} => ${st[i].label||"UNREVIEWED"}${st[i].note?" | note: "+st[i].note:""}`); }
function exportCsv(){
  const rows=[["scenario_id","arm","draft","ruling","note"]].concat(
    DATA.map((d,i)=>[d.id,d.arm,d.draft,st[i].label||"UNREVIEWED",st[i].note||""]));
  const csv=rows.map(r=>r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(",")).join("\n");
  const a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download="hit_adjudications.csv"; a.click();
}
function copyBlock(){
  const n=st.filter(x=>x.label).length;
  const counts={}; st.forEach(x=>{ if(x.label) counts[x.label]=(counts[x.label]||0)+1; });
  const txt="Stage-C hit adjudication complete ("+n+"/"+DATA.length+" ruled via adjudication_ui.html).\n"
    +"Tally: "+Object.entries(counts).map(([k,v])=>k+": "+v).join(", ")+"\n\nRulings:\n"
    +lines().join("\n")
    +"\n\nPlease fold these into reports_detection/full/hit_adjudications.md (promote the draft, mark ADJUDICATED), recompute R2 decomposed by label in FINDINGS.md, and update STATUS/THREATS/ISSUES #29 per the handoff §3.";
  navigator.clipboard.writeText(txt).then(()=>alert("Copied — paste it to Claude Code."));
}
document.addEventListener("keydown", e=>{
  if(e.target.tagName==="INPUT") return;
  if(e.key==="ArrowRight") go(cur+1);
  else if(e.key==="ArrowLeft") go(cur-1);
  else if(e.key==="a") accept();
  else if(e.key==="1") setLabel("CAUSAL");
  else if(e.key==="2") setLabel("REAL-BUT-INCIDENTAL");
  else if(e.key==="3") setLabel("DETECTOR-FP");
});
render();
</script>
</body>
</html>
"""


def main() -> None:
    data = build()
    js = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    out = HERE / "adjudication_ui.html"
    out.write_text(TEMPLATE.replace("%%DATA%%", js))
    n_pos = sum(1 for f in data if f["arm"] == "pos")
    n_ctl = len(data) - n_pos
    print(f"wrote {out} — {len(data)} flags ({n_pos} pos, {n_ctl} ctl), "
          f"{out.stat().st_size/1e6:.1f} MB")
    for f in data:
        print(f"  [{f['arm']}] {f['repo']:34} idents={len(f['idents'])} "
              f"lanes={f['lanes']} draft={f['draft']}")


if __name__ == "__main__":
    main()
