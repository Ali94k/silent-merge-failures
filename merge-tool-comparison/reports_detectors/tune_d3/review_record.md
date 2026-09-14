# S-D4 §12-Amendment-3 review record — D3 widening (ISSUES #31)

Lane under review: the flag-gated textual removed/renamed-declaration
differential added to `JoernUnresolvedReference`
(`semantic_merge_driver/strategies/joern_strategies/unresolved_reference.py`),
plus the FULL-suite extension of `tools/detector_tune_run.py`.
Review ran BEFORE the definitive GD2 runs; every fix below is inside the
gate-run commit `732d8ff`. Companion documents:
`review_oss_comparison.md` (pass c), the JLS probe script results (pass b,
summarized below), and the pre-registered probe record in the lane header.

## (a) Project code — /code-review at high effort

8 finder angles (line-by-line, removed-behavior, cross-file tracer,
reuse, simplification, efficiency, altitude, CLAUDE.md conventions),
1-vote verification. 19 candidate findings; dispositions:

### Fixed — FP-critical lane defects (all execution-verified pre-fix)

1. **Multi-declarator + C-style declarators invisible** (`int a, b;`,
   `int b[];`) — the second declarator was simultaneously missed as a
   declaration and counted as a usage, producing flags on compiling merges;
   the header's "neutralized by the exactly-one-parent rule" claim was
   refuted by construction. Fix: depth-0 comma-chain walk + `[` follower in
   `_scan_var_decls`.
2. **`case MODE ->` phantom declarations** — switch-rule labels matched the
   lambda-parameter shape; a deleted switch then read as a removed
   declaration of the label constant. Fix: arrow-enumerator rejects matches
   whose comma-chain head follows `case`.
3. **Scope-blindness of var candidates** — lambda params/locals seeded
   candidates, so deleting a lambda "removed" a name that an inherited-field
   read elsewhere still used legally. Fix: two-tier scan — candidates from
   FIELD-tier declarators (directly inside a named type body, brace-depth
   checked) only; suppression stays all-tier.
4. **Receiver re-binding to a surviving type import** (JLS 6.5.2 obscuring:
   `Config Config` removed ⇒ `Config.load()` re-binds to the imported type).
   Fix: var-kind candidates suppressed when merged covers the name as a
   TYPE or it is a java.lang type name.
5. **Statement labels after `)` / `else`** counted as var reads
   (`if (x) retry: …`). Fix: label-position rule extended to `)` and
   `else`/`do`/`try`/`finally` predecessors.
6. **Java 14 multi-label case** (`case FOO, MODE:`) — non-first labels
   counted as usages. Fixed at the root in the shared
   `_ipu._FileView._qualified_or_case` (comma-chain walk to the `case`
   head), so D1 inherits the fix — the one existing-lane touch of this
   session, sanctioned by Amendment 3 with the gate rerun provided by this
   session's full suite + FULL-composition tune run (both include D1).
7. **Type-kind remover absorption blind to bare positions** — a remover that
   kept `Ev cached;` (bare type position) after deleting the nested type
   proves the name resolves elsewhere, but the anchor-limited matcher saw
   nothing. Fix: suppression-only broad matchers for the remover side
   (`_type_mentions`; `_method_mentions` adds `::name` method references),
   keeper attribution stays precise.

Each fixed vector is pinned by a dedicated regression test
(`test_widened_second_declarator…` through
`test_widened_remover_bare_type_position_absorbs`).

### Fixed — harness/cleanup adoptions

8. `_method_call_sites` re-implemented D2's probed site classifier →
   replaced with an adapter over `_ssc._call_sites` (arity channel unused,
   documented); the two lanes now share one call-site definition.
9. The FP-critical absorption/attribution/emit tail was triplicated across
   the three kind loops → factored into `finish()` so the guard order is
   structural, with per-kind usage/mention closures.
10. `FULL_SUITE` vs `LANES` drift → module-level set-equality assert; LANES
    key ↔ strategy `.name` invariant now checked at startup.
11. Tune cache keys: `+dirty.<sha1[:8]>` suffix when the driver tree has
    uncommitted changes (GD2's sanctioned in-session tuning would otherwise
    be served stale pre-fix verdicts) and `::exp1` namespace so flag-ON rows
    can never be confused with the frozen Stage-C harness's flag-OFF keys.
12. Unknown `--lane` now exits via `argparse.error` (rc 2 + usage), matching
    the old `choices=` semantics instead of aliasing a gate FAIL (rc 1).
13. `save()` batched per scenario (was per detector result: ~1,700 full
    JSON dumps of a multi-MB cache per FULL run).
14. Drift tripwire test: `_declared_type_names` must agree with D1's
    `declares_type` on a header battery (they encode the same grammar in
    separate regexes).

### Documented non-fixes (with reasons)

- **Separate strategy module for the textual pass** (altitude): plan §6
  mandates "D3 keeps existing lane names"; the widened pass stays inside
  `JoernUnresolvedReference`. The measurement-attribution cost is handled by
  the distinctive message prefix ("Stale reference to a removed/renamed
  declaration") — S-D5 can attribute mechanisms by message. The
  UNANALYZABLE-vs-FLAG interplay on Joern failure is deliberate: genuine
  textual evidence rides along (`_fail_closed(…, widened)`), both buckets
  gate-fail identically. S-D5 note: a Joern env failure still marks the
  file UNANALYZABLE when the widened pass found nothing — that is honest
  (the lane's Joern half genuinely did not run), not attributable D3 noise.
- **`_TYPE_DECL_RE` / `_ARROW_DECL_RE` regex copies** of D1/rename-lane
  patterns: hoisting would touch two more gated lanes for a constant
  extraction; the tripwire test converts silent drift into a loud failure
  instead. (The rename lane's `_DECL_GUARD` stays untouched per the
  "not a licence" note in the S-D2/S-D3 close-outs.)
- **`_declared_method_names` vs `_ssc._declared_arities` divergence risk**:
  the finder's FP scenario is impossible — the keeper/remover split uses one
  classifier symmetrically on both parents, and the two classifiers are used
  in FN-safe directions (precise for candidates, overbroad for merged
  suppression). Drift concern folded into the tripwire/adapters above.
- **Per-site `s.count("\n")` line computation and whole-file slicing in
  `_match_group` calls** (efficiency): O(k·n) worst case, immaterial next to
  the multi-second Joern/Docker subprocesses that dominate every real run;
  a shared `line_of()` on `_FileView` would touch D1's lane for a
  non-semantic win — deferred.
- **Per-result durability → per-scenario durability** of the tune cache
  (review B3): deliberate; a crash re-runs at most one file's lanes.
- **Issue-message text of the Joern differential** still says "resolvable in
  neither parent" while the code suppresses on parent *unresolved sets*
  (absent ≠ unresolved — the probe finding): message left byte-identical;
  Stage-C adjudication artifacts reference it verbatim, and the widened pass
  now covers the absent-from-remover shapes textually anyway. Recorded in
  the lane header instead.

## (b) Standalone Java-semantics review (JLS)

Verified by targeted probes against the engine (8/8 behave per spec) plus
the fix set above:

- JLS 6.5.6.2 / 8.2 (field access, inheritance): bare + `this.`-qualified
  reads in scope; `super.f` excluded (explicitly binds the superclass field
  — probe); inherited-shadow re-binding registered as a residual, remover-
  absorption kills the common pull-up/cleanup shapes.
- JLS 15.12.1 / 6.5.7.1 (method invocation): absorbable spans suppress
  supertyped/enum/anonymous bodies; plain-interface default-method calls
  correctly flag while `extends`-interface bodies absorb (probes); Object
  method names never flag; `this.m()` excluded (documented FN — reaches
  inherited members).
- JLS 8.8 (constructors are not members / not inherited): constructor-only
  removals do not fire the type kind (probe); constructor-name/method-name
  ambiguity resolved by excluding base/merged type names from method
  candidates.
- JLS 8.10 (records): record headers are type declarations; removal covered
  (probe). JLS 8.9 (enums): enum-constant lists parsed via D1's dedicated
  walker for suppression.
- JLS 6.5.2 (obscuring): fix 4 above.
- JLS 6.5.5.1 (type-parameter shadowing) and anonymous-class fields:
  documented FNs (header).
- Varargs (15.12.2.4): irrelevant here by construction — method matching is
  name-level, no arity comparison; varargs-method removals covered (probe).

## (c) Open-source practice comparison

See `review_oss_comparison.md`: Error Prone, SpotBugs, IntelliJ, Checkstyle
consulted with citations; nothing ported (no new runtime dependencies);
deliberate divergences recorded (no symbol resolution; suppression replaces
IntelliJ's human preview; three-way differential evidence in place of
resolution — prior art in SafeMerge/IntelliMerge/Towqir ASE 2022 rather than
any linter). Error Prone's zero-FP ERROR-check policy cited as the
external precedent for the project's zero-FP bar.
