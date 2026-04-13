"""Scope 2 emissions calculations for SECR-style reporting."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from .io import read_csv_rows, write_csv_rows
from .models import EmissionsResult, InvoiceRecord
from .sources import load_scope_2_factor


def calculate_emissions(invoices_path: Path, factor_path: Path) -> list[EmissionsResult]:
    factor = load_scope_2_factor(factor_path)
    invoices = [InvoiceRecord.from_row(row) for row in read_csv_rows(invoices_path)]
    if not invoices:
        return []

    site_totals: dict[tuple[str, str], float] = defaultdict(float)
    period_start = min(invoice.month_start for invoice in invoices)
    period_end = max(invoice.month_start for invoice in invoices)

    for invoice in invoices:
        site_totals[(invoice.site_id, invoice.site_name)] += invoice.kwh

    results: list[EmissionsResult] = []
    for (site_id, site_name), total_kwh in sorted(site_totals.items()):
        kgco2e = round(total_kwh * factor, 2)
        results.append(
            EmissionsResult(
                summary_level="site",
                entity_id=site_id,
                entity_name=site_name,
                period_start=period_start,
                period_end=period_end,
                kwh=round(total_kwh, 2),
                defra_factor_kgco2e_per_kwh=factor,
                kgco2e=kgco2e,
                tco2e=round(kgco2e / 1000.0, 3),
                methodology="location-based",
            )
        )

    company_kwh = round(sum(result.kwh for result in results), 2)
    company_kgco2e = round(sum(result.kgco2e for result in results), 2)
    results.append(
        EmissionsResult(
            summary_level="company",
            entity_id="COMPANY",
            entity_name="Birmingham Metal Works Ltd",
            period_start=period_start,
            period_end=period_end,
            kwh=company_kwh,
            defra_factor_kgco2e_per_kwh=factor,
            kgco2e=company_kgco2e,
            tco2e=round(company_kgco2e / 1000.0, 3),
            methodology="location-based",
        )
    )
    return results


def run_calculate_emissions(args: argparse.Namespace) -> int:
    results = calculate_emissions(args.input, args.factor)
    write_csv_rows(args.output, [result.to_row() for result in results])
    company_row = next((row for row in results if row.summary_level == "company"), None)
    company_tco2e = company_row.tco2e if company_row is not None else 0.0
    print(
        f"Calculated Scope 2 emissions for {len(results) - 1 if results else 0} sites; "
        f"company total is {company_tco2e:.3f} tCO2e."
    )
    return 0
