"""iCalendar snapshot export: UTF-8, RFC 5545 line folding, safe read-only HTTP."""
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import urlopen
import unittest

from zefm.server.ical_export import export_ical
from zefm.server.calendar_pages import month_page
from zefm.server.http import BrowserServer
from zefm.storage.calendar_diary import CalendarDiary


class IcalExportTests(unittest.TestCase):
    def test_appointments_default_and_all_day_without_invented_times(self):
        with TemporaryDirectory() as tmp:
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            store.add("2026-11-25", "Doctor appointment", "appointment")
            store.add("2026-11-25", "Private diary", "diary")
            snapshot = store.revision()
            content = export_ical(
                store, timestamp=datetime(2026, 11, 25, 12, tzinfo=timezone.utc))
            self.assertIn(b"BEGIN:VCALENDAR\r\n", content)
            self.assertEqual(content.count(b"BEGIN:VEVENT"), 1)
            self.assertIn(b"DTSTART;VALUE=DATE:20261125\r\n", content)
            self.assertNotIn(b"DTSTART:20261125T", content)
            self.assertNotIn(b"DTEND", content)
            self.assertIn(b"DTSTAMP:20261125T120000Z", content)
            self.assertNotIn(b"Private diary", content)
            self.assertEqual(store.revision(), snapshot)
            self.assertEqual(export_ical(store, "all", timestamp=datetime(
                2026, 11, 25, 12, tzinfo=timezone.utc)).count(b"BEGIN:VEVENT"), 2)

    def test_unicode_multiline_escaping_and_octet_fold(self):
        with TemporaryDirectory() as tmp:
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            text = "Cœur ייִדיש 😄 " + "é" * 100 + "\nLine two; x,y\\z"
            store.add("2026-11-25", text, "appointment")
            data = export_ical(store)
            self.assertTrue(data.endswith(b"END:VCALENDAR\r\n"))
            lines = data.split(b"\r\n")
            self.assertTrue(all(len(line) <= 75 for line in lines))
            self.assertIn("DESCRIPTION:Cœur", data.decode("utf-8"))
            self.assertIn("\\nLine two\\; x\\,y\\\\z", data.decode("utf-8"))
            self.assertTrue(any(line.startswith(b" ") for line in lines))
            self.assertTrue(all(b"\n" not in line for line in lines))

    def test_duplicate_entries_produce_distinct_stable_uids(self):
        with TemporaryDirectory() as tmp:
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            store.add("2026-11-25", "same", "appointment")
            store.add("2026-11-25", "same", "appointment")
            now = datetime(2026, 11, 25, tzinfo=timezone.utc)
            output = export_ical(store, timestamp=now).decode("utf-8")
            unique_ids = [line for line in output.split("\r\n") if line.startswith("UID:")]
            self.assertEqual(len(unique_ids), 2)
            self.assertNotEqual(unique_ids[0], unique_ids[1])
            self.assertEqual(export_ical(store, timestamp=now).decode("utf-8"), output)

    def test_calendar_navigation_export_link(self):
        with TemporaryDirectory() as tmp:
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            self.assertIn('href="/calendar-export?kind=appointment"',
                          month_page(store, 2026, 11))

    def test_http_download_and_validation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = CalendarDiary(root / "calendar.csv")
            store.add("2026-11-25", "meeting", "appointment")
            server = BrowserServer(root, calendar_path=store.path)
            server.start()
            try:
                with urlopen(server.url + "calendar-export", timeout=5) as response:
                    data = response.read()
                    self.assertEqual(response.status, 200)
                    self.assertIn("text/calendar", response.headers["Content-Type"])
                    self.assertIn("attachment", response.headers["Content-Disposition"])
                self.assertIn(b"SUMMARY:meeting", data)
                for invalid in ("calendar-export?kind=invalid",
                                "calendar-export?unknown=1"):
                    with self.assertRaises(HTTPError) as err:
                        urlopen(server.url + invalid, timeout=5)
                    self.assertEqual(err.exception.code, 400)
                self.assertEqual(store.on_day("2026-11-25")[0]["text"], "meeting")
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
