"""ZEFM browser extensions: MIME detection separately from browser actions.

Keep legacy Mime.properties and MimeExtensions.properties compatible; these
defaults expand (not replace) the historic table. No archive is executed.
"""
from pathlib import Path
import mimetypes

_VIEW = {
    ".pdf": "pdf", ".ps": "postscript", ".eps": "postscript", ".epub": "epub", ".djvu": "djvu", ".djv": "djvu",
    ".html": "html", ".htm": "html", ".xhtml": "html",
    ".md": "markdown", ".markdown": "markdown", ".tex": "text",
    ".json": "structured", ".xml": "structured", ".ipynb": "structured",
    ".csv": "delimited", ".tsv": "delimited",
}
_IMAGES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".avif"}
_ARCHIVES = {".zip", ".jar", ".war", ".ear", ".tar", ".tgz",
             ".tar.gz", ".tbz", ".tbz2", ".tar.bz2", ".txz", ".tar.xz"}
_TEXT = {".txt", ".log", ".sty", ".cls", ".bib", ".aux", ".bbl",
         ".py", ".java", ".c", ".h", ".cc", ".cpp", ".rs", ".el",
         ".lua", ".sh", ".bash", ".zsh", ".js", ".mjs", ".css",
         ".xml", ".xsl", ".xslt", ".xsd", ".json", ".jsonl",
         ".yaml", ".yml", ".toml", ".ini", ".conf", ".cfg",
         ".properties", ".csv", ".tsv", ".sql", ".rb", ".pl",
         ".r", ".R", ".f", ".f90", ".maple", ".mpl"}
_BINARY = {".gz", ".bz2", ".xz", ".zst", ".7z", ".rar", ".class",
           ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
           ".odt", ".ods", ".odp", ".mp3", ".wav", ".ogg",
           ".flac", ".mp4", ".mov", ".webm", ".heic", ".tif", ".tiff",
           ".ps", ".eps", ".dvi", ".woff", ".woff2", ".ttf", ".otf"}
_MIME = {
    ".epub": "application/epub+zip", ".djvu": "image/vnd.djvu",
    ".djv": "image/vnd.djvu", ".jar": "application/java-archive",
    ".tgz": "application/gzip", ".tar.gz": "application/gzip",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif",
    ".svg": "image/svg+xml", ".mp3": "audio/mpeg",
    ".tex": "application/x-tex", ".dvi": "application/x-dvi",
}
_BUILDABLE = {".md": "discount", ".markdown": "discount", ".tex": "lualatex"}
_COMPOUND = (".tar.gz", ".tar.bz2", ".tar.xz")


def extension_for(name):
    lower = str(name).casefold()
    return next((ext for ext in _COMPOUND if lower.endswith(ext)),
                Path(lower).suffix)


def handler_for(name):
    ext = extension_for(name)
    if ext in _VIEW:
        view = _VIEW[ext]
    elif ext in _IMAGES:
        view = "image"
    elif ext in _ARCHIVES:
        view = "archive"
    elif ext in _TEXT:
        view = "text"
    elif ext in _BINARY or ext == ".svg":
        view = "download"
    else:
        view = "download"  # Never decode an unknown binary as UTF-8.
    mime = _MIME.get(ext) or mimetypes.guess_type(str(name))[0] or "application/octet-stream"
    return {"view": view, "build": _BUILDABLE.get(ext), "mime": mime,
            "extension": ext}
