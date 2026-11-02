"""Safe extensions of the user's port-8000 command-mapping idea.

JSON and XML use Python libraries; notebooks use optional nbconvert.
No shell, CGI, Perl or access outside the configured local root.
"""
from __future__ import annotations

from html import escape
import json
import shutil
import subprocess
from xml.dom import minidom
from .file_manager import BrowserError

MAX_SOURCE = 8 * 1024 * 1024
MAX_RESULT = 24 * 1024 * 1024


def transformed_document(files, relative):
    path = files.resolve(relative)
    suffix = path.suffix.casefold()
    if suffix not in {".json", ".xml", ".ipynb"} or not path.is_file():
        raise BrowserError("Unsupported structured document", 415)
    if path.stat().st_size > MAX_SOURCE:
        raise BrowserError("Structured document exceeds preview limit", 413)
    if suffix == ".json":
        try:
            content = json.dumps(json.loads(path.read_text(encoding="utf-8")),
                                 ensure_ascii=False, indent=2)
        except (ValueError, UnicodeError) as exc:
            raise BrowserError("Invalid JSON", 415) from exc
        return "<h2>" + escape(path.name) + "</h2><pre>" + escape(content) + "</pre>"
    if suffix == ".xml":
        try:
            # Equivalent to the original xq '.' display intent, but remains XML.
            content = minidom.parse(str(path)).toprettyxml(indent="  ")
        except Exception as exc:
            raise BrowserError("Invalid XML", 415) from exc
        return "<h2>" + escape(path.name) + "</h2><pre>" + escape(content) + "</pre>"
    executable = shutil.which("jupyter")
    if executable is None:
        raise BrowserError("Notebook preview requires Jupyter nbconvert", 501)
    try:
        result = subprocess.run([executable, "nbconvert", "--to", "html",
                                 "--stdout", str(path)], capture_output=True,
                                timeout=30, check=False)
    except subprocess.TimeoutExpired as exc:
        raise BrowserError("Notebook preview timed out", 504) from exc
    if result.returncode != 0:
        raise BrowserError("Notebook conversion failed", 415)
    if len(result.stdout) > MAX_RESULT:
        raise BrowserError("Notebook preview exceeds output limit", 413)
    # Return HTML to be rendered with a restrictive CSP in the HTTP handler.
    return result.stdout.decode("utf-8", errors="replace")
