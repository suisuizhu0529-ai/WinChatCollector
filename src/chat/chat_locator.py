"""High-level DingTalk chat layout locator."""

from __future__ import annotations

from typing import Any, TypeVar

from chat import locator_rules as rules
from chat.message_locator import MessageLocator
from chat.models import (
    ChatContent,
    ChatLayout,
    ConversationList,
    ConversationTopBar,
    FooterBar,
    InputArea,
    LocatedControl,
)
from models.ui_element import BoundingRectangle

TLocated = TypeVar("TLocated", bound=LocatedControl)


class ChatLocator:
    """Locate core chat regions from a DingTalk WindowControl."""

    def __init__(self, message_locator: MessageLocator | None = None) -> None:
        self.message_locator = message_locator or MessageLocator()

    def locate(self, window: Any) -> ChatLayout:
        """Return all known chat layout regions for a top-level window control."""
        conversation_list = self._locate(window, rules.CONVERSATION_LIST_RULES, ConversationList)
        chat_content = self._locate(window, rules.CHAT_CONTENT_RULES, ChatContent)
        message_container = self.message_locator.locate(chat_content)
        input_area = self._locate(chat_content.control, rules.INPUT_AREA_RULES, InputArea)
        footer_bar = self._locate(chat_content.control, rules.FOOTER_BAR_RULES, FooterBar)
        top_bar = self._locate(chat_content.control or window, rules.TOP_BAR_RULES, ConversationTopBar)
        return ChatLayout(
            conversation_list=conversation_list,
            conversation_top_bar=top_bar,
            chat_content=chat_content,
            message_container=message_container,
            input_area=input_area,
            footer_bar=footer_bar,
        )

    def _locate(
        self,
        root: Any | None,
        locator_rules: tuple[rules.ControlRule, ...],
        model_type: type[TLocated],
    ) -> TLocated:
        if root is None:
            return self._missing(model_type)
        match = self._find_first(root, locator_rules)
        return self._describe(match, model_type) if match is not None else self._missing(model_type)

    def _find_first(self, root: Any, locator_rules: tuple[rules.ControlRule, ...]) -> Any | None:
        queue = [root]
        while queue:
            control = queue.pop(0)
            if rules.matches_any(control, locator_rules):
                return control
            queue.extend(self._children(control))
        return None

    def _describe(self, control: Any, model_type: type[TLocated]) -> TLocated:
        children = self._children(control)
        return model_type(
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
            left=ChatLocator._rect_value(rectangle, "left", "Left"),
            top=ChatLocator._rect_value(rectangle, "top", "Top"),
            right=ChatLocator._rect_value(rectangle, "right", "Right"),
            bottom=ChatLocator._rect_value(rectangle, "bottom", "Bottom"),
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

    @staticmethod
    def _missing(model_type: type[TLocated]) -> TLocated:
        return model_type(
            control=None,
            automation_id="",
            class_name="",
            control_type="",
            bounding_rectangle=BoundingRectangle(0, 0, 0, 0),
            child_count=0,
        )
