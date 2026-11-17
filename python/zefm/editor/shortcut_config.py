"""Validated, optional shortcut overrides; original Java mapping is the default.

Fixed New/Close Buffer keys live outside the legacy menu registry.
Reject collisions and malformed keyboard sequences before Tk installs them.
"""
import json
from pathlib import Path
from .command_registry import MENUS, Command

RESERVED_SHORTCUTS = {
    "Ctrl+N": "New Buffer",
    "Ctrl+Shift+W": "Close Buffer",
}
MODIFIERS = {"Ctrl", "Shift", "Alt", "Command"}
KEYS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") | {
    f"F{i}" for i in range(1, 13)
}


def validate_shortcut(value):
    if value is None:
        return None
    if not isinstance(value, str) or value != value.strip() or not value:
        raise ValueError("Shortcut must be a nonempty string or null")
    parts = value.split("+")
    if not parts or parts[-1].upper() not in KEYS:
        raise ValueError(f"Invalid shortcut key: {value}")
    modifiers = parts[:-1]
    if any(part not in MODIFIERS for part in modifiers):
        raise ValueError(f"Invalid shortcut modifier: {value}")
    if len(set(modifiers)) != len(modifiers):
        raise ValueError(f"Duplicate modifier in shortcut: {value}")
    if not modifiers and parts[-1].upper() not in {f"F{i}" for i in range(1, 13)}:
        raise ValueError(f"Bare character shortcuts are not allowed: {value}")
    return value


def load_menus(path=None):
    defaults = {group: list(commands) for group, commands in MENUS.items()}
    if path is None or not Path(path).exists():
        overrides = {}
    else:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        if not isinstance(data, dict) or set(data) - {'shortcuts'}:
            raise ValueError('Keyboard configuration must contain only shortcuts')
        overrides = data.get('shortcuts', {})
        if not isinstance(overrides, dict):
            raise ValueError('shortcuts must be an object')
    labels = {command.label for group in defaults.values() for command in group}
    unknown = set(overrides) - labels
    if unknown:
        raise ValueError(f'Unknown editor command(s): {sorted(unknown)}')
    def signature(shortcut):
        parts = shortcut.split("+")
        return (frozenset(parts[:-1]), parts[-1].upper())

    used = {signature(key): label
            for key, label in RESERVED_SHORTCUTS.items()}
    output = {}
    for group, commands in defaults.items():
        output[group] = []
        for command in commands:
            shortcut = validate_shortcut(
                overrides.get(command.label, command.shortcut))
            if shortcut:
                # Modifier order does not affect actual Tk event dispatch.
                key = signature(shortcut)
                if key in used:
                    raise ValueError(
                        f'Duplicate shortcut {shortcut}: {used[key]} and {command.label}')
                used[key] = command.label
            output[group].append(Command(command.label, shortcut))
    return output
