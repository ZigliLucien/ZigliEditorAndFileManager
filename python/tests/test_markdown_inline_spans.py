"""Regression for INFO80.md with inline color spans and device metadata."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from zefm.server.document_build import (
    _protect_color_spans, _restore_color_spans, markdown_html
)
from zefm.server.file_manager import LocalFiles

ROKU_SAMPLE = (
    '* <span style=color:orange>deviceType</span> urn:roku-com:device:player:1-0  \n'
    '* <span style=color:orange>friendlyName</span> Roku Ultra  \n'
    '* <span style=color:orange>manufacturer</span> Roku  \n'
    '* <span style=color:orange>modelName</span> 4850RW  \n'
    '* <span style=color:orange>iconList</span> '
    r'{\\  icon\\":{\\"mimetype\\":\\"image/png\\",\\"width\\":\\"360\\"}}'
    '\n'
)


class MarkdownInlineSpanTests(unittest.TestCase):
    def test_all_color_spans_are_protected(self):
        prepared, spans = _protect_color_spans(ROKU_SAMPLE)
        self.assertEqual(len(spans), 5)
        self.assertNotIn('<span style=color:orange>', prepared)
        restored = _restore_color_spans(prepared, spans)
        self.assertIn('<span style="color:orange">deviceType</span>', restored)
        self.assertIn("Roku Ultra", restored)
        self.assertIn("4850RW", restored)

    def test_unsafe_inline_html_not_enabled(self):
        source = '<span style=color:orange><script>alert(1)</script></span>'
        prepared, spans = _protect_color_spans(source)
        self.assertFalse(spans)
        self.assertEqual(source, prepared)

    def test_preview_retains_labels_when_discount_suppresses_html(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "INFO80.md").write_text(ROKU_SAMPLE, encoding="utf-8")
            # Model Discount's nohtml mode without requiring it to be installed.
            def render(prepared, source):
                self.assertNotIn("<span style=color:orange>", prepared)
                return ("<!doctype html><html><head></head><body>"
                        "<ul><li>" + prepared + "</li></ul></body></html>")
            with patch("zefm.server.document_build._discount_render", side_effect=render):
                output = markdown_html(LocalFiles(root), "INFO80.md").decode("utf-8")
            self.assertIn('<span style="color:orange">friendlyName</span>', output)
            self.assertIn("Roku Ultra", output)
            self.assertIn("modelName", output)
            self.assertNotIn("<script>alert(1)</script>", output)


if __name__ == "__main__":
    unittest.main()
