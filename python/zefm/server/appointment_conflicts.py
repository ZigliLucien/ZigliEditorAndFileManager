"""Read-only detection of overlapping timed calendar appointments.

Compare timezone-aware UTC instants, not wall-clock strings or display
dates. Treat intervals as half-open: a meeting ending exactly when another
starts is not a conflict. No CSV modification and no all-day warnings.
"""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def appointment_interval(entry):
    """Return UTC start/end for a timed event, or None for all-day entries.

    Records have already passed CSV validation. Fallback None keeps view
    rendering resilient if timezone data becomes unavailable on the host.
    """
    if entry.get("kind") != "appointment" or not entry.get("start_time"):
        return None
    try:
        zone = ZoneInfo(entry["timezone"])
        start = datetime.fromisoformat(
            entry["date"] + "T" + entry["start_time"]).replace(tzinfo=zone)
        end = datetime.fromisoformat(
            entry["date"] + "T" + entry["end_time"]).replace(tzinfo=zone)
        first = start.astimezone(timezone.utc)
        last = end.astimezone(timezone.utc)
        if last <= first:
            return None
        return first, last
    except (KeyError, ValueError, OverflowError, ZoneInfoNotFoundError):
        return None


def conflicting_rows(records):
    """Map original CSV row indexes to one overlapping row each.

    O(n log n) through sorted interval starts; a running maximum end
    represents an overlapping earlier record when one exists. This
    avoids quadratic work even for thousands of identical appointments.
    """
    intervals = []
    for index, entry in enumerate(records):
        pair = appointment_interval(entry)
        if pair:
            intervals.append((pair[0], pair[1], index))
    intervals.sort(key=lambda item: item[0])
    conflicts = {}
    max_end = None
    max_index = None
    for start, end, index in intervals:
        if max_end is not None and start < max_end:
            conflicts.setdefault(index, max_index)
            conflicts.setdefault(max_index, index)
        if max_end is None or end > max_end:
            max_end, max_index = end, index
    return conflicts
