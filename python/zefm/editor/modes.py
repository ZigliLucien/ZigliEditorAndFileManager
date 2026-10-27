"""Per-buffer mode detection and validated JSON mode registry; no GUI dependency."""
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass(frozen=True)
class ModeSpec:
    name: str
    indent_width: int = 4
    use_tabs: bool = False

class ModeRegistry:
    def __init__(self, data):
        if not isinstance(data, dict) or set(data) != {'default_mode','extensions','filenames','modes'}:
            raise ValueError('Invalid mode registry structure')
        raw=data['modes']
        if not isinstance(raw,dict) or not raw:raise ValueError('modes must be a nonempty object')
        self.modes={}
        for name,settings in raw.items():
            if not isinstance(name,str) or not name or not isinstance(settings,dict) or set(settings)-{'indent_width','use_tabs'}:
                raise ValueError('Invalid mode specification')
            width=settings.get('indent_width',4); tabs=settings.get('use_tabs',False)
            if type(width) is not int or not 1<=width<=16 or type(tabs) is not bool:
                raise ValueError('Invalid indentation preferences')
            self.modes[name]=ModeSpec(name,width,tabs)
        self.default=data['default_mode']
        if self.default not in self.modes:raise ValueError('Unknown default mode')
        self.extensions=self._mapping(data['extensions'],extension=True)
        self.filenames=self._mapping(data['filenames'],extension=False)
    def _mapping(self,values,extension):
        if not isinstance(values,dict):raise ValueError('Mode mapping must be an object')
        for key,mode in values.items():
            if not isinstance(key,str) or not key or (extension and (not key.startswith('.') or key!=key.lower())) or mode not in self.modes:
                raise ValueError(f'Invalid mode mapping: {key}')
        return dict(values)
    @classmethod
    def load(cls,path):
        return cls(json.loads(Path(path).read_text(encoding='utf-8')))
    def detect(self,path=None,text='',override=None):
        if override is not None:
            if override not in self.modes:raise ValueError(f'Unknown mode: {override}')
            return self.modes[override]
        if path:
            name=Path(path).name
            if name in self.filenames:return self.modes[self.filenames[name]]
            extension=Path(name).suffix.lower()
            if extension in self.extensions:return self.modes[self.extensions[extension]]
        first=text.split('\n',1)[0].strip()
        if first.startswith('#!'):
            if 'python' in first and 'python' in self.modes:return self.modes['python']
        if (first.startswith('<?xml') or first.startswith('<!DOCTYPE')) and 'xml' in self.modes:
            return self.modes['xml']
        return self.modes[self.default]
