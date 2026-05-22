#!/usr/bin/env bash
# brac7 — full automated install (venv, deps, editable package, optional Django UI)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
VENV="${VENV:-$ROOT/.venv}"

echo "==> brac7 setup"
echo "    root: $ROOT"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Error: $PYTHON not found. Install Python 3.10+." >&2
  exit 1
fi

if [[ ! -d "$VENV" ]]; then
  echo "==> Creating virtualenv at $VENV"
  "$PYTHON" -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install -U pip setuptools wheel

INSTALL_UI="${INSTALL_UI:-ask}"
if [[ "$INSTALL_UI" == "ask" ]]; then
  read -r -p "Install Django UI extras? [y/N] " ui_ans || ui_ans="n"
  if [[ "$ui_ans" =~ ^[Yy] ]]; then
    INSTALL_UI=yes
  else
    INSTALL_UI=no
  fi
fi

echo "==> Installing brac7 (editable)"
if [[ "$INSTALL_UI" == "yes" ]]; then
  pip install -e ".[ui,dev]"
else
  pip install -e ".[dev]"
fi

mkdir -p "$ROOT/output"

echo ""
echo "==> Setup complete"
echo "    Activate:  source $VENV/bin/activate"
echo "    CLI:       brac7 --help"
echo "    Interactive: brac7 -i --all"
echo ""
echo "    Example:"
echo "      brac7 -i --format single_elimination --all -o output --slug demo"
echo ""

if [[ "$INSTALL_UI" == "yes" && -d "$ROOT/brac7_site" ]]; then
  echo "    Django UI:"
  echo "      cd brac7_site && python manage.py migrate && python manage.py runserver"
fi
