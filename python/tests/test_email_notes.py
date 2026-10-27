import tempfile
import unittest
from pathlib import Path
from zefm.storage.email_notes import EmailNotes

class EmailNotesTests(unittest.TestCase):
    def test_save_reload_and_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"notes.json"
            n=EmailNotes(path)
            n.set("<abc@example.org>","Yiddish: שלום")
            self.assertEqual(EmailNotes(path).get("<abc@example.org>"),"Yiddish: שלום")
            n.set("<abc@example.org>","")
            self.assertEqual(EmailNotes(path).get("<abc@example.org>"),"")
    def test_invalid_id_and_corrupt_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"notes.json"
            path.write_text("{broken",encoding="utf-8")
            notes=EmailNotes(path)
            self.assertEqual(notes.notes,{})
            with self.assertRaises(ValueError):notes.set("  ","hello")
            with self.assertRaises(TypeError):notes.set("valid",42)
