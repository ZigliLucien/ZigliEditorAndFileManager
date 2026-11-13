"""v94: LaTeX master selection and safe root resolution."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from zefm.editor.latex_master import resolve_latex_master, root_directive


class LatexMasterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        (self.folder / "chapters").mkdir()
        self.source = self.folder / "chapters" / "section.tex"
        self.source.write_text("Section")
        self.master = self.folder / "main.tex"
        self.master.write_text(r"\documentclass{article}")

    def test_single_file_remains_default(self):
        self.assertEqual(resolve_latex_master(self.source, "Hello"), self.source.resolve())

    def test_magic_comment_root_is_relative_to_current_source(self):
        text = "% !TEX root = ../main.tex\n\\section{Hello}"
        self.assertEqual(root_directive(text), "../main.tex")
        self.assertEqual(resolve_latex_master(self.source, text), self.master.resolve())

    def test_comment_case_and_leading_whitespace(self):
        self.assertEqual(root_directive("\n  % !TeX root = ../main.tex\n"), "../main.tex")

    def test_explicit_master_overrides_comment(self):
        alternative = self.folder / "other.tex"
        alternative.write_text("main")
        self.assertEqual(
            resolve_latex_master(self.source, "% !TEX root = ../main.tex", alternative),
            alternative.resolve())

    def test_missing_master_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            resolve_latex_master(self.source, "% !TEX root = missing.tex")

    def test_non_tex_master_is_rejected(self):
        (self.folder / "wrong.txt").write_text("text")
        with self.assertRaisesRegex(ValueError, r"\.tex"):
            resolve_latex_master(self.source, "", self.folder / "wrong.txt")

    def test_directive_only_scanned_at_top(self):
        self.assertIsNone(root_directive("\n".join(["line"] * 21 + ["% !TEX root = main.tex"])))

    def test_symlink_master_is_rejected(self):
        link = self.folder / "link.tex"
        try:
            link.symlink_to(self.master)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            resolve_latex_master(self.source, "% !TEX root = ../link.tex")

if __name__ == "__main__":
    unittest.main()
