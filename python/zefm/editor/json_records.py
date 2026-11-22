"""Lightweight top-level record navigation for JSON, JSONL and JSON streams.

Only offsets are retained: decoded JSON objects are discarded after indexing.
"""
import json
from bisect import bisect_right

_WHITESPACE = " \t\r\n"


def record_bounds(source):
    """Return (start, end) offsets for each top-level JSON value."""
    decoder = json.JSONDecoder()
    offsets = []
    i = 0
    n = len(source)
    while i < n:
        while i < n and source[i] in _WHITESPACE:
            i += 1
        if i == n:
            break
        _value, end = decoder.raw_decode(source, i)
        offsets.append((i, end))
        i = end
    if not offsets:
        raise json.JSONDecodeError("Expecting value", source, 0)
    return tuple(offsets)


def record_index(bounds, cursor):
    """Zero-based active record, or None before the first record."""
    if not bounds or cursor < bounds[0][0]:
        return None
    return bisect_right(bounds, (cursor, float("inf"))) - 1


def adjacent_record(bounds, cursor, direction):
    """Return target offset or None; direction must be +1 or -1."""
    if direction not in (-1, 1):
        raise ValueError("Record direction must be +1 or -1")
    active = record_index(bounds, cursor)
    if active is None:
        return bounds[0][0] if bounds and direction == 1 else None
    target = active + direction
    return bounds[target][0] if 0 <= target < len(bounds) else None

def outline_rows(source, bounds, preview_width=90):
    """Return (record number, line number, preview, start offset) for an outline.

    Count intervening newlines incrementally to avoid quadratic work on
    large streams. Preview only a small slice of each record.
    """
    rows = []
    previous = 0
    line = 1
    for number, (start, end) in enumerate(bounds, 1):
        line += source.count("\n", previous, start)
        preview = " ".join(source[start:min(end, start + preview_width * 3)].split())
        if len(preview) > preview_width:
            preview = preview[:preview_width - 3] + "..."
        rows.append((number, line, preview, start))
        previous = start
    return rows
