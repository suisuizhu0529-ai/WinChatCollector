"""Rich live inspector for the UI Automation control under the cursor."""

from __future__ import annotations

from rich.console import Console
from rich.live import Live
import typer

from automation.uia_client import AutomationError, UIAutomationClient
from config.settings import SETTINGS
from inspector.formatters import error_panel, snapshot_table
from utils.logging import configure_logging

app = typer.Typer(help="Live Rich UI Automation inspector for the mouse cursor.")


@app.command()
def main(
    interval: float = typer.Option(
        SETTINGS.poll_interval_seconds,
        "--interval",
        "-i",
        min=0.1,
        help="Refresh interval in seconds.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
) -> None:
    """Continuously refresh metadata for the control under the cursor."""
    configure_logging(verbose=verbose)
    console = Console()
    try:
        client = UIAutomationClient()
        with Live(console=console, refresh_per_second=max(1, int(1 / interval))) as live:
            while True:
                control = client.control_from_cursor()
                live.update(snapshot_table(client.snapshot(control)))
    except KeyboardInterrupt:
        console.print("[yellow]Stopped live inspector.[/yellow]")
    except AutomationError as exc:
        console.print(error_panel(str(exc)))
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
