"""Search helpers for serialized UI Automation trees."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SearchResult:
    """A matching node and its location metadata."""

    node: dict[str, Any]
    node_id: str
    path: str
    depth: int
    parent: str
    children: int


def load_tree(path: Path) -> dict[str, Any]:
    """Load a JSON tree produced by dump_tree.py."""
    return json.loads(path.read_text(encoding="utf-8"))


def search_tree(tree: dict[str, Any], term: str | None = None, **criteria: str | None) -> list[SearchResult]:
    """Search a tree by free text or explicit node fields."""
    results: list[SearchResult] = []
    wanted = {key: value for key, value in criteria.items() if value}

    def visit(node: dict[str, Any], depth: int, indexes: list[int], names: list[str]) -> None:
        if _matches(node, term, wanted):
            results.append(
                SearchResult(
                    node=node,
                    node_id=str(node.get("node_id") or _fallback_node_id(indexes)),
                    path=str(node.get("path") or " / ".join(names)),
                    depth=int(node.get("depth", depth)),
                    parent=str(node.get("parent") or "<none>"),
                    children=int(node.get("child_count", len(node.get("children", [])))),
                )
            )
        for index, child in enumerate(node.get("children", [])):
            label = _label(child)
            visit(child, depth + 1, [*indexes, index], [*names, label])

    visit(tree, 0, [0], [_label(tree)])
    return results


def _matches(node: dict[str, Any], term: str | None, criteria: dict[str, str]) -> bool:
    if term:
        haystack = " ".join(str(node.get(field, "")) for field in ("control_type", "automation_id", "class_name", "name"))
        if term.lower() not in haystack.lower():
            return False
    for field, value in criteria.items():
        if value.lower() not in str(node.get(field, "")).lower():
            return False
    return True


def _label(node: dict[str, Any]) -> str:
    return str(node.get("name") or node.get("automation_id") or node.get("class_name") or node.get("control_type") or "<unnamed>")


def _fallback_node_id(indexes: list[int]) -> str:
    return ".".join(str(index) for index in indexes)
