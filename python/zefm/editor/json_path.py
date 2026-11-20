"""Source-position-aware JSON paths. Offsets are Python string character offsets."""
import json
import re
from functools import lru_cache
from json.decoder import scanstring
from .json_stream import json_values

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

def _parse_source_spans(text):
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
        # Each top-level JSON text has its own root path (). The source
        # offsets remain absolute; jq likewise evaluates .key separately
        # against each top-level value in its input stream.
        for start, end, _value in json_values(text):
            if parse(start, ()) != end:
                return None
    except (ValueError, json.JSONDecodeError, IndexError, RecursionError):
        return None
    return spans


@lru_cache(maxsize=3)
def _cached_source_spans(text):
    """Reuse a stable buffer's paths while the user moves the cursor."""
    return _parse_source_spans(text)


def source_spans(text):
    """Return source-aware paths with bounded caching for interactive edits.

    Tk reports many cursor moves without modifying text. Previously each
    movement reparsed the entire JSON buffer. A three-entry cache handles
    cursor movement and Undo without retaining unbounded large documents.
    """
    if len(text) <= 250_000:
        return _cached_source_spans(text)
    return _parse_source_spans(text)


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


def _root_spans(spans):
    """Top-level JSON text extents in source order."""
    return [(start, end) for start, end, path in spans if path == ()]


def _active_root(spans, offset):
    """Return (record index, start, end) for a cursor inside a record.

    Immediately after a closing delimiter still belongs to that record,
    unless the next top-level value starts at that exact position.
    """
    roots = _root_spans(spans)
    for index, (start, end) in enumerate(roots):
        if start <= offset < end:
            return index, start, end
    for index, (start, end) in enumerate(roots):
        if offset == end:
            return index, start, end
    # Trailing whitespace after the final JSON value belongs to the
    # final record for path and navigation convenience.
    if roots and roots[-1][1] < offset:
        return len(roots) - 1, *roots[-1]
    return None


def record_at(text, offset):
    """Return (zero-based record index, total records), or None."""
    spans = source_spans(text)
    if spans is None:
        return None
    root = _active_root(spans, offset)
    return (root[0], len(_root_spans(spans))) if root else None


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
    active = _active_root(spans, offset)
    if active is None:
        return None
    _record_index, root_start, root_end = active
    current = _parts_from_spans(
        text, [span for span in spans
               if root_start <= span[0] and span[1] <= root_end], offset)
    if current is None:
        return None

    # Navigation is scoped to the record beneath the cursor; keys repeated
    # in other top-level JSON objects must not become false siblings.
    earliest = {}
    for start, end, path in spans:
        if root_start <= start and end <= root_end:
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


def locate_path(text, parts, cursor=None):
    """Return source offset for a path in the current JSON stream record.

    With cursor=None the first top-level record is chosen for compatibility.
    With a cursor inside a later record, paths resolve there instead.
    """
    spans = source_spans(text)
    if spans is None:
        return None
    roots = _root_spans(spans)
    if not roots:
        return None
    active = (_active_root(spans, cursor) if cursor is not None
              else (0, *roots[0]))
    if active is None:
        return None
    _record_index, lo, hi = active
    starts = [start for start, end, path in spans
              if lo <= start and end <= hi and path == tuple(parts)]
    return min(starts) if starts else None
