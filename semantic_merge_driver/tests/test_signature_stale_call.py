"""SignatureStaleCallStrategy — detector-cycle D2 (ISSUES #31, plan §2).

Fixture shapes mirror the S-D1 spec table (reports_detectors/specs/specs.csv,
D2 rows) restricted to the lane's design targets: same-file arity changes
with old-shape calls from the other side. Cross-category shapes, the plan-§2
guards (overloads with matching arity, varargs, builder/chained calls,
cross-file targets), and the lane's DOCUMENTED FN classes (same-arity type/
throws changes, Split/Merge Parameter) get negative fixtures.

Unit tests mock RM2 by patching the composed runner
(`RM2RenameConflictStrategy._run_rm2_pair`) keyed on the right-side text —
the test_rename_conflict.py `_patch_rm2_renames` precedent — with payloads
matching the PROBED location composition (the changed parameter rides along
as SINGLE_VARIABLE_DECLARATION next to the full METHOD_DECLARATIONs).
Fail-closed tests patch rename_conflict.subprocess like the rename lane's.
Image-gated tests pin the probed RM2 2.4.0 contract and run one end-to-end.

Each fixture hand-writes the MERGED text in the shape a structural merge
(mergiraf) produces for that scenario, exactly like MERGED_STALE in
test_unresolved_reference.py.
"""
from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.plugin_loader import StrategyLoader
from strategies.rm2_strategies import rename_conflict as rc
from strategies.rm2_strategies.signature_stale_call import (
    SignatureStaleCallStrategy,
    _absorbable_spans,
    _call_arity,
    _call_sites,
    _count_type_list,
    _declared_arities,
    _extract_arity_changes,
    _parse_method_decl,
)
from strategies.text_strategies.import_prune_usage import _FileView

FLAG = "SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"
dd = textwrap.dedent


@pytest.fixture
def strategy(monkeypatch):
    monkeypatch.setenv(FLAG, "1")
    return SignatureStaleCallStrategy()


def run(strategy, tmp_path, merged, base, ours, theirs, filename="Merged.java"):
    p = tmp_path / filename
    p.write_text(dd(merged), encoding="utf-8")
    return strategy.analyze(
        str(p),
        base_content=dd(base),
        ours_content=dd(ours),
        theirs_content=dd(theirs),
    )


def assert_flags(result, name):
    assert not result.is_clean, f"expected a flag for '{name}', got clean"
    assert any(f"'{name}'" in i.message for i in result.issues), \
        f"no issue mentions '{name}': {[i.message for i in result.issues]}"


def assert_clean(result):
    assert result.is_clean, \
        f"expected clean, got: {[(i.line_number, i.message) for i in result.issues]}"


# --- RM2 mock helpers (probed location composition) ---

def add_param_payload(old_decl, new_decl, changed_param="x : T"):
    return {
        "type": "Add Parameter",
        "leftSideLocations": [
            {"codeElementType": "METHOD_DECLARATION", "codeElement": old_decl},
        ],
        "rightSideLocations": [
            {"codeElementType": "SINGLE_VARIABLE_DECLARATION",
             "codeElement": changed_param},
            {"codeElementType": "METHOD_DECLARATION", "codeElement": new_decl},
        ],
    }


def remove_param_payload(old_decl, new_decl, changed_param="x : T"):
    return {
        "type": "Remove Parameter",
        "leftSideLocations": [
            {"codeElementType": "SINGLE_VARIABLE_DECLARATION",
             "codeElement": changed_param},
            {"codeElementType": "METHOD_DECLARATION", "codeElement": old_decl},
        ],
        "rightSideLocations": [
            {"codeElementType": "METHOD_DECLARATION", "codeElement": new_decl},
        ],
    }


def _patch_rm2(monkeypatch, by_right_text, calls=None):
    """Patch the composed RM2 runner; payloads keyed on right-side text."""
    def fake(self, left_content, right_text, basename):
        if calls is not None:
            calls.append(right_text)
        return by_right_text.get(right_text, [])

    monkeypatch.setattr(rc.RM2RenameConflictStrategy, "_run_rm2_pair", fake)
    return calls


# =========================================================================== #
# Canonical fixture — method parameter ADDED (buddycloud-analog, same-file)
# =========================================================================== #

P1_BASE = """\
    package p;

    public class Notifier {
        public void send(String host, int port) {
            System.out.println(host + port);
        }

        public void go() {
            send("h", 1);
        }
    }
    """
P1_OURS = """\
    package p;

    public class Notifier {
        public void send(String host, int port, boolean retry) {
            System.out.println(host + port + retry);
        }

        public void go() {
            send("h", 1, true);
        }
    }
    """
P1_THEIRS = """\
    package p;

    public class Notifier {
        public void send(String host, int port) {
            System.out.println(host + port);
        }

        public void go() {
            send("h", 1);
        }

        public void alert() {
            send("alert.example", 9090);
        }
    }
    """
P1_MERGED = """\
    package p;

    public class Notifier {
        public void send(String host, int port, boolean retry) {
            System.out.println(host + port + retry);
        }

        public void go() {
            send("h", 1, true);
        }

        public void alert() {
            send("alert.example", 9090);
        }
    }
    """

P1_PAYLOAD = [add_param_payload(
    "public send(host String, port int) : void",
    "public send(host String, port int, retry boolean) : void",
    "retry : boolean")]


def test_p1_param_added_theirs_stale_call(strategy, tmp_path, monkeypatch):
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_flags(result, "send")
    assert len(result.issues) == 1
    assert result.issues[0].line_number == 13
    assert result.issues[0].severity == "CRITICAL"
    assert result.issues[0].strategy_name == "SignatureStaleCall"
    assert "ours" in result.issues[0].message
    assert "theirs" in result.issues[0].message


def test_p2_symmetric_sides_swapped(strategy, tmp_path, monkeypatch):
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_THEIRS, P1_OURS)
    assert_flags(result, "send")
    assert result.issues[0].line_number == 13


def test_p1_multi_record_dedupe_still_flags(strategy, tmp_path, monkeypatch):
    """Probe G: multi-param additions emit one record per parameter, each
    carrying the same full old/new declarations — dedupe keeps the flag."""
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD + [add_param_payload(
        "public send(host String, port int) : void",
        "public send(host String, port int, retry boolean) : void",
        "retry : boolean")]})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_flags(result, "send")


# =========================================================================== #
# Parameter REMOVED (sonar-findbugs-analog, same-file)
# =========================================================================== #

P3_BASE = """\
    package p;

    public class ExecutorTest {
        void execute(boolean debug, boolean strict) {
            System.out.println(debug && strict);
        }

        void existing() {
            execute(true, false);
        }
    }
    """
P3_OURS = """\
    package p;

    public class ExecutorTest {
        void execute(boolean strict) {
            System.out.println(strict);
        }

        void existing() {
            execute(false);
        }
    }
    """
P3_THEIRS = """\
    package p;

    public class ExecutorTest {
        void execute(boolean debug, boolean strict) {
            System.out.println(debug && strict);
        }

        void existing() {
            execute(true, false);
        }

        void newTest() {
            execute(false, false);
        }
    }
    """
P3_MERGED = """\
    package p;

    public class ExecutorTest {
        void execute(boolean strict) {
            System.out.println(strict);
        }

        void existing() {
            execute(false);
        }

        void newTest() {
            execute(false, false);
        }
    }
    """

P3_PAYLOAD = [remove_param_payload(
    "execute(debug boolean, strict boolean) : void",
    "execute(strict boolean) : void",
    "debug : boolean")]


def test_p3_param_removed_stale_two_arg_call(strategy, tmp_path, monkeypatch):
    _patch_rm2(monkeypatch, {dd(P3_OURS): P3_PAYLOAD})
    result = run(strategy, tmp_path, P3_MERGED, P3_BASE, P3_OURS, P3_THEIRS)
    assert_flags(result, "execute")
    assert result.issues[0].line_number == 13


# =========================================================================== #
# Kept-from-base call (plan §2 "adds/KEEPS"; ardesco provenance analog)
# =========================================================================== #

P4_BASE = """\
    package p;

    public class Ops {
        void send(String host, int port) {
            System.out.println(host + port);
        }

        void notifyOps() {
            send("ops", 1);
        }
    }
    """
P4_OURS = """\
    package p;

    public class Ops {
        void send(String host, int port, boolean retry) {
            System.out.println(host + port + retry);
        }

        void notifyOps() {
            send("ops", 1, false);
        }
    }
    """
P4_THEIRS = """\
    package p;

    public class Ops {
        void send(String host, int port) {
            System.out.println(host + port);
        }

        void notifyOps() {
            send("ops", 1);
        }

        void audit() {
            System.out.println("audit");
        }
    }
    """
# Structural merge anchored ours' decl change but kept theirs' notifyOps body.
P4_MERGED = """\
    package p;

    public class Ops {
        void send(String host, int port, boolean retry) {
            System.out.println(host + port + retry);
        }

        void notifyOps() {
            send("ops", 1);
        }

        void audit() {
            System.out.println("audit");
        }
    }
    """

P4_PAYLOAD = [add_param_payload(
    "send(host String, port int) : void",
    "send(host String, port int, retry boolean) : void",
    "retry : boolean")]


def test_p4_kept_from_base_call_flags(strategy, tmp_path, monkeypatch):
    _patch_rm2(monkeypatch, {dd(P4_OURS): P4_PAYLOAD})
    result = run(strategy, tmp_path, P4_MERGED, P4_BASE, P4_OURS, P4_THEIRS)
    assert_flags(result, "send")
    assert result.issues[0].line_number == 9


# =========================================================================== #
# Constructor arity change (enderstone-analog, same-file)
# =========================================================================== #

P5_BASE = """\
    package p;

    public class Item {
        private final int id;

        Item(int id, int amount, int damage) {
            this.id = id + amount + damage;
        }

        static Item of() {
            return new Item(1, 2, 3);
        }
    }
    """
P5_OURS = """\
    package p;

    public class Item {
        private final int id;

        Item(int id, int amount, int damage, boolean nbt) {
            this.id = id + amount + damage + (nbt ? 1 : 0);
        }

        static Item of() {
            return new Item(1, 2, 3, true);
        }
    }
    """
P5_THEIRS = """\
    package p;

    public class Item {
        private final int id;

        Item(int id, int amount, int damage) {
            this.id = id + amount + damage;
        }

        static Item of() {
            return new Item(1, 2, 3);
        }

        static Item spawn() {
            return new Item(7, 8, 9);
        }
    }
    """
P5_MERGED = """\
    package p;

    public class Item {
        private final int id;

        Item(int id, int amount, int damage, boolean nbt) {
            this.id = id + amount + damage + (nbt ? 1 : 0);
        }

        static Item of() {
            return new Item(1, 2, 3, true);
        }

        static Item spawn() {
            return new Item(7, 8, 9);
        }
    }
    """

P5_PAYLOAD = [add_param_payload(
    "Item(id int, amount int, damage int)",
    "Item(id int, amount int, damage int, nbt boolean)",
    "nbt : boolean")]


def test_p5_constructor_arity_change_stale_new(strategy, tmp_path, monkeypatch):
    _patch_rm2(monkeypatch, {dd(P5_OURS): P5_PAYLOAD})
    result = run(strategy, tmp_path, P5_MERGED, P5_BASE, P5_OURS, P5_THEIRS,
                 filename="Item.java")
    assert_flags(result, "Item")
    assert result.issues[0].line_number == 15


def test_p5_ctor_plain_name_occurrence_never_counts(strategy, tmp_path, monkeypatch):
    """For constructor signatures only `new Name(…)` counts: a same-named
    3-arg METHOD call must not fire the constructor's arity change."""
    merged = """\
        package p;

        public class Item {
            private final int id;

            Item(int id, int amount, int damage, boolean nbt) {
                this.id = id + amount + damage + (nbt ? 1 : 0);
            }

            static Item of() {
                return new Item(1, 2, 3, true);
            }

            int total(int a, int b, int c) {
                return Item(a, b, c);
            }
        }
        """
    theirs = """\
        package p;

        public class Item {
            private final int id;

            Item(int id, int amount, int damage) {
                this.id = id + amount + damage;
            }

            static Item of() {
                return new Item(1, 2, 3);
            }

            int total(int a, int b, int c) {
                return Item(a, b, c);
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P5_OURS): P5_PAYLOAD})
    result = run(strategy, tmp_path, merged, P5_BASE, P5_OURS, theirs,
                 filename="Item.java")
    assert_clean(result)


# =========================================================================== #
# Zero-arg → one-arg (jcabi-shaped Add Parameter given a clean RM2 match)
# =========================================================================== #

P6_BASE = """\
    package p;

    public class Boot {
        private Config refresh() {
            return Config.load();
        }

        void boot() {
            refresh();
        }
    }
    """
P6_OURS = """\
    package p;

    public class Boot {
        private Config refresh(Mode mode) {
            return Config.load(mode);
        }

        void boot() {
            refresh(Mode.SAFE);
        }
    }
    """
P6_THEIRS = """\
    package p;

    public class Boot {
        private Config refresh() {
            return Config.load();
        }

        void boot() {
            refresh();
        }

        void recover() {
            refresh();
        }
    }
    """
P6_MERGED = """\
    package p;

    public class Boot {
        private Config refresh(Mode mode) {
            return Config.load(mode);
        }

        void boot() {
            refresh(Mode.SAFE);
        }

        void recover() {
            refresh();
        }
    }
    """

P6_PAYLOAD = [add_param_payload(
    "private refresh() : Config",
    "private refresh(mode Mode) : Config",
    "mode : Mode")]


def test_p6_zero_to_one_arg(strategy, tmp_path, monkeypatch):
    _patch_rm2(monkeypatch, {dd(P6_OURS): P6_PAYLOAD})
    result = run(strategy, tmp_path, P6_MERGED, P6_BASE, P6_OURS, P6_THEIRS)
    assert_flags(result, "refresh")
    assert result.issues[0].line_number == 13


# =========================================================================== #
# Literal-only stale argument (Angle-A finding 2, lane level)
# =========================================================================== #

P7_BASE = """\
    package p;

    public class Wire {
        void send(String host) {
            System.out.println(host);
        }

        void go() {
            send("h");
        }
    }
    """
P7_OURS = """\
    package p;

    public class Wire {
        void send(String host, int port) {
            System.out.println(host + port);
        }

        void go() {
            send("h", 1);
        }
    }
    """
P7_THEIRS = """\
    package p;

    public class Wire {
        void send(String host) {
            System.out.println(host);
        }

        void go() {
            send("h");
        }

        void alert() {
            send("boom");
        }
    }
    """
P7_MERGED = """\
    package p;

    public class Wire {
        void send(String host, int port) {
            System.out.println(host + port);
        }

        void go() {
            send("h", 1);
        }

        void alert() {
            send("boom");
        }
    }
    """

P7_PAYLOAD = [add_param_payload(
    "send(host String) : void",
    "send(host String, port int) : void",
    "port : int")]


def test_p7_literal_only_stale_argument_flags(strategy, tmp_path, monkeypatch):
    """A stale call whose only argument is a string literal must count as
    arity 1 — the blank-to-space projection would read it as `send()`."""
    _patch_rm2(monkeypatch, {dd(P7_OURS): P7_PAYLOAD})
    result = run(strategy, tmp_path, P7_MERGED, P7_BASE, P7_OURS, P7_THEIRS)
    assert_flags(result, "send")
    assert result.issues[0].line_number == 13


def test_p7_x_side_literal_leftover_suppresses(strategy, tmp_path, monkeypatch):
    """The self-consistency guard must also see literal-only leftovers: an
    X-side `send("legacy")` (old arity) means the breakage pre-exists X."""
    ours = """\
        package p;

        public class Wire {
            void send(String host, int port) {
                System.out.println(host + port);
            }

            void go() {
                send("h", 1);
            }

            void legacy() {
                send("legacy");
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(ours): P7_PAYLOAD})
    result = run(strategy, tmp_path, P7_MERGED, P7_BASE, ours, P7_THEIRS)
    assert_clean(result)


# =========================================================================== #
# Cross-category negatives
# =========================================================================== #

def test_n_rename_refactoring_is_not_this_lane(strategy, tmp_path, monkeypatch):
    """Pure renames (even with stale old-name callers) belong to
    RM2RenameConflict; this lane must stay silent."""
    payload = [{
        "type": "Rename Method",
        "leftSideLocations": [{"codeElementType": "METHOD_DECLARATION",
                               "codeElement": "public send(host String, port int) : void"}],
        "rightSideLocations": [{"codeElementType": "METHOD_DECLARATION",
                                "codeElement": "public dispatch(host String, port int) : void"}],
    }]
    _patch_rm2(monkeypatch, {dd(P1_OURS): payload})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


def test_n_add_param_with_name_mismatch_skipped(strategy, tmp_path, monkeypatch):
    """A rename+arity composite (names differ across the record) is the
    rename lane's territory — never matched by name here."""
    payload = [add_param_payload(
        "public send(host String, port int) : void",
        "public dispatch(host String, port int, retry boolean) : void",
        "retry : boolean")]
    _patch_rm2(monkeypatch, {dd(P1_OURS): payload})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


def test_n_import_prune_shape_silent(strategy, tmp_path, monkeypatch):
    """D1's category: import pruned + usage added — no signature evidence."""
    base = """\
        package p;
        import com.foo.Gadget;
        public class T {
            public void f(Gadget g) {}
        }
        """
    ours = """\
        package p;
        public class T {
            public void f() {}
        }
        """
    theirs = """\
        package p;
        import com.foo.Gadget;
        public class T {
            public void f(Gadget g) {}
            public Gadget make() { return new Gadget(); }
        }
        """
    merged = """\
        package p;
        public class T {
            public void f() {}
            public Gadget make() { return new Gadget(); }
        }
        """
    _patch_rm2(monkeypatch, {})
    result = run(strategy, tmp_path, merged, base, ours, theirs)
    assert_clean(result)


def test_n_clean_refactor_no_stale_call(strategy, tmp_path, monkeypatch):
    """X changed the signature and updated every call; Y touched something
    unrelated. Merged is consistent — silent."""
    theirs = """\
        package p;

        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }

            public void go() {
                send("h", 1);
            }

            public void audit() {
                System.out.println("audit");
            }
        }
        """
    merged = """\
        package p;

        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }

            public void go() {
                send("h", 1, true);
            }

            public void audit() {
                System.out.println("audit");
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, theirs)
    assert_clean(result)


def test_n_same_arity_type_change_documented_fn(strategy, tmp_path, monkeypatch):
    """DOCUMENTED FN (plan §2 arity-primary): same-arity parameter-type
    changes (ardesco/urbanairship shapes) are not flaggable file-locally."""
    payload = [{
        "type": "Change Parameter Type",
        "leftSideLocations": [
            {"codeElementType": "SINGLE_VARIABLE_DECLARATION", "codeElement": "port : int"},
            {"codeElementType": "METHOD_DECLARATION",
             "codeElement": "public send(host String, port int) : void"}],
        "rightSideLocations": [
            {"codeElementType": "SINGLE_VARIABLE_DECLARATION", "codeElement": "port : long"},
            {"codeElementType": "METHOD_DECLARATION",
             "codeElement": "public send(host String, port long) : void"}],
    }]
    _patch_rm2(monkeypatch, {dd(P1_OURS): payload})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


def test_n_split_parameter_documented_fn(strategy, tmp_path, monkeypatch):
    """DOCUMENTED FN: Split/Merge Parameter change arity but their location
    composition is unprobed — deliberately outside the accept set."""
    payload = [{
        "type": "Split Parameter",
        "leftSideLocations": [{"codeElementType": "METHOD_DECLARATION",
                               "codeElement": "public send(hostPort String) : void"}],
        "rightSideLocations": [{"codeElementType": "METHOD_DECLARATION",
                                "codeElement": "public send(host String, port int) : void"}],
    }]
    _patch_rm2(monkeypatch, {dd(P1_OURS): payload})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


# =========================================================================== #
# Guard negatives (plan §2 + prompt guards)
# =========================================================================== #

def test_g_overload_with_matching_arity_suppresses(strategy, tmp_path, monkeypatch):
    """Plan guard: an overload taking the OLD argument count survives in
    merged — the stale-looking call may bind it."""
    merged = """\
        package p;

        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }

            public void send(String host, int port) {
                send(host, port, false);
            }

            public void alert() {
                send("alert.example", 9090);
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


def test_g_varargs_signature_suppresses(strategy, tmp_path, monkeypatch):
    """Plan guard: varargs — every arity ≥ fixed prefix stays legal."""
    payload = [add_param_payload(
        "public send(host String, args Object...) : void",
        "public send(host String, port int, args Object...) : void",
        "port : int")]
    _patch_rm2(monkeypatch, {dd(P1_OURS): payload})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


def test_g_varargs_declaration_in_file_suppresses(strategy, tmp_path, monkeypatch):
    """A varargs declaration of the name anywhere in any version suppresses
    even when the changed signature itself is not varargs."""
    merged = """\
        package p;

        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }

            void send(Object... parts) {
                System.out.println(parts.length);
            }

            public void alert() {
                send("alert.example", 9090);
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


def test_g_qualified_and_chained_calls_never_count(strategy, tmp_path, monkeypatch):
    """Prompt guards: builder/chained calls and receivers the file-local view
    cannot type — `router.send(…)`, `route().send(…)`, `this.send(…)`,
    `Notifier::send` are not stale sites."""
    theirs = """\
        package p;

        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }

            public void go() {
                send("h", 1);
            }

            public void alert(Notifier router) {
                router.send("alert.example", 9090);
                route().send("alert.example", 9090);
                this.send("fallback.example", 9090);
            }

            private Notifier route() { return this; }
        }
        """
    merged = """\
        package p;

        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }

            public void go() {
                send("h", 1, true);
            }

            public void alert(Notifier router) {
                router.send("alert.example", 9090);
                route().send("alert.example", 9090);
                this.send("fallback.example", 9090);
            }

            private Notifier route() { return this; }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, theirs)
    assert_clean(result)


def test_g_static_import_suppresses_name(strategy, tmp_path, monkeypatch):
    """A static import can provide the unqualified name cross-file."""
    theirs = """\
        package p;

        import static net.wire.Util.send;

        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }

            public void go() {
                send("h", 1);
            }

            public void alert() {
                send("alert.example", 9090);
            }
        }
        """
    merged = """\
        package p;

        import static net.wire.Util.send;

        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }

            public void go() {
                send("h", 1, true);
            }

            public void alert() {
                send("alert.example", 9090);
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, theirs)
    assert_clean(result)


def _supertyped(text: str) -> str:
    return text.replace("public class Notifier {",
                        "public class Notifier extends BaseNotifier {")


def test_g_supertyped_class_absorbs(strategy, tmp_path, monkeypatch):
    """Prompt guard (cross-file targets): a supertype may declare an
    overload the file-local view cannot see — calls inside `extends`-headed
    bodies are suppressed."""
    _patch_rm2(monkeypatch, {dd(_supertyped(P1_OURS)): P1_PAYLOAD})
    result = run(strategy, tmp_path, _supertyped(P1_MERGED), _supertyped(P1_BASE),
                 _supertyped(P1_OURS), _supertyped(P1_THEIRS))
    assert_clean(result)


def test_g_anonymous_class_body_absorbs(strategy, tmp_path, monkeypatch):
    theirs = """\
        package p;

        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }

            public void go() {
                send("h", 1);
            }

            Runnable alert() {
                return new Runnable() {
                    public void run() {
                        send("alert.example", 9090);
                    }
                };
            }
        }
        """
    merged = """\
        package p;

        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }

            public void go() {
                send("h", 1, true);
            }

            Runnable alert() {
                return new Runnable() {
                    public void run() {
                        send("alert.example", 9090);
                    }
                };
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, theirs)
    assert_clean(result)


def test_g_enum_body_absorbs(strategy, tmp_path, monkeypatch):
    """Enums implicitly extend java.lang.Enum — their bodies are absorbable."""
    theirs = """\
        package p;

        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }

            public void go() {
                send("h", 1);
            }

            enum Channel {
                OPS;
                void alert() {
                    send("alert.example", 9090);
                }
            }
        }
        """
    merged = """\
        package p;

        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }

            public void go() {
                send("h", 1, true);
            }

            enum Channel {
                OPS;
                void alert() {
                    send("alert.example", 9090);
                }
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, theirs)
    assert_clean(result)


def test_g_object_method_name_never_flags(strategy, tmp_path, monkeypatch):
    """`wait`, `equals`, … can always bind java.lang.Object's members."""
    payload = [add_param_payload(
        "public wait(reason String) : void",
        "public wait(reason String, hard boolean) : void",
        "hard : boolean")]
    merged = """\
        package p;

        public class Latch {
            public void wait(String reason, boolean hard) {
                System.out.println(reason + hard);
            }

            void block() {
                wait("shutdown");
            }
        }
        """
    theirs = """\
        package p;

        public class Latch {
            public void wait(String reason) {
                System.out.println(reason);
            }

            void block() {
                wait("shutdown");
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): payload})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, theirs)
    assert_clean(result)


def test_g_x_side_leftover_old_call_suppresses(strategy, tmp_path, monkeypatch):
    """X kept an old-arity call of its own: the breakage (or its absorption)
    pre-exists X — not merge-induced."""
    ours = """\
        package p;

        public class Notifier {
            public void send(String host, int port, boolean retry) {
                System.out.println(host + port + retry);
            }

            public void go() {
                send("h", 1, true);
            }

            void legacy() {
                send("legacy", 0);
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(ours): P1_PAYLOAD})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, ours, P1_THEIRS)
    assert_clean(result)


def test_g_y_side_without_old_call_suppresses(strategy, tmp_path, monkeypatch):
    """A merged-only artifact: if Y's own text never calls the name at the
    old arity, the stale-looking merged call is attributable to neither
    side — suppressed."""
    theirs = """\
        package p;

        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }

            public void go() {
                System.out.println("inlined");
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, theirs)
    assert_clean(result)


def test_g_concurrent_signature_edits_suppress(strategy, tmp_path, monkeypatch):
    theirs_payload = [add_param_payload(
        "public send(host String, port int) : void",
        "public send(host String, port int, tag String) : void",
        "tag : String")]
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD,
                             dd(P1_THEIRS): theirs_payload})
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


def test_g_change_dropped_by_merge_suppresses(strategy, tmp_path, monkeypatch):
    """Merge kept the OLD declaration wholesale minus ours' region — the
    old-arity calls are consistent with the surviving declaration."""
    merged = """\
        package p;

        public class Notifier {
            public void send(String host, int port) {
                System.out.println(host + port);
            }

            public void go() {
                send("h", 1);
            }

            public void alert() {
                send("alert.example", 9090);
            }
        }
        """
    _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD})
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)


def test_g_conflict_markers_abstain(strategy, tmp_path, monkeypatch):
    calls = _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD}, calls=[])
    merged = P1_MERGED + """\
    // trailing context
    <<<<<<< ours
    int x = 1;
    =======
    int x = 2;
    >>>>>>> theirs
    """
    result = run(strategy, tmp_path, merged, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)
    assert calls == []  # abstention precedes any RM2 invocation


def test_g_flag_off_returns_clean_without_rm2(tmp_path, monkeypatch):
    monkeypatch.delenv(FLAG, raising=False)
    calls = _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD}, calls=[])
    result = run(SignatureStaleCallStrategy(), tmp_path,
                 P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_clean(result)
    assert calls == []


def test_g_missing_parents_abstain(strategy, tmp_path, monkeypatch):
    calls = _patch_rm2(monkeypatch, {}, calls=[])
    p = tmp_path / "Merged.java"
    p.write_text(dd(P1_MERGED), encoding="utf-8")
    assert strategy.analyze(str(p), base_content=dd(P1_BASE)).is_clean
    assert strategy.analyze(str(p), base_content=dd(P1_BASE),
                            ours_content=dd(P1_OURS)).is_clean
    assert strategy.analyze(str(p), base_content=None,
                            ours_content=dd(P1_OURS),
                            theirs_content=dd(P1_THEIRS)).is_clean
    assert calls == []


def test_g_non_java_file_abstains(strategy, tmp_path, monkeypatch):
    calls = _patch_rm2(monkeypatch, {dd(P1_OURS): P1_PAYLOAD}, calls=[])
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS,
                 filename="Merged.kt")
    assert_clean(result)
    assert calls == []


@pytest.mark.parametrize("fixture", [
    (P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS, P1_PAYLOAD),
    (P5_MERGED, P5_BASE, P5_OURS, P5_THEIRS, P5_PAYLOAD),
    (P6_MERGED, P6_BASE, P6_OURS, P6_THEIRS, P6_PAYLOAD),
])
def test_g_merged_identical_to_parent_is_clean(strategy, tmp_path, monkeypatch, fixture):
    """Soundness invariant (S-D2 addendum pattern): a merged file
    byte-identical to a parent can never be flagged — whatever it contains
    pre-existed in that parent."""
    merged, base, ours, theirs, payload = fixture
    calls = _patch_rm2(monkeypatch, {dd(ours): payload}, calls=[])
    for parent in (ours, theirs):
        result = run(strategy, tmp_path, parent, base, ours, theirs)
        assert_clean(result)
    assert calls == []


# =========================================================================== #
# Fail-closed paths (real _run_rm2_pair, patched subprocess — rename-lane style)
# =========================================================================== #

def _write_merged(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "Merged.java"
    p.write_text(dd(content), encoding="utf-8")
    return p


def _analyze_p1(strategy, merged_path):
    return strategy.analyze(
        str(merged_path), base_content=dd(P1_BASE),
        ours_content=dd(P1_OURS), theirs_content=dd(P1_THEIRS))


def _assert_inconclusive(result):
    assert not result.is_clean
    assert any("inconclusive" in i.message for i in result.issues)


def test_fc_docker_missing_fails_closed(strategy, tmp_path, monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("docker not on PATH")

    monkeypatch.setattr(rc.subprocess, "run", boom)
    _assert_inconclusive(_analyze_p1(strategy, _write_merged(tmp_path, P1_MERGED)))


def test_fc_nonzero_rc_fails_closed(strategy, tmp_path, monkeypatch):
    monkeypatch.setattr(rc.subprocess, "run",
                        lambda *a, **k: SimpleNamespace(returncode=3, stdout="", stderr="rm2 exploded"))
    _assert_inconclusive(_analyze_p1(strategy, _write_merged(tmp_path, P1_MERGED)))


def test_fc_malformed_json_fails_closed(strategy, tmp_path, monkeypatch):
    monkeypatch.setattr(rc.subprocess, "run",
                        lambda *a, **k: SimpleNamespace(returncode=0, stdout="not json", stderr=""))
    _assert_inconclusive(_analyze_p1(strategy, _write_merged(tmp_path, P1_MERGED)))


def test_fc_timeout_fails_closed(strategy, tmp_path, monkeypatch):
    def timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="docker run …", timeout=1)

    monkeypatch.setattr(rc.subprocess, "run", timeout)
    _assert_inconclusive(_analyze_p1(strategy, _write_merged(tmp_path, P1_MERGED)))


def test_fc_unreadable_merged_fails_closed(strategy, tmp_path):
    result = _analyze_p1(strategy, tmp_path / "does_not_exist.java")
    _assert_inconclusive(result)


# =========================================================================== #
# Helper unit tests
# =========================================================================== #

@pytest.mark.parametrize("ce, expected", [
    # Probed shapes (merge-tools/refactoring-miner:2.4.0, 2026-07-16).
    ("public send(host String, port int) : int", ("send", 2, False, False)),
    ("private static foo() : void", ("foo", 0, False, False)),
    ("public Foo(id int, amount int)", ("Foo", 2, True, False)),
    ("Item(id int, amount int, damage int)", ("Item", 3, True, False)),
    ("public log(fmt String, args Object...) : void", ("log", 2, False, True)),
    ("public put(m Map<String,List<Integer>>, ttl int) : void", ("put", 2, False, False)),
    ("public m() : void", ("m", 0, False, False)),
])
def test_parse_method_decl(ce, expected):
    assert _parse_method_decl(ce) == expected


@pytest.mark.parametrize("ce", ["", "no parens here", "((", "m(unbalanced"])
def test_parse_method_decl_rejects_malformed(ce):
    assert _parse_method_decl(ce) is None


@pytest.mark.parametrize("params, expected", [
    ("", 0), ("   ", 0),
    ("a int", 1),
    ("a int, b int", 2),
    ("m Map<String,List<Integer>>, ttl int", 2),
    ("m Map<String,Integer>", 1),
    ("a int[], b String", 2),
])
def test_count_type_list(params, expected):
    assert _count_type_list(params) == expected


@pytest.mark.parametrize("call, expected", [
    (")", 0), ("  )", 0),
    ("a)", 1), ("a, b)", 2),
    ("f(a, b), c)", 2),
    ("new int[]{1, 2}, x)", 2),
    ("new HashMap<String, Integer>(), x)", 2),        # generic hidden
    ("a < b, c > (d))", 2),                           # comparisons stay visible
    ("x -> f(x, y), z)", 2),                          # lambda body's call nested
    ("(a, b) -> a, c)", 2),                           # lambda params nested
    ("flag ? x : y, z)", 2),
    ("Foo::bar, x)", 2),
    ("(List<String>) x, y)", 2),                      # cast parens nest
    ("a, (b", None),                                  # unbalanced merge artifact
])
def test_call_arity(call, expected):
    assert _call_arity(call, 0) == expected


def test_call_arity_ambiguous_generic_poisons_site():
    # `Config<String> cfg` — a generic followed by an identifier does not
    # occur in call arguments; the site must not be guessed toward FLAG.
    assert _call_arity("Config<String> cfg, 2)", 0) is None


def test_call_arity_constant_shaped_angle_pieces_poison_site():
    # `a < LIMIT, X_MAX > (y)` — a non-new-rooted "generic" before `(` is
    # the comparison-pair trap; never guessed either way.
    assert _call_arity("a < LIMIT, X_MAX > (y))", 0) is None


def test_call_arity_pascalcase_comparison_pair_poisons_site():
    # Angle-A finding 1: `dispatch(Width < Height, Depth > (n))` is a legal
    # 2-arg call (two comparisons); classifying `<Height, Depth>` as a
    # generic would undercount to 1 and could FALSE-FLAG. Not new-rooted +
    # `(` follower → ambiguous → site dropped, never miscounted.
    assert _call_arity("Width < Height, Depth > (n))", 0) is None


def test_call_arity_new_rooted_generic_counts_normally():
    # Angle-A finding 3: `new Box<T>()` must stay countable — single-letter
    # type arguments are ubiquitous; the new-rooted rule admits them.
    assert _call_arity("new Box<T>(), x)", 0) == 2
    assert _call_arity("new java.util.ArrayList<T>())", 0) == 1


def test_call_arity_counts_literal_only_arguments():
    # Angle-A finding 2: literal-only argument lists must count — under a
    # blank-to-space projection `send("boom")` reads as arity 0, which both
    # misses genuine stale calls and false-flags legal 1-arg calls when the
    # old arity was 0. _strip_for_arity keeps a placeholder per literal.
    from strategies.rm2_strategies.signature_stale_call import _strip_for_arity
    t = _strip_for_arity('send("boom"); log(\'c\'); empty(); doc(/* x */);')
    assert _call_arity(t, t.index("send(") + 5) == 1
    assert _call_arity(t, t.index("log(") + 4) == 1
    assert _call_arity(t, t.index("empty(") + 6) == 0
    assert _call_arity(t, t.index("doc(") + 4) == 0  # comments stay contentless


def test_strip_for_arity_geometry_matches_structural_stripper():
    from strategies.rm2_strategies.signature_stale_call import _strip_for_arity
    from strategies.text_strategies.import_prune_usage import (
        _strip_comments_and_strings,
    )
    src = dd('''\
        class C { // comment "quoted"
            String s = """
                text block, with, commas""";
            void f() { g("a", 'b', /* c */ h()); }
        }
        ''')
    a = _strip_for_arity(src)
    b = _strip_comments_and_strings(src)
    assert len(a) == len(b) == len(src)
    # identical geometry: newlines and every non-blanked byte agree
    for i, (ca, cb) in enumerate(zip(a, b)):
        if ca != cb:
            assert ca == "\x00" and cb == " ", (i, ca, cb)


def test_declared_arities_method_forms():
    stripped = dd("""\
        class C {
            void m(int a) {}
            int[] m(int a, int b) throws E { return null; }
            abstract void m(int a, int b, int c);
            static List<String> m(int a, int b, int c, int d) { return null; }
        }
        """)
    assert _declared_arities(stripped, "m") == {1, 2, 3, 4}


def test_declared_arities_constructor_forms():
    stripped = dd("""\
        class C {
            private int x;
            C() { }
            C(int x) throws E { this.x = x; }
            void f() { new C(1); }
        }
        """)
    assert _declared_arities(stripped, "C") == {0, 1}


def test_declared_arities_excludes_calls():
    stripped = dd("""\
        class C {
            void f() {
                m(1);
                int r = m(1, 2);
                return m(1, 2, 3);
            }
        }
        """)
    assert _declared_arities(stripped, "m") == set()


def test_declared_arities_record_header():
    stripped = "record Point(int x, int y) implements Shape { }\n"
    assert _declared_arities(stripped, "Point") == {2}


def _sites(src: str, name: str, is_ctor: bool):
    from strategies.rm2_strategies.signature_stale_call import _strip_for_arity
    return _call_sites(_FileView(dd(src)), name, is_ctor, _strip_for_arity(dd(src)))


def test_call_sites_arrow_call_is_a_site_not_a_decl():
    """`case X -> m(1);` and `x -> m(1)` are call sites: the `>` of an arrow
    must not read as a generic-type close (declaration prefix)."""
    sites = _sites("""\
        class C {
            void f(int k) {
                switch (k) {
                    case 1 -> m(1);
                    default -> m(2);
                }
            }
        }
        """, "m", is_ctor=False)
    assert [s.arity for s in sites] == [1, 1]


def test_call_sites_qualified_and_methodref_excluded():
    sites = _sites("""\
        class C {
            void f() {
                m(1);
                obj.m(2);
                this.m(3);
                Runnable r = C::m;
            }
        }
        """, "m", is_ctor=False)
    assert len(sites) == 1 and sites[0].arity == 1


def test_call_sites_ctor_requires_new_prefix():
    src = """\
        class C {
            static C of() { return new C(1); }
            int C(int a, int b) { return a + b; }   // pathological same-named method
            void f() { int x = C(1, 2); }
        }
        """
    ctor_sites = _sites(src, "C", is_ctor=True)
    assert [s.arity for s in ctor_sites] == [1]
    method_sites = _sites(src, "C", is_ctor=False)
    assert [s.arity for s in method_sites] == [2]


def test_call_sites_literal_only_argument_counts():
    """Angle-A finding 2 at the site level: `send("boom")` is arity 1."""
    sites = _sites("""\
        class C {
            void f() {
                send("boom");
            }
        }
        """, "send", is_ctor=False)
    assert [s.arity for s in sites] == [1]


def test_absorbable_spans_shapes():
    assert _absorbable_spans("class A { void f() { m(1); } }") == []
    assert len(_absorbable_spans("class A extends B { }")) == 1
    assert len(_absorbable_spans("class A implements I { }")) == 1
    assert len(_absorbable_spans("enum E { X; }")) == 1
    assert len(_absorbable_spans(
        "class A { Runnable r = new Runnable() { public void run() {} }; }")) == 1
    # Type-parameter bounds are not supertypes.
    assert _absorbable_spans("class A<T extends Comparable<T>> { }") == []
    # new without a body is not an anonymous class.
    assert _absorbable_spans("class A { Object o = new Object(); }") == []
    # Angle-A finding 4: type-use annotations between `new` and the type.
    assert len(_absorbable_spans(
        "class A { Base b = new @NonNull Base() { void g() {} }; }")) == 1


def test_extract_arity_changes_selection_and_skips():
    changes = _extract_arity_changes([
        add_param_payload("public a(x int) : void", "public a(x int, y int) : void"),
        add_param_payload("public b(x int) : void", "public c(x int, y int) : void"),  # name mismatch
        add_param_payload("public d(x int) : void", "public d(y int) : void"),         # equal arity
        {"type": "Add Parameter", "leftSideLocations": [],
         "rightSideLocations": []},                                                    # no declarations
        {"type": "Extract Method",
         "leftSideLocations": [{"codeElementType": "METHOD_DECLARATION",
                                "codeElement": "public e() : void"}],
         "rightSideLocations": [{"codeElementType": "METHOD_DECLARATION",
                                 "codeElement": "public e(x int) : void"}]},           # wrong type
    ])
    assert [(c.name, c.old_arity, c.new_arity) for c in changes] == [("a", 1, 2)]


def test_loader_registers_each_strategy_once():
    """Guard against plugin_loader double-discovery: importing a strategy
    CLASS into another strategy module would register it twice (the loader
    walks module attributes) — this lane imports modules instead."""
    names = [s.name for s in StrategyLoader(None).load_strategies()]
    for expected in ("RM2RenameConflict", "SignatureStaleCall", "ImportPruneUsage"):
        assert names.count(expected) == 1, f"{expected} registered {names.count(expected)}×: {names}"


# =========================================================================== #
# Image-gated integration: pin the probed RM2 contract + one end-to-end
# =========================================================================== #

def _image_available() -> bool:
    try:
        proc = subprocess.run(
            ["docker", "image", "inspect", rc.RM2_IMAGE],
            capture_output=True,
            timeout=10,
        )
        return proc.returncode == 0
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return False


def _rm2_pair(tmp_path: Path, left: str, right: str) -> list:
    """Run the pair through the PRODUCTION runner (the lane's composed
    RM2RenameConflictStrategy._run_rm2_pair) so these contract probes pin
    the image's output against the exact invocation stack the detector
    uses — a probe passing against a stale hand-copied docker command line
    would be worthless."""
    refs = SignatureStaleCallStrategy()._rm2._run_rm2_pair(dd(left), dd(right), "Foo.java")
    assert refs is not None, "RM2 invocation failed (see stderr)"
    return refs


needs_image = pytest.mark.skipif(
    not _image_available(), reason=f"Docker or {rc.RM2_IMAGE} not available")


@needs_image
def test_integration_add_parameter_contract_probe(tmp_path):
    """Pin the probed Add Parameter composition: full METHOD_DECLARATIONs on
    both sides, `name Type` parameter rendering, ` : returnType` suffix."""
    refs = _rm2_pair(tmp_path, """\
        package com.example;
        public class Foo {
            public int send(String host, int port) { return port; }
            public void go() { send("h", 1); }
        }
        """, """\
        package com.example;
        public class Foo {
            public int send(String host, int port, boolean retry) { return port; }
            public void go() { send("h", 1, true); }
        }
        """)
    adds = [r for r in refs if r.get("type") == "Add Parameter"]
    assert adds, f"expected Add Parameter, got {[r.get('type') for r in refs]}"
    changes = _extract_arity_changes(adds)
    assert [(c.name, c.old_arity, c.new_arity, c.is_ctor) for c in changes] == \
        [("send", 2, 3, False)]
    assert "host String" in changes[0].old_decl
    assert changes[0].old_decl.rsplit(":", 1)[-1].strip() == "int"


@needs_image
def test_integration_constructor_contract_probe(tmp_path):
    """Constructor Add Parameter: codeElement has NO ` : returnType` suffix
    and parses as is_ctor=True."""
    refs = _rm2_pair(tmp_path, """\
        package com.example;
        public class Foo {
            private final int id;
            public Foo(int id) {
                this.id = id;
            }
        }
        """, """\
        package com.example;
        public class Foo {
            private final int id;
            public Foo(int id, boolean nbt) {
                this.id = id;
            }
        }
        """)
    changes = _extract_arity_changes(refs)
    assert [(c.name, c.old_arity, c.new_arity, c.is_ctor) for c in changes] == \
        [("Foo", 1, 2, True)]


@needs_image
def test_integration_varargs_rendering_probe(tmp_path):
    """Varargs render as `Type...` — the signature-level varargs guard keys
    off exactly that text."""
    refs = _rm2_pair(tmp_path, """\
        package com.example;
        public class Foo {
            public void log(String fmt, Object... args) { System.out.println(fmt + args.length); }
            public void go() { log("x", 1, 2); }
        }
        """, """\
        package com.example;
        public class Foo {
            public void log(int level, String fmt, Object... args) { System.out.println(level + fmt + args.length); }
            public void go() { log(1, "x", 1, 2); }
        }
        """)
    changes = _extract_arity_changes(refs)
    assert len(changes) == 1 and changes[0].varargs is True


@needs_image
def test_integration_kept_overload_emits_no_arity_change(tmp_path):
    """The core FP-safety assumption: when the old-arity overload SURVIVES,
    RM2 matches it exactly and reports no Add/Remove Parameter."""
    refs = _rm2_pair(tmp_path, """\
        package com.example;
        public class Foo {
            public void m(int a) { System.out.println(a); }
            public void go() { m(1); }
        }
        """, """\
        package com.example;
        public class Foo {
            public void m(int a) { System.out.println(a); }
            public void m(int a, int b) { System.out.println(a + b); }
            public void go() { m(1); m(1, 2); }
        }
        """)
    assert not [r for r in refs if r.get("type") in ("Add Parameter", "Remove Parameter")]


@needs_image
def test_integration_end_to_end_flags_p1(tmp_path, monkeypatch):
    monkeypatch.setenv(FLAG, "1")
    merged_path = tmp_path / "Notifier.java"
    merged_path.write_text(dd(P1_MERGED), encoding="utf-8")
    result = SignatureStaleCallStrategy().analyze(
        str(merged_path), base_content=dd(P1_BASE),
        ours_content=dd(P1_OURS), theirs_content=dd(P1_THEIRS))
    assert not result.is_clean
    assert any("'send'" in i.message and i.line_number == 13 for i in result.issues)
