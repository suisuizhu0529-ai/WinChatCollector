"""Tests for UI tree search helpers."""

from inspector.search import search_tree


def test_search_tree_returns_location_metadata() -> None:
    tree = {
        "name": "DingTalk",
        "automation_id": "root",
        "control_type": "WindowControl",
        "class_name": "Chrome_WidgetWin_1",
        "parent": None,
        "child_count": 1,
        "node_id": "0",
        "path": "WindowControl:DingTalk#root",
        "depth": 0,
        "children": [
            {
                "name": "convlist",
                "automation_id": "",
                "control_type": "ListControl",
                "class_name": "ChatBubbleWidget",
                "parent": "Window: DingTalk",
                "child_count": 0,
                "node_id": "0.0",
                "path": "WindowControl:DingTalk#root / ListControl:convlist",
                "depth": 1,
                "children": [],
            }
        ],
    }

    results = search_tree(tree, class_name="ChatBubble")

    assert len(results) == 1
    assert results[0].node_id == "0.0"
    assert results[0].depth == 1
    assert results[0].children == 0


def test_search_tree_free_text_checks_identity_fields() -> None:
    tree = {
        "name": "DingTalk",
        "automation_id": "root",
        "control_type": "WindowControl",
        "class_name": "Chrome_WidgetWin_1",
        "parent": None,
        "child_count": 0,
        "children": [],
    }

    assert search_tree(tree, term="Chrome_WidgetWin_1")


def test_search_tree_can_filter_by_control_type() -> None:
    tree = {
        "name": "DingTalk",
        "automation_id": "root",
        "control_type": "WindowControl",
        "class_name": "Chrome_WidgetWin_1",
        "parent": None,
        "child_count": 1,
        "children": [
            {
                "name": "messages",
                "automation_id": "",
                "control_type": "ListControl",
                "class_name": "",
                "parent": "Window: DingTalk",
                "child_count": 0,
                "children": [],
            }
        ],
    }

    assert search_tree(tree, control_type="List")
