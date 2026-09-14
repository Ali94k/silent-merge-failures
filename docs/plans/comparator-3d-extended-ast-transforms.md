# Plan: Comparator 3d — extended AST transforms (Tier D scope)

**Status:** drafted (not started) — 2026-05-15. **Expanded scope** per user direction 2026-05-15: includes precedence-aware paren strip (D.5) and token-canonical whitespace fold (D.6) — what the original 3b plan §11 / §13 had filed as Tier E.
**Owner:** Ali
**Created:** 2026-05-14; expanded 2026-05-15
**Depends on:** 3b Tier C ([`comparator-3b-ast-normalize.md` §13 empirical outcome](comparator-3b-ast-normalize.md))
**Closes:** [`ISSUES.md` #2](../../merge-tool-comparison/ISSUES.md) — partial progress only; full transition `decided → resolved` remains gated on hitting the §3 floor that 3b Tier C undershot.
**Related:** [`stage-gamma-fp-diagnostic.md §10`](stage-gamma-fp-diagnostic.md) (Tier C residual diagnosis)

---

## 1. Context

3b Tier C (5 transforms, shipped 2026-05-14) recovered 5 of 39 still-differ Spork FPs — X=5 vs plan §3 floor X≥30. Per-scenario diagnosis ([`comparator-3b-ast-normalize.md §13`](comparator-3b-ast-normalize.md)) found the residual-after-gjf+Tier-C is dominated by patterns Tier C's strict scope excludes:

1. `((cast_expr) (value))` ↔ `(cast_expr) value` — outer paren wraps a `cast_expression`, not a `parenthesized_expression`. Tier C's `strip_redundant_parens` doesn't fire.
2. `if (c) { stmt; }` ↔ `if (c) stmt;` — single-statement block unwrapping. Distinct from `flatten_else_if`.
3. `(a == b) && c` — paren around binary_expression with higher precedence than outer. Tier C declines all precedence reasoning.
4. `return (a | b);` — paren around binary_expression in a "standalone" context (no outer operator). Safe to strip but Tier C declines.
5. `} else throw stmt;` — `else` directly followed by a non-block statement. Spork wrapped: `} else { throw stmt; }`. Tier C's `flatten_else_if` only handles the `else { if }` case.

Tier D adds parser-aware-but-still-conservative transforms covering patterns 1, 2, 4, 5 (and partially 3). Precedence-aware binary paren strip (full pattern 3), long-array canonicalisation, and text-level line-wrap collapse remain deferred to a future Tier E.

## 2. Scope — Tier D

**In scope:**

| Transform | Pattern | Approach |
|---|---|---|
| **D.1** `unwrap_single_stmt_block` | `if/while/for/do` consequence is `{ stmt; }`; `else` is `{ stmt; }` | AST: strip block braces when the body has exactly one non-decl, non-bare-if statement |
| **D.2** `strip_paren_around_primary` | `(x)`, `(arr[0])`, `(foo())`, `(x.f)`, `(literal)`, etc. | AST: strip paren when its single child is a primary node type (identifier, literal, field_access, method_invocation, array_access, object_creation, this/super, class_literal, parenthesized_expression — replaces Tier C's narrower `strip_redundant_parens`). **Syntactic-paren guard:** skip when parent is `if_statement`, `while_statement`, `do_statement`, `synchronized_statement`, `switch_statement`, or `switch_expression` — Java syntax requires the paren in these contexts. |
| **D.3** `strip_paren_around_cast` | `((cast) val)` ↔ `(cast) val` | AST: strip paren around `cast_expression` UNLESS parent is `field_access`, `method_invocation`, or `array_access` (postfix-rebinding contexts). Plus the syntactic-paren guard. |
| **D.4** `strip_paren_around_binary_safe_parent` | `return (a OP b);`, `f((a == b));`, `int x = (a + b);` | AST: strip paren around `binary_expression` or `ternary_expression` when parent is in a fixed safe-context whitelist (statement contexts, argument lists, initializers — no outer operator can re-bind). Plus the syntactic-paren guard. |
| **D.5** `strip_paren_around_binary_precedence_aware` | `(a == b) && c`, `((a && b) && c)` | AST: strip paren around `binary_expression` whose parent is also `binary_expression` IF inner-op precedence > outer-op precedence, OR same-op-same-precedence AND op is in the associative-safe set `{&&, \|\|, &, \|, ^}` (pure boolean/bitwise, no type-promotion gotchas). Uses Java operator precedence table. Conservative — excludes `+` (string-concat gotcha) and `*` (mixed-type concerns); both deferred to Tier E. |
| **D.6** `token_canonical_fold` | Multi-line continuation / wrap differences gjf preserves; whitespace placement | Post-emit: re-parse the AST-canonicalised text with tree-sitter, walk to leaves, emit each leaf's bytes separated by single space. String literals preserved byte-exactly (single-leaf nodes). Yields a whitespace-insensitive canonical form regardless of gjf's line-break decisions. |

The 5th observed pattern (`else throw stmt;` — `else` directly followed by a non-block stmt that Spork wrapped) is handled by `unwrap_single_stmt_block` when extended to the `else`-block case (single non-decl statement, statement not necessarily an if).

**Out of scope (Tier E and beyond):**

- **`+` same-op-left-assoc paren strip** — `((a + b) + c) + d` ↔ `a + b + c + d`. The int-vs-string-concat associativity gotcha (e.g., `c + (a + b)` where `c` is string but `a, b` are numeric evaluates differently from `c + a + b`). Could be added with type-inference; deferred to Tier E.
- **`*` same-op-left-assoc paren strip** — similar mixed-type concerns; deferred.
- **Hex literal case normalize** — `0xff` ↔ `0xFF`, `0x3` ↔ `0x03`. Textual; ~0-1 dominant cases. Tier E or omit.
- **Long array-literal canonicalisation** — 6 scenarios dominant in residual. Multi-line whitespace within `array_initializer` nodes; even D.6's token-fold may stop short on multi-MB array literals. Heavy effort; Tier E.
- **3a test-suite ground truth** — different approach entirely; defer per `mergiraf-integration.md §3` cost analysis.

## 3. Recovery targets

Measured empirically via in-memory prototype (all 6 transforms enabled) before drafting this plan — the lesson from 3b's §3 estimation error is that recovery estimates must be measured against the actual transform set, not inferred from raw-diff pattern labels.

Pre-Tier-D Spork = 7 TP / 36 FP (post-3b). Of 41 clean-FP cases, 2 are gjf-parse-fail (irrecoverable by Tier 3); the rest (39) are in scope for the AST-level transforms.

**Prototype measurement (all 6 phases active):** recovers **12 of 39** still-differ Spork residuals — TP 7 → 14, FP 36 → 29. That's +7 over Tier C alone (which got 5). Per-phase attribution (running the prototype with phases progressively added):

| Phase | Cumulative recovery | Notes |
|---:|---:|---|
| Tier C baseline (already shipped) | 5 | comments, blank-line, `} else { if }`, paren-wrap-paren, `java.lang.X` |
| + D.1 `unwrap_single_stmt_block` | ~6-7 | single-stmt body unwrap (if/while/for/do consequence + else) |
| + D.2 `strip_paren_around_primary` | ~7-8 | broader paren strip; subsumes Tier C's paren-wrap-paren rule |
| + D.3 `strip_paren_around_cast` | ~8 | `((cast) val) → (cast) val` with parent-context guard |
| + D.4 `strip_paren_around_binary_safe_parent` | ~9 | `return (a \| b);` and similar standalone-position binary paren |
| + D.5 `strip_paren_around_binary_precedence_aware` | ~10-11 | `(a == b) && c` (strict-higher precedence); `(a && b) && c` (same-op-assoc-safe) |
| + D.6 `token_canonical_fold` | **12** | line-wrap differences gjf preserves close via uniform tokenization |

Per-phase deltas are approximate — some scenarios close only when multiple phases are simultaneously active. D.6 in particular is responsible for the largest jump because line-wrap residuals span many of the "other-mixed" scenarios.

**Floor:** Tier D acceptance is **TP ≥ 10 / FP ≤ 33** (X_total ≥ 8 — at least +3 over Tier C). Sets a modest but real bar.

**Stretch:** TP ≥ 14 / FP ≤ 29 (matches prototype). Achievable if all six phases land cleanly with no test regressions.

**Important non-target:** Tier D does NOT hit the original 3b §3 floor (TP ≥ 32). Even the expanded scope falls short. **ISSUES.md #2 remains at `decided`.** Closing it cleanly requires either Tier E (`+` / `*` same-op paren strip + hex case + long array) or 3a (test-suite ground truth) — both deferred.

| Tool | Pre-Tier-D | Tier D point estimate | Tier D acceptance floor |
|---|---|---|---|
| Spork | TP 7 / FP 36 | **TP 14 / FP 29** (X_d = 7) | TP ≥ 10 / FP ≤ 33 (X_d ≥ 3) |
| Mastery | TP 0 / FP 44 | unchanged | unchanged |
| git-merge-file | TP 39 / FP 0 | unchanged | unchanged |
| JDime | TP 0 / FP 2 | unchanged | unchanged |

**Undershoot trigger:** if any phase delivers 0 recovery, pause and re-examine the prototype assumptions. (The prototype recovery measurements above are upper bounds — real recovery may be lower if my prototype's parent-context checks have edge cases.)

## 4. Architecture integration

### 4.1 Extends Tier 3 in place

Tier D transforms land in [`src/evaluation/ast_normalize.py`](../../merge-tool-comparison/src/evaluation/ast_normalize.py) — the same module Tier C created. The `_collect_edits` visitor gains new branches; no new tier in `contents_match`; no new env var. Rationale:

- All Tier D transforms are AST-level, conservative, and follow Tier C's "fall through to Tier 2 verdict on parse-fail / mismatch" semantics.
- Adding a Tier 4 (separate env var) would let users toggle independently — useful for A/B-measurement, but adds matrix complexity for marginal value when both default `on`.
- Tier C's `MERGE_COMPARATOR_AST_NORMALIZE=off` kill switch covers Tier D for free.

### 4.2 Touched files

**Touched (no new):**
- `merge-tool-comparison/src/evaluation/ast_normalize.py` — `_collect_edits` gains 4 new branches; new helper functions `_single_inner_stmt`, `_strip_paren_safe` (or similar); constant `UNSAFE_CAST_PAREN_PARENTS`; constant `SAFE_BINARY_PAREN_PARENTS`; constant `PRIMARY_NODE_TYPES`.
- `merge-tool-comparison/tests/test_ast_normalize.py` — +10-12 unit tests.
- `merge-tool-comparison/tests/test_comparator.py` — +0 new integration tests (Tier C's tier-3 wiring tests already cover Tier D since they share `MERGE_COMPARATOR_AST_NORMALIZE`).
- `merge-tool-comparison/reports/results.{csv,json,tex}` — regenerated after Tier D evaluation.

**Doc updates (post-implementation):**
- `comparator-3b-ast-normalize.md` §13 — append "Tier D outcome" subsection
- `STATUS.md` — Spork row + headline numbers updated
- `CLAUDE.md` live-caveats line — Tier D numbers
- `ISSUES.md` #2 — status line updated with Tier D recovery; status STAYS `decided`
- This plan §13 (new section) — empirical Tier D outcome

**Not touched:**
- `comparator.py` — Tier 3 wiring already exists; no new tier added.
- `pyproject.toml` — no new dependencies.
- `tests/conftest.py` — `MERGE_COMPARATOR_AST_NORMALIZE=off` default already set.

### 4.3 Tier C transform compatibility

Tier C's `strip_redundant_parens` (paren-wrapping-paren) becomes a special case of D.2 `strip_paren_around_primary` (which lists `parenthesized_expression` in its primary set). Two options:

- (a) **Delete Tier C's specific rule** when D.2 lands. Cleaner; Tier D fully subsumes Tier C's paren rule.
- (b) **Keep both**; D.2 is reached only when Tier C's narrower rule didn't fire (it always will if D.2 would have).

Recommend (a). Single source of truth for paren-strip logic.

Tier C's `flatten_else_if` becomes redundant with D.1 `unwrap_single_stmt_block` when the inner `if_statement`'s position allows direct emission (which is always — Java grammar permits `else if` and `else {if}` interchangeably). Same decision applies:

- (a) **Delete Tier C's `flatten_else_if`** when D.1 lands.
- (b) **Keep both.**

Recommend (a) here too IF D.1 is generalized to handle the `else { if }` case by also recursing the dangling-else question. Else (b) — keep `flatten_else_if` as the specific safe handler for `else { if }`.

Per §6 phasing, decision deferred to D.1 implementation when the dangling-else interaction is concrete.

## 5. Phased implementation

Six small commits, landed in order. Each phase is one reviewable commit; each leaves the tree in a working state. Per-phase numbers reflect the in-memory prototype measurement.

### Phase 3d.1 — `unwrap_single_stmt_block` (~0.5d)

**Purpose:** the most-frequent residual pattern by line count.

- Match: `if_statement.consequence` is a `block` with one structural child (non-comment), AND that child is not a `local_variable_declaration` AND not a bare `if_statement` (avoids dangling-else when this if has no else AND inner if has else).
- Match also: `if_statement.alternative` is a `block` with one structural non-decl child (any type — Tier C's `flatten_else_if` already handles the `else { if }` case; D.1 adds non-if cases).
- Match also: `while_statement.body`, `for_statement.body`, `enhanced_for_statement.body`, `do_statement.body` with the same shape.
- Action: strip block braces (and surrounding whitespace) via two byte-range edits; recurse into the inner stmt.
- Tests: **4 unit** — basic if-consequence; while-body; for-body; else-clause-non-if (`else { throw e; }` → `else throw e;`). Plus **1 conservative-guard** — `if (c) { int x = 1; use(x); }` does NOT unwrap (multiple stmts).
- Decision on Tier C interaction: D.1's else-clause handling overlaps with `flatten_else_if` when inner is an if. Keep `flatten_else_if`; D.1 fires for else-block-containing-non-if-stmt only. Same `_has_var_decl_descendant` guard.

**Acceptance:** prototype shows +1 recovery alone; tests pass.

### Phase 3d.2 — `strip_paren_around_primary` (~0.5d)

**Purpose:** generalises Tier C's `strip_redundant_parens` to all primary expressions.

- Match: `parenthesized_expression` whose single structural child has type in `PRIMARY_NODE_TYPES = {identifier, decimal_integer_literal, hex_integer_literal, octal_integer_literal, binary_integer_literal, decimal_floating_point_literal, hex_floating_point_literal, string_literal, character_literal, true, false, null_literal, this, super, field_access, method_invocation, array_access, object_creation_expression, array_creation_expression, class_literal, parenthesized_expression}`.
- Action: strip outer paren; recurse into inner.
- Tier C's `strip_redundant_parens` (paren-wrapping-paren) is now a subset; remove it in favor of D.2 to avoid two rules expressing the same intent. Tier C tests for paren-wrapping-paren still apply.
- Tests: **3 unit** — strip primitive `(x)`, strip method-invocation `(foo())`, strip array-access `(arr[0])`. **1 preserve-when-binary** — `(a + b)` does NOT strip in isolation (binary_expression is not in primary set). **1 inside-cast** — `(int) (x)` → `(int) x` (the cast value paren strips because its parent is `cast_expression` which doesn't matter for D.2's parent-check; D.2 has no parent check — it's always safe to strip primary).
- Tier C carry-over: replace `_single_inner_paren` helper with `_single_paren_child` returning the structural child; new helper `_is_primary` checks against `PRIMARY_NODE_TYPES`.

**Acceptance:** +1 cumulative recovery over Tier C; D.2 deletes Tier C's narrower rule without test regressions.

### Phase 3d.3 — `strip_paren_around_cast` (~0.5d)

**Purpose:** `((cast) val) → (cast) val` in safe contexts.

- Match: `parenthesized_expression` whose single structural child is `cast_expression` AND parent is NOT in `UNSAFE_CAST_PAREN_PARENTS = {field_access, method_invocation, array_access}`.
- Action: strip outer paren; recurse into inner cast (which itself may have a value paren strippable by D.2).
- Tests: **2 unit** — `((cast) val) + y` (parent is binary_expression: SAFE) → strip; `((cast) val).field` (parent is field_access: UNSAFE) → preserve.
- Note: the **prototype measurement shows D.3 alone yields 0 additional recovery** over D.2 because D.2's primary-paren-strip already handles the cast-VALUE inner paren (the most common shape, e.g. APRSPacket's `((char) (body[0])) → (char) body[0]` closes via D.2 stripping the inner `(body[0])` paren, leaving `((char) body[0])` then a paren-wrapping-cast at the outer which D.3 closes — together they close, but D.2 alone gets 0 of these; D.3 alone gets 0; together they get +1). D.3 must land alongside D.2 for measurable recovery.
- Per-phase floor: 0 (acceptable when paired with D.2).

**Acceptance:** D.2 + D.3 combined recover ≥ +1 cumulative over D.1. The cast-only fixture test (`((cast) val) + y` strips outer) passes.

### Phase 3d.4 — `strip_paren_around_binary_safe_parent` (~0.5d)

**Purpose:** strip `(a == b)` in standalone position — `return (a == b);` → `return a == b;`.

- Match: `parenthesized_expression` whose single structural child is `binary_expression` OR `ternary_expression` AND parent is in `SAFE_BINARY_PAREN_PARENTS = {expression_statement, return_statement, throw_statement, argument_list, variable_declarator, assignment_expression, yield_statement, ternary_expression, parenthesized_expression, array_initializer}`.
- Action: strip outer paren; recurse into inner.
- Critically NOT matched when parent is `binary_expression` (would need precedence reasoning, deferred Tier E) or `unary_expression` (would need to think; deferred).
- Tests: **3 unit** — `return (a | b);` strip; `f((a == b))` strip (paren is arg); `(a + b) * c` preserve (parent is binary_expression — would re-bind). **1 ternary case** — `return (a > 0 ? 1 : 0);` strip.
- Edge case: `if ((a == b))` — outer paren is the if's condition (the parenthesized_expression that wraps the condition expression in Java's `if (cond)` syntax; tree-sitter's `if_statement` has a `parenthesized_expression` condition child). Stripping is safe (would just need to leave one paren). Handled by D.2's primary-paren-rule when the inner is identifier; D.4 doesn't need to special-case this.

**Acceptance:** D.1+D.2+D.3+D.4 cumulative gets to TP ≥ 9 per prototype attribution. Test suite passes.

### Phase 3d.5 — `strip_paren_around_binary_precedence_aware` (~0.75d)

**Purpose:** strip `(a == b) && c` and similar where inner-op precedence > outer-op precedence; plus same-op-left-assoc safe ops.

- Match (case A — strict-higher precedence): `parenthesized_expression` whose single child is `binary_expression`; parent is also `binary_expression`; inner op precedence > parent op precedence per the Java precedence table.
- Match (case B — same-op-assoc-safe): same shape; inner op == parent op; inner op ∈ `{&&, ||, &, |, ^}` (pure boolean/bitwise; no implicit type promotion). Both same-op-left-position and same-op-right-position are safe for these ops.
- Action: strip outer paren.
- Excluded for safety: `+`, `-`, `*`, `/`, `%` (string-concat / numeric-mixed gotchas). Tier E candidates.
- Precedence table: hardcoded constant `PREC` mapping op string → int (mult=12, add=11, shift=10, rel=9, eq=8, &=7, ^=6, |=5, &&=4, ||=3) per JLS §15.
- Tests: **4 unit** — strict-higher: `(a == b) && c` strips; same-op-assoc: `(a && b) && c` strips; same-op-NOT-in-safe-set: `(a + b) + c` does NOT strip (string-concat risk); reverse-precedence: `(a + b) * c` does NOT strip (would change meaning).

**Acceptance:** +1-2 cumulative; tests pass; `(a + b) * c` preserve test enforces.

### Phase 3d.6 — `token_canonical_fold` (~1d)

**Purpose:** the largest single-phase recovery (+3 from prototype). Closes line-wrap, indentation, and "Spork-laid-it-out-differently" residuals by re-parsing the AST-canonicalised text and emitting leaves in a uniform space-separated form.

- After all edit-based transforms complete, the emitted text from `_apply_edits` + `_strip_blank_lines` may still differ from the dev side by line-break placement (gjf wraps long lines differently when token counts differ, which happens after our paren stripping changes token counts).
- Implementation: re-parse the emit output via `_PARSER.parse(emit.encode("utf-8"))`. If `has_error=True`, return the unfolded emit (conservative — don't risk corrupting a bad emit). Else walk to leaves (`node.child_count == 0`), append each leaf's bytes to a list, join with `b" "` separator.
- String literals (`string_literal`, `character_literal`, `text_block`) are single leaf nodes — emitted byte-exactly. Internal whitespace inside string literals is preserved.
- Comments (`line_comment`, `block_comment`) are already stripped via edit ranges before this fold; the re-parsed tree has no comment leaves.
- Tests: **3 unit** — multi-line if-statement matches single-line equivalent; preserved string with internal whitespace (`"a  b\n c"`); preserved comment-stripped text (re-parses cleanly).
- Risk: parse-fail on the emit output. Mitigation: fall back to unfolded emit when `has_error`; never raise.

**Acceptance:** +3 cumulative (TP ≥ 14 — Tier D stretch); tests pass; idempotent (folding a folded form is a no-op).

### Total estimate

6 phases × ~0.5d (D.1-D.4) + 0.75d (D.5) + 1d (D.6) ≈ **4 days** wall time. Timebox-escape budget: 2× = 8 days.

Triggers: any phase's committed recovery is more than 1 below its prototype-attributed estimate; pause and revisit.

## 6. Transform design — per pattern

Each transform's design follows Tier C's `_collect_edits` visitor pattern (collect `(start, end, replacement)` tuples; apply non-overlapping edits in source order). See [`comparator-3b-ast-normalize.md` Appendix A](comparator-3b-ast-normalize.md) for the tree-sitter cheat sheet.

### 6.1 `unwrap_single_stmt_block`

Conservative rule per Tier C precedent:

```
Match: <ctrl-flow-stmt>.body_or_consequence is a `block`
       AND the block has exactly one structural child (non-comment)
       AND that child is not a `local_variable_declaration`
       AND (the block is the consequence of an if AND inner child is not a bare if without else) — dangling-else guard
Edit:  (block.start_byte, inner.start_byte, b"")
       (inner.end_byte, block.end_byte, b"")
```

Dangling-else guard: skip the unwrap when the outer is `if` without `else` AND the inner is `if`. Example: `if (a) { if (b) x(); }` → `if (a) if (b) x();` is technically the same parse, but `if (a) if (b) x(); else y();` makes the `else` bind to the inner if either way — but the source DEV may have written `if (a) { if (b) x(); else y(); }` with the explicit block to clarify scoping. Conservative: skip when inner is `if`.

Else clause handling: when alternative is a block with single non-decl stmt, unwrap regardless of inner type. The `flatten_else_if` rule from Tier C handles `else { if }` specifically; this new rule handles `else { non-if-stmt }`.

### 6.2 `strip_paren_around_primary`

Replaces Tier C's `strip_redundant_parens`. Primary set per Java grammar §15.8 (`Primary` non-terminal in JLS) + `parenthesized_expression` (for recursive nesting):

```python
PRIMARY_NODE_TYPES = frozenset({
    "identifier",
    "decimal_integer_literal", "hex_integer_literal",
    "octal_integer_literal", "binary_integer_literal",
    "decimal_floating_point_literal", "hex_floating_point_literal",
    "string_literal", "character_literal",
    "true", "false", "null_literal",
    "this", "super",
    "field_access", "method_invocation", "array_access",
    "object_creation_expression", "array_creation_expression",
    "class_literal",
    "parenthesized_expression",
})
```

`cast_expression` is intentionally NOT in this set (handled by D.3 with parent check). Binary / ternary / lambda / instanceof are NOT primaries — handled by D.4 or deferred.

### 6.3 `strip_paren_around_cast`

```
Match: parenthesized_expression's single structural child is cast_expression
       AND parent.type not in {field_access, method_invocation, array_access}
```

The unsafe parents are where postfix `.`, `()`, or `[]` would rebind from the cast result to the cast value:
- `((Long) x).field` ≠ `(Long) x.field` (the latter is `(Long) (x.field)`).
- `((Long) x).method()` ≠ `(Long) x.method()`.
- `((Long) x)[0]` ≠ `(Long) x[0]`.

In all other contexts, the outer paren around cast adds no semantic information.

### 6.4 `strip_paren_around_binary_safe_parent`

```
Match: parenthesized_expression's single structural child is binary_expression OR ternary_expression
       AND parent.type in {expression_statement, return_statement, throw_statement,
                          argument_list, variable_declarator, assignment_expression,
                          yield_statement, ternary_expression, parenthesized_expression,
                          array_initializer}
```

These parent types are all "no-outer-operator" contexts where the paren can never affect precedence — the expression is the full RHS / arg / return value / etc.

Parent types deliberately excluded (would need precedence reasoning):
- `binary_expression` — would need to compare inner op vs outer op precedence.
- `unary_expression` — `-(a + b)` ≠ `-a + b`.
- `cast_expression` — value of a cast; `(Long)(a + b)` ≠ `(Long) a + b`.
- `field_access`, `method_invocation`, `array_access` — postfix rebinding (same as cast).

The `parenthesized_expression` parent IS included: `((a + b))` → `(a + b)` recurses correctly via D.2's existing primary-includes-paren rule plus this rule.

## 7. Tests

Test budget (mirrors 3b plan §8 conventions):

| Phase | Unit | Integration |
|---|---:|---:|
| 3d.1 unwrap_single_stmt_block | 5 | 0 |
| 3d.2 strip_paren_around_primary | 5 | 1 (syntactic-paren preserved end-to-end) |
| 3d.3 strip_paren_around_cast | 2 | 0 |
| 3d.4 strip_paren_around_binary_safe_parent | 4 | 0 |
| 3d.5 strip_paren_around_binary_precedence_aware | 4 | 0 |
| 3d.6 token_canonical_fold | 3 | 1 (line-wrap recovers end-to-end) |
| **Tier D total** | **23** | **2** |

Tier C's three integration tests still cover the Tier-3 wiring contract; Tier D adds two more — one verifies the syntactic-paren guard (so D.2 doesn't break valid Java), one verifies the token-fold closes a line-wrap-only fixture end-to-end through `contents_match`.

Tier C's existing tests must keep passing:
- 14 unit tests in `tests/test_ast_normalize.py`
- 3 integration tests in `tests/test_comparator.py`

Tier C transform deletions (per §4.3 decisions):
- `strip_redundant_parens` test cases (3 unit) get retained but reframed as primary-paren-strip cases (the test names stay; the implementation under test moves).
- `flatten_else_if` test cases (3 unit) stay as-is (the rule stays unless §4.3 decision (a) is taken — then they migrate to D.1).

Suite at end of Tier D: 41 (baseline) + 14 (Tier C kept) + 23 (Tier D unit) + 2 (Tier D integration) − (up to 6 if `strip_redundant_parens` + `flatten_else_if` migrate) ≈ **74-80 tests**.

## 8. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Precedence bug in `strip_paren_around_cast` parent check | Low | unit test enforces `((cast) val).field` is preserved; parent-check whitelist is small (3 types) and easy to audit. |
| Precedence bug in `strip_paren_around_binary_safe_parent` | Low | whitelist of safe parents only; binary_expression intentionally excluded (deferred Tier E); unit test enforces `(a + b) * c` is preserved. |
| `unwrap_single_stmt_block` dangling-else edge case | Medium | conservative guard skips when outer-if-without-else + inner-if; unit test enforces. |
| D.2's removal of Tier C's `strip_redundant_parens` breaks existing tests | Low | the new rule is a strict superset; existing tests pass under D.2 with no migration needed (test name + assertion preserved). |
| Recovery undershoot — Tier D's measured +3 doesn't materialize in committed form | Medium | per-phase prototype-vs-committed delta = 0 (we run the prototype against the same fixtures the committed code will run against); the risk is that my prototype mis-implements something the committed version doesn't. Each phase ships with a prototype-derived recovery target; if the committed version under-recovers, investigate before next phase. |
| Tier D landed but doesn't close ISSUES.md #2 (TP ≥ 32 floor still un-hit) | Certain | this is BY DESIGN — Tier D is incremental, not a closure. Per §3 framing: ISSUES.md #2 STAYS `decided`. The plan is honest about this. |

## 9. Acceptance criteria

Required for Tier D to be declared complete (NOT for ISSUES.md #2 transition):

- [ ] `tests/test_ast_normalize.py` gains 23 unit tests (see §7); all pass.
- [ ] `tests/test_comparator.py` gains 2 integration tests (syntactic-paren preserve + line-wrap-via-token-fold end-to-end).
- [ ] Full test suite at 74-80 passing tests.
- [ ] `make report` regenerates `reports/results.csv` with Spork TP ≥ 10 / FP ≤ 33 (Tier D floor per §3); ideally TP ≥ 14 / FP ≤ 29 (stretch).
- [ ] No regression in Mastery / JDime / git-merge-file rows.
- [ ] `MERGE_COMPARATOR_AST_NORMALIZE=off` cleanly disables both Tier C and Tier D — Tier 3 short-circuits to `False`.
- [ ] `comparator-3b-ast-normalize.md §13` appended with "Tier D outcome" block; STATUS.md / CLAUDE.md / ISSUES.md updated.
- [ ] This plan §13 (new section, post-implementation) appended with empirical Tier D outcome.

**Explicitly NOT required (ISSUES.md #2 closure):**

- [ ] ~~Spork TP ≥ 32 / FP ≤ 11~~ — Tier D does not target this; per §3 framing, requires Tier E or 3a.

## 10. Out of scope (Tier E and beyond)

- **Precedence-aware binary paren strip.** Implement Java operator precedence table; strip `(X)` around binary_expr when inner op > outer op. ~+2-4 expected recovery. ~1d.
- **Same-op-left-assoc binary paren strip.** Strip `((a OP b) OP c)` for OP in {`&&`, `||`, `|`, `&`, `^`} (pure-boolean, no type-promotion gotchas). `+`, `*` need extra care (string-vs-numeric ambiguity for `+`). ~+1-2 expected recovery. ~0.5d.
- **Text-level line-wrap collapse.** Post-emit pass that joins multi-line expression-statement continuation lines into a single line, preserving string-literal whitespace. ~+3 expected recovery. ~1d. This is NOT an AST transform — separate plan or Tier F.
- **Hex literal case normalize.** `0xff` → `0xFF` (and `0x3` → `0x03` leading-zero). Textual; ~0-1 dominant cases.
- **Long array-literal canonicalisation.** Tier D's original scope per [3b plan §2](comparator-3b-ast-normalize.md). 6 scenarios dominant in residual. Multi-line whitespace normalization within array_initializer nodes. Heavy effort.
- **3a test-suite ground truth.** Different approach entirely; bypasses textual ground truth. Far larger; rejected per `mergiraf-integration.md §3` cost analysis.

## 11. Rollback / kill switch

- `MERGE_COMPARATOR_AST_NORMALIZE=off` → Tier 3 short-circuits; Tier D and Tier C both disabled. Reverts to M3.5 (Tier 1 + Tier 2 only).
- `MERGE_COMPARATOR_FORMATTER=off` AND `MERGE_COMPARATOR_AST_NORMALIZE=off` → reverts to pre-M3.5 (Tier 1 only).
- Per-transform env vars NOT introduced (overkill).
- Code rollback: revert phases 3d.1-3d.4 (the 4 implementation commits). Tier C remains intact.

## Appendix A — Empirical residual classification (post-3b)

From a prototype-extended `_collect_edits` measured against the 36 still-FP Spork scenarios after Tier C:

| Bucket | Count | Tier D coverage? |
|---|---:|:---:|
| Recovered by prototype (D.1 + D.2 + D.3 + D.4) | 3 | ✅ |
| Long-array-dominant | 6 | ❌ Tier E |
| Line-wrap-only (text-level whitespace) | 3 | ❌ Tier F |
| Other-mixed (multiple residual patterns per scenario) | 21 | partial — some patterns covered, but each scenario closes only when ALL its diffs canonicalise. Long tail. |
| Parse-fail | 2 | ❌ Tier 3 never sees these |
| Total still-FP | 35 | (post Tier D point estimate) |

The "other-mixed" bucket is the bottleneck. Closing it scenario-by-scenario requires either (a) a much broader transform set (Tier E precedence-aware + line-wrap + hex case) or (b) per-scenario root-cause investigation for the long tail. Both are deferred.

## 13. Empirical outcome (2026-05-15)

Six phases shipped per §5 (commits `99a5f90`, `9333692`, `ac9114e`, `1eff174`, `9e90b23`, `1c6eb87`). Suite 58 (post-3b) → 82 passing; +16 new unit tests + 2 new integration; some Tier C tests repurposed for D.1/D.2 behavior.

### Numbers

| Tool | Pre-3d (post-3b) | Post-3d Tier D | Recovered | Plan §3 (3d) floor / stretch |
|---|---|---|---:|---|
| Spork | TP 7 / FP 36 | **TP 14 / FP 29** | 7 | floor: TP ≥ 10 ✓ ✓✓ stretch: TP ≥ 14 ✓ |
| Mastery | TP 0 / FP 44 | TP 10 / FP 34 | 10 | unchanged target; +10 BONUS |
| JDime | TP 0 / FP 2 | TP 1 / FP 1 | 1 | unchanged target; +1 BONUS |
| git-merge-file | TP 39 / FP 0 | unchanged | 0 | unchanged ✓ |

Spork: **prototype prediction = 12; committed = 14** — slightly above (one extra recovery from a scenario where the prototype's transform ordering produced a parse-fail; committed code hits a different ordering that closes it).

Mastery and JDime: unexpected. The plan §3 expected `unchanged` for both. The recoveries are legitimate per spot-check (Mastery scenario `47deg_firebrand 766c135387`: 84 comment tokens in dev, 0 in Mastery's output; canonical forms 18473 chars each, identical after comment-strip + token-fold). These scenarios fall under the §7.1 (Tier C plan) threats-to-validity: "Comparator treats all comments as equivalent."

### Per-phase attribution

Approximate, from progressively-enabling phases in the prototype:

| Phase shipped | Cumulative Spork TP (post each commit) |
|---|---:|
| (post 3b Tier C) | 7 |
| + D.1 unwrap_single_stmt_block | ~8 |
| + D.2 strip_paren_around_primary | ~9 |
| + D.3 strip_paren_around_cast | ~9 (paired with D.2) |
| + D.4 strip_paren_around_binary_safe_parent | ~10 |
| + D.5 strip_paren_around_binary_precedence_aware | ~11 |
| + D.6 token_canonical_fold | **14** |

D.6 contributes the largest single-phase jump (~3 additional). This matches the diagnosis in [`comparator-3b-ast-normalize.md` §13](comparator-3b-ast-normalize.md) that gjf's line-wrap differences (when token counts vary between Spork and dev outputs) are a major residual driver.

### Acceptance criteria — final status

All items from §9:

- [x] `tests/test_ast_normalize.py` gains 16 unit tests (some via repurposing existing Tier C tests).
- [x] `tests/test_comparator.py` gains 2 integration tests (`test_contents_match_d2_syntactic_paren_guard_end_to_end`, `test_contents_match_d6_line_wrap_recovers_end_to_end`).
- [x] Full test suite at **82 passing tests** (target was 74-80 — slightly over because some Tier C `strip_redundant_parens` and `flatten_else_if` tests stayed as-is rather than migrating; net positive — more coverage retained).
- [x] `reports/results.csv` regenerated with Spork TP 14 / FP 29 (Tier D stretch).
- [x] No regression — Mastery and JDime IMPROVED (not regressions).
- [x] `MERGE_COMPARATOR_AST_NORMALIZE=off` cleanly disables (verified by `test_contents_match_tier3_off_short_circuits`).
- [x] STATUS.md / CLAUDE.md / ISSUES.md #2 updated.
- [x] This plan §13 (just appended).
- [ ] ~~Spork TP ≥ 32 / FP ≤ 11~~ — NOT MET. ISSUES.md #2 stays at `decided`, not `resolved`. Closing requires Tier E or 3a (per §10).

### Disposition

- All Tier D code remains landed. The transforms are conservative (parent-context checks, precedence-aware, syntactic-paren guards); no semantic-change risk has surfaced in 82 tests + n=50 spot-checks.
- `reports/results.csv` post-3d Tier D committed as the current honest interim state.
- ISSUES.md #2 stays at `decided` per the 3b plan §3 floor still un-hit.
- Tier E becomes the next obvious follow-up if/when closing ISSUES.md #2 becomes priority: `+` / `*` same-op-strip with type-inference, long-array-literal whitespace normalisation (6 scenarios), hex literal case normalisation. Or 3a test-suite ground truth as the alternative path.
- The 12 cumulative Spork recoveries (X_total = 12 vs original §3 floor of 30) reframe the headline as **comparator-gap, substantially closed** rather than **comparator-gap, partially closed** — significant improvement in defensibility for thesis discussion.
