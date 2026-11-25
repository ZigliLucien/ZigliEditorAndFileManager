"""Diary Markdown rendering, safe HTML and original-source preservation."""
import unittest
from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory

from zefm.server.diary_markup import render_diary
from zefm.server.calendar_pages import day_page
from zefm.storage.calendar_diary import CalendarDiary


class DiaryMarkupTests(unittest.TestCase):
    def test_markdown_headings_emphasis_lists_links(self):
        html = render_diary("# Heading\n\n**bold** and *italic*\n\n- alpha\n- beta\n\n[site](https://example.org/)")
        self.assertIn("<h1>Heading</h1>", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn("<li>alpha</li>", html)
        self.assertIn("https://example.org/", html)
        self.assertNotIn("<script", html)

    def test_safe_inline_standard_html(self):
        html = render_diary("<h3>Summary</h3>\n\nA <b>bold</b> sentence and <u>underline</u>.")
        self.assertIn("<h3>Summary</h3>", html)
        self.assertIn("<b>bold</b>", html)
        self.assertIn("<u>underline</u>", html)

    def test_scripts_css_event_handlers_and_unsafe_urls_not_rendered(self):
        source = ('<script>alert(1)</script><style>body{display:none}</style>'
                  '<iframe src="https://evil.test/"></iframe>'
                  '<b onclick="alert(7)" style="color:red">Safe</b>'
                  '<a href="javascript:alert(8)">unsafe</a>'
                  '<a href="https://example.org/" onclick="evil()">good</a>'
                  '[danger](javascript:alert(2))'
                  '<img src=x onerror=alert(3)>')
        html = render_diary(source)
        self.assertIn("<b>Safe</b>", html)
        self.assertIn(">unsafe</a>", html)
        self.assertIn('href="https://example.org/"', html)
        self.assertNotIn("onclick=", html)
        self.assertNotIn("onerror=", html)
        self.assertNotIn("javascript:", html.replace("[danger](javascript:alert(2))", ""))
        self.assertNotIn("<script", html)
        self.assertNotIn("<iframe", html)
        self.assertNotIn("<style", html)
        self.assertNotIn("<img", html)
        self.assertNotIn("alert(1)", html)

    def test_plain_text_is_escaped(self):
        html = render_diary("A < 2 & B > 1\n\nCœur ייִדיש")
        self.assertIn("Cœur ייִדיש", html)
        self.assertNotIn("< 2", html)
        self.assertIn("&lt;", html)
        self.assertIn("&amp;", html)

    def test_csv_source_kept_verbatim_and_diary_page_is_formatted(self):
        with TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "diary.csv")
            source = "# Notes\n\n**Important** <strong>HTML</strong>"
            store.add("2026-11-25", source)
            self.assertEqual(store.read()[0]["text"], source)
            html = day_page(store, "2026-11-25", "dummy-csrf")
            self.assertIn("<h1>Notes</h1>", html)
            self.assertIn("<strong>Important</strong>", html)
            self.assertIn("<strong>HTML</strong>", html)


if __name__ == "__main__":
    unittest.main()
