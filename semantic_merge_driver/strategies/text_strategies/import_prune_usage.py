import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from core.interfaces import MergeStrategy, AnalysisResult, Issue

# Detector-cycle D1 (ISSUES #31, outputs/detector-cycle-plan.md §2) —
# category `stale-usage-of-pruned-import` (12.7% of the #30 census).
#
# EXPERIMENTAL: gated by SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1 (plan §2 N2).
# With the flag unset, analyze() returns clean before doing any work, so the
# lane cannot affect driver verdicts until the cycle validates it.
#
# Shape (differential 3-way, merge-induced only): one side prunes an import
# (removes it, replaces it under a different simple name, or narrows a
# wildcard to an explicit list); the other side adds — or keeps from base —
# code using the pruned simple name. The structural merge combines the prune
# with the usage: the merged file references a name whose import is gone.
#
# Detection is TEXTUAL, not type resolution. Stage B built and dropped a
# Joern type-inference lane for exactly this breakage (javasrc2cpg gives up
# nondeterministically on single files — see unresolved_reference.py); this
# lane instead keys everything off the import DECLARATIONS, which are exact
# text, and uses the parents differentially:
#
#   lost = imports(ours) ∪ imports(theirs) − imports(merged)
#   flag symbol S iff:  a lost import provided S
#                    ∧  merged uses S unqualified          (outside comments,
#                       strings, import/package statements, `.`/`::`/case-
#                       label positions)
#                    ∧  merged does not cover S            (no explicit import
#                       of S, no surviving wildcard of the matching kind)
#                    ∧  no local declaration of S in merged (shadowing guard)
#                    ∧  every parent that lacks the lost import either does
#                       not use S or covers it otherwise   (absorption guard —
#                       plan §2's "usage resolves in each parent": a parent
#                       using S WITHOUT the import proves S resolves import-
#                       free (same-package type, inherited member), or that
#                       parent was already broken — either way not merge-
#                       induced)
#
# Guards from plan §2 + the S-D1 specs (reports_detectors/specs/specs.csv):
#   * wildcard imports — a surviving wildcard of the matching kind (type
#     wildcard for type names, static wildcard for members; static wildcards
#     also cover nested types) suppresses: it may still provide S.
#     A LOST wildcard conversely yields candidates (narrowing sub-shape,
#     4/21 spec units) under stricter usage-shape requirements below.
#   * java.lang — pruning `import java.lang.X;` / `java.lang.*` is harmless
#     (redundant import); bare java.lang names are never candidates. Static
#     imports FROM java.lang classes (e.g. Math.max) stay flaggable.
#   * same-package — pruning a type import from the file's own package is
#     harmless (jumblr spec note); such lost imports yield no candidates.
#     NOTE: the inverse case — a pruned FOREIGN import whose simple name
#     collides with a same-package type — IS flagged (ninja spec note: the
#     usage silently re-binds; the absorption guard keeps this precise).
#   * FQN usage — occurrences preceded by `.` (qualified) or `::` (method
#     refs are always qualified) never count as stale usage.
#   * local shadowing — a type/method/variable/enum-constant declaration of
#     S in the merged file suppresses (overbroad on purpose: errs FN);
#     `throws`/`implements`/`extends`/`permits` clause operands are USAGE
#     positions and are exempt from the declaration heuristic.
#   * switch-case labels — `case S:` resolves against the switch type
#     without an import; such occurrences never count.
#
# Narrowing (wildcard-lost) candidates cannot be enumerated from the import
# text, so they are mined from merged identifiers with extra conservatism:
#   type kind:   CamelCase, len ≥ 3 (excludes generic type params T/E/K/ID);
#                for lost `java.*` wildcards only names in the embedded JDK
#                sets (_JDK_WILDCARD_TYPES) qualify — membership of JDK
#                packages is knowable, so project-local names are never
#                credited to them (dynjs tune-control FP, GD2(iii) fix);
#   member kind: call-form occurrence `S(...)` for lowercase names, or
#                ALL_CAPS constant form (with `_` or len ≥ 4) for constants.
#
# KNOWN FN (documented, tested): a side that prunes an import while KEEPING
# its own usages of the name (assertj derivation unit) is suppressed by the
# absorption guard — file-locally indistinguishable from a deliberate
# re-bind to a same-package type, and the plan's zero-FP bar wins. Also FN:
# member candidates covered by an unrelated surviving static wildcard, and
# ≤3-char / no-underscore-short constants excluded by the shape rules above.
#
# Abstentions (return clean, by design): non-.java files (import semantics
# are language-specific), missing parents (no differential evidence — the
# unresolved_reference.py convention), conflict markers in the merged text
# (a textual conflict is already surfaced; nothing here is silent).

_ENV_FLAG = "SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"

_IMPORT_RE = re.compile(
    r"\bimport\s+(static\s+)?([\w$]+(?:\s*\.\s*[\w$]+)*)\s*(\.\s*\*)?\s*;",
    re.S,
)
_PACKAGE_RE = re.compile(r"\bpackage\s+([\w$]+(?:\s*\.\s*[\w$]+)*)\s*;", re.S)
_IDENT_RE = re.compile(r"[A-Za-z_$][\w$]*")

_KEYWORDS = frozenset(
    """abstract assert boolean break byte case catch char class const continue
    default do double else enum extends final finally float for goto if
    implements import instanceof int interface long native new package private
    protected public return short static strictfp super switch synchronized
    this throw throws transient try void volatile while var record yield
    sealed permits non true false null""".split()
)

# Words after which `S <,;(=…>` is a USAGE position, not a declaration of S:
# expression keywords (`new S(`, `return S;`) and clause keywords whose
# operands are type references (`throws S, T;`, `implements S,`,
# `extends S,`, `permits S,`).
_EXPR_KEYWORDS = frozenset(
    """new return throw throws case else assert yield do while if for switch
    synchronized instanceof extends implements permits""".split()
)

# java.lang public types (SE 17) — resolvable with no import at all.
_JAVA_LANG = frozenset(
    """Appendable AutoCloseable Boolean Byte CharSequence Character Class
    ClassLoader ClassValue Cloneable Comparable Compiler Double Enum Error
    Exception Float FunctionalInterface Integer Iterable Long Math Module
    ModuleLayer Number Object Package Process ProcessBuilder ProcessHandle
    Readable Record Runnable Runtime RuntimeException SafeVarargs Short
    StackTraceElement StackWalker StrictMath String StringBuffer
    StringBuilder System Thread ThreadGroup ThreadLocal Throwable Void
    Deprecated Override SuppressWarnings ArithmeticException
    ArrayIndexOutOfBoundsException ArrayStoreException ClassCastException
    ClassNotFoundException CloneNotSupportedException
    EnumConstantNotPresentException IllegalAccessException
    IllegalArgumentException IllegalCallerException
    IllegalMonitorStateException IllegalStateException
    IllegalThreadStateException IndexOutOfBoundsException
    InstantiationException InterruptedException LayerInstantiationException
    NegativeArraySizeException NoSuchFieldException NoSuchMethodException
    NullPointerException NumberFormatException ReflectiveOperationException
    SecurityException StringIndexOutOfBoundsException
    TypeNotPresentException UnsupportedOperationException AbstractMethodError
    AssertionError BootstrapMethodError ClassCircularityError
    ClassFormatError ExceptionInInitializerError IllegalAccessError
    IncompatibleClassChangeError InstantiationError InternalError
    LinkageError NoClassDefFoundError NoSuchFieldError NoSuchMethodError
    OutOfMemoryError StackOverflowError ThreadDeath UnknownError
    UnsatisfiedLinkError UnsupportedClassVersionError VerifyError
    VirtualMachineError""".split()
)

_CONFLICT_MARKER_RE = re.compile(r"^(<{7}|={7}|>{7})( |$)", re.M)

# Public top-level types of the commonly-wildcarded JDK packages (SE 17).
# A lost `java.*` TYPE wildcard only yields candidates from these sets:
# JDK package membership is knowable and stable, so an uncovered CamelCase
# name OUTSIDE the set (e.g. a same-package project type the other side
# started using) must not be credited to the lost wildcard. A `java.*`
# package with no set here yields no candidates at all (FN-only). Non-JDK
# wildcards keep conservative mining — their membership is unknowable.
# (GD2(iii) tuning fix, 2026-07-16: dynjs tune-control FP — same-package
# `VariableValues` wrongly credited to a narrowed `java.util.*`.)
_JDK_WILDCARD_TYPES = {
    "java.util": frozenset(
        """AbstractCollection AbstractList AbstractMap AbstractQueue
        AbstractSequentialList AbstractSet ArrayDeque ArrayList Arrays Base64
        BitSet Calendar Collection Collections Comparator
        ConcurrentModificationException Currency Date Deque Dictionary
        DoubleSummaryStatistics EmptyStackException EnumMap EnumSet
        Enumeration EventListener EventObject Formattable Formatter
        GregorianCalendar HashMap HashSet Hashtable HexFormat IdentityHashMap
        InputMismatchException IntSummaryStatistics Iterator LinkedHashMap
        LinkedHashSet LinkedList List ListIterator ListResourceBundle Locale
        LongSummaryStatistics MissingResourceException NavigableMap
        NavigableSet NoSuchElementException Objects Observable Observer
        Optional OptionalDouble OptionalInt OptionalLong PrimitiveIterator
        PriorityQueue Properties PropertyResourceBundle Queue Random
        RandomAccess ResourceBundle Scanner ServiceConfigurationError
        ServiceLoader Set SimpleTimeZone SortedMap SortedSet Spliterator
        Spliterators SplittableRandom Stack StringJoiner StringTokenizer
        TimeZone Timer TimerTask TreeMap TreeSet UUID Vector
        WeakHashMap""".split()),
    "java.io": frozenset(
        """BufferedInputStream BufferedOutputStream BufferedReader
        BufferedWriter ByteArrayInputStream ByteArrayOutputStream
        CharArrayReader CharArrayWriter Closeable Console DataInput
        DataInputStream DataOutput DataOutputStream EOFException
        Externalizable File FileDescriptor FileFilter FileInputStream
        FileNotFoundException FileOutputStream FilePermission FileReader
        FileWriter FilenameFilter FilterInputStream FilterOutputStream
        FilterReader FilterWriter Flushable IOError IOException InputStream
        InputStreamReader InterruptedIOException LineNumberReader
        NotSerializableException ObjectInput ObjectInputStream ObjectOutput
        ObjectOutputStream ObjectStreamClass ObjectStreamException
        ObjectStreamField OutputStream OutputStreamWriter PipedInputStream
        PipedOutputStream PipedReader PipedWriter PrintStream PrintWriter
        PushbackInputStream PushbackReader RandomAccessFile Reader
        SequenceInputStream Serializable StreamCorruptedException
        StreamTokenizer StringReader StringWriter UncheckedIOException
        UnsupportedEncodingException Writer""".split()),
    "java.util.concurrent": frozenset(
        """AbstractExecutorService ArrayBlockingQueue BlockingDeque
        BlockingQueue BrokenBarrierException Callable CancellationException
        CompletableFuture CompletionException CompletionService
        CompletionStage ConcurrentHashMap ConcurrentLinkedDeque
        ConcurrentLinkedQueue ConcurrentMap ConcurrentNavigableMap
        ConcurrentSkipListMap ConcurrentSkipListSet CopyOnWriteArrayList
        CopyOnWriteArraySet CountDownLatch CountedCompleter CyclicBarrier
        DelayQueue Delayed Exchanger ExecutionException Executor
        ExecutorCompletionService ExecutorService Executors Flow
        ForkJoinPool ForkJoinTask ForkJoinWorkerThread Future FutureTask
        LinkedBlockingDeque LinkedBlockingQueue LinkedTransferQueue Phaser
        PriorityBlockingQueue RecursiveAction RecursiveTask
        RejectedExecutionException RejectedExecutionHandler RunnableFuture
        RunnableScheduledFuture ScheduledExecutorService ScheduledFuture
        ScheduledThreadPoolExecutor Semaphore SynchronousQueue ThreadFactory
        ThreadLocalRandom ThreadPoolExecutor TimeUnit TimeoutException
        TransferQueue""".split()),
    "java.util.concurrent.atomic": frozenset(
        """AtomicBoolean AtomicInteger AtomicIntegerArray
        AtomicIntegerFieldUpdater AtomicLong AtomicLongArray
        AtomicLongFieldUpdater AtomicMarkableReference AtomicReference
        AtomicReferenceArray AtomicReferenceFieldUpdater
        AtomicStampedReference DoubleAccumulator DoubleAdder LongAccumulator
        LongAdder""".split()),
    "java.util.concurrent.locks": frozenset(
        """AbstractOwnableSynchronizer AbstractQueuedLongSynchronizer
        AbstractQueuedSynchronizer Condition Lock LockSupport ReadWriteLock
        ReentrantLock ReentrantReadWriteLock StampedLock""".split()),
    "java.util.function": frozenset(
        """BiConsumer BiFunction BiPredicate BinaryOperator BooleanSupplier
        Consumer DoubleBinaryOperator DoubleConsumer DoubleFunction
        DoublePredicate DoubleSupplier DoubleUnaryOperator Function
        IntBinaryOperator IntConsumer IntFunction IntPredicate IntSupplier
        IntUnaryOperator LongBinaryOperator LongConsumer LongFunction
        LongPredicate LongSupplier LongUnaryOperator ObjDoubleConsumer
        ObjIntConsumer ObjLongConsumer Predicate Supplier ToDoubleBiFunction
        ToDoubleFunction ToIntBiFunction ToIntFunction ToLongBiFunction
        ToLongFunction UnaryOperator""".split()),
    "java.util.stream": frozenset(
        """BaseStream Collector Collectors DoubleStream IntStream LongStream
        Stream StreamSupport""".split()),
    "java.util.regex": frozenset(
        """MatchResult Matcher Pattern PatternSyntaxException""".split()),
}


@dataclass(frozen=True)
class _Import:
    is_static: bool
    path: str           # dotted path without the trailing .*
    is_wildcard: bool
    span: Tuple[int, int]

    @property
    def key(self) -> Tuple[bool, str, bool]:
        return (self.is_static, self.path, self.is_wildcard)

    @property
    def simple(self) -> Optional[str]:
        return None if self.is_wildcard else self.path.rsplit(".", 1)[-1]

    @property
    def container(self) -> str:
        """Package (type imports) / enclosing class path (static explicit)."""
        return self.path if self.is_wildcard else self.path.rsplit(".", 1)[0]

    @property
    def statement(self) -> str:
        star = ".*" if self.is_wildcard else ""
        return f"import {'static ' if self.is_static else ''}{self.path}{star};"


@dataclass(frozen=True)
class _Occurrence:
    line: int           # 1-based
    call_form: bool     # identifier immediately (mod whitespace) before `(`


class _FileView:
    """Comment/string-stripped view of one Java file version."""

    def __init__(self, text: str):
        self.stripped = _strip_comments_and_strings(text)
        self._enum_consts: Optional[frozenset] = None
        self.imports: List[_Import] = []
        excluded: List[Tuple[int, int]] = []
        for m in _IMPORT_RE.finditer(self.stripped):
            path = re.sub(r"\s+", "", m.group(2))
            self.imports.append(_Import(
                is_static=bool(m.group(1)),
                path=path,
                is_wildcard=bool(m.group(3)),
                span=m.span(),
            ))
            excluded.append(m.span())
        pm = _PACKAGE_RE.search(self.stripped)
        self.package = re.sub(r"\s+", "", pm.group(1)) if pm else ""
        if pm:
            excluded.append(pm.span())
        self._excluded = sorted(excluded)
        self.import_keys = {im.key for im in self.imports}

    # -- coverage ---------------------------------------------------------- #
    def covers(self, symbol: str, kind: str) -> bool:
        """Can `symbol` (kind 'type'|'member') resolve via this file's imports?

        Conservative: any wildcard that COULD provide the symbol counts.
        Static wildcards can provide both members and nested types; type
        wildcards provide types only.
        """
        for im in self.imports:
            if im.is_wildcard:
                if im.is_static or kind == "type":
                    return True
            elif im.simple == symbol:
                if kind == "member" and not im.is_static:
                    continue  # `import a.b.C;` gives no unqualified member C
                return True
        return False

    # -- identifier occurrences -------------------------------------------- #
    def occurrences(self, symbol: str) -> List[_Occurrence]:
        out = []
        for m in re.finditer(rf"(?<![\w$]){re.escape(symbol)}(?![\w$])",
                             self.stripped):
            if self._in_excluded(m.start()):
                continue
            if self._qualified_or_case(m.start()):
                continue
            line = self.stripped.count("\n", 0, m.start()) + 1
            rest = self.stripped[m.end():m.end() + 40].lstrip()
            out.append(_Occurrence(line=line, call_form=rest.startswith("(")))
        return out

    def uses(self, symbol: str) -> bool:
        return bool(self.occurrences(symbol))

    def _in_excluded(self, pos: int) -> bool:
        return any(a <= pos < b for a, b in self._excluded)

    def _qualified_or_case(self, start: int) -> bool:
        """True for `.S` / `x . S` (qualified), `::S` (method ref), `case S` —
        including non-first multi-labels `case A, S` (legal since Java 14):
        the comma chain is walked back to its head, so a label list ends at
        `case` (excluded) while an argument list ends at `(` and stays a
        usage. (S-D4 review fix: the second label of `case FOO, MODE:` was
        counted as a usage by both this lane and the D3 widening.)"""
        i = start - 1
        s = self.stripped
        while True:
            while i >= 0 and s[i] in " \t\r\n":
                i -= 1
            if i < 0:
                return False
            if s[i] == ".":
                return True
            if s[i] == ":" and i >= 1 and s[i - 1] == ":":
                return True
            if s[i] == ",":
                i -= 1
                while i >= 0 and s[i] in " \t\r\n":
                    i -= 1
                if i < 0 or not (s[i].isalnum() or s[i] in "_$"):
                    return False
                while i >= 0 and (s[i].isalnum() or s[i] in "_$"):
                    i -= 1
                continue
            j = i
            while j >= 0 and (s[j].isalnum() or s[j] in "_$"):
                j -= 1
            return s[j + 1:i + 1] == "case"

    # -- shadowing / local declarations ------------------------------------ #
    def declares_type(self, symbol: str) -> bool:
        return bool(re.search(
            rf"(?:\b(?:class|interface|enum|record)|@\s*interface)\s+{re.escape(symbol)}\b",
            self.stripped))

    def declares_member(self, symbol: str) -> bool:
        """Method/field/variable/parameter/enum-constant `symbol` declared here.

        Overbroad by design (suppression errs toward FN): any
        `<word-or-generic-close> symbol <(=;,:)[>` where the preceding word
        is not an expression/clause keyword looks like a declaration; enum
        constants (which no such pattern catches) come from a dedicated
        constant-list parse.
        """
        if symbol in self.enum_constants:
            return True
        for m in re.finditer(
                rf"([\w$>\]])\s+{re.escape(symbol)}\s*[(=;,:)\[]",
                self.stripped):
            j = m.start(1)
            while j >= 0 and (self.stripped[j].isalnum() or self.stripped[j] in "_$"):
                j -= 1
            word = self.stripped[j + 1:m.start(1) + 1]
            if word not in _EXPR_KEYWORDS:
                return True
        return False

    @property
    def enum_constants(self) -> frozenset:
        if self._enum_consts is None:
            self._enum_consts = _enum_constants(self.stripped)
        return self._enum_consts


_ENUM_HEADER_RE = re.compile(r"\benum\s+[\w$]+")


def _enum_constants(stripped: str) -> frozenset:
    """Names declared as enum constants anywhere in the (stripped) file.

    For each `enum X ... {` header, walks the constant list at the top of
    the enum body: identifiers in constant position, separated by top-level
    commas, terminated by `;` or the body's closing `}`. Annotations,
    constructor argument lists, and constant class bodies are skipped via
    depth tracking. Enum constants match none of the declaration regexes
    (`{ FOO,` has no preceding type word), so without this parse a
    file-local constant could be mistaken for a stale usage.
    """
    out = set()
    n = len(stripped)
    for m in _ENUM_HEADER_RE.finditer(stripped):
        i = stripped.find("{", m.end())
        if i == -1:
            continue
        i += 1
        expect = True  # next identifier is a constant name
        while i < n:
            c = stripped[i]
            if c in " \t\r\n":
                i += 1
            elif c == "@" and expect:
                i += 1
                while i < n and (stripped[i].isalnum() or stripped[i] in "_$."):
                    i += 1
                while i < n and stripped[i] in " \t\r\n":
                    i += 1
                if i < n and stripped[i] == "(":
                    i = _skip_group(stripped, i, "(", ")")
            elif expect and (c.isalpha() or c in "_$"):
                j = i
                while j < n and (stripped[j].isalnum() or stripped[j] in "_$"):
                    j += 1
                out.add(stripped[i:j])
                i = j
                expect = False
            elif c == "(":
                i = _skip_group(stripped, i, "(", ")")
            elif c == "{":
                i = _skip_group(stripped, i, "{", "}")
            elif c == ",":
                expect = True
                i += 1
            else:
                break  # ';' ends the list; '}' ends the body; else malformed
    return frozenset(out)


def _skip_group(s: str, i: int, open_c: str, close_c: str) -> int:
    depth = 0
    n = len(s)
    while i < n:
        if s[i] == open_c:
            depth += 1
        elif s[i] == close_c:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def _strip_comments_and_strings(text: str) -> str:
    """Blank out comments, string/char literals, text blocks; keep newlines
    (and therefore line numbers) intact."""
    out = list(text)
    i, n = 0, len(text)

    def blank(a: int, b: int) -> None:
        for k in range(a, min(b, n)):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            j = text.find("\n", i)
            j = n if j == -1 else j
            blank(i, j)
            i = j
        elif c == "/" and nxt == "*":
            j = text.find("*/", i + 2)
            j = n if j == -1 else j + 2
            blank(i, j)
            i = j
        elif text.startswith('"""', i):
            j = i + 3
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text.startswith('"""', j):
                    j += 3
                    break
                j += 1
            blank(i, j)
            i = j
        elif c == '"' or c == "'":
            quote = c
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == quote or text[j] == "\n":
                    j += 1
                    break
                j += 1
            blank(i, j)
            i = j
        else:
            i += 1
    return "".join(out)


_ALL_CAPS_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
_CAMEL_TYPE_RE = re.compile(r"^[A-Z][\w$]*[a-z][\w$]*$")


class ImportPruneUsageStrategy(MergeStrategy):
    @property
    def name(self) -> str:
        return "ImportPruneUsage"

    def analyze(self, file_path: str, base_content: str = None,
                ours_content: str = None, theirs_content: str = None) -> AnalysisResult:
        if os.environ.get(_ENV_FLAG) != "1":
            return _clean()
        if not file_path.lower().endswith(".java"):
            return _clean()
        # Differential-only: without both parents there is no prune/usage
        # attribution (unresolved_reference.py abstention convention).
        if ours_content is None or theirs_content is None:
            return _clean()

        merged_text = Path(file_path).read_text(encoding="utf-8", errors="replace")
        merged = _FileView(merged_text)
        # Marker check on the STRIPPED text: real conflict markers are code-
        # level (never inside comments/strings), while a comment banner that
        # happens to look like one must not silence the whole file.
        if _CONFLICT_MARKER_RE.search(merged.stripped):
            return _clean()  # textual conflict already surfaced — not silent

        parents = [("ours", _FileView(ours_content)),
                   ("theirs", _FileView(theirs_content))]
        # base_content is deliberately unused: lost = (ours ∪ theirs) − merged
        # subsumes the base comparison (an import absent from BOTH parents is
        # dead on both sides — any surviving usage is a parent-side breakage,
        # not merge-induced, and the absorption guard covers it).

        lost = [im for _, pv in parents for im in pv.imports
                if im.key not in merged.import_keys]
        if not lost:
            return _clean()
        # de-dup (same import lost from both parents)
        lost = list({im.key: im for im in lost}.values())

        issues: List[Issue] = []
        flagged: set = set()

        for im in lost:
            for symbol, kind in self._candidates_of(im, merged):
                if symbol in flagged:
                    continue
                occ = self._stale_occurrences(symbol, kind, im, merged, parents)
                if occ:
                    flagged.add(symbol)
                    issues.append(Issue(
                        line_number=occ[0].line,
                        severity="CRITICAL",
                        message=(
                            f"Stale usage of pruned import: merged file uses "
                            f"'{symbol}' (line {occ[0].line}) but the import that "
                            f"provided it was pruned in the merge — '{im.statement}' "
                            f"survives in {self._holders(im, parents)} and is absent "
                            f"from the merged result, which retains no import "
                            f"covering the name."
                        ),
                        strategy_name=self.name,
                    ))
        return AnalysisResult(is_clean=(len(issues) == 0), issues=issues)

    # ------------------------------------------------------------------ #
    def _candidates_of(self, im: _Import, merged: _FileView):
        """(symbol, kind) candidates a lost import could have provided."""
        if not im.is_wildcard:
            if not im.is_static:
                if im.container == "java.lang":
                    return  # redundant import; removal harmless
                if im.container == merged.package:
                    return  # same-package import; removal harmless (jumblr)
                yield im.simple, "type"
            else:
                # Static explicit: kind by name shape. CamelCase = a nested
                # TYPE import (full type-coverage semantics, any wildcard may
                # suppress); lowercase/ALL_CAPS = a member, which only
                # static-capable imports can cover — a surviving TYPE wildcard
                # (e.g. java.util.*) cannot provide a bare method/constant and
                # must not suppress the flag.
                if _CAMEL_TYPE_RE.match(im.simple):
                    yield im.simple, "type"
                else:
                    yield im.simple, "member"
            return

        # Lost wildcard (narrowing sub-shape): mine merged identifiers.
        if not im.is_static:
            if im.path == "java.lang" or im.path == merged.package:
                return
            # JDK packages have knowable membership: only names in the
            # embedded set can be credited to the lost wildcard; a java.*
            # package without a set yields nothing (FN-only).
            jdk_set = (_JDK_WILDCARD_TYPES.get(im.path, frozenset())
                       if im.path.startswith("java.") else None)
            kind = "type"
        else:
            jdk_set = None
            kind = "member"
        for symbol in self._identifier_pool(merged):
            if kind == "type":
                if symbol in _JAVA_LANG:
                    continue
                if jdk_set is not None and symbol not in jdk_set:
                    continue
                if len(symbol) >= 3 and _CAMEL_TYPE_RE.match(symbol):
                    yield symbol, "type"
            else:
                if _ALL_CAPS_RE.match(symbol) and ("_" in symbol or len(symbol) >= 4):
                    yield symbol, "member"       # constant form
                elif symbol[0].islower():
                    yield symbol, "member-call"  # must show call-form usage

    @staticmethod
    def _identifier_pool(view: _FileView) -> List[str]:
        pool = set()
        for m in _IDENT_RE.finditer(view.stripped):
            name = m.group(0)
            if name in _KEYWORDS or len(name) < 2:
                continue
            pool.add(name)
        return sorted(pool)

    def _stale_occurrences(self, symbol: str, kind: str, im: _Import,
                           merged: _FileView, parents) -> List[_Occurrence]:
        base_kind = "member" if kind.startswith("member") else "type"
        if merged.covers(symbol, base_kind):
            return []
        if base_kind == "type" and merged.declares_type(symbol):
            return []
        if merged.declares_member(symbol):
            return []  # a local method/field/var named S shadows either kind
        occ = merged.occurrences(symbol)
        if kind == "member-call":
            occ = [o for o in occ if o.call_form]
        if not occ:
            return []
        # Absorption guard (§2 "usage resolves in each parent"): any parent
        # that lacks this import yet still uses S uncovered proves S resolves
        # without it (same-package/inherited) — or that parent was already
        # broken. Either way: not merge-induced.
        for _, pv in parents:
            if im.key in pv.import_keys:
                continue
            if pv.uses(symbol) and not pv.covers(symbol, base_kind):
                return []
        return occ

    @staticmethod
    def _holders(im: _Import, parents) -> str:
        holders = [label for label, pv in parents if im.key in pv.import_keys]
        return " and ".join(holders) if holders else "neither parent"


def _clean() -> AnalysisResult:
    return AnalysisResult(is_clean=True, issues=[])
