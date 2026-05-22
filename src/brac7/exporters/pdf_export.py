"""PDF bracket export — visual diagram with boxes, connectors, and formatted appendix."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from brac7.models import Bracket, MatchNode

PAGE_W, PAGE_H = landscape(letter)
MARGIN = 36
BOX_W = 118
SLOT_H = 14
MATCH_PAD = 4
ROUND_GAP = 52
HEADER_H = 52


def _truncate(text: str, max_len: int = 32) -> str:
    text = (text or "TBD").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _slot_label(match: MatchNode, side: str, bracket: Bracket) -> str:
    raw = match.display_slot(side, bracket.options)
    if raw == "BYE":
        return "BYE"
    if raw == "TBD":
        return "—"
    return _truncate(raw, 30)


def _winners_rounds(bracket: Bracket) -> list:
    return [r for r in bracket.rounds if "loser" not in r.name.lower()]


def _compute_y_centers(match_counts: list[int], block_h: float) -> list[list[float]]:
    """Even vertical spacing per round (handles play-in ≠ half of next round)."""
    if not match_counts:
        return []
    max_n = max(match_counts)
    unit = block_h * 2
    total_span = unit * max(max_n - 1, 1) + block_h * 2
    levels: list[list[float]] = []
    for n in match_counts:
        if n <= 1:
            levels.append([total_span / 2])
            continue
        step = (total_span - 2 * block_h) / (n - 1)
        levels.append([block_h + i * step for i in range(n)])
    return levels


def _draw_match_box(
    c: canvas.Canvas,
    x: float,
    y_center: float,
    match: MatchNode,
    bracket: Bracket,
    box_w: float,
    block_h: float,
) -> tuple[float, float, float, float]:
    top = y_center + block_h
    bottom = y_center - block_h
    right = x + box_w
    mid = y_center

    fill = colors.HexColor("#1e2d42") if not match.is_bye else colors.HexColor("#2a3a28")
    border = colors.HexColor("#3d8bfd")

    c.setFillColor(fill)
    c.setStrokeColor(border)
    c.setLineWidth(1.2)
    c.roundRect(x, bottom, box_w, top - bottom, 4, fill=1, stroke=1)

    c.setStrokeColor(colors.HexColor("#4a5f7a"))
    c.setLineWidth(0.6)
    c.line(x + 2, mid, right - 2, mid)

    c.setFillColor(colors.white)
    c.setFont("Helvetica", 7)
    c.drawString(x + MATCH_PAD, mid + 3, _slot_label(match, "a", bracket))
    c.drawString(x + MATCH_PAD, bottom + 4, _slot_label(match, "b", bracket))

    if match.is_bye:
        c.setFillColor(colors.HexColor("#8fbc8f"))
        c.setFont("Helvetica-Oblique", 6)
        c.drawRightString(right - MATCH_PAD, top - 8, "BYE")

    return x, bottom, right, top


def _draw_connector(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
    c.setStrokeColor(colors.HexColor("#6b8cae"))
    c.setLineWidth(0.8)
    mid_x = (x1 + x2) / 2
    c.line(x1, y1, mid_x, y1)
    c.line(mid_x, y1, mid_x, y2)
    c.line(mid_x, y2, x2, y2)


def _draw_bracket_diagram(c: canvas.Canvas, bracket: Bracket) -> None:
    rounds = _winners_rounds(bracket)
    if not rounds:
        return

    match_counts = [len(r.matches) for r in rounds]
    num_rounds = len(rounds)
    block_h = SLOT_H + 2

    levels = _compute_y_centers(match_counts, block_h)
    total_span = levels[0][-1] - levels[0][0] + block_h * 2 if levels[0] else block_h * 2
    drawable_h = PAGE_H - MARGIN * 2 - HEADER_H - 24
    scale = min(1.0, drawable_h / total_span) if total_span > 0 else 1.0
    scale = max(scale, 0.28)

    block_h *= scale
    box_w = BOX_W * scale
    round_gap = ROUND_GAP * scale

    base_y = PAGE_H - MARGIN - HEADER_H
    levels_top = [[base_y - y * scale for y in level] for level in levels]

    diagram_w = num_rounds * (box_w + round_gap) - round_gap
    start_x = MARGIN + max(0, (PAGE_W - 2 * MARGIN - diagram_w) / 2)

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#2F5496"))
    c.drawString(MARGIN, PAGE_H - MARGIN - 14, bracket.title)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(
        MARGIN,
        PAGE_H - MARGIN - 28,
        f"{bracket.format_label} · {len(bracket.participants)} entrants · "
        f"bracket {bracket.size}",
    )

    for r_idx, rnd in enumerate(rounds):
        rx = start_x + r_idx * (box_w + round_gap)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#2F5496"))
        c.drawCentredString(rx + box_w / 2, base_y + 14, rnd.name)

    match_bounds: dict[str, tuple[float, float, float, float]] = {}

    for r_idx, rnd in enumerate(rounds):
        rx = start_x + r_idx * (box_w + round_gap)
        for m_idx, match in enumerate(rnd.matches):
            yc = levels_top[r_idx][m_idx]
            match_bounds[match.id] = _draw_match_box(
                c, rx, yc, match, bracket, box_w, block_h
            )

    for rnd in rounds:
        for match in rnd.matches:
            if len(match.feeds_from) != 2:
                continue
            child = match_bounds.get(match.id)
            if not child:
                continue
            cx_left = child[0]
            cy = (child[1] + child[3]) / 2
            for fid in match.feeds_from:
                parent = match_bounds.get(fid)
                if not parent:
                    continue
                _draw_connector(c, parent[2], (parent[1] + parent[3]) / 2, cx_left, cy)

    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(
        MARGIN,
        MARGIN + 8,
        "Each box = one match (top slot vs bottom). Lines show who advances.",
    )


def _wrap_lines(text: str, max_chars: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = ""
    for w in words:
        candidate = f"{current} {w}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w if len(w) <= max_chars else _truncate(w, max_chars)
    if current:
        lines.append(current)
    return lines or [""]


def _draw_appendix_pages(c: canvas.Canvas, bracket: Bracket) -> None:
    """Formatted participant list and match schedule (wrapped rows, grid lines)."""
    y = PAGE_H - MARGIN

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#2F5496"))
    c.drawString(MARGIN, y, "Participants")
    y -= 22

    c.setFillColor(colors.HexColor("#4472C4"))
    c.rect(MARGIN, y - 14, PAGE_W - 2 * MARGIN, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN + 6, y - 10, "Seed")
    c.drawString(MARGIN + 50, y - 10, "Name")
    y -= 18

    c.setFont("Helvetica", 7)
    for i, p in enumerate(bracket.participants):
        lines = _wrap_lines(p.name, 100)
        row_px = 12 + (len(lines[:4]) - 1) * 9
        if y < MARGIN + 120:
            c.showPage()
            y = PAGE_H - MARGIN
            c.setFont("Helvetica-Bold", 12)
            c.drawString(MARGIN, y, "Participants (continued)")
            y -= 24
            c.setFont("Helvetica", 7)

        if i % 2 == 0:
            c.setFillColor(colors.HexColor("#EEF2FA"))
            c.rect(MARGIN, y - row_px + 2, PAGE_W - 2 * MARGIN, row_px, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.drawString(MARGIN + 6, y - 8, str(p.seed))
        for j, line in enumerate(lines[:4]):
            c.drawString(MARGIN + 50, y - 8 - j * 9, line)
        y -= row_px

    y -= 24
    if y < MARGIN + 200:
        c.showPage()
        y = PAGE_H - MARGIN

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#2F5496"))
    c.drawString(MARGIN, y, "Match schedule")
    y -= 20

    col_round, col_match, col_a, col_b = MARGIN, MARGIN + 90, MARGIN + 160, MARGIN + 400

    c.setFillColor(colors.HexColor("#2F5496"))
    c.rect(MARGIN, y - 14, PAGE_W - 2 * MARGIN, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(col_round + 4, y - 10, "Round")
    c.drawString(col_match + 4, y - 10, "Match")
    c.drawString(col_a + 4, y - 10, "Top slot")
    c.drawString(col_b + 4, y - 10, "Bottom slot")
    y -= 18

    c.setFont("Helvetica", 7)
    for rnd in _winners_rounds(bracket):
        for m in rnd.matches:
            a_lines = _wrap_lines(_slot_label(m, "a", bracket), 44)
            b_lines = _wrap_lines(_slot_label(m, "b", bracket), 44)
            row_lines = max(len(a_lines), len(b_lines), 1)
            row_px = 10 + (row_lines - 1) * 9

            if y < MARGIN + 40:
                c.showPage()
                y = PAGE_H - MARGIN - 20
                c.setFont("Helvetica-Bold", 12)
                c.drawString(MARGIN, y, "Match schedule (continued)")
                y -= 22
                c.setFont("Helvetica", 7)

            c.setStrokeColor(colors.HexColor("#cccccc"))
            c.setLineWidth(0.35)
            c.line(MARGIN, y - row_px + 2, PAGE_W - MARGIN, y - row_px + 2)

            c.setFillColor(colors.black)
            c.drawString(col_round + 4, y - 8, _truncate(rnd.name, 16))
            c.drawString(col_match + 4, y - 8, m.id)
            for j, line in enumerate(a_lines[:5]):
                c.drawString(col_a + 4, y - 8 - j * 9, line)
            for j, line in enumerate(b_lines[:5]):
                c.drawString(col_b + 4, y - 8 - j * 9, line)
            y -= row_px


def export_pdf(bracket: Bracket, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(path), pagesize=landscape(letter))
    # Page 1: visual bracket (boxes + connectors)
    _draw_bracket_diagram(c, bracket)
    c.showPage()
    # Page 2+: wrapped participant table + match schedule
    _draw_appendix_pages(c, bracket)
    c.save()
    return path
