"""Non-mutating Markdown/HTML preview for calendar diary forms."""
from __future__ import annotations

from html import escape
from .diary_markup import render_diary
from ..storage.calendar_diary import valid_date, validated_record


def preview_page(args, csrf):
    """Return an escaped editable form and sanitized rendering, no CSV writes."""
    if "row" in args:
        required = {"csrf", "date", "new_date", "row", "revision", "kind", "text"}
        if set(args) != required:
            raise ValueError("Unexpected diary preview fields")
        valid_date(args["date"])
        validated_record(args["new_date"], args["kind"], args["text"])
        action = "/diary-edit"
        heading = "Preview diary changes"
        hidden = [("date", args["date"]), ("row", args["row"]),
                  ("revision", args["revision"]), ("new_date", args["new_date"])]
        save_label = "Save Changes"
    else:
        required = {"csrf", "date", "kind", "text"}
        if set(args) != required:
            raise ValueError("Unexpected diary preview fields")
        validated_record(args["date"], args["kind"], args["text"])
        action = "/diary"
        heading = "Preview new diary entry"
        hidden = [("date", args["date"])]
        save_label = "Add Entry"

    fields = [('<input type="hidden" name="' + escape(name, quote=True)
               + '" value="' + escape(value, quote=True) + '">')
              for name, value in hidden]
    kind_select = '<select name="kind">' + "".join(
        '<option value="' + kind + '"' + (' selected' if kind == args["kind"] else '')
        + '>' + kind.title() + '</option>'
        for kind in ("diary", "appointment")) + '</select>'
    form = (
        '<form method="post" action="' + action + '" accept-charset="utf-8">'
        '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
        + "".join(fields)
        + '<p><label>Entry type ' + kind_select + '</label></p>'
        '<p><label>Source Markdown / HTML<br><textarea name="text" required '
        'maxlength="4000" style="min-height:220px">'
        + escape(args["text"]) + '</textarea></label></p>'
        '<button type="submit" formaction="/diary-preview">Refresh Preview</button> '
        '<button type="submit">' + save_label + '</button></form>'
    )
    # The preview must never trigger an HTML parser to run arbitrary source.
    return ('<h1>' + heading + '</h1>'
            '<p>Preview only: nothing has been saved.</p>'
            '<section aria-label="Rendered diary preview">'
            '<h2>Rendered entry</h2>' + render_diary(args["text"])
            + '</section><hr><h2>Edit source or save</h2>'
            + form
            + '<p><small>Changes made in another editor may cause Save to report a conflict.</small></p>')
