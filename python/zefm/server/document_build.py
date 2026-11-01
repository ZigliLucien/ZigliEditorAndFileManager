"""Bounded Markdown preview and PDF builds for local ZEFM documents.

Builds execute known programs with argv (never a shell), a timeout,
controlled per-source output directory, and explicit diagnostics.
TeX is a *programming language*: -no-shell-escape does not fully sandbox it;
only build trusted TeX files.
"""
from __future__ import annotations

from html import escape
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from .file_manager import BrowserError
from .file_types import handler_for

MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_PDF_BYTES = 128 * 1024 * 1024
BUILD_TIMEOUT = 45
MAX_OUTPUT = 100000

def checked_source(files, relative, *, for_build=False):
    path = files.resolve(relative)
    if not path.is_file() or (files.root / relative).is_symlink():
        raise BrowserError("Source file unavailable", 404)
    descriptor = handler_for(path.name)
    if for_build and descriptor["build"] is None:
        raise BrowserError("This file type has no PDF builder", 415)
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise BrowserError("Document exceeds browser source limit", 413)
    return path, descriptor


def markdown_html(files, relative):
    """Render Markdown into sandboxed HTML without exposing raw scripts.

    Pandoc is optional; when unavailable preserve a readable escaped source.
    HTML rendering and external resources remain blocked by the CSP.
    """
    source, desc = checked_source(files, relative)
    if desc["view"] != "markdown":
        raise BrowserError("Not a Markdown file", 415)
    raw = source.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise BrowserError("Markdown file is not UTF-8", 415) from exc
    pandoc = shutil.which("pandoc")
    if pandoc:
        try:
            result = subprocess.run(
                [pandoc, "--from=markdown-raw_html", "--to=html5",
                 "--no-highlight"], input=text, capture_output=True, text=True,
                timeout=10, check=False, cwd=str(source.parent))
        except (subprocess.TimeoutExpired, OSError):
            result = None
        if result is not None and result.returncode == 0 and len(result.stdout) < 2 * MAX_SOURCE_BYTES:
            body = result.stdout
        else:
            body = "<pre>" + escape(text) + "</pre>"
    else:
        body = "<pre>" + escape(text) + "</pre>"
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>" + escape(source.name) + "</title>"
            "<style>body{font:16px/1.6 system-ui,sans-serif;max-width:940px;"
            "margin:2rem auto;padding:0 1rem}pre{overflow:auto;background:#f4f4f4;"
            "padding:1rem}code{font-family:monospace}</style></head><body>"
            + body + "</body></html>").encode("utf-8")


def _command(source, output_dir, descriptor):
    if descriptor["build"] == "pandoc":
        binary = shutil.which("pandoc")
        if not binary:
            raise BrowserError("Pandoc is not installed or not on PATH", 503)
        # Deliberately do not allow raw TeX or raw HTML from Markdown.
        return [binary, "--from=markdown-raw_tex-raw_html",
                "--pdf-engine=lualatex", "--output",
                str(output_dir / "document.pdf"), str(source)]
    if descriptor["build"] == "lualatex":
        binary = shutil.which("lualatex")
        if not binary:
            raise BrowserError("LuaLaTeX is not installed or not on PATH", 503)
        return [binary, "-interaction=nonstopmode", "-halt-on-error",
                "-no-shell-escape", f"-output-directory={output_dir}",
                str(source)]
    raise BrowserError("File type cannot be built", 415)


def build_pdf(files, relative):
    """Compile to a new PDF, returning its root-relative path and log.

    Builds are deliberately performed in a new temporary directory. A PDF
    already present from a previous build never counts as a successful result.
    """
    source, descriptor = checked_source(files, relative, for_build=True)
    output_base = source.parent / ".zefm-build"
    output_base.mkdir(mode=0o700, exist_ok=True)
    if output_base.is_symlink() or not output_base.resolve().is_relative_to(files.root):
        raise BrowserError("Unsafe output directory", 403)
    temporary = Path(tempfile.mkdtemp(prefix="job-", dir=output_base))
    try:
        command = _command(source, temporary, descriptor)
        started = time.monotonic()
        try:
            process = subprocess.run(command, cwd=source.parent,
                                     capture_output=True, text=True,
                                     errors="replace", timeout=BUILD_TIMEOUT,
                                     check=False, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:
            raise BrowserError("PDF compilation exceeded 45 seconds", 408) from exc
        except OSError as exc:
            raise BrowserError(f"Could not launch PDF engine: {exc}", 503) from exc
        log = ((process.stdout or "") + "\n" + (process.stderr or ""))[-MAX_OUTPUT:]
        if descriptor["build"] == "lualatex":
            produced = temporary / (source.stem + ".pdf")
        else:
            produced = temporary / "document.pdf"
        if process.returncode != 0:
            return {"ok": False, "log": log, "returncode": process.returncode,
                    "elapsed": round(time.monotonic() - started, 2)}
        if not produced.is_file() or produced.is_symlink():
            return {"ok": False, "log": log + "\nNo PDF was produced.", "returncode": 0}
        if produced.stat().st_size > MAX_PDF_BYTES or produced.read_bytes()[:5] != b"%PDF-":
            return {"ok": False, "log": log + "\nInvalid or oversized PDF.", "returncode": 0}
        # The per-source published location distinguishes .tex from .md.
        # Never overwrite an existing user file: output_base is dedicated
        # to ZEFM-generated files only.
        digest = hashlib.sha256(str(source).encode("utf-8")).hexdigest()[:12]
        final = output_base / (source.name + "-" + digest + ".pdf")
        if final.is_symlink():
            raise BrowserError("Build output destination is a symlink", 409)
        produced.replace(final)
        return {"ok": True, "pdf": files.relative(final), "log": log,
                "returncode": 0, "elapsed": round(time.monotonic() - started, 2)}
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
