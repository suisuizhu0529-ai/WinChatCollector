"""Data models for Windows UI Automation inspection."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class BoundingRectangle:
    """Serializable UI Automation bounding rectangle."""

    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        """Return rectangle width."""
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        """Return rectangle height."""
        return max(0, self.bottom - self.top)


@dataclass(frozen=True)
class ElementSnapshot:
    """Serializable snapshot of a UI Automation control."""

    name: str
    automation_id: str
    control_type: str
    class_name: str
    bounding_rectangle: BoundingRectangle
    runtime_id: list[int]
    parent: str | None
    child_count: int
    children: list["ElementSnapshot"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert the snapshot and nested children to plain Python objects."""
        return asdict(self)
