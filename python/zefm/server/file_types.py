"""File-extension registry for the local ZEFM browser.

A single source of truth for natural View and optional Build actions.
"""
from pathlib import Path

_VIEW = {
    ".pdf": "pdf",
    ".html": "html", ".htm": "html",
    ".md": "markdown", ".markdown": "markdown",
    ".tex": "text",
}
_BUILDABLE = {".md": "discount", ".markdown": "discount", ".tex": "lualatex"}


def handler_for(name):
    suffix = Path(name).suffix.casefold()
    return {"view": _VIEW.get(suffix, "text"),
            "build": _BUILDABLE.get(suffix)}
