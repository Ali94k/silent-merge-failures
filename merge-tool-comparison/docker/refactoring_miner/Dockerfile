# RefactoringMiner 2.4.0 (last 2.x release).
# Pinned in docs/plans/rm2-integration-recon.md (Phase R0).
# RM 3.x is out of scope for the thesis — kept on the published 2.x line.
#
# D2 pattern (pull released ZIP from GitHub releases) + B (thin Java wrapper).
# Mirrors the existing tool Dockerfile shape under merge-tool-comparison/docker/.

# RM 2.4.0 ships Java 11 bytecode (class file v55). JDK 17 reads it fine
# and matches Joern's 17+ requirement, so 17-jdk satisfies both.
FROM eclipse-temurin:17-jdk

ARG RM_VERSION=2.4.0

RUN apt-get update \
 && apt-get install -y --no-install-recommends wget unzip \
 && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/rm.zip \
      "https://github.com/tsantalis/RefactoringMiner/releases/download/${RM_VERSION}/RefactoringMiner-${RM_VERSION}.zip" \
 && unzip -q /tmp/rm.zip -d /opt \
 && rm /tmp/rm.zip \
 && ln -s /opt/RefactoringMiner-${RM_VERSION} /opt/RefactoringMiner

COPY DirPairMain.java /opt/wrapper/DirPairMain.java
RUN javac -cp "/opt/RefactoringMiner/lib/*" -d /opt/wrapper /opt/wrapper/DirPairMain.java

WORKDIR /workspace
ENTRYPOINT ["java", "-cp", "/opt/wrapper:/opt/RefactoringMiner/lib/*", "DirPairMain"]
