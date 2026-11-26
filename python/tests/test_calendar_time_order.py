"""Timed appointments display in chronological order without changing CSV rows."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from zefm.server.calendar_pages import day_page, month_page
from zefm.server.diary_agenda import agenda_page, upcoming_entries
from zefm.storage.calendar_diary import CalendarDiary


class CalendarTimeOrderTests(unittest.TestCase):
    def make_store(self, temp):
        store = CalendarDiary(Path(temp) / "calendar.csv")
        # Deliberately out of order in the stored CSV.
        for text, start, end in (
            ("Late meeting", "16:00", "17:00"),
            ("Early meeting", "08:30", "09:30"),
            ("All-day note", "", ""),
            ("Noon meeting", "12:00", "13:00"),
            ("Another all-day", "", ""),
        ):
            store.add("2026-11-26", text, "appointment",
                      start_time=start, end_time=end,
                      timezone="America/Chicago" if start else "")
        return store

    def test_day_shows_all_day_first_then_chronological_times(self):
        with TemporaryDirectory() as temp:
            store = self.make_store(temp)
            original = [entry["text"] for entry in store.read()]
            page = day_page(store, "2026-11-26", "csrf")
            labels = ["All-day note", "Another all-day", "Early meeting",
                      "Noon meeting", "Late meeting"]
            self.assertEqual(sorted(labels, key=page.index), labels)
            # Links must refer to original CSV indexes, not displayed offsets.
            self.assertIn('diary-edit?date=2026-11-26&amp;row=1', page)
            self.assertIn('diary-delete?date=2026-11-26&amp;row=0', page)
            self.assertEqual([entry["text"] for entry in store.read()], original)

    def test_month_shows_first_two_all_day_instead_of_insertion_order(self):
        with TemporaryDirectory() as temp:
            store = self.make_store(temp)
            html = month_page(store, 2026, 11)
            self.assertIn("All-day note", html)
            self.assertIn("Another all-day", html)
            self.assertNotIn("Late meeting", html)  # only two previews per cell
            self.assertIn("+3 more", html)

    def test_agenda_sort_and_edit_links_preserve_indices(self):
        with TemporaryDirectory() as temp:
            store = self.make_store(temp)
            store.add("2026-11-27", "Next day", "appointment",
                      start_time="07:00", end_time="08:00",
                      timezone="America/Chicago")
            entries, total, _, _ = upcoming_entries(
                store, days=7, today=date(2026, 11, 26))
            self.assertEqual(total, 6)
            self.assertEqual([entry["text"] for _, entry in entries],
                             ["All-day note", "Another all-day", "Early meeting",
                              "Noon meeting", "Late meeting", "Next day"])
            self.assertEqual([index for index, _ in entries],
                             [2, 4, 1, 3, 0, 5])
            html = agenda_page(store, days=7, today=date(2026, 11, 26))
            self.assertLess(html.index("08:30"), html.index("12:00"))
            self.assertLess(html.index("12:00"), html.index("16:00"))
            self.assertIn('diary-edit?date=2026-11-26&amp;row=1', html)
            self.assertIn('diary-edit?date=2026-11-26&amp;row=0', html)

    def test_same_start_time_retains_original_csv_order(self):
        with TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "calendar.csv")
            for label in ("First", "Second", "Third"):
                store.add("2026-11-26", label, "appointment",
                          start_time="14:00", end_time="15:00",
                          timezone="America/Chicago")
            rows, _, _, _ = upcoming_entries(
                store, days=7, today=date(2026, 11, 26))
            self.assertEqual([entry["text"] for _, entry in rows],
                             ["First", "Second", "Third"])


if __name__ == "__main__":
    unittest.main()
