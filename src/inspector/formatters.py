"""Formatting helpers for inspector output."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from models.ui_element import ElementSnapshot


def _require_rich() -> tuple[Any, Any, Any, Any]:
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.tree import Tree
    except ImportError as exc:
        raise RuntimeError("rich is required for formatted inspector output.") from exc
    return Console, Panel, Table, Tree


def snapshot_table(snapshot: ElementSnapshot) -> Any:
    """Create a Rich table for a single element snapshot."""
    _, _, Table, _ = _require_rich()
    table = Table(title="Current UI Automation Control", show_header=True)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_row("Name", snapshot.name)
    table.add_row("AutomationId", snapshot.automation_id)
    table.add_row("ControlType", snapshot.control_type)
    table.add_row("ClassName", snapshot.class_name)
    table.add_row("BoundingRectangle", str(asdict(snapshot.bounding_rectangle)))
    table.add_row("RuntimeId", str(snapshot.runtime_id))
    table.add_row("Parent", snapshot.parent or "<none>")
    table.add_row("ChildCount", str(snapshot.child_count))
    return table


def print_snapshot(snapshot: ElementSnapshot, console: Any | None = None) -> None:
    """Print a snapshot using Rich."""
    Console, _, _, _ = _require_rich()
    target = console or Console()
    target.print(snapshot_table(snapshot))


def render_tree(snapshot: ElementSnapshot) -> str:
    """Render a snapshot tree to plain text."""
    lines: list[str] = []

    def visit(node: ElementSnapshot, depth: int) -> None:
        indent = "  " * depth
        label = (
            f"{node.control_type} name={node.name!r} "
            f"automation_id={node.automation_id!r} class={node.class_name!r} "
            f"children={node.child_count}"
        )
        lines.append(f"{indent}{label}")
        for child in node.children:
            visit(child, depth + 1)

    visit(snapshot, 0)
    return "\n".join(lines) + "\n"


def rich_tree(snapshot: ElementSnapshot) -> Any:
    """Build a Rich tree from a snapshot."""
    _, _, _, Tree = _require_rich()
    root = Tree(_node_label(snapshot))

    def add(parent: Any, node: ElementSnapshot) -> None:
        for child in node.children:
            branch = parent.add(_node_label(child))
            add(branch, child)

    add(root, snapshot)
    return root


def _node_label(snapshot: ElementSnapshot) -> str:
    return (
        f"[bold]{snapshot.control_type or 'Unknown'}[/bold] "
        f"{snapshot.name!r} [dim]{snapshot.automation_id}[/dim]"
    )


def write_text_tree(snapshot: ElementSnapshot, output_path: Path) -> None:
    """Write a plain-text tree dump."""
    output_path.write_text(render_tree(snapshot), encoding="utf-8")


def error_panel(message: str) -> Any:
    """Create a consistent Rich error panel."""
    _, Panel, _, _ = _require_rich()
    return Panel(message, title="Inspector Error", border_style="red")
