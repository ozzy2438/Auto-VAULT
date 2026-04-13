# Auto-VAULT

Auto-VAULT is a UK-focused energy invoice validation and Scope 2 reporting MVP for SMEs that need SECR-ready energy governance.

The current milestone demonstrates a Birmingham metalworking company with three sites. It uses versioned official-source samples plus synthetic invoice generation to show how a portfolio can:

- recreate supplier invoices from market assumptions
- flag anomalous bills and estimate savings opportunity
- convert electricity usage into DEFRA 2024 location-based Scope 2 emissions
- run end to end from a single CLI command

## Scenario

- Company: `Birmingham Metal Works Ltd`
- Region: `United Kingdom (West Midlands)`
- Portfolio: `3 sites`
- Coverage: `24 monthly billing periods`
- Output volume: `72 synthetic invoices`
- Seeded finding: `3 duplicate standing-charge anomalies worth GBP 1,840.00`

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
- `auto-vault run-demo`

All curated outputs are written under `data/curated/` and include:

- `synthetic_invoices.csv`
- `invoice_validation_results.csv`
- `invoice_validation_summary.json`
- `secr_emissions_summary.csv`
- `run_manifest.json`

## Expected Demo Outcome

The deterministic seed currently produces:

- `72` invoices
- `3` flagged anomalies
- `GBP 1,840.00` savings opportunity
- `170.753 tCO2e` company Scope 2 total

## Tests

```bash
.venv/bin/python -m pytest
```

The test suite covers deterministic generation, validation math, emissions outputs, and the end-to-end demo manifest.
