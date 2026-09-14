"""GitMergeFileBackend — three-way merge via `git merge-file`.

Wraps the inline subprocess call that previously lived at
core/driver.py:27-30. `git merge-file` is universally available (git is
a hard dependency of the driver itself), so no Docker or install layer
is needed for this backend.

Exit-code semantics (per git-merge-file(1)):
    0         = clean merge (no conflicts)
    1-127     = number of conflicts emitted (CONFLICT)
    128+      = fatal git error (e.g., unreadable input) -> CRASH
    negative  = killed by signal -> CRASH
"""
import subprocess
import sys

from core.backends.base import MergeBackend, MergeOutcome


class GitMergeFileBackend(MergeBackend):
    @property
    def name(self) -> str:
        return "git"

    def merge(
        self, base_path: str, ours_path: str, theirs_path: str
    ) -> MergeOutcome:
        try:
            proc = subprocess.run(
                ["git", "merge-file", ours_path, base_path, theirs_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
            print(
                f"GitMergeFileBackend: subprocess error: {e}\n"
                f"  Hint: ensure git is installed and on PATH.",
                file=sys.stderr,
            )
            return MergeOutcome.CRASH

        rc = proc.returncode
        if rc == 0:
            return MergeOutcome.CLEAN
        if 1 <= rc <= 127:
            return MergeOutcome.CONFLICT
        print(
            f"GitMergeFileBackend: git merge-file exited with returncode {rc}.\n"
            f"  stderr: {proc.stderr.strip() or '(empty)'}",
            file=sys.stderr,
        )
        return MergeOutcome.CRASH
