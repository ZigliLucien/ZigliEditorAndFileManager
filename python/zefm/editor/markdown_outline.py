"""Lightweight Markdown heading and syntax scanner for editor navigation."""
from dataclasses import dataclass
import re

_ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+|$)(.*)$")
_SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
_FENCE = re.compile(r"^ {0,3}(\x60{3,}|~{3,})(.*)$")
_INLINE = re.compile(
    r"(?P<verbatim>\x60+[^\x60\n]+\x60+)"
    r"|(?P<command>!?\[[^\]\n]+\]\([^)\n]+\))"
    r"|(?P<keyword>\*\*[^*\n]+\*\*|__[^_\n]+__)"
    r"|(?P<string>\*[^*\n]+\*|(?<!\w)_[^_\n]+_(?!\w))"
    r"|(?P<math>(?<!\\)\${1,2}[^$\n]+\${1,2})"
)
_PREFIX = re.compile(r"^ {0,3}(?:>+|[-+*][ \t]+|\d+[.)][ \t]+)")


@dataclass(frozen=True)
class MarkdownHeading:
    offset: int
    level: int
    title: str

    @property
    def kind(self):
        return "H" + str(self.level)

    starred = False


def markdown_scan(text):
    """Return headings and color spans; exclude fenced and indented code."""
    headings, spans = [], []
    offset = 0
    fence = None
    previous = None
    for raw in text.splitlines(keepends=True):
        line = raw.rstrip("\r\n")
        start = offset
        offset += len(raw)
        marker = _FENCE.match(line)
        if fence:
            spans.append((start, offset, "verbatim"))
            if (marker and marker[1][0] == fence[0]
                    and len(marker[1]) >= len(fence) and not marker[2].strip()):
                fence = None
            previous = None
            continue
        if marker:
            fence = marker[1]
            spans.append((start, offset, "verbatim"))
            previous = None
            continue
        if line.startswith(("    ", "\t")):
            spans.append((start, offset, "verbatim"))
            previous = None
            continue
        heading = _ATX.match(line)
        underline = _SETEXT.match(line)
        prefix = _PREFIX.match(line)
        if heading:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading[2]).strip()
            headings.append(MarkdownHeading(start, len(heading[1]), title))
            spans.append((start, start + len(line), "heading"))
            previous = None
            continue
        if underline and previous:
            old_start, title = previous
            headings.append(MarkdownHeading(old_start, 1 if underline[1][0] == "=" else 2, title))
            spans.append((old_start, start + len(line), "heading"))
            previous = None
            continue
        if prefix:
            spans.append((start, start + prefix.end(), "command"))
        for match in _INLINE.finditer(line):
            spans.append((start + match.start(), start + match.end(), match.lastgroup))
        previous = ((start, line.strip()) if line.strip() and not prefix
                    and not underline else None)
    return headings, spans


def markdown_outline(text):
    return markdown_scan(text)[0]


def adjacent_heading(text, cursor, direction):
    """Find the next/previous heading strictly beyond the current offset."""
    headings = markdown_outline(text)
    if direction == "next":
        return next((h for h in headings if h.offset > cursor), None)
    if direction == "previous":
        return next((h for h in reversed(headings) if h.offset < cursor), None)
    raise ValueError("Unknown heading direction")
