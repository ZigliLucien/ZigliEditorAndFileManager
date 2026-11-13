"""Persistent explicit LaTeX master selection for individual source files.

Only explicitly selected master paths are stored, not source contents.
Storage is a local UTF-8 JSON file and never enters the repository.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from .latex_master import resolve_latex_master

MAX_ENTRIES = 500


class LatexMasterPreferences:
    def __init__(self, state_path=None):
        self.path = (Path(state_path).expanduser() if state_path is not None
                     else Path.home() / ".config" / "zefm" / "latex_masters.json")
        self.entries: dict[str, str] = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            raw = data.get("masters") if isinstance(data, dict) else None
            if isinstance(raw, dict):
                for source, master in raw.items():
                    if (len(self.entries) >= MAX_ENTRIES):
                        break
                    if (isinstance(source, str) and source
                            and isinstance(master, str) and master
                            and Path(source).is_absolute()
                            and Path(master).is_absolute()):
                        self.entries[source] = master
        except (OSError, ValueError, TypeError):
            pass

    @staticmethod
    def _key(source):
        return str(Path(source).expanduser().resolve())

    def get(self, source):
        """Return a valid explicit master or None; never silently retarget."""
        stored = self.entries.get(self._key(source))
        if stored is None:
            return None
        # Return the raw persisted target so compile-time validation can
        # explicitly reject missing or replaced masters.
        return Path(stored)

    def set(self, source, master):
        source = self._key(source)
        master = str(resolve_latex_master(source, "", master))
        new_entries = dict(self.entries)
        if source not in new_entries and len(new_entries) >= MAX_ENTRIES:
            raise ValueError("LaTeX master preference limit reached")
        new_entries[source] = master
        self._write(new_entries)
        self.entries = new_entries
        return Path(master)

    def clear(self, source):
        key = self._key(source)
        if key not in self.entries:
            return
        new_entries = dict(self.entries)
        new_entries.pop(key)
        self._write(new_entries)
        self.entries = new_entries

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = None
        try:
            # A unique temporary file and atomic replace guard against
            # interrupted writes and concurrent editor processes.
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", prefix=".latex-masters-",
                    suffix=".tmp", dir=self.path.parent, delete=False) as output:
                temp = Path(output.name)
                if os.name == "posix":
                    os.fchmod(output.fileno(), 0o600)
                json.dump({"masters": data}, output, ensure_ascii=False, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temp, self.path)
        finally:
            if temp is not None:
                temp.unlink(missing_ok=True)
