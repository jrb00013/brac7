from __future__ import annotations

from pathlib import Path

from brac7.models import Bracket


def _bracket_ascii(bracket: Bracket) -> list[str]:
    lines = []
    max_rounds = len(bracket.rounds)
    if max_rounds == 0:
        return lines

    for i, rnd in enumerate(bracket.rounds):
        indent = "  " * (max_rounds - i - 1)
        lines.append(f"{indent}┌─ {rnd.name} ─────────────────────")
        for m in rnd.matches:
            a = m.display_slot("a", bracket.options)
            b = m.display_slot("b", bracket.options)
            bye = " (bye)" if m.is_bye else ""
            label = m.label or m.id
            match_line = f"{indent}│ {label}: {a} vs {b}{bye}"
            if m.is_bye:
                match_line += " ⏭"
            lines.append(match_line)
        lines.append(f"{indent}└──────────────────────────────")
        lines.append("")
    return lines


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

    lines.extend(["", "---", ""])
    lines.extend(_bracket_ascii(bracket))

    lines.extend(["", "## Matches", ""])
    for rnd in bracket.rounds:
        lines.append(f"### {rnd.name}")
        lines.append("")
        lines.append("| Match | Competitor 1 | vs | Competitor 2 | Note |")
        lines.append("|-------|-------------|:--:|-------------|------|")
        for m in rnd.matches:
            a = m.display_slot("a", bracket.options)
            b = m.display_slot("b", bracket.options)
            bye = "bye" if m.is_bye else ""
            lines.append(f"| {m.label or m.id} | {a} | vs | {b} | {bye} |")
        lines.append("")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
