"""Filesystem-only browser operations, inspired by ServPakDir GoFM/FileOps/WebEdit.

No SQL, shell execution, remote access or writable paths outside the chosen root.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import tempfile

MAX_EDIT_BYTES = 1024 * 1024
# Keep copy operations bounded: no giant uploads or unexpected disk exhaustion.
MAX_COPY_BYTES = 64 * 1024 * 1024


def _child_name(name: str) -> str:
    """A single UTF-8 filename, not a path or an absolute destination."""
    if (not isinstance(name, str) or not name or name in (".", "..")
            or "/" in name or "\\\\" in name
            or any(ord(char) < 32 or ord(char) == 127 for char in name)
            or len(name.encode("utf-8")) > 255):
        raise BrowserError("Enter one valid filename (no path separators or controls)")
    return name



class BrowserError(Exception):
    """An expected browser error with a corresponding HTTP status."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


class LocalFiles:
    def __init__(self, root: str | Path):
        p = Path(root).expanduser().resolve()
        if not p.is_dir():
            raise ValueError(f"Not a directory: {p}")
        self.root = p

    def resolve(self, relative: str = ".") -> Path:
        if not isinstance(relative, str) or "\0" in relative:
            raise BrowserError("Invalid file path")
        if Path(relative).is_absolute():
            raise BrowserError("Absolute paths are not allowed", 403)
        candidate = (self.root / relative).resolve()
        if not candidate.is_relative_to(self.root):
            raise BrowserError("Path leaves the shared directory", 403)
        return candidate

    def relative(self, path: Path) -> str:
        return str(path.relative_to(self.root)) or "."

    def list_directory(self, relative: str = ".") -> tuple[Path, list[Path]]:
        p = self.resolve(relative)
        if not p.exists():
            raise BrowserError("Directory not found", 404)
        if not p.is_dir():
            raise BrowserError("Not a directory", 404)
        try:
            entries = sorted(p.iterdir(), key=lambda f: (not f.is_dir(), f.name.casefold(), f.name))
        except OSError as exc:
            raise BrowserError(f"Directory cannot be read: {exc}", 403) from exc
        # A symlink is displayed but will not open if it points outside the root.
        return p, entries


    def create_directory(self, relative: str, name: str) -> Path:
        """Create one subdirectory; never overwrite any existing entry."""
        parent = self.resolve(relative)
        if not parent.is_dir():
            raise BrowserError("Parent directory not found", 404)
        target = parent / _child_name(name)
        try:
            target.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise BrowserError("A file or directory with that name already exists", 409) from exc
        except OSError as exc:
            raise BrowserError(f"Cannot create directory: {exc}", 403) from exc
        return target

    def copy_file(self, relative: str, new_name: str) -> Path:
        """Copy a file next to itself, atomically publishing without overwrite.

        A private temporary file is filled and fsynced first, then a hardlink
        publishes the completed copy only if the target does not already exist.
        Neither source nor target may escape the selected browser root.
        """
        source = self.resolve(relative)
        if not source.is_file() or (self.root / relative).is_symlink():
            raise BrowserError("Source must be a regular file, not a symlink", 404)
        target = source.parent / _child_name(new_name)
        if source == target:
            raise BrowserError("Choose a different filename for the copy", 409)
        temporary = None
        try:
            original = source.stat()
            if original.st_size > MAX_COPY_BYTES:
                raise BrowserError("File too large to copy in the browser", 413)
            with source.open("rb") as reader:
                with tempfile.NamedTemporaryFile(dir=source.parent,
                                                 prefix=".zefm-copy-", delete=False) as writer:
                    temporary = Path(writer.name)
                    total = 0
                    while chunk := reader.read(1024 * 1024):
                        total += len(chunk)
                        if total > MAX_COPY_BYTES:
                            raise BrowserError("File too large to copy in the browser", 413)
                        writer.write(chunk)
                    os.fchmod(writer.fileno(), stat.S_IMODE(original.st_mode))
                    writer.flush()
                    os.fsync(writer.fileno())
            current = source.stat()
            if ((original.st_ino, original.st_size, original.st_mtime_ns)
                    != (current.st_ino, current.st_size, current.st_mtime_ns)):
                raise BrowserError("Source changed during copying; retry", 409)
            # On POSIX this fails atomically when target exists, including
            # a symlink. Unlike os.rename/os.replace it can never clobber.
            os.link(temporary, target)
            return target
        except FileExistsError as exc:
            raise BrowserError("A file with that name already exists", 409) from exc
        except OSError as exc:
            raise BrowserError(f"Cannot copy file: {exc}", 403) from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def _text_bytes(self, relative: str) -> tuple[Path, bytes]:
        p = self.resolve(relative)
        if not p.is_file():
            raise BrowserError("File not found", 404)
        try:
            if p.stat().st_size > MAX_EDIT_BYTES:
                raise BrowserError("File too large for browser editing", 413)
            data = p.read_bytes()
        except OSError as exc:
            raise BrowserError(f"Cannot read file: {exc}", 403) from exc
        if len(data) > MAX_EDIT_BYTES:
            raise BrowserError("File too large for browser editing", 413)
        return p, data

    def read_text(self, relative: str) -> tuple[str, str]:
        _, data = self._text_bytes(relative)
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BrowserError("Not UTF-8 text; use Download instead", 415) from exc
        return content, hashlib.sha256(data).hexdigest()

    def save_text(self, relative: str, content: str, original_digest: str) -> None:
        p, previous = self._text_bytes(relative)
        if hashlib.sha256(previous).hexdigest() != original_digest:
            raise BrowserError("File changed since opening; reload before saving", 409)
        # Browser textareas transmit CRLF. Retain the file's existing newline style.
        text = content.replace("\r\n", "\n")
        if b"\r\n" in previous and b"\n" not in previous.replace(b"\r\n", b""):
            text = text.replace("\n", "\r\n")
        data = text.encode("utf-8")
        if len(data) > MAX_EDIT_BYTES:
            raise BrowserError("Edited text exceeds size limit", 413)
        tmp = None
        try:
            mode = stat.S_IMODE(p.stat().st_mode)
            with tempfile.NamedTemporaryFile(dir=p.parent, prefix=".zefm-save-", delete=False) as handle:
                tmp = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(tmp, mode)
            # Recheck stale contents before replacement (best-effort local concurrency).
            if hashlib.sha256(p.read_bytes()).hexdigest() != original_digest:
                raise BrowserError("File changed while saving; reload before saving", 409)
            os.replace(tmp, p)
        except OSError as exc:
            raise BrowserError(f"Cannot save file: {exc}", 403) from exc
        finally:
            if tmp is not None:
                tmp.unlink(missing_ok=True)
