"""Data models for DingTalk chat layout location."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models.ui_element import BoundingRectangle


@dataclass(frozen=True)
class LocatedControl:
    """Metadata for a UI Automation control located in the chat layout."""

    control: Any | None
    automation_id: str
    class_name: str
    control_type: str
    bounding_rectangle: BoundingRectangle
    child_count: int

    @property
    def found(self) -> bool:
        """Return whether the underlying control was found."""
        return self.control is not None


@dataclass(frozen=True)
class ConversationList(LocatedControl):
    """Located conversation list area."""


@dataclass(frozen=True)
class ConversationTopBar(LocatedControl):
    """Located conversation header/top-bar area."""


@dataclass(frozen=True)
class ChatContent(LocatedControl):
    """Located chat content area."""


@dataclass(frozen=True)
class MessageContainer(LocatedControl):
    """Located message-list container inside the chat content area."""


@dataclass(frozen=True)
class InputArea(LocatedControl):
    """Located message input area."""


@dataclass(frozen=True)
class FooterBar(LocatedControl):
    """Located footer/action bar area."""


@dataclass(frozen=True)
class ChatLayout:
    """All core regions needed to understand a DingTalk chat window layout."""

    conversation_list: ConversationList
    conversation_top_bar: ConversationTopBar
    chat_content: ChatContent
    message_container: MessageContainer
    input_area: InputArea
    footer_bar: FooterBar
