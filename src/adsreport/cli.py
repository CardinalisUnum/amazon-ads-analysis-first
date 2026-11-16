"""Command entry points for reporting, frozen review and explicit delivery."""

import argparse
import json
import sys
import webbrowser
from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path

from adsreport.config import ConfigError, load_config
from adsreport.operations import (
    execute_approval,
    execute_delivery,
    execute_run,
    inspect_report,
    log_path,
)
from adsreport.readiness import check_readiness
from adsreport.runlog import read_events, scheduled_rate
from adsreport.sample import generate_sample


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adsreport",
        description="Weekly Amazon Ads analysis and reviewed delivery.",
    )
    parser.add_argument("--config", type=Path, default=Path("config"))
    parser.add_argument("--check-config", action="store_true")
    commands = parser.add_subparsers(dest="command")
    sample = commands.add_parser(
        "generate-sample", help="Generate seeded sample inputs."
    )
    sample.add_argument("--seed", type=int, default=42)
    sample.add_argument("--out", type=Path, default=Path("data/sample"))
    run = commands.add_parser("run", help="Build and log a new DRAFT report.")
    run.add_argument("--input", type=Path, default=Path("data/sample"))
    run.add_argument("--out", type=Path)
    run.add_argument("--no-ai", action="store_true")
    run.add_argument(
        "--inject-failure",
        action="store_true",
        help="Label and exercise test_failure alert handling.",
    )
    run.add_argument(
        "--open",
        action="store_true",
        help="Open the generated local HTML after success.",
    )
    for name in ("inspect", "approve", "deliver"):
        command = commands.add_parser(name)
        command.add_argument("--report", type=Path, required=True)
        if name != "inspect":
            command.add_argument(
                "--expect-manifest",
                help="SHA-256 printed by inspect for the reviewed version.",
            )
        if name == "approve":
            command.add_argument("--reviewer")
            command.add_argument("--github-review", action="store_true")
            command.add_argument("--out", type=Path)
        if name == "deliver":
            command.add_argument(
                "--retry-uncertain",
                action="store_true",
                help="Explicitly retry ambiguous sends, which can duplicate a message.",
            )
    commands.add_parser(
        "doctor", help="Check local setup without making an AI or notification request."
    )
    commands.add_parser(
        "history",
        help="Show real recorded runs and scheduled success numerator/denominator.",
    )
    args = parser.parse_args(argv)
    if args.command is None and not args.check_config:
        parser.print_help()
        return 0
    try:
        if args.command == "doctor":
            result = check_readiness(args.config)
            print(json.dumps(result, indent=2))
            return 0 if result["local_reporting_ready"] else 2
        if args.command == "history":
            events = read_events(log_path())
            print(
                json.dumps(
                    {
                        "scheduled_rate": scheduled_rate(events),
                        "rate_scope": (
                            "App-observed scheduled builds only. GitHub failures "
                            "before app startup require workflow history."
                        ),
                        "events": [e.model_dump(mode="json") for e in events],
                    },
                    indent=2,
                )
            )
            return 0
        if args.command == "inspect":
            print(json.dumps(inspect_report(args.report), indent=2))
            return 0
        if args.command in {"approve", "deliver"}:
            if not args.expect_manifest:
                raise ValueError(
                    "Review the files, run inspect, and supply --expect-manifest "
                    "for that exact version."
                )
            if args.command == "approve":
                if not args.github_review and not args.reviewer:
                    raise ValueError(
                        "Supply --reviewer for a local self-attested review, "
                        "or --github-review in Actions."
                    )
                destination = args.out or args.report.with_name(
                    args.report.name + "-approved"
                )
                approved_bundle = execute_approval(
                    args.report,
                    destination,
                    args.expect_manifest,
                    args.reviewer or "",
                    github=args.github_review,
                )
                print(
                    json.dumps(
                        {
                            "status": "APPROVED",
                            "path": str(destination),
                            "manifest_sha256": approved_bundle.manifest_sha256,
                        }
                    )
                )
                return 0
            states = execute_delivery(
                args.report, args.expect_manifest, retry_uncertain=args.retry_uncertain
            )
            print(
                json.dumps(
                    {
                        "provider_acknowledgements": states,
                        "human_receipt_verified": False,
                    }
                )
            )
            return 0 if all(s == "accepted" for s in states.values()) else 3
        if args.command == "run":
            path = execute_run(
                args.input,
                args.out,
                args.config,
                no_ai=args.no_ai,
                inject_failure=args.inject_failure,
            )
            print(
                f"DRAFT SAMPLE DATA XLSX, HTML, PDF, PPTX and evidence ready at {path}."
            )
            print("Run inspect --report with this directory before approval.")
            if args.open:
                webbrowser.open((path / "SAMPLE_report.html").resolve().as_uri())
            return 0
        config = load_config(args.config)
        if args.check_config:
            print("Configuration valid.")
            return 0
        path = generate_sample(
            args.out, args.seed, Decimal(str(config.settings.vat_rate))
        )
        print(f"SAMPLE DATA ready at {path} (10 products, 8 weeks, seed {args.seed}).")
        return 0
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except (ValueError, OSError) as exc:
        print(f"Report input/output error: {exc}", file=sys.stderr)
        return 2
