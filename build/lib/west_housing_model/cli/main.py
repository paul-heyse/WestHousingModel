"""Command-line interface stub."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:  # pragma: no cover - stub
    """Create the top-level CLI argument parser."""

    parser = argparse.ArgumentParser(prog="west-housing-model")
    parser.add_argument("command", help="Subcommand to execute")
    return parser


def main() -> None:  # pragma: no cover - stub
    """Entry point for the CLI."""

    parser = build_parser()
    args = parser.parse_args()
    raise NotImplementedError(f"Command {args.command} is not yet implemented")


__all__ = ["build_parser", "main"]
