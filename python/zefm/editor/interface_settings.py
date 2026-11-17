"""Portable interface typography preferences, independent of editor text font."""
import json
import os
from pathlib import Path
import tempfile

DEFAULT_INTERFACE = {"size": 13}
MIN_INTERFACE_SIZE = 10
MAX_INTERFACE_SIZE = 24


def valid_interface(settings):
    return (isinstance(settings, dict)
            and type(settings.get("size")) is int
            and MIN_INTERFACE_SIZE <= settings["size"] <= MAX_INTERFACE_SIZE)


def read_interface(path):
    try:
        data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return dict(DEFAULT_INTERFACE)
    return {"size": data["size"]} if valid_interface(data) else dict(DEFAULT_INTERFACE)


def write_interface(path, settings):
    if not valid_interface(settings):
        raise ValueError("Interface font size must be between 10 and 24 points")
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", prefix=".interface-",
                suffix=".tmp", dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            if os.name == "posix":
                os.fchmod(output.fileno(), 0o600)
            json.dump({"size": settings["size"]}, output)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
