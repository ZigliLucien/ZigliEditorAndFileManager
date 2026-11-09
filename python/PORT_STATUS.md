Process-oriented foundation. See PROCESS_MAP.md. No Java feature parity claimed.
\nV3: editor master, selection/caret model, clipboard test double, copy/cut/paste dispatch added. GUI and source parity pending.\n\nV4: Tk/ttk desktop preview, multi-tab editor, OS clipboard adapter, file open/save, menu shortcuts. GUI requires manual display testing.\n\nV5: Native Tk clipboard events, find/find next, revert, dirty tabs. GUI requires live X11/macOS validation.\nV6: replace-all (literal case-sensitive), close buffer with unsaved prompt, cursor status, Alpine python3-tkinter instructions. Headless tests do not verify GUI event behavior.\n\nV7: Normalize single-letter Tk keysyms to lowercase, so Ctrl+S binds <Control-s> rather than <Control-S> (shifted on X11).\n\nV8: Shifted letter accelerators use uppercase Tk keysyms, ordinary letters lowercase. Preserves Ctrl+R behavior. Needs live Alpine verification.\n
V9: query-replace engine with y/n/!/q, tested without GUI. Tk query-replace prompt attached to Replace menu; incremental search is still pending. GUI behavior requires Alpine/macOS live testing.
\nV10: query-replace has clickable y/n/!/q controls and keyboard equivalents; fixed dirty flag reset in modified handler; basic properties-to-JSON importer. GUI needs Alpine validation.\n
V11: hybrid NORMAL mode with regex / ? n N and :s/:%%s with g/c/i flags; ordinary typing default. 17 headless tests pass; GUI awaits testing.
\nV12: Fix current-line :s offset/range via Tk text indices (previously escaped newline typo), preserve :%s; GUI requires live test.\n\nV13: :noh highlighting clear; Path import correction; 20 automated tests passing. Alpine GUI verification pending.\n
V14: configuration layer and CLI Java properties importer; optional validated
config/keyboard.json overrides original Java-derived shortcut registry. Default
shortcuts unchanged. 25 headless tests pass. Alpine GUI verification pending.

V15: independent mode registry and detection, per-tab assignment, manual Mode menu, status indicator; no highlighting or mode-specific execution yet.
\nV16: mode-specific Tab insertion, JSON validation command, pure mode_tools and tests. Tk GUI awaits Alpine verification.\n\nV17: JSON cursor path, copy path, jq on unsaved buffer, validation and Tab binding. 38 headless tests passing. GUI unverified.\n\nV18: JSON key-position fix; native JSON formatting and simple path evaluation; Trace menu relabeled Debug Python with saved-file pdb/xterm. 41 tests passing.\n
V19: JSON structural navigation and live status path; GUI pending live verification.

V21: configurable home and session-local working directory for File Open/Save As; no process cwd mutation.
\nV23: explicit per-tab successful-save status feedback; GUI live verification pending.\n
V24 scope cleanup: explicitly retired legacy modes TXML, HXML, JXML, CLSV and Utils operations Remote Save, Remote Edit, Upload, FTP. None were present in the v23 Python runtime menu or mode registry; no live code removal was necessary. Do not reintroduce during future Java menu migration.

V27: filtered font chooser with script preview; Unicode common-symbol palette.
GUI verification pending on Slackware.

V29: persistent recent files menu and Unicode character-at-cursor description;
font chooser preview expanded. Unit tests cover history state and name inspection;
GUI requires Slackware verification.

- v30: persistent font settings; Unicode base+combining codepoint inspector;
  Notes/email integration deferred pending original Java/browser audit.

- v31: macOS font fallback and installation-relative keyboard config.
- v31: email Message-ID annotation storage only; no mail/browser UI yet.

v32: prevent duplicated paste/copy/cut/undo on Tk Aqua by deferring standard edit shortcuts to native Text bindings.

V34: per-buffer Language selector and explicit UTF-8 dictionary shortcut expansion; OS input source remains external. Mac GUI verification pending.

v36: Alt-based input per buffer is available (source-guided by `Alphabet.java`),
with original French/Yiddish/Greek/etc maps retained. Tk/X11 and macOS live
keyboard testing required. Word/file Notes source relationship documented in
`SOURCE_GUIDED_MIGRATION.md`; no MyISAM records converted or bundled.

### v37 Notes implementation

- Desktop Notes menu: annotate current word / selected text with popup editor,
  list Notes for current file, edit and delete saved Notes.
- Persistent UTF-8 Notes store retains original `(filename, word, link, data)`
  schema; atomic writes, strict load validation, separate from editor buffers.
- Unicode word detection includes Hebrew/Yiddish combining marks.
- Source-guided importer of exported Notes JSON/JSONL. Optional one-time
  PyMySQL exporter for Notes and dictionaries, with strict UTF-8 and record
  count validation. The raw MyISAM archive itself is **not** extracted.
- Browser QuickEditor and email integration remain pending.
- Tests are headless plus one Tk/Xvfb Notes popup smoke test. Interactive
  Slackware and macOS confirmation still required.

## v38 progress
- Keymap reference is a GUI action (selectable language; searchable Alt chords,
  Unicode names, insertion, copy, activate). Uses preserved original `.keymap` files.
- Legacy lexical dictionary import tool and editor lookup dialog added. One
  UTF-8 JSONL dictionary file per language under XDG data dir; no MySQL runtime.
  Original dictionary records kept distinct from expansion shortcuts.
- The complete MyISAM dictionaries are NOT yet recovered; importer requires
  a validated SQL JSONL export. Browser/email quick editing still pending.
- Tests: see actual run output for counts; GUI smoke via Xvfb only.

### v39: First ServPakDir browser/file manager integration
- `File → Open Local File Manager in Browser...` launches a loopback HTTP server
  for the selected working directory and stops it on editor exit.
- Browse folders, view escaped UTF-8 text, download files, Quick Edit small UTF-8
  files with guarded save, read Notes linked to each file (read-only).
- Browser is bounded to one root and excludes FTP, remote actions, SQL, and
  subprocess routes. No desktop-buffer synchronization yet.
- Java source cross-check includes GoFM/FileOps/WebEdit/ShowNotes in ServPakDir.jar.
- Tests: actual suite run and Tk/Xvfb smoke test recorded in this version.

### v40: Notes save usability
- Desktop Save Note toolbar now appears before expanding note text; large
  display fonts can no longer push the save control below the dialog.
- Browser Notes changed from read-only to Create/Edit/Save with CSRF and
  revision checks. Both UIs share the original Notes `(filename, word)` key.
- Historical MyISAM conversion and desktop-file browser synchronization
  remain pending. The user's Slackware browser test of v39 was successful.


### v43 external file notifications
- Active file monitored approximately every 3 seconds and on tab changes.
- Nonmodal notification with explicit Reload (preserving unsaved work unless confirmed)
  and per-revision Dismiss.
- Missing disk file leaves in-memory edits intact; reload is unavailable.
- Existing v42 save conflict confirmation remains active after dismissing notices.
- SHA-256 monitor hashes the active file on the GUI thread; optimize for large files later.
- Tests added for per-tab dismissal/reappearance and optional Tk GUI interactions.


### v44 Maildir browser (initial)
- Loopback-only, read-only Maildir browser launched through the Tk File menu.
- Supports configured SIU/Personal/GMAIL paths, or a selected Maildir folder.
- MIME parsing prefers text/plain; HTML-only bodies become text; no active
  content, remote resources or attachments served.
- Word Notes linked by stable message ID in a local JSON store, not in mail files.
- Original mail fetching, sending, local HTML index, and MyISAM migration
  remain separate and unmodified.
- Bounded listing (100 recent entries, first 10,000 files/account), with a
  5 MiB preview cap; pagination/search and legacy HTML-index linking pending.
- See MAIL_ARCHIVE.md. Synthetic Maildir regression cases added.

### v45: Yiddish right-to-left editing
- Tk language Yiddish or Yiddish Alt keymap now right-aligns that buffer;
  switching to a non-RTL language/keymap removes alignment.
- The Tk 8.6 text widget still lacks full visual bidirectional/cursor behavior.
- File menu offers browser-native RTL editing for a saved file, using a
  `dir="rtl"` text area with protected Quick Edit Save.
- The browser file manager adds a general-purpose RTL edit link.
- Unsaved Tk buffers are never silently transferred, discarded or overwritten.
- Tests cover RTL HTML, logical UTF-8 preservation and optional GUI launching.

### v46: restore native Yiddish keyboard in actual RTL layout
- Browser-native RTL textarea now supports the original Yiddish.keymap
  without reversing or otherwise rewriting Unicode content.
- Alt and Alt+Shift combinations map via keyboard physical code; the
  legacy keymap is loaded at request time and no mapping is duplicated.
- New checkbox can disable mappings; local JavaScript is scoped to the
  RTL edit page by explicit same-origin CSP permission.
- New Language menu item opens browser RTL editing directly.
- Desktop Tk 8.6 still lacks true bidi editing/caret positioning; its
  right alignment must not be confused with proper RTL input.
- Tests cover mapped characters, serving the JS, form isolation and UTF-8.

### v47 — ServPakDir file-manager operations
- Added Create folder and Copy file (same directory) through the loopback
  browser, completing another concrete piece of Java FileOps migration.
- New files are published only when the destination does not exist; copying
  is bounded to 64 MiB, copies binary content and preserves POSIX mode.
- Rejects traversal, symlink escapes and unsafe names; POST actions require
  Host checks and the existing per-session CSRF token.
- Added focused tests for Unicode, conflicts, symlinks, invalid names,
  oversized files and HTML escaping.
- Rename, move, delete and Note migration are still unimplemented.

### v48 — source-faithful reconstruction of ZEFM listing
- Reproduced layout drawing from the original lister.xsl, locxsorter.xsl,
  listing.css, listing.js, Xlster.java and XCommands.java.
- Desktop File menu now opens the styled /listing page, which loads
  filesystem/notes data from a guarded JSON /api/files endpoint.
- Preserves directory checkerboard, top path/hostname, sorting/clock,
  colored radio options, yellow/cyan file rows and Notes previews.
- Adds filename filter, keyboard shortcuts and 25-file client pagination.
- Legacy plain HTML listing remains available; move/delete are disabled.
- Restrictive same-origin CSP and DOM textContent, no SQL/XML/XSLT for listing.
- See ORIGINAL_LISTING_DESIGN.md for the detailed original-source inventory.

### v49 — GoFM paging migrated
- Original GoFM.java distinguished page 0 (top) from numbered HEADERn
  pages; Xlster.java generated 25-file groups or extension-based groups.
- JavaScript now supports Top/Bottom/Previous/Next, Listing N of M, and
  progressively exposed page descriptors grouped ten per row.
- Filename page labels use four-character prefixes; extension groups use
  extension labels; other sort modes use page numbers.
- A page query parameter allows deep links and Back/Forward navigation;
  pages are clamped when directory contents or filters change.
- Existing JSON listing, file operations and safety checks remain intact.

### v49 GoFM paging
- Added server-side /api/listing-page with 25-file pages, extension grouping, filtered/sorted metadata and Notes previews.
- Browser now fetches requested pages instead of eagerly transferring the whole directory.
- V48 full JSON endpoint and basic listing remain compatible. Filesystem scan for exact counts remains O(N).

### v50 native PDF browser support
- View on PDF files now serves application/pdf inline, rather than UTF-8 text.
- Range requests (206, Content-Range, 416) support native PDF viewers.
- Bounded 128 MiB preview, PDF signature check, path restrictions, no-store.
- Download remains explicit and unchanged; standard text view stays intact.
- Synthetic PDF response tests cover byte ranges, invalid paths, MIME headers.

### v51 — safe rename with Notes
- Added same-directory rename form in both browser listings.
- POSIX no-clobber hardlink+unlink and best-effort rollback preserves file bytes.
- WordNotes records migrated to the new absolute filename with validation,
  no target overwrite, and rollback on failure.
- Desktop-open files are rejected through immutable snapshots produced on
  Tk's main thread; browser worker does not access Tk objects directly.
- Separate tests cover Unicode filenames, Notes, conflicts, CSRF, open tabs
  and failed filesystem/Notes writes.
- Directory moves/renames and trash remain unimplemented.

### v52 — preserve listing navigation across operations
- Original-style listing includes return state in View, Edit, Notes, Copy,
  Rename and desktop Open actions.
- Server checks every return URL is confined to /listing and a valid
  directory/sort/filter/page state; no open redirect.
- Confirmation pages and Notes subpages maintain prior GoFM listing context.
- PDF View opens a separate tab, retaining the existing page and filter.
- Filename filter debounced and does not fill browser Back history.
- Tests cover returning to page 3, Unicode filters, post-action links and
  rejection of malicious external return URLs.

### v53 — left-click View, right-click file options and rendered HTML
- Restored original filename interaction: ordinary left-click views; right-click
  (or Shift+F10) opens View, Copy, Rename, Edit, Quick Edit, Notes menu.
- HTML/HTM uses browser rendering at a confined /site URL, preserving
  relative local CSS and image assets; scripts/forms disabled by CSP sandbox.
- PDF native viewer and GoFM navigation continue unchanged.
- Added dedicated preview/path-security regression tests.

### v54 — compact listing and guarded file moves
- Desktop original-style listing compressed to 85% while keeping colors,
  typography proportions, GoFM pagination and right-click options.
- Implemented same-filesystem Move into an existing subdirectory in root.
- POSIX no-clobber target, Notes migration, destination confinement,
  symlink restrictions and desktop-open-file rejection.
- Source retained on failed Notes write or cross-device link.
- Tests cover Unicode names, Notes, collisions, POST authorization,
  unsafe destinations, and rollback. Directory moving/deleting remains pending.


## Planned: extension-aware browser presentation and document builds

These are **roadmap items**, not yet implemented. Preserve the original
ZEFM browsing model: left-click is the natural file presentation, right-click
is the operations menu, and opening a preview does not disturb the GoFM
listing's directory/page/sort/filter context.

### Markdown (`.md`)
- Render Markdown as HTML in the browser, using a Python library or Pandoc
  where available. Sanitize or sandbox generated HTML, including raw HTML.
- Expose a separate **Compile / Build PDF** operation using a configurable
  Pandoc command and PDF engine. Keep diagnostics visible even on failure.
- Open a generated PDF in the existing browser PDF viewer only if the build
  succeeds and a valid output file exists. A stale PDF should not be
  mistaken for the current result.

### LaTeX (`.tex`)
- Left-click defaults to a useful source/preview choice; add a
  **Compile → View PDF** operation, preferably accessible from right-click.
- Invoke an available configured engine (LuaLaTeX preferred, with possible
  latexmk support) using `subprocess` argument arrays, fixed working
  directory, timeouts, captured stdout/stderr, and explicit exit-code checks.
  Never concatenate filenames into shell commands.
- Launch compilation from a short-lived popup/dialog with a visible log and
  final status. Do not block the Tk event loop or HTTP request thread.
- Compile into a controlled output/build directory. Open the resulting PDF
  with the existing native browser viewer only after a verified successful
  build; avoid automatically showing an outdated PDF on failure.
- Treat TeX compilation as execution of potentially untrusted input:
  disable shell escape by default, use explicit command allowlists, and
  document that non-shell-escape TeX is not a full security sandbox.

### Email (`.eml`, Maildir message data)
- Use Python's standard `email` package with its modern policy and MIME
  tree traversal, respecting charset and multipart/alternative semantics.
- Display the HTML alternative when appropriate; otherwise convert the
  text/plain part into escaped, readable HTML. Never treat message HTML as
  trusted code: disable scripts, forms, active/remote content by default.
- Extract attachments to a dedicated per-message directory with safe,
  unique, Unicode-preserving filenames. Reject path traversal, reserved
  names, duplicate overwrites, symlinks, and unreasonable total sizes.
  Keep the original message intact and record attachment metadata.
- Show attachment links in the message view, with explicit **Save
  attachments** to disk (or a configurable extraction policy). Avoid
  automatically opening or executing attachment types.
- Reuse the existing local Maildir browser and browser-based HTML message
  reading workflow; this does not change the existing Emacs-based email
  composition/sending setup.

### Shared architecture and sequencing
1. Add a small extension/handler registry mapping suffixes to default View,
   Build, PDF and attachment actions, with safe fallback to raw/text view.
2. Implement Markdown rendering and PDF build with captured diagnostics.
3. Add LaTeX build popup and result verification, preserving compiled PDF
   links and logs.
4. Extend `.eml`/Maildir MIME rendering and per-message attachment
   extraction with explicit user controls.
5. Integrate each with the GoFM right-click menu and context-preserving
   navigation. Add unit/integration tests for Unicode paths, escaping,
   subprocess failure, stale outputs, malformed MIME, and attachment names.

### v55 — extension-aware Markdown View and PDF build popup
- New file-type registry recognizes PDF, HTML, Markdown and TeX, retaining
  ordinary text fallback and existing left-click/right-click semantics.
- Markdown View uses Pandoc HTML conversion when available, with sandboxed
  output and escaped source fallback if Pandoc is missing.
- Right-click Markdown or TeX → Compile PDF opens a separate build popup
  with CSRF-protected POST, visible diagnostics, timeouts and results.
- New PDFs are verified by signature in fresh per-run output folders
  before being offered through the existing browser PDF viewer.
- LuaLaTeX direct invocation uses -no-shell-escape, bounded runtime and
  explicit argument lists, not shell command strings.
- TeX processing is **not an OS security sandbox**; only trusted local
  source files should be compiled. Email MIME/attachment parsing remains
  a separate upcoming workstream.
- Regression tests cover build paths, error diagnostics, source previews,
  missing tools, Unicode names and old-PDF avoidance.

### v56 — Discount restored for Markdown
- Markdown HTML preview prefers Discount `makepage` (complete HTML document),
  then Discount `markdown` as fallback; no Pandoc invocation.
- Preserved original GoMD's `latex`/`nostyle` Discount flags and added
  `nohtml` to prevent arbitrary embedded HTML. Restrictive browser CSP
  still applies. Missing Discount yields escaped UTF-8 source.
- Markdown PDF path now uses Discount-generated HTML plus optional WeasyPrint,
  with fresh outputs, existing timeouts and diagnostics. If WeasyPrint is
  missing, HTML preview still works and PDF build reports a clear error.
- LuaLaTeX compilation and the `.tex` View behavior are unchanged.

### v57 — restored original ServPak mathematical page styling
- Inspected `TTT/ServPak/js/mathformat.js`, `TTT/ServPak/css/math.css`,
  and related `Plugins/GoMD.java`. The requested `web.css` was not found
  at the expected ServPak location.
- Added a scoped, locally served `/math.css` stylesheet, preserving the
  original dark-blue theorem text, green lemmas/propositions, brown lighter
  section headings, italic theorem blocks, numbered centered equations,
  and original link palette.
- Ported the presentation transformations from jQuery into Python's
  `HTMLParser`, performed before sending generated HTML. This supports
  theorem/proof labels, section headings, equation numbers, list elements
  and internal references without running JavaScript in the browser.
- Discount Markdown preview and intermediate HTML for PDF conversion use
  this shared presentation. Other locally generated ZEFM HTML pages link
  the stylesheet, though its mathematical styles are scoped to the
  `zefm-math-page` class to protect existing file manager layout.
- Existing CSP restrictions still block scripts and remote MathJax: this
  revision formats mathematical structure but does not provide a full
  TeX-to-typeset-math engine in the browser. LuaLaTeX PDF compilation
  remains the definitive route for typesetting equations.

### v58 — Python replacement for the original `mathjaxfilterr` Perl pipe
- Inspected the user's actual `mathjaxfilterr`: it streams HTML output
  from Discount `makepage` and inserts a MathJax configuration, CDN
  runtime, `mathformat.js` and `math.css` immediately before `</head>`.
- Added `server/mathjax_filter.py`, a robust, idempotent Python
  header filter. Mathematical structure formatting remains server-side
  Python (`math_presentation.py`), **not jQuery**.
- Added a local `mathjax-config.js` with the original inline `$…$`
  and `\\(…\\)` delimiters, plus display `$$…$$` and `\\[…\\]`.
- Preview uses modern MathJax 3 (TeX/MathML to SVG) loaded by HTTPS from
  jsDelivr, replacing the obsolete `http://cdn.mathjax.org` URL.
- MathJax scripts run only in sandboxed Markdown preview pages:
  CSP enables scripts but denies same-origin privileges, forms, frames,
  arbitrary network requests and general object embedding. Normal
  HTML previews continue with scripts disabled.
- PDF build HTML remains script-free, as WeasyPrint does not run JS;
  the existing direct LuaLaTeX compilation pipeline is unchanged.
- No jQuery dependency is introduced. Offline MathJax bundling is a
  possible subsequent step; the MathJax CDN currently requires internet.

### v59 — unified startup mode selection
- New `python -m zefm --mode {editor,files,both}` entrypoint.
- Default remains editor-only; existing editor and file-manager
  module entrypoints continue to work.
- File-manager-only starts the localhost HTTP server without Tk.
- Both mode creates one Tk editor and one browser file manager sharing
  the existing thread-safe open-file queue and file-in-use callbacks.
- `--root`, `--port`, `--no-browser` are available in files/both
  modes; automatic port selection stays the default.
- Closing Tk shuts down the combined file manager. Ctrl+C stops
  standalone file-manager mode.
- Unit tests verify options, dispatch, server cleanup, and no-browser mode.

### v60 — mouse-wheel file chooser and accessible RTL editor
- Replaced native Open/Save As filename dialogs with a compact Tk
  Treeview chooser, keeping the configured initial directory.
- Mouse wheel advances the selected file (including X11 Button-4/5)
  and scrolls the chosen item into view; tests cover platform deltas
  and directory sorting.
- Added an always-visible **RTL Browser** button, using the existing
  Yiddish browser-edit path for correct BiDi rendering.
- Tk Text still cannot natively reorder Yiddish right-to-left glyph
  runs on Tk 8.6/X11. No visual character reversal was applied to
  stored buffer contents; this avoids corrupting Unicode text, cursor
  offsets, search and saves.

### v61 — chooser scrolling and files-mode navigation
- Mouse wheel handling covers Tk chooser list, scrollbar and adjacent
  panel, with a pure function for bounded selected-row movement and
  immediate filename update (avoids virtual-event timing races).
- Styled GoFM file manager has explicit Home/Up directory controls.
  Both work with standalone `--mode files` as well as combined mode.
- Top has a single click callback; page URL canonicalizes when a
  requested page is no longer available. Browser history remains active.
- Tests check wheel direction/bounds, 62-file three-page navigation,
  nested Unicode directory breadcrumbs, no-editor standalone shell
  and standalone launcher operation.


### v74 — ServPakDir New File workflow

- The browser file manager now offers New File in both the styled and basic
  listings. It opens a directory-scoped form and creates an empty file with
  exclusive no-overwrite semantics using the same LocalFiles boundary.
- Filenames are validated as single UTF-8 names; existing files, directories
  and symlinks are preserved. POST creation requires the loopback session's
  CSRF token. Back navigation preserves the styled listing's sort, filter,
  directory and page state.
- A successful creation offers browser Quick Edit. When the browser is
  integrated with the desktop TPEditor, it additionally offers the existing
  `/open-editor` bridge. The browser never edits an existing unsaved
  desktop buffer without the editor's own guards.
- `tests/test_new_file_workflow.py` adds unit and HTTP integration coverage.
  Run the Python suite/GUI smoke tests locally; no Java source parity claim
  or verified GitHub Actions passing status is made for this increment.


### v75 — XCommands.runC copy destination support

- Inspected the original `NetsManager/XCommands.java` copy workflow:
  the old Copy form accepts destinations outside the source directory.
- Extended the Python `LocalFiles.copy_file` with an optional,
  browsing-root-relative destination directory. The implementation
  retains the existing source copy contract, guarded destination
  handling, bounded data transfer and exclusive no-clobber publishing.
- The browser Copy form now defaults to the source directory but lets
  the user select a different existing directory and filename.
  The result links back to the source listing or into the destination.
- Unit/HTTP tests cover Unicode names, no-clobber, symlink/traversal
  restrictions, regression of the older same-directory signature,
  CSRF and other forged form inputs.
- The implementation has been committed; full suite execution and
  interactive Slackware testing remain unverified.


### v77 — source-guided recoverable Delete/Restore

- Inspected the original `NetsManager/XCommands.java:runX` deletion
  path, including its MySQL annotation cleanup.
- Added `zefm/server/trash_ops.py`: regular-file Trash with unique
  private storage directories and an original-path JSON record.
  The existing Notes-aware no-clobber Move service moves files into
  Trash and back, preserving annotations.
- Wired `/delete` (GET confirmation, protected POST),
  `/trash` (GET list) and `/restore` (CSRF-protected POST)
  into the browser; enabled original-style dele radio and context
  menu, plus a Trash link in both browser layouts.
- No permanent deletion or arbitrary remote command execution.
  Directory deletion/restore is deliberately out of scope.
- Added unit/HTTP tests for Unicode, Notes, collisions, open buffers,
  malicious requests, rollback and normal browser navigation.
- GitHub Actions compilation and regression suite used to identify
  and fix HTML local-link parsing and stale test expectations.


### v78 — instant browser-save notification to desktop editor

- Extended the existing queue-only browser/Tk bridge to notify an
  open active TPEditor tab after a successful browser Quick Edit save,
  without waiting for the usual 3-second disk monitor tick.
- `BrowserServer` receives an optional `file_saved` callback; the
  integrated Tk launcher sends its event to a dedicated thread-safe
  `Queue`. Tk handles the SHA-256 external-change notice on the main
  thread only.
- The editor does not automatically overwrite or reload a buffer;
  its existing nonmodal Reload/Dismiss notice and conflict-safe Save
  semantics remain in force. Inactive tabs still check on selection.
- This works from both the file manager and the dedicated RTL browser
  editor, and does not alter standalone `--mode files` behavior.
- New `tests/test_browser_save_bridge.py` covers notification success,
  rejected saves and preservation of unsaved editor content (GUI tests
  run through Xvfb in CI).


### v79 — per-buffer external revision markers for browser saves

- Browser Quick Edit now signals **all** matching TPEditor buffers,
  including inactive tabs, through the existing HTTP→Tk queue.
- Tk marks an externally changed tab with `↻`; unsaved desktop edits
  independently retain the `*` marker (both may appear). The current
  tab still receives the nonmodal Reload/Dismiss notice immediately;
  selecting an inactive marked tab displays that same notice.
- Reverting/reloading or explicitly dismissing the observed disk
  revision clears its marker. Dismissal remains revision-specific:
  subsequent browser changes are detected again.
- The handler computes SHA-256 only for paths supplied by successful
  browser saves, not all files every 150 ms. The pre-existing periodic
  disk monitor still checks the active buffer. No buffer is automatically
  reloaded or overwritten, and standalone file-manager behavior is unchanged.
- Regression cases added to `tests/test_browser_save_bridge.py` for
  inactive-tab changes, unsaved buffer protection, and unchanged saves.


### v80 — persistent Save status and right-click Recent Files

- Added a separate bottom-margin status indicator in the Tk editor,
  independent of the long line/column/mode message. Successful disk writes
  show `✓ Saved: filename`; edited buffers show `● Unsaved changes`.
  The Saved indicator survives cursor movement and remains specific to the
  selected buffer. A declined conflict overwrite or failed write must not
  claim Save succeeded.
- Right-clicking within the Tk editor opens the existing bounded,
  persistent Recent Files history (full UTF-8 paths), plus Open File
  and Clear Recent Files commands. macOS Control-click is supported as
  an alternative context-menu gesture. The File → Recent Files submenu
  and editor popup use a single menu-population implementation; no new
  history store or separate list is maintained.
- Selecting a recent file uses the existing `_open_path` behavior:
  already-open buffers are reselected rather than duplicated and
  external-change/unsaved-edit protections remain in force.
- Added Tk/Xvfb GUI regression coverage in
  `tests/test_save_status_recent_popup_gui.py`.
