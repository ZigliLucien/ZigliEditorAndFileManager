"""Process 03: GUI-independent Unicode editor buffer."""
from dataclasses import dataclass

@dataclass
class Buffer:
    text: str = ""
    path: str | None = None
    modified: bool = False

    def replace(self, start: int, end: int, replacement: str):
        if not (0 <= start <= end <= len(self.text)):
            raise IndexError("Invalid text range")
        self.text = self.text[:start] + replacement + self.text[end:]
        self.modified = True
