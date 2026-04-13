# Auto-VAULT UK Case Study

## Project in One Sentence

I built a UK-focused energy analytics MVP that validates supplier invoices, calculates DEFRA Scope 2 emissions, produces a 12-month budget forecast, and generates finance-style month-end accruals for a Birmingham manufacturing SME.

## Problem

Many SMEs still manage electricity invoices manually. That creates three common problems:

1. overbilling is hard to spot
2. SECR-style carbon reporting is slow and error-prone
3. finance teams need better energy budgeting and month-end visibility

## What I Designed

I designed a reproducible Python package and CLI with five connected layers:

1. official-source sample inputs with provenance tracking
2. synthetic but market-grounded UK invoice generation
3. invoice validation against benchmark market assumptions
4. DEFRA 2024 Scope 2 emissions summaries
5. UK budgeting, monthly finance reporting, and month-end accrual outputs

## Tools and Methods

- Python package + CLI
- CSV and JSON outputs for portability
- official-source samples from ENTSO-E, National Grid ESO, and DEFRA
- deterministic synthetic data for privacy-safe demonstration
- pytest-based regression tests
- Git/GitHub with step-by-step commit history

## Workflow

1. start from source samples and internal planning assumptions
2. generate 72 synthetic invoices across 3 UK sites
3. recompute expected invoice totals from wholesale price, tariff multiplier, network adder, and standing charge
4. flag anomalies and quantify savings opportunity
5. convert electricity use to location-based Scope 2 emissions
6. project a 12-month budget using trailing same-month actuals and efficiency targets
7. generate monthly finance outputs and month-end accruals for the latest close
8. package everything into a single `run-demo` command and test it end to end

## Outputs and Impact

The deterministic demo currently shows:

- `72` invoice records
- `3` duplicate-standing-charge anomalies
- `GBP 1,840.00` savings opportunity
- `170.753 tCO2e` company Scope 2 total
- `GBP 47,339.87` next-12-month UK budget
- `GBP 932.63` latest month-end accrual

## Why This Is Strong for Energy and Financial Analysis Roles

This project shows that I can connect energy data, finance logic, and sustainability reporting in one workflow. It demonstrates:

- analytical problem solving
- invoice validation and retailer challenge logic
- carbon reporting fundamentals
- budget and accrual thinking
- reproducible, testable data tooling

## Short Interview Version

I built a UK energy invoice validation and reporting MVP for a Birmingham manufacturer. It uses official public-source samples plus synthetic invoice data to detect overbilling, calculate DEFRA Scope 2 emissions, produce a 12-month energy budget, and generate month-end accrual outputs. I packaged it as a tested Python CLI so the whole workflow can be rerun in one command.
