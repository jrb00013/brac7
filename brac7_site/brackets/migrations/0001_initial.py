from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="BracketProject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="Tournament Bracket", max_length=200)),
                ("format", models.CharField(default="single_elimination", max_length=32)),
                ("seeding", models.CharField(default="seeded", max_length=16)),
                ("supports_byes", models.BooleanField(default=True)),
                ("max_participants", models.PositiveIntegerField(blank=True, null=True)),
                ("match_format", models.CharField(default="standard", max_length=16)),
                ("members_text", models.TextField()),
                ("state_json", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
