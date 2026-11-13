"""Discount makepage preview and PDF builds for local ZEFM documents.

Builds execute known programs with argv (never a shell), a timeout,
controlled per-source output directory, and explicit diagnostics.
TeX is a *programming language*: -no-shell-escape does not fully sandbox it;
only build trusted TeX files.
"""
from __future__ import annotations

from html import escape, unescape
import hashlib
import os
import sys
import re
from uuid import uuid4
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from .file_manager import BrowserError
from .file_types import handler_for
from .math_presentation import format_math_html
from .mathjax_filter import inject_mathjax
from .latex_sequence import run_tex_sequence

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


# Discount's nohtml option intentionally suppresses arbitrary inline HTML.
# Preserve only safely recognized, simple foreground-color spans in Markdown.
# The source is never sent as executable HTML.
_COLOR_SPAN = re.compile(
    r"""<span\s+style\s*=\s*["']?color\s*:\s*(orange|red|blue|green|purple|gray|grey|black)["']?\s*>\s*([^<>\n]*)</span>""",
    re.IGNORECASE,
)


def _protect_color_spans(markdown: str):
    replacements = {}
    key = "ZEFMINLINE" + uuid4().hex.upper()
    def substitute(match):
        token = key + "TOKEN" + str(len(replacements)) + "END"
        color = match.group(1).casefold()
        if color == "grey":
            color = "gray"
        # Escape source text before restoring the intentional inline span.
        replacements[token] = (
            '<span style="color:' + color + '">' +
            escape(unescape(match.group(2))) + '</span>')
        return token
    return _COLOR_SPAN.sub(substitute, markdown), replacements


def _restore_color_spans(html: str, replacements: dict):
    for token, safe_span in replacements.items():
        html = html.replace(token, safe_span)
    return html


def _discount_command():
    """Prefer Discount's makepage, as in the original ZEFM workflow."""
    executable = shutil.which("makepage")
    if executable:
        return [executable, "-f", "latex,nostyle,nohtml"]
    executable = shutil.which("markdown")
    if executable:
        return [executable, "-f", "latex,nostyle,nohtml"]
    return None


def _discount_render(text: str, source: Path) -> str | None:
    command = _discount_command()
    if command is None:
        return None
    try:
        proc = subprocess.run(
            command, input=text, cwd=str(source.parent), capture_output=True,
            text=True, errors="replace", timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or len(proc.stdout.encode("utf-8")) > 2 * MAX_SOURCE_BYTES:
        return None
    result = proc.stdout
    # makepage creates a complete HTML page, while markdown produces a body
    # fragment. Keep that native makepage structure for visual fidelity.
    if Path(command[0]).name == "makepage":
        return result
    return ("<!doctype html><html><head><meta charset='utf-8'></head>"
            "<body>" + result + "</body></html>")


def markdown_html(files, relative):
    """Use Discount makepage to display Markdown, with escaped-source fallback."""
    source, desc = checked_source(files, relative)
    if desc["view"] != "markdown":
        raise BrowserError("Not a Markdown file", 415)
    try:
        text = source.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BrowserError("Markdown file is not UTF-8", 415) from exc
    prepared, spans = _protect_color_spans(text)
    rendered = _discount_render(prepared, source)
    if rendered is not None:
        rendered = _restore_color_spans(rendered, spans)
        return inject_mathjax(format_math_html(rendered)).encode("utf-8")
    fallback = ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>" + escape(source.name) + "</title>"
            "<style>body{font:16px/1.6 system-ui,sans-serif;max-width:940px;"
            "margin:2rem auto;padding:0 1rem}pre{overflow:auto;background:#f4f4f4;"
            "padding:1rem}</style></head><body>"
            "<pre>" + escape(text) + "</pre></body></html>")
    return inject_mathjax(format_math_html(fallback)).encode("utf-8")


def _command(source, output_dir, descriptor):
    if descriptor["build"] == "discount":
        # The Markdown build now follows Discount -> HTML -> PDF, not Pandoc.
        # The HTML conversion itself is done before this command is returned.
        engine = shutil.which("weasyprint")
        if not engine:
            raise BrowserError(
                "Markdown PDF requires WeasyPrint (and Discount makepage). "
                "The Markdown HTML preview already works without it.", 503)
        return [engine, str(output_dir / "document.html"),
                str(output_dir / "document.pdf")]
    if descriptor["build"] == "lualatex":
        binary = shutil.which("lualatex")
        if not binary and sys.platform == "darwin":
            # Finder/Aqua-launched applications may not inherit the shell PATH.
            # MacTeX publishes a stable symlink here; do not modify global PATH.
            standard = Path("/Library/TeX/texbin/lualatex")
            if standard.is_file() and os.access(standard, os.X_OK):
                binary = str(standard)
        if not binary:
            raise BrowserError(
                "LuaLaTeX was not found. On macOS check MacTeX at "
                "/Library/TeX/texbin/lualatex; on other systems check PATH.", 503)
        return [binary, "-interaction=nonstopmode", "-halt-on-error",
                "-no-shell-escape", f"-output-directory={output_dir}",
                str(source)]
    raise BrowserError("File type cannot be built", 415)


def _publish_adjacent_pdf(produced: Path, source: Path) -> Path:
    """Atomically update source.with_suffix('.pdf') after a verified build.

    The desktop Compile command intentionally updates the conventional
    TeX output, unlike browser builds, which retain their isolated previews.
    Refuse symlinks and nonregular targets rather than following them.
    """
    destination = source.with_suffix(".pdf")
    if destination.is_symlink() or (
            destination.exists() and not destination.is_file()):
        raise BrowserError("PDF destination must be a regular file, not a link or directory", 409)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                prefix=".zefm-pdf-", suffix=".tmp", dir=source.parent,
                delete=False) as out:
            temporary = Path(out.name)
            with produced.open("rb") as incoming:
                shutil.copyfileobj(incoming, out)
            out.flush()
            os.fsync(out.fileno())
        # Recheck immediately before publication; os.replace never follows
        # a destination symlink, but we also avoid replacing a named link.
        if destination.is_symlink() or (
                destination.exists() and not destination.is_file()):
            raise BrowserError("PDF destination changed to an unsafe file", 409)
        os.replace(temporary, destination)
        return destination
    except OSError as exc:
        raise BrowserError(f"Could not update {destination.name}: {exc}", 500) from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_pdf(files, relative, *, publish_adjacent=False):
    """Compile to a new PDF, returning its root-relative path and log.

    Builds are deliberately performed in a new temporary directory. A PDF
    already present from a previous build never counts as a successful result.
    The desktop editor explicitly requests publish_adjacent=True to refresh
    the ordinary source-name PDF after a successful and validated build.
    """
    source, descriptor = checked_source(files, relative, for_build=True)
    output_base = source.parent / ".zefm-build"
    output_base.mkdir(mode=0o700, exist_ok=True)
    if output_base.is_symlink() or not output_base.resolve().is_relative_to(files.root):
        raise BrowserError("Unsafe output directory", 403)
    temporary = Path(tempfile.mkdtemp(prefix="job-", dir=output_base))
    try:
        if descriptor["build"] == "discount":
            if not _discount_command():
                raise BrowserError("Discount makepage or markdown is required", 503)
            try:
                text = source.read_bytes().decode("utf-8")
            except UnicodeDecodeError as exc:
                raise BrowserError("Markdown file is not UTF-8", 415) from exc
            prepared, spans = _protect_color_spans(text)
            html = _discount_render(prepared, source)
            if html is None:
                raise BrowserError("Discount Markdown conversion failed", 422)
            html = _restore_color_spans(html, spans)
            (temporary / "document.html").write_text(format_math_html(html), encoding="utf-8")
        command = _command(source, temporary, descriptor)
        started = time.monotonic()
        if descriptor["build"] == "lualatex":
            # Both desktop F4 and browser Compile use the same bounded
            # multi-pass pipeline, including bibliography when detected.
            rc, log, elapsed = run_tex_sequence(
                command, source, temporary, timeout=BUILD_TIMEOUT)
        else:
            try:
                process = subprocess.run(command, cwd=source.parent,
                                         capture_output=True, text=True,
                                         errors="replace", timeout=BUILD_TIMEOUT,
                                         check=False, stdin=subprocess.DEVNULL)
            except subprocess.TimeoutExpired as exc:
                raise BrowserError("PDF compilation exceeded 45 seconds", 408) from exc
            except OSError as exc:
                raise BrowserError(f"Could not launch PDF engine: {exc}", 503) from exc
            rc = process.returncode
            log = ((process.stdout or "") + "\n" + (process.stderr or ""))[-MAX_OUTPUT:]
            elapsed = round(time.monotonic() - started, 2)
        if descriptor["build"] == "lualatex":
            produced = temporary / (source.stem + ".pdf")
        else:
            produced = temporary / "document.pdf"
        if rc != 0:
            return {"ok": False, "log": log, "returncode": rc,
                    "elapsed": elapsed}
        if not produced.is_file() or produced.is_symlink():
            return {"ok": False, "log": log + "\nNo PDF was produced.", "returncode": 0}
        if produced.stat().st_size > MAX_PDF_BYTES or produced.read_bytes()[:5] != b"%PDF-":
            return {"ok": False, "log": log + "\nInvalid or oversized PDF.", "returncode": 0}
        # The per-source published location distinguishes .tex from .md.
        # Never overwrite an existing user file: output_base is dedicated
        # to ZEFM-generated files only.
        digest = hashlib.sha256(str(source).encode("utf-8")).hexdigest()[:12]
        # A fresh URL for every build prevents browsers (especially native
        # PDF viewers handling file:// URLs) from showing a cached old PDF.
        # The source digest keeps names identifiable; the nonce identifies
        # this particular compilation.
        final = output_base / (
            source.name + "-" + digest + "-" + uuid4().hex + ".pdf")
        # No overwrite: atomically publish a new file in the same filesystem.
        # Old PDFs remain accessible and no previous result is mistaken for
        # the current successful compilation.
        os.link(produced, final, follow_symlinks=False)
        if publish_adjacent and descriptor["build"] == "lualatex":
            try:
                adjacent = _publish_adjacent_pdf(produced, source)
            except Exception:
                final.unlink(missing_ok=True)
                raise
        else:
            adjacent = None
        result = {"ok": True, "pdf": files.relative(final), "log": log,
                  "returncode": 0, "elapsed": elapsed}
        if adjacent is not None:
            result["output_pdf"] = files.relative(adjacent)
        return result
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
