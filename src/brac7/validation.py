from __future__ import annotations

from typing import Sequence


class ValidationError(ValueError):
    def __init__(self, message: str, detail: str | None = None):
        self.detail = detail
        super().__init__(message)


class ParticipantValidator:
    MIN_PARTICIPANTS = 2
    MAX_PARTICIPANTS = 65536

    @classmethod
    def validate_names(cls, names: Sequence[str]) -> list[str]:
        cleaned = [n.strip() for n in names]

        if len(cleaned) < cls.MIN_PARTICIPANTS:
            raise ValidationError(
                f"Need at least {cls.MIN_PARTICIPANTS} participants, got {len(cleaned)}"
            )

        if len(cleaned) > cls.MAX_PARTICIPANTS:
            raise ValidationError(
                f"Too many participants ({len(cleaned)}), maximum is {cls.MAX_PARTICIPANTS}"
            )

        empty = [i for i, n in enumerate(cleaned, 1) if not n]
        if empty:
            raise ValidationError(
                f"Empty participant name(s) on line(s): {', '.join(map(str, empty))}"
            )

        seen: dict[str, list[int]] = {}
        for i, name in enumerate(cleaned, 1):
            seen.setdefault(name, []).append(i)

        duplicates = {n: lines for n, lines in seen.items() if len(lines) > 1}
        if duplicates:
            msgs = [f"{n!r} on lines {', '.join(map(str, lines))}" for n, lines in duplicates.items()]
            raise ValidationError(
                f"Duplicate participant(s) found: {'; '.join(msgs)}",
                detail="Participant names should be unique",
            )

        return cleaned
