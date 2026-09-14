import argparse
import os
import sys
from pathlib import Path
from typing import List

# Allow `python /abs/path/core/driver.py` (e.g., as a git merge driver) to find
# sibling `core.*` modules — Python's script invocation only puts the script's
# own dir on sys.path, not its parent.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.backends.auto_backend import AutoBackend
from core.backends.base import MergeBackend, MergeOutcome
from core.backends.git_merge_file_backend import GitMergeFileBackend
from core.backends.mergiraf_backend import MergirafBackend
from core.backends.spork_backend import SporkBackend
from core.backends.weave_backend import WeaveBackend
from core.config import load_enabled_strategies
from core.plugin_loader import StrategyLoader


BACKENDS = {
    "git": GitMergeFileBackend,
    "mergiraf": MergirafBackend,
    "spork": SporkBackend,
    "weave": WeaveBackend,
    "auto": AutoBackend,
}
DEFAULT_BACKEND = "auto"


class SemanticMergeDriver:
    def __init__(self, backend: MergeBackend, strategies: List[str] = None):
        """
        Initialize the driver with a merge backend and an optional list of
        strategies to enable. If `strategies` is None, all discovered
        strategies are loaded.
        """
        self.backend = backend
        self.loader = StrategyLoader(config_enabled_list=strategies)

    def run_merge(self, base_path: str, current_path: str, other_path: str) -> int:
        """
        Executes the merge process.
        Returns:
            0: Success (clean merge, all strategies pass)
            1: Failure (textual conflict, semantic issue, or backend crash)
        """
        # Capture the two sides before the backend overwrites current_path
        # (Git's %A = ours) with the merged result — 3-way / merge-induced
        # strategies need the original ours + theirs.
        try:
            ours_content = Path(current_path).read_text(encoding="utf-8", errors="replace")
            theirs_content = Path(other_path).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"Could not read ours/theirs inputs: {e}", file=sys.stderr)
            return 1

        # 1. Backend-driven three-way merge (mutates current_path in place)
        outcome = self.backend.merge(base_path, current_path, other_path)
        if outcome == MergeOutcome.CRASH:
            print(f"Backend '{self.backend.name}' crashed; rejecting merge.")
            return 1

        # 2. Load Strategies
        strategies = self.loader.load_strategies()
        if not strategies:
            # No semantic checks; trust backend's outcome
            return 1 if outcome == MergeOutcome.CONFLICT else 0

        print(f"Running {len(strategies)} semantic analysis strategies on {current_path}...")

        # Read base once for any strategy that needs (base, merged) input.
        # Strategies that ignore base_content (the signature default) are
        # unaffected.
        try:
            base_content = Path(base_path).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"Could not read base file {base_path}: {e}", file=sys.stderr)
            return 1

        all_clean = True

        # 3. Execute Strategies
        for strategy in strategies:
            try:
                result = strategy.analyze(current_path, base_content, ours_content, theirs_content)

                if not result.is_clean:
                    all_clean = False
                    for issue in result.issues:
                        print(f"[{issue.severity}] {strategy.name}: {issue.message} at line {issue.line_number}")
            except Exception as e:
                print(f"Strategy {strategy.name} failed to execute: {e}")
                # Fail safe: if analysis fails, reject the merge
                return 1

        # 4. Return Status
        if not all_clean:
            print("Semantic Merge Rejected: Critical Logic Bugs Found.")
            return 1

        # If semantic checks passed, check if textual merge had conflicts
        if outcome == MergeOutcome.CONFLICT:
            print("Textual Merge Conflicts Exist.")
            return 1

        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base", help="Path to the common ancestor file")
    parser.add_argument("current", help="Path to the current file (Ours)")
    parser.add_argument("other", help="Path to the other file (Theirs)")

    args = parser.parse_args()

    backend_name = os.environ.get("SEMANTIC_MERGE_BACKEND", DEFAULT_BACKEND)
    if backend_name not in BACKENDS:
        print(
            f"Unknown SEMANTIC_MERGE_BACKEND={backend_name!r}; "
            f"expected one of {sorted(BACKENDS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    backend = BACKENDS[backend_name]()
    print(f"Using backend: {backend.name}", file=sys.stderr)

    enabled = load_enabled_strategies()
    driver = SemanticMergeDriver(backend=backend, strategies=enabled)
    exit_code = driver.run_merge(args.base, args.current, args.other)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
