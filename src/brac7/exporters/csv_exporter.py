from __future__ import annotations

import csv
from pathlib import Path

from brac7.models import Bracket


def export_csv(bracket: Bracket, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Title", bracket.title])
        w.writerow(["Format", bracket.format_label])
        w.writerow(["Seeding", bracket.options.seeding.value])
        w.writerow(["Bracket size", bracket.size])
        w.writerow(["Participants", len(bracket.participants)])
        w.writerow([])

        w.writerow(["Seed", "Name"])
        for p in bracket.participants:
            w.writerow([p.seed, p.name])
        w.writerow([])

        w.writerow(["Round", "Match ID", "Bracket", "Slot A", "Slot B", "Bye", "Label", "Feeds From"])
        for rnd in bracket.rounds:
            for m in rnd.matches:
                w.writerow([
                    rnd.name,
                    m.id,
                    m.bracket,
                    m.display_slot("a", bracket.options),
                    m.display_slot("b", bracket.options),
                    "Yes" if m.is_bye else "",
                    m.label,
                    ", ".join(m.feeds_from),
                ])
    return path
