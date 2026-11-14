"""v96: LaTeX source location extraction from bounded compiler diagnostics."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from zefm.editor.latex_diagnostics import parse_latex_errors


class DiagnosticParserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.master = self.root / "main.tex"
        self.master.write_text("main")

    def test_classic_tex_error(self):
        log = ("=== LuaLaTeX pass 1 (exit 1) ===\n"
               "(./main.tex\n! Undefined control sequence.\n"
               "l.17 \\unknown\n")
        items = parse_latex_errors(log, self.master)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].path, self.master)
        self.assertEqual(items[0].line, 17)
        self.assertEqual(items[0].log_line, 3)
        self.assertIn("Undefined control sequence", items[0].message)

    def test_included_file_location(self):
        log = "(./main.tex (./chapters/one.tex\n! Missing $ inserted.\n" \
              "l.42 foo\n"
        items = parse_latex_errors(log, self.master)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].path, self.root / "chapters" / "one.tex")
        self.assertEqual(items[0].line, 42)

    def test_direct_file_line_error(self):
        log = "./chapters/a.tex:29: Undefined control sequence\n"
        items = parse_latex_errors(log, self.master)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].line, 29)
        self.assertEqual(items[0].path, self.root / "chapters" / "a.tex")
        self.assertEqual(items[0].log_line, 1)

    def test_errors_from_different_passes(self):
        log = ("=== LuaLaTeX pass 1 (exit 0) ===\n"
               "(./other.tex\n"
               "=== LuaLaTeX pass 2 (exit 1) ===\n"
               "! Error.\nl.3 x\n")
        items = parse_latex_errors(log, self.master)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].path, self.master)

    def test_non_line_errors_are_not_guessed(self):
        self.assertEqual(parse_latex_errors(
            "! Emergency stop.\nNo pages of output.\n", self.master), [])

    def test_ignores_invalid_zero_line(self):
        self.assertEqual(parse_latex_errors(
            "! Error.\nl.0 invalid\n", self.master), [])


if __name__ == "__main__":
    unittest.main()
