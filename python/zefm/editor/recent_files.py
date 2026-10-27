"""Bounded, persistent recent local files, separate from working-directory state."""
import json
import os
from pathlib import Path


class RecentFiles:
    def __init__(self, state_path=None, limit=12):
        if not isinstance(limit, int) or not 1 <= limit <= 50:
            raise ValueError('Recent-files limit must be between 1 and 50')
        self.path = Path(state_path).expanduser() if state_path else Path.home() / '.config' / 'zefm' / 'recent_files.json'
        self.limit = limit
        self.entries = []
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if isinstance(data, dict) and isinstance(data.get('files'), list):
                for item in data['files']:
                    if isinstance(item, str) and item and item not in self.entries:
                        self.entries.append(item)
                        if len(self.entries) == limit:
                            break
        except (OSError, ValueError, TypeError):
            pass

    def record(self, filename):
        full = str(Path(filename).expanduser().resolve())
        self.entries = [full] + [entry for entry in self.entries if entry != full]
        self.entries = self.entries[:self.limit]
        self._write()

    def forget(self, filename):
        self.entries = [x for x in self.entries if x != str(Path(filename).expanduser().resolve())]
        self._write()

    def clear(self):
        self.entries.clear()
        self._write()

    def _write(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_name(self.path.name + '.tmp')
            tmp.write_text(json.dumps({'files': self.entries}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(tmp, self.path)
        except OSError:
            # Read-only home directories should not prevent editing files.
            pass
