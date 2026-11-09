# Source-guided migration: v36

Original source: `ZEFMEXPORT.zip` → `EXPORT/ZEdit_ZEFM_src.jar` and
`EXPORT/NetsManager_ZEFM_src.jar` (supplied separately, left unchanged).

## Alphabet.java

Java constructs `Keymaps/<language>.keymap`; plain decimal key codes use
`Event.ALT_MASK`, `S` suffix uses Alt+Shift, and `C` suffix uses Alt+Meta.
The decoder emits one Unicode character for decimal values under seven
digits, or splits longer eight-digit values into two groups of four.
Python `legacy_keymaps.py` implements these rules and a Tk keysym adapter.
The practical GUI presently supports Alt and Alt+Shift. Alt+Meta entries
are understood by the parser but require platform-specific GUI testing.

## Annotate.java

Constructor accepts `(word, fileName)`, escapes the word for an HTML link,
checks the `notes` MySQL table for `(filename, word)`, then starts a
`QuickEditor(fileName, title, existing, word, link)`. Thus the original Notes
model is contextual to both file and word and is not merely email metadata.
Preserve `(filename, word, link, data)` when migrating old records. The
original editor-popup and web-annotation UI are not yet implemented in Python.

## Browser / email

`NetsManager_ZEFM_src.jar` includes `ZEFMServer.java`, `QuickEditor.java`,
`XmlMail.java`, `ZConnection.java`. v36 does not claim to port them. Keep
local browser editor communication separate from the desktop editor and
never reintroduce MySQL/FTP merely to mimic implementation details.

## Database

`ZEFMdb.zip` contains legacy MyISAM tables. v36 does not extract or bundle
private database records. The later migration requires validated MySQL or
MariaDB export and independent UTF-8 verification of dictionary and notes
records.

## v37 implementation

Python `zefm/storage/word_notes.py` and the **Notes** menu implement the
original `(filename, word)` record model with `link` and `data`, using atomic
local UTF-8 JSON instead of MySQL. See `NOTES_AND_DB_MIGRATION.md` for
current features and migration limitations. The `data` field stays plain text,
not arbitrary HTML executed in the browser. Export/import utilities accept
validated JSONL/JSON produced by a separately restored database.


## Browser Search String — new Python adaptation

The original ServPakDir source inventory includes `Search.java`. The Python
`zefm/server/content_search.py` now provides a **read-only adaptation**
of file-content search, reachable from the formerly disabled **Search String**
link in the styled browser listing. Exact legacy Search.java match rules,
database fields, and traversal behavior have **not** yet been reverified, so
this is not a claim of one-for-one Java parity.

The search form is scoped to the currently browsed directory (including
subdirectories), stays within `LocalFiles.root`, ignores symlinks and
dot-prefixed names, and returns file, line number and escaped text snippet.
It uses Unicode-aware case-insensitive matching by default, with an optional
Match case toggle. Search is limited to a depth of 8 subdirectories, 100
directories, 5,000 directory entries, 500 inspected files, 1 MiB per file,
12 MiB total, and 100 matching lines. Limits are reported rather than
misrepresented as complete searches. It never calls the shell or writes data.

The existing **Find filename** filter is separate, unchanged and still fast
within a directory; this new feature searches file *contents*. Regression
tests: `tests/test_content_search.py`. Interactive browser verification and
actual Java Search.java output comparison remain pending.


## New File — next ServPakDir FileOps migration increment

The browser listing's New File action is now wired to an independent,
filesystem-only `LocalFiles.create_file()` operation and a CSRF-protected
HTTP form. It creates an empty UTF-8-ready file exclusively, then offers
the existing Quick Edit workflow. Unlike unrestricted Java file actions,
this implementation confines writes to the selected browser root,
validates the filename, and never overwrites an existing entry or symlink.

This is explicitly an adaptation from the FileOps workflow requirements;
the exact implementation and UI semantics of original `FileOps.java`
have not been reverified against its source for this increment.


## XCommands.runC — copy files to a different directory

Source inspected: `NetsManager/XCommands.java`, the overload
`runC(String req, boolean move)`. In the original Java code, a Copy
operation accepts either a new filename in the current directory or a
destination path; when the destination names a directory, the source
filename is appended. The operation dispatches to
`ZEdit.Commands.copy(XCommands.actfile, targfile, move)`.

The Python adaptation now accepts a **destination directory relative to
the selected browsing root** and a separate new filename.
`LocalFiles.copy_file(relative, new_name, destination_directory=None)`
preserves the original two-argument same-directory interface. It
validates source and destination paths, refuses destination directory
symlinks, limits copies to 64 MiB, writes a temporary file in the
destination directory, and uses an exclusive hardlink to publish only
when the target name is unused. It never overwrites existing entries.
Cross-directory copy is available from the existing Copy file form.

Legacy Java allowed path conventions and a more permissive command
router. The Python version intentionally restricts destinations to
the chosen root, requires CSRF for POST requests, and preserves existing
return-state navigation. Notes remain attached to the source file;
this implementation does not duplicate database/Notes records. This
matches the absence of active annotation transfer in the inspected
`runC` block (the corresponding code was commented out), but is not
a claim of full Java FileOps parity.


## XCommands.runX — Delete as recoverable local Trash

Source inspected: `NetsManager/XCommands.java`, method `runX`. The
original Java implementation deleted a file directly with
`new File(XCommands.actfile).delete()` and attempted to delete associated
MySQL `annotations` records. This was a destructive one-way operation.

The Python implementation deliberately chooses a safer migration:
the browser's **Delete** operation first presents a confirmation page
and then moves a *regular file* to the hidden `.zefm-trash` directory
inside the chosen browsing root. Each item has a private per-item
directory, JSON original-location record and unchanged file contents.
`TrashManager` uses the same Notes-preserving `RenameManager.move`
logic as ordinary Move. Restore returns the file and its WordNotes to
their original location, refusing collisions and missing directories.

There is **no permanent-delete HTTP route**. The browser requires the
per-session CSRF token and an explicit confirmation value, rejects
symbolic-link files, protects open desktop-editor buffers through
`file_in_use`, and never overwrites a file during restoration.
The original Java behavior is thus identified precisely, with the
intentional safer departure documented rather than silently claimed
as strict parity.
