"""Wheel selection and filesystem ordering for the v60 Tk file chooser."""
from pathlib import Path
import tkinter as tk
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from zefm.editor.gui.file_chooser import (
    wheel_steps, directory_entries, OPEN_FILTERS, FileChooser)


class WheelTests(unittest.TestCase):
    def test_x11_linux_button_scrolling(self):
        self.assertEqual(wheel_steps(SimpleNamespace(num=4, delta=0)), -1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=5, delta=0)), 1)

    def test_windows_macos_wheel(self):
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=120)), -1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=-120)), 1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=240)), -2)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=-240)), 2)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=1)), -1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=-1)), 1)
        self.assertEqual(wheel_steps(SimpleNamespace(num=None, delta=0)), 0)

    def test_directory_sorting(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("z.txt", "A.txt", "b.txt"):
                (root / name).write_text(name)
            for name in ("subDir", "Another"):
                (root / name).mkdir()
            self.assertEqual([p.name for p in directory_entries(root)],
                             ["Another", "subDir", "A.txt", "b.txt", "z.txt"])

    def test_nonexistent_directory(self):
        with TemporaryDirectory() as temp:
            with self.assertRaises(OSError):
                directory_entries(Path(temp) / "not-there")


class ExtensionFilterTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        for name in ("A.TEX", "b.tex", "program.py", "data.JSON",
                     "notes.md", "readme.markdown", "image.png", "plain.txt"):
            (self.folder / name).write_text(name, encoding="utf-8")
        (self.folder / "subfolder").mkdir()
        (self.folder / "subfolder" / "nested.tex").write_text("nested")
        (self.folder / ".zefm").mkdir()
        (self.folder / ".config").mkdir()
        (self.folder / ".private.json").write_text('{"secret": 1}')
        (self.folder / ".bashrc").write_text("config")

    def names(self, extensions):
        return [path.name for path in directory_entries(self.folder, extensions)]

    def test_dotfiles_hidden_by_default_under_json_filter(self):
        json_files = self.names(OPEN_FILTERS["JSON (*.json)"])
        self.assertEqual(json_files, ["subfolder", "data.JSON"])
        self.assertNotIn(".private.json", json_files)
        self.assertNotIn(".config", json_files)
        self.assertNotIn(".zefm", json_files)

        with_hidden = [
            p.name for p in directory_entries(
                self.folder, OPEN_FILTERS["JSON (*.json)"],
                show_hidden=True)]
        self.assertEqual(set(with_hidden),
                         {".config", ".zefm", ".private.json",
                          "data.JSON", "subfolder"})
        # Even with hidden entries visible, nonmatching hidden files
        # must not slip past a JSON extension filter.
        self.assertNotIn(".bashrc", with_hidden)

    def test_all_files_may_show_hidden_when_requested(self):
        default = self.names(None)
        self.assertNotIn(".bashrc", default)
        self.assertNotIn(".zefm", default)
        with_hidden = [
            p.name for p in directory_entries(
                self.folder, show_hidden=True)]
        self.assertIn(".bashrc", with_hidden)
        self.assertIn(".zefm", with_hidden)

    def test_extension_choices_are_present(self):
        self.assertEqual(
            list(OPEN_FILTERS),
            ["All files", "LaTeX (*.tex)", "Python (*.py)",
             "JSON (*.json)", "Markdown (*.md, *.markdown)",
             "All four types"])

    def test_filters_keep_directories_and_match_case_insensitively(self):
        for label, expected in (
                ("LaTeX (*.tex)", ["A.TEX", "b.tex"]),
                ("Python (*.py)", ["program.py"]),
                ("JSON (*.json)", ["data.JSON"]),
                ("Markdown (*.md, *.markdown)", ["notes.md", "readme.markdown"]),
                ("All four types", [
                    "A.TEX", "b.tex", "program.py", "data.JSON",
                    "notes.md", "readme.markdown"])):
            with self.subTest(filter=label):
                names = self.names(OPEN_FILTERS[label])
                self.assertIn("subfolder", names)
                self.assertEqual(set(names) - {"subfolder"}, set(expected))
        self.assertIn("image.png", self.names(OPEN_FILTERS["All files"]))
        self.assertEqual(self.names(OPEN_FILTERS["All files"]),
                         self.names(None))


class ExtensionFilterGuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        for name in ("draft.tex", "program.py", "data.json", "notes.md"):
            (self.folder / name).write_text(name)
        (self.folder / "subfolder").mkdir()
        (self.folder / ".git").mkdir()
        (self.folder / ".config").mkdir()
        (self.folder / ".secret.json").write_text('{"v": 1}')
        (self.folder / ".bashrc").write_text("hidden")
        self.previous_filter = FileChooser.last_open_filter
        FileChooser.last_open_filter = "All files"
        self.addCleanup(
            lambda: setattr(FileChooser, "last_open_filter", self.previous_filter))
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(
            lambda: self.root.destroy() if self.root.winfo_exists() else None)

    def chooser(self, *, save=False):
        dialog = FileChooser(self.root, self.folder, save=save)
        self.addCleanup(
            lambda: dialog.cancel() if dialog.winfo_exists() else None)
        return dialog

    @staticmethod
    def visible(dialog):
        return {p.name for p in dialog.paths.values()}

    def test_filter_switch_and_folder_navigation(self):
        dialog = self.chooser()
        self.assertEqual(self.visible(dialog),
                         {"draft.tex", "program.py", "data.json", "notes.md",
                          "subfolder"})
        dialog.filter_combo.set("LaTeX (*.tex)")
        dialog.filter_changed()
        self.assertEqual(self.visible(dialog), {"draft.tex", "subfolder"})
        self.assertEqual(FileChooser.last_open_filter, "LaTeX (*.tex)")
        # Navigate into an otherwise empty directory with the filter active.
        folder_iid = next(key for key, path in dialog.paths.items()
                          if path.name == "subfolder")
        dialog.tree.selection_set(folder_iid)
        dialog.activate()
        self.assertEqual(dialog.folder, (self.folder / "subfolder").resolve())
        dialog.go_up()
        self.assertEqual(self.visible(dialog), {"draft.tex", "subfolder"})
        # The chosen filter persists across the next Open dialog.
        dialog.cancel()
        another = self.chooser()
        self.assertEqual(another.file_filter.get(), "LaTeX (*.tex)")
        self.assertEqual(self.visible(another), {"draft.tex", "subfolder"})
        # Manual filename entry continues to allow an existing file even if
        # the current view is filtered to a different extension.
        another.name.set("program.py")
        another.accept()
        self.assertEqual(another.result, str((self.folder / "program.py").resolve()))

    def test_json_filter_hides_hidden_entries_until_opted_in(self):
        dialog = self.chooser()
        self.assertFalse(dialog.show_hidden.get())
        self.assertNotIn(".git", self.visible(dialog))
        self.assertNotIn(".config", self.visible(dialog))
        self.assertNotIn(".secret.json", self.visible(dialog))
        dialog.filter_combo.set("JSON (*.json)")
        dialog.filter_changed()
        self.assertEqual(self.visible(dialog), {"data.json", "subfolder"})

        dialog.show_hidden.set(True)
        dialog.filter_changed()
        self.assertEqual(
            self.visible(dialog),
            {"data.json", "subfolder", ".git", ".config",
             ".secret.json"})
        self.assertNotIn(".bashrc", self.visible(dialog))

        dialog.show_hidden.set(False)
        dialog.filter_changed()
        self.assertEqual(self.visible(dialog), {"data.json", "subfolder"})

    def test_save_as_is_never_filtered(self):
        FileChooser.last_open_filter = "JSON (*.json)"
        dialog = self.chooser(save=True)
        self.assertFalse(hasattr(dialog, "file_filter"))
        self.assertEqual(self.visible(dialog),
                         {"draft.tex", "program.py", "data.json", "notes.md",
                          "subfolder", ".git", ".config", ".secret.json",
                          ".bashrc"})
        self.assertEqual(FileChooser.last_open_filter, "JSON (*.json)")


if __name__ == "__main__":
    unittest.main()
