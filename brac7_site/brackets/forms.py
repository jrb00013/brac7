from django import forms

from .models import BracketProject


class BracketProjectForm(forms.ModelForm):
    class Meta:
        model = BracketProject
        fields = [
            "title",
            "format",
            "seeding",
            "supports_byes",
            "max_participants",
            "match_format",
            "members_text",
        ]
        widgets = {
            "members_text": forms.Textarea(attrs={"rows": 12, "placeholder": "One name per line"}),
            "title": forms.TextInput(attrs={"class": "input"}),
        }
