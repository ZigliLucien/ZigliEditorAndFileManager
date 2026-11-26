"""Read-only weekly calendar rendered in the configured viewing timezone.

An appointment's displayed date can differ from its CSV date. All navigation
uses local display dates; edit links deliberately use original CSV row/date.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from html import escape
from urllib.parse import urlencode

from .calendar_pages import (
    appointment_meta, default_appointment_timezone, display_entry, entry_time_key,
)
from .diary_markup import render_diary
from .appointment_conflicts import conflicting_rows
from ..storage.calendar_diary import valid_date

DAYS_PER_WEEK = 7
MAX_WEEK_ENTRIES = 200


def week_start(anchor=None):
    """Monday on or before anchor; invalid dates are rejected."""
    if anchor is None:
        value = date.today()
    elif isinstance(anchor, date) and not isinstance(anchor, datetime):
        value = anchor
    else:
        value = date.fromisoformat(valid_date(anchor))
    return value - timedelta(days=value.weekday())


def week_entries(store, anchor=None):
    """Return (Monday, date-indexed rows, total), never modifying CSV."""
    start = week_start(anchor)
    end = start + timedelta(days=DAYS_PER_WEEK - 1)
    indexed = { (start + timedelta(days=i)).isoformat(): []
               for i in range(DAYS_PER_WEEK) }
    total = 0
    for index, entry in enumerate(store.read()):
        local = display_entry(entry)
        day = local["date"]
        if start.isoformat() <= day <= end.isoformat():
            total += 1
            if total <= MAX_WEEK_ENTRIES:
                indexed[day].append((index, entry, local))
    for items in indexed.values():
        items.sort(key=lambda record: entry_time_key(record[2]))
    return start, indexed, total


def _nav(start):
    links = ['<a href="/calendar">Monthly calendar</a>',
             '<a href="/diary-agenda">Agenda</a>']
    for text, delta in (("Previous week", -7), ("Next week", 7)):
        try:
            target = (start + timedelta(days=delta)).isoformat()
        except OverflowError:
            continue
        links.append('<a href="/calendar-week?' +
                     escape(urlencode({"date": target}), quote=True) +
                     '">' + escape(text) + '</a>')
    links.append('<a href="/calendar-week">Current week</a>')
    return '<nav><p>' + ' · '.join(links) + '</p></nav>'


def week_page(store, anchor=None):
    start, rows, count = week_entries(store, anchor)
    source_rows = store.read()
    conflicts = conflicting_rows(source_rows)
    end = start + timedelta(days=DAYS_PER_WEEK - 1)
    result = [
        '<h1>Weekly Calendar</h1>',
        _nav(start),
        '<p>' + escape(start.isoformat()) + ' through ' +
        escape(end.isoformat()) + ' · Display time zone: ' +
        escape(default_appointment_timezone()) +
        '. All-day entries come first, then appointments by local time.</p>',
    ]
    for iso_day, entries in rows.items():
        current = date.fromisoformat(iso_day)
        day_url = '/diary?' + urlencode({"date": iso_day})
        result.append('<section style="border-top:1px solid #bbb;padding:.65em 0">'
                      '<h2><a href="' + escape(day_url, quote=True) + '">' +
                      escape(current.strftime("%A, %B %d")) +
                      '</a></h2>')
        if not entries:
            result.append('<p><small>No entries</small></p></section>')
            continue
        result.append('<ul>')
        for index, original, shown in entries:
            edit = '/diary-edit?' + urlencode({
                "date": original["date"], "row": index})
            share = '/calendar-export-one?' + urlencode({
                "date": original["date"], "row": index})
            share_link = (' · <a href="' + escape(share, quote=True) +
                          '">Download .ics</a>'
                          if original["kind"] == "appointment" else "")
            warning = ""
            if index in conflicts:
                other_index = conflicts[index]
                other = source_rows[other_index]
                other_link = '/diary-edit?' + urlencode({
                    "date": other["date"], "row": other_index})
                warning = (' <small role="status">⚠ Overlaps another appointment'
                           ' (<a href="' + escape(other_link, quote=True) +
                           '">view other</a>)</small>')
            result.append(
                '<li style="padding:.35em 0;overflow-wrap:anywhere">'
                '<strong>' + escape(original["kind"].title()) + '</strong> · ' +
                appointment_meta(original) + warning +
                '<div>' + render_diary(original["text"]) + '</div>'
                '<small><a href="' + escape(edit, quote=True) +
                '">Edit</a>' + share_link + '</small></li>')
        result.append('</ul></section>')
    if count > MAX_WEEK_ENTRIES:
        result.append('<p>Showing the first ' + str(MAX_WEEK_ENTRIES) +
                      ' of ' + str(count) + ' entries this week.</p>')
    else:
        result.append('<p>' + str(count) + ' entr' +
                      ('y' if count == 1 else 'ies') + ' this week.</p>')
    return ''.join(result)
