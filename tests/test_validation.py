import json
from pathlib import Path

from auto_vault.io import write_csv_rows
from auto_vault.synthetic import generate_synthetic_invoices
from auto_vault.validation import validate_invoices

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "data" / "sources" / "market" / "entsoe_day_ahead_prices_sample.csv"
LOAD_SHAPE = ROOT / "data" / "sources" / "demand" / "national_grid_load_shape_sample.csv"
FIXTURES = ROOT / "tests" / "fixtures"


def test_validation_matches_golden_summary(tmp_path: Path) -> None:
    invoices = generate_synthetic_invoices(PRICES, LOAD_SHAPE, seed=2438)
    invoice_path = tmp_path / "synthetic_invoices.csv"
    write_csv_rows(invoice_path, [invoice.to_row() for invoice in invoices])

    results, summary = validate_invoices(invoice_path, PRICES)
    expected = json.loads((FIXTURES / "expected_validation_summary.json").read_text())

    assert summary == expected
    assert sum(1 for result in results if result.anomaly_flag) == 3
    assert {result.anomaly_reason for result in results if result.anomaly_flag} == {"Duplicate standing charge"}
