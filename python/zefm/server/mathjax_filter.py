"""Python equivalent of the user's makepage | mathjaxfilterr pipeline.

The original Perl filter inserted MathJax v2, jQuery mathformat.js, and
math.css just before </head>.  ZEFM already ports mathformat.js into
server-side Python, so only MathJax and its *local* configuration are
inserted here.  The MathJax bundle is HTTPS-hosted by jsDelivr unless a
future locally installed bundle is configured.
"""
from __future__ import annotations
import re

MATHJAX_BUNDLE = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-svg.js"
MATHJAX_CONFIG_URL = "/mathjax-config.js"

# Browser document is sandboxed with an opaque origin.  Allow scripts for
# MathJax but NOT allow-same-origin, forms, frames, or arbitrary connections.
# SVG output has no external webfont requirement.
MATHJAX_PREVIEW_CSP = (
    "sandbox allow-scripts; default-src 'none'; "
    "script-src 'self' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; font-src 'self' data:; "
    "connect-src 'none'; base-uri 'none'; form-action 'none'; "
    "frame-ancestors 'none'; object-src 'none'"
)

_HEAD_CLOSE = re.compile(r"</head\s*>", re.IGNORECASE)
_HTML_OPEN = re.compile(r"<html(?:\s[^>]*)?>", re.IGNORECASE)
_ALREADY = re.compile(r'<script[^>]*src=["\']/mathjax-config\.js["\']', re.IGNORECASE)

_INSERT = (
    '<script defer src="/mathjax-config.js"></script>\n'
    '<script defer src="' + MATHJAX_BUNDLE + '"></script>\n'
)


def inject_mathjax(markup: str) -> str:
    """Inject MathJax into a complete HTML page, just as mathjaxfilterr did.

    Unlike Perl's line-based filter, handles multiline/attributed <head>
    tags, uppercase tags and a missing head.  Idempotent for repeated passes.
    """
    if _ALREADY.search(markup):
        return markup
    match = _HEAD_CLOSE.search(markup)
    if match:
        return markup[:match.start()] + _INSERT + markup[match.start():]
    match = _HTML_OPEN.search(markup)
    if match:
        return (markup[:match.end()] + '<head>' + _INSERT + '</head>'
                + markup[match.end():])
    return ('<!doctype html><html><head>' + _INSERT +
            '</head><body>' + markup + '</body></html>')
