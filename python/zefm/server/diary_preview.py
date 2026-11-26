"""Non-mutating Markdown/HTML preview for calendar diary forms."""
from __future__ import annotations

from html import escape
from urllib.parse import urlencode
from .appointment_conflicts import overlapping_candidates
from .calendar_pages import appointment_meta
from .diary_markup import render_diary
from ..storage.calendar_diary import valid_date, validated_record


def preview_page(args, csrf, store=None):
    """Return an escaped editable form and sanitized rendering, no CSV writes."""
    if "row" in args:
        required = {"csrf", "date", "new_date", "row", "revision", "kind", "text"}
        meta_names = {"start_time", "end_time", "timezone", "location"}
        if set(args) not in (required, required | meta_names):
            raise ValueError("Unexpected diary preview fields")
        valid_date(args["date"])
        meta = ({key: args[key] for key in meta_names}
                if meta_names <= set(args) else {})
        candidate = validated_record(args["new_date"], args["kind"], args["text"], **meta)
        action = "/diary-edit"
        heading = "Preview diary changes"
        hidden = [("date", args["date"]), ("row", args["row"]),
                  ("revision", args["revision"]), ("new_date", args["new_date"])]
        save_label = "Save Changes"
    else:
        required = {"csrf", "date", "kind", "text"}
        meta_names = {"start_time", "end_time", "timezone", "location"}
        if set(args) not in (required, required | meta_names):
            raise ValueError("Unexpected diary preview fields")
        meta = ({key: args[key] for key in meta_names}
                if meta_names <= set(args) else {})
        candidate = validated_record(args["date"], args["kind"], args["text"], **meta)
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
    metadata_fields = ""
    if meta:
        metadata_fields = (
            '<fieldset><legend>Appointment time and place</legend>'
            + ''.join('<p><label>' + escape(label)
                      + ' <input name="' + escape(name) + '" value="'
                      + escape(meta[name], quote=True) + '"'
                      + (' type="time"' if name in ("start_time", "end_time")
                         else ' maxlength="' + ('100' if name == "timezone" else "500") + '"')
                      + '></label></p>'
                      for name, label in (
                          ("start_time", "Start"), ("end_time", "End"),
                          ("timezone", "Timezone"), ("location", "Location")))
            + '</fieldset>')
    form = (
        '<form method="post" action="' + action + '" accept-charset="utf-8">'
        '<input type="hidden" name="csrf" value="' + escape(csrf, quote=True) + '">'
        + "".join(fields)
        + '<p><label>Entry type ' + kind_select + '</label></p>'
        + metadata_fields
        + '<p><label>Source Markdown / HTML<br><textarea name="text" required '
        'maxlength="4000" style="min-height:220px">'
        + escape(args["text"]) + '</textarea></label></p>'
        '<button type="submit" formaction="/diary-preview">Refresh Preview</button> '
        '<button type="submit">' + save_label + '</button></form>'
    )
    warnings = ""
    if store is not None and candidate.get("start_time"):
        exclude = int(args["row"]) if "row" in args else None
        matches = overlapping_candidates(
            candidate, store.read(), exclude_index=exclude)
        if matches:
            details = []
            for index, entry in matches:
                href = "/diary-edit?" + urlencode({
                    "date": entry["date"], "row": index})
                # Show the date, locally converted time, and escaped title.
                details.append(
                    '<li><a href="' + escape(href, quote=True) + '">'
                    + escape(entry["text"].splitlines()[0][:100])
                    + '</a> · ' + appointment_meta(entry) + '</li>')
            warnings = (
                '<section aria-label="Appointment overlap warnings">'
                '<h2>⚠ Scheduling overlap</h2>'
                '<p>This appointment overlaps an existing appointment. '
                'You can still save it.</p><ul>'
                + "".join(details) + '</ul></section>')
    # The preview must never trigger an HTML parser to run arbitrary source.
    return ('<h1>' + heading + '</h1>'
            '<p>Preview only: nothing has been saved.</p>'
            '<section aria-label="Rendered diary preview">'
            '<h2>Rendered entry</h2>' + render_diary(args["text"])
            + '</section>' + warnings + '<hr><h2>Edit source or save</h2>'
            + form
            + '<p><small>Changes made in another editor may cause Save to report a conflict.</small></p>')
