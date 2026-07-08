"""Entry point for WinChatCollector inspector tooling."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from inspector.live_inspector_cli import app


if __name__ == "__main__":
    app()
