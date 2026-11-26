"""Read-only iCalendar 2.0 export of ZEFM's UTF-8 date-only CSV records.

Legacy date-only entries are exported as all-day events; records with explicit
start/end time and IANA timezone are exported as timed events. Export is a
snapshot: importing an .ics file into another app is not two-way sync.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib

from ..storage.calendar_diary import valid_date

MAX_ICS_BYTES = 8 * 1024 * 1024
KINDS = {"appointment", "diary", "all"}


def _escape_ical(value: str) -> str:
    """RFC 5545 TEXT escaping; preserve Unicode, not rendered HTML."""
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return (value.replace("\\", "\\\\").replace("\n", "\\n")
            .replace(",", "\\,").replace(";", "\\;"))


def _fold(line: str) -> list[str]:
    """Fold lines to at most 75 UTF-8 octets, without splitting a codepoint."""
    chunks = []
    current = ""
    size = 0
    for character in line:
        character_size = len(character.encode("utf-8"))
        if size + character_size > 75:
            chunks.append(current)
            current = " "
            size = 1
        current += character
        size += character_size
    chunks.append(current)
    return chunks


def export_ical(store, kind="appointment", *, timestamp=None, row_index=None):
    """Generate downloadable ICS bytes without modifying calendar.csv."""
    if kind not in KINDS:
        raise ValueError("Invalid calendar export type")
    if row_index is not None and (type(row_index) is not int or row_index < 0):
        raise ValueError("Invalid calendar export row")
    now = timestamp or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("iCalendar export timestamp must include a timezone")
    stamp = now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ZEFM//Calendar Diary CSV//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:ZEFM Calendar",
    ]
    seen = Counter()
    records = store.read()
    if row_index is not None and row_index >= len(records):
        raise ValueError("Calendar export row not found")
    if row_index is not None and records[row_index]["kind"] != "appointment":
        raise ValueError("Only appointments can be shared individually")
    for index, entry in enumerate(records):
        if kind != "all" and entry["kind"] != kind:
            continue
        # Count all matching records to retain the same UID for a single
        # appointment as in the full export, even with duplicate entries.
        identity = tuple(entry.get(key, "") for key in (
            "date", "kind", "text", "start_time", "end_time",
            "timezone", "location"))
        seen[identity] += 1
        if row_index is not None and index != row_index:
            continue
        day = valid_date(entry["date"]).replace("-", "")
        # Hash of source content and duplicate ordinal provides a deterministic
        # identity for this snapshot. Editing a record changes its identity.
        unique = "\0".join(identity) + "\0" + str(seen[identity])
        uid = hashlib.sha256(unique.encode("utf-8")).hexdigest() + "@zefm.local"
        # A short, legible title; the full Markdown/HTML source is retained
        # as TEXT in DESCRIPTION. This export does not execute HTML.
        summary = entry["text"].strip().splitlines()[0].strip()
        if summary.startswith("#"):
            summary = summary.lstrip("#").strip()
        summary = summary[:120] or entry["kind"].title()
        start_field = "DTSTART;VALUE=DATE:" + day
        end_field = None
        if entry.get("start_time"):
            tzid = entry["timezone"]
            start_stamp = day + "T" + entry["start_time"].replace(":", "") + "00"
            end_stamp = day + "T" + entry["end_time"].replace(":", "") + "00"
            if tzid == "UTC":
                start_field = "DTSTART:" + start_stamp + "Z"
                end_field = "DTEND:" + end_stamp + "Z"
            else:
                start_field = "DTSTART;TZID=" + tzid + ":" + start_stamp
                end_field = "DTEND;TZID=" + tzid + ":" + end_stamp
        lines.extend([
            "BEGIN:VEVENT",
            "UID:" + uid,
            "DTSTAMP:" + stamp,
            start_field,
            "SUMMARY:" + _escape_ical(summary),
            "DESCRIPTION:" + _escape_ical(entry["text"]),
            "CATEGORIES:" + ("Appointment" if entry["kind"] == "appointment" else "Diary"),
            *(["LOCATION:" + _escape_ical(entry["location"])]
              if entry.get("location") else []),
            *([end_field] if end_field else []),
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    text = "\r\n".join(piece for line in lines for piece in _fold(line)) + "\r\n"
    result = text.encode("utf-8")
    if len(result) > MAX_ICS_BYTES:
        raise ValueError("Calendar export exceeds 8 MiB")
    return result
