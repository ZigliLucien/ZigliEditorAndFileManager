"""Single registry for menu display and shortcut dispatch.
File/Edit/Run accelerators transcribed from TPEditorX.java.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Command:
    label: str
    shortcut: str | None

MENUS = {
 "File": [Command(a,b) for a,b in zip(
 ["Open","Save","Save As","Revert Buffer","Print","Quit"],
 ["F9","F1","F3","Ctrl+F9","Ctrl+P","Ctrl+Q"])],
 "Edit": [Command(a,b) for a,b in zip(
 ["Refresh Buffer","Clear","Redo","Undo","Line Numbers","Find","Replace","Continue Find or Replace","Toggle ClickPad","Copy","Paste","Cut","Go to Matching LaTeX Delimiter","LaTeX Document Outline","Go to Line","Go to Record","Next Record","Previous Record"],
 ["F7","F8","F6","F5","Ctrl+F2","Ctrl+S","Ctrl+Shift+R","Ctrl+R","Ctrl+F","Ctrl+C","Ctrl+V","Ctrl+X","Ctrl+Shift+M","Ctrl+Shift+L","Ctrl+G",None,None,None])],
 "Run": [Command(a,b) for a,b in zip(
 ["Shell","Compile","Trace"],
 ["Ctrl+Shift+Z","F4","Ctrl+O"])]
}
class Registry:
    def __init__(self):
        self.commands = {c.label:c for menu in MENUS.values() for c in menu}
        self.keys = {c.shortcut:c.label for c in self.commands.values() if c.shortcut}
        self.handlers = {}
        if len(self.keys) != len(self.commands):
            raise ValueError("Duplicate accelerator")
    def bind(self, label, handler):
        if label not in self.commands: raise KeyError(label)
        self.handlers[label] = handler
    def invoke(self, label):
        if label not in self.handlers: raise NotImplementedError(label)
        return self.handlers[label]()
    def key(self, shortcut):
        return self.invoke(self.keys[shortcut])
