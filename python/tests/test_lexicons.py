import json
import tempfile
import unittest
from pathlib import Path
from zefm.storage.lexicons import (language_code,default_lexicon_dir,read_export,
                                 import_lexicons,lookup_lexicon)
from zefm.storage.import_legacy_dictionaries import main


class LexiconTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.export=self.root/'export.jsonl'
        self.rows=[
            {'lang':'French','word':'cœur','data':'heart, core'},
            {'lang':'French','word':'cœur','data':'middle'},
            {'lang':'Yiddish','word':'ייִדיש','data':'Yiddish language'},
            {'lang':'French','word':'été','data':'summer'},
        ]
        self.export.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in self.rows),encoding='utf-8')

    def test_langs(self):
        self.assertEqual(language_code('French'),'fr')
        self.assertEqual(language_code('Yiddish'),'yi')
        for bad in ('','../etc','a/b',None):
            with self.assertRaises(ValueError):language_code(bad)

    def test_import_duplicate_words_and_unicode(self):
        target=self.root/'store'
        self.assertEqual(import_lexicons(self.export,target),{'fr':3,'yi':1})
        self.assertEqual(lookup_lexicon(target,'fr','CŒUR'),['heart, core','middle'])
        self.assertEqual(lookup_lexicon(target,'yi','ייִדיש'),['Yiddish language'])
        self.assertEqual(len(list(read_export(target/'fr.jsonl'))),3)
        self.assertEqual((target/'yi.jsonl').stat().st_mode & 0o777,0o600)
        with self.assertRaises(FileExistsError):import_lexicons(self.export,target)
        self.assertEqual(import_lexicons(self.export,target,overwrite=True),{'fr':3,'yi':1})

    def test_dry_run(self):
        target=self.root/'store'
        self.assertEqual(import_lexicons(self.export,target,dry_run=True),{'fr':3,'yi':1})
        self.assertFalse(target.exists())
        self.assertEqual(main([str(self.export),'--output-dir',str(target),'--dry-run']),0)

    def test_invalid_export_never_modifies_existing(self):
        target=self.root/'store'
        import_lexicons(self.export,target)
        snapshot=(target/'fr.jsonl').read_bytes()
        with self.export.open('a') as f:f.write('{broken\n')
        with self.assertRaises(ValueError):import_lexicons(self.export,target,overwrite=True)
        self.assertEqual((target/'fr.jsonl').read_bytes(),snapshot)
        self.assertEqual(main([str(self.export),'--output-dir',str(target),'--force']),1)

    def test_empty_export(self):
        self.export.write_text('')
        self.assertEqual(import_lexicons(self.export,self.root/'store'),{})

    def test_missing_lexicon(self):
        self.assertEqual(lookup_lexicon(self.root,'fr','no'),[])

    def test_bad_record_fields(self):
        self.export.write_text(json.dumps({'lang':'French','word':'a','data':42})+'\n')
        with self.assertRaises(ValueError):list(read_export(self.export))


if __name__=='__main__':unittest.main()
