from pathlib import Path

from brac7.engine import BracketEngine
from brac7.exporters import export_markdown, export_mermaid, export_pdf, export_xlsx
from brac7.models import BracketOptions, TournamentFormat


def test_all_exports(tmp_path: Path):
    bracket = BracketEngine(
        BracketOptions(title="Test", format=TournamentFormat.SINGLE_ELIMINATION)
    ).generate(["One", "Two", "Three", "Four"])
    assert export_xlsx(bracket, tmp_path / "t.xlsx").exists()
    assert export_pdf(bracket, tmp_path / "t.pdf").exists()
    assert export_markdown(bracket, tmp_path / "t.md").exists()
    assert export_mermaid(bracket, tmp_path / "t.mmd").exists()
