"""ImportPruneUsageStrategy — detector-cycle D1 (ISSUES #31, plan §2).

Fixture shapes mirror the S-D1 spec table (reports_detectors/specs/specs.csv,
D1 rows): every distinct sub-shape observed on derivation units gets a
positive fixture, and the plan-§2 guards + cross-category shapes get
negative fixtures. Pure text lane — no Joern, no Docker; tests always run.

Each fixture hand-writes the MERGED text in the shape a structural merge
(mergiraf) produces for that scenario, exactly like MERGED_STALE in
test_unresolved_reference.py.
"""
import textwrap

import pytest

from core.plugin_loader import StrategyLoader
from strategies.text_strategies.import_prune_usage import ImportPruneUsageStrategy

FLAG = "SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"


@pytest.fixture
def strategy(monkeypatch):
    monkeypatch.setenv(FLAG, "1")
    return ImportPruneUsageStrategy()


def run(strategy, tmp_path, merged, base, ours, theirs, filename="Merged.java"):
    p = tmp_path / filename
    p.write_text(textwrap.dedent(merged), encoding="utf-8")
    return strategy.analyze(
        str(p),
        base_content=textwrap.dedent(base),
        ours_content=textwrap.dedent(ours),
        theirs_content=textwrap.dedent(theirs),
    )


def assert_flags(result, symbol):
    assert not result.is_clean, f"expected a flag for '{symbol}', got clean"
    assert any(f"'{symbol}'" in i.message for i in result.issues), \
        f"no issue mentions '{symbol}': {[i.message for i in result.issues]}"


# =========================================================================== #
# Positive fixtures — one per distinct D1 spec shape
# =========================================================================== #

# P1 — removed type import: THEIRS prunes, OURS adds usage
# (cternes_openkeepass shape: `import ...Group;` removed by theirs; ours'
# new test method uses Group).
P1_BASE = """\
    package de.slackspace.openkeepass.reader;

    import de.slackspace.openkeepass.domain.Group;
    import java.io.IOException;

    public class KeepassDatabaseReaderTest {
        public void existing() throws IOException {
            Group root = null;
        }
    }
    """
P1_OURS = """\
    package de.slackspace.openkeepass.reader;

    import de.slackspace.openkeepass.domain.Group;
    import java.io.IOException;

    public class KeepassDatabaseReaderTest {
        public void existing() throws IOException {
            Group root = null;
        }

        public void newTest() {
            Group group = database().getGroupByName("SomeGroup");
        }

        private Database database() { return null; }
    }
    """
P1_THEIRS = """\
    package de.slackspace.openkeepass.reader;

    import java.io.IOException;

    public class KeepassDatabaseReaderTest {
        public void existing() throws IOException {
        }
    }
    """
P1_MERGED = """\
    package de.slackspace.openkeepass.reader;

    import java.io.IOException;

    public class KeepassDatabaseReaderTest {
        public void existing() throws IOException {
        }

        public void newTest() {
            Group group = database().getGroupByName("SomeGroup");
        }

        private Database database() { return null; }
    }
    """


def test_p1_removed_type_import_theirs_prunes_ours_uses(strategy, tmp_path):
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_flags(result, "Group")
    line = next(i.line_number for i in result.issues if "'Group'" in i.message)
    assert line == 10  # first unqualified Group usage in merged


def test_p1_symmetric_ours_prunes_theirs_uses(strategy, tmp_path):
    # P2 — same scenario with the sides swapped (mikera_vectorz shape).
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_THEIRS, P1_OURS)
    assert_flags(result, "Group")


# P3 — removed EXPLICIT STATIC import, call-form member usage
# (apache_commons-collections shape: `import static ...Assertions.fail;`
# removed by theirs; ours adds fail(...) calls). The surviving unrelated
# TYPE wildcard must NOT suppress a member candidate.
P3_BASE = """\
    package org.apache.commons.collections4;

    import static org.junit.jupiter.api.Assertions.fail;
    import java.util.*;

    public class CollectionUtilsTest {
        public void existing() {
            List<String> l = new ArrayList<>();
        }
    }
    """
P3_OURS = """\
    package org.apache.commons.collections4;

    import static org.junit.jupiter.api.Assertions.fail;
    import java.util.*;

    public class CollectionUtilsTest {
        public void existing() {
            List<String> l = new ArrayList<>();
        }

        public void testPartition() {
            fail("failed to check if input chunk size is greater than 0");
        }
    }
    """
P3_THEIRS = """\
    package org.apache.commons.collections4;

    import java.util.*;

    public class CollectionUtilsTest {
        public void existing() {
            List<String> l = new ArrayList<>();
        }
    }
    """
P3_MERGED = """\
    package org.apache.commons.collections4;

    import java.util.*;

    public class CollectionUtilsTest {
        public void existing() {
            List<String> l = new ArrayList<>();
        }

        public void testPartition() {
            fail("failed to check if input chunk size is greater than 0");
        }
    }
    """


def test_p3_removed_static_import_member_call(strategy, tmp_path):
    result = run(strategy, tmp_path, P3_MERGED, P3_BASE, P3_OURS, P3_THEIRS)
    assert_flags(result, "fail")


# P4 — REPLACED import under a different simple name, annotation usage
# (jenkinsci_build-timeout shape: javax.annotation.Nonnull ->
# edu.umd.cs.findbugs.annotations.NonNull by theirs; ours adds @Nonnull).
P4_BASE = """\
    package hudson.plugins.build_timeout;

    import javax.annotation.Nonnull;

    public class BuildTimeOutOperation {
        public void existing(@Nonnull String reason) {
        }
    }
    """
P4_OURS = """\
    package hudson.plugins.build_timeout;

    import javax.annotation.Nonnull;

    public class BuildTimeOutOperation {
        public void existing(@Nonnull String reason) {
        }

        public void addAction(@Nonnull String build, @Nonnull String reason) {
        }
    }
    """
P4_THEIRS = """\
    package hudson.plugins.build_timeout;

    import edu.umd.cs.findbugs.annotations.NonNull;

    public class BuildTimeOutOperation {
        public void existing(@NonNull String reason) {
        }
    }
    """
P4_MERGED = """\
    package hudson.plugins.build_timeout;

    import edu.umd.cs.findbugs.annotations.NonNull;

    public class BuildTimeOutOperation {
        public void existing(@NonNull String reason) {
        }

        public void addAction(@Nonnull String build, @Nonnull String reason) {
        }
    }
    """


def test_p4_replaced_import_simple_name_changed_annotation_usage(strategy, tmp_path):
    result = run(strategy, tmp_path, P4_MERGED, P4_BASE, P4_OURS, P4_THEIRS)
    assert_flags(result, "Nonnull")


# P5 — TYPE wildcard narrowed to an explicit set missing the symbol
# (jnr_jnr-unixsocket shape: ours replaced `import jnr.ffi.*;` with explicit
# imports; theirs' added method needs Struct).
P5_BASE = """\
    package jnr.unixsocket;

    import jnr.ffi.*;

    public class Native {
        public static int existing(Pointer p) {
            return 0;
        }
    }
    """
P5_OURS = """\
    package jnr.unixsocket;

    import jnr.ffi.LastError;
    import jnr.ffi.Pointer;

    public class Native {
        public static int existing(Pointer p) {
            return LastError.value();
        }
    }
    """
P5_THEIRS = """\
    package jnr.unixsocket;

    import jnr.ffi.*;

    public class Native {
        public static int existing(Pointer p) {
            return 0;
        }

        public static int getsockopt(int s, Struct data) {
            Pointer struct_ptr = Struct.getMemory(data);
            return struct_ptr == null ? -1 : 0;
        }
    }
    """
P5_MERGED = """\
    package jnr.unixsocket;

    import jnr.ffi.LastError;
    import jnr.ffi.Pointer;

    public class Native {
        public static int existing(Pointer p) {
            return LastError.value();
        }

        public static int getsockopt(int s, Struct data) {
            Pointer struct_ptr = Struct.getMemory(data);
            return struct_ptr == null ? -1 : 0;
        }
    }
    """


def test_p5_type_wildcard_narrowed(strategy, tmp_path):
    result = run(strategy, tmp_path, P5_MERGED, P5_BASE, P5_OURS, P5_THEIRS)
    assert_flags(result, "Struct")
    # the local declared in the added code must NOT be flagged
    assert not any("'struct_ptr'" in i.message for i in result.issues)
    # Pointer/LastError stay covered by the explicit imports
    assert not any("'Pointer'" in i.message for i in result.issues)


# P6 — STATIC wildcard narrowed, ALL_CAPS constant usage
# (jmrozanec_cron-utils shape: theirs narrowed CronFieldName.* to an explicit
# list without DAY_OF_YEAR; ours' added code uses the constant).
P6_BASE = """\
    package com.cronutils.builder;

    import static com.cronutils.model.field.CronFieldName.*;
    import static com.cronutils.utils.Preconditions.checkState;

    public class CronBuilder {
        public CronBuilder withDoW(String expression) {
            return addField(DAY_OF_WEEK, expression);
        }

        private CronBuilder addField(Object f, String e) { return this; }
    }
    """
P6_OURS = """\
    package com.cronutils.builder;

    import static com.cronutils.model.field.CronFieldName.*;
    import static com.cronutils.utils.Preconditions.checkState;

    public class CronBuilder {
        public CronBuilder withDoW(String expression) {
            return addField(DAY_OF_WEEK, expression);
        }

        public CronBuilder withDoY(String expression) {
            return addField(DAY_OF_YEAR, expression);
        }

        private CronBuilder addField(Object f, String e) { return this; }
    }
    """
P6_THEIRS = """\
    package com.cronutils.builder;

    import static com.cronutils.model.field.CronFieldName.DAY_OF_WEEK;
    import static com.cronutils.utils.Preconditions.checkState;

    public class CronBuilder {
        public CronBuilder withDoW(String expression) {
            return addField(DAY_OF_WEEK, expression);
        }

        private CronBuilder addField(Object f, String e) { return this; }
    }
    """
P6_MERGED = """\
    package com.cronutils.builder;

    import static com.cronutils.model.field.CronFieldName.DAY_OF_WEEK;
    import static com.cronutils.utils.Preconditions.checkState;

    public class CronBuilder {
        public CronBuilder withDoW(String expression) {
            return addField(DAY_OF_WEEK, expression);
        }

        public CronBuilder withDoY(String expression) {
            return addField(DAY_OF_YEAR, expression);
        }

        private CronBuilder addField(Object f, String e) { return this; }
    }
    """


def test_p6_static_wildcard_narrowed_constant(strategy, tmp_path):
    result = run(strategy, tmp_path, P6_MERGED, P6_BASE, P6_OURS, P6_THEIRS)
    assert_flags(result, "DAY_OF_YEAR")
    # DAY_OF_WEEK survives via the explicit static import
    assert not any("'DAY_OF_WEEK'" in i.message for i in result.issues)


# P7 — STATIC wildcard narrowed, lowercase call-form usage, class EXTENDS
# (dius_java-faker shape: ours narrowed org.hamcrest.Matchers.* and renamed
# its own usages; theirs' new test still calls isEmptyOrNullString(); the
# test class extends a base class — inheritance must not suppress).
P7_BASE = """\
    package com.github.javafaker;

    import static org.hamcrest.MatcherAssert.assertThat;
    import static org.hamcrest.Matchers.*;

    public class AddressTest extends AbstractFakerTest {
        public void testFullAddress() {
            assertThat(faker().address(), not(isEmptyOrNullString()));
        }

        private Faker faker() { return null; }
    }
    """
P7_OURS = """\
    package com.github.javafaker;

    import static org.hamcrest.MatcherAssert.assertThat;
    import static org.hamcrest.Matchers.emptyOrNullString;
    import static org.hamcrest.Matchers.not;

    public class AddressTest extends AbstractFakerTest {
        public void testFullAddress() {
            assertThat(faker().address(), not(emptyOrNullString()));
        }

        private Faker faker() { return null; }
    }
    """
P7_THEIRS = """\
    package com.github.javafaker;

    import static org.hamcrest.MatcherAssert.assertThat;
    import static org.hamcrest.Matchers.*;

    public class AddressTest extends AbstractFakerTest {
        public void testFullAddress() {
            assertThat(faker().address(), not(isEmptyOrNullString()));
        }

        public void testCounty() {
            assertThat(faker().address(), not(isEmptyOrNullString()));
        }

        private Faker faker() { return null; }
    }
    """
P7_MERGED = """\
    package com.github.javafaker;

    import static org.hamcrest.MatcherAssert.assertThat;
    import static org.hamcrest.Matchers.emptyOrNullString;
    import static org.hamcrest.Matchers.not;

    public class AddressTest extends AbstractFakerTest {
        public void testFullAddress() {
            assertThat(faker().address(), not(emptyOrNullString()));
        }

        public void testCounty() {
            assertThat(faker().address(), not(isEmptyOrNullString()));
        }

        private Faker faker() { return null; }
    }
    """


def test_p7_static_wildcard_narrowed_call_form_with_extends(strategy, tmp_path):
    result = run(strategy, tmp_path, P7_MERGED, P7_BASE, P7_OURS, P7_THEIRS)
    assert_flags(result, "isEmptyOrNullString")
    # covered names must stay silent
    for ok in ("assertThat", "not", "emptyOrNullString"):
        assert not any(f"'{ok}'" in i.message for i in result.issues)


# P8 — usage KEPT FROM BASE: theirs removes import + its usages, ours edits
# nearby code so the structural merge keeps the base usage while the import
# deletion applies (movsim/segmentio shape).
P8_BASE = """\
    package org.movsim;

    import org.movsim.xml.MovsimInputLoader;

    public class SimulationScan {
        public void scan() {
            Object inputData = MovsimInputLoader.getInputData("f");
            System.out.println(inputData);
        }
    }
    """
P8_OURS = """\
    package org.movsim;

    import org.movsim.xml.MovsimInputLoader;

    public class SimulationScan {
        public void scan() {
            Object inputData = MovsimInputLoader.getInputData("f");
            System.out.println("scanning");
            System.out.println(inputData);
        }
    }
    """
P8_THEIRS = """\
    package org.movsim;

    public class SimulationScan {
        public void scan() {
            Object inputData = loadDirect("f");
            System.out.println(inputData);
        }

        private Object loadDirect(String f) { return null; }
    }
    """
P8_MERGED = """\
    package org.movsim;

    public class SimulationScan {
        public void scan() {
            Object inputData = MovsimInputLoader.getInputData("f");
            System.out.println("scanning");
            System.out.println(inputData);
        }

        private Object loadDirect(String f) { return null; }
    }
    """


def test_p8_usage_kept_from_base_import_pruned(strategy, tmp_path):
    result = run(strategy, tmp_path, P8_MERGED, P8_BASE, P8_OURS, P8_THEIRS)
    assert_flags(result, "MovsimInputLoader")


# P9 — two symmetric prunes in one file, both flagged
# (sander2798_enderstone shape).
P9_BASE = """\
    package org.enderstone.server.entity;

    import org.enderstone.server.regions.RegionSet;
    import org.enderstone.server.packet.PacketOutPlayerAbilities;

    public class EnderPlayer {
        public void existing(RegionSet r, PacketOutPlayerAbilities p) {
        }
    }
    """
P9_OURS = """\
    package org.enderstone.server.entity;

    import org.enderstone.server.regions.RegionSet;

    public class EnderPlayer {
        public void existing(RegionSet r) {
        }

        private final RegionSet loadedChunks = new RegionSet();
    }
    """
P9_THEIRS = """\
    package org.enderstone.server.entity;

    import org.enderstone.server.packet.PacketOutPlayerAbilities;

    public class EnderPlayer {
        public void existing(PacketOutPlayerAbilities p) {
        }

        public void sendAbilities() {
            broadcast(new PacketOutPlayerAbilities());
        }

        private void broadcast(Object packet) {}
    }
    """
P9_MERGED = """\
    package org.enderstone.server.entity;

    public class EnderPlayer {
        public void existing() {
        }

        private final RegionSet loadedChunks = new RegionSet();

        public void sendAbilities() {
            broadcast(new PacketOutPlayerAbilities());
        }

        private void broadcast(Object packet) {}
    }
    """


def test_p9_two_symmetric_prunes_both_flagged(strategy, tmp_path):
    result = run(strategy, tmp_path, P9_MERGED, P9_BASE, P9_OURS, P9_THEIRS)
    assert_flags(result, "RegionSet")
    assert_flags(result, "PacketOutPlayerAbilities")


# P10 — pruned exception import used in a multi-item `throws` clause
# (post-review fix: `throws`/`implements`/`extends`/`permits` operands are
# usage positions, not declarations of the type).
P10_BASE = """\
    package p;

    import com.foo.FooEx;

    public class C {
        public void old() throws FooEx, RuntimeException {}
    }
    """
P10_OURS = """\
    package p;

    public class C {
        public void old() {}
    }
    """
P10_THEIRS = """\
    package p;

    import com.foo.FooEx;

    public class C {
        public void old() throws FooEx, RuntimeException {}

        public void added() throws FooEx, RuntimeException {}
    }
    """
P10_MERGED = """\
    package p;

    public class C {
        public void old() {}

        public void added() throws FooEx, RuntimeException {}
    }
    """


def test_p10_throws_clause_usage_flags(strategy, tmp_path):
    result = run(strategy, tmp_path, P10_MERGED, P10_BASE, P10_OURS, P10_THEIRS)
    assert_flags(result, "FooEx")


def test_p11_implements_clause_usage_flags(strategy, tmp_path):
    base = """\
        package p;

        import com.foo.FooIntf;

        public class C {
            public void f(FooIntf x) {}
        }
        """
    ours = """\
        package p;

        public class C {
            public void f() {}
        }
        """
    theirs = """\
        package p;

        import com.foo.FooIntf;

        public class C {
            public void f(FooIntf x) {}

            static class Impl implements FooIntf, Cloneable {}
        }
        """
    merged = """\
        package p;

        public class C {
            public void f() {}

            static class Impl implements FooIntf, Cloneable {}
        }
        """
    result = run(strategy, tmp_path, merged, base, ours, theirs)
    assert_flags(result, "FooIntf")


# =========================================================================== #
# Cross-category negatives (must NOT fire)
# =========================================================================== #

def test_neg_signature_change_shape_silent(strategy, tmp_path):
    # D2 shape: ours adds a param; theirs adds an old-arity call. No import
    # was touched — the D1 lane must stay silent.
    base = """\
        package p;

        public class ItemStacks {
            public ItemStacks(short a, byte b) {}

            public void use() { helper(new ItemStacks((short) 1, (byte) 2)); }

            private void helper(ItemStacks s) {}
        }
        """
    ours = """\
        package p;

        public class ItemStacks {
            public ItemStacks(short a, byte b, boolean generateNBT) {}

            public void use() { helper(new ItemStacks((short) 1, (byte) 2, true)); }

            private void helper(ItemStacks s) {}
        }
        """
    theirs = """\
        package p;

        public class ItemStacks {
            public ItemStacks(short a, byte b) {}

            public void use() { helper(new ItemStacks((short) 1, (byte) 2)); }

            public void onSpawn() { helper(new ItemStacks((short) 3, (byte) 4)); }

            private void helper(ItemStacks s) {}
        }
        """
    merged = """\
        package p;

        public class ItemStacks {
            public ItemStacks(short a, byte b, boolean generateNBT) {}

            public void use() { helper(new ItemStacks((short) 1, (byte) 2, true)); }

            public void onSpawn() { helper(new ItemStacks((short) 3, (byte) 4)); }

            private void helper(ItemStacks s) {}
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_neg_rename_shape_silent(strategy, tmp_path):
    # D3/erudika shape: ours renamed a local, theirs added a stale reference.
    # No import involved — belongs to the rename lanes, not this one.
    base = """\
        package p;

        public class Aspect {
            public void invoke(int mi) {
                int m = mi;
                helper(m);
            }
            private void helper(int x) {}
        }
        """
    ours = """\
        package p;

        public class Aspect {
            public void invoke(int mi) {
                int method = mi;
                helper(method);
            }
            private void helper(int x) {}
        }
        """
    theirs = """\
        package p;

        public class Aspect {
            public void invoke(int mi) {
                int m = mi;
                helper(m);
                helper(m);
            }
            private void helper(int x) {}
        }
        """
    merged = """\
        package p;

        public class Aspect {
            public void invoke(int mi) {
                int method = mi;
                helper(m);
                helper(method);
            }
            private void helper(int x) {}
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_neg_clean_dead_import_refactor_silent(strategy, tmp_path):
    # Clean refactor: ours removes an import TOGETHER with all its usages;
    # theirs adds unrelated code. Merged has no usage of the pruned name.
    base = """\
        package p;

        import java.util.LinkedList;

        public class Holder {
            public void fill() {
                LinkedList<String> l = new LinkedList<>();
                l.add("x");
            }
        }
        """
    ours = """\
        package p;

        public class Holder {
            public void fill() {
            }
        }
        """
    theirs = """\
        package p;

        import java.util.LinkedList;

        public class Holder {
            public void fill() {
                LinkedList<String> l = new LinkedList<>();
                l.add("x");
            }

            public int count() { return 0; }
        }
        """
    merged = """\
        package p;

        public class Holder {
            public void fill() {
            }

            public int count() { return 0; }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


# =========================================================================== #
# Guard negatives (plan §2)
# =========================================================================== #

def test_guard_surviving_wildcard_covers(strategy, tmp_path):
    # Ours prunes `import java.util.List;` but `java.util.*` survives in the
    # merged file — the usage still resolves; silent.
    base = """\
        package p;

        import java.util.List;
        import java.util.*;

        public class W {
            public void f() {}
        }
        """
    ours = """\
        package p;

        import java.util.*;

        public class W {
            public void f() {}
        }
        """
    theirs = """\
        package p;

        import java.util.List;
        import java.util.*;

        public class W {
            public void f() {}

            public List<String> names() { return null; }
        }
        """
    merged = """\
        package p;

        import java.util.*;

        public class W {
            public void f() {}

            public List<String> names() { return null; }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_java_lang_import_pruned(strategy, tmp_path):
    # Pruning a redundant `import java.lang.String;` is harmless.
    base = """\
        package p;

        import java.lang.String;

        public class J {
            public void f() {}
        }
        """
    ours = """\
        package p;

        public class J {
            public void f() {}
        }
        """
    theirs = """\
        package p;

        import java.lang.String;

        public class J {
            public void f() {}

            public String greet() { return "hi"; }
        }
        """
    merged = """\
        package p;

        public class J {
            public void f() {}

            public String greet() { return "hi"; }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_fqn_usage_not_stale(strategy, tmp_path):
    # Theirs' new code uses the fully qualified name — no import needed.
    base = """\
        package p;

        import com.foo.Bar;

        public class F {
            public void f(Bar b) {}
        }
        """
    ours = """\
        package p;

        public class F {
            public void f() {}
        }
        """
    theirs = """\
        package p;

        import com.foo.Bar;

        public class F {
            public void f(Bar b) {}

            public void g() {
                com.foo.Bar x = new com.foo.Bar();
                x.toString();
            }
        }
        """
    merged = """\
        package p;

        public class F {
            public void f() {}

            public void g() {
                com.foo.Bar x = new com.foo.Bar();
                x.toString();
            }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_local_shadowing_type_declared(strategy, tmp_path):
    # Theirs adds a NESTED class Task and uses it; ours pruned an unrelated
    # com.foo.Task import — the local declaration resolves the usage; silent.
    base = """\
        package p;

        import com.foo.Task;

        public class S {
            public void f(Task t) {}
        }
        """
    ours = """\
        package p;

        public class S {
            public void f() {}
        }
        """
    theirs = """\
        package p;

        import com.foo.Task;

        public class S {
            public void f(Task t) {}

            static class Task {}

            public Task make() { return new Task(); }
        }
        """
    merged = """\
        package p;

        public class S {
            public void f() {}

            static class Task {}

            public Task make() { return new Task(); }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_same_package_import_pruned(strategy, tmp_path):
    # jumblr shape: `import com.tumblr.jumblr.request.MultipartConverter;`
    # inside package com.tumblr.jumblr.request is redundant; pruning it is
    # harmless even though usages remain everywhere.
    base = """\
        package com.tumblr.jumblr.request;

        import com.tumblr.jumblr.request.MultipartConverter;

        public class RequestBuilder {
            public Object convert() { return new MultipartConverter().go(); }
        }
        """
    ours = """\
        package com.tumblr.jumblr.request;

        public class RequestBuilder {
            public Object convert() { return new MultipartConverter().go(); }
        }
        """
    theirs = """\
        package com.tumblr.jumblr.request;

        import com.tumblr.jumblr.request.MultipartConverter;

        public class RequestBuilder {
            public Object convert() { return new MultipartConverter().go(); }

            public Object convertTwice() { return new MultipartConverter().go(); }
        }
        """
    merged = """\
        package com.tumblr.jumblr.request;

        public class RequestBuilder {
            public Object convert() { return new MultipartConverter().go(); }

            public Object convertTwice() { return new MultipartConverter().go(); }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_absorption_pruner_keeps_usages_documented_fn(strategy, tmp_path):
    # assertj shape — DOCUMENTED FN by design: the pruning side removed the
    # static import while KEEPING its own usages. File-locally this is
    # indistinguishable from a deliberate re-bind to an import-free name
    # (same-package/inherited), so the absorption guard (§2 "usage resolves
    # in each parent") suppresses. The zero-FP bar wins over this recall.
    base = """\
        package org.assertj.core.api;

        import static org.assertj.core.test.TestFailures.failBecauseExpectedAssertionErrorWasNotThrown;

        public class IterableAssertTest {
            public void t1() {
                failBecauseExpectedAssertionErrorWasNotThrown();
            }
        }
        """
    ours = """\
        package org.assertj.core.api;

        public class IterableAssertTest {
            public void t1() {
                failBecauseExpectedAssertionErrorWasNotThrown();
            }
        }
        """
    theirs = """\
        package org.assertj.core.api;

        import static org.assertj.core.test.TestFailures.failBecauseExpectedAssertionErrorWasNotThrown;

        public class IterableAssertTest {
            public void t1() {
                failBecauseExpectedAssertionErrorWasNotThrown();
            }

            public void t2() {
                failBecauseExpectedAssertionErrorWasNotThrown();
            }
        }
        """
    merged = """\
        package org.assertj.core.api;

        public class IterableAssertTest {
            public void t1() {
                failBecauseExpectedAssertionErrorWasNotThrown();
            }

            public void t2() {
                failBecauseExpectedAssertionErrorWasNotThrown();
            }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_same_package_collision_still_flags(strategy, tmp_path):
    # ninja shape (spec note): a same-package type with the pruned simple
    # name exists elsewhere in the package, so the merged file may even
    # compile — but the usage silently re-binds. The import was FOREIGN
    # (javax.servlet.http.Cookie) and the pruning side dropped its usages,
    # so the absorption guard does not suppress: this MUST flag.
    base = """\
        package ninja;

        import javax.servlet.http.Cookie;

        public class ContextImpl {
            public void existing(Cookie c) {}
        }
        """
    ours = """\
        package ninja;

        public class ContextImpl {
            public void existing() {}
        }
        """
    theirs = """\
        package ninja;

        import javax.servlet.http.Cookie;

        public class ContextImpl {
            public void existing(Cookie c) {}

            public void unset(Object resp, String name) {
                addCookie(new Cookie(name, null));
            }

            private void addCookie(Object c) {}
        }
        """
    merged = """\
        package ninja;

        public class ContextImpl {
            public void existing() {}

            public void unset(Object resp, String name) {
                addCookie(new Cookie(name, null));
            }

            private void addCookie(Object c) {}
        }
        """
    result = run(strategy, tmp_path, merged, base, ours, theirs)
    assert_flags(result, "Cookie")


def test_guard_jdk_wildcard_not_credited_with_project_types(strategy, tmp_path):
    # dynjs tune-control FP shape (GD2(iii) tuning fix): theirs narrowed
    # `java.util.*` to explicit imports; ours added usages of a SAME-PACKAGE
    # project type (no import needed). The lost JDK wildcard must not be
    # credited with providing a name outside the embedded java.util set.
    base = """\
        package org.dynjs.runtime;

        import java.util.*;

        public class ExecutionContext {
            public void f() {
                List<String> l = new ArrayList<>();
                l.add("x");
            }
        }
        """
    ours = """\
        package org.dynjs.runtime;

        import java.util.*;

        public class ExecutionContext {
            public void f() {
                List<String> l = new ArrayList<>();
                l.add("x");
            }

            public Object getVars(VariableValues vals) {
                return VariableValues.wrap(vals);
            }
        }
        """
    theirs = """\
        package org.dynjs.runtime;

        import java.util.ArrayList;
        import java.util.List;

        public class ExecutionContext {
            public void f() {
                List<String> l = new ArrayList<>();
                l.add("x");
            }
        }
        """
    merged = """\
        package org.dynjs.runtime;

        import java.util.ArrayList;
        import java.util.List;

        public class ExecutionContext {
            public void f() {
                List<String> l = new ArrayList<>();
                l.add("x");
            }

            public Object getVars(VariableValues vals) {
                return VariableValues.wrap(vals);
            }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_jdk_wildcard_narrowed_genuine_jdk_type_still_flags(strategy, tmp_path):
    # Counterpart to the dynjs guard: a name that IS in the embedded
    # java.util set, used only by the non-narrowing side, must still flag.
    base = """\
        package p;

        import java.util.*;

        public class Q {
            public void f() {
                List<String> l = new ArrayList<>();
                l.add("x");
            }
        }
        """
    ours = """\
        package p;

        import java.util.ArrayList;
        import java.util.List;

        public class Q {
            public void f() {
                List<String> l = new ArrayList<>();
                l.add("x");
            }
        }
        """
    theirs = """\
        package p;

        import java.util.*;

        public class Q {
            public void f() {
                List<String> l = new ArrayList<>();
                l.add("x");
            }

            public LinkedList<String> pending() {
                return new LinkedList<>();
            }
        }
        """
    merged = """\
        package p;

        import java.util.ArrayList;
        import java.util.List;

        public class Q {
            public void f() {
                List<String> l = new ArrayList<>();
                l.add("x");
            }

            public LinkedList<String> pending() {
                return new LinkedList<>();
            }
        }
        """
    result = run(strategy, tmp_path, merged, base, ours, theirs)
    assert_flags(result, "LinkedList")
    assert not any("'ArrayList'" in i.message for i in result.issues)
    assert not any("'List'" in i.message for i in result.issues)


def test_guard_case_label_not_usage(strategy, tmp_path):
    # Bare enum constants in `case` labels resolve against the switch type
    # without any import — must not count as stale usage.
    base = """\
        package p;

        import static p.Modes.*;

        public class C {
            public int f(Modes m) {
                if (m == ACTIVE) { return 1; }
                return 0;
            }
        }
        """
    ours = """\
        package p;

        import static p.Modes.ACTIVE;

        public class C {
            public int f(Modes m) {
                if (m == ACTIVE) { return 1; }
                return 0;
            }
        }
        """
    theirs = """\
        package p;

        import static p.Modes.*;

        public class C {
            public int f(Modes m) {
                if (m == ACTIVE) { return 1; }
                switch (m) {
                    case STANDBY_MODE:
                        return 2;
                    default:
                        return 0;
                }
            }
        }
        """
    merged = """\
        package p;

        import static p.Modes.ACTIVE;

        public class C {
            public int f(Modes m) {
                if (m == ACTIVE) { return 1; }
                switch (m) {
                    case STANDBY_MODE:
                        return 2;
                    default:
                        return 0;
                }
            }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_comments_and_strings_not_usage(strategy, tmp_path):
    # The pruned name appearing only in javadoc/strings is not a usage.
    base = """\
        package p;

        import com.foo.Widget;

        public class D {
            public void f(Widget w) {}
        }
        """
    ours = """\
        package p;

        public class D {
            public void f() {}
        }
        """
    theirs = """\
        package p;

        import com.foo.Widget;

        public class D {
            public void f(Widget w) {}

            /** Uses a Widget internally. */
            public String describe() {
                return "Widget factory: new Widget()";
            }
        }
        """
    merged = """\
        package p;

        public class D {
            public void f() {}

            /** Uses a Widget internally. */
            public String describe() {
                return "Widget factory: new Widget()";
            }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_method_ref_qualified_not_usage(strategy, tmp_path):
    # `Assertions::fail` is qualified by the type — pruning the STATIC
    # import of fail does not affect it.
    base = """\
        package p;

        import org.junit.jupiter.api.Assertions;
        import static org.junit.jupiter.api.Assertions.fail;

        public class M {
            public void f() {}
        }
        """
    ours = """\
        package p;

        import org.junit.jupiter.api.Assertions;

        public class M {
            public void f() {}
        }
        """
    theirs = """\
        package p;

        import org.junit.jupiter.api.Assertions;
        import static org.junit.jupiter.api.Assertions.fail;

        public class M {
            public void f() {}

            public Runnable g() {
                return Assertions::fail;
            }
        }
        """
    merged = """\
        package p;

        import org.junit.jupiter.api.Assertions;

        public class M {
            public void f() {}

            public Runnable g() {
                return Assertions::fail;
            }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_guard_enum_constant_declared_in_file(strategy, tmp_path):
    # Post-review fix: enum constants match no declaration regex (`{ FOO,`
    # has no preceding type word), so a dedicated constant-list parse must
    # suppress them. Constants with args and class bodies exercise the
    # depth-tracking; DAY_MODE is used bare inside the enum while a static
    # wildcard was narrowed away — must stay silent.
    base = """\
        package p;

        import static p.Legacy.*;

        public class C {
            public int f() { return legacyCall(); }
        }
        """
    ours = """\
        package p;

        import static p.Legacy.legacyCall;

        public class C {
            public int f() { return legacyCall(); }
        }
        """
    theirs = """\
        package p;

        import static p.Legacy.*;

        public class C {
            public int f() { return legacyCall(); }

            enum Mode {
                @Deprecated
                DAY_MODE(1) { void x() {} },
                NIGHT_MODE;

                Mode(int v) {}
                Mode() {}

                int pick() { return use(DAY_MODE); }
                int use(Mode m) { return 0; }
            }
        }
        """
    merged = """\
        package p;

        import static p.Legacy.legacyCall;

        public class C {
            public int f() { return legacyCall(); }

            enum Mode {
                @Deprecated
                DAY_MODE(1) { void x() {} },
                NIGHT_MODE;

                Mode(int v) {}
                Mode() {}

                int pick() { return use(DAY_MODE); }
                int use(Mode m) { return 0; }
            }
        }
        """
    assert run(strategy, tmp_path, merged, base, ours, theirs).is_clean


def test_invariant_merged_equals_parent_never_flags(strategy, tmp_path):
    # Core soundness invariant, independent of any fixture shape: if the
    # merged text is byte-identical to a parent, nothing merge-induced
    # exists and the lane must stay silent. Exercised on the flag-adjacent
    # P1 material (both parents) and on the absorption-path material.
    for merged_as in ("ours", "theirs"):
        for b, o, t in ((P1_BASE, P1_OURS, P1_THEIRS),
                        (P3_BASE, P3_OURS, P3_THEIRS),
                        (P6_BASE, P6_OURS, P6_THEIRS)):
            m = o if merged_as == "ours" else t
            result = run(strategy, tmp_path, m, b, o, t)
            assert result.is_clean, (
                f"flagged although merged == {merged_as}: "
                f"{[i.message for i in result.issues]}")


def test_comment_banner_is_not_a_conflict_marker(strategy, tmp_path):
    # A block-comment separator that textually matches a marker line must
    # not abstain the file (marker check runs on stripped text); the real
    # P1 defect must still flag.
    banner = "/*\n=======\n*/\n"
    result = run(strategy, tmp_path, banner + P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert_flags(result, "Group")


# =========================================================================== #
# Gating and abstentions
# =========================================================================== #

def test_flag_off_returns_clean(monkeypatch, tmp_path):
    monkeypatch.delenv(FLAG, raising=False)
    strategy = ImportPruneUsageStrategy()
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS)
    assert result.is_clean


def test_flag_off_never_reads_file(monkeypatch):
    # With the flag unset the lane must return before touching anything —
    # even a nonexistent path must not raise.
    monkeypatch.delenv(FLAG, raising=False)
    strategy = ImportPruneUsageStrategy()
    result = strategy.analyze("/nonexistent/Nope.java",
                              base_content="x", ours_content="y", theirs_content="z")
    assert result.is_clean


def test_no_parents_abstains(strategy, tmp_path):
    p = tmp_path / "Merged.java"
    p.write_text(textwrap.dedent(P1_MERGED), encoding="utf-8")
    assert strategy.analyze(str(p)).is_clean
    assert strategy.analyze(str(p), base_content=textwrap.dedent(P1_BASE)).is_clean


def test_non_java_file_abstains(strategy, tmp_path):
    result = run(strategy, tmp_path, P1_MERGED, P1_BASE, P1_OURS, P1_THEIRS,
                 filename="merged.py")
    assert result.is_clean


def test_conflict_markers_abstain(strategy, tmp_path):
    conflicted = P1_MERGED + """\
    <<<<<<< ours
    class X {}
    =======
    class Y {}
    >>>>>>> theirs
    """
    result = run(strategy, tmp_path, conflicted, P1_BASE, P1_OURS, P1_THEIRS)
    assert result.is_clean


def test_loader_discovers_lane():
    loader = StrategyLoader(config_enabled_list=["ImportPruneUsage"])
    names = [s.name for s in loader.load_strategies()]
    assert names == ["ImportPruneUsage"]
