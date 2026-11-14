"""Locate source positions in LuaLaTeX logs without interpreting TeX input.

Supports file:line: diagnostics and TeX's traditional exclamation / l.N
messages. Paths are checked by the caller before opening in the editor.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

_FILE_LINE = re.compile(r"(?P<path>(?:[A-Za-z]:)?[^\s():]+\.tex):(?P<line>\d+):\s*(?P<message>.*)")
_TEX_LINE = re.compile(r"^\s*l\.(\d+)\s")
_ERROR = re.compile(r"^!\s*(.+)")
_FILE_OPEN = re.compile(r"\((?P<path>(?:\./|\.\./|/)?[^()\s]+\.tex)(?=\s|$|\(|\))")


@dataclass(frozen=True)
class LatexDiagnostic:
    path: Path
    line: int
    message: str
    log_line: int


def parse_latex_errors(log: str, master: Path) -> list[LatexDiagnostic]:
    """Return positions for errors with a reported source line number."""
    master = Path(master).expanduser().resolve()
    errors: list[LatexDiagnostic] = []
    current = master
    pending: tuple[str, int, Path] | None = None
    lines = log.splitlines()
    for index, text in enumerate(lines, start=1):
        if text.startswith("=== LuaLaTeX pass"):
            current = master
            pending = None
        match = _FILE_OPEN.search(text)
        if match:
            file = Path(match.group("path"))
            current = (file if file.is_absolute() else master.parent / file).resolve()
        direct = _FILE_LINE.search(text)
        if direct:
            raw = Path(direct.group("path"))
            path = (raw if raw.is_absolute() else master.parent / raw).resolve()
            line = int(direct.group("line"))
            if line > 0:
                errors.append(LatexDiagnostic(path, line, direct.group("message"),
                                              index))
            pending = None
            continue
        error = _ERROR.match(text)
        if error:
            pending = (error.group(1).strip(), index, current)
            continue
        line_match = _TEX_LINE.match(text)
        if pending is not None and line_match:
            number = int(line_match.group(1))
            if number > 0:
                message, log_line, source = pending
                errors.append(LatexDiagnostic(source, number, message, log_line))
            pending = None
        if pending and index - pending[1] > 8:
            pending = None
    return errors
