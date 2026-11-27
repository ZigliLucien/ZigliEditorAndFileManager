"""Starter files for the desktop editor, independent of Tk."""
from dataclasses import dataclass


@dataclass(frozen=True)
class FileTemplate:
    text: str
    cursor: str


TEMPLATES = {
    "latex": FileTemplate(
        "\\documentclass{amsart}\n\n\\begin{document}\n\n\\end{document}\n", "4.0"),
    "html": FileTemplate(
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '  <meta charset="utf-8">\n  <title>Title</title>\n'
        '</head>\n<body>\n  \n</body>\n</html>\n', "8.2"),
    "markdown": FileTemplate("# Title\n\n", "1.2"),
    "python": FileTemplate("#!/usr/bin/env python3\n\n", "3.0"),
    "perl": FileTemplate("#!/usr/bin/env perl\n\nuse strict;\nuse warnings;\n\n", "6.0"),
}


def file_template(mode, current_text=""):
    """Return a starter only for an empty buffer; never overwrite source."""
    if current_text:
        raise ValueError("Insert File Template requires an empty buffer")
    try:
        return TEMPLATES[mode]
    except KeyError:
        raise ValueError("Choose latex, python, perl, markdown, or html") from None
