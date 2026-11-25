"""Agenda chronology, filtering, sanitization, and browser routing."""
import tempfile
import unittest
from datetime import date
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from zefm.server.calendar_pages import month_page, day_page
from zefm.server.diary_agenda import agenda_page, upcoming_entries, MAX_AGENDA_RESULTS
from zefm.server.http import BrowserServer
from zefm.storage.calendar_diary import CalendarDiary


class AgendaTests(unittest.TestCase):
    def test_inclusive_window_order_and_kind(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "calendar.csv")
            store.add("2026-11-30", "later", "appointment")
            store.add("2026-11-25", "**today**", "diary")
            store.add("2026-11-24", "yesterday", "appointment")
            store.add("2026-12-01", "outside a seven-day window")
            entries, count, first, last = upcoming_entries(
                store, days=7, today=date(2026, 11, 25))
            self.assertEqual((str(first), str(last)), ("2026-11-25", "2026-12-01"))
            self.assertEqual(count, 3)
            self.assertEqual([entry["date"] for _, entry in entries],
                             ["2026-11-25", "2026-11-30", "2026-12-01"])
            only_appointments, count, _, _ = upcoming_entries(
                store, days=7, kind="appointment", today=date(2026, 11, 25))
            self.assertEqual(count, 1)
            self.assertEqual(only_appointments[0][1]["text"], "later")
            html = agenda_page(store, days=7, today=date(2026, 11, 25))
            self.assertIn("<strong>today</strong>", html)
            self.assertNotIn("yesterday", html)
            self.assertLess(html.index("2026-11-25</a>"), html.index("2026-11-30</a>"))

    def test_safe_html_and_source_links(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "calendar.csv")
            store.add("2026-11-25", '<script>alert(1)</script><b onclick="bad()">Safe</b>')
            html = agenda_page(store, today=date(2026, 11, 25))
            self.assertIn("<b>Safe</b>", html)
            self.assertNotIn("<script", html)
            self.assertNotIn("onclick=", html)
            self.assertNotIn("alert(1)", html)
            self.assertIn("diary?date=2026-11-25", html)
            self.assertIn("diary-edit?date=2026-11-25&amp;row=0", html)

    def test_empty_result_and_rejected_options(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "calendar.csv")
            self.assertIn("No entries in this period.",
                          agenda_page(store, today=date(2026, 11, 25)))
            for opts in ({"days": 1}, {"days": 1000}, {"days": "30"},
                         {"kind": "invalid"}):
                with self.subTest(opts=opts):
                    with self.assertRaises(ValueError):
                        upcoming_entries(store, **opts)

    def test_result_cap_and_navigation_links(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "calendar.csv")
            store.append_many([
                {"date": "2026-11-26", "kind": "diary", "text": f"entry {i}"}
                for i in range(MAX_AGENDA_RESULTS + 3)])
            result, count, _, _ = upcoming_entries(store, today=date(2026, 11, 25))
            self.assertEqual(count, MAX_AGENDA_RESULTS + 3)
            self.assertEqual(len(result), MAX_AGENDA_RESULTS)
            self.assertIn("showing the first 100",
                          agenda_page(store, today=date(2026, 11, 25)))
            self.assertIn('href="/diary-agenda"', month_page(store, 2026, 11))
            self.assertIn('href="/diary-agenda"',
                          day_page(store, "2026-11-25", "csrf"))


class AgendaHttpTests(unittest.TestCase):
    def test_http_filter_and_parameter_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = CalendarDiary(root / "calendar.csv")
            store.add(date.today().isoformat(), "today's appointment", "appointment")
            server = BrowserServer(root, calendar_path=store.path)
            server.start()
            try:
                with urlopen(server.url + "diary-agenda?" +
                             urlencode({"days": "7", "kind": "appointment"}),
                             timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    html = response.read().decode("utf-8")
                self.assertIn("today&#x27;s appointment", html)
                for bad in ("diary-agenda?days=abc", "diary-agenda?days=365",
                            "diary-agenda?kind=garbage", "diary-agenda?unknown=1"):
                    with self.assertRaises(HTTPError) as error:
                        urlopen(server.url + bad, timeout=5)
                    self.assertEqual(error.exception.code, 400)
                self.assertEqual(len(store.read()), 1)
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
