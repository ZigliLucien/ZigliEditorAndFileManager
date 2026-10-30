"""Paged directory data for the GoFM/Xlster-style browser listing.

Only one file page is serialized per request. File and directory metadata are
scanned server-side, while per-file Notes previews are loaded for the chosen
page (except when sorting by Notes). The original full /api/files endpoint is
retained for older clients.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .file_manager import BrowserError
from .listing_view import MAX_LIST_ENTRIES
from ..storage.word_notes import WordNotes

PAGE_SIZE = 25
SORT_KEYS = frozenset({"filename", "filetype", "timekey", "size", "notes"})


def _display_name(name):
    return name.casefold()


def _preview(notes):
    content = " · ".join(
        record["data"].replace("\r", " ").replace("\n", " ").strip()
        for record in notes if record["data"].strip()
    )
    return (content[:155] + "…" if len(content) > 155 else content) or "—"


def paged_listing(files, relative=".", *, page=1, sort="filename", filter_text="",
                  notes_path=None):
    """Return directory structure and one selected file page as UTF-8 JSON data.

    Full-directory server scanning is needed for exact sorting and page counts,
    but the response and Notes enrichment are bounded to one page.
    """
    if sort not in SORT_KEYS:
        raise BrowserError("Unknown sort key")
    if type(page) is not int or page < 1 or page > 1000000:
        raise BrowserError("Invalid page number")
    if not isinstance(filter_text, str) or len(filter_text) > 200:
        raise BrowserError("Invalid filename filter")
    directory, entries = files.list_directory(relative)
    if len(entries) > MAX_LIST_ENTRIES:
        raise BrowserError("Directory has too many entries for listing", 413)

    folders, documents = [], []
    for entry in entries:
        if entry.name.startswith("."):
            continue
        try:
            # Exclude all symlinks from the styled paging view, avoiding
            # unnecessary disclosure and filesystem changes between checks.
            if entry.is_symlink():
                continue
            if entry.is_dir():
                folders.append({"name": entry.name, "path": files.relative(entry),
                                "kind": "directory"})
            elif entry.is_file():
                info = entry.stat()
                documents.append({
                    "name": entry.name, "path": files.relative(entry),
                    "modified": info.st_mtime, "size": info.st_size,
                    "type": entry.suffix[1:].lower() or "none"
                })
        except (FileNotFoundError, PermissionError):
            continue

    folders.sort(key=lambda r: (_display_name(r["name"]), r["name"]))
    filtered = [row for row in documents
                if filter_text.casefold() in row["name"].casefold()]
    notes_by_file = None

    if sort == "notes":
        # Notes.sort requires information on all matches, but the JSON body
        # still contains only the requested page.
        store = WordNotes(notes_path)
        notes_by_file = {}
        for note in store._notes.values():
            notes_by_file.setdefault(note["filename"], []).append(note)
        filtered.sort(key=lambda row: (
            _preview(notes_by_file.get(str(directory / row["name"]), [])).casefold(),
            _display_name(row["name"]), row["name"]))
    elif sort == "filetype":
        filtered.sort(key=lambda row: (
            _display_name(row["type"]), _display_name(row["name"]), row["name"]))
    elif sort == "size":
        filtered.sort(key=lambda row: (
            -row["size"], _display_name(row["name"]), row["name"]))
    elif sort == "timekey":
        filtered.sort(key=lambda row: (
            -row["modified"], _display_name(row["name"]), row["name"]))
    else:
        filtered.sort(key=lambda row: (_display_name(row["name"]), row["name"]))

    spans = []
    if sort == "filetype":
        # Xlster's filetype mode divides the list on extension changes.
        for index, row in enumerate(filtered):
            if not spans or filtered[spans[-1][0]]["type"] != row["type"]:
                spans.append([index, index + 1])
            else:
                spans[-1][1] = index + 1
    else:
        spans = [[offset, min(offset + PAGE_SIZE, len(filtered))]
                 for offset in range(0, len(filtered), PAGE_SIZE)]
    if not spans:
        spans = [[0, 0]]

    requested = min(page, len(spans))
    start, stop = spans[requested - 1]
    selected = filtered[start:stop]

    if notes_by_file is None:
        store = WordNotes(notes_path)
        notes_by_file = {}
        wanted = {str(directory / row["name"]) for row in selected}
        # Iterate once instead of calling for_file() for every document.
        for note in store._notes.values():
            if note["filename"] in wanted:
                notes_by_file.setdefault(note["filename"], []).append(note)
    for row in selected:
        stamp = datetime.fromtimestamp(row["modified"])
        attached = notes_by_file.get(str(directory / row["name"]), [])
        row["date"] = stamp.strftime("%b %d, %Y")
        row["time"] = stamp.strftime("%H:%M")
        row["note"] = _preview(attached)
        row["note_count"] = len(attached)

    refs = []
    for i, (first, last) in enumerate(spans):
        if sort == "filetype":
            descriptor = filtered[first]["type"] if last > first else "none"
        elif sort == "filename":
            descriptor = filtered[first]["name"][:4] if last > first else "1"
        else:
            descriptor = str(i + 1)
        refs.append({"page": i + 1, "label": descriptor,
                     "start": first + 1, "end": last})

    relative_path = files.relative(directory)
    crumbs = [{"name": "/", "path": "."}]
    if relative_path != ".":
        parts = Path(relative_path).parts
        for i, segment in enumerate(parts):
            crumbs.append({"name": segment, "path": str(Path(*parts[:i + 1]))})
    return {
        "directory": str(directory),
        "relative": relative_path,
        "parent": files.relative(directory.parent) if directory != files.root else None,
        "breadcrumbs": crumbs,
        "folders": folders,
        "files": selected,
        "count": len(folders) + len(documents),
        "total_files": len(filtered),
        "page": requested,
        "page_size": PAGE_SIZE,
        "page_count": len(spans),
        "page_start": start + 1 if selected else 0,
        "page_end": stop,
        "references": refs,
        "sort": sort,
        "filter": filter_text,
    }
