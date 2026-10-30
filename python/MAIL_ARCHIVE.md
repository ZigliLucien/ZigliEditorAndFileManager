# ZEFM v44 — local Maildir browser

This is a first, source-guided replacement for the mail **reading and
annotation** portion of the original Java `XmlMail`, `MailRun`, and
`ServPakDir/Email` workflow. The Python component intentionally does **not**
replace getmail, DavMail, the existing browser-generated HTML index, or
Emacs-based message composition.

## Launch in the editor

Use **File → Open Local Email Archive in Browser...**

The command discovers Maildir folders at:

- `~/Maildir` (label `SIU`)
- `~/Maildir/Personal` (label `Personal`)
- `~/Maildir/GMAIL` (label `GMAIL`)

Only existing Maildir directories with `cur/` or `new/` are included.
If none exist, the editor offers a directory chooser; select a Maildir root.
For nonstandard locations, place a **local, untracked** JSON configuration at
`~/.config/zefm/maildirs.json`:

```json
{
  "SIU": "/home/you/Maildir",
  "Personal": "/home/you/Maildir/Personal",
  "GMAIL": "/home/you/Maildir/GMAIL"
}
```

Replace paths with your actual folders. The file is read at browser launch.
It must **never** be committed along with mail messages or personal Notes.

## Standalone command

From the `python/` repository directory:

```sh
python3 -m zefm.server.mail_http --maildir "Personal=$HOME/Maildir/Personal"
```

For additional accounts repeat `--maildir NAME=PATH`. Without this argument
the defaults or the local JSON file are used. The service prints a random
loopback URL and runs until Ctrl+C.

## v44 features

- Browse explicitly configured accounts and their 100 most recently modified
  messages in Maildir `cur/` and `new/`; no SQL.
- Display subject, sender, date, message headers, and a **text-only** preview.
  Multipart messages prefer `text/plain`; an HTML-only message is reduced to
  plain text. No HTML is rendered as active content; no remote images or
  JavaScript, and no attachments are offered.
- The message's identity is an opaque hash: account + Message-ID where
  available, otherwise a Maildir filename identifier. A Maildir flag change
  from `new/` to `cur/` does not discard its Notes.
- **Notes for this message** stores annotations in the existing local
  `WordNotes` JSON store, keyed by message identity and word or phrase.
  The message file is never modified.
- Add/Edit Notes requires a one-session form token and an unchanged note
  revision; a stale form receives HTTP 409.

## Safety and limitations

This server is loopback-only (`127.0.0.1`) and intended for a trusted local
workstation, **not** exposure to the LAN or Internet. The browser has
`Cache-Control: no-store`, a restrictive CSP, and escaped output. As with
the file-manager browser, local processes can access its local HTTP port;
avoid running it on shared or untrusted workstations.

Maildir messages are **read only**. There is no mail retrieval, sending,
deletion, flag change, attachment download, search, or external command
execution. The listing is limited to the first 10,000 discovered files per
account and shows up to 100 recent messages; previews are capped at 5 MiB.
A later increment can add pagination/search, richer date sorting, and a link
to the user's existing HTML mail index. This version uses message file
modification time for ordering, not the email Date header.

The browser server shuts down when the Tk editor quits. Opening it from
a fresh editor process does not modify the user's existing mail pipeline.

## Tests

```sh
cd python
python3 -m unittest discover -s tests -v
```

Tests create **synthetic** local Maildir messages. No personal email data is
needed or bundled.
