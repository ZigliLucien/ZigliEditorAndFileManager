"""HTTP integration and path-safety regression tests for the v39 browser."""
import hashlib
from html import unescape
from pathlib import Path
import os
import re
import stat
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

from zefm.server.file_manager import BrowserError, LocalFiles, MAX_EDIT_BYTES
from zefm.server.http import BrowserServer


class FileManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "root"
        self.root.mkdir()
        self.outside = Path(self.tmp.name) / "outside.txt"
        self.outside.write_text("private")
        self.text = self.root / "bonjour français ייִדיש.txt"
        self.text.write_text('Bonjour <script>bad()</script>!\nייִדיש\n', encoding='utf-8')
        self.files = LocalFiles(self.root)
        self.srv = BrowserServer(str(self.root))
        self.srv.start()
        self.addCleanup(self.srv.close)

    def get(self, route="/", host=None):
        req=Request(self.srv.url.rstrip("/") + route)
        if host is not None:
            req.add_header("Host", host)
        try:
            with urlopen(req,timeout=4) as r:
                return r.status, r.read(),dict(r.headers)
        except HTTPError as err:
            return err.code,err.read(),dict(err.headers)

    def post(self, fields, host=None):
        data=urlencode(fields).encode('utf-8')
        req=Request(self.srv.url.rstrip("/") + '/edit',data=data,method='POST',
                    headers={"Content-Type":"application/x-www-form-urlencoded"})
        if host is not None:
            req.add_header("Host",host)
        try:
            with urlopen(req,timeout=4) as r:
                return r.status,r.read()
        except HTTPError as err:
            return err.code,err.read()

    def test_listing_unicode_links_and_html_escape(self):
        status,body,headers=self.get()
        self.assertEqual(status,200)
        self.assertIn('bonjour français ייִדיש.txt',body.decode())
        self.assertIn('Quick edit',body.decode())
        self.assertIn('no-store',headers['Cache-Control'])
        status,body,_=self.get('/view?'+urlencode({'path':self.text.name}))
        self.assertEqual(status,200)
        self.assertIn('&lt;script&gt;',body.decode())
        self.assertNotIn('<script>',body.decode())

    def test_directory_navigation(self):
        d=self.root/'folder';d.mkdir()
        (d/'example.txt').write_text('a')
        status,body,_=self.get('/browse?path=folder')
        self.assertEqual(status,200)
        self.assertIn('example.txt',body.decode())
        self.assertIn('Parent',body.decode())

    def test_guarded_text_save_roundtrip(self):
        status,body,_=self.get('/edit?'+urlencode({'path':self.text.name}))
        self.assertEqual(status,200)
        html=body.decode()
        m=re.search(r'name="digest" value="([0-9a-f]{64})"',html)
        self.assertIsNotNone(m)
        original_hash=m.group(1)
        new='français & ייִדיש \u05d1\u05bf\n'
        status,html=self.post({'csrf':self.srv.token,'path':self.text.name,
                               'digest':original_hash,'content':new})
        self.assertEqual(status,200,html)
        self.assertEqual(self.text.read_text(encoding='utf-8'),new)
        self.assertIn('Saved:',html.decode())
        status,_=self.post({'csrf':self.srv.token,'path':self.text.name,
                             'digest':original_hash,'content':'overwrite'})
        self.assertEqual(status,409)
        self.assertEqual(self.text.read_text(encoding='utf-8'),new)

    def test_bad_token_rejected_and_no_write(self):
        status,body=self.post({'csrf':'WRONG','path':self.text.name,
                               'digest':hashlib.sha256(self.text.read_bytes()).hexdigest(),
                               'content':'oops'})
        self.assertEqual(status,403)
        self.assertIn(b'Invalid form token',body)
        self.assertIn('Bonjour',self.text.read_text())

    def test_path_traversal_and_symlink_escape(self):
        for bad in ('../outside.txt','/etc/passwd','folder/../../outside.txt'):
            with self.subTest(bad=bad):
                status,_,_=self.get('/view?'+urlencode({'path':bad}))
                self.assertEqual(status,403)
        escape_link = self.root/'outside-link'
        escape_link.symlink_to(self.outside)
        status,_,_=self.get('/raw?path=outside-link')
        self.assertEqual(status,403)

    def test_host_header_restriction(self):
        status,_,_=self.get(host='evil.example')
        self.assertEqual(status,403)
        status,_=self.post({'csrf':self.srv.token,'path':self.text.name,
                            'digest':'0'*64,'content':'oops'},host='evil.example')
        self.assertEqual(status,403)

    def test_binary_quick_edit_rejected_but_downloads(self):
        (self.root/'binary.dat').write_bytes(b'abc\xff')
        status,_,_=self.get('/edit?path=binary.dat')
        self.assertEqual(status,415)
        status,data,headers=self.get('/raw?path=binary.dat')
        self.assertEqual(status,200)
        self.assertEqual(data,b'abc\xff')
        self.assertIn('attachment',headers['Content-Disposition'])

    def test_size_limit_and_unknown_routes(self):
        (self.root/'large.txt').write_bytes(b'x'*(MAX_EDIT_BYTES+1))
        status,_,_=self.get('/edit?path=large.txt')
        self.assertEqual(status,413)
        status,_,_=self.get('/run?cmd=whoami')
        self.assertEqual(status,404)

    def test_preserves_crlf_and_file_mode(self):
        p=self.root/'crlf.txt'
        p.write_bytes(b'one\r\ntwo\r\n')
        p.chmod(0o640)
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        status,body=self.post({'csrf':self.srv.token,'path':'crlf.txt',
                               'digest':digest,'content':'alpha\r\nbeta\r\n'})
        self.assertEqual(status,200,body)
        self.assertEqual(p.read_bytes(),b'alpha\r\nbeta\r\n')
        self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o640)

    def test_file_changed_before_save(self):
        digest=hashlib.sha256(self.text.read_bytes()).hexdigest()
        self.text.write_text('changed elsewhere')
        status,_=self.post({'csrf':self.srv.token,'path':self.text.name,
                            'digest':digest,'content':'stale'})
        self.assertEqual(status,409)
        self.assertEqual(self.text.read_text(),'changed elsewhere')

if __name__=='__main__':unittest.main()

class BrowserNotesTests(unittest.TestCase):
    def test_read_only_word_notes_for_a_file(self):
        from zefm.storage.word_notes import WordNotes
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); file=root/'yiddish.txt';file.write_text('ייִדיש')
            note_path=root/'store.json'
            notes=WordNotes(note_path)
            notes.put(str(file.resolve()),'ייִדיש','Meaning <not HTML>')
            server=BrowserServer(str(root),notes_path=note_path)
            server.start()
            try:
                with urlopen(server.url+'notes?path=yiddish.txt') as resp:
                    html=resp.read().decode('utf-8')
                self.assertIn('ייִדיש',html)
                self.assertIn('Meaning &lt;not HTML&gt;',html)
                self.assertNotIn('<not HTML>',html)
            finally:
                server.close()

class BrowserEditableNotesTests(unittest.TestCase):
    def setUp(self):
        from zefm.storage.word_notes import WordNotes
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'files';self.root.mkdir()
        self.file=self.root/'french יִידיש.txt'
        self.file.write_text('cœur יִידיש',encoding='utf-8')
        self.note_path=Path(self.tmp.name)/'notes.json'
        self.store=WordNotes(self.note_path)
        self.server=BrowserServer(str(self.root),notes_path=self.note_path)
        self.server.start()
        self.addCleanup(self.server.close)

    def request(self,route,fields=None):
        from urllib.parse import urlencode
        if fields is None:
            req=Request(self.server.url.rstrip('/')+route)
        else:
            req=Request(self.server.url.rstrip('/')+route,
                        data=urlencode(fields).encode('utf-8'),method='POST',
                        headers={'Content-Type':'application/x-www-form-urlencoded'})
        try:
            with urlopen(req,timeout=4) as resp:return resp.status,resp.read().decode('utf-8')
        except HTTPError as error:return error.code,error.read().decode('utf-8')

    def test_create_edit_and_read_unicode_note(self):
        from zefm.server.http import note_version
        from zefm.storage.word_notes import WordNotes
        name=self.file.name
        path='/note-edit?'+urlencode({'path':name})
        status,html=self.request(path)
        self.assertEqual(status,200)
        self.assertIn('Save Note',html)
        self.assertIn('name="word"',html)
        self.assertIn('name="digest"',html)
        content='French and יִידיש & <private>'
        fields={'csrf':self.server.token,'path':name,'word':'יִידיש',
                'digest':note_version(None),'content':content}
        status,html=self.request('/note-edit',fields)
        self.assertEqual(status,200,html)
        self.assertIn('Saved note:',html)
        self.assertEqual(WordNotes(self.note_path).get(str(self.file),'יִידיש')['data'],content)
        status,html=self.request('/notes?'+urlencode({'path':name}))
        self.assertEqual(status,200)
        self.assertIn('Edit note',html)
        self.assertIn('French and יִידיש &amp; &lt;private&gt;',html)
        self.assertNotIn('<private>',html)
        status,html=self.request('/note-edit?'+urlencode({'path':name,'word':'יִידיש'}))
        self.assertEqual(status,200)
        self.assertIn('French and יִידיש &amp; &lt;private&gt;',html)
        old=WordNotes(self.note_path).get(str(self.file),'יִידיש')
        fields['digest']=note_version(old)
        fields['content']='revised!'
        status,_=self.request('/note-edit',fields)
        self.assertEqual(status,200)
        self.assertEqual(WordNotes(self.note_path).get(str(self.file),'יִידיש')['data'],'revised!')

    def test_notes_edit_safety_and_stale_form(self):
        from zefm.server.http import note_version
        from zefm.storage.word_notes import WordNotes
        fields={'csrf':self.server.token,'path':self.file.name,'word':'cœur',
                'digest':note_version(None),'content':'original'}
        fields['csrf']='invalid'
        status,_=self.request('/note-edit',fields)
        self.assertEqual(status,403)
        fields['csrf']=self.server.token
        status,_=self.request('/note-edit',fields)
        self.assertEqual(status,200)
        status,_=self.request('/note-edit',fields)
        self.assertEqual(status,409)
        status,_=self.request('/note-edit',{**fields,'path':'../outside'})
        self.assertEqual(status,403)
        self.assertEqual(WordNotes(self.note_path).get(str(self.file),'cœur')['data'],'original')

    def test_empty_word_and_missing_file(self):
        from zefm.server.http import note_version
        fields={'csrf':self.server.token,'path':self.file.name,'word':' ',
                'digest':note_version(None),'content':'hello'}
        status,_=self.request('/note-edit',fields)
        self.assertEqual(status,400)
        status,_=self.request('/note-edit',{**fields,'path':'missing.txt','word':'x'})
        self.assertEqual(status,404)
