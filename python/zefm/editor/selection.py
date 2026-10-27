"""GUI-independent caret, selection and clipboard editing.

Offsets are Python Unicode string indices, not Java UTF-16 offsets. GUI adapters
must translate positions where needed. This is a foundation, not Swing parity.
"""
from dataclasses import dataclass
from .model import Buffer

@dataclass
class EditorState:
    buffer: Buffer
    point: int = 0
    mark: int | None = None

    def move(self, position: int, selecting: bool = False):
        if not 0 <= position <= len(self.buffer.text):
            raise IndexError("Caret outside buffer")
        if selecting:
            if self.mark is None: self.mark = self.point
        else:
            self.mark = None
        self.point = position

    def region(self):
        if self.mark is None or self.mark == self.point: return None
        return min(self.point, self.mark), max(self.point, self.mark)

    def selected_text(self):
        region = self.region()
        return "" if region is None else self.buffer.text[region[0]:region[1]]

    def copy(self, clipboard):
        region = self.region()
        if region is None: return False
        clipboard.write(self.selected_text())
        return True

    def cut(self, clipboard):
        region = self.region()
        if region is None: return False
        clipboard.write(self.selected_text())
        self.buffer.replace(*region, "")
        self.point, self.mark = region[0], None
        return True

    def paste(self, clipboard):
        value = clipboard.read()
        region = self.region()
        start,end = region if region is not None else (self.point,self.point)
        self.buffer.replace(start,end,value)
        self.point,self.mark = start+len(value),None
        return value

class MemoryClipboard:
    """Test double; GUI adapter must supply the operating-system clipboard."""
    def __init__(self, text=""): self.text=text
    def read(self): return self.text
    def write(self, text): self.text=text
