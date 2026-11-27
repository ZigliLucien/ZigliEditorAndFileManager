import unittest

from zefm.editor.markup_tags import matching_tag, scan_tags, html_markup
from zefm.editor.syntax_highlight import syntax_spans


class MarkupTests(unittest.TestCase):
    def test_nested_html_and_case(self):
        text = '<DIV class="a>b"><div>text</div></div>'
        first_end = text.index('"><') + 2
        expected = ((0, first_end), (text.rindex("</div>"), len(text)))
        self.assertEqual(matching_tag(text, 2, "html"), expected)
        self.assertEqual(matching_tag(text, len(text), "html"), expected[::-1])

    def test_xml_namespaces_and_case(self):
        text = '<x:A><x:A/><x:B>text</x:B></x:A>'
        self.assertEqual(matching_tag(text, 1, "xml"),
                         ((0, 5), (text.rindex("</x:A>"), len(text))))
        self.assertIsNone(matching_tag(text, 8, "xml"))
        self.assertEqual(matching_tag("<A></a>", 1, "xml"), ((0, 3), None))

    def test_comments_cdata_and_declarations(self):
        text = '<?xml version="1.0"?><r><!--<bad>--><![CDATA[</r>]]><n/></r>'
        tokens, spans = scan_tags(text, "xml")
        self.assertEqual([name for _, name, _ in tokens], ["r", "n", "r"])
        self.assertIn("comment", {style for _, _, style in spans})
        self.assertIn("verbatim", {style for _, _, style in spans})

    def test_html_raw_text_and_void(self):
        text = '<div><br><script>let a = "<x>";</script><img src="a"></div>'
        tokens, _ = scan_tags(text, "html")
        self.assertEqual([name for _, name, _ in tokens],
                         ["div", "br", "script", "script", "img", "div"])
        self.assertEqual(matching_tag(text, 1, "html"),
                         ((0, 5), (text.rindex("</div>"), len(text))))
        self.assertIsNone(matching_tag(text, 7, "html"))

    def test_optional_html_end_tags(self):
        text = "<ul><li>one<li>two</ul>"
        self.assertEqual(matching_tag(text, 1, "html"),
                         ((0, 4), (text.index("</ul>"), len(text))))
        self.assertIsNone(matching_tag(text, 6, "html"))

    def test_unmatched(self):
        self.assertEqual(matching_tag("<a><b></a>", 4, "xml"),
                         ((3, 6), None))

    def test_insertions(self):
        self.assertEqual(html_markup("strong", "שלום"), ("<strong>שלום</strong>", 12))
        value, caret = html_markup("a", "notes")
        self.assertEqual(value, '<a href="">notes</a>')
        self.assertEqual(value[caret], '"')
        self.assertIn("<li>two</li>", html_markup("ul", "one\ntwo")[0])
        self.assertIn("&quot;", html_markup("img", 'a"b')[0])
        with self.assertRaises(ValueError):
            html_markup("table", "keep me")

    def test_xml_highlighting(self):
        self.assertTrue(syntax_spans("<x attr='value'/>", "xml"))


if __name__ == "__main__":
    unittest.main()
