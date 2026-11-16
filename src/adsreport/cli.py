"""Command entry points for the phased reporting implementation."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from adsreport.config import ConfigError, load_config


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adsreport",
        description="Weekly Amazon Ads analysis and reviewed delivery.",
    )
    parser.add_argument("--config", type=Path, default=Path("config"))
    parser.add_argument(
        "--check-config", action="store_true", help="Validate configuration and exit."
    )
    commands = parser.add_subparsers(dest="command")
    sample = commands.add_parser(
        "generate-sample", help="Generate seeded sample inputs."
    )
    sample.add_argument("--seed", type=int, default=42)
    sample.add_argument("--out", type=Path, default=Path("data/sample"))
    run = commands.add_parser("run", help="Build draft reports from validated inputs.")
    run.add_argument("--input", type=Path, default=Path("data/sample"))
    run.add_argument("--out", type=Path, default=Path("out"))
    run.add_argument("--no-ai", action="store_true")
    for name in ("approve", "deliver"):
        command = commands.add_parser(
            name, help=f"{name.capitalize()} a reviewed report."
        )
        command.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command is None and not args.check_config:
        parser.print_help()
        return 0
    try:
        load_config(args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    if args.check_config:
        print("Configuration valid.")
        return 0
    phases = {"generate-sample": "P2", "run": "P3-P6", "approve": "P7", "deliver": "P7"}
    print(
        f"{args.command} is scheduled for {phases[args.command]}. "
        "Current checkpoint provides CLI and configuration validation.",
        file=sys.stderr,
    )
    return 2
