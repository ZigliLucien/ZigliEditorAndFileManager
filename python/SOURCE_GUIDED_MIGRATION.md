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
