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


## Browser Quick Edit → TPEditor save notification

The old Java distribution couples `NetsManager/ZConnection.java` request
handling to `NetsManager/QuickEditor.java` and
`ZEdit/TPEditorX.java`. The Python port deliberately separates the
HTTP server thread from Tk UI operations: the existing
`/open-editor` route queues a filename and Tk processes it on its
main thread.

The same architecture now handles successful browser Quick Edit saves.
`BrowserServer(..., file_saved=callback)` only invokes its optional
callback after `LocalFiles.save_text` succeeds, with the absolute
root-confined file path. The desktop editor supplies a
`Queue.put` callback; its regular 150 ms UI-thread queue drain
checks whether the active tab owns the saved file and immediately
runs the already-existing SHA-256 external-change detector. This
raises the nonmodal Reload/Dismiss notice without replacing an
editor buffer. Inactive tabs retain the existing notification on
selection. A rejected browser save sends no signal. Standalone
`--mode files` works without Tk or a callback.

This is a new, safer integration contract; it does **not** pretend to
reproduce the original Java threading or Swing internals.


## Per-buffer browser revision awareness (Tk synchronization)

The existing Python browser/editor callback now examines all open
TPEditor buffers for a saved file rather than notifying only the
selected tab. The HTTP side still sends *only a path* into a queue,
and the Tk main thread performs digest comparisons. External-change
revision markers are distinct from the editor's ordinary unsaved-state
marker and do not modify the buffer or its Undo history.

The implementation extends the previous v78 bridge without reviving
Java's shared mutable Swing/socket state. The existing digest baseline
and revision-specific dismissal logic remain authoritative.


## TPEditor desktop usability — Save confirmation and Recent Files popup

The Python Tk editor now reserves a dedicated bottom status-field
for the last successful save of the active buffer. Unlike a transient
message appended to cursor/mode information, `✓ Saved: filename`
remains visible until that buffer changes, at which point the status
becomes `● Unsaved changes`. The indication is per-buffer; unsuccessful
or cancelled saves never claim success. It supplements the tab `*`
(unsaved) and `↻` (external revision) markers.

Editor text right-click now exposes a compact Recent Files popup.
It reuses the File menu's bounded UTF-8 recent-file model and the
same file-open command, preserving recent-file deduplication and
existing-buffer navigation. This is a Python usability adaptation,
not a revival of the Java XML/XSLT browser pipeline.


## Vim-style NORMAL-mode search prompt layout

The Tk editor's `_vim_key` handler already implemented `/`, `?`,
`:` and `n`. The regression was in Tk geometry management, not
pattern parsing: `_vim_prompt` inserted its bottom-entry after the
already-packed expanding Notebook, so the entry was obscured. The
prompt is now inserted before the Notebook, retaining the reserved
permanent Save-status row and existing normal/insert mode controls.


## XCommands.runQ — QuickEditor from TPEditor

The original Java `NetsManager/XCommands.java` implements
`runQ(String req)` by delegating to `runE(req, true)`, which opens
`NetsManager.QuickEditor(filepath)`. The existing Python browser
`/edit` route already handled small UTF-8 Quick Edit files, but
TPEditor previously offered only a direct RTL browser command.

The File menu now includes **Quick Edit Current File in Browser...**
for standard left-to-right text. Both that command and the preexisting
**Edit Current File RTL in Browser...** share
`Window.edit_current_file_in_browser(direction)`. It requires the
current buffer to have been saved and to have no pending unsaved
changes; checks the on-disk file is UTF-8 and at most 1 MiB; reuses
an existing loopback BrowserServer if it contains the file; and uses
the bounded `/edit` route, with the correct root-relative Unicode
path and `dir=ltr` or `dir=rtl`.

The browser's revision-checked Save continues to notify Tk through
the queue-backed `file_saved` callback. No direct HTTP-to-Tk widget
calls or automatic buffer replacement occur. Files outside a running
browser root retain the pre-existing behavior of switching to a
browser rooted at the selected file's directory when the user
explicitly invokes the desktop command.

This completes the *desktop launch* part of the Java QuickEditor
workflow without porting Swing or XML/XSLT code verbatim. Java's
QuickEditor UI and database features are not claimed to be fully
equivalent to the Python HTML Quick Edit page.


## v85 — combined Move + Rename from XCommands.runM

The source-guided audit of `NetsManager/XCommands.java` confirms
that `runM` delegates to `runC(req, true)`. The Java form accepts
either a replacement filename within the current directory or a path
to another directory with an optional replacement filename. Until
now Python Move required a destination directory and retained the
original basename; Rename was a separate operation.

The Python `RenameManager.move(relative, destination_directory,
new_name=None)` now supports an optional replacement name as part
of the same Notes-aware, no-clobber transaction. The original
two-argument API remains valid (including Trash/Restore). A blank
replacement name also preserves the current filename. The browser
Move form defaults its destination to the source directory and
offers an optional **New filename** field.

The implementation uses the existing guarded hardlink publish,
atomic WordNotes rewrite, and source unlink/rollback logic:
no overwrite, no directory traversal, no symbolic-link destination,
no moving files open in TPEditor. It preserves the root boundary
and browser Back listing state. It deliberately does not claim
support for moving whole directories or Java's unrestricted
filesystem destinations.


## v86 — XCommands.runT: selected archive member extraction

Source: `NetsManager/XCommands.java`, `runT(String req)`.
The Java command could display a member of a ZIP/TAR archive or
extract it under an implicit `Xtrax` path. The Python port previously
offered only a bounded, read-only ZIP/JAR/TAR member listing.

The new **Extract…** action is opt-in on individual ordinary-file
members in the browser archive preview. It opens a separate confirmation
form, whose destination is an existing directory relative to the
selected browsing root and whose filename can be changed. Paths
inside the archive are **not** recreated: members are extracted as
individual flat files in the chosen directory. This avoids an
untrusted archive silently creating directories or writing outside
the root.

`server/archive_extract.py` supports ZIP/JAR/WAR/EAR and the
existing TAR formats (.tar, .tgz, .tar.gz, .tbz, .tar.bz2,
.txz, .tar.xz). It rejects unsafe member names, duplicate names,
symbolic links, hard links, directory entries, symlink destinations,
absolute/traversal destination paths, and extraction into ZEFM
internal Trash. The archive itself must be 128 MiB or smaller and
contain at most 5,000 members; one selected member may expand to
at most 64 MiB. Extraction is streaming and bounded, publishes only
via an exclusive hardlink from a private temporary file, and never
overwrites existing paths. Extracted files have mode 0600 and
are never executed. The form requires the browser's CSRF token.
Nothing is extracted just by viewing an archive.

This replaces the permissive implicit `Xtrax` destination from
Java with an explicit bounded filesystem transaction. It is
intentionally not a full-archive extraction feature.
