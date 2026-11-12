"""Bounded ZIP/JAR and TAR archive listing with optional guarded Extract links."""
from collections import Counter
from html import escape
import stat
import tarfile
from urllib.parse import urlencode
from zipfile import ZipFile, BadZipFile
from .file_manager import BrowserError
from .file_types import handler_for

MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_MEMBERS = 5000
DISPLAY_MEMBERS = 500


def archive_listing(files, relative, *, enable_extract=False, enable_preview=False):
    path = files.resolve(relative)
    if not path.is_file() or (files.root / relative).is_symlink():
        raise BrowserError("Archive not found", 404)
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise BrowserError("Archive exceeds listing size limit", 413)
    name = path.name.casefold()
    try:
        if name.endswith((".zip", ".jar", ".war", ".ear")):
            with ZipFile(path) as archive:
                members = archive.infolist()
                if len(members) > MAX_MEMBERS:
                    raise BrowserError("Archive has too many members", 413)
                entries = [(m.filename, m.file_size, m.is_dir(),
                            not m.is_dir() and
                            stat.S_IFMT(m.external_attr >> 16) in (0, stat.S_IFREG))
                           for m in members]
        elif name.endswith((".tar", ".tgz", ".tar.gz", ".tbz", ".tbz2",
                             ".tar.bz2", ".txz", ".tar.xz")):
            with tarfile.open(path, "r:*") as archive:
                entries = []
                for member in archive:
                    if len(entries) >= MAX_MEMBERS:
                        raise BrowserError("Archive has too many members", 413)
                    entries.append((member.name, member.size, member.isdir(),
                                    member.isfile()))
        else:
            raise BrowserError("Unsupported archive", 415)
    except (BadZipFile, tarfile.TarError, OSError, EOFError) as exc:
        raise BrowserError("Invalid or unreadable archive", 415) from exc

    # Import only when building optional links: the extraction module reuses
    # the member-count/size constants defined above.
    if enable_extract or enable_preview:
        from .archive_extract import MAX_EXTRACT_BYTES, MAX_PREVIEW_BYTES, _member_name
    counts = Counter(entry[0] for entry in entries)
    rows = []
    for entry_name, size, directory, regular in entries[:DISPLAY_MEMBERS]:
        suffix = "/" if directory and not entry_name.endswith("/") else ""
        action = ""
        if regular and counts[entry_name] == 1 and (enable_extract or enable_preview):
            try:
                filename = _member_name(entry_name)
            except BrowserError:
                pass
            else:
                if enable_preview and size <= MAX_PREVIEW_BYTES:
                    kind = handler_for(filename)["view"]
                    if kind in ("text", "markdown", "structured", "delimited",
                                "yiddish", "html"):
                        view_href = "/view-entry?" + urlencode(
                            {"path": relative, "member": entry_name})
                        action = '<a href="' + escape(view_href, quote=True) + '">View text</a>'
                if enable_extract and size <= MAX_EXTRACT_BYTES:
                    href = "/extract-entry?" + urlencode(
                        {"path": relative, "member": entry_name})
                    action += (' · ' if action else '') + (
                        '<a href="' + escape(href, quote=True) + '">Extract…</a>')
        cells = ("<tr><td style='text-align:left'>" + escape(entry_name + suffix) +
                 "</td><td style='text-align:right'>" + str(size) + "</td>")
        if enable_extract or enable_preview:
            cells += "<td>" + action + "</td>"
        rows.append(cells + "</tr>")

    note = (f"<p>Showing first {DISPLAY_MEMBERS} of {len(entries)} entries.</p>"
            if len(entries) > DISPLAY_MEMBERS else
            f"<p>{len(entries)} entries.</p>")
    if enable_preview:
        message = ("<p>View text reads small UTF-8 members without extracting; "
                   "Extract… requires confirmation and never overwrites.</p>")
    elif enable_extract:
        message = ("<p>Select Extract… for one regular file; extraction requires "
                   "confirmation and never overwrites an existing file.</p>")
    else:
        message = "<p>Read-only listing; no files are extracted or executed.</p>"
    columns = "<th>Member</th><th>Bytes</th>" + (
        "<th>Action</th>" if enable_extract or enable_preview else "")
    return ("<h2>Archive: " + escape(path.name) + "</h2>" +
            message + note + "<table><tr>" + columns + "</tr>" +
            "".join(rows) + "</table>")
