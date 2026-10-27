# ZEFM: system-wide overview (v35)

## What the original system comprises

1. **Desktop editor**: TPEditorX and Swing support, multilingual text, menus,
   LaTeX, dictionaries, word notes, local file actions.
2. **Browser/file manager**: ServPak/HTTP layer, document/file browsing,
   quick editing and a local socket bridge into the editor.
3. **Document formats**: HTML, XML/XSLT, Markdown, LaTeX and other filters.
4. **Email/document collection**: downloaded messages rendered into the browser,
   alongside file-specific word Notes and document annotations.
5. **Persistence**: original MyISAM `ZEFMdb`, not needed as a runtime dependency
   in the Python design.
6. **Language input**: original `Keymaps/*.keymap` files contain Java event
   keycodes mapped to decimal Unicode payloads; language dictionaries are a
   separate subsystem.

## Architecture for the Python version

```
Tk editor -- editor model -- filesystem (UTF-8 documents)
    |             |             \
    |             +-- language keymaps / dictionaries
    |             +-- Unicode tools / fonts / recent files
    +-- local quick-edit interface (NOT YET IMPLEMENTED)

Browser -- localhost HTTP server -- file index / HTML previews
    |                        |         (NOT YET IMPLEMENTED)
    +-- email message viewer + annotations / Notes
                          |
                  filesystem JSON/UTF-8 data
```

## Implemented vs planned

| Subsystem | Current status | Next milestone |
|---|---|---|
| Tk editor on Linux/macOS | functional, ongoing GUI testing | consistent keyboard/input bindings |
| Unicode and fonts | input helpers, font persistence | rendering/combining-mark tests |
| Keymaps | legacy sources preserved; parser in v35 | audit Java event handler, then optional input mode |
| Dictionaries | per-language JSON scaffolding | recover original database records |
| Notes | separate email-note storage foundation | recover original word-note records and define stable IDs |
| MyISAM tables | byte-size/CRC inventories only | restore with compatible MySQL/MariaDB instance for SQL/CSV export |
| Browser/file manager | routing interfaces only | localhost read-only directory listing + secure file preview |
| Editor/browser bridge | not implemented | protocol specification and safety checks |
| Email browser | not implemented | HTML viewing and file-based index |
| External tools / TeX | subprocess foundation | LuaLaTeX workflow and exit-code reporting |

## Original database inventory

Nine tables: `dictionaries`, `notes`, `annotations`, `main`, `texts`,
`xml`, `listings`, `sentMail`, `tmpZefm`. See `legacy_database_inventory.json`
for file lengths and CRCs. `.frm` holds legacy table structure,
`.MYD` the data and `.MYI` index files. They are **not parsed in v35**.
Import should be done on a working copy using a compatible server/version,
then verify record counts, character encoding, and representative records.
Never serve or publish this archive as part of the browser application.

## Notes and email

Do not discard the original `filename` + `word` notes semantics. Separate
message annotations by stable message identity, and keep notes outside the
original message/document bytes. The model must allow several occurrences
of a word in one document, without accidentally moving annotations after
text edits. Popups can be decided once records and browser context are ported.

## Keymap cautions

`English.keymap` is byte-for-byte identical to `Greek.keymap` in the upload;
this must not be assumed to be an English layout. Some payloads concatenate
multiple decimal code points without delimiters (e.g. `14881497`). v35 keeps
such payloads unmodified. Do not bind them into Tk until the original Java
parser and modifier semantics have been audited. On macOS use native system
input sources by default, avoiding duplicate key bindings.

## Deployment

Run from the unpacked ZIP on Slackware or macOS using Python 3 and Tkinter.
No MySQL, Java, or packaged fonts are required to run the current editor.
The legacy database ZIP is **not included** in this release, for privacy and size.

## Progress: v37

The editor now includes the source-guided `Annotate`/`QuickEditor` word-Notes
workflow. `zefm.storage.word_notes.WordNotes` replaces the MySQL `notes` table
with a local JSON store while preserving filename/word/link/data fields.
The browser, full dictionary migration, and mail-to-notes integration remain
pending. See NOTES_AND_DB_MIGRATION.md.

## v39 update

The **local** browser/file-manager foundation is implemented and can be opened
from the editor File menu or started as a standalone Python module. It offers
folder navigation, escaped text viewing, downloads, restricted browser Quick Edit,
and file-specific read-only Notes. It uses no SQL or Java runtime. The
browser-to-editor live tab bridge, email rendering/indexing and remaining
file-management operations are **not implemented**. See
`BROWSER_FILE_MANAGER.md` for the current architecture, risks and roadmap.
