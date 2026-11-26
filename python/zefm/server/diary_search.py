"""Read-only calendar/diary search, with bounded results and safe HTML output."""
from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from .diary_markup import render_diary
from .calendar_pages import appointment_meta, display_entry
from ..storage.calendar_diary import valid_date

MAX_QUERY = 200
MAX_RESULTS = 100


def find_entries(store, query="", start="", end="", kind="all"):
    """Case-insensitive literal substring search over stored Markdown source."""
    if len(query) > MAX_QUERY:
        raise ValueError("Search text exceeds 200 characters")
    if kind not in {"all", "diary", "appointment"}:
        raise ValueError("Invalid entry type")
    if start:
        valid_date(start)
    if end:
        valid_date(end)
    if start and end and start > end:
        raise ValueError("Start date must be on or before end date")
    needle = query.casefold()
    matches = [
        (index, entry) for index, entry in enumerate(store.read())
        if (not needle or needle in entry["text"].casefold())
        and (kind == "all" or entry["kind"] == kind)
        and (not start or display_entry(entry)["date"] >= start)
        and (not end or display_entry(entry)["date"] <= end)
    ]
    # Newest dates first, preserving CSV row order within each date.
    matches.sort(key=lambda pair: display_entry(pair[1])["date"], reverse=True)
    return matches[:MAX_RESULTS], len(matches)


def search_page(store, query="", start="", end="", kind="all"):
    results, count = find_entries(store, query, start, end, kind)
    options = "".join(
        '<option value="' + value + '"' + (" selected" if value == kind else "")
        + ">" + label + "</option>"
        for value, label in (("all", "All entries"), ("diary", "Diary"),
                             ("appointment", "Appointments")))
    form = (
        '<h1>Search Calendar / Diary</h1>'
        '<p><a href="/calendar">← Calendar</a></p>'
        '<form method="get" action="/diary-search" accept-charset="utf-8">'
        '<label>Search text <input type="search" name="q" maxlength="200" '
        'value="' + escape(query, quote=True) + '"></label> '
        '<label>From <input type="date" name="from" value="'
        + escape(start, quote=True) + '"></label> '
        '<label>Through <input type="date" name="to" value="'
        + escape(end, quote=True) + '"></label> '
        '<label>Type <select name="kind">' + options + '</select></label> '
        '<button type="submit">Search</button></form>')
    if not (query or start or end or kind != "all"):
        return form + '<p>Enter search text, a date range, or an entry type.</p>'
    cards = []
    for index, entry in results:
        shown = display_entry(entry)
        day_url = "/diary?" + urlencode({"date": shown["date"]})
        edit_url = "/diary-edit?" + urlencode({"date": entry["date"], "row": index})
        share_link = ""
        if entry["kind"] == "appointment":
            share_url = "/calendar-export-one?" + urlencode({
                "date": entry["date"], "row": index})
            share_link = (' · <a href="' + escape(share_url, quote=True)
                          + '">Download .ics</a>')
        cards.append(
            '<li style="margin:1em 0;padding:.5em;border-bottom:1px solid #bbb">'
            '<strong><a href="' + escape(day_url, quote=True) + '">'
            + escape(shown["date"]) + '</a> — '
            + escape(entry["kind"].title()) + '</strong> '
            '<small><a href="' + escape(edit_url, quote=True)
            + '">Edit</a>' + share_link + '</small>'
            '<div style="max-height:12em;overflow:auto;overflow-wrap:anywhere">'
            + appointment_meta(entry) + render_diary(entry["text"]) + '</div></li>')
    summary = (f'<p>{count} matching entr{"y" if count == 1 else "ies"}'
               + (f" (showing the first {MAX_RESULTS})" if count > MAX_RESULTS else "")
               + '.</p>')
    return form + summary + '<ol>' + ''.join(cards) + '</ol>'
