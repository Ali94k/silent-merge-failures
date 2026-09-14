"""Generate review_ui.html — standalone browser UI for adjudicating the 23
pilot misses (plan §4.7). Side-by-side developer-resolution vs Mergiraf
output per scored file, line-aligned (difflib opcodes precomputed here),
intraline non-matching spans highlighted, label picker with localStorage
persistence and CSV export. Regenerate after any draft/label change:

    ../../.venv/bin/python make_review_ui.py        (from this directory)
"""
from __future__ import annotations

import csv
import difflib
import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CTX = 3          # context lines kept around changes
COLLAPSE_MIN = 8 # equal runs longer than this are collapsed

csv.field_size_limit(10 ** 8)


def load_inputs():
    cache = json.loads((HERE / "raw_results.json").read_text())
    drafts = {}
    with open(HERE / "misses_classified_draft.csv") as fh:
        for r in csv.DictReader(fh):
            drafts[r["merge_id"]] = (
                r["suspected_category(1-7|none)"].replace("DRAFT:", ""),
                r["rationale"].replace("DRAFT(claude): ", ""),
            )
    scns: dict[str, list[dict]] = {}
    for f in glob.glob(str(ROOT / "data/scenarios_semantic/*.json")):
        s = json.loads(Path(f).read_text())
        scns.setdefault(s["merge_id"], []).append(s)
    idx = {}
    with open(ROOT / "data/schesch-dataset/results/reaper/result_adjusted.csv") as fh:
        for r in csv.DictReader(fh):
            idx[(r["repository"].replace("/", "_"), r["merge"][:10])] = r
    return cache, drafts, scns, idx


def inline_segs(a: str, b: str):
    """Char-level segments [[text, changed]] for one replace-paired line."""
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
    """Aligned row list for side-by-side rendering.

    Row shapes: ["e",text,ll,rl] equal | ["r",lsegs,rsegs,ll,rl] replace pair |
    ["d",text,ll] dev-only | ["i",text,rl] mergiraf-only |
    ["s",[rows]] collapsed equal run.
    """
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


def build_data():
    cache, drafts, scns, idx = load_inputs()
    merges = []
    for mid, (draft, why) in drafts.items():
        repo, sha = mid.rsplit("__", 1)
        row = idx.get((repo, sha), {})
        files = []
        for s in scns[mid]:
            rec = cache[f"{s['scenario_id']}::__merge__::merge-tools/mergiraf:0.17.0"]
            fr = {"p": s["file_path"], "o": rec["outcome"]}
            if rec["outcome"] == "clean":
                dev, mg = s["developer_resolution"], rec["merged"]
                fr["eq"] = [l.rstrip() for l in dev.split("\n") if l.strip()] == \
                           [l.rstrip() for l in mg.split("\n") if l.strip()]
                fr["rows"] = align(dev, mg)
            files.append(fr)
        merges.append({"id": mid, "git": row.get("gitmerge_ort", "?"),
                       "spork": row.get("spork", "?"), "files": files,
                       "draft": draft, "why": why})
    return merges


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Miss classification review — detection pilot (Stage A)</title>
<style>
  :root { --red-bg:#fdecec; --red-hl:#f6b4b4; --red-tx:#8f1d1d;
          --grn-bg:#e9f6ec; --grn-hl:#a9dfb4; --grn-tx:#1d5c2e;
          --mut:#6b7280; --bd:#d6d3cd; --info-bg:#e8f0fb; --info-tx:#1d4f8f; }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, "Segoe UI", Roboto, sans-serif; margin:0;
         color:#1f2937; background:#faf9f5; }
  #app { display:flex; height:100vh; }
  #side { width:300px; min-width:300px; border-right:1px solid var(--bd);
          overflow-y:auto; background:#fff; }
  #main { flex:1; overflow-y:auto; padding:16px 20px; }
  .sideItem { padding:8px 12px; border-bottom:1px solid #eee; cursor:pointer; font-size:12.5px; }
  .sideItem:hover { background:#f5f4f0; }
  .sideItem.cur { background:var(--info-bg); }
  .sideItem .mid { font-family: ui-monospace, Menlo, monospace; word-break:break-all; }
  .sideItem .meta { color:var(--mut); font-size:11.5px; margin-top:2px; display:flex; gap:6px; align-items:center;}
  .dot { width:9px; height:9px; border-radius:50%; background:#d1d5db; display:inline-block; flex:none;}
  .dot.done { background:#34a35b; }
  .chip { font-size:11px; padding:2px 8px; border-radius:10px; white-space:nowrap; display:inline-block; }
  .c-red { background:var(--red-bg); color:var(--red-tx); }
  .c-grn { background:var(--grn-bg); color:var(--grn-tx); }
  .c-amb { background:#fdf3df; color:#7a5410; }
  .c-inf { background:var(--info-bg); color:var(--info-tx); }
  #head { position:sticky; top:0; background:#fff; border-bottom:1px solid var(--bd);
          padding:10px 12px; z-index:5; font-size:13px; }
  #bar { height:5px; background:#eee; border-radius:3px; margin-top:6px; }
  #barFill { height:5px; background:#2f6fce; border-radius:3px; width:0; }
  button { font: inherit; font-size:12.5px; padding:5px 11px; border:1px solid var(--bd);
           border-radius:7px; background:#fff; cursor:pointer; }
  button:hover { background:#f3f2ee; }
  button.sel { border:1.5px solid #2f6fce; background:var(--info-bg); color:var(--info-tx); }
  .draftBox { background:var(--info-bg); color:var(--info-tx); border-radius:9px;
              padding:10px 12px; margin:10px 0; display:flex; gap:12px; align-items:flex-start; font-size:13px;}
  .fileHead { display:flex; gap:8px; align-items:center; margin:14px 0 4px; flex-wrap:wrap; }
  .fileHead .fp { font-family: ui-monospace, Menlo, monospace; font-size:12.5px; font-weight:600; word-break:break-all;}
  table.diff { width:100%; border-collapse:collapse; table-layout:fixed;
               font-family: ui-monospace, Menlo, monospace; font-size:11.8px; line-height:1.45;
               border:1px solid var(--bd); border-radius:8px; }
  table.diff td { vertical-align:top; padding:0 6px; white-space:pre-wrap; word-break:break-all; }
  td.ln { width:42px; text-align:right; color:#9ca3af; user-select:none;
          border-right:1px solid #eee; background:#fafafa; }
  td.lc { width:calc(50% - 42px); }
  td.lc.del { background:var(--red-bg); }
  td.lc.ins { background:var(--grn-bg); }
  td.lc.empty { background:#f3f4f6; }
  mark.del { background:var(--red-hl); color:inherit; padding:0; }
  mark.ins { background:var(--grn-hl); color:inherit; padding:0; }
  tr.skip td { background:#f0f6ff; color:var(--info-tx); text-align:center; cursor:pointer;
               padding:3px; font-size:11.5px; }
  .colHead td { font-family:inherit; font-size:12px; font-weight:600; color:var(--mut);
                background:#fafafa; padding:4px 6px; border-bottom:1px solid var(--bd);}
  .labels { display:flex; flex-wrap:wrap; gap:6px; margin:14px 0 8px; }
  input[type=text] { width:100%; font:inherit; font-size:13px; padding:7px 10px;
                     border:1px solid var(--bd); border-radius:7px; }
  .nav { display:flex; gap:8px; margin-top:14px; align-items:center; }
  .why { font-size:12.5px; }
  kbd { background:#eee; border-radius:4px; padding:0 5px; font-size:11px; }
</style>
</head>
<body>
<div id="app">
  <div id="side">
    <div id="head">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>Miss review</strong><span id="prog"></span>
      </div>
      <div id="bar"><div id="barFill"></div></div>
      <div style="margin-top:8px;display:flex;gap:6px;">
        <button onclick="exportCsv()">Download CSV</button>
        <button onclick="copyBlock()">Copy labels for Claude</button>
      </div>
      <div style="margin-top:6px;color:var(--mut);font-size:11px;">
        <kbd>&larr;</kbd><kbd>&rarr;</kbd> navigate &nbsp;<kbd>a</kbd> accept draft &nbsp;&middot;&nbsp; saved to localStorage
      </div>
    </div>
    <div id="list"></div>
  </div>
  <div id="main"></div>
</div>
<script>
const DATA = %%DATA%%;
const OPTS = [["1","1 · Atomic updates"],["2","2 · Control-flow"],["3","3 · Stale read"],
  ["4","4 · Exceptions"],["5","5 · Loop semantics"],["6","6 · Rename / decl-change"],
  ["7","7 · Scope capture"],["none","none-of-7"],["none-identified","none-identified"],
  ["indeterminate","indeterminate"]];
const LS = "miss-review-v1";
let st = DATA.map(d => ({label:null, note:""}));
try { const saved = JSON.parse(localStorage.getItem(LS) || "{}");
      DATA.forEach((d,i)=>{ if(saved[d.id]) st[i]=saved[d.id]; }); } catch(e) {}
let cur = 0;
function save(){ const o={}; DATA.forEach((d,i)=>o[d.id]=st[i]); localStorage.setItem(LS, JSON.stringify(o)); }
function esc(s){ return s.replace(/&/g,"&amp;").replace(/</g,"&lt;"); }
function lblChip(name,v){ const c = v==="Tests_passed"?"c-grn":(v==="Tests_failed"?"c-red":"c-amb");
  return `<span class="chip ${c}">${name}: ${v}</span>`; }
function segHtml(segs, cls){ return segs.map(([t,h]) => h?`<mark class="${cls}">${esc(t)}</mark>`:esc(t)).join(""); }
function rowHtml(r){
  if(r[0]==="e") return `<tr><td class="ln">${r[2]}</td><td class="lc">${esc(r[1])}</td><td class="ln">${r[3]}</td><td class="lc">${esc(r[1])}</td></tr>`;
  if(r[0]==="r") return `<tr><td class="ln">${r[3]}</td><td class="lc del">${segHtml(r[1],"del")}</td><td class="ln">${r[4]}</td><td class="lc ins">${segHtml(r[2],"ins")}</td></tr>`;
  if(r[0]==="d") return `<tr><td class="ln">${r[2]}</td><td class="lc del">${esc(r[1])}</td><td class="ln"></td><td class="lc empty"></td></tr>`;
  if(r[0]==="i") return `<tr><td class="ln"></td><td class="lc empty"></td><td class="ln">${r[2]}</td><td class="lc ins">${esc(r[1])}</td></tr>`;
}
function renderList(){
  document.getElementById("list").innerHTML = DATA.map((d,i)=>{
    const s=st[i];
    return `<div class="sideItem ${i===cur?"cur":""}" onclick="go(${i})">
      <div class="mid">${i+1}. ${d.id}</div>
      <div class="meta"><span class="dot ${s.label?"done":""}"></span>
        <span>draft: ${d.draft}</span>${s.label?`<span>&rarr; <strong>${s.label}</strong></span>`:""}</div></div>`;
  }).join("");
  const n = st.filter(x=>x.label).length;
  document.getElementById("prog").textContent = n+" / "+DATA.length;
  document.getElementById("barFill").style.width = Math.round(100*n/DATA.length)+"%";
}
function renderMain(){
  const d = DATA[cur], s = st[cur];
  let h = `<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
    <span style="font-family:ui-monospace,Menlo,monospace;font-weight:600;font-size:14px;">${d.id}</span>
    ${lblChip("mergiraf","Tests_failed")} ${lblChip("git",d.git)} ${lblChip("spork",d.spork)}</div>
    <div class="draftBox"><div style="flex:1;">
      <div style="font-weight:600;">Claude draft: ${(OPTS.find(o=>o[0]===d.draft)||[,d.draft])[1]}</div>
      <div class="why">${esc(d.why)}</div></div>
      <button onclick="accept()">&#10003; Accept draft</button></div>`;
  h += `<div class="labels">` + OPTS.map(([v,t]) =>
    `<button class="${s.label===v?"sel":""}" onclick="setLabel('${v}')">${t}</button>`).join("") + `</div>`;
  h += `<input type="text" placeholder="Optional note (override rationale, nuance)" value="${esc(s.note||"").replace(/"/g,"&quot;")}"
        oninput="st[${cur}].note=this.value;save()">`;
  d.files.forEach((f,fi)=>{
    h += `<div class="fileHead"><span class="fp">${f.p}</span>`;
    if(f.o!=="clean"){ h += `<span class="chip c-amb">diverged (${f.o}) — no merged output to compare</span></div>`; return; }
    h += f.eq ? `<span class="chip c-grn">&#8801; dev resolution (ws-normalized)</span>`
              : `<span class="chip c-red">differs from dev</span>`;
    h += `</div><table class="diff"><tr class="colHead"><td colspan="2">developer resolution</td><td colspan="2">mergiraf output</td></tr>`;
    f.rows.forEach((r,ri)=>{
      if(r[0]==="s"){ h += `<tr class="skip" id="sk-${fi}-${ri}" onclick="expand(${fi},${ri})"><td colspan="4">&#8943; ${r[1].length} unchanged lines — click to expand</td></tr>`; }
      else h += rowHtml(r);
    });
    h += `</table>`;
  });
  h += `<div class="nav"><button onclick="go(cur-1)">&larr; Prev</button>
        <button onclick="go(cur+1)">Next &rarr;</button>
        <span style="color:var(--mut);font-size:12px;" id="tally"></span></div>`;
  document.getElementById("main").innerHTML = h;
  const t={}; st.forEach(x=>{ if(x.label) t[x.label]=(t[x.label]||0)+1; });
  document.getElementById("tally").textContent = Object.entries(t).map(([k,v])=>k+": "+v).join("   ");
}
function expand(fi,ri){
  const tr = document.getElementById(`sk-${fi}-${ri}`);
  const rows = DATA[cur].files[fi].rows[ri][1];
  tr.outerHTML = rows.map(rowHtml).join("");
}
function render(){ renderList(); renderMain(); }
function go(i){ if(i<0||i>=DATA.length) return; cur=i; render(); document.getElementById("main").scrollTop=0; }
function setLabel(v){ st[cur].label = (st[cur].label===v? null : v); save(); render(); }
function accept(){ st[cur].label = DATA[cur].draft; save(); if(cur<DATA.length-1) cur++; render(); }
function lines(){ return DATA.map((d,i)=> d.id+" => "+(st[i].label||"UNREVIEWED")+(st[i].note?" | note: "+st[i].note:"")); }
function exportCsv(){
  const rows = [["merge_id","label","note"]].concat(DATA.map((d,i)=>[d.id, st[i].label||"UNREVIEWED", st[i].note||""]));
  const csv = rows.map(r=>r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(",")).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download = "misses_adjudicated.csv"; a.click();
}
function copyBlock(){
  const n = st.filter(x=>x.label).length;
  const txt = "Miss-classification review complete ("+n+"/"+DATA.length+" labeled via review_ui.html). Final labels:\n"
    + lines().join("\n")
    + "\nPlease write these into misses_to_classify.csv as the adjudicated labels and recompute the base-rate table.";
  navigator.clipboard.writeText(txt).then(()=>alert("Copied — paste it to Claude Code."));
}
document.addEventListener("keydown", e => {
  if(e.target.tagName==="INPUT") return;
  if(e.key==="ArrowRight") go(cur+1);
  else if(e.key==="ArrowLeft") go(cur-1);
  else if(e.key==="a") accept();
});
render();
</script>
</body>
</html>
"""


def main() -> None:
    data = build_data()
    js = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    out = HERE / "review_ui.html"
    out.write_text(TEMPLATE.replace("%%DATA%%", js))
    n_files = sum(len(m["files"]) for m in data)
    print(f"wrote {out} — {len(data)} merges, {n_files} files, {out.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
