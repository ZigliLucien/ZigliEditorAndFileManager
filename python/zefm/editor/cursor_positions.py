"""Persistent insertion positions for local ZEFM editor buffers.

Separate from Recent Files ordering; storing a cursor must never reorder
which document opens at the next launch.
"""
import json
import os
from pathlib import Path
import re
import tempfile

_INDEX = re.compile(r"^[1-9][0-9]{0,8}\.[0-9]{1,9}$")
MAX_POSITIONS = 100


class CursorPositions:
    def __init__(self, path=None):
        self.path = (Path(path).expanduser() if path is not None else
                     Path.home() / ".config" / "zefm" / "cursor_positions.json")
        self.positions = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("positions"), dict):
                for key, position in data["positions"].items():
                    if (isinstance(key, str) and key and isinstance(position, str)
                            and _INDEX.fullmatch(position)):
                        self.positions[key] = position
                        if len(self.positions) == MAX_POSITIONS:
                            break
        except (OSError, UnicodeError, ValueError, TypeError):
            pass

    @staticmethod
    def _key(filename):
        return str(Path(filename).expanduser().resolve())

    def get(self, filename):
        return self.positions.get(self._key(filename))

    def record(self, filename, index):
        if not isinstance(index, str) or not _INDEX.fullmatch(index):
            raise ValueError("Invalid Tk text insertion index")
        key = self._key(filename)
        self.positions.pop(key, None)
        self.positions[key] = index
        while len(self.positions) > MAX_POSITIONS:
            self.positions.pop(next(iter(self.positions)))
        self._write()

    def _write(self):
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=self.path.parent,
                    prefix=".zefm-cursor-", suffix=".tmp", delete=False) as out:
                temporary = Path(out.name)
                if os.name == "posix":
                    os.fchmod(out.fileno(), 0o600)
                json.dump({"positions": self.positions}, out, ensure_ascii=False)
                out.write("\n")
                out.flush()
                os.fsync(out.fileno())
            os.replace(temporary, self.path)
        except OSError:
            # Read-only home directory must not prevent editing.
            pass
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass
