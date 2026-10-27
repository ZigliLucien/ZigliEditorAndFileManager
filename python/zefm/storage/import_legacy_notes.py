"""Import *exported* legacy Notes records; never parse raw MyISAM files.

Input must be a UTF-8 JSON array of objects with filename, word, link, data,
or a JSONL stream of those objects. Export from a working MySQL/MariaDB
instance with a separate script and review files before import.

Usage:
  python3 -m zefm.storage.import_legacy_notes /path/to/notes.json [--output notes.json]
  python3 -m zefm.storage.import_legacy_notes /path/to/notes.jsonl --replace
"""
import argparse
import json
import sys
from pathlib import Path
from .word_notes import WordNotes


def parse_export(path):
    path = Path(path)
    if path.suffix.lower() == ".jsonl":
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                if line.strip():
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"JSONL line {line_no}: {exc}") from exc
    elif path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Notes export JSON must be an array")
        yield from data
    else:
        raise ValueError("Input must be .json or .jsonl (UTF-8)")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="UTF-8 JSON or JSONL export of legacy notes")
    parser.add_argument("--output", help="New local notes store; default XDG data directory")
    parser.add_argument("--replace", action="store_true", help="Replace matching (filename,word) records")
    args = parser.parse_args(argv)
    try:
        notes = WordNotes(args.output)
        imported, skipped = notes.import_records(parse_export(args.input), replace=args.replace)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1
    print(f"Imported {imported} notes; skipped {skipped} existing records; total {len(notes)}. Output: {notes.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
