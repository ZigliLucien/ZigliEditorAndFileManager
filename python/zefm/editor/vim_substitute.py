"""Small Python-regex subset of Vim :s and :%s, with g/c/i flags."""
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Substitute:
    whole_buffer: bool
    pattern: str
    replacement: str
    global_line: bool
    confirm: bool
    ignore_case: bool

def parse_substitute(command):
    whole=command.startswith('%')
    rest=command[1:] if whole else command
    if not rest.startswith('s') or len(rest)<3:
        raise ValueError('Expected s/pattern/replacement/flags or %s/...')
    delim=rest[1]
    if delim.isalnum() or delim.isspace():raise ValueError('Invalid delimiter')
    def field(i):
        chars=[]
        while i<len(rest):
            c=rest[i]
            if c=='\\' and i+1<len(rest):
                if rest[i+1]==delim:chars.append(delim);i+=2;continue
                chars.extend((c,rest[i+1]));i+=2;continue
            if c==delim:return ''.join(chars),i+1
            chars.append(c);i+=1
        raise ValueError('Missing substitution delimiter')
    pattern,i=field(2)
    replacement,i=field(i)
    flags=rest[i:]
    if not pattern:raise ValueError('Empty pattern')
    if any(c not in 'gci' for c in flags):raise ValueError('Supported flags: g, c, i')
    re.compile(pattern)
    return Substitute(whole,pattern,replacement,'g' in flags,'c' in flags,'i' in flags)

def substitution_matches(text,spec,start,end):
    regex=re.compile(spec.pattern,re.IGNORECASE if spec.ignore_case else 0)
    matches=[]
    segment=text[start:end]
    for line in segment.splitlines(keepends=True):
        line_start=start
        count=0
        for m in regex.finditer(line.rstrip('\n')):
            matches.append((line_start+m.start(),line_start+m.end(),m.expand(spec.replacement)))
            count+=1
            if not spec.global_line:break
        start+=len(line)
    return matches
