"""v98: selected LaTeX engines and persistent desktop choice."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from zefm.editor.latex_engine_preferences import LatexEnginePreference
from zefm.server.document_build import _command
from zefm.server.file_types import handler_for


class LatexEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = self.directory / "main.tex"
        self.source.write_text("text")
        self.preference = self.directory / "prefs.json"

    def test_default_engine_and_persistent_selection(self):
        store = LatexEnginePreference(self.preference)
        self.assertEqual(store.engine, "lualatex")
        store.set("xelatex")
        self.assertEqual(LatexEnginePreference(self.preference).engine, "xelatex")
        store.set("pdflatex")
        self.assertEqual(LatexEnginePreference(self.preference).engine, "pdflatex")

    def test_invalid_engine_does_not_replace_preference(self):
        store = LatexEnginePreference(self.preference)
        store.set("xelatex")
        original = self.preference.read_bytes()
        for invalid in ("latex", "sh", "/usr/bin/lualatex", "xelatex --shell-escape", ""):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                store.set(invalid)
        self.assertEqual(self.preference.read_bytes(), original)

    def test_corrupt_settings_fall_back_to_lualatex(self):
        self.preference.write_text('{"engine":"shell"}')
        self.assertEqual(LatexEnginePreference(self.preference).engine, "lualatex")
        self.preference.write_text("{")
        self.assertEqual(LatexEnginePreference(self.preference).engine, "lualatex")

    def test_builder_arguments_use_engine_without_shell_escape(self):
        descriptor = handler_for("main.tex")
        for engine in ("lualatex", "pdflatex", "xelatex"):
            with self.subTest(engine=engine), \
                 patch("zefm.server.document_build.shutil.which",
                       return_value="/usr/bin/" + engine):
                argv = _command(self.source, self.directory, descriptor,
                                latex_engine=engine)
            self.assertEqual(argv[0], "/usr/bin/" + engine)
            self.assertIn("-no-shell-escape", argv)
            self.assertIn("-file-line-error", argv)

    def test_browser_default_remains_lualatex(self):
        descriptor = handler_for("main.tex")
        with patch("zefm.server.document_build.shutil.which",
                   return_value="/usr/bin/lualatex") as which:
            argv = _command(self.source, self.directory, descriptor)
        self.assertEqual(argv[0], "/usr/bin/lualatex")
        which.assert_called_once_with("lualatex")


if __name__ == "__main__":
    unittest.main()
