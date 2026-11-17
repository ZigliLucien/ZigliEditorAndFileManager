"""Choose a safe startup buffer from ZEFM's persisted Recent Files list.

Missing, non-text or unreadable files are skipped without warning dialogs.
The recent-files history is not pruned just because a mount is unavailable.
"""
from pathlib import Path

from .files import open_buffer


def last_recent_buffer(recent_files):
    for filename in recent_files.entries:
        try:
            path = Path(filename).expanduser().resolve()
            if not path.is_file():
                continue
            return open_buffer(path)
        except (OSError, UnicodeError, ValueError):
            continue
    return None
