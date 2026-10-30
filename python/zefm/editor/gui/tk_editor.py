"""Tkinter/ttk desktop adapter for the ZEFM editor.

Run: python3 -m zefm.editor.gui.tk_editor
Each tab has a TPEditor controller and a Tk Text widget. Tk's undo manager
handles typed input; controller handles the three explicit clipboard commands.
"""
import sys
import re
import webbrowser
from queue import Queue, Empty
from urllib.parse import urlencode
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font as tkfont
from ..model import Buffer
from ...config import load as load_config
from ..working_directory import WorkingDirectory
from ..external_changes import disk_signature, changed_on_disk, ExternalChangeDismissals
from ..recent_files import RecentFiles
from ..font_settings import read_font, write_font
from ..language_tools import LANGUAGES, language_dictionary, expand_suffix
from ..legacy_keymaps import read_keymap,translation
from ..keymap_view import mapping_rows, mapping_text
from ...storage.lexicons import default_lexicon_dir, lookup_lexicon
from ...storage.word_notes import WordNotes, word_at
from ..tp_editor import TPEditor
from ..shortcut_config import load_menus
from ..modes import ModeRegistry
from ..json_path import paths_at, navigate, locate_path, jq_path
from ..json_tools import parse_simple_path, value_at_path, format_json
from ..mode_tools import validate_json, indentation
from .tk_clipboard import TkClipboard
from .keyboard_policy import install_editor_shortcut

class Window:
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("ZEFM Python editor (preview)")
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)
        self.font_settings_path=Path.home()/".config"/"zefm"/"font.json"
        font_options=read_font(self.font_settings_path)
        # Prefer a native-looking monospace font on macOS, but preserve saved preferences.
        if sys.platform=="darwin" and not self.font_settings_path.exists():
            font_options["family"]="Menlo"
        self.editor_font=tkfont.Font(root=self.root,**font_options)
        self.views = {}
        self.saved_messages = {}
        self.disk_signatures = {}
        self.external_dismissals = ExternalChangeDismissals()
        settings=load_config(Path(__file__).resolve().parents[3] / "config/zefm.json")
        self.working_directory=WorkingDirectory(settings["home_directory"],settings["remember_last_directory"],
            state_path=Path.home()/".config"/"zefm"/"session.json")
        self.mode_registry = ModeRegistry.load(Path(__file__).resolve().parents[3] / "config/modes.json")
        self.buffer_modes = {}
        self.buffer_languages = {}
        self.buffer_keymaps = {}
        self.keymap_dir=Path(__file__).resolve().parents[3] / "legacy_keymaps"
        self.available_keymaps={p.stem:p for p in self.keymap_dir.glob("*.keymap")}
        self._keymap_cache={}
        self.dictionary_dir=Path(__file__).resolve().parents[3] / "dictionaries"
        self.word_notes = None  # Initialized when first used; storage errors are displayed.
        self.local_browser = None  # Start only on explicit File menu request.
        self.mail_browser = None  # Separately scoped local Maildir reader.
        self.browser_open_requests = Queue()
        self.browser_poll_id = None
        self.recent_files = RecentFiles()
        self.recent_menu = None
        self.search_term = ""
        self.vim_normal = False
        self.vim_direction = 1
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status, anchor="w").pack(side="bottom", fill="x")
        # A nonmodal warning above the status line; it never replaces user edits.
        self.external_notice_text = tk.StringVar()
        self.external_notice = ttk.Frame(self.root, padding=(6, 4))
        ttk.Label(self.external_notice, textvariable=self.external_notice_text, wraplength=500).pack(
            side="left", fill="x", expand=True)
        self.external_reload = ttk.Button(
            self.external_notice, text="Reload from disk...", command=self._reload_external)
        self.external_reload.pack(side="right", padx=4)
        ttk.Button(self.external_notice, text="Dismiss this change",
                   command=self._dismiss_external).pack(side="right", padx=4)
        self.noticed_signature = None
        self.disk_poll_id = None
        self.command_bar = ttk.Frame(self.root)
        self.command_label = ttk.Label(self.command_bar, text="/")
        self.command_label.pack(side="left")
        self.command_value = tk.StringVar()
        self.command_entry = ttk.Entry(self.command_bar, textvariable=self.command_value)
        self.command_entry.pack(side="left", fill="x", expand=True)
        self.command_entry.bind("<Return>", self._vim_submit)
        self.command_entry.bind("<Escape>", self._vim_cancel)
        self.clipboard = TkClipboard(self.root)
        self.menus = load_menus(Path(__file__).resolve().parents[3] / "config/keyboard.json")
        from ..command_registry import Command
        self.menus = {group:[Command("Debug Python" if item.label=="Trace" else item.label,item.shortcut)
                              for item in items] for group,items in self.menus.items()}
        self._make_menus()
        self.new_buffer()
        self.tabs.bind("<<NotebookTabChanged>>", self._tab_changed)
        self.disk_poll_id = self.root.after(3000, self._disk_monitor_tick)
        self.root.geometry("920x680")

    def new_buffer(self, path=None, text=""):
        frame=ttk.Frame(self.tabs)
        widget=tk.Text(frame, wrap="none", undo=True, maxundo=-1, font=self.editor_font)
        y=ttk.Scrollbar(frame, orient="vertical", command=widget.yview)
        x=ttk.Scrollbar(frame, orient="horizontal", command=widget.xview)
        widget.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        y.pack(side="right",fill="y"); x.pack(side="bottom",fill="x")
        widget.pack(fill="both",expand=True)
        widget.insert("1.0",text);widget.edit_reset();widget.edit_modified(False)
        editor=TPEditor(self.clipboard,Buffer(text,path))
        self.views[str(frame)] = (widget,editor)
        self.saved_messages[str(frame)] = None
        self.disk_signatures[str(frame)] = disk_signature(path) if path else None
        self.external_dismissals.reset(str(frame))
        self.buffer_modes[str(frame)] = self.mode_registry.detect(path,text)
        self.buffer_languages[str(frame)] = "system"
        self.buffer_keymaps[str(frame)] = None
        self.tabs.add(frame,text=path.rsplit("/",1)[-1] if path else "Untitled")
        self.tabs.select(frame);widget.focus_set()
        widget.bind("<<Modified>>",lambda event,w=widget,e=editor:self._changed(w,e))
        widget.bind("<KeyRelease>", lambda event,w=widget:self._status(w))
        widget.bind("<KeyPress>", self._vim_key)
        widget.bind("<Tab>", self._mode_tab)
        widget.bind("<ButtonRelease-1>", lambda event,w=widget:self._status(w))
        self._status(widget)
        return widget

    def current(self):
        key=self.tabs.select()
        return self.views[key] if key else (None,None)

    def _status(self, widget):
        if widget is self.current()[0]:
            line,col=widget.index("insert").split(".")
            mode=self.buffer_modes.get(self.tabs.select())
            label=f"Line {line}, column {int(col)+1}  [{mode.name if mode else 'text'}]"
            if mode and mode.name=='json':
                path=paths_at(widget.get('1.0','end-1c'),len(widget.get('1.0','insert')))
                if path is not None:label+=f"  jq: {path}"
            label += "  |  Lang: " + LANGUAGES[self.buffer_languages.get(self.tabs.select(), "system")]
            active_keymap=self.buffer_keymaps.get(self.tabs.select())
            label += "  |  Keys: " + (active_keymap + " (Alt)" if active_keymap else "System")
            label += "  |  NORMAL (Esc to edit)" if self.vim_normal else "  |  INSERT (Esc for commands)"
            saved=self.saved_messages.get(self.tabs.select())
            if saved and not self.current()[1].state.buffer.modified:
                label += f"  |  {saved}"
            self.status.set(label)

    def _hide_external_notice(self):
        if self.external_notice.winfo_manager():
            self.external_notice.pack_forget()

    def _check_external_changes(self):
        """Check the active buffer periodically, without changing its text."""
        tab = self.tabs.select()
        if not tab or tab not in self.views:
            self._hide_external_notice()
            return
        _widget, editor = self.views[tab]
        path = editor.state.buffer.path
        if not path:
            self._hide_external_notice()
            return
        try:
            current = disk_signature(path)
        except OSError as exc:
            self.external_notice_text.set(f"Cannot check {Path(path).name}: {exc}")
            self.external_reload.configure(state="disabled")
            if not self.external_notice.winfo_manager():
                self.external_notice.pack(side="bottom", fill="x")
            return
        baseline = self.disk_signatures.get(tab)
        if not self.external_dismissals.pending(tab, baseline, current):
            self._hide_external_notice()
            return
        self.noticed_signature = current
        if current is None:
            message = f"{Path(path).name} was removed from disk. Your editor buffer is unchanged."
        else:
            message = f"{Path(path).name} changed on disk. Reload or keep your current buffer."
        self.external_notice_text.set(message)
        self.external_reload.configure(state="normal" if current is not None else "disabled")
        if not self.external_notice.winfo_manager():
            self.external_notice.pack(side="bottom", fill="x")

    def _tab_changed(self, event=None):
        widget, _editor = self.current()
        if widget is not None:
            self._status(widget)
        self._check_external_changes()

    def _disk_monitor_tick(self):
        self.disk_poll_id = None
        self._check_external_changes()
        self.disk_poll_id = self.root.after(3000, self._disk_monitor_tick)

    def _dismiss_external(self):
        tab = self.tabs.select()
        if tab:
            self.external_dismissals.dismiss(tab, self.noticed_signature)
        self._check_external_changes()

    def _reload_external(self):
        """Revert with the existing unsaved-edits confirmation."""
        self.revert_file()
        self._check_external_changes()

    def _changed(self, widget, editor):
        if widget.edit_modified():
            for tab, (w, _e) in self.views.items():
                if w is widget and (
                        self.buffer_languages.get(tab) == "yi" or
                        self.buffer_keymaps.get(tab) == "Yiddish"):
                    self._apply_rtl_alignment(tab)
                    break
            editor.state.buffer.text=widget.get("1.0","end-1c")
            editor.state.buffer.modified=True
            for tab,(w,e) in self.views.items():
                if w is widget:
                    self.saved_messages[tab]=None
                    break
            widget.edit_modified(False)
            self._update_title(widget,editor)
            self._status(widget)

    def _update_title(self,widget,editor):
        for tab,(w,e) in self.views.items():
            if w is widget:
                name=Path(editor.state.buffer.path).name if editor.state.buffer.path else "Untitled"
                self.tabs.tab(tab,text=("* " if editor.state.buffer.modified else "")+name)
                break

    def _mode_tab(self,event):
        if self.vim_normal:return "break"
        widget=event.widget
        if widget is not self.current()[0]:return
        if widget.tag_ranges("sel"):return
        widget.insert("insert",indentation(self.buffer_modes[self.tabs.select()]))
        return "break"

    def _json_path(self):
        widget,_=self.current()
        if not widget or self.buffer_modes[self.tabs.select()].name!="json":
            self.status.set("JSON path requires a JSON buffer");return None
        text=widget.get("1.0","end-1c")
        offset=len(widget.get("1.0","insert"))
        path=paths_at(text,offset)
        if path is None:self.status.set("No path (check JSON validity/cursor position)")
        else:self.status.set(f"jq path: {path}")
        return path

    def navigate_json(self,direction):
        widget,_=self.current()
        if not widget or self.buffer_modes[self.tabs.select()].name!='json':
            self.status.set('JSON navigation requires JSON mode');return
        text=widget.get('1.0','end-1c')
        result=navigate(text,len(widget.get('1.0','insert')),direction)
        if result is None:
            self.status.set('No destination (boundary or invalid JSON)');return
        offset,path=result
        widget.mark_set('insert',f'1.0 + {offset} chars')
        widget.see('insert');widget.focus_set();self._status(widget)

    def jump_json_path(self):
        widget,_=self.current()
        if not widget or self.buffer_modes[self.tabs.select()].name!='json':
            self.status.set('Jump to JSON path requires JSON mode');return
        expression=simpledialog.askstring('Jump to JSON Path','Simple jq path:',
                            initialvalue=self._json_path() or '.',parent=self.root)
        if expression is None:return
        try:
            parts=parse_simple_path(expression)
            offset=locate_path(widget.get('1.0','end-1c'),parts)
        except ValueError as exc:
            messagebox.showerror('JSON path',str(exc),parent=self.root);return
        if offset is None:
            self.status.set('JSON path not found or buffer invalid');return
        widget.mark_set('insert',f'1.0 + {offset} chars')
        widget.see('insert');widget.focus_set();self._status(widget)

    def copy_json_path(self):
        path=self._json_path()
        if path is not None:
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            self.status.set(f"Copied jq path: {path}")

    def validate_buffer(self):
        widget,_=self.current()
        if not widget:return
        if self.buffer_modes[self.tabs.select()].name!="json":
            self.status.set("Validation currently supports JSON mode");return
        _,diagnostic=validate_json(widget.get("1.0","end-1c"))
        self.status.set(diagnostic)

    def json_value_at_path(self):
        widget,_=self.current()
        if not widget or self.buffer_modes[self.tabs.select()].name!="json":return
        expression=simpledialog.askstring("JSON value","Simple path:",
                            initialvalue=self._json_path() or ".",parent=self.root)
        if expression is None:return
        try:
            value=value_at_path(widget.get("1.0","end-1c"),parse_simple_path(expression))
            import json
            output=json.dumps(value,ensure_ascii=False,indent=2)
        except (ValueError,KeyError,IndexError,TypeError) as exc:
            messagebox.showerror("JSON path",str(exc),parent=self.root);return
        self.new_buffer(text=output+"\\n")

    def format_json_buffer(self):
        widget,_=self.current()
        if not widget or self.buffer_modes[self.tabs.select()].name!="json":return
        try:formatted=format_json(widget.get("1.0","end-1c"))
        except ValueError as exc:
            messagebox.showerror("JSON",str(exc),parent=self.root);return
        widget.delete("1.0","end");widget.insert("1.0",formatted)

    def debug_python(self):
        """Launch pdb in a terminal for a saved Python file; never run via shell."""
        import subprocess,shutil
        widget,editor=self.current()
        if not widget:return
        if self.buffer_modes[self.tabs.select()].name!="python":
            self.status.set("Debug Python requires Python mode");return
        path=editor.state.buffer.path
        if not path or editor.state.buffer.modified:
            messagebox.showinfo("Debug Python","Save the Python buffer before debugging.",parent=self.root)
            return
        terminal=shutil.which("xterm")
        if not terminal:
            messagebox.showerror("Debug Python","Install xterm for interactive pdb (apk add xterm).",parent=self.root)
            return
        try:subprocess.Popen([terminal,"-e",sys.executable,"-m","pdb",path],
                             cwd=str(Path(path).resolve().parent))
        except OSError as exc:messagebox.showerror("Debug Python",str(exc),parent=self.root)

    def run_jq(self):
        """Execute jq on the unsaved buffer, never through a shell."""
        import subprocess
        widget,_=self.current()
        if not widget or self.buffer_modes[self.tabs.select()].name!="json":
            self.status.set("jq requires JSON mode");return
        source=widget.get("1.0","end-1c")
        valid,diagnostic=validate_json(source)
        if not valid:self.status.set(diagnostic);return
        expression=simpledialog.askstring("jq", "Filter (current unsaved buffer):",
            initialvalue=self._json_path() or ".",parent=self.root)
        if expression is None:return
        try:
            result=subprocess.run(["jq",expression],input=source,text=True,
                                  capture_output=True,timeout=10,check=False)
        except (OSError,subprocess.TimeoutExpired) as exc:
            messagebox.showerror("jq",str(exc),parent=self.root);return
        if result.returncode:
            messagebox.showerror("jq",result.stderr[:3000],parent=self.root);return
        self.new_buffer(text=result.stdout)
        self.status.set("jq output opened in new buffer (source unchanged)")

    def select_buffer_mode(self):
        widget,_=self.current()
        if not widget:return
        current=self.buffer_modes[self.tabs.select()].name
        choice=simpledialog.askstring('Buffer Mode',
            'Choose mode ('+', '.join(sorted(self.mode_registry.modes))+'):',
            initialvalue=current,parent=self.root)
        if choice is None:return
        try:mode=self.mode_registry.detect(override=choice.strip())
        except ValueError as exc:
            messagebox.showerror('Buffer Mode',str(exc),parent=self.root);return
        self.buffer_modes[self.tabs.select()]=mode
        self._status(widget)

    def _sync_selection(self, widget, editor):
        state=editor.state
        state.buffer.text=widget.get("1.0","end-1c")
        state.point=len(widget.get("1.0","insert"))
        state.mark=None
        try:
            a=widget.index("sel.first");b=widget.index("sel.last")
            start=len(widget.get("1.0",a));end=len(widget.get("1.0",b))
            state.mark=end if state.point==start else start
            if state.point not in (start,end): state.point=end
        except tk.TclError: pass

    def action(self, name):
        widget,editor=self.current()
        if not widget:return
        if name in ("Copy","Cut","Paste"):
            # Native Text operations preserve Tk's undo history, selection,
            # OS clipboard and text tags; do not reconstruct the whole buffer.
            event = {"Copy":"<<Copy>>","Cut":"<<Cut>>","Paste":"<<Paste>>"}[name]
            widget.event_generate(event)
            widget.focus_set()
        elif name=="Undo":
            try:widget.edit_undo()
            except tk.TclError:pass
        elif name=="Redo":
            try:widget.edit_redo()
            except tk.TclError:pass
        elif name=="Find":self.find_text()
        elif name=="Replace":self.query_replace()
        elif name=="Continue Find or Replace":self.find_next()
        elif name=="Open":self.open_file()
        elif name=="Save":self.save_file()
        elif name=="Save As":self.save_file(as_new=True)
        elif name=="Quit":self.quit()
        elif name=="Debug Python":self.debug_python()
        elif name=="Revert File":self.revert_file()
        elif name=="Clear":
            if messagebox.askyesno("Clear buffer","Delete all text in this buffer?",parent=self.root):
                widget.delete("1.0","end")
        else:messagebox.showinfo("Not yet ported",name,parent=self.root)

    def describe_unicode_at_cursor(self):
        from ..unicode_tools import character_description
        widget,_=self.current()
        if widget is None:return
        try:
            start=widget.index('sel.first')
            character=widget.get(start,f'{start} + 1 chars')
        except tk.TclError:
            character=widget.get('insert','insert + 1 chars')
        if not character:
            self.status.set('No Unicode character at cursor')
            return
        self.status.set(character_description(character))

    def describe_unicode_sequence_at_cursor(self):
        from ..unicode_tools import character_context_description
        widget,_=self.current()
        if widget is None:return
        content=widget.get('1.0','end-1c')
        try:position=len(widget.get('1.0','sel.first'))
        except tk.TclError:position=len(widget.get('1.0','insert'))
        if position>=len(content):
            self.status.set('No Unicode character at cursor');return
        try:sequence,descriptions=character_context_description(content,position)
        except ValueError as exc:
            self.status.set(str(exc));return
        messagebox.showinfo('Unicode character sequence',
            f'Sequence: {sequence}\n\n'+ '\n'.join(descriptions),parent=self.root)

    def insert_unicode_codepoint(self):
        from ..unicode_tools import parse_codepoint
        answer=simpledialog.askstring("Unicode", "Code point (e.g. U+05D0, 03BB):",parent=self.root)
        if answer is None:return
        try:char=parse_codepoint(answer)
        except ValueError as exc:
            messagebox.showerror("Invalid Unicode character",str(exc),parent=self.root);return
        widget,_=self.current()
        if widget:
            widget.insert("insert",char)
            widget.focus_set()

    def browse_unicode_range(self, initial=None):
        from ..unicode_tools import unicode_range
        answer=initial if initial is not None else simpledialog.askstring("Unicode range", "Hex start and end (e.g. 0590-05FF):",parent=self.root)
        if answer is None:return
        try:
            points=unicode_range(answer)
        except ValueError as exc:
            messagebox.showerror("Invalid range",str(exc),parent=self.root);return
        dialog=tk.Toplevel(self.root);dialog.title("Unicode characters")
        frame=ttk.Frame(dialog);frame.pack(fill="both",expand=True)
        listing=tk.Listbox(frame,width=56,height=22,font=self.editor_font)
        scroll=ttk.Scrollbar(frame,command=listing.yview)
        listing.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right",fill="y");listing.pack(side="left",fill="both",expand=True)
        for cp,name in points:listing.insert("end",f"U+{cp:04X}  {chr(cp)}  {name}")
        def insert_selected(event=None):
            selection=listing.curselection()
            if not selection:return
            cp=points[selection[0]][0]
            widget,_=self.current()
            if widget:widget.insert("insert",chr(cp));widget.focus_set()
        listing.bind("<Double-Button-1>",insert_selected)
        listing.bind("<Return>",insert_selected)
        ttk.Button(dialog,text="Insert selected",command=insert_selected).pack(pady=4)

    def search_unicode_characters(self):
        from ..unicode_tools import search_unicode_names
        answer=simpledialog.askstring("Unicode name search",
            "Search Unicode names (e.g. HEBREW LETTER, GREEK SMALL LAMBDA):",
            parent=self.root)
        if answer is None:return
        try:points=search_unicode_names(answer)
        except ValueError as exc:
            messagebox.showerror("Invalid search",str(exc),parent=self.root);return
        dialog=tk.Toplevel(self.root);dialog.title("Unicode name search")
        ttk.Label(dialog,text=f"{len(points)} matching characters (first 200 maximum)").pack()
        frame=ttk.Frame(dialog);frame.pack(fill="both",expand=True)
        listing=tk.Listbox(frame,width=65,height=22,font=self.editor_font,exportselection=False)
        scroll=ttk.Scrollbar(frame,command=listing.yview)
        listing.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right",fill="y");listing.pack(side="left",fill="both",expand=True)
        for cp,name in points:listing.insert("end",f"U+{cp:04X}  {chr(cp)}  {name}")
        def insert_selected(event=None):
            selection=listing.curselection()
            if not selection:return
            widget,_=self.current()
            if widget:
                widget.insert("insert",chr(points[selection[0]][0]))
                widget.focus_set()
        listing.bind("<Double-Button-1>",insert_selected)
        listing.bind("<Return>",insert_selected)
        ttk.Button(dialog,text="Insert selected",command=insert_selected).pack(pady=4)

    def unicode_quick_characters(self):
        """Convenient recurring mathematical and typographic characters."""
        symbols=[("Greek", "αβγδεθλμπσφωΓΔΠΣΩ"),
                 ("Math", "±×÷≤≥≠≈∞∑∏∫√∂∇∈∉⊂⊆∪∩→↔⇒"),
                 ("Typography", "–—…‘’“”«»°§¶•")]
        dialog=tk.Toplevel(self.root);dialog.title("Insert common Unicode symbols")
        for title,chars in symbols:
            frame=ttk.LabelFrame(dialog,text=title);frame.pack(fill="x",padx=8,pady=5)
            for i,char in enumerate(chars):
                ttk.Button(frame,text=char,width=3,
                    command=lambda c=char:self._insert_unicode_symbol(c)).grid(row=i//12,column=i%12,padx=1,pady=2)

    def _insert_unicode_symbol(self, char):
        widget,_=self.current()
        if widget:
            widget.insert("insert",char)
            widget.focus_set()

    def _save_font_preferences(self):
        settings={key:self.editor_font.actual(key) for key in ("family","size","weight","slant")}
        settings["size"]=abs(int(settings["size"]))
        try:
            write_font(self.font_settings_path,settings)
        except OSError as exc:
            self.status.set(f"Font preference not saved: {exc}")

    def _set_font_style(self, **style):
        self.editor_font.configure(**style)
        self._save_font_preferences()

    def choose_font_family(self):
        """Filter installed fonts and preview scripts before applying."""
        available=sorted(set(tkfont.families(root=self.root)),key=str.casefold)
        dialog=tk.Toplevel(self.root);dialog.title("Editor font chooser")
        dialog.geometry("720x540")
        dialog.transient(self.root)
        filter_text=tk.StringVar()
        row=ttk.Frame(dialog);row.pack(fill="x",padx=8,pady=8)
        ttk.Label(row,text="Filter fonts:").pack(side="left")
        entry=ttk.Entry(row,textvariable=filter_text)
        entry.pack(side="left",fill="x",expand=True,padx=8)
        listing=tk.Listbox(dialog,height=12,exportselection=False)
        listing.pack(fill="both",expand=True,padx=8)
        current=self.editor_font.actual("family")
        preview_font=tkfont.Font(root=self.root,family=current,
            size=abs(self.editor_font.actual("size")),
            weight=self.editor_font.actual("weight"),slant=self.editor_font.actual("slant"))
        preview_options=ttk.Frame(dialog)
        preview_options.pack(fill="x",padx=8)
        ttk.Label(preview_options,text="Size:").pack(side="left")
        size_value=tk.IntVar(value=abs(self.editor_font.actual("size")))
        ttk.Spinbox(preview_options,from_=6,to=72,width=5,textvariable=size_value).pack(side="left",padx=(4,12))
        bold_value=tk.BooleanVar(value=self.editor_font.actual("weight")=="bold")
        italic_value=tk.BooleanVar(value=self.editor_font.actual("slant")=="italic")
        ttk.Checkbutton(preview_options,text="Bold",variable=bold_value).pack(side="left",padx=5)
        ttk.Checkbutton(preview_options,text="Italic",variable=italic_value).pack(side="left",padx=5)
        preview=tk.Text(dialog,height=6,wrap="word",font=preview_font)
        preview.pack(fill="x",padx=8,pady=8)
        preview.insert("1.0","Latin: café cœur naïve\nGreek: α β γ λ π Ω\nMath: ∑ ∫ ∞ √ ≠ ≤ ≥\nHebrew / Yiddish: שלום ייִדיש אַ בֿ אָ פֿ ײַ")
        preview.configure(state="disabled")
        shown=[]
        def refresh(*_):
            shown[:]=[family for family in available if filter_text.get().casefold() in family.casefold()]
            listing.delete(0,"end")
            for family in shown:listing.insert("end",family)
            if shown:
                index=shown.index(current) if current in shown else 0
                listing.selection_set(index);listing.see(index)
                preview_font.configure(family=shown[index])
        def selected(event=None):
            indices=listing.curselection()
            if indices:preview_font.configure(family=shown[indices[0]])
        def preview_style(*_):
            try:
                point_size=int(size_value.get())
                if not 6 <= point_size <= 72:return
                preview_font.configure(size=point_size,
                    weight="bold" if bold_value.get() else "normal",
                    slant="italic" if italic_value.get() else "roman")
            except (ValueError,tk.TclError):
                return
        size_value.trace_add("write",preview_style)
        bold_value.trace_add("write",preview_style)
        italic_value.trace_add("write",preview_style)
        def apply(event=None):
            indices=listing.curselection()
            if indices:
                try:
                    point_size=int(size_value.get())
                    if not 6 <= point_size <= 72:raise ValueError()
                except (ValueError,tk.TclError):
                    messagebox.showerror("Font size","Choose a font size from 6 to 72.",parent=dialog)
                    return
                self._set_font_style(family=shown[indices[0]],size=point_size,
                    weight="bold" if bold_value.get() else "normal",
                    slant="italic" if italic_value.get() else "roman")
                dialog.destroy()
        listing.bind("<<ListboxSelect>>",selected)
        listing.bind("<Double-Button-1>",apply)
        filter_text.trace_add("write",refresh)
        controls=ttk.Frame(dialog);controls.pack(fill="x",padx=8,pady=8)
        ttk.Button(controls,text="Apply font",command=apply).pack(side="right")
        ttk.Button(controls,text="Cancel",command=dialog.destroy).pack(side="right",padx=8)
        refresh();entry.focus_set()

    def choose_font_size(self):
        size=simpledialog.askinteger("Editor font size","Size in points:",parent=self.root,
            initialvalue=abs(self.editor_font.actual("size")),minvalue=6,maxvalue=72)
        if size is not None:self._set_font_style(size=size)

    def _apply_rtl_alignment(self, tab):
        """Align Yiddish paragraphs on the right without altering stored text.

        Tk 8.6/X11 does NOT implement full Unicode BiDi editing. For correct
        mixed-script ordering and cursor movement use the RTL browser editor.
        """
        if tab not in self.views:
            return
        widget, _editor = self.views[tab]
        tag = "zefm-rtl-alignment"
        widget.tag_configure(tag, justify="right")
        if self.buffer_languages.get(tab) == "yi" or self.buffer_keymaps.get(tab) == "Yiddish":
            widget.tag_add(tag, "1.0", "end")
        else:
            widget.tag_remove(tag, "1.0", "end")

    def choose_language(self, language):
        if language not in LANGUAGES:return
        tab=self.tabs.select()
        if not tab:return
        self.buffer_languages[tab]=language
        self._apply_rtl_alignment(tab)
        widget,_=self.current()
        if widget:self._status(widget)

    def choose_keymap(self,name):
        tab=self.tabs.select()
        if not tab:return
        if name is not None and name not in self.available_keymaps:return
        self.buffer_keymaps[tab]=name
        self._apply_rtl_alignment(tab)
        widget,_=self.current()
        if widget:widget.focus_set();self._status(widget)

    def _keymap_input(self,event):
        if self.vim_normal:return None
        name=self.buffer_keymaps.get(self.tabs.select())
        if not name:return None
        # Tk X11 Alt/Mod1 is bit 0x8; Control bit 0x4 is left to commands.
        # On macOS, Option may produce a compose sequence; custom mappings
        # are opt-in and only consume actual Alt/Option modified key events.
        if not (event.state & 0x0008) or (event.state & 0x0004):return None
        if name not in self._keymap_cache:
            try:self._keymap_cache[name]=read_keymap(self.available_keymaps[name])
            except (OSError,ValueError) as exc:
                self.status.set(f"Keymap error: {exc}");return None
        char=translation(self._keymap_cache[name],event.keysym,
                         shift=bool(event.state & 0x0001),alt=True)
        if char is None:return None
        event.widget.insert('insert',char)
        return 'break'

    def show_keymap(self):
        """Display and optionally activate/insert from the original Alt keymaps."""
        names=sorted(name for name in self.available_keymaps if name!='English')
        if not names:
            messagebox.showinfo("Keymaps","No keymap files were found.",parent=self.root)
            return
        dialog=tk.Toplevel(self.root)
        dialog.title("ZEFM keymap reference")
        dialog.geometry("790x530")
        dialog.transient(self.root)
        top=ttk.Frame(dialog);top.pack(fill='x',padx=8,pady=8)
        ttk.Label(top,text="Layout:").pack(side='left')
        active=self.buffer_keymaps.get(self.tabs.select())
        chosen=tk.StringVar(value=active if active in names else ('Yiddish' if 'Yiddish' in names else names[0]))
        selector=ttk.Combobox(top,state='readonly',textvariable=chosen,values=names,width=20)
        selector.pack(side='left',padx=6)
        filter_value=tk.StringVar()
        ttk.Label(top,text="Find:").pack(side='left',padx=(16,4))
        search=ttk.Entry(top,textvariable=filter_value)
        search.pack(side='left',fill='x',expand=True)
        ttk.Label(dialog,text="Key combination     Output      Unicode name(s).  Double-click to insert.",
                  anchor='w').pack(fill='x',padx=8)
        frame=ttk.Frame(dialog);frame.pack(fill='both',expand=True,padx=8,pady=5)
        listing=tk.Listbox(frame,font=self.editor_font,exportselection=False)
        scroll=ttk.Scrollbar(frame,command=listing.yview)
        listing.configure(yscrollcommand=scroll.set)
        listing.pack(side='left',fill='both',expand=True)
        scroll.pack(side='right',fill='y')
        shown=[]
        def get_mapping():
            name=chosen.get()
            if name not in self._keymap_cache:
                self._keymap_cache[name]=read_keymap(self.available_keymaps[name])
            return self._keymap_cache[name]
        def refresh(*unused):
            nonlocal shown
            try:rows=mapping_rows(get_mapping())
            except (OSError,ValueError) as exc:
                messagebox.showerror('Keymaps',str(exc),parent=dialog);return
            term=filter_value.get().casefold().strip()
            shown=[row for row in rows if term in ' '.join(row).casefold()]
            listing.delete(0,'end')
            for chord,chars,description in shown:
                listing.insert('end',f'{chord:17} {chars:8} {description}')
        def insert_selected(event=None):
            selected=listing.curselection()
            if not selected:return
            widget,_=self.current()
            if widget:
                widget.insert('insert',shown[selected[0]][1]);widget.focus_set()
        def copy_reference():
            try:data=mapping_text(get_mapping(),chosen.get())
            except (OSError,ValueError) as exc:
                messagebox.showerror('Keymaps',str(exc),parent=dialog);return
            dialog.clipboard_clear();dialog.clipboard_append(data)
            self.status.set(f'Copied {chosen.get()} keymap to clipboard')
        def activate():
            self.choose_keymap(chosen.get());dialog.destroy()
        selector.bind('<<ComboboxSelected>>',refresh)
        filter_value.trace_add('write',refresh)
        listing.bind('<Double-Button-1>',insert_selected)
        listing.bind('<Return>',insert_selected)
        controls=ttk.Frame(dialog);controls.pack(fill='x',padx=8,pady=8)
        ttk.Button(controls,text='Use this keymap',command=activate).pack(side='left')
        ttk.Button(controls,text='Insert selected',command=insert_selected).pack(side='left',padx=5)
        ttk.Button(controls,text='Copy reference',command=copy_reference).pack(side='left')
        ttk.Button(controls,text='Close',command=dialog.destroy).pack(side='right')
        refresh()
        search.focus_set()

    def lookup_lexical_word(self):
        """Look up a selected/nearby word in the migrated legacy dictionary."""
        tab=self.tabs.select()
        if not tab:return
        language=self.buffer_languages.get(tab,'system')
        if language == 'system':
            self.status.set('Select French or Yiddish under Language to look up a word')
            return
        widget,_=self.current()
        content=widget.get('1.0','end-1c')
        from ...storage.word_notes import word_at
        try:
            selected=(len(widget.get('1.0','sel.first')),
                      len(widget.get('1.0','sel.last')))
        except tk.TclError:selected=None
        term=word_at(content,len(widget.get('1.0','insert')),selection=selected)
        if not term:
            self.status.set('Select a word or position the cursor within one')
            return
        try:definitions=lookup_lexicon(default_lexicon_dir(),language,term)
        except (OSError,UnicodeError,ValueError) as exc:
            messagebox.showerror('Dictionary',str(exc),parent=self.root)
            return
        dialog=tk.Toplevel(self.root);dialog.title(f'{LANGUAGES[language]}: {term}')
        dialog.geometry('610x320')
        ttk.Label(dialog,text=f'{LANGUAGES[language]} dictionary — {term}',
                  font=self.editor_font).pack(anchor='w',padx=10,pady=9)
        display=tk.Text(dialog,wrap='word',font=self.editor_font,height=12)
        display.pack(fill='both',expand=True,padx=10,pady=4)
        if definitions:
            display.insert('1.0','\n\n'.join(definitions))
        else:
            display.insert('1.0','No entry found. To migrate your original dictionary,\n'
                          'use python3 -m zefm.storage.import_legacy_dictionaries\n'
                          'on a validated JSONL export of the old SQL table.')
        display.configure(state='disabled')
        ttk.Button(dialog,text='Close',command=dialog.destroy).pack(pady=8)

    def expand_dictionary_shortcut(self):
        """Explicit expansion only; does not intercept typing or input methods."""
        tab=self.tabs.select()
        if not tab:return
        language=self.buffer_languages.get(tab,"system")
        widget,_=self.current()
        if language=="system":
            self.status.set("Select French or Yiddish under Language first")
            return
        try:
            entries=language_dictionary(self.dictionary_dir,language)
            content=widget.get("1.0","end-1c")
            cursor=len(widget.get("1.0","insert"))
            match=expand_suffix(content,cursor,entries)
        except (OSError,ValueError) as exc:
            messagebox.showerror("Dictionary",str(exc),parent=self.root)
            return
        if match is None:
            self.status.set("No dictionary shortcut immediately before cursor")
            return
        start,end,replacement=match
        widget.delete(f"1.0 + {start} chars",f"1.0 + {end} chars")
        widget.insert(f"1.0 + {start} chars",replacement)
        widget.focus_set()

    def _get_word_notes(self):
        # Always reload notes from disk: the browser may have edited them since
        # this editor last opened the Notes dialog.
        try:
            self.word_notes = WordNotes()
        except (OSError, ValueError) as exc:
            messagebox.showerror("Notes storage", str(exc), parent=self.root)
            return None
        return self.word_notes

    def _note_document(self):
        widget,editor=self.current()
        if widget is None:return None
        filename=editor.state.buffer.path
        if not filename:
            messagebox.showinfo("Notes","Save the file before attaching a note to a word.",parent=self.root)
            return None
        return str(Path(filename).expanduser().resolve())

    def annotate_word(self):
        """Edit a note for selected text or the Unicode word at the insertion point."""
        filename=self._note_document()
        if filename is None:return
        widget,_=self.current()
        text=widget.get("1.0","end-1c")
        position=len(widget.get("1.0","insert"))
        try:
            selection=(len(widget.get("1.0","sel.first")),
                       len(widget.get("1.0","sel.last")))
        except tk.TclError:
            selection=None
        word=word_at(text,position,selection=selection)
        if not word:
            messagebox.showinfo("Notes","Select a word or place the cursor inside one.",parent=self.root)
            return
        self._edit_word_note(filename,word)

    def _edit_word_note(self,filename,word):
        from html import escape
        store=self._get_word_notes()
        if store is None:return
        old=store.get(filename,word)
        dialog=tk.Toplevel(self.root)
        dialog.title(f"Note: {word[:48]}")
        dialog.transient(self.root)
        dialog.geometry("700x410")
        dialog.minsize(420,210)
        # Pack the Save toolbar FIRST so neither long filenames, words nor
        # large editor fonts can push it below the visible popup.
        buttons=ttk.Frame(dialog)
        buttons.pack(side="top",fill="x",padx=10,pady=(8,5))
        ttk.Label(dialog,text=f"File: {filename}",wraplength=660).pack(anchor="w",padx=10,pady=(2,2))
        ttk.Label(dialog,text=f"Word: {word}",wraplength=660).pack(anchor="w",padx=10,pady=(0,6))
        content=tk.Text(dialog,wrap="word",undo=True,font=self.editor_font,height=10)
        content.pack(side="top",fill="both",expand=True,padx=10,pady=(0,10))
        original=old["data"] if old else ""
        if original:content.insert("1.0",original)
        def current_text():
            return content.get("1.0","end-1c")
        def save(event=None):
            try:
                # Read the live store: a browser Notes change may have happened
                # while the dialog was open. Refuse to overwrite it silently.
                current_store=WordNotes(store.path)
                current_record=current_store.get(filename,word)
                if current_record != old:
                    messagebox.showerror("Save note failed",
                        "This note changed elsewhere. Reopen it before saving.",parent=dialog)
                    return "break"
                current_store.put(filename,word,current_text(),
                                  link=old["link"] if old else escape(word,quote=True))
            except (OSError,ValueError) as exc:
                messagebox.showerror("Save note failed",str(exc),parent=dialog)
                return "break"
            self.status.set(f"Saved note: {word} [{Path(filename).name}]")
            dialog.destroy()
            return "break"
        def delete():
            if not messagebox.askyesno("Delete note",f"Delete note for {word!r}?",parent=dialog):return
            try:
                current_store=WordNotes(store.path)
                if current_store.get(filename,word)!=old:
                    messagebox.showerror("Delete note failed",
                        "This note changed elsewhere. Reopen it before deleting.",parent=dialog)
                    return
                current_store.delete(filename,word)
            except (OSError,ValueError) as exc:
                messagebox.showerror("Delete note failed",str(exc),parent=dialog)
                return
            self.status.set(f"Deleted note: {word} [{Path(filename).name}]")
            dialog.destroy()
        def close():
            if current_text()!=original and not messagebox.askyesno(
                    "Discard note edits?","Close without saving this note?",parent=dialog):
                return
            dialog.destroy()
        ttk.Button(buttons,text="Save Note",command=save).pack(side="left",padx=4)
        ttk.Button(buttons,text="Delete Note",command=delete,
                   state="normal" if old else "disabled").pack(side="left",padx=4)
        ttk.Button(buttons,text="Close",command=close).pack(side="right",padx=4)
        dialog.bind("<Control-s>",save)
        dialog.bind("<Command-s>",save)
        dialog.protocol("WM_DELETE_WINDOW",close)
        content.focus_set()

    def list_word_notes(self):
        filename=self._note_document()
        if filename is None:return
        store=self._get_word_notes()
        if store is None:return
        records=store.for_file(filename)
        dialog=tk.Toplevel(self.root);dialog.title(f"Notes: {Path(filename).name}")
        dialog.transient(self.root)
        dialog.geometry("620x340")
        ttk.Label(dialog,text=f"{len(records)} notes for {filename}",wraplength=590).pack(anchor="w",padx=10,pady=8)
        listing=tk.Listbox(dialog,exportselection=False)
        listing.pack(fill="both",expand=True,padx=10,pady=5)
        for r in records:listing.insert("end",f"{r['word']}  —  {r['data'][:100].replace(chr(10),' ')}")
        def open_note(event=None):
            selection=listing.curselection()
            if not selection:return
            word=records[selection[0]]["word"]
            dialog.destroy()
            self._edit_word_note(filename,word)
        listing.bind("<Double-Button-1>",open_note)
        listing.bind("<Return>",open_note)
        buttons=ttk.Frame(dialog);buttons.pack(pady=5)
        ttk.Button(buttons,text="Open Note",command=open_note).pack(side="left",padx=4)
        ttk.Button(buttons,text="Close",command=dialog.destroy).pack(side="left",padx=4)

    def _make_menus(self):
        bar=tk.Menu(self.root)
        for group,items in self.menus.items():
            menu=tk.Menu(bar,tearoff=False)
            if group=="File":
                menu.add_command(label="New Buffer",command=self.new_buffer,accelerator="Ctrl+N")
                menu.add_command(label="Close Buffer",command=self.close_buffer,accelerator="Ctrl+Shift+W")
                menu.add_command(label="Set Working Directory...",command=self.set_working_directory)
                menu.add_command(label="Open Local File Manager in Browser...",command=self.open_local_file_manager)
                menu.add_command(label="Edit Current File RTL in Browser...",command=self.edit_current_file_rtl)
                menu.add_command(label="Open Local Email Archive in Browser...",command=self.open_local_email_archive)
                self.recent_menu=tk.Menu(menu,tearoff=False,postcommand=self._populate_recent_files)
                menu.add_cascade(label="Recent Files",menu=self.recent_menu)
                menu.add_separator()
            for item in items:
                shortcut=item.shortcut
                shown=shortcut.replace("Ctrl","Cmd") if sys.platform=="darwin" and shortcut else shortcut
                menu.add_command(label=item.label,accelerator=shown or "",
                                 command=lambda name=item.label:self.action(name))
                if shortcut and install_editor_shortcut(item.label,sys.platform):
                    parts=shortcut.split("+")
                    rawkey=parts[-1]
                    shifted="Shift" in parts[:-1]
                    key=(rawkey.upper() if shifted else rawkey.lower()) if len(rawkey)==1 else rawkey
                    modifiers=[{"Ctrl":"Control","Shift":"Shift"}.get(m,m) for m in parts[:-1]]
                    sequence="<"+"-".join(modifiers+[key])+">"
                    self.root.bind_all(sequence,lambda event,name=item.label:self._key(event,name))
                    if sys.platform=="darwin" and shortcut.startswith("Ctrl+"):
                        mac="<"+"-".join(["Command"]+modifiers[1:]+[key])+">"
                        self.root.bind_all(mac,lambda event,name=item.label:self._key(event,name))
            bar.add_cascade(label=group,menu=menu)
        mode_menu=tk.Menu(bar,tearoff=False)
        mode_menu.add_command(label="Select Buffer Mode...",command=self.select_buffer_mode)
        mode_menu.add_separator()
        mode_menu.add_command(label="Validate JSON",command=self.validate_buffer)
        mode_menu.add_command(label="Show jq Path at Cursor",command=self._json_path)
        mode_menu.add_command(label="Copy jq Path",command=self.copy_json_path)
        mode_menu.add_command(label="JSON Parent",command=lambda:self.navigate_json('parent'))
        mode_menu.add_command(label="JSON First Child",command=lambda:self.navigate_json('child'))
        mode_menu.add_command(label="Jump to JSON Path...",command=self.jump_json_path)
        mode_menu.add_command(label="JSON Next Sibling",command=lambda:self.navigate_json('next'))
        mode_menu.add_command(label="JSON Previous Sibling",command=lambda:self.navigate_json('previous'))
        mode_menu.add_command(label="Get JSON Value at Path...",command=self.json_value_at_path)
        mode_menu.add_command(label="Format JSON",command=self.format_json_buffer)
        mode_menu.add_command(label="Run jq on Buffer... (external)",command=self.run_jq)
        bar.add_cascade(label="Mode",menu=mode_menu)
        unicode_menu=tk.Menu(bar,tearoff=False)
        unicode_menu.add_command(label="Insert Unicode Character (U+...)...",command=self.insert_unicode_codepoint)
        unicode_menu.add_command(label="Describe Character at Cursor",command=self.describe_unicode_at_cursor)
        unicode_menu.add_command(label="Describe Character Sequence at Cursor...",command=self.describe_unicode_sequence_at_cursor)
        unicode_menu.add_command(label="Browse Unicode Range...",command=self.browse_unicode_range)
        blocks=tk.Menu(unicode_menu,tearoff=False)
        for label,spec in (("Hebrew / Yiddish (0590–05FF)","0590-05FF"),
                           ("Greek and Coptic (0370–03FF)","0370-03FF"),
                           ("Mathematical Operators (2200–22FF)","2200-22FF"),
                           ("Arrows (2190–21FF)","2190-21FF"),
                           ("Latin-1 Supplement (00A0–00FF)","00A0-00FF")):
            blocks.add_command(label=label,command=lambda x=spec:self.browse_unicode_range(x))
        unicode_menu.add_cascade(label="Browse Common Blocks",menu=blocks)
        unicode_menu.add_command(label="Search Unicode Names...",command=self.search_unicode_characters)
        unicode_menu.add_command(label="Common Symbols...",command=self.unicode_quick_characters)
        language_menu=tk.Menu(bar,tearoff=False)
        for code,label in LANGUAGES.items():
            language_menu.add_command(label=label,command=lambda lang=code:self.choose_language(lang))
        language_menu.add_separator()
        language_menu.add_command(label="Expand Dictionary Shortcut at Cursor",command=self.expand_dictionary_shortcut)
        language_menu.add_command(label="Look Up Word in Dictionary...",command=self.lookup_lexical_word)
        keymaps_menu=tk.Menu(language_menu,tearoff=False)
        keymaps_menu.add_command(label="System keyboard (off)",command=lambda:self.choose_keymap(None))
        keymaps_menu.add_separator()
        for name in sorted(self.available_keymaps):
            if name=="English":continue  # Original English file duplicates Greek; do not advertise.
            keymaps_menu.add_command(label=name,command=lambda n=name:self.choose_keymap(n))
        language_menu.add_cascade(label="Alt Keymaps (per buffer)",menu=keymaps_menu)
        language_menu.add_command(label="Show Keymap / Keyboard Reference...",command=self.show_keymap)
        bar.add_cascade(label="Language",menu=language_menu)
        notes_menu=tk.Menu(bar,tearoff=False)
        notes_menu.add_command(label="Annotate Selected Word / Word at Cursor...",command=self.annotate_word)
        notes_menu.add_command(label="Notes for Current File...",command=self.list_word_notes)
        bar.add_cascade(label="Notes",menu=notes_menu)
        bar.add_cascade(label="Unicode",menu=unicode_menu)
        fonts=tk.Menu(bar,tearoff=False)
        fonts.add_command(label="Choose Font Family...",command=self.choose_font_family)
        fonts.add_command(label="Choose Font Size...",command=self.choose_font_size)
        fonts.add_command(label="Toggle Bold",command=lambda:self._set_font_style(weight="normal" if self.editor_font.actual("weight")=="bold" else "bold"))
        fonts.add_command(label="Toggle Italic",command=lambda:self._set_font_style(slant="roman" if self.editor_font.actual("slant")=="italic" else "italic"))
        bar.add_cascade(label="Fonts",menu=fonts)
        self.root.configure(menu=bar)
        self.root.bind_all("<Control-n>",lambda e:self._key(e,"New Buffer"))
        self.root.bind_all("<Control-Shift-W>",lambda e:self._key(e,"Close Buffer"))
        if sys.platform=="darwin":
            self.root.bind_all("<Command-n>",lambda e:self._key(e,"New Buffer"))
            self.root.bind_all("<Command-Shift-W>",lambda e:self._key(e,"Close Buffer"))

    def _key(self,event,name):
        if name=="New Buffer":self.new_buffer()
        elif name=="Close Buffer":self.close_buffer()
        else:self.action(name)
        return "break"

    def close_buffer(self):
        tab=self.tabs.select()
        if not tab:return
        widget,editor=self.views[tab]
        if editor.state.buffer.modified and not messagebox.askyesno(
            "Unsaved changes","Close this buffer without saving?",parent=self.root):
            return
        self.tabs.forget(tab)
        del self.views[tab]
        self.saved_messages.pop(tab,None)
        self.disk_signatures.pop(tab,None)
        self.external_dismissals.reset(tab)
        self.buffer_modes.pop(tab,None)
        self.buffer_languages.pop(tab,None)
        self.buffer_keymaps.pop(tab,None)
        widget.master.destroy()
        if not self.views:self.new_buffer()

    def query_replace(self):
        """Modeless query-replace; y/n/!/q are handled in a focused prompt."""
        from ..query_replace import QueryReplace
        widget,_=self.current()
        if not widget:return
        needle=simpledialog.askstring("Query Replace","Find:",parent=self.root,
                                     initialvalue=self.search_term)
        if not needle:return
        replacement=simpledialog.askstring("Query Replace","Replace with:",parent=self.root)
        if replacement is None:return
        self.search_term=needle
        session=QueryReplace(widget.get("1.0","end-1c"),needle,replacement,
                             cursor=len(widget.get("1.0","insert")))
        if session.done:
            self.status.set("No occurrences found after cursor")
            return
        prompt=tk.Toplevel(self.root)
        prompt.title("Query Replace")
        prompt.transient(self.root)
        label=ttk.Label(prompt,padding=12)
        label.pack()
        controls=ttk.Frame(prompt,padding=8)
        controls.pack()
        def finish():
            widget.tag_remove("query_match","1.0","end")
            self.status.set(f"Replaced {session.replaced}; skipped {session.skipped}")
            prompt.destroy()
            widget.focus_set()
        def show():
            widget.tag_remove("query_match","1.0","end")
            if session.done:
                finish();return
            a=f"1.0 + {session.match} chars"
            b=f"1.0 + {session.match+len(needle)} chars"
            widget.tag_configure("query_match",background="yellow",foreground="black")
            widget.tag_add("query_match",a,b);widget.see(a)
            label.configure(text=f"Replace {needle!r} with {replacement!r}?")
        def choose(key):
            if not prompt.winfo_exists():return
            old=session.text
            pos=session.match
            session.answer(key)
            if key in ('y','!') and session.text!=old:
                if key=='y':
                    a=f"1.0 + {pos} chars";b=f"1.0 + {pos+len(needle)} chars"
                    widget.delete(a,b);widget.insert(a,replacement)
                else:
                    widget.delete("1.0","end");widget.insert("1.0",session.text)
            show()
            if prompt.winfo_exists():prompt.focus_set()
        for label_text,key in (("Yes (y)","y"),("No (n)","n"),
                               ("All (!)","!"),("Quit (q)","q")):
            ttk.Button(controls,text=label_text,
                       command=lambda k=key:choose(k)).pack(side="left",padx=4)
        def respond(event):
            key=event.char.lower()
            if event.keysym=="Escape":key="q"
            if key in ("y","n","!","q"):
                choose(key)
            return "break"
        prompt.bind("<Key>",respond)
        prompt.protocol("WM_DELETE_WINDOW",lambda:choose("q"))
        show()
        prompt.lift()
        prompt.after_idle(prompt.focus_set)

    def _vim_key(self,event):
        if event.keysym=="Escape":
            self.vim_normal=not self.vim_normal
            widget,_=self.current()
            if widget:self._status(widget)
            return "break"
        if not self.vim_normal:
            mapped=self._keymap_input(event)
            if mapped:return mapped
            return
        if event.state & 0x0c:return  # preserve existing Ctrl/Alt shortcuts
        if event.char=="i":
            self.vim_normal=False
            widget,_=self.current()
            if widget:self._status(widget)
            return "break"
        if event.char in ("/","?",":"):
            self._vim_prompt(event.char);return "break"
        if event.char in ("n","N"):
            self._vim_find(self.vim_direction * (1 if event.char=="n" else -1))
            return "break"
        return "break"  # normal mode must never insert characters

    def _vim_prompt(self,prefix):
        self.command_label.configure(text=prefix)
        self.command_value.set("")
        self.command_bar.pack(side="bottom",fill="x")
        self.command_entry.focus_set()

    def _vim_cancel(self,event=None):
        self.command_bar.pack_forget()
        widget,_=self.current()
        if widget:widget.focus_set()
        return "break"

    def _vim_submit(self,event=None):
        prefix=self.command_label.cget("text")
        value=self.command_value.get()
        self._vim_cancel()
        if prefix in ("/","?"):
            try:re.compile(value)
            except re.error as exc:
                self.status.set(f"Regex error: {exc}");return "break"
            if value:self.search_term=value
            self.vim_direction=1 if prefix=="/" else -1
            self._vim_find(self.vim_direction)
        elif prefix==":":
            if value.strip() in ("noh", "nohlsearch"):
                widget,_=self.current()
                if widget:
                    widget.tag_remove("sel","1.0","end")
                    widget.tag_remove("query_match","1.0","end")
                self.status.set("Search highlighting cleared")
            else:
                self._vim_substitute(value)
        return "break"

    def _vim_find(self,direction):
        widget,_=self.current()
        if not widget or not self.search_term:return
        text=widget.get("1.0","end-1c")
        try:regex=re.compile(self.search_term)
        except re.error as exc:self.status.set(f"Regex error: {exc}");return
        pos=len(widget.get("1.0","insert"))
        if direction>0:
            match=regex.search(text,pos)
            if match is None:match=regex.search(text,0,pos)
        else:
            matches=list(regex.finditer(text,0,pos))
            if not matches:matches=list(regex.finditer(text,pos))
            match=matches[-1] if matches else None
        if match:
            widget.tag_remove("sel","1.0","end")
            a=f"1.0 + {match.start()} chars";b=f"1.0 + {match.end()} chars"
            widget.tag_add("sel",a,b)
            widget.mark_set("insert",b if direction>0 else a)
            widget.see(a)
            self.status.set(f"{'/' if direction>0 else '?'}{self.search_term}")
        else:self.status.set("Pattern not found")

    def _vim_substitute(self,command):
        from ..vim_substitute import parse_substitute, substitution_matches
        widget,_=self.current()
        if not widget:return
        try:
            spec=parse_substitute(command)
            text=widget.get("1.0","end-1c")
            if spec.whole_buffer:
                start,end=0,len(text)
            else:
                line=int(widget.index("insert").split(".")[0])
                start=len(widget.get("1.0",f"{line}.0"))
                end=len(widget.get("1.0",f"{line}.end"))
            matches=substitution_matches(text,spec,start,end)
        except (ValueError,re.error,IndexError) as exc:
            self.status.set(f"Substitute: {exc}");return
        if not matches:self.status.set("Pattern not found");return
        # Apply from right to left so original offsets stay valid.
        if not spec.confirm:
            for a,b,repl in reversed(matches):
                widget.delete(f"1.0 + {a} chars",f"1.0 + {b} chars")
                widget.insert(f"1.0 + {a} chars",repl)
            self.status.set(f"{len(matches)} substitution(s)")
            return
        dialog=tk.Toplevel(self.root);dialog.title("Confirm substitution")
        label=ttk.Label(dialog,padding=10);label.pack()
        buttons=ttk.Frame(dialog);buttons.pack(padx=8,pady=8)
        pending=list(matches)
        chosen=[]
        def finish():
            for a,b,repl in reversed(chosen):
                widget.delete(f"1.0 + {a} chars",f"1.0 + {b} chars")
                widget.insert(f"1.0 + {a} chars",repl)
            self.status.set(f"{len(chosen)} substitution(s)")
            dialog.destroy();widget.focus_set()
        def show():
            widget.tag_remove("query_match","1.0","end")
            if not pending:finish();return
            a,b,_=pending[0]
            widget.tag_configure("query_match",background="yellow",foreground="black")
            widget.tag_add("query_match",f"1.0 + {a} chars",f"1.0 + {b} chars")
            widget.see(f"1.0 + {a} chars")
            label.configure(text="Replace highlighted match? y / n / ! / q")
        def choose(key):
            if key=="q":finish();return
            if key=="!":
                chosen.extend(pending);pending.clear()
            elif pending:
                item=pending.pop(0)
                if key=="y":chosen.append(item)
            show()
            if dialog.winfo_exists():dialog.focus_set()
        for title,key in (("Yes (y)","y"),("No (n)","n"),("All (!)","!"),("Quit (q)","q")):
            ttk.Button(buttons,text=title,command=lambda k=key:choose(k)).pack(side="left")
        def keypress(event):
            key=event.char.lower()
            if event.keysym=="Escape":key="q"
            if key in ("y","n","!","q"):choose(key)
            return "break"
        dialog.bind("<Key>",keypress)
        dialog.protocol("WM_DELETE_WINDOW",lambda:choose("q"))
        show();dialog.after_idle(dialog.focus_set)

    def replace_text(self):
        widget,_=self.current()
        if not widget:return
        needle=simpledialog.askstring("Replace","Find:",parent=self.root,
                                     initialvalue=self.search_term)
        if not needle:return
        replacement=simpledialog.askstring("Replace","Replace with:",parent=self.root)
        if replacement is None:return
        self.search_term=needle
        start="1.0"
        count=0
        # Search and replace forward; never re-scan replacement text.
        while True:
            found=widget.search(needle,start,stopindex="end")
            if not found:break
            end=widget.index(f"{found} + {len(needle)} chars")
            widget.delete(found,end)
            widget.insert(found,replacement)
            start=widget.index(f"{found} + {len(replacement)} chars")
            count+=1
        self.status.set(f"Replaced {count} occurrence(s)")

    def find_text(self):
        term=simpledialog.askstring("Find","Search text:",parent=self.root,
                                   initialvalue=getattr(self,"search_term",""))
        if term:
            self.search_term=term
            self.find_next(from_start=True)

    def find_next(self,from_start=False):
        widget,_=self.current()
        term=getattr(self,"search_term","")
        if not widget or not term:return
        start="1.0" if from_start else widget.index("insert")
        found=widget.search(term,start,stopindex="end",nocase=False)
        if not found and not from_start:
            found=widget.search(term,"1.0",stopindex=start,nocase=False)
        if found:
            end=widget.index(f"{found} + {len(term)} chars")
            widget.tag_remove("sel","1.0","end")
            widget.tag_add("sel",found,end)
            widget.mark_set("insert",end)
            widget.see(found);widget.focus_set()
        else:
            self.root.bell()

    def revert_file(self):
        widget,editor=self.current()
        if not widget or not editor.state.buffer.path:return
        if editor.state.buffer.modified and not messagebox.askyesno(
            "Revert","Discard edits and reload from disk?",parent=self.root):return
        try:
            from ..files import open_buffer
            b=open_buffer(editor.state.buffer.path)
            widget.delete("1.0","end");widget.insert("1.0",b.text)
            widget.edit_reset();widget.edit_modified(False)
            editor.state.buffer=b
            self.disk_signatures[self.tabs.select()]=disk_signature(b.path)
            self.external_dismissals.reset(self.tabs.select())
            self._check_external_changes()
            self.saved_messages[self.tabs.select()]=None
            self.buffer_modes[self.tabs.select()]=self.mode_registry.detect(b.path,b.text)
            self.tabs.tab(self.tabs.select(),text=Path(b.path).name)
        except (OSError,UnicodeError) as exc:
            messagebox.showerror("Revert failed",str(exc),parent=self.root)

    def set_working_directory(self):
        path=filedialog.askdirectory(parent=self.root,initialdir=self.working_directory.initial_directory(),
                                    title="Set ZEFM Working Directory",mustexist=True)
        if path:
            try:self.working_directory.set_directory(path)
            except ValueError as exc:messagebox.showerror("Working Directory",str(exc),parent=self.root);return
            self.status.set(f"Working directory: {self.working_directory.initial_directory()}")

    def _populate_recent_files(self):
        menu=self.recent_menu
        if menu is None:return
        menu.delete(0,'end')
        if not self.recent_files.entries:
            menu.add_command(label='(No recent files)',state='disabled')
        for i,path in enumerate(self.recent_files.entries):
            # Preserve full path in the menu to distinguish same-named files.
            menu.add_command(label=f'{i+1}. {path}',
                             command=lambda p=path:self.open_recent_file(p))
        menu.add_separator()
        menu.add_command(label='Clear Recent Files',command=self._clear_recent_files,
                         state='normal' if self.recent_files.entries else 'disabled')

    def _clear_recent_files(self):
        self.recent_files.clear()
        self.status.set('Recent files cleared')

    def open_recent_file(self,path):
        if not Path(path).is_file():
            if messagebox.askyesno('File not found',
                    f'{path}\n\nRemove this missing file from Recent Files?',parent=self.root):
                self.recent_files.forget(path)
            return
        self._open_path(path)

    def _open_path(self,path):
        # Re-select an already-open buffer rather than opening duplicate tabs.
        resolved=Path(path).expanduser().resolve()
        for tab,(widget,editor) in self.views.items():
            old=editor.state.buffer.path
            if old is not None and Path(old).expanduser().resolve()==resolved:
                self.tabs.select(tab)
                widget.focus_set()
                if changed_on_disk(resolved,self.disk_signatures.get(tab)):
                    if editor.state.buffer.modified:
                        messagebox.showwarning("File changed on disk",
                            "The file changed outside ZEFM, but this buffer has unsaved edits. "
                            "Your edits are preserved. Use File → Revert to reload, or Save to confirm an overwrite.",
                            parent=self.root)
                    elif messagebox.askyesno("File changed on disk",
                            f"{resolved.name} changed outside ZEFM. Reload it from disk?",
                            parent=self.root):
                        self.revert_file()
                self._status(widget)
                self.recent_files.record(resolved)
                return
        try:
            from ..files import open_buffer
            b=open_buffer(str(resolved))
            self.new_buffer(path=b.path,text=b.text)
            self.working_directory.used_file(b.path)
            self.recent_files.record(b.path)
        except (OSError,UnicodeError) as exc:
            messagebox.showerror('Open failed',str(exc),parent=self.root)

    def open_file(self):
        path=filedialog.askopenfilename(parent=self.root,initialdir=self.working_directory.initial_directory())
        if path:self._open_path(path)

    def save_file(self,as_new=False):
        widget,editor=self.current()
        if not widget:return
        path=editor.state.buffer.path
        if as_new or not path:
            path=filedialog.asksaveasfilename(parent=self.root,initialdir=self.working_directory.initial_directory())
            if not path:return
        # A file may have changed in the browser or another program.
        # Check BEFORE writing and leave the editor text untouched on refusal.
        current_tab=self.tabs.select()
        old_path=editor.state.buffer.path
        same_path=(old_path is not None and Path(old_path).expanduser().resolve()==Path(path).expanduser().resolve())
        if same_path:
            try:
                external_change = changed_on_disk(path, self.disk_signatures.get(current_tab))
            except OSError as exc:
                messagebox.showerror("Save blocked",
                    f"Unable to verify the disk version of {Path(path).name}: {exc}",
                    parent=self.root)
                return
        else:
            external_change = False
        if external_change:
            if not messagebox.askyesno("External file changes",
                f"{Path(path).name} has changed on disk since ZEFM opened or last saved it.\n\n"
                "Overwrite the newer disk version with the editor buffer?",
                parent=self.root):
                self.status.set("Save cancelled: file changed outside ZEFM")
                return
        editor.state.buffer.text=widget.get("1.0","end-1c")
        try:
            from ..files import save_buffer
            save_buffer(editor.state.buffer,path)
            self.disk_signatures[current_tab]=disk_signature(path)
            self.external_dismissals.reset(current_tab)
            self._check_external_changes()
            self.working_directory.used_file(path)
            self.recent_files.record(path)
            self.tabs.tab(self.tabs.select(),text=path.rsplit("/",1)[-1])
            widget.edit_modified(False)
            editor.state.buffer.modified=False
            self._update_title(widget,editor)
            self.saved_messages[self.tabs.select()]=f"Saved: {Path(path).name}"
            self._status(widget)
        except (OSError,UnicodeError) as exc:messagebox.showerror("Save failed",str(exc),parent=self.root)

    def _drain_browser_requests(self):
        """Process HTTP-originated requests exclusively on the Tk main thread."""
        self.browser_poll_id = None
        try:
            while True:
                path = self.browser_open_requests.get_nowait()
                self._open_path(path)
                self.root.lift()
        except Empty:
            pass
        if self.local_browser is not None:
            self.browser_poll_id = self.root.after(150, self._drain_browser_requests)

    def edit_current_file_rtl(self):
        """Edit the saved file in a browser with real RTL cursor/layout support.

        This is intentionally a disk-based bridge: unsaved Tk edits are never
        uploaded or discarded, and the browser's digest-protected Save applies.
        """
        widget, editor = self.current()
        if not widget:
            return
        path = editor.state.buffer.path
        if not path:
            messagebox.showinfo("RTL editing", "Save the file before opening its RTL browser editor.",
                                parent=self.root)
            return
        if (editor.state.buffer.modified or
                widget.get("1.0", "end-1c") != editor.state.buffer.text):
            messagebox.showwarning("Unsaved changes",
                "Please save this buffer before editing it in the RTL browser. "
                "ZEFM will not discard unsaved changes.", parent=self.root)
            return
        try:
            from ...server.http import BrowserServer
            resolved = Path(path).expanduser().resolve()
            if not resolved.is_file():
                raise OSError(f"File does not exist: {resolved}")
            directory = resolved.parent
            if self.local_browser is not None and self.local_browser.files.root != directory:
                self.local_browser.close()
                self.local_browser = None
            if self.local_browser is None:
                self.local_browser = BrowserServer(
                    str(directory), open_in_editor=self.browser_open_requests.put)
            url = self.local_browser.start()
            if self.browser_poll_id is None:
                self.browser_poll_id = self.root.after(150, self._drain_browser_requests)
            webbrowser.open(url + "edit?" + urlencode({"path": resolved.name, "dir": "rtl"}))
            self.status.set("RTL browser editor opened; save there, then reload in ZEFM.")
        except (OSError, ValueError) as exc:
            messagebox.showerror("RTL editing", str(exc), parent=self.root)

    def open_local_file_manager(self):
        """Serve only the currently selected local directory, using loopback HTTP."""
        from ...server.http import BrowserServer
        root=self.working_directory.initial_directory()
        try:
            if self.local_browser is not None and self.local_browser.files.root != Path(root).resolve():
                self.local_browser.close()
                self.local_browser=None
            if self.local_browser is None:
                self.local_browser=BrowserServer(root, open_in_editor=self.browser_open_requests.put)
            url=self.local_browser.start()
            if self.browser_poll_id is None:
                self.browser_poll_id = self.root.after(150, self._drain_browser_requests)
            webbrowser.open(url)
            self.status.set(f"Local file manager: {url} (root: {root})")
        except (OSError,ValueError) as exc:
            messagebox.showerror("Local file manager",str(exc),parent=self.root)

    def open_local_email_archive(self):
        """Open existing local Maildir accounts without fetching or sending mail."""
        from ...server.mail_archive import discover_maildirs
        from ...server.mail_http import MailBrowser
        try:
            accounts = discover_maildirs()
            if not accounts:
                selected = filedialog.askdirectory(
                    parent=self.root, initialdir=str(Path.home()),
                    title="Select a Maildir folder (contains cur/ and new/)")
                if not selected:
                    return
                accounts = {"Local": selected}
            if self.mail_browser is None or self.mail_browser.archive.accounts != {
                    label: Path(directory).expanduser().resolve()
                    for label, directory in accounts.items()}:
                if self.mail_browser is not None:
                    self.mail_browser.close()
                self.mail_browser = MailBrowser(accounts)
            url = self.mail_browser.start()
            webbrowser.open(url)
            self.status.set(f"Local Maildir browser: {url} ({', '.join(accounts)})")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Local email archive", str(exc), parent=self.root)

    def quit(self):
        for widget,editor in self.views.values():
            if widget.get("1.0","end-1c") != editor.state.buffer.text:
                editor.state.buffer.modified=True
        if any(e.state.buffer.modified for _,e in self.views.values()):
            if not messagebox.askyesno("Unsaved changes","Quit with unsaved buffers?",parent=self.root):
                return
        if self.disk_poll_id is not None:
            self.root.after_cancel(self.disk_poll_id)
            self.disk_poll_id = None
        if self.browser_poll_id is not None:
            self.root.after_cancel(self.browser_poll_id)
            self.browser_poll_id = None
        if self.local_browser is not None:
            self.local_browser.close()
            self.local_browser=None
        if self.mail_browser is not None:
            self.mail_browser.close()
            self.mail_browser = None
        self.root.destroy()

def main():
    window=Window()
    window.root.protocol("WM_DELETE_WINDOW",window.quit)
    window.root.mainloop()

if __name__=="__main__":main()
