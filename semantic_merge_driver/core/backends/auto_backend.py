"""AutoBackend — classifier-driven dispatch.

Phase 1 (wired here): classify each merge by RM2 refactoring cluster, then
route to the designated backend. Phase 2 (separate, deferred) validates
whether the routing is *sound* on real data; this module only implements and
exercises the *mechanism*.

Routing map — **post-flip default** (#27/#28 DROP landed 2026-06-27; NONE→git
decided 2026-05-19):

    cluster = NONE                         → GitMergeFileBackend
        (no refactoring → fastest/simplest tool)
    everything else                        → MergirafBackend (default)
    any routed backend returns CRASH       → GitMergeFileBackend (fallback)

The two specialist arms were **empirically refuted** — #27 (INTRA_BODY→Spork:
pooled precision 0.49 vs Mergiraf 0.78, Wilson non-overlapping, 0 strict wins),
#28 (MIGRATE_DECL→Weave: 0/38 wins, McNemar p=0.0078), corroborated end-to-end
by P2 (pre-flip auto cost 2055 vs always-Mergiraf 1994; 33/239 good merges
silently broken, Spork FP 64/79 on its routed files;
reports_whole_driver/FINDINGS.md §4). They remain available as *apparatus*
behind an opt-in flag (reproduces the P2 before/after; demonstrable mechanism
for future specialist candidates):

    SEMANTIC_MERGE_SPECIALIST_ROUTING=1 additionally enables
        cluster = MIGRATE_DECL                 → WeaveBackend        (W5, refuted)
        cluster = INTRA_BODY and language=JAVA → SporkBackend        (S2, refuted)

Sequence per merge:
    1. RefactoringClusterClassifier.cluster(base, ours, theirs) → Cluster
       (fail-closed → Cluster.NONE on any RM2 failure; defensive try here too).
    2. language_of(ours_path) → Language (UNKNOWN if extension unmapped).
    3. Route by (cluster, language) per the map above.
    4. If the chosen backend returns CRASH, log and retry once via the
       git-merge-file fallback — unless git-merge-file was already the chosen
       backend (NONE cluster, or its own crash), in which case there is
       nothing better to try and the CRASH is returned. CONFLICT is *not* a
       fallback trigger — markers in the output are a valid outcome.
    5. The dispatch decision (cluster, language, chosen backend) is logged
       to stderr on every invocation.

Fail-closed contract preserved end-to-end: AutoBackend.merge() never raises;
on any unexpected exception from the classifier, the cluster is treated as
NONE and routing continues (NONE → git-merge-file).
"""
import os
import sys

from core.backends.base import MergeBackend, MergeOutcome
from core.backends.git_merge_file_backend import GitMergeFileBackend
from core.backends.mergiraf_backend import MergirafBackend
from core.backends.spork_backend import SporkBackend
from core.backends.weave_backend import WeaveBackend
from core.language_detect import Language, language_of
from core.refactoring_classifier import Cluster, RefactoringClusterClassifier

# Opt-in re-enable of the refuted specialist arms (#27/#28). Read at
# _route() call time (not import time) so a single process can flip it —
# mirrors how driver.py reads SEMANTIC_MERGE_BACKEND from the environment.
SPECIALIST_ROUTING_ENV = "SEMANTIC_MERGE_SPECIALIST_ROUTING"


class AutoBackend(MergeBackend):
    @property
    def name(self) -> str:
        return "auto"

    def __init__(
        self,
        classifier: RefactoringClusterClassifier = None,
        primary: MergeBackend = None,
        fallback: MergeBackend = None,
        spork: MergeBackend = None,
        weave: MergeBackend = None,
    ):
        self._classifier = classifier or RefactoringClusterClassifier()
        self._primary = primary or MergirafBackend()
        self._fallback = fallback or GitMergeFileBackend()
        self._spork = spork or SporkBackend()
        self._weave = weave or WeaveBackend()

    def merge(
        self, base_path: str, ours_path: str, theirs_path: str
    ) -> MergeOutcome:
        try:
            cluster = self._classifier.cluster(base_path, ours_path, theirs_path)
        except Exception as e:
            print(
                f"AutoBackend: classifier raised {type(e).__name__}: {e}; "
                f"treating as cluster=NONE",
                file=sys.stderr,
            )
            cluster = Cluster.NONE

        language = language_of(ours_path)
        chosen = self._route(cluster, language)

        print(
            f"AutoBackend: cluster={cluster.value} language={language.value} "
            f"→ {chosen.name}",
            file=sys.stderr,
        )

        outcome = chosen.merge(base_path, ours_path, theirs_path)
        if outcome != MergeOutcome.CRASH:
            return outcome

        if chosen is self._fallback:
            return outcome

        print(
            f"AutoBackend: {chosen.name} crashed; "
            f"falling back to {self._fallback.name}",
            file=sys.stderr,
        )
        return self._fallback.merge(base_path, ours_path, theirs_path)

    def _route(self, cluster: Cluster, language: Language) -> MergeBackend:
        """Map a (cluster, language) pair to a backend instance.

        **MUST NOT RAISE.** Returns an already-constructed `MergeBackend`
        held on `self`. Backend constructors may touch the filesystem or
        Docker and could fail; that work belongs in `__init__` so the
        must-not-raise contract on `merge()` is preserved end-to-end.

        Precedence between clusters is already resolved by the classifier
        (it returns a single Cluster); this method only maps that single
        label, with one language gate on the INTRA_BODY arm.
        """
        if cluster == Cluster.NONE:
            # No refactoring detected → fastest/simplest tool. git-merge-file
            # is both this cluster's target and the universal crash fallback.
            return self._fallback
        if os.environ.get(SPECIALIST_ROUTING_ENV) == "1":
            # REFUTED arms (#27 Spork, #28 Weave; P2 in-vivo corroboration —
            # see module docstring). Opt-in apparatus only: reproduces the P2
            # pre-flip behavior and keeps the mechanism demonstrable for any
            # future specialist candidate. Never enabled by default.
            if cluster == Cluster.MIGRATE_DECL:
                return self._weave
            if cluster == Cluster.INTRA_BODY and language == Language.JAVA:
                # The `language == JAVA` conjunct is a defensive guard for
                # Java-only Spork, not an active dispatch axis (RM2, the only
                # INTRA_BODY producer, is Java-only). Non-Java INTRA_BODY
                # falls through to Mergiraf. See
                # docs/plans/spork-driver-integration.md header note.
                return self._spork
        # Default (post-flip, #27/#28): SYMBOL_CASCADE, CONTAINER_MOVE,
        # HIERARCHY_RESHAPE, LOCAL_DECL_EDIT, MIGRATE_DECL, INTRA_BODY —
        # everything non-NONE → Mergiraf.
        return self._primary
