"""Validated, optional shortcut overrides; original Java mapping is the default."""
import json
from pathlib import Path
from .command_registry import MENUS, Command


def load_menus(path=None):
    defaults = {group: list(commands) for group, commands in MENUS.items()}
    if path is None or not Path(path).exists():
        return defaults
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
    used = {}
    output = {}
    for group, commands in defaults.items():
        output[group] = []
        for command in commands:
            shortcut = overrides.get(command.label, command.shortcut)
            if shortcut is not None and (not isinstance(shortcut, str) or not shortcut.strip()):
                raise ValueError(f'Invalid shortcut for {command.label}')
            if shortcut:
                if shortcut in used:
                    raise ValueError(f'Duplicate shortcut {shortcut}: {used[shortcut]} and {command.label}')
                used[shortcut] = command.label
            output[group].append(Command(command.label, shortcut))
    return output
