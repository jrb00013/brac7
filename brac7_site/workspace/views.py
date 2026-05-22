import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from brac7.engine import BracketEngine
from brac7.models import BracketOptions, MatchFormat, SeedingMode, TournamentFormat

from brackets.models import BracketProject


def _options(p: BracketProject) -> BracketOptions:
    return BracketOptions(
        title=p.title,
        format=TournamentFormat(p.format),
        seeding=SeedingMode(p.seeding),
        supports_byes=p.supports_byes,
        max_participants=p.max_participants,
        match_format=MatchFormat(p.match_format),
    )


def design(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(BracketProject, pk=pk)
    bracket = BracketEngine(_options(project)).generate(project.member_list())
    nodes = []
    for rnd in bracket.rounds:
        for m in rnd.matches:
            nodes.append(
                {
                    "id": m.id,
                    "round": rnd.name,
                    "round_index": rnd.index,
                    "label": m.label,
                    "a": m.display_slot("a", bracket.options),
                    "b": m.display_slot("b", bracket.options),
                    "feeds_from": list(m.feeds_from),
                    "is_bye": m.is_bye,
                }
            )
    return render(
        request,
        "workspace/design.html",
        {
            "project": project,
            "bracket_json": json.dumps(
                {
                    "title": bracket.title,
                    "size": bracket.size,
                    "format": bracket.format_label,
                    "nodes": nodes,
                }
            ),
        },
    )


@require_http_methods(["POST"])
def save_layout(request: HttpRequest, pk: int) -> JsonResponse:
    project = get_object_or_404(BracketProject, pk=pk)
    layout = json.loads(request.body)
    state = project.state_json or {}
    state["layout"] = layout
    project.state_json = state
    project.save(update_fields=["state_json", "updated_at"])
    return JsonResponse({"ok": True})
