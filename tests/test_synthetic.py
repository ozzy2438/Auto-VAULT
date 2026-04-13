from pathlib import Path

from auto_vault.synthetic import generate_synthetic_invoices

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "data" / "sources" / "market" / "entsoe_day_ahead_prices_sample.csv"
LOAD_SHAPE = ROOT / "data" / "sources" / "demand" / "national_grid_load_shape_sample.csv"


def test_generate_synthetic_invoices_is_deterministic() -> None:
    first_run = generate_synthetic_invoices(PRICES, LOAD_SHAPE, seed=2438)
    second_run = generate_synthetic_invoices(PRICES, LOAD_SHAPE, seed=2438)

    assert len(first_run) == 72
    assert len({invoice.site_id for invoice in first_run}) == 3
    assert first_run[0].invoice_id == "AV-SITE-01-202401"
    assert first_run[0].mpan == "2200001234501"
    assert [invoice.kwh for invoice in first_run[:10]] == [invoice.kwh for invoice in second_run[:10]]
    assert round(
        sum(invoice.billed_standing_charge_gbp - invoice.expected_standing_charge_gbp for invoice in first_run),
        2,
    ) == 1840.0
