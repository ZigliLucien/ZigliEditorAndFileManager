"""Source-position-aware JSON paths. Offsets are Python string character offsets."""
import json
import re
from json.decoder import scanstring

_NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')
_IDENT = re.compile(r'^[A-Za-z_][A-Za-z_0-9]*$')

def jq_path(parts):
    out = "."
    for part in parts:
        if isinstance(part, int):
            out += f"[{part}]"
        elif _IDENT.fullmatch(part):
            out += ("" if out == "." else ".") + part
        else:
            out += "[" + json.dumps(part, ensure_ascii=False) + "]"
    return out

def source_spans(text):
    """Return deepest JSON path covering offset; None for invalid JSON/outside."""
    spans = []
    n = len(text)
    def ws(i):
        while i < n and text[i] in " \t\r\n": i += 1
        return i
    def string(i):
        if i >= n or text[i] != '"': raise ValueError("Expected string")
        value, end = scanstring(text, i + 1, True)
        return value, end
    def parse(i, path):
        i = ws(i)
        start = i
        if i >= n: raise ValueError("Unexpected end")
        c = text[i]
        if c == '{':
            i = ws(i + 1)
            if i < n and text[i] == '}': i += 1
            else:
                while True:
                    key_start = i
                    key, i = string(i)
                    key_end = i
                    spans.append((key_start, key_end, path + (key,)))
                    i = ws(i)
                    if i >= n or text[i] != ':': raise ValueError("Expected colon")
                    value_start = i + 1
                    i = parse(value_start, path + (key,))
                    spans.append((key_end, i, path + (key,)))
                    i = ws(i)
                    if i < n and text[i] == '}': i += 1; break
                    if i >= n or text[i] != ',': raise ValueError("Expected comma")
                    i = ws(i + 1)
        elif c == '[':
            i = ws(i + 1)
            if i < n and text[i] == ']': i += 1
            else:
                k = 0
                while True:
                    i = parse(i, path + (k,))
                    k += 1
                    i = ws(i)
                    if i < n and text[i] == ']': i += 1; break
                    if i >= n or text[i] != ',': raise ValueError("Expected comma")
                    i = ws(i + 1)
        elif c == '"':
            _, i = string(i)
        elif c in '-0123456789':
            m = _NUMBER.match(text, i)
            if not m: raise ValueError("Invalid number")
            i = m.end()
        else:
            literal = next((v for v in ('true','false','null') if text.startswith(v,i)), None)
            if literal is None: raise ValueError("Invalid literal")
            i += len(literal)
        spans.append((start, i, path))
        return i
    try:
        end = ws(parse(0, ()))
        if end != n: return None
        # Check syntax strictly, including duplicate handling consistent with stdlib.
        json.loads(text)
    except (ValueError, json.JSONDecodeError, IndexError):
        return None
    return spans

def _parts_from_spans(text, spans, offset):
    """Find the deepest path beside the insertion point.

    Positions immediately AFTER a JSON token (closing quote/bracket/brace or
    a primitive value) still refer to that token when it is deeper than the
    surrounding object/array. This is important after bracket matching has
    positioned Tk's insertion cursor just after the matched delimiter.
    """
    if not isinstance(offset, int) or not 0 <= offset <= len(text):
        return None
    candidates = [entry for entry in spans
                  if entry[0] <= offset < entry[1]]
    endings = [entry for entry in spans
               if entry[0] < offset and entry[1] == offset]
    best = max(candidates, key=lambda entry: len(entry[2]), default=None)
    boundary = max(endings, key=lambda entry: len(entry[2]), default=None)
    if boundary is not None and (
            best is None or len(boundary[2]) > len(best[2])):
        return boundary[2]
    if best is not None:
        return best[2]
    # The caret may be after the last newline in a pretty-printed file.
    # That position denotes the document root rather than an invalid path.
    if offset >= len(text.rstrip(" \t\r\n")):
        return ()
    return None


def path_parts_at(text, offset):
    spans = source_spans(text)
    return _parts_from_spans(text, spans, offset) if spans is not None else None

def paths_at(text, offset):
    parts = path_parts_at(text, offset)
    return jq_path(parts) if parts is not None else None

def navigate(text, offset, direction):
    """Navigate one JSON structure from a cursor position.

    Parse the buffer only once. In particular, large arrays/objects must not
    trigger a complete JSON reparse for every possible child/sibling.
    Returns (source offset, jq path) or None at boundaries/invalid JSON.
    """
    if direction not in ("parent", "child", "next", "previous"):
        raise ValueError("Unknown navigation direction")
    spans = source_spans(text)
    if spans is None:
        return None
    current = _parts_from_spans(text, spans, offset)
    if current is None:
        return None

    # Each path may have several spans (key token, colon, value). Its first
    # appearance is the navigation target, preserving the document's order.
    earliest = {}
    for start, _end, path in spans:
        if path not in earliest or start < earliest[path]:
            earliest[path] = start

    if direction == "parent":
        target = current[:-1] if current else None
    elif direction == "child":
        children = [path for path in earliest
                    if len(path) == len(current) + 1
                    and path[:-1] == current]
        target = min(children, key=earliest.get) if children else None
    else:
        if not current:
            return None
        siblings = [path for path in earliest
                    if len(path) == len(current)
                    and path[:-1] == current[:-1]]
        siblings.sort(key=earliest.get)
        index = siblings.index(current)
        index += 1 if direction == "next" else -1
        target = siblings[index] if 0 <= index < len(siblings) else None

    if target is None:
        return None
    start = earliest.get(target)
    if start is None:
        return None
    return start, jq_path(target)


def locate_path(text, parts):
    """Return source offset for exact structural path, or None."""
    spans=source_spans(text)
    if spans is None:return None
    starts=[start for start,end,path in spans if path==tuple(parts)]
    return min(starts) if starts else None
