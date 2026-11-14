"""Optional desktop TeX engine preference; browser builds retain LuaLaTeX."""
import json
import os
from pathlib import Path
import tempfile

ENGINES = ("lualatex", "pdflatex", "xelatex")


def validate_engine(engine):
    if engine not in ENGINES or not isinstance(engine, str):
        raise ValueError("Choose lualatex, pdflatex, or xelatex")
    return engine


class LatexEnginePreference:
    def __init__(self, path=None):
        self.path = (Path(path).expanduser() if path is not None else
                     Path.home() / ".config" / "zefm" / "latex_engine.json")
        self.engine = "lualatex"
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.engine = validate_engine(data["engine"])
        except (OSError, ValueError, KeyError, TypeError):
            pass

    def set(self, engine):
        engine = validate_engine(engine)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                    prefix=".latex-engine-", suffix=".tmp",
                    dir=self.path.parent, delete=False) as out:
                tmp = Path(out.name)
                if os.name == "posix":
                    os.fchmod(out.fileno(), 0o600)
                json.dump({"engine": engine}, out, ensure_ascii=False, indent=2)
                out.write("\n")
                out.flush()
                os.fsync(out.fileno())
            os.replace(tmp, self.path)
        finally:
            if tmp is not None:
                tmp.unlink(missing_ok=True)
        self.engine = engine
