"""Process 01: JSON configuration."""
import json
from pathlib import Path

DEFAULTS = {"encoding": "utf-8", "dictionary_dir": "dictionaries", "command_timeout": 30, "home_directory": "~", "remember_last_directory": True}

def load(path):
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    if not isinstance(data, dict):
        raise ValueError("Configuration must be a JSON object")
    result = {**DEFAULTS, **data}
    if result["encoding"].lower() != "utf-8":
        raise ValueError("ZEFM requires UTF-8")
    if not isinstance(result["command_timeout"], (int, float)) or result["command_timeout"] <= 0:
        raise ValueError("command_timeout must be positive")
    if not isinstance(result["home_directory"], str) or not result["home_directory"].strip():
        raise ValueError("home_directory must be a nonempty string")
    if type(result["remember_last_directory"]) is not bool:
        raise ValueError("remember_last_directory must be boolean")
    return result
