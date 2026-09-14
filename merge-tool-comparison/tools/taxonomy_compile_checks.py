"""Single-file javac compile checks (ISSUES #30, S1, protocol §5).

For every *scored* file (both strata) compiles the Mergiraf-merged content and
the developer-resolution content in a pinned ``eclipse-temurin:17-jdk`` image
(``--platform linux/amd64``, Docker-only per CLAUDE.md; javac is a checker
here, not a merge tool). No project classpath — single-file compilation — so
RESOLVE errors ("cannot find symbol", "package does not exist") are expected
noise; only the merged-minus-dev delta (computed at assembly time, matching
ignoring line numbers) reaches the prompt. Diagnostics are classified
PARSE / RESOLVE / OTHER and written to ``reports_taxonomy/compile_checks.json``.

Batched: each chunk of scenarios is compiled in ONE container (the JVM/QEMU
startup dominates), results flushed per chunk -> resumable after a crash or
timeout. Each file is placed in its own directory under its real basename so a
``public`` class name matches its filename (no spurious naming errors) and
files never collide across units.

    .venv/bin/python tools/taxonomy_compile_checks.py
Env: CHUNK (scenarios per container, default 60), CHUNK_TIMEOUT (s, default 2400).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import taxonomy_common as tc  # noqa: E402
from src.core.docker_runner import run_in_docker  # noqa: E402

IMAGE = "eclipse-temurin:17-jdk"
OUT = ROOT / "reports_taxonomy/compile_checks.json"
CHUNK = int(os.environ.get("CHUNK", "60"))
CHUNK_TIMEOUT = int(os.environ.get("CHUNK_TIMEOUT", "2400"))

_ERR_RE = re.compile(r"^(?P<path>.*\.java):(?:(?P<line>\d+):)?\s*error:\s*(?P<msg>.*)$")
_PARSE_HINTS = ("expected", "illegal", "reached end of file while parsing",
                "not a statement", "unclosed", "malformed", "premature end",
                "class, interface, enum, or record expected", "<identifier>")
_RESOLVE_HINTS = ("cannot find symbol", "does not exist", "cannot access",
                  "package ", "symbol not found")


def classify(msg: str) -> str:
    m = msg.lower()
    if any(h in m for h in _PARSE_HINTS):
        return "PARSE"
    if any(h in m for h in _RESOLVE_HINTS):
        return "RESOLVE"
    return "OTHER"


def parse_errors(stderr_text: str) -> list[dict]:
    errs = []
    for line in stderr_text.splitlines():
        m = _ERR_RE.match(line.strip())
        if not m:
            continue
        msg = m.group("msg").strip()
        errs.append({"class": classify(msg), "msg": msg,
                     "line": int(m.group("line")) if m.group("line") else None})
    return errs


def _basename(file_path: str) -> str:
    b = file_path.rsplit("/", 1)[-1]
    return b if b.endswith(".java") else b + ".java"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = json.loads(OUT.read_text()) if OUT.exists() else {}

    units = tc.scored_units()
    # (scenario_id, stratum, file_path, side, content) for every scored file
    pending = []
    seen = set()
    for u in units:
        for e in u["scored"]:
            s = e["scenario"]
            sid = s["scenario_id"]
            if sid in seen:
                continue
            seen.add(sid)
            done = results.get(sid)
            if done and "merged" in done and "dev" in done:
                continue
            pending.append((sid, u["stratum"], s["file_path"],
                            e["merged"], s["developer_resolution"]))

    total_scored = len(seen)
    print(f"compile_checks: {total_scored} scored files, {total_scored - len(pending)} "
          f"already done, {len(pending)} pending, chunk={CHUNK} image={IMAGE}", flush=True)

    for start in range(0, len(pending), CHUNK):
        chunk = pending[start:start + CHUNK]
        tmp = Path(tempfile.mkdtemp(prefix="taxcc_"))
        try:
            index = {}          # dir-key -> (sid, side)
            for n, (sid, _stratum, fpath, merged, dev) in enumerate(chunk):
                base = _basename(fpath)
                for side, content in (("merged", merged), ("dev", dev)):
                    d = tmp / f"{n}_{side}"
                    d.mkdir(parents=True, exist_ok=True)
                    (d / base).write_text(content, encoding="utf-8", errors="replace")
                    index[f"{n}_{side}"] = (sid, side)
            script = (
                "set -u\n"
                'for d in /workspace/*/; do\n'
                '  f="$(ls "$d"*.java 2>/dev/null | head -1)"\n'
                '  [ -z "$f" ] && continue\n'
                '  javac -encoding UTF-8 -nowarn -d /tmp/out "$f" 2> "$d/diag.err"\n'
                '  echo $? > "$d/diag.rc"\n'
                "done\n"
            )
            (tmp / "run.sh").write_text(script)
            res = run_in_docker(IMAGE, ["sh", "/workspace/run.sh"], str(tmp), timeout=CHUNK_TIMEOUT)
            if res.timed_out:
                print(f"  chunk {start//CHUNK} TIMED OUT after {CHUNK_TIMEOUT}s "
                      f"(reducing CHUNK and rerunning will resume)", flush=True)
                # salvage whatever diagnostics were written before the kill
            for key, (sid, side) in index.items():
                d = tmp / key
                err_f, rc_f = d / "diag.err", d / "diag.rc"
                if not rc_f.exists():
                    continue  # not reached before timeout -> leave for a resume
                stderr_text = err_f.read_text() if err_f.exists() else ""
                entry = results.setdefault(sid, {"stratum": next(
                    c[1] for c in chunk if c[0] == sid), "file_path": next(
                    c[2] for c in chunk if c[0] == sid)})
                entry[side] = {"rc": int(rc_f.read_text().strip() or "-1"),
                               "errors": parse_errors(stderr_text)}
            OUT.write_text(json.dumps(results, indent=2))
            done_files = sum(1 for v in results.values() if "merged" in v and "dev" in v)
            print(f"  chunk {start//CHUNK}: +{len(chunk)} scenarios, "
                  f"{done_files}/{total_scored} complete ({res.runtime_seconds:.0f}s)", flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # summary
    complete = [v for v in results.values() if "merged" in v and "dev" in v]
    delta_hits = 0
    for sid, v in results.items():
        if "merged" not in v or "dev" not in v:
            continue
        d = tc.compile_delta(sid, results)
        if d != "(none)":
            delta_hits += 1
    print(f"DONE compile_checks: {len(complete)}/{total_scored} files complete; "
          f"{delta_hits} have a non-empty merged-minus-dev delta", flush=True)


if __name__ == "__main__":
    main()
