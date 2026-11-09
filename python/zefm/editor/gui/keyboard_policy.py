"""Platform-aware keyboard policy for native Tk text widget bindings."""

# Native macOS Cmd+Z performs Undo, but the historical F5/F6 shortcuts
# are distinct function keys and still require explicit Tk bindings.
NATIVE_MAC_TEXT_COMMANDS = frozenset({"Copy", "Cut", "Paste"})


def install_editor_shortcut(command, platform):
    """Avoid sending duplicate native edit events on macOS.

    Tk Aqua already binds Cmd+C/X/V to native Text class bindings.
    The historical F5/F6 Undo/Redo keys are separate and must be installed.
    Other editor actions (Open, Save, etc.) need explicit bindings.
    """
    return not (platform == "darwin" and command in NATIVE_MAC_TEXT_COMMANDS)
