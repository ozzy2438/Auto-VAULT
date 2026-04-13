import json
from pathlib import Path

from auto_vault.constants import SITE_COUNT
from auto_vault.forecasting import build_budget_forecast
from auto_vault.io import write_csv_rows
from auto_vault.synthetic import generate_synthetic_invoices

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "data" / "sources" / "market" / "entsoe_day_ahead_prices_sample.csv"
LOAD_SHAPE = ROOT / "data" / "sources" / "demand" / "national_grid_load_shape_sample.csv"
ASSUMPTIONS = ROOT / "data" / "sources" / "planning" / "uk_budget_assumptions.json"
FIXTURES = ROOT / "tests" / "fixtures"


def test_budget_forecast_matches_golden_summary(tmp_path: Path) -> None:
    invoices = generate_synthetic_invoices(PRICES, LOAD_SHAPE, seed=2438)
    invoice_path = tmp_path / "synthetic_invoices.csv"
    write_csv_rows(invoice_path, [invoice.to_row() for invoice in invoices])

    results, summary = build_budget_forecast(invoice_path, PRICES, ASSUMPTIONS)
    expected = json.loads((FIXTURES / "expected_budget_forecast_summary.json").read_text())

    assert summary == expected
    assert sum(1 for row in results if row.summary_level == "site") == SITE_COUNT * 12
    assert sum(1 for row in results if row.summary_level == "company") == 12
