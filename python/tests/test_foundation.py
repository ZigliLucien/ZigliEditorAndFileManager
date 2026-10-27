import json
import sys
import tempfile
import unittest
from pathlib import Path
from zefm.core.commands import run
from zefm.editor.model import Buffer
from zefm.editor.files import open_buffer, save_buffer
from zefm.editor.dictionary import load_dictionary
from zefm.document.interchange import xml_to_json, json_to_xml

class FoundationTests(unittest.TestCase):
    def test_command(self):
        result = run([sys.executable, "-c", "print('é')"])
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "é"))
    def test_buffer_and_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "é.txt"
            b = Buffer("שלום")
            b.replace(0, 0, "cœur ")
            save_buffer(b, p)
            self.assertFalse(b.modified)
            self.assertEqual(open_buffer(p).text, "cœur שלום")
    def test_dictionary(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/"fr.json").write_text('{"oe":"œ"}', encoding="utf-8")
            self.assertEqual(load_dictionary(d, "fr")["oe"], "œ")
    def test_xml_json_mixed_content(self):
        original = '<root lang="yi">a<b>שלום</b>tail<c/>end</root>'
        self.assertEqual(xml_to_json(json_to_xml(xml_to_json(original))),
                         xml_to_json(original))

if __name__ == "__main__":
    unittest.main()
