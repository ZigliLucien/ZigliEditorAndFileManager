"""Monthly calendar shows formatted diary entries, never raw markup."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from zefm.server.calendar_pages import month_page
from zefm.storage.calendar_diary import CalendarDiary


class MonthlyDiaryFormattingTests(unittest.TestCase):
    def test_month_renders_markdown_and_safe_html(self):
        with TemporaryDirectory() as folder:
            store = CalendarDiary(Path(folder) / "calendar.csv")
            store.add("2026-11-25", "**Important** and *italic* <u>underlined</u>")
            store.add("2026-11-25", "## Notes\n\n- first\n- second")
            html = month_page(store, 2026, 11)
            self.assertIn("<strong>Important</strong>", html)
            self.assertIn("<em>italic</em>", html)
            self.assertIn("<u>underlined</u>", html)
            self.assertIn("<h2>Notes</h2>", html)
            self.assertIn("<li>first</li>", html)
            self.assertNotIn("**Important**", html)
            self.assertIn('class="calendar-entry"', html)
            self.assertIn('max-height:7em;overflow:auto', html)

    def test_no_raw_script_or_javascript_link(self):
        with TemporaryDirectory() as folder:
            store = CalendarDiary(Path(folder) / "calendar.csv")
            store.add("2026-11-25", '<script>alert(1)</script><b onclick="evil()">Safe</b>')
            html = month_page(store, 2026, 11)
            self.assertNotIn("<script", html)
            self.assertNotIn("alert(1)", html)
            self.assertNotIn("onclick=", html)
            self.assertIn("<b>Safe</b>", html)

    def test_month_does_not_render_unrelated_entries(self):
        with TemporaryDirectory() as folder:
            store = CalendarDiary(Path(folder) / "calendar.csv")
            store.add("2026-10-20", "**October only**")
            html = month_page(store, 2026, 11)
            self.assertNotIn("October only", html)


if __name__ == "__main__":
    unittest.main()
