"""Validate bounded browser image previews using actual file signatures.

This is not a full image decoder. It avoids interpreting unrelated files as
images based solely on their extensions; browsers handle rendering.
"""
from pathlib import Path
from .file_manager import BrowserError

MAX_IMAGE_BYTES = 32 * 1024 * 1024
_SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".avif"}


def valid_image_header(extension, header):
    extension = extension.casefold()
    if extension in (".jpg", ".jpeg"):
        return header.startswith(bytes.fromhex("ff d8 ff"))
    if extension == ".png":
        return header.startswith(bytes.fromhex("89 50 4e 47 0d 0a 1a 0a"))
    if extension == ".gif":
        return header.startswith((b"GIF87a", b"GIF89a"))
    if extension == ".webp":
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    if extension == ".bmp":
        return header.startswith(b"BM")
    if extension == ".avif":
        # ISO Base Media File Format (AVIF brands in ftyp).
        return (len(header) >= 16 and header[4:8] == b"ftyp"
                and any(brand in header[8:32] for brand
                        in (b"avif", b"avis", b"mif1", b"msf1")))
    return False


def image_preview(files, relative, extension):
    if extension.casefold() not in _SUPPORTED:
        raise BrowserError("Unsupported image type", 415)
    image = files.resolve(relative)
    if not image.is_file():
        raise BrowserError("Image not found", 404)
    if image.stat().st_size > MAX_IMAGE_BYTES:
        raise BrowserError("Image too large to preview", 413)
    with image.open("rb") as stream:
        header = stream.read(32)
        if not valid_image_header(extension, header):
            raise BrowserError("Invalid image signature", 415)
        return header + stream.read()
