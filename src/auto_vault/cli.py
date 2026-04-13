"""Command line interface for Auto-VAULT."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from . import __version__
from .demo import run_demo
from .emissions import run_calculate_emissions
from .forecasting import run_forecast_budget
from .paths import curated_dir, sources_dir
from .synthetic import run_generate_synthetic_invoices
from .validation import run_validate_invoices

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
        "--prices",
        type=Path,
        default=sources_dir() / "market" / "entsoe_day_ahead_prices_sample.csv",
        help="CSV input path for sampled market prices.",
    )
    generate.add_argument(
        "--load-shape",
        type=Path,
        default=sources_dir() / "demand" / "national_grid_load_shape_sample.csv",
        help="CSV input path for seasonal demand shaping.",
    )
    generate.add_argument(
        "--seed",
        type=int,
        default=2438,
        help="Random seed used for deterministic invoice generation.",
    )
    generate.add_argument(
        "--output",
        type=Path,
        default=curated_dir() / "synthetic_invoices.csv",
        help="CSV output path for generated synthetic invoices.",
    )
    generate.set_defaults(handler=run_generate_synthetic_invoices)

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
    validate.add_argument(
        "--summary-output",
        type=Path,
        default=curated_dir() / "invoice_validation_summary.json",
        help="JSON output path for validation portfolio summary.",
    )
    validate.set_defaults(handler=run_validate_invoices)

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
        "--factor",
        type=Path,
        default=sources_dir() / "emissions" / "defra_2024_scope2_factor.csv",
        help="CSV input path for the DEFRA electricity factor.",
    )
    emissions.add_argument(
        "--output",
        type=Path,
        default=curated_dir() / "secr_emissions_summary.csv",
        help="CSV output path for emissions summaries.",
    )
    emissions.set_defaults(handler=run_calculate_emissions)

    forecast = subparsers.add_parser(
        "forecast-budget",
        help="Create a 12-month UK energy budget forecast.",
    )
    forecast.add_argument(
        "--input",
        type=Path,
        default=curated_dir() / "synthetic_invoices.csv",
        help="CSV input path for invoice records.",
    )
    forecast.add_argument(
        "--prices",
        type=Path,
        default=sources_dir() / "market" / "entsoe_day_ahead_prices_sample.csv",
        help="CSV input path for sampled market prices.",
    )
    forecast.add_argument(
        "--assumptions",
        type=Path,
        default=sources_dir() / "planning" / "uk_budget_assumptions.json",
        help="JSON assumptions file for the UK budget forecast.",
    )
    forecast.add_argument(
        "--output",
        type=Path,
        default=curated_dir() / "uk_budget_forecast.csv",
        help="CSV output path for the UK budget forecast.",
    )
    forecast.add_argument(
        "--summary-output",
        type=Path,
        default=curated_dir() / "uk_budget_forecast_summary.json",
        help="JSON output path for the UK budget summary.",
    )
    forecast.set_defaults(handler=run_forecast_budget)

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
    demo.add_argument(
        "--seed",
        type=int,
        default=2438,
        help="Random seed used for deterministic demo runs.",
    )
    demo.set_defaults(handler=run_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler: CommandHandler = args.handler
    return handler(args)
