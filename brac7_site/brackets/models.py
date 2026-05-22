from django.db import models


class BracketProject(models.Model):
    title = models.CharField(max_length=200, default="Tournament Bracket")
    format = models.CharField(
        max_length=32,
        default="single_elimination",
        choices=[
            ("single_elimination", "Single elimination"),
            ("double_elimination", "Double elimination"),
        ],
    )
    seeding = models.CharField(
        max_length=16,
        default="seeded",
        choices=[("seeded", "Seeded"), ("random", "Random")],
    )
    supports_byes = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    match_format = models.CharField(
        max_length=16,
        default="standard",
        choices=[
            ("standard", "Standard"),
            ("compact", "Compact"),
            ("detailed", "Detailed"),
        ],
    )
    members_text = models.TextField(help_text="One participant per line")
    state_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def member_list(self) -> list[str]:
        return [ln.strip() for ln in self.members_text.splitlines() if ln.strip()]

    def __str__(self) -> str:
        return self.title
