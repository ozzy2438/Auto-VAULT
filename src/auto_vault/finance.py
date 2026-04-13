"""Finance-style reporting outputs for the UK demo."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
from pathlib import Path

from .io import read_csv_rows, read_json, write_csv_rows, write_json
from .models import AccrualResult, FinanceMonthlyResult, InvoiceRecord, ValidationResult


def build_finance_report(
    invoices_path: Path,
    validation_path: Path,
    budget_summary_path: Path,
    assumptions_path: Path,
) -> tuple[list[FinanceMonthlyResult], list[AccrualResult], dict[str, object]]:
    invoices = [InvoiceRecord.from_row(row) for row in read_csv_rows(invoices_path)]
    validations = [
        ValidationResult(
            invoice_id=row["invoice_id"],
            site_id=row["site_id"],
            month_start=row["month_start"],
            expected_total_gbp=float(row["expected_total_gbp"]),
            billed_total_gbp=float(row["billed_total_gbp"]),
            variance_gbp=float(row["variance_gbp"]),
            variance_pct=float(row["variance_pct"]),
            anomaly_flag=row["anomaly_flag"] == "True",
            anomaly_reason=row["anomaly_reason"],
        )
        for row in read_csv_rows(validation_path)
    ]
    budget_summary = read_json(budget_summary_path)
    assumptions = read_json(assumptions_path)

    invoice_lookup = {invoice.invoice_id: invoice for invoice in invoices}
    site_names = {invoice.site_id: invoice.site_name for invoice in invoices}
    monthly_buckets: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"billed": 0.0, "expected": 0.0, "variance": 0.0, "anomalies": 0.0}
    )

    for validation in validations:
        monthly_key = (validation.site_id, validation.month_start)
        bucket = monthly_buckets[monthly_key]
        bucket["billed"] += validation.billed_total_gbp
        bucket["expected"] += validation.expected_total_gbp
        bucket["variance"] += validation.variance_gbp
        bucket["anomalies"] += 1 if validation.anomaly_flag else 0

    monthly_results: list[FinanceMonthlyResult] = []
    all_months = sorted({validation.month_start for validation in validations})
    for site_id, site_name in sorted(site_names.items()):
        for month_start in all_months:
            bucket = monthly_buckets[(site_id, month_start)]
            monthly_results.append(
                FinanceMonthlyResult(
                    summary_level="site",
                    entity_id=site_id,
                    entity_name=site_name,
                    month_start=month_start,
                    billed_actual_gbp=round(bucket["billed"], 2),
                    benchmark_gbp=round(bucket["expected"], 2),
                    variance_gbp=round(bucket["variance"], 2),
                    anomaly_count=int(bucket["anomalies"]),
                    period_status="closed_actual",
                )
            )

    for month_start in all_months:
        site_rows = [row for row in monthly_results if row.summary_level == "site" and row.month_start == month_start]
        monthly_results.append(
            FinanceMonthlyResult(
                summary_level="company",
                entity_id="COMPANY",
                entity_name="Birmingham Metal Works Ltd",
                month_start=month_start,
                billed_actual_gbp=round(sum(row.billed_actual_gbp for row in site_rows), 2),
                benchmark_gbp=round(sum(row.benchmark_gbp for row in site_rows), 2),
                variance_gbp=round(sum(row.variance_gbp for row in site_rows), 2),
                anomaly_count=sum(row.anomaly_count for row in site_rows),
                period_status="closed_actual",
            )
        )

    close_day = int(assumptions["close_day_of_month"])
    accrual_basis = assumptions["accrual_basis"]
    latest_month = max(date.fromisoformat(invoice.month_start) for invoice in invoices)
    latest_month_key = latest_month.isoformat()
    accrual_results: list[AccrualResult] = []
    for site_id, site_name in sorted(site_names.items()):
        latest_invoice = next(
            invoice for invoice in invoices if invoice.site_id == site_id and invoice.month_start == latest_month_key
        )
        unbilled_days = max(0, latest_invoice.billed_days - close_day)
        daily_benchmark_cost = latest_invoice.expected_total_gbp / latest_invoice.billed_days
        accrual_results.append(
            AccrualResult(
                summary_level="site",
                entity_id=site_id,
                entity_name=site_name,
                accrual_month=latest_month_key,
                close_day_of_month=close_day,
                unbilled_days=unbilled_days,
                accrued_cost_gbp=round(daily_benchmark_cost * unbilled_days, 2),
                accrual_basis=accrual_basis,
            )
        )

    accrual_results.append(
        AccrualResult(
            summary_level="company",
            entity_id="COMPANY",
            entity_name="Birmingham Metal Works Ltd",
            accrual_month=latest_month_key,
            close_day_of_month=close_day,
            unbilled_days=max((row.unbilled_days for row in accrual_results), default=0),
            accrued_cost_gbp=round(sum(row.accrued_cost_gbp for row in accrual_results), 2),
            accrual_basis=accrual_basis,
        )
    )

    company_rows = [row for row in monthly_results if row.summary_level == "company"]
    company_accrual = next(row for row in accrual_results if row.summary_level == "company")
    summary = {
        "report_currency": assumptions["report_currency"],
        "months_reported": len(company_rows),
        "company_historical_billed_gbp": round(sum(row.billed_actual_gbp for row in company_rows), 2),
        "company_historical_variance_gbp": round(sum(row.variance_gbp for row in company_rows), 2),
        "next_12m_budget_gbp": float(budget_summary["company_forecast_cost_gbp"]),
        "latest_month_accrual_gbp": company_accrual.accrued_cost_gbp,
        "open_month": latest_month_key,
        "close_day_of_month": close_day,
    }
    return monthly_results, accrual_results, summary


def run_build_finance_report(args: argparse.Namespace) -> int:
    monthly_results, accrual_results, summary = build_finance_report(
        invoices_path=args.invoices,
        validation_path=args.validation,
        budget_summary_path=args.budget_summary,
        assumptions_path=args.assumptions,
    )
    write_csv_rows(args.monthly_output, [row.to_row() for row in monthly_results])
    write_csv_rows(args.accrual_output, [row.to_row() for row in accrual_results])
    write_json(args.summary_output, summary)
    print(
        f"Built UK finance outputs with {summary['months_reported']} closed months and "
        f"GBP {summary['latest_month_accrual_gbp']:.2f} accrued at month end."
    )
    return 0
