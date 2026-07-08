"""Windows UI Automation client abstraction.

This module centralizes direct access to third-party Windows automation
libraries so command modules remain testable on non-Windows CI hosts.
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from typing import Any, Protocol

from loguru import logger

from models.ui_element import BoundingRectangle, ElementSnapshot


class AutomationError(RuntimeError):
    """Raised when Windows UI Automation cannot be queried."""


class ControlProtocol(Protocol):
    """Subset of uiautomation.Control used by the inspector."""

    Name: str
    AutomationId: str
    ControlTypeName: str
    ClassName: str
    BoundingRectangle: Any

    def GetRuntimeId(self) -> list[int]: ...

    def GetParentControl(self) -> Any: ...

    def GetChildren(self) -> list[Any]: ...


class UIAutomationClient:
    """Small adapter around ``uiautomation`` and ``pywinauto``."""

    def __init__(self) -> None:
        self._automation = self._load_uiautomation()
        self._pywinauto_loaded = self._load_pywinauto()

    @staticmethod
    def _load_uiautomation() -> Any:
        try:
            import uiautomation as auto  # type: ignore[import-not-found]
        except ImportError as exc:
            raise AutomationError(
                "uiautomation is required and only works on supported Windows environments."
            ) from exc
        return auto

    @staticmethod
    def _load_pywinauto() -> bool:
        try:
            import pywinauto  # noqa: F401  # type: ignore[import-not-found]
        except ImportError:
            logger.warning("pywinauto is not installed; window backend integration is limited.")
            return False
        return True

    def desktop_control(self) -> Any:
        """Return the desktop root control."""
        try:
            return self._automation.GetRootControl()
        except Exception as exc:  # pragma: no cover - COM/library boundary
            raise AutomationError("Failed to read the desktop root control.") from exc

    def children(self, control: Any) -> list[Any]:
        """Return non-null child controls for a UI Automation control."""
        children = self._safe_call(control, "GetChildren") or []
        return list(self._iter_controls(children))

    def process_id(self, control: Any) -> int | None:
        """Return the owning process id when UIA exposes it."""
        value = self._safe_attr(control, "ProcessId")
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def process_name(self, control: Any) -> str:
        """Return the executable name for the owning process when available."""
        pid = self.process_id(control)
        if pid is None:
            return ""
        try:
            import psutil  # type: ignore[import-not-found]

            return str(psutil.Process(pid).name())
        except Exception:  # pragma: no cover - optional dependency / OS boundary
            return ""

    def safe_attr(self, control: Any, attr_name: str) -> str:
        """Safely read a UIA attribute as text."""
        return self._safe_attr(control, attr_name)

    def control_from_cursor(self) -> Any:
        """Return the UI Automation control currently under the mouse cursor."""
        try:
            return self._automation.ControlFromCursor()
        except Exception as exc:  # pragma: no cover - COM/library boundary
            raise AutomationError("Failed to read control under cursor.") from exc

    def wait_for_cursor_control(self, delay_seconds: float = 0.2) -> Any:
        """Pause briefly, then return the control under the mouse cursor."""
        time.sleep(delay_seconds)
        return self.control_from_cursor()

    def snapshot(self, control: Any, include_children: bool = False, max_depth: int = 0) -> ElementSnapshot:
        """Build an :class:`ElementSnapshot` from a UI Automation control."""
        return self._snapshot(
            control,
            include_children=include_children,
            max_depth=max_depth,
            depth=0,
            node_id="0",
            path_parts=[],
        )

    def _snapshot(
        self,
        control: Any,
        *,
        include_children: bool,
        max_depth: int,
        depth: int,
        node_id: str,
        path_parts: list[str],
    ) -> ElementSnapshot:
        parent = self._safe_call(control, "GetParentControl")
        children = self._safe_call(control, "GetChildren") or []
        current_label = self._node_label(control)
        current_path_parts = [*path_parts, current_label]
        child_snapshots: list[ElementSnapshot] = []

        if include_children and depth < max_depth:
            for index, child in enumerate(self._iter_controls(children)):
                child_snapshots.append(
                    self._snapshot(
                        child,
                        include_children=True,
                        max_depth=max_depth,
                        depth=depth + 1,
                        node_id=f"{node_id}.{index}",
                        path_parts=current_path_parts,
                    )
                )

        return ElementSnapshot(
            name=self._safe_attr(control, "Name"),
            automation_id=self._safe_attr(control, "AutomationId"),
            control_type=self._safe_attr(control, "ControlTypeName"),
            class_name=self._safe_attr(control, "ClassName"),
            bounding_rectangle=self._rectangle_from_control(control),
            runtime_id=self._runtime_id(control),
            parent=self._describe_parent(parent),
            child_count=len(list(self._iter_controls(children))),
            node_id=node_id,
            path=" / ".join(current_path_parts),
            depth=depth,
            children=child_snapshots,
        )

    @staticmethod
    def _iter_controls(children: Iterable[Any]) -> Iterable[Any]:
        return (child for child in children if child is not None)

    @staticmethod
    def _safe_attr(control: Any, attr_name: str) -> str:
        try:
            value = getattr(control, attr_name, "")
        except Exception:  # pragma: no cover - COM/library boundary
            logger.debug("Failed to read UIA attribute: {}", attr_name)
            return ""
        return "" if value is None else str(value)

    @staticmethod
    def _safe_call(control: Any, method_name: str) -> Any:
        try:
            method = getattr(control, method_name)
            return method()
        except Exception:  # pragma: no cover - COM/library boundary
            logger.debug("Failed to call UIA method: {}", method_name)
            return None

    def _rectangle_from_control(self, control: Any) -> BoundingRectangle:
        rectangle = getattr(control, "BoundingRectangle", None)
        return BoundingRectangle(
            left=self._rect_value(rectangle, "left", "Left"),
            top=self._rect_value(rectangle, "top", "Top"),
            right=self._rect_value(rectangle, "right", "Right"),
            bottom=self._rect_value(rectangle, "bottom", "Bottom"),
        )

    @staticmethod
    def _rect_value(rectangle: Any, *names: str) -> int:
        for name in names:
            if hasattr(rectangle, name):
                try:
                    return int(getattr(rectangle, name))
                except (TypeError, ValueError):
                    return 0
        return 0

    def _runtime_id(self, control: Any) -> list[int]:
        runtime_id = self._safe_call(control, "GetRuntimeId") or []
        try:
            return [int(item) for item in runtime_id]
        except (TypeError, ValueError):
            return []

    def _node_label(self, control: Any) -> str:
        name = self._safe_attr(control, "Name") or "<unnamed>"
        control_type = self._safe_attr(control, "ControlTypeName") or "Unknown"
        automation_id = self._safe_attr(control, "AutomationId")
        return f"{control_type}:{name}#{automation_id}" if automation_id else f"{control_type}:{name}"

    def _describe_parent(self, parent: Any) -> str | None:
        if parent is None:
            return None
        name = self._safe_attr(parent, "Name") or "<unnamed>"
        control_type = self._safe_attr(parent, "ControlTypeName") or "Unknown"
        automation_id = self._safe_attr(parent, "AutomationId")
        return f"{control_type}: {name} ({automation_id})" if automation_id else f"{control_type}: {name}"
