"""Regression tests for desktop LaTeX engine preferences.

Run with: python3 -m unittest discover -s python/tests -v
"""
import json
import tempfile
import unittest
from pathlib import Path

from zefm.editor.latex_engine_preferences import (
    ENGINES, LatexEnginePreference, validate_engine,
)


class LatexEnginePreferenceTests(unittest.TestCase):
    def test_all_supported_engines_validate(self):
        self.assertEqual(
            ENGINES, ("lualatex", "pdflatex", "xelatex", "latexmk")
        )
        for engine in ENGINES:
            with self.subTest(engine=engine):
                self.assertEqual(validate_engine(engine), engine)

    def test_unknown_engine_is_rejected(self):
        for value in ("latex", "tectonic", "", None, 123, []):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_engine(value)

    def test_missing_configuration_defaults_to_lualatex(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config" / "latex_engine.json"
            preference = LatexEnginePreference(path)
            self.assertEqual(preference.engine, "lualatex")
            self.assertFalse(path.exists())

    def test_latexmk_choice_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config" / "latex_engine.json"
            preference = LatexEnginePreference(path)
            preference.set("latexmk")
            self.assertEqual(preference.engine, "latexmk")
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"engine": "latexmk"},
            )
            self.assertEqual(LatexEnginePreference(path).engine, "latexmk")

    def test_invalid_configuration_falls_back_to_default(self):
        for payload in ('not json', '{}', '{"engine": "unknown"}',
                        '{"engine": null}', '[]'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "latex_engine.json"
                    path.write_text(payload, encoding="utf-8")
                    self.assertEqual(LatexEnginePreference(path).engine,
                                     "lualatex")

    def test_rejected_selection_leaves_prior_setting_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "latex_engine.json"
            preference = LatexEnginePreference(path)
            preference.set("latexmk")
            original = path.read_bytes()
            with self.assertRaises(ValueError):
                preference.set("unsupported")
            self.assertEqual(preference.engine, "latexmk")
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
