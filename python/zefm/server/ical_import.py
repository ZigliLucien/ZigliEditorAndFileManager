"""Conservative, two-phase iCalendar import into CSV-backed ZEFM appointments.

Only explicit all-day DTSTART;VALUE=DATE events are accepted. Timed,
recurring, or ambiguous events abort parsing instead of silently losing data.
Never reads remote URL, opens external files, or expands RRULE expressions.
"""
from __future__ import annotations

from datetime import date
from html import escape
from urllib.parse import urlencode

from ..storage.calendar_diary import validated_record, valid_date

MAX_ICS_SOURCE = 128 * 1024
MAX_ICS_EVENTS = 500


def _text(value):
    """Decode RFC 5545 escaped TEXT; reject unexpected backslash escapes."""
    out = []
    i = 0
    while i < len(value):
        if value[i] != "\\":
            out.append(value[i])
            i += 1
        else:
            if i + 1 >= len(value):
                raise ValueError("Trailing iCalendar escape")
            nxt = value[i + 1]
            if nxt in "nN":
                out.append("\n")
            elif nxt in "\\;,":
                out.append(nxt)
            else:
                raise ValueError("Unsupported iCalendar text escape")
            i += 2
    return "".join(out)


def parse_ics(source):
    """Read a bounded subset of RFC 5545. Return validated appointment rows."""
    if not isinstance(source, str) or len(source.encode("utf-8")) > MAX_ICS_SOURCE:
        raise ValueError("iCalendar text exceeds 128 KiB")
    if "\x00" in source or ("\r" in source.replace("\r\n", "")):
        raise ValueError("Invalid iCalendar line endings")
    lines = source.replace("\r\n", "\n").split("\n")
    unfolded = []
    for line in lines:
        if len(line.encode("utf-8")) > 4096:
            raise ValueError("Overlong iCalendar line")
        if line.startswith((" ", "\t")):
            if not unfolded:
                raise ValueError("Unexpected continuation line")
            unfolded[-1] += line[1:]
        elif line:
            unfolded.append(line)
    if not unfolded or unfolded[0].upper() != "BEGIN:VCALENDAR" or unfolded[-1].upper() != "END:VCALENDAR":
        raise ValueError("Expected a complete VCALENDAR")
    if not any(line.upper() == "VERSION:2.0" for line in unfolded):
        raise ValueError("Only iCalendar VERSION:2.0 is supported")
    entries = []
    event = None
    in_alarm = False
    for line in unfolded[1:-1]:
        upper = line.upper()
        if upper == "BEGIN:VALARM":
            # Explicitly reject alarms, including nested alarm blocks.
            raise ValueError("Events containing alarms are not supported")
        if upper == "BEGIN:VEVENT":
            if event is not None:
                raise ValueError("Nested VEVENT is not supported")
            event = {}
            continue
        if upper == "END:VEVENT":
            if event is None:
                raise ValueError("Unexpected END:VEVENT")
            if len(entries) >= MAX_ICS_EVENTS:
                raise ValueError("iCalendar exceeds 500 events")
            values = event.get("DTSTART;VALUE=DATE")
            if not values or len(values) != 1:
                raise ValueError("Only explicit all-day DTSTART;VALUE=DATE events are supported")
            raw_day = values[0]
            if len(raw_day) != 8 or not raw_day.isascii() or not raw_day.isdecimal():
                raise ValueError("Invalid iCalendar DTSTART date")
            try:
                day = date(int(raw_day[:4]), int(raw_day[4:6]), int(raw_day[6:])).isoformat()
            except ValueError as exc:
                raise ValueError("Invalid iCalendar DTSTART date") from exc
            if any(k.startswith("DTSTART") and k != "DTSTART;VALUE=DATE" for k in event):
                raise ValueError("Timed events are not supported")
            if any(k in event for k in ("RRULE", "RDATE", "EXDATE", "RECURRENCE-ID", "DURATION")):
                raise ValueError("Recurring or duration-based events are not supported")
            end = event.get("DTEND;VALUE=DATE")
            if end:
                if len(end) != 1 or len(end[0]) != 8 or not end[0].isascii() or not end[0].isdecimal():
                    raise ValueError("Invalid all-day event end date")
                try:
                    end_date = date(int(end[0][:4]), int(end[0][4:6]), int(end[0][6:])).isoformat()
                except ValueError as exc:
                    raise ValueError("Invalid event end date") from exc
                if (date.fromisoformat(end_date) - date.fromisoformat(day)).days != 1:
                    raise ValueError("Only one-day events are supported")
            if any(k.startswith("DTEND") and k != "DTEND;VALUE=DATE" for k in event):
                raise ValueError("Timed event end date not supported")
            if event.get("STATUS", [""])[0].upper() == "CANCELLED":
                raise ValueError("Cancelled events cannot be imported")
            description = event.get("DESCRIPTION", [""])
            summary = event.get("SUMMARY", [""])
            if len(description) != 1 or len(summary) != 1:
                raise ValueError("Duplicate event summary or description")
            note = _text(description[0]) if description[0] else _text(summary[0])
            entries.append(validated_record(day, "appointment", note))
            event = None
            continue
        if upper.startswith(("BEGIN:", "END:")):
            raise ValueError("Unsupported iCalendar component")
        if event is None:
            # Calendar-level headers can be ignored.
            continue
        if ":" not in line:
            raise ValueError("Invalid iCalendar property")
        name, value = line.split(":", 1)
        name = name.upper()
        if name in event:
            event[name].append(value)
        else:
            event[name] = [value]
    if event is not None:
        raise ValueError("Unclosed VEVENT")
    return entries


def import_page():
    return (
        '<h1>Import iCalendar appointments</h1>'
        '<p><a href="/calendar">← Calendar</a></p>'
        '<p>Only one-day, all-day events are accepted. Timed appointments, '
        'recurrences and alarms are rejected rather than guessed. '
        'Your CSV is not modified until you confirm the preview.</p>'
        '<form method="post" action="/calendar-import-preview" accept-charset="utf-8">'
        '<label>Select an .ics file (loaded locally in your browser) '
        '<input id="ics-file" type="file" accept=".ics,text/calendar"></label>'
        '<p><label>Or paste the contents of an .ics file<br>'
        '<textarea id="ics-data" name="ics" required maxlength="131072" '
        'style="width:100%;min-height:180px"></textarea></label></p>'
        '<button type="submit">Preview Import</button></form>'
        '<script>'
        'document.getElementById("ics-file").addEventListener("change",async(e)=>{'
        'const file=e.target.files[0];if(!file)return;'
        'if(file.size>131072){alert("iCalendar file too large");return;}'
        'document.getElementById("ics-data").value=await file.text();'
        '});</script>'
    )


def import_preview_page(entries, source, revision, csrf):
    output = ['<h1>Preview iCalendar import</h1>',
              '<p><a href="/calendar-import">← Cancel and return</a></p>',
              '<p>Nothing has been imported. These entries will be appended as '
              'appointments; exact duplicates are skipped.</p>']
    for item in entries[:MAX_ICS_EVENTS]:
        output.append('<p><strong>' + escape(item["date"]) + '</strong>: '
                      + escape(item["text"][:250]) + '</p>')
    output.append(
        '<form method="post" action="/calendar-import" accept-charset="utf-8">'
        '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
        '<input type="hidden" name="revision" value="' + escape(revision, quote=True) + '">'
        '<textarea name="ics" hidden>' + escape(source) + '</textarea>'
        '<button type="submit">Confirm Import (' + str(len(entries))
        + ' entries)</button></form>')
    return "".join(output)
