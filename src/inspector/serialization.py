"""Serialization helpers for inspector snapshots."""

from __future__ import annotations

import json
from pathlib import Path

from models.ui_element import ElementSnapshot


def write_snapshot_json(snapshot: ElementSnapshot, output_path: Path) -> None:
    """Write a snapshot tree to JSON."""
    output_path.write_text(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
