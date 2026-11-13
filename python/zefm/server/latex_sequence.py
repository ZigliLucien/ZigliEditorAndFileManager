"""Bounded LuaLaTeX/BibTeX/Biber sequence shared by browser and desktop.

Only run on trusted TeX sources. The caller owns an isolated build directory.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import time

LATEX_PASSES = 2
MAX_LATEX_PASSES = 3
MAX_LOG = 100000


def bibliography_tool(work: Path, stem: str) -> str | None:
    """Detect bibliography processing from compiler-generated metadata."""
    if (work / (stem + ".bcf")).is_file():
        return "biber"
    aux = work / (stem + ".aux")
    if aux.is_file():
        # BibTeX requires a bibliography declaration; do not run merely
        # because an aux file exists for labels or cross-references.
        if b"\\bibdata{" in aux.read_bytes()[:2_000_000]:
            return "bibtex"
    return None


def _bibliography_argv(tool: str, directory: Path, stem: str):
    binary = shutil.which(tool)
    if not binary:
        raise RuntimeError(
            f"{tool} is needed for this document but is not installed or on PATH")
    if tool == "biber":
        return [binary, "--input-directory", str(directory),
                "--output-directory", str(directory), stem]
    return [binary, stem]


def run_tex_sequence(command: list[str], source: Path, directory: Path,
                     *, timeout: int = 45, passes: int = LATEX_PASSES):
    """Run an isolated TeX sequence; return (returncode, combined_log, elapsed).

    `command` is the existing secured LuaLaTeX argv, including no-shell-escape
    and a fresh output directory. Compile twice for references, or three times
    when bibliography processing is needed. Do not publish failed PDFs.
    """
    if not 1 <= passes <= MAX_LATEX_PASSES:
        raise ValueError("Invalid LuaLaTeX pass count")
    started = time.monotonic()
    logs = []
    # Child programs read/write files in the build directory, while TeX
    # source-relative includes continue resolving in the source's directory.
    env = os.environ.copy()
    for variable in ("BIBINPUTS", "BSTINPUTS"):
        env[variable] = str(source.parent) + os.pathsep + env.get(variable, "")
    def run(argv, cwd, label):
        try:
            proc = subprocess.run(argv, cwd=str(cwd), env=env,
                                  capture_output=True, text=True, errors="replace",
                                  timeout=timeout, check=False, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"{label} timed out after {timeout} seconds") from exc
        except OSError as exc:
            raise RuntimeError(f"Could not launch {label}: {exc}") from exc
        logs.append(f"=== {label} (exit {proc.returncode}) ===\n"
                    + (proc.stdout or "") + "\n" + (proc.stderr or ""))
        return proc.returncode

    rc = run(command, source.parent, "LuaLaTeX pass 1")
    if rc:
        return rc, "\n".join(logs)[-MAX_LOG:], round(time.monotonic()-started, 2)
    tool = bibliography_tool(directory, source.stem)
    extra = 0
    if tool:
        try:
            argv = _bibliography_argv(tool, directory, source.stem)
        except RuntimeError as exc:
            return 127, ("\n".join(logs) + "\n" + str(exc))[-MAX_LOG:], round(time.monotonic()-started, 2)
        rc = run(argv, directory if tool == "bibtex" else source.parent, tool)
        if rc:
            return rc, "\n".join(logs)[-MAX_LOG:], round(time.monotonic()-started, 2)
        extra = 1
    for n in range(2, passes + extra + 1):
        rc = run(command, source.parent, f"LuaLaTeX pass {n}")
        if rc:
            return rc, "\n".join(logs)[-MAX_LOG:], round(time.monotonic()-started, 2)
    return 0, "\n".join(logs)[-MAX_LOG:], round(time.monotonic()-started, 2)
