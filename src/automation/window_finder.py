"""Window discovery helpers that do not depend on mouse position."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import logging

from automation.uia_client import AutomationError, UIAutomationClient
from models.ui_element import BoundingRectangle

logger = logging.getLogger(__name__)

DINGTALK_WINDOW_CLASS = "StandardFrame_DingTalk"
DINGTALK_PROCESS_NAME = "DingTalk.exe"


@dataclass(frozen=True)
class WindowQuery:
    """Criteria used to locate a top-level window."""

    title: str | None = None
    process_name: str | None = None
    pid: int | None = None

    def validate(self) -> None:
        if not any((self.title, self.process_name, self.pid is not None)):
            raise AutomationError("Provide --window, --process-name, or --pid to locate a window.")


@dataclass(frozen=True)
class WindowInfo:
    """Display metadata for a top-level window."""

    title: str
    class_name: str
    process_name: str
    pid: int | None
    handle: int | None
    bounding_rectangle: BoundingRectangle


class WindowFinder:
    """Find top-level UI Automation windows by title, process name, or PID."""

    def __init__(self, client: UIAutomationClient | None = None) -> None:
        self.client = client or UIAutomationClient()

    def top_level_windows(self) -> list[Any]:
        """Return direct desktop children that represent top-level windows."""
        desktop = self.client.desktop_control()
        return self.client.children(desktop)

    def list_windows(self, title: str | None = None) -> list[tuple[Any, WindowInfo]]:
        """Return top-level windows and display metadata, optionally filtered by title."""
        windows: list[tuple[Any, WindowInfo]] = []
        for window in self.top_level_windows():
            info = self.describe(window)
            if title and title.lower() not in info.title.lower():
                continue
            windows.append((window, info))
        return windows

    def describe(self, control: Any) -> WindowInfo:
        """Return display metadata for a top-level window control."""
        return WindowInfo(
            title=self.client.safe_attr(control, "Name"),
            class_name=self.client.safe_attr(control, "ClassName"),
            process_name=self.client.process_name(control),
            pid=self.client.process_id(control),
            handle=self.client.window_handle(control),
            bounding_rectangle=self.client.bounding_rectangle(control),
        )

    def find_one(self, query: WindowQuery) -> Any:
        """Return the first matching top-level window for the query."""
        matches = self.find_all(query)
        if not matches:
            raise AutomationError(f"No top-level window matched {query}.")
        selected = self._select_best_match(matches, query)
        if len(matches) > 1:
            logger.warning(
                "%s windows matched %s; selected %s.",
                len(matches),
                query,
                self.describe(selected),
            )
        return selected

    def find_all(self, query: WindowQuery) -> list[Any]:
        """Return all matching top-level windows for the query."""
        query.validate()
        return [window for window in self.top_level_windows() if self._matches(window, query)]

    def _select_best_match(self, matches: list[Any], query: WindowQuery) -> Any:
        """Choose the most likely DingTalk window while preserving fallback behavior."""
        if not query.title:
            return matches[0]

        dingtalk_class_matches = [
            window
            for window in matches
            if self.client.safe_attr(window, "ClassName") == DINGTALK_WINDOW_CLASS
        ]
        if len(dingtalk_class_matches) == 1:
            return dingtalk_class_matches[0]
        candidates = dingtalk_class_matches or matches

        dingtalk_process_matches = [
            window
            for window in candidates
            if self.client.process_name(window).lower() == DINGTALK_PROCESS_NAME.lower()
        ]
        if len(dingtalk_process_matches) == 1:
            return dingtalk_process_matches[0]
        if dingtalk_process_matches:
            return dingtalk_process_matches[0]
        return candidates[0]

    def _matches(self, control: Any, query: WindowQuery) -> bool:
        if query.title:
            title = self.client.safe_attr(control, "Name").lower()
            if query.title.lower() not in title:
                return False
        if query.pid is not None and self.client.process_id(control) != query.pid:
            return False
        if query.process_name:
            process_name = self.client.process_name(control)
            if query.process_name.lower() not in process_name.lower():
                return False
        return True
