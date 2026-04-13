"""Synthetic invoice generation for the Auto-VAULT MVP."""

from __future__ import annotations

import argparse
import calendar
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .constants import (
    DEFAULT_DUOS_GBP_PER_KWH,
    HISTORICAL_YEARS,
    DEFAULT_MARKET_MULTIPLIER,
    DEFAULT_RANDOM_SEED,
    DEFAULT_STANDING_CHARGE_GBP_PER_DAY,
    SITE_COUNT,
    TARGET_COMPANY,
    TARGET_REGION,
)
from .io import write_csv_rows
from .models import InvoiceRecord
from .sources import load_monthly_load_shape, load_monthly_market_prices


@dataclass(frozen=True, slots=True)
class SiteProfile:
    site_id: str
    site_name: str
    mpan: str
    annual_mwh: float
    shift_intensity: float


SITE_PROFILES = [
    SiteProfile("SITE-01", "Birmingham Forge", "2200001234501", 1180.0, 0.97),
    SiteProfile("SITE-02", "Walsall Pressing", "2200001234502", 1340.0, 1.00),
    SiteProfile("SITE-03", "Coventry Finishing", "2200001234503", 1460.0, 1.05),
    SiteProfile("SITE-04", "Wolverhampton Fabrication", "2200001234504", 980.0, 0.92),
    SiteProfile("SITE-05", "Dudley Components", "2200001234505", 1120.0, 0.95),
    SiteProfile("SITE-06", "Solihull Packaging", "2200001234506", 1260.0, 0.98),
    SiteProfile("SITE-07", "West Bromwich Castings", "2200001234507", 1510.0, 1.03),
    SiteProfile("SITE-08", "Cannock Materials", "2200001234508", 1670.0, 1.06),
    SiteProfile("SITE-09", "Tamworth Logistics Hub", "2200001234509", 910.0, 0.90),
    SiteProfile("SITE-10", "Redditch Process Plant", "2200001234510", 1080.0, 0.94),
    SiteProfile("SITE-11", "Stafford Assembly", "2200001234511", 1390.0, 1.01),
    SiteProfile("SITE-12", "Telford Distribution", "2200001234512", 1590.0, 1.04),
]

SEEDED_ANOMALIES_GBP = {
    ("SITE-01", "2024-03-01"): 610.0,
    ("SITE-02", "2024-11-01"): 615.0,
    ("SITE-03", "2025-02-01"): 615.0,
}


def month_starts() -> list[date]:
    starts: list[date] = []
    for year in HISTORICAL_YEARS:
        for month in range(1, 13):
            starts.append(date(year, month, 1))
    return starts


def month_end(value: date) -> date:
    last_day = calendar.monthrange(value.year, value.month)[1]
    return value.replace(day=last_day)


def _month_kwh(
    rng: random.Random,
    annual_mwh: float,
    seasonal_index: float,
    shift_intensity: float,
    growth_factor: float,
) -> float:
    baseline_monthly_kwh = (annual_mwh * 1000.0) / 12.0
    noise = rng.uniform(0.972, 1.028)
    kwh = baseline_monthly_kwh * seasonal_index * shift_intensity * growth_factor * noise
    return round(kwh, 2)


def _expected_unit_rate(market_price: float) -> float:
    return round((market_price * DEFAULT_MARKET_MULTIPLIER) + DEFAULT_DUOS_GBP_PER_KWH, 6)


def generate_synthetic_invoices(
    prices_path: Path,
    load_shape_path: Path,
    seed: int = DEFAULT_RANDOM_SEED,
) -> list[InvoiceRecord]:
    monthly_prices = load_monthly_market_prices(prices_path)
    monthly_shape = load_monthly_load_shape(load_shape_path)
    rng = random.Random(seed)

    invoices: list[InvoiceRecord] = []
    for month_start_value in month_starts():
        month_key = month_start_value.isoformat()
        market_price = monthly_prices[month_key]
        seasonal_index = monthly_shape[month_start_value.month]
        growth_factor = 1.0 if month_start_value.year == 2024 else 1.03
        billed_days = calendar.monthrange(month_start_value.year, month_start_value.month)[1]

        for site in SITE_PROFILES:
            kwh = _month_kwh(
                rng=rng,
                annual_mwh=site.annual_mwh,
                seasonal_index=seasonal_index,
                shift_intensity=site.shift_intensity,
                growth_factor=growth_factor,
            )
            unit_rate = _expected_unit_rate(market_price)
            expected_standing_charge = round(DEFAULT_STANDING_CHARGE_GBP_PER_DAY * billed_days, 2)
            anomaly_extra = SEEDED_ANOMALIES_GBP.get((site.site_id, month_key), 0.0)
            billed_standing_charge = round(expected_standing_charge + anomaly_extra, 2)
            expected_total = round((kwh * unit_rate) + expected_standing_charge, 2)
            billed_total = round((kwh * unit_rate) + billed_standing_charge, 2)
            anomaly_seed = "duplicate_standing_charge" if anomaly_extra else "none"

            invoices.append(
                InvoiceRecord(
                    invoice_id=f"AV-{site.site_id}-{month_start_value:%Y%m}",
                    site_id=site.site_id,
                    site_name=site.site_name,
                    mpan=site.mpan,
                    month_start=month_key,
                    billing_start=month_key,
                    billing_end=month_end(month_start_value).isoformat(),
                    billed_days=billed_days,
                    kwh=kwh,
                    market_reference_rate_gbp_per_kwh=market_price,
                    market_multiplier=DEFAULT_MARKET_MULTIPLIER,
                    network_adder_gbp_per_kwh=DEFAULT_DUOS_GBP_PER_KWH,
                    billed_unit_rate_gbp_per_kwh=unit_rate,
                    standing_charge_gbp_per_day=DEFAULT_STANDING_CHARGE_GBP_PER_DAY,
                    expected_standing_charge_gbp=expected_standing_charge,
                    billed_standing_charge_gbp=billed_standing_charge,
                    expected_total_gbp=expected_total,
                    billed_total_gbp=billed_total,
                    anomaly_seed=anomaly_seed,
                    notes=(
                        f"{TARGET_COMPANY} - {TARGET_REGION} baseline scenario"
                        if not anomaly_extra
                        else "Seeded supplier error: duplicate standing charge block"
                    ),
                )
            )
    return invoices


def run_generate_synthetic_invoices(args: argparse.Namespace) -> int:
    invoices = generate_synthetic_invoices(
        prices_path=args.prices,
        load_shape_path=args.load_shape,
        seed=args.seed,
    )
    write_csv_rows(args.output, [invoice.to_row() for invoice in invoices])
    total_anomaly = sum(
        invoice.billed_standing_charge_gbp - invoice.expected_standing_charge_gbp for invoice in invoices
    )
    print(
        f"Generated {len(invoices)} invoices across {SITE_COUNT} sites; "
        f"seeded standing-charge overbilling totals GBP {total_anomaly:.2f}."
    )
    return 0
