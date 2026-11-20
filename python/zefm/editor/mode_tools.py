"""Pure mode operations, independent of Tk and external programs."""
import json

def indentation(mode):
    """Return the characters inserted by Tab in this mode."""
    return "\t" if mode.use_tabs else " " * mode.indent_width

def validate_json_details(text):
    """Return (valid, diagnostic, error offset) for the live JSON buffer."""
    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        diagnostic = f"JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})"
        if exc.msg == "Expecting value" and exc.pos < len(text) and text[exc.pos].isalpha():
            diagnostic += " — string values need double quotes"
        return False, diagnostic, exc.pos
    return True, "Valid JSON", None


def validate_json(text):
    """Return (valid, diagnostic); report line and column on errors."""
    valid, diagnostic, _offset = validate_json_details(text)
    return valid, diagnostic
