"""Choose the browser's navigation boundary separately from its initial folder.

The editor's last-used directory is a *starting location*, not a security root.
Never broaden an explicitly supplied --root option.
"""
from pathlib import Path


def browser_location(home, recent, explicit_root=None):
    if explicit_root is not None:
        root = Path(explicit_root).expanduser().resolve()
        return root, "."
    root = Path(home).expanduser().resolve()
    start = Path(recent).expanduser().resolve()
    if not start.is_dir():
        start = root
    if not start.is_relative_to(root):
        # Do not expand the browser boundary to / or an arbitrary common ancestor.
        # An outside-home working folder can still go Up once to its parent.
        root = start.parent
    return root, str(start.relative_to(root)) or "."
