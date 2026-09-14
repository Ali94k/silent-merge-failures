# S-D7 control-flag package for Ali — 2 experimental-arm flags on the Stage-C 193 controls

Per the S-D7 kickoff: flags on the 193 controls **gate NOTHING automatically**;
each goes to Ali with a package. Rulings requested: CAUSAL-FP vs
INCIDENTAL-BUT-TRUE (S-D6 GD3 convention — rulings judge the merged artifact
actually scored). Baseline arm flagged **0/193** (reproducing the frozen
post-fix Stage-C R1 = 0/193 exactly; known-answer gate PASS 2215/2215
file×lane verdicts).

Never-blend note: these are Stage-C-instrument controls (the ORIGINAL 193) —
disjoint from the S-D5 tune/eval-control/spgroup pools; the S-D5 zero-FP
record (0 adjudicated FPs / 363 controls) is a separate instrument and is
not modified by anything here.

---

## Flag 1 — `jgralab_jgralab__d631209030` · D1 `ImportPruneUsage` · FunLib.java

**Lane evidence (execution-verified):** `import java.io.IOException;` present
in base and ours, pruned in theirs; the mergiraf-0.17.0-reproduced merged
file has **no covering import** while keeping **9 bare `IOException` uses**
(first flagged use L371). JLS 6.5.5: unresolvable simple type name — the
scored merged file is uncompilable. The breakage is merge-induced
(each parent resolves all its own uses).

**Developer resolution (shipped in the scenario):** also drops the import but
has **0 bare `IOException` uses** — the developer refactored the uses away.
`merged != developer_resolution`.

**Reading:** real breakage in the 0.17.0-reproduced merge; the control's
`Tests_passed` label describes the DATASET's mergiraf output — the
mergiraf-version-skew class. This is the same repo and the same defect shape
as the S-D5 GD3 flag `jgralab_jgralab__d1a767cb2d` (different merge), which
Ali ruled **INCIDENTAL-BUT-TRUE** on 2026-07-20. Drafted ruling:
same class, same reasoning — but the ruling is Ali's.

---

## Flag 2 — `yubico_ykneo-openpgp__2766bd7444` · D2 `SignatureStaleCall` · OpenPGPAppletTest.java

**This is D2's first flag on real data anywhere** (held-out: 0 flags,
file-local ceiling; tune/eval controls: 0).

**Lane evidence (execution-verified, full D2 chain):**
- base + theirs declare `private boolean doVerify(String pin, byte mode)` (arity 2);
- ours changes it to `private void doVerify(String pin, byte mode, State state)`
  (arity 3) — RM2 `Add Parameter` on (base, ours), exactly one (old,new) pair,
  none on theirs; no varargs; ours' own call sites all updated (X
  self-consistency guard);
- theirs adds test cases calling the OLD 2-arg form
  (`assertEquals(true, doVerify("123456", (byte) 0x82));` — Y attribution);
- the merged file declares **only** the 3-arity version (L328, no overload)
  while keeping **12 two-arg call sites**
  (L171–L251) → no applicable method (JLS 15.12.2); also `void` inside
  `assertEquals` — doubly uncompilable.

**Developer resolution:** `merged == developer_resolution` **byte-identical**
— the developer's own shipped merge carries all 12 stale calls (the jOOQ
class).

**Real-repo probe (github.com/Yubico/ykneo-openpgp):** merge commit
`2766bd74444ce9…` exists upstream with the 12 stale calls; its **immediate
descendant** (`git rev-list --count` = 1) is
`de02622` — **"Fix tests for PDOs"** (Alessio Di Mauro, 2017-01-10) — whose
diff converts exactly the flagged calls:
`- assertEquals(true, doVerify("12345678", (byte) 0x83));`
`+ doVerify("12345678", (byte) 0x83, State.GOOD);`
The developer confirmed and repaired precisely the breakage D2 flagged, one
commit later.

**Reading:** true stale-caller-of-changed-signature breakage in the shipped
merge; the `Tests_passed` label most plausibly reflects a build that does not
compile/run this applet test path (label-construct blind spot, as with jOOQ's
behavioral-interference construct). Drafted ruling: INCIDENTAL-BUT-TRUE with
developer confirmation — doubles as external validation of D2's evidence
chain. Ruling is Ali's.

---

## Bookkeeping

- Both flags are experimental-arm only; baseline = 0/193 (frozen R1 reproduced).
- If either flag is ruled a genuine DETECTOR-FP, the S-D5 freeze discipline
  applies to any lane change (dated §12 amendment + full S-D5 rerun); the
  S-D7 rerun itself would then also need re-running.
- Machine numbers already reported in `summary.txt` / FINDINGS addendum are
  labeled as machine flags with rulings PENDING-ALI.

---

# RULINGS — Ali, 2026-07-22 (both flags)

**Flag 1 `jgralab_jgralab__d631209030` (D1): INCIDENTAL-BUT-TRUE.** Ruled
after an explicit FP challenge by Ali, resolved against the four-version
differential (ours: import + 11 uses; theirs: no import + 0 uses;
mergiraf-0.17.0 merged: no import + 9 uses — uncompilable, JLS 6.5.5;
developer: no import + 0 uses). The detector's claim is true of the scored
artifact; the `Tests_passed` control label describes the dataset-mergiraf
output, not this reproduction — the mergiraf-version-skew class, same
ruling as S-D5's `jgralab_jgralab__d1a767cb2d`.

**Flag 2 `yubico_ykneo-openpgp__2766bd7444` (D2): INCIDENTAL-BUT-TRUE
(developer-confirmed).** The merged file is byte-identical to the shipped
developer resolution; 12 two-arg `doVerify` calls against the sole 3-arity
declaration; the immediate next upstream commit `de02622` "Fix tests for
PDOs" converts exactly the flagged calls. External validation of D2's
evidence chain — its first real-data catch. The label construct does not
exercise this test path.

**Consequence:** no amendment, no rerun — the §3 freeze stands. Instrument
record: **0 adjudicated false positives on the 193 Stage-C controls**
(2 machine flags, both ruled true breakage outside the label construct).
This statement is per-instrument; it is NOT summed with the S-D5 zero-FP
record (separate instrument, never blend).
