import json
from pathlib import Path

from django.http import FileResponse, Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from brac7.engine import BracketEngine
from brac7.exporters import (
    export_csv,
    export_html,
    export_json,
    export_markdown,
    export_mermaid,
    export_pdf,
    export_xlsx,
)
from brac7.interactive import InteractiveState, create_interactive
from brac7.models import BracketOptions, MatchFormat, SeedingMode, TournamentFormat

from .forms import BracketProjectForm
from .models import BracketProject


def _options_from_project(p: BracketProject) -> BracketOptions:
    return BracketOptions(
        title=p.title,
        format=TournamentFormat(p.format),
        seeding=SeedingMode(p.seeding),
        supports_byes=p.supports_byes,
        max_participants=p.max_participants,
        match_format=MatchFormat(p.match_format),
    )


def home(request: HttpRequest) -> HttpResponse:
    projects = BracketProject.objects.order_by("-updated_at")[:20]
    return render(request, "brackets/home.html", {"projects": projects})


def create_bracket(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BracketProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect("bracket_detail", pk=project.pk)
    else:
        form = BracketProjectForm()
    return render(request, "brackets/create.html", {"form": form})


def bracket_detail(request: HttpRequest, pk: int) -> HttpResponse:
    project = get_object_or_404(BracketProject, pk=pk)
    members = project.member_list()
    bracket = BracketEngine(_options_from_project(project)).generate(members)
    return render(
        request,
        "brackets/detail.html",
        {
            "project": project,
            "bracket": bracket,
            "rounds": bracket.rounds,
            "member_count": len(members),
        },
    )


def bracket_workspace_link(request: HttpRequest, pk: int) -> HttpResponse:
    return redirect("workspace_design", pk=pk)


@require_http_methods(["GET"])
def export_file(request: HttpRequest, pk: int, fmt: str) -> FileResponse:
    project = get_object_or_404(BracketProject, pk=pk)
    members = project.member_list()
    bracket = BracketEngine(_options_from_project(project)).generate(members)
    out = Path(request.GET.get("dir", "/tmp")) / f"brac7-{pk}"
    out.mkdir(parents=True, exist_ok=True)
    exporters = {
        "xlsx": export_xlsx,
        "pdf": export_pdf,
        "md": export_markdown,
        "mermaid": export_mermaid,
        "json": export_json,
        "csv": export_csv,
        "html": export_html,
    }
    fn = exporters.get(fmt)
    if not fn:
        raise Http404("Unknown format")
    path = fn(bracket, out / f"bracket.{fmt if fmt != 'md' else 'md'}")
    return FileResponse(open(path, "rb"), as_attachment=True, filename=path.name)


@require_http_methods(["POST"])
def api_set_winner(request: HttpRequest, pk: int) -> JsonResponse:
    project = get_object_or_404(BracketProject, pk=pk)
    payload = json.loads(request.body)
    state = InteractiveState(**project.state_json) if project.state_json else None
    if state is None:
        _, state = create_interactive(project.member_list(), _options_from_project(project))
    state.set_winner(payload["match_id"], payload["winner"])
    project.state_json = state.__dict__ if hasattr(state, "__dict__") else json.loads(
        json.dumps({"match_results": state.match_results})
    )
    project.save(update_fields=["state_json", "updated_at"])
    return JsonResponse({"ok": True, "match_id": payload["match_id"], "winner": payload["winner"]})
