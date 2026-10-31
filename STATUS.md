# STATUS — Free Meal Train Kit

Last updated: 2026-10-31

## What was built

A free, offline, printable kit for coordinating meals for a new baby, surgery
recovery, or any hard season. Everything is HTML/CSS under `src/`, rendered to
unbranded US-Letter PDFs in `printables/` by one build script (`build.py`, using
the WeasyPrint engine). No signups, nothing online, no personal data.

**8 printable sheets** (each with a matching warm one-page captain's guide PDF):

1. Meal Train Sign-Up Sheet — date/name/contact/dish drop-off grid for volunteers
2. Dietary Needs Grid — one row per household member: allergies, must-avoids,
   dislikes, comfort favorites, best drop-off times
3. Meal Drop-Off Instructions — fold-in-half card with the porch-and-cooler
   protocol (text, knock, don't ring, photo, leave)
4. Delivery Day Log — track who delivered what, allergen/check/freeze/thank-you
   columns, plus a freezer inventory and food-safety line
5. Portion & Container Labels — 6 cut-apart labels (made/contains/made on/
   keep-freeze-serve/reheat)
6. Allergen Flags — 12 cut-apart badges (nuts, dairy, gluten, eggs, soy,
   fish/shellfish, spicy, vegetarian, vegan, allergen-free-for, freezer, "easy")
7. Thank-You Note Starters — fill-in-the-blank openers/details/closers plus a
   thank-you bookkeeping table
8. Family Wrap-Up Recap — season totals, "what helped most" prompts, gentle
   next steps (return pans, freezer use, stocking guide for the next hard week)

## How to run

```bash
pip install weasyprint     # the only dependency
python3 build.py           # builds 16 PDFs + MANIFEST.txt into printables/
python3 build.py --out DIR # build somewhere else
python3 build.py --list    # list kit contents without building
python3 -m pytest tests/ -q   # full test suite
```

## Verification results

- `python3 build.py` — succeeds; 16 PDFs + `MANIFEST.txt` written (reproduced).
- `python3 -m pytest tests/ -q` — **38 passed** (6.3 s). Coverage includes:
  - all 16 expected PDFs exist in the build output, non-trivially sized
  - each PDF is valid: `%PDF-` header, parseable by pypdf, US-Letter geometry
  - every sheet and guide contains its expected unique content on extractable text
  - printables are unbranded: no Asdale/Dylan names, no URLs, no copyright
    strings anywhere in the printed output (tested token by token)
  - manifest lists all 16 files and is itself unbranded
  - robustness: an empty source fragment fails the build loudly (exit 1
    with a clear message, no garbage PDF emitted)
  - `--list` mode lists every sheet and guide
- Visual spot-check of rendered pages (rendered PNG previews) — clean layout,
  no overflow; the delivery log was re-flowed to a single page after an
  orphaned line was caught in review.

## Known gaps

- Password-less/--simple accessibility pass not attempted beyond high-contrast
  print styling; fillable text fields are not PDF form fields (written by hand).
- No A4 variant (sheet geometry is US Letter; WeasyPrint `@page size` is a
  one-line change in `src/css/styles.css` if needed).
- WeasyPrint versions other than 70.x are untested; tests would catch gross
  layout/content breakage either way.
- Guide page counts assume letter margins; very long guides could spill to a
  second page in future edits (each is currently exactly one page).

## Repo notes

- MIT LICENSE — `Copyright (c) 2026 Asdale Dynamics, LLC`; README credits
  Asdale Dynamics, LLC.
- Built PDFs are committed alongside sources so the kit works from a fresh
  clone with zero Python installed.
- No secrets, API keys, or personal data anywhere in the repo (verified by the
  unbranded-content tests and by hand).
