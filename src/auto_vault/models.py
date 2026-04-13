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

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "InvoiceRecord":
        return cls(
            invoice_id=row["invoice_id"],
            site_id=row["site_id"],
            site_name=row["site_name"],
            mpan=row["mpan"],
            month_start=row["month_start"],
            billing_start=row["billing_start"],
            billing_end=row["billing_end"],
            billed_days=int(row["billed_days"]),
            kwh=float(row["kwh"]),
            market_reference_rate_gbp_per_kwh=float(row["market_reference_rate_gbp_per_kwh"]),
            market_multiplier=float(row["market_multiplier"]),
            network_adder_gbp_per_kwh=float(row["network_adder_gbp_per_kwh"]),
            billed_unit_rate_gbp_per_kwh=float(row["billed_unit_rate_gbp_per_kwh"]),
            standing_charge_gbp_per_day=float(row["standing_charge_gbp_per_day"]),
            expected_standing_charge_gbp=float(row["expected_standing_charge_gbp"]),
            billed_standing_charge_gbp=float(row["billed_standing_charge_gbp"]),
            expected_total_gbp=float(row["expected_total_gbp"]),
            billed_total_gbp=float(row["billed_total_gbp"]),
            anomaly_seed=row["anomaly_seed"],
            notes=row["notes"],
        )


@dataclass(frozen=True, slots=True)
class ValidationResult:
    invoice_id: str
    site_id: str
    month_start: str
    expected_total_gbp: float
    billed_total_gbp: float
    variance_gbp: float
    variance_pct: float
    anomaly_flag: bool
    anomaly_reason: str

    def to_row(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EmissionsResult:
    summary_level: str
    entity_id: str
    entity_name: str
    period_start: str
    period_end: str
    kwh: float
    defra_factor_kgco2e_per_kwh: float
    kgco2e: float
    tco2e: float
    methodology: str

    def to_row(self) -> dict[str, object]:
        return asdict(self)
