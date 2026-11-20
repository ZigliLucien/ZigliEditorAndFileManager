"""Commands without accelerators must not cause a duplicate shortcut error."""
import unittest

from zefm.editor.command_registry import Registry


class RegistryOptionalShortcutTests(unittest.TestCase):
    def test_unbound_shortcuts_are_permitted(self):
        registry = Registry()
        self.assertIn("Go to Record", registry.commands)
        self.assertIsNone(registry.commands["Go to Record"].shortcut)
        self.assertEqual(registry.keys["Ctrl+G"], "Go to Line")

    def test_register_handlers_for_commands_without_shortcuts(self):
        registry = Registry()
        called = []
        registry.bind("Go to Record", lambda: called.append("record"))
        registry.invoke("Go to Record")
        self.assertEqual(called, ["record"])


if __name__ == "__main__":
    unittest.main()
