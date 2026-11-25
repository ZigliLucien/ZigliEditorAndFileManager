"""Read-only iCalendar 2.0 export of ZEFM's UTF-8 date-only CSV records.

No appointment times exist in the current CSV schema. Entries are therefore
represented as all-day events (not midnight appointments). Export is a
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


def export_ical(store, kind="appointment", *, timestamp=None):
    """Generate downloadable ICS bytes without modifying calendar.csv."""
    if kind not in KINDS:
        raise ValueError("Invalid calendar export type")
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
    for entry in store.read():
        if kind != "all" and entry["kind"] != kind:
            continue
        day = valid_date(entry["date"]).replace("-", "")
        # Hash of source content and duplicate ordinal provides a deterministic
        # identity for this snapshot. Editing a record changes its identity.
        identity = (entry["date"], entry["kind"], entry["text"])
        seen[identity] += 1
        unique = "\0".join(identity) + "\0" + str(seen[identity])
        uid = hashlib.sha256(unique.encode("utf-8")).hexdigest() + "@zefm.local"
        # A short, legible title; the full Markdown/HTML source is retained
        # as TEXT in DESCRIPTION. This export does not execute HTML.
        summary = entry["text"].strip().splitlines()[0].strip()
        if summary.startswith("#"):
            summary = summary.lstrip("#").strip()
        summary = summary[:120] or entry["kind"].title()
        lines.extend([
            "BEGIN:VEVENT",
            "UID:" + uid,
            "DTSTAMP:" + stamp,
            "DTSTART;VALUE=DATE:" + day,
            "SUMMARY:" + _escape_ical(summary),
            "DESCRIPTION:" + _escape_ical(entry["text"]),
            "CATEGORIES:" + ("Appointment" if entry["kind"] == "appointment" else "Diary"),
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    text = "\r\n".join(piece for line in lines for piece in _fold(line)) + "\r\n"
    result = text.encode("utf-8")
    if len(result) > MAX_ICS_BYTES:
        raise ValueError("Calendar export exceeds 8 MiB")
    return result
