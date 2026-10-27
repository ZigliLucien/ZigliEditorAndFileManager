"""Process 06: master editor controller, independent of GUI toolkit."""
from .model import Buffer
from .selection import EditorState
from .command_registry import Registry

class TPEditor:
    def __init__(self, clipboard, buffer=None):
        self.state = EditorState(buffer if buffer is not None else Buffer())
        self.clipboard = clipboard
        self.commands = Registry()
        self.commands.bind("Copy", lambda: self.state.copy(self.clipboard))
        self.commands.bind("Cut", lambda: self.state.cut(self.clipboard))
        self.commands.bind("Paste", lambda: self.state.paste(self.clipboard))

    def menu(self, label):
        return self.commands.invoke(label)

    def shortcut(self, accelerator):
        return self.commands.key(accelerator)
