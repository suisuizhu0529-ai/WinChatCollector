"""Tests for window discovery query matching."""

import sys
import types

loguru = types.ModuleType("loguru")
loguru.logger = types.SimpleNamespace(warning=lambda *args, **kwargs: None, debug=lambda *args, **kwargs: None)
sys.modules.setdefault("loguru", loguru)

from automation.window_finder import WindowFinder, WindowQuery


class FakeControl:
    def __init__(self, name: str, process_id: int) -> None:
        self.Name = name
        self.ProcessId = process_id


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


def test_window_finder_matches_title_process_name_and_pid() -> None:
    finder = WindowFinder(FakeClient())  # type: ignore[arg-type]

    assert finder.find_one(WindowQuery(title="ding")).Name == "DingTalk Main"
    assert finder.find_one(WindowQuery(process_name="DingTalk")).ProcessId == 42
    assert finder.find_one(WindowQuery(pid=42)).Name == "DingTalk Main"
