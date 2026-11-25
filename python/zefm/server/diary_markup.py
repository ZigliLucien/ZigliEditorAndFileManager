"""Safe Markdown and limited HTML for diary entries; no script/style execution."""
from __future__ import annotations
from html import escape
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit

ALLOWED = {"p","div","span","br","hr","strong","b","em","i","u","del","s",
           "code","pre","blockquote","ul","ol","li","h1","h2","h3","h4",
           "h5","h6","a","table","thead","tbody","tr","th","td","mark",
           "small","sub","sup"}
VOID = {"br","hr"}
HIDDEN = {"script","style","iframe","svg","math","template","object"}
RAW_TAG = re.compile(r"(<[^>]*>)")
LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
INLINE = re.compile(r"(\*\*[^*\n]+\*\*|__[^_\n]+__|\x60[^\x60\n]+\x60|\*[^*\n]+\*|_[^_\n]+_|~~[^~\n]+~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
BULLET = re.compile(r"^\s*[-*+]\s+(.+)$")
NUMBER = re.compile(r"^\s*\d+[.)]\s+(.+)$")


def safe_url(url):
    if not url or any(c.isspace() or ord(c) < 32 for c in url):
        return None
    if url.startswith("#") and not url.startswith("##"):
        return url
    parsed = urlsplit(url)
    if parsed.scheme.lower() in ("http", "https") and parsed.netloc:
        return url
    if parsed.scheme.lower() == "mailto" and parsed.path:
        return url
    return None


class SafeHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self.open_tags = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if self.hidden:
            if tag in HIDDEN:
                self.hidden += 1
            return
        if tag in HIDDEN:
            self.hidden = 1
            return
        if tag not in ALLOWED:
            return
        attributes = ""
        if tag == "a":
            destination = next((v for k, v in attrs if k == "href"), None)
            checked = safe_url(destination)
            if checked:
                attributes = ' href="' + escape(checked, quote=True) + '" rel="noopener noreferrer"'
        self.output.append("<" + tag + attributes + ">")
        if tag not in VOID:
            self.open_tags.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.hidden:
            if tag in HIDDEN:
                self.hidden -= 1
            return
        if tag in self.open_tags:
            while self.open_tags:
                name = self.open_tags.pop()
                self.output.append("</" + name + ">")
                if name == tag:
                    break

    def handle_data(self, value):
        if not self.hidden:
            self.output.append(escape(value))

    def finish(self):
        while self.open_tags:
            self.output.append("</" + self.open_tags.pop() + ">")
        return "".join(self.output)


def inline_markup(source):
    pieces = []
    for segment in RAW_TAG.split(source):
        if segment.startswith("<") and segment.endswith(">"):
            pieces.append(segment)  # Sanitize after parsing.
            continue
        parts = []
        offset = 0
        for match in LINK.finditer(segment):
            parts.append(escape(segment[offset:match.start()]))
            url = safe_url(match.group(2))
            if url:
                parts.append('<a href="' + escape(url, quote=True) + '">'
                             + escape(match.group(1)) + '</a>')
            else:
                parts.append(escape(match.group(0)))
            offset = match.end()
        parts.append(escape(segment[offset:]))
        def replace_inline(match):
            item = match.group(0)
            if item.startswith(("**", "__")):
                return "<strong>" + item[2:-2] + "</strong>"
            if item.startswith("~~"):
                return "<del>" + item[2:-2] + "</del>"
            if item.startswith(chr(96)):
                return "<code>" + item[1:-1] + "</code>"
            return "<em>" + item[1:-1] + "</em>"
        pieces.append(INLINE.sub(replace_inline, "".join(parts)))
    return "".join(pieces)


def basic_markdown(source):
    result = []
    active_list = None
    fenced = False
    for line in source.splitlines():
        if line.strip().startswith(chr(96) * 3):
            if active_list:
                result.append("</" + active_list + ">")
                active_list = None
            fenced = not fenced
            result.append("<pre><code>" if fenced else "</code></pre>")
            continue
        if fenced:
            result.append(escape(line) + "\n")
            continue
        heading = HEADING.match(line)
        bullet = BULLET.match(line)
        number = NUMBER.match(line)
        desired = "ul" if bullet else "ol" if number else None
        if active_list and desired != active_list:
            result.append("</" + active_list + ">")
            active_list = None
        if desired:
            if not active_list:
                result.append("<" + desired + ">")
                active_list = desired
            result.append("<li>" + inline_markup((bullet or number).group(1)) + "</li>")
        elif heading:
            level = len(heading.group(1))
            result.append(f"<h{level}>" + inline_markup(heading.group(2)) + f"</h{level}>")
        elif not line.strip():
            continue
        elif line.startswith("> "):
            result.append("<blockquote>" + inline_markup(line[2:]) + "</blockquote>")
        elif line.lstrip().startswith("<"):
            result.append(line)
        else:
            result.append("<p>" + inline_markup(line) + "</p>")
    if active_list:
        result.append("</" + active_list + ">")
    if fenced:
        result.append("</code></pre>")
    return "\n".join(result)


def render_diary(source):
    """Render Markdown, sanitize every resulting HTML node and attribute."""
    try:
        import markdown  # optional, more complete Markdown syntax
    except ImportError:
        rendered = basic_markdown(source)
    else:
        rendered = markdown.markdown(source, extensions=["extra", "sane_lists"])
    sanitizer = SafeHTML()
    sanitizer.feed(rendered)
    sanitizer.close()
    return '<div class="zefm-diary-markup">' + sanitizer.finish() + '</div>'
