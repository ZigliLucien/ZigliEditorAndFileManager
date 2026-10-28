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
