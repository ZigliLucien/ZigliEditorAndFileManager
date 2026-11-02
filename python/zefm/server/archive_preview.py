"""Bounded, read-only ZIP/JAR and TAR archive listing. Never extract entries."""
from html import escape
import tarfile
from zipfile import ZipFile, BadZipFile
from .file_manager import BrowserError

MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_MEMBERS = 5000
DISPLAY_MEMBERS = 500


def archive_listing(files, relative):
    path = files.resolve(relative)
    if not path.is_file():
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
                entries = [(m.filename, m.file_size, m.is_dir()) for m in members]
        elif name.endswith((".tar", ".tgz", ".tar.gz", ".tbz", ".tbz2",
                             ".tar.bz2", ".txz", ".tar.xz")):
            with tarfile.open(path, "r:*") as archive:
                entries = []
                for member in archive:
                    if len(entries) >= MAX_MEMBERS:
                        raise BrowserError("Archive has too many members", 413)
                    entries.append((member.name, member.size, member.isdir()))
        else:
            raise BrowserError("Unsupported archive", 415)
    except (BadZipFile, tarfile.TarError, OSError, EOFError) as exc:
        raise BrowserError("Invalid or unreadable archive", 415) from exc
    rows = []
    for name, size, directory in entries[:DISPLAY_MEMBERS]:
        suffix = "/" if directory and not name.endswith("/") else ""
        rows.append("<tr><td style='text-align:left'>" + escape(name + suffix) +
                    "</td><td style='text-align:right'>" + str(size) + "</td></tr>")
    note = (f"<p>Showing first {DISPLAY_MEMBERS} of {len(entries)} entries.</p>"
            if len(entries) > DISPLAY_MEMBERS else
            f"<p>{len(entries)} entries.</p>")
    return ("<h2>Archive: " + escape(path.name) + "</h2>" +
            "<p>Read-only listing; no files are extracted or executed.</p>" +
            note + "<table><tr><th>Member</th><th>Bytes</th></tr>" +
            "".join(rows) + "</table>")
