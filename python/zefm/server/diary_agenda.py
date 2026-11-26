"""Read-only upcoming agenda built from ZEFM's calendar CSV."""
from __future__ import annotations

from datetime import date, timedelta
from html import escape
from urllib.parse import urlencode

from .diary_markup import render_diary
from .calendar_pages import appointment_meta, entry_time_key, display_entry, default_appointment_timezone

MAX_AGENDA_RESULTS = 100
WINDOWS = (7, 30, 90)
KINDS = {"all", "diary", "appointment"}


def upcoming_entries(store, *, days=30, kind="all", today=None):
    """Return at most 100 entries, earliest dates first, including today.

    Timed events are grouped by their converted viewing-zone date.
    """
    if type(days) is not int or days not in WINDOWS:
        raise ValueError("Agenda window must be 7, 30 or 90 days")
    if kind not in KINDS:
        raise ValueError("Invalid agenda entry type")
    start = today if today is not None else date.today()
    end = start + timedelta(days=days - 1)
    matches = [
        (index, entry) for index, entry in enumerate(store.read())
        if start.isoformat() <= display_entry(entry)["date"] <= end.isoformat()
        and (kind == "all" or entry["kind"] == kind)
    ]
    # Sort by date then time; stable ordering retains original CSV position
    # for entries with the same date and time (including all-day entries).
    matches.sort(key=lambda pair: (
        display_entry(pair[1])["date"],
        *entry_time_key(display_entry(pair[1]))))
    return matches[:MAX_AGENDA_RESULTS], len(matches), start, end


def agenda_page(store, *, days=30, kind="all", today=None):
    matches, count, start, end = upcoming_entries(
        store, days=days, kind=kind, today=today)
    options = "".join(
        f'<option value="{window}"' + (" selected" if window == days else "")
        + f'>{window} days</option>' for window in WINDOWS)
    types = "".join(
        f'<option value="{value}"' + (" selected" if value == kind else "")
        + f'>{label}</option>'
        for value, label in (("all", "All entries"), ("appointment", "Appointments"),
                             ("diary", "Diary")))
    header = (
        '<h1>Calendar Agenda</h1>'
        '<p><a href="/calendar">← Monthly calendar</a> · '
        '<a href="/diary-search">Search Diary</a></p>'
        '<form method="get" action="/diary-agenda">'
        '<label>Upcoming <select name="days">' + options + '</select></label> '
        '<label>Type <select name="kind">' + types + '</select></label> '
        '<button type="submit">Show Agenda</button></form>'
        '<p>From ' + escape(start.isoformat()) + ' through '
        + escape(end.isoformat()) + ' (inclusive). '
        'Times and dates are shown in ' + escape(default_appointment_timezone())
        + '; all-day entries come first on each date.</p>'
    )
    if not matches:
        return header + '<p>No entries in this period.</p>'
    parts = []
    current_date = None
    for index, entry in matches:
        shown = display_entry(entry)
        if shown["date"] != current_date:
            if current_date is not None:
                parts.append("</ul>")
            current_date = shown["date"]
            day_url = "/diary?" + urlencode({"date": current_date})
            parts.append('<h2><a href="' + escape(day_url, quote=True) + '">'
                         + escape(current_date) + "</a></h2><ul>")
        edit_url = "/diary-edit?" + urlencode({"date": entry["date"], "row": index})
        parts.append(
            '<li style="margin:.5em 0;padding:.3em 0">'
            '<strong>' + escape(entry["kind"].title()) + '</strong> · '
            '<a href="' + escape(edit_url, quote=True) + '">Edit</a>'
            '<div style="overflow-wrap:anywhere;max-height:12em;overflow:auto">'
            + appointment_meta(entry) + render_diary(entry["text"]) + "</div></li>")
    parts.append("</ul>")
    summary = (f'<p>{count} upcoming entr{"y" if count == 1 else "ies"}'
               + (f" (showing the first {MAX_AGENDA_RESULTS})"
                  if count > MAX_AGENDA_RESULTS else "") + ".</p>")
    return header + summary + "".join(parts)
