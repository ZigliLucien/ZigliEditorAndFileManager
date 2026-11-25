"""Search historical Calendar/Diary records without modifying CSV."""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
import unittest

from zefm.server.calendar_pages import month_page, day_page
from zefm.server.diary_search import find_entries, search_page, MAX_RESULTS
from zefm.server.http import BrowserServer
from zefm.storage.calendar_diary import CalendarDiary


class DiarySearchTests(unittest.TestCase):
    def test_literal_unicode_search_with_date_and_kind(self):
        with TemporaryDirectory() as temporary:
            store = CalendarDiary(Path(temporary) / "calendar.csv")
            store.add("2026-11-25", "**Cœur** ייִדיש", "diary")
            store.add("2026-11-20", "CŒUR appointment", "appointment")
            store.add("2026-10-25", "Other", "diary")
            results, total = find_entries(store, "cœur", kind="diary")
            self.assertEqual(total, 1)
            self.assertEqual(results[0][1]["date"], "2026-11-25")
            results, total = find_entries(
                store, "cœur", "2026-11-01", "2026-11-30", kind="all")
            self.assertEqual(total, 2)
            self.assertEqual([entry["date"] for _, entry in results],
                             ["2026-11-25", "2026-11-20"])
            html = search_page(store, "cœur")
            self.assertIn("<strong>Cœur</strong>", html)
            self.assertIn("diary?date=2026-11-25", html)
            self.assertIn("diary-edit?date=2026-11-20&amp;row=1", html)
            self.assertEqual(len(store.read()), 3)

    def test_search_is_literal_and_markup_safe(self):
        with TemporaryDirectory() as temporary:
            store = CalendarDiary(Path(temporary) / "calendar.csv")
            store.add("2026-11-25",
                      '<script>alert(1)</script><b onclick="evil()">item[1]</b>')
            html = search_page(store, query="item[1]")
            self.assertIn("<b>item[1]</b>", html)
            self.assertNotIn("<script", html)
            self.assertNotIn("alert(1)", html)
            self.assertNotIn("onclick=", html)
            self.assertIn("item[1]", html)
            _, total = find_entries(store, "item.*")
            self.assertEqual(total, 0)  # never interpret a search as a regex

    def test_date_and_length_validation(self):
        with TemporaryDirectory() as temporary:
            store = CalendarDiary(Path(temporary) / "calendar.csv")
            for options in [
                {"start": "2026-02-30"},
                {"start": "2026-11-25", "end": "2026-11-24"},
                {"query": "X" * 201},
                {"kind": "unknown"},
            ]:
                with self.subTest(options=options):
                    with self.assertRaises(ValueError):
                        find_entries(store, **options)

    def test_result_cap_is_explicit(self):
        with TemporaryDirectory() as temporary:
            store = CalendarDiary(Path(temporary) / "calendar.csv")
            store.append_many([
                {"date": "2026-11-25", "kind": "diary", "text": f"note {i}"}
                for i in range(MAX_RESULTS + 3)])
            found, total = find_entries(store, "note")
            self.assertEqual(total, MAX_RESULTS + 3)
            self.assertEqual(len(found), MAX_RESULTS)
            self.assertIn(f"showing the first {MAX_RESULTS}",
                          search_page(store, "note"))

    def test_calendar_and_day_link_to_search(self):
        with TemporaryDirectory() as temporary:
            store = CalendarDiary(Path(temporary) / "calendar.csv")
            self.assertIn('href="/diary-search"', month_page(store, 2026, 11))
            self.assertIn('href="/diary-search"',
                          day_page(store, "2026-11-25", "csrf"))


class DiarySearchHttpTests(unittest.TestCase):
    def test_search_http_and_rejected_parameters(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            store = CalendarDiary(root / "diary.csv")
            store.add("2026-11-25", "testing ייִדיש")
            server = BrowserServer(root, calendar_path=store.path)
            server.start()
            try:
                with urlopen(server.url + "diary-search?" +
                             urlencode({"q": "ייִדיש"}), timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    html = response.read().decode("utf-8")
                self.assertIn("ייִדיש", html)
                self.assertIn("2026-11-25", html)
                for bad in ["diary-search?unknown=1",
                            "diary-search?from=2026-02-30",
                            "diary-search?kind=invalid"]:
                    with self.assertRaises(HTTPError) as error:
                        urlopen(server.url + bad, timeout=5)
                    self.assertEqual(error.exception.code, 400)
                self.assertEqual(len(store.read()), 1)
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
