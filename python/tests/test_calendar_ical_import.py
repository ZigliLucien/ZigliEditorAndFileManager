"""Conservative two-phase iCalendar import: validation, preview and CSV safety."""
import re
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from zefm.server.ical_export import export_ical
from zefm.server.ical_import import parse_ics
from zefm.server.http import BrowserServer
from zefm.storage.calendar_diary import CalendarDiary, CalendarConflictError


def calendar_event(*lines):
    return "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "BEGIN:VEVENT",
        *lines, "END:VEVENT", "END:VCALENDAR", ""
    ])


class ICalendarParserTests(unittest.TestCase):
    def test_export_roundtrip_unicode_multiline_and_escaped_text(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "source.csv")
            original = "Cœur ייִדיש 😄\nSecond line, with; punctuation\\"
            store.add("2026-11-25", original, "appointment")
            data = export_ical(store, timestamp=datetime(
                2026, 11, 25, tzinfo=timezone.utc))
            parsed = parse_ics(data.decode("utf-8"))
            self.assertEqual(parsed, [{
                "date": "2026-11-25", "kind": "appointment", "text": original}])

    def test_accept_one_day_all_day_no_time_guessing(self):
        source = calendar_event(
            "DTSTART;VALUE=DATE:20261125",
            "DTEND;VALUE=DATE:20261126",
            "SUMMARY:Meeting\\, notes",
        )
        self.assertEqual(parse_ics(source)[0]["text"], "Meeting, notes")

    def test_timed_utc_and_iana_timezone_and_location(self):
        utc = calendar_event(
            "DTSTART:20261125T130000Z", "DTEND:20261125T143000Z",
            "SUMMARY:UTC meeting", "LOCATION:Room 5")
        entry = parse_ics(utc)[0]
        self.assertEqual((entry["start_time"], entry["end_time"], entry["timezone"]),
                         ("13:00", "14:30", "UTC"))
        self.assertEqual(entry["location"], "Room 5")
        local = calendar_event(
            "DTSTART;TZID=America/Chicago:20261125T090000",
            "DTEND;TZID=America/Chicago:20261125T103000",
            "SUMMARY:Local meeting", "LOCATION:Carbondale")
        entry = parse_ics(local)[0]
        self.assertEqual(entry["timezone"], "America/Chicago")
        self.assertEqual(entry["date"], "2026-11-25")
        self.assertEqual(entry["location"], "Carbondale")

    def test_reject_timed_multiday_and_recurring(self):
        unsafe = [
            ("DTSTART:20261125T130000Z", "SUMMARY:Missing end"),
            ("DTSTART;TZID=America/Chicago:20261125T130000", "SUMMARY:Missing end"),
            ("DTSTART;VALUE=DATE:20261125", "DTEND;VALUE=DATE:20261127", "SUMMARY:Two days"),
            ("DTSTART;VALUE=DATE:20261125", "RRULE:FREQ=MONTHLY", "SUMMARY:Repeats"),
            ("DTSTART;VALUE=DATE:20261125", "BEGIN:VALARM", "END:VALARM", "SUMMARY:Alarm"),
            ("DTSTART;VALUE=DATE:20260230", "SUMMARY:Impossible"),
            ("DTSTART;VALUE=DATE:20261125", "STATUS:CANCELLED", "SUMMARY:Cancelled"),
        ]
        for event in unsafe:
            with self.subTest(event=event), self.assertRaises(ValueError):
                parse_ics(calendar_event(*event))

    def test_oversize_and_broken_calendar_rejected(self):
        for source in (
            "BEGIN:VCALENDAR\nEND:VCALENDAR",
            "not a calendar",
            calendar_event("DTSTART;VALUE=DATE:20261125", "SUMMARY:x" * 150000),
        ):
            with self.subTest(source=source[:60]), self.assertRaises(ValueError):
                parse_ics(source)


class ICalendarImportHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = CalendarDiary(self.root / "calendar.csv")
        self.server = BrowserServer(self.root, calendar_path=self.store.path)
        self.server.start()
        self.addCleanup(self.server.close)

    def request(self, endpoint, fields=None):
        if fields is None:
            req = Request(self.server.url + endpoint)
        else:
            req = Request(self.server.url + endpoint,
                          data=urlencode(fields).encode("utf-8"),
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as error:
            return error.code, error.read().decode("utf-8")

    def test_preview_confirm_dedup_and_zero_implicit_writes(self):
        source = calendar_event(
            "DTSTART;VALUE=DATE:20261125",
            "SUMMARY:First appointment",
        )
        status, form = self.request("calendar-import")
        self.assertEqual(status, 200)
        self.assertIn('name="csrf"', form)
        self.assertIn('action="/calendar-import-preview"', form)
        fields = {"csrf": self.server.token, "ics": source}
        code, preview = self.request("calendar-import-preview", fields)
        self.assertEqual(code, 200, preview)
        self.assertIn("First appointment", preview)
        self.assertIn("Confirm Import", preview)
        self.assertFalse(self.store.path.exists())
        revision = re.search(r'name="revision" value="([0-9a-f]{64})"', preview)
        self.assertIsNotNone(revision)
        approved = {**fields, "revision": revision.group(1)}
        status, result = self.request("calendar-import", approved)
        self.assertEqual(status, 200, result)
        self.assertIn("1 appointments added", result)
        self.assertEqual(self.store.on_day("2026-11-25")[0]["text"], "First appointment")
        status, preview2 = self.request("calendar-import-preview", fields)
        self.assertEqual(status, 200)
        newer_revision = re.search(
            r'name="revision" value="([0-9a-f]{64})"', preview2).group(1)
        status, result2 = self.request("calendar-import",
                                       {**fields, "revision": newer_revision})
        self.assertEqual(status, 200, result2)
        self.assertIn("0 appointments added; 1 exact duplicates skipped", result2)
        self.assertEqual(len(self.store.read()), 1)

    def test_stale_revision_and_malicious_input_rejected(self):
        source = calendar_event("DTSTART;VALUE=DATE:20261125", "SUMMARY:Test")
        fields = {"csrf": self.server.token, "ics": source}
        status, preview = self.request("calendar-import-preview", fields)
        self.assertEqual(status, 200)
        digest = re.search(r'name="revision" value="([0-9a-f]{64})"', preview).group(1)
        self.store.add("2026-11-20", "Existing diary", "diary")
        code, _ = self.request("calendar-import", {**fields, "revision": digest})
        self.assertEqual(code, 409)
        self.assertEqual(len(self.store.read()), 1)
        bad_source = calendar_event("DTSTART:20261125T130000Z", "SUMMARY:Unsafe")
        status, _ = self.request("calendar-import-preview",
                                 {"csrf": self.server.token, "ics": bad_source})
        self.assertEqual(status, 400)
        code, _ = self.request("calendar-import-preview",
                                {"csrf": "WRONG", "ics": source})
        self.assertEqual(code, 403)
        self.assertEqual(len(self.store.read()), 1)


if __name__ == "__main__":
    unittest.main()
