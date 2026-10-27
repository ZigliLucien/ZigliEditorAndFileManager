"""Source-position-aware JSON paths. Offsets are Python string character offsets."""
import json
import re
from json.decoder import scanstring

_NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')
_IDENT = re.compile(r'^[A-Za-z_][A-Za-z_0-9]*$')

def jq_path(parts):
    out = "."
    for part in parts:
        if isinstance(part, int):
            out += f"[{part}]"
        elif _IDENT.fullmatch(part):
            out += ("" if out == "." else ".") + part
        else:
            out += "[" + json.dumps(part, ensure_ascii=False) + "]"
    return out

def source_spans(text):
    """Return deepest JSON path covering offset; None for invalid JSON/outside."""
    spans = []
    n = len(text)
    def ws(i):
        while i < n and text[i] in " \t\r\n": i += 1
        return i
    def string(i):
        if i >= n or text[i] != '"': raise ValueError("Expected string")
        value, end = scanstring(text, i + 1, True)
        return value, end
    def parse(i, path):
        i = ws(i)
        start = i
        if i >= n: raise ValueError("Unexpected end")
        c = text[i]
        if c == '{':
            i = ws(i + 1)
            if i < n and text[i] == '}': i += 1
            else:
                while True:
                    key_start = i
                    key, i = string(i)
                    key_end = i
                    spans.append((key_start, key_end, path + (key,)))
                    i = ws(i)
                    if i >= n or text[i] != ':': raise ValueError("Expected colon")
                    value_start = i + 1
                    i = parse(value_start, path + (key,))
                    spans.append((key_end, i, path + (key,)))
                    i = ws(i)
                    if i < n and text[i] == '}': i += 1; break
                    if i >= n or text[i] != ',': raise ValueError("Expected comma")
                    i = ws(i + 1)
        elif c == '[':
            i = ws(i + 1)
            if i < n and text[i] == ']': i += 1
            else:
                k = 0
                while True:
                    i = parse(i, path + (k,))
                    k += 1
                    i = ws(i)
                    if i < n and text[i] == ']': i += 1; break
                    if i >= n or text[i] != ',': raise ValueError("Expected comma")
                    i = ws(i + 1)
        elif c == '"':
            _, i = string(i)
        elif c in '-0123456789':
            m = _NUMBER.match(text, i)
            if not m: raise ValueError("Invalid number")
            i = m.end()
        else:
            literal = next((v for v in ('true','false','null') if text.startswith(v,i)), None)
            if literal is None: raise ValueError("Invalid literal")
            i += len(literal)
        spans.append((start, i, path))
        return i
    try:
        end = ws(parse(0, ()))
        if end != n: return None
        # Check syntax strictly, including duplicate handling consistent with stdlib.
        json.loads(text)
    except (ValueError, json.JSONDecodeError, IndexError):
        return None
    return spans

def path_parts_at(text, offset):
    spans = source_spans(text)
    if spans is None:return None
    candidates = [x for x in spans if x[0] <= offset < x[1]]
    if not candidates and offset == len(text):
        candidates = [x for x in spans if x[0] <= offset <= x[1]]
    return max(candidates, key=lambda x:len(x[2]))[2] if candidates else None

def paths_at(text, offset):
    parts = path_parts_at(text, offset)
    return jq_path(parts) if parts is not None else None

def navigate(text, offset, direction):
    """Return (target source offset, jq path), or None at boundaries/invalid JSON.

    Navigation targets the key token of object members and value of array members.
    """
    spans=source_spans(text)
    if spans is None:return None
    current=path_parts_at(text,offset)
    if current is None:return None
    if direction == 'parent':
        target=current[:-1] if current else None
    elif direction == 'child':
        children={path for start,end,path in spans
                  if len(path)==len(current)+1 and path[:-1]==current}
        target=min(children,key=lambda p:locate_path(text,p)) if children else None
    elif direction in ('next','previous'):
        if not current:return None
        siblings=[]
        for start,end,path in spans:
            if len(path)==len(current) and path[:-1]==current[:-1] and path not in siblings:
                siblings.append(path)
        # Order by first source occurrence; spans include object keys.
        siblings.sort(key=lambda path:min(start for start,end,p in spans if p==path))
        pos=siblings.index(current)
        dest=pos+(1 if direction=='next' else -1)
        if not 0<=dest<len(siblings):return None
        target=siblings[dest]
    else:raise ValueError('Unknown navigation direction')
    if target is None:return None
    starts=[start for start,end,path in spans if path==target]
    if not starts:return None
    return min(starts),jq_path(target)


def locate_path(text, parts):
    """Return source offset for exact structural path, or None."""
    spans=source_spans(text)
    if spans is None:return None
    starts=[start for start,end,path in spans if path==tuple(parts)]
    return min(starts) if starts else None
