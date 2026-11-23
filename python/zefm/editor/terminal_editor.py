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
    last_search: str = ""

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

    def goto_line(self, number):
        self.row = max(0, min(len(self.lines) - 1, int(number) - 1))
        self.col = 0

    def search(self, query, direction=-1, repeat=False, origin=None, remember=True):
        if not query:
            return False
        contents = self.text
        row, col = origin if origin is not None else (self.row, self.col)
        offset = sum(len(line) + 1 for line in self.lines[:row]) + col
        if direction < 0:
            cutoff = offset if repeat else offset + 1
            at = contents.rfind(query, 0, cutoff)
            if at < 0:
                at = contents.rfind(query, cutoff)
        else:
            start = offset + (1 if repeat else 0)
            at = contents.find(query, start)
            if at < 0:
                at = contents.find(query, 0, start)
        if at < 0:
            return False
        preceding = contents[:at]
        self.row = preceding.count("\n")
        self.col = len(preceding.rsplit("\n", 1)[-1])
        if remember:
            self.last_search = query
        return True

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


def render_document(screen, path, document, top=0, left=0, message=""):
    """Draw the visible text and status, returning the updated scroll offsets."""
    height, width = screen.getmaxyx()
    content_height = max(1, height - 1)
    top = min(top, document.row)
    if document.row >= top + content_height:
        top = document.row - content_height + 1
    left = min(left, document.col)
    if document.col >= left + width - 1:
        left = document.col - width + 2
    screen.erase()
    for y in range(content_height):
        index = top + y
        if index >= len(document.lines):
            break
        line = "".join(c if c.isprintable() else " " for c in document.lines[index])
        try:
            screen.addnstr(y, 0, line[left:], max(0, width - 1))
        except curses.error:
            pass
    status = (f" {path.name}{' *' if document.dirty else ''}"
              f"  {document.row + 1}:{document.col + 1}"
              f"  C-S Save  C-Q Quit  C-G Line  C-R Search")
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
    return top, left


def prompt_input(screen, label, on_change=None, redraw=None):
    """Editable status-line prompt; redraw document during incremental search."""
    entered = ""
    while True:
        height, width = screen.getmaxyx()
        if height < 2:
            return None
        if redraw is not None:
            redraw()
        display = (label + entered)[-max(1, width - 1):]
        try:
            screen.addnstr(height - 1, 0, display.ljust(width - 1),
                           max(0, width - 1), curses.A_REVERSE)
            screen.move(height - 1, min(len(label + entered), width - 2))
        except curses.error:
            pass
        screen.refresh()
        try:
            key = screen.get_wch()
        except curses.error:
            continue
        if key in ("\x1b", "\x07"):
            return None
        if key in ("\n", "\r", curses.KEY_ENTER):
            return entered
        if key in ("\x7f", "\b", curses.KEY_BACKSPACE):
            entered = entered[:-1]
        elif isinstance(key, str) and key.isprintable():
            entered += key
        else:
            continue
        if on_change is not None:
            on_change(entered)


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
        top, left = render_document(screen, path, document, top, left, message)
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
            elif key == "\x12":  # Ctrl-X Ctrl-R
                key = "REDO"
            elif key == "\x06":  # Ctrl-X Ctrl-F
                key = "SEARCH_FORWARD"
            else:
                message = "Unknown Ctrl-X command"
                continue
        elif key == "\x18":  # Ctrl-X prefix
            ctrl_x_pending = True
            message = "Ctrl-X: Ctrl-S save, Ctrl-C quit, Ctrl-F search, Ctrl-R redo"
            continue
        if key == "\x11":  # Ctrl-Q / Ctrl-X Ctrl-C
            if document.dirty and not confirm_quit:
                message = "Unsaved changes. Quit again to discard; Ctrl-S to save."
                confirm_quit = True
                continue
            return
        confirm_quit = False
        if key in ("\x1f", "\x1a"):  # Ctrl-_ or Ctrl-Z: Undo
            message = "Undo" if document.undo() else "Nothing to undo"
            continue
        if key == "REDO":  # Ctrl-X Ctrl-R: Redo
            message = "Redo" if document.redo() else "Nothing to redo"
            continue
        if key == "\x07":  # Ctrl-G: Go to Line
            response = prompt_input(screen, "Go to line: ")
            if response is not None:
                if response.strip().isdigit() and int(response) >= 1:
                    document.goto_line(int(response))
                    message = f"Line {document.row + 1}"
                else:
                    message = "Enter a positive line number"
            continue
        if key in ("\x12", "SEARCH_FORWARD"):  # backward / forward search
            direction = -1 if key == "\x12" else 1
            origin = (document.row, document.col)
            def preview(query):
                document.row, document.col = origin
                if query:
                    document.search(query, direction=direction,
                                    origin=origin, remember=False)
            response = prompt_input(
                screen, "Search backward: " if direction < 0 else "Search forward: ",
                on_change=preview,
                redraw=lambda: render_document(screen, path, document))
            if response is None:
                document.row, document.col = origin
                message = "Search cancelled"
            else:
                query = response or document.last_search
                document.row, document.col = origin
                if not query or not document.search(
                        query, direction=direction, repeat=not response):
                    message = "Not found" if query else "No previous search"
                else:
                    message = f"Found: {query}"
            continue
        before = (document.text, document.row, document.col)
        if key == "\x13":  # Ctrl-S / Ctrl-X Ctrl-S
            try:
                save_buffer(Buffer(text=document.text, path=str(path)), str(path))
                document.saved_text = document.text
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
        if document.text != before[0]:
            document.history.append(before)
            if len(document.history) > 100:
                document.history.pop(0)
            document.future.clear()
            document.dirty = document.text != document.saved_text


def run_terminal_editor(filename):
    """Run without Tk or any graphical-display requirement."""
    path = Path(filename).expanduser().resolve()
    if path.exists() and not path.is_file():
        raise OSError(f"Not a regular file: {path}")
    if not path.parent.is_dir():
        raise OSError(f"Parent directory does not exist: {path.parent}")
    source = path.read_text(encoding="utf-8") if path.exists() else ""
    curses.wrapper(edit_screen, path, TextDocument.from_text(source))
