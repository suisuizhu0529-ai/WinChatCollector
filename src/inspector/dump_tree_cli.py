"""CLI for dumping a UI Automation tree from a discovered window."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from rich.console import Console
import typer

from automation.uia_client import AutomationError, UIAutomationClient
from automation.window_finder import WindowFinder, WindowQuery
from config.settings import SETTINGS
from inspector.formatters import error_panel, write_text_tree
from inspector.serialization import write_snapshot_json
from utils.logging import configure_logging

app = typer.Typer(help="Dump a UI Automation tree from a window without using the mouse.")


@app.command()
def main(
    window: str | None = typer.Option(None, "--window", "-w", help="Substring of the top-level window title."),
    process_name: str | None = typer.Option(None, "--process-name", "-p", help="Substring of the owning process name."),
    pid: int | None = typer.Option(None, "--pid", help="Owning process id."),
    max_depth: int = typer.Option(
        SETTINGS.default_max_depth,
        "--max-depth",
        "-d",
        min=0,
        help="Maximum child depth to export.",
    ),
    output_dir: Path = typer.Option(
        SETTINGS.default_output_dir,
        "--output-dir",
        "-o",
        help="Directory that receives tree.txt and tree.json.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
) -> None:
    """Export ``tree.txt`` and ``tree.json`` for a discovered window subtree."""
    configure_logging(verbose=verbose)
    console = Console()
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        client = UIAutomationClient()
        control = WindowFinder(client).find_one(WindowQuery(title=window, process_name=process_name, pid=pid))
        snapshot = client.snapshot(control, include_children=True, max_depth=max_depth)
        tree_path = output_dir / "tree.txt"
        json_path = output_dir / "tree.json"
        write_text_tree(snapshot, tree_path)
        write_snapshot_json(snapshot, json_path)
        logger.info("Wrote {}", tree_path)
        logger.info("Wrote {}", json_path)
        console.print(f"[green]Exported:[/green] {tree_path} and {json_path}")
    except AutomationError as exc:
        console.print(error_panel(str(exc)))
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
