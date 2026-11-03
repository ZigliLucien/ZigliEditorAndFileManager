"""Confined rendered HTML previews with relative local stylesheet/image support.

Local HTML is untrusted: browser CSP sandbox forbids scripts, forms, plugins,
top-level navigation and same-origin privilege. Only a narrow set of static
resource extensions is exposed from the selected filesystem root.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote, unquote

from .file_manager import BrowserError

MAX_HTML_BYTES = 4 * 1024 * 1024
MAX_RESOURCE_BYTES = 16 * 1024 * 1024
_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".webp": "image/webp",
    ".ico": "image/x-icon", ".bmp": "image/bmp",
    ".woff": "font/woff", ".woff2": "font/woff2",
}


def site_url(relative: str) -> str:
    return "/site/" + "/".join(quote(part, safe="") for part in Path(relative).parts)


def site_resource(files, url_path: str):
    if not url_path.startswith("/site/"):
        raise BrowserError("Unknown resource route", 404)
    tail = url_path[len("/site/"):]
    if not tail or "%" in unquote(tail) or "\x00" in tail:
        raise BrowserError("Invalid local resource name")
    try:
        relative = unquote(tail, encoding="utf-8", errors="strict")
    except UnicodeError as exc:
        raise BrowserError("Invalid UTF-8 resource path") from exc
    # Backslashes and navigation elements are not needed in ordinary HTML
    # resource links. Explicitly reject rather than normalize.
    if ("\\" in relative or any(bit in (".", "..", "") for bit in relative.split("/"))
            or relative.startswith("/")):
        raise BrowserError("Invalid local resource path", 403)
    path = files.resolve(relative)
    if (not path.is_file() or (files.root / relative).is_symlink()):
        raise BrowserError("Static resource not found", 404)
    suffix = path.suffix.casefold()
    if suffix not in _TYPES:
        raise BrowserError("Resource type not permitted in HTML preview", 415)
    size = path.stat().st_size
    limit = MAX_HTML_BYTES if suffix in (".htm", ".html", ".css") else MAX_RESOURCE_BYTES
    if size > limit:
        raise BrowserError("HTML preview resource too large", 413)
    data = path.read_bytes()
    if len(data) > limit:
        raise BrowserError("HTML preview resource too large", 413)
    if suffix in (".html", ".htm", ".css"):
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BrowserError("HTML preview expects UTF-8 text", 415) from exc
    return data, _TYPES[suffix], suffix in (".html", ".htm")


HTML_PREVIEW_CSP = (
    "default-src 'none'; "
    "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "font-src 'self'; base-uri 'none'; form-action 'none'; "
    "frame-ancestors 'none'; object-src 'none'; "
    "sandbox allow-top-navigation-by-user-activation"
)
