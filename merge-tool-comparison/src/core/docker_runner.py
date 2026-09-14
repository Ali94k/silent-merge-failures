import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DockerResult:
    return_code: int
    stdout: str
    stderr: str
    runtime_seconds: float
    timed_out: bool


def run_in_docker(
    image: str,
    cmd: list[str],
    workspace_dir: str,
    timeout: int = 60,
) -> DockerResult:
    """
    Run a command inside a Docker container with /workspace mounted.

    Args:
        image: Docker image name.
        cmd: Command and arguments to run inside the container.
        workspace_dir: Host directory to bind-mount at /workspace.
        timeout: Max seconds before killing the container.

    Returns:
        DockerResult with return code, output, and timing.
    """
    docker_cmd = [
        "docker", "run", "--rm",
        "--platform", "linux/amd64",
        "-v", f"{Path(workspace_dir).resolve()}:/workspace",
        image,
    ] + cmd

    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - start
        return DockerResult(
            return_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            runtime_seconds=elapsed,
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return DockerResult(
            return_code=-1,
            stdout="",
            stderr=f"Docker command timed out after {timeout}s",
            runtime_seconds=elapsed,
            timed_out=True,
        )


def run_native(
    cmd: list[str],
    cwd: Optional[str] = None,
    timeout: int = 60,
) -> DockerResult:
    """
    Run a command natively (no Docker).

    Returns:
        DockerResult with return code, output, and timing.
    """
    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        elapsed = time.monotonic() - start
        return DockerResult(
            return_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            runtime_seconds=elapsed,
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return DockerResult(
            return_code=-1,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            runtime_seconds=elapsed,
            timed_out=True,
        )


def write_workspace_files(
    workspace: Path,
    base: str,
    ours: str,
    theirs: str,
) -> tuple[Path, Path, Path]:
    """Write base/ours/theirs content to workspace directory. Returns file paths."""
    base_path = workspace / "base.java"
    ours_path = workspace / "ours.java"
    theirs_path = workspace / "theirs.java"
    base_path.write_text(base)
    ours_path.write_text(ours)
    theirs_path.write_text(theirs)
    return base_path, ours_path, theirs_path
