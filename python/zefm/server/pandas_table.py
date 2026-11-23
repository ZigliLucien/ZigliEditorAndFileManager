"""Optional, read-only pandas DataFrame view of local CSV/TSV files.

No eval/query strings, code execution, or data writes. Pandas is imported only
when this view is requested; the browser and editor work without it.
"""
from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from .delimited_preview import MAX_CSV_BYTES, MAX_CSV_ROWS, MAX_CSV_COLUMNS
from .file_manager import BrowserError


def dataframe_preview(files, relative, sort="", descending=False, contains=""):
    path = files.resolve(relative)
    if not path.is_file() or path.suffix.casefold() not in {".csv", ".tsv"}:
        raise BrowserError("CSV/TSV file not found", 404)
    if path.stat().st_size > MAX_CSV_BYTES:
        raise BrowserError("Delimited file exceeds preview size limit", 413)
    if len(contains) > 200:
        raise BrowserError("Filter is too long")
    try:
        import pandas as pd
    except ImportError as exc:
        raise BrowserError("Pandas is not installed; install it to use the DataFrame view", 501) from exc
    try:
        frame = pd.read_csv(
            path, sep="\t" if path.suffix.casefold() == ".tsv" else ",",
            encoding="utf-8-sig", dtype=str, keep_default_na=False,
            nrows=MAX_CSV_ROWS + 1, on_bad_lines="error")
    except (UnicodeError, ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise BrowserError("Invalid CSV/TSV table", 415) from exc
    if frame.shape[1] > MAX_CSV_COLUMNS:
        raise BrowserError("Delimited file has too many columns", 413)
    truncated = len(frame) > MAX_CSV_ROWS
    frame = frame.head(MAX_CSV_ROWS)
    if contains:
        mask = frame.apply(
            lambda col: col.str.contains(contains, case=False, regex=False, na=False)
        ).any(axis=1)
        frame = frame.loc[mask]
    if sort:
        if sort not in frame.columns:
            raise BrowserError("Unknown column for sorting")
        frame = frame.sort_values(by=sort, ascending=not descending, kind="stable")
    if any(len(str(value)) > 12000 for values in frame.itertuples(index=False, name=None)
           for value in values):
        raise BrowserError("Delimited table contains oversized cells", 413)
    columns = [str(col) for col in frame.columns]
    options = ['<option value="">Original row order</option>']
    for column in columns:
        selected = ' selected' if column == sort else ''
        options.append(
            '<option value="' + escape(column, quote=True) + '"' + selected + '>'
            + escape(column) + '</option>')
    rows = ['<tr>' + ''.join('<th>' + escape(c) + '</th>' for c in columns) + '</tr>']
    for values in frame.itertuples(index=False, name=None):
        rows.append('<tr>' + ''.join('<td>' + escape(str(v)) + '</td>' for v in values) + '</tr>')
    back = '/view?' + urlencode({"path": relative, "format": "html"})
    form = ('<form method="get" action="/view" accept-charset="utf-8">'
            '<input type="hidden" name="format" value="pandas">'
            '<input type="hidden" name="path" value="' + escape(relative, quote=True) + '">'
            '<label>Filter text <input name="filter" maxlength="200" value="'
            + escape(contains, quote=True) + '"></label> '
            '<label>Sort column <select name="sort">' + ''.join(options) + '</select></label> '
            '<label><input type="checkbox" name="desc" value="1"'
            + (' checked' if descending else '') + '> Descending</label> '
            '<button type="submit">Apply</button></form>')
    return ('<h2>' + escape(path.name) + ' — pandas DataFrame</h2>'
            '<p><a href="' + escape(back, quote=True) + '">Standard CSV view</a>'
            ' · Read-only, text columns preserve leading zeros</p>'
            + form + '<div style="overflow-x:auto"><table border="1">'
            + ''.join(rows) + '</table></div>'
            + '<p>' + str(len(frame)) + ' matching rows'
            + (' (preview limited to first 1,000 source rows)' if truncated else '')
            + '</p>')
