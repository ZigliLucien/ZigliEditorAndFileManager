"""Independent, literal, case-sensitive Emacs-style query-replace engine."""
from dataclasses import dataclass

@dataclass
class QueryReplace:
    text: str
    needle: str
    replacement: str
    cursor: int = 0
    replaced: int = 0
    skipped: int = 0
    done: bool = False

    def __post_init__(self):
        if not self.needle:
            raise ValueError('Search string must not be empty')
        self.advance()

    def advance(self):
        self.match = self.text.find(self.needle, self.cursor)
        if self.match < 0:
            self.done = True
        return self.match

    def answer(self, key):
        if self.done:
            return self.match
        if key == 'q':
            self.done = True
            return self.match
        if key not in ('y', 'n', '!'):
            raise ValueError('Expected y, n, !, or q')
        if key == '!':
            while not self.done:
                self.answer('y')
            return self.match
        start = self.match
        if key == 'y':
            self.text = self.text[:start] + self.replacement + self.text[start + len(self.needle):]
            self.cursor = start + len(self.replacement)
            self.replaced += 1
        else:
            self.cursor = start + len(self.needle)
            self.skipped += 1
        return self.advance()
