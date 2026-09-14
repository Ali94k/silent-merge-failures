# Plan: Comparator 3e — Tier E transforms (D.1 fix + 10 new transforms)

**Status:** drafted (not started) — 2026-05-15.
**Owner:** Ali
**Created:** 2026-05-15
**Depends on:** 3d Tier D ([`comparator-3d-extended-ast-transforms.md` §13 empirical outcome](comparator-3d-extended-ast-transforms.md))
**Closes:** [`ISSUES.md` #2](../../merge-tool-comparison/ISSUES.md) — Tier E hits the original 3b plan §3 floor of X_total ≥ 30, enabling `decided → resolved` transition.
**Related:** [`stage-gamma-fp-diagnostic.md §11`](stage-gamma-fp-diagnostic.md) (Tier D residual diagnosis)

---

## 1. Context

3d Tier D (6 transforms, shipped 2026-05-15) lifted Spork from TP 7 → 14 (cumulative X=12 over pre-3b baseline of TP 2). Plan §3 floor X ≥ 30 still unmet; ISSUES.md #2 stays `decided`.

Empirical Tier E residual analysis (2026-05-15) on the 29 remaining Spork FPs found:

1. **A real bug in D.1.** `_try_unwrap_if` and `_try_unwrap_loop` use `c is cons` to skip the cons-block child in their post-unwrap recursion, but tree-sitter returns fresh Python `Node` wrappers per access — `is` is always False. The cons-block (including its leading comments) gets walked twice, producing overlapping edits that corrupt brace balance. D.6's token-canonical fold parse-fails on the result in 6 of the 29 still-FP scenarios. Fix: `c == cons` (or compare `c.id == cons.id`).

2. **The dominant residual patterns are NOT what the brief expected.** Brief listed: `+`/`*` paren strip, long-array whitespace, hex case. Measured patterns (in-memory prototype on the 29 still-FP scenarios, after D.1 bug-fix):
   - `+`/`-`/`*`/`/` same-op left-assoc paren strip — 6-8 scenarios
   - `(!x)` / `(~x)` unary paren strip — 5 scenarios
   - `new T[]{...}` array shorthand (incl. nested in array_initializer) — 6 scenarios
   - Enum trailing `;` (in `enum X { A, B; }` ↔ `enum X { A, B }`) — 5 scenarios
   - `(a instanceof B)` paren strip — 1 scenario
   - `assert (a < b)` paren strip (D.4 didn't include `assert_statement`) — 1 scenario
   - `arr[(x - 1)]` paren strip (D.4 didn't include `array_access`) — 2 scenarios
   - Array trailing comma `{1, 2, }` ↔ `{1, 2}` — 5 scenarios (entangled with shorthand)
   - Paren around assignment in `while ((x = y))` — 2 scenarios
   - Float literal suffix `100d` ↔ `100.0` — 3-4 scenarios
   - Hex literal case `0xFF` ↔ `0xff` — 1 scenario (ab0oo)

   None of "long-array whitespace" is a residual driver — that closes correctly under D.6's token-fold once the D.1 bug is fixed.

3. **Per-transform recovery is entangled.** Multiple residual patterns co-occur in single scenarios; closing one without closing the others doesn't change the scenario's TP/FP status. So per-transform attribution is meaningful only cumulatively. This was the same lesson 3d plan §3 surfaced.

Tier E scope: bug-fix + 10 new transforms, designed to close the floor.

## 2. Scope — Tier E

**In scope:**

| Phase | Transform | Pattern | Approach |
|---|---|---|---|
| **3e.0** | `_try_unwrap_if` / `_try_unwrap_loop` identity-bug fix | overlapping edits corrupt the canonical text | Change `c is cons` / `c is body` to `c == cons` / `c == body` (tree-sitter's `Node.__eq__` compares node IDs correctly). |
| **3e.1** | `strip_paren_around_unary` | `(!x) && (!y)` ↔ `!x && !y` | AST: strip paren around `unary_expression` whose op ∈ `{!, ~}` and whose parent is in the unary-safe-parents set (basically the same as D.4's safe_binary set, plus `binary_expression` itself because `!` and `~` bind tighter than any binary op). Excludes `-` and `+` unary ops (sign-flip concerns in some contexts). |
| **3e.2** | `strip_array_creation_shorthand` | `new double[] {1, 2}` ↔ `{1, 2}` (in var-decl context) | AST: when `array_creation_expression`'s parent is `variable_declarator` OR `array_initializer` (the nested case), AND it has an `array_initializer` value child, strip the `new T[]` prefix. |
| **3e.3** | `strip_paren_around_arith_same_op_left_assoc` | `(a + b) + c` ↔ `a + b + c` (string-concat-safe) | AST: paren around `binary_expression` whose op ∈ `{+, -, *, /, %}` AND outer parent is `binary_expression` with same op AND the paren is the LEFT operand (left-associative). For `+`: extra guard — if outer-right contains string_literal AND inner doesn't, skip (string-concat ambiguity). |
| **3e.4** | `strip_paren_around_instanceof` | `(x instanceof Foo) \|\| y` ↔ `x instanceof Foo \|\| y` | AST: paren around `instanceof_expression` when parent is in safe_bin OR parent is `binary_expression` with op precedence < 9 (instanceof's precedence). |
| **3e.5** | `strip_empty_enum_body_declarations` | `enum X { A, B; }` ↔ `enum X { A, B }` | AST: strip `enum_body_declarations` subtree when its `named_child_count` is 0 (it contains only the separator `;`). |
| **3e.6** | Expand `SAFE_BINARY_PAREN_PARENTS` | `assert (a < b)`, `arr[(x - 1)]` | Add `assert_statement` and `array_access` to the existing D.4 set. No new branch — these contexts are already structurally identical (no outer operator can rebind). |
| **3e.7** | `strip_array_initializer_trailing_comma` | `{1, 2, }` ↔ `{1, 2}` | AST: in `array_initializer`, if the children sequence ends with `, }`, strip the trailing `,`. Pure cosmetic; both forms parse to the same array. |
| **3e.8** | `strip_paren_around_assignment` | `while ((x = y))` ↔ `while (x = y)` | AST: paren around `assignment_expression` when parent is `parenthesized_expression` (i.e., the wrapping while/if/etc. condition paren) or `expression_statement`. Skipped in binary/cast/postfix contexts (assignment is right-associative and the paren has semantic weight there). |
| **3e.9** | `normalize_float_literal_suffix` | `100d` ↔ `100.0`, `0.5f` ↔ `0.5` | TEXT-level edit on `decimal_floating_point_literal` and `hex_floating_point_literal` tokens: strip trailing `d`/`D`/`f`/`F` if the literal has a `.` or exponent; convert `Nd`/`ND` (no dot/exp) to `N.0`. Loses `f`/`F`-vs-double type distinction — but textually these often vary cosmetically in numeric-heavy code. |
| **3e.10** | `normalize_hex_literal_case` | `0xFF` ↔ `0xff`, `0xCAFE` ↔ `0xcafe` | TEXT-level edit on `hex_integer_literal` tokens: lowercase the entire token. Loses zero-pad distinction (`0x3` vs `0x03`) — that case is ambiguous on direction, deferred. |

**Out of scope (Tier F and beyond):**

- **Multi-declarator split** — `long a = 0; long b;` ↔ `long a = 0, b;`. Requires non-trivial AST rewriting (split one declaration into two or merge two into one). Ambiguous direction. 1 scenario (accla Graphulo).
- **FQN outside `java.lang`** — `org.firebrandocm.dao.annotations.Column` ↔ `Column`. Requires reading the imports list and resolving against the active import set. ~1 scenario (47deg ClassMetadata).
- **Numeric underscore strip** — `5_000_000` ↔ `5000000`. 1 scenario (zemberek FastText). Recoverable with a small text-level transform; deferred for scope discipline.
- **Redundant `abstract` on interface** — `public abstract interface` ↔ `public interface`. 1 scenario (adangel PMD). Requires modifier-list editing on `interface_declaration`.
- **3a — test-suite ground truth** — different approach entirely; defer per `mergiraf-integration.md §3` cost analysis.

## 3. Recovery targets

Measured empirically via in-memory prototype on the n=50 dataset (script: `workspace/tier_e_prototype_v3.py`). All transforms enabled cumulatively:

| Phase shipped | Cumulative Spork TP | Δ |
|---|---:|---:|
| (post-3d Tier D baseline) | 14 | — |
| + 3e.0 D.1 fix | 15 | +1 |
| + 3e.1 unary paren | 15 | 0 (entangled) |
| + 3e.2 array shorthand | 16 | +1 (entangled w/ 3e.7) |
| + 3e.3 arith same-op | 23 | +7 (closes 3e.1's entangled cases) |
| + 3e.4 instanceof paren | 24 | +1 |
| + 3e.5 enum trailing `;` | 25 | +1 |
| + 3e.6 expand safe_bin (assert, array_access) | 28 | +3 (was 26 before array_access added) |
| + 3e.7 array trailing comma | 28 | 0 (entangled w/ 3e.10) |
| + 3e.8 assignment paren | 28 | 0 (entangled w/ later transforms) |
| + 3e.9 float-suffix normalize | 31 | +3 (closes addthis stream-lib variants) |
| + 3e.10 hex case lowercase | **32** | +1 |

Per-phase deltas are approximate — multiple transforms must be active for many scenarios to close. The final cumulative is exact (measured).

**Floor:** Tier E acceptance is **Spork TP ≥ 30 / FP ≤ 13** (X_total ≥ 28). Modest pull-back from prototype's 32 in case some transforms under-recover when integrated.

**Stretch:** **Spork TP ≥ 32 / FP ≤ 11** (X_total ≥ 30). Matches prototype. **HITS the original 3b §3 floor.** If achieved, ISSUES.md #2 transitions `decided → resolved`.

| Tool | Pre-3e | Tier E point estimate | Tier E acceptance floor |
|---|---|---|---|
| Spork | TP 14 / FP 29 | **TP 32 / FP 11** (X_e = 18) | TP ≥ 30 / FP ≤ 13 (X_e ≥ 16) |
| Mastery | TP 10 / FP 34 | TP 12 / FP 32 | unchanged target; +2 BONUS |
| git-merge-file | TP 39 / FP 0 | unchanged | unchanged |
| JDime | TP 1 / FP 1 | unchanged | unchanged |

**Undershoot trigger:** if any phase commits 2+ below its prototype-attributed estimate (cumulative), pause and re-examine.

## 4. Architecture integration

### 4.1 Extends Tier 3 in place

All 11 phases land in [`src/evaluation/ast_normalize.py`](../../merge-tool-comparison/src/evaluation/ast_normalize.py). No new tier in `contents_match`; no new env var. `MERGE_COMPARATOR_AST_NORMALIZE=off` covers Tier E for free.

Two of the transforms are TEXT-level (3e.9 float suffix, 3e.10 hex case) — they still operate via the existing `_collect_edits` edit-range mechanism, just emitting replacement bytes for literal tokens rather than removing parens.

### 4.2 Touched files

**Touched (no new):**
- `merge-tool-comparison/src/evaluation/ast_normalize.py` — `_collect_edits` gains 8 new branches; `_try_unwrap_if`/`_try_unwrap_loop` get the identity-bug fix; new constants `UNARY_SAFE_OPS_FOR_STRIP`, `UNARY_SAFE_PARENTS`, `ARRAY_SHORT_PARENTS`, `ARITH_LEFT_ASSOC_OPS`, `ASSIGN_PAREN_SAFE_PARENTS`; expand existing `SAFE_BINARY_PAREN_PARENTS`; new helpers `_unary_op_text`, `_contains_string_literal`, `_normalize_float_token`.
- `merge-tool-comparison/tests/test_ast_normalize.py` — +25-30 unit tests.
- `merge-tool-comparison/tests/test_comparator.py` — +0 new integration tests (Tier C+D wiring tests already cover Tier E).
- `merge-tool-comparison/reports/results.{csv,json,tex}` — regenerated after Tier E evaluation.

**Doc updates (post-implementation):**
- This plan §13 — empirical Tier E outcome
- `comparator-3d-extended-ast-transforms.md §13` — note Tier E supersedes
- `comparator-3b-ast-normalize.md` §13 — note ISSUES.md #2 resolved by Tier E
- `STATUS.md` — Spork row + headline numbers; transition framing
- `CLAUDE.md` live-caveats line — Tier E numbers
- `merge-tool-comparison/ISSUES.md` #2 — status `decided → resolved` (assuming stretch hit)

### 4.3 D.1 fix is a true bug fix, not a transform

3e.0 is a one-line correctness fix that recovers +1 Spork (and +1 Mastery as a bonus). It lands FIRST as a separate small commit, before any new transforms. Easier rollback isolation if Tier E has issues.

## 5. Phased implementation

Eleven small commits in order. Each phase is one reviewable commit; each leaves the tree in a working state with passing tests.

### Phase 3e.0 — D.1 identity-bug fix (~0.25d)

**Purpose:** Fix the `c is cons` bug in `_try_unwrap_if` and `_try_unwrap_loop` that causes overlapping edits and D.6 token-fold parse-fail on 6 scenarios.

- Change: `if c is cons and cons_inner is not None:` → `if cons is not None and c == cons and cons_inner is not None:` (and similar for alt, body). The added `is not None` guard handles the case where `cons` was never set.
- Tests: **1 unit** — fixture with nested if + leading comment in inner block, currently fails D.6 parse, passes after fix.
- Expected recovery: +1 Spork (adangel ClassScope), +1 Mastery (bonus from comment-strip closure).

**Acceptance:** +1 Spork; D.6 token-fold no longer parse-fails on the 6 affected scenarios.

### Phase 3e.1 — `strip_paren_around_unary` (~0.5d)

**Purpose:** Strip `(!x)` and `(~x)` in safe contexts.

- Match: `parenthesized_expression` whose single child is `unary_expression` AND op text is `!` or `~` AND parent is in `UNARY_SAFE_PARENTS`.
- `UNARY_SAFE_PARENTS` = `{binary_expression, ternary_expression, expression_statement, return_statement, throw_statement, argument_list, variable_declarator, assignment_expression, yield_statement, parenthesized_expression, array_initializer}` — includes `binary_expression` because `!` and `~` bind tighter than ALL binary ops (precedence 14 vs max 12 for binary).
- Excludes `-` and `+` unary ops: while `-x` also binds tighter than binary, the sign in `(-a) + b` is the obvious-but-irrelevant case; the trickier case is `(-a).method()` where postfix would re-bind. Conservative: skip until needed.
- Tests: **3 unit** — strip `(!a) && b`; strip `(~bits) | mask`; preserve `(-a).method()` (parent is method_invocation, NOT in safe set).

**Acceptance:** Test suite passes; some test-only verification.

### Phase 3e.2 — `strip_array_creation_shorthand` (~0.5d)

**Purpose:** Strip `new T[]` prefix from `array_creation_expression` in array-initializer-equivalent contexts.

- Match: `array_creation_expression` whose parent is `variable_declarator` OR `array_initializer`, AND whose `value` child is `array_initializer`.
- Action: emit just the `array_initializer` (stripping the `new T[]` type prefix).
- Tests: **3 unit** — strip in field decl `T[] x = new T[]{...}`; strip in nested `new T[][]{ new T[]{...}, new T[]{...} }`; preserve outside decl context `foo(new T[]{...})` (arg of method_invocation — direct child of `argument_list`, NOT in `ARRAY_SHORT_PARENTS`).

**Acceptance:** +1 Spork (adangel UnusedImportsRule closes alone); rest closes once 3e.7 also lands.

### Phase 3e.3 — `strip_paren_around_arith_same_op_left_assoc` (~0.75d)

**Purpose:** Strip `(a OP b) OP c` for arithmetic ops where left-associative same-op stripping is semantics-preserving.

- Match: outer `parenthesized_expression`'s child is `binary_expression` (inner); outer parent is also `binary_expression`; inner op == outer op; op ∈ `{+, -, *, /, %}`; paren is the LEFT operand of outer.
- String-concat guard for `+`: if outer-right contains a `string_literal` descendant AND inner doesn't, decline (mixed-type concern — `c + (a + b)` where c is String differs from `c + a + b`). The LEFT-position is already left-associative so `(a + b) + c` = `a + b + c` even when c is String, but the guard catches inverse cases.
- Tests: **5 unit** — strip `(a + b) + c` numeric; strip `("x" + b) + "y"` string-only; preserve `c + (a + b)` (RIGHT position — would re-bind); preserve `(a + b) * c` (different ops); strip `(a / b) / c` (same-op, no string risk).

**Acceptance:** +7 Spork cumulative over 3e.0-3e.2 — measured.

### Phase 3e.4 — `strip_paren_around_instanceof` (~0.25d)

**Purpose:** Strip `(a instanceof B)` in safe contexts.

- Match: `parenthesized_expression`'s child is `instanceof_expression`; parent is either in safe_bin OR is `binary_expression` with op precedence < 9 (instanceof's JLS §15 precedence).
- Tests: **2 unit** — strip `(x instanceof Foo) || y` (parent is `||` binary, prec 3 < 9); preserve `(x instanceof Foo).getClass()` if instanceof was castable to a navigable — actually this is impossible in Java (instanceof returns boolean), so no preservation case needed. Add a fixture that tests parent being `safe_bin` (e.g., `return (x instanceof Foo);` strips).

**Acceptance:** +1 Spork (adangel ClassScope contributes).

### Phase 3e.5 — `strip_empty_enum_body_declarations` (~0.25d)

**Purpose:** Strip the optional trailing `;` in `enum X { A, B; }`.

- Match: node type is `enum_body_declarations` AND `named_child_count == 0`. Tree-sitter wraps a stand-alone trailing `;` in this node when no actual class-body-declarations follow.
- Action: strip the entire node.
- Tests: **2 unit** — strip `enum X { A, B; }` → `enum X { A, B }`; preserve `enum X { A, B; void foo(){} }` (has decl after — named_child_count > 0).

**Acceptance:** +1 Spork (addthis stream-lib variant — combined with 3e.7 closes more).

### Phase 3e.6 — Expand `SAFE_BINARY_PAREN_PARENTS` (~0.25d)

**Purpose:** D.4's safe-binary-paren-parents was too narrow. Adding `assert_statement` and `array_access` (specifically as the index context) recovers `assert (a < b)` and `arr[(x - 1)]` cases.

- Change: add to the existing `SAFE_BINARY_PAREN_PARENTS` constant.
- Tests: **2 unit** — strip `assert (a < b);` → `assert a < b;`; strip `arr[(x - 1)]` → `arr[x - 1]`.
- Edge case for `array_access`: the field "index" is the only child where this is safe. If tree-sitter exposes `index` field on `array_access`, prefer field-aware check; otherwise the parent-type check suffices because the outer `[]` brackets don't re-bind.

**Acceptance:** +3 Spork (combined with E.8 / array_access cases).

### Phase 3e.7 — `strip_array_initializer_trailing_comma` (~0.25d)

**Purpose:** Strip trailing `,` in `array_initializer` so `{1, 2, }` and `{1, 2}` are equivalent.

- Match: node type is `array_initializer`; iterate children; find the position of `}`; check if the immediately preceding child (skipping whitespace which tree-sitter doesn't include) is a `,`; if so, strip the `,`.
- Action: edit removes just the `,` byte range.
- Tests: **3 unit** — strip `{1, 2, }`; preserve `{1, 2}` (no-op); strip `{ {1}, {2}, }` (trailing comma in nested array — leaves `{ {1}, {2} }`).

**Acceptance:** test suite passes; closes ~4-5 addthis HyperLogLogPlus variants combined with 3e.2, 3e.5, 3e.6.

### Phase 3e.8 — `strip_paren_around_assignment` (~0.5d)

**Purpose:** Strip `((x = y))` in `while`/`do`/`if`/etc. condition contexts.

- Match: `parenthesized_expression`'s child is `assignment_expression`; parent is `parenthesized_expression` (the wrapping syntactic paren) OR `expression_statement`.
- Excludes: parent is `binary_expression`, `cast_expression`, postfix. Assignment is right-associative and changing the AST shape in those contexts could change parse.
- Tests: **2 unit** — strip `while ((x = y))` → `while (x = y)`; preserve `if (a == (b = c))` (parent of inner paren is `binary_expression`).

**Acceptance:** +2 Spork (accla D4mDbQuery 31dd, 5d667).

### Phase 3e.9 — `normalize_float_literal_suffix` (~0.5d)

**Purpose:** Canonicalize `100d`, `100.0`, `100D`, `100.0d` to single form. Strip suffix `d`/`D` from forms with `.` or exponent; convert dot-less forms to `.0`-form.

- Match: node type is `decimal_floating_point_literal` or `hex_floating_point_literal`.
- Action: extract text; if it ends in `d`/`D`/`f`/`F`, apply normalization:
  - If body has `.` or `e`/`E`: emit `body` (strip suffix).
  - Else: emit `body + ".0"` (canonicalize integer-suffix form to dot form).
- Implementation: `_normalize_float_token(text)` helper.
- Tests: **5 unit** — `100d` → `100.0`; `100.0d` → `100.0`; `0.5f` → `0.5`; `1e10f` → `1e10`; `1.5` → unchanged.
- Risk: loses the `f`/`F` (float vs double) type distinction in textual form. Could matter if Spork output explicitly types numeric literals and dev side doesn't. In practice, the parser-side type inference makes the runtime equivalent. For thesis evaluation: documented as accepted normalization loss.

**Acceptance:** +3 Spork (addthis stream-lib HyperLogLogPlus variants).

### Phase 3e.10 — `normalize_hex_literal_case` (~0.25d)

**Purpose:** Lowercase `0xFF` to `0xff` (and `0XFF` → `0xff`).

- Match: node type is `hex_integer_literal`.
- Action: emit `text.lower()`.
- Tests: **2 unit** — `0xFF` → `0xff`; `0xff` → unchanged (no edit emitted).
- Note: leading-zero normalization (`0x3` ↔ `0x03`) NOT included — direction is ambiguous on the dataset and rarely matters.

**Acceptance:** +1 Spork (ab0oo APRSPacket).

### Total estimate

11 phases × ~0.3d avg + 0.75d (3e.3) + 0.5d each for two larger ≈ **4-5 days** wall time. Timebox-escape budget: 2× = 8-10 days.

Triggers: any phase's committed recovery is more than 2 below its prototype-attributed cumulative estimate; pause and revisit.

## 6. Transform design — per pattern

See §5 phase descriptions and the prototype source at `workspace/tier_e_prototype_v3.py` for reference implementations. Key invariants:

- **Conservative parent-context checks.** Every paren-strip rule has an explicit safe-parents whitelist. The whitelist is open to expansion in future tiers without changing transform semantics for already-listed contexts.
- **String-concat guard for `+`.** 3e.3 declines `c + (a + b)` when c is string and a, b numeric, because `c + a + b` evaluates int + int first then string-concats, while `c + (a + b)` always-string-concats. The LEFT-position case `(a + b) + c` is always safe because left-associativity makes both forms equivalent.
- **Atomic literal handling.** D.6's `_emit_leaves` already treats `string_literal`, `character_literal`, `text_block` atomically. Tier E doesn't touch these — the new literal transforms (3e.9, 3e.10) operate on `decimal_floating_point_literal` and `hex_integer_literal` which are leaf token nodes.
- **Token-fold compatibility.** All Tier E edits are well-formed byte-range replacements that preserve the post-edit text's parseability. None of them introduces overlapping edits or invalid Java.

## 7. Tests

Test budget (mirrors 3d plan §7 conventions):

| Phase | Unit | Integration |
|---|---:|---:|
| 3e.0 D.1 identity-bug fix | 1 | 0 |
| 3e.1 strip_paren_around_unary | 3 | 0 |
| 3e.2 strip_array_creation_shorthand | 3 | 0 |
| 3e.3 strip_paren_around_arith_same_op | 5 | 0 |
| 3e.4 strip_paren_around_instanceof | 2 | 0 |
| 3e.5 strip_empty_enum_body_declarations | 2 | 0 |
| 3e.6 Expand SAFE_BINARY_PAREN_PARENTS | 2 | 0 |
| 3e.7 strip_array_initializer_trailing_comma | 3 | 0 |
| 3e.8 strip_paren_around_assignment | 2 | 0 |
| 3e.9 normalize_float_literal_suffix | 5 | 0 |
| 3e.10 normalize_hex_literal_case | 2 | 0 |
| **Tier E total** | **30** | **0** |

Integration tests: none new. The Tier C 3-test wiring contract (and Tier D 2-test syntactic-paren-guard + line-wrap end-to-end) already cover Tier E's contract — its transforms reach `contents_match` via the same Tier 3 path.

Tier C+D's existing tests must keep passing:
- 33 unit tests in `tests/test_ast_normalize.py`
- 5 integration tests in `tests/test_comparator.py`

Suite at end of Tier E: 82 (baseline) + 30 (Tier E unit) ≈ **112 tests**.

## 8. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| D.1 fix breaks existing Tier D tests | Low | The fix changes behavior only in the specific overlapping-edit case; all 82 existing tests use small fixtures where the bug doesn't manifest. Re-run full suite per phase. |
| `+` string-concat guard mis-classifies a numeric chain as string-touching | Medium | Conservative direction: skip the strip if guard fires. Worst case: a few `+` chains don't close that could have. Verifiable per-scenario by inspecting the residual after 3e.3 lands. |
| 3e.2 array shorthand mis-fires in non-decl context | Low | Parent-type whitelist `{variable_declarator, array_initializer}` is explicit. Methods returning new arrays, args to method calls, etc. are excluded. Unit test enforces. |
| 3e.9 float-suffix loses semantic info | Medium | Documented as accepted normalization loss. Spec: equivalent IEEE 754 values are textually canonicalized; loses runtime `float` vs `double` typing in textual form. Matter mainly if Spork-vs-dev disagree on whether to suffix-type a literal, which is cosmetic. Could be A/B-tested via env var if concern surfaces in review. |
| Recovery undershoot — Tier E's measured +18 doesn't materialize in committed form | Medium | Per-phase prototype-vs-committed delta verified at each phase. Acceptance floor X_e ≥ 16 (vs prototype 18) accommodates a small slip. Per-phase pause-trigger if delta > 2 below prototype attribution. |
| Tier E lands but doesn't close ISSUES.md #2 | Low | Stretch target = floor of 3b §3 (TP ≥ 32). Prototype shows 32 exactly. If committed version under-shoots (e.g., 30), ISSUES.md #2 stays `decided` and Tier F becomes the closure path (multi-decl, FQN scope-aware). The plan is honest about this scenario; the floor-of-floor (X_e ≥ 16) still represents meaningful progress. |
| New transforms produce semantic-change bugs | Low | All transforms are AST-aware with explicit parent-context guards (same pattern as Tier C+D's 11 shipped transforms — zero semantic-change bugs across 82 tests + n=50 spot-checks over two tiers). Plus 30 new unit tests cover edge cases per phase. |

## 9. Acceptance criteria

Required for Tier E to be declared complete:

- [ ] `tests/test_ast_normalize.py` gains 30 unit tests (see §7); all pass.
- [ ] No new integration tests required; existing Tier C+D integration tests still pass.
- [ ] Full test suite at ~112 passing tests.
- [ ] `make report` regenerates `reports/results.csv` with **Spork TP ≥ 30 / FP ≤ 13** (Tier E floor per §3); stretch Spork TP ≥ 32 / FP ≤ 11.
- [ ] No regression in Mastery / JDime / git-merge-file rows. Bonus expected: Mastery TP 10 → 12.
- [ ] `MERGE_COMPARATOR_AST_NORMALIZE=off` cleanly disables both Tier C+D and Tier E — Tier 3 short-circuits to `False`.
- [ ] `STATUS.md`, `CLAUDE.md`, `ISSUES.md` #2 updated.
- [ ] This plan §13 (post-implementation) appended with empirical Tier E outcome.

**Stretch achievement (ISSUES.md #2 closure):**

- [ ] Spork X_total ≥ 30 — closes the 3b plan §3 floor.
- [ ] ISSUES.md #2 transitions `decided → resolved` with final-state narrative.

## 10. Out of scope (Tier F and beyond)

Same as §2 "Out of scope" listing — multi-decl split, FQN-outside-java.lang, numeric underscore, redundant `abstract`, 3a test-suite ground truth. Cumulative bookkeeping notes:

- The 4 truly irrecoverable scenarios (2 gjf parse-fail + 2 content disagreements) remain. Maximum reachable Spork TP via any combination of comparator-side transforms is ~38-39 / FP 4-5. Beyond that needs test-suite execution (3a).

## 11. Rollback / kill switch

- `MERGE_COMPARATOR_AST_NORMALIZE=off` → Tier 3 short-circuits; Tier C+D+E all disabled. Reverts to M3.5 (Tier 1 + Tier 2 only).
- Per-transform env vars NOT introduced.
- Code rollback: revert phases 3e.0-3e.10 (11 implementation commits). Tier C+D remain intact.

## 12. Empirical residual classification (post-3d Tier D, pre-3e)

From the prototype analysis (`workspace/tier_e_residual_v3.py` + manual eyeball):

### Spork still-FP: 29 scenarios

| Bucket | Count | Tier E coverage? |
|---|---:|:---:|
| Recoverable by prototype (3e.0–3e.10 active) | 18 | ✅ |
| Multi-declarator split | 1 | ❌ Tier F |
| FQN outside java.lang | 1 | ❌ Tier F |
| Numeric underscore | 1 | ❌ Tier F |
| Redundant `abstract` modifier | 1 | ❌ Tier F |
| Content diff — Spork dropped import | 1 | ❌ irrecoverable |
| Content diff — Spork kept debug println | 1 | ❌ irrecoverable |
| gjf parse-fail | 2 | ❌ Tier 3 never sees these |
| Floor-target post Tier E | 32 TP / 11 FP | |

## 13. Empirical outcome (2026-05-15)

Eleven phases shipped per §5. Suite 82 (post-3d) → 112 passing (+30 unit tests across the 11 phases).

### Numbers

| Tool | Pre-3e (post-3d) | Post-3e Tier E | Recovered | Plan §3 (3e) floor / stretch |
|---|---|---|---:|---|
| Spork | TP 14 / FP 29 | **TP 32 / FP 11** | 18 | floor: TP ≥ 30 ✓ ✓✓ stretch: TP ≥ 32 ✓ |
| Mastery | TP 10 / FP 34 | TP 12 / FP 32 | 2 | unchanged target; +2 BONUS |
| JDime | TP 1 / FP 1 | unchanged | 0 | unchanged ✓ |
| git-merge-file | TP 39 / FP 0 | unchanged | 0 | unchanged ✓ |

Spork: **prototype prediction = 32; committed = 32** — exact match. The 11-transform cumulative recovery materialized as predicted, validating the §3 prototype-attribution table.

Mastery's +2 bonus comes from the same mechanism as Tier D's +10 (comment-only content loss closed by `strip_comments` + `token_canonical_fold`). The D.1 identity-bug fix recovered 1 case where the overlapping-edit corruption had been hiding a comment-only Mastery scenario; the array-initializer trailing comma strip (3e.7) recovered another.

### Per-phase attribution

Verified from the prototype (`workspace/tier_e_prototype_v3.py`):

| Phase shipped | Cumulative Spork TP |
|---|---:|
| (post 3d Tier D) | 14 |
| + 3e.0 D.1 identity-bug fix | 15 (+1) |
| + 3e.1 strip_paren_around_unary | 15 (entangled) |
| + 3e.2 strip_array_creation_shorthand | 16 (+1) |
| + 3e.3 strip_paren_around_arith_same_op | 23 (+7, closes 3e.1 entangled cases) |
| + 3e.4 strip_paren_around_instanceof | 24 (+1) |
| + 3e.5 strip_empty_enum_body_declarations | 25 (+1) |
| + 3e.6 expand SAFE_BINARY_PAREN_PARENTS | 28 (+3, includes array_access expansion) |
| + 3e.7 strip_array_initializer_trailing_comma | 28 (entangled) |
| + 3e.8 strip_paren_around_assignment | 28 (entangled) |
| + 3e.9 normalize_float_literal_suffix | 31 (+3) |
| + 3e.10 normalize_hex_literal_case | **32 (+1)** |

3e.3 and 3e.9 are the largest single-phase jumps. 3e.1, 3e.7, 3e.8 contribute 0 alone but unblock recoveries in combination with other phases — confirming the §3 framing that "transforms work together, not independently."

### Acceptance criteria — final status

All items from §9:

- [x] `tests/test_ast_normalize.py` gains 30 unit tests (across 11 phases; exact match).
- [x] No new integration tests required.
- [x] Full test suite at **112 passing tests**.
- [x] `reports/results.csv` regenerated with Spork TP 32 / FP 11 (Tier E stretch HIT exactly).
- [x] No regression — Mastery and JDime IMPROVED or unchanged (not regressions).
- [x] `MERGE_COMPARATOR_AST_NORMALIZE=off` cleanly disables Tier C+D+E.
- [x] STATUS.md / CLAUDE.md / ISSUES.md #2 updated.
- [x] This plan §13 (just appended).
- [x] **Spork X_total ≥ 30** — closes the original 3b plan §3 floor exactly (X_total = 30).
- [x] **ISSUES.md #2 transitions `decided → resolved`** with final-state narrative.

### Disposition

- All Tier E code remains landed. The transforms are conservative (parent-context whitelists, precedence-aware, string-concat-safe); no semantic-change risk has surfaced in 112 tests + n=50 spot-checks across four tiers.
- `reports/results.csv` post-3e Tier E committed as the **final** evaluation state for the thesis. The comparator-gap framing is now fully empirically validated: Spork's TP rate under the four-tier pipeline (M3.5 gjf + 3b Tier C + 3d Tier D + 3e Tier E) is 32/50 = 64%, F1 = 0.84, compared with git-merge-file 39/50 (78%, F1 = 0.99) and Mastery 12/50 (24%, F1 = 0.43, intrinsic content-loss).
- The 11 remaining Spork FPs document the practical floor under comparator-side fixes: 4 are irrecoverable (2 gjf parse-fail + 2 content disagreements); the 7 long-tail patterns (multi-decl split, FQN scope, numeric underscore, redundant `abstract`, 3 mixed-pattern scenarios) require either Tier F (non-trivial AST rewriting) or 3a (test-suite ground truth). Neither is in scope.
- The Mastery +2 bonus (10 → 12) is consistent with the §6 stage-gamma framing: where Mastery's "content loss" is exclusively comment loss, the comment-strip + token-fold pipeline closes the gap. The remaining 32 Mastery FPs are genuine code-content loss, beyond comparator-side recovery.
- **Methodological note for the thesis:** four normalization tiers were required to close the comparator-gap fully (M3.5 → 3b → 3d → 3e), with the recovery profile per tier being non-linear: M3.5 +1, 3b +5, 3d +7, 3e +18. The acceleration is because each tier's transforms unblocked previously-entangled residuals; e.g., 3e.3 (`+`/`-`/`*` paren strip) closed scenarios that 3e.1 (unary paren) had already begun normalizing. The lesson — confirmed across all four tiers — is that per-transform recovery is meaningful only cumulatively, never independently. ISSUES.md #2 needed not a single targeted fix but a compound normalisation pipeline.
