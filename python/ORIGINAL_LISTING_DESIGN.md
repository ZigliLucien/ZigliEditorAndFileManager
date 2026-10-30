# Reconstructing the original ZEFM listing interface (v48)

## Original sources inspected

The available historical ZIP/JAR archives and the source tree contain
**`lister.xsl`**, not a file literally named `listing.xsl`.
The listing page is assembled from several components, which explain why
recreating the stylesheet alone would miss much of the design:

| Original Java/XML resource | Role | Python/JavaScript replacement |
|---|---|---|
| `TTT/ServPak/xsl/lister.xsl` | Main three-column file table, file-operation radios, striped row classes | `zefm/server/listing_view.py` and `listing.js` |
| `TTT/ServPak/xsl/locxsorter.xsl` | Sort transformation, metadata, notes, operation form | JavaScript sort selectors |
| `TTT/ServPak/css/listing.css` | Pale yellow/cyan rows, small caps, blue filenames, colored operations, gray metadata, checked directory cells | `zefm/server/listing.css` |
| `TTT/ServPak/js/listing.js` | Keyboard navigation and operation selection, clock, file searches | `zefm/server/listing.js` |
| `NetsManager/Xlster.java` | Breadcrumbs, `zefm@hostname`, utility links, four-column directory grid, sort/update panel, pagination | Same browser assets; Python directory JSON |
| `NetsManager/XCommands.java` | Generate XML `filedata` records containing `filename`, `sdt`, `timekey`, `filetype`, `key1`, `key2`, `annotation`; omit dotfiles | `listing_data` filesystem/Notes JSON |
| `ServPakDir/ServPak/jv/GoFM.java` | Serve stored listings, page fragments `HEADERn` | JSON API + client-side 25-row pagination |
| `TTT/ServPak/xql/sorter.xql` / `TTT/ServPak/xsl/xsort.xsl` | XQuery/XSL-based sorting by filename, type, date and keyword | JavaScript client-side sorting |
| `TTT/ServPak/xsl/shownotes.xsl` and `tpw.xsl` | Legacy XML note and TPW document presentation | Existing read-only/annotatable JSON Notes views; rich TPW rendering not yet ported |

The historical stylesheet references `listing.css` and `listing.js` and
uses the original operation codes `VVV` (view), `CCC` (copy), `MMM`
(move), `XXX` (delete), `EEE` (edit), `QQQ` (quick edit) and
`AAA` (annotate). The new listing retains their *visual identity* without
restoring unsafe or unimplemented operations.

## Visual reconstruction

The v48 browser presents:

- A **breadcrumb/title area** across the top, plus a right-aligned
  `zefm@hostname` utility menu.
- A **sort/update/clock** panel to the left of a four-column directory matrix
  with alternating light-gray/white cells and muted blue/teal links.
- The original **colored operation-radio strip** before the file table:
  view black, copy red, move dark red, delete orange, edit blue,
  quick edit green, note magenta.
- The three-column **Filename / Size–Date–Time / Notes** table, with
  alternating `#ffffee` and `#eeffff` rows, blue filename buttons,
  gray centered metadata and inline Notes previews.
- A numbered **25-files-per-page** reference strip, analogous to the
  original paginated `GoFM` view.
- Keyboard conveniences: up/down move between filename buttons;
  `V,C,E,Q,N` select supported operations; `U` goes to the parent;
  `F` or `/` focuses the filename filter; `R` refreshes.

Move and delete are intentionally **disabled** until their guarded back-end
implementations exist. New File, Search String and database Text Search are
shown as disabled historical controls. The existing **Create folder** and
**Copy...** back-end operations work without enabling deletion.

## Architecture

`GET /listing?path=...` returns a semantic HTML shell with a restrictive CSP.
Local `/listing.css` and `/listing.js` reproduce the historical design.
`GET /api/files?path=...` returns UTF-8 JSON containing confined relative
paths, subdirectories, file size, timestamp, type and a shortened Notes preview.
The browser uses `document.createElement` and `textContent`, **never
`innerHTML`**, for these untrusted values.

The original Python-generated HTML listing remains available at `/` and
`/browse`. It includes a link to the new original-style presentation.
Opening the file manager from the Tk File menu now visits `/listing`.

- No XML intermediary or XSLT engine is used by this listing.
- Only the already configured loopback server exposes the JSON endpoint.
- Existing CSRF/Host/path/size/write checks still apply to write operations.
- A 3,000-entry ceiling bounds the JSON response for very large directories.
- The original styled listing hides dotfiles, as the Java implementation did.
  The basic listing can still show them.
- Notes are read from the current JSON Notes store; the old MyISAM database
  contents are **not** assumed to have been migrated.
- The browser uses client-side pagination, not the cached XML `HEADERn`
  fragments from the original Java implementation.

## Trying it

From the checkout:

```sh
git switch python-port
git pull --ff-only
cd python
python3 -m zefm.editor.gui.tk_editor
```

Use **File → Open Local File Manager in Browser...**. The Tk editor launches
the reconstructed original listing. Alternatively run:

```sh
python3 -m zefm.server.http --root "$HOME/Documents"
```

Then visit the printed local URL with `listing` appended.
Choose **Basic listing** to compare the old Python interface.

## Fidelity notes

This is a design reconstruction from the archived original sources, not a
byte-for-byte replay of the old HTML: browser layout engines differ, the
directory/item counts may differ, legacy formatted TPW annotations are not
rendered as HTML, and the old SQL-only operations do not run. We have kept
the characteristic visual structure and color choices while preserving the
new Python server's safety boundaries.

## v49 — GoFM.java paging behavior

The original `usr/Project/ServPakDir/ServPak/jv/GoFM.java` has two
distinct page types: `directory^0` reloads the complete top listing,
whereas `directory^N` extracts the `HEADERN` section from compressed
XML using XQuery. The page heading is `directory : Listing N`.
Its **Top** and **Bottom** links jump to page 0 and the final page.
`Xlster.reffout` provides a *progressively extended reference strip*
through the current/next page, in roughly ten columns; filename-sort
references use a short filename prefix, file-type-sort references show the
extension, and other sorting modes show numbers. `Xlster` starts a new
`HEADER` every 25 file rows for ordinary sorting, but **starts a new page
whenever the file type changes** for file-type sorting.

The v49 JavaScript frontend now reproduces these behaviors without keeping
XML `HEADERN` fragments or a MySQL `listings` table:

- **Top**, **Previous**, **Listing N of M**, **Next**, and **Bottom**
  controls; Top selects the first file page and scrolls to the directory
  overview, rather than fetching a separate HTML page.
- Page references grow through the next page; ten columns preserve the
  original visual rhythm. Filename references use the first four characters,
  and file-type references use the extension.
- 25-file chunks for filename, date, size and Notes ordering; **one page per
  file extension** when File Type is selected. Files remain in logical
  filename order inside each type group.
- Deep links use `/listing?path=...&page=N` (1-based). Navigating pages
  participates in browser history, so Back/Forward restores the file page.
- Sorting or filtering resets to the first page. Refresh keeps the
  current page where it still exists. Page numbers are safely clamped
  if contents change.
- No network access beyond ZEFM localhost; page state and grouping happen
  in the existing JavaScript/JSON frontend.

Unlike the original cached `HEADER` system, the four-column directory
grid stays in the page header while files are paged below. We preserve
the directory overview without an extra server round trip. We also avoid
the original automatic page reload on missing XML/SQL state.
