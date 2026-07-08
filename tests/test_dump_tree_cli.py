"""Tests for dump_tree window-discovery behavior."""

from pathlib import Path

from inspector import dump_tree_cli


class FakeRectangle:
    left = 0
    top = 0
    right = 100
    bottom = 80


class FakeControl:
    def __init__(self, name: str, class_name: str = "WindowClass") -> None:
        self.Name = name
        self.AutomationId = ""
        self.ControlTypeName = "WindowControl"
        self.ClassName = class_name
        self.ProcessId = 100 if name == "DingTalk" else 200
        self.NativeWindowHandle = 1000 if name == "DingTalk" else 2000
        self.BoundingRectangle = FakeRectangle()

    def GetRuntimeId(self) -> list[int]:
        return [self.NativeWindowHandle]

    def GetParentControl(self) -> None:
        return None

    def GetChildren(self) -> list[object]:
        return []


class FakeClient:
    def __init__(self) -> None:
        self.cursor_used = False
        self.windows = [FakeControl("CMD", "ConsoleWindowClass"), FakeControl("DingTalk", "Chrome_WidgetWin_1")]

    def desktop_control(self) -> object:
        return object()

    def children(self, control: object) -> list[FakeControl]:
        return self.windows

    def control_from_cursor(self) -> object:
        self.cursor_used = True
        raise AssertionError("dump_tree must not use cursor lookup")

    def wait_for_cursor_control(self, delay_seconds: float = 0.2) -> object:
        self.cursor_used = True
        raise AssertionError("dump_tree must not use cursor lookup")

    def process_id(self, control: FakeControl) -> int:
        return control.ProcessId

    def process_name(self, control: FakeControl) -> str:
        return "DingTalk.exe" if control.Name == "DingTalk" else "cmd.exe"

    def safe_attr(self, control: FakeControl, attr_name: str) -> str:
        return str(getattr(control, attr_name, ""))

    def snapshot(self, control: FakeControl, include_children: bool = False, max_depth: int = 0):
        assert control.Name == "DingTalk"
        from models.ui_element import BoundingRectangle, ElementSnapshot

        return ElementSnapshot(
            name=control.Name,
            automation_id="",
            control_type=control.ControlTypeName,
            class_name=control.ClassName,
            bounding_rectangle=BoundingRectangle(0, 0, 100, 80),
            runtime_id=[control.NativeWindowHandle],
            parent=None,
            child_count=0,
            node_id="0",
            path="WindowControl:DingTalk",
            depth=0,
        )


def test_dump_tree_window_option_is_used_instead_of_cursor(monkeypatch, tmp_path: Path) -> None:
    fake_client = FakeClient()
    monkeypatch.setattr(dump_tree_cli, "UIAutomationClient", lambda: fake_client)

    dump_tree_cli.main(window="DingTalk", process_name=None, pid=None, max_depth=1, output_dir=tmp_path, verbose=False)

    assert not fake_client.cursor_used
    assert 'DingTalk' in (tmp_path / "tree.json").read_text(encoding="utf-8")
    assert 'ConsoleWindowClass' not in (tmp_path / "tree.json").read_text(encoding="utf-8")
