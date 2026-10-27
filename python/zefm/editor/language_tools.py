"""Language-specific buffer expansion; never intercepts system keyboard input."""
from .dictionary import load_dictionary

LANGUAGES={"system": "System Default", "fr": "French", "yi": "Yiddish"}

def expand_suffix(text, cursor, entries):
    """Return (start, end, expansion) for longest shortcut before cursor, if any."""
    if not 0 <= cursor <= len(text):
        raise ValueError("Invalid cursor")
    matches=[key for key in entries if key and text[:cursor].endswith(key)]
    if not matches:
        return None
    key=max(matches,key=len)
    return cursor-len(key),cursor,entries[key]

def language_dictionary(directory, lang):
    if lang == "system":
        return {}
    if lang not in LANGUAGES:
        raise ValueError("Unknown language")
    return load_dictionary(directory,lang)
