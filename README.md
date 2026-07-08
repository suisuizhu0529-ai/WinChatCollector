# WinChatCollector

WinChatCollector is an open-source Windows desktop automation research project.
Phase 1.5 is limited to Windows UI Automation window discovery and UI-tree analysis for Windows DingTalk v8.3.15.

> Scope guard: this phase does not include chat exporting, OCR, or AI features.

## Requirements

- Python 3.11
- Windows with UI Automation support
- DingTalk for Windows v8.3.15 for the first target validation

## Installation

```bash
python -m pip install -e .
```

## Tools

### `inspect.py`

Prints the UI Automation control currently under the mouse cursor. This legacy inspector remains useful for quick spot checks.

```bash
python inspect.py --delay 0.2
```

### `dump_tree.py`

Exports the UI Automation tree rooted at a discovered top-level window. It no longer depends on mouse position.

```bash
python dump_tree.py --window DingTalk --max-depth 6 --output-dir .
python dump_tree.py --process-name DingTalk.exe --max-depth 6 --output-dir .
python dump_tree.py --pid 12345 --max-depth 6 --output-dir .
```

Outputs:

- `tree.txt`
- `tree.json`


### `find_window.py`

Lists all top-level windows discovered from the desktop root, with optional title filtering.

```bash
python find_window.py
python find_window.py --title DingTalk
```

Output columns: `Title`, `ClassName`, `PID`, `Handle`, and `BoundingRectangle`.

### `find_control.py`

Searches the discovered window tree and prints `NodeId`, `Path`, `Depth`, `Parent`, and `Children` for matches. The default window title filter is `DingTalk`.

```bash
python find_control.py --type List
python find_control.py --class ChatBubbleWidget
python find_control.py --name convlist
python find_control.py --automation-id some-id
```

### `tree_search.py`

Searches an exported `tree.json` without opening the target application again.

```bash
python tree_search.py tree.json TextControl
python tree_search.py tree.json ListControl
python tree_search.py tree.json ChatBubble
python tree_search.py tree.json Chrome_WidgetWin_1
```

### `live_inspector.py`

Starts a Rich-based live inspector that refreshes the UI Automation control under the mouse cursor.

```bash
python live_inspector.py --interval 0.5
```

## Development

```bash
python -m pip install -e .[dev]
pytest
```

## Project Layout

```text
src/
  automation/   # Windows automation adapters and window discovery
  inspector/    # CLI tools, search, serialization, and output formatting
  models/       # Serializable UI element models
  utils/        # Logging and shared utilities
  config/       # Runtime defaults
docs/           # Project documentation
tests/          # Automated tests
```
