"""Read-only, paginated pandas data browser for local CSV/TSV files."""
from __future__ import annotations

from html import escape
from pathlib import PurePosixPath
from urllib.parse import urlencode
import math

from .delimited_preview import MAX_CSV_BYTES, MAX_CSV_ROWS, MAX_CSV_COLUMNS, MAX_CSV_CELL
from .file_manager import BrowserError

PAGE_SIZES = (25, 50, 100, 250)


def dataframe_preview(files, relative, sort="", descending=False, contains="",
                      column="", sort_type="text", page=1, page_size=50, export=""):
    if export not in ("", "json", "jsonl", "markdown", "csv", "html"):
        raise BrowserError("Unknown DataFrame export format")
    path = files.resolve(relative)
    if not path.is_file() or path.suffix.casefold() not in {".csv", ".tsv"}:
        raise BrowserError("CSV/TSV file not found", 404)
    if path.stat().st_size > MAX_CSV_BYTES:
        raise BrowserError("Delimited file exceeds preview size limit", 413)
    if len(contains) > 200:
        raise BrowserError("Filter is too long")
    if sort_type not in ("text", "number") or page < 1 or page_size not in PAGE_SIZES:
        raise BrowserError("Invalid table display options")
    try:
        import pandas as pd
    except ImportError as exc:
        raise BrowserError("Pandas is not installed; install it to use the DataFrame view", 501) from exc
    try:
        frame = pd.read_csv(
            path, sep="\t" if path.suffix.casefold() == ".tsv" else ",",
            encoding="utf-8-sig", dtype=str, keep_default_na=False,
            nrows=None if export else MAX_CSV_ROWS + 1, on_bad_lines="error")
    except (UnicodeError, ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise BrowserError("Invalid CSV/TSV table", 415) from exc
    if frame.shape[1] > MAX_CSV_COLUMNS:
        raise BrowserError("Delimited file has too many columns", 413)
    truncated = len(frame) > MAX_CSV_ROWS
    if not export:
        frame = frame.head(MAX_CSV_ROWS)
    source_count = len(frame)
    columns = [str(col) for col in frame.columns]
    if column and column not in columns:
        raise BrowserError("Unknown filter column")
    if sort and sort not in columns:
        raise BrowserError("Unknown column for sorting")
    if any(len(str(value)) > MAX_CSV_CELL for values in frame.itertuples(index=False, name=None)
           for value in values):
        raise BrowserError("Delimited table contains oversized cells", 413)
    if contains:
        if column:
            mask = frame[column].str.contains(contains, case=False, regex=False, na=False)
        else:
            mask = frame.apply(
                lambda col: col.str.contains(contains, case=False, regex=False, na=False)
            ).any(axis=1)
        frame = frame.loc[mask]
    if sort:
        if sort_type == "number":
            frame = frame.sort_values(by=sort, ascending=not descending, kind="stable",
                                      key=lambda values: pd.to_numeric(values, errors="coerce"),
                                      na_position="last")
        else:
            frame = frame.sort_values(by=sort, ascending=not descending, kind="stable")
    if export:
        if export == "json":
            return frame.to_json(orient="records", force_ascii=False, indent=2) + "\n"
        if export == "jsonl":
            return frame.to_json(orient="records", force_ascii=False, lines=True)
        if export == "csv":
            return frame.to_csv(index=False)
        if export == "html":
            return ('<!doctype html>\n<html><head><meta charset="utf-8">'
                    '<title>' + escape(path.name) + '</title></head><body>\n'
                    + frame.to_html(index=False, escape=True) + '\n</body></html>\n')
        # Avoid requiring the optional tabulate dependency. Escape table
        # separators, HTML, and inline Markdown formatting in literal cells.
        def cell(value):
            value = escape(str(value), quote=False).replace("\\", "\\\\")
            for char in "|*_[]~" + chr(96):
                value = value.replace(char, "\\" + char)
            return value.replace("\r\n", "<br>").replace("\r", "<br>").replace("\n", "<br>")
        def row(values):
            return "| " + " | ".join(cell(v) for v in values) + " |"
        return "\n".join([row(columns), "| " + " | ".join(["---"] * len(columns)) + " |"]
                         + [row(values) for values in frame.itertuples(index=False, name=None)]) + "\n"
    count = len(frame)
    pages = max(1, math.ceil(count / page_size))
    page = min(page, pages)
    start = (page - 1) * page_size
    visible = frame.iloc[start:start + page_size]

    def e(value):
        return escape(str(value), quote=True)

    params = {"path": relative, "format": "pandas", "sort": sort,
              "desc": int(descending), "filter": contains, "column": column,
              "sort_type": sort_type, "page_size": page_size, "page": page}

    def link(label, **changes):
        return '<a href="' + e('/view?' + urlencode(dict(params, **changes))) + '">' + e(label) + '</a>'

    def options(items, selected):
        return ''.join('<option value="' + e(value) + '"' +
                       (' selected' if value == selected else '') + '>' +
                       e(label) + '</option>' for value, label in items)

    headings = []
    for c in columns:
        arrow = (' ↓' if descending else ' ↑') if c == sort else ''
        headings.append('<th>' + link(c + arrow, sort=c, desc=int(not descending) if c == sort else 0, page=1) + '</th>')
    rows = ['<tr><th>Row</th>' + ''.join(headings) + '</tr>']
    for values in visible.itertuples(index=True, name=None):
        rows.append('<tr><th>' + e(values[0] + 1) + '</th>' +
                    ''.join('<td>' + e(v) + '</td>' for v in values[1:]) + '</tr>')
    back = '/view?' + urlencode({"path": relative, "format": "html"})
    parent = str(PurePosixPath(relative).parent)
    directory = '/listing?' + urlencode({"path": "" if parent == "." else parent})
    reset = '/view?' + urlencode({"path": relative, "format": "pandas"})
    form = ('<form method="get" action="/view" accept-charset="utf-8">'
            '<input type="hidden" name="format" value="pandas">'
            '<input type="hidden" name="path" value="' + e(relative) + '">'
            '<label>Filter text <input name="filter" maxlength="200" value="' + e(contains) + '"></label> '
            '<label>Filter column <select name="column">' +
            options([("", "All columns")] + [(c, c) for c in columns], column) + '</select></label> '
            '<label>Sort column <select name="sort">' +
            options([("", "Original row order")] + [(c, c) for c in columns], sort) + '</select></label> '
            '<label>Sort as <select name="sort_type">' +
            options([("text", "Text"), ("number", "Number")], sort_type) + '</select></label> '
            '<label><input type="checkbox" name="desc" value="1"' +
            (' checked' if descending else '') + '> Descending</label> '
            '<label>Rows per page <select name="page_size">' +
            options([(n, n) for n in PAGE_SIZES], page_size) + '</select></label> '
            '<button type="submit">Apply</button> <a href="' + e(reset) + '">Reset</a></form>')
    nav = '<p>' + (' '.join([link("First", page=1), link("Previous", page=page-1)]) if page > 1 else '') 
    nav += ' Page ' + str(page) + ' of ' + str(pages) + ' '
    nav += (' '.join([link("Next", page=page+1), link("Last", page=pages)]) if page < pages else '') + '</p>'
    summary = str(count) + ' matching rows of ' + str(source_count)
    if count:
        summary += ' — showing ' + str(start + 1) + '–' + str(start + len(visible))
    if truncated:
        summary += ' (preview limited to first ' + str(MAX_CSV_ROWS) + ' source rows)'
    exports = '<p>Export all matching records: ' + ' · '.join(
        link(label, export=kind) for kind, label in (
            ("json", "JSON"), ("jsonl", "JSONL"), ("markdown", "Markdown"),
            ("csv", "CSV"), ("html", "HTML"))) + '</p>'
    return ('<h2>' + e(path.name) + ' — pandas DataFrame</h2>'
            '<p><a href="' + e(directory) + '">Return to source directory</a> · '
            '<a href="' + e(back) + '">Standard CSV view</a>'
            ' · Read-only, text columns preserve leading zeros</p>'
            + form + exports + '<p>' + e(summary) + '</p>' + nav
            + '<div style="overflow-x:auto"><table border="1" cellspacing="0" cellpadding="4">'
            + ''.join(rows) + '</table></div>' + nav)
