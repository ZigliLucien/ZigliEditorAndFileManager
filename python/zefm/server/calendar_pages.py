"""Calendar month and diary day browser views, independent of legacy DB."""
from __future__ import annotations

import calendar
from datetime import date
from html import escape
from urllib.parse import urlencode


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
    nav = ['<p><a href="/listing?path=.">← Files</a> · ',
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
            style = 'height:90px;opacity:.5' if day.month != month else 'height:90px'
            shown = ''.join('<div><small>' + escape(item["text"][:70])
                            + ('…' if len(item["text"]) > 70 else '') + '</small></div>'
                            for item in events[:2])
            if len(events) > 2:
                shown += '<small>+' + str(len(events) - 2) + ' more</small>'
            table.append('<td valign="top" style="' + style + '">'
                         + '<a href="' + href + '">' + label + '</a>' + shown + '</td>')
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
            + escape(entry["text"]).replace("\n", "<br>") + ' '
            + '<small><a href="' + edit_url + '">Edit</a> · '
            + '<a href="' + delete_url + '">Delete…</a></small></li>')
    form = ('<form method="post" action="/diary" accept-charset="utf-8">'
            '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
            '<input type="hidden" name="date" value="' + escape(day, quote=True) + '">'
            '<label>Entry type <select name="kind">'
            '<option value="diary">Diary</option>'
            '<option value="appointment">Appointment</option></select></label> '
            '<p><label>Entry<br><textarea name="text" required maxlength="4000" '
            'style="min-height:110px"></textarea></label></p>'
            '<button type="submit">Add Entry</button></form>')
    return ('<p><a href="' + escape(month_url, quote=True) + '">← Calendar</a></p>'
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
        '<p><label>Text<br><textarea name="text" required maxlength="4000" '
        'style="min-height:110px">' + escape(entry["text"]) + '</textarea></label></p>'
        '<button type="submit">Save Changes</button></form>'
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
