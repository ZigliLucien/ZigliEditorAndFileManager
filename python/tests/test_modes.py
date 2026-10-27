import unittest
from pathlib import Path
from zefm.editor.modes import ModeRegistry
CONFIG=Path(__file__).resolve().parents[1]/'config/modes.json'
class ModeTests(unittest.TestCase):
 def setUp(self):self.r=ModeRegistry.load(CONFIG)
 def test_extension_and_case(self):
  self.assertEqual(self.r.detect('abc.PY').name,'python')
  self.assertEqual(self.r.detect('paper.tex').name,'latex')
 def test_filename_precedence(self):self.assertEqual(self.r.detect('Makefile').name,'makefile')
 def test_content_and_fallback(self):
  self.assertEqual(self.r.detect(text='#!/usr/bin/env python3\nprint(1)').name,'python')
  self.assertEqual(self.r.detect(text='<?xml version="1.0"?>').name,'xml')
  self.assertEqual(self.r.detect('unknown.zzz').name,'text')
 def test_override(self):
  self.assertEqual(self.r.detect('a.py',override='markdown').name,'markdown')
  with self.assertRaises(ValueError):self.r.detect(override='unregistered')
 def test_validation(self):
  with self.assertRaises(ValueError):ModeRegistry({'default_mode':'text','extensions':{'.py':'bad'},'filenames':{},'modes':{'text':{}}})
 def test_indentation_settings(self):
  self.assertEqual(self.r.detect('a.tex').indent_width,2)
  self.assertTrue(self.r.detect('Makefile').use_tabs)
