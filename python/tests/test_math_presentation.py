"""v57: original ZEFM mathformat.js/math.css presentation, without runtime JS."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.request import urlopen
import unittest

from zefm.server.math_presentation import format_math_html
from zefm.server.document_build import markdown_html
from zefm.server.file_manager import LocalFiles
from zefm.server.http import BrowserServer


class MathPresentationTests(unittest.TestCase):
    def test_theorem_lemma_and_proof_headings(self):
        markup = ('<!doctype html><html><head><title>Math</title></head>'
                  '<body><div class="theorem" id="T_1">Statement</div>'
                  '<lemma id="L_2">Result</lemma>'
                  '<div class="proof">Argument</div></body></html>')
        html = format_math_html(markup)
        self.assertIn('<link rel="stylesheet" href="/math.css">', html)
        self.assertIn('class="zefm-math-page"', html)
        self.assertIn('Theorem T_1', html)
        self.assertIn('Lemma L_2', html)
        self.assertIn('Proof.', html)
        self.assertIn('Statement', html)
        self.assertNotIn('<script', html)

    def test_equations_sections_and_references_escape_input(self):
        markup = ('<html><head></head><body>'
                  '<div class="section" id="Main_Result">Text</div>'
                  '<equation num="2.3">x=y</equation>'
                  '<ref name="Main_Result">See section</ref>'
                  '<theorem id="&quot;&gt;&lt;img&gt;">Done</theorem>'
                  '</body></html>')
        html = format_math_html(markup)
        self.assertIn('<h2>Main Result</h2>', html)
        self.assertIn('class="eqno">(2.3)</span>', html)
        self.assertIn('href="#Main_Result"', html)
        self.assertNotIn('<img>', html)
        self.assertIn('&lt;img&gt;', html)

    def test_list_elements_and_unicode(self):
        html = format_math_html(
            '<html><head></head><body><itemize><item>שלום</item></itemize></body></html>')
        self.assertIn('<ul', html)
        self.assertIn('<li', html)
        self.assertIn('שלום', html)

    def test_generated_markdown_injects_math_styles(self):
        with TemporaryDirectory() as temp:
            source = Path(temp) / "Math.md"
            source.write_text('# Theorem\n\nStatement', encoding='utf-8')
            class Result:
                returncode = 0
                stdout = '<html><head></head><body><h1>Theorem</h1></body></html>'
            with patch('zefm.server.document_build.shutil.which',
                       side_effect=lambda name: '/usr/bin/makepage' if name == 'makepage' else None), \
                 patch('zefm.server.document_build.subprocess.run', return_value=Result()):
                html = markdown_html(LocalFiles(temp), 'Math.md').decode('utf-8')
            self.assertIn('href="/math.css"', html)
            self.assertIn('class="zefm-math-page"', html)
            self.assertIn('<h1>Theorem</h1>', html)

    def test_shared_style_is_served_and_basic_page_links_it(self):
        with TemporaryDirectory() as temp:
            browser = BrowserServer(temp)
            browser.start()
            try:
                with urlopen(browser.url + 'math.css', timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn('text/css', response.headers['Content-Type'])
                    data = response.read().decode()
                    self.assertIn('#aa4400', data)
                    self.assertIn('.theorem', data)
                with urlopen(browser.url, timeout=5) as response:
                    page = response.read().decode()
                    self.assertIn('href="/math.css"', page)
            finally:
                browser.close()


if __name__ == '__main__':
    unittest.main()
