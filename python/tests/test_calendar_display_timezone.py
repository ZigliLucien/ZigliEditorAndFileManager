"""Read-only calendar projection from invitation timezone to Central viewing time."""
from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zefm.server.calendar_pages import display_entry, appointment_meta, day_page, month_page
from zefm.server.http import BrowserServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zefm.server.diary_agenda import upcoming_entries, agenda_page
from zefm.server.diary_search import find_entries, search_page
from zefm.server.ical_export import export_ical
from zefm.server.ical_import import import_preview_page
from zefm.storage.calendar_diary import CalendarDiary


class ViewingTimezoneTests(unittest.TestCase):
    def test_winter_and_summer_eastern_convert_to_central(self):
        with patch.dict("os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
            for day, source, shown, zone in (
                ("2026-01-15", "15:00", "14:00", "CST"),
                ("2026-07-15", "15:00", "14:00", "CDT"),
            ):
                with self.subTest(day=day):
                    record = {"date": day, "kind": "appointment", "text": "Meeting",
                              "start_time": source, "end_time": "16:00",
                              "timezone": "America/New_York", "location": "Office"}
                    display = display_entry(record)
                    self.assertEqual((display["date"], display["start_time"],
                                      display["end_time"], display["timezone"]),
                                     (day, shown, "15:00", "America/Chicago"))
                    self.assertIn(shown + "–15:00 " + zone, appointment_meta(record))
                    self.assertEqual(record["start_time"], source)
                    self.assertEqual(record["timezone"], "America/New_York")

    def test_utc_and_pacific_display_in_central(self):
        with patch.dict("os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
            utc = {"date": "2026-01-15", "start_time": "10:00",
                   "end_time": "11:00", "timezone": "UTC"}
            pacific = dict(utc, start_time="10:00", end_time="11:00",
                           timezone="America/Los_Angeles")
            self.assertEqual(display_entry(utc)["start_time"], "04:00")
            self.assertEqual(display_entry(pacific)["start_time"], "12:00")

    def test_cross_midnight_moves_event_to_previous_central_date(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "calendar.csv")
            store.add("2026-07-01", "Midnight Eastern", "appointment",
                      start_time="00:30", end_time="01:30",
                      timezone="America/New_York")
            original = store.record(0)
            with patch.dict("os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
                display = display_entry(original)
                self.assertEqual(display["date"], "2026-06-30")
                self.assertEqual(display["start_time"], "23:30")
                self.assertEqual(display["end_time"], "00:30")
                self.assertEqual(display["_end_date"], "2026-07-01")
                june = month_page(store, 2026, 6)
                july = month_page(store, 2026, 7)
                self.assertIn("Midnight Eastern", june)
                self.assertNotIn("Midnight Eastern", july)
                day = day_page(store, "2026-06-30", "token")
                self.assertIn("23:30–00:30 (2026-07-01) CDT", day)
                self.assertIn("diary-edit?date=2026-07-01&amp;row=0", day)
                self.assertNotIn("Midnight Eastern",
                                 day_page(store, "2026-07-01", "token"))
                rows, count, _, _ = upcoming_entries(
                    store, days=7, today=date(2026, 6, 30))
                self.assertEqual(count, 1)
                self.assertEqual(rows[0][0], 0)
                agenda = agenda_page(store, days=7, today=date(2026, 6, 30))
                self.assertIn("23:30–00:30 (2026-07-01) CDT", agenda)
                self.assertIn("diary-edit?date=2026-07-01&amp;row=0", agenda)
                found, count = find_entries(store, query="Midnight",
                                            start="2026-06-30", end="2026-06-30")
                self.assertEqual(count, 1)
                self.assertEqual(found[0][0], 0)
                search = search_page(store, query="Midnight",
                                     start="2026-06-30", end="2026-06-30")
                self.assertIn('diary?date=2026-06-30', search)
                self.assertIn('diary-edit?date=2026-07-01&amp;row=0', search)
            self.assertEqual(store.record(0), original)
            exported = export_ical(store).decode("utf-8")
            self.assertIn("DTSTART;TZID=America/New_York:20260701T003000", exported)

    def test_browser_save_returns_to_local_date(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = CalendarDiary(root / "calendar.csv")
            server = BrowserServer(root, calendar_path=store.path)
            server.start()
            try:
                with patch.dict("os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
                    fields = {
                        "csrf": server.token, "date": "2026-07-01",
                        "kind": "appointment", "text": "Eastern after midnight",
                        "start_time": "00:30", "end_time": "01:30",
                        "timezone": "America/New_York", "location": "",
                    }
                    req = Request(
                        server.url + "diary",
                        data=urlencode(fields).encode("utf-8"),
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
                    with urlopen(req, timeout=5) as response:
                        self.assertTrue(response.url.endswith("diary?date=2026-06-30"))
                        self.assertIn("Eastern after midnight",
                                      response.read().decode("utf-8"))
                    self.assertEqual(store.record(0)["date"], "2026-07-01")
            finally:
                server.close()

    def test_all_day_records_do_not_shift(self):
        with patch.dict("os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
            entry = {"date": "2026-07-01", "kind": "appointment",
                     "text": "All day"}
            self.assertEqual(display_entry(entry), entry)
            self.assertIsNot(display_entry(entry), entry)

    def test_other_display_timezone_works_without_changing_storage(self):
        original = {"date": "2026-07-01", "start_time": "14:00",
                    "end_time": "15:00", "timezone": "America/Chicago"}
        with patch.dict("os.environ", {"ZEFM_TIMEZONE": "America/New_York"}):
            self.assertEqual(display_entry(original)["start_time"], "15:00")
            self.assertIn("EDT", appointment_meta(original))

    def test_invitation_preview_shows_local_time(self):
        entry = {"date": "2026-07-15", "kind": "appointment", "text": "Invitation",
                 "start_time": "15:00", "end_time": "16:00",
                 "timezone": "America/New_York", "location": "Room"}
        with patch.dict("os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
            html = import_preview_page([entry], "BEGIN:VCALENDAR\nEND:VCALENDAR",
                                       "a" * 64, "csrf")
            self.assertIn("14:00–15:00 CDT", html)
            self.assertIn("Room", html)
            self.assertEqual(entry["start_time"], "15:00")


if __name__ == "__main__":
    unittest.main()
