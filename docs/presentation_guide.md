# Auto-VAULT Presentation Guide

## Fastest Way to Show the Project

Run:

```bash
cd "/Users/osmanorka/Documents/New project"
.venv/bin/auto-vault run-demo --output-dir data/curated/my_run
```

Then open:

- [presentation_report.html](/Users/osmanorka/Documents/New project/data/curated/my_run/presentation_report.html)

This file is the easiest visual artifact to show in an interview, live call, or application follow-up.

## Best 3-Minute Demo Flow

### 1. Start with the big picture

Say:

> I built a UK energy analytics workflow for a Birmingham manufacturing SME. It validates invoices, calculates Scope 2 emissions, produces a 12-month budget, and generates month-end accrual outputs in one tested workflow.

Show:

- the top section of `presentation_report.html`

### 2. Show the commercial value

Say:

> The workflow checked 72 invoices across a meaningful industrial cost base, found 3 billing anomalies, and identified GBP 1,840.00 in savings opportunity.

Show:

- the KPI cards
- the flagged anomaly table

### 3. Show the sustainability value

Say:

> The same validated electricity data is translated into DEFRA 2024 location-based Scope 2 emissions, so the workflow supports SECR-style reporting as well as invoice challenge.

Show:

- the SECR emissions summary table

### 4. Show the finance value

Say:

> This is not only an audit tool. It also produces a 12-month UK energy budget of roughly GBP 490k and a month-end accrual estimate of about GBP 9.6k, which makes it useful for finance and planning teams.

Show:

- the budget and close highlights section
- the accrual table

### 5. Close with the engineering point

Say:

> I packaged the workflow as a tested Python CLI rather than a notebook-only prototype, so it is reproducible and easy to rerun with controlled inputs.

Show:

- [README.md](/Users/osmanorka/Documents/New project/README.md)
- [docs/uk_case_study.md](/Users/osmanorka/Documents/New project/docs/uk_case_study.md)

## What to Send If You Cannot Present Live

If you need to send material by email or application portal, send these three things:

1. a screenshot or PDF export of `presentation_report.html`
2. the GitHub repository link
3. the short case study in `docs/uk_case_study.md`

## Best Screenshot Order

If you want only 4 screenshots, use this order:

1. KPI cards from `presentation_report.html`
2. anomaly table
3. SECR emissions table
4. budget and accrual section

## What the Audience Should Remember

After your explanation, the other person should leave with these ideas:

- you can work with energy invoice data
- you understand sustainability reporting, not only coding
- you can connect operations, finance, and ESG in one workflow
- you build reproducible and testable analytics tools

## One-Line Summary for a CV or Email

Built a UK-focused energy analytics MVP that validates supplier invoices, quantifies savings opportunities, calculates DEFRA Scope 2 emissions, produces a 12-month budget forecast, and generates month-end accrual outputs in a tested Python CLI workflow.
