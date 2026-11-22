"""Structural outline of a Python buffer, using the standard AST.

No execution/import of buffer code. Reports classes, sync/async functions,
and nested definitions with their source lines. Syntax errors are explicit.
"""
import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class PythonHeading:
    line: int
    column: int
    level: int
    kind: str
    title: str


def python_outline(source):
    """Return PythonHeading objects in source order, or raise SyntaxError."""
    tree = ast.parse(source)
    headings = []

    def visit(body, ancestors=()):
        for node in body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if isinstance(node, ast.ClassDef):
                    kind = "class"
                elif isinstance(node, ast.AsyncFunctionDef):
                    kind = "async def"
                else:
                    kind = "method" if ancestors and ancestors[-1] == "class" else "def"
                # Decorator lines are intentionally not used: land at the definition.
                headings.append(PythonHeading(
                    line=node.lineno, column=node.col_offset,
                    level=len(ancestors), kind=kind, title=node.name))
                visit(node.body, ancestors + (
                    "class" if isinstance(node, ast.ClassDef) else "function",))
            elif isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While,
                                   ast.With, ast.AsyncWith, ast.Try, ast.TryStar)):
                # Conditional definitions, including those inside try/except.
                for attr in ("body", "orelse", "finalbody"):
                    visit(getattr(node, attr, ()), ancestors)
                for handler in getattr(node, "handlers", ()):
                    visit(handler.body, ancestors)
            elif isinstance(node, ast.Match):
                for case in node.cases:
                    visit(case.body, ancestors)

    visit(tree.body)
    return sorted(headings, key=lambda h: (h.line, h.column))
