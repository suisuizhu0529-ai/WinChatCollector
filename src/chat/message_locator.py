"""Message container locator for DingTalk chat content."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import Any

from chat import locator_rules as rules
from chat.models import ChatContent, MessageContainer
from models.ui_element import BoundingRectangle

DebugLogger = Callable[[str], None]


class MessageLocator:
    """Locate the message-list container without reading message text."""

    def __init__(self, debug_logger: DebugLogger | None = None) -> None:
        self.debug_logger = debug_logger

    def locate(
        self,
        chat_content: ChatContent,
        fallback_root: Any | None = None,
    ) -> MessageContainer:
        """Return message container metadata for the supplied chat content area."""
        search_root = chat_content.control or fallback_root
        if search_root is None:
            self._debug("✗ MessageContainer: no search root")
            return self._missing()
        match = self._find_first(search_root, rules.MESSAGE_CONTAINER_RULES, chat_content.control)
        if match is None:
            self._debug("✗ MessageContainer")
            return self._missing()
        self._debug(f"✓ MessageContainer ({self._identity(match)})")
        return self._describe(match)

    def _find_first(
        self,
        root: Any,
        locator_rules: tuple[rules.ControlRule, ...],
        chat_content_control: Any | None,
    ) -> Any | None:
        queue = deque([root])
        while queue:
            control = queue.popleft()
            self._debug(f"Checking MessageContainer: {self._identity(control)}")
            reason = rules.match_reason(control, locator_rules)
            if reason is not None and control is not chat_content_control:
                self._debug(f"Matched MessageContainer by {reason}: {self._identity(control)}")
                return control
            queue.extend(self._children(control))
        return None

    def _describe(self, control: Any) -> MessageContainer:
        children = self._children(control)
        return MessageContainer(
            control=control,
            automation_id=rules.safe_text(control, rules.ControlField.AUTOMATION_ID),
            class_name=rules.safe_text(control, rules.ControlField.CLASS_NAME),
            control_type=rules.safe_text(control, rules.ControlField.CONTROL_TYPE),
            bounding_rectangle=self._bounding_rectangle(control),
            child_count=len(children),
        )

    @staticmethod
    def _children(control: Any) -> list[Any]:
        try:
            children = control.GetChildren()
        except Exception:
            return []
        return [child for child in children if child is not None]

    @staticmethod
    def _bounding_rectangle(control: Any) -> BoundingRectangle:
        rectangle = getattr(control, rules.ControlField.BOUNDING_RECTANGLE, None)
        return BoundingRectangle(
            left=MessageLocator._rect_value(rectangle, "left", "Left"),
            top=MessageLocator._rect_value(rectangle, "top", "Top"),
            right=MessageLocator._rect_value(rectangle, "right", "Right"),
            bottom=MessageLocator._rect_value(rectangle, "bottom", "Bottom"),
        )

    @staticmethod
    def _rect_value(rectangle: Any, *names: str) -> int:
        for name in names:
            if hasattr(rectangle, name):
                try:
                    return int(getattr(rectangle, name))
                except (TypeError, ValueError):
                    return 0
        return 0

    def _missing(self) -> MessageContainer:
        return MessageContainer(
            control=None,
            automation_id="",
            class_name="",
            control_type="",
            bounding_rectangle=BoundingRectangle(0, 0, 0, 0),
            child_count=0,
        )

    def _identity(self, control: Any) -> str:
        name = rules.safe_text(control, rules.ControlField.NAME)
        automation_id = rules.safe_text(control, rules.ControlField.AUTOMATION_ID)
        class_name = rules.safe_text(control, rules.ControlField.CLASS_NAME)
        control_type = rules.safe_text(control, rules.ControlField.CONTROL_TYPE)
        return (
            f"Name={name!r} AutomationId={automation_id!r} "
            f"ClassName={class_name!r} ControlType={control_type!r}"
        )

    def _debug(self, message: str) -> None:
        if self.debug_logger is not None:
            self.debug_logger(message)
