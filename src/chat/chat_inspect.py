"""CLI for inspecting located DingTalk chat layout regions."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer

from automation.uia_client import AutomationError, UIAutomationClient
from automation.window_finder import WindowFinder, WindowQuery
from chat.chat_locator import ChatLocator
from chat.models import ChatLayout, LocatedControl
from inspector.formatters import error_panel
from utils.logging import configure_logging

app = typer.Typer(help="Locate core regions in a DingTalk chat window.")


@app.command()
def main(
    window: str = typer.Option(..., "--window", "-w", help="Top-level window title substring."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging."),
    debug: bool = typer.Option(False, "--debug", help="Print locator traversal details."),
) -> None:
    """Print a non-invasive chat layout report for a matching window."""
    configure_logging(verbose=verbose)
    console = Console()
    try:
        finder = WindowFinder(UIAutomationClient())
        control = finder.find_one(WindowQuery(title=window))
        debug_logger = console.print if debug else None
        layout = ChatLocator(debug_logger=debug_logger).locate(control)
        print_layout(layout, console)
    except AutomationError as exc:
        console.print(error_panel(str(exc)))
        raise typer.Exit(code=1) from exc


def print_layout(layout: ChatLayout, console: Console) -> None:
    """Render chat layout metadata using Rich."""
    console.print("======== Chat Layout ========")
    for title, control in (
        ("Conversation List", layout.conversation_list),
        ("Conversation TopBar", layout.conversation_top_bar),
        ("Chat Content", layout.chat_content),
        ("Message Container", layout.message_container),
        ("Input Area", layout.input_area),
        ("Footer Bar", layout.footer_bar),
    ):
        console.print(_control_panel(title, control))
        console.print("--------------------")


def _control_panel(title: str, control: LocatedControl) -> Panel:
    status = "✓" if control.found else "✗"
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold")
    table.add_column()
    table.add_row("AutomationId", control.automation_id)
    table.add_row("ClassName", control.class_name)
    table.add_row("ControlType", control.control_type)
    table.add_row("BoundingRectangle", str(control.bounding_rectangle))
    table.add_row("Children", str(control.child_count))
    return Panel(table, title=f"{title}  {status}", expand=False)


if __name__ == "__main__":
    app()
