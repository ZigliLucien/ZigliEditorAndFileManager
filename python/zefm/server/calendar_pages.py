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
    if target_year < 1 or target_year > 9999:
        return None
    return target_year, target_month + 1


def month_page(store, year, month):
    if not 1 <= year <= 9999 or not 1 <= month <= 12:
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
            muted = ' style="opacity:.5"' if day.month != month else ''
            shown = ''.join('<div><small>' + escape(item["text"][:70])
                            + ('…' if len(item["text"]) > 70 else '') + '</small></div>'
                            for item in events[:2])
            if len(events) > 2:
                shown += '<small>+' + str(len(events) - 2) + ' more</small>'
            table.append('<td valign="top"' + muted + ' style="height:90px"'
                         if not muted else '<td valign="top"' + muted)
            table.append('><a href="' + href + '">' + label + '</a>' + shown + '</td>')
        table.append('</tr>')
    table.append('</tbody></table>')
    return ('<h1>Calendar — ' + escape(calendar.month_name[month]) + ' ' + str(year)
            + '</h1>' + ''.join(nav) + ''.join(table)
            + '<p>Choose a date to view or add diary entries and appointments.</p>')


def day_page(store, day, csrf):
    from ..storage.calendar_diary import valid_date
    valid_date(day)
    items = store.on_day(day)
    month_url = _url("calendar", year=int(day[:4]), month=int(day[5:7]))
    rows = ''.join('<li><strong>' + escape(entry["kind"].title()) + '</strong>: '
                   + escape(entry["text"]).replace("\n", "<br>") + '</li>'
                   for entry in items)
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
            + ('<ul>' + rows + '</ul>' if items else '<p>No entries yet.</p>')
            + form)
