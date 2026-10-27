"""Unicode codepoint and bounded block browsing utilities."""
import re
import unicodedata

def parse_codepoint(value):
    value=value.strip()
    match=re.fullmatch(r"(?:U\+)?([0-9A-Fa-f]{1,6})",value,re.IGNORECASE)
    if not match:raise ValueError("Enter a hexadecimal code point, such as U+05D0")
    cp=int(match.group(1),16)
    if cp>0x10FFFF or 0xD800<=cp<=0xDFFF:raise ValueError("Invalid Unicode scalar value")
    return chr(cp)

def unicode_range(spec):
    match=re.fullmatch(r"\s*(?:U\+)?([0-9a-fA-F]{1,6})\s*[-:]\s*(?:U\+)?([0-9a-fA-F]{1,6})\s*",spec,re.I)
    if not match:raise ValueError("Use a range like 0590-05FF")
    start,end=(int(x,16) for x in match.groups())
    if start>end or end>0x10FFFF or end-start>1023:raise ValueError("Choose an ascending range of at most 1024 code points")
    return [(cp,unicodedata.name(chr(cp))) for cp in range(start,end+1)
            if not 0xD800<=cp<=0xDFFF and unicodedata.name(chr(cp),None)]

def search_unicode_names(query, limit=200):
    """Search Unicode character names, bounded for interactive use."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Enter a Unicode name or part of a name")
    words=query.upper().split()
    if not isinstance(limit,int) or not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000")
    found=[]
    for cp in range(0x110000):
        if 0xD800 <= cp <= 0xDFFF:continue
        name=unicodedata.name(chr(cp),None)
        if name and all(word in name for word in words):
            found.append((cp,name))
            if len(found)>=limit:break
    return found

def character_description(character):
    """Explain a Unicode scalar, including combining marks used in Yiddish."""
    if len(character) != 1:
        raise ValueError('Select exactly one Unicode character')
    cp = ord(character)
    if 0xD800 <= cp <= 0xDFFF:
        raise ValueError('Unicode surrogates are not characters')
    name = unicodedata.name(character, 'UNNAMED CHARACTER')
    combining = unicodedata.combining(character)
    label = f'U+{cp:04X}  {name}'
    if combining:
        label += f'  [combining class {combining}]'
    return label


def character_context_description(text, index):
    """Show a character plus preceding base/combining sequence when applicable."""
    if not isinstance(text,str) or not 0 <= index < len(text):
        raise ValueError("Cursor must be on a character")
    start=index
    while start>0 and unicodedata.combining(text[start]):
        start-=1
    end=index+1
    while end<len(text) and unicodedata.combining(text[end]):
        end+=1
    cluster=text[start:end]
    descriptions=[character_description(char) for char in cluster]
    return cluster, descriptions
