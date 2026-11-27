"""Lightweight syntax color spans and LaTeX delimiter matching.

Pure functions: no Tk dependency and no changes to document contents.
Offsets are Python character offsets, compatible with Tk Text indexing.
"""
import io
import keyword
import re
import token
import tokenize

from .code_delimiters import json_spans

MAX_CHARS = 250_000
COLORS = {
    "heading": "#165eaa",
    "comment": "#667381",
    "keyword": "#7039a7",
    "string": "#167044",
    "number": "#a45116",
    "command": "#165eaa",
    "brace": "#86449a",
    "verbatim": "#52606b",
    "math": "#a25216",
}


def python_spans(text):
    line_starts = [0]
    line_starts.extend(m.end() for m in re.finditer("\n", text))
    result = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            style = {
                token.COMMENT: "comment",
                token.STRING: "string",
                token.NUMBER: "number",
            }.get(tok.type)
            if tok.type == token.NAME and keyword.iskeyword(tok.string):
                style = "keyword"
            if style and 1 <= tok.start[0] <= len(line_starts) and 1 <= tok.end[0] <= len(line_starts):
                a = line_starts[tok.start[0] - 1] + tok.start[1]
                b = line_starts[tok.end[0] - 1] + tok.end[1]
                if 0 <= a < b <= len(text):
                    result.append((a, b, style))
    except (tokenize.TokenError, SyntaxError, IndentationError):
        pass  # Incomplete source is normal while typing.
    return result


_JAVA = re.compile(
    r"(?P<comment>//[^\n]*|/\*[\s\S]*?(?:\*/|\Z))"
    r"|(?P<string>\"\"\"[\s\S]*?(?:\"\"\"|\Z)|\"(?:\\.|[^\"\\])*(?:\"|\Z)|'(?:\\.|[^'\\])*(?:'|\Z))"
    r"|(?P<number>\b(?:0[xX][0-9a-fA-F_]+|\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d+)?)[fFdDlL]?\b)"
    r"|(?P<word>\b[A-Za-z_$][A-Za-z_0-9$]*\b)"
)
_JAVA_KEYWORDS = frozenset("""
abstract assert boolean break byte case catch char class const continue default
do double else enum extends final finally float for goto if implements import
instanceof int interface long native new package private protected public return
short static strictfp super switch synchronized this throw throws transient
try void volatile while var record sealed permits yield true false null
""".split())


def java_spans(text):
    result = []
    for match in _JAVA.finditer(text):
        style = match.lastgroup
        if style == "word":
            if match.group() not in _JAVA_KEYWORDS:
                continue
            style = "keyword"
        result.append((match.start(), match.end(), style))
    return result


_VERBATIM_ENVIRONMENTS = frozenset({
    "verbatim", "verbatim*", "Verbatim", "Verbatim*",
    "lstlisting", "minted", "comment",
})
_INLINE_VERBATIM = re.compile(r"\\(?:verb|lstinline)\*?")


def latex_scan(text):
    """Return syntax spans and structural delimiters outside literal regions.

    Verbatim-like environments suppress all ordinary syntax inside them,
    including fake \begin/\end commands, comments, braces and parentheses.
    Inline \verb/\lstinline bodies are also treated as literal text.
    """
    spans, brackets = [], []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "%":
            end = text.find("\n", i)
            end = n if end < 0 else end
            spans.append((i, end, "comment"))
            i = end
        elif c == "\\":
            # A matching \begin{verbatim-like} initiates raw content.
            # The first exact \end{name} closes it, regardless of any
            # seemingly valid TeX commands within the raw content.
            environment = _ENVIRONMENT.match(text, i)
            if (environment is not None
                    and environment.group(1) == "begin"
                    and environment.group(2) in _VERBATIM_ENVIRONMENTS):
                name = environment.group(2)
                opening_end = environment.end()
                marker = r"\end{" + name + "}"
                closing_start = text.find(marker, opening_end)
                closing_end = n if closing_start < 0 else closing_start
                spans.append((i, opening_end, "command"))
                if opening_end < closing_end:
                    spans.append((opening_end, closing_end, "verbatim"))
                if closing_start >= 0:
                    spans.append((closing_start, closing_start + len(marker),
                                  "command"))
                    i = closing_start + len(marker)
                else:
                    i = n
                continue

            # \verb|{\end{fake} % }| and \lstinline!code! contain no
            # structural TeX syntax. The delimiter is the next nonletter,
            # nonwhitespace character; an unfinished body ends at newline.
            inline = _INLINE_VERBATIM.match(text, i)
            if inline is not None:
                delimiter_at = inline.end()
                if (delimiter_at < n
                        and not text[delimiter_at].isspace()
                        and not text[delimiter_at].isalpha()):
                    delimiter = text[delimiter_at]
                    newline = text.find("\n", delimiter_at + 1)
                    boundary = n if newline < 0 else newline
                    closing = text.find(delimiter, delimiter_at + 1, boundary)
                    end = closing + 1 if closing >= 0 else boundary
                    spans.append((i, end, "verbatim"))
                    i = end
                    continue

            end = i + 1
            if end < n and (text[end].isalpha() or text[end] == "@"):
                while end < n and (text[end].isalpha() or text[end] == "@"):
                    end += 1
                if end < n and text[end] == "*":
                    end += 1
            elif end < n:
                end += 1
            spans.append((i, end, "command"))
            i = end
        elif c in "{}[]()":
            brackets.append((i, c))
            if c in "{}":
                spans.append((i, i + 1, "brace"))
            i += 1
        else:
            i += 1
    return spans, brackets

_OPEN = {"{": "}", "[": "]", "(": ")"}
_CLOSE = {value: key for key, value in _OPEN.items()}


def latex_match(text, cursor):
    """Return (delimiter offset, match offset or None), or None.

    A cursor immediately after a delimiter highlights that delimiter;
    otherwise it examines the character under the insertion point.
    Escaped delimiters and comment contents are ignored.
    """
    if not isinstance(cursor, int) or cursor < 0 or cursor > len(text):
        return None
    if len(text) > MAX_CHARS:
        return None
    _spans, pairs = latex_scan(text)
    by_offset = dict(pairs)
    pos = cursor - 1 if cursor > 0 and cursor - 1 in by_offset else cursor
    c = by_offset.get(pos)
    if c is None:
        return None
    if c in _OPEN:
        stack = []
        for off, value in pairs:
            if off < pos:
                continue
            if value in _OPEN:
                stack.append((off, value))
            elif stack:
                top_off, opening = stack[-1]
                if _OPEN[opening] != value:
                    if top_off == pos or any(x[0] == pos for x in stack):
                        return pos, None
                    continue
                stack.pop()
                if top_off == pos:
                    return pos, off
        return pos, None
    stack = []
    for off, value in reversed(pairs):
        if off > pos:
            continue
        if value in _CLOSE:
            stack.append((off, value))
        elif stack:
            top_off, closing = stack[-1]
            if _CLOSE[closing] != value:
                if top_off == pos or any(x[0] == pos for x in stack):
                    return pos, None
                continue
            stack.pop()
            if top_off == pos:
                return pos, off
    return pos, None



_ENVIRONMENT = re.compile(r"\\(begin|end)\{([A-Za-z][A-Za-z0-9*@._-]*)\}")


def latex_environment_match(text, cursor):
    """Match a complete \begin{name} or \end{name} at the caret.

    Return ((start, end), (match_start, match_end)) for a matched pair,
    or ((start, end), None) for an unmatched or misnested command.
    Endpoints are exclusive. Comments and escaped commands are ignored.
    This is a structural aid, not a full TeX macro expander.
    """
    if not isinstance(cursor, int) or not 0 <= cursor <= len(text):
        return None
    if len(text) > MAX_CHARS:
        return None
    spans, _brackets = latex_scan(text)
    commands = {a for a, _b, style in spans if style == "command"}
    tokens = []
    for match in _ENVIRONMENT.finditer(text):
        if match.start() not in commands:
            continue
        tokens.append((match.start(), match.end(),
                       match.group(1), match.group(2)))
    # Match only properly nested environments with identical names.
    stack = []
    partners = {}
    for start, end, kind, name in tokens:
        span = (start, end)
        if kind == "begin":
            stack.append((span, name))
        elif stack and stack[-1][1] == name:
            opening, _ = stack.pop()
            partners[opening] = span
            partners[span] = opening
        else:
            partners[span] = None
    for opening, _name in stack:
        partners[opening] = None
    # Cursor on/inside the command or immediately after the closing brace.
    for start, end, _kind, _name in tokens:
        if start <= cursor <= end:
            span = (start, end)
            return span, partners.get(span)
    return None




_MATH_PAIRS = {"\\(": "\\)", "\\[": "\\]", "$": "$", "$": "$"}
_MATH_OPEN = frozenset(("\\(", "\\[", "$", "$"))
_MATH_CLOSE = frozenset(("\\)", "\\]"))


def latex_math_tokens(text, spans=None):
    """Yield (start, end, marker) for genuine math delimiters.

    TeX comments, verbatim content and escaped dollars are excluded by the
    existing scanner. The command forms must be complete two-character TeX
    commands; a second backslash must not introduce a false math delimiter.
    """
    if len(text) > MAX_CHARS:
        return []
    if spans is None:
        spans, _delimiters = latex_scan(text)
    suppressed = [(a, b) for a, b, style in spans
                  if style in ("comment", "verbatim")]
    commands = {a: (b, text[a:b]) for a, b, style in spans
                if style == "command"}
    tokens = []
    i, k, n = 0, 0, len(text)
    while i < n:
        while k < len(suppressed) and suppressed[k][1] <= i:
            k += 1
        if k < len(suppressed) and suppressed[k][0] <= i < suppressed[k][1]:
            i = suppressed[k][1]
            continue
        command = commands.get(i)
        if command is not None:
            end, name = command
            if name in (r"\(", r"\)", r"\[", r"\]"):
                tokens.append((i, end, name))
            i = end
            continue
        if text[i] == "$":
            end = i + (2 if text.startswith("$", i) else 1)
            tokens.append((i, end, text[i:end]))
            i = end
            continue
        i += 1
    return tokens


def latex_math_pairs(text, spans=None):
    """Return tokens paired with their mate, or None for a bad delimiter."""
    tokens = latex_math_tokens(text, spans)
    partner = {}
    stack = []
    for start, end, marker in tokens:
        key = (start, end)
        if marker in _MATH_CLOSE:
            opening = next((op for op, pair in _MATH_PAIRS.items()
                            if pair == marker and op != pair), None)
            if stack and stack[-1][2] == opening:
                previous = stack.pop()
                other = previous[:2]
                partner[key] = other
                partner[other] = key
            else:
                partner[key] = None
        elif stack and stack[-1][2] == marker and marker in ("$", "$"):
            previous = stack.pop()
            other = previous[:2]
            partner[key] = other
            partner[other] = key
        else:
            stack.append((start, end, marker))
    for start, end, _marker in stack:
        partner[(start, end)] = None
    return tokens, partner


def latex_math_match(text, cursor):
    """Return (source_span, partner_span or None) near the insertion point."""
    if not isinstance(cursor, int) or not 0 <= cursor <= len(text):
        return None
    if len(text) > MAX_CHARS:
        return None
    tokens, partners = latex_math_pairs(text)
    for start, end, _marker in tokens:
        if start <= cursor <= end:
            span = (start, end)
            return span, partners.get(span)
    return None



def latex_matching_delimiter(text, cursor):
    """Find the matched structure at the cursor without editing the source.

    Return (source_span, partner_span or None) with half-open character
    offsets, or None if the cursor is not on a supported delimiter.
    Environments take precedence over their argument braces; math
    delimiters take precedence over ordinary grouping delimiters.
    """
    if not isinstance(cursor, int) or not 0 <= cursor <= len(text):
        return None
    if len(text) > MAX_CHARS:
        return None

    environment = latex_environment_match(text, cursor)
    if environment is not None:
        return environment
    math = latex_math_match(text, cursor)
    if math is not None:
        return math
    brace = latex_match(text, cursor)
    if brace is None:
        return None
    position, partner = brace
    return ((position, position + 1),
            (partner, partner + 1) if partner is not None else None)


def latex_issues(text):
    """Find unmatched TeX grouping braces and environment commands.

    Returns sorted (offset, length, description) tuples.  This deliberately
    checks only curly braces, not ordinary mathematical parentheses/brackets.
    It ignores comments, escaped braces and verbatim-style contents using
    the same scanner as the cursor-based matching feature.
    """
    if len(text) > MAX_CHARS:
        return []
    spans, delimiters = latex_scan(text)
    issues = []
    braces = []
    for pos, char in delimiters:
        if char == "{":
            braces.append(pos)
        elif char == "}":
            if braces:
                braces.pop()
            else:
                issues.append((pos, 1, "Unexpected closing brace }"))
    issues.extend((pos, 1, "Unclosed opening brace {") for pos in braces)

    command_starts = {start for start, _end, style in spans
                      if style == "command"}
    environments = []
    for match in _ENVIRONMENT.finditer(text):
        if match.start() not in command_starts:
            continue
        pos, end = match.span()
        kind, name = match.group(1), match.group(2)
        if kind == "begin":
            environments.append((pos, end, name))
        elif environments and environments[-1][2] == name:
            environments.pop()
        else:
            issues.append((pos, end - pos,
                           "Unmatched \\\\end{" + name + "}"))
    for pos, end, name in environments:
        issues.append((pos, end - pos,
                       "Unclosed \\\\begin{" + name + "}"))
    math_tokens, math_partners = latex_math_pairs(text, spans)
    for start, end, marker in math_tokens:
        if math_partners[(start, end)] is None:
            label = "Unexpected" if marker in _MATH_CLOSE else "Unmatched"
            issues.append((start, end - start,
                           f"{label} math delimiter {marker}"))
    return sorted(issues, key=lambda entry: entry[0])


def syntax_spans(text, mode):
    if len(text) > MAX_CHARS:
        return []
    if mode == "latex":
        spans, _delimiters = latex_scan(text)
        spans.extend((a, b, "math")
                     for a, b, _marker in latex_math_tokens(text, spans))
        return spans
    if mode == "python":
        return python_spans(text)
    if mode == "json":
        return json_spans(text)
    if mode == "java":
        return java_spans(text)
    if mode in ("html", "xml"):
        from .markup_tags import scan_tags
        return scan_tags(text, mode)[1]
    if mode == "markdown":
        from .markdown_outline import markdown_scan
        return markdown_scan(text)[1]
    return []
