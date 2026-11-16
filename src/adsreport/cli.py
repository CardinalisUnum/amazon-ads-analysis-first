"""Command entry points for the phased reporting implementation."""

import argparse
import sys
from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path

from adsreport.config import ConfigError, load_config
from adsreport.io.loader import InputError
from adsreport.pipeline import run_numerical_draft
from adsreport.sample import generate_sample


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
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    if args.check_config:
        print("Configuration valid.")
        return 0
    if args.command == "generate-sample":
        try:
            path = generate_sample(
                args.out, args.seed, Decimal(str(config.settings.vat_rate))
            )
        except (OSError, ValueError) as exc:
            print(f"Sample generation error: {exc}", file=sys.stderr)
            return 2
        print(f"SAMPLE DATA ready at {path} (10 products, 8 weeks, seed {args.seed}).")
        return 0
    if args.command == "run":
        try:
            path = run_numerical_draft(
                args.input,
                args.out,
                args.config,
                config,
                no_ai=args.no_ai,
            )
        except (InputError, OSError, ValueError) as exc:
            print(f"Report input/output error: {exc}", file=sys.stderr)
            return 2
        print(f"DRAFT SAMPLE DATA XLSX, HTML, PDF, PPTX and evidence ready at {path}.")
        return 0
    phases = {"approve": "P7", "deliver": "P7"}
    print(
        f"{args.command} is scheduled for {phases[args.command]}. "
        "See docs/STATUS.md for the current implementation checkpoint.",
        file=sys.stderr,
    )
    return 2
