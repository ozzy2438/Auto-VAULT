"""Command line interface for Auto-VAULT."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from . import __version__
from .paths import curated_dir, sources_dir

CommandHandler = Callable[[argparse.Namespace], int]


def _not_implemented(command_name: str) -> CommandHandler:
    def runner(_: argparse.Namespace) -> int:
        raise SystemExit(f"{command_name} is not implemented yet.")

    return runner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auto-vault",
        description="UK energy invoice validation and Scope 2 reporting MVP.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate-synthetic-invoices",
        help="Create deterministic synthetic invoice records.",
    )
    generate.add_argument(
        "--output",
        type=Path,
        default=curated_dir() / "synthetic_invoices.csv",
        help="CSV output path for generated synthetic invoices.",
    )
    generate.set_defaults(handler=_not_implemented("generate-synthetic-invoices"))

    validate = subparsers.add_parser(
        "validate-invoices",
        help="Validate billed invoices against market assumptions.",
    )
    validate.add_argument(
        "--input",
        type=Path,
        default=curated_dir() / "synthetic_invoices.csv",
        help="CSV input path for invoice records.",
    )
    validate.add_argument(
        "--prices",
        type=Path,
        default=sources_dir() / "market" / "entsoe_day_ahead_prices_sample.csv",
        help="CSV input path for sampled market prices.",
    )
    validate.add_argument(
        "--output",
        type=Path,
        default=curated_dir() / "invoice_validation_results.csv",
        help="CSV output path for validation results.",
    )
    validate.set_defaults(handler=_not_implemented("validate-invoices"))

    emissions = subparsers.add_parser(
        "calculate-emissions",
        help="Calculate DEFRA location-based Scope 2 emissions.",
    )
    emissions.add_argument(
        "--input",
        type=Path,
        default=curated_dir() / "synthetic_invoices.csv",
        help="CSV input path for invoice records.",
    )
    emissions.add_argument(
        "--output",
        type=Path,
        default=curated_dir() / "secr_emissions_summary.csv",
        help="CSV output path for emissions summaries.",
    )
    emissions.set_defaults(handler=_not_implemented("calculate-emissions"))

    demo = subparsers.add_parser(
        "run-demo",
        help="Run the end-to-end demo pipeline.",
    )
    demo.add_argument(
        "--output-dir",
        type=Path,
        default=curated_dir(),
        help="Directory for curated pipeline outputs.",
    )
    demo.set_defaults(handler=_not_implemented("run-demo"))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler: CommandHandler = args.handler
    return handler(args)
