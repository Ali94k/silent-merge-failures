"""G3 condition 2 — Phase-3 RELIABILITY adjudication UI (ISSUES #30, S4, §7).

Builds a standalone browser UI (make_adjudication_ui.py precedent) for Ali to
rule the reliability subset:

  adjudication set = ALL pass-a/b disagreements  +  a stratified random sample of
  AGREEING units, to a total of 40-60 (proportional to the agreed primary label,
  min 3 per category where available, escape strata included).

Per unit the UI shows: the unit inputs AS THE MODEL SAW THEM (the assembled
Phase-3 USER text, byte-identical to what both passes received), both passes'
primary/secondary/confidence/evidence/notes, and the frozen category definitions
inline. Ali accepts or overrides the primary (with a written rationale).

Gate (§7.G3.2): PASS iff Ali accepts >= 75% of the sampled AGREEING units'
labels. (Disagreement rulings become final labels but do NOT count toward the
75%.) The session pauses for Ali's ruling.

All evidence precomputed + embedded; no server/network; localStorage +
CSV/clipboard export. Deterministic seeded draw recorded in adjudication_set.json.

    ../.venv/bin/python tools/taxonomy_g3_adjudication_ui.py
"""
from __future__ import annotations

import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import taxonomy_common as tc  # noqa: E402

P3 = tc.REPORTS / "phase3"
RAW_A = P3 / "raw_results_a.json"
RAW_B = P3 / "raw_results_b.json"
INPUTS = P3 / "inputs"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
CODEBOOK = tc.REPORTS / "phase2/codebook_frozen.md"
ADJ_DIR = P3 / "adjudication"
OUT_HTML = ADJ_DIR / "adjudication_ui.html"
OUT_SET = ADJ_DIR / "adjudication_set.json"

SEED = 20260711            # S4 reliability draw (documented; distinct from split seed)
TARGET_TOTAL = 50          # aim; clamped to [40, 60]
LO, HI = 40, 60
MIN_AGREE = 12             # floor on the agreeing sample so the ≥75% gate stays computable

PRIMARY_ENUM = [
    "stale-usage-of-pruned-import", "stale-reference-to-removed-declaration",
    "stale-reference-to-renamed-or-relocated-declaration", "stale-caller-of-changed-signature",
    "stale-expectation-of-changed-behavior", "overlapping-edit-interleaving",
    "insertion-anchored-to-relocated-code", "duplicate-concurrent-addition",
    "residual-other", "none-identified", "indeterminate", "flaky-suspect",
]
ESCAPE = {"none-identified", "indeterminate", "flaky-suspect"}
ESCAPE_DEFS = {
    "none-identified": "Escape hatch: examined the interaction, found no plausible merge-induced mechanism.",
    "indeterminate": "Escape hatch: a mechanism may exist but the visible evidence cannot establish it.",
    "flaky-suspect": "Escape hatch: the plausible failure is environmental/nondeterministic, not a semantic property of the merged code.",
    "residual-other": "A real, attributed two-sided mechanism that fits none of the named categories.",
}


# --------------------------------------------------------------------------- #
# Codebook §2 parser (category id -> fields).
# --------------------------------------------------------------------------- #

def parse_codebook() -> dict[str, dict]:
    txt = CODEBOOK.read_text()
    body = txt[txt.index("## 2. Categories"):txt.index("## 3.")]
    cats: dict[str, dict] = {}
    for block in body.split("\n### `")[1:]:
        cid = block[:block.index("`")]
        fields = {"id": cid}
        for key in ("name", "mechanism", "definition", "inclusion", "exclusion", "boundary"):
            m = re.search(rf"- \*\*{key}:\*\* (.+?)(?:\n- \*\*|\n---|\Z)", block, re.S)
            if m:
                fields[key] = re.sub(r"\s+", " ", m.group(1)).strip()
        cats[cid] = fields
    return cats


# --------------------------------------------------------------------------- #
# Load passes.
# --------------------------------------------------------------------------- #

def load_pass(path: Path) -> dict[str, dict]:
    raw = json.loads(path.read_text())
    return {mid: rec["parsed"] for mid, rec in raw.items()
            if rec.get("result_type") == "succeeded" and rec.get("conforms")}


def scored_meta() -> dict[str, tuple[str, str]]:
    meta = {}
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            meta[r["merge_id"]] = (r["split"], r["stratum"])
    return meta


# --------------------------------------------------------------------------- #
# Deterministic stratified sample of AGREEING units.
# --------------------------------------------------------------------------- #

def build_agree_sample(agree_by_label: dict[str, list[str]], n_disagree: int) -> dict[str, list[str]]:
    """Return {label: [sampled mids]} — proportional, min 3 where available, seeded."""
    rng = random.Random(SEED)
    labels = sorted(agree_by_label)
    sizes = {L: len(agree_by_label[L]) for L in labels}
    total_agree = sum(sizes.values())

    # agreeing budget: hit ~TARGET_TOTAL but never fewer than MIN_AGREE (so the
    # ≥75% gate is always computable), keep the grand total <= HI, never exceed supply.
    budget = max(TARGET_TOTAL - n_disagree, MIN_AGREE)
    budget = max(0, min(budget, HI - n_disagree, total_agree))

    floor = {L: min(3, sizes[L]) for L in labels}
    # If the min-3 floor alone overflows the budget, keep floors for the largest
    # categories first (coverage priority) until the budget is exhausted.
    if sum(floor.values()) > budget:
        alloc = {L: 0 for L in labels}
        left = budget
        for L in sorted(labels, key=lambda x: -sizes[x]):
            take = min(floor[L], left)
            alloc[L] = take
            left -= take
            if left <= 0:
                break
    else:
        alloc = dict(floor)
        left = budget - sum(alloc.values())
        # distribute the remainder proportional to spare capacity (largest remainder).
        spare = {L: sizes[L] - alloc[L] for L in labels}
        cap_total = sum(spare.values())
        if left > 0 and cap_total > 0:
            quota = {L: left * spare[L] / cap_total for L in labels}
            base = {L: int(quota[L]) for L in labels}
            for L in labels:
                add = min(base[L], spare[L])
                alloc[L] += add
                left -= add
            # largest fractional remainder gets the leftover seats
            rema = sorted(labels, key=lambda L: -(quota[L] - int(quota[L])))
            i = 0
            while left > 0 and any(sizes[L] - alloc[L] > 0 for L in labels):
                L = rema[i % len(rema)]
                if sizes[L] - alloc[L] > 0:
                    alloc[L] += 1
                    left -= 1
                i += 1

    sample = {}
    for L in labels:
        k = alloc[L]
        if k > 0:
            sample[L] = sorted(rng.sample(agree_by_label[L], k))
    return sample


def build_set() -> tuple[list[dict], dict]:
    A, B = load_pass(RAW_A), load_pass(RAW_B)
    meta = scored_meta()
    mids = sorted(meta)
    miss = [m for m in mids if m not in A or m not in B]
    if miss:
        sys.exit(f"ABORT: {len(miss)} units missing/non-conforming in a pass: {miss[:5]}")

    agree_by_label: dict[str, list[str]] = defaultdict(list)
    disagree = []
    for m in mids:
        la, lb = A[m]["primary"], B[m]["primary"]
        if la == lb:
            agree_by_label[la].append(m)
        else:
            disagree.append(m)

    sample = build_agree_sample(dict(agree_by_label), len(disagree))
    sampled_agree = sorted(x for v in sample.values() for x in v)

    def payload(m: str, kind: str) -> dict:
        la, lb = A[m], B[m]
        repo = m.rsplit("__", 1)[0]
        return {
            "mid": m, "repo": repo, "split": meta[m][0], "stratum": meta[m][1],
            "kind": kind,
            "agreed": la["primary"] if kind == "agree" else None,
            "a": {"primary": la["primary"], "secondary": la.get("secondary", []),
                  "confidence": la.get("confidence"), "evidence": la.get("evidence", []),
                  "notes": la.get("notes", "")},
            "b": {"primary": lb["primary"], "secondary": lb.get("secondary", []),
                  "confidence": lb.get("confidence"), "evidence": lb.get("evidence", []),
                  "notes": lb.get("notes", "")},
            "inputs": (INPUTS / f"input__{m}.txt").read_text(),
        }

    units = ([payload(m, "disagree") for m in disagree]
             + [payload(m, "agree") for m in sampled_agree])
    # disagreements first, then agreeing sample; stable by mid within group
    units.sort(key=lambda u: (u["kind"] != "disagree", u["mid"]))

    meta_out = {
        "seed": SEED, "n_scored": len(mids),
        "n_disagree": len(disagree), "n_agree_total": len(mids) - len(disagree),
        "n_agree_sampled": len(sampled_agree), "n_total": len(units),
        "target_total": TARGET_TOTAL, "bounds": [LO, HI],
        "agree_sample_by_label": {L: sample.get(L, []) for L in sorted(agree_by_label)},
        "agree_available_by_label": {L: len(v) for L, v in sorted(agree_by_label.items())},
        "disagreements": sorted(disagree),
        "gate": "Ali accepts >= 75% of the sampled AGREEING units' labels",
    }
    return units, meta_out


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>G3 reliability adjudication — ISSUES #30 Phase 3</title>
<style>
  :root{--red-bg:#fdecec;--red-tx:#8f1d1d;--grn-bg:#e9f6ec;--grn-tx:#1d5c2e;
        --amb-bg:#fdf3df;--amb-tx:#7a5410;--mut:#6b7280;--bd:#d6d3cd;
        --inf-bg:#e8f0fb;--inf-tx:#1d4f8f;--pos:#efe3fb;--posx:#5b2a86;}
  *{box-sizing:border-box}
  body{font-family:-apple-system,"Segoe UI",Roboto,sans-serif;margin:0;color:#1f2937;background:#faf9f5}
  #app{display:flex;height:100vh}
  #side{width:340px;min-width:340px;border-right:1px solid var(--bd);overflow-y:auto;background:#fff}
  #main{flex:1;overflow-y:auto;padding:16px 22px 90px}
  #head{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--bd);padding:10px 12px;z-index:5}
  #bar{height:5px;background:#eee;border-radius:3px;margin-top:6px}
  #barFill{height:5px;background:#2f6fce;border-radius:3px;width:0}
  .sideItem{padding:8px 12px;border-bottom:1px solid #eee;cursor:pointer;font-size:12.5px}
  .sideItem:hover{background:#f5f4f0}.sideItem.cur{background:var(--inf-bg)}
  .sideItem .mid{font-family:ui-monospace,Menlo,monospace;word-break:break-all}
  .sideItem .meta{color:var(--mut);font-size:11.5px;margin-top:3px;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
  .dot{width:9px;height:9px;border-radius:50%;background:#d1d5db;display:inline-block;flex:none}
  .dot.done{background:#34a35b}
  .chip{font-size:11px;padding:2px 8px;border-radius:10px;white-space:nowrap;display:inline-block}
  .c-red{background:var(--red-bg);color:var(--red-tx)}.c-grn{background:var(--grn-bg);color:var(--grn-tx)}
  .c-amb{background:var(--amb-bg);color:var(--amb-tx)}.c-inf{background:var(--inf-bg);color:var(--inf-tx)}
  .c-dis{background:#fde8cf;color:#9a4a10}.c-agr{background:#e3eef0;color:#27606b}
  button{font:inherit;font-size:12.5px;padding:5px 11px;border:1px solid var(--bd);border-radius:7px;background:#fff;cursor:pointer}
  button:hover{background:#f3f2ee}
  button.selA{border:1.5px solid var(--grn-tx);background:var(--grn-bg);color:var(--grn-tx);font-weight:600}
  h2.id{font-family:ui-monospace,Menlo,monospace;font-size:15px;margin:2px 0;word-break:break-all}
  .sub{color:var(--mut);font-size:12px;font-family:ui-monospace,Menlo,monospace;margin-bottom:8px}
  .passGrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}
  .passCard{border:1px solid var(--bd);border-radius:9px;padding:10px 12px;background:#fff}
  .passCard.agree{grid-column:1 / span 2;background:#f4faf5}
  .passHd{font-weight:600;font-size:12.5px;color:#374151;margin-bottom:6px}
  .lab{font-family:ui-monospace,Menlo,monospace;font-weight:600;font-size:13px}
  .ev{font-size:11.8px;border-left:3px solid var(--bd);padding:2px 8px;margin:5px 0;color:#333;background:#fafafa}
  .ev .src{color:var(--inf-tx);font-weight:600}
  .note{font-size:12px;color:#444;margin-top:6px;white-space:pre-wrap}
  .sec{margin:18px 0 6px;font-weight:600;font-size:13px;color:#374151;border-bottom:1px solid var(--bd);padding-bottom:4px}
  .labels{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
  .labels button{font-family:ui-monospace,Menlo,monospace;font-size:11.5px}
  .labels button.aMark{box-shadow:inset 0 -3px 0 #2f9e5a}.labels button.bMark{box-shadow:inset 0 3px 0 #b06a10}
  input[type=text]{width:100%;font:inherit;font-size:13px;padding:7px 10px;border:1px solid var(--bd);border-radius:7px}
  details{margin:8px 0}details>summary{cursor:pointer;font-size:12.5px;color:var(--inf-tx);padding:4px 0}
  pre.inputs{margin:6px 0;border:1px solid var(--bd);border-radius:8px;overflow:auto;max-height:60vh;
             font-family:ui-monospace,Menlo,monospace;font-size:11.4px;line-height:1.45;background:#fff;padding:8px 10px;white-space:pre-wrap;word-break:break-word}
  table.cb{border-collapse:collapse;font-size:11.6px;width:100%}
  table.cb td{border:1px solid var(--bd);padding:5px 8px;vertical-align:top}
  table.cb td.k{font-family:ui-monospace,Menlo,monospace;font-weight:600;white-space:nowrap;background:#fafafa}
  .nav{display:flex;gap:8px;margin-top:20px;align-items:center}
  kbd{background:#eee;border-radius:4px;padding:0 5px;font-size:11px}
  .accBtn{border:1.5px solid var(--grn-tx);background:var(--grn-bg);color:var(--grn-tx);font-weight:600}
</style></head>
<body>
<div id="app">
  <div id="side">
    <div id="head">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>G3 reliability</strong><span id="prog"></span></div>
      <div id="bar"><div id="barFill"></div></div>
      <div id="rate" style="font-size:11.5px;color:var(--mut);margin-top:5px;"></div>
      <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
        <button onclick="exportCsv()">Download CSV</button>
        <button onclick="copyBlock()">Copy rulings for Claude</button></div>
      <div style="margin-top:6px;color:var(--mut);font-size:11px;">
        <kbd>&larr;</kbd><kbd>&rarr;</kbd> nav &middot; <kbd>a</kbd> accept (agree) &middot; click a label to set final &middot; localStorage</div>
    </div>
    <div id="list"></div>
  </div>
  <div id="main"></div>
</div>
<script>
const DATA = %%DATA%%;
const CB = %%CB%%;
const ENUM = %%ENUM%%;
const ESC = %%ESC%%;
const LS = "g3-reliability-adjudication-v1";
let st = DATA.map(()=>({final:null, note:""}));
try{const s=JSON.parse(localStorage.getItem(LS)||"{}");DATA.forEach((d,i)=>{if(s[d.mid])st[i]=s[d.mid];});}catch(e){}
let cur=0;
function save(){const o={};DATA.forEach((d,i)=>o[d.mid]=st[i]);localStorage.setItem(LS,JSON.stringify(o));}
function esc(s){return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function labChip(l){const c=ESC[l]?"c-amb":"c-inf";return `<span class="chip ${c}">${l}</span>`;}
function evHtml(ev){return (ev||[]).map(e=>`<div class="ev"><span class="src">${esc(e.source)}</span> — <i>${esc(e.role)}</i><br>${esc(e.quote)}</div>`).join("")||`<div style="color:var(--mut);font-size:11.5px">(no quotes)</div>`;}

function renderList(){
  document.getElementById("list").innerHTML=DATA.map((d,i)=>{
    const s=st[i];const done=s.final!=null;
    const acc=(d.kind==="agree"&&s.final===d.agreed);
    return `<div class="sideItem ${i===cur?"cur":""}" onclick="go(${i})">
      <div class="mid">${i+1}. ${esc(d.repo)}</div>
      <div class="meta"><span class="dot ${done?"done":""}"></span>
        <span class="chip ${d.kind==="disagree"?"c-dis":"c-agr"}">${d.kind}</span>
        <span class="chip ${d.split==="heldout"?"c-inf":"c-agr"}">${d.split[0].toUpperCase()}${d.stratum}</span>
        ${d.kind==="agree"?`<span>${d.agreed}</span>`:`<span>${d.a.primary} / ${d.b.primary}</span>`}
        ${done?`<span>&rarr; <strong>${s.final}</strong>${acc?" ✓":""}</span>`:""}</div></div>`;
  }).join("");
  const n=st.filter(x=>x.final!=null).length;
  document.getElementById("prog").textContent=n+" / "+DATA.length;
  document.getElementById("barFill").style.width=Math.round(100*n/DATA.length)+"%";
  // acceptance rate on AGREE units (the gated metric)
  const ag=DATA.map((d,i)=>[d,st[i]]).filter(([d])=>d.kind==="agree");
  const ruled=ag.filter(([,s])=>s.final!=null);
  const acc=ruled.filter(([d,s])=>s.final===d.agreed).length;
  document.getElementById("rate").textContent=
    `agree accepted: ${acc}/${ruled.length} ruled (${ag.length} total)`+
    (ruled.length?` = ${(100*acc/ruled.length).toFixed(0)}%  [gate ≥75%]`:"");
}
function renderMain(){
  const d=DATA[cur],s=st[cur];
  let h=`<h2 class="id">${esc(d.repo)}</h2><div class="sub">${esc(d.mid)}</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
      <span class="chip ${d.kind==="disagree"?"c-dis":"c-agr"}">${d.kind.toUpperCase()}</span>
      <span class="chip c-inf">${d.split} / ${d.stratum}</span></div>`;

  if(d.kind==="agree"){
    h+=`<div class="passGrid"><div class="passCard agree">
      <div class="passHd">Both passes agree — proposed label</div>
      <span class="lab">${labChip(d.agreed)}</span>
      <button class="accBtn" style="margin-left:10px" onclick="acceptAgree()">&#10003; Accept</button>
      <details><summary>pass a / pass b evidence + notes</summary>
        <div class="passGrid"><div class="passCard"><div class="passHd">pass a (conf ${d.a.confidence})</div>
          sec: ${d.a.secondary.map(labChip).join(" ")||"—"}${evHtml(d.a.evidence)}<div class="note">${esc(d.a.notes)}</div></div>
        <div class="passCard"><div class="passHd">pass b (conf ${d.b.confidence})</div>
          sec: ${d.b.secondary.map(labChip).join(" ")||"—"}${evHtml(d.b.evidence)}<div class="note">${esc(d.b.notes)}</div></div></div>
      </details></div></div>`;
  }else{
    h+=`<div class="passGrid">
      <div class="passCard"><div class="passHd">pass a &mdash; ${labChip(d.a.primary)} <span style="color:var(--mut)">conf ${d.a.confidence}</span></div>
        sec: ${d.a.secondary.map(labChip).join(" ")||"—"}${evHtml(d.a.evidence)}<div class="note">${esc(d.a.notes)}</div></div>
      <div class="passCard"><div class="passHd">pass b &mdash; ${labChip(d.b.primary)} <span style="color:var(--mut)">conf ${d.b.confidence}</span></div>
        sec: ${d.b.secondary.map(labChip).join(" ")||"—"}${evHtml(d.b.evidence)}<div class="note">${esc(d.b.notes)}</div></div></div>`;
  }

  // ruling selector (all enum values; a/b marked)
  h+=`<div class="sec">Final ruling ${d.kind==="agree"?"(accept = keep proposed label; counts toward the ≥75% gate)":"(pick the correct label; not gated, becomes the final label)"}</div>`;
  h+=`<div class="labels">`+ENUM.map(l=>{
    const mk=(l===d.a.primary?"aMark ":"")+(l===d.b.primary?"bMark ":"");
    return `<button class="${mk}${s.final===l?"selA":""}" title="${esc((CB[l]&&CB[l].mechanism)||ESC[l]||"")}" onclick="setFinal('${l}')">${l}</button>`;
  }).join("")+`</div>`;
  h+=`<div style="font-size:11px;color:var(--mut)">underline-green = pass a's label · underline-amber = pass b's label</div>`;
  h+=`<input type="text" placeholder="Rationale / override note (audit trail)" value="${esc(s.note).replace(/"/g,"&quot;")}" oninput="st[${cur}].note=this.value;save()">`;

  // model-visible inputs
  h+=`<div class="sec">Unit inputs — exactly as both passes saw them</div>`;
  h+=`<details open><summary>show/hide assembled inputs (${d.inputs.length.toLocaleString()} chars)</summary>
      <pre class="inputs">${esc(d.inputs)}</pre></details>`;

  // codebook reference
  h+=`<div class="sec">Frozen codebook — category definitions</div>`;
  h+=`<details><summary>show all category definitions</summary><table class="cb">`;
  ENUM.forEach(l=>{ if(CB[l]){const c=CB[l];
    h+=`<tr><td class="k">${l}</td><td><b>${esc(c.name)}</b> — ${esc(c.mechanism)}<br>
        <i>incl:</i> ${esc(c.inclusion||"")}<br><i>excl:</i> ${esc(c.exclusion||"")}<br><i>bound:</i> ${esc(c.boundary||"")}</td></tr>`;
  } else { h+=`<tr><td class="k">${l}</td><td>${esc(ESC[l]||"")}</td></tr>`; } });
  h+=`</table></details>`;

  h+=`<div class="nav"><button onclick="go(cur-1)">&larr; Prev</button>
      <button onclick="go(cur+1)">Next &rarr;</button></div>`;
  document.getElementById("main").innerHTML=h;
}
function render(){renderList();renderMain();}
function go(i){if(i<0||i>=DATA.length)return;cur=i;render();document.getElementById("main").scrollTop=0;}
function setFinal(l){st[cur].final=(st[cur].final===l?null:l);save();render();}
function acceptAgree(){st[cur].final=DATA[cur].agreed;save();if(cur<DATA.length-1)cur++;render();}
function rows(){return DATA.map((d,i)=>({mid:d.mid,kind:d.kind,split:d.split,stratum:d.stratum,
  agreed:d.agreed||"",a:d.a.primary,b:d.b.primary,final:st[i].final||"UNREVIEWED",
  accepted:(d.kind==="agree"?(st[i].final===d.agreed?"1":"0"):""),note:st[i].note||""}));}
function exportCsv(){
  const R=rows();const cols=["mid","kind","split","stratum","agreed","a","b","final","accepted","note"];
  const csv=[cols.join(",")].concat(R.map(r=>cols.map(c=>`"${String(r[c]).replace(/"/g,'""')}"`).join(","))).join("\n");
  const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download="phase3_reliability_rulings.csv";a.click();
}
function copyBlock(){
  const R=rows();const ag=R.filter(r=>r.kind==="agree");
  const ruled=ag.filter(r=>r.final!=="UNREVIEWED");const acc=ruled.filter(r=>r.accepted==="1").length;
  const dis=R.filter(r=>r.kind==="disagree");const disRuled=dis.filter(r=>r.final!=="UNREVIEWED").length;
  const txt="G3 reliability adjudication (Phase 3, ISSUES #30).\n"+
    `Agree units accepted: ${acc}/${ruled.length} ruled of ${ag.length} sampled = `+
    (ruled.length?(100*acc/ruled.length).toFixed(1)+"%":"—")+"  [gate ≥75%]\n"+
    `Disagreements ruled: ${disRuled}/${dis.length}\n\nRulings:\n`+
    R.map(r=>`${r.mid} => ${r.final}${r.kind==="agree"&&r.accepted==="0"?" (OVERRIDE of "+r.agreed+")":""}${r.note?" | "+r.note:""}`).join("\n")+
    "\n\nPlease fold into labels_final.csv (agree keep/override, disagree=this ruling), report the override rate, and compute FINDINGS base rates.";
  navigator.clipboard.writeText(txt).then(()=>alert("Copied — paste to Claude Code."));
}
document.addEventListener("keydown",e=>{if(e.target.tagName==="INPUT")return;
  if(e.key==="ArrowRight")go(cur+1);else if(e.key==="ArrowLeft")go(cur-1);
  else if(e.key==="a"&&DATA[cur].kind==="agree")acceptAgree();});
render();
</script></body></html>
"""


def main() -> None:
    ADJ_DIR.mkdir(parents=True, exist_ok=True)
    units, meta = build_set()
    cb = parse_codebook()
    OUT_SET.write_text(json.dumps({"meta": meta,
                                   "units": [{k: u[k] for k in ("mid", "kind", "split", "stratum",
                                              "agreed") if k in u} | {"a": u["a"]["primary"],
                                              "b": u["b"]["primary"]} for u in units]}, indent=2))
    html = (TEMPLATE
            .replace("%%DATA%%", json.dumps(units, separators=(",", ":")).replace("</", "<\\/"))
            .replace("%%CB%%", json.dumps(cb, separators=(",", ":")).replace("</", "<\\/"))
            .replace("%%ENUM%%", json.dumps(PRIMARY_ENUM))
            .replace("%%ESC%%", json.dumps(ESCAPE_DEFS)))
    OUT_HTML.write_text(html)
    print(f"adjudication set: {meta['n_total']} units "
          f"({meta['n_disagree']} disagreements + {meta['n_agree_sampled']} agreeing sample; "
          f"seed {SEED})")
    print(f"agree sample by label: "
          + ", ".join(f"{L}={len(v)}" for L, v in meta['agree_sample_by_label'].items() if v))
    print(f"wrote {OUT_HTML.relative_to(ROOT)} ({OUT_HTML.stat().st_size/1e6:.1f} MB)")
    print(f"wrote {OUT_SET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
