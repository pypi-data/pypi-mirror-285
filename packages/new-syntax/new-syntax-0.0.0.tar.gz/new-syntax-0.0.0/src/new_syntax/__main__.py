"""Support executing the CLI by doing `python -m new_syntax`."""
from __future__ import annotations

from new_syntax.cli import cli

if __name__ == "__main__":
    raise SystemExit(cli())
