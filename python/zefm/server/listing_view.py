"""Original ZEFM listing layout, sourced from lister.xsl/Xlster.java.

The listing data is JSON; the browser builds the DOM with textContent.
No XML or XSLT is involved in the browser listing itself.
"""
from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

from .file_manager import BrowserError
from ..storage.word_notes import WordNotes

MAX_LIST_ENTRIES = 3000


def listing_data(files, relative=".", notes_path=None):
    """Return a confined, bounded listing model for the JavaScript frontend."""
    directory, entries = files.list_directory(relative)
    if len(entries) > MAX_LIST_ENTRIES:
        raise BrowserError("Directory has too many entries for this listing view", 413)

    store = WordNotes(notes_path)
    folders, documents = [], []
    for entry in entries:
        # Original XCommands.updateList and Xlster omitted dot-prefixed entries.
        if entry.name.startswith("."):
            continue
        try:
            target = entry.resolve()
            # An externally pointing symlink should not disclose metadata,
            # nor be displayed as an actionable link.
            if not target.is_relative_to(files.root):
                continue
            if not target.is_file() and not target.is_dir():
                continue
            stat = target.stat()
            is_dir = target.is_dir()
            rel = files.relative(entry)
            row = {"name": entry.name, "path": rel, "kind": "directory" if is_dir else "file",
                   "modified": stat.st_mtime, "type": entry.suffix[1:].lower() or "none"}
            if is_dir:
                folders.append(row)
                continue

            stamp = datetime.fromtimestamp(stat.st_mtime)
            attached = store.for_file(str(target))
            previews = [note["data"].replace("\r", " ").replace("\n", " ").strip()
                        for note in attached]
            preview = " · ".join(text for text in previews if text)
            row.update({"size": stat.st_size, "date": stamp.strftime("%b %d, %Y"),
                        "time": stamp.strftime("%H:%M"),
                        "note": (preview[:155] + "…" if len(preview) > 155 else preview) or "—",
                        "note_count": len(attached)})
            documents.append(row)
        except (FileNotFoundError, PermissionError):
            # An external writer may have removed this entry during a scan.
            continue

    relative_path = files.relative(directory)
    crumb = [{"name": "/", "path": "."}]
    if relative_path != ".":
        parts = Path(relative_path).parts
        for i, part in enumerate(parts):
            crumb.append({"name": part, "path": str(Path(*parts[:i+1]))})
    return {
        "directory": str(directory),
        "relative": relative_path,
        "parent": files.relative(directory.parent) if directory != files.root else None,
        "breadcrumbs": crumb,
        "folders": folders,
        "files": documents,
        "count": len(folders) + len(documents),
    }


def listing_shell(hostname: str, token: str, desktop_editor: bool) -> bytes:
    """Minimal semantic shell; layout and interaction live in local CSS/JS."""
    flag = "true" if desktop_editor else "false"
    title = escape(hostname)
    csrf = escape(token, quote=True)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>ZEFM · {title} · Listing</title>'
            '<link rel="stylesheet" href="/listing.css">'
            '<script src="/listing.js" defer></script></head>'
            f'<body data-editor="{flag}" data-csrf="{csrf}">'
            '<main id="zefm-app">'
            '<header class="top-line"><div id="top"><div id="breadcrumbs" aria-label="Current directory"></div>'
            '<div id="directory-title">ZEFM file listing</div></div>'
            f'<aside id="local"><a href="/" id="home-name">zefm@{title}</a>'
            '<ul class="utility-links">'
            '<li><button type="button" disabled title="New file is not ported">New File</button></li>'
            '<li><button type="button" disabled title="Text search is not ported">Search String</button></li>'
            '<li><button type="button" id="find-file">Find File</button></li>'
            '<li><button type="button" disabled title="Database search is not ported">Text Search</button></li>'
            '</ul></aside></header>'
            '<div class="top-panels"><aside id="options">'
            '<label for="sort-key">Sort by</label>'
            '<select id="sort-key"><option value="filename">Filename</option>'
            '<option value="filetype">File Type</option>'
            '<option value="timekey">Date / Time</option>'
            '<option value="size">Size</option>'
            '<option value="notes">Notes</option></select>'
            '<p><button type="button" id="refresh" class="update">Update</button></p>'
            '<div id="sort-summary" class="sort-summary"></div>'
            '<div id="time" aria-label="Local date and time"></div>'
            '<p class="filter-label"><label for="filter">Find filename</label>'
            '<input id="filter" type="search" placeholder="Filter filenames"></p>'
            '<a class="basic-link" href="/">Basic listing</a>'
            '</aside><section id="directories" aria-label="Subdirectories">'
            '<div class="directories-heading">Directories</div>'
            '<table id="directory-grid"><tbody></tbody></table>'
            '<form id="mkdir-form" action="/mkdir" method="post">'
            f'<input type="hidden" name="csrf" value="{csrf}">'
            '<input type="hidden" name="path" id="folder-parent">'
            '<label>New folder <input type="text" maxlength="255" name="name" required></label>'
            '<button type="submit">Create</button></form>'
            '</section></div>'
            '<section class="file-panel">'
            '<fieldset id="file-operations"><legend>File operations</legend>'
            '<label class="op v"><input type="radio" name="fileops" value="view" checked> view</label>'
            '<label class="op c"><input type="radio" name="fileops" value="copy"> copy</label>'
            '<label class="op m unavailable" title="Move is not yet ported"><input type="radio" name="fileops" value="move" disabled> move</label>'
            '<label class="op d unavailable" title="Delete is not yet ported"><input type="radio" name="fileops" value="delete" disabled> dele</label>'
            '<label class="op e"><input type="radio" name="fileops" value="edit"> edit</label>'
            '<label class="op q"><input type="radio" name="fileops" value="quick"> quik</label>'
            '<label class="op a"><input type="radio" name="fileops" value="notes"> note</label>'
            '</fieldset>'
            '<table id="file-list"><colgroup><col style="width:30%"><col style="width:30%">'
            '<col style="width:40%"></colgroup>'
            '<thead><tr><th>Filename</th><th>Size &nbsp; Date &nbsp; Time</th><th>Notes</th></tr></thead>'
            '<tbody></tbody></table>'
            '<nav id="pages" aria-label="File list pages"></nav>'
            '<p id="listing-info" role="status"></p></section>'
            '<footer>Original ZEFM listing layout · Python + JSON + JavaScript · localhost</footer>'
            '<form id="open-desktop-form" action="/open-editor" method="post" hidden>'
            f'<input type="hidden" name="csrf" value="{csrf}">'
            '<input type="hidden" name="path" id="open-desktop-path"></form>'
            '</main></body></html>').encode("utf-8")
