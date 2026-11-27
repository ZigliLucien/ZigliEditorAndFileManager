"""Pure Markdown insertion helpers, shared by editor menus."""

MARKUP_ITEMS = (
    ("bold", "Bold"),
    ("italic", "Italic"),
    ("link", "Hyperlink"),
    ("image", "Image"),
    ("table", "Table (3 columns)"),
    ("code", "Fenced Code Block"),
    ("inline_math", "Inline Mathematics"),
    ("display_math", "Displayed Mathematics"),
    ("heading", "Section Heading"),
    ("quote", "Block Quote"),
)


def markdown_markup(kind, selected=""):
    """Return insertion text and cursor offset; never discard selection."""
    if kind in ("bold", "italic", "inline_math"):
        marker = {"bold": "**", "italic": "*", "inline_math": "$"}[kind]
        value = marker + selected + marker
        return value, len(marker) + len(selected)
    if kind in ("link", "image"):
        label = selected or ("description" if kind == "image" else "link text")
        label = label.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
        prefix = ("!" if kind == "image" else "") + "[" + label + "]("
        return prefix + ")", len(prefix)
    if kind == "code":
        fence = chr(96) * 3
        while fence in selected:
            fence += chr(96)
        prefix = "\n" + fence + "\n"
        return prefix + selected + "\n" + fence + "\n", len(prefix)
    if kind == "display_math":
        marker = "$" * 2
        prefix = "\n" + marker + "\n"
        return prefix + selected + "\n" + marker + "\n", len(prefix) + len(selected)
    if kind == "heading":
        return "## " + selected, 3 + len(selected)
    if kind == "quote":
        value = "\n".join("> " + line for line in selected.split("\n"))
        return value, len(value)
    if kind == "table":
        if selected:
            raise ValueError("Clear the selection before inserting a table")
        value = ("\n| Column 1 | Column 2 | Column 3 |\n"
                 "| --- | --- | --- |\n"
                 "|  |  |  |\n")
        return value, value.index("|  |") + 2
    raise ValueError("Unknown Markdown insertion: " + kind)
