"""Read-only appointment overlap warnings across timezone and date boundaries."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from zefm.server.appointment_conflicts import appointment_interval, conflicting_rows
from zefm.server.calendar_pages import day_page
from zefm.server.week_calendar import week_page
from zefm.storage.calendar_diary import CalendarDiary


class OverlapTests(unittest.TestCase):
    def test_different_zones_same_instant_overlap(self):
        records = [
            {"date": "2026-07-01", "kind": "appointment", "text": "Eastern meeting",
             "start_time": "11:00", "end_time": "12:00",
             "timezone": "America/New_York"},
            {"date": "2026-07-01", "kind": "appointment", "text": "Central meeting",
             "start_time": "10:30", "end_time": "11:30",
             "timezone": "America/Chicago"},
        ]
        self.assertEqual(conflicting_rows(records), {1: 0, 0: 1})
        self.assertNotEqual(appointment_interval(records[0])[0],
                            appointment_interval(records[1])[0])

    def test_touching_endpoints_are_not_conflicts(self):
        records = [
            {"date": "2026-07-01", "kind": "appointment",
             "start_time": "10:00", "end_time": "11:00",
             "timezone": "America/Chicago"},
            {"date": "2026-07-01", "kind": "appointment",
             "start_time": "12:00", "end_time": "13:00",
             "timezone": "America/New_York"},
            {"date": "2026-07-01", "kind": "diary", "text": "All day"},
        ]
        # Eastern noon is Central 11:00, precisely when the first ends.
        self.assertEqual(conflicting_rows(records), {})
        self.assertIsNone(appointment_interval(records[-1]))

    def test_overlap_across_source_dates_and_day_boundary(self):
        with TemporaryDirectory() as tmp, patch.dict(
            "os.environ", {"ZEFM_TIMEZONE": "America/Chicago"}):
            store = CalendarDiary(Path(tmp) / "calendar.csv")
            store.add("2026-07-01", "Late Eastern", "appointment",
                      start_time="00:30", end_time="01:30",
                      timezone="America/New_York")
            store.add("2026-06-30", "Late Central", "appointment",
                      start_time="23:45", end_time="23:59",
                      timezone="America/Chicago")
            rows_before = store.read()
            self.assertEqual(conflicting_rows(store.read()), {1: 0, 0: 1})
            day = day_page(store, "2026-06-30", "csrf")
            self.assertEqual(day.count("Overlaps another appointment"), 2)
            self.assertIn("diary-edit?date=2026-07-01&amp;row=0", day)
            self.assertIn("diary-edit?date=2026-06-30&amp;row=1", day)
            weekly = week_page(store, "2026-06-30")
            self.assertEqual(weekly.count("Overlaps another appointment"), 2)
            self.assertIn("view other", weekly)
            self.assertEqual(store.read(), rows_before)

    def test_nonoverlap_all_day_and_large_identical_batch(self):
        records = [
            {"date": "2026-07-01", "kind": "appointment",
             "start_time": "09:00", "end_time": "10:00",
             "timezone": "America/Chicago"}
            for _ in range(500)
        ]
        flags = conflicting_rows(records)
        self.assertEqual(len(flags), 500)
        self.assertTrue(all(0 <= other < 500 and index != other
                            for index, other in flags.items()))
        records = [{"date": "2026-07-01", "kind": "diary", "text": "No times"}]
        self.assertFalse(conflicting_rows(records))


if __name__ == "__main__":
    unittest.main()
