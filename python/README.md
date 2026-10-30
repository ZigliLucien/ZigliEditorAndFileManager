# ZEFM Python port — v6 desktop preview

On Alpine: `apk add python3 python3-tkinter unzip`

From the extracted directory: `python3 -m zefm.editor.gui.tk_editor`

Implemented preview: multiple tabbed buffers, UTF-8 open/save/save as,
clipboard, native Tk undo/redo, find/find next, replace-all (literal,
case-sensitive), revert, close buffer, dirty tabs, cursor status. Some
legacy menu commands remain explicit placeholders. This is not a complete
port of TPEditorX. See PROCESS_MAP.md and PORT_STATUS.md.

Tests: `python3 -m unittest discover -s tests -v`
\nV10: Query Replace offers clickable buttons if popup key focus is unreliable. Basic .properties import via zefm.config_import.import_properties(source,target); review unusual Java escaping manually.\n
V11 hybrid Vim search:
- Ordinary typing remains the default. Press Esc in the text widget for NORMAL command mode.
- In NORMAL mode: / forward regex, ? backward regex, n repeat, N opposite, : substitution, i resumes typing.
- :s/pat/repl/ current line; :%s/pat/repl/g whole buffer; c confirms with y/n/!/q; i ignores case.
- Regex syntax is Python re, not full Vim regex syntax. Capture replacements use \\1, \\2.
- Query-replace popup from earlier versions remains available. GUI behavior requires live Alpine verification.

V13 maintenance: fixed missing pathlib.Path import (used for tab titles and Revert);
added :noh / :nohlsearch to clear search highlighting; added regression tests for
regex capture replacements, case-insensitive confirmation and line-scoped substitution.
Ordinary typing remains default. Existing search/replace/quit behavior preserved.

V14 configuration: see config/README.md. From project root, use
`python3 -m zefm.config_import old.properties config/imported.json`.
Edit config/keyboard.json only to override known menu command shortcuts.
The original Java-derived mapping remains default; v13 search and replace
are not intentionally modified. GUI shortcut override requires app restart.

V15 buffer modes: config/modes.json is the validated UTF-8 registry. Detection: manual override > exact filename > extension > shebang/XML declaration > plain text. Each open tab stores its own mode; use Mode > Select Buffer Mode... to override without renaming. Mode shown in status line. This version supplies metadata and indentation preferences only; highlighting, automatic indentation, Run, validation, and preview are NOT yet attached. Natural-language dictionaries remain separate.

V16: Tab inserts indentation according to the current buffer mode (spaces or a
literal tab); an active selection retains Tk's native Tab behavior. Mode >
Validate Buffer checks JSON with line/column diagnostics. No external command
execution or syntax highlighting is claimed. Ordinary typing and Vim search
remain unchanged.


V17 JSON structural tools (Mode menu):
- Show jq Path at Cursor / Copy jq Path: uses source-offset structural parsing.
- Validate JSON; Run jq on Buffer: prompts for a filter and passes unsaved buffer
  through subprocess argv with stdin, captured output and 10-second timeout.
  jq must be installed separately (Alpine: apk add jq). Results open in a new tab.
- JSON paths use jq notation; Python json decoding is used for strict validation.
- Mode-specific Tab insertion is now actually wired to Tk.
- These features have headless tests; GUI needs live Alpine verification.

V18:
- JSON cursor path now includes object key spans and whitespace between key and value.
- Native Python JSON value-at-path and formatting use the current unsaved buffer.
  The path evaluator is intentionally limited to simple paths, not full jq.
- External jq remains available as an explicitly labeled optional command.
- Run > Trace is presented as Debug Python (original Ctrl+O retained). It launches
  interactive pdb in xterm for a SAVED Python-mode buffer. Alpine: apk add xterm.
  This debugger requires a terminal, but not Java or an external debug library.
- 41 automated tests pass; GUI changes require Alpine verification.

V19: JSON parent/next sibling/previous sibling navigation in Mode menu, jq path displayed automatically in JSON status line. No extra utilities required. Source offset indexing is headless-testable. GUI requires Alpine verification.

V21: File dialogs start in the configured home directory (~ by default). File > Set Working Directory... changes the dialog directory without changing process cwd. With remember_last_directory=true, successfully opened/saved files update the dialog directory for this session. Settings live in config/zefm.json; last directory is not persisted between sessions.


V23: successful File > Save / Save As now shows persistent `Saved: filename`
in the status bar until the next edit. The tab's leading `*` disappears
on successful save and returns after modification. A failed/cancelled save
does not report success. Status feedback is maintained separately per tab.

### Retired legacy functionality (v24)
The old TXML, HXML, JXML, and CLSV modes are intentionally excluded. The Utils menu operations Remote Save, Remote Edit, Upload, and FTP are also excluded from the Python port. Local file operations, ordinary XML and HTML modes, and the planned local browser/editor integration remain in scope.


## V25 Unicode and fonts

Unicode menu: enter a Unicode code point or browse a bounded range (double-click
a named character to insert). Fonts menu: choose from installed Tk/X11 families,
set point size, toggle bold or italic. All tabs share the editor font; no font
files are bundled. Glyph availability depends on fonts installed on the host.
Tk GUI needs live verification on Slackware.


V26: Unicode > Search Unicode Names... searches Unicode character names and inserts selected characters. Results limited to 200.

### Version 27: Unicode and font usability

- Fonts > Choose Font Family offers case-insensitive filtering and a live
  preview of Latin, Greek, mathematical symbols, and Hebrew/Yiddish.
- Apply commits the selection; Cancel leaves the current font unchanged.
- Unicode > Common Symbols provides quick insertion buttons for common
  mathematical, Greek, and typographic characters.
- Font availability and glyph coverage depend on the Linux font installation.
- GUI interactions need testing on Slackware; automated headless tests cover
  the existing non-GUI components.

### Version 28: faster Unicode browsing and font preview

- Unicode > Browse Common Blocks provides direct browsing of Hebrew/Yiddish, Greek,
  mathematical operators, arrows, and Latin-1 without manually typing a range.
- Font chooser previews **size, bold, italic, and family together** before applying.
- Cancel leaves the editor unchanged, and the applied font settings affect all tabs.
- This build does not include any font files or change Unicode input methods.

### Version 29: Recent Files and Unicode character inspection

- **File → Recent Files** remembers up to 12 opened or saved file paths across
  restarts, in `~/.config/zefm/recent_files.json`. The list is most-recent-first,
  deduplicated, and can be cleared. Existing buffers are reselected instead
  of duplicated. Missing files can be removed by confirmation.
- **Unicode → Describe Character at Cursor** displays the Unicode code point,
  official Unicode name, and (where applicable) its combining class in the
  status line. This is particularly helpful with Yiddish combining marks.
- The font preview was enlarged slightly, with more Yiddish marks to check
  installed font coverage. This does not install fonts or configure input methods.
- The GUI changes require live verification on Slackware.


## v30: Fonts, Unicode, Notes decision

- Font selections persist at `~/.config/zefm/font.json`. The chooser, direct size
  setting, bold and italic toggle all save settings. Corrupt/missing preferences
  restore default font; no font files are bundled. Font availability depends on
  the local Tk/X11 installation.
- `Unicode → Describe Character Sequence at Cursor` identifies the base code point
  and contiguous Unicode combining marks (helpful for Hebrew/Yiddish niqqud and
  other combining accents). This is a codepoint sequence inspector, **not** a full
  grapheme-cluster segmenter; ZWJ emoji and noncombining modifiers are excluded.
- **Notes**: preserve the existing Java/browser email annotation semantics until
  the email download/render pipeline is audited. Do not yet reimplement the generic
  per-word editor popup, nor erase historic notes. Future path: email-bound
  annotations stored alongside the downloaded-message metadata, with stable
  message IDs and safe HTML display. No Notes menu is claimed in this release.

### v31: macOS testing and email notes foundation

- Keyboard shortcuts now load from the package's `config/keyboard.json` even when
  ZEFM is launched from `~` or another working directory.
- On macOS, when no font preference file exists, Menlo is the initial family;
  existing font preferences remain authoritative.
- `zefm.storage.email_notes.EmailNotes` provides UTF-8, atomic, local notes
  indexed by email Message-ID. This is a **storage foundation only**: browser
  integration and annotation popup are not implemented yet.

**Mac launch** (from the extracted project root, with Python 3 and Tkinter):

```sh
python3 -m tkinter
python3 -m unittest discover -s tests -v
python3 -m zefm.editor.gui.tk_editor
```

The macOS window manager may render menus at the top of the screen; test
Command+O/S alongside the menu accelerators.

### v32 macOS clipboard correction
On macOS, use Tk Aqua native Command+C/X/V/Z bindings for Copy/Cut/Paste/Undo/Redo; do not register duplicate app-level global shortcuts. File commands such as Command+S/O remain explicitly bound. Linux Ctrl shortcuts are unchanged.


V33: Escape toggles NORMAL search-command mode and INSERT editing mode.
The status line displays the current mode. `i` remains an optional way to
return to editing. Escape inside an active search prompt cancels the prompt
first; Escape in the editor then switches modes.


## v34 multilingual editing
**Language → System Default / French / Yiddish** sets a ZEFM dictionary language for the current buffer; it does **not** switch macOS/Linux keyboard input sources. **Language → Expand Dictionary Shortcut at Cursor** explicitly expands the longest matching shortcut immediately before the cursor. The illustrative French dictionary contains `coeur` → `cœur`; Yiddish mappings remain unpopulated pending the original dictionary. System input methods remain available and are not intercepted. See `dictionaries/README.md`.


## v35 migration overview

See `SYSTEM_OVERVIEW.md` for the whole-system architecture, the legacy database
metadata inventory, and the original keymap reader. No MyISAM extraction yet.

## v36: original Alt keymaps (source-guided)

Use **Language → Alt Keymaps (per buffer)** to select French, Yiddish, Greek,
Polish, Russian, or Assamese; **System keyboard (off)** restores your usual
operating-system input method. Selection is per tab and is off by default.
In INSERT mode, use **Alt + letter** and **Alt+Shift + letter** following the
original Java `Alphabet.java` mapping; press ESC to enter/leave command mode.
For example, French Alt+E inserts `é`, Yiddish Alt+B inserts `ב`, and
Yiddish Alt+Shift+I inserts `אי`. ZEFM does not change the operating-system
keyboard layout or dictionary language when switching its Alt keymap.

On macOS, Option/Alt may be handled by the operating system as a dead key or
compose sequence; the editor-local mapper is experimental there. Use the
native system input source instead if chords do not reach Tk as Alt events.
On X11, window-manager Alt shortcuts may take precedence. The original
`English.keymap` duplicates Greek and is intentionally hidden from the menu.

Legacy keymap payloads are interpreted according to source in
`ZEdit_ZEFM_src.jar/Alphabet.java`: values shorter than seven digits are a
single decimal Unicode point; eight-digit values are pairs of four-digit
Unicode values. Source archives are reference material, not included in this
binary-independent Python distribution.

### Version 37: Original word-attached Notes

Notes > Annotate Selected Word / Word at Cursor... saves an annotation for the
word in a **saved** file without modifying its text. Notes > Notes for Current
File... lists and reopens the annotations. Supports Unicode combining marks.
The local private store is under ~/.local/share/zefm/word_notes.json by default
(or `$XDG_DATA_HOME`).

For migration from the original MyISAM tables, see
`NOTES_AND_DB_MIGRATION.md`. A separately restored database can be exported
once with optional PyMySQL; the final ZEFM editor does not require SQL.
Historical database records are **not** packaged into this ZIP.

### v38 — keymap reference and lexical dictionary migration

**Language → Show Keymap / Keyboard Reference...** displays the original
French/Yiddish/Greek/etc Alt mappings. Filter by key, Unicode character,
or name; insert a selected character, copy the table, or activate the keymap.
The installed original `.keymap` files remain unchanged. The system keyboard
is unaffected, and the custom map stays off unless enabled for a buffer.

**Language → Look Up Word in Dictionary...** reads original lexical dictionary
entries after import; this is different from the existing dictionary-shortcut
expansion command. Dictionary records are imported from a verified JSONL
SQL export into private, per-language UTF-8 JSONL files. See
`DICTIONARY_MIGRATION.md` for commands and limitations. The original raw
MyISAM files have not been restored or converted. The browser/quick-editor
subsystem remains the next major development stage.

## v39: Local browser / file manager (source-guided by ServPakDir)

**File → Open Local File Manager in Browser...** starts a loopback-only HTTP
browser rooted at your chosen working directory. It supports directory listings,
UTF-8 text previews, downloads, up-to-1 MiB UTF-8 Quick Edit with explicit
save/conflict detection, and read-only browser views of the word-attached Notes
already stored by the desktop editor. Standalone use:

```sh
python3 -m zefm.server.http --root "$HOME"
```

No SQL, external command handlers, FTP, or remote editing is exposed. The
browser does **not** yet open a desktop editor tab or synchronize modified
buffers after Quick Edit. See `BROWSER_FILE_MANAGER.md` for use, safety scope,
and precise source references.

### v40 — Notes save controls (desktop and browser)

- Desktop Notes popup: Save Note toolbar at the top so it remains visible with
  large fonts or a small display; Ctrl+S / Command+S saves the note.
- Confirm before discarding unsaved note edits; main editor shows saved status.
- Browser Notes: Add Note and Edit note now open editable UTF-8 forms, with a
  visible Save Note button and confirmation page. Browser and editor use the
  same Notes store. Stale note edits are rejected rather than overwritten.
- Test: `python3 -m unittest discover -s tests -v`.


## v44: local email archive browser

The File menu now includes **Open Local Email Archive in Browser...**.
It reads existing Maildir folders via Python's email parser (read-only), and
shows recent messages as escaped text with no active HTML or attachments.
Annotations for a message can be added through **Notes for this message**
and are stored separately from the original email using WordNotes.
The original getmail/DavMail and Python-generated HTML index are unchanged.
See [MAIL_ARCHIVE.md](MAIL_ARCHIVE.md) for local account configuration and
the standalone browser command. Never commit real mail data.

## v45: Yiddish / Hebrew RTL editing

Choosing Yiddish in either the Language selector or the per-buffer Alt keymaps
right-aligns the Tk editor's paragraphs. This is only **alignment**: Tk 8.6/X11
cannot guarantee correct Unicode bidirectional visual order or RTL cursor motion.

For accurate RTL text entry and mixed Hebrew/Latin/numeric layout, save the file
and choose **File → Edit Current File RTL in Browser...**. The local browser
uses its native `dir="rtl"` textarea; Save writes logical-order UTF-8 text
with the usual digest and CSRF safeguards. External-change notification from
v43 then lets you Reload from disk in the Tk editor. The browser uses the
system's input method or paste, not ZEFM's Tk-only Alt keymaps.

The normal file-browser listing also offers **RTL edit**. See
[BROWSER_FILE_MANAGER.md](BROWSER_FILE_MANAGER.md) for details.
