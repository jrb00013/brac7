"""brac7 CLI — interactive prompts and argument mode."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from brac7.engine import BracketEngine
from brac7.exporters import export_markdown, export_mermaid, export_pdf, export_xlsx
from brac7.models import BracketOptions, MatchFormat, SeedingMode, TournamentFormat


def _parse_format(value: str) -> TournamentFormat:
    key = value.lower().replace("-", "_").replace(" ", "_")
    for fmt in TournamentFormat:
        if key in (fmt.value, fmt.name.lower()):
            return fmt
    raise argparse.ArgumentTypeError(f"Unknown format: {value}")


def _parse_seeding(value: str) -> SeedingMode:
    key = value.lower()
    if key in ("random", "rand"):
        return SeedingMode.RANDOM
    return SeedingMode.SEEDED


def _parse_match_format(value: str) -> MatchFormat:
    key = value.lower()
    for mf in MatchFormat:
        if key == mf.value or key == mf.name.lower():
            return mf
    return MatchFormat.STANDARD


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="brac7",
        description="Generate tournament brackets (XLSX, PDF, Markdown, Mermaid).",
    )
    p.add_argument("--title", "-t", help="Bracket title")
    p.add_argument(
        "--format", "-f",
        type=_parse_format,
        default=TournamentFormat.SINGLE_ELIMINATION,
        help="single_elimination | double_elimination",
    )
    p.add_argument(
        "--seeding", "-s",
        type=_parse_seeding,
        default=SeedingMode.SEEDED,
        help="seeded | random",
    )
    p.add_argument("--byes", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--max-participants", type=int, default=None)
    p.add_argument("--match-format", type=_parse_match_format, default=MatchFormat.STANDARD)
    p.add_argument("--seed", type=int, default=None, help="RNG seed for random seeding")
    p.add_argument("--members", "-m", nargs="+", help="Participant names")
    p.add_argument("--members-file", type=Path, help="One name per line")
    p.add_argument("--output-dir", "-o", type=Path, default=Path("output"))
    p.add_argument("--slug", default="bracket", help="Output filename stem")
    p.add_argument("--xlsx", action="store_true", help="Export Excel")
    p.add_argument("--pdf", action="store_true", help="Export PDF")
    p.add_argument("--markdown", action="store_true", help="Export Markdown")
    p.add_argument("--mermaid", action="store_true", help="Export Mermaid (.md)")
    p.add_argument("--all", action="store_true", help="Export all formats")
    p.add_argument("--interactive", "-i", action="store_true", help="Prompt for options")
    p.add_argument("--no-interactive", action="store_true", help="Skip prompts if args provided")
    return p


def _prompt_members() -> list[str]:
    print("\nEnter participants (one per line, blank line to finish):")
    members: list[str] = []
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        if not line:
            if members:
                break
            continue
        members.append(line)
    return members


def _prompt_options(args: argparse.Namespace) -> BracketOptions:
    if args.interactive and not args.no_interactive:
        print("\n=== brac7 bracket setup ===\n")

    if not args.title and (args.interactive and not args.no_interactive):
        args.title = input("Bracket title [Tournament Bracket]: ").strip() or "Tournament Bracket"

    if args.interactive and not args.no_interactive:
        fmt = input("Format (single/double) [single]: ").strip().lower() or "single"
        args.format = _parse_format("double_elimination" if fmt.startswith("d") else "single_elimination")

        seed_in = input("Seeding (seeded/random) [seeded]: ").strip().lower() or "seeded"
        args.seeding = _parse_seeding(seed_in)

        byes_in = input("Support byes? [Y/n]: ").strip().lower()
        args.byes = byes_in not in ("n", "no")

        max_in = input("Max participants (blank = all): ").strip()
        args.max_participants = int(max_in) if max_in.isdigit() else None

        mf = input("Match format (standard/compact/detailed) [standard]: ").strip().lower()
        if mf:
            args.match_format = _parse_match_format(mf)

    return BracketOptions(
        format=args.format,
        seeding=args.seeding,
        supports_byes=args.byes,
        max_participants=args.max_participants,
        match_format=args.match_format,
        title=args.title or "Tournament Bracket",
        random_seed=args.seed,
    )


def load_members(args: argparse.Namespace) -> list[str]:
    if args.members:
        return list(args.members)
    if args.members_file:
        text = args.members_file.read_text(encoding="utf-8")
        return [ln.strip() for ln in text.splitlines() if ln.strip()]
    if args.interactive or (not args.no_interactive and not sys.stdin.isatty() is False):
        return _prompt_members()
    return _prompt_members()


def resolve_exports(args: argparse.Namespace) -> set[str]:
    if args.all:
        return {"xlsx", "pdf", "markdown", "mermaid"}
    out: set[str] = set()
    if args.xlsx:
        out.add("xlsx")
    if args.pdf:
        out.add("pdf")
    if args.markdown:
        out.add("markdown")
    if args.mermaid:
        out.add("mermaid")
    return out or {"xlsx", "pdf", "markdown", "mermaid"}


def run_exports(bracket, out_dir: Path, slug: str, formats: set[str]) -> list[Path]:
    written: list[Path] = []
    if "xlsx" in formats:
        written.append(export_xlsx(bracket, out_dir / f"{slug}.xlsx"))
    if "pdf" in formats:
        written.append(export_pdf(bracket, out_dir / f"{slug}.pdf"))
    if "markdown" in formats:
        written.append(export_markdown(bracket, out_dir / f"{slug}.md"))
    if "mermaid" in formats:
        written.append(export_mermaid(bracket, out_dir / f"{slug}.mmd"))
    return written


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.interactive or (not args.members and not args.members_file):
        args.interactive = True

    options = _prompt_options(args)
    members = load_members(args)
    if len(members) < 2:
        print("Error: need at least 2 participants.", file=sys.stderr)
        return 1

    engine = BracketEngine(options)
    bracket = engine.generate(members)
    formats = resolve_exports(args)
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = run_exports(bracket, out_dir, args.slug, formats)

    print(f"\nGenerated {bracket.format_label} bracket — {len(bracket.participants)} entrants, size {bracket.size}")
    for p in paths:
        print(f"  → {p.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
