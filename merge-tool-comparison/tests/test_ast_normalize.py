from src.evaluation.ast_normalize import ast_canonicalize


def _canon(text):
    """Whitespace-fold for unit-test comparison. The comparator pairs
    `ast_canonicalize` outputs through `normalize_content`; this helper does
    a stronger fold so test fixtures stay readable."""
    return " ".join((text or "").split())


# --- §7.1 strip_comments ---

def test_strip_line_comment():
    a = "class A { void m() { // hello\n int x = 1; } }"
    b = "class A { void m() { int x = 1; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_block_comment():
    a = "class A { /* doc */ int x = 1; }"
    b = "class A { int x = 1; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_javadoc():
    a = "class A { /** Javadoc for m */ void m() {} }"
    b = "class A { void m() {} }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


# --- §7.2 strip_blank_lines ---

def test_collapse_multiple_blanks():
    a = "class A {\n\n\n  int x = 1;\n\n\n}"
    b = "class A {\n  int x = 1;\n}"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_no_blanks_already_canonical():
    """Round-trip on a source with no blank lines emits the D.6 token-fold
    canonical form (every leaf separated by single space)."""
    src = "class A { int x = 1; }"
    out = ast_canonicalize(src)
    assert out is not None
    assert out == "class A { int x = 1 ; }"


# --- §6.1 D.1 unwrap_single_stmt_block (3d.1; supersedes Tier C's flatten_else_if) ---

def test_flatten_basic():
    """`} else { if (y) { ... } }` canonicalises to `} else if (y) { ... }`.
    Now handled by D.1's general single-stmt-block unwrap on the alternative
    clause (inner is an if_statement; var-decl direct-check passes)."""
    a = "class A { void m() { if (x) { a(); } else { if (y) { b(); } } } }"
    b = "class A { void m() { if (x) { a(); } else if (y) { b(); } } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_unwrap_alt_when_inner_block_has_vd():
    """D.1's `_has_var_decl_direct` (looser than the old descendant-check)
    permits the alt-block unwrap when the var-decl is inside the inner
    if's own block — z's scope is unchanged by stripping the outer
    alt-block's braces, since the inner block already scopes it.

    Output is D.6 token-canonical (every leaf single-space-separated)."""
    src = "class A { void m() { if (x) {} else { if (y) { int z = 1; use(z); } } } }"
    out = ast_canonicalize(src)
    assert out is not None
    # Outer alt-block stripped (D.1 looser check applies):
    assert "else {" not in out
    # Inner block preserved (multi-stmt body — single-stmt rule doesn't apply):
    assert "{ int z = 1 ; use ( z ) ; }" in out


def test_flatten_does_not_apply_with_multiple_statements():
    """Structural-single check: the wrapping block must contain only one
    structural child. Multiple statements → no unwrap."""
    src = "class A { void m() { if (x) {} else { a(); if (y) { b(); } } } }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "else {" in out or "else{" in out


def test_unwrap_skipped_when_direct_var_decl():
    """D.1 skips when the block has a direct var-decl child — unwrapping
    would produce invalid Java (`if (cond) int x = 1;` is not a valid
    single-statement form)."""
    src = "class A { void m() { if (cond) { int x = 1; } } }"
    out = ast_canonicalize(src)
    assert out is not None
    # Block braces preserved (D.6 token-canonical form):
    assert "{ int x = 1 ; }" in out


def test_unwrap_consequence_single_stmt():
    """D.1 unwraps the consequence-block of an if when it's `{ single-stmt; }`
    and there's no dangling-else risk."""
    a = "class A { void m() { if (cond) { stmt(); } } }"
    b = "class A { void m() { if (cond) stmt(); } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_unwrap_else_with_non_if_stmt():
    """D.1 handles the `else { throw e; }` case — single non-decl, non-if
    statement in the else clause unwraps."""
    a = "class A { void m() throws Exception { if (cond) {} else { throw new Exception(); } } }"
    b = "class A { void m() throws Exception { if (cond) {} else throw new Exception(); } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_unwrap_while_body():
    """D.1 unwraps single-stmt body of a while loop."""
    a = "class A { void m() { while (cond) { stmt(); } } }"
    b = "class A { void m() { while (cond) stmt(); } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_dangling_else_guard():
    """D.1 must NOT unwrap the consequence-block when the outer if has an
    `else` AND the inner of the consequence contains an if_statement.
    Stripping the braces could rebind the outer's else to an inner bare-if
    (dangling-else rule). Conservative guard preserves both sides' explicit
    bracketing."""
    src = "class A { void m() { if (a) { if (b) x(); } else y(); } }"
    out = ast_canonicalize(src)
    assert out is not None
    # Consequence block persists (D.6 token-canonical form).
    assert "{ if ( b ) x ( ) ; }" in out


def test_unwrap_with_trailing_comment_in_block():
    """3e.0 regression: D.1's _try_unwrap_if uses `c == cons` (not `c is cons`)
    when iterating node.children. Tree-sitter returns fresh Node wrappers per
    access; `is` always returned False, so the cons-block was walked TWICE.
    The brace-strip edit (cons.start → inner.start, inner.end → cons.end)
    already spans any leading/trailing comments; the second walk re-emits a
    comment-strip edit *inside* that span, producing OVERLAPPING edits that
    `_apply_edits` resolves by rewinding the cursor — corrupting brace balance
    and leaving the text un-token-foldable (D.6 parse-fails, falls back to the
    unfolded source with stray newlines).

    The fixture MUST have a comment *after* the unwrapped statement (a
    leading-comment-only block does NOT diverge: the overlap is absorbed
    benignly there, which is why the previous nested-if/leading-comment
    fixture passed even against the buggy `is` code and did not actually
    guard this regression). With a trailing comment the buggy code yields
    `'class A {\\n  void m() {\\n    if (a) \\n      foo();\\n    }\\n  }\\n}\\n'`
    (3 `}` vs 2 `{`, newlines retained) while the fixed code yields the clean
    token-folded `'class A { void m ( ) { if ( a ) foo ( ) ; } }'`. Each of
    the three asserts below passes only under the fixed `==` code."""
    src = (
        "class A {\n"
        "  void m() {\n"
        "    if (a) {\n"
        "      // pre\n"
        "      foo();\n"
        "      // post\n"
        "    }\n"
        "  }\n"
        "}\n"
    )
    out = ast_canonicalize(src)
    assert out is not None
    # D.6 token-canonical fold succeeded (buggy code leaves stray newlines
    # because the corrupted text fails to re-parse and falls through).
    assert "\n" not in out
    # Brace balance intact (buggy code drops the cons-block `{` but keeps
    # both `}` — 2 `{` vs 3 `}`).
    assert out.count("{") == out.count("}")
    # The consequence block was unwrapped, in token-folded form.
    assert "if ( a ) foo ( ) ;" in out


# --- §6.2 D.2 strip_paren_around_primary (3d.2; supersedes Tier C's narrower rule) ---

def test_strip_double_paren():
    """`((x))` collapses to `(x)` — now via D.2's `parenthesized_expression`
    inclusion in `PRIMARY_NODE_TYPES`."""
    a = "class A { int m() { return ((1)); } }"
    b = "class A { int m() { return (1); } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_precedence_paren():
    """Paren around a `binary_expression` is NOT in PRIMARY_NODE_TYPES and is
    preserved at this phase (D.4 + D.5 will handle some of these later)."""
    src = "class A { int m(int a, int b, int c) { return (a + b) * c; } }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "( a + b )" in out


def test_strip_nested_triple():
    """`(((x)))` collapses to `(x)` in one pass — visitor recurses into the
    inner paren after stripping the outer."""
    a = "class A { int m() { return (((1))); } }"
    b = "class A { int m() { return (1); } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_paren_around_method_call():
    """D.2: `(foo())` → `foo()` — method_invocation is a primary."""
    a = "class A { int m() { return (foo()); } }"
    b = "class A { int m() { return foo(); } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_paren_around_array_access():
    """D.2: `(arr[0])` → `arr[0]` — array_access is a primary."""
    a = "class A { int m(int[] arr) { return (arr[0]); } }"
    b = "class A { int m(int[] arr) { return arr[0]; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_paren_around_field_access():
    """D.2: `(x.f)` → `x.f` — field_access is a primary."""
    a = "class A { int m(A x) { return (x.f); } int f; }"
    b = "class A { int m(A x) { return x.f; } int f; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_d2_preserves_if_condition_paren():
    """Syntactic-paren guard: `if (cond)` must NOT have its paren stripped to
    `if cond` (invalid Java). Tested by round-tripping through ast_canonicalize
    and asserting the output still parses successfully — i.e. the canonical
    output re-parses without error."""
    src = "class A { void m(boolean cond) { if (cond) {} } }"
    out = ast_canonicalize(src)
    assert out is not None
    # Re-parseable, condition paren preserved (D.6 token-canonical form).
    from src.evaluation.ast_normalize import _PARSER
    tree = _PARSER.parse(out.encode("utf-8"))
    assert not tree.root_node.has_error
    assert "if ( cond )" in out


# --- §6.3 D.3 strip_paren_around_cast (3d.3) ---

def test_strip_cast_paren_in_safe_context():
    """D.3: `((cast) val) OP x` strips outer paren when parent is a safe
    context (here: binary_expression on the right side, the cast is the LHS)."""
    a = "class A { long m(int x, int y) { return ((long) x) + y; } }"
    b = "class A { long m(int x, int y) { return (long) x + y; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_cast_paren_in_unsafe_context():
    """D.3: `((Long) x).bitCount(x)` MUST preserve the outer paren — stripping
    would let `.bitCount` bind to `x` (the cast value) instead of the cast
    result, changing the parse."""
    src = "class A { int m(Object x) { return ((Long) x).intValue(); } }"
    out = ast_canonicalize(src)
    assert out is not None
    # Cast-paren retained for field/method postfix binding (D.6 form).
    assert "( ( Long ) x )" in out


# --- §6.4 D.4 strip_paren_around_binary_safe_parent (3d.4) ---

def test_strip_binary_paren_in_return():
    """D.4: paren around binary expression in `return` strips."""
    a = "class A { boolean m(boolean a, boolean b) { return (a | b); } }"
    b = "class A { boolean m(boolean a, boolean b) { return a | b; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_binary_paren_in_argument():
    """D.4: paren around binary expression in a call argument strips."""
    a = "class A { void f(boolean x) {} void m(int a, int b) { f((a == b)); } }"
    b = "class A { void f(boolean x) {} void m(int a, int b) { f(a == b); } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_binary_paren_inside_binary():
    """D.4: paren around binary whose parent is itself a binary_expression
    is preserved (would need precedence reasoning — D.5 handles this)."""
    src = "class A { int m(int a, int b, int c) { return (a + b) * c; } }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "( a + b )" in out


def test_strip_ternary_paren_in_return():
    """D.4: ternary expression paren in `return` strips."""
    a = "class A { int m(int a) { return (a > 0 ? 1 : 0); } }"
    b = "class A { int m(int a) { return a > 0 ? 1 : 0; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


# --- §6.5 D.5 strip_paren_around_binary_precedence_aware (3d.5) ---

def test_strip_paren_strict_higher_precedence():
    """D.5 case A: `(a == b) && c` — inner == has precedence 8, outer && has
    precedence 4. Strict-higher → strip safe."""
    a = "class A { boolean m(int a, int b, boolean c) { return (a == b) && c; } }"
    b = "class A { boolean m(int a, int b, boolean c) { return a == b && c; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_paren_same_op_assoc_safe():
    """D.5 case B: `(a && b) && c` — same op, pure-boolean, both sides safe."""
    a = "class A { boolean m(boolean a, boolean b, boolean c) { return (a && b) && c; } }"
    b = "class A { boolean m(boolean a, boolean b, boolean c) { return a && b && c; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_paren_plus_not_assoc_safe():
    """D.5: `+` is NOT in ASSOC_SAFE_OPS — string-concat-vs-numeric gotcha
    makes same-op-strip unsafe. `((a + b) + c)` does NOT lose its inner paren."""
    src = "class A { String m(int a, int b, String c) { return c + (a + b); } }"
    out = ast_canonicalize(src)
    assert out is not None
    # Inner `+` paren preserved
    assert "( a + b )" in out


def test_preserve_paren_reverse_precedence():
    """D.5: `(a + b) * c` — inner + (11) is LOWER than outer * (12). Strip
    would change semantics to `a + b * c` = `a + (b * c)`. Skip."""
    src = "class A { int m(int a, int b, int c) { return (a + b) * c; } }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "( a + b )" in out


# --- 3e.1 strip_paren_around_unary ---

def test_strip_paren_around_logical_not_in_binary():
    """3e.1: `(!a) && b` strips to `!a && b`. Unary `!` binds tighter than
    `&&` so the paren is purely cosmetic."""
    a = "class A { boolean m(boolean a, boolean b) { return (!a) && b; } }"
    b = "class A { boolean m(boolean a, boolean b) { return !a && b; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_paren_around_bitwise_not_in_binary():
    """3e.1: `(~bits) | mask` strips. `~` is in UNARY_SAFE_OPS_FOR_STRIP."""
    a = "class A { int m(int bits, int mask) { return (~bits) | mask; } }"
    b = "class A { int m(int bits, int mask) { return ~bits | mask; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_paren_around_unary_minus():
    """3e.1 conservatively skips unary `-` and `+` (not in
    UNARY_SAFE_OPS_FOR_STRIP). `(-a) + b` stays parenthesized in canonical
    form — postfix-rebind concerns make the strip non-trivial; defer."""
    src = "class A { int m(int a, int b) { return (-a) + b; } }"
    out = ast_canonicalize(src)
    assert out is not None
    # Paren around the unary `-a` preserved.
    assert "( - a )" in out


# --- 3e.2 strip_array_creation_shorthand ---

def test_strip_array_creation_shorthand_in_var_decl():
    """3e.2: `T[] x = new T[]{1, 2}` ↔ `T[] x = {1, 2}` in field/local decl."""
    a = "class A { int[] xs = new int[]{1, 2, 3}; }"
    b = "class A { int[] xs = {1, 2, 3}; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_array_creation_shorthand_nested():
    """3e.2: nested array_initializer parent. `new T[][]{ new T[]{1}, new T[]{2} }`
    ↔ `{ {1}, {2} }`. Both inner `new T[]{...}`s strip; outer `new T[][]`
    has var-decl parent so it also strips. Together they collapse to `{ {1}, {2} }`."""
    a = "class A { int[][] xs = new int[][]{new int[]{1}, new int[]{2}}; }"
    b = "class A { int[][] xs = {{1}, {2}}; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_array_creation_in_arg_list():
    """3e.2 does NOT strip in argument-list context — `foo({1, 2})` is not
    valid Java; the explicit `new T[]{...}` form is required there."""
    src = "class A { void m() { foo(new int[]{1, 2}); } void foo(int[] xs) {} }"
    out = ast_canonicalize(src)
    assert out is not None
    # `new int []` preserved (parent is `argument_list`, not in ARRAY_SHORT_PARENTS).
    assert "new int [ ]" in out


# --- 3e.3 strip_paren_around_arith_same_op_left_assoc ---

def test_strip_plus_chain_left_assoc_numeric():
    """3e.3: `(a + b) + c` strips when all-numeric. Left-associative."""
    a = "class A { int m(int a, int b, int c) { return (a + b) + c; } }"
    b = "class A { int m(int a, int b, int c) { return a + b + c; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_plus_chain_left_assoc_strings():
    """3e.3: `("x" + b) + "y"` strips — pure string concat is associative."""
    a = 'class A { String m(String b) { return ("x" + b) + "y"; } }'
    b = 'class A { String m(String b) { return "x" + b + "y"; } }'
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_plus_chain_when_only_outer_right_has_string():
    """3e.3 string-concat guard: `(1 + 2) + "x"` — inner is all numeric, outer
    right is a string. In LEFT position this IS safe (both forms produce "3x"),
    but the guard is conservative and skips to avoid analyzing left-assoc
    evaluation order under widening. Documents the conservative-skip behavior."""
    src = 'class A { String m() { return (1 + 2) + "x"; } }'
    out = ast_canonicalize(src)
    assert out is not None
    assert "( 1 + 2 )" in out


def test_preserve_paren_around_arith_different_ops():
    """3e.3 only fires same-op. `(a + b) * c` ≠ `a + b * c`. Already covered
    by D.5's preserve test but worth a direct E.3-context fixture."""
    src = "class A { int m(int a, int b, int c) { return (a + b) * c; } }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "( a + b )" in out


def test_strip_div_chain_left_assoc():
    """3e.3: `(a / b) / c` strips. Division is left-associative; both forms
    produce `((a/b)/c)`."""
    a = "class A { int m(int a, int b, int c) { return (a / b) / c; } }"
    b = "class A { int m(int a, int b, int c) { return a / b / c; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


# --- 3e.4 strip_paren_around_instanceof ---

def test_strip_instanceof_paren_in_or_chain():
    """3e.4: `(x instanceof Foo) || y` strips — `||` (prec 3) < instanceof (9)."""
    a = "class A { boolean m(Object x, boolean y) { return (x instanceof String) || y; } }"
    b = "class A { boolean m(Object x, boolean y) { return x instanceof String || y; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_instanceof_paren_in_return():
    """3e.4: `return (x instanceof Foo);` strips — parent is return_statement
    (in SAFE_BINARY_PAREN_PARENTS)."""
    a = "class A { boolean m(Object x) { return (x instanceof String); } }"
    b = "class A { boolean m(Object x) { return x instanceof String; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


# --- 3e.5 strip_empty_enum_body_declarations ---

def test_strip_enum_trailing_semi():
    """3e.5: `enum X { A, B; }` and `enum X { A, B }` produce equal canonical
    forms — the trailing `;` separator after enum constants is optional when
    no member declarations follow."""
    a = "class C { enum E { A, B; } }"
    b = "class C { enum E { A, B } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_enum_with_member_decls():
    """3e.5 strip is gated on `named_child_count == 0` in the
    `enum_body_declarations` node. When real member decls follow the `;`,
    the node has named children and the `;` is structurally required."""
    src = "class C { enum E { A, B; void greet() {} } }"
    out = ast_canonicalize(src)
    assert out is not None
    # The `;` separator before the method decl is preserved.
    assert "B ; void greet" in out


# --- 3e.6 expand SAFE_BINARY_PAREN_PARENTS ---

def test_strip_binary_paren_in_assert():
    """3e.6: `assert (a < b);` ↔ `assert a < b;`. `assert_statement` added
    to D.4's SAFE_BINARY_PAREN_PARENTS — the assertion expression has no
    outer operator that could rebind."""
    a = "class A { void m(int a, int b) { assert (a < b); } }"
    b = "class A { void m(int a, int b) { assert a < b; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_strip_binary_paren_in_array_index():
    """3e.6: `arr[(x - 1)]` ↔ `arr[x - 1]`. `array_access` added to D.4's
    set — the index brackets bind to the array, not to the index expression,
    so the inner paren is purely cosmetic."""
    a = "class A { int m(int[] arr, int x) { return arr[(x - 1)]; } }"
    b = "class A { int m(int[] arr, int x) { return arr[x - 1]; } }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


# --- 3e.7 strip_array_initializer_trailing_comma ---

def test_strip_array_trailing_comma_simple():
    """3e.7: `{1, 2, }` ↔ `{1, 2}`. Java accepts trailing comma in
    array_initializer; canonical form has no trailing comma."""
    a = "class A { int[] xs = {1, 2, 3,}; }"
    b = "class A { int[] xs = {1, 2, 3}; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_array_with_no_trailing_comma():
    """3e.7 is a no-op when there's already no trailing comma. Canonical
    form unchanged."""
    src = "class A { int[] xs = {1, 2, 3}; }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "1 , 2 , 3" in out


def test_strip_nested_array_trailing_commas():
    """3e.7: both inner and outer trailing commas strip when both exist.
    Combined with 3e.2 array shorthand, `new T[][]{{1,},{2,},}` collapses
    fully to `{{1},{2}}`."""
    a = "class A { int[][] xs = {{1,}, {2,},}; }"
    b = "class A { int[][] xs = {{1}, {2}}; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


# --- 3e.8 strip_paren_around_assignment ---

def test_strip_assignment_paren_in_while_condition():
    """3e.8: `while ((x = compute()))` ↔ `while (x = compute())`. The inner
    paren wraps an `assignment_expression`; its parent is the outer (syntactic)
    `parenthesized_expression`. In ASSIGN_PAREN_SAFE_PARENTS, so strips."""
    src = "class A { boolean x; void m() { while ((x = compute())) ; } boolean compute() { return false; } }"
    out = ast_canonicalize(src)
    assert out is not None
    # After E.8 strips the inner paren, only the syntactic while-paren remains.
    assert "while ( x = compute ( ) )" in out
    # And no double-paren `( ( x = compute` remains.
    assert "( ( x = compute" not in out


def test_preserve_assignment_paren_in_binary_context():
    """3e.8 conservatively skips when parent is `binary_expression` — assignment
    is right-associative and the paren may carry semantic weight there. E.g.,
    `(x = y) + 1` should stay as written; E.8 doesn't strip."""
    src = "class A { int x; int m() { return (x = 5) + 1; } }"
    out = ast_canonicalize(src)
    assert out is not None
    # Paren preserved around the assignment.
    assert "( x = 5 )" in out


# --- 3e.9 normalize_float_literal_suffix ---

def test_float_suffix_strip_with_dot():
    """3e.9: `100.0d` and `100.0` produce same canonical form."""
    a = "class A { double x = 100.0d; }"
    b = "class A { double x = 100.0; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_float_suffix_strip_with_exponent():
    """3e.9: `1e10f` and `1e10` produce same canonical form."""
    a = "class A { float x = 1e10f; }"
    b = "class A { float x = 1e10; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_float_suffix_canonicalize_no_dot():
    """3e.9: `100d` (no `.`, no exponent) converts to `100.0`."""
    a = "class A { double x = 100d; }"
    b = "class A { double x = 100.0; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_float_suffix_uppercase_F():
    """3e.9: uppercase suffix `F` handled same as `f`."""
    a = "class A { float x = 0.5F; }"
    b = "class A { float x = 0.5; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_float_no_suffix_unchanged():
    """3e.9: literal without `d`/`D`/`f`/`F` suffix is not touched."""
    src = "class A { double x = 1.5; }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "1.5" in out


# --- 3e.10 normalize_hex_literal_case ---

def test_hex_literal_uppercase_lowercased():
    """3e.10: `0xFF` lowercases to `0xff` in canonical form."""
    a = "class A { int x = 0xFF; }"
    b = "class A { int x = 0xff; }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_hex_literal_already_lowercase_unchanged():
    """3e.10: a lowercase hex literal is not re-emitted (no edit added)."""
    src = "class A { int x = 0xff; }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "0xff" in out

def test_strip_javalang_throwable():
    """`java.lang.Throwable` (in the hardcoded set) collapses to `Throwable`."""
    a = "class A { void m() throws java.lang.Throwable {} }"
    b = "class A { void m() throws Throwable {} }"
    assert _canon(ast_canonicalize(a)) == _canon(ast_canonicalize(b))


def test_preserve_javalang_uncommon():
    """`java.lang.Process` is NOT in the hardcoded set — preserve the FQN
    rather than risk a false match against a user-shadowed `Process`.
    (D.6 token-fold splits the `.` separators as anonymous leaves.)"""
    src = "class A { java.lang.Process p; }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "java . lang . Process" in out


def test_preserve_non_javalang_fqn():
    """`java.util.List` is not under `java.lang.*` — preserve the FQN."""
    src = "class A { java.util.List<String> xs; }"
    out = ast_canonicalize(src)
    assert out is not None
    assert "java . util . List" in out


# --- §6.6 D.6 token_canonical_fold (3d.6) ---

def test_token_fold_multi_line_matches_single_line():
    """D.6: two textually-different but token-equivalent forms (one
    multi-line, one single-line) produce the same canonical output."""
    a = "class A {\n  void m() {\n    stmt();\n  }\n}"
    b = "class A { void m() { stmt(); } }"
    assert ast_canonicalize(a) == ast_canonicalize(b)


def test_token_fold_preserves_string_literal_whitespace():
    """D.6: internal whitespace inside string literals is preserved (string
    literals are single leaf nodes, emitted byte-exactly)."""
    src = 'class A { String s = "hello  world\\n"; }'
    out = ast_canonicalize(src)
    assert out is not None
    # The double-space and \n stay inside the literal.
    assert '"hello  world\\n"' in out


def test_token_fold_idempotent():
    """D.6: folding a folded form is a no-op — canonical-form is a fixed
    point of `ast_canonicalize`."""
    src = "class A { int x = 1; void m() { if (x > 0) { y(); } } void y() {} }"
    once = ast_canonicalize(src)
    twice = ast_canonicalize(once)
    assert once == twice
