# brac7

Tournament bracket generator by [**jrb00013**](https://github.com/jrb00013).

**CLI** · **Python library** · **XLSX / PDF / Markdown / Mermaid** · **Django UI** · **2D design workspace** · **interactive** winner tracking

## Features

| Option | Values |
|--------|--------|
| Format | `single_elimination`, `double_elimination` |
| Seeding | `seeded`, `random` |
| Byes | on/off (pads to next power of 2) |
| Max participants | optional cap |
| Match labels | `standard`, `compact`, `detailed` |

## Quick install

```bash
git clone https://github.com/jrb00013/brac7.git
cd brac7
chmod +x setup.sh
./setup.sh
source .venv/bin/activate
```

## CLI

**Interactive** (prompts for members and options):

```bash
brac7 -i --all -o output --slug my-event
```

**Arguments**:

```bash
brac7 \
  --title "AI Startup Showdown" \
  --format single_elimination \
  --seeding seeded \
  --members-file examples/ai-startups.txt \
  --output-dir output \
  --slug ai-bracket \
  --all
```

Or use the helper script:

```bash
./scripts/generate_ai_bracket.sh
```

## Python library

```python
from brac7 import BracketEngine, BracketOptions, TournamentFormat
from brac7.exporters import export_pdf, export_xlsx, export_mermaid
from brac7.interactive import create_interactive
from pathlib import Path

opts = BracketOptions(title="Demo", format=TournamentFormat.SINGLE_ELIMINATION)
bracket = BracketEngine(opts).generate(["Alice", "Bob", "Carol", "Dave"])
export_xlsx(bracket, Path("out/bracket.xlsx"))
export_pdf(bracket, Path("out/bracket.pdf"))

bracket, state = create_interactive(["A", "B", "C", "D"], opts)
state.set_winner("W-R1-M1", "Alice")
state.save(Path("state.json"))
```

## Django UI

```bash
./setup.sh   # answer Y for Django UI
cd brac7_site
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000 — create a bracket, export files, open **2D workspace** to drag matches and save layout.

## License

MIT © jrb00013
