"""Portable print preview for live editor buffers.

Render escaped UTF-8 text into a temporary local HTML document. The browser
provides its native Print / Save as PDF dialog; ZEFM never sends a print job
without explicit user action.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

MAX_PRINT_CHARS = 4_000_000


def render_print_html(text: str, title: str) -> str:
    if not isinstance(text, str) or not isinstance(title, str):
        raise ValueError("Print preview requires text and title strings")
    if len(text) > MAX_PRINT_CHARS:
        raise ValueError("Buffer is too large for print preview")
    # HTML escaping is essential: contents may be HTML, XML, TeX or code.
    safe_title = escape(title, quote=True)
    safe_text = escape(text, quote=False)
    return (
        '<!doctype html>\n<html lang="en"><head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<meta http-equiv="Content-Security-Policy" '
        'content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;">\n'
        f'<title>Print — {safe_title}</title>\n'
        '<style>\n'
        '@page { size: auto; margin: 18mm; }\n'
        'body { background: white; color: black; margin: 1.5rem auto; '
        'max-width: 100ch; padding: 0 1rem; }\n'
        'h1 { font: 600 16px system-ui,sans-serif; border-bottom: 1px solid #aaa; '
        'padding-bottom: .5rem; overflow-wrap: anywhere; }\n'
        'pre { font: 11pt/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,'
        '"DejaVu Sans Mono",monospace; white-space: pre-wrap; '
        'overflow-wrap: anywhere; tab-size: 4; }\n'
        '.help { font: 13px system-ui,sans-serif; color: #555; }\n'
        '@media print { body { margin: 0; padding: 0; max-width: none; } '
        '.help { display: none; } h1 { font-size: 11pt; } '
        'pre { font-size: 10pt; } }\n'
        '</style></head><body>\n'
        f'<h1>{safe_title}</h1>\n'
        '<p class="help">Use your browser’s Print command '
        '(Ctrl+P / Cmd+P) to print or save as PDF.</p>\n'
        f'<pre>{safe_text}</pre>\n'
        '</body></html>\n'
    )


def write_print_preview(text: str, title: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.write_text(render_print_html(text, title), encoding="utf-8")
    return output_path
