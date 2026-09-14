import subprocess
import os
from core.interfaces import MergeStrategy, AnalysisResult, Issue

# Conflict category #5 — Loop Semantics Divergence (constant-condition loops).
#
# v2 (Stage B, 2026-06-11 — ISSUES #29 pilot evidence). All five v1 pilot
# FLAGs were false positives of three distinct shapes, each fixed here:
#   1. v1's query (`condition.isLiteral.code("1|true").astParent`) matched ANY
#      control structure — `if(true)` (clojure Compiler.java:7397) is not a
#      loop. v2 restricts to controlStructureType WHILE/DO/FOR.
#   2. Deliberate `while(true) { ... break/return/throw ... }` idioms (4 of 5
#      pilot sites; server/wait/REPL loops). v2 suppresses loops with any
#      BREAK control structure, RETURN, or `<operator>.throw` call in the
#      loop body (probed against javasrc2cpg 2026-06-11: break/return are
#      CONTROL_STRUCTURE/RETURN nodes, throw lowers to a `<operator>.throw`
#      CALL). Conservative: an exit on ANY path (even a nested loop's break)
#      suppresses — precision-first for R1.
#   3. Every pilot site was present verbatim in base+ours+theirs — pre-
#      existing code is not the merge driver's concern. v2 is differential
#      (the DFI Phase-2a pattern): with parents supplied, only loops whose
#      (method, condition) key appears in NEITHER parent are flagged.
#      Phase-1 fallback without parents: flag all (standalone unit calls).
#
# Remaining scope limits: literal `1`/`true` conditions only (`for(;;)` and
# constant-folded conditions are not matched — unchanged from v1); the
# (method, condition) differential key is coarse — a method that already had
# any constant-condition loop in a parent suppresses new ones in the same
# method (conservative, fewer FPs).

_QUERY = r"""
import io.shiftleft.semanticcpg.language._
{
  val loops = cpg.controlStructure.controlStructureType("WHILE", "DO", "FOR")
    .where(_.condition.isLiteral.code("1|true")).l
  val noExit = loops.filter(l =>
    l.ast.isControlStructure.controlStructureType("BREAK").isEmpty &&
    l.ast.isReturn.isEmpty &&
    l.ast.isCall.nameExact("<operator>.throw").isEmpty)
  noExit.foreach { l =>
    val ln = l.lineNumber.map(_.toString.toInt).getOrElse(-1)
    val m = l.method.name
    val cond = l.condition.code.headOption.getOrElse("?")
    println(s"DETECTED_ISSUE_AT:$ln||$m||$cond")
  }
}
"""


class _JoernError(Exception):
    """Raised when a Joern parse/query is inconclusive (drives fail-closed)."""


class JoernInfiniteLoopStrategy(MergeStrategy):
    @property
    def name(self) -> str:
        return "JoernInfiniteLoop"

    def analyze(self, file_path: str, base_content: str = None,
                ours_content: str = None, theirs_content: str = None) -> AnalysisResult:
        try:
            merged_loops = self._run_query(file_path)
        except _JoernError as e:
            return self._fail_closed(f"merged analysis inconclusive: {e}")

        # Phase-1 fallback: no parents supplied -> flag every exit-less
        # constant-condition loop.
        if ours_content is None and theirs_content is None:
            return self._result(merged_loops)

        # Differential: keep only loops whose (method, condition) key is
        # absent from BOTH parents (i.e. the merge introduced them).
        parent_keys = set()
        for label, content in (("ours", ours_content), ("theirs", theirs_content)):
            if content is None:
                continue
            tmp = f"{file_path}.{label}.java"
            try:
                with open(tmp, "w") as f:
                    f.write(content)
                parent_keys |= {(m, cond) for (_, m, cond) in self._run_query(tmp)}
            except _JoernError as e:
                return self._fail_closed(f"{label} analysis inconclusive: {e}")
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)

        induced = [(ln, m, cond) for (ln, m, cond) in merged_loops
                   if (m, cond) not in parent_keys]
        return self._result(induced)

    def _run_query(self, file_path: str):
        """Run the exit-less constant-loop query on one file.

        Returns [(line, method, condition)]. Raises _JoernError on any
        parse/query failure so the caller can fail closed.
        """
        cpg_out = f"{file_path}.cpg.bin"
        query_file = f"{file_path}.query.sc"
        try:
            try:
                subprocess.run(["joern-parse", file_path, "--output", cpg_out],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                raise _JoernError(f"joern-parse failed: {e}")

            with open(query_file, "w") as f:
                f.write(_QUERY)

            process = subprocess.run(
                f"cat {query_file} | joern --cpg {cpg_out} --nocolors",
                shell=True, capture_output=True, text=True,
            )
            if process.returncode != 0:
                raise _JoernError(
                    f"joern query rc={process.returncode}: {process.stderr.strip() or '(empty)'}"
                )

            loops = []
            for line in process.stdout.splitlines():
                if "DETECTED_ISSUE_AT:" not in line:
                    continue
                parts = line.split("DETECTED_ISSUE_AT:", 1)[1].strip().split("||")
                if len(parts) < 3:
                    continue
                try:
                    ln = int(parts[0].strip())
                except ValueError:
                    continue
                loops.append((ln, parts[1].strip(), parts[2].strip()))
            return loops
        finally:
            if os.path.exists(cpg_out):
                os.remove(cpg_out)
            if os.path.exists(query_file):
                os.remove(query_file)

    def _result(self, loops) -> AnalysisResult:
        issues = [
            Issue(
                line_number=ln,
                severity="CRITICAL",
                message=(
                    f"Potential infinite loop in method '{m}': constant condition "
                    f"({cond}) with no break/return/throw on any path."
                ),
                strategy_name=self.name,
            )
            for (ln, m, cond) in loops
        ]
        return AnalysisResult(is_clean=(len(issues) == 0), issues=issues)

    def _fail_closed(self, msg: str) -> AnalysisResult:
        return AnalysisResult(
            is_clean=False,
            issues=[Issue(line_number=0, severity="CRITICAL",
                          message=f"Joern analysis inconclusive: {msg}",
                          strategy_name=self.name)],
        )
