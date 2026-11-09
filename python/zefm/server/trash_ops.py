"""Recoverable, root-local Trash for the ServPakDir delete workflow.

Unlike Java XCommands.runX (permanent deletion), this implementation moves
regular files and their WordNotes to a hidden .zefm-trash folder. No file
is permanently deleted through the browser, and restoration never overwrites.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import secrets
import time

from .file_manager import BrowserError

_ID = re.compile(r"[0-9a-f]{32}\Z")
_MAX_RECORD_BYTES = 4096
_MAX_LISTED = 200


class TrashManager:
    def __init__(self, files, rename_manager):
        self.files = files
        self.renames = rename_manager

    def _root(self, create=False):
        root = self.files.root / ".zefm-trash"
        if create:
            try:
                root.mkdir(mode=0o700, exist_ok=True)
            except OSError as exc:
                raise BrowserError(f"Cannot create local Trash: {exc}", 403) from exc
        if root.is_symlink() or (root.exists() and not root.is_dir()):
            raise BrowserError("Unsafe local Trash directory", 403)
        return root

    def _record(self, item_id):
        if not isinstance(item_id, str) or not _ID.fullmatch(item_id):
            raise BrowserError("Invalid Trash item")
        item = self._root() / item_id
        if item.is_symlink() or not item.is_dir():
            raise BrowserError("Trash item unavailable", 404)
        record_path = item / "record.json"
        payload_dir = item / "file"
        if (record_path.is_symlink() or payload_dir.is_symlink()
                or not payload_dir.is_dir() or not record_path.is_file()):
            raise BrowserError("Invalid Trash item", 409)
        if record_path.stat().st_size > _MAX_RECORD_BYTES:
            raise BrowserError("Invalid Trash record", 409)
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
        except (UnicodeError, ValueError, OSError) as exc:
            raise BrowserError("Unreadable Trash record", 409) from exc
        original = record.get("original") if isinstance(record, dict) else None
        if (not isinstance(record, dict) or record.get("version") != 1 or not isinstance(original, str)
                or not isinstance(record.get("time"), (int, float))):
            raise BrowserError("Invalid Trash record", 409)
        # Relative to the user's chosen root, and never inside Trash.
        if (Path(original).is_absolute() or not Path(original).parts
                or Path(original).parts[0] == ".zefm-trash"):
            raise BrowserError("Invalid original filename", 409)
        original_path = self.files.resolve(original)
        name = original_path.name
        payload = payload_dir / name
        if not payload.is_file() or payload.is_symlink():
            raise BrowserError("Trashed file unavailable", 404)
        return record, payload, original_path, item

    def trash(self, relative):
        source = self.files.resolve(relative)
        if (not source.is_file() or (self.files.root / relative).is_symlink()
                or not Path(relative).parts
                or Path(relative).parts[0] == ".zefm-trash"):
            raise BrowserError("Only ordinary files can be moved to Trash", 404)
        root = self._root(create=True)
        item_id = secrets.token_hex(16)
        item = root / item_id
        owned = False
        try:
            item.mkdir(mode=0o700)
            owned = True
            destination = item / "file"
            destination.mkdir(mode=0o700)
            record = {"version": 1, "original": self.files.relative(source),
                      "time": time.time()}
            with (item / "record.json").open("x", encoding="utf-8") as out:
                json.dump(record, out, ensure_ascii=False)
                out.flush()
                os.fsync(out.fileno())
            moved, count = self.renames.move(relative, self.files.relative(destination))
            return item_id, count
        except FileExistsError as exc:
            raise BrowserError("Trash item collision; retry", 409) from exc
        finally:
            # If the move failed, remove only empty temporary directories.
            # If a file was moved despite a failure, retain it for recovery.
            if owned and item.is_dir():
                destination = item / "file"
                if destination.is_dir() and not any(destination.iterdir()):
                    destination.rmdir()
                    (item / "record.json").unlink(missing_ok=True)
                    item.rmdir()

    def restore(self, item_id):
        record, payload, original, item = self._record(item_id)
        parent = original.parent
        if not parent.is_dir():
            raise BrowserError("Original directory no longer exists", 409)
        if parent.is_symlink():
            raise BrowserError("Original directory is a symbolic link", 403)
        moved, count = self.renames.move(
            self.files.relative(payload), self.files.relative(parent))
        # The restore has already succeeded if a cleanup operation fails.
        # Retain any leftover metadata for manual inspection in that case.
        try:
            (item / "record.json").unlink()
            (item / "file").rmdir()
            item.rmdir()
        except OSError:
            pass
        return moved, count

    def list_items(self):
        root = self._root()
        if not root.exists():
            return []
        items = []
        try:
            candidates = root.iterdir()
            for candidate in candidates:
                if len(items) >= _MAX_LISTED:
                    break
                if not _ID.fullmatch(candidate.name):
                    continue
                try:
                    record, payload, original, folder = self._record(candidate.name)
                except BrowserError:
                    continue
                items.append({"id": candidate.name,
                              "original": record["original"],
                              "time": record["time"]})
        except OSError as exc:
            raise BrowserError("Cannot list local Trash", 403) from exc
        return sorted(items, key=lambda entry: entry["time"], reverse=True)
