"""Message tree dump utility for debugging DingTalk chat UI structure.

Accepts an already-located MessageContainer control and recursively dumps
all descendants with their UI Automation properties.

Usage (development only):

    from chat.message_tree_dump import MessageTreeDump
    dump = MessageTreeDump()
    text = dump.dump(message_container)
    print(text)
"""

from __future__ import annotations

from typing import Any

from chat import locator_rules as rules

MAX_DEPTH = 20
NAME_MAX_LEN = 80


class MessageTreeDump:
    """Recursively dump the UI tree under a MessageContainer."""

    def dump(self, message_container: Any) -> str:
        """Return a text representation of the message container's subtree."""
        lines: list[str] = []
        self._walk(message_container, lines, depth=0)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal recursion

    def _walk(self, control: Any, lines: list[str], depth: int) -> None:
        if depth > MAX_DEPTH:
            return

        indent = "  " * depth
        info = self._describe(control, depth)
        lines.append(f"{indent}{info}")

        try:
            children = control.GetChildren()
        except Exception:
            return

        for child in children:
            if child is not None:
                self._walk(child, lines, depth + 1)

    # ------------------------------------------------------------------
    # Property extraction

    def _describe(self, control: Any, depth: int) -> str:
        ct = rules.safe_text(control, rules.ControlField.CONTROL_TYPE)
        aid = rules.safe_text(control, rules.ControlField.AUTOMATION_ID)
        cn = rules.safe_text(control, rules.ControlField.CLASS_NAME)
        name = rules.safe_text(control, rules.ControlField.NAME)

        parts = [f"[D{depth}] {ct}"]
        if aid:
            parts.append(f"AutomationId={aid}")
        if cn:
            parts.append(f"ClassName={cn}")
        if name:
            name = name[:NAME_MAX_LEN]
            parts.append(f"Name={name!r}")
        return " ".join(parts)
