"""Safe same-directory file rename, with Notes migration.

POSIX hard-link publishing avoids overwriting targets. The file remains
available under its original name until associated Notes are saved. Any
failure during the transaction attempts to remove the new name and restore
the original Notes. No directory-tree renaming or symlinks.
"""
import os
import threading

from .file_manager import BrowserError, _child_name
from ..storage.word_notes import WordNotes


class RenameManager:
    def __init__(self, files, notes_path=None, file_in_use=None):
        self.files = files
        self.notes_path = notes_path
        self.file_in_use = file_in_use
        self._lock = threading.RLock()

    def rename(self, relative, new_name):
        """Rename a regular file within its existing directory."""
        return self._relocate(relative, new_name=new_name)

    def move(self, relative, destination_directory):
        """Move a file into another directory within this root, without overwrites."""
        return self._relocate(relative, destination_directory=destination_directory)

    def _relocate(self, relative, new_name=None, destination_directory=None):
        with self._lock:
            source = self.files.resolve(relative)
            if not source.is_file() or (self.files.root / relative).is_symlink():
                raise BrowserError("Only regular files may be renamed", 404)
            if destination_directory is None:
                destination = source.parent / _child_name(new_name)
            else:
                target_parent = self.files.resolve(destination_directory)
                if not target_parent.is_dir():
                    raise BrowserError("Destination directory not found", 404)
                if (self.files.root / destination_directory).is_symlink():
                    raise BrowserError("Destination cannot be a symlink", 403)
                destination = target_parent / source.name
            if source == destination:
                raise BrowserError("Choose a different directory or name", 409)
            if self.file_in_use is not None and self.file_in_use(source):
                raise BrowserError("File is open in the desktop editor; close its tab before renaming", 409)

            try:
                store = WordNotes(self.notes_path)
            except (OSError, ValueError) as exc:
                raise BrowserError(f"Cannot load Notes; rename cancelled: {exc}", 500) from exc

            source_key = str(source)
            target_key = str(destination)
            entries = store.for_file(source_key)
            if store.for_file(target_key):
                raise BrowserError("Notes already exist under the requested name", 409)
            changed = dict(store._notes)
            for record in entries:
                changed.pop((source_key, record["word"]))
                replacement = {**record, "filename": target_key}
                changed[(target_key, record["word"])] = replacement

            linked = False
            notes_changed = False
            try:
                # This fails with FileExistsError even if the target is a symlink.
                # The source remains intact until the notes update succeeds.
                os.link(source, destination, follow_symlinks=False)
                linked = True
                if entries:
                    store._write(changed)
                    notes_changed = True
                os.unlink(source)
            except FileExistsError as exc:
                raise BrowserError("Destination already exists; nothing was renamed", 409) from exc
            except (OSError, ValueError) as exc:
                # Best-effort rollback; never touch the original file contents.
                if linked:
                    try:
                        if notes_changed:
                            undo = WordNotes(self.notes_path)
                            restore = dict(undo._notes)
                            for record in entries:
                                restore.pop((target_key, record["word"]), None)
                                restore[(source_key, record["word"])] = record
                            undo._write(restore)
                        destination.unlink(missing_ok=True)
                    except (OSError, ValueError) as rollback:
                        raise BrowserError(
                            f"Rename failed; manual recovery may be necessary: {rollback}", 500
                        ) from exc
                raise BrowserError(f"Rename cancelled: {exc}", 500) from exc
            return destination, len(entries)
