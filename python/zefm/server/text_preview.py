"""Safe, bounded UTF-8 document preview independent of the quick-edit limit.

An unrecognized filename extension is not evidence of binary content.
We sniff the actual bytes and display readable text as escaped HTML.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

from .file_manager import BrowserError

MAX_TEXT_VIEW_BYTES = 4 * 1024 * 1024


def readable_utf8(data: bytes) -> str | None:
    """Return decoded text only when the bytes resemble a text document."""
    if b"\x00" in data:
        return None
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None
    # Accept tabs, CR, LF, form feeds; reject other C0/C1 controls.
    if any((ord(char) < 32 and char not in "\t\n\r\f")
           or 127 <= ord(char) <= 159 for char in text):
        return None
    return text


def preview_text(files, relative: str, *, automatic: bool = False) -> str | None:
    """Return escaped browser HTML or None for unknown/likely binary content."""
    path = files.resolve(relative)
    if not path.is_file():
        raise BrowserError("File not found", 404)
    if path.stat().st_size > MAX_TEXT_VIEW_BYTES:
        if automatic:
            return None
        raise BrowserError("Text preview exceeds 4 MiB limit; use Download", 413)
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_TEXT_VIEW_BYTES + 1)
    except OSError as exc:
        raise BrowserError("Cannot read file", 403) from exc
    if len(data) > MAX_TEXT_VIEW_BYTES:
        if automatic:
            return None
        raise BrowserError("Text preview exceeds 4 MiB limit; use Download", 413)
    content = readable_utf8(data)
    if content is None:
        if automatic:
            return None
        raise BrowserError("Not readable UTF-8 text; use Download", 415)
    suffix = path.suffix.casefold()
    if suffix == ".yid":
        # The actual Yiddish text is inserted only through HTML escaping.
        # dir=rtl + unicode-bidi:plaintext allows embedded Latin/numbers.
        body = ('<pre lang="yi" dir="rtl" '
                'style="direction:rtl;text-align:right;unicode-bidi:plaintext;'
                'white-space:pre-wrap;overflow-wrap:anywhere">')
    else:
        body = '<pre style="white-space:pre-wrap;overflow-wrap:anywhere">'
    return '<h2>' + escape(path.name) + '</h2>' + body + escape(content) + '</pre>'
