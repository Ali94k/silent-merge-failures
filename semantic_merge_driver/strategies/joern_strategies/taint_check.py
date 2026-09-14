import subprocess
import os
from core.interfaces import MergeStrategy, AnalysisResult, Issue

# Conflict category #3 — Data Flow Interference (Stale Read).
#
# Detects the "stale read" shape: within a single method a collection is reset
# (`X.clear()`) and then read (iterated / queried) with no intervening
# repopulation, so the read observes empty/stale state.
#
# Phase 2 (differential / merge-induced): when both branch versions are
# supplied (ours_content + theirs_content), only patterns present in the MERGED
# file but in NEITHER parent are flagged — i.e. the merge itself introduced the
# stale read (one side added the reset, the other the read). A stale read
# carried in from a parent is not the merge driver's concern and is not flagged.
#
# Phase 1 fallback: if the parents are not supplied (e.g. a standalone unit
# call), any stale read found in the merged file is flagged.
#
# SCOPE & LIMITATIONS (honest framing — the class name overstates what this does):
#   * Heuristic, NOT data-flow analysis: kill and read are ordered by LINE
#     NUMBER within a method, not by Joern's CFG/DDG. Conditional clears,
#     branches, loops, and early returns are not modelled -> false positive on a
#     conditional reset; false negative when a repopulating call sits between the
#     lines on only one path.
#   * No types: read/reset are matched by METHOD NAME only (single-file
#     javasrc2cpg resolves no collection types), so clear()/get()/size() on a
#     non-collection can false-positive.
#   * Only a literal `X.clear()` counts as a reset (not `= null`, reassignment,
#     removeAll, ...). Intra-method, intra-file only.
#   * No soundness evidence yet: verified against the canonical fixture only;
#     FP/FN rates are unmeasured pending the Phase-2b static-semantic-merge oracle.

_READ_METHODS = (
    'Set("iterator","get","size","isEmpty","contains","stream","forEach",'
    '"toArray","listIterator","peek","element","getFirst","getLast")'
)
_MUT_METHODS = (
    'Set("add","addAll","put","putAll","set","push","offer","offerFirst",'
    '"offerLast","addFirst","addLast","putIfAbsent","merge","replace","removeIf")'
)

# Emits one `DETECTED_ISSUE_AT:<line>||<collection>||<method-fullName>` line per
# (method, collection) stale read. Kill/read/mut are matched within the same
# enclosing method; a repopulating call between the clear and the read suppresses.
_QUERY_TEMPLATE = r"""
import io.shiftleft.semanticcpg.language._
{
  val READ = %(read)s
  val MUT  = %(mut)s
  def evs(pred: String => Boolean) =
    cpg.call.filter(c => pred(c.name)).map { c =>
      val rc = c.receiver.code.headOption.getOrElse("").stripPrefix("this.").trim
      val ln = c.lineNumber.map(_.toString.toInt).getOrElse(-1)
      val m  = c.start.method.fullName.l.headOption.getOrElse("?")
      (rc, ln, m)
    }.l.filter { case (rc, ln, m) => rc.nonEmpty && ln > 0 }
  val kills = evs(_ == "clear")
  val reads = evs(READ.contains)
  val muts  = evs(MUT.contains)
  val hits = (for {
    (kk, kl, km) <- kills
    (rk, rl, rm) <- reads
    if rk == kk && rm == km && rl > kl
    if !muts.exists { case (mk, ml, mm) => mk == kk && mm == km && ml > kl && ml < rl }
  } yield (rl, kk, km)).distinct
  hits.foreach { case (ln, key, m) => println(s"DETECTED_ISSUE_AT:$ln||$key||$m") }
}
""" % {"read": _READ_METHODS, "mut": _MUT_METHODS}


class _JoernError(Exception):
    """Raised when a Joern parse/query is inconclusive (drives fail-closed)."""


class JoernDataFlowInterferenceStrategy(MergeStrategy):
    @property
    def name(self) -> str:
        return "JoernDataFlowInterference"

    def analyze(self, file_path: str, base_content: str = None,
                ours_content: str = None, theirs_content: str = None) -> AnalysisResult:
        try:
            merged_issues, _ = self._run_query(file_path)
        except _JoernError as e:
            return self._fail_closed(f"merged analysis inconclusive: {e}")

        # Phase 1 fallback: no parents supplied -> flag any stale read.
        if ours_content is None and theirs_content is None:
            return self._result(merged_issues)

        # Phase 2: keep only (method, collection) pairs absent from BOTH parents
        # (i.e. the merge introduced the stale read).
        parent_pairs = set()
        for label, content in (("ours", ours_content), ("theirs", theirs_content)):
            if content is None:
                continue
            tmp = f"{file_path}.{label}.java"
            try:
                with open(tmp, "w") as f:
                    f.write(content)
                _, pairs = self._run_query(tmp)
                parent_pairs |= pairs
            except _JoernError as e:
                return self._fail_closed(f"{label} analysis inconclusive: {e}")
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)

        induced = [(ln, coll, method) for (ln, coll, method) in merged_issues
                   if (method, coll) not in parent_pairs]
        return self._result(induced)

    def _run_query(self, file_path: str):
        """Run the stale-read query on one file.

        Returns (issues, pairs) where issues = [(line, collection, method)] and
        pairs = {(method, collection)}. Raises _JoernError on parse/query
        failure so the caller can fail closed.
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
                f.write(_QUERY_TEMPLATE)

            process = subprocess.run(
                f"cat {query_file} | joern --cpg {cpg_out} --nocolors",
                shell=True, capture_output=True, text=True,
            )
            if process.returncode != 0:
                raise _JoernError(
                    f"joern query rc={process.returncode}: {process.stderr.strip() or '(empty)'}"
                )

            issues = []
            pairs = set()
            for line in process.stdout.splitlines():
                if "DETECTED_ISSUE_AT:" not in line:
                    continue
                payload = line.split("DETECTED_ISSUE_AT:", 1)[1].strip()
                parts = payload.split("||")
                if len(parts) < 3:
                    continue
                try:
                    ln = int(parts[0].strip())
                except ValueError:
                    continue
                coll, method = parts[1].strip(), parts[2].strip()
                issues.append((ln, coll, method))
                pairs.add((method, coll))
            return issues, pairs
        finally:
            if os.path.exists(cpg_out):
                os.remove(cpg_out)
            if os.path.exists(query_file):
                os.remove(query_file)

    def _result(self, issues) -> AnalysisResult:
        out = [
            Issue(
                line_number=ln,
                severity="CRITICAL",
                message=(
                    f"Potential stale read: collection '{coll}' is reset (clear) "
                    f"and then read without repopulation."
                ),
                strategy_name=self.name,
            )
            for (ln, coll, _method) in issues
        ]
        return AnalysisResult(is_clean=(len(out) == 0), issues=out)

    def _fail_closed(self, msg: str) -> AnalysisResult:
        return AnalysisResult(
            is_clean=False,
            issues=[Issue(line_number=0, severity="CRITICAL",
                          message=f"Joern analysis inconclusive: {msg}",
                          strategy_name=self.name)],
        )
