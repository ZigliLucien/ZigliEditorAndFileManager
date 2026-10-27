"""Pure mode operations, independent of Tk and external programs."""
import json

def indentation(mode):
    """Return the characters inserted by Tab in this mode."""
    return "\t" if mode.use_tabs else " " * mode.indent_width

def validate_json(text):
    """Return (valid, diagnostic); report line and column on errors."""
    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        return False, f"JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})"
    return True, "Valid JSON"
