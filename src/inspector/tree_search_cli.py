"""CLI for searching an exported UI Automation tree JSON file."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table
import typer

from inspector.search import SearchResult, load_tree, search_tree

app = typer.Typer(help="Search a dumped tree.json file.")


@app.command()
def main(tree_json: Path = typer.Argument(...), term: str = typer.Argument(...)) -> None:
    """Search ControlType, AutomationId, ClassName, and Name for TERM."""
    results = search_tree(load_tree(tree_json), term=term)
    _print_results(results, Console())


def _print_results(results: list[SearchResult], console: Console) -> None:
    table = Table(title=f"Tree Search Results ({len(results)})", show_header=True)
    for column in ("NodeId", "Path", "Depth", "Parent", "Children"):
        table.add_column(column)
    for result in results:
        table.add_row(result.node_id, result.path, str(result.depth), result.parent, str(result.children))
    console.print(table)


if __name__ == "__main__":
    app()
