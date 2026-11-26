"""Browser .ics invitation selection and timed CSV backward compatibility."""
import csv
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from urllib.parse import quote, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from zefm.server.http import BrowserServer
from zefm.server.calendar_pages import day_page, month_page
from zefm.server.diary_agenda import agenda_page
from zefm.server.ical_export import export_ical
from zefm.server.ical_import import parse_ics
from zefm.storage.calendar_diary import CalendarDiary


INVITE = ("\r\n".join([
    "BEGIN:VCALENDAR", "VERSION:2.0",
    "BEGIN:VTIMEZONE", "TZID:America/Chicago",
    "BEGIN:STANDARD", "DTSTART:20251102T020000",
    "TZOFFSETFROM:-0500", "TZOFFSETTO:-0600", "END:STANDARD",
    "END:VTIMEZONE",
    "BEGIN:VEVENT", "UID:meeting-1@example.org",
    "DTSTART;TZID=America/Chicago:20261125T143000",
    "DTEND;TZID=America/Chicago:20261125T153000",
    "SUMMARY:Music practice",
    "LOCATION:Room 3",
    "END:VEVENT", "END:VCALENDAR", ""
]))


class TimedStoreTests(unittest.TestCase):
    def test_timed_invitation_upgrades_three_column_csv_without_loss(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "calendar.csv"
            store = CalendarDiary(path)
            store.add("2026-11-24", "Diary **legacy**", "diary")
            with path.open(encoding="utf-8", newline="") as stream:
                self.assertEqual(next(csv.reader(stream)), ["date", "kind", "text"])
            rows = parse_ics(INVITE)
            self.assertEqual(rows[0]["timezone"], "America/Chicago")
            self.assertEqual(rows[0]["location"], "Room 3")
            self.assertEqual(store.append_many(rows), (1, 0))
            with path.open(encoding="utf-8", newline="") as stream:
                self.assertEqual(next(csv.reader(stream)),
                    ["date", "kind", "text", "start_time", "end_time", "timezone", "location"])
            self.assertEqual(store.read()[0]["text"], "Diary **legacy**")
            self.assertEqual(store.read()[1]["start_time"], "14:30")
            self.assertEqual(store.append_many(rows), (0, 1))
            html = day_page(store, "2026-11-25", "token")
            self.assertIn("14:30–15:30", html)
            self.assertIn("America/Chicago", html)
            self.assertIn("Room 3", html)
            agenda = agenda_page(store, today=datetime(2026, 11, 25).date())
            self.assertIn("14:30–15:30", agenda)
            export = export_ical(store, timestamp=datetime(
                2026, 11, 25, tzinfo=timezone.utc)).decode("utf-8")
            self.assertIn("DTSTART;TZID=America/Chicago:20261125T143000", export)
            self.assertIn("DTEND;TZID=America/Chicago:20261125T153000", export)
            self.assertIn("LOCATION:Room 3", export)
            self.assertEqual(parse_ics(export)[0]["timezone"], "America/Chicago")

    def test_invitation_preserves_distinct_title_and_description(self):
        source = "\r\n".join([
            "BEGIN:VCALENDAR", "VERSION:2.0", "BEGIN:VEVENT",
            "DTSTART;TZID=America/Chicago:20261125T100000",
            "DTEND;TZID=America/Chicago:20261125T110000",
            "SUMMARY:Research meeting",
            "DESCRIPTION:Discuss new results\\nBring the notes",
            "LOCATION:Seminar room", "END:VEVENT", "END:VCALENDAR", "",
        ])
        item = parse_ics(source)[0]
        self.assertEqual(item["text"],
                         "Research meeting\\n\\nDiscuss new results\\nBring the notes")
        self.assertEqual(item["location"], "Seminar room")

    def test_edit_timed_appointment_metadata_and_clear_it(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "calendar.csv")
            store.append_many([{
                "date": "2026-11-25", "kind": "appointment",
                "text": "Meeting", "start_time": "09:00",
                "end_time": "10:00", "timezone": "America/Chicago",
                "location": "Office",
            }])
            version = store.revision()
            store.update(0, "2026-11-25", "Meeting adjusted", "appointment",
                         version, start_time="09:30", end_time="11:00",
                         timezone="America/Chicago", location="Library")
            entry = store.record(0)
            self.assertEqual(entry["start_time"], "09:30")
            self.assertEqual(entry["location"], "Library")
            self.assertEqual(entry["text"], "Meeting adjusted")
            with self.assertRaises(ValueError):
                store.update(0, "2026-11-25", "Invalid", "appointment",
                             store.revision(), start_time="09:30",
                             end_time="11:00", timezone="Not/AZone",
                             location="Library")
            store.update(0, "2026-11-25", "All-day", "appointment",
                         store.revision(), start_time="", end_time="",
                         timezone="", location="")
            self.assertEqual(store.record(0),
                             {"date": "2026-11-25", "kind": "appointment",
                              "text": "All-day"})

    def test_old_entries_still_three_column_when_no_timed_event(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CalendarDiary(Path(temp) / "calendar.csv")
            store.add("2026-11-25", "hello")
            self.assertEqual(store.read()[0], {"date": "2026-11-25",
                                                  "kind": "diary", "text": "hello"})


class BrowserInvitationTests(unittest.TestCase):
    def test_click_local_ics_and_preview_confirm(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "meeting.ics").write_text(INVITE, encoding="utf-8")
            store = CalendarDiary(root / "cal.csv")
            server = BrowserServer(root, calendar_path=store.path)
            server.start()
            try:
                with urlopen(server.url + "browse", timeout=5) as response:
                    listing = response.read().decode("utf-8")
                self.assertIn("Preview Invitation", listing)
                with urlopen(server.url + "view?path=meeting.ics", timeout=5) as response:
                    preview_form = response.read().decode("utf-8")
                self.assertIn("Music practice", preview_form)
                self.assertIn('type="file"', preview_form)
                self.assertIn('src="/calendar-import.js"', preview_form)
                with urlopen(server.url + "calendar-import.js", timeout=5) as response:
                    self.assertIn("text/javascript", response.headers["Content-Type"])
                    self.assertIn("file.text()", response.read().decode("utf-8"))
                self.assertFalse(store.path.exists())
                req = Request(server.url + "calendar-import-preview",
                    data=urlencode({"csrf": server.token, "ics": INVITE}).encode("utf-8"),
                    headers={"Content-Type":"application/x-www-form-urlencoded"})
                with urlopen(req, timeout=5) as response:
                    html = response.read().decode("utf-8")
                self.assertIn("14:30", html)
                self.assertIn("Room 3", html)
                self.assertFalse(store.path.exists())
            finally:
                server.close()

    def test_symlink_or_non_ics_file_not_importable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "notes.txt").write_text("not ics")
            server = BrowserServer(root, calendar_path=root / "calendar.csv")
            server.start()
            try:
                with self.assertRaises(HTTPError) as error:
                    urlopen(server.url + "calendar-import?path=notes.txt", timeout=5)
                self.assertEqual(error.exception.code, 404)
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
