"""Calendar month and diary day browser views, independent of legacy DB."""
from __future__ import annotations

import calendar
from datetime import date
from html import escape
from urllib.parse import urlencode
from .diary_markup import render_diary


def appointment_meta(entry):
    """Readable, escaped optional time and location metadata."""
    details = []
    if entry.get("start_time"):
        details.append(entry["start_time"] + "–" + entry["end_time"]
                       + " (" + entry["timezone"] + ")")
    if entry.get("location"):
        details.append(entry["location"])
    return ('<small>' + escape(" · ".join(details)) + '</small>') if details else ""


def _url(route, **params):
    return "/" + route + "?" + urlencode(params)


def _month_offset(year, month, step):
    number = year * 12 + month - 1 + step
    target_year, target_month = divmod(number, 12)
    if target_year < 2 or target_year > 9998:
        return None
    return target_year, target_month + 1


def month_page(store, year, month):
    if not 2 <= year <= 9998 or not 1 <= month <= 12:
        raise ValueError("Invalid calendar month")
    month_events = {}
    for entry in store.in_month(year, month):
        month_events.setdefault(entry["date"], []).append(entry)
    today = date.today()
    nav = ['<p><a href="/listing?path=.">← Files</a> · '
           '<a href="/diary-search">Search Diary</a> · '
           '<a href="/diary-agenda">Agenda</a> · '
           '<a href="/calendar-export?kind=appointment">Export appointments (.ics)</a> · '
           '<a href="/calendar-import">Import appointments (.ics)</a> · ',
           '<a href="' + escape(_url("calendar", year=today.year, month=today.month), quote=True) + '">Today</a>']
    for title, offset in (("Previous month", -1), ("Next month", 1)):
        shifted = _month_offset(year, month, offset)
        if shifted:
            nav.append(' · <a href="' + escape(_url("calendar", year=shifted[0], month=shifted[1]), quote=True) + '">' + title + '</a>')
    nav.append('</p>')
    weekdays = [calendar.day_abbr[(i + 6) % 7] for i in range(7)]
    table = ['<table border="1" style="width:100%;table-layout:fixed"><thead><tr>']
    table.extend('<th>' + escape(day) + '</th>' for day in weekdays)
    table.append('</tr></thead><tbody>')
    for week in calendar.Calendar(firstweekday=6).monthdatescalendar(year, month):
        table.append('<tr>')
        for day in week:
            key = day.isoformat()
            events = month_events.get(key, [])
            label = str(day.day)
            href = escape(_url("diary", date=key), quote=True)
            is_today = day == today
            style = ('height:90px;background:#ffca55;color:#332000;'
                     'font-weight:700'
                     if is_today else
                     ('height:90px;opacity:.5' if day.month != month
                      else 'height:90px'))
            today_marker = (' <strong style="color:#703400">● Today</strong>'
                            if is_today else '')
            current_attr = ' aria-current="date"' if is_today else ''
            # Render complete source before clipping the visual preview: cutting
            # raw Markdown/HTML would expose syntax and can break formatting.
            shown = ''.join(
                '<div class="calendar-entry" style="font-size:.78em;'
                'line-height:1.25;max-height:7em;overflow:auto;'
                'overflow-wrap:anywhere;margin:.2em 0">'
                + appointment_meta(item) + render_diary(item["text"]) + '</div>'
                for item in events[:2])
            if len(events) > 2:
                shown += '<small>+' + str(len(events) - 2) + ' more</small>'
            table.append('<td valign="top" style="' + style + '">'
                         + '<a href="' + href + '"' + current_attr
                         + ' style="' + ('color:#332000' if is_today else '')
                         + '">' + label + '</a>' + today_marker + shown + '</td>')
        table.append('</tr>')
    table.append('</tbody></table>')
    return ('<h1>Calendar — ' + escape(calendar.month_name[month]) + ' ' + str(year)
            + '</h1>' + ''.join(nav) + ''.join(table)
            + '<p>Choose a date to view or add diary entries and appointments.</p>')


def day_page(store, day, csrf):
    from ..storage.calendar_diary import valid_date
    valid_date(day)
    items = [(index, entry) for index, entry in enumerate(store.read())
             if entry["date"] == day]
    month_url = _url("calendar", year=int(day[:4]), month=int(day[5:7]))
    rows = []
    for index, entry in items:
        edit_url = escape(_url("diary-edit", date=day, row=index), quote=True)
        delete_url = escape(_url("diary-delete", date=day, row=index), quote=True)
        rows.append(
            '<li><strong>' + escape(entry["kind"].title()) + '</strong>: '
            + appointment_meta(entry) + render_diary(entry["text"]) + ' '
            + '<small><a href="' + edit_url + '">Edit</a> · '
            + '<a href="' + delete_url + '">Delete…</a></small></li>')
    form = ('<form method="post" action="/diary" accept-charset="utf-8">'
            '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
            '<input type="hidden" name="date" value="' + escape(day, quote=True) + '">'
            '<p><small>Entries support Markdown and safe HTML formatting (headings, lists, links, emphasis). Scripts and event handlers are not allowed.</small></p>'
            '<label>Entry type <select name="kind">'
            '<option value="diary">Diary</option>'
            '<option value="appointment">Appointment</option></select></label> '
            '<fieldset><legend>Appointment time and place (optional)</legend>'
            '<p><label>Start <input type="time" name="start_time"></label> '
            '<label>End <input type="time" name="end_time"></label></p>'
            '<p><label>Timezone (IANA, e.g. America/Chicago) '
            '<input name="timezone" maxlength="100"></label></p>'
            '<p><label>Location <input name="location" maxlength="500"></label></p>'
            '<small>Leave all fields empty for an all-day entry. '
            'Timed appointments require start, end and timezone; '
            'end must be later on the same date.</small>'
            '</fieldset>'
            '<p><label>Entry<br><textarea name="text" required maxlength="4000" '
            'style="min-height:110px"></textarea></label></p>'
            '<button type="submit" formaction="/diary-preview">Preview</button> <button type="submit">Add Entry</button></form>')
    return ('<p><a href="' + escape(month_url, quote=True) + '">← Calendar</a>'
            ' · <a href="/diary-search">Search Diary</a>'
            ' · <a href="/diary-agenda">Agenda</a></p>'
            '<h1>' + escape(day) + '</h1><h2>Diary and appointments</h2>'
            + ('<ul>' + ''.join(rows) + '</ul>' if items else '<p>No entries yet.</p>')
            + form)


def entry_edit_page(store, day, index, csrf):
    """Render an explicit, revision-protected edit form for one CSV row."""
    entry = store.record(index, expected_day=day)
    revision = store.revision()
    back = escape(_url("diary", date=day), quote=True)
    kind_select = ('<select name="kind">'
                   + ''.join('<option value="' + escape(kind) + '"'
                             + (' selected' if entry["kind"] == kind else '') + '>'
                             + escape(kind.title()) + '</option>'
                             for kind in ("diary", "appointment"))
                   + '</select>')
    return (
        '<p><a href="' + back + '">← Back to diary</a></p>'
        '<h1>Edit calendar entry</h1>'
        '<form method="post" action="/diary-edit" accept-charset="utf-8">'
        '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
        '<input type="hidden" name="date" value="' + escape(day, quote=True) + '">'
        '<input type="hidden" name="row" value="' + str(index) + '">'
        '<input type="hidden" name="revision" value="' + escape(revision, quote=True) + '">'
        '<p><label>Date <input type="date" name="new_date" required value="'
        + escape(entry["date"], quote=True) + '"></label></p>'
        '<p><label>Entry type ' + kind_select + '</label></p>'
        '<p><small>Markdown and safe HTML are displayed when viewing the diary; the source stays editable.</small></p>'
        + '<fieldset><legend>Appointment time and place (optional)</legend>'
        + '<p><label>Start <input type="time" name="start_time" value="'
        + escape(entry.get("start_time", ""), quote=True) + '"></label> '
        + '<label>End <input type="time" name="end_time" value="'
        + escape(entry.get("end_time", ""), quote=True) + '"></label></p>'
        + '<p><label>Timezone (IANA, e.g. America/Chicago) '
        + '<input name="timezone" maxlength="100" value="'
        + escape(entry.get("timezone", ""), quote=True) + '"></label></p>'
        + '<p><label>Location <input name="location" maxlength="500" value="'
        + escape(entry.get("location", ""), quote=True) + '"></label></p>'
        + '<small>For all-day entries leave all fields empty. Timed entries need '
        + 'start, end and timezone; the end must be later on the same day.</small>'
        + '</fieldset>'
        + '<p><label>Text<br><textarea name="text" required maxlength="4000" '
        'style="min-height:110px">' + escape(entry["text"]) + '</textarea></label></p>'
        '<button type="submit" formaction="/diary-preview">Preview</button> <button type="submit">Save Changes</button></form>'
        '<p>Changes made elsewhere since opening this form prevent saving.</p>'
    )


def entry_delete_page(store, day, index, csrf):
    """A GET displays confirmation; deletion only happens on an explicit POST."""
    entry = store.record(index, expected_day=day)
    revision = store.revision()
    back = escape(_url("diary", date=day), quote=True)
    return (
        '<p><a href="' + back + '">← Cancel and return</a></p>'
        '<h1>Delete calendar entry?</h1>'
        '<p><strong>' + escape(entry["kind"].title()) + '</strong> — '
        + escape(day) + '</p>'
        '<blockquote>' + escape(entry["text"]).replace("\n", "<br>") + '</blockquote>'
        '<form method="post" action="/diary-delete" accept-charset="utf-8">'
        '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
        '<input type="hidden" name="date" value="' + escape(day, quote=True) + '">'
        '<input type="hidden" name="row" value="' + str(index) + '">'
        '<input type="hidden" name="revision" value="' + escape(revision, quote=True) + '">'
        '<button type="submit">Confirm Delete</button></form>'
    )
