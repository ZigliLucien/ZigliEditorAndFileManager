"""One local UTF-8 JSONL lexical dictionary per language.

The legacy `dictionaries` SQL table stores (lang, word, data), where `data`
contains translations (often comma-separated), NOT keyboard shortcuts.
Keep it distinct from the small language shortcut/expansion JSON files.
"""
import json
import os
import re
import tempfile
from pathlib import Path

_LANGUAGE_ALIASES = {'french': 'fr', 'fr': 'fr', 'yiddish': 'yi', 'yi': 'yi'}
_CODE = re.compile(r'[a-z][a-z0-9_-]{0,39}\Z')


def language_code(original):
    if not isinstance(original,str) or not original.strip():
        raise ValueError('Dictionary language must be nonempty text')
    code=_LANGUAGE_ALIASES.get(original.strip().casefold(),original.strip().lower())
    if not _CODE.fullmatch(code):
        raise ValueError(f'Unsafe/invalid dictionary language identifier: {original!r}')
    return code


def default_lexicon_dir():
    root=Path(os.environ.get('XDG_DATA_HOME') or Path.home()/'.local'/'share').expanduser()
    return root/'zefm'/'dictionaries'


def validate_record(entry):
    if not isinstance(entry,dict) or set(entry) != {'lang','word','data'}:
        raise ValueError('Dictionary record requires exactly lang, word, data')
    if not all(isinstance(entry[field],str) for field in ('lang','word','data')):
        raise ValueError('All dictionary fields must be Unicode text')
    if not entry['word'].strip():
        raise ValueError('Dictionary word must be nonempty')
    language_code(entry['lang'])
    return {field:entry[field] for field in ('lang','word','data')}


def read_export(source):
    """Stream the JSONL export produced by export_legacy_tables."""
    with Path(source).expanduser().open('r',encoding='utf-8') as f:
        for lineno,line in enumerate(f,1):
            if not line.strip():continue
            try:
                yield validate_record(json.loads(line))
            except (ValueError,TypeError) as exc:
                raise ValueError(f'Invalid dictionary entry, line {lineno}: {exc}') from exc


def import_lexicons(source, output_dir=None, *, overwrite=False, dry_run=False):
    """Split an exported DB table by language, without discarding duplicate words.

    Validates all input before modifying any existing dictionary. Stages every
    output in a private temporary file before commit. Doesn't convert commas
    into new records, since legacy data often contains multiple translations.
    """
    directory=Path(output_dir).expanduser() if output_dir else default_lexicon_dir()
    records={}
    for entry in read_export(source):
        records.setdefault(language_code(entry['lang']),[]).append(entry)
    targets={code:directory/f'{code}.jsonl' for code in records}
    if not overwrite:
        existing=[str(p) for p in targets.values() if p.exists()]
        if existing:raise FileExistsError('Refusing to replace existing dictionaries: '+', '.join(existing))
    counts={code:len(entries) for code,entries in records.items()}
    if dry_run or not records:return counts
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    staged={}
    try:
        for code,entries in records.items():
            with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',dir=directory,
                prefix=f'.{code}-',suffix='.tmp',delete=False) as out:
                path=Path(out.name)
                staged[code]=path
                os.chmod(path,0o600)
                for entry in entries:
                    out.write(json.dumps(entry,ensure_ascii=False)+'\n')
                out.flush();os.fsync(out.fileno())
        for code,path in staged.items():
            os.replace(path,targets[code])
    finally:
        for path in staged.values():path.unlink(missing_ok=True)
    return counts


def lookup_lexicon(directory, language, word):
    """Exact-word lookup, case-insensitive for Latin text; no SQL dependency."""
    code=language_code(language)
    if not isinstance(word,str) or not word.strip():return []
    source=Path(directory).expanduser()/f'{code}.jsonl'
    if not source.exists():return []
    found=[]
    for entry in read_export(source):
        if language_code(entry['lang']) != code:
            raise ValueError(f'Unexpected language in {source}')
        if entry['word'].casefold()==word.casefold():
            found.append(entry['data'])
    return found
