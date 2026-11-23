"""Private calendar/diary entries stored as UTF-8 RFC 4180 CSV.

Separate from legacy MySQL, .clsv and diary-USER.txt files. Writes are atomic,
locked within one browser server, and do not overwrite legacy diary data.
"""
from __future__ import annotations

import csv
from datetime import date
import os
from pathlib import Path
import tempfile
import threading

HEADERS = ("date", "kind", "text")
MAX_ROWS = 10000
MAX_BYTES = 4 * 1024 * 1024
MAX_TEXT = 4000
KINDS = {"diary", "appointment"}


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


class CalendarDiary:
    def __init__(self, path=None):
        self.path = Path(path).expanduser() if path is not None else default_calendar_path()
        self._lock = threading.RLock()

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
                        valid_date(row["date"])
                        if row["kind"] not in KINDS:
                            raise ValueError("Invalid calendar entry type")
                        if not row["text"] or len(row["text"]) > MAX_TEXT:
                            raise ValueError("Invalid calendar entry text")
                        rows.append(row)
                except csv.Error as exc:
                    raise ValueError("Malformed calendar CSV") from exc
                return rows

    def add(self, day, text, kind="diary"):
        valid_date(day)
        if kind not in KINDS:
            raise ValueError("Invalid calendar entry type")
        if not text.strip() or len(text) > MAX_TEXT:
            raise ValueError("Diary entry must contain 1 to 4,000 characters")
        with self._lock:
            records = self.read()
            if len(records) >= MAX_ROWS:
                raise ValueError("Calendar CSV exceeds row limit")
            records.append({"date": day, "kind": kind, "text": text})
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

    def on_day(self, day):
        valid_date(day)
        return [entry for entry in self.read() if entry["date"] == day]

    def in_month(self, year, month):
        return [entry for entry in self.read()
                if entry["date"].startswith(f"{year:04d}-{month:02d}-")]
