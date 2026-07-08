"""Entry point for searching controls in a discovered window."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from inspector.find_control_cli import app
if __name__ == "__main__":
    app()
