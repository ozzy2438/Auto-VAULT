"""Budgeting and forecasting outputs for the UK demo."""

from __future__ import annotations

import argparse
import calendar
from collections import defaultdict
from datetime import date
from pathlib import Path

from .io import read_csv_rows, read_json, write_csv_rows, write_json
from .models import BudgetForecastResult, InvoiceRecord
from .sources import load_monthly_market_prices


def _next_month(value: date) -> date:
    month = value.month + 1
    year = value.year
    if month == 13:
        month = 1
        year += 1
    return date(year, month, 1)


def _month_sequence(start_month: date, months: int) -> list[date]:
    values: list[date] = []
    current = start_month
    for _ in range(months):
        values.append(current)
        current = _next_month(current)
    return values


def _trailing_same_month_average(
    invoices: list[InvoiceRecord],
) -> dict[tuple[str, int], float]:
    buckets: dict[tuple[str, int], list[float]] = defaultdict(list)
    for invoice in invoices:
        month_number = date.fromisoformat(invoice.month_start).month
        buckets[(invoice.site_id, month_number)].append(invoice.kwh)
    return {key: sum(values) / len(values) for key, values in buckets.items()}


def _year_totals(invoices: list[InvoiceRecord]) -> dict[tuple[str, int], float]:
    totals: dict[tuple[str, int], float] = defaultdict(float)
    for invoice in invoices:
        invoice_date = date.fromisoformat(invoice.month_start)
        totals[(invoice.site_id, invoice_date.year)] += invoice.kwh
    return totals


def _site_names(invoices: list[InvoiceRecord]) -> dict[str, str]:
    names: dict[str, str] = {}
    for invoice in invoices:
        names[invoice.site_id] = invoice.site_name
    return names


def build_budget_forecast(
    invoices_path: Path,
    prices_path: Path,
    assumptions_path: Path,
) -> tuple[list[BudgetForecastResult], dict[str, object]]:
    invoices = [InvoiceRecord.from_row(row) for row in read_csv_rows(invoices_path)]
    price_lookup = load_monthly_market_prices(prices_path)
    assumptions = read_json(assumptions_path)

    start_month = date.fromisoformat(assumptions["forecast_start_month"])
    months_ahead = int(assumptions["months_ahead"])
    wholesale_uplift_pct = float(assumptions["wholesale_uplift_pct"])
    confidence_band_pct = float(assumptions["confidence_band_pct"])
    site_efficiency_targets = {
        key: float(value) for key, value in assumptions["site_efficiency_targets_pct"].items()
    }
    basis = assumptions["budget_basis"]

    monthly_same_month_average = _trailing_same_month_average(invoices)
    annual_totals = _year_totals(invoices)
    site_names = _site_names(invoices)

    site_growth_factors: dict[str, float] = {}
    for site_id in site_names:
        total_2024 = annual_totals[(site_id, 2024)]
        total_2025 = annual_totals[(site_id, 2025)]
        observed_growth = (total_2025 / total_2024) - 1 if total_2024 else 0.0
        efficiency_target = site_efficiency_targets.get(site_id, 0.0)
        site_growth_factors[site_id] = 1.0 + observed_growth - efficiency_target

    results: list[BudgetForecastResult] = []
    forecast_months = _month_sequence(start_month, months_ahead)
    for forecast_month in forecast_months:
        proxy_price_key = forecast_month.replace(year=2025).isoformat()
        market_price = price_lookup[proxy_price_key] * (1.0 + wholesale_uplift_pct)
        for site_id, site_name in sorted(site_names.items()):
            base_kwh = monthly_same_month_average[(site_id, forecast_month.month)]
            forecast_kwh = round(base_kwh * site_growth_factors[site_id], 2)
            reference_invoice = next(invoice for invoice in invoices if invoice.site_id == site_id)
            unit_rate = round(
                (market_price * reference_invoice.market_multiplier) + reference_invoice.network_adder_gbp_per_kwh,
                6,
            )
            billing_days = calendar.monthrange(forecast_month.year, forecast_month.month)[1]
            standing_charge = round(
                reference_invoice.standing_charge_gbp_per_day * billing_days,
                2,
            )
            forecast_cost = round((forecast_kwh * unit_rate) + standing_charge, 2)
            results.append(
                BudgetForecastResult(
                    summary_level="site",
                    entity_id=site_id,
                    entity_name=site_name,
                    forecast_month=forecast_month.isoformat(),
                    forecast_kwh=forecast_kwh,
                    forecast_unit_rate_gbp_per_kwh=unit_rate,
                    forecast_cost_gbp=forecast_cost,
                    budget_low_gbp=round(forecast_cost * (1.0 - confidence_band_pct), 2),
                    budget_high_gbp=round(forecast_cost * (1.0 + confidence_band_pct), 2),
                    basis=basis,
                )
            )

    company_rows: list[BudgetForecastResult] = []
    for forecast_month in forecast_months:
        monthly_rows = [
            row for row in results if row.summary_level == "site" and row.forecast_month == forecast_month.isoformat()
        ]
        total_cost = round(sum(row.forecast_cost_gbp for row in monthly_rows), 2)
        total_kwh = round(sum(row.forecast_kwh for row in monthly_rows), 2)
        company_rows.append(
            BudgetForecastResult(
                summary_level="company",
                entity_id="COMPANY",
                entity_name="Birmingham Metal Works Ltd",
                forecast_month=forecast_month.isoformat(),
                forecast_kwh=total_kwh,
                forecast_unit_rate_gbp_per_kwh=round(
                    total_cost / total_kwh,
                    6,
                ) if total_kwh else 0.0,
                forecast_cost_gbp=total_cost,
                budget_low_gbp=round(sum(row.budget_low_gbp for row in monthly_rows), 2),
                budget_high_gbp=round(sum(row.budget_high_gbp for row in monthly_rows), 2),
                basis=basis,
            )
        )

    summary = {
        "forecast_start_month": start_month.isoformat(),
        "months_ahead": months_ahead,
        "company_forecast_kwh": round(sum(row.forecast_kwh for row in company_rows), 2),
        "company_forecast_cost_gbp": round(sum(row.forecast_cost_gbp for row in company_rows), 2),
        "confidence_band_pct": confidence_band_pct,
        "budget_basis": basis,
    }
    return results + company_rows, summary


def run_forecast_budget(args: argparse.Namespace) -> int:
    results, summary = build_budget_forecast(
        invoices_path=args.input,
        prices_path=args.prices,
        assumptions_path=args.assumptions,
    )
    write_csv_rows(args.output, [result.to_row() for result in results])
    write_json(args.summary_output, summary)
    print(
        f"Built a {summary['months_ahead']}-month UK budget forecast worth GBP "
        f"{summary['company_forecast_cost_gbp']:.2f}."
    )
    return 0
