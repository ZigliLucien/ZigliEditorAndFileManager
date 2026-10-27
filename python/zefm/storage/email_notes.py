"""Local email annotations keyed by stable message identifiers.

No editor popups or email transport are implemented here. This is a storage
building block for the later web/mail subsystem; never mutate message bodies.
"""
import json
import os
from pathlib import Path


class EmailNotes:
    def __init__(self, store_path=None):
        self.path=Path(store_path).expanduser() if store_path else Path.home()/".config"/"zefm"/"email_notes.json"
        self.notes={}
        try:
            data=json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data,dict) and isinstance(data.get("notes"),dict):
                self.notes={k:v for k,v in data["notes"].items()
                            if isinstance(k,str) and k.strip() and isinstance(v,str)}
        except (OSError,ValueError,TypeError):
            pass

    @staticmethod
    def _key(message_id):
        if not isinstance(message_id,str) or not message_id.strip():
            raise ValueError("A nonempty email message identifier is required")
        return message_id.strip()

    def get(self,message_id):
        return self.notes.get(self._key(message_id),"")

    def set(self,message_id,note):
        key=self._key(message_id)
        if not isinstance(note,str):raise TypeError("Notes must be text")
        if note.strip():self.notes[key]=note
        else:self.notes.pop(key,None)
        self._save()

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.path.with_name(self.path.name+".tmp")
        tmp.write_text(json.dumps({"notes":self.notes},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        os.replace(tmp,self.path)
