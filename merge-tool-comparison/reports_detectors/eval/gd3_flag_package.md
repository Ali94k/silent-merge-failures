# GD3 control-flag package — Ali's adjudication required (plan §5 GD3, ISSUES #31 S-D5)

**Status: the S-D5 battery is COMPLETE and both zero-FP gates FAILED by one flag each.**
Per the frozen plan (§5 GD3) and the S-D5 kickoff prompt, any eval-control or
spgroup flag stops the session for your adjudication: *"genuine FP ⇒ dated
amendment (fix or disable the lane) + full S-D5 rerun; incidental-but-true
finding ⇒ recorded, gate re-judged by Ali."* Nothing below pre-judges the
ruling; the ANALYSIS sections are technical findings, execution-verified.

Both flags come from the same lane — **D1 `ImportPruneUsage`** — in the
experimental arm (baseline arm: zero flags anywhere). Machine numbers, all
populations, are in `summary.txt`; per-unit rows in `units_*.csv`; verbatim
lane output in `flags.json`; raw caches in `eval_cache_*.json`.

---

## Flag 1 — GD3(ii), eval-control `jgralab_jgralab__d1a767cb2d`

**Unit provenance:** eval-controls primary #83, stratum ≤3 (2 files
materialized), drawn S-D1 (SEED_EVAL=20260716) from the `semantic_ctl` pool —
Schesch reaper rows with **mergiraf == Tests_passed**. Never seen before this
session (contents materialized on-instance 2026-07-16, after the suite freeze).

**Lane evidence (verbatim):**
> `[ImportPruneUsage::flag1] L371: Stale usage of pruned import: merged file
> uses 'IOException' (line 371) but the import that provided it was pruned in
> the merge — 'import java.io.IOException;' survives in ours and is absent
> from the merged result, which retains no import covering the name.`

**Execution-verified facts** (file `src/de/uni_koblenz/jgralab/greql2/funlib/FunLib.java`):

| version | `IOException` occurrences | `import java.io.IOException;` |
|---|---|---|
| base | 3 | yes |
| ours | 12 | yes |
| theirs | 0 | **no** (side removed the import AND every use) |
| **merged (mergiraf 0.17.0)** | **9** | **no** |
| developer resolution | 0 | no (developer took theirs' shape) |

- The merged file's full import block contains no `java.io.IOException`, no
  `java.io.*` (verified line-by-line).
- All 9 merged sites are type positions (`throws IOException` ×9, incl.
  `main`). `public class FunLib` — no extends clause, no in-file
  `IOException` declaration, package `de.uni_koblenz.jgralab.greql2.funlib`.
  Under JLS 6.5.5 the simple name cannot resolve ⇒ **the mergiraf-reproduced
  merged file does not compile.**

**ANALYSIS (not a ruling):** this is textually a true finding on the artifact
analyzed — the exact ours-keeps-uses / theirs-prunes-import interaction D1
was built for, produced here by `merge-tools/mergiraf:0.17.0` on a real
merge. The unit sits in the *control* pool because the Schesch table's
`mergiraf == Tests_passed` column was computed with the dataset's mergiraf
(0.4.x era — the version divergence CLAUDE.md already records for the 0.17.0
pin). The control premise ("mergiraf merges this cleanly and tests pass")
evidently does not transfer to 0.17.0 for this unit: the flag exposes a
mergiraf-version skew in the pool criterion, not an over-eager guard. Note
the scale: 196 of 197 scored eval-controls produced zero flags; the
development-side record (100 tune-controls, same pool, same criterion)
was also zero.

**Ruling options (plan §5):**
- `DETECTOR-FP` ⇒ dated §12 amendment (fix or disable D1) + **full S-D5 rerun**.
- `INCIDENTAL-BUT-TRUE` (real breakage in the reproduced merge; control
  label an artifact of the version skew) ⇒ recorded; you re-judge GD3(ii)
  with the flag explained; no rerun mandated by the plan.

---

## Flag 2 — GD3(iii), spgroup labeled-clean `jOOQ__d96120f327__org.jooq.impl.DSL`

**Unit provenance:** spgroup mergedataset @ `04a18017` (pinned clone,
byte-identical rematerialization verified this session), unit labeled
**"No" Locally Observable Interference** (the Phase-2b clean set, 66 units).
Merged source = the **developer's own shipped merge** (`merge.java`), per the
phase2b harness pattern — no mergiraf involved.

**Lane evidence (verbatim):**
> `[ImportPruneUsage::flag1] L334: Stale usage of pruned import: merged file
> uses 'Settings' (line 334) but the import that provided it was pruned in
> the merge — 'import org.jooq.conf.Settings;' survives in ours and theirs
> and is absent from the merged result, which retains no import covering the
> name.`

**Execution-verified facts** (class `org.jooq.impl.DSL`, 13,353 lines):

| version | `Settings` occurrences | `import org.jooq.conf.Settings;` |
|---|---|---|
| base | 35 | yes |
| ours (left) | 35 | yes |
| theirs (right) | 35 | yes |
| **merged (developer's commit)** | **34** | **no** — 196 imports, zero from `org.jooq.conf` |

- The dataset's `merge.java` is **byte-identical** to the real
  `jOOQ/src/main/java/org/jooq/impl/DSL.java` at merge commit `d96120f327`
  (fetched from github.com/jOOQ/jOOQ and compared this session) — not an
  extraction artifact.
- No `org.jooq.conf.*` wildcard, no same-package or in-repo `Settings` type
  in scope at that commit (`org/jooq/impl/Settings.java` does not exist).
- `d96120f327` is on jOOQ's mainline, and the **next commit touching
  DSL.java is `9e404cff0f` — "[#3992] Grr Git" (2015-01-28) — which restores
  exactly the two `org.jooq.conf` imports** (`Settings`,
  `RenderNameStyle`) the merge had dropped.

**ANALYSIS (not a ruling):** the developer's shipped merge of this file was
genuinely compile-broken by exactly the pruned-import mechanism D1 detects
(both parents held the import; the merge lost it while keeping 34 bare
uses), and the developer's immediate follow-up commit — titled by them
"Grr Git" — is contemporaneous confirmation. The benchmark's "No" label is
about their construct (*behavioral* locally-observable interference); it
does not attest compile-cleanliness of the shipped artifact. Phase-2b's own
FINDINGS anticipated construct mismatch as a threat class. Note the scale:
65 of 66 labeled-clean units produced zero flags.

**Ruling options (plan §5):** as Flag 1 —
`DETECTOR-FP` ⇒ amendment + full rerun; `INCIDENTAL-BUT-TRUE` ⇒ recorded,
GD3(iii) re-judged by you. (If ruled true, the finding is also a nontrivial
external validation datum: D1 caught a real, developer-confirmed silent
import-prune breakage in a 13k-line file of a major OSS project, on a corpus
curated as interference-free.)

---

## What is NOT gated by this package

Held-out flags (20 units, experimental arm) go to the S-D6 adjudication UI
regardless (`../adjudication/adjudication_ui.html`), per plan §5 GD4. The
held-out and derivation machine numbers stand as measured; only the GD3
(ii)/(iii) gate verdicts wait on these two rulings.
