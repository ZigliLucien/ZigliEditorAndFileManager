# ZEFM construction: one program per process

## Overall flow

```text
Desktop editor -> editor.model -> editor.files -> document XML/JSON
       |               |
       +-> editor.dictionary (language files)
       +-> core.commands -> external executable (optional)
       +-> document.transform -> XSLT adapter (pending)
Browser/HTTP -> server.http -> server.routes -> document/store/search (pending)
                         |
                         +-> core.commands (only when authorized)
```

## Program contracts

| Process | Python program | Inputs -> outputs | Java reference | State |
|---|---|---|---|---|
| 01 Configuration | `zefm/config.py` | JSON file -> validated settings | scattered configuration | implemented foundation |
| 02 External execution | `zefm/core/commands.py` | argv, timeout -> return code/stdout/stderr | Commands, XCommands, TPEditorX.runIt | implemented foundation |
| 03 Editor buffer | `zefm/editor/model.py` | Unicode text and edits -> buffer state | Buffer, TPEditorX | implemented foundation |
| 04 File load/save | `zefm/editor/files.py` | path, text -> UTF-8 text/file | TPEditorX.callPage/savePage | implemented foundation |
| 05 Language dictionaries | `zefm/editor/dictionary.py` | one UTF-8 JSON per language -> shortcut expansions | Alphabet, Modes, QuickEditor | implemented foundation; mappings to extract |
| 06 Desktop editor UI | `zefm/editor/ui.py` | events -> editor model | TPEditorX, ZEditor | interface only; GUI toolkit undecided |
| 07 Document interchange | `zefm/document/interchange.py` | XML <-> JSON-preserving representation | Query, Traxit | implemented basic lossless tree representation |
| 08 XML transformations | `zefm/document/transform.py` | XML + stylesheet -> XML/HTML | Traxit | interface only; select engine after stylesheet audit |
| 09 HTTP transport | `zefm/server/http.py` | request -> response | ZEFMServer, ZConnection | interface only; audit routes first |
| 10 Request routing | `zefm/server/routes.py` | route + request -> operation | ZConnection | interface only; audit routes first |
| 11 Server actions | `zefm/server/actions.py` | authorized operation -> result | XCommands | interface only; audit command semantics |
| 12 Persistence/search | `zefm/storage/store.py` | document ID/query -> content/results | Searcher, MakeRootList | interface only; audit data format |
| 13 Import/export | `zefm/document/import_export.py` | input -> converted document | ContentSplitter, XmlMail etc. | interface only; audit formats |
| 14 Network clients | `zefm/network/clients.py` | remote request -> response | FTP/mail/remote classes | interface only; separate protocols later |
| 15 Application bootstrap | `zefm/main.py` | config -> chosen mode | ZEditor, ZEFMServer | placeholder |

An *interface only* program deliberately raises `NotImplementedError`: no claim of parity is made.

## Migration order

1. Extract precise Java method inventories and event/route tables.
2. Implement core configuration, process execution and Unicode file/buffer handling.
3. Extract and transcribe alphabets, dictionaries, modes and shortcuts; test against Java fixtures.
4. Implement editor GUI by binding actions to small services; preserve menus and key bindings.
5. Audit XML stylesheets and document formats; keep XML where semantic markup/XSLT is needed and use JSON for configuration and internal interchange.
6. Reconstruct HTTP request parsing, routes and XCommands with security review.
7. Port persistence, search, networking, printing and ancillary tools separately.
8. Compare outputs and representative workflows against the Java application.

## Design rules

- Each module has one clear responsibility and can be tested without opening a GUI.
- UTF-8 is explicit at all disk and subprocess boundaries.
- Command execution uses argument arrays, never implicit shell evaluation.
- The server must never expose a generic unrestricted command runner.
- Preserve XML mixed content, namespaces, attributes and order when converting to JSON; the chosen tree representation is structural rather than a simplified business-object mapping.
- Keep original Java sources as read-only reference. Mark features complete only after parity tests.


## Source audit: editor master and Buffer

TPEditorX.java is the editor master (4,989 lines). Buffer.java is a
46-line subclass of TPEditorX which creates a frame, selects a file and
calls callPage; it is not the underlying Emacs-derived text store.
TPEditorX uses Swing writer.copy(), writer.paste(), writer.cut() in macro
replay (around lines 1056-1066). The File/Edit/Run label and accelerator
arrays (around lines 100-120 and 390-410) are now represented in
zefm/editor/command_registry.py. Clipboard bindings are user-confirmed.
This is a registry foundation, not completed GUI parity.


## Source audit 2: editor commands and selection

Verified in `TPEditorX.java`: `writer` is a `JTextPane` (line ~146),
`UndoManager` appears near line ~237, File/Edit/Run accelerator arrays
appear near lines ~393-406, and macro replay explicitly invokes
`writer.paste()`, `writer.cut()`, `writer.copy()` near lines ~1056-1066.
`Buffer.java` creates another editor frame, not the text store.

`selection.py` now implements independent point/mark, selected region,
copy/cut/paste, and a test-only clipboard. `tp_editor.py` is the master
controller wiring keyboard and menu actions to the SAME handler.
A real GUI clipboard adapter, undo manager, styled document semantics,
Java UTF-16 position translation and complete event mapping remain pending.


## V4 GUI preview
`python3 -m zefm.editor.gui.tk_editor` launches a Tk/ttk tabbed editor
on a desktop with Tk and a display. Implemented: open, save, save as,
new buffer, UTF-8, clipboard, menu/key dispatch, basic Tk undo/redo.
Other original menu entries are explicitly marked unported. Current Tk
Text content is mirrored into the controller; this is not yet full
Java Swing styled-document or undo parity. Headless CI cannot exercise
the actual window; verify on macOS and Linux/X11.


## V5 desktop changes
Tk Text now handles Copy/Cut/Paste using virtual events, preserving native
undo groups and formatting instead of replacing the entire widget content.
Added Find/Find Next, Revert File confirmation, and dirty-tab indicator.
These are preview implementations, not full legacy Find/Replace parity.
\n## V6 GUI additions\nClose Buffer (Ctrl+Shift+W), literal case-sensitive Replace All via existing Replace menu, status line, safer Clear confirmation. These are new preview behaviors and are not asserted as original Java parity.\n
## V9 Query Replace
`zefm/editor/query_replace.py` contains the independently testable query-replace state machine. The Tk adapter prompts for the find/replacement strings, highlights the current match and accepts y/n/!/q. This is literal, case-sensitive, searches from the current cursor forward, and does not wrap. Ctrl+S/Ctrl+R incremental search is not yet implemented.

- Mail notes (v31): message-ID keyed local UTF-8 JSON storage prototype.
  Browser integration, fallback IDs, HTML annotation workflow pending.

### v39 — ServPakDir source-informed browser implementation

`GoFM.java` → `zefm/server/file_manager.py` + `zefm/server/http.py` directory listing.
`FileOps.java` → tightly scoped local file operations only (view/download/edit).
`WebEdit.java` → browser form interaction adapted to small UTF-8 filesystem files
(original Java WebEdit stored annotations in MySQL, so this is **not** a direct port).
`ShowNotes.java` → read-only `/notes` view using `WordNotes` JSON store.

No MyISAM-backed listings, SQL, FTP, remote editing, shell command dispatch,
or generalized Java servlets are retained. Full browser/editor bridge and mail
views remain pending.
