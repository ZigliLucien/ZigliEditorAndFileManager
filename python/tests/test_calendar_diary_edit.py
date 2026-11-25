"""Calendar edit/delete forms, revision conflicts and historic diary migration."""
from pathlib import Path
import re
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.http import BrowserServer
from zefm.storage.calendar_diary import (
    CalendarDiary, CalendarConflictError, CalendarEntryNotFound)
from zefm.storage.import_legacy_diary import import_legacy_diary, parse_legacy_diary


class CalendarEntryTests(unittest.TestCase):
    def test_update_delete_duplicate_rows_and_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CalendarDiary(Path(directory) / "calendar.csv")
            store.add("2026-11-23", "same")
            store.add("2026-11-23", "same")
            original_revision = store.revision()
            store.update(1, "2026-11-24", "changed", "appointment",
                         original_revision, expected_day="2026-11-23")
            self.assertEqual([x["text"] for x in store.read()], ["same", "changed"])
            with self.assertRaises(CalendarConflictError):
                store.delete(0, original_revision, expected_day="2026-11-23")
            with self.assertRaises(CalendarEntryNotFound):
                store.record(1, expected_day="2026-11-23")
            current = store.revision()
            removed = store.delete(0, current, expected_day="2026-11-23")
            self.assertEqual(removed["text"], "same")
            self.assertEqual(store.read()[0]["text"], "changed")

    def test_stale_version_is_not_lost_after_external_change(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CalendarDiary(Path(directory) / "calendar.csv")
            store.add("2026-11-23", "original")
            revision = store.revision()
            store.add("2026-11-23", "new from another browser")
            with self.assertRaises(CalendarConflictError):
                store.update(0, "2026-11-23", "overwrite", "diary", revision)
            self.assertEqual(store.read()[0]["text"], "original")
            self.assertEqual(len(store.read()), 2)

    def test_batch_import_skips_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CalendarDiary(Path(directory) / "calendar.csv")
            entry = {"date": "2026-11-23", "kind": "diary", "text": "Hello"}
            self.assertEqual(store.append_many([entry, entry]), (1, 1))
            self.assertEqual(store.append_many([entry]), (0, 1))
            self.assertEqual(len(store.read()), 1)


class LegacyDiaryImportTests(unittest.TestCase):
    def test_year_required_and_preserve_original(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "diary-user.txt"
            destination = root / "calendar.csv"
            original.write_text("# historic\nNov 23 | Had a meeting\n"
                                "Feb 29 | Birthday <important>\n", encoding="utf-8")
            count, skip = import_legacy_diary(
                original, year=2024, output=destination, dry_run=True)
            self.assertEqual((count, skip), (2, 0))
            self.assertFalse(destination.exists())
            self.assertEqual(import_legacy_diary(original, year=2024, output=destination),
                             (2, 0))
            self.assertEqual(import_legacy_diary(original, year=2024, output=destination),
                             (0, 2))
            store = CalendarDiary(destination)
            self.assertEqual([r["date"] for r in store.read()],
                             ["2024-11-23", "2024-02-29"])
            self.assertIn("Feb 29 |", original.read_text(encoding="utf-8"))
            with self.assertRaises(ValueError):
                import_legacy_diary(original, year=2026, output=destination)
            self.assertEqual(len(store.read()), 2)

    def test_unsupported_all_entries_fail_without_partial_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "diary-user.txt"
            original.write_text("Nov 23 | Good\nAll 5 | Recurring\n", encoding="utf-8")
            destination = root / "calendar.csv"
            with self.assertRaisesRegex(ValueError, "line 2"):
                import_legacy_diary(original, year=2026, output=destination)
            self.assertFalse(destination.exists())

    def test_explicit_all_day_recurrence_for_selected_years(self):
        source = "All 5 | Monthly task\nAll 31 | Month end\nAll 29 | Special day\n"
        entries = parse_legacy_diary(
            source, 2024, expand_all=True, through_year=2025)
        fifth = [r for r in entries if r["text"] == "Monthly task"]
        end = [r for r in entries if r["text"] == "Month end"]
        twenty_ninth = [r for r in entries if r["text"] == "Special day"]
        self.assertEqual(len(fifth), 24)
        self.assertEqual(len(end), 14)
        self.assertEqual(len(twenty_ninth), 23)
        self.assertIn("2024-02-29", [r["date"] for r in twenty_ninth])
        self.assertNotIn("2025-02-29", [r["date"] for r in twenty_ninth])
        self.assertEqual(fifth[0]["date"], "2024-01-05")
        self.assertEqual(fifth[-1]["date"], "2025-12-05")

    def test_all_requires_opt_in_and_bounded_years(self):
        with self.assertRaisesRegex(ValueError, "expand-all"):
            parse_legacy_diary("All 5 | Repeating", 2024)
        with self.assertRaises(ValueError):
            parse_legacy_diary("All 5 | Repeating", 2024, through_year=2025)
        with self.assertRaises(ValueError):
            parse_legacy_diary("All 0 | Invalid", 2024, expand_all=True)
        with self.assertRaises(ValueError):
            parse_legacy_diary("All 32 | Invalid", 2024, expand_all=True)
        with self.assertRaises(ValueError):
            parse_legacy_diary("All 5 | Repeating", 2024, expand_all=True,
                               through_year=2023)
        with self.assertRaises(ValueError):
            parse_legacy_diary("All 5 | Repeating", 2024, expand_all=True,
                               through_year=2130)

    def test_recurring_import_is_idempotent_and_non_destructive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "diary-user.txt"
            csv = root / "calendar.csv"
            source.write_text("Nov 23 | Single entry\nAll 5 | Monthly\n",
                              encoding="utf-8")
            self.assertEqual(import_legacy_diary(
                source, year=2024, output=csv, dry_run=True,
                expand_all=True, through_year=2025), (25, 0))
            self.assertFalse(csv.exists())
            self.assertEqual(import_legacy_diary(
                source, year=2024, output=csv, expand_all=True,
                through_year=2025), (25, 0))
            self.assertEqual(import_legacy_diary(
                source, year=2024, output=csv, expand_all=True,
                through_year=2025), (0, 25))
            self.assertEqual(len(CalendarDiary(csv).read()), 25)
            self.assertIn("All 5", source.read_text(encoding="utf-8"))

    def test_no_invented_year_or_invalid_february(self):
        with self.assertRaises(ValueError):
            parse_legacy_diary("Feb 29 | Special day", 2026)
        with self.assertRaises(ValueError):
            parse_legacy_diary("Nov 31 | Impossible", 2026)


class CalendarEditHttpTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "calendar.csv"
        self.server = BrowserServer(Path(self.folder.name), calendar_path=self.path)
        self.server.start()
        self.addCleanup(self.server.close)
        self.store = CalendarDiary(self.path)

    def get(self, relative):
        try:
            with urlopen(self.server.url + relative, timeout=4) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def post(self, endpoint, fields):
        req = Request(self.server.url + endpoint,
                      data=urlencode(fields).encode("utf-8"),
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urlopen(req, timeout=4) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    def form_revision(self, html):
        match = re.search(r'name="revision" value="([0-9a-f]{64})"', html)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_edit_move_date_and_delete_confirmed(self):
        self.store.add("2026-11-23", "<script>old</script>")
        status, day = self.get("diary?date=2026-11-23")
        self.assertEqual(status, 200)
        self.assertIn("diary-edit?date=2026-11-23&amp;row=0", day)
        self.assertIn("diary-delete?date=2026-11-23&amp;row=0", day)
        status, form = self.get("diary-edit?date=2026-11-23&row=0")
        self.assertEqual(status, 200)
        self.assertIn("&lt;script&gt;old&lt;/script&gt;", form)
        revision = self.form_revision(form)
        status, edited = self.post("diary-edit", {
            "csrf": self.server.token, "date": "2026-11-23", "row": "0",
            "new_date": "2026-11-24", "kind": "appointment",
            "text": "Moved & edited", "revision": revision})
        self.assertEqual(status, 200, edited)
        self.assertIn("Moved &amp; edited", edited)
        self.assertEqual(self.store.record(0)["date"], "2026-11-24")
        status, confirm = self.get("diary-delete?date=2026-11-24&row=0")
        self.assertEqual(status, 200)
        self.assertIn("Confirm Delete", confirm)
        self.assertEqual(len(self.store.read()), 1)  # GET must never delete
        revision = self.form_revision(confirm)
        status, deleted = self.post("diary-delete", {
            "csrf": self.server.token, "date": "2026-11-24", "row": "0",
            "revision": revision})
        self.assertEqual(status, 200, deleted)
        self.assertEqual(self.store.read(), [])

    def test_stale_edit_and_delete_return_409(self):
        self.store.add("2026-11-23", "first")
        status, form = self.get("diary-edit?date=2026-11-23&row=0")
        self.assertEqual(status, 200)
        version = self.form_revision(form)
        self.store.add("2026-11-23", "second")
        status, body = self.post("diary-edit", {
            "csrf": self.server.token, "date": "2026-11-23", "row": "0",
            "new_date": "2026-11-23", "kind": "diary",
            "text": "overwrite", "revision": version})
        self.assertEqual(status, 409, body)
        status, body = self.post("diary-delete", {
            "csrf": self.server.token, "date": "2026-11-23", "row": "0",
            "revision": version})
        self.assertEqual(status, 409, body)
        self.assertEqual([r["text"] for r in self.store.read()], ["first", "second"])

    def test_bad_row_and_csrf_do_not_modify(self):
        self.store.add("2026-11-23", "safe")
        status, _ = self.get("diary-edit?date=2026-11-23&row=999")
        self.assertEqual(status, 404)
        revision = self.store.revision()
        status, _ = self.post("diary-delete", {
            "csrf": "invalid", "date": "2026-11-23", "row": "0",
            "revision": revision})
        self.assertEqual(status, 403)
        self.assertEqual(self.store.record(0)["text"], "safe")


if __name__ == "__main__":
    unittest.main()
