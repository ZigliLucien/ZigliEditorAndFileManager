"""Bounded, no-clobber extraction of one regular ZIP/TAR member.

Source-guided by NetsManager/XCommands.java:runT. The unsafe legacy
"Xtrax" destination is deliberately replaced with a root-confined,
explicitly selected existing directory and a flat output filename.
No archive entry paths are recreated, no symlinks are extracted.
"""
from __future__ import annotations

import io
import os
from pathlib import Path, PurePosixPath
import stat
import tarfile
import tempfile
from zipfile import ZipFile, BadZipFile

from .archive_preview import MAX_ARCHIVE_BYTES, MAX_MEMBERS
from .file_manager import BrowserError, _child_name
from .file_types import handler_for

MAX_EXTRACT_BYTES = 64 * 1024 * 1024
MAX_PREVIEW_BYTES = 1 * 1024 * 1024
_CHUNK = 1024 * 1024


def _member_name(name):
    """Validate the *archive* path, even though output is always flat."""
    if (not isinstance(name, str) or not name or name.startswith("/")
            or "\\" in name
            or any(ord(ch) < 32 or ord(ch) == 127 for ch in name)):
        raise BrowserError("Unsafe archive member name")
    parts = name.split("/")
    if (not parts or any(part in ("", "..") for part in parts)
            or (len(parts) > 0 and ":" in parts[0])):
        raise BrowserError("Unsafe archive member path")
    # A leading ./ from tar is harmless; reject any other dot component.
    if any(part == "." for part in parts[1:]):
        raise BrowserError("Unsafe archive member path")
    candidate = PurePosixPath(name)
    basename = candidate.name
    if basename in ("", ".", ".."):
        raise BrowserError("A regular file member must be selected")
    _child_name(basename)
    return basename


def _archive_source(files, relative):
    if handler_for(relative)["view"] != "archive":
        raise BrowserError("Not a supported ZIP or TAR archive", 415)
    file = files.resolve(relative)
    if not file.is_file() or (files.root / relative).is_symlink():
        raise BrowserError("Archive must be an ordinary file", 404)
    try:
        size = file.stat().st_size
    except OSError as exc:
        raise BrowserError(f"Cannot inspect archive: {exc}", 403) from exc
    if size > MAX_ARCHIVE_BYTES:
        raise BrowserError("Archive exceeds size limit", 413)
    return file


def _select_zip(archive, member):
    infos = archive.infolist()
    if len(infos) > MAX_MEMBERS:
        raise BrowserError("Archive has too many members", 413)
    matches = [info for info in infos if info.filename == member]
    if len(matches) != 1:
        raise BrowserError("Archive member missing or ambiguous", 409 if matches else 404)
    info = matches[0]
    mode = info.external_attr >> 16
    kind = stat.S_IFMT(mode)
    if info.is_dir() or (kind and kind != stat.S_IFREG):
        raise BrowserError("Only regular archive files can be extracted", 415)
    return info, info.file_size


def _select_tar(archive, member):
    matches = []
    for index, info in enumerate(archive):
        if index >= MAX_MEMBERS:
            raise BrowserError("Archive has too many members", 413)
        if info.name == member:
            matches.append(info)
            if len(matches) > 1:
                raise BrowserError("Archive has ambiguous duplicate members", 409)
    if not matches:
        raise BrowserError("Archive member not found", 404)
    info = matches[0]
    if not info.isfile():
        raise BrowserError("Only regular archive files can be extracted", 415)
    return info, info.size


def _checked_member(files, relative, member):
    """Validate target metadata without extracting or writing anything."""
    source = _archive_source(files, relative)
    name = _member_name(member)
    try:
        if source.name.casefold().endswith((".zip", ".jar", ".war", ".ear")):
            with ZipFile(source) as archive:
                info, size = _select_zip(archive, member)
        else:
            with tarfile.open(source, "r:*") as archive:
                info, size = _select_tar(archive, member)
    except (BadZipFile, tarfile.TarError, EOFError, OSError) as exc:
        raise BrowserError("Invalid or unreadable archive", 415) from exc
    if size > MAX_EXTRACT_BYTES:
        raise BrowserError("Archive member exceeds 64 MiB extraction limit", 413)
    return source, name, size


def member_details(files, relative, member):
    """Return a safe default filename and byte count for the confirmation."""
    _, name, size = _checked_member(files, relative, member)
    return name, size



def view_text_member(files, relative, member):
    """Read one small, ordinary UTF-8 archive member without writing a file.

    The byte limit and member metadata are checked *before* decompression.
    Streaming checks ensure even an archive with a forged size cannot push
    more data than declared or allowed into the in-memory preview.
    """
    source, _filename, expected_size = _checked_member(files, relative, member)
    if expected_size > MAX_PREVIEW_BYTES:
        raise BrowserError("Archive member exceeds the 1 MiB text preview limit", 413)
    original = source.stat()
    output = io.BytesIO()
    try:
        if source.name.casefold().endswith((".zip", ".jar", ".war", ".ear")):
            with ZipFile(source) as archive:
                info, size = _select_zip(archive, member)
                if size != expected_size or size > MAX_PREVIEW_BYTES:
                    raise BrowserError("Archive member changed; retry", 409)
                with archive.open(info) as reader:
                    _copy_limited(reader, output, expected_size)
        else:
            with tarfile.open(source, "r:*") as archive:
                info, size = _select_tar(archive, member)
                if size != expected_size or size > MAX_PREVIEW_BYTES:
                    raise BrowserError("Archive member changed; retry", 409)
                reader = archive.extractfile(info)
                if reader is None:
                    raise BrowserError("Archive member is unreadable", 415)
                with reader:
                    _copy_limited(reader, output, expected_size)
        after = source.stat()
        if ((original.st_ino, original.st_size, original.st_mtime_ns)
                != (after.st_ino, after.st_size, after.st_mtime_ns)):
            raise BrowserError("Archive changed during preview; retry", 409)
    except (BadZipFile, tarfile.TarError, EOFError, RuntimeError, OSError) as exc:
        raise BrowserError("Invalid or unreadable archive member", 415) from exc

    data = output.getvalue()
    if b"\\x00" in data:
        raise BrowserError("Binary archive members cannot be previewed as text", 415)
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise BrowserError("Archive member is not UTF-8 text", 415) from exc


def extract_entry(files, relative, member, destination_directory, new_name=""):
    """Extract ONE regular archive file to an existing directory.

    Temporary output is private and fsynced; publishing with hardlink
    guarantees no-clobber (even for a preexisting symlink). No directories
    are created; no external archive tools or commands are invoked.
    """
    source, suggested, expected_size = _checked_member(files, relative, member)
    destination = files.resolve(destination_directory)
    if not destination.is_dir():
        raise BrowserError("Destination directory does not exist", 404)
    # Check the *supplied* path before its symlinks are resolved; examining
    # only the final canonical path would miss a symlink to a directory
    # elsewhere inside the root. The existing root is always trusted.
    submitted = Path(destination_directory)
    if ".." in submitted.parts:
        raise BrowserError("Destination traversal is not allowed", 403)
    if submitted.parts[:1] == (".zefm-trash",):
        raise BrowserError("Cannot extract into ZEFM internal Trash", 403)
    current = files.root
    for segment in submitted.parts:
        current = current / segment
        if current.is_symlink():
            raise BrowserError("Destination contains a symbolic link", 403)
    relative_path = destination.relative_to(files.root)
    if relative_path.parts[:1] == (".zefm-trash",):
        raise BrowserError("Cannot extract into ZEFM internal Trash", 403)
    filename = _child_name(new_name) if new_name else suggested
    target = destination / filename
    temporary = None
    try:
        original = source.stat()
        with tempfile.NamedTemporaryFile(
                dir=destination, prefix=".zefm-extract-", delete=False) as output:
            temporary = Path(output.name)
            # Restrict permissions: archive bits must not create executables.
            os.fchmod(output.fileno(), 0o600)
            if source.name.casefold().endswith((".zip", ".jar", ".war", ".ear")):
                with ZipFile(source) as archive:
                    info, size = _select_zip(archive, member)
                    if size != expected_size or size > MAX_EXTRACT_BYTES:
                        raise BrowserError("Archive member changed; retry", 409)
                    with archive.open(info) as reader:
                        _copy_limited(reader, output, expected_size)
            else:
                with tarfile.open(source, "r:*") as archive:
                    info, size = _select_tar(archive, member)
                    if size != expected_size or size > MAX_EXTRACT_BYTES:
                        raise BrowserError("Archive member changed; retry", 409)
                    reader = archive.extractfile(info)
                    if reader is None:
                        raise BrowserError("Archive member is unreadable", 415)
                    with reader:
                        _copy_limited(reader, output, expected_size)
            output.flush()
            os.fsync(output.fileno())
        after = source.stat()
        if ((original.st_ino, original.st_size, original.st_mtime_ns)
                != (after.st_ino, after.st_size, after.st_mtime_ns)):
            raise BrowserError("Archive changed during extraction; retry", 409)
        # Exclusive publication: never replace files, symlinks or directories.
        os.link(temporary, target, follow_symlinks=False)
        return target
    except FileExistsError as exc:
        raise BrowserError("Destination already exists; nothing was extracted", 409) from exc
    except (BadZipFile, tarfile.TarError, EOFError, RuntimeError, OSError) as exc:
        raise BrowserError(f"Archive extraction failed: {exc}", 415) from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _copy_limited(reader, writer, expected_size):
    total = 0
    while chunk := reader.read(_CHUNK):
        total += len(chunk)
        if total > MAX_EXTRACT_BYTES or total > expected_size:
            raise BrowserError("Archive member expanded beyond allowed size", 413)
        writer.write(chunk)
    if total != expected_size:
        raise BrowserError("Archive member ended prematurely", 415)
