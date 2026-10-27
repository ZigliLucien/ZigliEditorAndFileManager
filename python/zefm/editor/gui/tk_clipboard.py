"""Operating-system clipboard via Tk."""
import tkinter as tk
class TkClipboard:
    def __init__(self, window): self.window=window
    def read(self):
        try: return self.window.clipboard_get()
        except tk.TclError: return ""
    def write(self, value):
        self.window.clipboard_clear()
        self.window.clipboard_append(value)
        self.window.update_idletasks()
