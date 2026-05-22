#!/usr/bin/env bash
# Build incremental git history for brac7 (phase 1 + phase 2)
set -euo pipefail
cd "$(dirname "$0")/.."
export GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-jrb00013}"
export GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-jrb00013@users.noreply.github.com}"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"

if [[ ! -d .git ]]; then
  git init -b main
fi

commit() {
  git add -A
  git commit -m "$1" --allow-empty 2>/dev/null || git commit -m "$1"
}

# Phase 1 — scaffold through CLI
[[ -f .gitignore ]] && git add .gitignore LICENSE output/.gitkeep && commit "chore: initialize brac7 repository with MIT license"
git add README.md && commit "docs: add project README and feature overview"
git add pyproject.toml && commit "build: add pyproject.toml and package metadata for jrb00013"
git add src/brac7/models.py && commit "feat(core): add BracketOptions and domain models"
git add src/brac7/seeding.py && commit "feat(seeding): standard bracket seed order and slot builder"
git add src/brac7/engine.py && commit "feat(engine): single and double elimination bracket generator"
git add src/brac7/exporters/markdown.py && commit "feat(export): markdown bracket export"
git add src/brac7/exporters/mermaid.py && commit "feat(export): mermaid flowchart and markdown wrapper export"
git add src/brac7/exporters/xlsx.py && commit "feat(export): Excel workbook with matches and bracket view"
git add src/brac7/exporters/pdf_export.py src/brac7/exporters/__init__.py && commit "feat(export): PDF export via ReportLab"
git add src/brac7/cli.py src/brac7/__main__.py && commit "feat(cli): interactive prompts and argparse flags"
git add setup.sh && commit "chore: add setup.sh for automated venv and install"
git add tests/ && commit "test: engine and exporter smoke tests"
git add examples/ai-startups.txt scripts/generate_ai_bracket.sh && commit "examples: AI startup single-elimination member list"
git add examples/generated/ && commit "examples: sample XLSX PDF and Mermaid for AI startup bracket"
git add src/brac7/__init__.py && commit "chore: public package exports and version 0.1.0"

# Phase 2 — library + UI
git add src/brac7/interactive.py && commit "feat(interactive): JSON state and winner advancement API"
PYVER=$(grep '^version' pyproject.toml | head -1)
sed -i 's/version = "0.1.0"/version = "0.2.0"/' pyproject.toml 2>/dev/null || true
git add pyproject.toml src/brac7/__init__.py README.md && commit "feat(library): publish installable brac7 0.2.0 with interactive API"
git add brac7_site/config/ brac7_site/manage.py && commit "feat(ui): Django project config and manage.py"
git add brac7_site/brackets/models.py brac7_site/brackets/migrations/ && commit "feat(ui): BracketProject model and migrations"
git add brac7_site/brackets/forms.py brac7_site/brackets/admin.py && commit "feat(ui): bracket creation form and admin"
git add brac7_site/brackets/views.py brac7_site/brackets/urls.py && commit "feat(ui): bracket CRUD views and export endpoints"
git add brac7_site/brackets/templates/ && commit "feat(ui): HTML templates for home create and detail"
git add brac7_site/workspace/ && commit "feat(ui): 2D canvas workspace with drag layout and save API"
git add README.md setup.sh && commit "docs: document Django UI workspace and library usage"

echo "Done. $(git rev-list --count HEAD) commits on $(git branch --show-current)"
