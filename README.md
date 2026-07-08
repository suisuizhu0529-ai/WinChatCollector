# WinChatCollector

WinChatCollector is an open-source Windows desktop automation research project.
Phase 1 is limited to a Windows UI Automation Inspector for Windows DingTalk v8.3.15.

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

Prints the UI Automation control currently under the mouse cursor:

- control name
- AutomationId
- ControlType
- ClassName
- BoundingRectangle
- RuntimeId
- parent node summary
- child count

```bash
python inspect.py --delay 0.2
```

### `dump_tree.py`

Exports the subtree rooted at the control under the mouse cursor. The maximum traversal
height is configurable.

```bash
python dump_tree.py --max-depth 6 --output-dir .
```

Outputs:

- `tree.txt`
- `inspect.json`

### `live_inspector.py`

Starts a Rich-based live inspector that refreshes the UI Automation control under the
mouse cursor.

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
  automation/   # Windows automation adapters
  inspector/    # CLI tools and output formatting
  models/       # Serializable UI element models
  utils/        # Logging and shared utilities
  config/       # Runtime defaults
docs/           # Project documentation
tests/          # Automated tests
```
