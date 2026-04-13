"""End-to-end demo orchestration."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from .constants import DEFAULT_FORMULA_VERSION, PROJECT_NAME
from .emissions import calculate_emissions
from .io import read_json, write_csv_rows, write_json
from .paths import find_repo_root, sources_dir
from .synthetic import generate_synthetic_invoices
from .validation import validate_invoices


def _relative_to_repo(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(repo_root))
    except ValueError:
        return str(resolved)


def run_demo(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    output_dir = args.output_dir
    prices_path = sources_dir(repo_root) / "market" / "entsoe_day_ahead_prices_sample.csv"
    load_shape_path = sources_dir(repo_root) / "demand" / "national_grid_load_shape_sample.csv"
    factor_path = sources_dir(repo_root) / "emissions" / "defra_2024_scope2_factor.csv"
    source_manifest_path = sources_dir(repo_root) / "manifest.json"

    synthetic_output = output_dir / "synthetic_invoices.csv"
    validation_output = output_dir / "invoice_validation_results.csv"
    validation_summary_output = output_dir / "invoice_validation_summary.json"
    emissions_output = output_dir / "secr_emissions_summary.csv"
    run_manifest_output = output_dir / "run_manifest.json"

    invoices = generate_synthetic_invoices(
        prices_path=prices_path,
        load_shape_path=load_shape_path,
        seed=args.seed,
    )
    write_csv_rows(synthetic_output, [invoice.to_row() for invoice in invoices])

    validation_results, validation_summary = validate_invoices(synthetic_output, prices_path)
    write_csv_rows(validation_output, [result.to_row() for result in validation_results])
    write_json(validation_summary_output, validation_summary)

    emissions_results = calculate_emissions(synthetic_output, factor_path)
    write_csv_rows(emissions_output, [result.to_row() for result in emissions_results])
    company_row = next((row for row in emissions_results if row.summary_level == "company"), None)

    source_manifest = read_json(source_manifest_path)
    run_manifest = {
        "project": PROJECT_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "formula_version": DEFAULT_FORMULA_VERSION,
        "seed": args.seed,
        "source_manifest": _relative_to_repo(source_manifest_path, repo_root),
        "official_source_count": len(source_manifest["files"]),
        "outputs": {
            "synthetic_invoices": _relative_to_repo(synthetic_output, repo_root),
            "invoice_validation_results": _relative_to_repo(validation_output, repo_root),
            "invoice_validation_summary": _relative_to_repo(validation_summary_output, repo_root),
            "secr_emissions_summary": _relative_to_repo(emissions_output, repo_root),
        },
        "metrics": {
            "synthetic_invoice_count": len(invoices),
            "flagged_invoices": validation_summary["flagged_invoices"],
            "savings_opportunity_gbp": validation_summary["total_savings_opportunity_gbp"],
            "company_tco2e": company_row.tco2e if company_row is not None else 0.0,
        },
    }
    write_json(run_manifest_output, run_manifest)

    print(
        f"Demo complete: {len(invoices)} invoices, "
        f"{validation_summary['flagged_invoices']} flagged anomalies, "
        f"GBP {validation_summary['total_savings_opportunity_gbp']:.2f} savings opportunity."
    )
    return 0
