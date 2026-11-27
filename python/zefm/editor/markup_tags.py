"""Source-level HTML/XML tag matching, without parsing external entities."""
import re

MAX_CHARS = 250_000
_NAME = re.compile(r"([^\W\d]|:)[\w.:\-]*", re.UNICODE)
_VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())
_RAW = frozenset(("script", "style", "textarea", "title"))
_OPTIONAL = frozenset("html head body li dt dd p rt rp optgroup option colgroup thead tbody tfoot tr td th".split())
_P_BREAK = frozenset("address article aside blockquote div dl fieldset footer form h1 h2 h3 h4 h5 h6 header hgroup hr main menu nav ol p pre section table ul".split())


def _end(text, start, declaration=False):
    """Find an unquoted >; respect an XML declaration's internal subset."""
    quote = None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if quote:
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
        elif declaration and ch == "[":
            depth += 1
        elif declaration and ch == "]":
            depth = max(0, depth - 1)
        elif ch == ">" and not depth:
            return i + 1
        elif ch == "<" and not declaration:
            return None
    return None


def scan_tags(text, mode):
    """Return (span, name, kind) tokens and syntax spans; tolerate edits."""
    if len(text) > MAX_CHARS or mode not in ("html", "xml"):
        return [], []
    html = mode == "html"
    tokens, colors = [], []
    pos = 0
    while pos < len(text):
        start = text.find("<", pos)
        if start < 0:
            break
        special = next(((prefix, close, style) for prefix, close, style in (
            ("<!--", "-->", "comment"), ("<![CDATA[", "]]>", "verbatim"),
            ("<?", "?>", "keyword")) if text.startswith(prefix, start)), None)
        if special:
            prefix, close, style = special
            found = text.find(close, start + len(prefix))
            pos = len(text) if found < 0 else found + len(close)
            colors.append((start, pos, style))
            continue
        if text.startswith("<!", start):
            pos = _end(text, start + 2, declaration=True) or len(text)
            colors.append((start, pos, "keyword"))
            continue
        closing = text.startswith("</", start)
        name_start = start + (2 if closing else 1)
        match = _NAME.match(text, name_start)
        if not match:
            pos = start + 1
            continue
        end = _end(text, match.end())
        if end is None:
            pos = match.end()
            continue
        name = match.group()
        if html:
            name = name.lower()
        raw = text[start:end]
        kind = "close" if closing else "single" if raw[:-1].rstrip().endswith("/") or (html and name in _VOID) else "open"
        tokens.append(((start, end), name, kind))
        colors.append((start, end, "command"))
        if not closing:
            for attr in re.finditer(r"""(?P<string>"[^"]*"|'[^']*')|(?P<keyword>[^\s=<>/"']+)(?=\s*=)""", text[match.end():end-1]):
                colors.append((match.end()+attr.start(), match.end()+attr.end(), attr.lastgroup))
        pos = end
        if html and kind == "open" and name in _RAW:
            close = re.search(r"</" + re.escape(name) + r"\s*>", text[pos:], re.I)
            pos = pos + close.start() if close else len(text)
    return tokens, colors


def _implicit_close(open_name, next_name):
    if open_name == "p":
        return next_name in _P_BREAK
    if open_name in ("dt", "dd"):
        return next_name in ("dt", "dd")
    if open_name in ("td", "th"):
        return next_name in ("td", "th", "tr")
    if open_name in ("thead", "tbody", "tfoot"):
        return next_name in ("thead", "tbody", "tfoot")
    if open_name in ("li", "option", "tr", "optgroup", "rt", "rp"):
        return open_name == next_name
    return False


def matching_tag(text, cursor, mode):
    """Return (source span, partner span or None); ignore singleton tags.

    XML matching is case-sensitive. HTML recognizes void elements and some
    commonly omitted end tags. This is not a full HTML5 conformance checker.
    """
    tokens, _ = scan_tags(text, mode)
    stack, pairs = [], {}
    html = mode == "html"
    for span, name, kind in tokens:
        if kind == "single":
            continue
        if kind == "open":
            while html and stack and _implicit_close(stack[-1][1], name):
                stack.pop()
            stack.append((span, name))
            continue
        while html and stack and stack[-1][1] != name and stack[-1][1] in _OPTIONAL:
            stack.pop()
        if stack and stack[-1][1] == name:
            opening, _ = stack.pop()
            pairs[opening] = span
            pairs[span] = opening
        else:
            pairs[span] = None
            # Do not pair crossed nesting.
            if stack:
                opening, _ = stack.pop()
                pairs[opening] = None
    for opening, name in stack:
        if not html or name not in _OPTIONAL:
            pairs[opening] = None
    # Prefer a tag just before the caret so repeated jumps are reversible.
    source = next((s for s in pairs if s[1] == cursor), None)
    if source is None:
        source = next((s for s in pairs if s[0] <= cursor < s[1]), None)
    return (source, pairs[source]) if source is not None else None


HTML_ITEMS = (
    ("p", "Paragraph"), ("h1", "Heading 1"), ("h2", "Heading 2"),
    ("h3", "Heading 3"), ("strong", "Bold"), ("em", "Italic"),
    ("a", "Hyperlink"), ("img", "Image"), ("div", "Division"),
    ("span", "Inline Span"), ("blockquote", "Block Quote"),
    ("pre", "Preformatted Text"), ("ul", "Unordered List"),
    ("ol", "Ordered List"), ("table", "Table (3 columns)"),
)


def html_markup(kind, selected=""):
    """Wrap existing source verbatim; return replacement and caret offset."""
    if kind not in dict(HTML_ITEMS):
        raise ValueError("Unknown HTML insertion")
    if kind == "a":
        prefix = '<a href="'
        return prefix + '">' + (selected or "link text") + "</a>", len(prefix)
    if kind == "img":
        from html import escape
        prefix = '<img src="'
        return prefix + '" alt="' + escape(selected, quote=True) + '">', len(prefix)
    if kind in ("ul", "ol"):
        prefix = "<" + kind + ">\n  <li>"
        value = "</li>\n  <li>".join(selected.splitlines()) if selected else ""
        return prefix + value + "</li>\n</" + kind + ">", len(prefix)
    if kind == "table":
        if selected:
            raise ValueError("Clear the selection before inserting a table")
        prefix = "<table>\n  <tr><th>"
        return prefix + "</th><th></th><th></th></tr>\n  <tr><td></td><td></td><td></td></tr>\n</table>", len(prefix)
    prefix = "<" + kind + ">"
    return prefix + selected + "</" + kind + ">", len(prefix) + len(selected)
