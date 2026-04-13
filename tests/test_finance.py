import json
from pathlib import Path

from auto_vault.constants import HISTORICAL_YEARS, SITE_COUNT
from auto_vault.finance import build_finance_report
from auto_vault.forecasting import build_budget_forecast
from auto_vault.io import write_csv_rows, write_json
from auto_vault.synthetic import generate_synthetic_invoices
from auto_vault.validation import validate_invoices

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "data" / "sources" / "market" / "entsoe_day_ahead_prices_sample.csv"
LOAD_SHAPE = ROOT / "data" / "sources" / "demand" / "national_grid_load_shape_sample.csv"
BUDGET_ASSUMPTIONS = ROOT / "data" / "sources" / "planning" / "uk_budget_assumptions.json"
FINANCE_ASSUMPTIONS = ROOT / "data" / "sources" / "planning" / "uk_finance_assumptions.json"
FIXTURES = ROOT / "tests" / "fixtures"


def test_finance_report_matches_golden_summary(tmp_path: Path) -> None:
    invoices = generate_synthetic_invoices(PRICES, LOAD_SHAPE, seed=2438)
    invoice_path = tmp_path / "synthetic_invoices.csv"
    validation_path = tmp_path / "invoice_validation_results.csv"
    budget_summary_path = tmp_path / "uk_budget_forecast_summary.json"
    write_csv_rows(invoice_path, [invoice.to_row() for invoice in invoices])

    validation_results, _ = validate_invoices(invoice_path, PRICES)
    write_csv_rows(validation_path, [row.to_row() for row in validation_results])

    _, budget_summary = build_budget_forecast(invoice_path, PRICES, BUDGET_ASSUMPTIONS)
    write_json(budget_summary_path, budget_summary)

    monthly_results, accrual_results, summary = build_finance_report(
        invoice_path,
        validation_path,
        budget_summary_path,
        FINANCE_ASSUMPTIONS,
    )
    expected = json.loads((FIXTURES / "expected_finance_summary.json").read_text())
    historical_months = len(HISTORICAL_YEARS) * 12

    assert summary == expected
    assert sum(1 for row in monthly_results if row.summary_level == "site") == SITE_COUNT * historical_months
    assert sum(1 for row in monthly_results if row.summary_level == "company") == historical_months
    assert len(accrual_results) == SITE_COUNT + 1
