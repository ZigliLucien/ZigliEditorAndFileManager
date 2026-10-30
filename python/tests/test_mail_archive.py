"""Offline tests; use synthetic messages, never personal Maildir data."""
from email.message import EmailMessage
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import tempfile
import unittest

from zefm.server.mail_archive import MailArchive, MailArchiveError, discover_maildirs, message_body
from zefm.server.mail_http import MailBrowser
from zefm.storage.word_notes import WordNotes
from zefm.server.http import note_version


class MailFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.maildir = self.home / 'Maildir'
        for sub in ('cur', 'new', 'tmp'):
            (self.maildir / sub).mkdir(parents=True)
        msg = EmailMessage()
        msg['Subject'] = 'français <script>bad()</script> ייִדיש'
        msg['From'] = 'Someone <test@example.invalid>'
        msg['Message-ID'] = '<stable@example.invalid>'
        msg.set_content('שלום עולם\nBonjour cœur!\n<script>plain text</script>', charset='utf-8')
        self.mail = self.maildir / 'new' / 'first-message'
        self.mail.write_bytes(msg.as_bytes())
        self.accounts = {'Personal': str(self.maildir)}


class MailArchiveTests(MailFixture):
    def test_auto_discovery(self):
        self.assertEqual(discover_maildirs(self.home), {'SIU': str(self.maildir)})

    def test_headers_unicode_and_plain_text(self):
        a = MailArchive(self.accounts)
        entry, subject, sender, _date = a.listing('Personal')[0]
        self.assertIn('ייִדיש', subject)
        self.assertIn('test@example.invalid', sender)
        headers, body, note_key = a.message('Personal', entry.key)
        self.assertIn('cœur', body)
        self.assertIn('français', headers['Subject'])
        self.assertTrue(note_key.startswith('maildir://Personal/'))

    def test_maildir_new_cur_rename_retains_identity(self):
        a = MailArchive(self.accounts)
        key = a.listing('Personal')[0][0].key
        note_key = a.message('Personal', key)[2]
        self.mail.rename(self.maildir / 'cur' / 'first-message:2,S')
        self.assertEqual(a.listing('Personal')[0][0].key, key)
        self.assertEqual(a.message('Personal', key)[2], note_key)

    def test_unknown_account_and_bad_message_id(self):
        a = MailArchive(self.accounts)
        with self.assertRaises(MailArchiveError):
            a.listing('../etc')
        with self.assertRaises(MailArchiveError):
            a.message('Personal', '../other')

    def test_html_only_is_flat_text_and_not_script(self):
        msg = EmailMessage()
        msg.set_content('<p>Hello <b>world</b><script>alert(1)</script></p>', subtype='html')
        body = message_body(msg)
        self.assertIn('Hello world', body)
        self.assertNotIn('alert(1)', body)

    def test_attachments_are_not_displayed(self):
        msg = EmailMessage()
        msg.set_content('Plain text')
        msg.add_attachment(b'secret binary', maintype='application',
                           subtype='octet-stream', filename='secret.bin')
        self.assertEqual(message_body(msg).strip(), 'Plain text')


class MailBrowserTests(MailFixture):
    def setUp(self):
        super().setUp()
        self.notes = self.home / 'notes.json'
        self.browser = MailBrowser(self.accounts, notes_path=self.notes)
        self.browser.start()
        self.addCleanup(self.browser.close)
        self.entry = self.browser.archive.listing('Personal')[0][0]

    def request(self, route, data=None, host=None):
        body = urlencode(data).encode('utf-8') if data is not None else None
        request = Request(self.browser.url.rstrip('/') + route, data=body,
                          headers={'Content-Type': 'application/x-www-form-urlencoded'} if body else {})
        if host is not None:
            request.add_header('Host', host)
        try:
            with urlopen(request, timeout=4) as response:
                return response.status, response.read().decode('utf-8'), dict(response.headers)
        except HTTPError as err:
            return err.code, err.read().decode('utf-8'), dict(err.headers)

    def test_accounts_and_escaped_messages(self):
        status, html, _ = self.request('/')
        self.assertEqual(status, 200)
        self.assertIn('Personal', html)
        status, html, _ = self.request('/messages?' + urlencode({'account': 'Personal'}))
        self.assertEqual(status, 200)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>bad()', html)
        status, html, headers = self.request('/message?' + urlencode({
            'account': 'Personal', 'id': self.entry.key}))
        self.assertEqual(status, 200)
        self.assertIn('שלום עולם', html)
        self.assertNotIn('<script>plain text</script>', html)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertIn("default-src 'none'", headers['Content-Security-Policy'])

    def test_notes_save_and_stale_conflict(self):
        fields = {'csrf': self.browser.token, 'account': 'Personal', 'id': self.entry.key,
                  'digest': note_version(None), 'word': 'ייִדיש', 'content': 'a local note'}
        status, html, _ = self.request('/note?' + urlencode({'account': 'Personal',
                                                              'id': self.entry.key}))
        self.assertEqual(status, 200)
        self.assertIn('Save Note', html)
        status, _, _ = self.request('/note', fields)
        self.assertEqual(status, 200)
        note_key = self.browser.archive.message('Personal', self.entry.key)[2]
        self.assertEqual(WordNotes(self.notes).get(note_key, 'ייִדיש')['data'], 'a local note')
        status, _, _ = self.request('/note', fields)
        self.assertEqual(status, 409)

    def test_csrf_and_host_rejected(self):
        fields = {'csrf': 'bad', 'account': 'Personal', 'id': self.entry.key,
                  'digest': note_version(None), 'word': 'test', 'content': 'text'}
        self.assertEqual(self.request('/note', fields)[0], 403)
        self.assertFalse(self.notes.exists())
        self.assertEqual(self.request('/', host='example.org')[0], 403)

    def test_unknown_message_rejected(self):
        status, _, _ = self.request('/message?' + urlencode({'account': 'Personal', 'id': '../etc'}))
        self.assertEqual(status, 400)


if __name__ == '__main__':
    unittest.main()
