"""Human-readable description of original ZEFM Alt keyboard mappings."""
import unicodedata

_PUNCT = {
    91: '[', 93: ']', 59: ';', 44: ',', 46: '.', 47: '/',
    92: '\\', 222: "'", 45: '-', 61: '=',
}


def shortcut_name(keycode, modifier):
    """Represent Java keycode+modifier without assuming a physical keyboard."""
    if 65 <= keycode <= 90 or 48 <= keycode <= 57:
        key = chr(keycode)
    else:
        key = _PUNCT.get(keycode, f'VK_{keycode}')
    prefix = 'Alt+Meta+' if modifier == 'C' else 'Alt+Shift+' if modifier == 'S' else 'Alt+'
    return prefix + key


def mapping_rows(mapping):
    """Sorted (shortcut, Unicode output, character names) tuples."""
    rows = []
    for (keycode, modifier), entry in mapping.items():
        chars = entry.characters
        description = ' + '.join(
            f'U+{ord(ch):04X} {unicodedata.name(ch, "UNNAMED CHARACTER")}' for ch in chars
        )
        rows.append((shortcut_name(keycode,modifier),chars,description))
    return sorted(rows, key=lambda row: (row[0].casefold(), row[0]))


def mapping_text(mapping, name):
    lines = [f'{name} — ZEFM original Alt keymap',
             'Alt/Option keystrokes, as delivered by Tk (may conflict with OS shortcuts).', '']
    lines.extend(f'{shortcut:17} {chars:8} {description}'
                 for shortcut, chars, description in mapping_rows(mapping))
    return '\n'.join(lines) + '\n'
