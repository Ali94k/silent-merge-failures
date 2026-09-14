# D3 Gap Inventory — shapes the existing lanes miss (ISSUES #31, S-D1)

Source: spec-extraction batch `msgbatch_01EwsTTHk1AHnDw1b98AXwxY`
(claude-opus-4-8, structured outputs) over the **13 D3 derivation units**
(6 `stale-reference-to-removed-declaration` + 7
`stale-reference-to-renamed-or-relocated-declaration`), with lane-fire
verdicts judged against the actual code of
`semantic_merge_driver/strategies/rm2_strategies/rename_conflict.py` and
`.../joern_strategies/unresolved_reference.py` (read pre-batch, summarized
in the frozen prompt). Derivation units only (§3 firewall) — S-D4 designs
from this file + the underlying unit contents, nothing else.

**Lane-verdict totals:** rm2=yes 1, rm2=uncertain 1, both-no 11.

- `softinstigate_restheart__98dda32101` — parameter rename `request→req` /
  `response→res`: **RM2 var-lane plausibly fires** (Rename Parameter on
  (base, theirs), new names present in merged, old names referenced with
  no surviving declaration). Existing-lane coverage — NOT in the
  inventory; it is the D3 sanity anchor that the current lanes are not
  empty on this category.
- `jline_jline2__5acfe59453` — see S1b below (RM2 uncertain).

## Widening candidates (file-local reach — S-D4 targets)

### S1 — one-side-REMOVED field, other side references it: Joern's
both-parents guard self-defeats
The removing parent no longer resolves the name, so "flag only names
resolvable in BOTH parents" suppresses exactly the merge-induced case it
exists to catch; RM2 sees a removal, not a rename.
- `datastax_java-driver__e1535e89ad` — ours removed field `isShutdown`
  (replaced by `shutdownFuture`); theirs added a fresh `isShutdown.get()`.
- `yandex-qatools_postgresql-embedded__6e15a53c7e` — ours deleted field
  `processReady` (+ accessor); theirs added a write to it.

*Widening sketch:* differential rule "unresolved in merged AND resolvable
in ≥1 parent" (instead of "in neither parent's unresolved set"), guarded
to identifiers whose declaration existed in base and survives in exactly
one parent — keeps the inherited-field/same-package noise cancellation
(those are unresolved in BOTH parents) while un-suppressing the
one-side-removed shape.

### S1b — one-side-RENAMED field, same guard failure (S1 variant)
- `jline_jline2__5acfe59453` — ours renamed field
  `nonBlockingInput→in`; old name unresolved in the ours parent → Joern
  suppresses; RM2 var-lane fires ONLY IF the image classifies a plain
  field rename as `Rename Attribute` (verified limitation: it does NOT for
  static-final constants; this one is a non-final field — uncertain).
  Same ≥1-parent widening covers it regardless of RM2's behavior.

### S2 — REMOVED method still CALLED: calls are invisible to both lanes
Method calls are not identifier nodes (Joern lane scans
`cpg.identifier` only) and a removal is not a rename (RM2 reports
nothing).
- `javaparser_javaparser__dc6254f1bf` — ours removed `getWrappedNode()`;
  theirs-added method body still calls it. **File-local.**
- `jcabi_jcabi-github__b13d2596ba` — ours removed private static helper
  `milestones()`; theirs-added tests still call it. **File-local.**

*Widening sketch:* call-aware differential — unresolved-callee check
(`cpg.call` name vs methods declared/visible in file, differential
against both parents with the S1 ≥1-parent rule), or a textual
declared-method-set differential for private/static locals.

### S3 — removed inner CLASS referenced via constructor/type position
- `gwtbootstrap3_gwtbootstrap3__5c0d1eab79` — ours removed inner class
  `SubmitEvent`; theirs kept `new SubmitEvent()`. Type/constructor
  references are neither identifiers (Joern lane) nor renames (RM2).

*Widening caution:* the Stage-B "lost type resolution" lane was BUILT AND
DROPPED for javasrc2cpg nondeterminism — any S3 lane must be narrower
(e.g. `new T(` / `extends T` textual differential against the file's own
declared-type set), not a revival of the dropped lane.

## Out of file-local reach (documented misses — no S-D4 target)

### S4 — cross-file class RELOCATION breaking imports/wildcards
- `elisarver_selophane__4ecc600017` — `Select` moved to a subpackage;
  surviving wildcard import of the emptied package + ours' `Select
  option1` field no longer resolve. Declaration lives outside the unit.
- `gitools_gitools__02221bf3d8` — package move
  `org.gitools.matrix.model → org.gitools.core.matrix.model`; theirs
  added an import of the old package, kept by the merge.

### S5 — cross-file / external-library API rename or replacement
- `imixs_imixs-workflow__23b86de5b4` — javax→jakarta migration vs a
  theirs-added `javax.ejb.AccessTimeout` import+annotation.
- `openpnp_openpnp__b62c0ce826` — `CvPipeline.setCamera/setNozzle`
  replaced by `setProperty` (declared in a file outside the unit); theirs
  added a block calling the old methods.
- `qcadoo_mes__c6cb8180e5` — `DataFieldDefinition.setValidators` →
  fluent `withValidator` (declarations outside the unit); theirs added
  `setValidators(...)` call sites.

These match the Stage-B pilot's documented miss class (nysenate,
cloudfoundry): no (base, version) pair of any file in the unit shows the
declaration change, so no file-local differential can anchor it. They are
FN targets for FINDINGS/THREATS framing, not for lane widening this
cycle.

### Boundary case
- `jdeparser_jdeparser2__868afefbb4` — ours removed
  `hasStaticImport(String)` (declaration IS file-local and quoted), but
  no caller is visible in the unit (cross-file or T3-elided): a detector
  could see the removal but has no stale site to flag within the unit.

## GD1 count

Distinct concrete missed shapes with unit ids: **S1, S1b, S2, S3, S4, S5
= 6 shapes / 12 units** (≥5 required) — of which S1/S1b/S2/S3 (6 units)
are in file-local reach and become S-D4's widening targets.

## S-D4 addendum (2026-07-16) — probe correction to two lane-fire verdicts

Live-Joern probes on minimal reconstructions (S-D4 session, recorded in the
lane header of `unresolved_reference.py`) refine the S1/S1b mechanism
claims above, which the spec batch judged from the frozen lane summary:

- The existing lane's suppression key is membership in the parents'
  UNRESOLVED sets — a name **absent** from the removing parent is not in
  that set, so "resolvable in BOTH parents" was the docstring's intent, not
  the code's behavior. On the minimal datastax (S1 bare-receiver
  `isShutdown.get()`) and jline (S1b `nonBlockingInput.peek(…)`) shapes the
  **existing lane already fires** end-to-end. Those two units may therefore
  be baseline-arm catches in S-D5, not experimental-arm deltas — exactly
  what GD3's two-arm design measures.
- The probe-confirmed genuinely-Joern-invisible shapes are:
  `this.`-qualified field references (yandex — lowered to fieldIdentifier
  nodes), method calls (S2 — call nodes), and type/constructor references
  (S3) — these drove the S-D4 widening, which covers the bare-receiver
  shapes too (deterministic textual net alongside the Joern path).
- GD1's floor is unaffected (6 shapes / 12 units stands; the shape list and
  unit ids are unchanged — only the fired/not-fired attribution of two
  units is corrected).
