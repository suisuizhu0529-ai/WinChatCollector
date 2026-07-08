"""Tests for window discovery query matching."""

import sys
import types

loguru = types.ModuleType("loguru")
loguru.logger = types.SimpleNamespace(
    warning=lambda *args, **kwargs: None,
    debug=lambda *args, **kwargs: None,
)
sys.modules.setdefault("loguru", loguru)

from automation.window_finder import WindowFinder, WindowQuery


class FakeRectangle:
    left = 0
    top = 0
    right = 10
    bottom = 10


class FakeControl:
    def __init__(
        self,
        name: str,
        process_id: int,
        class_name: str = "WindowClass",
        process_name: str | None = None,
    ) -> None:
        self.Name = name
        self.ClassName = class_name
        self.ProcessId = process_id
        self.ProcessName = process_name or f"Process{process_id}.exe"
        self.NativeWindowHandle = process_id * 10
        self.BoundingRectangle = FakeRectangle()


class FakeClient:
    def __init__(self, windows: list[FakeControl] | None = None) -> None:
        self.windows = windows or [
            FakeControl("DingTalk Main", 42, process_name="DingTalk.exe"),
            FakeControl("Other", 7, process_name="Other.exe"),
        ]

    def desktop_control(self) -> object:
        return object()

    def children(self, control: object) -> list[FakeControl]:
        return self.windows

    def safe_attr(self, control: FakeControl, attr_name: str) -> str:
        return str(getattr(control, attr_name, ""))

    def process_id(self, control: FakeControl) -> int | None:
        return control.ProcessId

    def process_name(self, control: FakeControl) -> str:
        return control.ProcessName

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
    assert windows[0][1].process_name == "DingTalk.exe"


def test_window_finder_prefers_dingtalk_class_for_title_matches() -> None:
    chrome = FakeControl(
        "钉钉 - Google Chrome",
        100,
        class_name="Chrome_WidgetWin_1",
        process_name="chrome.exe",
    )
    dingtalk = FakeControl(
        "钉钉",
        42,
        class_name="StandardFrame_DingTalk",
        process_name="OtherHost.exe",
    )
    finder = WindowFinder(FakeClient([chrome, dingtalk]))  # type: ignore[arg-type]

    assert finder.find_one(WindowQuery(title="钉钉")) is dingtalk


def test_window_finder_prefers_dingtalk_process_after_class_tie() -> None:
    helper = FakeControl(
        "钉钉 helper",
        101,
        class_name="StandardFrame_DingTalk",
        process_name="helper.exe",
    )
    dingtalk = FakeControl(
        "钉钉",
        42,
        class_name="StandardFrame_DingTalk",
        process_name="DingTalk.exe",
    )
    finder = WindowFinder(FakeClient([helper, dingtalk]))  # type: ignore[arg-type]

    assert finder.find_one(WindowQuery(title="钉钉")) is dingtalk


def test_window_finder_falls_back_to_title_order_when_priority_ties() -> None:
    first = FakeControl("钉钉 first", 1, process_name="chrome.exe")
    second = FakeControl("钉钉 second", 2, process_name="msedge.exe")
    finder = WindowFinder(FakeClient([first, second]))  # type: ignore[arg-type]

    assert finder.find_one(WindowQuery(title="钉钉")) is first
