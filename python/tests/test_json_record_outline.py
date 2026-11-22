"""Record-outline summaries and GUI navigation for JSON streams."""
import tkinter as tk
import unittest
from unittest import mock

from zefm.editor.json_records import record_bounds, outline_rows
from zefm.editor.gui.tk_editor import Window


class OutlineRowsTests(unittest.TestCase):
    def test_multiline_start_lines_and_previews(self):
        source = '{"name": "first"}\n{\n  "name": "second",\n  "id": 2\n}\n{"name": "third"}'
        rows = outline_rows(source, record_bounds(source))
        self.assertEqual([row[1] for row in rows], [1, 2, 6])
        self.assertEqual([row[0] for row in rows], [1, 2, 3])
        self.assertIn("second", rows[1][2])

    def test_large_jsonl_outline(self):
        source = "".join('{"id": %d}\n' % i for i in range(10000))
        rows = outline_rows(source, record_bounds(source))
        self.assertEqual(len(rows), 10000)
        self.assertEqual(rows[-1][1], 10000)
        self.assertIn("9999", rows[-1][2])


class OutlineGuiTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("Tk display unavailable")
        self.addCleanup(self.root.destroy)
        self.app = Window(self.root)
        self.widget, _ = self.app.current()
        self.widget.delete("1.0", "end")
        self.widget.insert("1.0", '{"a":1}\n{"b":2}\n{"c":3}')
        self.app.buffer_modes[self.app.tabs.select()] = self.app.mode_registry.modes["json"]

    def test_outline_opens_and_jumps_to_record(self):
        self.app.show_json_record_outline()
        dialog = next(w for w in self.root.winfo_children()
                      if isinstance(w, tk.Toplevel) and w.title() == "JSON Record Outline")
        lists = []
        def walk(w):
            if isinstance(w, tk.Listbox):
                lists.append(w)
            for child in w.winfo_children():
                walk(child)
        walk(dialog)
        self.assertEqual(len(lists), 1)
        listing = lists[0]
        self.assertEqual(listing.size(), 3)
        listing.selection_clear(0, "end")
        listing.selection_set(2)
        listing.event_generate("<<ListboxSelect>>")
        def buttons(w):
            found=[]
            for child in w.winfo_children():
                if isinstance(child, __import__("tkinter").ttk.Button):
                    found.append(child)
                found.extend(buttons(child))
            return found
        go_to = next(b for b in buttons(dialog) if b.cget("text") == "Go To")
        go_to.invoke()
        self.assertEqual(self.widget.index("insert"), "3.0")
        dialog.destroy()

    def test_context_menu_includes_outline(self):
        self.app._fill_recent_files_menu(self.app.recent_popup)
        self.app._populate_mode_context_menu()
        popup=self.app.recent_popup
        index=next(i for i in range(popup.index("end")+1)
                   if popup.type(i) == "cascade"
                   and popup.entrycget(i, "label") == "JSON / jq Tools")
        submenu=popup.nametowidget(popup.entrycget(index, "menu"))
        labels=[submenu.entrycget(i, "label") for i in range(submenu.index("end")+1)
                if submenu.type(i) == "command"]
        self.assertIn("Record Outline...", labels)


if __name__ == "__main__":
    unittest.main()
