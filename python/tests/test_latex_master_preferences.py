"""v95: persistent master choices, precedence, and safe JSON persistence."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from zefm.editor.latex_master import resolve_latex_master
from zefm.editor.latex_master_preferences import LatexMasterPreferences


class LatexMasterPreferencesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "config" / "latex_masters.json"
        self.chapter = self.root / "chapters" / "cœur ייִדיש.tex"
        self.chapter.parent.mkdir()
        self.chapter.write_text("Chapter", encoding="utf-8")
        self.master = self.root / "main.tex"
        self.master.write_text("Main", encoding="utf-8")

    def test_selection_survives_recreation(self):
        initial = LatexMasterPreferences(self.path)
        initial.set(self.chapter, self.master)
        self.assertEqual(LatexMasterPreferences(self.path).get(self.chapter),
                         self.master.resolve())
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data["masters"][str(self.chapter.resolve())],
                         str(self.master.resolve()))

    def test_clear_survives_recreation(self):
        initial = LatexMasterPreferences(self.path)
        initial.set(self.chapter, self.master)
        initial.clear(self.chapter)
        self.assertIsNone(LatexMasterPreferences(self.path).get(self.chapter))
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")),
                         {"masters": {}})

    def test_different_documents_retain_independent_masters(self):
        second = self.root / "chapters" / "other.tex"
        second.write_text("Second")
        alternative = self.root / "alternate.tex"
        alternative.write_text("Different")
        store = LatexMasterPreferences(self.path)
        store.set(self.chapter, self.master)
        store.set(second, alternative)
        reopened = LatexMasterPreferences(self.path)
        self.assertEqual(reopened.get(self.chapter), self.master.resolve())
        self.assertEqual(reopened.get(second), alternative.resolve())

    def test_explicit_precedence_over_magic_comment(self):
        store = LatexMasterPreferences(self.path)
        store.set(self.chapter, self.master)
        alternate = self.root / "other.tex"
        alternate.write_text("Other")
        content = "% !TEX root = ../other.tex\n"
        self.assertEqual(resolve_latex_master(
            self.chapter, content, store.get(self.chapter)), self.master.resolve())
        store.clear(self.chapter)
        self.assertEqual(resolve_latex_master(
            self.chapter, content, store.get(self.chapter)), alternate.resolve())

    def test_invalid_json_does_not_crash(self):
        self.path.parent.mkdir()
        self.path.write_text("{broken", encoding="utf-8")
        store = LatexMasterPreferences(self.path)
        self.assertIsNone(store.get(self.chapter))
        store.set(self.chapter, self.master)
        self.assertEqual(LatexMasterPreferences(self.path).get(self.chapter),
                         self.master.resolve())

    def test_invalid_entries_are_ignored(self):
        self.path.parent.mkdir()
        self.path.write_text(json.dumps({"masters": {
            "relative.tex": "main.tex",
            "x": 42,
            str(self.chapter.resolve()): str(self.master.resolve())
        }}), encoding="utf-8")
        store = LatexMasterPreferences(self.path)
        self.assertEqual(len(store.entries), 1)

    def test_missing_saved_master_is_reported_on_resolution(self):
        store = LatexMasterPreferences(self.path)
        store.set(self.chapter, self.master)
        self.master.unlink()
        with self.assertRaisesRegex(ValueError, "does not exist"):
            resolve_latex_master(self.chapter, "",
                                 LatexMasterPreferences(self.path).get(self.chapter))

    def test_invalid_selection_preserves_existing_preferences(self):
        store = LatexMasterPreferences(self.path)
        store.set(self.chapter, self.master)
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            store.set(self.chapter, self.root / "missing.tex")
        self.assertEqual(self.path.read_bytes(), before)

if __name__ == "__main__":
    unittest.main()
