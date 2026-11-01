"""v58: Perl mathjaxfilterr compatibility without jQuery."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.request import urlopen
import unittest

from zefm.server.mathjax_filter import inject_mathjax, MATHJAX_PREVIEW_CSP
from zefm.server.document_build import markdown_html
from zefm.server.file_manager import LocalFiles
from zefm.server.http import BrowserServer


class MathJaxFilterTests(unittest.TestCase):
    def test_head_injection_preserves_body_and_math_delimiters(self):
        source = ('<!doctype html><html><head><title>Research</title></head>'
                  '<body><p>Inline $x^2$ and \\(x+y\\), display $$a=b$$ '
                  'and \\[c=d\\].</p></body></html>')
        result = inject_mathjax(source)
        self.assertIn('<script defer src="/mathjax-config.js"></script>', result)
        self.assertIn('https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-svg.js', result)
        self.assertLess(result.index('mathjax-config.js'), result.index('tex-mml-svg.js'))
        self.assertLess(result.index('tex-mml-svg.js'), result.index('</head>'))
        self.assertIn('Inline $x^2$', result)
        self.assertIn('display $$a=b$$', result)
        self.assertNotIn('jquery', result.lower())
        self.assertNotIn('mathformat.js', result)
        self.assertEqual(inject_mathjax(result), result)

    def test_case_attributes_and_missing_head(self):
        text = '<HTML><HEAD class="chapter"><title>T</title></HEAD><BODY>Math</BODY></HTML>'
        result = inject_mathjax(text)
        self.assertLess(result.index('mathjax-config.js'), result.index('</HEAD>'))
        result = inject_mathjax('<html><body>$x$</body></html>')
        self.assertIn('<head>', result)
        self.assertIn('mathjax-config.js', result)
        self.assertEqual(result.count('<head>'), 1)

    def test_restrictive_sandbox_and_self_script(self):
        self.assertIn('sandbox allow-scripts', MATHJAX_PREVIEW_CSP)
        self.assertNotIn('allow-same-origin', MATHJAX_PREVIEW_CSP)
        self.assertNotIn('unsafe-eval', MATHJAX_PREVIEW_CSP)
        self.assertNotIn('unsafe-inline', MATHJAX_PREVIEW_CSP.split('script-src')[1].split(';')[0])
        self.assertIn("form-action 'none'", MATHJAX_PREVIEW_CSP)

    def test_markdown_and_http_config_script(self):
        with TemporaryDirectory() as d:
            Path(d, 'test.md').write_text('Math $x^2$ and \\(y\\).', encoding='utf-8')
            class Result:
                returncode = 0
                stdout = ('<html><head><title>M</title></head>'
                          '<body><p>Math $x^2$ and \\(y\\).</p></body></html>')
            with patch('zefm.server.document_build.shutil.which',
                       side_effect=lambda name: '/usr/local/bin/makepage' if name == 'makepage' else None), \
                 patch('zefm.server.document_build.subprocess.run', return_value=Result()):
                html = markdown_html(LocalFiles(d), 'test.md').decode()
            self.assertIn('mathjax-config.js', html)
            self.assertIn('href="/math.css"', html)
            self.assertIn('$x^2$', html)
            browser = BrowserServer(d)
            browser.start()
            try:
                with urlopen(browser.url + 'mathjax-config.js', timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn('javascript', response.headers['Content-Type'])
                    config = response.read().decode()
                    self.assertIn('inlineMath', config)
                    self.assertIn('displayMath', config)
                    self.assertIn('\\\\(', config)
                with urlopen(browser.url + 'view?path=test.md', timeout=5) as response:
                    csp = response.headers['Content-Security-Policy']
                    self.assertIn('sandbox allow-scripts', csp)
                    self.assertNotIn('allow-same-origin', csp)
                    self.assertIn('cdn.jsdelivr.net', csp)
            finally:
                browser.close()


if __name__ == '__main__':
    unittest.main()
