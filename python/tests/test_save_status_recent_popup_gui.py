"""Bottom-edge Save status and right-click Recent Files (Tk/Xvfb).

The same recent-file history must feed the File menu and the context menu.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import tkinter as tk
import unittest
from unittest import mock

from zefm.editor.gui.tk_editor import Window
from zefm.editor.recent_files import RecentFiles


class SaveStatusRecentPopupTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.app = Window(self.root)
        self.app.recent_files = RecentFiles(Path(self.temp.name) / "recent.json")
        self.path = Path(self.temp.name) / "cœur ייִדיש.txt"
        self.path.write_text("initial text", encoding="utf-8")
        self.app._open_path(str(self.path))
        self.root.update()

    def test_save_indication_stays_at_bottom_after_cursor_movement(self):
        widget, editor = self.app.current()
        widget.insert("end", " modified")
        self.root.update()
        self.assertIn("Unsaved changes", self.app.save_indicator.get())
        self.app.save_file()
        self.root.update()
        self.assertEqual(self.path.read_text(encoding="utf-8"), "initial text modified")
        self.assertEqual(self.app.save_indicator.get(), "✓ Saved: cœur ייִדיש.txt")
        self.assertEqual(self.app.save_indicator_label.winfo_manager(), "grid")
        self.assertTrue(self.app.save_indicator_label.winfo_ismapped())
        self.assertIs(self.app.save_indicator_label.master, self.app.status_bar)
        widget.mark_set("insert", "1.0")
        self.app._status(widget)
        self.assertEqual(self.app.save_indicator.get(), "✓ Saved: cœur ייִדיש.txt")
        self.assertFalse(editor.state.buffer.modified)

        widget.insert("end", " new change")
        self.root.update()
        self.assertEqual(self.app.save_indicator.get(), "● Unsaved changes")
        self.assertTrue(editor.state.buffer.modified)

    def test_saved_status_remains_visible_below_slider_after_resize(self):
        # A previous Tk layout placed the notebook first and packed the
        # lengthy cursor/mode label before Save, hiding Save at small widths.
        widget, _editor = self.app.current()
        widget.insert("end", " updated")
        self.root.update()
        self.app.save_file()
        self.root.update()
        self.assertIn("✓ Saved:", self.app.save_indicator.get())

        # An arbitrarily long JSON/cursor message must never claim all the
        # bottom-row space or push the Save field off the window.
        self.app.status.set("Long status " * 120)
        self.root.geometry("640x420")
        self.root.update()
        indicator = self.app.save_indicator_label
        self.assertEqual(indicator.winfo_manager(), "grid")
        self.assertTrue(self.app.status_bar.winfo_ismapped())
        self.assertTrue(indicator.winfo_ismapped())
        self.assertGreater(indicator.winfo_width(), 100)
        self.assertLessEqual(indicator.winfo_rootx() + indicator.winfo_width(),
                             self.root.winfo_rootx() + self.root.winfo_width())
        self.assertGreater(indicator.winfo_rooty(), widget.winfo_rooty())
        self.assertEqual(self.app.save_indicator.get(), "✓ Saved: cœur ייִדיש.txt")

    def test_indicator_is_per_buffer_not_stale_after_tab_switch(self):
        widget, _editor = self.app.current()
        widget.insert("end", " edited")
        self.root.update()
        self.app.save_file()
        saved_tab = self.app.tabs.select()
        other = Path(self.temp.name) / "another.txt"
        other.write_text("another", encoding="utf-8")
        self.app._open_path(str(other))
        self.root.update()
        self.assertNotIn("Saved:", self.app.save_indicator.get())
        self.app.tabs.select(saved_tab)
        self.root.update()
        self.assertIn("✓ Saved:", self.app.save_indicator.get())

    def test_cancelled_conflicting_save_not_reported_as_saved(self):
        widget, _editor = self.app.current()
        widget.insert("end", " editor")
        self.root.update()
        self.path.write_text("external version", encoding="utf-8")
        with mock.patch("zefm.editor.gui.tk_editor.messagebox.askyesno", return_value=False):
            self.app.save_file()
        self.assertEqual(self.app.save_indicator.get(), "Save cancelled")
        self.assertEqual(self.path.read_text(encoding="utf-8"), "external version")
        self.assertIn(" editor", widget.get("1.0", "end-1c"))

    def test_right_click_uses_shared_recent_history_and_opens_file(self):
        recent = Path(self.temp.name) / "French and ייִדיש.tex"
        recent.write_text("x", encoding="utf-8")
        self.app.recent_files.record(recent)
        self.app.recent_files.record(self.path)
        self.app._fill_recent_files_menu(self.app.recent_popup)
        self.assertIn(str(self.path), self.app.recent_popup.entrycget(0, "label"))
        self.assertIn(str(recent), self.app.recent_popup.entrycget(1, "label"))
        self.app._populate_recent_files()
        self.assertEqual(self.app.recent_menu.entrycget(0, "label"),
                         self.app.recent_popup.entrycget(0, "label"))

        original_count = len(self.app.views)
        # The popup is anchored to the cursor but does not move the insertion mark.
        widget, _editor = self.app.current()
        widget.mark_set("insert", "1.2")
        before = widget.index("insert")
        with mock.patch.object(self.app.recent_popup, "tk_popup") as popup:
            result = self.app._show_recent_files_popup(
                SimpleNamespace(x_root=150, y_root=210))
        popup.assert_called_once_with(150, 210)
        self.assertEqual(result, "break")
        self.assertEqual(widget.index("insert"), before)

        self.app.recent_popup.invoke(1)
        self.root.update()
        self.assertEqual(Path(self.app.current()[1].state.buffer.path), recent)
        self.assertEqual(len(self.app.views), original_count + 1)

    def test_empty_recent_list_shows_open_file_option(self):
        self.app.recent_files.clear()
        self.app._fill_recent_files_menu(self.app.recent_popup)
        self.assertEqual(self.app.recent_popup.entrycget(0, "label"), "(No recent files)")
        self.assertEqual(self.app.recent_popup.entrycget(0, "state"), "disabled")
        labels = [self.app.recent_popup.entrycget(index, "label")
                  for index in range(self.app.recent_popup.index("end") + 1)
                  if self.app.recent_popup.type(index) == "command"]
        self.assertIn("Open File...", labels)
        self.assertIn("Clear Recent Files", labels)
        self.assertTrue(self.app.current()[0].bind("<Button-3>"))
        widget = self.app.current()[0]
        self.assertEqual(widget.bindtags()[0], "ZefmRecentFilesPopup")
        self.assertTrue(self.root.bind_class("ZefmRecentFilesPopup", "<Button-3>"))
        self.assertTrue(self.root.bind_class("ZefmRecentFilesPopup", "<Shift-F10>"))


if __name__ == "__main__":
    unittest.main()
