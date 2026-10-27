"""Basic Java .properties to UTF-8 JSON migration helper.

Review complex escape syntax and duplicate keys against the Java original.
"""
import json
import re
from pathlib import Path


def import_properties(source, target):
    raw = Path(source).read_text(encoding='iso-8859-1')
    logical = []
    pending = ''
    for line in raw.splitlines():
        line = pending + (line.lstrip() if pending else line)
        trailing = len(line) - len(line.rstrip('\\'))
        if trailing % 2:
            pending = line[:-1]
        else:
            logical.append(line)
            pending = ''
    if pending:
        logical.append(pending)

    def decode(value):
        value = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), value)
        return re.sub(r'\\([tnrf =:#!\\])', lambda m: {'t':'\t','n':'\n','r':'\r','f':'\f'}.get(m.group(1),m.group(1)), value)

    result = {}
    for line in logical:
        line = line.lstrip()
        if not line or line[0] in '#!':
            continue
        match = re.match(r'((?:\\.|[^=:\s])+)\s*(?:[=:]\s*|\s+)(.*)$', line)
        key, value = match.groups() if match else (line, '')
        result[decode(key)] = decode(value)
    Path(target).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import Java .properties into UTF-8 JSON")
    parser.add_argument("source")
    parser.add_argument("target")
    args = parser.parse_args()
    result = import_properties(args.source, args.target)
    print(f"Imported {len(result)} properties into {args.target}")
