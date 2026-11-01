"""Server-side equivalent of ZEFM's original ServPak/js/mathformat.js.

Original JavaScript depended on jQuery and changed document markup after load.
For generated Markdown we apply the same semantic transformations before sending
the page, because the browser preview intentionally disables all JavaScript.
"""
from __future__ import annotations
from html import escape
from html.parser import HTMLParser

THEOREMS = {"theorem", "proposition", "lemma", "corollary", "remark", "example"}
SECTIONS = {"section": 2, "subsection": 3, "subsubsection": 4,
            "paragraph": 5, "subparagraph": 6}
LISTS = {"enumerate": "ol", "itemize": "ul", "description": "dl",
         "item": "li"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}


class _MathFormatter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []
        self.closers = []
        self.in_body = False
        self.has_body = False
        self.has_head = False

    @staticmethod
    def _attrs(items):
        return "".join(
            " " + name + (('="' + escape(value, quote=True) + '"')
                          if value is not None else "")
            for name, value in items
        )

    def handle_starttag(self, tag, items):
        attrs = dict(items)
        classes = set(attrs.get("class", "").split())
        semantic = next((cls for cls in SECTIONS if cls in classes), None)
        theorem = next((cls for cls in THEOREMS if cls in classes), None)
        if tag in SECTIONS:
            semantic = tag
        if tag in THEOREMS:
            theorem = tag

        if tag == "head":
            self.has_head = True
        if tag == "body":
            self.has_body = True
            classes.add("zefm-math-page")
            items = [(k, v) for k, v in items if k != "class"]
            items.append(("class", " ".join(sorted(classes))))

        heading = attrs.get("id", "")
        if semantic and heading:
            level = SECTIONS[semantic]
            self.output.append(f"<h{level}>" + escape(heading.replace("_", " ")) +
                               f"</h{level}>")
        if theorem:
            label = theorem.capitalize()
            identifier = attrs.get("id")
            if identifier:
                label += " " + identifier
            self.output.append('<div class="zefm-math-heading">' +
                               escape(label) + '</div>')
        elif tag == "proof" or "proof" in classes:
            self.output.append('<span class="zefm-proof-heading">Proof.</span> ')

        mapped = LISTS.get(tag, tag)
        if mapped == "eq" or mapped == "equation":
            mapped = "div"
            classes.add("equation")
        if tag in LISTS:
            classes.add("zefm-math-list")
        if mapped != tag:
            items = [(k, v) for k, v in items if k != "class"]
            items.append(("class", " ".join(sorted(classes))))
        if tag == "ref" or tag == "labelref" or "ref" in classes or "labelref" in classes:
            name = attrs.get("name", "")
            self.output.append('<a href="#' + escape(name, quote=True) + '">')
            self.closers.append((tag, "</a>"))
            return
        if tag in ("quad", "qquad", "skip", "cr"):
            self.output.append('<span class="' + tag + '"></span>')
            self.closers.append((tag, ""))
            return
        if tag == "head":
            self.output.append("<head" + self._attrs(items) + ">")
            self.output.append('<link rel="stylesheet" href="/math.css">')
        else:
            self.output.append("<" + mapped + self._attrs(items) + ">")

        if tag not in VOID:
            closing = "</" + mapped + ">"
            if tag in ("eq", "equation"):
                number = attrs.get("num", "")
                if number:
                    closing = ('<span class="eqno">(' + escape(number) +
                               ')</span>' + closing)
            self.closers.append((tag, closing))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.closers and self.closers[-1][0] == tag:
            self.output.append(self.closers.pop()[1])
        else:
            self.output.append("</" + tag + ">")

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append("&" + name + ";")

    def handle_charref(self, name):
        self.output.append("&#" + name + ";")

    def handle_decl(self, decl):
        self.output.append("<!" + decl + ">")

    def handle_comment(self, data):
        self.output.append("<!--" + data + "-->")


def format_math_html(markup: str) -> str:
    formatter = _MathFormatter()
    formatter.feed(markup)
    formatter.close()
    result = "".join(formatter.output)
    if not formatter.has_head:
        # Discount's markdown fragment fallback has its own complete wrapper;
        # support minimal standalone HTML from makepage too.
        result = '<link rel="stylesheet" href="/math.css">' + result
    if not formatter.has_body:
        result = '<div class="zefm-math-page">' + result + '</div>'
    return result
