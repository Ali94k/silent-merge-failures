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

## 5. Provisional Coverage Table (gate audit)

60 attributed units; `residual-other` = 0/60 (0%, within the ≤10% gate).

| unit_id | category |
|---|---|
| apache_commons-collections__84e70353ad | stale-usage-of-pruned-import |
| ardesco_selenium-standalone-server-plugin__957d978135 | stale-usage-of-pruned-import |
| atam4j_atam4j__71fcecb071 | stale-usage-of-pruned-import |
| bguerout_jongo__3aaaf0e4c7 | stale-reference-to-removed-declaration |
| blockchain_api-v1-client-java__e349598f95 | overlapping-edit-interleaving |
| buddycloud_buddycloud-server-java__48e4675ee2 | stale-caller-of-changed-signature |
| cloudfoundry_cf-java-client__80d0a0dff9 | stale-caller-of-changed-signature |
| cloudfoundry_cf-java-client__a9d35d542d | stale-caller-of-changed-signature |
| cloudfoundry_cf-java-client__b0add1ef2a | stale-caller-of-changed-signature |
| cloudslang_score__ace2958fc1 | stale-reference-to-renamed-or-relocated-declaration |
| comatoes_ftl-profile-editor__e87fe65818 | insertion-anchored-to-relocated-code |
| cternes_openkeepass__bb53512ab2 | stale-usage-of-pruned-import |
| datastax_java-driver__e1535e89ad | stale-reference-to-removed-declaration |
| dius_java-faker__9f0019116a | stale-usage-of-pruned-import |
| elisarver_selophane__4ecc600017 | stale-reference-to-renamed-or-relocated-declaration |
| feroult_yawp__141f79a8e9 | stale-usage-of-pruned-import |
| flaxsearch_luwak__9f54b4463e | stale-reference-to-removed-declaration |
| gitools_gitools__02221bf3d8 | stale-reference-to-renamed-or-relocated-declaration |
| gwtbootstrap3_gwtbootstrap3__5c0d1eab79 | stale-reference-to-removed-declaration |
| imixs_imixs-workflow__23b86de5b4 | stale-reference-to-renamed-or-relocated-declaration |
| jacquesberger_jsonparsingexample__ac521954c2 | overlapping-edit-interleaving |
| jakewharton_disklrucache__7f28919d2a | stale-expectation-of-changed-behavior |
| javaparser_javaparser__41a398414f | stale-caller-of-changed-signature |
| javaparser_javaparser__dc6254f1bf | stale-reference-to-removed-declaration |
| jcabi_jcabi-github__b13d2596ba | stale-reference-to-removed-declaration |
| jcabi_jcabi-github__e18a8ffd16 | stale-reference-to-removed-declaration |
| jdupl_lancoder__407742ea19 | overlapping-edit-interleaving |
| jenkinsci_coverity-plugin__62bdb6232e | stale-expectation-of-changed-behavior |
| jline_jline2__5acfe59453 | stale-reference-to-renamed-or-relocated-declaration |
| jmetal_jmetal__162d1a63b7 | stale-caller-of-changed-signature |
| jnr_jnr-unixsocket__467698b6bd | stale-usage-of-pruned-import |
| joel-costigliola_assertj-core__df351133a9 | stale-usage-of-pruned-import |
| jsprit_jsprit__df2e3e4b7e | stale-expectation-of-changed-behavior |
| kaazing_k3po__084cc0b426 | duplicate-concurrent-addition |
| kaazing_robot__084cc0b426 | duplicate-concurrent-addition |
| kongchen_swagger-maven-plugin__10c79c6df1 | stale-expectation-of-changed-behavior |
| logstash_log4j-jsonevent-layout__ee90110799 | stale-usage-of-pruned-import |
| mercadopago_sdk-java__9dfc950fd2 | stale-caller-of-changed-signature |
| mikera_vectorz__d93ef1b341 | stale-usage-of-pruned-import |
| mitre_http-proxy-servlet__b7a68118f2 | stale-caller-of-changed-signature |
| movsim_movsim__6dae25caf7 | stale-usage-of-pruned-import |
| msopentech_azure-activedirectory-library-for-java__d3f143872b | stale-caller-of-changed-signature |
| ninjaframework_ninja__94b2365be3 | stale-usage-of-pruned-import |
| openhft_chronicle-bytes__0fb20d3a47 | overlapping-edit-interleaving |
| openpnp_openpnp__a43f3e919e | insertion-anchored-to-relocated-code |
| openpnp_openpnp__b62c0ce826 | stale-reference-to-renamed-or-relocated-declaration |
| sailthru_sailthru-java-client__ee1f917600 | overlapping-edit-interleaving |
| sander2798_enderstone__9d0d7b7ba8 | stale-expectation-of-changed-behavior |
| sandergielisse_enderstone__df0826f63b | stale-caller-of-changed-signature |
| sandergielisse_enderstone__febdb02eb3 | stale-caller-of-changed-signature |
| segmentio_analytics-java__0d4a7b4e69 | stale-usage-of-pruned-import |
| softinstigate_restheart__98dda32101 | stale-reference-to-renamed-or-relocated-declaration |
| sonarsource_sonar-findbugs__b2fd863305 | stale-caller-of-changed-signature |
| square_javapoet__d019b6f624 | stale-usage-of-pruned-import |
| stevespringett_dependency-check-sonar-plugin__03377193d3 | duplicate-concurrent-addition |
| sviperll_static-mustache__271693c779 | stale-reference-to-removed-declaration |
| thenewcircle_spring-hibernate-20120924__7ec9c1b4bb | stale-usage-of-pruned-import |
| urbanairship_java-library__bbe0297a10 | stale-caller-of-changed-signature |
| winder_universal-g-code-sender__c93fec43ee | stale-caller-of-changed-signature |
| yandex-qatools_postgresql-embedded__6e15a53c7e | stale-reference-to-removed-declaration |

**Category sizes (provisional):** stale-usage-of-pruned-import 15; stale-caller-of-changed-signature 14; stale-reference-to-removed-declaration 9; stale-reference-to-renamed-or-relocated-declaration 7; stale-expectation-of-changed-behavior 5; overlapping-edit-interleaving 5; duplicate-concurrent-addition 3; insertion-anchored-to-relocated-code 2; residual-other 0. No category rests on a single unit, so none is flagged `provisional`.