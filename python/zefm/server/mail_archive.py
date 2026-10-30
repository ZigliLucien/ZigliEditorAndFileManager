"""Read-only Maildir index and safe MIME-to-text conversion for local ZEFM mail.

No mail retrieval, outbound network requests, attachment extraction, HTML
rendering, or modifications to Maildir files.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from email import policy
from email.parser import BytesHeaderParser, BytesParser
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

MAX_MAIL_BYTES = 5 * 1024 * 1024
MAX_LIST = 100
MAX_SCAN = 10000


def discover_maildirs(home=None, config=None):
    """Detect familiar maildirs, or use an explicit local JSON name:path map."""
    base = Path(home).expanduser() if home is not None else Path.home()
    cfg = Path(config).expanduser() if config is not None else base / '.config' / 'zefm' / 'maildirs.json'
    if cfg.is_file():
        mapping = json.loads(cfg.read_text(encoding='utf-8'))
        if not isinstance(mapping, dict) or not mapping or not all(
                isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
                for k, v in mapping.items()):
            raise ValueError('maildirs.json must be an object mapping account labels to folders')
        return {k: str(Path(v).expanduser()) for k, v in mapping.items()}
    roots = {'SIU': base / 'Maildir', 'Personal': base / 'Maildir' / 'Personal',
             'GMAIL': base / 'Maildir' / 'GMAIL'}
    return {k: str(v) for k, v in roots.items() if any((v / part).is_dir() for part in ('cur', 'new'))}


class MailArchiveError(ValueError):
    pass


@dataclass(frozen=True)
class MailEntry:
    account: str
    key: str
    path: Path
    mtime: float
    size: int


class _HTMLToText(HTMLParser):
    """Extract readable text; scripts, style, and external resources are ignored."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in ('script', 'style', 'head', 'svg'):
            self.hidden += 1
        if self.hidden == 0 and tag in ('p', 'br', 'div', 'li', 'tr', 'h1', 'h2', 'h3'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag.lower() in ('script', 'style', 'head', 'svg'):
            self.hidden = max(0, self.hidden - 1)
        if self.hidden == 0 and tag.lower() in ('p', 'div', 'li', 'tr'):
            self.parts.append('\n')

    def handle_data(self, data):
        if self.hidden == 0:
            self.parts.append(data)

    def text(self):
        return unescape(''.join(self.parts)).strip()


def _part_text(part):
    try:
        result = part.get_content()
    except (LookupError, UnicodeError, ValueError, AssertionError):
        raw = part.get_payload(decode=True) or b''
        result = raw.decode('utf-8', errors='replace')
    return result if isinstance(result, str) else ''


def message_body(message):
    """Choose a text/plain part, otherwise flatten HTML to escaped display text."""
    parts = list(message.walk()) if message.is_multipart() else [message]
    for kind in ('text/plain', 'text/html'):
        for part in parts:
            if part.is_multipart() or part.get_content_disposition() == 'attachment':
                continue
            if part.get_content_type() == kind:
                body = _part_text(part)
                if kind == 'text/html':
                    parser = _HTMLToText()
                    parser.feed(body)
                    return parser.text()
                return body
    return '[No plain-text message body; attachments are not displayed.]'


class MailArchive:
    def __init__(self, accounts):
        if not isinstance(accounts, dict) or not accounts:
            raise MailArchiveError('No Maildir accounts configured')
        self.accounts = {}
        for label, directory in accounts.items():
            if not isinstance(label, str) or not label.strip() or '/' in label or '\\' in label:
                raise MailArchiveError('Invalid account label')
            root = Path(directory).expanduser().resolve()
            if not root.is_dir() or not any((root / p).is_dir() for p in ('new', 'cur')):
                raise MailArchiveError(f'Not a Maildir: {root}')
            self.accounts[label] = root

    def _entries(self, account):
        if account not in self.accounts:
            raise MailArchiveError('Unknown mail account')
        root = self.accounts[account]
        found = {}
        scanned = 0
        for sub in ('cur', 'new'):
            folder = root / sub
            if not folder.is_dir() or folder.is_symlink():
                continue
            for path in folder.iterdir():
                scanned += 1
                if scanned > MAX_SCAN:
                    break
                if path.is_symlink() or not path.is_file():
                    continue
                # Ignore Maildir flags; moving a message between new/cur keeps its ID.
                original = path.name.split(':2,', 1)[0]
                identifier = hashlib.sha256((account + '\0' + original).encode('utf-8')).hexdigest()
                stat = path.stat()
                entry = MailEntry(account, identifier, path, stat.st_mtime, stat.st_size)
                if identifier not in found or entry.mtime > found[identifier].mtime:
                    found[identifier] = entry
            if scanned > MAX_SCAN:
                break
        return found

    def listing(self, account, limit=MAX_LIST):
        entries = sorted(self._entries(account).values(), key=lambda e: (-e.mtime, e.key))[:limit]
        rows = []
        for entry in entries:
            with entry.path.open('rb') as f:
                sample = f.read(32768)
            header = BytesHeaderParser(policy=policy.default).parsebytes(sample)
            rows.append((entry, str(header.get('Subject', '(no subject)')),
                         str(header.get('From', '')), str(header.get('Date', ''))))
        return rows

    def message(self, account, key):
        entry = self._entries(account).get(key)
        if entry is None:
            raise MailArchiveError('Message not found')
        if entry.size > MAX_MAIL_BYTES:
            raise MailArchiveError('Message is too large for browser preview')
        raw = entry.path.read_bytes()
        if len(raw) > MAX_MAIL_BYTES:
            raise MailArchiveError('Message is too large for browser preview')
        message = BytesParser(policy=policy.default).parsebytes(raw)
        msgid = str(message.get('Message-ID', '')).strip()
        identity = msgid if msgid else entry.path.name.split(':2,', 1)[0]
        digest = hashlib.sha256((account + '\0' + identity).encode('utf-8')).hexdigest()
        note_key = f'maildir://{account}/{digest}'
        headers = {name: str(message.get(name, '')) for name in ('Subject', 'From', 'To', 'Date', 'Message-ID')}
        return headers, message_body(message), note_key
