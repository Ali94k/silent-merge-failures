# G3 Condition 2 — Adjudication Record (audit trail)

**Ruled by:** Ali, 2026-07-12, via `adjudication_ui.html` (59 units: 47 pass-a/b disagreements + 12 seeded stratified agreeing units). Official rulings: `phase3_reliability_rulings.csv`. **Result: 12/12 sampled agreements ACCEPTED (100% [75.8, 100], gate ≥75% → PASS); 0 overrides on sampled agreements; 47/47 disagreements ruled (22 pass-a / 25 pass-b / 0 third-label).**

## Process

Two-draft protocol, documented for transparency:

1. **Draft 1** (Ali, all 59 ruled) → Claude review: programmatic validation (completeness, gate math, third-label scan) + code-level verification of every session-discussed case and all rulings asserting positive mechanisms not previously verified. Review produced 4 flags (below); the other 55 rulings validated clean.
2. **Draft 2** (Ali) revised 3 of the 4 flagged rulings and consciously retained 1; re-validation clean. Draft 2 = the official CSV.

The 12 gated agreeing units were untouched across both drafts (all ACCEPT); the flags concerned disagreement rulings only, so the gate result was identical in both drafts.

## The four flagged rulings

| unit | draft 1 | flag | verification | final |
|---|---|---|---|---|
| `apache_opennlp__8240a2c660` (D/B) | `overlapping-edit-interleaving` (=pass b) | **HARD:** pass b's central quote — `<<<<<<<` conflict markers "in the merged result" — appears **nowhere** in the model input (grep 0/entire input) or any merged file; its compile-delta support is single-file classpath noise (R7). Fabricated evidence. | theirs-side is cosmetic-only reformatting; overlap resolved cleanly to ours | **`none-identified`** (=pass a) |
| `sander2798_enderstone__9d0d7b7ba8` (D/B) | `stale-expectation-of-changed-behavior` (=pass b) | **HARD:** byte-identical fork twin of `sandergielisse_enderstone__9d0d7b7ba8` (same 3 scored files, EnderPlayer.java byte-equal, same two used-but-unimported symbols) ruled differently (twin = `stale-usage-of-pruned-import`). | both twins carry the same two missing-import compile breaks; compile-level dominates the runtime interaction (which both passes list as the other candidate) | **`stale-usage-of-pruned-import`** — twins consistent |
| `frankbille_scoreboard__890ecd0bdb` (H/A) | `overlapping-edit-interleaving` (=pass a) | **MEDIUM:** hybrid verified real, but whether it *breaks* hinges on the unshown pom.xml; per Amendment-2 tree (nameable interaction, breakage unsettleable from shown files) `indeterminate` is the rule-faithful call. | merged keeps one side's JPA annotation+import on the class the other side de-JPA-fied; dev dropped both; breakage undeterminable without the build file | **`indeterminate`** (=pass b) |
| `vkostyukov_la4j__d216aa8928` (D/A) | `stale-expectation-of-changed-behavior` (=pass b) | **SOFT:** mechanism (JUnit3-idiom additions meeting a JUnit4 assertion migration) plausible but hinges on the unshown test-base-class hierarchy (inherited members would shadow the static import). | not resolvable from shown files; both readings defensible | **kept `stale-expectation-of-changed-behavior`** — ruled judgment call, hinge acknowledged |

## Conventions Ali applied across the 47 disagreements (established case-by-case, then held consistently)

1. **`merged == developer-resolution` proves nothing by itself** — it is the population's normal case (the developer's own merge commit failed); the discriminator is whether the merged code contains an actual defect (`square_javapoet` — defect present → attribute; `spigotmc_bungeecord__8943` — dead-code-only difference → `none-identified`).
2. **Compile-level beats runtime-level for primacy** when both mechanisms are present (enderstone twins).
3. **"Candidate interaction" means ours×theirs.** A one-sided refactor whose unshown callers might be inconsistent is `none-identified`, not `indeterminate` — any such break would be pre-existing in that side, not merge-induced (`glowroot`, `structr`).
4. **Dropped/unshown deciding evidence + a nameable two-sided candidate → `indeterminate`** (`apache_directory-kerby`: dropped conflict file + flag-encoding change vs its callers).
5. **Removed vs renamed/relocated:** a pre-existing external/library type sharing the simple name is **not** a successor declaration (`gwtbootstrap3` → removed).
6. **Interleaving requires an actual hybrid neither side wrote**; if the merged region equals one side's version and the break is a reference elsewhere, it is a removal/rename/signature case (`jdeparser2` → removed-declaration).

Notes column in the CSV is empty; the per-case rationales are the verified analyses above and in the session log (S4), summarized here as the durable audit trail.
