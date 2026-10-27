"""Track external changes to open files without touching the editor buffer.

Content hashes avoid false alarms from timestamp-only updates. A missing file
counts as changed. The editor chooses whether to reload or overwrite.
"""
import hashlib
from pathlib import Path


def disk_signature(path):
    """Return SHA-256 of file bytes, or None if no file exists."""
    try:
        data = Path(path).read_bytes()
    except FileNotFoundError:
        return None
    return hashlib.sha256(data).hexdigest()


def changed_on_disk(path, original_signature):
    return disk_signature(path) != original_signature
