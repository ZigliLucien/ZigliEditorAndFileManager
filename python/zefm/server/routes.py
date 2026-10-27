"""Explicit, deliberately small local file-manager route registry."""
GET_ROUTES = frozenset({"/", "/browse", "/view", "/edit", "/raw", "/notes", "/note-edit", "/note-edit"})
POST_ROUTES = frozenset({"/edit", "/note-edit"})


def permitted(method: str, path: str) -> bool:
    return path in (GET_ROUTES if method == "GET" else POST_ROUTES if method == "POST" else ())
