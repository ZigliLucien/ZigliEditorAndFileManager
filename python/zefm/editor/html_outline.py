"""HTML syntax spans and heading offsets for the desktop editor."""
from html.parser import HTMLParser
import re

from .markdown_outline import MarkdownHeading

_ATTR = re.compile(r"""[^\s=<>/]+(?=\s*=)|"[^"]*"|'[^']*'|(?<==)[^\s>"']+""")
_HEADING = re.compile(r"h[1-6]$")


class _Scanner(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.text = text
        self.lines = [0] + [m.end() for m in re.finditer("\n", text)]
        self.spans = []
        self.headings = []
        self.heading = None
        self.parts = []
        self.hidden = None

    def _source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def mark(self, length, style):
        start = self._source_offset()
        self.spans.append((start, min(start + length, len(self.text)), style))

    def finish_heading(self):
        if self.heading is not None:
            start, level = self.heading
            title = " ".join("".join(self.parts).split())
            self.headings.append(MarkdownHeading(start, level, title))
        self.heading = None
        self.parts = []

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        start = self._source_offset()
        self.mark(len(raw), "command")
        name_end = re.match(r"<[^\s/>]+", raw)
        if name_end:
            for match in _ATTR.finditer(raw, name_end.end()):
                token = match.group()
                style = "string" if token.startswith(("'", '"')) or raw[match.start()-1] == "=" else "keyword"
                self.spans.append((start + match.start(), start + match.end(), style))
        if self.hidden:
            return
        if tag in ("script", "style", "pre", "code", "textarea", "template"):
            self.hidden = tag
        elif _HEADING.fullmatch(tag):
            self.finish_heading()
            self.heading = (start, int(tag[1]))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.hidden == tag:
            self.hidden = None

    def handle_endtag(self, tag):
        start = self._source_offset()
        end = self.text.find(">", start)
        if end >= 0:
            self.mark(end - start + 1, "command")
        if self.hidden:
            if tag == self.hidden:
                self.hidden = None
            return
        if self.heading and tag == "h" + str(self.heading[1]):
            self.finish_heading()

    def handle_data(self, data):
        if self.heading and not self.hidden:
            self.parts.append(data)

    def handle_comment(self, data):
        self.mark(len(data) + 7, "comment")

    def handle_decl(self, decl):
        self.mark(len(decl) + 3, "keyword")


def html_scan(text):
    scanner = _Scanner(text)
    try:
        scanner.feed(text)
        scanner.close()
    except (ValueError, AssertionError):
        pass
    scanner.finish_heading()
    return scanner.headings, scanner.spans


def html_outline(text):
    return html_scan(text)[0]
