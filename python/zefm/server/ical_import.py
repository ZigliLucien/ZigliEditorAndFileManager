"""Conservative, two-phase iCalendar import into CSV-backed ZEFM appointments.

Only explicit all-day DTSTART;VALUE=DATE events are accepted. Timed,
recurring, or ambiguous events abort parsing instead of silently losing data.
Never reads remote URL, opens external files, or expands RRULE expressions.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from html import escape

from .calendar_pages import timezone_label, display_entry
from ..storage.calendar_diary import validated_record

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


def _event_times(event):
    """Parse either a date-only event or explicitly zoned same-day times."""
    if any(k in event for k in ("RRULE", "RDATE", "EXDATE", "RECURRENCE-ID", "DURATION")):
        raise ValueError("Recurring or duration-based events are not supported")
    starts = [key for key in event if key.startswith("DTSTART")]
    ends = [key for key in event if key.startswith("DTEND")]
    if len(starts) != 1 or len(event[starts[0]]) != 1 or len(ends) > 1:
        raise ValueError("Event must have one DTSTART and at most one DTEND")
    start_key = starts[0]
    raw_start = event[start_key][0]
    if start_key == "DTSTART;VALUE=DATE":
        if len(raw_start) != 8 or not raw_start.isascii() or not raw_start.isdecimal():
            raise ValueError("Invalid all-day DTSTART")
        try:
            day = datetime.strptime(raw_start, "%Y%m%d").date()
        except ValueError as exc:
            raise ValueError("Invalid all-day DTSTART") from exc
        if ends:
            if ends[0] != "DTEND;VALUE=DATE":
                raise ValueError("Incompatible all-day DTEND")
            try:
                day_end = datetime.strptime(event[ends[0]][0], "%Y%m%d").date()
            except ValueError as exc:
                raise ValueError("Invalid all-day DTEND") from exc
            if day_end != day + timedelta(days=1):
                raise ValueError("Multi-day events are not supported")
        return day.isoformat(), {}
    if start_key == "DTSTART" and raw_start.endswith("Z"):
        tzid = "UTC"
        start_value = raw_start[:-1]
        end_key = "DTEND"
        if not ends or ends[0] != end_key or not event[end_key][0].endswith("Z"):
            raise ValueError("UTC events require a matching UTC end time")
        end_value = event[end_key][0][:-1]
    elif start_key.startswith("DTSTART;TZID="):
        tzid = start_key.split("=", 1)[1]
        start_value = raw_start
        end_key = "DTEND;TZID=" + tzid
        if not ends or ends[0] != end_key:
            raise ValueError("Appointment timezone must match on start and end")
        end_value = event[end_key][0]
    else:
        raise ValueError("Timed events require UTC (Z) or an IANA TZID")
    try:
        first = datetime.strptime(start_value, "%Y%m%dT%H%M%S")
        last = datetime.strptime(end_value, "%Y%m%dT%H%M%S")
    except ValueError as exc:
        raise ValueError("Timed appointments require HHMMSS start and end") from exc
    if first.date() != last.date() or last <= first:
        raise ValueError("Only same-day positive-length appointments are supported")
    return first.date().isoformat(), {
        "start_time": first.strftime("%H:%M"),
        "end_time": last.strftime("%H:%M"),
        "timezone": tzid,
    }


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
    timezone_depth = 0
    for line in unfolded[1:-1]:
        upper = line.upper()
        if timezone_depth:
            if upper.startswith("BEGIN:"):
                timezone_depth += 1
            elif upper.startswith("END:"):
                timezone_depth -= 1
            continue
        if upper == "BEGIN:VTIMEZONE" and event is None:
            # Ignore embedded timezone definitions; use only a validated
            # IANA TZID and the system's zoneinfo rules, never execute data.
            timezone_depth = 1
            continue
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
            day, timing = _event_times(event)
            if event.get("STATUS", [""])[0].upper() == "CANCELLED":
                raise ValueError("Cancelled events cannot be imported")
            description = event.get("DESCRIPTION", [""])
            summary = event.get("SUMMARY", [""])
            if len(description) != 1 or len(summary) != 1:
                raise ValueError("Duplicate event summary or description")
            title = _text(summary[0])
            details = _text(description[0])
            # Preserve both fields without repeating ZEFM's own full-source
            # DESCRIPTION when its SUMMARY is derived from the first line.
            if not details:
                note = title
            elif not title or title.strip() in (details.splitlines()[0].strip(),
                                                 details.splitlines()[0].lstrip("# ").strip()):
                note = details
            else:
                note = title + "\n\n" + details
            location = event.get("LOCATION", [""])
            if len(location) != 1:
                raise ValueError("Duplicate LOCATION fields")
            if timing:
                timing["location"] = _text(location[0])
            entries.append(validated_record(day, "appointment", note, **timing))
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
        original_name = name
        name = name.upper()
        # Property/parameter NAMES are case-insensitive; an IANA TZID's
        # VALUE is case-sensitive. Do not turn America/Chicago into
        # AMERICA/CHICAGO, which zoneinfo cannot resolve.
        if name.startswith(("DTSTART;TZID=", "DTEND;TZID=")):
            name = name.split("=", 1)[0] + "=" + original_name.split("=", 1)[1]
        if name in event:
            event[name].append(value)
        else:
            event[name] = [value]
    if event is not None or timezone_depth:
        raise ValueError("Unclosed iCalendar component")
    return entries


def import_page(csrf, source="", filename=""):
    """Browser file chooser or prefilled local .ics source, with no auto-import."""
    return (
        '<h1>Import iCalendar invitation</h1>'
        '<p><a href="/calendar">← Calendar</a></p>'
        '<p>Choose an .ics file, or open one from the ZEFM file listing. '
        'Preview its dates, times, timezones and descriptions before importing. '
        'Only explicit single-day events are supported; ambiguous invitations '
        'and recurrence rules are rejected.</p>'
        '<form id="ical-import-form" method="post" action="/calendar-import-preview" '
        'accept-charset="utf-8">'
        '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
        '<p><label>Choose .ics invitation '
        '<input type="file" id="ical-file" accept=".ics,text/calendar"></label></p>'
        '<p><label>iCalendar text<br>'
        '<textarea id="ical-source" name="ics" required maxlength="131072" '
        'style="width:100%;min-height:180px">'
        + escape(source) + '</textarea></label></p>'
        '<button type="submit">Preview Invitation</button>'
        '</form><script defer src="/calendar-import.js"></script>'
        '<p><small>The file is read in your browser and sent only to the local '
        'ZEFM server for preview; it is not imported until you confirm.</small></p>'
    )


def import_preview_page(entries, source, revision, csrf):
    output = ['<h1>Preview iCalendar import</h1>',
              '<p><a href="/calendar-import">← Cancel and return</a></p>',
              '<p>Nothing has been imported. These entries will be appended as '
              'appointments; exact duplicates are skipped.</p>']
    for item in entries[:MAX_ICS_EVENTS]:
        time_info = ""
        if item.get("start_time"):
            shown = display_entry(item)
            end_date = (" (" + shown["_end_date"] + ")"
                        if shown.get("_end_date") else "")
            time_info = (" · " + escape(shown["date"]) + " "
                         + escape(shown["start_time"]) + "–"
                         + escape(shown["end_time"]) + escape(end_date) + " "
                         + escape(timezone_label(shown["date"], shown["start_time"],
                                                 shown["timezone"])))
        if item.get("location"):
            time_info += " · " + escape(item["location"])
        output.append('<p><strong>' + (escape(item["date"]) if not item.get("start_time")
                      else "Local") + time_info
                      + '</strong>: ' + escape(item["text"][:250]) + '</p>')
    output.append(
        '<form method="post" action="/calendar-import" accept-charset="utf-8">'
        '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
        '<input type="hidden" name="revision" value="' + escape(revision, quote=True) + '">'
        '<textarea name="ics" hidden>' + escape(source) + '</textarea>'
        '<button type="submit">Confirm Import (' + str(len(entries))
        + ' entries)</button></form>')
    return "".join(output)
