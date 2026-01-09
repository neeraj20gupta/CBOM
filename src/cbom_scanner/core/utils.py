"""Utility helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Optional, TYPE_CHECKING

import importlib
import importlib.util


if TYPE_CHECKING:  # pragma: no cover
    from tree_sitter import Node, Parser


@dataclass(frozen=True)
class CallSite:
    function: str
    args: List[str]
    line: int
    column: int
    snippet: str
    function_context: Optional[str]


def _load_tree_sitter():
    if importlib.util.find_spec("tree_sitter") is None or importlib.util.find_spec(
        "tree_sitter_languages"
    ) is None:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "tree-sitter is required for this scanner. "
            "Install tree_sitter and tree_sitter_languages."
        )
    ts_module = importlib.import_module("tree_sitter")
    tsl_module = importlib.import_module("tree_sitter_languages")
    return ts_module, tsl_module


def _get_language(name: str):
    _, tsl_module = _load_tree_sitter()
    return tsl_module.get_language(name)


def _extract_text(source: bytes, node: "Node") -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _string_literal(value: str) -> str:
    value = value.strip()
    if value.startswith(("'", '"', "`")) and value.endswith(("'", '"', "`")):
        return value[1:-1]
    return value


def _collect_args(source: bytes, args_node: "Node") -> List[str]:
    args: List[str] = []
    for child in args_node.named_children:
        text = _extract_text(source, child).strip()
        if text:
            args.append(_string_literal(text))
    return args


def _find_function_context(node: "Node") -> Optional[str]:
    if node is None:
        return None
    current = node
    while current is not None:
        if "name" in current.field_names:
            name_node = current.child_by_field_name("name")
            if name_node is not None:
                return name_node.text.decode("utf-8", errors="replace")
        current = current.parent
    return None


def collect_call_sites(
    source_text: str,
    language_name: str,
    call_node_type: str = "call_expression",
) -> Iterator[CallSite]:
    ts_module, _ = _load_tree_sitter()
    parser = ts_module.Parser()
    parser.set_language(_get_language(language_name))
    source = source_text.encode("utf-8")
    tree = parser.parse(source)
    root = tree.root_node
    stack: List[Node] = [root]
    lines = source_text.splitlines()
    while stack:
        node = stack.pop()
        if node.type == call_node_type:
            function_node = node.child_by_field_name("function")
            args_node = (
                node.child_by_field_name("arguments")
                or node.child_by_field_name("argument_list")
            )
            if function_node is None or args_node is None:
                stack.extend(node.children)
                continue
            function_text = _extract_text(source, function_node)
            args = _collect_args(source, args_node)
            line, column = node.start_point
            snippet = lines[line].rstrip() if line < len(lines) else ""
            yield CallSite(
                function=function_text,
                args=args,
                line=line + 1,
                column=column + 1,
                snippet=snippet,
                function_context=_find_function_context(node),
            )
        stack.extend(node.children)
