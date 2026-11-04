"""Confined rendered HTML previews with relative local stylesheet/image support.

Local HTML is untrusted: browser CSP sandbox forbids scripts, forms, plugins,
top-level navigation and same-origin privilege. Only a narrow set of static
resource extensions is exposed from the selected filesystem root.
"""
from __future__ import annotations

from pathlib import Path
from html import escape as html_escape, unescape as html_unescape
import re
from urllib.parse import quote, unquote, urlsplit

from .file_manager import BrowserError

MAX_HTML_BYTES = 4 * 1024 * 1024
MAX_RESOURCE_BYTES = 16 * 1024 * 1024
_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".xhtml": "application/xhtml+xml; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".webp": "image/webp",
    ".ico": "image/x-icon", ".bmp": "image/bmp",
    ".woff": "font/woff", ".woff2": "font/woff2",
}


# HTML, CSS, images and fonts may load as passive resources. All other
# linked extensions go through the normal ZEFM View dispatcher instead.
STATIC_SITE_EXTENSIONS = frozenset(_TYPES)


def site_url(relative: str) -> str:
    return "/site/" + "/".join(quote(part, safe="") for part in Path(relative).parts)


def site_relative_path(url_path: str):
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
    # A single trailing slash is normal for directory hyperlinks, whereas
    # empty components in the middle, dot segments, and traversal are forbidden.
    components = relative.rstrip("/").split("/")
    if (("\\" in relative or relative.startswith("/")
            or relative.endswith("//")
            or any(part in (".", "..", "") for part in components))):
        raise BrowserError("Invalid local resource path", 403)
    return "/".join(components)


# Rewrite only explicit local hyperlinks/resources. The browser cannot follow
# file:// links from an http:// origin; filesystem paths must be mapped through
# the root-confined /site/ endpoint. No external URLs are rewritten.
_LOCAL_ATTRIBUTES = re.compile(r"""(?i)\\b(href|src)\\s*=\\s*([\\x22\\x27])(.*?)\\2""", re.DOTALL)


def rewrite_local_links(document: str, files) -> str:
    def replace(match):
        raw = html_unescape(match.group(3).strip())
        parsed = urlsplit(raw)
        target = None
        if parsed.scheme.casefold() == "file" and parsed.netloc.lower() in ("", "localhost"):
            target = Path(unquote(parsed.path))
        elif not parsed.scheme and not parsed.netloc and parsed.path.startswith("/"):
            # A root-relative URL may name an actual absolute filesystem
            # location, or a location relative to the configured ZEFM root.
            absolute = Path(unquote(parsed.path))
            if absolute.is_relative_to(files.root):
                target = absolute
            else:
                target = files.root / unquote(parsed.path).lstrip("/")
        if target is None:
            return match.group(0)
        candidate = target.resolve()
        if not candidate.is_relative_to(files.root) or not candidate.exists():
            return match.group(0)
        relative = files.relative(candidate)
        if relative == ".":
            return match.group(0)
        url = site_url(relative)
        if candidate.is_dir():
            url += "/"
        if parsed.fragment:
            url += "#" + quote(unquote(parsed.fragment), safe="-_.~")
        return match.group(1) + "=" + match.group(2) + html_escape(url, quote=True) + match.group(2)
    return _LOCAL_ATTRIBUTES.sub(replace, document)


def site_resource(files, url_path):
    relative = site_relative_path(url_path)
    path = files.resolve(relative)
    if (not path.is_file() or (files.root / relative).is_symlink()):
        raise BrowserError("Static resource not found", 404)
    suffix = path.suffix.casefold()
    if suffix not in _TYPES:
        raise BrowserError("Resource type not permitted in HTML preview", 415)
    size = path.stat().st_size
    limit = MAX_HTML_BYTES if suffix in (".htm", ".html", ".xhtml", ".css") else MAX_RESOURCE_BYTES
    if size > limit:
        raise BrowserError("HTML preview resource too large", 413)
    data = path.read_bytes()
    if len(data) > limit:
        raise BrowserError("HTML preview resource too large", 413)
    if suffix in (".html", ".htm", ".xhtml", ".css"):
        try:
            decoded = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BrowserError("HTML preview expects UTF-8 text", 415) from exc
        if suffix in (".html", ".htm", ".xhtml"):
            data = rewrite_local_links(decoded, files).encode("utf-8")
    return data, _TYPES[suffix], suffix in (".html", ".htm", ".xhtml")


HTML_PREVIEW_CSP = (
    "default-src 'none'; "
    "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "font-src 'self'; base-uri 'none'; form-action 'none'; "
    "frame-ancestors 'none'; object-src 'none'; "
    "sandbox allow-top-navigation-by-user-activation"
)
