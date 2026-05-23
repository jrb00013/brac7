"""Mermaid flowchart export for brackets."""

from __future__ import annotations

from pathlib import Path

from brac7.models import Bracket


def _safe_id(match_id: str) -> str:
    return match_id.replace("-", "_")


def _style_class(match, bracket) -> str:
    if match.is_bye:
        return ":::bye"
    return ""


def export_mermaid(bracket: Bracket, path: Path) -> Path:
    lines = [
        "---",
        f"title: {bracket.title}",
        "---",
        "flowchart TB",
        "",
        "    classDef default fill:#1e2d42,stroke:#3d8bfd,color:#e7ecf3",
        "    classDef bye fill:#2a3a28,stroke:#4a7a4a,color:#8fbc8f,stroke-dasharray:4 3",
        "    classDef champ fill:#2a3d1a,stroke:#ffd700,color:#ffd700",
        "",
        f"    subgraph meta[\"{bracket.format_label} | {len(bracket.participants)} entrants / size {bracket.size}\"]",
        "        direction TB",
        "    end",
        "",
    ]

    for i, rnd in enumerate(bracket.rounds):
        subgraph_id = f"round_{rnd.index}"
        lines.append(f"    subgraph {subgraph_id}[\"{rnd.name}\"]")
        for m in rnd.matches:
            node_id = _safe_id(m.id)
            a = m.display_slot("a", bracket.options).replace('"', "'")
            b = m.display_slot("b", bracket.options).replace('"', "'")
            bye_tag = " <i>BYE</i>" if m.is_bye else ""
            label = f"{m.id}<br/>{a}<br/>vs<br/>{b}{bye_tag}"
            lines.append(f'        {node_id}["{label}"]{_style_class(m, bracket)}')
        lines.append("    end")
        lines.append("")

    final_round = bracket.rounds[-1] if bracket.rounds else None
    for m in bracket.all_matches():
        for src in m.feeds_from:
            lines.append(f"    {_safe_id(src)} --> {_safe_id(m.id)}")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines) + "\n"
    # Also write a .md wrapper for GitHub rendering
    md_path = path if path.suffix == ".md" else path.with_suffix(".md")
    md_content = f"# {bracket.title}\n\n```mermaid\n{content}```\n"
    md_path.write_text(md_content, encoding="utf-8")
    if path.suffix == ".mmd":
        path.write_text(content, encoding="utf-8")
    return md_path
