import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from zefm.storage.word_notes import WordNotes, default_notes_path, word_at
from zefm.storage.import_legacy_notes import parse_export, main as importer_main


class WordExtractionTests(unittest.TestCase):
    def test_latin_french_and_greek(self):
        self.assertEqual(word_at('étude grecque', 2), 'étude')
        self.assertEqual(word_at('abc λογος xyz', 8), 'λογος')
        self.assertEqual(word_at('abc λογος xyz', 0), 'abc')
        self.assertEqual(word_at('abc λογος xyz', 3), 'abc')

    def test_yiddish_combining_marks(self):
        word = 'ייִדיש'
        self.assertEqual(word_at(f'שלום {word} יפה', 8), word)
        self.assertEqual(word_at('בֿ שלום', 1), 'בֿ')
        self.assertEqual(word_at('בֿ שלום', 2), 'בֿ')

    def test_selected_phrase_and_missing_word(self):
        self.assertEqual(word_at('alpha + beta', 0, (0, 12)), 'alpha + beta')
        self.assertEqual(word_at(' (+) ', 2), '')
        self.assertEqual(word_at('', 0), '')
        with self.assertRaises(ValueError):word_at('abc', 12)
        with self.assertRaises(ValueError):word_at('abc', 0, (2, 8))


class NotesStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'state'/'notes.json'
        self.notes = WordNotes(self.path)

    def test_write_reopen_and_edit(self):
        self.notes.put('/home/a/doc.tex','λ','Greek letter xi? nope','λ')
        self.notes.put('/home/a/doc.tex','ייִדיש','אַ גוטן טאָג','ייִדיש')
        self.notes.put('/home/a/doc.tex','λ','updated')
        self.assertEqual(len(self.notes),2)
        same=WordNotes(self.path)
        self.assertEqual(same.get('/home/a/doc.tex','ייִדיש')['data'],'אַ גוטן טאָג')
        self.assertEqual(same.get('/home/a/doc.tex','λ')['data'],'updated')
        self.assertIsNone(same.get('/home/b/doc.tex','λ'))
        self.assertEqual(len(same.for_file('/home/a/doc.tex')),2)
        self.assertEqual(same.for_file('/home/b/doc.tex'),[])
        self.assertEqual(json.loads(self.path.read_text())['version'],1)

    def test_delete(self):
        self.notes.put('/home/a','word','text')
        self.assertTrue(self.notes.delete('/home/a','word'))
        self.assertFalse(self.notes.delete('/home/a','word'))
        self.assertIsNone(WordNotes(self.path).get('/home/a','word'))

    def test_privacy_file_mode(self):
        self.notes.put('f','w','private')
        self.assertEqual(self.path.stat().st_mode & 0o777,0o600)

    def test_bad_existing_data_not_overwritten(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text('{invalid',encoding='utf8')
        with self.assertRaises(ValueError):WordNotes(self.path)
        self.assertEqual(self.path.read_text(),'{invalid')
        self.path.write_text('{"version":99,"notes":[]}',encoding='utf8')
        with self.assertRaises(ValueError):WordNotes(self.path)
        self.assertIn('99',self.path.read_text())

    def test_record_schema(self):
        with self.assertRaises(ValueError):self.notes.put('','w','text')
        with self.assertRaises(ValueError):self.notes.put('doc','', 'text')
        with self.assertRaises(ValueError):self.notes.put('doc','w',None)
        self.assertFalse(self.path.exists())

    def test_import_batch_atomic_and_collision(self):
        self.notes.put('/old','word','existing','old-link')
        rows=[{'filename':'/old','word':'word','link':'replacement-link','data':'new'},
              {'filename':'/old','word':'ξ','link':'&#958;','data':'Greek letter xi'}]
        count,skipped=self.notes.import_records(rows)
        self.assertEqual((count,skipped),(1,1))
        self.assertEqual(self.notes.get('/old','word')['data'],'existing')
        self.assertEqual(self.notes.get('/old','ξ')['link'],'&#958;')
        self.assertEqual(self.notes.import_records(rows,replace=True),(2,0))
        self.assertEqual(self.notes.get('/old','word')['data'],'new')
        snapshot=self.path.read_bytes()
        with self.assertRaises(ValueError):
            self.notes.import_records([rows[1],{'filename':'x','word':'w','data':'missing link'}],replace=True)
        self.assertEqual(self.path.read_bytes(),snapshot)

    def test_xdg_data_path(self):
        with patch.dict(os.environ,{'XDG_DATA_HOME':str(Path(self.temp.name)/'xdg')}):
            self.assertEqual(default_notes_path(),Path(self.temp.name)/'xdg'/'zefm'/'word_notes.json')


class ImportCLI(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir=Path(self.tmp.name)
        self.record={'filename':'legacy/file','word':'ξ','link':'&#958;','data':'Greek letter xi'}

    def test_json_and_jsonl(self):
        outfile=self.dir/'notes.json'
        export=self.dir/'export.json'
        export.write_text(json.dumps([self.record],ensure_ascii=False))
        self.assertEqual(importer_main([str(export),'--output',str(outfile)]),0)
        self.assertEqual(WordNotes(outfile).get('legacy/file','ξ')['data'],'Greek letter xi')
        exportl=self.dir/'export.jsonl'
        exportl.write_text(json.dumps(self.record,ensure_ascii=False)+'\n')
        self.assertEqual(list(parse_export(exportl)),[self.record])

    def test_invalid_jsonl_leaves_existing_untouched(self):
        outfile=self.dir/'notes.json'
        WordNotes(outfile).put('old','word','old')
        old=outfile.read_bytes()
        export=self.dir/'export.jsonl'
        export.write_text(json.dumps(self.record)+'\n{broken\n')
        self.assertEqual(importer_main([str(export),'--output',str(outfile)]),1)
        self.assertEqual(outfile.read_bytes(),old)


if __name__=='__main__':unittest.main()

class ExportTests(unittest.TestCase):
    def test_convert_utf8_bytes(self):
        from zefm.storage.export_legacy_tables import convert_row
        fields=("filename","word","link","data")
        rec=convert_row(fields,(b'file', 'בֿ', 'link', b'\xce\xbe'))
        self.assertEqual(rec['data'],'ξ')
        with self.assertRaises(UnicodeError):convert_row(fields,(b'\xff','w','link','data'))
        with self.assertRaises(ValueError):convert_row(fields,('file','word','link',None))

    def test_export_atomic_count_and_overwrite(self):
        from zefm.storage.export_legacy_tables import write_rows
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'notes.jsonl'
            columns=('filename','word','link','data')
            rows=[('file','word','link','notes'),('file','ξ','link','αβγ')]
            self.assertEqual(write_rows(dest,columns,rows,expected_count=2),2)
            content=dest.read_bytes()
            with self.assertRaises(FileExistsError):write_rows(dest,columns,rows)
            with self.assertRaises(ValueError):write_rows(dest,columns,rows,
                                                           expected_count=3,overwrite=True)
            self.assertEqual(dest.read_bytes(),content)
            self.assertEqual(write_rows(dest,columns,[rows[0]],expected_count=1,overwrite=True),1)
            self.assertEqual(len(dest.read_text().splitlines()),1)
