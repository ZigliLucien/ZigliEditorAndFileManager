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
 ["Open","Save","Save As","Revert Buffer","Print","Quit","Insert File Template"],
 ["F9","F1","F3","Ctrl+F9","Ctrl+P","Ctrl+Q","Ctrl+Shift+T"])],
 "Edit": [Command(a,b) for a,b in zip(
 ["Refresh Buffer","Clear","Redo","Undo","Line Numbers","Find","Replace","Continue Find or Replace","Toggle ClickPad","Copy","Paste","Cut","Go to Matching LaTeX Delimiter","LaTeX Document Outline","Go to Line","Go to Record","Next Record","Previous Record","Markup Document Outline","Next Markup Heading","Previous Markup Heading"],
 ["F7","F8","F6","F5","Ctrl+F2","Ctrl+S","Ctrl+Shift+R","Ctrl+R","Ctrl+F","Ctrl+C","Ctrl+V","Ctrl+X","Ctrl+Shift+M","Ctrl+Shift+L","Ctrl+G",None,None,None,"Ctrl+Shift+H",None,None])],
 "Run": [Command(a,b) for a,b in zip(
 ["Shell","Compile","Trace","Run Script","Preview Document","Export Document PDF"],
 ["Ctrl+Shift+Z","F4","Ctrl+O","Ctrl+Shift+E","Ctrl+Shift+P",None])]
}
class Registry:
    def __init__(self):
        self.commands = {c.label:c for menu in MENUS.values() for c in menu}
        self.keys = {c.shortcut:c.label for c in self.commands.values() if c.shortcut}
        self.handlers = {}
        shortcut_count = sum(bool(c.shortcut) for c in self.commands.values())
        if len(self.keys) != shortcut_count:
            raise ValueError("Duplicate accelerator")
    def bind(self, label, handler):
        if label not in self.commands: raise KeyError(label)
        self.handlers[label] = handler
    def invoke(self, label):
        if label not in self.handlers: raise NotImplementedError(label)
        return self.handlers[label]()
    def key(self, shortcut):
        return self.invoke(self.keys[shortcut])
