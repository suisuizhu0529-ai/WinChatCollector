"""Entry point for point-in-time UI inspection.

When imported as ``inspect`` this file proxies Python's standard-library module so
repo-local tooling such as pytest is not broken by the CLI filename requirement.
"""

from pathlib import Path
import sys
import sysconfig

if __name__ != "__main__":
    _stdlib_inspect = Path(sysconfig.get_path("stdlib")) / "inspect.py"
    exec(compile(_stdlib_inspect.read_text(encoding="utf-8"), str(_stdlib_inspect), "exec"), globals())
else:
    ROOT = Path(__file__).resolve().parent
    SRC = ROOT / "src"
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))

    from inspector.inspect_cli import app

    app()
