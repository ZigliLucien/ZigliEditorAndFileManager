"""Private calendar/diary entries stored as UTF-8 RFC 4180 CSV.

Separate from legacy MySQL, .clsv and diary-USER.txt files. All writes are
atomic, with a revision check for edits/deletions and a per-instance lock.
"""
from __future__ import annotations

import csv
from datetime import date
import hashlib
import hmac
import os
from pathlib import Path
import re
import tempfile
import threading

HEADERS = ("date", "kind", "text")
MAX_ROWS = 10000
MAX_BYTES = 4 * 1024 * 1024
MAX_TEXT = 4000
KINDS = {"diary", "appointment"}
_REVISION_RE = re.compile(r"[0-9a-f]{64}\Z")


class CalendarConflictError(ValueError):
    """An entry changed since a browser form was opened."""


class CalendarEntryNotFound(ValueError):
    """The requested row number or date is not present."""


def default_calendar_path():
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_home / "zefm" / "calendar.csv"


def valid_date(value):
    try:
        day = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Date must be YYYY-MM-DD") from exc
    if day.isoformat() != value:
        raise ValueError("Date must be YYYY-MM-DD")
    return value


def validated_record(day, kind, text):
    valid_date(day)
    if kind not in KINDS:
        raise ValueError("Invalid calendar entry type")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT:
        raise ValueError("Diary entry must contain 1 to 4,000 characters")
    return {"date": day, "kind": kind, "text": text}


class CalendarDiary:
    def __init__(self, path=None):
        self.path = Path(path).expanduser() if path is not None else default_calendar_path()
        self._lock = threading.RLock()

    def _revision_locked(self):
        if not self.path.exists():
            return hashlib.sha256(b"").hexdigest()
        if self.path.stat().st_size > MAX_BYTES:
            raise ValueError("Calendar CSV exceeds size limit")
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def revision(self):
        """Digest of the complete source file, for optimistic concurrency."""
        with self._lock:
            return self._revision_locked()

    def _check_revision_locked(self, expected):
        if not isinstance(expected, str) or not _REVISION_RE.fullmatch(expected):
            raise ValueError("Missing or invalid calendar revision")
        if not hmac.compare_digest(self._revision_locked(), expected):
            raise CalendarConflictError("Calendar changed elsewhere; reload before saving")

    def read(self):
        with self._lock:
            if not self.path.exists():
                return []
            if self.path.stat().st_size > MAX_BYTES:
                raise ValueError("Calendar CSV exceeds size limit")
            with self.path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream, strict=True)
                if reader.fieldnames != list(HEADERS):
                    raise ValueError("Calendar CSV columns must be date,kind,text")
                rows = []
                try:
                    for row in reader:
                        if len(rows) >= MAX_ROWS:
                            raise ValueError("Calendar CSV exceeds row limit")
                        if None in row or any(value is None for value in row.values()):
                            raise ValueError("Invalid calendar CSV row")
                        rows.append(validated_record(row["date"], row["kind"], row["text"]))
                except csv.Error as exc:
                    raise ValueError("Malformed calendar CSV") from exc
                return rows

    def _write_locked(self, records):
        if len(records) > MAX_ROWS:
            raise ValueError("Calendar CSV exceeds row limit")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", newline="",
                dir=self.path.parent, prefix=".zefm-calendar-", suffix=".tmp",
                delete=False
            ) as stream:
                temp = Path(stream.name)
                os.chmod(temp, 0o600)
                writer = csv.DictWriter(stream, fieldnames=HEADERS)
                writer.writeheader()
                writer.writerows(records)
                stream.flush()
                os.fsync(stream.fileno())
            if temp.stat().st_size > MAX_BYTES:
                raise ValueError("Calendar CSV exceeds size limit")
            os.replace(temp, self.path)
            temp = None
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)

    def add(self, day, text, kind="diary"):
        record = validated_record(day, kind, text)
        with self._lock:
            records = self.read()
            records.append(record)
            self._write_locked(records)

    def append_many(self, entries, *, skip_duplicates=True):
        """Import a batch atomically. Repeated imports skip exact duplicate rows."""
        validated = [validated_record(item["date"], item["kind"], item["text"])
                     for item in entries]
        with self._lock:
            records = self.read()
            existing = {(r["date"], r["kind"], r["text"]) for r in records}
            added = 0
            for record in validated:
                key = (record["date"], record["kind"], record["text"])
                if skip_duplicates and key in existing:
                    continue
                records.append(record)
                existing.add(key)
                added += 1
            if added:
                self._write_locked(records)
            return added, len(validated) - added

    def record(self, index, expected_day=None):
        with self._lock:
            records = self.read()
            if type(index) is not int or not 0 <= index < len(records):
                raise CalendarEntryNotFound("Calendar entry not found")
            selected = records[index]
            if expected_day is not None and selected["date"] != valid_date(expected_day):
                raise CalendarEntryNotFound("Entry does not belong to that date")
            return dict(selected)

    def update(self, index, day, text, kind, expected_revision, expected_day=None):
        new = validated_record(day, kind, text)
        with self._lock:
            self._check_revision_locked(expected_revision)
            records = self.read()
            if type(index) is not int or not 0 <= index < len(records):
                raise CalendarEntryNotFound("Calendar entry not found")
            if expected_day is not None and records[index]["date"] != valid_date(expected_day):
                raise CalendarEntryNotFound("Entry does not belong to that date")
            records[index] = new
            self._write_locked(records)

    def delete(self, index, expected_revision, expected_day=None):
        with self._lock:
            self._check_revision_locked(expected_revision)
            records = self.read()
            if type(index) is not int or not 0 <= index < len(records):
                raise CalendarEntryNotFound("Calendar entry not found")
            if expected_day is not None and records[index]["date"] != valid_date(expected_day):
                raise CalendarEntryNotFound("Entry does not belong to that date")
            removed = records.pop(index)
            self._write_locked(records)
            return removed

    def on_day(self, day):
        valid_date(day)
        return [entry for entry in self.read() if entry["date"] == day]

    def in_month(self, year, month):
        return [entry for entry in self.read()
                if entry["date"].startswith(f"{year:04d}-{month:02d}-")]
