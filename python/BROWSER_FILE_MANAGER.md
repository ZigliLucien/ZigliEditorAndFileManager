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
