# Inspector Phase 1.5: Window Discovery

WinChatCollector phase 1.5 provides Windows UI Automation window discovery and UI-tree analysis.
It does **not** export chat records, perform OCR, or use AI.

## Window discovery

`WindowFinder` can locate top-level windows without reading the mouse cursor:

- window title substring via `--window`
- process name substring via `--process-name`
- process id via `--pid`

## Tools

- `inspect.py`: legacy cursor-based spot inspector for a single UI Automation control.
- `dump_tree.py`: discovers a top-level window and exports a limited-depth subtree to `tree.txt` and `tree.json`.
- `find_window.py`: lists all top-level windows with `Title`, `ClassName`, `PID`, `Handle`, and `BoundingRectangle`, optionally filtered by `--title`.
- `find_control.py`: discovers a window, searches the full exported tree by `ControlType`, `AutomationId`, `ClassName`, or `Name`, and prints location metadata.
- `tree_search.py`: searches an already-exported `tree.json` for quick offline UI-tree analysis.
- `live_inspector.py`: continuously refreshes the current cursor control in a Rich terminal view, similar in spirit to Microsoft Inspect.exe.

## Examples

```bash
python find_window.py
python find_window.py --title DingTalk

python dump_tree.py --window DingTalk
python dump_tree.py --process-name DingTalk.exe
python dump_tree.py --pid 12345

python find_control.py --type List
python find_control.py --class ChatBubbleWidget
python find_control.py --name convlist

python tree_search.py tree.json TextControl
python tree_search.py tree.json ListControl
python tree_search.py tree.json ChatBubble
python tree_search.py tree.json Chrome_WidgetWin_1
```

Search result tables include:

- `NodeId`
- `Path`
- `Depth`
- `Parent`
- `Children`

## Target

The initial compatibility target is Windows DingTalk v8.3.15. The inspector remains client-agnostic so future phases can add platform-specific knowledge without changing core UI Automation collection.
