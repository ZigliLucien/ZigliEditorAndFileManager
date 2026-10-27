"""File-dialog directory state, persisted without changing process cwd."""
import json
import os
from pathlib import Path

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
        self.state_path = Path(state_path).expanduser() if state_path is not None else None
        if self.remember and self.state_path is not None:
            try:
                data=json.loads(self.state_path.read_text(encoding='utf-8'))
                candidate=data.get('last_directory')
                if isinstance(candidate,str) and Path(candidate).is_dir():
                    self.current=Path(candidate).resolve()
            except (OSError,ValueError,TypeError,AttributeError):
                pass

    def initial_directory(self):
        return str(self.current if self.current.is_dir() else self.home)

    def _persist(self):
        if not self.remember or self.state_path is None:return
        try:
            self.state_path.parent.mkdir(parents=True,exist_ok=True)
            temp=self.state_path.with_name(self.state_path.name+'.tmp')
            temp.write_text(json.dumps({'last_directory':str(self.current)},ensure_ascii=False)+'\n',encoding='utf-8')
            os.replace(temp,self.state_path)
        except OSError:
            pass

    def set_directory(self, directory):
        path = Path(directory).expanduser().resolve()
        if not path.is_dir():
            raise ValueError(f'Not a directory: {path}')
        self.current = path
        self._persist()

    def used_file(self, filename):
        if self.remember:
            self.set_directory(Path(filename).expanduser().resolve().parent)
