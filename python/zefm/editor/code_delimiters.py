"""Lightweight structural bracket matching for Python and JSON buffers.

Everything here is pure source analysis: offsets, not edits or Tk commands.
Python uses the standard tokenizer so comments and quoted literals are not
mistaken for code; JSON uses a small escape-aware string scanner.
"""
import io
import re
import token
import tokenize

MAX_CHARS = 250_000

_OPEN = {"(": ")", "[": "]", "{": "}"}
_CLOSE = {right: left for left, right in _OPEN.items()}
_JSON_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_JSON_WORD = re.compile(r"(?:true|false|null)(?![A-Za-z0-9_])")


def python_brackets(text):
    """Return (character offset, delimiter) tokens outside Python literals.

    tokenize also tolerates most in-progress edits. On an incomplete string
    or unfinished expression it can raise TokenError; retain tokens that
    appeared before the error rather than disturbing the editor.
    """
    line_offsets = [0]
    line_offsets.extend(match.end() for match in re.finditer("\n", text))
    found = []
    try:
        for item in tokenize.generate_tokens(io.StringIO(text).readline):
            if item.type != token.OP or item.string not in "()[]{}":
                continue
            row, column = item.start
            if 1 <= row <= len(line_offsets):
                position = line_offsets[row - 1] + column
                if 0 <= position < len(text):
                    found.append((position, item.string))
    except (tokenize.TokenError, SyntaxError, IndentationError):
        pass
    return found


def _json_scan(text):
    """Return JSON delimiters and syntax spans, ignoring quoted strings.

    A backslash escapes its following character inside a string. An
    unfinished string consumes the rest of the buffer, avoiding false
    bracket matches during typing.
    """
    found, spans, quote_partners = [], [], {}
    i, n = 0, len(text)
    while i < n:
        char = text[i]
        if char == '"':
            start = i
            i += 1
            closing = None
            while i < n:
                if text[i] == "\\":
                    i = min(i + 2, n)
                elif text[i] == '"':
                    closing = i
                    i += 1
                    break
                else:
                    i += 1
            quote_partners[start] = closing
            if closing is not None:
                quote_partners[closing] = start
            spans.append((start, i, "string"))
        elif char in "{}[]":
            found.append((i, char))
            spans.append((i, i + 1, "brace"))
            i += 1
        elif char == "-" or char.isdigit():
            number = _JSON_NUMBER.match(text, i)
            if number is not None:
                spans.append((i, number.end(), "number"))
                i = number.end()
            else:
                i += 1
        elif char in "tfn":
            word = _JSON_WORD.match(text, i)
            if word is not None:
                spans.append((i, word.end(), "keyword"))
                i = word.end()
            else:
                i += 1
        else:
            i += 1
    return found, spans, quote_partners


def json_brackets(text):
    """Return JSON object/array delimiter locations outside quoted strings."""
    return _json_scan(text)[0]


def json_quote_match(text, cursor):
    """Match unescaped double quotes, or flag an unfinished string.

    Only the quote itself and its counterpart are highlighted, not the
    entire string. An unclosed string has an opening quote with no partner.
    """
    if (not isinstance(text, str) or not isinstance(cursor, int)
            or not 0 <= cursor <= len(text) or len(text) > MAX_CHARS):
        return None
    partners = _json_scan(text)[2]
    # Prefer the character immediately before the caret, as for brackets.
    source = (cursor - 1 if cursor > 0 and cursor - 1 in partners
              else cursor)
    if source not in partners:
        return None
    return source, partners[source]


def json_spans(text):
    """Return syntax spans for JSON strings, punctuation, values and numbers."""
    if len(text) > MAX_CHARS:
        return []
    return _json_scan(text)[1]


def _partners(tokens):
    """Pair only correctly nested delimiters; mark mismatches as unmatched."""
    result = {}
    stack = []
    for position, char in tokens:
        if char in _OPEN:
            stack.append((position, char))
        elif stack and _OPEN[stack[-1][1]] == char:
            opening, _kind = stack.pop()
            result[position] = opening
            result[opening] = position
        elif char in _CLOSE:
            # Reject crossed nesting, e.g. ([)] must not appear paired.
            # The invalid closer and the now-invalid top opener are red.
            result[position] = None
            if stack:
                opening, _kind = stack.pop()
                result[opening] = None
    for position, _char in stack:
        result[position] = None
    return result


def code_bracket_match(text, cursor, mode):
    """Return (source offset, matching offset or None), or None.

    The character immediately before the insertion point has precedence,
    matching the existing LaTeX behavior. No syntax check is implied by
    a green match; this only checks correctly nested bracket pairs.
    """
    if (not isinstance(text, str) or not isinstance(cursor, int)
            or not 0 <= cursor <= len(text) or len(text) > MAX_CHARS):
        return None
    if mode == "python":
        tokens = python_brackets(text)
    elif mode == "json":
        tokens = json_brackets(text)
    else:
        return None
    at = {position for position, _char in tokens}
    pos = cursor - 1 if cursor > 0 and cursor - 1 in at else cursor
    if pos not in at:
        return None
    return pos, _partners(tokens)[pos]
