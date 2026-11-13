"""Select a LaTeX master document without changing included-file buffers.

Explicit per-tab choices take precedence over the conventional TeX magic
comment: % !TEX root = ../main.tex
No root search, recursive project scanning, or shell interpretation.
"""
from pathlib import Path
import re

_ROOT = re.compile(r"^\s*%\s*!\s*TEX\s+root\s*=\s*(.*?)\s*$", re.IGNORECASE)


def root_directive(source_text: str) -> str | None:
    """Read a TeX root directive from the first 20 source lines."""
    for line in source_text.splitlines()[:20]:
        match = _ROOT.match(line)
        if match:
            return match.group(1).strip() or None
    return None


def resolve_latex_master(source, source_text: str, explicit=None) -> Path:
    """Resolve the compilation target; no side effects or file creation.

    A missing, non-TeX, directory or symlink master is refused with a useful
    diagnostic instead of silently compiling the wrong document.
    """
    source = Path(source).expanduser().resolve()
    reference = explicit if explicit is not None else root_directive(source_text)
    if reference is None:
        return source
    reference = Path(reference).expanduser()
    candidate = reference if reference.is_absolute() else source.parent / reference
    if candidate.is_symlink():
        raise ValueError("LaTeX master must not be a symbolic link")
    target = candidate.resolve()
    if target.suffix.lower() != ".tex":
        raise ValueError("LaTeX master must be a .tex file")
    if not target.is_file():
        raise ValueError(f"LaTeX master does not exist: {target}")
    return target
