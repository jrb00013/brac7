"""Mermaid flowchart export for brackets."""

from __future__ import annotations

from pathlib import Path

from brac7.models import Bracket


def _safe_id(match_id: str) -> str:
    return match_id.replace("-", "_")


def export_mermaid(bracket: Bracket, path: Path) -> Path:
    lines = [
        "---",
        f"title: {bracket.title}",
        "---",
        "flowchart TB",
        f"    subgraph meta[\"{bracket.format_label} | {len(bracket.participants)} entrants / size {bracket.size}\"]",
        "        direction TB",
        "    end",
    ]

    for rnd in bracket.rounds:
        subgraph_id = f"round_{rnd.index}"
        lines.append(f"    subgraph {subgraph_id}[\"{rnd.name}\"]")
        for m in rnd.matches:
            node_id = _safe_id(m.id)
            a = m.display_slot("a", bracket.options).replace('"', "'")
            b = m.display_slot("b", bracket.options).replace('"', "'")
            label = f"{m.id}<br/>{a}<br/>vs<br/>{b}"
            lines.append(f'        {node_id}["{label}"]')
        lines.append("    end")

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
