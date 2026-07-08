"""Centralized UI Automation matching rules for chat locators.

All chat locators must use this module instead of embedding AutomationId,
ClassName, or ControlType string literals in locator implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ControlRule:
    """A reusable set of UI Automation identity fields for locating controls."""

    automation_ids: tuple[str, ...] = ()
    class_names: tuple[str, ...] = ()
    control_types: tuple[str, ...] = ()

    def matches(self, control: Any) -> bool:
        """Return True when the control matches all populated rule fields."""
        automation_id = safe_text(control, ControlField.AUTOMATION_ID)
        class_name = safe_text(control, ControlField.CLASS_NAME)
        control_type = safe_text(control, ControlField.CONTROL_TYPE)
        if self.automation_ids and automation_id not in self.automation_ids:
            return False
        if self.class_names and class_name not in self.class_names:
            return False
        if self.control_types and control_type not in self.control_types:
            return False
        return True


class ControlField:
    """UI Automation property names used by locator rules."""

    AUTOMATION_ID = "AutomationId"
    CLASS_NAME = "ClassName"
    CONTROL_TYPE = "ControlTypeName"
    BOUNDING_RECTANGLE = "BoundingRectangle"


class AutomationIds:
    """Known AutomationId values for DingTalk chat surfaces."""

    CONVERSATION_LIST = "ConvListView"
    CHAT_CONTENT = "DTIMContentModule"
    CHAT_BUBBLE_WIDGET = "ChatBubbleWidget"
    FOOTER_BAR = "FootBar"
    SPLITTER = "QSplitter"


class ClassNames:
    """Known ClassName values for DingTalk chat surfaces."""

    STANDARD_FRAME = "StandardFrame_DingTalk"
    NAVIGATOR_VIEW = "NavigatorView"
    CHAT_WINDOW = "DingChatWnd"
    CONVERSATION_LIST = "ConvListView"
    CHAT_CONTENT = "DTIMContentModule"
    CHAT_BUBBLE_WIDGET = "ChatBubbleWidget"
    FOOTER_BAR = "FootBar"
    SPLITTER = "QSplitter"
    CEF_BROWSER_WINDOW = "CefBrowserWindow"


class ControlTypes:
    """Known ControlTypeName values used as secondary matching signals."""

    PANE = "PaneControl"
    LIST = "ListControl"
    DOCUMENT = "DocumentControl"
    EDIT = "EditControl"
    CUSTOM = "CustomControl"


CONVERSATION_LIST_RULES = (
    ControlRule(automation_ids=(AutomationIds.CONVERSATION_LIST,)),
    ControlRule(class_names=(ClassNames.CONVERSATION_LIST,)),
)

CHAT_CONTENT_RULES = (
    ControlRule(automation_ids=(AutomationIds.CHAT_CONTENT,)),
    ControlRule(class_names=(ClassNames.CHAT_CONTENT,)),
)

MESSAGE_CONTAINER_RULES = (
    ControlRule(automation_ids=(AutomationIds.CHAT_BUBBLE_WIDGET,)),
    ControlRule(class_names=(ClassNames.CHAT_BUBBLE_WIDGET,)),
    ControlRule(class_names=(ClassNames.CEF_BROWSER_WINDOW,)),
)

INPUT_AREA_RULES = (
    ControlRule(control_types=(ControlTypes.EDIT,)),
)

FOOTER_BAR_RULES = (
    ControlRule(automation_ids=(AutomationIds.FOOTER_BAR,)),
    ControlRule(class_names=(ClassNames.FOOTER_BAR,)),
)

TOP_BAR_RULES = (
    ControlRule(control_types=(ControlTypes.PANE,), class_names=(ClassNames.SPLITTER,)),
    ControlRule(automation_ids=(AutomationIds.SPLITTER,)),
)


def safe_text(control: Any, field_name: str) -> str:
    """Read a UI Automation identity field without leaking COM exceptions."""
    try:
        value = getattr(control, field_name, "")
    except Exception:
        return ""
    return "" if value is None else str(value)


def matches_any(control: Any, rules: tuple[ControlRule, ...]) -> bool:
    """Return True if the control matches one of the supplied rules."""
    return any(rule.matches(control) for rule in rules)
