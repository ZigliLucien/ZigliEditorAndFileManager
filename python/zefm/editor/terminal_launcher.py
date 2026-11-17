"""Open an interactive terminal from the editor without a shell command string.

Linux uses xterm. macOS asks Terminal.app to open a new session in the
active file's directory. No editor document is read, written or saved.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys


def terminal_argv(directory, *, platform=None, executable=None):
    """Return a safe argv array for launching a terminal in directory."""
    directory = Path(directory).expanduser().resolve()
    if not directory.is_dir():
        raise ValueError("Terminal working directory does not exist")
    platform = sys.platform if platform is None else platform
    if platform == "darwin":
        script = "cd " + shlex.quote(str(directory))
        # Escape an AppleScript string, not a shell command. POSIX quoting
        # above protects the path when Terminal executes the cd command.
        escaped = script.replace("\\", "\\\\").replace('"', '\\"')
        return [
            executable or "/usr/bin/osascript",
            "-e", 'tell application "Terminal" to activate',
            "-e", 'tell application "Terminal" to do script "' + escaped + '"',
        ]
    if platform.startswith("linux"):
        xterm = executable or shutil.which("xterm")
        if not xterm:
            raise ValueError("xterm is not installed or is not on PATH")
        shell = os.environ.get("SHELL") or "/bin/sh"
        if not Path(shell).is_file():
            shell = "/bin/sh"
        return [xterm, "-e", shell, "-i"]
    raise ValueError("Interactive terminal launch is supported on Linux and macOS")


def open_terminal(directory, *, platform=None, executable=None):
    directory = Path(directory).expanduser().resolve()
    argv = terminal_argv(directory, platform=platform, executable=executable)
    return subprocess.Popen(
        argv, cwd=str(directory), stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
