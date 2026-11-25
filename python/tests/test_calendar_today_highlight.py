"""Today's date is visually and semantically highlighted in the calendar."""
import unittest
from datetime import date
from unittest.mock import patch

from zefm.server.calendar_pages import month_page


class FakeStore:
    def in_month(self, year, month):
        return []


class FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2026, 11, 25)


class CalendarTodayHighlightTests(unittest.TestCase):
    def test_today_is_amber_and_marked_accessibly(self):
        with patch("zefm.server.calendar_pages.date", FixedDate):
            html = month_page(FakeStore(), 2026, 11)
        self.assertEqual(html.count('aria-current="date"'), 1)
        self.assertEqual(html.count('● Today'), 1)
        self.assertIn('background:#ffca55', html)
        self.assertIn('border:3px solid #d66a00', html)
        self.assertIn('diary?date=2026-11-25', html)

    def test_different_month_has_no_today_highlight(self):
        with patch("zefm.server.calendar_pages.date", FixedDate):
            html = month_page(FakeStore(), 2026, 10)
        self.assertNotIn('aria-current="date"', html)
        self.assertNotIn('background:#ffca55', html)
        self.assertNotIn('● Today', html)


if __name__ == "__main__":
    unittest.main()
