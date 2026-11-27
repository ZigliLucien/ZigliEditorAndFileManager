import unittest
from pathlib import Path

from zefm.editor.file_templates import file_template
from zefm.editor.modes import ModeRegistry
from zefm.editor.shortcut_config import load_menus


class FileTemplateTests(unittest.TestCase):
    def test_latex(self):
        template = file_template("latex")
        self.assertEqual(template.text,
                         "\\documentclass{amsart}\n\n\\begin{document}\n\n\\end{document}\n")
        self.assertEqual(template.cursor, "4.0")

    def test_scripts(self):
        python = file_template("python")
        perl = file_template("perl")
        self.assertTrue(python.text.startswith("#!/usr/bin/env python3\n"))
        self.assertTrue(perl.text.startswith("#!/usr/bin/env perl\n"))
        self.assertIn("use strict;\nuse warnings;\n", perl.text)
        self.assertEqual(python.cursor, "3.0")
        self.assertEqual(perl.cursor, "6.0")

    def test_markdown(self):
        template = file_template("markdown")
        self.assertEqual(template.text, "# Title\n\n")
        self.assertEqual(template.cursor, "1.2")
        commands = load_menus()["Run"]
        self.assertEqual(next(c.shortcut for c in commands
                              if c.label == "Preview Document"), "Ctrl+Shift+P")

    def test_html(self):
        template = file_template("html")
        self.assertIn("<!doctype html>", template.text)
        self.assertIn("<body>", template.text)
        self.assertIn("</html>", template.text)
        self.assertEqual(template.cursor, "8.2")

    def test_no_overwrite(self):
        for mode in ("latex", "python", "perl", "markdown", "html"):
            with self.assertRaises(ValueError):
                file_template(mode, "existing source")
        with self.assertRaises(ValueError):
            file_template("json")

    def test_perl_detection(self):
        registry = ModeRegistry.load(
            Path(__file__).resolve().parents[1] / "config" / "modes.json")
        for filename in ("test.pl", "Test.pm"):
            self.assertEqual(registry.detect(filename).name, "perl")
        self.assertEqual(registry.detect(text=file_template("perl").text).name,
                         "perl")

    def test_registry_shortcut(self):
        commands = load_menus()["File"]
        self.assertEqual(next(c.shortcut for c in commands
                              if c.label == "Insert File Template"),
                         "Ctrl+Shift+T")


if __name__ == "__main__":
    unittest.main()
