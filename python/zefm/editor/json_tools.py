"""Pure Python JSON utilities; no jq executable required for path extraction."""
import json
from .json_path import paths_at, jq_path

def format_json(source, indent=2):
    return json.dumps(json.loads(source), ensure_ascii=False, indent=indent) + "\n"

def value_at_path(source, parts):
    value=json.loads(source)
    for part in parts:
        value=value[part]
    return value

def parse_simple_path(expression):
    """A deliberately limited jq-style path: .key, [N], and [quoted JSON key]."""
    import re
    if not expression.startswith("."):
        raise ValueError("Path must begin with .")
    parts=[];i=1
    decoder=json.JSONDecoder()
    while i<len(expression):
        if expression[i]==".":
            i+=1
        if i>=len(expression):break
        if expression[i]=="[":
            i+=1
            if i<len(expression) and expression[i]=='"':
                key,end=decoder.raw_decode(expression[i:])
                if not isinstance(key,str):raise ValueError("Expected key")
                i+=end
                if i>=len(expression) or expression[i]!="]":raise ValueError("Expected ]")
                i+=1;parts.append(key)
            else:
                match=re.match(r"(0|[1-9][0-9]*)\]",expression[i:])
                if not match:raise ValueError("Expected nonnegative index")
                parts.append(int(match.group(1)));i+=len(match.group())
        else:
            match=re.match(r"[A-Za-z_][A-Za-z_0-9]*",expression[i:])
            if not match:raise ValueError("Invalid path component")
            parts.append(match.group());i+=len(match.group())
            if i<len(expression) and expression[i] not in ".[":raise ValueError("Unexpected character")
    return parts
