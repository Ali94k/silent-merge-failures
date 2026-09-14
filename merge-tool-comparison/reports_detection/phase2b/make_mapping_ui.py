"""Generate mapping_ui.html — standalone browser UI for the Phase-2b category
mapping adjudication (17 labeled positives -> 7-category taxonomy + none-of-7).

Adapted from ../full/make_adjudication_ui.py (the §4.6 tool Ali used). All
evidence is precomputed and embedded as JSON — no server, no network;
localStorage persistence + CSV export. Regenerate after any draft edit:

    ../../.venv/bin/python make_mapping_ui.py            (from this directory)

Per unit the UI shows: the frozen draft (category + confidence + rationale from
category_mapping_draft.md), the benchmark metadata (declarations, source study),
what the detectors did (dev arm: all CLEAN; remerge arm: 2 units CONFLICT),
side-by-side base->LEFT and base->RIGHT diffs (the categorization evidence),
a base->MERGED diff, and full-source tabs. Rulings: category 1-7 / none-of-7
(keyboard 1..7, n; a = accept draft; arrows navigate).

Export produces (a) category_mapping_adjudicated.csv — commit,class,draft,
ruling,category,notes — and (b) a ready-to-paste 3-column category_mapping.csv
replacement. Post-run protocol note: rulings recorded after seeing detector
output must stay labeled as such — the run's zeros make relabeling risk-free
for recall direction (any relabel keeps 0/n), but the disclosure stands.
"""
from __future__ import annotations

import csv
import difflib
import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent           # reports_detection/phase2b
ROOT = HERE.parent.parent                         # merge-tool-comparison
POS_DIR = ROOT / "data" / "scenarios_phase2b"
CTX = 4
COLLAPSE_MIN = 8

CATEGORIES = {
    "1-atomic-updates": ("Atomic Updates",
        "Concurrent updates to related state violate a shared invariant "
        "(canonical: A raises min to 10, B lowers max to 5 -> min<=max broken). "
        "Includes OA/both-write shapes: both parents write the same state element."),
    "2-cfi-short-circuit": ("Control Flow Interference (Short Circuit)",
        "A adds a guard/early-return; B adds code meant to always run (or "
        "downstream logic) that the new control flow now bypasses."),
    "3-dfi-stale-read": ("Data Flow Interference (Stale Read)",
        "A resets/clears state (canonical: pendingTasks.clear()); B adds a read "
        "of it -> merged code reads empty/stale state. Def-use across branches."),
    "4-exception-divergence": ("Exception Handling Divergence",
        "A narrows a catch (Exception -> IOException); B adds a call in the try "
        "that throws something no longer caught."),
    "5-loop-semantics": ("Loop Semantics Divergence",
        "A changes loop bounds; B adds continue/skip of the manual increment -> "
        "merged loop is infinite or iterates wrongly."),
    "6-rename-family": ("Method Rename / dangling declaration",
        "A renames or deletes a declaration and fixes existing sites; B adds a "
        "new reference to the OLD name -> dangling reference."),
    "7-scope-capture": ("Scope Capture (Variable Shadowing)",
        "A introduces a local shadowing a field; B adds logic reading the name, "
        "assuming the field -> B's logic silently reads A's local."),
    "none-of-7": ("None of the 7",
        "Real interference, but its shape matches none of the taxonomy "
        "categories (e.g. two flags interacting on one computation)."),
}

# Frozen drafts, transcribed from category_mapping_draft.md (2026-07-04 — BEFORE
# the detector run). Keyed (commit[:10], class-leaf). `conf` in {high,med,low};
# `verify` marks rows the draft flagged for extra scrutiny.
DRAFTS = {
    ("69ff2669ee", "Python2Target"): dict(conf="med", verify=False,
        why="Both parents insert different keywords into the same array initializer "
            "(python2Keywords); concurrent writes to one state element (OA-shape); "
            "nearest of the 7 is #1."),
    ("69ff2669ee", "Python3Target"): dict(conf="med", verify=False,
        why="Identical shape to Python2Target."),
    ("20bac30d9b", "SlangImpl"): dict(conf="med", verify=False,
        why="L adds EVENT_TASK_START to the returned event set; R swaps ASYNC_LOOP_* "
            "for SPLIT/JOIN_* adds — concurrent writes to the same collection build."),
    ("4d9ba9d221", "SlimTableFactory"): dict(conf="med", verify=False,
        why="L adds ddt:/dynamic-decision: table types, R adds script: — concurrent "
            "addTableType writes to one map."),
    ("71f622ce51", "RequestBuilder"): dict(conf="high", verify=False,
        why="L prepends '?' to the requestQuery append; R independently manages "
            "first ? '?' : '&' in the param loop — two writers of one URL-prefix "
            "invariant (double-? class of bug)."),
    ("e825a7fdc6", "AbstractReader"): dict(conf="med", verify=False,
        why="L adds RequestParam/RequestBody/PathVariable, R adds RequestParam/"
            "RequestBody to the same validParameterAnnotations — overlapping "
            "concurrent adds (duplicate-element/import invariant). NOTE: Mergiraf "
            "re-merge CONFLICTs on this unit — surfaced, not silent, under the driver."),
    ("4c506dce43", "MultiShortestPathTree"): dict(conf="med", verify=False,
        why="R adds an isBikeParked early-return-false guard in dominates; L rewrites "
            "the downstream dominance computation the guard now bypasses."),
    ("6fdb8f27b5", "Parser"): dict(conf="med", verify=False,
        why="R inserts a new else-if (hasCssTextContent) branch ahead of the "
            "plain-text branch; L modified that downstream branch (net.extractUrls) "
            "— R's branch diverts flow around L's change."),
    ("3f7d2c71db", "HttpConnection"): dict(conf="low", verify=False,
        why="L makes 307 responses take the redirect branch; R rewrote the "
            "content-type validation those responses previously reached."),
    ("a8b6982de9", "HttpConnection"): dict(conf="low", verify=False,
        why="R conditionalizes redirect data-clearing on status != 307; L adds proxy "
            "plumbing into createConnection used on the re-request path."),
    ("afb82cb3e8", "ClassJsonAdapter"): dict(conf="high", verify=False,
        why="R moves 'if (!annotations.isEmpty()) return null;' above the platform "
            "check; L appends a Kotlin-metadata rejection loop — R's hoisted early "
            "return can bypass L's new check."),
    ("867b917c43", "DirectRestServiceInterfaceClassCreator"): dict(conf="med", verify=False,
        why="L replaces the head guard (void -> primitive-boxing early return); R adds "
            "an overlay-callback branch at the tail — L's early return bypasses R's "
            "branch for primitive returns."),
    ("3d4f99516b", "Slurper"): dict(conf="med", verify=False,
        why="L conditionally re-points/reassigns oplogDb (auth DB selection + late "
            "oplogDb = ...getDB(LOCAL)); R adds a new read of it (oplogRefsCollection) "
            "— def-use/stale-read family, though the reset is REASSIGNMENT, not "
            "literal .clear() (outside the detector's documented shape -> the "
            "expected-FN unit; it was indeed missed in the run)."),
    ("ad2be67883", "KafkaSpoutConfig"): dict(conf="low", verify=True,
        why="VERIFY: L deletes the maxRetries field/builder/getter; R's refactor adds "
            "new references into the retry constants — drafted as delete-vs-reference "
            "(dangling declaration). Check whether R's DEFAULT_MAX_RETRIES reference "
            "actually dangles in the merge. NOTE: Mergiraf re-merge CONFLICTs on this "
            "unit — under the driver it is surfaced, not silent."),
    ("50d8e43eb5", "DeploymentEntityManager"): dict(conf="med", verify=False,
        why="L fixes the process-definition comparison condition; R adds event "
            "dispatch in the timer-job loop — behavioral interference in one method, "
            "no short-circuit/def-use/rename shape."),
    ("a44e18aa3c", "TextNode"): dict(conf="med", verify=False,
        why="L migrates preserveWhitespace to a static-call form; R widens the indent "
            "condition — interacting whitespace behavior, no taxonomy shape."),
    ("193acdb36c", "LengthFieldBasedFrameDecoder"): dict(conf="med", verify=False,
        why="L guards the frameLength += adjustment behind a new flag; R changes "
            "failure timing via another new flag — two flags interacting on one "
            "computation, no taxonomy shape."),
}


# --- diff machinery (house pattern: copied from ../full/make_adjudication_ui.py) ---
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


def align(src: str, dst: str):
    a = [l.rstrip() for l in src.split("\n")]
    b = [l.rstrip() for l in dst.split("\n")]
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


def load_drafts_csv() -> dict[tuple[str, str], str]:
    out = {}
    with open(HERE / "category_mapping.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            out[(r["commit"], r["class"])] = r["category"]
    return out


def remerge_conflicts() -> set[str]:
    out = set()
    p = HERE / "remerge" / "scenarios.csv"
    if p.exists():
        with open(p, newline="") as fh:
            for r in csv.DictReader(fh):
                if r["arm"] == "pos" and r["merge_outcome"] != "clean":
                    out.add(r["scenario_id"])
    return out


def build():
    draft_cat = load_drafts_csv()
    conflicted = remerge_conflicts()
    units = []
    for f in sorted(glob.glob(str(POS_DIR / "*.json"))):
        s = json.loads(Path(f).read_text())
        meta = s["phase2b"]
        cls = meta["class"]
        leaf = cls.split(".")[-1].split("$")[0]
        key = (s["merge_commit"][:10], leaf)
        d = DRAFTS.get(key, dict(conf="?", verify=False, why="(no draft transcribed)"))
        units.append({
            "id": s["scenario_id"],
            "commit": s["merge_commit"],
            "cls": cls,
            "repo": s["repo_name"],
            "decls": meta["declarations"],
            "studies": meta["studies"],
            "draft": draft_cat.get((s["merge_commit"], cls), "unmapped"),
            "conf": d["conf"],
            "verify": d["verify"],
            "why": d["why"],
            "conflicted": s["scenario_id"] in conflicted,
            "diffL": align(s["base_content"], s["ours_content"]),
            "diffR": align(s["base_content"], s["theirs_content"]),
            "diffM": align(s["base_content"], s["developer_resolution"]),
            "src": {"base": s["base_content"], "left": s["ours_content"],
                    "right": s["theirs_content"], "merged": s["developer_resolution"]},
        })
    # draft-category order mirrors the draft doc: 1,2,3,6,none; stable by id
    order = list(CATEGORIES)
    units.sort(key=lambda u: (order.index(u["draft"]) if u["draft"] in order else 99, u["id"]))
    return units


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Phase-2b category mapping adjudication</title>
<style>
  :root { --red-bg:#fdecec; --red-hl:#f6b4b4; --red-tx:#8f1d1d;
          --grn-bg:#e9f6ec; --grn-hl:#a9dfb4; --grn-tx:#1d5c2e;
          --amb-bg:#fdf3df; --amb-tx:#7a5410;
          --mut:#6b7280; --bd:#d6d3cd; --info-bg:#e8f0fb; --info-tx:#1d4f8f; }
  * { box-sizing:border-box; }
  body { font-family:-apple-system,"Segoe UI",Roboto,sans-serif; margin:0; color:#1f2937; background:#faf9f5; }
  #app { display:flex; height:100vh; }
  #side { width:330px; min-width:330px; border-right:1px solid var(--bd); overflow-y:auto; background:#fff; }
  #main { flex:1; overflow-y:auto; padding:16px 22px 90px; }
  #head { position:sticky; top:0; background:#fff; border-bottom:1px solid var(--bd); padding:10px 12px; z-index:5; font-size:13px; }
  #bar { height:5px; background:#eee; border-radius:3px; margin-top:6px; }
  #barFill { height:5px; background:#2f6fce; border-radius:3px; width:0; }
  .sideItem { padding:8px 12px; border-bottom:1px solid #eee; cursor:pointer; font-size:12.5px; }
  .sideItem:hover { background:#f5f4f0; }
  .sideItem.cur { background:var(--info-bg); }
  .sideItem .mid { font-family:ui-monospace,Menlo,monospace; word-break:break-all; }
  .sideItem .meta { color:var(--mut); font-size:11.5px; margin-top:3px; display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
  .dot { width:9px; height:9px; border-radius:50%; background:#d1d5db; display:inline-block; flex:none; }
  .dot.done { background:#34a35b; }
  .chip { font-size:11px; padding:2px 8px; border-radius:10px; white-space:nowrap; display:inline-block; }
  .c-grn { background:var(--grn-bg); color:var(--grn-tx); }
  .c-amb { background:var(--amb-bg); color:var(--amb-tx); }
  .c-red { background:var(--red-bg); color:var(--red-tx); }
  .c-inf { background:var(--info-bg); color:var(--info-tx); }
  button { font:inherit; font-size:12.5px; padding:5px 11px; border:1px solid var(--bd); border-radius:7px; background:#fff; cursor:pointer; }
  button:hover { background:#f3f2ee; }
  button.catBtn { display:block; width:100%; text-align:left; margin:4px 0; padding:8px 11px; }
  button.catBtn .cid { font-family:ui-monospace,Menlo,monospace; font-weight:600; }
  button.catBtn .cdesc { display:block; font-size:11.5px; color:var(--mut); margin-top:2px; }
  button.catBtn.sel { border:1.5px solid var(--grn-tx); background:var(--grn-bg); }
  button.catBtn.sel .cdesc { color:var(--grn-tx); }
  button.catBtn.isDraft { box-shadow:inset 3px 0 0 #2f6fce; }
  h2.id { font-family:ui-monospace,Menlo,monospace; font-size:15px; margin:2px 0; word-break:break-all; }
  .sub { color:var(--mut); font-size:12px; font-family:ui-monospace,Menlo,monospace; margin-bottom:8px; word-break:break-all; }
  .draftBox { background:var(--info-bg); color:var(--info-tx); border-radius:9px; padding:10px 12px; margin:10px 0; font-size:13px; line-height:1.5; }
  .verifyBox { background:#fff7e6; color:#8a5a00; border:1px solid #f0c674; border-radius:9px; padding:9px 12px; margin:10px 0; font-size:12.5px; }
  .surfBox { background:var(--grn-bg); color:var(--grn-tx); border-radius:9px; padding:9px 12px; margin:10px 0; font-size:12.5px; }
  .sec { margin:18px 0 6px; font-weight:600; font-size:13px; color:#374151; border-bottom:1px solid var(--bd); padding-bottom:4px; }
  input[type=text] { width:100%; font:inherit; font-size:13px; padding:7px 10px; border:1px solid var(--bd); border-radius:7px; }
  .cols { display:flex; gap:14px; align-items:flex-start; }
  .cols > div { flex:1; min-width:0; }
  table.diff { width:100%; border-collapse:collapse; table-layout:fixed; font-family:ui-monospace,Menlo,monospace; font-size:11.4px; line-height:1.45; border:1px solid var(--bd); }
  table.diff td { vertical-align:top; padding:0 6px; white-space:pre-wrap; word-break:break-all; }
  td.dln { width:40px; text-align:right; color:#9ca3af; user-select:none; border-right:1px solid #eee; background:#fafafa; }
  td.lc { width:calc(50% - 40px); }
  td.lc.del { background:var(--red-bg); } td.lc.ins { background:var(--grn-bg); } td.lc.empty { background:#f3f4f6; }
  mark.del { background:var(--red-hl); } mark.ins { background:var(--grn-hl); }
  tr.skip td { background:#f0f6ff; color:var(--info-tx); text-align:center; cursor:pointer; padding:3px; font-size:11.5px; }
  .colHead td { font-size:12px; font-weight:600; color:var(--mut); background:#fafafa; padding:4px 6px; border-bottom:1px solid var(--bd); }
  details { margin:10px 0; }
  details > summary { cursor:pointer; font-size:12.5px; color:var(--info-tx); padding:4px 0; }
  pre.src { border:1px solid var(--bd); border-radius:8px; padding:8px 12px; font-size:11.5px; line-height:1.5; overflow-x:auto; background:#fff; max-height:480px; overflow-y:auto; }
  .tabs { display:flex; gap:4px; margin:6px 0; flex-wrap:wrap; }
  .tabs button.act { border:1.5px solid #2f6fce; background:var(--info-bg); color:var(--info-tx); }
  .nav { display:flex; gap:8px; margin-top:20px; align-items:center; }
  kbd { background:#eee; border-radius:4px; padding:0 5px; font-size:11px; }
  .catgrid { display:grid; grid-template-columns:1fr 1fr; gap:2px 14px; }
  #expBox { position:fixed; bottom:0; left:330px; right:0; background:#fff; border-top:1px solid var(--bd); padding:9px 22px; display:flex; gap:10px; align-items:center; font-size:12.5px; z-index:6; }
</style>
</head>
<body>
<div id="app">
  <div id="side">
    <div id="head">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>Phase-2b mapping</strong><span id="prog"></span>
      </div>
      <div id="bar"><div id="barFill"></div></div>
      <div style="color:var(--mut);margin-top:5px;">17 positives → categories 1–7 / none.
      <kbd>1</kbd>–<kbd>7</kbd> pick, <kbd>n</kbd> none, <kbd>a</kbd> accept draft, <kbd>←</kbd><kbd>→</kbd> navigate.</div>
    </div>
    <div id="list"></div>
  </div>
  <div id="main"></div>
</div>
<div id="expBox">
  <button onclick="exportCsv()">Export adjudicated CSV</button>
  <button onclick="copyMapping()">Copy 3-col category_mapping.csv</button>
  <button onclick="resetAll()" style="color:var(--red-tx)">Reset all</button>
  <span id="expMsg" style="color:var(--mut)"></span>
</div>
<script>
const DATA = __DATA__;
const CATS = __CATS__;
const CATKEYS = Object.keys(CATS);
const LS = "phase2b_mapping_v1";
let state = JSON.parse(localStorage.getItem(LS) || "{}");
let cur = 0, tab = {};

function save() { localStorage.setItem(LS, JSON.stringify(state)); }
function st(id) { return state[id] || (state[id] = {ruling:"", notes:""}); }
function esc(s) { return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function segs(sg, cls) { return sg.map(([t,d]) => d ? `<mark class="${cls}">${esc(t)}</mark>` : esc(t)).join(""); }

function diffHtml(rows, li, ri, uid, key) {
  let h = `<table class="diff"><tr class="colHead"><td colspan=2>${li}</td><td colspan=2>${ri}</td></tr>`;
  rows.forEach((r, ix) => {
    const k = r[0];
    if (k === "e") h += `<tr><td class=dln>${r[2]}</td><td class=lc>${esc(r[1])}</td><td class=dln>${r[3]}</td><td class=lc>${esc(r[1])}</td></tr>`;
    else if (k === "s") h += `<tr class=skip data-u="${uid}" data-k="${key}" data-i="${ix}"><td colspan=4>··· ${r[1].length} unchanged lines — click to expand ···</td></tr>`;
    else if (k === "r") h += `<tr><td class=dln>${r[3]}</td><td class="lc del">${segs(r[1],"del")}</td><td class=dln>${r[4]}</td><td class="lc ins">${segs(r[2],"ins")}</td></tr>`;
    else if (k === "d") h += `<tr><td class=dln>${r[2]}</td><td class="lc del">${esc(r[1])}</td><td class=dln></td><td class="lc empty"></td></tr>`;
    else h += `<tr><td class=dln></td><td class="lc empty"></td><td class=dln>${r[2]}</td><td class="lc ins">${esc(r[1])}</td></tr>`;
  });
  return h + "</table>";
}

function expand(el) {
  const u = DATA[+el.dataset.u], key = el.dataset.k, ix = +el.dataset.i;
  const rows = {L:u.diffL, R:u.diffR, M:u.diffM}[key];
  rows.splice(ix, 1, ...rows[ix][1]);
  render();
}
document.addEventListener("click", e => {
  const t = e.target.closest("tr.skip"); if (t) expand(t);
});

function sideList() {
  document.getElementById("list").innerHTML = DATA.map((u, i) => {
    const s = st(u.id);
    const leaf = u.cls.split(".").pop();
    return `<div class="sideItem ${i===cur?"cur":""}" onclick="go(${i})">
      <div class=mid>${esc(u.repo)} · <b>${esc(leaf)}</b></div>
      <div class=meta><span class="dot ${s.ruling?"done":""}"></span>
        <span class="chip c-inf">draft ${esc(u.draft)}</span>
        ${s.ruling ? `<span class="chip ${s.ruling===u.draft?"c-grn":"c-amb"}">ruled ${esc(s.ruling)}</span>` : ""}
        ${u.verify ? `<span class="chip c-red">VERIFY</span>` : ""}
        ${u.conflicted ? `<span class="chip c-grn">remerge: CONFLICT</span>` : ""}
      </div></div>`;
  }).join("");
  const done = DATA.filter(u => st(u.id).ruling).length;
  document.getElementById("prog").textContent = `${done}/${DATA.length}`;
  document.getElementById("barFill").style.width = (100*done/DATA.length) + "%";
}

function catButtons(u) {
  const s = st(u.id);
  return `<div class=catgrid>` + CATKEYS.map((k, i) => {
    const key = k === "none-of-7" ? "n" : String(i+1);
    return `<button class="catBtn ${s.ruling===k?"sel":""} ${u.draft===k?"isDraft":""}"
      onclick="rule('${u.id}','${k}')">
      <span class=cid><kbd>${key}</kbd> ${esc(k)}</span> — ${esc(CATS[k][0])}
      <span class=cdesc>${esc(CATS[k][1])}</span></button>`;
  }).join("") + `</div>`;
}

function render() {
  sideList();
  const u = DATA[cur], s = st(u.id);
  const t = tab[u.id] || "none";
  document.getElementById("main").innerHTML = `
    <h2 class=id>${esc(u.id)}</h2>
    <div class=sub>${esc(u.cls)} · decl: ${esc(u.decls.join(", "))} · study: ${esc(u.studies.join(", "))} · merge ${u.commit.slice(0,12)}</div>
    <div class=draftBox><b>Frozen draft: ${esc(u.draft)}</b> (confidence ${esc(u.conf)}) — ${esc(u.why)}</div>
    ${u.verify ? `<div class=verifyBox><b>Draft flagged VERIFY</b> — check the noted claim against the diffs before ruling.</div>` : ""}
    ${u.conflicted ? `<div class=surfBox>Deployment note: Mergiraf re-merge CONFLICTs here — under the driver this unit is surfaced textually, not a silent miss. (Detectors on the developer merge: all CLEAN.)</div>` : `<div class=surfBox style="background:#f3f4f6;color:#4b5563">Detectors on the developer merge: all CLEAN (run of 2026-07-04, commit f964354).</div>`}
    <div class=sec>Your ruling</div>
    ${catButtons(u)}
    <div style="margin:10px 0"><input type=text placeholder="notes (optional — recorded in the export)" value="${esc(s.notes||"")}"
      onchange="st('${u.id}').notes=this.value;save()"></div>
    <div class=nav>
      <button onclick="rule('${u.id}','${u.draft}')">Accept draft (<kbd>a</kbd>)</button>
      <button onclick="go(cur-1)">← prev</button><button onclick="go(cur+1)">next →</button>
    </div>
    <div class=sec>Evidence — what each parent changed vs base</div>
    <div class=cols>
      <div>${diffHtml(u.diffL, "base", "LEFT (ours)", cur, "L")}</div>
      <div>${diffHtml(u.diffR, "base", "RIGHT (theirs)", cur, "R")}</div>
    </div>
    <details><summary>base → developer MERGE diff</summary>${diffHtml(u.diffM, "base", "developer merge", cur, "M")}</details>
    <details><summary>full sources</summary>
      <div class=tabs>${["base","left","right","merged"].map(k =>
        `<button class="${t===k?"act":""}" onclick="tab['${u.id}']='${k}';render()">${k}</button>`).join("")}</div>
      ${t !== "none" && u.src[t] !== undefined ? `<pre class=src>${esc(u.src[t])}</pre>` : `<div style="color:var(--mut);font-size:12.5px">pick a tab</div>`}
    </details>`;
}

function rule(id, cat) { st(id).ruling = cat; save(); render(); }
function go(i) { cur = Math.max(0, Math.min(DATA.length-1, i)); render(); document.getElementById("main").scrollTop = 0; }

document.addEventListener("keydown", e => {
  if (e.target.tagName === "INPUT") return;
  const u = DATA[cur];
  if (e.key >= "1" && e.key <= "7") rule(u.id, CATKEYS[+e.key - 1]);
  else if (e.key === "n") rule(u.id, "none-of-7");
  else if (e.key === "a") rule(u.id, u.draft);
  else if (e.key === "ArrowLeft") go(cur-1);
  else if (e.key === "ArrowRight") go(cur+1);
});

function dl(name, text) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], {type:"text/csv"}));
  a.download = name; a.click();
}
function exportCsv() {
  const q = v => `"${String(v).replace(/"/g,'""')}"`;
  let rows = ["commit,class,draft,ruling,category,notes"];
  DATA.forEach(u => { const s = st(u.id);
    rows.push([u.commit, u.cls, u.draft, s.ruling||"", s.ruling||u.draft, q(s.notes||"")].join(","));
  });
  dl("category_mapping_adjudicated.csv", rows.join("\n") + "\n");
  document.getElementById("expMsg").textContent = "exported category_mapping_adjudicated.csv";
}
function copyMapping() {
  let rows = ["commit,class,category"];
  DATA.forEach(u => rows.push([u.commit, u.cls, st(u.id).ruling || u.draft].join(",")));
  navigator.clipboard.writeText(rows.join("\n") + "\n");
  document.getElementById("expMsg").textContent = "3-col mapping copied to clipboard";
}
function resetAll() {
  if (confirm("Clear all rulings + notes?")) { state = {}; save(); render(); }
}
render();
</script>
</body>
</html>
"""


def main() -> None:
    units = build()
    assert len(units) == 17, f"expected 17 positives, got {len(units)}"
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(units))
            .replace("__CATS__", json.dumps(CATEGORIES)))
    out = HERE / "mapping_ui.html"
    out.write_text(html)
    print(f"wrote {out} ({out.stat().st_size/1e6:.1f} MB, {len(units)} units)")


if __name__ == "__main__":
    main()
