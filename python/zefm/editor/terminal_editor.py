"""Minimal curses terminal editor for quick, menu-free file edits.

Designed for SSH, terminal shells and EDITOR integrations. The Tk GUI remains
independent. Ctrl-S saves; Ctrl-Q quits (twice to discard unsaved changes).
"""
from __future__ import annotations

import curses
from dataclasses import dataclass, field
from pathlib import Path
from .files import save_buffer
from .model import Buffer


@dataclass
class TextDocument:
    lines: list[str]
    row: int = 0
    col: int = 0
    dirty: bool = False
    kill_buffer: str = ""
    history: list = field(default_factory=list, repr=False)
    future: list = field(default_factory=list, repr=False)
    saved_text: str | None = field(default=None, repr=False)

    @classmethod
    def from_text(cls, text):
        return cls(text.split("\n"), saved_text=text)

    @property
    def text(self):
        return "\n".join(self.lines)

    def undo(self):
        if not self.history:
            return False
        self.future.append((self.text, self.row, self.col))
        text, self.row, self.col = self.history.pop()
        self.lines = text.split("\n")
        self.dirty = self.text != self.saved_text
        return True

    def redo(self):
        if not self.future:
            return False
        self.history.append((self.text, self.row, self.col))
        text, self.row, self.col = self.future.pop()
        self.lines = text.split("\n")
        self.dirty = self.text != self.saved_text
        return True

    def insert(self, text):
        if "\n" in text:
            raise ValueError("Insert one character at a time")
        current = self.lines[self.row]
        self.lines[self.row] = current[:self.col] + text + current[self.col:]
        self.col += len(text)
        self.dirty = True

    def newline(self):
        current = self.lines[self.row]
        self.lines[self.row] = current[:self.col]
        self.lines.insert(self.row + 1, current[self.col:])
        self.row += 1
        self.col = 0
        self.dirty = True

    def backspace(self):
        if self.col:
            current = self.lines[self.row]
            self.lines[self.row] = current[:self.col - 1] + current[self.col:]
            self.col -= 1
            self.dirty = True
        elif self.row:
            self.col = len(self.lines[self.row - 1])
            self.lines[self.row - 1] += self.lines.pop(self.row)
            self.row -= 1
            self.dirty = True

    def delete(self):
        current = self.lines[self.row]
        if self.col < len(current):
            self.lines[self.row] = current[:self.col] + current[self.col + 1:]
            self.dirty = True
        elif self.row + 1 < len(self.lines):
            self.lines[self.row] += self.lines.pop(self.row + 1)
            self.dirty = True

    def kill_line(self):
        """Emacs Ctrl-K: kill to line end, or the newline when at end."""
        current = self.lines[self.row]
        if self.col < len(current):
            self.kill_buffer = current[self.col:]
            self.lines[self.row] = current[:self.col]
        elif self.row + 1 < len(self.lines):
            self.kill_buffer = "\n"
            self.lines[self.row] += self.lines.pop(self.row + 1)
        else:
            self.kill_buffer = ""
            return
        self.dirty = True

    def yank(self):
        """Insert the most recently killed text (Ctrl-Y)."""
        if not self.kill_buffer:
            return
        for part_number, part in enumerate(self.kill_buffer.split("\n")):
            if part_number:
                self.newline()
            if part:
                self.insert(part)

    def move(self, row_delta=0, col_delta=0):
        if col_delta < 0 and self.col == 0 and self.row > 0:
            self.row -= 1
            self.col = len(self.lines[self.row])
        elif col_delta > 0 and self.col == len(self.lines[self.row]) and self.row + 1 < len(self.lines):
            self.row += 1
            self.col = 0
        else:
            self.row = max(0, min(len(self.lines) - 1, self.row + row_delta))
            self.col = max(0, min(len(self.lines[self.row]), self.col + col_delta))


def edit_screen(screen, path, document):
    """Edit one document, blocking until the user quits."""
    screen.keypad(True)
    curses.noecho()
    # Raw input delivers Ctrl-S and Ctrl-C to the editor instead of the TTY.
    # curses.wrapper restores the original terminal mode when we exit.
    curses.raw()
    top = 0
    left = 0
    message = ""
    confirm_quit = False
    ctrl_x_pending = False
    while True:
        height, width = screen.getmaxyx()
        if height < 3 or width < 12:
            screen.erase()
            screen.addstr(0, 0, "Resize terminal"[:max(0, width - 1)])
            screen.refresh()
            screen.get_wch()
            continue
        content_height = height - 1
        if document.row < top:
            top = document.row
        if document.row >= top + content_height:
            top = document.row - content_height + 1
        if document.col < left:
            left = document.col
        if document.col >= left + width - 1:
            left = document.col - width + 2
        screen.erase()
        for y in range(content_height):
            index = top + y
            if index >= len(document.lines):
                break
            # Avoid control characters that could distort terminal rendering.
            line = "".join(c if c.isprintable() else " " for c in document.lines[index])
            try:
                screen.addnstr(y, 0, line[left:], max(0, width - 1))
            except curses.error:
                pass
        status = (f" {path.name}{' *' if document.dirty else ''}"
                  f"  {document.row + 1}:{document.col + 1}"
                  f"  C-S Save  C-Q Quit  C-X C-S/C-C")
        if message:
            status = " " + message
        try:
            screen.addnstr(height - 1, 0, status.ljust(width - 1),
                           width - 1, curses.A_REVERSE)
            screen.move(min(document.row - top, content_height - 1),
                        min(max(document.col - left, 0), width - 2))
        except curses.error:
            pass
        screen.refresh()
        try:
            key = screen.get_wch()
        except curses.error:
            continue
        message = ""
        if ctrl_x_pending:
            ctrl_x_pending = False
            if key == "\x13":  # Ctrl-X Ctrl-S
                key = "\x13"
            elif key == "\x03":  # Ctrl-X Ctrl-C
                key = "\x11"
            else:
                message = "Unknown Ctrl-X command"
                continue
        elif key == "\x18":  # Ctrl-X prefix
            ctrl_x_pending = True
            message = "Ctrl-X: Ctrl-S save, Ctrl-C quit"
            continue
        if key == "\x11":  # Ctrl-Q / Ctrl-X Ctrl-C
            if document.dirty and not confirm_quit:
                message = "Unsaved changes. Quit again to discard; Ctrl-S to save."
                confirm_quit = True
                continue
            return
        confirm_quit = False
        if key == "\x13":  # Ctrl-S / Ctrl-X Ctrl-S
            try:
                save_buffer(Buffer(text=document.text, path=str(path)), str(path))
                document.dirty = False
                message = "Saved " + str(path)
            except (OSError, UnicodeError, ValueError) as exc:
                message = "Save failed: " + str(exc)
        elif key in (curses.KEY_UP, "\x10"):  # Up / Ctrl-P
            document.move(row_delta=-1)
        elif key in (curses.KEY_DOWN, "\x0e"):  # Down / Ctrl-N
            document.move(row_delta=1)
        elif key in (curses.KEY_LEFT, "\x02"):  # Left / Ctrl-B
            document.move(col_delta=-1)
        elif key in (curses.KEY_RIGHT, "\x06"):  # Right / Ctrl-F
            document.move(col_delta=1)
        elif key in (curses.KEY_HOME, "\x01"):
            document.col = 0
        elif key in (curses.KEY_END, "\x05"):
            document.col = len(document.lines[document.row])
        elif key == curses.KEY_PPAGE:
            document.move(row_delta=-content_height)
        elif key == curses.KEY_NPAGE:
            document.move(row_delta=content_height)
        elif key in (curses.KEY_BACKSPACE, "\x7f", "\b"):
            document.backspace()
        elif key in (curses.KEY_DC, "\x04"):  # Delete / Ctrl-D
            document.delete()
        elif key == "\x0b":  # Ctrl-K
            document.kill_line()
        elif key == "\x19":  # Ctrl-Y
            document.yank()
        elif key in ("\n", "\r", curses.KEY_ENTER):
            document.newline()
        elif key == "\t":
            document.insert("    ")
        elif isinstance(key, str) and key.isprintable():
            document.insert(key)


def run_terminal_editor(filename):
    """Run without Tk or any graphical-display requirement."""
    path = Path(filename).expanduser().resolve()
    if path.exists() and not path.is_file():
        raise OSError(f"Not a regular file: {path}")
    if not path.parent.is_dir():
        raise OSError(f"Parent directory does not exist: {path.parent}")
    source = path.read_text(encoding="utf-8") if path.exists() else ""
    curses.wrapper(edit_screen, path, TextDocument.from_text(source))
