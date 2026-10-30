"""Bounded local PDF preview with HTTP byte-range support.

Only regular, PDF-signature files inside LocalFiles.root are served. Byte ranges
are important for native browser PDF viewers seeking to later pages.
"""
from __future__ import annotations

from pathlib import Path
import re

from .file_manager import BrowserError

MAX_PDF_BYTES = 128 * 1024 * 1024
_RANGE = re.compile(r"bytes=(\d*)-(\d*)\Z")


def select_pdf(files, relative: str) -> Path:
    path = files.resolve(relative)
    if not path.is_file():
        raise BrowserError("PDF not found", 404)
    if path.suffix.casefold() != ".pdf":
        raise BrowserError("Only PDF files can be previewed here", 415)
    if path.stat().st_size > MAX_PDF_BYTES:
        raise BrowserError("PDF exceeds browser preview limit (128 MiB)", 413)
    return path


def byte_range(header: str | None, size: int) -> tuple[int, int, bool]:
    """Return inclusive start/end and whether a Range request was supplied."""
    if header is None:
        return 0, max(0, size - 1), False
    match = _RANGE.fullmatch(header.strip())
    if not match or not size:
        raise BrowserError("Unsupported or unsatisfiable PDF byte range", 416)
    first, last = match.groups()
    if not first and not last:
        raise BrowserError("Invalid PDF byte range", 416)
    if first:
        start = int(first)
        end = int(last) if last else size - 1
        if start >= size or end < start:
            raise BrowserError("Unsatisfiable PDF byte range", 416)
        return start, min(end, size - 1), True
    suffix = int(last)
    if not suffix:
        raise BrowserError("Unsatisfiable PDF byte range", 416)
    return max(0, size - suffix), size - 1, True
