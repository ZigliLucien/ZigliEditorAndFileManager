"""v46: ensure original keymap is available to real browser bidi input."""
import json
import tempfile
import unittest
from html import unescape
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from zefm.editor.legacy_keymaps import read_keymap
from zefm.server.http import BrowserServer
from zefm.server.rtl_keymap import RTL_KEYMAP_JS, yiddish_keymap_json


class YiddishBrowserKeymapTests(unittest.TestCase):
    def test_browser_mapping_matches_legacy_source(self):
        source = Path(__file__).resolve().parents[1] / 'legacy_keymaps' / 'Yiddish.keymap'
        original = read_keymap(source)
        encoded = json.loads(yiddish_keymap_json())
        self.assertEqual(encoded['66'], 'ב')
        self.assertEqual(encoded['73S'], 'אי')
        self.assertEqual(encoded['91'], '־')
        self.assertEqual(encoded,
                         {f'{code}{suffix}': record.characters
                          for (code, suffix), record in original.items()
                          if suffix in ('', 'S')})
        self.assertNotIn('65C', encoded)

    def test_rtl_form_and_standalone_script(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ייִדיש.txt'
            path.write_text('שלום עולם 123 abc', encoding='utf-8')
            server = BrowserServer(directory)
            server.start()
            try:
                with urlopen(server.url + 'edit?' + urlencode(
                        {'path': path.name, 'dir': 'rtl'}), timeout=4) as response:
                    html = response.read().decode('utf-8')
                    policy = response.headers['Content-Security-Policy']
                self.assertIn('dir="rtl"', html)
                self.assertIn('id="zefm-rtl-content"', html)
                self.assertIn('id="zefm-yiddish-keymap" checked', html)
                self.assertIn('src="/rtl-keymap.js"', html)
                self.assertIn("script-src 'self'", policy)
                self.assertIn('שלום עולם 123 abc', html)
                self.assertIn('73S', unescape(html))
                with urlopen(server.url + 'rtl-keymap.js', timeout=4) as response:
                    script = response.read().decode('utf-8')
                    self.assertIn('javascript', response.headers['Content-Type'])
                self.assertEqual(script, RTL_KEYMAP_JS)
                self.assertIn('textarea.setRangeText(', script)
                self.assertIn('event.preventDefault()', script)
                self.assertNotIn('reverse(', script)
                with urlopen(server.url + 'edit?' + urlencode(
                        {'path': path.name}), timeout=4) as response:
                    html = response.read().decode('utf-8')
                    policy = response.headers['Content-Security-Policy']
                self.assertNotIn('src="/rtl-keymap.js"', html)
                self.assertNotIn("script-src 'self'", policy)
            finally:
                server.close()

    def test_browser_form_keeps_file_bytes_until_save(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'שלום.txt'
            text = 'שלום עברית English 123\nבוקר טוב'
            path.write_text(text, encoding='utf-8')
            server = BrowserServer(directory)
            server.start()
            try:
                with urlopen(server.url + 'edit?' + urlencode(
                        {'path': path.name, 'dir': 'rtl'}), timeout=4) as response:
                    self.assertIn(text, unescape(response.read().decode('utf-8')))
                self.assertEqual(path.read_text(encoding='utf-8'), text)
            finally:
                server.close()


if __name__ == '__main__':
    unittest.main()
