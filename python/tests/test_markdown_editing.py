import unittest

from zefm.editor.markdown_outline import markdown_outline, adjacent_heading
from zefm.editor.syntax_highlight import syntax_spans, COLORS
from zefm.editor.shortcut_config import load_menus


class MarkdownEditingTests(unittest.TestCase):
    def test_headings_and_offsets(self):
        text = "# Introduction\n\nÉquations\n---------\n\n### Details ###\n"
        headings = markdown_outline(text)
        self.assertEqual([(h.level, h.title) for h in headings],
                         [(1, "Introduction"), (2, "Équations"), (3, "Details")])
        self.assertEqual(headings[1].offset, text.index("Équations"))
        self.assertEqual(headings[2].offset, text.index("###"))

    def test_fenced_and_indented_code_not_headings(self):
        fence = chr(96) * 3
        text = ("# Real\n" + fence + "python\n# fake\n" + fence +
                "\n    # also fake\n~~~\n## fake\n~~~~\n## Next\n")
        self.assertEqual([h.title for h in markdown_outline(text)], ["Real", "Next"])

    def test_navigation(self):
        text = "# A\n\n## B\n\n### C\n"
        middle = text.index("## B")
        self.assertEqual(adjacent_heading(text, middle, "next").title, "C")
        self.assertEqual(adjacent_heading(text, middle, "previous").title, "A")
        self.assertIsNone(adjacent_heading(text, 0, "previous"))
        self.assertIsNone(adjacent_heading(text, len(text), "next"))

    def test_styles(self):
        text = "# Title\n\n**bold** *italic* [link](a.md) $x+y$\n- item\n"
        marked = [(text[a:b], style) for a, b, style in syntax_spans(text, "markdown")]
        for item in (("# Title", "heading"), ("**bold**", "keyword"),
                     ("*italic*", "string"), ("[link](a.md)", "command"),
                     ("$x+y$", "math"), ("- ", "command")):
            self.assertIn(item, marked)
        self.assertTrue(all(style in COLORS for _, style in marked))

    def test_outline_shortcut(self):
        commands = load_menus()["Edit"]
        self.assertEqual(next(c.shortcut for c in commands
                              if c.label == "Markdown Document Outline"),
                         "Ctrl+Shift+H")


if __name__ == "__main__":
    unittest.main()
