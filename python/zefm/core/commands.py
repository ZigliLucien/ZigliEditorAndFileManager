"""Process 02: safe external command execution (local trusted caller only)."""
from dataclasses import dataclass
import subprocess

@dataclass(frozen=True)
class Result:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

class CommandError(RuntimeError):
    pass

def run(argv, *, timeout=30, cwd=None):
    if not isinstance(argv, (list, tuple)) or not argv or not all(isinstance(x, str) and x for x in argv):
        raise ValueError("argv must be a nonempty list/tuple of nonempty strings")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout,
                           shell=False, check=False)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise CommandError(f"Could not run {argv[0]!r}: {e}") from e
    return Result(tuple(argv), p.returncode, p.stdout, p.stderr)
