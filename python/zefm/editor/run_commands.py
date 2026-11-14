"""Configurable, non-shell Run commands for saved editor buffers.

Commands are explicit argv arrays keyed by buffer mode. Only the exact
placeholders {file}, {name}, and {dir} expand; never use shell=True.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile

TIMEOUT = 30
MAX_OUTPUT = 100000
MAX_ARGV = 32
MAX_MODES = 40
PLACEHOLDERS = {"{file}", "{name}", "{dir}"}


def validate_argv(argv):
    if not isinstance(argv, list) or not 1 <= len(argv) <= MAX_ARGV:
        raise ValueError("Run command must be a JSON array of 1–32 arguments")
    if any(not isinstance(arg, str) or not arg or "\x00" in arg
           or len(arg) > 2048 for arg in argv):
        raise ValueError("Run command arguments must be nonempty strings")
    if any("{" in arg or "}" in arg for arg in argv
           if not any(token in arg for token in PLACEHOLDERS)):
        raise ValueError("Allowed placeholders are {file}, {name}, {dir}")
    # Disallow unsupported tokens even when a supported one is present.
    for arg in argv:
        remainder = arg
        for token in PLACEHOLDERS:
            remainder = remainder.replace(token, "")
        if "{" in remainder or "}" in remainder:
            raise ValueError("Allowed placeholders are {file}, {name}, {dir}")
    return list(argv)


class RunCommands:
    def __init__(self, path=None):
        self.path = (Path(path).expanduser() if path is not None
                     else Path.home() / ".config" / "zefm" / "run_commands.json")
        self.commands = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            entries = data.get("modes") if isinstance(data, dict) else None
            if isinstance(entries, dict):
                for mode, argv in list(entries.items())[:MAX_MODES]:
                    if isinstance(mode, str) and mode and len(mode) <= 60:
                        try:
                            self.commands[mode] = validate_argv(argv)
                        except ValueError:
                            continue
        except (OSError, ValueError, TypeError):
            pass

    def get(self, mode):
        argv = self.commands.get(mode)
        return list(argv) if argv is not None else None

    def set(self, mode, argv):
        if not isinstance(mode, str) or not mode or len(mode) > 60:
            raise ValueError("Invalid mode name")
        argv = validate_argv(argv)
        entries = dict(self.commands)
        if mode not in entries and len(entries) >= MAX_MODES:
            raise ValueError("Run command mode limit reached")
        entries[mode] = argv
        self._write(entries)
        self.commands = entries

    def clear(self, mode):
        if mode in self.commands:
            entries = dict(self.commands)
            del entries[mode]
            self._write(entries)
            self.commands = entries

    def _write(self, entries):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", prefix=".run-commands-",
                    suffix=".tmp", dir=self.path.parent, delete=False) as output:
                temporary = Path(output.name)
                if os.name == "posix":
                    os.fchmod(output.fileno(), 0o600)
                json.dump({"modes": entries}, output, ensure_ascii=False, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def expand_command(argv, source):
    source = Path(source).expanduser().resolve()
    values = {"{file}": str(source), "{name}": source.name,
              "{dir}": str(source.parent)}
    expanded = []
    for part in validate_argv(argv):
        for key, value in values.items():
            part = part.replace(key, value)
        expanded.append(part)
    return expanded


def execute_command(argv, source, *, timeout=TIMEOUT):
    """Run an explicitly user-configured process, with bounded diagnostics."""
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise ValueError("Save an existing file before running a command")
    command = expand_command(argv, source)
    try:
        proc = subprocess.run(command, cwd=str(source.parent),
                              capture_output=True, text=True, errors="replace",
                              stdin=subprocess.DEVNULL, timeout=timeout,
                              check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None,
                "log": f"Command timed out after {timeout} seconds"}
    except OSError as exc:
        return {"ok": False, "returncode": None,
                "log": f"Could not launch command: {exc}"}
    return {"ok": proc.returncode == 0, "returncode": proc.returncode,
            "log": ((proc.stdout or "") + "\n" + (proc.stderr or ""))[-MAX_OUTPUT:]}
