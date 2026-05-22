"""Excel bracket workbook export."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from brac7.models import Bracket


def export_xlsx(bracket: Bracket, path: Path) -> Path:
    wb = Workbook()
    ws_meta = wb.active
    ws_meta.title = "Info"
    header_font = Font(bold=True, size=12)
    fill = PatternFill("solid", fgColor="D9E1F2")

    meta = [
        ("Title", bracket.title),
        ("Format", bracket.format_label),
        ("Seeding", bracket.options.seeding.value),
        ("Byes", "Yes" if bracket.options.supports_byes else "No"),
        ("Max participants", bracket.options.max_participants or "—"),
        ("Bracket size", bracket.size),
        ("Entrants", len(bracket.participants)),
        ("Match format", bracket.options.match_format.value),
    ]
    for row, (k, v) in enumerate(meta, start=1):
        ws_meta.cell(row, 1, k).font = header_font
        ws_meta.cell(row, 2, v)

    ws_p = wb.create_sheet("Participants")
    ws_p.append(["Seed", "Name"])
    for cell in ws_p[1]:
        cell.font = header_font
        cell.fill = fill
    for p in bracket.participants:
        ws_p.append([p.seed, p.name])

    ws_m = wb.create_sheet("Matches")
    ws_m.append(
        ["Round", "Match ID", "Bracket", "Slot A", "Slot B", "Bye", "Label", "Feeds From"]
    )
    for cell in ws_m[1]:
        cell.font = header_font
        cell.fill = fill
    for rnd in bracket.rounds:
        for m in rnd.matches:
            ws_m.append(
                [
                    rnd.name,
                    m.id,
                    m.bracket,
                    m.display_slot("a", bracket.options),
                    m.display_slot("b", bracket.options),
                    "Yes" if m.is_bye else "",
                    m.label,
                    ", ".join(m.feeds_from),
                ]
            )

    ws_v = wb.create_sheet("Bracket View")
    ws_v.append(["Round", "Match", "Competitor 1", "vs", "Competitor 2"])
    for cell in ws_v[1]:
        cell.font = header_font
        cell.fill = fill
    col = 1
    for rnd in bracket.rounds:
        row = 2
        for m in rnd.matches:
            ws_v.cell(row, col, rnd.name)
            ws_v.cell(row, col + 1, m.id)
            ws_v.cell(row, col + 2, m.display_slot("a", bracket.options))
            ws_v.cell(row, col + 3, "vs")
            ws_v.cell(row, col + 4, m.display_slot("b", bracket.options))
            for c in range(col, col + 5):
                ws_v.cell(row, c).alignment = Alignment(vertical="center")
            row += 2
        col += 6

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path
