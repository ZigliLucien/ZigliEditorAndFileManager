"""Portable, optional font preferences for ZEFM Tk editor."""
import json
import os
from pathlib import Path

DEFAULT_FONT = {"family":"DejaVu Sans Mono", "size":13, "weight":"normal", "slant":"roman"}

def valid_font(settings):
    if not isinstance(settings,dict):return False
    return (isinstance(settings.get("family"),str) and bool(settings["family"].strip())
        and type(settings.get("size")) is int and 6<=settings["size"]<=72
        and settings.get("weight") in ("normal","bold")
        and settings.get("slant") in ("roman","italic"))

def read_font(path):
    try:
        data=json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError,ValueError,TypeError):return dict(DEFAULT_FONT)
    return {key:data[key] for key in DEFAULT_FONT} if valid_font(data) else dict(DEFAULT_FONT)

def write_font(path,settings):
    if not valid_font(settings):raise ValueError("Invalid font preferences")
    path=Path(path).expanduser()
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps({key:settings[key] for key in DEFAULT_FONT},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temp,path)
