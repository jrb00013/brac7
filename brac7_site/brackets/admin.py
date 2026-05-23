from django.contrib import admin

from .models import BracketProject


@admin.register(BracketProject)
class BracketProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "format", "seeding", "supports_byes", "created_at", "updated_at"]
    list_filter = ["format", "seeding", "supports_byes"]
    search_fields = ["title", "members_text"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["title", "format", "seeding", "supports_byes", "max_participants", "match_format"]}),
        ("Participants", {"fields": ["members_text"]}),
        ("State", {"fields": ["state_json"], "classes": ["collapse"]}),
        ("Timestamps", {"fields": ["created_at", "updated_at"]}),
    ]
