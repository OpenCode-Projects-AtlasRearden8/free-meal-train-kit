"""Tests for the Free Meal Train Kit.

Every test builds from source (no pre-committed PDFs are trusted):
the build script must succeed, every sheet and guide must produce a
valid, letter-size, content-correct, unbranded PDF, and the manifest
must index everything.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

PROJECT = Path(__file__).resolve().parent.parent
BUILD = PROJECT / "build.py"
SRC = PROJECT / "src"

SHEET_KEYWORDS = {
    "coordinator-sign-up": "Meal Train Sign-Up Sheet",
    "dietary-needs-grid": "Dietary Needs Grid",
    "drop-off-instructions": "THE PORCH & COOLER ROUTINE",
    "delivery-day-log": "Delivery Day Log",
    "portion-container-labels": "MADE:",
    "allergen-flags": "CONTAINS NUTS",
    "thank-you-note-starters": "Thank-You Note Starters",
    "family-wrap-up": "Season recap",
}

GUIDE_KEYWORDS = {
    "coordinator-sign-up": "captain, not a caterer",
    "dietary-needs-grid": "One row per person",
    "drop-off-instructions": "cooler on the porch",
    "delivery-day-log": "zero-effort for tired people",
    "portion-container-labels": "tiny system",
    "allergen-flags": "home kitchen",
    "thank-you-note-starters": "two blanks",
    "family-wrap-up": "Close the books warmly",
}

BRAND_TOKENS = [
    "asdale",
    "dylan",
    "massive ai manual",
    "license",
    "copyright",
    "http://",
    "https://",
    "www.",
    ".com",
    ".org",
    ".io",
]


def build_kit(out_dir: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out_dir)],
        capture_output=True,
        text=True,
        cwd=PROJECT,
        timeout=300,
    )
    assert result.returncode == 0, f"build failed:\n{result.stdout}\n{result.stderr}"


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("kit-build") / "printables"
    build_kit(out)
    return out


def pdf_text(pdf: Path) -> str:
    reader = PdfReader(pdf)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def expected_pdfs(prefix: str, keywords: dict) -> list[str]:
    return [f"{prefix}{slug}.pdf" for slug in keywords]


# ---------------------------------------------------------------- build success


def test_builds_all_pdfs(built: Path):
    expected = expected_pdfs("", SHEET_KEYWORDS) + expected_pdfs("guide-", GUIDE_KEYWORDS)
    for name in expected:
        assert (built / name).is_file(), f"missing PDF: {name}"
        assert (built / name).stat().st_size > 2000, f"PDF suspiciously small: {name}"


def test_builds_manifest(built: Path):
    manifest = (built / "MANIFEST.txt").read_text(encoding="utf-8")
    for name in expected_pdfs("", SHEET_KEYWORDS) + expected_pdfs("guide-", GUIDE_KEYWORDS):
        assert name in manifest, f"manifest missing entry: {name}"
    assert "No signups, nothing online" in manifest


def test_list_flag_lists_every_kit_piece():
    result = subprocess.run(
        [sys.executable, str(BUILD), "--list"],
        capture_output=True,
        text=True,
        cwd=PROJECT,
        timeout=60,
    )
    assert result.returncode == 0
    for slug in SHEET_KEYWORDS:
        assert f"sheets/{slug}.html" in result.stdout
        assert f"guide-{slug}.pdf" in result.stdout


# ------------------------------------------------------- per-PDF validation


@pytest.mark.parametrize("name", expected_pdfs("", SHEET_KEYWORDS))
def test_sheet_pdf_is_valid_and_content_correct(name, built: Path):
    _assert_valid_pdf_and_content(built / name, SHEET_KEYWORDS)


@pytest.mark.parametrize("name", expected_pdfs("guide-", GUIDE_KEYWORDS))
def test_guide_pdf_is_valid_and_content_correct(name, built: Path):
    _assert_valid_pdf_and_content(built / name, GUIDE_KEYWORDS)


def _assert_valid_pdf_and_content(pdf: Path, keywords: dict) -> None:
    raw = pdf.read_bytes()
    assert raw[:5] == b"%PDF-", f"{pdf.name} is not a PDF"

    reader = PdfReader(pdf)
    assert len(reader.pages) >= 1
    box = reader.pages[0].mediabox
    # US Letter: 8.5in x 11in = 612 x 792 pt
    assert abs(float(box.width) - 612) < 2, f"{pdf.name} width is {box.width}"
    assert abs(float(box.height) - 792) < 2, f"{pdf.name} height is {box.height}"

    slug = pdf.name.replace("guide-", "").replace(".pdf", "")
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    # PDF extraction wraps lines inside headings; compare with normalized whitespace
    text = re.sub(r"\s+", " ", text).lower()
    keyword = re.sub(r"\s+", " ", keywords[slug].lower())
    assert keyword in text, f"{pdf.name} missing its key content"

    # blank write-in rules really render (lines with underscores appear)
    assert "___" in text or "\u05f5" in text or "—" in text


# ------------------------------------------------------------------ unbranded


@pytest.mark.parametrize("name", expected_pdfs("", SHEET_KEYWORDS) + expected_pdfs("guide-", GUIDE_KEYWORDS))
def test_printables_are_unbranded(name, built: Path):
    text = pdf_text(built / name).lower()
    for token in BRAND_TOKENS:
        assert token not in text, f"{name} is branded/linked: found {token!r}"


def test_manifest_is_unbranded(built: Path):
    text = (built / "MANIFEST.txt").read_text(encoding="utf-8").lower()
    for token in ("asdale", "dylan", "http", "www.", ".com", ".org"):
        assert token not in text


# ------------------------------------------------------------ robustness


def test_build_fails_on_empty_fragment(tmp_path: Path):
    """An empty source fragment must fail the build loudly, not emit junk."""
    sandbox = tmp_path / "proj"
    shutil.copytree(PROJECT / "src", sandbox / "src")
    shutil.copy2(BUILD, sandbox / "build.py")
    empty = sandbox / "src" / "sheets" / "coordinator-sign-up.html"
    empty.write_text("", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(sandbox / "build.py"), "--out", str(tmp_path / "out")],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 1
    assert "empty" in result.stderr.lower()
    assert not (tmp_path / "out" / "coordinator-sign-up.pdf").exists()


def test_source_uses_shared_stylesheet():
    for fragment in SRC.glob("sheets/*.html"):
        pass  # fragments are wrapped by build.py; nothing to assert per-file
    css = (SRC / "css" / "styles.css").read_text(encoding="utf-8")
    assert "@page" in css
    assert "letter" in css
    wrapper = (PROJECT / "build.py").read_text(encoding="utf-8")
    assert 'href="css/styles.css"' in wrapper or "CSS_HREF" in wrapper
