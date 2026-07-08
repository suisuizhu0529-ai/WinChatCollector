"""Default settings for inspector tools."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InspectorSettings:
    """Runtime settings shared by inspector commands."""

    poll_interval_seconds: float = 0.5
    default_max_depth: int = 6
    default_output_dir: Path = Path(".")


SETTINGS = InspectorSettings()
