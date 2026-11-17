"""UTF-8 document file operations with atomic replacement on Save."""
import os
import stat
import tempfile
from pathlib import Path
from .model import Buffer


def open_buffer(path):
    p = Path(path)
    return Buffer(text=p.read_text(encoding="utf-8"), path=str(p), modified=False)


def save_buffer(buffer, path=None):
    """Write completely before replacing an existing file.

    All temporary files are created alongside the destination, allowing
    os.replace to be atomic on ordinary local filesystems. A failed write
    leaves the previous destination intact and the buffer unsaved.
    """
    destination = path or buffer.path
    if destination is None:
        raise ValueError("A destination path is required")
    p = Path(destination).expanduser()
    temporary = None
    try:
        original_mode = stat.S_IMODE(p.stat().st_mode) if p.exists() else None
        with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="",
                dir=p.parent, prefix=".zefm-save-", suffix=".tmp",
                delete=False) as output:
            temporary = Path(output.name)
            if os.name == "posix":
                os.fchmod(output.fileno(),
                          original_mode if original_mode is not None else 0o666 & ~_umask())
            output.write(buffer.text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, p)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    buffer.path = str(p)
    buffer.modified = False


def _umask():
    """Inspect current process umask without permanently modifying it."""
    mask = os.umask(0)
    os.umask(mask)
    return mask
