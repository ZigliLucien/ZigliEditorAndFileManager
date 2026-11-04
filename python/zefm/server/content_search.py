"""Bounded, read-only UTF-8 content search for the local file manager.

An adaptation of the legacy ServPakDir search workflow, not yet verified
against Search.java's precise matching semantics. Search does not execute
commands, follow symlinks, or read files outside LocalFiles.root.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .file_manager import BrowserError
from .file_types import handler_for

MAX_QUERY_CHARS = 200
MAX_DEPTH = 8
MAX_FILES = 500
MAX_FILE_BYTES = 1 * 1024 * 1024
MAX_TOTAL_BYTES = 12 * 1024 * 1024
MAX_RESULTS = 100
MAX_SNIPPET = 220

# Source, structured documents, Yiddish and other unrecognized extensions
# may be UTF-8 text. Known binary formats are never scanned as text.
_SKIP_TYPES = {"download", "image", "archive", "pdf", "postscript",
               "epub", "djvu"}


@dataclass(frozen=True)
class SearchHit:
    path: str
    line: int
    excerpt: str


@dataclass(frozen=True)
class SearchResults:
    hits: tuple[SearchHit, ...]
    files_scanned: int
    bytes_scanned: int
    truncated: bool


def search_text(files, directory: str, query: str, *,
                case_sensitive: bool = False) -> SearchResults:
    if not isinstance(query, str) or not query or not query.strip():
        raise BrowserError("Enter a nonempty search string")
    if len(query) > MAX_QUERY_CHARS or any(ord(c) < 32 for c in query):
        raise BrowserError("Search string is too long or contains control characters")
    starting, _ = files.list_directory(directory)
    needle = query if case_sensitive else query.casefold()
    hits = []
    scanned = 0
    total_bytes = 0
    truncated = False
    # LIFO traversal is sorted deterministically for stable search output.
    stack = [(starting, 0)]
    while stack:
        folder, depth = stack.pop()
        try:
            entries = sorted(folder.iterdir(), key=lambda x: x.name.casefold())
        except OSError:
            continue
        subdirs = []
        for path in entries:
            if path.name.startswith(".") or path.is_symlink():
                continue
            try:
                if path.is_dir():
                    if depth < MAX_DEPTH:
                        subdirs.append((path, depth + 1))
                    else:
                        truncated = True
                    continue
                if not path.is_file() or handler_for(path.name)["view"] in _SKIP_TYPES:
                    continue
                size = path.stat().st_size
                if size > MAX_FILE_BYTES:
                    continue
                if scanned >= MAX_FILES or total_bytes + size > MAX_TOTAL_BYTES:
                    truncated = True
                    break
                data = path.read_bytes()
            except OSError:
                continue
            scanned += 1
            total_bytes += len(data)
            if b"\x00" in data:
                continue
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                continue
            for line_number, line in enumerate(text.splitlines(), 1):
                if needle not in (line if case_sensitive else line.casefold()):
                    continue
                clean = line.replace("\t", " ").strip()
                if len(clean) > MAX_SNIPPET:
                    index = (clean if case_sensitive else clean.casefold()).find(needle)
                    start = min(max(0, index - 60), len(clean) - MAX_SNIPPET)
                    clean = ("…" if start else "") + clean[start:start + MAX_SNIPPET]
                    if start + MAX_SNIPPET < len(line):
                        clean += "…"
                hits.append(SearchHit(files.relative(path), line_number, clean))
                if len(hits) >= MAX_RESULTS:
                    truncated = True
                    return SearchResults(tuple(hits), scanned, total_bytes, truncated)
        if truncated:
            break
        stack.extend(reversed(subdirs))
    return SearchResults(tuple(hits), scanned, total_bytes, truncated)
