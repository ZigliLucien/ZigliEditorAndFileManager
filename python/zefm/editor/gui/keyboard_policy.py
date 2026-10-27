"""Platform-aware keyboard policy for native Tk text widget bindings."""

NATIVE_MAC_TEXT_COMMANDS = frozenset({"Copy", "Cut", "Paste", "Undo", "Redo"})


def install_editor_shortcut(command, platform):
    """Avoid sending duplicate native edit events on macOS.

    Tk Aqua already binds Cmd+C/X/V/Z to the native Text class bindings.
    Registering bind_all for these commands generates a second edit event.
    Other editor actions (Open, Save, etc.) need explicit bindings.
    """
    return not (platform == "darwin" and command in NATIVE_MAC_TEXT_COMMANDS)
