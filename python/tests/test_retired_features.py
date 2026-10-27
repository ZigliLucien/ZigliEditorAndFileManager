"""Prevent retired Java features from being reintroduced."""
import unittest
from pathlib import Path
from zefm.editor.modes import ModeRegistry
from zefm.editor.command_registry import MENUS

ROOT=Path(__file__).resolve().parents[1]
RETIRED_MODES={'txml','hxml','jxml','clsv'}
RETIRED_ACTIONS={'remote save','remote edit','upload','ftp'}

class RetiredFeaturesTests(unittest.TestCase):
    def test_retired_modes_absent(self):
        registry=ModeRegistry.load(ROOT/'config/modes.json')
        self.assertFalse(RETIRED_MODES.intersection(registry.modes))
        self.assertFalse(RETIRED_MODES.intersection(registry.extensions.values()))
        self.assertFalse(RETIRED_MODES.intersection(registry.filenames.values()))

    def test_retired_utils_absent(self):
        self.assertFalse(RETIRED_ACTIONS.intersection(
            item.label.casefold() for items in MENUS.values() for item in items))
