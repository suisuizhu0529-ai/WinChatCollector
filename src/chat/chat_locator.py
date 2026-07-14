"""High-level DingTalk chat layout locator."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
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
DebugLogger = Callable[[str], None]


class ChatLocator:
    """Locate core chat regions from a DingTalk WindowControl."""

    def __init__(
        self,
        message_locator: MessageLocator | None = None,
        debug_logger: DebugLogger | None = None,
    ) -> None:
        self.debug_logger = debug_logger
        self.message_locator = message_locator or MessageLocator(debug_logger=debug_logger)

    def locate(self, window: Any) -> ChatLayout:
        """Return all known chat layout regions for a top-level window control."""
        self._debug("Searching...")
        chat_root = self._find_first(window, rules.CHAT_WINDOW_RULES, "DingChatWnd") or window
        if chat_root is window:
            self._debug("DingChatWnd not found; searching from the supplied window.")
        else:
            self._debug(f"✓ DingChatWnd ({self._identity(chat_root)})")

        conversation_list = self._locate(
            chat_root,
            rules.CONVERSATION_LIST_RULES,
            ConversationList,
            "ConversationList",
        )
        top_bar = self._locate(
            chat_root,
            rules.TOP_BAR_RULES,
            ConversationTopBar,
            "ConversationTopBar",
        )
        chat_content = self._locate(
            chat_root,
            rules.CHAT_CONTENT_RULES,
            ChatContent,
            "ChatContent",
        )
        message_container = self.message_locator.locate(chat_content, fallback_root=chat_root)
        input_area = self._locate(
            chat_content.control or chat_root,
            rules.INPUT_AREA_RULES,
            InputArea,
            "InputArea",
        )
        footer_bar = self._locate(
            chat_content.control or chat_root,
            rules.FOOTER_BAR_RULES,
            FooterBar,
            "FooterBar",
        )
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
        label: str,
    ) -> TLocated:
        if root is None:
            self._debug(f"✗ {label}: no search root")
            return self._missing(model_type)
        match = self._find_first(root, locator_rules, label)
        if match is None:
            self._debug(f"✗ {label}")
            return self._missing(model_type)
        self._debug(f"✓ {label} ({self._identity(match)})")
        return self._describe(match, model_type)

    def _find_first(
        self,
        root: Any,
        locator_rules: tuple[rules.ControlRule, ...],
        label: str,
    ) -> Any | None:
        queue = deque([root])
        while queue:
            control = queue.popleft()
            self._debug(f"Checking {label}: {self._identity(control)}")
            reason = rules.match_reason(control, locator_rules)
            if reason is not None:
                self._debug(f"Matched {label} by {reason}: {self._identity(control)}")
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
