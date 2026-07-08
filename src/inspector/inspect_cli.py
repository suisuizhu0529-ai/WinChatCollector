"""CLI for inspecting the UI Automation control under the cursor."""

from __future__ import annotations

from rich.console import Console
import typer

from automation.uia_client import AutomationError, UIAutomationClient
from inspector.formatters import error_panel, print_snapshot
from utils.logging import configure_logging

app = typer.Typer(help="Inspect the Windows UI Automation control under the mouse cursor.")


@app.command()
def main(
    delay: float = typer.Option(0.2, "--delay", help="Delay before reading cursor position."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
) -> None:
    """Print metadata for the current control under the mouse cursor."""
    configure_logging(verbose=verbose)
    console = Console()
    try:
        client = UIAutomationClient()
        control = client.wait_for_cursor_control(delay_seconds=delay)
        print_snapshot(client.snapshot(control), console=console)
    except AutomationError as exc:
        console.print(error_panel(str(exc)))
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
