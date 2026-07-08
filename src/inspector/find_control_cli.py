"""CLI for finding controls inside a discovered window."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
import typer

from automation.uia_client import AutomationError, UIAutomationClient
from automation.window_finder import WindowFinder, WindowQuery
from config.settings import SETTINGS
from inspector.formatters import error_panel
from inspector.search import SearchResult, search_tree
from utils.logging import configure_logging

app = typer.Typer(help="Search controls inside a discovered window.")


@app.command()
def main(
    window: str | None = typer.Option("DingTalk", "--window", "-w", help="Substring of the top-level window title."),
    process_name: str | None = typer.Option(None, "--process-name", "-p", help="Substring of the owning process name."),
    pid: int | None = typer.Option(None, "--pid", help="Owning process id."),
    control_type: str | None = typer.Option(None, "--type", help="ControlType / ControlTypeName substring."),
    automation_id: str | None = typer.Option(None, "--automation-id", "--id", help="AutomationId substring."),
    class_name: str | None = typer.Option(None, "--class", help="ClassName substring."),
    name: str | None = typer.Option(None, "--name", help="Name substring."),
    max_depth: int = typer.Option(SETTINGS.default_max_depth, "--max-depth", "-d", min=0),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
) -> None:
    """Print matching NodeId, Path, Depth, Parent, and Children for a window."""
    configure_logging(verbose=verbose)
    console = Console()
    try:
        if not any((control_type, automation_id, class_name, name)):
            raise AutomationError("Provide --type, --automation-id, --class, or --name to search controls.")
        client = UIAutomationClient()
        control = WindowFinder(client).find_one(WindowQuery(title=window, process_name=process_name, pid=pid))
        snapshot = client.snapshot(control, include_children=True, max_depth=max_depth)
        results = search_tree(
            snapshot.to_dict(),
            control_type=control_type,
            automation_id=automation_id,
            class_name=class_name,
            name=name,
        )
        _print_results(results, console)
    except AutomationError as exc:
        console.print(error_panel(str(exc)))
        raise typer.Exit(code=1) from exc


def _print_results(results: list[SearchResult], console: Console) -> None:
    table = Table(title=f"Matched Controls ({len(results)})", show_header=True)
    for column in ("NodeId", "Path", "Depth", "Parent", "Children"):
        table.add_column(column)
    for result in results:
        table.add_row(result.node_id, result.path, str(result.depth), result.parent, str(result.children))
    console.print(table)


if __name__ == "__main__":
    app()
