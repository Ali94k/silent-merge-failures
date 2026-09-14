import hashlib
import logging
import os
import subprocess
from enum import Enum

from src.core.interfaces import MergeResult, MergeOutcome
from src.evaluation.ast_normalize import ast_canonicalize


log = logging.getLogger(__name__)


class Classification(Enum):
    TRUE_POSITIVE = "TP"    # Clean merge, matches developer resolution
    FALSE_POSITIVE = "FP"   # Clean merge, differs from developer resolution (silent error)
    TRUE_NEGATIVE = "TN"    # Conflict reported, developer also had non-trivial resolution
    FALSE_NEGATIVE = "FN"   # Conflict reported, but merge was actually trivial
    CRASH = "CRASH"
    TIMEOUT = "TIMEOUT"


FORMATTER_IMAGE = "merge-tools/google-java-format:1.22.0"
FORMATTER_TIMEOUT_S = 30
FORMATTER_ENV = "MERGE_COMPARATOR_FORMATTER"  # values: "on" (default), "off"
AST_NORMALIZE_ENV = "MERGE_COMPARATOR_AST_NORMALIZE"  # values: "on" (default), "off"

# Module-level caches.
# _format_cache: keyed by sha256 of the base-normalized content; value is the
# gjf-formatted content, or None if the formatter failed (parse error, Docker
# unavailable, timeout). Cached failures so we don't retry every comparison.
# _ast_cache: keyed by sha256 of the gjf-normalized content (Tier 3 always
# runs on Tier 2's output, never on raw input — see plan §4.4).
_format_cache: dict[str, str | None] = {}
_ast_cache: dict[str, str | None] = {}


def normalize_content(content: str) -> str:
    """Whitespace-and-line-ending normalization. Cheap; safe on any text.

    Used directly for non-source comparisons (e.g., comparing developer
    resolution against base/ours/theirs files) and as the input to the
    formatter roundtrip in `contents_match`.
    """
    lines = content.replace("\r\n", "\n").split("\n")
    lines = [line.rstrip() for line in lines]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _format_java(content: str) -> str | None:
    """Run google-java-format on `content` via Docker. Returns formatted text
    on success, or None if the formatter rejects the input or is unavailable.

    Results cached per-process by content hash.
    """
    key = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if key in _format_cache:
        return _format_cache[key]

    try:
        proc = subprocess.run(
            ["docker", "run", "--rm", "-i", FORMATTER_IMAGE],
            input=content.encode("utf-8"),
            capture_output=True,
            timeout=FORMATTER_TIMEOUT_S,
        )
    except FileNotFoundError:
        log.warning("docker not found; formatter disabled for this run")
        _format_cache[key] = None
        return None
    except subprocess.TimeoutExpired:
        log.warning("google-java-format timed out after %ds", FORMATTER_TIMEOUT_S)
        _format_cache[key] = None
        return None

    if proc.returncode != 0:
        # Most common cause: input does not parse (e.g., conflict markers,
        # tool-mangled output). Debug-log; treat as non-formattable.
        log.debug(
            "google-java-format rc=%d stderr=%r",
            proc.returncode,
            proc.stderr[:200],
        )
        _format_cache[key] = None
        return None

    formatted = proc.stdout.decode("utf-8", errors="replace")
    _format_cache[key] = formatted
    return formatted


def _ast_normalize(content: str) -> str | None:
    """Run `ast_canonicalize` on `content`, caching by content hash. Tier 3
    of `contents_match`; always invoked on Tier 2's output (gjf-formatted
    source). Returns None if the source does not parse."""
    key = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if key in _ast_cache:
        return _ast_cache[key]
    result = ast_canonicalize(content)
    _ast_cache[key] = result
    return result


def contents_match(a: str, b: str) -> bool:
    """Compare two file contents for equivalence.

    Three-tier check:
      1. Whitespace/line-ending normalization (cheap; handles trailing-space,
         CRLF/LF, trailing-blank differences).
      2. If (1) disagrees and the formatter is enabled, roundtrip both sides
         through `google-java-format` and re-compare. Collapses brace style,
         import order, method-signature line breaks — patterns gjf rewrites.
      3. If (2) still disagrees and AST normalize is enabled, parse both
         gjf-formatted sides via tree-sitter-java, apply semantics-preserving
         canonicalisation transforms (comment + blank-line stripping; later
         phases add `else { if }` flattening, paren-wrapping-paren collapse,
         hardcoded java.lang.* FQN stripping), and re-compare. Recovers
         §9-observed Spork FPs that are AST-equivalent reformatting gjf
         preserves rather than canonicalises.

    Set `MERGE_COMPARATOR_FORMATTER=off` to disable tier (2);
    `MERGE_COMPARATOR_AST_NORMALIZE=off` to disable tier (3). Each tier
    silently degrades to "different" when its parser rejects the input or
    its runtime is unavailable; the conservative fallback preserves
    correctness rather than masking real disagreement as a match.
    """
    na, nb = normalize_content(a), normalize_content(b)
    if na == nb:
        return True
    if os.environ.get(FORMATTER_ENV, "on").lower() == "off":
        return False
    fa = _format_java(na)
    if fa is None:
        return False
    fb = _format_java(nb)
    if fb is None:
        return False
    if normalize_content(fa) == normalize_content(fb):
        return True
    if os.environ.get(AST_NORMALIZE_ENV, "on").lower() == "off":
        return False
    aa = _ast_normalize(fa)
    if aa is None:
        return False
    ab = _ast_normalize(fb)
    if ab is None:
        return False
    return normalize_content(aa) == normalize_content(ab)


def classify_result(
    result: MergeResult,
    developer_resolution: str,
    base_content: str,
    ours_content: str,
    theirs_content: str,
) -> Classification:
    """
    Classify a merge tool's result against the developer's resolution.

    Logic:
    - CRASH/TIMEOUT → tracked separately
    - Tool says clean + matches developer → TP (correct merge)
    - Tool says clean + differs from developer → FP (silent error)
    - Tool says conflict + dev reverted to base → FN (false alarm)
    - Tool says conflict + dev picked a parent + both parents changed → TN (real conflict)
    - Tool says conflict + dev picked a parent + only one changed → FN (false alarm)
    - Tool says conflict + dev wrote novel resolution → TN (real conflict)
    """
    if result.outcome == MergeOutcome.CRASH:
        return Classification.CRASH

    if result.outcome == MergeOutcome.TIMEOUT:
        return Classification.TIMEOUT

    if result.outcome == MergeOutcome.CLEAN:
        if result.merged_content and contents_match(
            result.merged_content, developer_resolution
        ):
            return Classification.TRUE_POSITIVE
        return Classification.FALSE_POSITIVE

    # CONFLICT case
    dev_matches_ours = contents_match(developer_resolution, ours_content)
    dev_matches_theirs = contents_match(developer_resolution, theirs_content)
    dev_matches_base = contents_match(developer_resolution, base_content)

    if dev_matches_base:
        # Developer reverted to base — conflict was a false alarm
        return Classification.FALSE_NEGATIVE

    if dev_matches_ours or dev_matches_theirs:
        # Developer picked one side. Check if both sides actually changed from
        # base — if so, it's a real conflict and the developer chose one side
        # as a deliberate resolution, not because the conflict was unnecessary.
        ours_changed = not contents_match(ours_content, base_content)
        theirs_changed = not contents_match(theirs_content, base_content)
        if ours_changed and theirs_changed:
            return Classification.TRUE_NEGATIVE
        # Only one side changed — conflict was unnecessary
        return Classification.FALSE_NEGATIVE

    return Classification.TRUE_NEGATIVE
