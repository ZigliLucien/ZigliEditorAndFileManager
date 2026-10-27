"""Process 04: explicit UTF-8 file operations."""
from pathlib import Path
from .model import Buffer

def open_buffer(path):
    p = Path(path)
    return Buffer(text=p.read_text(encoding="utf-8"), path=str(p), modified=False)

def save_buffer(buffer, path=None):
    destination = path or buffer.path
    if destination is None:
        raise ValueError("A destination path is required")
    p = Path(destination)
    p.write_text(buffer.text, encoding="utf-8")
    buffer.path = str(p)
    buffer.modified = False
