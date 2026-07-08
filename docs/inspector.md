# Inspector Phase 1

WinChatCollector phase 1 only provides a Windows UI Automation inspection framework.
It does **not** export chat records, perform OCR, or use AI.

## Tools

- `inspect.py`: waits briefly, reads the UI Automation control under the mouse cursor,
  and prints name, AutomationId, ControlType, ClassName, BoundingRectangle, RuntimeId,
  parent, and child count.
- `dump_tree.py`: reads the control under the mouse cursor and exports a limited-depth
  subtree to `tree.txt` and `inspect.json`.
- `live_inspector.py`: continuously refreshes the current cursor control in a Rich
  terminal view, similar in spirit to Microsoft Inspect.exe.

## Target

The initial compatibility target is Windows DingTalk v8.3.15. The inspector remains
client-agnostic so future phases can add platform-specific knowledge without changing
core UI Automation collection.
