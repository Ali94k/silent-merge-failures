"""AST-aware canonicalisation for Java source (Tier 3 of comparator pipeline).

Parses source via tree-sitter-java, applies a fixed set of semantics-preserving
transforms, and re-emits text. Used after Tier 2 (gjf roundtrip) when the
formatter agrees the source is well-formed but the two outputs still differ on
patterns that gjf does not canonicalise (blank lines, comment placement,
paren-wrapping-paren, `} else { if }` vs `} else if`, hardcoded java.lang.*
FQN expansion).

See `docs/plans/comparator-3b-ast-normalize.md` for the design.
"""

import re

import tree_sitter_java
from tree_sitter import Language, Node, Parser


_LANG = Language(tree_sitter_java.language())
_PARSER = Parser(_LANG)

_BLANK_LINE_RE = re.compile(r"\n[ \t]*\n")

# Common java.lang.* short names. Matching this set scopes `strip_javalang_fqn`
# conservatively: out-of-set names retain the `java.lang.` prefix, so the
# transform produces at-most-equal recovery and never false matches against
# user-shadowed names of uncommon java.lang.* members. See plan §7.5.
JAVALANG_SIMPLE_NAMES = frozenset({
    "Object", "String", "Integer", "Long", "Boolean", "Character", "Byte",
    "Short", "Float", "Double", "Number", "Math", "System", "Thread",
    "Runnable", "Class", "Throwable", "Error", "Exception",
    "RuntimeException", "InstantiationException", "IllegalAccessException",
    "ClassNotFoundException", "NullPointerException",
    "IllegalArgumentException", "IllegalStateException",
    "ArithmeticException", "ArrayIndexOutOfBoundsException",
    "ClassCastException", "NumberFormatException",
    "UnsupportedOperationException", "InterruptedException",
    "StringBuilder", "StringBuffer", "Iterable", "Comparable",
    "Override", "Deprecated", "SuppressWarnings", "FunctionalInterface",
})
_JAVALANG_PREFIX = b"java.lang."

# Java "primary" expressions (JLS §15.8 + parenthesized_expression for recursive
# nesting). Stripping a paren around any of these never changes the parse —
# primaries are atomic from an operator-precedence perspective. See plan §6.2.
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
    "parenthesized_expression",  # Tier C's paren-wrap-paren is a sub-case
})

# Parents where a `parenthesized_expression` is required by Java syntax
# (the if/while/do/synchronized/switch conditions). Stripping a paren in these
# contexts produces invalid Java; the syntactic-paren guard skips them.
SYNTACTIC_PAREN_PARENTS = frozenset({
    "if_statement", "while_statement", "do_statement",
    "synchronized_statement", "switch_statement", "switch_expression",
})

# Parents where stripping a `parenthesized_expression` wrapping a cast would
# rebind a postfix operator (`.field`, `[idx]`, `.method()`) to the cast's
# value instead of the cast result. `((Long) x).field` ≠ `(Long) x.field`
# because `.` binds tighter than the unary cast.
UNSAFE_CAST_PAREN_PARENTS = frozenset({
    "field_access", "method_invocation", "array_access",
})

# Parents where stripping a `parenthesized_expression` wrapping a binary or
# ternary expression is always safe — no outer operator can re-bind. Excludes
# `binary_expression` (handled by D.5 with precedence reasoning), `cast_expression`,
# and the postfix-rebinding parents from above.
# 3e.6 additions: `assert_statement` (the condition is the full statement, no
# outer op) and `array_access` (the index expression is bracketed; `[]` is
# a postfix on the array, not on the index — no re-bind risk).
SAFE_BINARY_PAREN_PARENTS = frozenset({
    "expression_statement", "return_statement", "throw_statement",
    "argument_list", "variable_declarator", "assignment_expression",
    "yield_statement", "ternary_expression", "parenthesized_expression",
    "array_initializer",
    "assert_statement", "array_access",
})

# Java binary operator precedence per JLS §15 (higher number = binds tighter).
# Used by D.5 strip_paren_around_binary_precedence_aware. Unary, cast, postfix
# are not in this table; they're handled by separate transforms.
JAVA_BINARY_PREC = {
    "*": 12, "/": 12, "%": 12,
    "+": 11, "-": 11,
    "<<": 10, ">>": 10, ">>>": 10,
    "<": 9, ">": 9, "<=": 9, ">=": 9, "instanceof": 9,
    "==": 8, "!=": 8,
    "&": 7,
    "^": 6,
    "|": 5,
    "&&": 4,
    "||": 3,
}

# Operators safe for same-op-same-precedence paren strip on either side. Pure
# boolean/bitwise — no implicit type promotion or string-concat ambiguity.
# Excludes `+` (numeric vs. string concat is non-associative when mixed) and
# `*` (mixed int/double precision concerns); these are handled by 3e.3 with
# a left-position-only rule and string-concat guard.
ASSOC_SAFE_OPS = frozenset({"&&", "||", "&", "|", "^"})

# 3e.1: unary ops where paren-strip is always safe. `!` and `~` bind tighter
# than ALL binary ops (JLS §15: precedence 14 vs max 12 for binary), so
# `(!x) OP y` always equals `!x OP y`. Excludes unary `-` and `+`: while they
# also bind tighter than binary ops, `(-x).method()` would re-bind postfix —
# we'd need the same parent-context guard as cast (D.3). Conservative skip.
UNARY_SAFE_OPS_FOR_STRIP = frozenset({"!", "~"})

# Parents where stripping a paren around a unary_expression with op in
# UNARY_SAFE_OPS_FOR_STRIP is safe. Includes `binary_expression` because the
# unary op binds tighter; D.4's SAFE_BINARY_PAREN_PARENTS already covers
# the no-outer-op cases.
UNARY_SAFE_PARENTS = SAFE_BINARY_PAREN_PARENTS | frozenset({"binary_expression"})

# 3e.2: parents where `new T[]{...}` is equivalent to the bare `{...}`
# array initializer. `variable_declarator` covers `T[] x = new T[]{...}`;
# `array_initializer` covers the nested case `{ new T[]{...}, new T[]{...} }`
# which Java parses as a 2D-array initializer.
ARRAY_SHORT_PARENTS = frozenset({"variable_declarator", "array_initializer"})

# 3e.3: arithmetic operators where `(a OP b) OP c` (LEFT position) can be
# unparenthesized to `a OP b OP c`. All are left-associative per JLS §15.18-23,
# so the LEFT-position case is always safe. RIGHT-position `a OP (b OP c)` is
# NOT safe for `-`, `/`, `%` (non-commutative under reassociation) and for `+`
# / `*` with mixed string/numeric. Deferred.
ARITH_LEFT_ASSOC_OPS = frozenset({"+", "-", "*", "/", "%"})

# 3e.8: parents where stripping a paren around `assignment_expression` is
# safe. `parenthesized_expression` covers `while ((x = y))` where the inner
# paren wraps the assignment (outer paren is the while's syntactic paren);
# `expression_statement` covers `(x = y);` at statement-position (rare).
# Excluded: binary_expression, cast_expression, postfix contexts — these
# would re-bind to the assignment's LHS in unexpected ways.
ASSIGN_PAREN_SAFE_PARENTS = frozenset({
    "parenthesized_expression", "expression_statement",
})


def ast_canonicalize(source: str) -> str | None:
    """Parse `source` as Java, apply Tier-C + Tier-D canonicalisation, return
    the canonicalised text. Returns None if the source does not parse (so the
    caller can fall through to the Tier 2 verdict).

    Output form (D.6 token-canonical fold): every leaf is emitted separated
    by a single space. String / character / text_block literals are preserved
    byte-exactly. This yields a whitespace-insensitive canonical form so that
    gjf's line-wrap decisions (which differ between Spork output and dev
    resolution when token counts differ) don't cause spurious mismatches.

    If the post-edit text fails to re-parse (e.g. an over-aggressive edit
    produced invalid Java), the token-fold is skipped and the pre-fold text
    is returned — conservative fall-through preserves Tier C + D.1-D.5
    output even when D.6 can't normalize."""
    src_bytes = source.encode("utf-8")
    tree = _PARSER.parse(src_bytes)
    if tree.root_node.has_error:
        return None
    edits: list[tuple[int, int, bytes]] = []
    _collect_edits(tree.root_node, edits)
    text = _apply_edits(src_bytes, edits).decode("utf-8", errors="replace")
    text = _strip_blank_lines(text)
    folded = _token_canonical_fold(text)
    return folded if folded is not None else text


def _token_canonical_fold(text: str) -> str | None:
    """D.6: re-parse `text` and emit each leaf separated by single space.
    Returns None on parse-fail (caller falls back to the unfolded text)."""
    src_bytes = text.encode("utf-8")
    tree = _PARSER.parse(src_bytes)
    if tree.root_node.has_error:
        return None
    parts: list[bytes] = []
    _emit_leaves(tree.root_node, parts)
    return b" ".join(parts).decode("utf-8", errors="replace")


_ATOMIC_LEAF_TYPES = frozenset({
    "string_literal", "character_literal", "text_block",
    # Comments are already stripped via edit ranges before the fold runs, but
    # treat them atomically in case any survive (defensive).
    "line_comment", "block_comment",
})


def _emit_leaves(node: Node, parts: list[bytes]) -> None:
    """Walk `node` to its leaves, appending each leaf's bytes. Leaves include
    named tokens (identifiers, literals) and anonymous tokens (operators,
    punctuation, keywords). `string_literal` / `character_literal` /
    `text_block` are emitted ATOMICALLY (as their full source text) rather
    than decomposed into their `"`, `string_fragment`, `escape_sequence`,
    `"` children — which would otherwise insert spurious spaces inside the
    quoted text."""
    if node.type in _ATOMIC_LEAF_TYPES:
        if node.text:
            parts.append(node.text)
        return
    if node.child_count == 0:
        if node.text:
            parts.append(node.text)
        return
    for c in node.children:
        _emit_leaves(c, parts)


def _collect_edits(node: Node, edits: list[tuple[int, int, bytes]]) -> None:
    """Walk the tree, appending (start, end, replacement) tuples for any node
    a transform rewrites. Skips recursion into replaced nodes (the replacement
    bytes stand in for the entire subtree)."""
    if node.type in ("line_comment", "block_comment"):
        edits.append((node.start_byte, node.end_byte, b""))
        return
    if node.type == "if_statement":
        # D.1: unwrap consequence and/or alternative when they're single-stmt
        # blocks. Supersedes Tier C's narrower `flatten_else_if` per plan §4.3.
        if _try_unwrap_if(node, edits):
            return
    if node.type in ("while_statement", "for_statement",
                     "enhanced_for_statement", "do_statement"):
        # D.1: same single-stmt-block unwrap for loop bodies.
        if _try_unwrap_loop(node, edits):
            return
    if node.type == "enum_body_declarations" and node.named_child_count == 0:
        # 3e.5: tree-sitter-java wraps the trailing `;` after the last enum
        # constant in an `enum_body_declarations` node. When that node contains
        # no actual member declarations (named_child_count == 0), the `;` is a
        # vestigial separator that can be stripped — `enum X { A; }` and
        # `enum X { A }` are equivalent.
        edits.append((node.start_byte, node.end_byte, b""))
        return
    if node.type == "array_initializer":
        # 3e.7: strip trailing `,` before the closing `}`. Java allows
        # `{1, 2, }` and `{1, 2}` interchangeably; canonicalize to the
        # no-trailing-comma form. Fall through to recurse afterwards.
        children = node.children
        close_idx = None
        for i, c in enumerate(children):
            if c.type == "}":
                close_idx = i
                break
        if close_idx is not None and close_idx > 0:
            prev = children[close_idx - 1]
            if prev.type == ",":
                edits.append((prev.start_byte, prev.end_byte, b""))
    if node.type == "parenthesized_expression":
        # Syntactic-paren guard: never strip a paren that's required by Java
        # syntax (`if`/`while`/`do`/`synchronized`/`switch` condition). Still
        # recurse into its child for downstream transforms.
        if _is_syntactic_paren(node):
            for c in node.children:
                _collect_edits(c, edits)
            return
        inner = _single_paren_child(node)
        if inner is not None and inner.type in PRIMARY_NODE_TYPES:
            # D.2: strip paren around a primary. Subsumes Tier C's narrower
            # paren-wrapping-paren rule (parenthesized_expression is itself a
            # primary). Recurse into the inner so triple+ nesting collapses
            # in one pass.
            edits.append((node.start_byte, inner.start_byte, b""))
            edits.append((inner.end_byte, node.end_byte, b""))
            _collect_edits(inner, edits)
            return
        if inner is not None and inner.type == "cast_expression" \
           and node.parent is not None \
           and node.parent.type not in UNSAFE_CAST_PAREN_PARENTS:
            # D.3: strip paren around cast in safe parent context. Skipped
            # when parent is field_access / method_invocation / array_access
            # (postfix would re-bind to the cast value instead of the cast
            # result — `((Long) x).field` ≠ `(Long) x.field`).
            edits.append((node.start_byte, inner.start_byte, b""))
            edits.append((inner.end_byte, node.end_byte, b""))
            _collect_edits(inner, edits)
            return
        if inner is not None and inner.type in ("binary_expression", "ternary_expression") \
           and node.parent is not None \
           and node.parent.type in SAFE_BINARY_PAREN_PARENTS:
            # D.4: strip paren around binary/ternary in a no-outer-op context
            # (return / throw / arg / initializer / assignment RHS / etc).
            # Parent contexts where an outer operator could re-bind (another
            # binary_expression, cast, postfix) are excluded — handled by
            # D.5 with precedence reasoning where safe.
            edits.append((node.start_byte, inner.start_byte, b""))
            edits.append((inner.end_byte, node.end_byte, b""))
            _collect_edits(inner, edits)
            return
        if inner is not None and inner.type == "instanceof_expression" \
           and node.parent is not None:
            # 3e.4: instanceof has JLS precedence 9 (same as relational ops).
            # Strip when (a) parent is in SAFE_BINARY_PAREN_PARENTS — no outer
            # op can rebind, OR (b) parent is binary_expression with op
            # precedence < 9 — instanceof binds tighter so paren is cosmetic.
            if node.parent.type in SAFE_BINARY_PAREN_PARENTS:
                edits.append((node.start_byte, inner.start_byte, b""))
                edits.append((inner.end_byte, node.end_byte, b""))
                _collect_edits(inner, edits)
                return
            if node.parent.type == "binary_expression":
                parent_op = _binary_op_text(node.parent)
                parent_prec = JAVA_BINARY_PREC.get(parent_op, 0)
                if 0 < parent_prec < 9:
                    edits.append((node.start_byte, inner.start_byte, b""))
                    edits.append((inner.end_byte, node.end_byte, b""))
                    _collect_edits(inner, edits)
                    return
        if inner is not None and inner.type == "binary_expression" \
           and node.parent is not None \
           and node.parent.type == "binary_expression":
            # D.5: precedence-aware strip when paren is inside another
            # binary_expression. Two safe cases:
            #   (A) strict-higher precedence: inner op > outer op — paren
            #       cannot affect parse.
            #   (B) same-op, same-precedence, and op is in the pure
            #       boolean/bitwise associative-safe set — left- and right-
            #       position strip both safe (`&&`, `||`, `&`, `|`, `^`).
            inner_op = _binary_op_text(inner)
            outer_op = _binary_op_text(node.parent)
            if inner_op and outer_op:
                ip = JAVA_BINARY_PREC.get(inner_op, 0)
                op = JAVA_BINARY_PREC.get(outer_op, 0)
                if (ip > op > 0) \
                   or (ip == op and inner_op == outer_op and inner_op in ASSOC_SAFE_OPS):
                    edits.append((node.start_byte, inner.start_byte, b""))
                    edits.append((inner.end_byte, node.end_byte, b""))
                    _collect_edits(inner, edits)
                    return
                # 3e.3: arithmetic same-op left-associative strip. `(a OP b) OP c`
                # ↔ `a OP b OP c` when op is in ARITH_LEFT_ASSOC_OPS and the
                # paren is the LEFT operand. For `+`, additionally guard against
                # mixed string-concat: skip if outer-right has string but inner
                # doesn't (e.g., `(1 + 2) + "x"` is safe in left-assoc, but
                # `"x" + (1 + 2)` is RIGHT-position so we never see it here).
                if inner_op == outer_op and inner_op in ARITH_LEFT_ASSOC_OPS:
                    outer_left = node.parent.child_by_field_name("left")
                    if outer_left is not None and outer_left == node:
                        allow = True
                        if inner_op == "+":
                            outer_right = node.parent.child_by_field_name("right")
                            if outer_right is not None \
                               and _contains_string_literal(outer_right) \
                               and not _contains_string_literal(inner):
                                allow = False
                        if allow:
                            edits.append((node.start_byte, inner.start_byte, b""))
                            edits.append((inner.end_byte, node.end_byte, b""))
                            _collect_edits(inner, edits)
                            return
        if inner is not None and inner.type == "unary_expression" \
           and node.parent is not None \
           and node.parent.type in UNARY_SAFE_PARENTS:
            # 3e.1: strip paren around unary_expression when op is `!` or `~`
            # (binds tighter than all binary ops; safe in any UNARY_SAFE_PARENTS
            # context). Excludes `-` / `+` unary due to postfix-rebind concerns.
            op = _unary_op_text(inner)
            if op in UNARY_SAFE_OPS_FOR_STRIP:
                edits.append((node.start_byte, inner.start_byte, b""))
                edits.append((inner.end_byte, node.end_byte, b""))
                _collect_edits(inner, edits)
                return
        if inner is not None and inner.type == "assignment_expression" \
           and node.parent is not None \
           and node.parent.type in ASSIGN_PAREN_SAFE_PARENTS:
            # 3e.8: strip paren around assignment_expression in
            # `while ((x = y))` / `if ((x = y))` patterns where the outer paren
            # is the loop/condition's syntactic paren and the inner paren is
            # cosmetic. Also handles `(x = y);` at statement position.
            edits.append((node.start_byte, inner.start_byte, b""))
            edits.append((inner.end_byte, node.end_byte, b""))
            _collect_edits(inner, edits)
            return
    if node.type == "array_creation_expression" \
       and node.parent is not None \
       and node.parent.type in ARRAY_SHORT_PARENTS:
        # 3e.2: in var-decl or nested-initializer context, `new T[]{...}` is
        # equivalent to the bare `{...}` array initializer. Strip the `new T[]`
        # prefix, leaving just the initializer subtree.
        init = node.child_by_field_name("value")
        if init is not None and init.type == "array_initializer":
            edits.append((node.start_byte, init.start_byte, b""))
            _collect_edits(init, edits)
            return
    if node.type in ("decimal_floating_point_literal", "hex_floating_point_literal"):
        # 3e.9: normalize trailing d/D/f/F suffix. Strip when literal already
        # has `.` or exponent; else convert `Nd`-form to `N.0`-form. Loses the
        # textual float-vs-double distinction (accepted normalization).
        text = node.text.decode("utf-8", errors="replace") if node.text else ""
        canon = _normalize_float_token(text)
        if canon is not None:
            edits.append((node.start_byte, node.end_byte, canon.encode("utf-8")))
            return
    if node.type == "hex_integer_literal":
        # 3e.10: lowercase the hex literal token so `0xFF` and `0xff` produce
        # identical canonical form. Does NOT normalize leading-zero padding
        # (`0x3` vs `0x03`) — direction is ambiguous on the dataset.
        text = node.text.decode("utf-8", errors="replace") if node.text else ""
        if text != text.lower():
            edits.append((node.start_byte, node.end_byte, text.lower().encode("utf-8")))
            return
    if node.type in ("scoped_identifier", "scoped_type_identifier"):
        text = node.text or b""
        if text.startswith(_JAVALANG_PREFIX):
            tail = text[len(_JAVALANG_PREFIX):]
            try:
                name = tail.decode("utf-8")
            except UnicodeDecodeError:
                name = ""
            if name in JAVALANG_SIMPLE_NAMES:
                edits.append((node.start_byte, node.end_byte, tail))
                return
    for child in node.children:
        _collect_edits(child, edits)


def _try_unwrap_if(node: Node, edits: list[tuple[int, int, bytes]]) -> bool:
    """D.1 unwrap for if_statement. Considers both consequence and alternative
    independently. Returns True iff at least one branch was unwrapped (and
    recursion into children was handled here); False to fall through to the
    default child-walk.

    Consequence unwrap is gated by a dangling-else guard (skip when outer has
    `else` AND inner of consequence contains an if_statement that could rebind
    the outer's else after brace removal). Alternative unwrap has no such
    guard — the wrapping else-block isn't a dangling-else target."""
    cons = node.child_by_field_name("consequence")
    alt = node.child_by_field_name("alternative")
    cons_inner = None
    if cons is not None and cons.type == "block":
        inner = _single_non_decl_stmt(cons)
        if inner is not None and not _has_var_decl_direct(cons) \
           and not _dangling_else_unsafe(node, inner):
            cons_inner = inner
    alt_inner = None
    if alt is not None and alt.type == "block":
        inner = _single_non_decl_stmt(alt)
        if inner is not None and not _has_var_decl_direct(alt):
            alt_inner = inner
    if cons_inner is None and alt_inner is None:
        return False
    if cons_inner is not None:
        edits.append((cons.start_byte, cons_inner.start_byte, b""))
        edits.append((cons_inner.end_byte, cons.end_byte, b""))
    if alt_inner is not None:
        edits.append((alt.start_byte, alt_inner.start_byte, b""))
        edits.append((alt_inner.end_byte, alt.end_byte, b""))
    for c in node.children:
        if cons is not None and c == cons and cons_inner is not None:
            _collect_edits(cons_inner, edits)
        elif alt is not None and c == alt and alt_inner is not None:
            _collect_edits(alt_inner, edits)
        else:
            _collect_edits(c, edits)
    return True


def _try_unwrap_loop(node: Node, edits: list[tuple[int, int, bytes]]) -> bool:
    """D.1 unwrap for while/for/do/enhanced-for body. No dangling-else risk
    (loops don't have else). Returns True iff body was unwrapped."""
    body = node.child_by_field_name("body")
    if body is None or body.type != "block":
        return False
    inner = _single_non_decl_stmt(body)
    if inner is None or _has_var_decl_direct(body):
        return False
    edits.append((body.start_byte, inner.start_byte, b""))
    edits.append((inner.end_byte, body.end_byte, b""))
    for c in node.children:
        _collect_edits(inner if c == body else c, edits)
    return True


def _single_non_decl_stmt(block: Node) -> Node | None:
    """If `block` has exactly one structural child (comments ignored) and that
    child is not a `local_variable_declaration` (which would produce invalid
    Java if the wrapping braces were stripped — `if (c) int x = 1;` is not a
    legal statement), return the child. Otherwise None."""
    structural = [
        c for c in block.named_children
        if c.type not in ("line_comment", "block_comment")
    ]
    if len(structural) != 1:
        return None
    if structural[0].type == "local_variable_declaration":
        return None
    return structural[0]


def _has_var_decl_direct(block: Node) -> bool:
    """D.1 guard: direct `local_variable_declaration` children only. Looser
    than `_has_var_decl_descendant` (used by older Tier C `flatten_else_if`);
    the descendant variant was over-conservative — var-decls inside a child
    block are already scoped to that child block, so the wrapping block's
    braces can be stripped without changing semantics."""
    return any(c.type == "local_variable_declaration" for c in block.named_children)


def _has_var_decl_descendant(node: Node) -> bool:
    """Recursive var-decl scan. Kept available for transforms that need the
    stricter scope-change guard; D.1 uses the looser `_has_var_decl_direct`."""
    if node.type in ("variable_declarator", "local_variable_declaration"):
        return True
    for c in node.children:
        if _has_var_decl_descendant(c):
            return True
    return False


def _contains_if_stmt(node: Node) -> bool:
    """Recursive `if_statement` presence check, for `_dangling_else_unsafe`."""
    if node.type == "if_statement":
        return True
    for c in node.children:
        if _contains_if_stmt(c):
            return True
    return False


def _dangling_else_unsafe(outer_if: Node, inner_of_cons: Node) -> bool:
    """Consequence-unwrap is unsafe when stripping the consequence-block's
    braces could let the outer if's `else` rebind to an inner bare `if`.

    Conservative rule: skip when outer has `else` AND inner-of-consequence
    contains any if_statement. Over-conservative — proceeds-with-unwrap would
    sometimes still be safe (e.g. when the inner if's else clauses are all
    matched) — but verifying that requires precise dangling-else analysis;
    the conservative check covers all unsafe cases at the cost of a few
    missed safe unwraps."""
    if outer_if.child_by_field_name("alternative") is None:
        return False
    return _contains_if_stmt(inner_of_cons)


def _single_paren_child(paren: Node) -> Node | None:
    """Return the sole structural child (comments ignored) of a
    `parenthesized_expression`, or None if the paren has zero or multiple
    structural children. Replaces Tier C's narrower `_single_inner_paren`;
    callers now check the child's type against `PRIMARY_NODE_TYPES` (and
    later phases against `cast_expression` / `binary_expression`)."""
    structural = [
        c for c in paren.named_children
        if c.type not in ("line_comment", "block_comment")
    ]
    return structural[0] if len(structural) == 1 else None


def _is_syntactic_paren(paren: Node) -> bool:
    """True iff `paren` is a parenthesized_expression directly required by
    Java syntax (parent is if/while/do/synchronized/switch). Stripping these
    produces invalid source — `if cond {}` is not legal Java."""
    p = paren.parent
    return p is not None and p.type in SYNTACTIC_PAREN_PARENTS


def _binary_op_text(node: Node) -> str | None:
    """Return the operator text of a `binary_expression`, e.g. `"&&"`, `"=="`,
    `"+"`. Used by D.5 precedence-aware paren strip."""
    op = node.child_by_field_name("operator")
    if op is not None and op.text:
        return op.text.decode("utf-8", errors="replace")
    for c in node.children:
        if c.type in JAVA_BINARY_PREC:
            return c.type
    return None


def _unary_op_text(node: Node) -> str | None:
    """Return the operator text of a `unary_expression`, e.g. `"!"`, `"~"`,
    `"-"`. tree-sitter-java exposes the operator as the first child."""
    if node.child_count >= 1 and node.children[0].text:
        return node.children[0].text.decode("utf-8", errors="replace")
    return None


def _normalize_float_token(text: str) -> str | None:
    """3e.9: canonicalize a Java float/double literal token. Strips trailing
    `d`/`D`/`f`/`F` suffix when the literal has a `.` or exponent; converts
    suffix-only forms (`Nd`) to dotted form (`N.0`). Returns the canonical
    text, or None if unchanged (no edit needed).

      100d   -> 100.0
      100.0d -> 100.0
      0.5f   -> 0.5
      1e10f  -> 1e10
      1.5    -> None (unchanged)
    """
    if not text:
        return None
    if text[-1] not in "dDfF":
        return None
    body = text[:-1]
    if "." in body or "e" in body.lower():
        return body
    return body + ".0"


def _contains_string_literal(node: Node) -> bool:
    """Recursive scan for `string_literal` descendants. Used by 3e.3's
    string-concat guard: `(a + b) + c` where one of the operand subtrees
    contains a string literal but the other doesn't is a mixed-type chain
    that can evaluate differently when re-associated."""
    if node.type == "string_literal":
        return True
    for c in node.children:
        if _contains_string_literal(c):
            return True
    return False


def _apply_edits(src_bytes: bytes, edits: list[tuple[int, int, bytes]]) -> bytes:
    """Apply non-overlapping byte-range replacements in source order."""
    edits.sort()
    out = bytearray()
    cursor = 0
    for start, end, replacement in edits:
        out.extend(src_bytes[cursor:start])
        out.extend(replacement)
        cursor = end
    out.extend(src_bytes[cursor:])
    return bytes(out)


def _strip_blank_lines(text: str) -> str:
    while True:
        new = _BLANK_LINE_RE.sub("\n", text)
        if new == text:
            return new
        text = new
