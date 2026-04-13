"""Load versioned sample inputs."""

from __future__ import annotations

from pathlib import Path

from .io import read_csv_rows


def load_monthly_market_prices(path: Path) -> dict[str, float]:
    rows = read_csv_rows(path)
    return {row["month_start"]: float(row["day_ahead_price_gbp_per_kwh"]) for row in rows}


def load_monthly_load_shape(path: Path) -> dict[int, float]:
    rows = read_csv_rows(path)
    return {int(row["month_number"]): float(row["seasonal_index"]) for row in rows}


def load_scope_2_factor(path: Path) -> float:
    rows = read_csv_rows(path)
    if not rows:
        raise ValueError(f"No DEFRA factor rows found in {path}")
    return float(rows[0]["factor_kgco2e_per_kwh"])
