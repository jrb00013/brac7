from __future__ import annotations

import json
from pathlib import Path

from brac7.models import Bracket


def export_json(bracket: Bracket, path: Path, indent: int = 2) -> Path:
    def _match_to_dict(m):
        return {
            "id": m.id,
            "round_index": m.round_index,
            "match_index": m.match_index,
            "bracket": m.bracket,
            "participant_a": m.participant_a,
            "participant_b": m.participant_b,
            "seed_a": m.seed_a,
            "seed_b": m.seed_b,
            "is_bye": m.is_bye,
            "feeds_from": list(m.feeds_from),
            "label": m.label,
            "display_a": m.display_slot("a", bracket.options),
            "display_b": m.display_slot("b", bracket.options),
        }

    data = {
        "title": bracket.title,
        "format": bracket.options.format.value,
        "seeding": bracket.options.seeding.value,
        "supports_byes": bracket.options.supports_byes,
        "match_format": bracket.options.match_format.value,
        "size": bracket.size,
        "participants": [
            {"name": p.name, "seed": p.seed} for p in bracket.participants
        ],
        "rounds": [
            {
                "index": r.index,
                "name": r.name,
                "matches": [_match_to_dict(m) for m in r.matches],
            }
            for r in bracket.rounds
        ],
    }

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent), encoding="utf-8")
    return path
