"""One-off external commands from the editor's legacy Shell menu.

A quoted command line is parsed into argv (never passed to a shell).
Pipes, redirects and other shell syntax are intentionally not interpreted.
"""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from .run_commands import MAX_OUTPUT, TIMEOUT, MAX_ARGV

MAX_COMMAND_LENGTH = 4096


def parse_shell_command(line: str) -> list[str]:
    if not isinstance(line, str) or not line.strip() or len(line) > MAX_COMMAND_LENGTH:
        raise ValueError("Enter a command of 1–4096 characters")
    if "\x00" in line or "\n" in line or "\r" in line:
        raise ValueError("Command may not contain NUL or newline characters")
    try:
        argv = shlex.split(line, posix=True)
    except ValueError as exc:
        raise ValueError(f"Invalid quoting: {exc}") from exc
    if not 1 <= len(argv) <= MAX_ARGV or any(not item or len(item) > 2048 for item in argv):
        raise ValueError("Command must have 1–32 nonempty arguments")
    # Avoid giving users the impression that pipelines or redirects work.
    operators = {"|", "||", "&&", ";", ">", ">>", "<", "<<", "&"}
    if any(item in operators for item in argv):
        raise ValueError("Pipes and redirects are not supported; use a script or configured Run command")
    return argv


def run_shell_command(argv: list[str], cwd: Path, *, timeout=TIMEOUT) -> dict:
    if not isinstance(argv, list) or not argv or len(argv) > MAX_ARGV:
        raise ValueError("Invalid command arguments")
    if any(not isinstance(arg, str) or not arg or "\x00" in arg for arg in argv):
        raise ValueError("Invalid command argument")
    directory = Path(cwd).expanduser().resolve()
    if not directory.is_dir():
        raise ValueError("Working directory does not exist")
    try:
        proc = subprocess.run(argv, cwd=str(directory), capture_output=True,
                              text=True, errors="replace", stdin=subprocess.DEVNULL,
                              timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None,
                "log": f"Command timed out after {timeout} seconds"}
    except OSError as exc:
        return {"ok": False, "returncode": None,
                "log": f"Could not launch command: {exc}"}
    return {"ok": proc.returncode == 0, "returncode": proc.returncode,
            "log": ((proc.stdout or "") + "\n" + (proc.stderr or ""))[-MAX_OUTPUT:]}
