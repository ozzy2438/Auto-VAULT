"""Presentation-friendly HTML reporting for Auto-VAULT runs."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path

from .io import read_csv_rows, read_json


def _format_gbp(value: float) -> str:
    return f"GBP {value:,.2f}"


def _format_tco2e(value: float) -> str:
    return f"{value:,.3f} tCO2e"


def _metric_card(label: str, value: str, accent: str) -> str:
    return f"""
        <article class="metric-card">
          <div class="metric-accent {accent}"></div>
          <p class="metric-label">{escape(label)}</p>
          <p class="metric-value">{escape(value)}</p>
        </article>
    """


def _table(headers: list[str], rows: list[list[str]]) -> str:
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    row_html = "".join(
        "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"""
      <div class="table-shell">
        <table>
          <thead><tr>{header_html}</tr></thead>
          <tbody>{row_html}</tbody>
        </table>
      </div>
    """


def build_html_report(run_dir: Path) -> str:
    run_dir = run_dir.resolve()
    manifest = read_json(run_dir / "run_manifest.json")
    validation_summary = read_json(run_dir / "invoice_validation_summary.json")
    budget_summary = read_json(run_dir / "uk_budget_forecast_summary.json")
    finance_summary = read_json(run_dir / "uk_finance_summary.json")
    validation_results = read_csv_rows(run_dir / "invoice_validation_results.csv")
    emissions_rows = read_csv_rows(run_dir / "secr_emissions_summary.csv")
    accrual_rows = read_csv_rows(run_dir / "uk_month_end_accruals.csv")
    budget_rows = read_csv_rows(run_dir / "uk_budget_forecast.csv")

    flagged_rows = [row for row in validation_results if row["anomaly_flag"] == "True"]
    site_emissions = [row for row in emissions_rows if row["summary_level"] == "site"]
    company_emissions = next(row for row in emissions_rows if row["summary_level"] == "company")
    site_accruals = [row for row in accrual_rows if row["summary_level"] == "site"]
    company_budget_rows = [row for row in budget_rows if row["summary_level"] == "company"]
    peak_budget_month = max(company_budget_rows, key=lambda row: float(row["forecast_cost_gbp"]))

    anomaly_table = _table(
        ["Invoice", "Site", "Month", "Variance", "Reason"],
        [
            [
                row["invoice_id"],
                row["site_id"],
                row["month_start"],
                _format_gbp(float(row["variance_gbp"])),
                row["anomaly_reason"],
            ]
            for row in flagged_rows
        ],
    )
    emissions_table = _table(
        ["Entity", "kWh", "Scope 2"],
        [
            [
                row["entity_name"],
                f"{float(row['kwh']):,.2f} kWh",
                _format_tco2e(float(row["tco2e"])),
            ]
            for row in site_emissions
        ]
        + [[company_emissions["entity_name"], f"{float(company_emissions['kwh']):,.2f} kWh", _format_tco2e(float(company_emissions["tco2e"]))]],
    )
    accrual_table = _table(
        ["Entity", "Open Month", "Unbilled Days", "Accrual"],
        [
            [
                row["entity_name"],
                row["accrual_month"],
                row["unbilled_days"],
                _format_gbp(float(row["accrued_cost_gbp"])),
            ]
            for row in site_accruals
        ],
    )
    talk_track = [
        "This is a UK energy analytics workflow for a Birmingham manufacturing SME with three sites.",
        "The model recreates expected invoice costs from public-market assumptions and flags billing anomalies automatically.",
        "The same workflow converts usage into DEFRA Scope 2 emissions, then extends into a 12-month budget and month-end finance close outputs.",
        "The outcome is a tested, repeatable workflow that joins sustainability reporting, invoice validation, forecasting, and accrual logic.",
    ]

    metrics_html = "".join(
        [
            _metric_card("Invoices Validated", str(manifest["metrics"]["synthetic_invoice_count"]), "teal"),
            _metric_card("Flagged Anomalies", str(manifest["metrics"]["flagged_invoices"]), "copper"),
            _metric_card("Savings Opportunity", _format_gbp(float(manifest["metrics"]["savings_opportunity_gbp"])), "teal"),
            _metric_card("Scope 2 Total", _format_tco2e(float(manifest["metrics"]["company_tco2e"])), "slate"),
            _metric_card("Next 12M Budget", _format_gbp(float(manifest["metrics"]["company_budget_gbp"])), "copper"),
            _metric_card("Latest Accrual", _format_gbp(float(manifest["metrics"]["latest_month_accrual_gbp"])), "slate"),
        ]
    )
    talk_track_html = "".join(
        f"<li>{escape(line)}</li>"
        for line in talk_track
    )

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Auto-VAULT Presentation Report</title>
    <style>
      :root {{
        --bg: #f3efe7;
        --bg-2: #e4ece8;
        --card: rgba(255, 255, 255, 0.92);
        --ink: #17313a;
        --muted: #58727c;
        --line: rgba(23, 49, 58, 0.12);
        --teal: #1f7a78;
        --copper: #a55a2a;
        --slate: #355c6b;
        --shadow: 0 18px 40px rgba(23, 49, 58, 0.10);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: "Avenir Next", "Trebuchet MS", "Segoe UI", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(31, 122, 120, 0.16), transparent 26%),
          radial-gradient(circle at top right, rgba(165, 90, 42, 0.16), transparent 24%),
          linear-gradient(180deg, var(--bg), var(--bg-2));
      }}
      .page {{
        max-width: 1180px;
        margin: 0 auto;
        padding: 32px 20px 48px;
      }}
      .hero {{
        background: linear-gradient(135deg, rgba(23, 49, 58, 0.96), rgba(31, 122, 120, 0.92));
        color: #f8f6f1;
        border-radius: 28px;
        padding: 30px;
        box-shadow: var(--shadow);
      }}
      .eyebrow {{
        margin: 0 0 10px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 12px;
        opacity: 0.8;
      }}
      h1, h2 {{
        margin: 0 0 12px;
        font-family: Georgia, "Times New Roman", serif;
      }}
      .hero p {{
        max-width: 820px;
        line-height: 1.6;
        margin: 0;
        color: rgba(248, 246, 241, 0.88);
      }}
      .section {{
        margin-top: 24px;
        background: var(--card);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 24px;
        padding: 24px;
        box-shadow: var(--shadow);
      }}
      .metrics {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px;
      }}
      .metric-card {{
        position: relative;
        overflow: hidden;
        padding: 18px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid var(--line);
      }}
      .metric-accent {{
        position: absolute;
        inset: 0 auto 0 0;
        width: 8px;
      }}
      .metric-accent.teal {{ background: var(--teal); }}
      .metric-accent.copper {{ background: var(--copper); }}
      .metric-accent.slate {{ background: var(--slate); }}
      .metric-label {{
        margin: 0 0 8px 0;
        color: var(--muted);
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .metric-value {{
        margin: 0;
        font-size: 28px;
        line-height: 1.1;
        font-weight: 700;
      }}
      .two-col {{
        display: grid;
        grid-template-columns: 1.1fr 0.9fr;
        gap: 20px;
      }}
      .note-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 14px;
      }}
      .note {{
        border-radius: 18px;
        padding: 16px;
        background: rgba(31, 122, 120, 0.06);
        border: 1px solid rgba(31, 122, 120, 0.12);
      }}
      .note strong {{
        display: block;
        margin-bottom: 8px;
      }}
      .table-shell {{
        overflow-x: auto;
        border: 1px solid var(--line);
        border-radius: 16px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
      }}
      th, td {{
        text-align: left;
        padding: 12px 14px;
        border-bottom: 1px solid var(--line);
      }}
      th {{
        background: rgba(53, 92, 107, 0.07);
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.07em;
        font-size: 12px;
      }}
      tbody tr:last-child td {{
        border-bottom: none;
      }}
      ul {{
        margin: 0;
        padding-left: 18px;
        line-height: 1.7;
      }}
      .footer {{
        margin-top: 18px;
        color: var(--muted);
        font-size: 13px;
      }}
      @media (max-width: 860px) {{
        .two-col {{
          grid-template-columns: 1fr;
        }}
        .page {{
          padding: 20px 14px 36px;
        }}
        .hero, .section {{
          padding: 20px;
          border-radius: 20px;
        }}
      }}
    </style>
  </head>
  <body>
    <main class="page">
      <section class="hero">
        <p class="eyebrow">Auto-VAULT | UK Demo Report</p>
        <h1>Energy invoice validation, carbon reporting, budgeting, and finance close in one workflow.</h1>
        <p>
          This report turns the command-line run into a presentation-ready story for a Birmingham manufacturing SME.
          It shows what the workflow checked, what it found, and why the result matters commercially and for SECR-style reporting.
        </p>
      </section>

      <section class="section">
        <h2>Executive Snapshot</h2>
        <div class="metrics">{metrics_html}</div>
      </section>

      <section class="section two-col">
        <div>
          <h2>What This Run Proves</h2>
          <div class="note-grid">
            <div class="note">
              <strong>Invoice challenge</strong>
              The workflow recomputed expected supplier charges from benchmark market assumptions and isolated three duplicate standing-charge cases.
            </div>
            <div class="note">
              <strong>Sustainability view</strong>
              The same validated usage footprint was translated into DEFRA 2024 location-based Scope 2 emissions.
            </div>
            <div class="note">
              <strong>Budgeting</strong>
              Historical usage was rolled forward into a 12-month UK budget forecast with a documented planning basis.
            </div>
            <div class="note">
              <strong>Finance close</strong>
              The model produced a month-end accrual estimate that a finance stakeholder can discuss immediately.
            </div>
          </div>
        </div>
        <div>
          <h2>30-Second Talk Track</h2>
          <ul>{talk_track_html}</ul>
        </div>
      </section>

      <section class="section two-col">
        <div>
          <h2>Flagged Anomalies</h2>
          {anomaly_table}
        </div>
        <div>
          <h2>Budget and Close Highlights</h2>
          <div class="note-grid">
            <div class="note">
              <strong>Budget Basis</strong>
              {escape(budget_summary["budget_basis"])}
            </div>
            <div class="note">
              <strong>Peak Budget Month</strong>
              {escape(peak_budget_month["forecast_month"])} at {escape(_format_gbp(float(peak_budget_month["forecast_cost_gbp"])))}
            </div>
            <div class="note">
              <strong>Historical Variance</strong>
              {escape(_format_gbp(float(finance_summary["company_historical_variance_gbp"])))}
            </div>
            <div class="note">
              <strong>Latest Open Month</strong>
              {escape(finance_summary["open_month"])} close with {escape(_format_gbp(float(finance_summary["latest_month_accrual_gbp"])))}
            </div>
          </div>
        </div>
      </section>

      <section class="section two-col">
        <div>
          <h2>SECR Emissions Summary</h2>
          {emissions_table}
        </div>
        <div>
          <h2>Month-End Accrual by Site</h2>
          {accrual_table}
        </div>
      </section>

      <section class="section">
        <h2>How To Present This Live</h2>
        <ul>
          <li>Start with the six KPI cards and say the workflow validates invoices, quantifies savings, and extends into carbon and finance outputs.</li>
          <li>Move to the anomaly table and explain that the system identified three duplicate standing-charge issues worth {escape(_format_gbp(float(validation_summary["total_savings_opportunity_gbp"])))}.</li>
          <li>Show the SECR table to connect energy accounting with sustainability reporting and point to the total of {escape(_format_tco2e(float(company_emissions["tco2e"])))}.</li>
          <li>Finish on budget and accruals to show that the workflow is useful for finance planning, not just auditing past invoices.</li>
        </ul>
        <p class="footer">Generated from: {escape(str(run_dir))}</p>
      </section>
    </main>
  </body>
</html>
"""


def run_render_report(args: argparse.Namespace) -> int:
    html = build_html_report(args.run_dir)
    output_path = args.output or (args.run_dir / "presentation_report.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Presentation report written to {output_path}")
    return 0
