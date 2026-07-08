"""Message container locator for DingTalk chat content."""

from __future__ import annotations

from typing import Any

from chat import locator_rules as rules
from chat.models import ChatContent, MessageContainer
from models.ui_element import BoundingRectangle


class MessageLocator:
    """Locate the message-list container without reading message text."""

    def locate(self, chat_content: ChatContent) -> MessageContainer:
        """Return message container metadata for the supplied chat content area."""
        if chat_content.control is None:
            return self._missing()
        match = self._find_first(chat_content.control, rules.MESSAGE_CONTAINER_RULES)
        return self._describe(match) if match is not None else self._missing()

    def _find_first(self, root: Any, locator_rules: tuple[rules.ControlRule, ...]) -> Any | None:
        queue = [root]
        while queue:
            control = queue.pop(0)
            if control is not root and rules.matches_any(control, locator_rules):
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
