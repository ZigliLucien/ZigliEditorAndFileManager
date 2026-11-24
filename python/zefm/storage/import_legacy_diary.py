"""One-time, non-destructive importer for original ZEFM diary-USER.txt files.

Original DiaryOut.java appended lines like 'Nov 23 | appointment details'.
These lines contain NO YEAR. Require --year explicitly rather than assigning
historical appointments to an arbitrary year. Unsupported All dates and
malformed rows fail the entire import; the source is never changed.

Usage:
    python3 -m zefm.storage.import_legacy_diary diary-user.txt --year 2024
    python3 -m zefm.storage.import_legacy_diary diary-user.txt --year 2024 --dry-run
"""
from __future__ import annotations

import argparse
import calendar
from datetime import date
from pathlib import Path
import re

from .calendar_diary import CalendarDiary, default_calendar_path

# Java MKcal used three-character English abbreviated month names.
_MONTHS = {calendar.month_abbr[n].casefold(): n for n in range(1, 13)}
_LEGACY = re.compile(r"^\s*([A-Za-z]{3})\s+([0-9]{1,2})\s*\|\s*(.*?)\s*$")


def parse_legacy_diary(source_text, year, kind="diary"):
    if not 1 <= year <= 9999:
        raise ValueError("Year must be in 1..9999")
    if kind not in {"diary", "appointment"}:
        raise ValueError("Invalid entry kind")
    entries = []
    for line_number, line in enumerate(source_text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        matched = _LEGACY.fullmatch(line)
        if matched is None:
            raise ValueError(
                f"Unsupported diary date or entry on line {line_number}: "
                "expected 'Nov 23 | entry'; All/repeating entries require separate migration")
        short_month, day, text = matched.groups()
        month = _MONTHS.get(short_month.casefold())
        if month is None:
            raise ValueError(f"Unknown diary month on line {line_number}")
        try:
            stamp = date(year, month, int(day)).isoformat()
        except ValueError as exc:
            raise ValueError(f"Invalid calendar date on line {line_number}") from exc
        if not text.strip():
            raise ValueError(f"Empty diary entry on line {line_number}")
        entries.append({"date": stamp, "kind": kind, "text": text})
    return entries


def import_legacy_diary(source, *, year, output=None, kind="diary",
                        dry_run=False, encoding="utf-8"):
    original = Path(source).expanduser()
    destination = Path(output).expanduser() if output else default_calendar_path()
    if original.resolve() == destination.resolve():
        raise ValueError("Source and destination must be different")
    entries = parse_legacy_diary(original.read_text(encoding=encoding), year, kind)
    if dry_run:
        return len(entries), 0
    store = CalendarDiary(destination)
    return store.append_many(entries, skip_duplicates=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Original diary-USER.txt")
    parser.add_argument("--year", type=int, required=True,
                        help="Year to assign to every month/day in this file (required)")
    parser.add_argument("--output", default=str(default_calendar_path()),
                        help="Destination calendar CSV (default: private ZEFM calendar)")
    parser.add_argument("--kind", choices=("diary", "appointment"), default="diary")
    parser.add_argument("--encoding", default="utf-8", help="Source file encoding")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate only; do not create or modify the CSV")
    args = parser.parse_args(argv)
    try:
        imported, skipped = import_legacy_diary(
            args.source, year=args.year, output=args.output, kind=args.kind,
            dry_run=args.dry_run, encoding=args.encoding)
    except (OSError, UnicodeError, ValueError, LookupError) as exc:
        parser.exit(1, f"Diary import failed: {exc}\n")
    if args.dry_run:
        print(f"Validated {imported} entries; nothing written.")
    else:
        print(f"Imported {imported} entries; skipped {skipped} exact duplicates."
              f" Destination: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
