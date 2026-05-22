"""PDF bracket export via ReportLab."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from brac7.models import Bracket


def export_pdf(bracket: Bracket, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=landscape(letter),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BracketTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    story = [
        Paragraph(bracket.title, title_style),
        Paragraph(
            f"{bracket.format_label} · {bracket.options.seeding.value} seeding · "
            f"{len(bracket.participants)} entrants · bracket size {bracket.size}",
            styles["Normal"],
        ),
        Spacer(1, 0.2 * inch),
    ]

    seed_data = [["Seed", "Participant"]] + [[p.seed, p.name] for p in bracket.participants]
    seed_table = Table(seed_data, colWidths=[0.6 * inch, 5.5 * inch])
    seed_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FA")]),
            ]
        )
    )
    story.extend([Paragraph("Participants", styles["Heading2"]), seed_table, Spacer(1, 0.25 * inch)])

    for rnd in bracket.rounds:
        story.append(Paragraph(rnd.name, styles["Heading2"]))
        rows = [["Match", "Slot A", "Slot B", "Notes"]]
        for m in rnd.matches:
            note = "BYE" if m.is_bye else ""
            rows.append(
                [
                    m.label or m.id,
                    m.display_slot("a", bracket.options),
                    m.display_slot("b", bracket.options),
                    note,
                ]
            )
        t = Table(rows, colWidths=[2.2 * inch, 2.5 * inch, 2.5 * inch, 0.8 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F5496")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.extend([t, Spacer(1, 0.15 * inch)])

    doc.build(story)
    return path
