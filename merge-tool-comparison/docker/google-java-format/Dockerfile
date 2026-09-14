# google-java-format — canonical Java formatter.
#
# Used by the comparator (src/evaluation/comparator.py) as an M3.5 (3e)
# normalisation step: both candidate and reference are roundtripped through
# the formatter before text comparison, so AST-equivalent reformatting
# (brace style, blank lines, redundant parens, import order, method-signature
# line breaks) does not register as a FP.
#
# Version pinned per docs/plans/mergiraf-integration.md §Phase 3.5.
# Invocation:
#   docker run --rm -i merge-tools/google-java-format:1.22.0
# Reads Java source from stdin, writes formatted Java to stdout, rc=0 on
# success; rc!=0 if input does not parse.
#
# The `--add-exports` flags are required since 1.10 — google-java-format
# touches jdk.compiler internals that are encapsulated by default on JDK 17+.

FROM eclipse-temurin:17-jdk
ARG GJF_VERSION=1.22.0
ADD https://github.com/google/google-java-format/releases/download/v${GJF_VERSION}/google-java-format-${GJF_VERSION}-all-deps.jar /opt/gjf.jar
ENTRYPOINT ["java", \
    "--add-exports", "jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED", \
    "--add-exports", "jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED", \
    "--add-exports", "jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED", \
    "--add-exports", "jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED", \
    "--add-exports", "jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED", \
    "--add-exports", "jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED", \
    "-jar", "/opt/gjf.jar", "-"]
