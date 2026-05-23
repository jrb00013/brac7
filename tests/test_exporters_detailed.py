import json
from pathlib import Path

from brac7.engine import BracketEngine
from brac7.exporters import (
    export_csv,
    export_html,
    export_json,
    export_markdown,
    export_mermaid,
    export_pdf,
    export_xlsx,
)
from brac7.models import BracketOptions, TournamentFormat


def test_json_export_roundtrip(tmp_path: Path):
    bracket = BracketEngine(
        BracketOptions(title="JSON Test")
    ).generate(["A", "B", "C", "D"])
    p = export_json(bracket, tmp_path / "test.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["title"] == "JSON Test"
    assert len(data["participants"]) == 4
    assert len(data["rounds"]) > 0


def test_csv_export_content(tmp_path: Path):
    bracket = BracketEngine(
        BracketOptions(title="CSV Test")
    ).generate(["A", "B", "C", "D"])
    p = export_csv(bracket, tmp_path / "test.csv")
    content = p.read_text(encoding="utf-8")
    assert "Title" in content
    assert "CSV Test" in content
    assert "Seed" in content and "Name" in content


def test_html_export_content(tmp_path: Path):
    bracket = BracketEngine(
        BracketOptions(title="HTML Test")
    ).generate(["A", "B", "C", "D"])
    p = export_html(bracket, tmp_path / "test.html")
    content = p.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "HTML Test" in content
    assert "Participants" in content


def test_all_new_exporters_work(tmp_path: Path):
    bracket = BracketEngine(
        BracketOptions(title="New Exports", format=TournamentFormat.ROUND_ROBIN)
    ).generate(["A", "B", "C", "D"])
    assert export_json(bracket, tmp_path / "t.json").exists()
    assert export_csv(bracket, tmp_path / "t.csv").exists()
    assert export_html(bracket, tmp_path / "t.html").exists()
    assert export_markdown(bracket, tmp_path / "t.md").exists()
    assert export_mermaid(bracket, tmp_path / "t.mmd").exists()
    assert export_xlsx(bracket, tmp_path / "t.xlsx").exists()
    assert export_pdf(bracket, tmp_path / "t.pdf").exists()
