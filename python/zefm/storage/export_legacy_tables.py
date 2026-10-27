"""One-time export from an independently restored MySQL/MariaDB ZEFM database.

This utility is NOT used by the ZEFM editor. It requires optional PyMySQL,
and deliberately exports only the legacy `notes` or `dictionaries` tables.
Output is UTF-8 JSONL, one record per line, with original database field names.
For the Notes importer run: python3 -m zefm.storage.import_legacy_notes notes.jsonl

The original .frm/.MYD/.MYI archive cannot be passed to this utility directly.
"""

import argparse
import getpass
import json
import os
import sys
import tempfile
from pathlib import Path

TABLE_COLUMNS = {
    "notes": ("filename", "word", "link", "data"),
    "dictionaries": ("lang", "word", "data"),
}


def convert_row(columns, row):
    """Strict UTF-8 conversion; do not silently repair source text."""
    if len(row) != len(columns):
        raise ValueError("Unexpected legacy table column count")
    result = {}
    for name, value in zip(columns, row):
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if not isinstance(value, str):
            raise ValueError(f"Legacy field {name!r} has invalid type {type(value).__name__}")
        result[name] = value
    return result


def write_rows(output, columns, rows, *, expected_count=None, overwrite=False):
    """Write validated records atomically, with strict record-count checking."""
    target = Path(output).expanduser()
    if target.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite {target}; use --force")
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    count = 0
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n",
                                         dir=target.parent, prefix=".zefm-export-",
                                         suffix=".jsonl", delete=False) as f:
            temp = Path(f.name)
            os.chmod(temp, 0o600)
            for row in rows:
                record = convert_row(columns, row)
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
            f.flush()
            os.fsync(f.fileno())
        if expected_count is not None and count != expected_count:
            raise ValueError(f"Record count mismatch: database={expected_count}, export={count}")
        os.replace(temp, target)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
    return count


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table",choices=sorted(TABLE_COLUMNS))
    parser.add_argument("output",help="Path to UTF-8 JSONL file")
    parser.add_argument("--database",default="ZEFMdb",help="Restored database name")
    parser.add_argument("--host",default="localhost")
    parser.add_argument("--port",type=int,default=3306)
    parser.add_argument("--user",default="root")
    parser.add_argument("--socket",help="Optional Unix domain socket path")
    parser.add_argument("--force",action="store_true",help="Overwrite previous export")
    args=parser.parse_args(argv)
    try:
        import pymysql  # optional dependency only for one-time migration
    except ImportError:
        print("Install PyMySQL for migration only (python3 -m pip install pymysql)",file=sys.stderr)
        return 2
    password=getpass.getpass("Password for legacy database: ")
    opts=dict(user=args.user,password=password,database=args.database,
              charset="utf8mb4",use_unicode=True)
    if args.socket:opts["unix_socket"]=args.socket
    else:opts.update(host=args.host,port=args.port)
    try:
        connection=pymysql.connect(**opts)
        try:
            with connection.cursor() as c:
                c.execute(f"SELECT COUNT(*) FROM `{args.table}`")
                expected=int(c.fetchone()[0])
            columns=TABLE_COLUMNS[args.table]
            fields=", ".join(f"`{column}`" for column in columns)
            with connection.cursor(pymysql.cursors.SSCursor) as c:
                c.execute(f"SELECT {fields} FROM `{args.table}`")
                count=write_rows(args.output,columns,iter(c.fetchone,None),
                                 expected_count=expected,overwrite=args.force)
        finally:
            connection.close()
    except (OSError, UnicodeError, ValueError, pymysql.MySQLError) as exc:
        print(f"Export failed: {exc}",file=sys.stderr)
        return 1
    print(f"Exported {count} {args.table} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
