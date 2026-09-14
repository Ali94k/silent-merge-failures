"""G1 spot-check UI generator (ISSUES #30, S2, protocol §7 condition iii).

Ali's ruling: a stratified draw of 15 Phase-1 drafts (5 high / 5 medium /
5 low-or-escape confidence) rendered in a standalone, no-server review UI in
the make_adjudication_ui.py style. Per draft the reviewer sees:

  * the unit's inputs EXACTLY as the model saw them (the assembled prompt text,
    phase1/inputs/input__<mid>.txt),
  * the model's structured output — per-side changes, interaction point,
    mechanism summary + tags + counterfactual, evidence quotes, verdict,
    confidence, notes,
  * a client-side check of whether each evidence quote is a VERBATIM substring
    of the input (directly supports the "unsupported-by-quotes" judgment),
  * accept / reject-hallucinated / reject-unsupported controls + a reason box.

Pass (protocol §7): <= 3/15 rejected as hallucinated or unsupported-by-quotes.

Deterministic draw (seed recorded). Output:
  reports_taxonomy/phase1/spotcheck/spotcheck_ui.html
  reports_taxonomy/phase1/spotcheck/spotcheck_draw.json   (the 15 mids + seed)

    ../.venv/bin/python tools/taxonomy_spotcheck_ui.py
"""
from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import taxonomy_common as tc  # noqa: E402

P1_DIR = tc.REPORTS / "phase1"
RAW = P1_DIR / "raw_results.json"
INPUTS_DIR = P1_DIR / "inputs"
SPLIT_CSV = tc.REPORTS / "split_assignment.csv"
OUT_DIR = P1_DIR / "spotcheck"

ESCAPE = ("none-identified", "indeterminate", "flaky-suspect")
SEED = 20260709          # protocol split seed, reused for the spot-check draw
PER_BUCKET = 5
BUCKETS = ("high", "medium", "low_or_escape")


def bucket_of(obj: dict) -> str:
    if obj["verdict"] in ESCAPE or obj["confidence"] == "low":
        return "low_or_escape"
    return obj["confidence"]          # 'high' or 'medium' (attributed units)


def load_conforming() -> dict[str, dict]:
    raw = json.loads(RAW.read_text())
    split = {}
    with open(SPLIT_CSV) as fh:
        for r in csv.DictReader(fh):
            split[r["merge_id"]] = (r["split"], r["stratum"])
    out = {}
    for mid, rec in raw.items():
        if split.get(mid, (None,))[0] != "derivation":
            continue
        if rec.get("result_type") == "succeeded" and rec.get("conforms"):
            out[mid] = {"rec": rec, "stratum": split[mid][1]}
    return out


def draw(units: dict[str, dict]) -> tuple[list[str], dict]:
    """Seeded stratified draw: 5 per bucket, topped up from other buckets to 15."""
    rng = random.Random(SEED)
    by_bucket: dict[str, list[str]] = {b: [] for b in BUCKETS}
    for mid, u in units.items():
        by_bucket[bucket_of(u["rec"]["parsed"])].append(mid)
    for b in BUCKETS:
        by_bucket[b].sort()
        rng.shuffle(by_bucket[b])

    picked: list[str] = []
    per_bucket_taken = {}
    for b in BUCKETS:
        take = by_bucket[b][:PER_BUCKET]
        per_bucket_taken[b] = len(take)
        picked.extend(take)

    # top-up to 15 from any remaining, preserving determinism.
    if len(picked) < PER_BUCKET * len(BUCKETS):
        pool = [m for b in BUCKETS for m in by_bucket[b][PER_BUCKET:]]
        pool.sort()
        rng.shuffle(pool)
        for m in pool:
            if len(picked) >= PER_BUCKET * len(BUCKETS):
                break
            picked.append(m)

    meta = {
        "seed": SEED,
        "per_bucket_target": PER_BUCKET,
        "bucket_population": {b: len(by_bucket[b]) for b in BUCKETS},
        "bucket_taken": per_bucket_taken,
        "n_drawn": len(picked),
        "bucket_definition": "low_or_escape = verdict in {none-identified, indeterminate, "
                             "flaky-suspect} OR confidence == low; else confidence bucket.",
    }
    return picked, meta


def build(units: dict[str, dict], picked: list[str]) -> list[dict]:
    data = []
    for mid in picked:
        u = units[mid]
        rec = u["rec"]
        obj = rec["parsed"]
        input_text = (INPUTS_DIR / f"input__{mid}.txt").read_text()
        data.append({
            "mid": mid,
            "stratum": u["stratum"],
            "level": rec.get("level", "?"),
            "bucket": bucket_of(obj),
            "verdict": obj["verdict"],
            "confidence": obj["confidence"],
            "per_side": obj["per_side_changes"],
            "interaction_point": obj.get("interaction_point", ""),
            "mechanism": obj["mechanism"],
            "evidence": obj.get("evidence", []),
            "notes": obj.get("notes", ""),
            "usage": rec.get("usage", {}),
            "input": input_text,
        })
    return data


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Phase-1 spot-check — ISSUES #30 G1(iii)</title>
<style>
  :root { --red-bg:#fdecec; --red-tx:#8f1d1d; --grn-bg:#e9f6ec; --grn-tx:#1d5c2e;
          --amb-bg:#fdf3df; --amb-tx:#7a5410; --mut:#6b7280; --bd:#d6d3cd;
          --info-bg:#e8f0fb; --info-tx:#1d4f8f; --hl:#fff3cd; }
  * { box-sizing:border-box; }
  body { font-family:-apple-system,"Segoe UI",Roboto,sans-serif; margin:0;
         color:#1f2937; background:#faf9f5; }
  #app { display:flex; height:100vh; }
  #side { width:300px; min-width:300px; border-right:1px solid var(--bd);
          overflow-y:auto; background:#fff; }
  #main { flex:1; overflow-y:auto; padding:16px 22px 90px; }
  #head { position:sticky; top:0; background:#fff; border-bottom:1px solid var(--bd);
          padding:10px 12px; z-index:5; font-size:13px; }
  #bar { height:5px; background:#eee; border-radius:3px; margin-top:6px; }
  #barFill { height:5px; background:#2f6fce; border-radius:3px; width:0; }
  .sideItem { padding:8px 12px; border-bottom:1px solid #eee; cursor:pointer; font-size:12.5px; }
  .sideItem:hover { background:#f5f4f0; }
  .sideItem.cur { background:var(--info-bg); }
  .sideItem .mid { font-family:ui-monospace,Menlo,monospace; word-break:break-all; }
  .sideItem .meta { color:var(--mut); font-size:11.5px; margin-top:3px;
                    display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
  .dot { width:9px; height:9px; border-radius:50%; background:#d1d5db; display:inline-block; flex:none; }
  .dot.done { background:#34a35b; }
  .chip { font-size:11px; padding:2px 8px; border-radius:10px; white-space:nowrap; display:inline-block; }
  .c-red { background:var(--red-bg); color:var(--red-tx); }
  .c-grn { background:var(--grn-bg); color:var(--grn-tx); }
  .c-amb { background:var(--amb-bg); color:var(--amb-tx); }
  .c-inf { background:var(--info-bg); color:var(--info-tx); }
  .c-att { background:#efe3fb; color:#5b2a86; }
  button { font:inherit; font-size:12.5px; padding:5px 11px; border:1px solid var(--bd);
           border-radius:7px; background:#fff; cursor:pointer; }
  button:hover { background:#f3f2ee; }
  button.sel-acc { border:1.5px solid var(--grn-tx); background:var(--grn-bg); color:var(--grn-tx); font-weight:600; }
  button.sel-hal { border:1.5px solid var(--red-tx); background:var(--red-bg); color:var(--red-tx); font-weight:600; }
  button.sel-uns { border:1.5px solid var(--amb-tx); background:var(--amb-bg); color:var(--amb-tx); font-weight:600; }
  h2.id { font-family:ui-monospace,Menlo,monospace; font-size:15px; margin:2px 0; word-break:break-all; }
  .sec { margin:18px 0 6px; font-weight:600; font-size:13px; color:#374151;
         border-bottom:1px solid var(--bd); padding-bottom:4px; }
  .card { border:1px solid var(--bd); border-radius:9px; padding:10px 13px; margin:8px 0; background:#fff; }
  .kv { display:flex; gap:8px; margin:4px 0; font-size:13px; }
  .kv .k { color:var(--mut); min-width:120px; font-weight:600; }
  .tag { font-family:ui-monospace,Menlo,monospace; font-size:12px; background:#eef; color:#3b3b8f;
         padding:2px 7px; border-radius:6px; margin:0 4px 4px 0; display:inline-block; }
  .quote { border:1px solid var(--bd); border-radius:8px; padding:8px 10px; margin:8px 0; background:#fff; }
  .quote .src { font-size:11px; color:var(--mut); font-weight:600; text-transform:uppercase; }
  .quote pre { margin:5px 0; font-family:ui-monospace,Menlo,monospace; font-size:12px;
               white-space:pre-wrap; word-break:break-word; background:#faf9f5; padding:6px 8px;
               border-radius:6px; border-left:3px solid var(--bd); }
  .quote .role { font-size:12px; color:#374151; }
  .vbadge { font-size:11px; padding:2px 8px; border-radius:10px; font-weight:600; }
  .vbadge.ok { background:var(--grn-bg); color:var(--grn-tx); }
  .vbadge.soft { background:#edf6ef; color:var(--grn-tx); }
  .vbadge.mid { background:var(--amb-bg); color:var(--amb-tx); }
  .vbadge.no { background:var(--red-bg); color:var(--red-tx); }
  .labels { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0 6px; align-items:center; }
  input[type=text] { width:100%; font:inherit; font-size:13px; padding:7px 10px;
                     border:1px solid var(--bd); border-radius:7px; }
  details > summary { cursor:pointer; font-size:12.5px; color:var(--info-tx); padding:5px 0; }
  pre.input { border:1px solid var(--bd); border-radius:8px; overflow:auto; max-height:640px;
              font-family:ui-monospace,Menlo,monospace; font-size:11.5px; line-height:1.45;
              background:#fff; padding:10px 12px; white-space:pre; }
  .nav { display:flex; gap:8px; margin-top:20px; align-items:center; }
  kbd { background:#eee; border-radius:4px; padding:0 5px; font-size:11px; }
  .warn { background:#fff7e6; color:#8a5a00; border:1px solid #f0c674; border-radius:8px;
          padding:8px 11px; margin:8px 0; font-size:12.5px; }
</style>
</head>
<body>
<div id="app">
  <div id="side">
    <div id="head">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>Phase-1 spot-check</strong><span id="prog"></span>
      </div>
      <div id="bar"><div id="barFill"></div></div>
      <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
        <button onclick="exportCsv()">Download CSV</button>
        <button onclick="copyBlock()">Copy result for Claude</button>
      </div>
      <div style="margin-top:6px;color:var(--mut);font-size:11px;">
        <kbd>&larr;</kbd><kbd>&rarr;</kbd> nav &middot; <kbd>1</kbd>accept <kbd>2</kbd>halluc <kbd>3</kbd>unsupported &middot; saved to localStorage
      </div>
      <div style="margin-top:6px;color:var(--mut);font-size:11px;">
        Reject only if the mechanism is <b>hallucinated</b> or <b>unsupported by its quotes</b>.
        Pass = &le; 3 / 15 rejected.
      </div>
    </div>
    <div id="list"></div>
  </div>
  <div id="main"></div>
</div>
<script>
const DATA = %%DATA%%;
const LABELS = [["ACCEPT","sel-acc","1"],["REJECT-HALLUCINATED","sel-hal","2"],["REJECT-UNSUPPORTED","sel-uns","3"]];
const LS = "phase1-spotcheck-v1";
let st = DATA.map(()=>({label:null, note:""}));
try { const s=JSON.parse(localStorage.getItem(LS)||"{}"); DATA.forEach((d,i)=>{ if(s[d.mid]) st[i]=s[d.mid]; }); } catch(e){}
let cur = 0;
function save(){ const o={}; DATA.forEach((d,i)=>o[d.mid]=st[i]); localStorage.setItem(LS, JSON.stringify(o)); }
function esc(s){ return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function norm(s){ return String(s||"").replace(/\s+/g," ").trim(); }
function degut(t){ return String(t||"").split("\n").map(l=>l.replace(/^[+\- ]\s*/,"")).join("\n"); }
// Graded verbatim check. A quote copied from a unified diff often drops the
// +/- gutter or reflows indentation, and a multi-line quote may concatenate
// non-adjacent diff lines; none of those make it "unsupported". Only 'absent'
// (content genuinely not present) is grounds for REJECT-UNSUPPORTED.
function grade(text, q){
  if(!q) return "empty";
  if(text.indexOf(q)>=0) return "exact";
  if(norm(text).indexOf(norm(q))>=0) return "ws";
  const nt = norm(degut(text));
  if(nt.indexOf(norm(degut(q)))>=0) return "gutter";
  const ql = q.split("\n").map(l=>norm(degut(l))).filter(Boolean);
  if(ql.length && ql.every(l=>nt.indexOf(l)>=0)) return "perline";
  if(ql.length){ const hit=ql.filter(l=>nt.indexOf(l)>=0).length;
    if(hit>=Math.max(1,Math.ceil(ql.length/2))) return "partial"; }
  return "absent";
}
const GBADGE = {
  exact:  ["ok",  "&#10003; verbatim in input"],
  ws:     ["soft","&#10003; sourced (whitespace-normalized)"],
  gutter: ["soft","&#10003; sourced (diff-gutter/whitespace-normalized)"],
  perline:["soft","&#10003; sourced (lines present; non-contiguous in diff)"],
  partial:["mid", "~ partially present &mdash; inspect"],
  absent: ["no",  "&#10007; not found &mdash; inspect for paraphrase"],
  empty:  ["mid", "(no quote text)"],
};
function vChip(v){ return v==="attributed"?"c-att":(v==="flaky-suspect"?"c-amb":"c-inf"); }

function renderList(){
  document.getElementById("list").innerHTML = DATA.map((d,i)=>{
    const s=st[i];
    return `<div class="sideItem ${i===cur?"cur":""}" onclick="go(${i})">
      <div class="mid">${i+1}. ${esc(d.mid.split("__")[0])}</div>
      <div class="meta"><span class="dot ${s.label?"done":""}"></span>
        <span class="chip c-inf">${d.bucket}</span>
        <span class="chip ${vChip(d.verdict)}">${d.verdict}</span>
        ${s.label?`<span>&rarr; <strong>${s.label==="ACCEPT"?"acc":"REJ"}</strong></span>`:""}</div></div>`;
  }).join("");
  const n=st.filter(x=>x.label).length;
  const rej=st.filter(x=>x.label&&x.label!=="ACCEPT").length;
  document.getElementById("prog").textContent=n+" / "+DATA.length+(n?`  (rej ${rej})`:"");
  document.getElementById("barFill").style.width=Math.round(100*n/DATA.length)+"%";
}
function renderMain(){
  const d=DATA[cur], s=st[cur], m=d.mechanism;
  let h=`<h2 class="id">${esc(d.mid)}</h2>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin:6px 0;">
      <span class="chip c-inf">bucket: ${d.bucket}</span>
      <span class="chip ${vChip(d.verdict)}">verdict: ${d.verdict}</span>
      <span class="chip c-amb">confidence: ${d.confidence}</span>
      <span class="chip c-inf">stratum ${d.stratum}</span>
      <span class="chip c-inf">trunc ${esc(d.level)}</span></div>`;

  h+=`<div class="labels"><span style="color:var(--mut);font-size:12px;">Ruling:</span>`+
     LABELS.map(([v,cls,k])=>`<button class="${s.label===v?cls:""}" onclick="setLabel('${v}')">${v} <span style="opacity:.5">[${k}]</span></button>`).join("")+`</div>`;
  h+=`<input type="text" placeholder="Reason (required for a reject; recorded as audit trail)" value="${esc(s.note||"").replace(/"/g,"&quot;")}" oninput="st[${cur}].note=this.value;save()">`;

  // model output
  h+=`<div class="sec">Model output</div>`;
  h+=`<div class="card"><div class="kv"><span class="k">ours changed</span><span>${esc(d.per_side.ours)}</span></div>
      <div class="kv"><span class="k">theirs changed</span><span>${esc(d.per_side.theirs)}</span></div>
      <div class="kv"><span class="k">interaction pt</span><span>${esc(d.interaction_point)||"<i>(none)</i>"}</span></div></div>`;
  h+=`<div class="card"><div class="kv"><span class="k">mechanism</span><span>${esc(m.summary)||"<i>(empty — escape hatch)</i>"}</span></div>
      <div class="kv"><span class="k">counterfactual</span><span>${esc(m.counterfactual)||"<i>(empty)</i>"}</span></div>
      <div class="kv"><span class="k">merge-induced</span><span>${esc(m.merge_induced)}</span></div>
      <div class="kv"><span class="k">tags</span><span>${(m.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join("")||"<i>(none)</i>"}</span></div></div>`;
  if(d.notes) h+=`<div class="card"><div class="kv"><span class="k">notes</span><span>${esc(d.notes)}</span></div></div>`;

  // evidence + graded verbatim check
  h+=`<div class="sec">Evidence quotes &mdash; sourced in the model's input? (${d.evidence.length})</div>`;
  const grades = d.evidence.map(e=>grade(d.input, e.quote));
  const hard = grades.filter(g=>g==="absent").length;
  const softc = grades.filter(g=>["ws","gutter","perline","partial"].includes(g)).length;
  const attributed = d.verdict==="attributed";
  if(attributed && d.evidence.length<2)
    h+=`<div class="warn">&#9888; R4 requires &ge; 2 quotes for an attributed verdict; only ${d.evidence.length} present.</div>`;
  if(hard) h+=`<div class="warn">&#9888; ${hard} of ${d.evidence.length} quote(s) NOT found in the input even after diff-gutter/whitespace normalization. Inspect &mdash; a fabricated quote is grounds for REJECT-UNSUPPORTED.</div>`;
  else if(softc) h+=`<div style="color:var(--mut);font-size:12px;margin:4px 0;">All quotes are sourced; ${softc} matched only after normalizing diff-gutter/whitespace or across non-contiguous lines (green = content present, not a paraphrase).</div>`;
  if(!d.evidence.length) h+=`<div style="color:var(--mut);font-size:12.5px;">(no quotes supplied)</div>`;
  d.evidence.forEach((e,ei)=>{
    const [cls,lbl]=GBADGE[grades[ei]]||GBADGE.absent;
    h+=`<div class="quote"><div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
        <span class="src">${esc(e.source)}</span>
        <span class="vbadge ${cls}">${lbl}</span></div>
        <pre>${esc(e.quote)}</pre>
        <div class="role"><b>role:</b> ${esc(e.role)}</div></div>`;
  });

  // the model's exact input
  h+=`<div class="sec">The unit's input &mdash; exactly as the model saw it</div>`;
  h+=`<div style="color:var(--mut);font-size:12px;margin-bottom:4px;">tokens: in=${d.usage.input||"?"} out=${d.usage.output||"?"} &middot; use browser Find (&#8984;F) to check quotes.</div>`;
  h+=`<details><summary>Show / hide full input (${(d.input.length/1000).toFixed(0)}k chars)</summary><pre class="input">${esc(d.input)}</pre></details>`;

  h+=`<div class="nav"><button onclick="go(cur-1)">&larr; Prev</button>
      <button onclick="go(cur+1)">Next &rarr;</button>
      <span style="color:var(--mut);font-size:12px;" id="tally"></span></div>`;
  document.getElementById("main").innerHTML=h;
  const t={}; st.forEach(x=>{ if(x.label) t[x.label]=(t[x.label]||0)+1; });
  document.getElementById("tally").textContent=Object.entries(t).map(([k,v])=>k+": "+v).join("   ");
}
function render(){ renderList(); renderMain(); }
function go(i){ if(i<0||i>=DATA.length) return; cur=i; render(); document.getElementById("main").scrollTop=0; }
function setLabel(v){ st[cur].label=(st[cur].label===v?null:v); save(); render(); }
function lines(){ return DATA.map((d,i)=>`${d.mid} => ${st[i].label||"UNREVIEWED"}${st[i].note?" | "+st[i].note:""}`); }
function exportCsv(){
  const rows=[["merge_id","bucket","verdict","confidence","ruling","reason"]].concat(
    DATA.map((d,i)=>[d.mid,d.bucket,d.verdict,d.confidence,st[i].label||"UNREVIEWED",st[i].note||""]));
  const csv=rows.map(r=>r.map(c=>`"${String(c).replace(/"/g,'""')}"`).join(",")).join("\n");
  const a=document.createElement("a"); a.href=URL.createObjectURL(new Blob([csv],{type:"text/csv"}));
  a.download="spotcheck_rulings.csv"; a.click();
}
function copyBlock(){
  const n=st.filter(x=>x.label).length;
  const rej=st.filter(x=>x.label&&x.label!=="ACCEPT").length;
  const verdict = rej<=3 ? "PASS" : "FAIL";
  const txt="Phase-1 G1 spot-check complete ("+n+"/"+DATA.length+" ruled via spotcheck_ui.html).\n"
    +"Rejected (hallucinated or unsupported): "+rej+" / "+DATA.length+"  ->  condition (iii) "+verdict
    +" (pass = <= 3 rejected).\n\nRulings:\n"+lines().join("\n")
    +"\n\nPlease record the G1(iii) verdict in manifest.json + ISSUES #30 S2 summary. "
    +(verdict==="PASS"?"If (i) and (ii) also passed, G1 PASSES; hand off to S3 (Phase 2)."
                      :"Condition (iii) FAILED -> prompt revision + full Phase-1 rerun via a dated §12 amendment.");
  navigator.clipboard.writeText(txt).then(()=>alert("Copied — paste it to Claude Code."));
}
document.addEventListener("keydown", e=>{
  if(e.target.tagName==="INPUT") return;
  if(e.key==="ArrowRight") go(cur+1);
  else if(e.key==="ArrowLeft") go(cur-1);
  else if(e.key==="1") setLabel("ACCEPT");
  else if(e.key==="2") setLabel("REJECT-HALLUCINATED");
  else if(e.key==="3") setLabel("REJECT-UNSUPPORTED");
});
render();
</script>
</body>
</html>
"""


def main() -> None:
    if not RAW.exists():
        sys.exit(f"no raw results at {RAW} — run tools/taxonomy_phase1.py first.")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    units = load_conforming()
    picked, meta = draw(units)
    data = build(units, picked)

    js = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    out = OUT_DIR / "spotcheck_ui.html"
    out.write_text(TEMPLATE.replace("%%DATA%%", js))
    (OUT_DIR / "spotcheck_draw.json").write_text(json.dumps(
        {**meta, "drawn": [{"mid": d["mid"], "bucket": d["bucket"], "verdict": d["verdict"],
                            "confidence": d["confidence"], "stratum": d["stratum"]} for d in data]},
        indent=2))

    print(f"wrote {out} — {len(data)} drafts, {out.stat().st_size/1e6:.2f} MB")
    print("draw meta:", json.dumps(meta, indent=2))
    for d in data:
        print(f"  [{d['bucket']:14s}] {d['verdict']:15s} conf={d['confidence']:6s} "
              f"str{d['stratum']} {d['mid']}")


if __name__ == "__main__":
    main()
