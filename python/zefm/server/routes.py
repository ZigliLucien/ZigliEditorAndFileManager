"""Explicit, deliberately small local file-manager route registry."""
GET_ROUTES = frozenset({
    "/", "/browse", "/view", "/edit", "/raw", "/notes", "/note-edit",
    "/rtl-keymap.js", "/copy", "/listing", "/listing.css", "/listing.js",
    "/api/files", "/api/listing-page", "/pdf",
})
POST_ROUTES = frozenset({
    "/edit", "/note-edit", "/open-editor", "/mkdir", "/copy",
})


def permitted(method: str, path: str) -> bool:
    return path in (GET_ROUTES if method == "GET" else POST_ROUTES if method == "POST" else ())
