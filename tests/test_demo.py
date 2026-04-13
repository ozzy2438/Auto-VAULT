import json
from pathlib import Path

from auto_vault.cli import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def test_run_demo_writes_expected_artifacts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(ROOT)

    exit_code = main(["run-demo", "--output-dir", str(tmp_path), "--seed", "2438"])
    manifest = json.loads((tmp_path / "run_manifest.json").read_text())
    expected_metrics = json.loads((FIXTURES / "expected_demo_metrics.json").read_text())

    assert exit_code == 0
    assert (tmp_path / "synthetic_invoices.csv").exists()
    assert (tmp_path / "invoice_validation_results.csv").exists()
    assert (tmp_path / "invoice_validation_summary.json").exists()
    assert (tmp_path / "secr_emissions_summary.csv").exists()
    assert manifest["metrics"] == expected_metrics
