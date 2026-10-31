#!/usr/bin/env python3
"""Free Meal Train Kit -- build script.

Wraps the HTML sheet/guide fragments in the shared print stylesheet and
renders each one to an unbranded US-Letter PDF in the output directory
(default: printables/). Also writes a MANIFEST.txt index next to the PDFs.

Usage:
    python3 build.py             # build everything into printables/
    python3 build.py --out DIR   # build into a custom directory
    python3 build.py --list      # list kit contents and exit
"""

import argparse
import datetime
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
CSS_HREF = "css/styles.css"

SHEETS = [
    ("coordinator-sign-up", "Meal Train Sign-Up Sheet"),
    ("dietary-needs-grid", "Dietary Needs Grid"),
    ("drop-off-instructions", "Meal Drop-Off Instructions"),
    ("delivery-day-log", "Delivery Day Log"),
    ("portion-container-labels", "Portion & Container Labels"),
    ("allergen-flags", "Allergen Flags"),
    ("thank-you-note-starters", "Thank-You Note Starters"),
    ("family-wrap-up", "Family Wrap-Up Recap"),
]

GUIDES = [
    ("coordinator-sign-up", "Captain's Guide -- Meal Train Sign-Up Sheet"),
    ("dietary-needs-grid", "Captain's Guide -- Dietary Needs Grid"),
    ("drop-off-instructions", "Captain's Guide -- Meal Drop-Off Instructions"),
    ("delivery-day-log", "Captain's Guide -- Delivery Day Log"),
    ("portion-container-labels", "Captain's Guide -- Portion & Container Labels"),
    ("allergen-flags", "Captain's Guide -- Allergen Flags"),
    ("thank-you-note-starters", "Captain's Guide -- Thank-You Note Starters"),
    ("family-wrap-up", "Captain's Guide -- Family Wrap-Up Recap"),
]


def load_fragment(path: Path) -> str:
    fragment = path.read_text(encoding="utf-8").strip()
    if not fragment:
        raise SystemExit(f"ERROR: fragment is empty: {path}")
    return fragment


def wrap_in_document(body: str, title: str, base_dir: Path, is_guide: bool) -> str:
    """Wrap a body fragment in a full HTML document pointing at the shared CSS."""
    guide_class = "guide" if is_guide else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{CSS_HREF}">
</head>
<body class="{guide_class}">
{body}
</body>
</html>
"""


def render_fragment(fragment: Path, title: str, out_pdf: Path, is_guide: bool) -> None:
    from weasyprint import HTML  # imported lazily so --list works without it

    body = load_fragment(fragment)
    doc = wrap_in_document(body, title, SRC, is_guide)
    html = HTML(string=doc, base_url=str(SRC))
    html.write_pdf(str(out_pdf))


def build(out_dir: Path) -> None:
    from weasyprint import __version__ as weasy_version  # also validates the import

    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    def run(fragments: Path, spec: list, is_guide: bool, prefix: str = "") -> None:
        for slug, title in spec:
            out = out_dir / f"{prefix}{slug}.pdf"
            render_fragment(fragments / f"{slug}.html", title, out, is_guide)
            rows.append((slug, title, out.name, is_guide))
            kind = "guide" if is_guide else "sheet"
            print(f"  built {out.name:40s} ({kind}: {title})")

    print(f"Building Free Meal Train Kit -> {out_dir}")
    print(f"WeasyPrint {weasy_version}\n")

    print("Sheets:")
    run(SRC / "sheets", SHEETS, is_guide=False)
    print("\nCaptain's guides:")
    run(SRC / "guides", GUIDES, is_guide=True, prefix="guide-")

    manifest = build_manifest(rows)
    manifest_path = out_dir / "MANIFEST.txt"
    manifest_path.write_text(manifest, encoding="utf-8")
    print(f"\n{len(rows)} PDFs + MANIFEST.txt written to {out_dir}")


def build_manifest(rows: list) -> str:
    today = datetime.date.today().isoformat()
    lines = [
        "Free Meal Train Kit -- printable PDF index",
        f"Built: {today}",
        "",
        "Print on US Letter, 'Actual size'. Both sheets and guides are",
        "ink-friendly and photocopy fine in grayscale.",
        "",
    ]
    sheets = [r for r in rows if not r[3]]
    guides = [r for r in rows if r[3]]
    lines.append("SHEETS:")
    for slug, _title, filename, _ in sheets:
        lines.append(f"  {filename}")
    lines.append("")
    lines.append("CAPTAIN'S GUIDES (how to run the matching sheet):")
    for slug, _title, filename, _ in guides:
        lines.append(f"  {filename}")
    lines.append("")
    lines.append(
        "No signups, nothing online: everything here is a plain printable."
    )
    return "\n".join(lines) + "\n"


def show_list() -> None:
    print("Free Meal Train Kit contents\n")
    print("Sheets:")
    for slug, title in SHEETS:
        print(f"  sheets/{slug}.html -> {slug}.pdf        ({title})")
    print("Captain's guides:")
    for slug, title in GUIDES:
        print(f"  guides/{slug}.html -> guide-{slug}.pdf  ({title})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Free Meal Train Kit PDFs")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "printables")
    parser.add_argument("--list", action="store_true", help="list kit contents and exit")
    args = parser.parse_args()

    if args.list:
        show_list()
        return 0

    try:
        build(args.out)
    except SystemExit:
        raise
    except Exception as exc:  # give the user a clear failure, not a traceback wall
        print(f"ERROR: build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
