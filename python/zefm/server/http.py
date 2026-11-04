"""Loopback-only ZEFM browser/file manager.

Run: python3 -m zefm.server.http --root ~/Documents
The HTTP form is a local quick editor, not a network/FTP service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import secrets
import threading
from pathlib import Path
from socket import gethostname
from urllib.parse import parse_qs, quote, urlencode, urlsplit

from .file_manager import BrowserError, LocalFiles, MAX_EDIT_BYTES, MAX_COPY_BYTES
from .routes import permitted
from ..storage.word_notes import WordNotes
from .rtl_keymap import RTL_KEYMAP_JS, yiddish_keymap_json
from .listing_view import listing_data, listing_shell
from .listing_paging import paged_listing
from .pdf_delivery import select_pdf, byte_range
from .rename_ops import RenameManager
from .navigation import safe_listing_return
from .html_preview import site_url, site_resource, site_relative_path, HTML_PREVIEW_CSP, STATIC_SITE_EXTENSIONS
from .file_types import handler_for
from .book_preview import epub_page, djvu_page
from .archive_preview import archive_listing
from .postscript_preview import postscript_pdf
from .image_preview import image_preview
from .text_preview import preview_text
from .delimited_preview import csv_preview
from .structured_preview import transformed_document
from .document_build import markdown_html, checked_source, build_pdf
from .mathjax_filter import MATHJAX_PREVIEW_CSP


_STYLE = """<style>body{max-width:1000px;margin:2rem auto;padding:0 1rem;font:16px system-ui,sans-serif}
a{color:#155d91}table{border-collapse:collapse;width:100%}td{padding:.3rem .7rem;border-bottom:1px solid #ddd}
textarea{width:100%;box-sizing:border-box;font:14px/1.4 monospace;min-height:65vh}pre{white-space:pre-wrap;overflow-wrap:anywhere}
.actions a{margin-right:1rem}button{padding:.4rem 1rem}small{color:#555}</style>"""


def link(path: str, relative: str = ".") -> str:
    return path + "?" + urlencode({"path": relative})


def page(title: str, body: str) -> bytes:
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>"
            + escape(title) + " — ZEFM</title>" + _STYLE
            + '<link rel="stylesheet" href="/math.css"></head><body class="zefm-local-page">'
            + body + "<hr><small>ZEFM local browser · UTF-8 · loopback only</small></body></html>").encode("utf-8")


def note_version(record) -> str:
    """Form revision token for one word-attached note, including absence."""
    payload=json.dumps(record,ensure_ascii=False,sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def make_handler(files: LocalFiles, token: str, bound_port, notes_path=None, open_in_editor=None, file_in_use=None):
    note_lock=threading.RLock()
    rename_manager = RenameManager(files, notes_path, file_in_use)
    class BrowserHandler(BaseHTTPRequestHandler):
        server_version = "ZEFM-local/1"

        def log_message(self, format, *args):
            pass  # No accidental logging of private filenames into stdout.

        def _send(self, status: int, data: bytes, content_type: str = "text/html; charset=utf-8",
                  extra: dict[str, str] | None = None, allow_local_script: bool = False):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            csp = "default-src 'none'; style-src 'self' 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
            if allow_local_script:
                csp += "; script-src 'self'; connect-src 'self'"
            if extra and "Content-Security-Policy" in extra:
                csp = extra["Content-Security-Policy"]
            self.send_header("Content-Security-Policy", csp)
            for key, value in (extra or {}).items():
                if key.lower() != "content-security-policy":
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(data)

        def _serve_pdf(self, relative):
            """Stream a native-browser PDF response, including single byte ranges."""
            p = select_pdf(files, relative)
            with p.open("rb") as stream:
                if stream.read(5) != b"%PDF-":
                    raise BrowserError("File does not have a PDF signature", 415)
                stream.seek(0, 2)
                size = stream.tell()
                from .pdf_delivery import MAX_PDF_BYTES
                if size > MAX_PDF_BYTES:
                    raise BrowserError("PDF exceeds browser preview limit", 413)
                header = self.headers.get("Range")
                try:
                    start, end, partial = byte_range(header, size)
                except BrowserError as exc:
                    self.send_response(exc.status)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.end_headers()
                    return
                amount = end - start + 1 if size else 0
                self.send_response(206 if partial else 200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", "inline")
                self.send_header("Content-Length", str(amount))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Referrer-Policy", "no-referrer")
                if partial:
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.end_headers()
                stream.seek(start)
                remaining = amount
                while remaining:
                    chunk = stream.read(min(65536, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)

        def _host_ok(self):
            host = self.headers.get("Host", "")
            return host in {f"127.0.0.1:{bound_port()}", f"localhost:{bound_port()}"}

        def _params(self, body: str) -> dict[str, str]:
            try:
                args = parse_qs(body, encoding="utf-8", errors="strict", max_num_fields=8,
                                strict_parsing=bool(body), keep_blank_values=True)
            except (UnicodeError, ValueError) as exc:
                raise BrowserError("Invalid request parameters") from exc
            if any(len(values) != 1 for values in args.values()):
                raise BrowserError("Duplicate parameters")
            return {key: values[0] for key, values in args.items()}

        def _render_listing(self, relative):
            directory, entries = files.list_directory(relative)
            crumb = files.relative(directory)
            header = (f"<h1>Files: {escape(str(directory))}</h1>"
                      f'<p><a href="{escape(link("/listing", files.relative(directory)), quote=True)}">'
                      'Original ZEFM-style listing</a></p>')
            if directory != files.root:
                parent = files.relative(directory.parent)
                header += f'<p><a href="{escape(link("/browse", parent), quote=True)}">↑ Parent</a></p>'
            folder_form = (
                '<form action="/mkdir" method="post" accept-charset="utf-8">'
                f'<input type="hidden" name="csrf" value="{escape(token, quote=True)}">'
                f'<input type="hidden" name="path" value="{escape(crumb, quote=True)}">'
                '<label>New folder: <input name="name" required maxlength="255"'
                ' aria-label="New folder name"></label> '
                '<button type="submit">Create folder</button></form>'
            )
            rows = []
            for entry in entries:
                rel = files.relative(entry)
                is_dir = entry.is_dir()
                action = "browse" if is_dir else ("pdf" if entry.suffix.casefold() == ".pdf" else "view")
                label = entry.name + ("/" if is_dir else "")
                url = escape(link("/" + action, rel), quote=True)
                links = f'<a href="{url}">{escape(label)}</a>'
                if not is_dir:
                    if entry.suffix.casefold() == ".pdf":
                        links += f' &nbsp; <a href="{escape(link("/pdf", rel), quote=True)}">Open PDF</a>'
                    else:
                        links += (f' &nbsp; <a href="{escape(link("/edit", rel), quote=True)}">Quick edit</a>'
                              f' &nbsp; <a href="{escape(link("/edit", rel) + "&dir=rtl", quote=True)}">RTL edit</a>'
                              f' &nbsp; <a href="{escape(link("/raw", rel), quote=True)}">Download</a>'
                              f' &nbsp; <a href="{escape(link("/copy", rel), quote=True)}">Copy...</a>'
                              f' &nbsp; <a href="{escape(link("/rename", rel), quote=True)}">Rename...</a>'
                              f' &nbsp; <a href="{escape(link("/notes", rel), quote=True)}">Notes</a>')
                    if entry.suffix.casefold() == ".pdf":
                        links += (f' &nbsp; <a href="{escape(link("/raw", rel), quote=True)}">Download</a>'
                                  f' &nbsp; <a href="{escape(link("/notes", rel), quote=True)}">Notes</a>')
                if not is_dir:
                    links += f' &nbsp; <a href="{escape(link("/move", rel), quote=True)}">Move...</a>'
                if not is_dir and open_in_editor is not None:
                    links += (' &nbsp; <form action="/open-editor" method="post" style="display:inline">'
                              f'<input type="hidden" name="csrf" value="{escape(token,quote=True)}">'
                              f'<input type="hidden" name="path" value="{escape(rel,quote=True)}">'
                              '<button type="submit">Open in ZEFM</button></form>')
                rows.append(f"<tr><td>{links}</td></tr>")
            return page("File manager", header + folder_form + "<table>" + "".join(rows) + "</table>"
                        + f"<p><small>{len(entries)} entries. Local files only; browser editing limited to 1 MiB UTF-8 files.</small></p>")

        def do_GET(self):
            try:
                if not self._host_ok():
                    raise BrowserError("Invalid Host header", 403)
                parsed = urlsplit(self.path)
                if not permitted("GET", parsed.path):
                    raise BrowserError("Unknown route", 404)
                args = self._params(parsed.query)
                rel = args.get("path", ".")
                back_state = args.get("back")
                if back_state:
                    safe_listing_return(files, back_state)
                if parsed.path.startswith("/site/"):
                    if args:
                        raise BrowserError("Unexpected site resource parameters")
                    site_relative = site_relative_path(parsed.path)
                    site_file = files.resolve(site_relative)
                    if (files.root / site_relative).is_symlink():
                        raise BrowserError("Linked symbolic links are not browsable", 403)
                    if site_file.is_dir():
                        # HTML hyperlinks can point to a directory, not just
                        # a file. The normal listing route owns directories.
                        self._send(302, b"", extra={
                            "Location": link("/listing", site_relative)})
                        return
                    if not site_file.is_file():
                        raise BrowserError("Linked file or directory not found", 404)
                    extension = site_file.suffix.casefold()
                    if extension == ".pdf":
                        # Linked PDFs retain native browser range requests.
                        self._serve_pdf(site_relative)
                        return
                    if extension not in STATIC_SITE_EXTENSIONS:
                        # Every other file link uses the same dispatch as the
                        # main ZEFM listing: text, archives, books, conversion,
                        # or download. Never serve executable browser scripts.
                        self._send(302, b"", extra={
                            "Location": link("/view", site_relative)})
                        return
                    data, media_type, html_document = site_resource(files, parsed.path)
                    self._send(200, data, media_type,
                               {"Content-Security-Policy": HTML_PREVIEW_CSP}
                               if html_document else None)
                elif parsed.path in ("/", "/browse"):
                    self._send(200, self._render_listing(rel))
                elif parsed.path == "/listing":
                    if set(args) - {"path", "page", "sort", "filter"}:
                        raise BrowserError("Unexpected listing parameters")
                    if "page" in args and (not args["page"].isdigit()
                                           or not (1 <= len(args["page"]) <= 9)
                                           or int(args["page"]) < 1):
                        raise BrowserError("Invalid listing page")
                    if args.get("sort", "timekey") not in {
                            "filename", "filetype", "timekey", "size", "notes"}:
                        raise BrowserError("Invalid listing sort")
                    if len(args.get("filter", "")) > 200:
                        raise BrowserError("Filename filter is too long")
                    # Validate the directory before showing a JavaScript shell.
                    files.list_directory(rel)
                    self._send(200, listing_shell(gethostname(), token, open_in_editor is not None),
                               allow_local_script=True)
                elif parsed.path == "/api/listing-page":
                    if set(args) - {"path", "page", "sort", "filter"}:
                        raise BrowserError("Unexpected paging parameters")
                    raw_page = args.get("page", "1")
                    if not raw_page.isdecimal() or len(raw_page) > 7:
                        raise BrowserError("Invalid page number")
                    data = paged_listing(files, rel, page=int(raw_page),
                                         sort=args.get("sort", "timekey"),
                                         filter_text=args.get("filter", ""),
                                         notes_path=notes_path)
                    self._send(200, json.dumps(data, ensure_ascii=False).encode("utf-8"),
                               "application/json; charset=utf-8")
                elif parsed.path == "/api/files":
                    if set(args) - {"path"}:
                        raise BrowserError("Unexpected listing parameters")
                    data = listing_data(files, rel, notes_path)
                    self._send(200, json.dumps(data, ensure_ascii=False).encode("utf-8"),
                               "application/json; charset=utf-8")
                elif parsed.path in ("/listing.css", "/listing.js", "/build.js", "/math.css", "/mathjax-config.js"):
                    if args:
                        raise BrowserError("Unexpected asset parameters")
                    name = parsed.path[1:]
                    data = (Path(__file__).resolve().parent / name).read_bytes()
                    self._send(200, data, ("text/css" if name.endswith(".css")
                                           else "text/javascript") + "; charset=utf-8")
                elif parsed.path == "/rtl-keymap.js":
                    if args:
                        raise BrowserError("Unexpected script parameters")
                    self._send(200, RTL_KEYMAP_JS.encode("utf-8"),
                               "text/javascript; charset=utf-8")
                elif parsed.path == "/build":
                    if set(args) - {"path", "back"}:
                        raise BrowserError("Unexpected build parameters")
                    source, descriptor = checked_source(files, rel, for_build=True)
                    target = escape(safe_listing_return(files, back_state,
                                        files.relative(source.parent)), quote=True)
                    engine = escape(descriptor["build"])
                    content = (
                        f'<p><a href="{target}">← Return to listing</a></p>'
                        f'<h2>Build PDF: {escape(source.name)}</h2>'
                        f'<p>Engine: {engine}. Build may take several seconds. '
                        'The browser opens the new PDF only after a successful build.</p>'
                        '<p><small>Only compile trusted documents. TeX can access '
                        'local files even when shell escape is disabled.</small></p>'
                        '<form action="/build" method="post" id="zefm-build-form">'
                        f'<input type="hidden" name="csrf" value="{escape(token,quote=True)}">'
                        f'<input type="hidden" name="path" value="{escape(rel,quote=True)}">'
                        f'<button type="submit" id="zefm-build-button">Compile and view PDF</button>'
                        '</form>'
                        '<p id="zefm-build-status" role="status"></p>'
                        '<pre id="zefm-build-log" style="white-space:pre-wrap"></pre>'
                        '<script src="/build.js" defer></script>'
                    )
                    self._send(200, page("Build PDF", content), allow_local_script=True)
                elif parsed.path == "/rename":
                    if set(args) - {"path", "back"}:
                        raise BrowserError("Unexpected rename parameters")
                    source = files.resolve(rel)
                    if not source.is_file() or (files.root / rel).is_symlink():
                        raise BrowserError("File not found for rename", 404)
                    back = escape(safe_listing_return(files, back_state, files.relative(source.parent)), quote=True)
                    content = (
                        f'<p><a href="{back}">← Back</a></p>'
                        f'<h2>Rename: {escape(rel)}</h2>'
                        '<p>Existing files are never overwritten. Notes follow the renamed file.'
                        ' Close any open desktop editor buffer before renaming.</p>'
                        '<form method="post" action="/rename" accept-charset="utf-8">'
                        f'<input type="hidden" name="csrf" value="{escape(token,quote=True)}">'
                        f'<input type="hidden" name="path" value="{escape(rel,quote=True)}">'
                        f'<input type="hidden" name="back" value="{escape(back_state or "",quote=True)}">'
                        f'<label>New filename: <input name="name" required maxlength="255"'
                        f' value="{escape(source.name,quote=True)}"></label> '
                        '<button type="submit">Rename file</button></form>'
                    )
                    self._send(200, page("Rename file", content))
                elif parsed.path == "/move":
                    if set(args) - {"path", "back"}:
                        raise BrowserError("Unexpected move parameters")
                    source = files.resolve(rel)
                    if not source.is_file() or (files.root / rel).is_symlink():
                        raise BrowserError("File not found for moving", 404)
                    back = escape(safe_listing_return(files, back_state, files.relative(source.parent)), quote=True)
                    content = (
                        f'<p><a href="{back}">← Back</a></p>'
                        f'<h2>Move file: {escape(rel)}</h2>'
                        '<p>Move to another existing directory inside this ZEFM root. '
                        'No file will be overwritten; Notes move with the file. '
                        'Close any open desktop editor buffer first.</p>'
                        '<form method="post" action="/move" accept-charset="utf-8">'
                        f'<input type="hidden" name="csrf" value="{escape(token,quote=True)}">'
                        f'<input type="hidden" name="path" value="{escape(rel,quote=True)}">'
                        f'<input type="hidden" name="back" value="{escape(back_state or "",quote=True)}">'
                        '<label>Destination directory (relative to browsing root): '
                        '<input name="destination" required value="."></label> '
                        '<button type="submit">Move file</button></form>'
                    )
                    self._send(200, page("Move file", content))
                elif parsed.path == "/copy":
                    if set(args) - {"path", "back"}:
                        raise BrowserError("Unexpected copy parameters")
                    source = files.resolve(rel)
                    if not source.is_file():
                        raise BrowserError("Source file not found", 404)
                    if source.stat().st_size > MAX_COPY_BYTES:
                        raise BrowserError("File too large to copy in browser", 413)
                    back = escape(safe_listing_return(files, back_state, files.relative(source.parent)), quote=True)
                    default_name = "Copy of " + source.name
                    content = (
                        f'<p><a href="{back}">← Back to directory</a></p>'
                        f'<h2>Copy file: {escape(rel)}</h2>'
                        '<p>Make a copy in the same directory. Existing files are never replaced.</p>'
                        '<form method="post" action="/copy" accept-charset="utf-8">'
                        f'<input type="hidden" name="csrf" value="{escape(token, quote=True)}">'
                        f'<input type="hidden" name="path" value="{escape(rel, quote=True)}">'
                        f'<input type="hidden" name="back" value="{escape(back_state or "",quote=True)}">'
                        f'<label>New filename: <input name="name" maxlength="255" required'
                        f' value="{escape(default_name, quote=True)}"></label> '
                        '<button type="submit">Create copy</button></form>'
                    )
                    self._send(200, page("Copy file", content))
                elif parsed.path == "/pdf":
                    if set(args) - {"path", "back"}:
                        raise BrowserError("Unexpected PDF parameters")
                    self._serve_pdf(rel)
                elif parsed.path == "/djvu-page":
                    if set(args) - {"path", "page"}:
                        raise BrowserError("Unexpected DjVu parameters")
                    raw_page = args.get("page", "1")
                    if not raw_page.isdecimal() or len(raw_page) > 5:
                        raise BrowserError("Invalid DjVu page")
                    self._send(200, djvu_page(files, rel, int(raw_page)), "image/png")
                elif parsed.path == "/view":
                    if set(args) - {"path", "back", "chapter", "page", "format"}:
                        raise BrowserError("Unexpected view parameters")
                    descriptor = handler_for(rel)
                    kind = descriptor["view"]
                    if kind == "delimited":
                        self._send(200, page(rel, csv_preview(files, rel, args.get("format", "html"))))
                        return
                    if kind == "structured":
                        content = transformed_document(files, rel)
                        if descriptor["extension"] == ".ipynb":
                            self._send(200, content.encode("utf-8"),
                                       extra={"Content-Security-Policy":
                                              "default-src 'none'; style-src 'unsafe-inline'; "
                                              "img-src data:; font-src data:; "
                                              "base-uri 'none'; frame-ancestors 'none'"})
                        else:
                            self._send(200, page(rel, content))
                        return
                    if kind == "postscript":
                        self._send(200, postscript_pdf(files, rel), "application/pdf",
                                   {"Content-Disposition": "inline"})
                        return
                    if kind == "archive":
                        self._send(200, page(rel, archive_listing(files, rel)))
                        return
                    if kind == "image":
                        data = image_preview(files, rel, descriptor["extension"])
                        self._send(200, data, descriptor["mime"])
                        return
                    if kind in ("download", "auto"):
                        if kind == "auto":
                            preview = preview_text(files, rel, automatic=True)
                            if preview is not None:
                                back = escape(safe_listing_return(
                                    files, back_state,
                                    files.relative(files.resolve(rel).parent)), quote=True)
                                self._send(200, page(rel,
                                    f'<p><a href="{back}">← Back</a></p>' + preview))
                                return
                        self._send(302, b"", extra={"Location": link("/raw", rel)})
                        return
                    if kind == "epub":
                        raw_chapter = args.get("chapter", "0")
                        if not raw_chapter.isdecimal() or len(raw_chapter) > 5:
                            raise BrowserError("Invalid EPUB chapter")
                        self._send(200, page(rel, epub_page(files, rel, int(raw_chapter))))
                        return
                    if kind == "djvu":
                        raw_page = args.get("page", "1")
                        if not raw_page.isdecimal() or len(raw_page) > 5 or int(raw_page) < 1:
                            raise BrowserError("Invalid DjVu page")
                        number = int(raw_page)
                        previous = (f'<a href="{escape(link("/view", rel) + "&page=" + str(number-1), quote=True)}">← Previous</a> '
                                    if number > 1 else "")
                        following = f' <a href="{escape(link("/view", rel) + "&page=" + str(number+1), quote=True)}">Next →</a>'
                        src = escape(link("/djvu-page", rel) + "&page=" + str(number), quote=True)
                        body = (f"<h2>{escape(rel)}</h2><nav>{previous}Page {number}{following}</nav>"
                                f'<p><img src="{src}" alt="DjVu page {number}" style="max-width:100%;height:auto"></p>')
                        self._send(200, page(rel, body), extra={
                            "Content-Security-Policy": "default-src 'none'; img-src 'self'; style-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'"})
                        return
                    suffix = files.resolve(rel).suffix.casefold()
                    if suffix == ".pdf":
                        self._serve_pdf(rel)
                        return
                    if handler_for(rel)["view"] == "markdown":
                        self._send(200, markdown_html(files, rel),
                                   extra={"Content-Security-Policy": MATHJAX_PREVIEW_CSP})
                        return
                    if suffix in (".html", ".htm", ".xhtml"):
                        # Redirect so relative CSS/images resolve beside the
                        # HTML document instead of under the /view endpoint.
                        self._send(302, b"", extra={"Location": site_url(rel)})
                        return
                    preview = preview_text(files, rel)
                    back = escape(safe_listing_return(
                        files, back_state,
                        files.relative(files.resolve(rel).parent)), quote=True)
                    quick_edit = (f' <a href="{escape(link("/edit", rel), quote=True)}">'
                                  'Quick edit</a>'
                                  if files.resolve(rel).stat().st_size <= MAX_EDIT_BYTES
                                  else "")
                    self._send(200, page(rel, f'<p><a href="{back}">← Back</a>'
                                              + quick_edit + '</p>' + preview))
                elif parsed.path == "/edit":
                    if set(args) - {"path", "dir", "back"}:
                        raise BrowserError("Unexpected edit parameters", 400)
                    direction = args.get("dir", "ltr")
                    if direction not in ("ltr", "rtl"):
                        raise BrowserError("Invalid text direction", 400)
                    text, digest = files.read_text(rel)
                    textarea_direction = (' dir="rtl" style="text-align:right" id="zefm-rtl-content"'
                                          f' data-zefm-keymap="{escape(yiddish_keymap_json(), quote=True)}"'
                                          if direction == "rtl" else '')
                    rtl_controls = (
                        '<p><label><input type="checkbox" id="zefm-yiddish-keymap" checked>'
                        ' Enable original Yiddish Alt keymap</label></p>'
                        '<p><small>Alt+B = ב; Alt+Shift+I = אי. '
                        'Characters advance leftward; text is stored in logical Unicode order. '
                        'Uncheck to use the system keyboard.</small></p>'
                        if direction == "rtl" else '')
                    rtl_script = ('<script src="/rtl-keymap.js" defer></script>'
                                  if direction == "rtl" else '')
                    content = (f'<p><a href="{escape(safe_listing_return(files, back_state, files.relative(files.resolve(rel).parent)), quote=True)}">← Back</a></p>'
                               f'<h2>Quick edit{" (RTL)" if direction == "rtl" else ""}: {escape(rel)}</h2>'
                               '<form action="/edit" method="post" accept-charset="utf-8">'
                               f'<input type="hidden" name="csrf" value="{escape(token, quote=True)}">'
                               f'<input type="hidden" name="path" value="{escape(rel, quote=True)}">'
                               f'<input type="hidden" name="back" value="{escape(back_state or "",quote=True)}">'
                               f'<input type="hidden" name="digest" value="{digest}">'
                               f'{rtl_controls}'
                               f'<textarea name="content"{textarea_direction}>{escape(text)}</textarea><p><button type="submit">Save</button></p></form>'
                               f'{rtl_script}')
                    self._send(200, page(rel, content), allow_local_script=(direction == "rtl"))
                elif parsed.path == "/notes":
                    if set(args) - {"path", "back"}:
                        raise BrowserError("Unexpected notes parameters")
                    p = files.resolve(rel)
                    if not p.is_file():
                        raise BrowserError("Not a file", 404)
                    with note_lock:
                        try:
                            notes = WordNotes(notes_path).for_file(str(p))
                        except (OSError, ValueError) as exc:
                            raise BrowserError(f"Cannot read local notes: {exc}", 500) from exc
                    results = "".join(
                        f'<section><h3>{escape(note["word"])}</h3>'
                        f'<p><a href="{escape(link("/note-edit", rel) + "&word=" + quote(note["word"], safe="") + ("&" + urlencode({"back":back_state}) if back_state else ""), quote=True)}">Edit note</a></p>'
                        f'<pre>{escape(note["data"])}</pre></section>' for note in notes)
                    if not results:
                        results = '<p>No word-attached Notes for this file.</p>'
                    back = escape(safe_listing_return(files, back_state, files.relative(p.parent)), quote=True)
                    create = escape(link("/note-edit", rel) + ("&" + urlencode({"back":back_state}) if back_state else ""), quote=True)
                    self._send(200, page(f"Notes: {rel}", f'<p><a href="{back}">← Back</a></p>'
                                         f'<h2>Notes: {escape(rel)}</h2>'
                                         f'<p><a href="{create}">Add Note</a></p>{results}'))
                elif parsed.path == "/note-edit":
                    if set(args) - {"path", "word", "back"}:
                        raise BrowserError("Unexpected note-edit parameters")
                    p = files.resolve(rel)
                    if not p.is_file():
                        raise BrowserError("Not a file", 404)
                    word=args.get("word", "")
                    if len(word)>500:
                        raise BrowserError("Note word is too long", 400)
                    with note_lock:
                        try:
                            record=WordNotes(notes_path).get(str(p),word) if word else None
                        except (OSError,ValueError) as exc:
                            raise BrowserError(f"Cannot read local notes: {exc}", 500) from exc
                    data=record["data"] if record else ""
                    revision=note_version(record)
                    back=escape(link("/notes",rel) + ("&" + urlencode({"back":back_state}) if back_state else ""),quote=True)
                    word_label=(f'<strong>Word: {escape(word)}</strong>' if word else
                                '<label>Word or phrase: <input name="word" required maxlength="500"></label>')
                    word_field=(f'<input type="hidden" name="word" value="{escape(word,quote=True)}">' if word else "")
                    body=(f'<p><a href="{back}">← Notes</a></p><h2>Note: {escape(rel)}</h2>'
                          '<form action="/note-edit" method="post" accept-charset="utf-8">'
                          f'<input type="hidden" name="csrf" value="{escape(token,quote=True)}">'
                          f'<input type="hidden" name="path" value="{escape(rel,quote=True)}">'
                          f'<input type="hidden" name="back" value="{escape(back_state or "",quote=True)}">'
                          f'<input type="hidden" name="digest" value="{revision}">'
                          f'{word_label}{word_field}'
                          '<p><button type="submit">Save Note</button></p>'
                          f'<textarea name="content" aria-label="Note text">{escape(data)}</textarea>'
                          '<p><button type="submit">Save Note</button></p></form>')
                    self._send(200,page(f"Edit Note: {rel}",body))
                elif parsed.path == "/raw":
                    if set(args) - {"path", "back"}:
                        raise BrowserError("Unexpected raw parameters")
                    p = files.resolve(rel)
                    if not p.is_file():
                        raise BrowserError("Not a file", 404)
                    if p.stat().st_size > 16 * MAX_EDIT_BYTES:
                        raise BrowserError("File too large to download through browser", 413)
                    data = p.read_bytes()
                    filename = quote(p.name)
                    self._send(200, data, "application/octet-stream",
                               {"Content-Disposition": "attachment; filename*=UTF-8''" + filename})
            except BrowserError as exc:
                self._send(exc.status, page("File manager error", f"<h2>{escape(str(exc))}</h2>"))
            except (OSError, ValueError) as exc:
                self._send(400, page("File manager error", f"<h2>{escape(str(exc))}</h2>"))

        def do_POST(self):
            try:
                if not self._host_ok():
                    raise BrowserError("Invalid Host header", 403)
                if not permitted("POST", urlsplit(self.path).path):
                    raise BrowserError("Unknown route", 404)
                if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/x-www-form-urlencoded":
                    raise BrowserError("Expected URL-encoded form", 415)
                try:
                    n = int(self.headers.get("Content-Length", ""))
                except ValueError as exc:
                    raise BrowserError("Missing or invalid Content-Length", 411) from exc
                if n <= 0 or n > 5 * MAX_EDIT_BYTES:
                    raise BrowserError("Form too large", 413)
                body = self.rfile.read(n).decode("utf-8", "strict")
                args = self._params(body)
                if not secrets.compare_digest(args.get("csrf", ""), token):
                    raise BrowserError("Invalid form token", 403)
                route = urlsplit(self.path).path
                return_to = args.get("back")
                if return_to:
                    safe_listing_return(files, return_to)
                if route=="/build":
                    if set(args) != {"csrf", "path"}:
                        raise BrowserError("Unexpected build parameters")
                    try:
                        result = build_pdf(files, args["path"])
                    except BrowserError as exc:
                        self._send(exc.status, json.dumps(
                            {"ok": False, "error": str(exc)}).encode("utf-8"),
                            "application/json; charset=utf-8")
                        return
                    self._send(200, json.dumps(result, ensure_ascii=False).encode("utf-8"),
                               "application/json; charset=utf-8")
                elif route=="/mkdir":
                    if set(args) - {"csrf", "path", "name", "back"} or not {"csrf", "path", "name"} <= set(args):
                        raise BrowserError("Unexpected create-directory parameters")
                    created = files.create_directory(args["path"], args["name"])
                    back = escape(safe_listing_return(files, return_to, files.relative(created.parent)), quote=True)
                    self._send(201, page("Folder created",
                        f'<h2>Created folder: {escape(created.name)}</h2>'
                        f'<p><a href="{back}">Back to directory</a></p>'))
                elif route=="/rename":
                    if set(args) - {"csrf", "path", "name", "back"} or not {"csrf", "path", "name"} <= set(args):
                        raise BrowserError("Unexpected rename parameters")
                    with note_lock:
                        renamed, count = rename_manager.rename(args["path"], args["name"])
                    directory = files.relative(renamed.parent)
                    back = escape(safe_listing_return(files, return_to, directory), quote=True)
                    self._send(200, page("File renamed",
                        f'<h2>Renamed to: {escape(renamed.name)}</h2>'
                        f'<p>{count} attached Notes retained under the new filename.</p>'
                        f'<p><a href="{back}">Back to original-style listing</a></p>'))
                elif route=="/move":
                    if (set(args) - {"csrf", "path", "destination", "back"}
                            or not {"csrf", "path", "destination"} <= set(args)):
                        raise BrowserError("Unexpected move parameters")
                    with note_lock:
                        moved, count = rename_manager.move(args["path"], args["destination"])
                    back = escape(safe_listing_return(
                        files, return_to, files.relative(moved.parent)), quote=True)
                    destination_link = escape(link("/listing", files.relative(moved.parent)), quote=True)
                    self._send(200, page("File moved",
                        f'<h2>Moved to: {escape(files.relative(moved))}</h2>'
                        f'<p>{count} attached Notes retained.</p>'
                        f'<p><a href="{back}">Return to previous listing</a> · '
                        f'<a href="{destination_link}">Open destination directory</a></p>'))
                elif route=="/copy":
                    if set(args) - {"csrf", "path", "name", "back"} or not {"csrf", "path", "name"} <= set(args):
                        raise BrowserError("Unexpected copy parameters")
                    copied = files.copy_file(args["path"], args["name"])
                    back = escape(safe_listing_return(files, return_to, files.relative(copied.parent)), quote=True)
                    self._send(201, page("File copied",
                        f'<h2>Copied to: {escape(copied.name)}</h2>'
                        f'<p><a href="{back}">Back to directory</a></p>'))
                elif route=="/open-editor":
                    if open_in_editor is None:
                        raise BrowserError("Desktop editor integration unavailable", 404)
                    if set(args) - {"csrf", "path", "back"} or not {"csrf", "path"} <= set(args):
                        raise BrowserError("Unexpected editor-open parameters")
                    p=files.resolve(args["path"])
                    if not p.is_file():
                        raise BrowserError("File not found",404)
                    # Never touch Tk widgets from a background HTTP thread.
                    open_in_editor(str(p))
                    self._send(200,page("Open in ZEFM",
                        f'<h2>Sent to ZEFM: {escape(args["path"])}</h2>'
                        '<p>Return to the editor window. An already open buffer is reused.</p>'
                        f'<p><a href="{escape(safe_listing_return(files, return_to, files.relative(p.parent)),quote=True)}">Back to files</a></p>'))
                elif route=="/note-edit":
                    for key in ("path", "word", "digest", "content"):
                        if key not in args:
                            raise BrowserError("Missing form parameter")
                    p=files.resolve(args["path"])
                    if not p.is_file():
                        raise BrowserError("Not a file", 404)
                    word=args["word"].strip()
                    if not word or len(word)>500:
                        raise BrowserError("Enter a word or phrase (at most 500 characters)", 400)
                    if len(args["content"].encode("utf-8"))>MAX_EDIT_BYTES:
                        raise BrowserError("Note exceeds size limit",413)
                    with note_lock:
                        try:
                            store=WordNotes(notes_path)
                            old=store.get(str(p),word)
                            if note_version(old)!=args["digest"]:
                                raise BrowserError("Note changed elsewhere; reopen before saving",409)
                            store.put(str(p),word,args["content"],
                                      link=old["link"] if old else escape(word,quote=True))
                        except (OSError,ValueError) as exc:
                            raise BrowserError(f"Could not save note: {exc}",500) from exc
                    self._send(200,page("Note Saved",f'<h2>Saved note: {escape(word)}</h2>'
                           f'<p><a href="{escape(link("/notes",args["path"]) + ("&" + urlencode({"back": return_to}) if return_to else ""),quote=True)}">Back to Notes</a></p>'))
                else:
                    for key in ("path", "digest", "content"):
                        if key not in args:
                            raise BrowserError("Missing form parameter")
                    files.save_text(args["path"], args["content"], args["digest"])
                    self._send(200, page("Saved", f"<h2>Saved: {escape(args['path'])}</h2>"
                               f'<p><a href="{escape(safe_listing_return(files, return_to, files.relative(files.resolve(args["path"]).parent)), quote=True)}">Back to directory</a></p>'
                               "<p>If this file is open in the desktop editor, reload it there before editing further.</p>"))
            except (BrowserError, UnicodeDecodeError) as exc:
                status = exc.status if isinstance(exc, BrowserError) else 400
                self._send(status, page("Save failed", f"<h2>{escape(str(exc))}</h2>"))
            except (OSError, ValueError) as exc:
                self._send(400, page("Save failed", f"<h2>{escape(str(exc))}</h2>"))
    return BrowserHandler


class BrowserServer:
    def __init__(self, root: str, port: int = 0, notes_path=None, open_in_editor=None, file_in_use=None):
        self.files = LocalFiles(root)
        self.token = secrets.token_urlsafe(32)
        server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(self.files, self.token,
                                                  lambda: server.server_address[1], notes_path, open_in_editor, file_in_use))
        server.daemon_threads = True
        self.server = server
        self.thread = None

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_address[1]}/"

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True, name="ZEFM local browser")
            self.thread.start()
        return self.url

    def close(self):
        if self.thread is not None:
            self.server.shutdown()
            self.thread.join(timeout=3)
            self.thread = None
        self.server.server_close()


def main():
    parser = argparse.ArgumentParser(description="ZEFM local browser/file manager")
    parser.add_argument("--root", default="~", help="directory to browse (defaults to home)")
    parser.add_argument("--port", type=int, default=0, help="loopback port (0 chooses an available port)")
    args = parser.parse_args()
    browser = BrowserServer(args.root, args.port)
    print(browser.start(), flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        browser.close()


if __name__ == "__main__":
    main()
