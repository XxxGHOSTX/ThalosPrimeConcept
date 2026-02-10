#!/usr/bin/env python3
"""Utility for rendering the repository's file structure and detecting empty files.

Usage:
    python src/structure.py --base .
    python src/structure.py --base . --report docs/structure.md
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Set

DEFAULT_IGNORES: Set[str] = {
    ".git",
    ".github",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "dist",
    "build",
}


def _should_ignore(path: Path, ignores: Set[str]) -> bool:
    return any(part in ignores for part in path.parts)


def iter_paths(base: Path, ignores: Set[str]) -> Iterable[Path]:
    for path in sorted(base.rglob("*")):
        if _should_ignore(path, ignores):
            continue
        yield path


def render_tree(base: Path, ignores: Set[str]) -> str:
    lines = [base.resolve().name]

    def walk(current: Path, prefix: str = "") -> None:
        children = [
            child
            for child in sorted(current.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            if not _should_ignore(child, ignores)
        ]
        for index, child in enumerate(children):
            is_last = index == len(children) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if child.is_dir() else ""
            lines.append(f"{prefix}{connector}{child.name}{suffix}")
            if child.is_dir():
                extension = "    " if is_last else "│   "
                walk(child, prefix + extension)

    walk(base)
    return "\n".join(lines)


def find_empty_files(base: Path, ignores: Set[str]) -> list[Path]:
    return [
        path
        for path in iter_paths(base, ignores)
        if path.is_file() and path.stat().st_size == 0
    ]


def _default_base() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render repository file structure and ensure no empty files are present."
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=_default_base(),
        help="Base directory to inspect. Defaults to the repository root.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path to write the rendered tree to a file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    base = args.base.resolve()
    if not base.exists():
        print(f"Base path does not exist: {base}")
        return 1

    tree = render_tree(base, DEFAULT_IGNORES)
    empty_files = find_empty_files(base, DEFAULT_IGNORES)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(tree)

    if empty_files:
        print("Empty files detected:")
        for path in empty_files:
            print(f"- {path.relative_to(base)}")
        return 1

    print(tree)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
