"""Process 05: one UTF-8 JSON dictionary per language."""
import json
from pathlib import Path

def load_dictionary(directory, language):
    if not language or not all(c.isalnum() or c in "-_" for c in language):
        raise ValueError("Invalid language identifier")
    data = json.loads((Path(directory) / (language + ".json")).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
        raise ValueError("Dictionary must map shortcut strings to expansion strings")
    return data
