"""Markdown bracket export."""

from __future__ import annotations

from pathlib import Path

from brac7.models import Bracket


def export_markdown(bracket: Bracket, path: Path) -> Path:
    lines = [
        f"# {bracket.title}",
        "",
        f"- **Format:** {bracket.format_label}",
        f"- **Seeding:** {bracket.options.seeding.value}",
        f"- **Byes:** {'yes' if bracket.options.supports_byes else 'no'}",
        f"- **Bracket size:** {bracket.size}",
        f"- **Participants:** {len(bracket.participants)}",
        "",
        "## Participants",
        "",
    ]
    for p in bracket.participants:
        lines.append(f"{p.seed}. {p.name}")
    lines.extend(["", "## Matches", ""])
    for rnd in bracket.rounds:
        lines.append(f"### {rnd.name}")
        lines.append("")
        for m in rnd.matches:
            a = m.display_slot("a", bracket.options)
            b = m.display_slot("b", bracket.options)
            bye = " *(bye)*" if m.is_bye else ""
            lines.append(f"- **{m.label or m.id}** — {a} vs {b}{bye}")
        lines.append("")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
