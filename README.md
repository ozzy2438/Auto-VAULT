# Auto-VAULT

Auto-VAULT is a UK-focused energy invoice validation and Scope 2 reporting MVP for mid-sized industrial and commercial energy users that need SECR-ready governance.

The current milestone demonstrates a multi-site West Midlands industrial portfolio. It uses versioned official-source samples plus synthetic invoice generation to show how a portfolio can:

- recreate supplier invoices from market assumptions
- flag anomalous bills and estimate savings opportunity
- convert electricity usage into DEFRA 2024 location-based Scope 2 emissions
- build a 12-month UK energy budget forecast
- produce finance-style monthly reporting and month-end accruals
- run end to end from a single CLI command

## Scenario

- Company: `Birmingham Metal Works Ltd`
- Region: `United Kingdom (West Midlands)`
- Portfolio: `12 sites`
- Coverage: `36 monthly billing periods`
- Output volume: `432 synthetic invoices`
- Seeded finding: `3 duplicate standing-charge anomalies worth GBP 1,840.00`
- Forecast layer: `12-month UK budget forecast`
- Finance layer: `monthly actual-vs-benchmark reporting and month-end accrual`
- Operating scale: `~£5.57m historical spend across ~47.65 GWh over 36 months`

## Data Provenance

Checked-in source samples live under [data/sources](/Users/osmanorka/Documents/New project/data/sources) and are tracked in [data/sources/manifest.json](/Users/osmanorka/Documents/New project/data/sources/manifest.json).

- ENTSO-E Transparency Platform: monthly day-ahead electricity price samples
- National Grid ESO Data Portal: monthly seasonal demand-shape samples
- UK Government GHG Conversion Factors 2024: DEFRA location-based electricity factor

The repository intentionally avoids live API calls in phase 1 so the demo is reproducible without credentials.

## Quickstart

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/auto-vault run-demo
```

If you do not want to install the package yet, use:

```bash
PYTHONPATH=src python3 -m auto_vault run-demo
```

## CLI Commands

- `auto-vault generate-synthetic-invoices`
- `auto-vault validate-invoices`
- `auto-vault calculate-emissions`
- `auto-vault forecast-budget`
- `auto-vault build-finance-report`
- `auto-vault render-report`
- `auto-vault run-demo`

All curated outputs are written under `data/curated/` and include:

- `synthetic_invoices.csv`
- `invoice_validation_results.csv`
- `invoice_validation_summary.json`
- `secr_emissions_summary.csv`
- `uk_budget_forecast.csv`
- `uk_budget_forecast_summary.json`
- `uk_finance_monthly_report.csv`
- `uk_month_end_accruals.csv`
- `uk_finance_summary.json`
- `presentation_report.html`
- `run_manifest.json`

## Expected Demo Outcome

The deterministic seed currently produces:

- `432` invoices
- `3` flagged anomalies
- `GBP 1,840.00` savings opportunity
- `9,864.295 tCO2e` company Scope 2 total
- `GBP 1,905,615.06` next-12-month budget
- `GBP 36,996.47` month-end accrual on the latest close

## Portfolio Positioning

This project is designed to present a UK energy and sustainability analytics workflow in a way that is easy to discuss on a CV or in interview:

- invoice validation and retailer-cost challenge
- sustainability reporting with auditable public-source provenance
- budgeting and forecasting for energy spend
- finance-style monthly reporting and accrual logic
- reproducible Python package, CLI, and tests instead of a notebook-only demo

For a concise interview narrative, see [docs/uk_case_study.md](/Users/osmanorka/Documents/New project/docs/uk_case_study.md).
For a step-by-step visual handoff, see [docs/presentation_guide.md](/Users/osmanorka/Documents/New project/docs/presentation_guide.md).

## Tests

```bash
.venv/bin/python -m pytest
```

The test suite covers deterministic generation, validation math, emissions outputs, and the end-to-end demo manifest.
