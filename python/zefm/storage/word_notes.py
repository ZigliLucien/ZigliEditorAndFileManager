"""Portable, local replacement for ZEFM's MySQL `notes` table.

Keys retain the original (filename, word) identity and fields are
(filename, word, link, data). The data file contains *annotations only*, never
edits to the underlying document. All text is UTF-8.
"""

import json
import os
import tempfile
from pathlib import Path
from unicodedata import category


def default_notes_path():
    """Respect XDG storage on Linux and keep annotations out of source trees."""
    root = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
    return root.expanduser() / "zefm" / "word_notes.json"


def word_at(text, position, selection=None):
    """Return selected text or a Unicode word around the cursor.

    Letter, mark, number, and connector punctuation characters comprise a
    word; combining marks stay attached to Hebrew/Yiddish and French letters.
    At a word boundary, use the character immediately before the cursor.
    """
    if selection is not None:
        start, end = selection
        if not (0 <= start <= end <= len(text)):
            raise ValueError("Invalid selection")
        return text[start:end].strip()
    if not 0 <= position <= len(text):
        raise ValueError("Cursor is outside the buffer")

    def is_word(ch):
        return category(ch)[0] in ("L", "M", "N") or category(ch) == "Pc"

    index = position
    if index >= len(text) or not is_word(text[index]):
        if index == 0 or not is_word(text[index - 1]):
            return ""
        index -= 1
    start = index
    end = index + 1
    while start > 0 and is_word(text[start - 1]):
        start -= 1
    while end < len(text) and is_word(text[end]):
        end += 1
    return text[start:end]


class WordNotes:
    """Per-file/per-word note CRUD with atomic persistence.

    Invalid existing files raise ValueError instead of being silently replaced;
    this prevents destructive edits when data is corrupt or a future format
    version is encountered.
    """

    def __init__(self, path=None):
        self.path = Path(path).expanduser() if path is not None else default_notes_path()
        self._notes = {}
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, ValueError) as exc:
                raise ValueError(f"Cannot read notes at {self.path}: {exc}") from exc
            if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("notes"), list):
                raise ValueError(f"Unsupported notes data format: {self.path}")
            for entry in data["notes"]:
                record = self._validate_record(entry)
                key = (record["filename"], record["word"])
                if key in self._notes:
                    raise ValueError(f"Duplicate note key in {self.path}: {key}")
                self._notes[key] = record

    @staticmethod
    def _validate_record(record):
        if not isinstance(record, dict):
            raise ValueError("A note must be an object")
        for name in ("filename", "word", "link", "data"):
            if not isinstance(record.get(name), str):
                raise ValueError(f"Note field {name} must be text")
        if not record["filename"].strip() or not record["word"].strip():
            raise ValueError("A note needs a filename and a word")
        return {name: record[name] for name in ("filename", "word", "link", "data")}

    def get(self, filename, word):
        record = self._notes.get((filename, word))
        return record.copy() if record is not None else None

    def for_file(self, filename):
        return [entry.copy() for (name, _), entry in sorted(self._notes.items()) if name == filename]

    def __len__(self):
        return len(self._notes)

    def _write(self, updated):
        data = {"version": 1, "notes": sorted(updated.values(), key=lambda r: (r["filename"], r["word"]))}
        directory = self.path.parent
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix=".notes-",
                                             suffix=".tmp", dir=directory, delete=False) as out:
                temporary = Path(out.name)
                os.chmod(temporary, 0o600)
                json.dump(data, out, ensure_ascii=False, indent=2)
                out.write("\n")
                out.flush()
                os.fsync(out.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        self._notes = updated

    def put(self, filename, word, data, link=""):
        record = self._validate_record({"filename": filename, "word": word,
                                        "link": link, "data": data})
        updated = dict(self._notes)
        updated[(filename, word)] = record
        self._write(updated)

    def delete(self, filename, word):
        key = (filename, word)
        if key not in self._notes:
            return False
        updated = dict(self._notes)
        del updated[key]
        self._write(updated)
        return True

    def import_records(self, records, replace=False):
        """Import validated legacy records, leaving existing keys intact by default.

        Applies the whole batch in one atomic write; invalid data leaves the
        existing store untouched. `replace=True` updates conflicting keys.
        """
        updated = dict(self._notes)
        imported = skipped = 0
        for source in records:
            record = self._validate_record(source)
            key = (record["filename"], record["word"])
            if key in updated and not replace:
                skipped += 1
                continue
            updated[key] = record
            imported += 1
        if imported:
            self._write(updated)
        return imported, skipped
