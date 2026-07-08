"""Tests for DingTalk chat layout locators using fake UIA controls."""

from chat import locator_rules as rules
from chat.chat_locator import ChatLocator


class Rect:
    def __init__(self, left: int = 1, top: int = 2, right: int = 3, bottom: int = 4) -> None:
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom


class FakeControl:
    def __init__(
        self,
        *,
        name: str = "",
        automation_id: str = "",
        class_name: str = "",
        control_type: str = "PaneControl",
        children: list["FakeControl"] | None = None,
    ) -> None:
        self.Name = name
        self.AutomationId = automation_id
        self.ClassName = class_name
        self.ControlTypeName = control_type
        self.BoundingRectangle = Rect()
        self._children = children or []

    def GetChildren(self) -> list["FakeControl"]:
        return self._children


def test_chat_locator_finds_core_regions_from_ding_chat_window_subtree() -> None:
    message = FakeControl(automation_id=rules.AutomationIds.CHAT_BUBBLE_WIDGET)
    input_area = FakeControl(control_type=rules.ControlTypes.EDIT)
    footer = FakeControl(automation_id=rules.AutomationIds.FOOTER_BAR)
    top_bar = FakeControl(class_name=rules.ClassNames.CONVERSATION_TOP_BAR)
    content = FakeControl(
        automation_id=rules.AutomationIds.CHAT_CONTENT,
        children=[top_bar, message, footer, input_area],
    )
    conversation_list = FakeControl(class_name=rules.ClassNames.CONVERSATION_LIST)
    stale_list_outside_chat = FakeControl(
        automation_id=rules.AutomationIds.CONVERSATION_LIST,
    )
    chat_window = FakeControl(
        class_name=rules.ClassNames.CHAT_WINDOW,
        children=[content, conversation_list],
    )
    window = FakeControl(
        class_name=rules.ClassNames.STANDARD_FRAME,
        children=[stale_list_outside_chat, chat_window],
    )

    layout = ChatLocator().locate(window)

    assert layout.conversation_list.found
    assert layout.conversation_list.control is conversation_list
    assert layout.conversation_top_bar.found
    assert layout.chat_content.found
    assert layout.message_container.found
    assert layout.message_container.automation_id == rules.AutomationIds.CHAT_BUBBLE_WIDGET
    assert layout.input_area.found
    assert layout.footer_bar.found


def test_chat_locator_walks_complete_descendant_tree() -> None:
    message = FakeControl(automation_id=rules.AutomationIds.CHAT_BUBBLE_WIDGET)
    nested_content = FakeControl(
        automation_id=rules.AutomationIds.CHAT_CONTENT,
        children=[FakeControl(children=[message])],
    )
    chat_window = FakeControl(
        class_name=rules.ClassNames.CHAT_WINDOW,
        children=[FakeControl(children=[nested_content])],
    )

    layout = ChatLocator().locate(chat_window)

    assert layout.chat_content.found
    assert layout.message_container.found


def test_chat_locator_emits_debug_match_reasons() -> None:
    debug_messages: list[str] = []
    content = FakeControl(automation_id=rules.AutomationIds.CHAT_CONTENT)
    chat_window = FakeControl(
        class_name=rules.ClassNames.CHAT_WINDOW,
        children=[content],
    )

    ChatLocator(debug_logger=debug_messages.append).locate(chat_window)

    assert any("Checking ChatContent" in message for message in debug_messages)
    assert any("Matched ChatContent by AutomationId" in message for message in debug_messages)


def test_chat_locator_returns_missing_models_when_regions_are_absent() -> None:
    layout = ChatLocator().locate(FakeControl())

    assert not layout.chat_content.found
    assert not layout.message_container.found
    assert layout.message_container.child_count == 0
