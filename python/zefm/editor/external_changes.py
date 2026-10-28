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


class ExternalChangeDismissals:
    """Dismiss only a particular disk revision, not all future changes.

    Tab IDs can be any hashable values. A missing disk file is represented by
    a None signature; membership checks avoid confusing it with no dismissal.
    """

    def __init__(self):
        self._ignored = {}

    def pending(self, tab, baseline, current):
        return (current != baseline and
                (tab not in self._ignored or self._ignored[tab] != current))

    def dismiss(self, tab, signature):
        self._ignored[tab] = signature

    def reset(self, tab):
        self._ignored.pop(tab, None)
