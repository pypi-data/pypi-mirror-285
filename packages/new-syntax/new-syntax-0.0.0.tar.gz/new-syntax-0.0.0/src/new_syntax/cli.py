"""CLI interface for new_syntax."""
from __future__ import annotations

import argparse

from new_syntax import greet


class CLIArgs:
    name: str


def cli(argv: list[str] | None = None) -> int:
    """CLI interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args(argv, namespace=CLIArgs)

    print(greet(args.name))
    return 0
