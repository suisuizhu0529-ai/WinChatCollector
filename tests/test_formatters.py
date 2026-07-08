"""Tests for inspector formatting helpers."""

from inspector.formatters import render_tree
from models.ui_element import BoundingRectangle, ElementSnapshot


def test_render_tree_includes_control_identity() -> None:
    snapshot = ElementSnapshot(
        name="Send",
        automation_id="send-button",
        control_type="ButtonControl",
        class_name="Button",
        bounding_rectangle=BoundingRectangle(0, 0, 10, 10),
        runtime_id=[1],
        parent="Window: DingTalk",
        child_count=0,
    )

    rendered = render_tree(snapshot)

    assert "ButtonControl" in rendered
    assert "send-button" in rendered
    assert "children=0" in rendered
