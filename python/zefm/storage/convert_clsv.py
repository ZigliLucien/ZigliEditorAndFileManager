"""Explicit one-time conversion of legacy ZEFM .clsv tables to UTF-8 CSV.

The historic format is colon-delimited with a title: prefix, field-name
header ending in an XML record tag (often 'entry'), and '#' separators.
Because .clsv has no standard quoting for field delimiters, extra colons
are assigned to the final data field; inspect exported CSV before relying
on it. Original input is never changed.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import tempfile


def parse_clsv(content):
    rows = content.splitlines()
    position = 0
    while position < len(rows) and (not rows[position].strip()
                                    or rows[position].lstrip().startswith("#")):
        position += 1
    if position >= len(rows) or not rows[position].startswith("title:"):
        raise ValueError("Legacy .clsv must begin with title:NAME")
    title = rows[position][len("title:"):].strip()
    if not title:
        raise ValueError("Missing .clsv title")
    position += 1
    while position < len(rows) and (not rows[position].strip()
                                    or rows[position].lstrip().startswith("#")):
        position += 1
    if position >= len(rows):
        raise ValueError("Missing .clsv field headers")
    schema = [field.strip() for field in rows[position].split(":")]
    headers = schema[:-1]  # last token is the legacy XML record element
    if len(headers) < 1 or any(not col for col in headers) or not schema[-1]:
        raise ValueError("Invalid .clsv field headers")
    result = []
    for line_number, line in enumerate(rows[position + 1:], start=position + 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cells = line.split(":", maxsplit=len(headers) - 1)
        if len(cells) != len(headers):
            raise ValueError(f"Row {line_number} has fewer fields than expected")
        result.append(cells)
    return title, headers, result


def convert_file(source, destination, force=False):
    source, destination = Path(source).expanduser(), Path(destination).expanduser()
    if source.resolve() == destination.resolve():
        raise ValueError("Source and destination must differ")
    if destination.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite {destination}; use --force")
    title, headers, rows = parse_clsv(source.read_text(encoding="utf-8"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=destination.parent,
            prefix=".zefm-clsv-export-", suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            os.chmod(temporary, 0o600)
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return title, len(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Legacy .clsv input file")
    parser.add_argument("output", help="New UTF-8 .csv file")
    parser.add_argument("--force", action="store_true", help="Overwrite existing CSV")
    args = parser.parse_args(argv)
    try:
        title, count = convert_file(args.input, args.output, args.force)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, f"CLSV conversion failed: {exc}\n")
    print(f"Converted {count} rows ({title}) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
