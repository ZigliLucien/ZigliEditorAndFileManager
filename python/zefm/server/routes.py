"""Explicit, deliberately small local file-manager route registry."""
GET_ROUTES = frozenset({
    "/", "/browse", "/new-file", "/view", "/edit", "/raw", "/notes", "/note-edit",
    "/rtl-keymap.js", "/copy", "/rename", "/move", "/delete", "/trash", "/extract-entry", "/listing", "/listing.css", "/listing.js", "/math.css", "/mathjax-config.js",
    "/api/files", "/api/listing-page", "/search-text", "/pdf", "/djvu-page", "/site/", "/build", "/build.js",
})
POST_ROUTES = frozenset({
    "/edit", "/note-edit", "/new-file", "/open-editor", "/mkdir", "/copy", "/rename", "/move", "/delete", "/restore", "/extract-entry", "/build",
})


def permitted(method: str, path: str) -> bool:
    return (method == "GET" and path.startswith("/site/")) or path in (GET_ROUTES if method == "GET" else POST_ROUTES if method == "POST" else ())
