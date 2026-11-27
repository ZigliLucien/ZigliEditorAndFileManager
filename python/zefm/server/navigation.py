"""Confined, same-origin return links for the original ZEFM listing.

Accept a listing URL only; never redirect to external addresses or other routes.
Validate all its query parameters and keep directory traversal inside the root.
"""
from html import escape
import re
from urllib.parse import parse_qs, urlencode, urlsplit

from .file_manager import BrowserError

_ALLOWED_SORTS = {"filename", "filetype", "timekey", "timeold", "size", "notes"}


def safe_listing_return(files, candidate, default_path="."):
    default = "/listing?" + urlencode({"path": default_path})
    if not candidate:
        return default
    if not isinstance(candidate, str) or len(candidate) > 1400:
        raise BrowserError("Invalid return location")
    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc or parsed.fragment or parsed.path != "/listing":
        raise BrowserError("Return location must be a local ZEFM listing")
    try:
        args = parse_qs(parsed.query, strict_parsing=True, max_num_fields=4,
                        keep_blank_values=True, encoding="utf-8", errors="strict")
    except (UnicodeError, ValueError) as exc:
        raise BrowserError("Invalid return parameters") from exc
    if set(args) - {"path", "page", "sort", "filter"} or any(len(v) != 1 for v in args.values()):
        raise BrowserError("Unexpected return parameters")
    path = args.get("path", [default_path])[0]
    directory = files.resolve(path)
    if not directory.is_dir():
        raise BrowserError("Return directory not found", 404)
    # listing.js omits sort=timekey because Date/Time is the default.
    sort = args.get("sort", ["timekey"])[0]
    filt = args.get("filter", [""])[0]
    page = args.get("page", ["1"])[0]
    if sort not in _ALLOWED_SORTS or len(filt) > 200 or not page.isascii() or not page.isdecimal() or len(page) > 7 or not 1 <= int(page) <= 1000000:
        raise BrowserError("Invalid return listing state")
    return "/listing?" + urlencode({"path": files.relative(directory),
                                   "page": str(int(page)), "sort": sort, "filter": filt})


def preview_navigation(markup, directory_url, return_url=None):
    """Add a visible directory link to rendered HTML without rewriting its body."""
    links = ('<a href="' + escape(directory_url, quote=True)
             + '">← Open source directory</a>')
    if return_url and return_url != directory_url:
        links += (' · <a href="' + escape(return_url, quote=True)
                  + '">Return to previous listing</a>')
    nav = ('<nav aria-label="ZEFM preview navigation" '
           'style="padding:.65rem 1rem;margin:0 0 1rem;'
           'background:#f4f4f4;border-bottom:1px solid #ccc;'
           'font:14px system-ui,sans-serif">' + links + '</nav>')
    match = re.search(r"<body(?:\s[^>]*)?>", markup, re.IGNORECASE)
    if match:
        return markup[:match.end()] + nav + markup[match.end():]
    return nav + markup
