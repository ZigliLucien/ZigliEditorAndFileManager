"""Share exactly one appointment as an iCalendar attachment."""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import urlopen
import re
import unittest

from zefm.server.ical_export import export_ical
from zefm.server.calendar_pages import day_page
from zefm.server.week_calendar import week_page
from zefm.server.diary_agenda import agenda_page
from zefm.server.diary_search import search_page
from datetime import date
from unittest.mock import patch
from zefm.server.http import BrowserServer
from zefm.server.ical_import import parse_ics
from zefm.storage.calendar_diary import CalendarDiary


class SingleIcsExportTests(unittest.TestCase):
    def build(self, root):
        store = CalendarDiary(Path(root) / "calendar.csv")
        store.add("2026-07-01", "Private diary entry", "diary")
        store.add("2026-07-01", "Eastern appointment", "appointment",
                  start_time="15:00", end_time="16:00",
                  timezone="America/New_York", location="Conference room")
        store.add("2026-07-01", "Other appointment", "appointment",
                  start_time="18:00", end_time="19:00",
                  timezone="America/Chicago")
        return store

    def test_export_exactly_one_and_preserve_original_timezone(self):
        with TemporaryDirectory() as tmp:
            store = self.build(tmp)
            before = store.revision()
            data = export_ical(store, row_index=1)
            text = data.decode("utf-8")
            self.assertEqual(text.count("BEGIN:VEVENT"), 1)
            self.assertIn("SUMMARY:Eastern appointment", text)
            self.assertIn("DTSTART;TZID=America/New_York:20260701T150000", text)
            self.assertIn("DTEND;TZID=America/New_York:20260701T160000", text)
            self.assertIn("LOCATION:Conference room", text)
            self.assertNotIn("Private diary entry", text)
            self.assertNotIn("Other appointment", text)
            self.assertEqual(parse_ics(text)[0]["timezone"], "America/New_York")
            self.assertEqual(store.revision(), before)

    def test_single_export_uid_matches_full_export_even_with_duplicate(self):
        with TemporaryDirectory() as tmp:
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            for _ in range(2):
                store.add("2026-07-01", "same appointment", "appointment",
                          start_time="09:00", end_time="10:00",
                          timezone="America/Chicago")
            full = export_ical(store).decode("utf-8")
            uids = re.findall(r"^UID:([^\r\n]+)", full, re.MULTILINE)
            self.assertEqual(len(uids), 2)
            self.assertNotEqual(uids[0], uids[1])
            for row, expected in enumerate(uids):
                single = export_ical(store, row_index=row).decode("utf-8")
                self.assertIn("UID:" + expected, single)

    def test_agenda_and_search_offer_source_safe_single_export(self):
        with TemporaryDirectory() as tmp, patch.dict(
            "os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            store.add("2026-07-01", "Private diary", "diary")
            # This Eastern start is June 30 in the Central display zone.
            store.add("2026-07-01", "Late Eastern", "appointment",
                      start_time="00:30", end_time="01:30",
                      timezone="America/New_York")
            store.add("2026-06-30", "Morning Central", "appointment",
                      start_time="09:00", end_time="10:00",
                      timezone="America/Chicago")
            before = store.read()
            link = 'calendar-export-one?date=2026-07-01&amp;row=1'
            agenda = agenda_page(store, days=7, today=date(2026, 6, 30))
            search = search_page(store, query="Late Eastern",
                                 start="2026-06-30", end="2026-06-30")
            self.assertIn(link, agenda)
            self.assertIn(link, search)
            self.assertIn('diary?date=2026-06-30', search)
            self.assertEqual(agenda.count("Download .ics"), 2)
            self.assertEqual(search.count("Download .ics"), 1)
            self.assertEqual(store.read(), before)

    def test_search_does_not_offer_private_diary_as_ics(self):
        with TemporaryDirectory() as tmp:
            store = self.build(tmp)
            diary_search = search_page(store, query="Private diary")
            self.assertNotIn("Download .ics", diary_search)
            all_search = search_page(store, kind="all", start="2026-07-01",
                                     end="2026-07-01")
            self.assertEqual(all_search.count("Download .ics"), 2)

    def test_http_download_and_edit_links(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = self.build(root)
            server = BrowserServer(root, calendar_path=store.path)
            server.start()
            try:
                day = day_page(store, "2026-07-01", server.token)
                week = week_page(store, "2026-07-01")
                link = 'calendar-export-one?date=2026-07-01&amp;row=1'
                self.assertIn(link, day)
                self.assertIn(link, week)
                self.assertEqual(day.count("Download .ics"), 2)
                self.assertEqual(week.count("Download .ics"), 2)
                before = store.revision()
                with urlopen(server.url +
                             "calendar-export-one?date=2026-07-01&row=1",
                             timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn("text/calendar", response.headers["Content-Type"])
                    self.assertIn("attachment", response.headers["Content-Disposition"])
                    data = response.read()
                self.assertEqual(data.count(b"BEGIN:VEVENT"), 1)
                self.assertIn(b"SUMMARY:Eastern appointment", data)
                self.assertEqual(store.revision(), before)
                for suffix, expected_status in [
                    ("date=2026-07-01&row=0", 400),
                    ("date=2026-07-02&row=1", 404),
                    ("date=2026-07-01&row=20", 404),
                    ("date=2026-07-01&row=-1", 400),
                    ("date=2026-07-01&row=1&extra=1", 400),
                ]:
                    with self.subTest(suffix=suffix):
                        with self.assertRaises(HTTPError) as error:
                            urlopen(server.url + "calendar-export-one?" + suffix,
                                    timeout=5)
                        self.assertEqual(error.exception.code, expected_status)
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
