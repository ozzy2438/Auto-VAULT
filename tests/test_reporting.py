from pathlib import Path

from auto_vault.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_render_report_creates_shareable_html(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(ROOT)

    main(["run-demo", "--output-dir", str(tmp_path), "--seed", "2438"])
    output_path = tmp_path / "auto_vault_report.html"
    exit_code = main(["render-report", "--run-dir", str(tmp_path), "--output", str(output_path)])
    html = output_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert output_path.exists()
    assert "Executive Snapshot" in html
    assert "GBP 1,840.00" in html
    assert "1,707.530 tCO2e" in html
    assert "GBP 490,097.29" in html
