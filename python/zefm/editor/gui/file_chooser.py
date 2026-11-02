"""Mouse-wheel-friendly file chooser for the Tk ZEFM editor.

Unlike some Tk native file dialog builds, a Treeview gives predictable
Linux/X11 Button-4/5 and Windows/macOS MouseWheel behavior.  The wheel
advances the current file selection, and the list scrolls with it.
No filesystem writes happen in this dialog.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


def wheel_steps(event):
    """Number of visible rows to move; positive means down the file list."""
    number = getattr(event, "num", None)
    if number == 4:
        return -1
    if number == 5:
        return 1
    delta = getattr(event, "delta", 0)
    if not delta:
        return 0
    # X11/macOS and Windows report different units and possibly smooth deltas.
    if abs(delta) >= 120:
        return -int(delta / 120)
    return -1 if delta > 0 else 1


def directory_entries(folder):
    """Directories first, then files, sorted case-insensitively."""
    entries = [p for p in Path(folder).iterdir() if not p.is_symlink()]
    return sorted(entries, key=lambda p: (not p.is_dir(), p.name.casefold(), p.name))


class FileChooser(tk.Toplevel):
    def __init__(self, parent, initialdir, *, save=False, initialfile=""):
        super().__init__(parent)
        self.withdraw()
        self.parent = parent
        self.save_mode = save
        self.folder = Path(initialdir).expanduser().resolve()
        if not self.folder.is_dir():
            self.folder = Path.home()
        self.result = None
        self.title("ZEFM — " + ("Save As" if save else "Open File"))
        self.geometry("780x530")
        self.minsize(460, 320)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        header = ttk.Frame(self, padding=(10, 8))
        header.pack(fill="x")
        ttk.Button(header, text="Up", command=self.go_up).pack(side="left")
        self.location = tk.StringVar()
        ttk.Label(header, textvariable=self.location, anchor="w").pack(
            side="left", fill="x", expand=True, padx=(10, 0))
        area = ttk.Frame(self, padding=(10, 0))
        area.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(area, columns=("size", "type"), show="tree headings",
                                 selectmode="browse")
        self.tree.heading("#0", text="Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("type", text="Type")
        self.tree.column("#0", minwidth=180, width=450, stretch=True)
        self.tree.column("size", minwidth=65, width=95, anchor="e", stretch=False)
        self.tree.column("type", minwidth=70, width=95, stretch=False)
        bar = ttk.Scrollbar(area, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=bar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")

        # Bind on the list, not bind_all: no interference with the editor
        # or other dialogs. Linux wheel buttons and Windows/macOS MouseWheel.
        for event in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.tree.bind(event, self.on_wheel)
        self.tree.bind("<Double-1>", self.activate)
        self.tree.bind("<Return>", self.activate)
        self.tree.bind("<BackSpace>", lambda event: self.go_up() or "break")

        bottom = ttk.Frame(self, padding=(10, 8))
        bottom.pack(fill="x")
        ttk.Label(bottom, text="File name:").pack(side="left")
        self.name = tk.StringVar(value=initialfile)
        self.name_entry = ttk.Entry(bottom, textvariable=self.name)
        self.name_entry.pack(side="left", fill="x", expand=True, padx=8)
        self.name_entry.bind("<Return>", lambda event: self.accept() or "break")
        ttk.Button(bottom, text="Cancel", command=self.cancel).pack(side="right")
        ttk.Button(bottom, text="Save" if save else "Open",
                   command=self.accept).pack(side="right", padx=(0, 6))
        self.tree.bind("<<TreeviewSelect>>", self.selection_changed)
        self.populate()
        self.deiconify()
        self.grab_set()
        self.tree.focus_set()

    def populate(self):
        self.location.set(str(self.folder))
        self.tree.delete(*self.tree.get_children())
        try:
            entries = directory_entries(self.folder)
        except OSError as exc:
            messagebox.showerror("Cannot list directory", str(exc), parent=self)
            entries = []
        self.paths = {}
        for index, path in enumerate(entries):
            try:
                is_dir = path.is_dir()
                size = "" if is_dir else str(path.stat().st_size)
            except OSError:
                continue
            item = str(index)
            self.paths[item] = path
            self.tree.insert("", "end", iid=item, text=path.name,
                             values=(size, "Folder" if is_dir else "File"))
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.focus(children[0])
            self.tree.see(children[0])

    def on_wheel(self, event):
        items = self.tree.get_children()
        if not items:
            return "break"
        selected = self.tree.selection()
        current = selected[0] if selected else items[0]
        step = wheel_steps(event)
        if step:
            index = max(0, min(len(items) - 1, items.index(current) + step))
            target = items[index]
            self.tree.selection_set(target)
            self.tree.focus(target)
            self.tree.see(target)
        return "break"

    def selection_changed(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        path = self.paths.get(selected[0])
        if path is not None:
            self.name.set(path.name if path.is_file() else "")

    def go_up(self):
        if self.folder.parent != self.folder:
            self.folder = self.folder.parent
            self.name.set("")
            self.populate()

    def activate(self, event=None):
        selected = self.tree.selection()
        if selected:
            path = self.paths.get(selected[0])
            if path is not None and path.is_dir():
                self.folder = path
                self.name.set("")
                self.populate()
                return "break"
        self.accept()
        return "break"

    def accept(self):
        name = self.name.get().strip()
        if not name:
            selected = self.tree.selection()
            path = self.paths.get(selected[0]) if selected else None
        else:
            path = Path(name).expanduser()
            if not path.is_absolute():
                path = self.folder / path
        if path is None:
            return
        try:
            path = path.resolve()
            if path.is_dir():
                self.folder = path
                self.name.set("")
                self.populate()
                return
            if not self.save_mode and not path.is_file():
                messagebox.showwarning("File not found", str(path), parent=self)
                return
            if self.save_mode and path.exists():
                if not messagebox.askyesno("Overwrite file?",
                        f"{path.name} already exists. Choose this filename?",
                        parent=self):
                    return
        except OSError as exc:
            messagebox.showerror("File error", str(exc), parent=self)
            return
        self.result = str(path)
        self.cancel()

    def cancel(self):
        self.grab_release()
        self.destroy()


def choose_file(parent, initialdir, *, save=False, initialfile=""):
    dialog = FileChooser(parent, initialdir, save=save, initialfile=initialfile)
    parent.wait_window(dialog)
    return dialog.result
