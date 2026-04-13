"""Shared record contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class InvoiceRecord:
    invoice_id: str
    site_id: str
    site_name: str
    mpan: str
    month_start: str
    billing_start: str
    billing_end: str
    billed_days: int
    kwh: float
    market_reference_rate_gbp_per_kwh: float
    market_multiplier: float
    network_adder_gbp_per_kwh: float
    billed_unit_rate_gbp_per_kwh: float
    standing_charge_gbp_per_day: float
    expected_standing_charge_gbp: float
    billed_standing_charge_gbp: float
    expected_total_gbp: float
    billed_total_gbp: float
    anomaly_seed: str
    notes: str

    def to_row(self) -> dict[str, object]:
        return asdict(self)
