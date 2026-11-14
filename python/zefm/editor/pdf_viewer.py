"""Optional PDF viewer selection for the desktop editor.

The browser is the portable default. Okular is explicitly opt-in on machines
where it is installed, and receives argv (never a shell command).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

VIEWERS = ("browser", "okular")


class PdfViewerPreference:
    def __init__(self, path=None):
        self.path = (Path(path).expanduser() if path is not None else
                     Path.home() / ".config" / "zefm" / "pdf_viewer.json")
        self.viewer = "browser"
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("viewer") in VIEWERS:
                self.viewer = data["viewer"]
        except (OSError, ValueError, TypeError):
            pass

    def set(self, viewer):
        if viewer not in VIEWERS:
            raise ValueError("PDF viewer must be browser or okular")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8",
                    prefix=".pdf-viewer-", suffix=".tmp",
                    dir=self.path.parent, delete=False) as out:
                temporary = Path(out.name)
                if os.name == "posix":
                    os.fchmod(out.fileno(), 0o600)
                json.dump({"viewer": viewer}, out, ensure_ascii=False, indent=2)
                out.write("\n")
                out.flush()
                os.fsync(out.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        self.viewer = viewer


def okular_argv(pdf, *, source=None, line=None):
    binary = shutil.which("okular")
    if not binary:
        raise ValueError("Okular is not installed or is absent from PATH")
    pdf = Path(pdf).expanduser().resolve()
    if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
        raise ValueError("The compiled PDF does not exist")
    if source is None:
        return [binary, "--unique", str(pdf)]
    source = Path(source).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".tex":
        raise ValueError("SyncTeX needs an existing .tex source")
    if not isinstance(line, int) or line < 1:
        raise ValueError("Invalid source line")
    companion = pdf.with_suffix(".synctex.gz")
    if companion.is_symlink() or not companion.is_file():
        raise ValueError("No matching SyncTeX index for this PDF")
    # Okular's supported forward-search syntax; use a single argv token so
    # filenames containing spaces, Unicode, etc. are never shell-split.
    return [binary, "--unique", pdf.as_uri() + f"#src:{line}" + str(source)]


def launch_okular(pdf, *, source=None, line=None):
    argv = okular_argv(pdf, source=source, line=line)
    try:
        subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True, cwd=str(Path(pdf).resolve().parent))
    except OSError as exc:
        raise ValueError(f"Could not open Okular: {exc}") from exc
