import subprocess
import os
import sys
from core.interfaces import MergeStrategy, AnalysisResult, Issue

class JoernInvalidLoopBoundsStrategy(MergeStrategy):
    @property
    def name(self) -> str:
        return "JoernInvalidLoopBounds"

    def analyze(self, file_path: str, base_content: str = None,
                ours_content: str = None, theirs_content: str = None) -> AnalysisResult:
        """
        Checks for loops where the start index is already greater than the end condition
        (e.g., for(i=10; i<5; i++)), rendering the loop dead code.
        """
        cpg_out = f"{file_path}.cpg.bin"
        query_file = f"{file_path}.query.sc"
        
        try:
            # 1. Generate CPG
            parse_cmd = ["joern-parse", file_path, "--output", cpg_out]
            subprocess.run(parse_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 2. Create a temporary Scala script file
            # Improvement: This script ignores rigid child ordering (0 vs 1).
            # Instead, it finds the 'Header' children (everything except the last child/Body).
            # Inside the header, it looks for:
            #  - Start: A literal on the RHS of an Assignment (<operator>.assignment)
            #  - End:   A literal on the RHS of a Comparison (<operator>.lessThan, etc.)
            scala_script = """
            import io.shiftleft.semanticcpg.language._
            
            println("--- START JOERN ANALYSIS ---")

            cpg.controlStructure.controlStructureType("FOR").map { loop =>
                val line = loop.lineNumber.getOrElse(-1)
                
                // 1. Isolate the Loop Header
                // The body is typically the last child with the highest 'order'.
                // We take all children except the last one to inspect the control logic.
                val allChildren = loop.astChildren.sortBy(_.order).l
                val headerChildren = if (allChildren.nonEmpty) allChildren.dropRight(1) else List()

                // 2. Find START Value (Assignment RHS)
                // We scan header nodes for assignments: i = 15
                val startVals = headerChildren.ast.isCall
                    .nameExact("<operator>.assignment")
                    .argument(2).isLiteral.code.l
                    .flatMap(c => scala.util.Try(c.toInt).toOption)

                // 3. Find END Value (Comparison RHS)
                // We scan header nodes for comparisons: i < 10
                val endVals = headerChildren.ast.isCall
                    .name("<operator>.lessThan", "<operator>.lessEquals")
                    .argument(2).isLiteral.code.l
                    .flatMap(c => scala.util.Try(c.toInt).toOption)

                println(s"[DEBUG] Line: $line | Start candidates: $startVals | End candidates: $endVals")

                // 4. Comparison Logic
                (startVals.lastOption, endVals.lastOption) match {
                    case (Some(start), Some(end)) if start > end => 
                        line // Bug Found
                    case _ => 
                        -1   // Clean
                }
            }.filter(_ != -1).l.distinct.foreach(ln => println(s"DETECTED_ISSUE_AT:$ln"))
            
            println("--- END JOERN ANALYSIS ---")
            """
            
            with open(query_file, "w") as f:
                f.write(scala_script)

            # 3. Execute the script
            cmd = f"cat {query_file} | joern --cpg {cpg_out} --nocolors"
            
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if process.returncode != 0:
                # Fail-closed: a crashed Joern query yields empty stdout, which the
                # parser below would silently treat as zero issues → is_clean=True.
                return AnalysisResult(
                    is_clean=False,
                    issues=[Issue(
                        line_number=0,
                        severity="CRITICAL",
                        message=f"Joern query exited rc={process.returncode}; analysis inconclusive: {process.stderr.strip() or '(empty)'}",
                        strategy_name=self.name,
                    )],
                )
            output = process.stdout

            # Print output for debugging in your tests
            print(output)

            # 4. Parse Result
            issues = []
            for line in output.splitlines():
                if "DETECTED_ISSUE_AT:" in line:
                    try:
                        ln = int(line.split(":")[1].strip())
                        issues.append(Issue(
                            line_number=ln,
                            severity="WARNING",
                            message="Dead Loop Detected: Initializer is greater than terminal condition (Start > End).",
                            strategy_name=self.name
                        ))
                    except ValueError:
                        continue

            return AnalysisResult(is_clean=(len(issues) == 0), issues=issues)

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[ERROR] Joern execution failed: {e}")
            return AnalysisResult(
                is_clean=False,
                issues=[Issue(
                    line_number=0,
                    severity="CRITICAL",
                    message=f"Joern subprocess failed; analysis inconclusive: {e}",
                    strategy_name=self.name,
                )],
            )
            
        finally:
            # Cleanup
            if os.path.exists(cpg_out):
                os.remove(cpg_out)
            if os.path.exists(query_file):
                os.remove(query_file)