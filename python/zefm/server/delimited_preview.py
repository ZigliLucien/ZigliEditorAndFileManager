"""Bounded CSV/TSV preview as HTML table or Markdown.

Always escape user-controlled cells. No spreadsheet formula evaluation and no
external programs. Preview is read-only and leaves the source unchanged.
"""
from __future__ import annotations

import csv
from html import escape
from io import StringIO
from urllib.parse import urlencode

from .file_manager import BrowserError

MAX_CSV_BYTES = 2 * 1024 * 1024
MAX_CSV_ROWS = 1000
MAX_CSV_COLUMNS = 100
MAX_CSV_CELL = 12000


def csv_preview(files, relative, format="html"):
    if format not in ("html", "markdown"):
        raise BrowserError("Unknown CSV table format")
    path = files.resolve(relative)
    if not path.is_file() or path.suffix.casefold() not in (".csv", ".tsv"):
        raise BrowserError("CSV/TSV file not found", 404)
    if path.stat().st_size > MAX_CSV_BYTES:
        raise BrowserError("Delimited file exceeds preview size limit", 413)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as input_file:
            reader = csv.reader(input_file, delimiter="\t" if path.suffix.casefold() == ".tsv" else ",")
            rows = []
            truncated = False
            for index, row in enumerate(reader):
                if index >= MAX_CSV_ROWS:
                    truncated = True
                    break
                if len(row) > MAX_CSV_COLUMNS or any(len(cell) > MAX_CSV_CELL for cell in row):
                    raise BrowserError("Delimited file has too many columns or oversized cells", 413)
                rows.append(row)
    except (UnicodeError, csv.Error) as exc:
        raise BrowserError("Invalid CSV/TSV text", 415) from exc
    def md_cell(value):
        return value.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")

    column_count = max((len(row) for row in rows), default=0)
    def padded(row):
        return row + [""] * (column_count - len(row))

    table = []
    if format == "markdown":
        if rows:
            table.append("| " + " | ".join(md_cell(v) for v in padded(rows[0])) + " |")
            table.append("| " + " | ".join(["---"] * column_count) + " |")
            for row in rows[1:]:
                table.append("| " + " | ".join(md_cell(v) for v in padded(row)) + " |")
        return "<h2>" + escape(path.name) + " — Markdown</h2><pre>" + escape("\n".join(table)) + "</pre>" + ("<p>Preview truncated.</p>" if truncated else "")
    for index, row in enumerate(rows):
        tag = "th" if index == 0 else "td"
        cells = "".join(f"<{tag}>" + escape(value) + f"</{tag}>" for value in padded(row))
        table.append("<tr>" + cells + "</tr>")
    markdown_url = "/view?" + urlencode({"path": relative, "format": "markdown"})
    html_url = "/view?" + urlencode({"path": relative, "format": "html"})
    nav = ('<p><a href="' + escape(markdown_url, quote=True) + '">Markdown table</a> · '
           '<a href="' + escape(html_url, quote=True) + '">HTML table</a></p>')
    return ('<h2>' + escape(path.name) + '</h2>' + nav +
            '<div style="overflow-x:auto"><table border="1" cellspacing="0" cellpadding="4">' +
            "".join(table) + '</table></div>' +
            ("<p>Preview truncated at 1,000 rows.</p>" if truncated else ""))
