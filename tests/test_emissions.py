import json
from pathlib import Path

from auto_vault.emissions import calculate_emissions
from auto_vault.io import write_csv_rows
from auto_vault.synthetic import generate_synthetic_invoices

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "data" / "sources" / "market" / "entsoe_day_ahead_prices_sample.csv"
LOAD_SHAPE = ROOT / "data" / "sources" / "demand" / "national_grid_load_shape_sample.csv"
FACTOR = ROOT / "data" / "sources" / "emissions" / "defra_2024_scope2_factor.csv"
FIXTURES = ROOT / "tests" / "fixtures"


def test_company_emissions_match_golden_fixture(tmp_path: Path) -> None:
    invoices = generate_synthetic_invoices(PRICES, LOAD_SHAPE, seed=2438)
    invoice_path = tmp_path / "synthetic_invoices.csv"
    write_csv_rows(invoice_path, [invoice.to_row() for invoice in invoices])

    results = calculate_emissions(invoice_path, FACTOR)
    company = next(result.to_row() for result in results if result.summary_level == "company")
    expected = json.loads((FIXTURES / "expected_company_emissions.json").read_text())

    assert company == expected
