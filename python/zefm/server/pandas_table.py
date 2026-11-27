"""Read-only, paginated pandas data browser for local CSV/TSV files."""
from __future__ import annotations

from html import escape
from pathlib import PurePosixPath
from urllib.parse import urlencode, urlsplit, quote
import math
import re
import json

DATAFRAME_EXTENSIONS = frozenset({".csv", ".tsv", ".json", ".jsonl", ".ndjson", ".bib"})
JSON_EXTENSIONS = frozenset({".json", ".jsonl", ".ndjson"})

from .delimited_preview import MAX_CSV_BYTES, MAX_CSV_ROWS, MAX_CSV_COLUMNS, MAX_CSV_CELL
from .file_manager import BrowserError

PAGE_SIZES = (25, 50, 100, 250)


def _read_json_records(path, pd, limit):
    """Accept records only; retain nested JSON values and native scalars."""
    def invalid_constant(value):
        raise ValueError("Nonstandard JSON constant: " + value)
    def decode(line):
        return json.loads(line, parse_constant=invalid_constant)
    if path.suffix.casefold() == ".json":
        data = decode(path.read_text(encoding="utf-8-sig"))
        if isinstance(data, dict) and "schema" in data and "data" in data:
            data = data["data"]
        if not isinstance(data, list):
            raise ValueError("Expected a JSON array of records or pandas table data")
        records = data if limit is None else data[:limit]
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
    # Object dtype avoids converting integer identifiers or nulls to floats.
    return pd.DataFrame([[record.get(key) for key in columns] for record in records],
                        columns=columns, dtype=object)


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
CACHE_MAX_CELLS = 500_000
CACHE_MAX_BYTES = 32 * 1024 * 1024


def _signature(path):
    stat = path.stat()
    return (stat.st_dev, stat.st_ino, stat.st_size,
            stat.st_mtime_ns, stat.st_ctime_ns)


def _read_frame(path, pd, full):
    suffix = path.suffix.casefold()
    if suffix == ".bib":
        frame = _read_bib_records(path, pd)
    elif suffix in JSON_EXTENSIONS:
        frame = _read_json_records(path, pd, None if full else MAX_CSV_ROWS + 1)
    else:
        frame = pd.read_csv(
            path, sep="\t" if suffix == ".tsv" else ",",
            encoding="utf-8-sig", dtype=str, keep_default_na=False,
            nrows=None if full else MAX_CSV_ROWS + 1, on_bad_lines="error")
    if frame.shape[1] > MAX_CSV_COLUMNS:
        raise BrowserError("Delimited file has too many columns", 413)
    if any(len(_display(value)) > MAX_CSV_CELL
           for values in frame.itertuples(index=False, name=None)
           for value in values):
        raise BrowserError("Delimited table contains oversized cells", 413)
    return frame


def _cached_frame(path, pd, full=False):
    # BibTeX parsing always loads the entire file, so preview and export share
    # one entry. Other formats retain the existing bounded preview read.
    full = bool(full or path.suffix.casefold() == ".bib")
    with _CACHE_LOCK:
        signature = _signature(path)
        if signature[2] > MAX_CSV_BYTES:
            raise BrowserError("Data file exceeds 2 MB size limit", 413)
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


def dataframe_preview(files, relative, sort="", descending=False, contains="",
                      column="", sort_type="text", page=1, page_size=50, export=""):
    if export not in ("", "json", "jsonl", "markdown", "csv", "html", "bib"):
        raise BrowserError("Unknown DataFrame export format")
    path = files.resolve(relative)
    if not path.is_file() or path.suffix.casefold() not in DATAFRAME_EXTENSIONS:
        raise BrowserError("Data file not found", 404)
    if path.stat().st_size > MAX_CSV_BYTES:
        raise BrowserError("Data file exceeds 2 MB size limit", 413)
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
    try:
        frame = _cached_frame(path, pd, full=bool(export))
    except (UnicodeError, ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise BrowserError("Invalid data table: " + str(exc), 415) from exc
    truncated = len(frame) > MAX_CSV_ROWS
    if not export:
        frame = frame.head(MAX_CSV_ROWS)
    source_count = len(frame)
    columns = [str(col) for col in frame.columns]
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
    if export:
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
        record = dict(zip(columns, values[1:])) if is_bib else None
        rows.append('<tr><th>' + e(values[0] + 1) + '</th>' +
                    ''.join('<td>' + (_bibliography_cell(c, v, record) if is_bib else _linked_cell(v)) + '</td>' for c, v in zip(columns, values[1:])) + '</tr>')
    back = '/view?' + urlencode({"path": relative} if is_json or is_bib else {"path": relative, "format": "html"})
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
            ("csv", "CSV"), ("html", "HTML")) + ((("bib", "BibTeX"),) if is_bib else ())) + '</p>'
    return ('<h2>' + e(path.name) + ' — pandas DataFrame</h2>'
            '<p><a href="' + e(directory) + '">Return to source directory</a> · '
            '<a href="' + e(back) + '">Standard source view</a>'
            ' · Read-only, original string identifiers preserved</p>'
            + form + exports + '<p>' + e(summary) + '</p>' + nav
            + '<div style="overflow-x:auto"><table border="1" cellspacing="0" cellpadding="4">'
            + ''.join(rows) + '</table></div>' + nav)
