"""Invoice validation engine."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .io import read_csv_rows, write_csv_rows, write_json
from .models import InvoiceRecord, ValidationResult
from .sources import load_monthly_market_prices


def _expected_unit_rate(invoice: InvoiceRecord, price_lookup: dict[str, float]) -> float:
    market_price = price_lookup[invoice.month_start]
    return round((market_price * invoice.market_multiplier) + invoice.network_adder_gbp_per_kwh, 6)


def _expected_standing_charge(invoice: InvoiceRecord) -> float:
    return round(invoice.standing_charge_gbp_per_day * invoice.billed_days, 2)


def _classify_anomaly(
    invoice: InvoiceRecord,
    expected_unit_rate: float,
    expected_standing_charge: float,
    variance_gbp: float,
) -> str:
    unit_rate_delta = round(invoice.billed_unit_rate_gbp_per_kwh - expected_unit_rate, 6)
    standing_charge_delta = round(invoice.billed_standing_charge_gbp - expected_standing_charge, 2)

    if standing_charge_delta > 1 and abs(unit_rate_delta) <= 0.0005:
        return "Duplicate standing charge"
    if unit_rate_delta > 0.002:
        return "Unit rate above benchmark"
    if unit_rate_delta < -0.002:
        return "Unit rate below benchmark"
    if variance_gbp > 1:
        return "Billed total above expected benchmark"
    if variance_gbp < -1:
        return "Billed total below expected benchmark"
    return "No anomaly detected"


def validate_invoices(invoices_path: Path, prices_path: Path) -> tuple[list[ValidationResult], dict[str, object]]:
    price_lookup = load_monthly_market_prices(prices_path)
    invoices = [InvoiceRecord.from_row(row) for row in read_csv_rows(invoices_path)]

    results: list[ValidationResult] = []
    for invoice in invoices:
        expected_unit_rate = _expected_unit_rate(invoice, price_lookup)
        expected_standing_charge = _expected_standing_charge(invoice)
        expected_total = round((invoice.kwh * expected_unit_rate) + expected_standing_charge, 2)
        variance_gbp = round(invoice.billed_total_gbp - expected_total, 2)
        variance_pct = round((variance_gbp / expected_total) * 100, 2) if expected_total else 0.0
        anomaly_reason = _classify_anomaly(invoice, expected_unit_rate, expected_standing_charge, variance_gbp)
        anomaly_flag = anomaly_reason != "No anomaly detected"
        results.append(
            ValidationResult(
                invoice_id=invoice.invoice_id,
                site_id=invoice.site_id,
                month_start=invoice.month_start,
                expected_total_gbp=expected_total,
                billed_total_gbp=invoice.billed_total_gbp,
                variance_gbp=variance_gbp,
                variance_pct=variance_pct,
                anomaly_flag=anomaly_flag,
                anomaly_reason=anomaly_reason,
            )
        )

    anomaly_results = [result for result in results if result.anomaly_flag]
    anomaly_reason_counts = Counter(result.anomaly_reason for result in anomaly_results)
    summary = {
        "total_invoices": len(results),
        "flagged_invoices": len(anomaly_results),
        "total_expected_gbp": round(sum(result.expected_total_gbp for result in results), 2),
        "total_billed_gbp": round(sum(result.billed_total_gbp for result in results), 2),
        "total_savings_opportunity_gbp": round(
            sum(max(result.variance_gbp, 0.0) for result in anomaly_results),
            2,
        ),
        "top_anomaly_reason": anomaly_reason_counts.most_common(1)[0][0] if anomaly_reason_counts else "none",
        "anomaly_reason_counts": dict(anomaly_reason_counts),
        "formula_version": "uk-secr-v1"
    }
    return results, summary


def run_validate_invoices(args: argparse.Namespace) -> int:
    results, summary = validate_invoices(args.input, args.prices)
    write_csv_rows(args.output, [result.to_row() for result in results])
    write_json(args.summary_output, summary)
    print(
        f"Validated {summary['total_invoices']} invoices; "
        f"flagged {summary['flagged_invoices']} anomaly cases worth GBP "
        f"{summary['total_savings_opportunity_gbp']:.2f}."
    )
    return 0
