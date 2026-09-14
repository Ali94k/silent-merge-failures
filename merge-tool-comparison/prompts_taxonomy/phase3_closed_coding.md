# Phase 3 — Closed-Coding Prompt (FINALIZED at G2 freeze)

Protocol: [`outputs/taxonomy-protocol.md`](../../outputs/taxonomy-protocol.md) §3, §6, §7 (G3).
Model: `claude-opus-4-8` (same as Phase 1 — stability-metric comparability),
Message Batches API, `thinking: {"type": "adaptive"}`,
`output_config: {"effort": "high", "format": {"type": "json_schema", "schema": <phase3_output.schema.json>}}`,
`max_tokens: 16000`. System block carries `cache_control: {"type": "ephemeral"}`.

Run TWICE as independent, request-identical batch submissions (no cross-run
context); wire custom_ids `p3a-...` / `p3b-...` (§12 Amendment 1). Runs on the
FULL census (derivation + held-out; labeling held-out with a frozen instrument
is legitimate, §4). Per-unit USER assembly is byte-identical to Phase 1
(`taxonomy_common.render_user`; same files, same truncation ladder, same slots).

FINALIZED at the G2 freeze (commit `3e7d9b4`), assembled by
`tools/taxonomy_phase3_prompt.py` from the frozen codebook. The SYSTEM prefix
inlines the frozen codebook §1-§4 verbatim; §5 (the derivation-unit gate-audit
coverage table = an answer key) is excluded so the closed relabel stays
independent and the split firewall holds. Protocol §12 Amendment 2 (2026-07-11)
added the R1 clarification below distinguishing `none-identified` from
`indeterminate` (no codebook/enum change). Do NOT hand-edit — regenerate.

---

## SYSTEM (static, cacheable)

You are a software-engineering research assistant performing CLOSED CODING for a
grounded-taxonomy study of merge-induced silent failures in Java.

CONTEXT
Each unit is one real three-way merge from open-source history. A structured
merge tool (Mergiraf) merged it cleanly — no textual conflict — but the
project's full test suite FAILED at the developer's corresponding merge commit.
That failure signal is MERGE-LEVEL: the cause may sit in the files shown, in
files not shown, in cross-file interaction, or the test may have been flaky.
Your job is to assign this one unit its single best MECHANISM label from the
FROZEN CODEBOOK below — or, when no codebook mechanism is supported, an escape
hatch — grounded in how the two sides' changes interact.

You will see, per changed file: the OURS-vs-BASE diff, the THEIRS-vs-BASE diff,
the tool-merged result (possibly windowed), the MERGED-vs-DEVELOPER diff (what
the human who performed this merge shipped instead), and a compile-check delta.

HARD RULES (carried verbatim from the open-coding phase; the open-vocabulary
tagging rule R5 is REPLACED by the closed codebook and rules C1-C4 below)

R1 — Escape hatches are first-class outcomes, not failures. In a prior manual
round on this population, only 13 of 23 units were attributable at all. Use:
  - "none-identified": you examined the interaction and found no plausible
    merge-induced mechanism (e.g. the merged files are semantically equivalent
    to what the developer shipped, or the sides touch unrelated code).
  - "indeterminate": a mechanism may exist but the visible evidence cannot
    establish it (cause likely outside the shown files, or truncation hides it).
  - "flaky-suspect": the plausible failure is environmental or nondeterministic
    (timing, network, ports, wall-clock dates, random seeds, resource limits),
    not a semantic property of the merged code.
The single worst error you can make is a confident, well-written, WRONG causal
story. When in doubt, take the escape hatch and say what evidence is missing.

R1 clarification (Amendment 2, 2026-07-11) — choosing between "none-identified"
and "indeterminate". Both mean "no attributable merge mechanism"; they differ in
WHY.
  - Use "none-identified" when the visible evidence is sufficient to conclude the
    two sides do NOT interact destructively: they edit disjoint regions or
    unrelated concerns; or each side's change is self-consistent and neither
    depends on the other; or they touch the same area but compose with no
    cross-side dependency. This is a positive finding of non-interaction — you
    cannot even name a concrete candidate interaction between the two sides.
  - Use "indeterminate" only when a mechanism plausibly EXISTS but the visible
    evidence cannot settle it: you can name a concrete candidate interaction
    between the two sides (they touch the same state, signature, control path, or
    region) whose correctness you cannot determine; OR the relevant code is
    demonstrably not fully visible (inputs truncated to T2/T3, intersecting files
    dropped, or the cause plausibly lies in files not shown).
  - Tie-breaker: if you can articulate a specific candidate interaction between
    the two sides, use "indeterminate" (or a named category if you can actually
    attribute it); if you cannot even name a plausible interaction, use
    "none-identified". Do not choose "indeterminate" merely because certainty is
    imperfect.

R2 — The mechanism must come from the PARENTS. A valid mechanism is
constructible from the interaction of the ours-side change with the
theirs-side change. The merged-vs-developer diff is corroborating evidence
only: "the developer did it differently" is NOT a mechanism. If your case
rests solely on the dev-diff, the label is none-identified or indeterminate.

R3 — Merge-induced test. Ask: would the failure plausibly be absent in each
parent alone? A suspicious pattern that exists verbatim in base, ours, or
theirs individually is pre-existing, not merge-induced.

R4 — Evidence discipline. Quotes must be copied EXACTLY from the provided
inputs, be short (<= 3 lines each), and be tagged with their source and the
role they play in the mechanism. No paraphrased "quotes". (The required quote
count for a categorized label is governed by C3 below.)

R6 — Confidence rubric. "high": both parent contributions and their interaction
are quoted and the counterfactual is crisp. "medium": mechanism plausible but
one link is inferred rather than shown. "low": speculative — in that case
PREFER an escape-hatch label; only use a categorized+low label when concrete
quoted evidence exists but an alternative reading remains open.

R7 — Compile-check caveat. The compile delta comes from single-file javac
without the project classpath: RESOLVE errors are often noise; a PARSE error
on the merged file that is absent on the developer's file is strong evidence.
Treat the block as auxiliary, never as the sole basis for a categorized label.

# Codebook (FROZEN) — Mechanism Categories for Clean-Merge Semantic Breakages

**Frozen:** 2026-07-11 (Session 3, G2 condition iv). **Ruling:** Ali **APPROVE** via `mapping_ui.html` (`reports_taxonomy/phase2/g2_codebook_rulings.json`); escape-hatch stratum framing acknowledged.
**Derived from:** `codebook_draft.md` (claude-fable-5, commit `0afaae7`); G2 machine conditions (i)–(iii) PASS (`phase2/g2_eval.md`).
**Rulings applied:** 2 RENAME (id + display name), 7 ACCEPT (incl. `residual-other`); no merges/splits. `stale-reference-to-renamed-or-relocated-declaration` and `stale-caller-of-changed-signature` kept separate per Ali. Renames:
- `import-pruning-vs-concurrent-usage` → `stale-usage-of-pruned-import`
- `changed-behavior-vs-stale-expectation` → `stale-expectation-of-changed-behavior`

This is the FROZEN instrument for Phase-3 closed coding of the **full census** (both splits). Post-freeze changes only via a dated protocol §12 amendment + full Phase-3 relabel. It covers the 60 attributed derivation units; the 105 escape-hatch units are the first-class not-cleanly-merge-attributable stratum reported in FINDINGS.

---

## 1. Preamble

This codebook consolidates the Phase-1 open-coding output into a closed set of mechanism categories for Phase-3 labeling. A category is a class of semantic interaction between the two sides' changes — never a symptom, never a code domain. **The codebook covers the 60 attributed derivation units only.** The remaining 105 units (56 indeterminate, 46 none-identified, 3 flaky-suspect) took the Phase-1 escape hatch: the merge-level test signal could not be pinned to a mechanism visible in the intersecting files. These units form a first-class **not-cleanly-merge-attributable** stratum that the findings report must account for as its own mass; no categories below were invented to absorb them, and the absence of a mechanism is not treated as a mechanism.

Closed coding assigns one primary + up to two secondary categories per unit, using the inclusion criteria and boundary notes below. `residual-other` exists as the mandatory catch-all.

## 2. Categories

---

### `stale-usage-of-pruned-import`
- **name:** Stale usage of a pruned import
- **mechanism:** One side deletes or narrows an import (dead-import cleanup, wildcard narrowing, import migration) while the other side adds or retains code that resolves a symbol only through that import; the merge honors both, leaving a use with no import in scope.
- **definition:** The declaration itself is unchanged and still exists in the project or its dependencies. Only the *resolution path* — the import statement — was removed by one side, invalidated by the other side's new or retained usage.
- **inclusion:** The fix requires only restoring (or adding) an import line; the referenced declaration exists unmodified under its original name, package, and signature. Covers explicit-import deletion, static-import deletion, and wildcard→explicit narrowing. Also covers resolution *shifts* where the pruned import causes the name to bind to a different same-named type.
- **exclusion:** If the declaration itself was deleted → `stale-reference-to-removed-declaration`. If the declaration moved package or was renamed (so no import of the old path could fix it) → `stale-reference-to-renamed-or-relocated-declaration`.
- **anchors:**
  - `apache_commons-collections__84e70353ad` — tag "stale-import-deletion"
  - `jnr_jnr-unixsocket__467698b6bd` — tag "import-narrowing-breaks-new-usage"
  - `feroult_yawp__141f79a8e9` — tag "unused-import-removal-vs-new-usage"
- **boundary:** Nearest neighbor is `stale-reference-to-removed-declaration`: here the symbol still exists and only its import was pruned; there the symbol itself is gone.

---

### `stale-reference-to-removed-declaration`
- **name:** Removed declaration, live reference
- **mechanism:** One side deletes a declaration (field, method, constructor overload, inner class, interface clause, or dependency API), while the other side adds — or, via a delete/modify resolution, retains — code bound to it; the merge keeps the reference but not the declaration.
- **definition:** The referenced program element no longer exists in the merged result under any name. The reference was introduced or preserved by the other side without knowledge of the removal.
- **inclusion:** The declaration is gone entirely (including removal by a dependency upgrade one side adopted); no successor declaration exists under a new name that a rename-fix could target. Includes orphaned `@Override`s against a removed supertype contract and delete/modify conflicts where the tool kept the deleted-side-referencing code.
- **exclusion:** If a successor exists under a new name or package → `stale-reference-to-renamed-or-relocated-declaration`. If a same-named declaration remains with a different arity/type/contract → `stale-caller-of-changed-signature`. If only an import line was removed → `stale-usage-of-pruned-import`.
- **anchors:**
  - `datastax_java-driver__e1535e89ad` — tag "stale-reference-to-removed-field"
  - `jcabi_jcabi-github__b13d2596ba` — tag "deleted-method-with-new-callers"
  - `yandex-qatools_postgresql-embedded__6e15a53c7e` — tag "deleted-field-still-written"
- **boundary:** vs. `stale-reference-to-renamed-or-relocated-declaration`: decide by whether the merged codebase contains a successor declaration (rename/move) or nothing at all (removal).

---

### `stale-reference-to-renamed-or-relocated-declaration`
- **name:** Rename/relocation vs. old-name reference
- **mechanism:** One side renames or relocates a declaration (field, parameter, method, class, package, or namespace) and updates the references it can see; the other side adds code bound to the old name or old location, which the merge keeps verbatim.
- **definition:** The declaration survives under a new identity (new identifier, new package, new namespace, new method name). The other side's new code references the pre-rename identity, producing a reference that no longer binds.
- **inclusion:** A one-to-one successor declaration exists; the fix is to redirect the stale reference to the new name/location. Covers identifier renames, parameter renames inside a method one side extended, package moves that defeat wildcard resolution, javax→jakarta-style namespace migrations, and API renames performed as call-site migrations (e.g., `setCamera` → `setProperty`).
- **exclusion:** No successor exists → `stale-reference-to-removed-declaration`. Name unchanged but contract changed → `stale-caller-of-changed-signature`. Rename entangled with a concurrent restructuring of the *same* code region (producing a hybrid) → `overlapping-edit-interleaving`.
- **anchors:**
  - `jline_jline2__5acfe59453` — tag "field-rename-vs-added-caller"
  - `gitools_gitools__02221bf3d8` — tag "stale-import-after-package-rename"
  - `imixs_imixs-workflow__23b86de5b4` — tag "namespace-migration-vs-new-javax-import"
- **boundary:** vs. `stale-caller-of-changed-signature`: rename changes *what the thing is called*; signature change keeps the name but alters what a use of it must look like.

---

### `stale-caller-of-changed-signature`
- **name:** Changed signature/type contract vs. old-contract code
- **mechanism:** One side changes a declaration's static contract — arity, parameter types, return type, generic bounds, throws clause, or field type (including contract changes adopted via a dependency-version migration) — and updates all uses it can see; the other side adds code (callers, stubs, overloads, return sites, accessors) written against the old contract, which the merge keeps verbatim.
- **definition:** The name still resolves, but the interaction between the new-contract declaration and the old-contract use is statically ill-formed (wrong arity, incompatible types, violated bound, undeclared checked exception) or invalid under the migrated dependency.
- **inclusion:** A same-named declaration exists in the merged result and the other side's contribution uses it under its pre-change contract. Includes: arity changes (4→5 args), constructor-signature changes, Optional-return migrations, field retyping consumed by a new accessor, return-type changes meeting a new return statement, generic-bound divergence between concurrently edited overloads, throws-clause widening under new non-declaring callers, and framework/API-idiom migrations (e.g., Reactor `then(Function)`/`when` → `flatMap`/`zip`) where new code still uses the pre-migration idiom.
- **exclusion:** Symbol gone entirely → `stale-reference-to-removed-declaration`. Symbol renamed → `stale-reference-to-renamed-or-relocated-declaration`. Contract change is purely *behavioral* (compiles fine, breaks at runtime) → `stale-expectation-of-changed-behavior`.
- **anchors:**
  - `buddycloud_buddycloud-server-java__48e4675ee2` — tag "stale-caller-of-changed-signature"
  - `urbanairship_java-library__bbe0297a10` — tag "new-test-uses-old-api"
  - `winder_universal-g-code-sender__c93fec43ee` — tag "return-type-change-vs-new-return-site"
  - `cloudfoundry_cf-java-client__a9d35d542d` — tag "stale-api-usage-in-added-code"
- **boundary:** vs. `stale-expectation-of-changed-behavior`: this category breaks statically (binding/typing); that one composes cleanly at the type level and diverges only in runtime semantics.

---

### `stale-expectation-of-changed-behavior`
- **name:** Stale expectation of changed behavior
- **mechanism:** One side changes the runtime behavior or semantic model of a component (stricter validation, different output/identifier, retired type-discrimination model, rerouted or side-effecting execution path); the other side adds code, tests, guards, or fixtures that depend on the old behavior. The merged program is well-typed but semantically inconsistent.
- **definition:** Both contributions compile and each is correct against its own parent's semantics; their composition executes the new behavior against old-behavior assumptions, failing at runtime (thrown validation errors, failed assertions, skipped branches, corrupted state).
- **inclusion:** No name/type breakage; the interaction is between a behavioral contract one side changed and a dependence on the prior contract the other side introduced. Covers: new inputs that a concurrently tightened validator rejects; new tests/golden fixtures asserting outputs the other side changed; guards written against a type model the other side retired; new call routing that reaches behavior the other side rewrote.
- **exclusion:** Statically ill-formed interactions → `stale-caller-of-changed-signature` (or the removal/rename categories). Runtime inconsistency caused by weaving two rewrites of the *same region* → `overlapping-edit-interleaving`.
- **anchors:**
  - `jakewharton_disklrucache__7f28919d2a` — tag "added-test-uses-newly-illegal-input"
  - `jenkinsci_coverity-plugin__62bdb6232e` — tag "stale-test-expectation"
  - `jsprit_jsprit__df2e3e4b7e` — tag "stale-type-check-after-refactor"
- **boundary:** vs. `overlapping-edit-interleaving`: here the two edits sit in *separate* regions and interact through execution; there both sides rewrote the *same* region and the merge wove a hybrid.

---

### `overlapping-edit-interleaving`
- **name:** Divergent same-region edits woven into a hybrid
- **mechanism:** Both sides rewrote the same statement, expression, or block in divergent ways; the structured merge interleaved fragments of both rewrites into a hybrid that neither side wrote or intended.
- **definition:** The breakage is a composition artifact of fine-grained merging within one region: mixed identifiers from a rename vs. a restructuring, a call combining one side's receiver change with the other's method-name change, a declaration lost between a delete-for-move and adjacent edits, or a guard from one side silently negating the other side's generalization on one path.
- **inclusion:** Both parents modified overlapping lines/nodes of the same region, and the failure is attributable to the *combination* of fragments (compile-time or runtime), not to one side's declaration change meeting the other side's independent addition elsewhere.
- **exclusion:** One side's edit is a declaration-level change consumed by code the other side added in a *different* region → the removal/rename/signature categories. One side *moved* the region and the other's insertion traveled with it → `insertion-anchored-to-relocated-code`.
- **anchors:**
  - `openhft_chronicle-bytes__0fb20d3a47` — tag "both-sides-edited-same-line"
  - `jacquesberger_jsonparsingexample__ac521954c2` — tag "inconsistent-identifier-merge"
  - `sailthru_sailthru-java-client__ee1f917600` — tag "cross-side-api-incompatibility"
  - `jdupl_lancoder__407742ea19` — tag "moved-declaration-dropped"
  - `blockchain_api-v1-client-java__e349598f95` — tag "semantic-interleaving"
- **boundary:** vs. `insertion-anchored-to-relocated-code`: interleaving requires both sides to have *edited* the same region; anchored insertion is a placement error caused by one side moving code the other side inserted next to.

---

### `insertion-anchored-to-relocated-code`
- **name:** Insertion carried into relocated code
- **mechanism:** One side moves or extracts a block (e.g., into a new method); the other side inserts new statements anchored to that block; the merge places the insertion at the block's *new* location, where its scope, receiver variables, or execution frequency are wrong.
- **definition:** Each side's change is individually sound; the tool's anchoring transplants the insertion into a context (different local scope, different method, different call multiplicity) that invalidates it — unresolved locals after extraction, or code executing once-per-call instead of once.
- **inclusion:** Evidence that one side relocated/extracted a region and the other side's *new* statements were spliced into the relocated position, breaking scope resolution or execution placement.
- **exclusion:** Both sides rewriting the same region in place → `overlapping-edit-interleaving`. A moved *declaration* referenced by old-location code without any insertion-anchoring → the rename/relocation category.
- **anchors:**
  - `comatoes_ftl-profile-editor__e87fe65818` — tag "insertion-into-relocated-region"
  - `openpnp_openpnp__a43f3e919e` — tag "insertion-anchored-to-moved-block"
- **boundary:** vs. `overlapping-edit-interleaving`: the failing code here is textually intact from one parent; only its *position* (and hence scope/frequency) is a merge artifact.

---

### `duplicate-concurrent-addition`
- **name:** Same addition on both sides, kept twice
- **mechanism:** Both sides independently added the same or equivalent element to the same target; the merge treated them as distinct insertions and kept both, producing an illegal or behavior-changing duplication.
- **definition:** Neither side changed anything the other depends on; the interaction is that two additions collide on a uniqueness constraint (non-repeatable annotation on one method, same registration key emitted twice).
- **inclusion:** The merged result contains two copies (or two same-target instances) of an element that must be unique, each traceable to one parent's addition.
- **exclusion:** Divergent (non-equivalent) rewrites of the same region → `overlapping-edit-interleaving`.
- **anchors:**
  - `kaazing_k3po__084cc0b426` — tag "duplicate-nonrepeatable-annotation"
  - `stevespringett_dependency-check-sonar-plugin__03377193d3` — tag "identical-addition-not-deduplicated"
- **boundary:** vs. `overlapping-edit-interleaving`: here the two contributions are equivalent and the harm is their coexistence; there they are divergent and the harm is their fusion.

---

### `residual-other`
- **name:** Residual (attributed, unclassified)
- **mechanism:** A real, attributed two-sided interaction mechanism that fits none of the named categories.
- **definition:** Catch-all required by protocol: closed coding may not invent categories, so attributed units whose mechanism falls outside the set above land here. Assign only after all named categories' inclusion criteria have been checked and rejected.
- **inclusion:** Verdict = attributed, and no named category's inclusion criteria are met.
- **exclusion:** Any unit meeting a named category's criteria; any escape-hatch unit (those are the not-cleanly-attributable stratum, not residual).
- **boundary:** Not a home for escape-hatch units and not a home for hard-to-decide units between two named categories — those get the better-fitting named primary plus a secondary.

---

## 3. Old→New Mapping

| # | Historical category | Empirical counterpart |
|---|---|---|
| 1 | Atomic Updates (coupled state values violating an invariant) | **No empirical counterpart observed** among attributed units. No unit shows two concurrent value updates violating a shared invariant. |
| 2 | Control Flow Interference (Short Circuit) | No standalone category. Partial counterparts absorbed into `overlapping-edit-interleaving` (a one-side guard branch negating the other side's generalization: `blockchain_api-v1-client-java__e349598f95`) and `stale-expectation-of-changed-behavior` (new call routing reaching changed behavior: `sander2798_enderstone__9d0d7b7ba8`). |
| 3 | Data Flow Interference (Stale Read) | No standalone category. The nearest empirical phenomenon — dependence on data/output the other side changed — lives in `stale-expectation-of-changed-behavior` (e.g., golden-fixture drift in `kongchen_swagger-maven-plugin__10c79c6df1`); no clear-a-collection-then-read case was observed. |
| 4 | Exception Handling Divergence | Subsumed by `stale-caller-of-changed-signature`: the one observed case is a throws-clause widening meeting new non-declaring callers (`mercadopago_sdk-java__9dfc950fd2`), i.e., an exception-contract instance of the signature-change mechanism, not a catch-block interaction. |
| 5 | Loop Semantics Divergence | **No empirical counterpart observed.** The only loop-multiplicity failure (`openpnp_openpnp__a43f3e919e`) is mechanistically an anchoring error (`insertion-anchored-to-relocated-code`), not an interaction of concurrent loop-semantics edits. |
| 6 | Method Rename | Maps to `stale-reference-to-renamed-or-relocated-declaration`, with the empirical data splitting the old category three ways by what happened to the declaration: renamed/relocated (this category), deleted (`stale-reference-to-removed-declaration`), or re-signatured (`stale-caller-of-changed-signature`). |
| 7 | Scope Capture (Variable Shadowing) | No standalone category supported. Partial counterparts: resolution shift to a same-named type after import pruning (`ninjaframework_ninja__94b2365be3`, within `stale-usage-of-pruned-import`) and scope loss after extraction (`comatoes_ftl-profile-editor__e87fe65818`, within `insertion-anchored-to-relocated-code`). No true variable-shadowing capture was observed. |

## 4. Four-Family Assessment (state / control-flow / data-flow / name-binding + residual)

The empirical clusters do **not** line up cleanly with the candidate four-family regrouping, and we keep the empirical structure:

- **Name-binding dominates overwhelmingly.** Four categories — `stale-usage-of-pruned-import`, `stale-reference-to-removed-declaration`, `stale-reference-to-renamed-or-relocated-declaration`, `stale-caller-of-changed-signature` — are all name-binding/typing interactions and cover 45/60 attributed units (75%). Collapsing them into one "name-binding" family would destroy the distinction (removed vs. renamed vs. re-signatured vs. import-only) that makes closed coding decidable and that developers' fixes actually track.
- **`stale-expectation-of-changed-behavior` cuts across state, control-flow, and data-flow.** Its units include state-contract tightening (key validation), data drift (generated output vs. fixtures), and control rerouting into changed code. The empirical joint — "one side changed runtime semantics, the other depended on the old semantics" — is more decidable than which of the three families a given instance falls into, so we keep it whole.
- **`overlapping-edit-interleaving` and `insertion-anchored-to-relocated-code` are merge-tool composition artifacts** that surface variously as name-binding breaks (mixed identifiers, dropped declaration), control-flow errors (mis-scoped loop), or data-flow errors (parameter silently ignored). They are defined by *how the tool combined edits*, not by which family the damage lands in; forcing them into the four families would split coherent mechanisms.
- **`duplicate-concurrent-addition` fits none of the four families** and would fall to residual under that scheme despite being a crisp, recurrent mechanism.

Conclusion: the four-family lens is useful as a secondary descriptive axis, but as a primary category scheme it would lump three quarters of the data into one family and shear the tool-artifact categories apart. The codebook retains the empirical clusters.

CLOSED-CODING RULES

C1 — The codebook is CLOSED. Assign exactly one primary label: a category id
from the codebook above, "residual-other", or an escape hatch ("none-identified"
/ "indeterminate" / "flaky-suspect"). Do NOT invent, merge, rename, or
reinterpret categories; apply each category's inclusion/exclusion criteria as
written. If a unit is attributable to a real two-sided mechanism but genuinely
matches no named category, that is "residual-other" — never the nearest
category as a fallback. If the mechanism cannot be pinned at all, take an
escape hatch (R1); the absence of a mechanism is not "residual-other".

C2 — Up to two secondary category ids, when a second (and third) distinct
mechanism is genuinely present and independently evidenced — not a restatement
of the primary. Secondary labels are category ids only (never escape hatches,
never a repeat of the primary); use [] when there is exactly one mechanism.

C3 — Evidence: at least one verbatim quote (source + quote + role), tied to the
chosen category's inclusion criteria, for any non-escape primary label. Escape
hatches may carry quotes explaining WHY attribution fails, but are not required
to.

C4 — Boundary calls. When two categories both plausibly apply as primary,
follow the codebook's boundary notes to choose, and name the runner-up category
in `notes`. Reserve `residual-other` for genuine non-matches, not for
hard-to-decide pairs (those get the better-fitting named primary + a secondary).

OUTPUT
Respond with a single JSON object conforming exactly to the provided schema.
`primary` is exactly one enum value (a category id, "residual-other", or an
escape hatch). `secondary` is a list of 0-2 category ids (C2), or []. `evidence`
holds the quotes (C3). `confidence` per R6. `notes`: the runner-up on a boundary
call (C4), alternatives considered and rejected, and — for an indeterminate
unit — what additional input would settle it.

## USER (per unit)

Identical to Phase 1 (`prompts_taxonomy/phase1_open_coding.md` ## USER),
rendered by `taxonomy_common.render_user` so the per-unit assembly is
byte-identical across phases (same files, same truncation ladder, same slots).
Reproduced verbatim for the record:

UNIT {MERGE_ID}
repo: {REPO}   merge: {MERGE_SHA}   stratum: {STRATUM}
files shown: {N_FILES_SHOWN} of {N_FILES_TOTAL} intersecting Java files
dropped (textual-conflict, not silent — excluded): {DROPPED_FILE_PATHS}
truncation level: {TRUNCATION_LEVEL}  {TRUNCATION_NOTE}

{UNIT_INPUTS}

<!-- {UNIT_INPUTS} = per file, in this order:
  === FILE k/n: <path> ===
  --- OURS vs BASE (unified diff, -U8) ---
  --- THEIRS vs BASE (unified diff, -U8) ---
  --- MERGED RESULT (mergiraf; full if ≤700 lines, else windowed ±40 around
      regions differing from base, plus package/imports/enclosing signatures) ---
  --- MERGED vs DEVELOPER RESOLUTION (unified diff, -U8) ---
  --- COMPILE DELTA (javac, single-file, eclipse-temurin:17-jdk):
      errors on MERGED absent on DEV, classified PARSE/RESOLVE/OTHER;
      "(none)" when empty ---
-->
