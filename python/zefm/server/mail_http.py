"""Local, read-only Maildir browser with separately stored word annotations.

CLI: python3 -m zefm.server.mail_http --maildir SIU=~/Maildir
"""
from __future__ import annotations

import argparse
import secrets
import threading
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit

from .http import page, note_version
from .mail_archive import MailArchive, MailArchiveError, discover_maildirs
from ..storage.word_notes import WordNotes


class MailBrowser:
    def __init__(self, maildirs, port=0, notes_path=None):
        self.archive = MailArchive(maildirs)
        self.token = secrets.token_urlsafe(32)
        archive, token = self.archive, self.token
        note_lock = threading.RLock()

        class Handler(BaseHTTPRequestHandler):
            server_version = 'ZEFM-mail-local/1'

            def log_message(self, format, *args):
                pass  # Do not log message subjects, IDs or addresses.

            def _send(self, status, content):
                self.send_response(status)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Referrer-Policy', 'no-referrer')
                self.send_header('Content-Security-Policy',
                                 "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
                self.end_headers()
                self.wfile.write(content)

            def _params(self, query):
                parsed = parse_qs(query, encoding='utf-8', errors='strict',
                                  max_num_fields=8, keep_blank_values=True)
                if any(len(v) != 1 for v in parsed.values()):
                    raise MailArchiveError('Duplicate form parameter')
                return {k: v[0] for k, v in parsed.items()}

            def _check_host(self):
                port = self.server.server_address[1]
                if self.headers.get('Host') not in (f'127.0.0.1:{port}', f'localhost:{port}'):
                    raise PermissionError('Invalid Host header')

            def _message_info(self, params):
                account, key = params.get('account', ''), params.get('id', '')
                if not account or not key:
                    raise MailArchiveError('Missing message selection')
                return account, key, *archive.message(account, key)

            def _back(self, account):
                return '<p><a href="/messages?' + escape(urlencode({'account': account}), quote=True) + '">← Messages</a></p>'

            def do_GET(self):
                try:
                    self._check_host()
                    route = urlsplit(self.path)
                    params = self._params(route.query)
                    if route.path == '/':
                        rows = ''.join('<li><a href="/messages?' +
                                       escape(urlencode({'account': label}), quote=True) + '">' + escape(label) + '</a></li>'
                                       for label in archive.accounts)
                        self._send(200, page('Email accounts',
                                '<h1>Local email archives</h1><ul>' + rows + '</ul>'
                                '<p>Read-only Maildir view. No mail is sent or fetched.</p>'))
                    elif route.path == '/messages':
                        account = params.get('account', '')
                        rows = []
                        for entry, subject, sender, date in archive.listing(account):
                            url = '/message?' + escape(urlencode({'account': account, 'id': entry.key}), quote=True)
                            rows.append(f'<tr><td><a href="{url}">{escape(subject)}</a></td>'
                                        f'<td>{escape(sender)}</td><td>{escape(date)}</td></tr>')
                        self._send(200, page('Email: ' + account,
                            '<p><a href="/">← Accounts</a></p>'
                            f'<h1>{escape(account)} — recent messages</h1>'
                            '<table><tr><th>Subject</th><th>From</th><th>Date</th></tr>' +
                            ''.join(rows) + '</table><p>Up to 100 messages; newest files first.</p>'))
                    elif route.path in ('/message', '/note'):
                        account, key, headers, body, note_key = self._message_info(params)
                        back = self._back(account)
                        if route.path == '/message':
                            metadata = ''.join(f'<p><strong>{escape(name)}:</strong> {escape(value)}</p>'
                                               for name, value in headers.items() if value)
                            note_link = '/note?' + escape(urlencode({'account': account, 'id': key}), quote=True)
                            self._send(200, page('Email message', back +
                                '<h1>Message</h1>' + metadata + '<h2>Body</h2>'
                                f'<pre>{escape(body)}</pre><p><a href="{note_link}">Notes for this message</a></p>'
                                '<p>Attachments and active HTML are not displayed.</p>'))
                        else:
                            word = params.get('word', '')
                            if len(word) > 500:
                                raise MailArchiveError('Note word is too long')
                            with note_lock:
                                store = WordNotes(notes_path)
                                notes = store.for_file(note_key)
                                current = store.get(note_key, word) if word else None
                            lines = ''.join('<li><a href="/note?' +
                                            escape(urlencode({'account': account, 'id': key, 'word': n['word']}), quote=True) +
                                            '">' + escape(n['word']) + '</a></li>' for n in notes)
                            word_input = (f'<input type="hidden" name="word" value="{escape(word,quote=True)}">'
                                          f'<strong>{escape(word)}</strong>' if word else
                                          '<label>Word or phrase: <input name="word" maxlength="500" required></label>')
                            fields = ''.join(f'<input type="hidden" name="{k}" value="{escape(v,quote=True)}">'
                                             for k, v in (('csrf', token), ('account', account), ('id', key),
                                                          ('digest', note_version(current))))
                            self._send(200, page('Email Notes', back +
                                f'<h1>Notes for message: {escape(headers["Subject"])}</h1>'
                                f'<ul>{lines}</ul><form action="/note" method="post" accept-charset="utf-8">'
                                + fields + word_input +
                                '<p><button type="submit">Save Note</button></p>'
                                f'<textarea name="content" aria-label="Note text">{escape(current["data"] if current else "")}</textarea>'
                                '<p><button type="submit">Save Note</button></p></form>'))
                    else:
                        self._send(404, page('Not found', '<h2>Unknown mail route</h2>'))
                except PermissionError as exc:
                    self._send(403, page('Forbidden', f'<h2>{escape(str(exc))}</h2>'))
                except (MailArchiveError, OSError, UnicodeError, ValueError) as exc:
                    self._send(400, page('Mail error', f'<h2>{escape(str(exc))}</h2>'))

            def do_POST(self):
                try:
                    self._check_host()
                    if urlsplit(self.path).path != '/note':
                        raise MailArchiveError('Unknown mail form')
                    if self.headers.get('Content-Type', '').split(';', 1)[0].strip() != 'application/x-www-form-urlencoded':
                        raise MailArchiveError('Expected form submission')
                    n = int(self.headers.get('Content-Length', '0'))
                    if n <= 0 or n > 1024 * 1024:
                        raise MailArchiveError('Form is too large')
                    params = self._params(self.rfile.read(n).decode('utf-8', 'strict'))
                    if not secrets.compare_digest(params.get('csrf', ''), token):
                        raise PermissionError('Invalid form token')
                    if set(params) != {'csrf', 'account', 'id', 'digest', 'word', 'content'}:
                        raise MailArchiveError('Missing or extra form parameters')
                    account, key, _headers, _body, note_key = self._message_info(params)
                    word = params['word'].strip()
                    if not word or len(word) > 500 or len(params['content'].encode('utf-8')) > 500000:
                        raise MailArchiveError('Invalid note word or text length')
                    with note_lock:
                        store = WordNotes(notes_path)
                        old = store.get(note_key, word)
                        if note_version(old) != params['digest']:
                            self._send(409, page('Note changed', '<h2>Note changed elsewhere; reopen before saving.</h2>'))
                            return
                        store.put(note_key, word, params['content'], link=old['link'] if old else '')
                    self._send(200, page('Note saved',
                        '<h2>Saved Note</h2><p><a href="/note?' +
                        escape(urlencode({'account': account, 'id': key}), quote=True) + '">Back to Notes</a></p>'))
                except PermissionError as exc:
                    self._send(403, page('Forbidden', f'<h2>{escape(str(exc))}</h2>'))
                except (MailArchiveError, ValueError, OSError, UnicodeError) as exc:
                    self._send(400, page('Mail error', f'<h2>{escape(str(exc))}</h2>'))

        self.server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
        self.server.daemon_threads = True
        self.thread = None

    @property
    def url(self):
        return f'http://127.0.0.1:{self.server.server_address[1]}/'

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True,
                                           name='ZEFM Maildir browser')
            self.thread.start()
        return self.url

    def close(self):
        if self.thread is not None:
            self.server.shutdown()
            self.thread.join(timeout=3)
            self.thread = None
        self.server.server_close()


def main():
    parser = argparse.ArgumentParser(description='Read-only local Maildir browser')
    parser.add_argument('--maildir', action='append', default=[], metavar='NAME=PATH',
                        help='Maildir account location (repeat for multiple accounts)')
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    accounts = discover_maildirs()
    if args.maildir:
        accounts = {}
        for item in args.maildir:
            name, sep, directory = item.partition('=')
            if not sep:
                parser.error('--maildir expects NAME=PATH')
            accounts[name] = directory
    if not accounts:
        parser.error('No Maildir folders found; use --maildir NAME=PATH')
    server = MailBrowser(accounts, port=args.port)
    print(server.start(), flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()


if __name__ == '__main__':
    main()
