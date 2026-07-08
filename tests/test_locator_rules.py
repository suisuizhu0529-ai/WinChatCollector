"""Tests for centralized chat locator rules."""

from chat import locator_rules as rules


class FakeControl:
    def __init__(
        self,
        automation_id: str = "",
        class_name: str = "",
        control_type: str = "",
    ) -> None:
        self.AutomationId = automation_id
        self.ClassName = class_name
        self.ControlTypeName = control_type


def test_control_rule_matches_automation_id() -> None:
    control = FakeControl(automation_id=rules.AutomationIds.CONVERSATION_LIST)

    assert rules.matches_any(control, rules.CONVERSATION_LIST_RULES)


def test_control_rule_rejects_non_matching_populated_fields() -> None:
    rule = rules.ControlRule(
        automation_ids=(rules.AutomationIds.CONVERSATION_LIST,),
        class_names=(rules.ClassNames.CONVERSATION_LIST,),
    )
    control = FakeControl(
        automation_id=rules.AutomationIds.CONVERSATION_LIST,
        class_name=rules.ClassNames.CHAT_CONTENT,
    )

    assert not rule.matches(control)
