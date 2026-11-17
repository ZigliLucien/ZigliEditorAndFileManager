"""Working-directory selection, separate from the last opened file.

An explicitly chosen working directory stays pinned across Open and Save.
Without an explicit choice, the file dialogs retain their historical
follow-the-last-file behavior. Persisted state is backward-compatible.
"""
import json
import os
from pathlib import Path
import tempfile


class WorkingDirectory:
    def __init__(self, home_directory='~', remember_last_directory=True, state_path=None):
        if not isinstance(home_directory, str) or not home_directory.strip():
            raise ValueError('home_directory must be a nonempty string')
        if type(remember_last_directory) is not bool:
            raise ValueError('remember_last_directory must be boolean')
        self.home = Path(home_directory).expanduser().resolve()
        if not self.home.is_dir():
            raise ValueError(f'Home directory does not exist: {self.home}')
        self.remember = remember_last_directory
        self.current = self.home
        self.pinned = False
        self.state_path = Path(state_path).expanduser() if state_path is not None else None
        if self.remember and self.state_path is not None:
            try:
                data = json.loads(self.state_path.read_text(encoding='utf-8'))
                if isinstance(data, dict):
                    candidate = data.get('last_directory')
                    if isinstance(candidate, str) and Path(candidate).expanduser().is_dir():
                        self.current = Path(candidate).expanduser().resolve()
                        self.pinned = data.get('pinned') is True
            except (OSError, ValueError, TypeError, AttributeError):
                pass

    def initial_directory(self):
        return str(self.current if self.current.is_dir() else self.home)

    def _persist(self):
        if not self.remember or self.state_path is None:
            return
        temporary = None
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                    mode='w', encoding='utf-8', prefix='.zefm-session-',
                    suffix='.tmp', dir=self.state_path.parent, delete=False) as output:
                temporary = Path(output.name)
                if os.name == 'posix':
                    os.fchmod(output.fileno(), 0o600)
                json.dump({'last_directory': str(self.current),
                           'pinned': self.pinned}, output, ensure_ascii=False)
                output.write('\n')
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.state_path)
        except OSError:
            pass
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

    def set_directory(self, directory):
        """Pin an explicit choice until the user changes or resets it."""
        path = Path(directory).expanduser().resolve()
        if not path.is_dir():
            raise ValueError(f'Not a directory: {path}')
        self.current = path
        self.pinned = True
        self._persist()

    def use_last_file_directory(self):
        """Return to automatic directory selection based on Open / Save."""
        self.pinned = False
        self._persist()

    def used_file(self, filename):
        if not self.remember or self.pinned:
            return
        parent = Path(filename).expanduser().resolve().parent
        if parent.is_dir():
            self.current = parent
            self._persist()
