"""Forward SyncTeX: map a saved .tex source location to its PDF page.

No shell, no viewer-specific application commands. ZEFM uses a browser
PDF URL with #page=N (where supported by the browser PDF viewer).
"""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

_PAGE = re.compile(r"^Page:\s*(\d+)\s*$", re.MULTILINE)


def synctex_page(source: Path, line: int, pdf: Path, *, column: int = 1,
                 timeout: int = 8) -> int:
    """Return a 1-based PDF page for a SyncTeX forward-search query.

    The PDF and its .synctex.gz companion must represent the same build.
    Callers should pass the fresh preview PDF returned by the build step.
    """
    source = Path(source).expanduser().resolve()
    pdf = Path(pdf).expanduser().resolve()
    if source.suffix.lower() != ".tex" or not source.is_file():
        raise ValueError("A saved .tex source file is required")
    if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
        raise ValueError("A compiled PDF is required")
    companion = pdf.with_suffix(".synctex.gz")
    if companion.is_symlink() or not companion.is_file():
        raise ValueError("This PDF has no matching SyncTeX data; compile first")
    if not isinstance(line, int) or line < 1 or not isinstance(column, int) or column < 1:
        raise ValueError("Invalid LaTeX source location")
    executable = shutil.which("synctex")
    if not executable:
        raise ValueError("The synctex command is not installed or on PATH")
    argv = [executable, "view", "-i", f"{line}:{column}:{source}",
            "-o", str(pdf)]
    try:
        result = subprocess.run(
            argv, cwd=str(pdf.parent), stdin=subprocess.DEVNULL,
            capture_output=True, text=True, errors="replace",
            check=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("SyncTeX lookup timed out") from exc
    except OSError as exc:
        raise ValueError(f"Could not launch SyncTeX: {exc}") from exc
    if result.returncode:
        raise ValueError(
            "SyncTeX could not locate that source line in the PDF: "
            + (result.stderr or result.stdout or "unknown error").strip()[:250])
    pages = [int(value) for value in _PAGE.findall(result.stdout or "")
             if int(value) > 0]
    if not pages:
        raise ValueError("No corresponding PDF page was reported by SyncTeX")
    return pages[0]


def pdf_page_uri(pdf: Path, page: int) -> str:
    if not isinstance(page, int) or page < 1:
        raise ValueError("PDF page must be positive")
    return Path(pdf).expanduser().resolve().as_uri() + f"#page={page}"
