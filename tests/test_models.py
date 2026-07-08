"""Tests for serializable UI element models."""

from models.ui_element import BoundingRectangle, ElementSnapshot


def test_bounding_rectangle_dimensions_are_non_negative() -> None:
    rectangle = BoundingRectangle(left=10, top=20, right=5, bottom=25)

    assert rectangle.width == 0
    assert rectangle.height == 5


def test_element_snapshot_to_dict_contains_nested_children() -> None:
    child = ElementSnapshot(
        name="Child",
        automation_id="child-id",
        control_type="ButtonControl",
        class_name="Button",
        bounding_rectangle=BoundingRectangle(1, 2, 3, 4),
        runtime_id=[1, 2],
        parent="Window: Parent",
        child_count=0,
    )
    parent = ElementSnapshot(
        name="Parent",
        automation_id="parent-id",
        control_type="WindowControl",
        class_name="Chrome_WidgetWin_1",
        bounding_rectangle=BoundingRectangle(0, 0, 100, 100),
        runtime_id=[9],
        parent=None,
        child_count=1,
        children=[child],
    )

    data = parent.to_dict()

    assert data["name"] == "Parent"
    assert data["children"][0]["automation_id"] == "child-id"
