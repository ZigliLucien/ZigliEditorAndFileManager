"""Small LaTeX section-outline extractor for the Tk editor.

Uses ZEFM's existing verbatim-aware lexer so headings written in comments,
verbatim examples and escaped backslash sequences are not navigation targets.
This is an outline of the current buffer, not a TeX macro-expansion engine.
"""
from dataclasses import dataclass
import re

from .syntax_highlight import MAX_CHARS, latex_scan


LEVELS = {
    "part": 0,
    "chapter": 1,
    "section": 2,
    "subsection": 3,
    "subsubsection": 4,
    "paragraph": 5,
    "subparagraph": 6,
}
_SECTION = re.compile(
    r"\\(part|chapter|section|subsection|subsubsection|paragraph|subparagraph)(\*)?"
)


@dataclass(frozen=True)
class OutlineHeading:
    offset: int
    level: int
    kind: str
    title: str
    starred: bool = False


def _group_end(text, start, opening, closing):
    """Return index after a balanced TeX group, or None for incomplete input.

    Skips escaped characters, TeX comment bodies and nested groups.  The
    bracket variant is used only for an optional short title.
    """
    if start >= len(text) or text[start] != opening:
        return None
    depth = 0
    i = start
    while i < len(text):
        char = text[i]
        if char == "\\":
            i += 2
            continue
        if char == "%":
            newline = text.find("\n", i)
            if newline < 0:
                return None
            i = newline + 1
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return None


def latex_outline(text):
    """Return headings in source order, using character offsets.

    Recognizes starred and unstarred part/chapter/section/subsection/etc.,
    including optional short titles and nested braces in the long title.
    """
    if not isinstance(text, str) or len(text) > MAX_CHARS:
        return []
    spans, _brackets = latex_scan(text)
    command_positions = {start for start, _end, style in spans
                         if style == "command"}
    headings = []
    for match in _SECTION.finditer(text):
        if match.start() not in command_positions:
            continue
        kind, starred = match.group(1), bool(match.group(2))
        i = match.end()
        while i < len(text) and text[i].isspace():
            i += 1
        if i < len(text) and text[i] == "[":
            short_end = _group_end(text, i, "[", "]")
            if short_end is None:
                continue
            i = short_end
            while i < len(text) and text[i].isspace():
                i += 1
        if i >= len(text) or text[i] != "{":
            continue
        end = _group_end(text, i, "{", "}")
        if end is None:
            continue
        title = " ".join(text[i + 1:end - 1].split())
        if not title:
            title = "(untitled)"
        headings.append(OutlineHeading(
            offset=match.start(), level=LEVELS[kind], kind=kind,
            title=title, starred=starred))
    return headings
