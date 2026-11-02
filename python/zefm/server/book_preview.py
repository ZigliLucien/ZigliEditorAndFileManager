"""Safe local EPUB and DjVu previews for ZEFM.

EPUB is rendered as escaped chapter text (no executable book HTML).
DjVu pages use DjVuLibre's ddjvu, if installed, rendered to PNG.
"""
from __future__ import annotations

from html import escape
from pathlib import PurePosixPath
import io
import re
import shutil
import struct
import subprocess
from urllib.parse import urlencode
from xml.etree import ElementTree as ET
from zipfile import ZipFile, BadZipFile
import zlib

from .file_manager import BrowserError

MAX_BOOK_BYTES = 128 * 1024 * 1024
MAX_CHAPTER_BYTES = 2 * 1024 * 1024
MAX_RENDER_BYTES = 30 * 1024 * 1024
MAX_PIXELS = 12_000_000


def _document(files, relative, endings):
    path = files.resolve(relative)
    if not path.is_file() or path.suffix.casefold() not in endings:
        raise BrowserError("Unsupported document", 415)
    if path.stat().st_size > MAX_BOOK_BYTES:
        raise BrowserError("Document exceeds preview limit", 413)
    return path


def _inside(base, candidate):
    parts = PurePosixPath(base, candidate).parts
    if not parts or any(p == ".." for p in parts):
        raise BrowserError("Invalid EPUB internal path", 415)
    return str(PurePosixPath(*parts))


def _epub_spine(archive):
    try:
        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfile = next(n.attrib["full-path"] for n in container.iter()
                        if n.tag.endswith("rootfile"))
        opf = ET.fromstring(archive.read(rootfile))
    except (KeyError, StopIteration, ET.ParseError, ValueError) as exc:
        raise BrowserError("Invalid EPUB package", 415) from exc
    manifest = {n.attrib.get("id"): n.attrib for n in opf.iter()
                if n.tag.endswith("item") and n.attrib.get("id")}
    spine = [n.attrib.get("idref") for n in opf.iter() if n.tag.endswith("itemref")]
    base = str(PurePosixPath(rootfile).parent)
    if base == ".": base = ""
    return [_inside(base, manifest[idref]["href"].split("#")[0])
            for idref in spine if idref in manifest
            and manifest[idref].get("media-type") in {"application/xhtml+xml", "text/html"}]


def epub_page(files, relative, chapter=0):
    path = _document(files, relative, {".epub"})
    try:
        with ZipFile(path) as archive:
            if len(archive.infolist()) > 10000:
                raise BrowserError("EPUB has too many entries", 413)
            names = _epub_spine(archive)
            if not names:
                raise BrowserError("EPUB has no readable chapters", 415)
            if chapter < 0 or chapter >= len(names):
                raise BrowserError("Chapter out of range", 404)
            info = archive.getinfo(names[chapter])
            if info.file_size > MAX_CHAPTER_BYTES:
                raise BrowserError("Chapter exceeds preview limit", 413)
            source = archive.read(info).decode("utf-8", "replace")
        root = ET.fromstring(source)
        blocks = []
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1].lower() in {"p", "h1", "h2", "h3", "h4", "li", "blockquote", "pre"}:
                value = " ".join("".join(element.itertext()).split())
                if value: blocks.append("<p>" + escape(value) + "</p>")
        if not blocks:
            value = " ".join("".join(root.itertext()).split())
            blocks = ["<p>" + escape(value) + "</p>"]
    except (BadZipFile, KeyError, ET.ParseError, ValueError) as exc:
        raise BrowserError("Invalid or unsupported EPUB", 415) from exc
    def href(index):
        return "/view?" + urlencode({"path": relative, "chapter": index})
    navigation = (('<a href="' + escape(href(chapter - 1), quote=True) + '">← Previous</a> ') if chapter else "")
    navigation += f"Chapter {chapter + 1} of {len(names)}"
    if chapter + 1 < len(names):
        navigation += ' <a href="' + escape(href(chapter + 1), quote=True) + '">Next →</a>'
    body = "<h2>" + escape(path.name) + "</h2><nav>" + navigation + "</nav>"
    body += "".join(blocks) + "<hr><nav>" + navigation + "</nav>"
    return body


def _ppm_to_png(data):
    # ddjvu -format=ppm returns binary P6 RGB; reject other PNM variants.
    header = re.match(rb"P6\s+(?:#[^\n]*\n\s*)*(\d+)\s+(\d+)\s+(255)\s", data)
    if header is None:
        raise BrowserError("Unsupported DjVu raster output", 415)
    width, height = int(header[1]), int(header[2])
    if not (0 < width * height <= MAX_PIXELS):
        raise BrowserError("DjVu page is too large", 413)
    start = header.end()
    pixels = data[start:]
    if len(pixels) != width * height * 3:
        raise BrowserError("Invalid DjVu raster output", 415)
    stride = width * 3
    scanlines = b"".join(b"\0" + pixels[i:i + stride]
                         for i in range(0, len(pixels), stride))
    def chunk(kind, value):
        return (struct.pack(">I", len(value)) + kind + value +
                struct.pack(">I", zlib.crc32(kind + value) & 0xffffffff))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(scanlines)) + chunk(b"IEND", b""))


def djvu_page(files, relative, page=1):
    path = _document(files, relative, {".djvu", ".djv"})
    if not 1 <= page <= 10000:
        raise BrowserError("Page out of range", 404)
    executable = shutil.which("ddjvu")
    if not executable:
        raise BrowserError("DjVu preview requires DjVuLibre (ddjvu); download the file or install DjVuLibre", 501)
    try:
        output = subprocess.run([executable, "-format=ppm", f"-page={page}",
                                 "-size=1600x1600", str(path), "-"],
                                capture_output=True, timeout=25, check=False)
    except subprocess.TimeoutExpired as exc:
        raise BrowserError("DjVu rendering timed out", 504) from exc
    if output.returncode or len(output.stdout) > MAX_RENDER_BYTES:
        raise BrowserError("Could not render DjVu page", 415)
    return _ppm_to_png(output.stdout)
