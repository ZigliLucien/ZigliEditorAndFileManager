"""Convert trusted local PostScript/EPS to a temporary browser PDF.

Ghostscript executes a programming language. Only use this localhost feature
with files you trust; SAFER is defense in depth, not a security boundary.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

from .file_manager import BrowserError

MAX_SOURCE_BYTES = 32 * 1024 * 1024
MAX_OUTPUT_BYTES = 128 * 1024 * 1024


def postscript_pdf(files, relative):
    path = files.resolve(relative)
    if path.suffix.casefold() not in {".ps", ".eps"} or not path.is_file():
        raise BrowserError("Not a PostScript or EPS file", 415)
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise BrowserError("PostScript exceeds preview limit", 413)
    gs = shutil.which("gs")
    if not gs:
        raise BrowserError("Install Ghostscript (gs) for PS/EPS preview", 501)
    with tempfile.TemporaryDirectory(prefix="zefm-ps-") as directory:
        pdf = Path(directory) / "preview.pdf"
        cmd = [gs, "-dSAFER", "-dBATCH", "-dNOPAUSE",
               "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.6",
               "-sOutputFile=" + str(pdf)]
        if path.suffix.casefold() == ".eps":
            cmd.append("-dEPSCrop")
        cmd.append(str(path))
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, timeout=30,
                                    check=False)
        except subprocess.TimeoutExpired as exc:
            raise BrowserError("PostScript conversion timed out", 504) from exc
        if result.returncode != 0 or not pdf.is_file():
            raise BrowserError("Ghostscript could not convert the document", 415)
        if pdf.stat().st_size > MAX_OUTPUT_BYTES:
            raise BrowserError("Converted PDF exceeds preview limit", 413)
        with pdf.open("rb") as f:
            if f.read(5) != b"%PDF-":
                raise BrowserError("Converted file has invalid PDF header", 415)
            f.seek(0)
            return f.read()
