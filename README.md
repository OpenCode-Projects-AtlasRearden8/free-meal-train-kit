# Free Meal Train Kit

Free printable kit for coordinating meals for someone you love — a new baby,
surgery recovery, or any hard season. Sign-up sheet, dietary-needs grid,
drop-off instructions card, delivery-day log, portion-and-container labels,
allergen flags, thank-you note starters, and a wrap-up recap for the family.

Everything is plain HTML/CSS that gets printed to PDF by one build script.
No signups, nothing online, no accounts. Print it, hand it out, be kind.

Each printable comes with a warm one-page **captain's guide** — a short,
friend-like note for whoever is coordinating, explaining how to use that sheet
without making it heavy.

## What's in `printables/` (after you build)

Eight unbranded, ready-to-print PDF sheets:

| File | Use it for |
| --- | --- |
| `coordinator-sign-up.pdf` | Meal schedule sign-up grid |
| `dietary-needs-grid.pdf` | One-row-per-person dietary needs at a glance |
| `drop-off-instructions.pdf` | Cooler-and-porch protocol card (fold in half) |
| `delivery-day-log.pdf` | Track who delivered what, and when |
| `portion-container-labels.pdf` | Cut-apart labels for lids and containers |
| `allergen-flags.pdf` | Cut-apart badges for serious allergens |
| `thank-you-note-starters.pdf` | Sentence starters for kind thank-yous |
| `family-wrap-up.pdf` | Gentle ends-of-the-season recap for the family |

Plus eight matching captain's guides: `guide-coordinator-sign-up.pdf` and so on.

## How to build

You need Python 3.9+ with WeasyPrint (installed with `pip install weasyprint`).

```bash
python3 build.py            # builds all PDFs into printables/
python3 build.py --out /tmp/mykit   # build somewhere else
python3 build.py --list     # just list the kit contents
```

The output is deterministic: same sources, same PDFs. PDFs land in
`printables/` and a `MANIFEST.txt` is written next to them.

## How to test

```bash
python3 -m pytest tests/ -v
```

The tests build the whole kit into a scratch directory and verify that every
sheet and every guide builds a valid PDF: correct header, parseable pages,
letter-size geometry, expected content on each page, and — importantly —
that nothing in the printables is branded: no company names, no URLs, no
web links. The printouts are yours to hand to a neighbor.

## Printing tips

- Print on regular US Letter paper, `Actual size` (not "fit to page").
- Sheets are designed in ink-friendly color; they photocopy fine in grayscale.
- The drop-off card is designed to be folded in half; labels and allergen
  flags have cut lines you can follow with scissors.

## Privacy by design

Nothing about this kit phones home. Fill the sheets in by hand. If you like,
keep the filled originals in the family's paperwork folder — the delivery log
doubles as a record of who helped, which is worth keeping.

## Credits

Built and maintained by **Asdale Dynamics, LLC** — the practical-tools arm of
Dylan Asdale's beginner-friendly AI work (the book *The Massive AI Manual* and
the hub at `dylanasdale.github.io` explain AI "like a friend would"). This kit
is one of the LLC's free, local-first, offline printable tools: zero signups,
zero tracking, zero websites required.

MIT licensed — see `LICENSE`.
