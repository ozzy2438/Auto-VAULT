# Auto-VAULT

Auto-VAULT is a UK-focused energy invoice validation and Scope 2 reporting MVP for SMEs subject to SECR-style data governance requirements.

The first milestone delivers:

- synthetic but market-grounded electricity invoices for a Birmingham manufacturer
- deterministic validation against versioned wholesale and policy assumptions
- DEFRA 2024 location-based Scope 2 calculations
- a small CLI for repeatable portfolio demos

This repository intentionally starts with checked-in sample data derived from official public sources so the demo is reproducible without live API keys.

The implementation will be built in small, reviewable commits:

1. bootstrap the repo
2. scaffold the Python package and CLI
3. add source manifests and sample inputs
4. generate synthetic invoices
5. validate invoice charges
6. calculate emissions and SECR summaries
7. add an end-to-end demo command
8. add tests and a concise runbook
