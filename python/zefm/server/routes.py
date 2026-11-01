"""Explicit, deliberately small local file-manager route registry."""
GET_ROUTES = frozenset({
    "/", "/browse", "/view", "/edit", "/raw", "/notes", "/note-edit",
    "/rtl-keymap.js", "/copy", "/rename", "/move", "/listing", "/listing.css", "/listing.js",
    "/api/files", "/api/listing-page", "/pdf", "/site/",
})
POST_ROUTES = frozenset({
    "/edit", "/note-edit", "/open-editor", "/mkdir", "/copy", "/rename", "/move",
})


def permitted(method: str, path: str) -> bool:
    return (method == "GET" and path.startswith("/site/")) or path in (GET_ROUTES if method == "GET" else POST_ROUTES if method == "POST" else ())
