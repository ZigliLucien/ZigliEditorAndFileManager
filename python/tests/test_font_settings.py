import json
import tempfile
import unittest
from pathlib import Path
from zefm.editor.font_settings import DEFAULT_FONT,read_font,write_font,valid_font

class FontSettingsTests(unittest.TestCase):
    def test_default_missing(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(read_font(Path(d)/'notthere.json'),DEFAULT_FONT)
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'nested'/'font.json'
            value={'family':'DejaVu Sans Mono','size':17,'weight':'bold','slant':'italic'}
            write_font(path,value)
            self.assertEqual(read_font(path),value)
    def test_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'font.json'
            path.write_text('{bad')
            self.assertEqual(read_font(path),DEFAULT_FONT)
            for value in ({'family':'X','size':False,'weight':'bold','slant':'roman'},
                {'family':'X','size':73,'weight':'bold','slant':'roman'}):
                self.assertFalse(valid_font(value))
                with self.assertRaises(ValueError):write_font(path,value)
            self.assertEqual(read_font(path),DEFAULT_FONT)
