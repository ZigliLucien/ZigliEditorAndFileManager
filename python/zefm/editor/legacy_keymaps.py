"""Original ZEFM Alphabet.java keymap format (decimal Java VK codes)."""
from dataclasses import dataclass
from pathlib import Path
import re

_RECORD = re.compile(r"([0-9]+)([SC]?)=([0-9]+)")

@dataclass(frozen=True)
class LegacyKey:
    keycode: int
    modifier: str
    decimal_payload: str

    @property
    def characters(self):
        """Alphabet.java: one decimal codepoint (<7 digits), or two 4-digit values."""
        payload=self.decimal_payload
        if len(payload)<7:
            numbers=[int(payload)]
        elif len(payload)==8:
            numbers=[int(payload[:4]),int(payload[4:])]
        else:
            raise ValueError(f"Unsupported original Unicode payload: {payload}")
        if any(n>0x10ffff or 0xd800<=n<=0xdfff for n in numbers):
            raise ValueError(f"Invalid Unicode codepoint in {payload}")
        return ''.join(chr(n) for n in numbers)

    @property
    def single_character(self):
        return self.characters if len(self.characters)==1 else None

def parse_keymap(text):
    result={}
    for line_number,raw in enumerate(text.splitlines(),1):
        line=raw.strip()
        if not line or line.startswith('#'):continue
        match=_RECORD.fullmatch(line)
        if not match:raise ValueError(f"Invalid keymap entry at line {line_number}: {line!r}")
        keycode,modifier,payload=match.groups()
        key=(int(keycode),modifier)
        if key in result:raise ValueError(f"Duplicate keymap entry at line {line_number}: {key!r}")
        result[key]=LegacyKey(key[0],modifier,payload)
    return result

def read_keymap(path):
    return parse_keymap(Path(path).read_text(encoding='utf-8'))

# Java VK_* for alphabetic and punctuation keys in the legacy maps.
_KEYSYMS={'bracketleft':91,'bracketright':93,'semicolon':59,'comma':44,'period':46,
          'slash':47,'backslash':92,'apostrophe':222,'minus':45,'equal':61}

def key_event_to_java_code(keysym):
    """Translate Tk logical key names, rather than platform-dependent hardware codes."""
    if len(keysym)==1:
        return ord(keysym.upper())
    return _KEYSYMS.get(keysym)

def translation(mapping,keysym,shift=False,alt=False,meta=False):
    """Return mapped string or None; maps are active only for explicit Alt chords."""
    if not alt:return None
    code=key_event_to_java_code(keysym)
    if code is None:return None
    suffix='C' if meta else 'S' if shift else ''
    entry=mapping.get((code,suffix))
    return entry.characters if entry is not None else None
