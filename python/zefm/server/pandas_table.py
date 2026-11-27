"""Read-only, paginated pandas data browser for local CSV/TSV files."""
from __future__ import annotations

from html import escape
from pathlib import PurePosixPath
from urllib.parse import urlencode, urlsplit, quote
import math
from decimal import Decimal, localcontext
import re
import json

DATAFRAME_EXTENSIONS = frozenset({".csv", ".tsv", ".json", ".jsonl", ".ndjson", ".bib"})
JSON_EXTENSIONS = frozenset({".json", ".jsonl", ".ndjson"})

from .delimited_preview import MAX_CSV_COLUMNS, MAX_CSV_CELL
from .file_manager import BrowserError

PAGE_SIZES = (25, 50, 100, 250)
MAX_DATA_BYTES = 32 * 1024 * 1024
MAX_DATA_ROWS = 100_000
MAX_DATA_CELLS = 2_000_000


def _check_shape(rows, columns):
    if rows > MAX_DATA_ROWS or rows * max(1, columns) > MAX_DATA_CELLS:
        raise BrowserError("DataFrame exceeds 100,000 rows or 2,000,000 cells", 413)


def _read_json_records(path, pd, limit):
    """Accept records and indexed records; retain nested values and native scalars."""
    def invalid_constant(value):
        raise ValueError("Nonstandard JSON constant: " + value)
    def decode(line):
        return json.loads(line, parse_constant=invalid_constant)
    index_field = None
    if path.suffix.casefold() == ".json":
        data = decode(path.read_text(encoding="utf-8-sig"))
        if isinstance(data, dict) and "schema" in data and "data" in data:
            data = data["data"]
        if isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
            # Interpret object-of-objects as pandas orient="index".
            # Keep the original keys as an ordinary, exportable column.
            fields = {key for record in data.values() for key in record}
            index_field = "index"
            while index_field in fields:
                index_field = "_" + index_field
            from itertools import islice
            items = data.items() if limit is None else islice(data.items(), limit)
            records = [{index_field: key, **record} for key, record in items]
        elif isinstance(data, list):
            records = data if limit is None else data[:limit]
        else:
            raise ValueError("Expected a JSON array, indexed records, or pandas table data")
    else:
        records = []
        with path.open(encoding="utf-8-sig") as stream:
            for line_no, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    records.append(decode(line))
                except ValueError as exc:
                    raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
                if limit is not None and len(records) >= limit:
                    break
    if any(not isinstance(record, dict) for record in records):
        raise ValueError("Every record must be a JSON object")
    columns = list(dict.fromkeys(key for record in records for key in record))
    if len(columns) > MAX_CSV_COLUMNS:
        raise ValueError("Too many columns")
    _check_shape(len(records), len(columns))
    # Object dtype avoids converting integer identifiers or nulls to floats.
    frame = pd.DataFrame([[record.get(key) for key in columns] for record in records],
                         columns=columns, dtype=object)
    if index_field is not None:
        frame.attrs["zefm_index_field"] = index_field
    return frame


def _bib_module():
    try:
        import bibtexparser
        from bibtexparser.bparser import BibTexParser
        from bibtexparser.bwriter import BibTexWriter
        from bibtexparser.bibdatabase import BibDatabase
    except ImportError as exc:
        raise BrowserError("BibTeX requires bibtexparser 1.x: install bibtexparser>=1.4,<2", 501) from exc
    return bibtexparser, BibTexParser, BibTexWriter, BibDatabase


def _read_bib_records(path, pd):
    module, parser_class, _, _ = _bib_module()
    parser = parser_class(ignore_nonstandard_types=False, homogenize_fields=False,
                          interpolate_strings=True, common_strings=True)
    try:
        database = module.loads(path.read_text(encoding="utf-8-sig"), parser=parser)
    except Exception as exc:
        raise BrowserError("Invalid BibTeX: " + str(exc), 415) from exc
    records = database.entries
    columns = ["ID", "ENTRYTYPE"]
    columns += [key for key in dict.fromkeys(k for row in records for k in row)
                if key not in columns]
    if len(columns) > MAX_CSV_COLUMNS:
        raise BrowserError("Too many BibTeX fields", 413)
    _check_shape(len(records), len(columns))
    return pd.DataFrame([[record.get(k) for k in columns] for record in records],
                        columns=columns, dtype=object)


def _bib_export(frame):
    _, _, writer_class, database_class = _bib_module()
    database = database_class()
    database.entries = [{k: str(v) for k, v in row.items() if v is not None}
                        for row in frame.to_dict(orient="records")]
    writer = writer_class()
    writer.order_entries_by = None
    return writer.write(database)


def _display(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list, bool)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


_URL = re.compile(r"""https?://[^\s<>"'\\]+""", re.IGNORECASE)


def _linked_text(text):
    """Escape all content; link only explicit HTTP(S) URLs."""
    pieces = []
    offset = 0
    for match in _URL.finditer(text):
        url = match.group().rstrip(".,;:!?")
        for left, right in (("(", ")"), ("[", "]"), ("{", "}")):
            while url.endswith(right) and url.count(right) > url.count(left):
                url = url[:-1]
        try:
            parsed = urlsplit(url)
            valid = parsed.scheme.lower() in ("http", "https") and bool(parsed.hostname)
        except ValueError:
            valid = False
        if not valid:
            continue
        pieces.append(escape(text[offset:match.start()]))
        safe = escape(url, quote=True)
        pieces.append('<a href="' + safe + '" target="_blank" rel="noopener noreferrer">' + safe + '</a>')
        offset = match.start() + len(url)
    pieces.append(escape(text[offset:]))
    return "".join(pieces)


def _linked_cell(value):
    """Render nested JSON recursively so URL boundaries remain intact."""
    if isinstance(value, list):
        return "[" + ", ".join(_linked_cell(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(
            escape(json.dumps(key, ensure_ascii=False)) + ": " + _linked_cell(item)
            for key, item in value.items()) + "}"
    if isinstance(value, str):
        return _linked_text(value)
    return escape(_display(value))


def _bibliography_cell(column, value, record):
    if isinstance(value, str):
        raw = value.strip()
        target = None
        if column.casefold() == "doi" and re.fullmatch(r"10\.\d{4,9}/[^\s<>]+", raw):
            target = "https://doi.org/" + quote(raw, safe="/")
        elif column.casefold() == "eprint":
            archive = str(record.get("archiveprefix") or record.get("archivePrefix") or "").casefold()
            if archive == "arxiv" or raw.lower().startswith("arxiv:"):
                identifier = re.sub(r"^arxiv:\s*", "", raw, flags=re.I)
                if re.fullmatch(r"(?:\d{4}\.\d{4,5}|[a-zA-Z.-]+/\d{7})(?:v\d+)?", identifier):
                    target = "https://arxiv.org/abs/" + quote(identifier, safe="/")
        if target:
            return '<a href="' + escape(target, quote=True) + '" target="_blank" rel="noopener noreferrer">' + escape(value) + '</a>'
    return _linked_cell(value)


# Bounded process-local LRU. Only parsed, validated source frames are cached;
# callers must not modify them in place.
from collections import OrderedDict
from threading import RLock

_CACHE = OrderedDict()
_CACHE_LOCK = RLock()
CACHE_MAX_FILES = 8
CACHE_MAX_CELLS = MAX_DATA_CELLS
CACHE_MAX_BYTES = 128 * 1024 * 1024


def _signature(path):
    stat = path.stat()
    return (stat.st_dev, stat.st_ino, stat.st_size,
            stat.st_mtime_ns, stat.st_ctime_ns)


def _read_frame(path, pd, full):
    suffix = path.suffix.casefold()
    if suffix == ".bib":
        frame = _read_bib_records(path, pd)
    elif suffix in JSON_EXTENSIONS:
        frame = _read_json_records(path, pd, MAX_DATA_ROWS + 1)
    else:
        frame = pd.read_csv(
            path, sep="\t" if suffix == ".tsv" else ",",
            encoding="utf-8-sig", dtype=str, keep_default_na=False,
            nrows=MAX_DATA_ROWS + 1, on_bad_lines="error")
    _check_shape(*frame.shape)
    if frame.shape[1] > MAX_CSV_COLUMNS:
        raise BrowserError("Delimited file has too many columns", 413)
    if any(len(_display(value)) > MAX_CSV_CELL
           for values in frame.itertuples(index=False, name=None)
           for value in values):
        raise BrowserError("Delimited table contains oversized cells", 413)
    return frame


def _cached_frame(path, pd, full=False):
    # All supported sources now use one complete, bounded frame for every view.
    full = True
    with _CACHE_LOCK:
        signature = _signature(path)
        if signature[2] > MAX_DATA_BYTES:
            raise BrowserError("Data file exceeds 32 MiB size limit", 413)
        for key in list(_CACHE):
            if key[0] == path and key[1] != signature:
                del _CACHE[key]
        key = (path, signature, full)
        complete = (path, signature, True)
        if not full and complete in _CACHE:
            key = complete
        if key in _CACHE:
            _CACHE.move_to_end(key)
            return _CACHE[key][0]
        frame = _read_frame(path, pd, full)
        if _signature(path) != signature:
            raise BrowserError("Data file changed while reading; retry", 409)
        cells = frame.shape[0] * max(1, frame.shape[1])
        # Estimate object storage, including nested JSON's serialized contents.
        size = int(frame.memory_usage(index=True, deep=True).sum())
        size += sum(len(_display(v).encode("utf-8"))
                    for row in frame.itertuples(index=False, name=None)
                    for v in row if isinstance(v, (dict, list)))
        if cells <= CACHE_MAX_CELLS and size <= CACHE_MAX_BYTES:
            while _CACHE and (len(_CACHE) >= CACHE_MAX_FILES
                              or sum(v[1] for v in _CACHE.values()) + size > CACHE_MAX_BYTES
                              or sum(v[2] for v in _CACHE.values()) + cells > CACHE_MAX_CELLS):
                _CACHE.popitem(last=False)
            _CACHE[(path, signature, full)] = (frame, size, cells)
        return frame


def _column_totals(frame, selected):
    """Exact decimal totals for ordinary numeric fields; blanks are missing."""
    totals = {}
    for column in selected:
        total = Decimal(0)
        used = 0
        with localcontext() as ctx:
            ctx.prec = 512
            for index, value in frame[column].items():
                if value is None or (isinstance(value, str) and not value.strip()):
                    continue
                raw = _display(value).strip()
                if (len(raw) > 100 or not re.fullmatch(
                        r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d{1,3})?", raw)):
                    raise BrowserError(f"Cannot total {column}: nonnumeric value at source row {index + 1}")
                number = Decimal(raw)
                if not number.is_finite() or abs(number.as_tuple().exponent) > 200 or abs(number.adjusted()) > 200:
                    raise BrowserError(f"Cannot total {column}: number out of range at source row {index + 1}")
                total += number
                used += 1
        totals[column] = format(total, "f") if used else ""
    return totals


def _transpose_frame(frame, pd):
    """Rotate a complete source table, preserving both axes as data."""
    if len(frame) + 1 > MAX_CSV_COLUMNS:
        raise BrowserError("Transpose requires at most " + str(MAX_CSV_COLUMNS - 1) +
                           " source rows; the result would have too many columns", 413)
    index_field = frame.attrs.get("zefm_index_field")
    if index_field is not None and index_field in frame.columns:
        labels = [str(v) for v in frame[index_field]]
        values = frame.drop(columns=[index_field])
    else:
        labels = [str(i + 1) for i in range(len(frame))]
        values = frame
    field = "field"
    while field in labels:
        field = "_" + field
    rotated = values.T.copy()
    rotated.columns = labels
    rotated.insert(0, field, [str(c) for c in values.columns])
    return rotated.reset_index(drop=True)


def dataframe_preview(files, relative, sort="", descending=False, contains="",
                      column="", sort_type="text", page=1, page_size=50, export="", total1="", total2="", total3="", transpose=False, hidden=""):
    if export not in ("", "json", "jsonl", "markdown", "csv", "html", "bib"):
        raise BrowserError("Unknown DataFrame export format")
    path = files.resolve(relative)
    if not path.is_file() or path.suffix.casefold() not in DATAFRAME_EXTENSIONS:
        raise BrowserError("Data file not found", 404)
    if path.stat().st_size > MAX_DATA_BYTES:
        raise BrowserError("Data file exceeds 32 MiB size limit", 413)
    if len(contains) > 200:
        raise BrowserError("Filter is too long")
    if sort_type not in ("text", "number") or page < 1 or page_size not in PAGE_SIZES:
        raise BrowserError("Invalid table display options")
    try:
        import pandas as pd
    except ImportError as exc:
        raise BrowserError("Pandas is not installed; install it to use the DataFrame view", 501) from exc
    is_json = path.suffix.casefold() in JSON_EXTENSIONS
    is_bib = path.suffix.casefold() == ".bib"
    if export == "bib" and not is_bib:
        raise BrowserError("BibTeX export currently requires a BibTeX source")
    selected = list(dict.fromkeys(c for c in (total1, total2, total3) if c))
    if transpose and is_bib:
        raise BrowserError("Transpose is not supported for bibliographies")
    if selected and export == "bib":
        raise BrowserError("Totals are not supported in BibTeX exports")
    try:
        frame = _cached_frame(path, pd, full=bool(export or selected or transpose))
    except (UnicodeError, ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise BrowserError("Invalid data table: " + str(exc), 415) from exc
    if transpose:
        frame = _transpose_frame(frame, pd)
    source_count = len(frame)
    columns = [str(col) for col in frame.columns]
    try:
        omitted = json.loads(hidden) if hidden else []
        if not isinstance(omitted, list) or any(not isinstance(c, str) or c not in columns for c in omitted):
            raise ValueError("Unknown hidden column")
    except (ValueError, TypeError) as exc:
        raise BrowserError("Invalid column selection") from exc
    shown = [c for c in columns if c not in omitted]
    if columns and not shown:
        raise BrowserError("At least one column must remain visible")
    if omitted and export == "bib":
        raise BrowserError("Show all fields before exporting BibTeX")
    if any(c not in shown for c in selected):
        raise BrowserError("Unknown total column")
    if column and column not in columns:
        raise BrowserError("Unknown filter column")
    if sort and sort not in columns:
        raise BrowserError("Unknown column for sorting")
    if contains:
        if column:
            mask = frame[column].map(_display).str.contains(contains, case=False, regex=False, na=False)
        else:
            mask = frame.apply(
                lambda col: col.map(_display).str.contains(contains, case=False, regex=False, na=False)
            ).any(axis=1)
        frame = frame.loc[mask]
    if sort:
        if sort_type == "number":
            frame = frame.sort_values(by=sort, ascending=not descending, kind="stable",
                                      key=lambda values: pd.to_numeric(values.map(_display), errors="coerce"),
                                      na_position="last")
        else:
            frame = frame.sort_values(by=sort, ascending=not descending, kind="stable", key=lambda values: values.map(_display))
    totals = _column_totals(frame, selected)
    if export:
        frame = frame[shown]
        columns = shown
        if totals:
            # A dedicated, collision-safe label column distinguishes the
            # derived summary row from actual source records.
            label = "__summary__"
            while label in columns:
                label += "_"
            frame = frame.copy()
            frame[label] = None
            columns = [label] + columns
            frame = frame[columns]
            summary_record = dict.fromkeys(columns)
            summary_record.update(totals)
            summary_record[label] = "Total"
            frame = pd.concat([frame, pd.DataFrame([summary_record], columns=columns, dtype=object)],
                              ignore_index=True)
        if export == "bib":
            return _bib_export(frame)
        if export == "json":
            return json.dumps(frame.to_dict(orient="records"), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if export == "jsonl":
            return "".join(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n" for record in frame.to_dict(orient="records"))
        if export == "csv":
            return frame.apply(lambda col: col.map(_display)).to_csv(index=False)
        if export == "html":
            return ('<!doctype html>\n<html><head><meta charset="utf-8">'
                    '<title>' + escape(path.name) + '</title></head><body>\n'
                    + frame.apply(lambda col: col.map(_display)).to_html(index=False, escape=True) + '\n</body></html>\n')
        # Avoid requiring the optional tabulate dependency. Escape table
        # separators, HTML, and inline Markdown formatting in literal cells.
        def cell(value):
            value = escape(_display(value), quote=False).replace("\\", "\\\\")
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
              "sort_type": sort_type, "page_size": page_size, "page": page,
              "total1": total1, "total2": total2, "total3": total3,
              "transpose": int(transpose), "hidden": hidden}

    def link(label, **changes):
        return '<a href="' + e('/view?' + urlencode(dict(params, **changes))) + '">' + e(label) + '</a>'

    def options(items, selected):
        return ''.join('<option value="' + e(value) + '"' +
                       (' selected' if value == selected else '') + '>' +
                       e(label) + '</option>' for value, label in items)

    headings = []
    for c in shown:
        arrow = (' ↓' if descending else ' ↑') if c == sort else ''
        headings.append('<th>' + link(c + arrow, sort=c, desc=int(not descending) if c == sort else 0, page=1) + '</th>')
    rows = ['<tr><th>Row</th>' + ''.join(headings) + '</tr>']
    for values in visible.itertuples(index=True, name=None):
        record = dict(zip(columns, values[1:]))
        rows.append('<tr><th>' + e(values[0] + 1) + '</th>' +
                    ''.join('<td>' + (_bibliography_cell(c, record[c], record) if is_bib else _linked_cell(record[c])) + '</td>' for c in shown) + '</tr>')
    if totals:
        rows.append('<tr><th>Total</th>' + ''.join('<td><strong>' + e(totals.get(c, "")) + '</strong></td>' for c in shown) + '</tr>')
    back = '/view?' + urlencode({"path": relative} if is_json or is_bib else {"path": relative, "format": "html"})
    parent = str(PurePosixPath(relative).parent)
    directory = '/listing?' + urlencode({"path": "" if parent == "." else parent})
    reset = '/view?' + urlencode({"path": relative, "format": "pandas", "transpose": int(transpose)})
    orientation = "" if is_bib else (" · " + link(
        "Normal view" if transpose else "Transpose", transpose=int(not transpose),
        sort="", desc=0, filter="", column="", total1="", total2="", total3="", hidden="", page=1))
    column_links = []
    for c in columns:
        if c in omitted:
            changed = [v for v in omitted if v != c]
            label = "Show " + c
        elif len(shown) > 1:
            changed = omitted + [c]
            label = "Hide " + c
        else:
            continue
        column_links.append(link(label, hidden=json.dumps(changed, ensure_ascii=False),
                                 total1="" if total1 == c else total1,
                                 total2="" if total2 == c else total2,
                                 total3="" if total3 == c else total3))
    column_controls = ('<details><summary>Columns (' + str(len(shown)) + ' of ' +
                       str(len(columns)) + ' visible)</summary><p>' +
                       link("Show all columns", hidden="") + ' · ' +
                       ' · '.join(column_links) + '</p></details>') if columns else ""
    total_controls = ''.join(
        '<label>Total column ' + str(i) + ' <select name="total' + str(i) + '">' +
        options([("", "None")] + [(c, c) for c in shown], chosen) + '</select></label> '
        for i, chosen in enumerate((total1, total2, total3), 1))
    form = ('<form method="get" action="/view" accept-charset="utf-8">'
            '<input type="hidden" name="format" value="pandas">'
            '<input type="hidden" name="transpose" value="' + str(int(transpose)) + '">'
            '<input type="hidden" name="path" value="' + e(relative) + '">' 
            '<input type="hidden" name="hidden" value="' + e(hidden) + '">'
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
            + total_controls +
            '<button type="submit">Apply</button> <a href="' + e(reset) + '">Reset</a></form>')
    nav = '<p>' + (' '.join([link("First", page=1), link("Previous", page=page-1)]) if page > 1 else '') 
    nav += ' Page ' + str(page) + ' of ' + str(pages) + ' '
    nav += (' '.join([link("Next", page=page+1), link("Last", page=pages)]) if page < pages else '') + '</p>'
    summary = str(count) + ' matching rows of ' + str(source_count)
    if count:
        summary += ' — showing ' + str(start + 1) + '–' + str(start + len(visible))
    if transpose:
        summary += ' — transposed view'
    if totals:
        summary += ' — totals across all matching rows (blank values omitted)'
    exports = '<p>Export all matching records (visible columns): ' + ' · '.join(
        link(label, export=kind) for kind, label in (
            ("json", "JSON"), ("jsonl", "JSONL"), ("markdown", "Markdown"),
            ("csv", "CSV"), ("html", "HTML")) + ((("bib", "BibTeX"),) if is_bib and not selected and not omitted else ())) + '</p>'
    return ('<h2>' + e(path.name) + ' — pandas DataFrame</h2>'
            '<p><a href="' + e(directory) + '">Return to source directory</a> · '
            '<a href="' + e(back) + '">Standard source view</a>'
            + orientation + ' · Read-only, original string identifiers preserved</p>'
            + form + column_controls + exports + '<p>' + e(summary) + '</p>' + nav
            + '<div style="overflow-x:auto"><table border="1" cellspacing="0" cellpadding="4">'
            + ''.join(rows) + '</table></div>' + nav)
