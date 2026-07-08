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
        return self.match_reason(control) is not None

    def match_reason(self, control: Any) -> str | None:
        """Return the UIA field that matched, or None when this rule does not match."""
        automation_id = safe_text(control, ControlField.AUTOMATION_ID)
        class_name = safe_text(control, ControlField.CLASS_NAME)
        control_type = safe_text(control, ControlField.CONTROL_TYPE)
        matched_fields: list[str] = []
        if self.automation_ids:
            if automation_id not in self.automation_ids:
                return None
            matched_fields.append("AutomationId")
        if self.class_names:
            if class_name not in self.class_names:
                return None
            matched_fields.append("ClassName")
        if self.control_types:
            if control_type not in self.control_types:
                return None
            matched_fields.append("ControlType")
        return ", ".join(matched_fields) if matched_fields else None


class ControlField:
    """UI Automation property names used by locator rules."""

    NAME = "Name"
    AUTOMATION_ID = "AutomationId"
    CLASS_NAME = "ClassName"
    CONTROL_TYPE = "ControlTypeName"
    BOUNDING_RECTANGLE = "BoundingRectangle"


class AutomationIds:
    """Known AutomationId values for DingTalk chat surfaces."""

    CONVERSATION_LIST = "ConvListView"
    CONVERSATION_TOP_BAR = "ConvTabTopBar"
    CHAT_CONTENT = "DTIMContentModule"
    CHAT_BUBBLE_WIDGET = "ChatBubbleWidget"
    FOOTER_BAR = "FootBar"
    SPLITTER = "QSplitter"
    INPUT_AREA = "InputArea"


class ClassNames:
    """Known ClassName values for DingTalk chat surfaces."""

    STANDARD_FRAME = "StandardFrame_DingTalk"
    NAVIGATOR_VIEW = "NavigatorView"
    CHAT_WINDOW = "DingChatWnd"
    CONVERSATION_LIST = "ConvListView"
    CONVERSATION_TOP_BAR = "ConvTabTopBar"
    CHAT_CONTENT = "DTIMContentModule"
    CHAT_BUBBLE_WIDGET = "ChatBubbleWidget"
    FOOTER_BAR = "FootBar"
    SPLITTER = "QSplitter"
    CEF_BROWSER_WINDOW = "CefBrowserWindow"
    INPUT_AREA = "InputArea"


class ControlTypes:
    """Known ControlTypeName values used as secondary matching signals."""

    PANE = "PaneControl"
    LIST = "ListControl"
    DOCUMENT = "DocumentControl"
    EDIT = "EditControl"
    CUSTOM = "CustomControl"


CHAT_WINDOW_RULES = (
    ControlRule(class_names=(ClassNames.CHAT_WINDOW,)),
)

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
    ControlRule(automation_ids=(AutomationIds.INPUT_AREA,)),
    ControlRule(class_names=(ClassNames.INPUT_AREA,)),
    ControlRule(control_types=(ControlTypes.EDIT,)),
)

FOOTER_BAR_RULES = (
    ControlRule(automation_ids=(AutomationIds.FOOTER_BAR,)),
    ControlRule(class_names=(ClassNames.FOOTER_BAR,)),
)

TOP_BAR_RULES = (
    ControlRule(automation_ids=(AutomationIds.CONVERSATION_TOP_BAR,)),
    ControlRule(class_names=(ClassNames.CONVERSATION_TOP_BAR,)),
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


def match_reason(control: Any, locator_rules: tuple[ControlRule, ...]) -> str | None:
    """Return the first matching rule reason for a control."""
    for rule in locator_rules:
        reason = rule.match_reason(control)
        if reason is not None:
            return reason
    return None


def matches_any(control: Any, rules: tuple[ControlRule, ...]) -> bool:
    """Return True if the control matches one of the supplied rules."""
    return match_reason(control, rules) is not None
