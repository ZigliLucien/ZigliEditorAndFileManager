"""CSV calendar/diary, legacy CLSV migration, and browser integration."""
import csv
from datetime import date
from html import unescape
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.storage.calendar_diary import CalendarDiary
from zefm.storage.convert_clsv import convert_file
from zefm.server.http import BrowserServer
from zefm.server.file_manager import LocalFiles, BrowserError
from zefm.server.pandas_table import dataframe_preview


class DiaryCsvTests(unittest.TestCase):
    def test_unicode_multiline_roundtrip_and_no_legacy_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            legacy = root / "diary-user.txt"
            legacy.write_text("Nov 23 | Historic event\n")
            store = CalendarDiary(root / "calendar.csv")
            store.add("2026-11-23", "ייִדיש\nCœur: testing", "diary")
            store.add("2026-11-23", "Appointment 9:00", "appointment")
            self.assertEqual(len(store.on_day("2026-11-23")), 2)
            self.assertEqual(len(store.in_month(2026, 11)), 2)
            self.assertEqual(store.read()[0]["text"], "ייִדיש\nCœur: testing")
            self.assertEqual(legacy.read_text(), "Nov 23 | Historic event\n")
            with store.path.open(newline="", encoding="utf-8") as stream:
                self.assertEqual(list(csv.DictReader(stream))[0]["kind"], "diary")
            with self.assertRaises(ValueError):
                store.add("../bad", "nope")

    def test_bad_calendar_csv_refuses_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "calendar.csv"
            path.write_text("date,wrong,text\n2026-11-23,diary,test\n")
            with self.assertRaises(ValueError):
                CalendarDiary(path).add("2026-11-24", "other")
            self.assertIn("wrong", path.read_text())


class ClsvConversionTests(unittest.TestCase):
    def test_clsv_to_csv_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "old.clsv"
            target = Path(temporary) / "new.csv"
            source.write_text(
                "title:Helpers\n####\ncommand:shortkey:menu:description:entry\n"
                "#\nSave:F1:File Menu:Save this: with a colon\n"
                "Quit:Ctrl-Q:File Menu:Bye\n", encoding="utf-8")
            title, count = convert_file(source, target)
            self.assertEqual((title, count), ("Helpers", 2))
            with target.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows[0]["description"], "Save this: with a colon")
            self.assertEqual(source.read_text(encoding="utf-8").splitlines()[0], "title:Helpers")
            with self.assertRaises(FileExistsError):
                convert_file(source, target)


class CalendarBrowserTests(unittest.TestCase):
    def test_calendar_and_diary_post(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / "files"
            folder.mkdir()
            diary_path = root / "calendar.csv"
            server = BrowserServer(folder, calendar_path=diary_path)
            server.start()
            try:
                def get(relative):
                    with urlopen(server.url + relative, timeout=5) as response:
                        return response.status, response.read().decode("utf-8")
                status, listing = get("listing")
                self.assertEqual(status, 200)
                self.assertIn("Calendar / Diary", listing)
                status, calendar = get("calendar?year=2026&month=11")
                self.assertEqual(status, 200)
                self.assertIn("November 2026", calendar)
                self.assertIn("diary?date=2026-11-23", calendar)
                fields = {"csrf": server.token, "date": "2026-11-23",
                          "kind": "appointment", "text": "<script>bad()</script> ייִדיש"}
                req = Request(server.url + "diary",
                              data=urlencode(fields).encode("utf-8"),
                              headers={"Content-Type":"application/x-www-form-urlencoded"})
                with urlopen(req, timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    html = response.read().decode("utf-8")
                # Diary now renders sanitized Markdown/HTML, not raw source.
                self.assertNotIn("&lt;script&gt;", html)
                self.assertNotIn("<script>", html)
                self.assertNotIn("bad()", html)
                self.assertIn("ייִדיש", html)
                self.assertEqual(len(CalendarDiary(diary_path).on_day("2026-11-23")), 1)
                fields["csrf"] = "bad"
                bad = Request(server.url + "diary",
                              data=urlencode(fields).encode("utf-8"),
                              headers={"Content-Type":"application/x-www-form-urlencoded"})
                with self.assertRaises(HTTPError) as error:
                    urlopen(bad, timeout=5)
                self.assertEqual(error.exception.code, 403)
                self.assertEqual(len(CalendarDiary(diary_path).read()), 1)
            finally:
                server.close()

    def test_invalid_date_does_not_create_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            server = BrowserServer(root, calendar_path=root / "calendar.csv")
            server.start()
            try:
                with self.assertRaises(HTTPError) as error:
                    urlopen(server.url + "diary?date=2026-02-30", timeout=5)
                self.assertEqual(error.exception.code, 400)
                self.assertFalse((root / "calendar.csv").exists())
            finally:
                server.close()


class PandasPreviewTests(unittest.TestCase):
    def test_dataframe_optional_sort_filter_and_html_escaping(self):
        try:
            import pandas
        except ImportError:
            self.skipTest("Optional pandas not installed")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "table.csv").write_text(
                'Code,Title\n001,"<script>alert(1)</script>"\n010,Hello\n002,Hello world\n',
                encoding="utf-8")
            html = dataframe_preview(LocalFiles(root), "table.csv", sort="Code",
                                     descending=True, contains="hello")
            self.assertIn("<td>010</td>", html)
            self.assertIn("<td>002</td>", html)
            self.assertNotIn("<td>001</td>", html)
            self.assertNotIn("<script>", html)
            self.assertIn("pandas DataFrame", html)
            with self.assertRaises(BrowserError):
                dataframe_preview(LocalFiles(root), "table.csv", sort="__import__")


if __name__ == "__main__":
    unittest.main()
