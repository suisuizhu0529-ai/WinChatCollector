"""Tests for window discovery query matching."""

import sys
import types

loguru = types.ModuleType("loguru")
loguru.logger = types.SimpleNamespace(warning=lambda *args, **kwargs: None, debug=lambda *args, **kwargs: None)
sys.modules.setdefault("loguru", loguru)

from automation.window_finder import WindowFinder, WindowQuery


class FakeRectangle:
    left = 0
    top = 0
    right = 10
    bottom = 10


class FakeControl:
    def __init__(self, name: str, process_id: int) -> None:
        self.Name = name
        self.ClassName = "WindowClass"
        self.ProcessId = process_id
        self.NativeWindowHandle = process_id * 10
        self.BoundingRectangle = FakeRectangle()


class FakeClient:
    def __init__(self) -> None:
        self.windows = [FakeControl("DingTalk Main", 42), FakeControl("Other", 7)]

    def desktop_control(self) -> object:
        return object()

    def children(self, control: object) -> list[FakeControl]:
        return self.windows

    def safe_attr(self, control: FakeControl, attr_name: str) -> str:
        return str(getattr(control, attr_name, ""))

    def process_id(self, control: FakeControl) -> int | None:
        return control.ProcessId

    def process_name(self, control: FakeControl) -> str:
        return "DingTalk.exe" if control.ProcessId == 42 else "Other.exe"

    def window_handle(self, control: FakeControl) -> int:
        return control.NativeWindowHandle

    def bounding_rectangle(self, control: FakeControl):
        from models.ui_element import BoundingRectangle

        return BoundingRectangle(0, 0, 10, 10)


def test_window_finder_matches_title_process_name_and_pid() -> None:
    finder = WindowFinder(FakeClient())  # type: ignore[arg-type]

    assert finder.find_one(WindowQuery(title="ding")).Name == "DingTalk Main"
    assert finder.find_one(WindowQuery(process_name="DingTalk")).ProcessId == 42
    assert finder.find_one(WindowQuery(pid=42)).Name == "DingTalk Main"


def test_window_finder_list_windows_supports_title_filter() -> None:
    finder = WindowFinder(FakeClient())  # type: ignore[arg-type]

    windows = finder.list_windows(title="Ding")

    assert len(windows) == 1
    assert windows[0][1].title == "DingTalk Main"
