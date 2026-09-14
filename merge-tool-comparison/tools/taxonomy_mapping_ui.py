"""G2(iv) codebook review UI generator (ISSUES #30, S3, protocol §6/§7 G2 iv).

Ali's ruling on the Phase-2 codebook draft, via a standalone no-server review UI
in the mapping_ui.html / make_adjudication_ui.py style. Parses
`reports_taxonomy/phase2/codebook_draft.md` into structured categories (each
anchor enriched with its Phase-1 mechanism.summary + tags for provenance — all
derivation units), plus the old->new mapping and four-family assessment, and
renders per-category controls:

  ACCEPT / RENAME / EDIT / MERGE (into another category) / SPLIT / REJECT
  + a reason box; plus a mapping/four-family comment and a top-level codebook
  ruling (APPROVE / REVISE). Rulings export to JSON + CSV and a copy-for-Claude
  block. Applying them + freezing (codebook_frozen.md + the Phase-3 schema enum)
  is a SEPARATE freeze commit — this tool only collects the ruling.

Output: reports_taxonomy/phase2/mapping_ui.html

    ../.venv/bin/python tools/taxonomy_mapping_ui.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "reports_taxonomy/phase2/codebook_draft.md"
RAW = ROOT / "reports_taxonomy/phase1/raw_results.json"
SPLIT_CSV = ROOT / "reports_taxonomy/split_assignment.csv"
OUT = ROOT / "reports_taxonomy/phase2/mapping_ui.html"

FIELDS = ["name", "mechanism", "definition", "inclusion", "exclusion", "boundary"]


def derivation_lookup() -> dict[str, dict]:
    raw = json.loads(RAW.read_text())
    deriv = set()
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            if r["split"] == "derivation":
                deriv.add(r["merge_id"])
    out = {}
    for mid in deriv:
        p = raw[mid]["parsed"]
        out[mid] = {"verdict": p["verdict"],
                    "summary": (p.get("mechanism", {}) or {}).get("summary", ""),
                    "tags": (p.get("mechanism", {}) or {}).get("tags", []),
                    "interaction_point": p.get("interaction_point", "")}
    return out


def _field(block: str, name: str) -> str:
    """Text after '- **name:**' up to the next '- **' marker or block end."""
    m = re.search(rf"- \*\*{name}:\*\*\s*(.*?)(?=\n- \*\*|\n---|\Z)", block, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def parse_categories(txt: str, look: dict) -> list[dict]:
    sec = txt.split("## 3.")[0]
    cats = []
    for part in re.split(r"\n### ", sec)[1:]:
        m = re.match(r"`([^`]+)`", part.strip())
        if not m:
            continue
        cid = m.group(1)
        anchors = []
        for aid, note in re.findall(r"^  - `([^`]+)` — (.+)$", part, re.M):
            info = look.get(aid, {})
            anchors.append({"unit_id": aid, "note": note.strip(),
                            "in_derivation": aid in look,
                            "verdict": info.get("verdict", "?"),
                            "summary": info.get("summary", ""),
                            "tags": info.get("tags", []),
                            "interaction_point": info.get("interaction_point", "")})
        cats.append({
            "id": cid,
            "name": _field(part, "name"),
            "mechanism": _field(part, "mechanism"),
            "definition": _field(part, "definition"),
            "inclusion": _field(part, "inclusion"),
            "exclusion": _field(part, "exclusion"),
            "boundary": _field(part, "boundary"),
            "anchors": anchors,
            "provisional": "provisional" in part.lower() and "flag" in part.lower(),
        })
    return cats


def parse_mapping(txt: str) -> list[dict]:
    sec = txt.split("## 3.")[-1].split("## 4.")[0]
    rows = []
    for line in sec.splitlines():
        m = re.match(r"\|\s*(\d)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", line)
        if m:
            rows.append({"num": m.group(1), "historical": m.group(2),
                         "counterpart": m.group(3)})
    return rows


def coverage_sizes(txt: str) -> dict:
    sec = txt.split("## 5.")[-1]
    sizes = {}
    for _u, c in re.findall(r"^\| (\S[^|]*?) \| ([a-z][a-z0-9-]*) \|", sec, re.M):
        if _u.strip() == "unit_id":
            continue
        sizes[c] = sizes.get(c, 0) + 1
    return sizes


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Phase-2 codebook review — ISSUES #30 G2(iv)</title>
<style>
  :root{--red-bg:#fdecec;--red-tx:#8f1d1d;--grn-bg:#e9f6ec;--grn-tx:#1d5c2e;
        --amb-bg:#fdf3df;--amb-tx:#7a5410;--mut:#6b7280;--bd:#d6d3cd;
        --info-bg:#e8f0fb;--info-tx:#1d4f8f;--pur-bg:#efe3fb;--pur-tx:#5b2a86;}
  *{box-sizing:border-box;}
  body{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;margin:0;color:#1f2937;background:#faf9f5;}
  #app{display:flex;height:100vh;}
  #side{width:320px;min-width:320px;border-right:1px solid var(--bd);overflow-y:auto;background:#fff;}
  #main{flex:1;overflow-y:auto;padding:16px 24px 100px;}
  #head{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--bd);padding:10px 12px;z-index:5;font-size:13px;}
  #bar{height:5px;background:#eee;border-radius:3px;margin-top:6px;}#barFill{height:5px;background:#2f6fce;border-radius:3px;width:0;}
  .sideItem{padding:9px 12px;border-bottom:1px solid #eee;cursor:pointer;font-size:12.5px;}
  .sideItem:hover{background:#f5f4f0;}.sideItem.cur{background:var(--info-bg);}
  .sideItem .id{font-family:ui-monospace,Menlo,monospace;word-break:break-all;font-size:12px;}
  .sideItem .meta{color:var(--mut);font-size:11.5px;margin-top:3px;display:flex;gap:6px;align-items:center;flex-wrap:wrap;}
  .dot{width:9px;height:9px;border-radius:50%;background:#d1d5db;display:inline-block;flex:none;}.dot.done{background:#34a35b;}
  .chip{font-size:11px;padding:2px 8px;border-radius:10px;white-space:nowrap;display:inline-block;}
  .c-inf{background:var(--info-bg);color:var(--info-tx);}.c-att{background:var(--pur-bg);color:var(--pur-tx);}
  .c-grn{background:var(--grn-bg);color:var(--grn-tx);}.c-amb{background:var(--amb-bg);color:var(--amb-tx);}.c-red{background:var(--red-bg);color:var(--red-tx);}
  button{font:inherit;font-size:12.5px;padding:5px 11px;border:1px solid var(--bd);border-radius:7px;background:#fff;cursor:pointer;}
  button:hover{background:#f3f2ee;}
  button.on{border-width:1.5px;font-weight:600;}
  button.on-acc{border-color:var(--grn-tx);background:var(--grn-bg);color:var(--grn-tx);}
  button.on-ren{border-color:var(--info-tx);background:var(--info-bg);color:var(--info-tx);}
  button.on-edit{border-color:var(--amb-tx);background:var(--amb-bg);color:var(--amb-tx);}
  button.on-mrg{border-color:var(--pur-tx);background:var(--pur-bg);color:var(--pur-tx);}
  button.on-spl{border-color:var(--pur-tx);background:var(--pur-bg);color:var(--pur-tx);}
  button.on-rej{border-color:var(--red-tx);background:var(--red-bg);color:var(--red-tx);}
  h2.id{font-family:ui-monospace,Menlo,monospace;font-size:16px;margin:2px 0;word-break:break-all;}
  .sec{margin:18px 0 6px;font-weight:600;font-size:13px;color:#374151;border-bottom:1px solid var(--bd);padding-bottom:4px;}
  .card{border:1px solid var(--bd);border-radius:9px;padding:10px 13px;margin:8px 0;background:#fff;}
  .kv{display:flex;gap:8px;margin:5px 0;font-size:13px;line-height:1.5;}
  .kv .k{color:var(--mut);min-width:110px;font-weight:600;flex:none;}
  .tag{font-family:ui-monospace,Menlo,monospace;font-size:11.5px;background:#eef;color:#3b3b8f;padding:1px 6px;border-radius:6px;margin:0 4px 3px 0;display:inline-block;}
  .anchor{border:1px solid var(--bd);border-radius:8px;padding:8px 10px;margin:7px 0;background:#fff;}
  .anchor .uid{font-family:ui-monospace,Menlo,monospace;font-size:12px;word-break:break-all;}
  .anchor pre{margin:5px 0 0;font-size:11.5px;white-space:pre-wrap;word-break:break-word;background:#faf9f5;padding:6px 8px;border-radius:6px;border-left:3px solid var(--bd);}
  .labels{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0 6px;align-items:center;}
  input[type=text],textarea{width:100%;font:inherit;font-size:13px;padding:7px 10px;border:1px solid var(--bd);border-radius:7px;}
  textarea{min-height:52px;resize:vertical;}
  select{font:inherit;font-size:12.5px;padding:5px 8px;border:1px solid var(--bd);border-radius:7px;}
  .sub{margin:8px 0;padding:8px 10px;border:1px dashed var(--bd);border-radius:8px;background:#fcfbf7;}
  kbd{background:#eee;border-radius:4px;padding:0 5px;font-size:11px;}
  table{border-collapse:collapse;width:100%;font-size:12.5px;}
  td,th{border:1px solid var(--bd);padding:6px 8px;text-align:left;vertical-align:top;}
  th{background:#f5f4f0;}
  .warn{background:#fff7e6;color:#8a5a00;border:1px solid #f0c674;border-radius:8px;padding:8px 11px;margin:8px 0;font-size:12.5px;}
  .ok{color:var(--grn-tx);}.bad{color:var(--red-tx);font-weight:600;}
  .nav{display:flex;gap:8px;margin-top:22px;align-items:center;}
</style></head><body>
<div id="app">
  <div id="side">
    <div id="head">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>Codebook review — G2(iv)</strong><span id="prog"></span></div>
      <div id="bar"><div id="barFill"></div></div>
      <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
        <button onclick="exportJson()">Download rulings JSON</button>
        <button onclick="exportCsv()">CSV</button>
        <button onclick="copyBlock()">Copy for Claude</button></div>
      <div style="margin-top:6px;color:var(--mut);font-size:11px;">
        <kbd>&larr;</kbd><kbd>&rarr;</kbd> nav &middot; rule each category, then set the
        overall codebook ruling on the last screen &middot; saved to localStorage.</div>
    </div>
    <div id="list"></div>
  </div>
  <div id="main"></div>
</div>
<script>
const CATS=%%CATS%%, MAP=%%MAP%%, SIZES=%%SIZES%%, FOURFAMILY=%%FF%%, META=%%META%%;
const ACTIONS=[["ACCEPT","on-acc","keep as-is"],["RENAME","on-ren","new id/name"],
  ["EDIT","on-edit","adjust definition/criteria"],["MERGE","on-mrg","fold into another"],
  ["SPLIT","on-spl","break into >1"],["REJECT","on-rej","drop"]];
const LS="phase2-codebook-review-v1";
// screens = categories + [mapping/four-family] + [overall submit]
const N=CATS.length;
let st=CATS.map(()=>({action:null,note:"",new_id:"",merge_target:""}));
let extra={map_comment:"",ff_comment:"",overall:null,escape_ack:false,overall_note:""};
try{const s=JSON.parse(localStorage.getItem(LS)||"{}");
  if(s.st)CATS.forEach((c,i)=>{if(s.st[c.id])st[i]=s.st[c.id];});
  if(s.extra)extra=Object.assign(extra,s.extra);}catch(e){}
let cur=0;
function save(){const o={st:{},extra};CATS.forEach((c,i)=>o.st[c.id]=st[i]);localStorage.setItem(LS,JSON.stringify(o));}
function esc(s){return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function ruled(i){return st[i].action!=null;}

function renderList(){
  let h=CATS.map((c,i)=>{const s=st[i];
    return `<div class="sideItem ${cur===i?"cur":""}" onclick="go(${i})">
      <div class="id">${i+1}. ${esc(c.id)}</div>
      <div class="meta"><span class="dot ${ruled(i)?"done":""}"></span>
        <span class="chip c-att">${SIZES[c.id]||0} units</span>
        ${s.action?`<span class="chip c-inf">${s.action}</span>`:""}</div></div>`;}).join("");
  h+=`<div class="sideItem ${cur===N?"cur":""}" onclick="go(${N})">
      <div class="id">${N+1}. Old&rarr;new mapping &amp; four-family</div>
      <div class="meta"><span class="dot ${extra.map_comment||extra.ff_comment?"done":""}"></span></div></div>`;
  h+=`<div class="sideItem ${cur===N+1?"cur":""}" onclick="go(${N+1})">
      <div class="id">${N+2}. Overall ruling + submit</div>
      <div class="meta"><span class="dot ${extra.overall?"done":""}"></span>
        ${extra.overall?`<span class="chip ${extra.overall==="APPROVE"?"c-grn":"c-amb"}">${extra.overall}</span>`:""}</div></div>`;
  document.getElementById("list").innerHTML=h;
  const n=st.filter((_,i)=>ruled(i)).length;
  document.getElementById("prog").textContent=n+" / "+N+" cats";
  document.getElementById("barFill").style.width=Math.round(100*n/N)+"%";
}

function catScreen(){
  const c=CATS[cur],s=st[cur];
  let h=`<h2 class="id">${esc(c.id)}</h2>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin:6px 0;">
      <span class="chip c-att">${SIZES[c.id]||0} attributed units</span>
      ${c.provisional?`<span class="chip c-amb">provisional</span>`:""}
      <span class="chip c-inf">${c.anchors.length} anchor(s)</span></div>`;
  // ruling controls
  h+=`<div class="labels"><span style="color:var(--mut);font-size:12px;">Ruling:</span>`+
     ACTIONS.map(([v,cls,tip])=>`<button title="${tip}" class="${s.action===v?"on "+cls:""}" onclick="setAction('${v}')">${v}</button>`).join("")+`</div>`;
  if(s.action==="RENAME"||s.action==="MERGE"){
    h+=`<div class="sub">`;
    if(s.action==="RENAME")h+=`<div class="kv"><span class="k">new id/name</span>
      <input type="text" value="${esc(s.new_id)}" placeholder="new-kebab-id / New name" oninput="st[${cur}].new_id=this.value;save()"></div>`;
    if(s.action==="MERGE"){h+=`<div class="kv"><span class="k">merge into</span>
      <select onchange="st[${cur}].merge_target=this.value;save()"><option value="">— pick target —</option>`+
      CATS.filter(x=>x.id!==c.id).map(x=>`<option value="${esc(x.id)}" ${s.merge_target===x.id?"selected":""}>${esc(x.id)}</option>`).join("")+`</select></div>`;}
    h+=`</div>`;}
  h+=`<textarea placeholder="Reason / edit notes (required for anything other than ACCEPT)" oninput="st[${cur}].note=this.value;save()">${esc(s.note)}</textarea>`;
  // category definition
  h+=`<div class="sec">Definition</div><div class="card">
    <div class="kv"><span class="k">name</span><span>${esc(c.name)}</span></div>
    <div class="kv"><span class="k">mechanism</span><span>${esc(c.mechanism)}</span></div>
    <div class="kv"><span class="k">definition</span><span>${esc(c.definition)}</span></div>
    <div class="kv"><span class="k">inclusion</span><span>${esc(c.inclusion)}</span></div>
    <div class="kv"><span class="k">exclusion</span><span>${esc(c.exclusion)}</span></div>
    <div class="kv"><span class="k">boundary</span><span>${esc(c.boundary)}</span></div></div>`;
  // anchors (provenance)
  h+=`<div class="sec">Anchors — Phase-1 provenance (derivation units)</div>`;
  if(!c.anchors.length)h+=`<div style="color:var(--mut);font-size:12.5px;">(residual-other: no anchors expected)</div>`;
  c.anchors.forEach(a=>{
    const fw=a.in_derivation?`<span class="chip c-grn">&#10003; derivation</span>`:`<span class="chip c-red">&#10007; NOT in derivation</span>`;
    const vch=a.verdict==="attributed"?"c-att":"c-amb";
    h+=`<div class="anchor"><div style="display:flex;justify-content:space-between;gap:8px;align-items:center;flex-wrap:wrap;">
      <span class="uid">${esc(a.unit_id)}</span><span>${fw} <span class="chip ${vch}">${a.verdict}</span></span></div>
      <div style="font-size:12px;color:var(--mut);margin-top:4px;">anchor note: ${esc(a.note)}</div>
      <div style="margin-top:5px;">${(a.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join("")}</div>
      <pre>${esc(a.summary||"(no summary)")}</pre></div>`;});
  h+=nav();
  return h;
}

function mapScreen(){
  let h=`<h2 class="id">Old&rarr;new mapping &amp; four-family</h2>`;
  h+=`<div class="sec">Old (7 historical) &rarr; new mapping</div><table>
    <tr><th>#</th><th>Historical category</th><th>Empirical counterpart</th></tr>`+
    MAP.map(r=>`<tr><td>${esc(r.num)}</td><td>${esc(r.historical)}</td><td>${esc(r.counterpart)}</td></tr>`).join("")+`</table>`;
  h+=`<textarea placeholder="Comment on the old→new mapping (optional)" oninput="extra.map_comment=this.value;save()">${esc(extra.map_comment)}</textarea>`;
  h+=`<div class="sec">Four-family assessment</div><div class="card" style="white-space:pre-wrap;font-size:12.5px;line-height:1.55;">${esc(FOURFAMILY)}</div>`;
  h+=`<textarea placeholder="Comment on the four-family assessment (optional)" oninput="extra.ff_comment=this.value;save()">${esc(extra.ff_comment)}</textarea>`;
  h+=nav();return h;
}

function submitScreen(){
  const ruledN=st.filter((_,i)=>ruled(i)).length;
  const nonAccept=st.filter(s=>s.action&&s.action!=="ACCEPT");
  let h=`<h2 class="id">Overall codebook ruling</h2>`;
  h+=`<div class="card"><div class="kv"><span class="k">categories</span><span>${N} (${ruledN} ruled)</span></div>
    <div class="kv"><span class="k">non-ACCEPT</span><span>${nonAccept.length} (${nonAccept.map(s=>"").length?"":""}${st.map((s,i)=>s.action&&s.action!=="ACCEPT"?CATS[i].id+"="+s.action:null).filter(Boolean).join(", ")||"none"})</span></div>
    <div class="kv"><span class="k">G2 machine</span><span class="ok">(i)(ii)(iii) PASS — see phase2/g2_eval.md</span></div></div>`;
  if(ruledN<N)h+=`<div class="warn">&#9888; ${N-ruledN} category(ies) not yet ruled.</div>`;
  h+=`<div class="sec">Escape-hatch stratum acknowledgment</div>
    <div class="card" style="font-size:12.5px;">The codebook covers the <b>60 attributed</b> derivation units only. The
    <b>105 escape-hatch</b> units (56 indeterminate / 46 none-identified / 3 flaky-suspect) are the
    first-class <b>not-cleanly-merge-attributable</b> stratum reported in FINDINGS — no categories were invented for them.
    <label style="display:block;margin-top:8px;"><input type="checkbox" ${extra.escape_ack?"checked":""} onchange="extra.escape_ack=this.checked;save()"> I acknowledge this framing.</label></div>`;
  h+=`<div class="labels"><span style="color:var(--mut);font-size:12px;">Codebook ruling:</span>
    <button class="${extra.overall==="APPROVE"?"on on-acc":""}" onclick="setOverall('APPROVE')">APPROVE (freeze as ruled)</button>
    <button class="${extra.overall==="REVISE"?"on on-edit":""}" onclick="setOverall('REVISE')">REVISE (one Fable-5 round)</button></div>`;
  h+=`<textarea placeholder="Overall note / instructions for the freeze or revision" oninput="extra.overall_note=this.value;save()">${esc(extra.overall_note)}</textarea>`;
  h+=`<div style="margin-top:14px;display:flex;gap:8px;"><button onclick="exportJson()">Download rulings JSON</button>
    <button onclick="copyBlock()">Copy summary for Claude</button></div>`;
  h+=nav();return h;
}

function nav(){return `<div class="nav"><button onclick="go(cur-1)">&larr; Prev</button>
  <button onclick="go(cur+1)">Next &rarr;</button></div>`;}
function renderMain(){
  document.getElementById("main").innerHTML =
    cur<N?catScreen():(cur===N?mapScreen():submitScreen());
}
function render(){renderList();renderMain();}
function go(i){if(i<0||i>N+1)return;cur=i;render();document.getElementById("main").scrollTop=0;}
function setAction(v){st[cur].action=(st[cur].action===v?null:v);save();render();}
function setOverall(v){extra.overall=(extra.overall===v?null:v);save();render();}
function rulingLines(){return CATS.map((c,i)=>{const s=st[i];
  let x=`${c.id} => ${s.action||"UNRULED"}`;
  if(s.action==="RENAME"&&s.new_id)x+=` [new: ${s.new_id}]`;
  if(s.action==="MERGE"&&s.merge_target)x+=` [into: ${s.merge_target}]`;
  if(s.note)x+=` | ${s.note}`;return x;});}
function exportJson(){
  const o={meta:META,categories:CATS.map((c,i)=>({id:c.id,size:SIZES[c.id]||0,ruling:st[i]})),
    mapping_comment:extra.map_comment,four_family_comment:extra.ff_comment,
    escape_ack:extra.escape_ack,overall:extra.overall,overall_note:extra.overall_note};
  const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([JSON.stringify(o,null,2)],{type:"application/json"}));
  a.download="g2_codebook_rulings.json";a.click();}
function exportCsv(){
  const rows=[["category","size","action","new_id","merge_target","note"]].concat(
    CATS.map((c,i)=>[c.id,SIZES[c.id]||0,st[i].action||"UNRULED",st[i].new_id||"",st[i].merge_target||"",st[i].note||""]));
  const csv=rows.map(r=>r.map(x=>`"${String(x).replace(/"/g,'""')}"`).join(",")).join("\n");
  const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download="g2_codebook_rulings.csv";a.click();}
function copyBlock(){
  const nonAccept=CATS.map((c,i)=>st[i].action&&st[i].action!=="ACCEPT"?c.id+"="+st[i].action:null).filter(Boolean);
  const txt="Phase-2 codebook G2(iv) ruling (via mapping_ui.html).\n"
    +"Overall: "+(extra.overall||"UNSET")+(extra.overall_note?"  — "+extra.overall_note:"")+"\n"
    +"Escape-hatch framing acknowledged: "+(extra.escape_ack?"yes":"NO")+"\n"
    +"Non-ACCEPT categories: "+(nonAccept.join(", ")||"none")+"\n\n"
    +"Per-category rulings:\n"+rulingLines().join("\n")
    +(extra.map_comment?"\n\nMapping comment: "+extra.map_comment:"")
    +(extra.ff_comment?"\n\nFour-family comment: "+extra.ff_comment:"")
    +"\n\nNext for Claude: if APPROVE -> apply rulings, write codebook_frozen.md + fill "
    +"prompts_taxonomy/phase3_output.schema.json category enum, and make the single FREEZE COMMIT "
    +"(record in manifest). If REVISE -> one Fable-5 revision round pre-freeze.";
  navigator.clipboard.writeText(txt).then(()=>alert("Copied — paste to Claude Code."));}
document.addEventListener("keydown",e=>{if(e.target.tagName==="INPUT"||e.target.tagName==="TEXTAREA")return;
  if(e.key==="ArrowRight")go(cur+1);else if(e.key==="ArrowLeft")go(cur-1);});
render();
</script></body></html>
"""


def main() -> None:
    if not DRAFT.exists():
        sys.exit(f"no codebook draft at {DRAFT} — run tools/taxonomy_phase2.py first.")
    txt = DRAFT.read_text()
    look = derivation_lookup()
    cats = parse_categories(txt, look)
    mapping = parse_mapping(txt)
    sizes = coverage_sizes(txt)
    ff = txt.split("## 4.")[-1].split("## 5.")[0].strip()
    # strip the leading "Four-Family Assessment (...)" heading line if present.
    ff = re.sub(r"^Four-Family Assessment[^\n]*\n", "", ff).strip()

    meta = {"draft": "reports_taxonomy/phase2/codebook_draft.md",
            "n_categories": len(cats), "n_named": len([c for c in cats if c["id"] != "residual-other"]),
            "n_mapping_rows": len(mapping), "attributed_covered": sum(sizes.values())}

    def js(o):
        return json.dumps(o, separators=(",", ":")).replace("</", "<\\/")

    html = (TEMPLATE
            .replace("%%CATS%%", js(cats))
            .replace("%%MAP%%", js(mapping))
            .replace("%%SIZES%%", js(sizes))
            .replace("%%FF%%", js(ff))
            .replace("%%META%%", js(meta)))
    OUT.write_text(html)

    # sanity: every anchor + category structurally parsed
    fw = [(c["id"], a["unit_id"]) for c in cats for a in c["anchors"] if not a["in_derivation"]]
    print(f"wrote {OUT} — {len(cats)} categories, {len(mapping)} mapping rows, "
          f"{OUT.stat().st_size/1e6:.2f} MB")
    print(f"anchors NOT in derivation (firewall): {len(fw)} {fw[:5]}")
    for c in cats:
        empty = [f for f in FIELDS if not c[f]]
        flag = f"  MISSING {empty}" if empty else ""
        print(f"  {c['id']:52s} anchors={len(c['anchors'])}{flag}")


if __name__ == "__main__":
    main()
