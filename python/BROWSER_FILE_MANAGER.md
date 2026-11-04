# ZEFM v39 — local browser / ServPakDir port, first increment

## Source references

This work draws on the original Java source at `ZEFMEXPORT.zip`, nested
`EXPORT/ServPakDir.jar`, notably:

- `ServPakDir/ServPak/jv/GoFM.java`: directory/file listing in a browser;
  original implementation read listings and data through MySQL and XQuery.
- `ServPakDir/ServPak/jv/FileOps.java`: user-initiated file actions,
  previously delegated through `NetsManager.XCommands`.
- `ServPakDir/ServPak/jv/WebEdit.java`: browser textarea editing of **stored
  annotations** via MySQL; not the same as writing filesystem text files.
- `ServPakDir/ServPak/jv/ShowNotes.java`: displaying notes through the browser.

The Python browser reproduces the useful *workflow*, **not** the original
URL formats, Java servlet classes, database-stored listings, or all file
operations. It deliberately avoids dynamic shell/SQL execution.

## Launch from editor

1. From extracted project root, start `python3 -m zefm.editor.gui.tk_editor`.
2. Use **File → Set Working Directory...** to choose the tree to share.
3. Choose **File → Open Local File Manager in Browser...**. A URL such as
   `http://127.0.0.1:38291/` opens in the system browser. The server is started
   only on user request, binds exclusively to the loopback address, and uses
   an ephemeral port. The selected root directory is fixed for that server.
4. Browse folders, view UTF-8 text, download files, or use **Quick edit**.
   Quick edit is limited to text files up to 1 MiB. The browser's **Save**
   button writes explicitly after checking that the file hasn't changed since
   the form was loaded. If it has, HTTP 409 is shown; reload before saving.
5. The **Notes** link for each file displays the word-attached notes from
   `~/.local/share/zefm/word_notes.json` (or `$XDG_DATA_HOME/zefm/word_notes.json`).
   Since v40, the browser Notes page offers **Add Note** and **Edit note**;
   use **Save Note** on the form to persist to the same UTF-8 JSON store.
   The form checks for concurrent changes to the note and requires a
   session-specific CSRF token. Only notes for files under the selected root
   are displayed. No database export/import is performed.
6. On editor quit, the server shuts down. The browser tab may stay open but
   won't serve files. If you change the working directory, activating the
   File Manager menu again restarts the service with the new root.

Alternatively, use the standalone interface:

```sh
python3 -m zefm.server.http --root "$HOME"  # Ctrl+C stops server
```

## Security and scope

- HTTP listens on `127.0.0.1` only and accepts local Host headers only.
- The chosen root is a directory boundary, including resolved symlinks.
- Browser contents and filenames are HTML escaped; web pages are not executed
  as HTML. Download uses `Content-Disposition: attachment`.
- Form writes require a per-server unpredictable token and the original file
  digest; saves use temporary files and atomic replacement within the folder.
- There are no remote editing, FTP, upload, MySQL, arbitrary command or
  user-defined subprocess routes.
- **This is for a trusted local workstation, not an internet-facing server.**
  Another process on the same machine could visit loopback services. Keep
  private files outside the chosen root when you do not intend to browse them.
- Existing editor tabs are **not automatically refreshed** after a browser
  Quick Edit. Revert/reopen the file in ZEFM before editing further; otherwise
  an editor save may overwrite the browser's newer file content. This is a
  known integration limitation that will be addressed in a later version.
- The original MyISAM data is not bundled or served by the browser.

## Remaining steps

The full ServPakDir migration still needs: explicit file operations
(copy/move/rename/delete) with confirmation, the browser→editor open/refresh
bridge, downloaded email indexing, message display, and contextual Notes on
email messages. The Python v39 routes intentionally expose none of the old
remote commands.

## Tests

`python3 -m unittest discover -s tests -v` exercises traversal rejection,
Host/CSRF checks, Unicode and HTML escaping, directory navigation, file
modified-during-edit conflict detection, preservation of file permissions and
CRLF line endings, UTF-8 Notes rendering, and other earlier editor features.

A Tk/Xvfb smoke test verifies that the File menu creates a working browser
server; native Slackware/macOS interactive behavior still needs confirmation.


## v41 — Open directly in desktop ZEFM

Start the file manager from **File → Open Local File Manager in Browser...** in the Tk editor.
The browser listing displays **Open in ZEFM** for each file. Clicking it submits a
same-origin POST request with a per-session form token. The local server validates
the file path within the selected root, then queues the absolute path for the
Tk main thread. It does not manipulate widgets from the HTTP worker thread.
If the file is already open, ZEFM selects that tab instead of opening another.
Standalone `python3 -m zefm.server.http` does not show this button.

**Known limitation:** Browser Quick Edit and other external changes still require
manual **File → Revert** in already-open desktop buffers. V41 does not overwrite
an unsaved editor buffer in response to a browser request.

## v42 — external file change safety

When the desktop editor opens a file, it records a SHA-256 signature of the
bytes on disk. Saves refresh the signature. If another application or browser
Quick Edit changes that file, **File → Save** warns before overwriting the
newer version. Choosing No preserves both the editor buffer and disk data.

**Open in ZEFM** for a file already in an editor tab checks the disk signature.
For an unmodified tab, it offers to reload; for an unsaved tab, it warns without
destroying the unsaved edits. **File → Revert** remains an explicit way to
reload a buffer.

This is a snapshot check rather than continuous filesystem watching.
There is a possible time-of-check/time-of-use race if another writer modifies
the file between confirmation and writing; fully atomic conflict-safe saves
will require a later revision.


## v43 — nonmodal external-change notifications

When the Tk editor has a file open, it checks the *active buffer* against
the saved disk SHA-256 approximately every **3 seconds**, and again when
switching tabs. If the file has changed outside ZEFM, a nonmodal strip appears
above the status line:

- **Reload from disk...** explicitly reloads the disk version. For an
  unsaved buffer it asks before discarding those edits.
- **Dismiss this change** suppresses the warning for that particular disk
  revision. A further external change produces a new warning.
- A deleted disk file is reported without deleting the editor buffer;
  reload is disabled until the file becomes available again.

Nothing is reloaded automatically, and merely dismissing the notice does
**not** disable the separate v42 warning shown before overwriting a newer
disk version with File → Save. Save and Revert reset the notice state.

These checks are performed on the Tk main thread and hash the entire active
file; there is no kernel file watcher and no instantaneous notification. For
very large files, a later version should use a metadata precheck and/or a
background worker. The existing check-before-write safeguard still has the
documented time-of-check/time-of-use race.


## v45 — Yiddish and other right-to-left writing

The desktop Tk `Text` widget on Tk 8.6/X11 does not fully implement Unicode
bidirectional layout. Selecting **Language → Yiddish**, or **Language →
Alt Keymaps (per buffer) → Yiddish**, now right-aligns paragraphs *in the
desktop editor*, and switching back removes that alignment. Right justification
does **not** reverse glyphs, move the cursor in visual RTL order, or implement
the Unicode Bidirectional Algorithm. The underlying UTF-8 contents are never
reversed or otherwise rewritten.

For **correct RTL editing**, save the current file and select
**File → Edit Current File RTL in Browser...**. ZEFM opens the local Quick Edit
page with `dir="rtl"` and right alignment. The browser handles bidi layout
(including Hebrew/Yiddish with numbers and embedded Latin words). Its Save
button retains the same optimistic digest check and CSRF guard as normal Quick
Edit, and writes the original logical Unicode character sequence.

If the Tk buffer has unsaved edits, the command refuses to launch until
you explicitly save it. After saving from the browser, switch back to ZEFM:
v43 will report the external change, where you can choose **Reload from disk...**
without losing unsaved changes automatically.

The file-manager listing also exposes **RTL edit** for any file.

**Important:** The desktop's legacy Alt keymap works inside the Tk widget
only; the browser uses its normal operating-system/IME keyboard setup (or
paste) for Yiddish input. A future integration may offer browser-side
legacy keymap shortcuts without relaxing the browser's restrictive CSP.


## v46 — original Yiddish Alt keymap in the real RTL browser editor

**The Tk 8.6 widget still cannot insert Hebrew/Yiddish with correct RTL cursor
movement. Right alignment is not bidi layout.** This limitation is not fixed
by choosing Language → Yiddish in the desktop editor.

To type Yiddish with correct direction, save your desktop buffer and choose
**Language → Edit Yiddish RTL in Browser (Alt keymap)...** or
**File → Edit Current File RTL in Browser...**.

The RTL browser editor now loads the original
`legacy_keymaps/Yiddish.keymap` and enables **Use original Yiddish Alt
keymap** by default. Examples:

- **Alt+B** inserts `ב`.
- **Alt+Shift+I** inserts `אי`.

The browser handles visual right-to-left layout and cursor placement.
New letters appear **to the left** of earlier Hebrew letters.
The underlying UTF-8 text remains in logical order and is never reversed.

The checkbox can be unchecked to use the system's own keyboard input.
Only Alt/Alt+Shift chords mapped in the legacy file are intercepted;
Ctrl/Command shortcuts and unmapped Alt shortcuts are left untouched.
A browser or desktop environment may reserve particular Alt shortcuts
before the page receives them.

The keymap script is served only by ZEFM's loopback server; the RTL edit page
permits this same-origin script while all other browser pages retain the
earlier restrictive content security policy. The file manager's RTL edit
link offers the same control.

Saving the file in the browser retains digest conflict protection. Return to
Tk and choose **Reload from disk...** when ZEFM detects the external change.
No private mail or text data is sent to GitHub.


## v47 — local file operations (ServPakDir FileOps increment)

The browser file manager can now **Create folder** in the current directory
and **Copy...** a regular file into the **same directory**, under a new name.

To use these operations, start **File → Open Local File Manager in Browser...**
and use the form above the directory listing, or choose **Copy...** next to a
file. Operations only modify the selected local file-tree root. The existing
browser-to-Tk Open in ZEFM bridge and text Quick Edit are unchanged.

Safety limits:
- Every write requires the existing per-session CSRF token and valid Host
  header. No FTP, LAN server, arbitrary command execution, or MySQL.
- New file/folder names must be a single name, not an absolute path,
  parent-traversal path or path containing slash/backslash/control characters.
  Names are UTF-8 and checked against a 255-byte limit.
- Copy is bounded to **64 MiB**, supports arbitrary binary files, preserves
  Unix file permissions, and leaves the source untouched. A private temporary
  copy is completed and synced before publishing it via a no-clobber link.
- Existing target files, directories or symlinks are **never replaced**.
  A name collision returns HTTP 409. This means a copy with the same filename
  must be given a new name.
- Direct symlink sources are not copyable; paths escaping the selected root
  are rejected. File changes while a copy is underway are checked before
  publishing, with the normal limitations of a trusted local filesystem.
- Creating a folder uses owner-only default permissions (subject to umask).
- Word Notes belong to the original file identity and are **not automatically
  duplicated** when copying a file.

The no-overwrite copy uses a POSIX filesystem hardlink as an atomic publish
operation; this increment targets the user's Linux/macOS workstation. It does
not provide atomic source snapshots under concurrent writes.

**Not yet implemented:** rename, move between directories, delete/trash,
multi-file selection, copy directory trees, and automatic Note migration. The
absence of destructive operations is intentional while we validate the new
browser file actions.

## v50 — view PDFs directly in the browser

With **view** selected in the reconstructed listing, click a `.pdf` file
to open the **native browser PDF viewer**. The basic HTML listing also links
PDF files directly to that view. The new `GET /pdf?path=...` endpoint sends
the original PDF bytes as `application/pdf` with inline disposition, and
supports a single `Range: bytes=...` request for efficient seeking to pages.

Use the existing **Download** link to save the file instead. Neither action
changes the original PDF. Only files inside the configured directory root,
with a `.pdf` extension and a PDF header, are viewable. Preview size is
limited to 128 MiB. The server is loopback-only; PDF viewing uses the
browser's built-in PDF capabilities and does not execute an external program.

Firefox: ensure the PDF content-type action is configured to **Open in
Firefox** if you want the viewer rather than the browser's download prompt.
PDFs larger than the preview limit must be opened locally outside this
browser interface. The normal Quick Edit textarea is deliberately not
offered for PDF files.

## v51 — guarded file renaming and Note migration

The reconstructed listing now includes a **rename** operation alongside
View/Copy/Edit/Notes. In the styled listing, choose **rename** and click a
filename; in Basic listing, select **Rename...** next to the file. A form
accepts a new filename in the *same directory*, preserving its contents and
existing word-attached Notes.

The operation does not overwrite existing destinations and rejects absolute
paths, path separators, control characters, symlink sources, and renaming a
directory. It checks that a file is not open in the desktop editor when
launched through Tk (main-thread snapshots; external editors cannot be
detected). All write requests have the existing loopback Host and CSRF checks.

The operation uses a no-clobber hardlink plus unlink on the same POSIX
filesystem, with an atomic JSON Notes store update between those steps.
On a failure it attempts to roll back the new link and Notes change.
There is a short-lived duplicate hardlink while Notes are being updated;
this is a **best-effort local transaction**, not crash-safe across power
loss, and an external concurrent writer may still race with it. Users should
not use renaming for files being edited elsewhere.

**Still pending:** cross-directory move, directory-tree rename, delete/trash,
and a more general open-file coordination system. The original PDF viewing,
GoFM paging and older Basic listing remain available.

## v52 — navigation that preserves your place

The original-style ZEFM file listing now carries its directory, page number,
sort order and filename filter into its **View, Notes, Edit, Copy, Rename and
Open in ZEFM** actions. Back links and successful form submissions return to
that same listing state, rather than dropping to an unfiltered Basic listing.
Existing direct URLs without return context continue to work.

PDFs opened from the styled listing now open in a **separate browser tab**,
leaving the directory page, selected operation and GoFM navigation untouched.
The Basic listing retains its ordinary direct PDF link.

The return address is verified as an internal `/listing` URL with a confined
directory and valid paging/sort/filter parameters. External URLs, traversal
and arbitrary HTTP routes are rejected. No JavaScript framework or XML/XSLT
is required. Typing into the filename filter is debounced and updates the
current history entry instead of adding one Back entry per keystroke.

## v53 — original mouse interaction and natural browser presentation

The original ZEFM interaction is restored: **left-click a filename** to view it,
**right-click** to open the file-operation menu (View, Copy, Rename, Edit,
Quick Edit, Notes). The keyboard equivalent is **Shift+F10** on a focused
filename button. The colored operation strip is retained for its original
visual identity, but normal left-click no longer applies its selected radio
operation.

PDFs continue to use the Firefox/native PDF viewer. HTML and HTM files
now open as rendered documents rather than escaped source text. A confined
`/site/...` URL preserves relative links to local CSS and image assets.
The HTML preview response is protected with a restrictive CSP sandbox:
embedded JavaScript, forms, and plugins cannot execute; linked resources
are limited to allowed static formats within the selected root and size
limits. Other text formats retain ZEFM's source/text viewer.

The styled listing opens PDF and HTML documents in another tab so the
GoFM page, sort order and filter remain intact. Browser settings and popup
blocking may affect opening a new tab.

## v54 — compact listing and guarded directory moves

The original-style desktop listing now uses **85% CSS zoom**, reducing text,
whitespace and controls together while maintaining the original checkerboard,
blue filename buttons, GoFM paging and right-click operation palette.
The compact zoom applies only at desktop widths (700px and above); small
screens retain responsive sizing.

The previously disabled **Move** operation is now available in the
right-click menu and operation strip, and the Basic listing has a **Move...**
link. It opens a form accepting an *existing* destination directory relative
to the file-manager root (for example `Research/2026`). Files retain their
original names. Move refuses to overwrite another file, traverse outside
the selected root, follow directory symlinks or move a file open in the
ZEFM desktop editor. Existing word Notes follow the file.

Like Rename, Move uses POSIX no-clobber `os.link` followed by `os.unlink`
with an intervening atomic Notes update and best-effort rollback. A move
across different filesystems is **not supported** (no unsafe copy/unlink
fallback). Do not move files being written by external programs, or rely on
this operation as a crash-safe filesystem transaction. Directory-tree moves
and trash/delete remain unimplemented.

## v55 — Markdown viewing and PDF compilation for Markdown/LaTeX

The local browser file manager now has a file-type registry. Left-clicking
`.md` or `.markdown` produces a **sandboxed HTML preview** with Pandoc if
it is installed. The preview falls back to escaped source when Pandoc is not
available or conversion fails. Raw HTML is excluded from Pandoc's Markdown
input; the preview's CSP blocks scripts and remote resources.

Right-click `.md`, `.markdown` or `.tex` and choose **Compile PDF**.
This opens a separate local browser tab containing a form, compilation
status and error log. The form uses a protected POST request. Compilation
runs in a short-lived worker thread (the HTTP request thread, not Tk's UI
thread) using a trusted executable name and argv-list subprocess invocation;
no shell string is evaluated. Successful compilation automatically opens
the new PDF in the same tab using ZEFM's existing native browser PDF route.
On failure, the diagnostics stay visible in the build tab. LaTeX source
continues to open in ZEFM's text/source View when left-clicked.

Builders require local installations of **pandoc** (Markdown) and
**lualatex** (LaTeX and Pandoc's PDF engine). The build has a 45-second
timeout, UTF-8 source size limit of 2 MiB, bounded logs, and a newly created
temporary output folder beneath `.zefm-build` in the source directory.
The generated PDF is published under that build folder. A failed attempt
never opens an older PDF. PDF previews continue to have a 128 MiB limit.
`.zefm-build` directories are hidden from the styled GoFM listing, but
can be found through the Basic listing.

**Security**: compile only files you trust. Although the direct LuaLaTeX
command disables shell escape and none of the commands invoke a shell,
TeX itself is powerful enough to read or write files accessible to the
running account; it is *not* a sandbox. The HTTP server remains bound to
loopback and protects build POSTs with the existing CSRF token. Do not
expose it to untrusted users. Builds do not yet run in an OS sandbox.
The browser-side status view appears immediately; the actual PDF opens
only after a success response.

**Not part of v55**: MIME email extraction, attachment directories,
build cancellation, a configurable engine selection UI, and caching of
Markdown HTML. These remain on the development roadmap.

## v56 — Markdown via Discount `makepage`, not Pandoc

Markdown View now runs Discount **`makepage`** using the `latex`,
`nostyle` and `nohtml` flags. This follows the original ZEFM
`Plugins/GoMD.java` Markdown presentation: that Java code used
`/usr/local/bin/markdown -f latex -f nostyle`, then assembled the HTML
page. Using `makepage` produces the complete page directly. When
`makepage` is unavailable, the Discount `markdown` executable is tried
instead; if neither is installed or conversion fails, an escaped Markdown
source preview remains available. HTML stays in the restricted preview
sandbox. Raw HTML from Markdown is intentionally disabled.

Markdown **Compile PDF** no longer invokes Pandoc. ZEFM now builds HTML
with Discount first and, **if WeasyPrint is installed**, converts that HTML
to a newly generated PDF. A missing WeasyPrint executable yields a clear
build diagnostic without affecting Markdown HTML viewing. The `.tex`
LuaLaTeX compilation path has not changed. MathJax's historical CDN script
is not automatically loaded because preview scripts are blocked; any future
local mathematical typesetting must preserve the sandbox model.

## v57 — original ServPak mathematical presentation

The original `TTT/ServPak/js/mathformat.js` and
`TTT/ServPak/css/math.css` have been adapted into the Python
browser renderer. They originally used jQuery to manipulate theorem,
lemma, corollary, proof, numbered equation, section, list and internal
reference elements after the page loaded.

Since ZEFM intentionally disables JavaScript inside generated Markdown
previews, the corresponding transformations now occur **on the Python
server**, before the document is delivered. The new local `/math.css`
reconstructs the typography and color palette with styles scoped to
`zefm-math-page`. It is also linked from other locally generated HTML
pages without disturbing their controls or the GoFM directory listing.

The transformed HTML preserves Discount's UTF-8 content and existing
strict sandbox Content Security Policy. The original remote MathJax
script is **not enabled**; `$...$` and `\\(...\\)` formulas may still
appear as TeX text until an approved local math renderer is introduced.
LuaLaTeX-to-PDF remains available for fully typeset mathematics.

## v58 — native Python replacement for `makepage | mathjaxfilterr`

The user's original 33-line Perl `mathjaxfilterr` has been ported to
`server/mathjax_filter.py`. It inserts scripts just before `</head>`,
without modifying the Discount HTML body. The old filter used MathJax
version 2 via HTTP and depended on jQuery to run `mathformat.js`.

The new pipeline is:

```text
Markdown → Discount makepage → Python mathformat equivalent
         → Python mathjaxfilterr equivalent → sandboxed browser view
```

The JavaScript formatting effects of `mathformat.js` remain implemented
in Python, and the original typography lives in `/math.css`. The page
also receives local `/mathjax-config.js` and MathJax version 3's SVG
component from `https://cdn.jsdelivr.net`. The configuration supports
`$…$`, `\\(…\\)`, `$$…$$`, and `\\[…\\]` delimiters. This
requires **no jQuery**.

The preview CSP allows script execution only for the local configuration
and HTTPS MathJax bundle and retains an **opaque sandbox origin**, which
prevents generated Markdown from acting as a privileged ZEFM page.
Embedded forms, framing, remote images, and arbitrary external resources
remain blocked. This means MathJax is no longer an entirely offline
feature; a connection to jsDelivr is required for this version.
Ordinary `.html` previews remain strictly script-disabled. Markdown-to-PDF
still uses Discount/WeasyPrint without browser JavaScript. The direct
LuaLaTeX compilation path for `.tex` files is unchanged.


## v62 — compact directories and EPUB/DjVu previews

The original-style directory grid retains four columns, names, clickable
navigation, and alternating palette while reducing cell padding and
surrounding whitespace. File metadata/notes remain unchanged.

The extension dispatch registry recognizes `.epub`, `.djvu`, and `.djv`.
EPUB left-click opens an in-browser, escaped-text chapter reader using the
standard-library ZIP/XML modules. Chapter navigation follows the EPUB
spine. Book-authored HTML/scripts are not executed, and book images and
advanced CSS/layout are not yet displayed.

DjVu left-click opens a page viewer. Install DjVuLibre's `ddjvu` executable
to render each page via a local, bounded subprocess to a PNG response.
The interface provides previous/next page links; an out-of-range page returns
an error. This is a raster-only preview and does not expose DjVu OCR text.
No browser DjVu plugin is necessary. For example on Alpine use
`apk add djvulibre` if that package is available for your release.

The original document remains available for download through the existing
download route (subject to its current file-size limit). Neither format
runs untrusted embedded scripts or external programs from inside archives.
The EPUB and DjVu readers are initial implementations requiring browser
testing on Slackware/macOS/Alpine.


## v63 — port-8000 extension-command workflow

The user's local `server.py` mapped extensions to subprocess commands:
`.ipynb` → `jupyter nbconvert --to html --stdout`,
`.json` → `jq .`, `.xml` → `xq .`, `.md` → `mdownpl`,
`.tex` → `goTEX`, and `.ps` → `goPS`.
ZEFM now shares the **extension-to-preview** behavior without importing
the old CGI scripts or exposing an arbitrary command runner.

- `.json`: pretty-print parsed JSON as escaped HTML text using stdlib `json`.
- `.xml`: pretty-print XML as escaped HTML text using stdlib `minidom`.
  This retains XML, rather than reproducing `xq .`'s XML-to-JSON output.
- `.ipynb`: optional `jupyter nbconvert --to html --stdout` using
  argv-based subprocess, timeout, output-size limit, and no shell.
  The resulting notebook HTML is served with a restrictive CSP that
  blocks executable scripts and remote resources; advanced notebook
  interactions may not display.
- Existing Markdown (Discount), TeX (LuaLaTeX build), and PS/EPS
  (Ghostscript) handlers are unchanged.

All new preview paths use the current root-confined file resolver. No CGI
or public port-8000 listener is created. The browser server remains
loopback-only and the source files remain unmodified.

Run tests: `python3 -m unittest discover -s tests -v`.


## v64 — fix Home/Up when opening the remembered folder

The Tk File menu used to pass the last-used editor working directory as
the HTTP server root, making Home and Up unable to leave that directory.
The launcher now separates a server browsing boundary from the initial
listing folder. When invoked from the Tk File menu without an explicit
root, the browser is rooted at the editor's configured home directory
and opens at the remembered folder within that home.

If the remembered directory lies outside the configured home, only its
immediate parent is used as a restricted browsing root; the entire
filesystem is never exposed implicitly. An explicit `--root` remains a
strict boundary as before. The browser still listens on loopback only.

The original Home, Up, and breadcrumb links continue to use
`/listing?path=...`. Browser root is a security boundary, not necessarily
the folder shown on the first page. Tests are in
`tests/test_browser_root_navigation.py`.


## v65 — hyperlinks inside local HTML previews

The original HTML preview allowlist omitted PDF, so relative `<a href="paper.pdf">`
links returned an HTML preview resource error. Clicking HTML links also
encountered the document sandbox's top-level navigation restriction.

The `/site/` handler now recognizes linked `.pdf` documents and delegates
them to the existing bounded PDF viewer, including its byte-range support
and PDF signature check. Other HTML files still load as sandboxed HTML.
The CSP permits explicit user-activated top-level navigation while retaining
restrictions on scripts, forms, and same-origin privilege. Files remain
confined to the configured browsing root. Ordinary links use their normal
browser-relative URL resolution; links using the original machine's
`file://` URLs are not automatically rewritten.

Test coverage: `tests/test_html_preview.py`. Browser click behavior still
requires manual verification in Firefox/Safari.


## v66 — link any local file extension from an HTML page

In the sandboxed local HTML preview, relative hyperlinks no longer stop at a
short allowlist of HTML/CSS/images/PDF. The `/site/` route now identifies the
linked file within the configured root and delegates non-static files to the
same `/view` handler used by the original-style listing:

- PDF links use the built-in byte-range PDF viewer.
- JPG/PNG/GIF/WebP and other passive image resources remain directly served.
- EPUB, DjVu, PS/EPS, Markdown, JSON, XML, notebook and text links go to their
  existing viewers/converters where available.
- ZIP/JAR/TAR archives show read-only contents.
- Unsupported or unknown binary types use the existing bounded download route.

This is link support, not a promise that every binary format has a renderer.
Scripts are not served as active script resources; a clicked .js file opens as
escaped source text, and document CSP continues to prevent script execution.
All links remain restricted by the same filesystem boundary and size limits;
URLs outside the root and unknown/missing files remain rejected. External
and absolute file:/// links are not rewritten automatically.

Regression coverage: tests/test_html_preview.py.


## v67 — previews stay in the current tab

The styled listing previously opened PDF, HTML, images, books and archives
with `window.open(..., "_blank")`, and PDF builds likewise used a separate
tab. This prevented ordinary browser Back from returning to the listing.

File View and Build now navigate in the **same tab** using normal browser
history. The original listing URL retains the current path, page, sort and
filter, so Back returns to the previous listing view. The change applies to
clicks **in the ZEFM listing**; explicit `target="_blank"` links inside
a user's own HTML documents, Ctrl/Cmd-click, and browser new-tab commands
still follow normal browser behavior. Navigation remains root-confined.

Regression coverage: `tests/test_same_tab_navigation.py`.


## v68 — links to local directories and filesystem paths

Relative HTML hyperlinks to an existing folder (with or without a
trailing slash) now redirect to the standard ZEFM directory listing.
The `/site/` validator allows one trailing slash but still forbids
traversal components and paths leaving the browser root.

For existing files under the configured root, HTML attributes `href`
and `src` containing `file:///...`, `file://localhost/...`, or
absolute filesystem/root-relative paths are mapped to safe `/site/`
URLs. Nonlocal links are not rewritten. The destination uses the same
file-extension dispatch as the directory listing; files outside the
root remain inaccessible. Unlike a full HTML parser, attribute
rewriting targets quoted attributes and does not attempt to fix
JavaScript-generated links, CSS URLs, or arbitrary URL schemes.
The browser remains loopback-only.

Tests: `tests/test_html_preview.py`; live-browser verification required.


## v69 — correct JPEG and PNG binary signatures

The image View handler previously checked literal backslash-escaped text
instead of binary JPEG/PNG magic bytes, producing `Invalid image signature`
for valid images. `server/image_preview.py` now performs the appropriate
binary checks using `bytes.fromhex`. It also verifies the WebP RIFF/WEBP
marker and AVIF ftyp brand rather than just a generic prefix, with bounded
reading and size limits. All image files still require being within the
configured browser root. Tests: `tests/test_image_preview.py`.


## v70 — CSV/TSV tables and complete filetype jump index

Opening `.csv` or `.tsv` from the file listing (or a local HTML
hyperlink) renders a read-only HTML table, with the first row used as
column headings and browser-escaped cell contents. A **Markdown table**
link gives a Markdown source representation. The Python stdlib `csv`
parser handles quoted fields, commas, Unicode and multiline fields.
For TSV, it uses a tab delimiter. The preview is limited to 2 MiB input,
1,000 rows, 100 columns, and 12,000 characters per cell. No files are
modified and no spreadsheet formulas are evaluated.

When **Sort by → File Type** is selected, a compact, complete alphabetical
extension index appears above the file list. Each entry shows the
extension and count of matching files and jumps directly to that type's
page; all available types in the selected directory are shown, including
those beyond the first two pages. The existing bottom GoFM references
are also fully visible for File Type mode; other sort modes retain their
progressive page references. The extension list reflects the current
directory and any filename filter, not every extension supported by the
system globally.

Tests: `tests/test_delimited_and_filetype_index.py`.


## v71 — preview readable files before downloading

- `.yid` is a Yiddish UTF-8 text file, shown in a browser `<pre>` with
  `lang="yi"`, `dir="rtl"`, preserved line breaks, and escaped contents.
- `.info` is treated as ordinary text.
- Additional text/source extensions and SVG source use safe escaped text
  preview. SVG is not executed as an active graphic in this mode.
- Unknown extensions are no longer automatically downloaded. View reads
  at most 4 MiB, checks UTF-8 decoding and rejects NUL bytes or binary
  control characters, then displays likely text as escaped HTML.
- Known binary formats still download unless a specific viewer exists.
  Unknown likely-binary files fall back to the existing bounded Download
  route. Files larger than the preview cap also fall back to Download.
- Preview limits are independent of Quick Edit's 1 MiB safety limit;
  an inline text preview does not imply that editing is available.

Run `python3 -m unittest tests.test_text_preview
tests.test_text_view_http tests.test_extension_registry_v62 -v` from `python/`.
Regression tests cover RTL Hebrew/Yiddish Unicode, escaped markup,
plain Info files, arbitrary unknown UTF-8 extensions, and binary fallback.


## v72 — INFO80.md inline color spans

Discount's Markdown preview intentionally uses `nohtml` to suppress raw
HTML from untrusted Markdown. The user's Roku `INFO80.md` has inline
`<span style=color:orange>label</span>` labels, which were previously
suppressed by this setting. The Markdown adapter now protects only simple
foreground-color spans with an explicit small allowlist (orange, red,
blue, green, purple, gray/grey, black), renders Markdown with the same
`nohtml` option, and restores the labels as escaped-text HTML color
spans afterward. Arbitrary inline HTML is **not enabled**. Markdown PDF
build uses the same transformation.

The fallback when Discount is not installed remains the readable, escaped
Markdown source, rather than pretending to render formatted Markdown.
Tests: `python3 -m unittest tests.test_markdown_inline_spans -v`.
This addresses the stripped-label case; other Markdown preview failures
should be diagnosed using the exact HTTP error/visible output.


## v73 — Search String: browser text-content search

The styled file manager's previously disabled `Search String` control now
opens `/search-text?path=...` with the current directory. The existing
filename filter remains unchanged. The new search finds text *within* files,
including nested directories, and lists escaped file paths, line numbers,
and excerpts. Click a result to View that file in the same browser tab;
Back returns to the search results.

The search is read-only and confined to the selected browser root. It
excludes hidden entries, symlinks, recognized binary file formats, files
larger than 1 MiB and invalid UTF-8. Bounds: 8 levels deep, 100
directories, 5,000 entries, 500 candidate text files, 12 MiB read in
total, 100 results. Reaching a bound yields an incomplete-results notice.
Default matching uses Unicode `casefold()`; an optional case-sensitive
checkbox switches to exact substring matching. No SQL, external search
service, or shell is involved.

Tests: `tests/test_content_search.py`. The workflow also runs
`compileall` to catch Python syntax regressions before the main suite.
Legacy ServPakDir `Search.java` semantics still require source-level
comparison; this is a safe workflow adaptation, not a parity claim.


## v74 — New File browser operation (FileOps adaptation)

The styled original ZEFM listing's previously disabled **New File** control
now opens a dedicated form scoped to the current directory. The basic listing
provides the same action. After creating the file, the response links to
**Quick edit new file** or **Back to directory**. The styled listing carries
its page, filename filter and sort state to the form and back.

Creation uses `LocalFiles.create_file()`: only one validated UTF-8 filename,
within the configured browsing root; a new empty file is created with owner
read/write (subject to umask) using `os.open(O_CREAT|O_EXCL)`.
Existing files, directories and symlinks are **never overwritten**.
The GET form validates the directory, and the POST requires the current
loopback session's CSRF token, allowed form keys, and a valid same-origin
return URL. No code runs, no SQL is used, and the editor's unsaved buffers
are not changed.

Tests: `tests/test_new_file_workflow.py` plus all existing file-manager
tests. This is a safe Python adaptation of a FileOps workflow, not yet
confirmed as verbatim Java method parity.


The v74 New File result also offers **Open new file in ZEFM editor** when the
desktop callback is available, using the existing CSRF-protected
`/open-editor` route and Tk-thread scheduling bridge. Browser-only mode
keeps Quick Edit and Back links. The operation is intentionally
non-destructive and does not alter current editor buffers.


## v75 — source-guided cross-directory copy

The Copy form now accepts a filename and a **Destination directory**
relative to the selected browser root, defaulting to the source
directory. It can create a new filename in that directory or copy
into another existing directory. Existing two-argument
`LocalFiles.copy_file` calls and browser Copy POSTs without the new
parameter still copy within the source directory. No target can
be overwritten, including symlinks.

After copying, the page offers **Back to source directory** (retaining
the original listing state) and **Open destination directory**. The
original source is preserved. No Notes are copied to the destination.
The safe, bounded implementation and tests are based on the behavior
of `NetsManager/XCommands.java`'s `runC` Copy path.

Regression test: `python3 -m unittest tests.test_copy_to_directory -v`.
Retest existing `tests.test_file_operations` as well.
