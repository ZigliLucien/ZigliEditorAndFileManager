"""Weekly browser calendar: local-time ordering, navigation, safe edit links."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import urlopen
from unittest.mock import patch
import unittest

from zefm.server.week_calendar import week_start, week_entries, week_page
from zefm.server.calendar_pages import day_page, month_page
from zefm.server.http import BrowserServer
from zefm.storage.calendar_diary import CalendarDiary


class WeeklyCalendarTests(unittest.TestCase):
    def make_store(self, root):
        store = CalendarDiary(Path(root) / "calendar.csv")
        # CSV deliberately out of chronological order.
        store.add("2026-07-01", "Afternoon Central", "appointment",
                  start_time="15:00", end_time="16:00",
                  timezone="America/Chicago")
        store.add("2026-07-01", "Midnight Eastern", "appointment",
                  start_time="00:30", end_time="01:30",
                  timezone="America/New_York")
        store.add("2026-06-30", "Early Central", "appointment",
                  start_time="08:00", end_time="09:00",
                  timezone="America/Chicago")
        store.add("2026-06-30", "All-day note")
        return store

    def test_anchor_monday_navigation_and_boundary(self):
        self.assertEqual(week_start("2026-07-01"), date(2026, 6, 29))
        self.assertEqual(week_start(date(2026, 6, 29)), date(2026, 6, 29))
        with self.assertRaises(ValueError):
            week_start("2026-02-30")
        with TemporaryDirectory() as tmp:
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            html = week_page(store, "2026-07-01")
            self.assertIn("2026-06-29 through 2026-07-05", html)
            self.assertIn("calendar-week?date=2026-06-22", html)
            self.assertIn("calendar-week?date=2026-07-06", html)
            self.assertIn("No entries", html)

    def test_local_day_order_and_original_edit_row(self):
        with TemporaryDirectory() as tmp, patch.dict(
            "os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
            store = self.make_store(tmp)
            original = store.read()
            monday, indexed, total = week_entries(store, "2026-07-01")
            self.assertEqual(monday, date(2026, 6, 29))
            self.assertEqual(total, 4)
            self.assertEqual(
                [entry["text"] for _, entry, _ in indexed["2026-06-30"]],
                ["All-day note", "Early Central", "Midnight Eastern"])
            self.assertEqual(
                [entry["text"] for _, entry, _ in indexed["2026-07-01"]],
                ["Afternoon Central"])
            html = week_page(store, "2026-07-01")
            self.assertLess(html.index("All-day note"), html.index("Early Central"))
            self.assertLess(html.index("Early Central"), html.index("Midnight Eastern"))
            self.assertIn("23:30–00:30 (2026-07-01) CDT", html)
            self.assertIn("diary-edit?date=2026-07-01&amp;row=1", html)
            self.assertIn("diary-edit?date=2026-06-30&amp;row=2", html)
            self.assertEqual(store.read(), original)

    def test_prior_and_next_week_do_not_leak_entries(self):
        with TemporaryDirectory() as tmp:
            store = self.make_store(tmp)
            prior = week_page(store, "2026-06-25")
            current = week_page(store, "2026-07-01")
            next_week = week_page(store, "2026-07-07")
            self.assertNotIn("Midnight Eastern", prior)
            self.assertIn("Midnight Eastern", current)
            self.assertNotIn("Midnight Eastern", next_week)

    def test_month_day_navigation_contains_week_link(self):
        with TemporaryDirectory() as tmp:
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            self.assertIn('href="/calendar-week"', month_page(store, 2026, 7))
            self.assertIn('calendar-week?date=2026-07-01',
                          day_page(store, "2026-07-01", "token"))

    def test_http_week_view_and_invalid_params(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = self.make_store(tmp)
            server = BrowserServer(root, calendar_path=store.path)
            server.start()
            try:
                with urlopen(server.url + "calendar-week?date=2026-07-01",
                             timeout=5) as response:
                    html = response.read().decode("utf-8")
                self.assertIn("Weekly Calendar", html)
                self.assertIn("Midnight Eastern", html)
                for invalid in ("calendar-week?date=invalid",
                                "calendar-week?date=2026-02-30",
                                "calendar-week?unexpected=yes"):
                    with self.subTest(invalid=invalid):
                        with self.assertRaises(HTTPError) as error:
                            urlopen(server.url + invalid, timeout=5)
                        self.assertEqual(error.exception.code, 400)
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
