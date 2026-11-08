"""Bundled photos must exist and carry complete, free-licence attribution."""
import json
import re
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[1] / "itihaas"
CREDITS = json.loads((PACKAGE / "data" / "media_credits.json").read_text(encoding="utf-8"))
FREE_LICENCE = re.compile(r"^(CC0|Public domain|PD|CC BY(-SA)?( [0-9.]+)?)", re.I)


def test_manifest_is_not_empty():
    assert len(CREDITS) >= 40


@pytest.mark.parametrize("slug, entry", sorted(CREDITS.items()))
def test_photo_has_file_and_attribution(slug, entry):
    assert (PACKAGE / "static" / entry["file"]).is_file()
    assert FREE_LICENCE.match(entry["license"]), entry["license"]
    assert entry["author"] and entry["source"].startswith("https://commons.wikimedia.org/")


def test_templates_reference_existing_media():
    missing = set()
    for template in (PACKAGE / "templates").rglob("*.html"):
        for ref in re.findall(r"media/[A-Za-z0-9._-]+\.jpg", template.read_text(encoding="utf-8")):
            if not (PACKAGE / "static" / ref).is_file():
                missing.add(f"{template.name}: {ref}")
    assert not missing


def test_credits_page_lists_every_photo(client):
    page = client.get("/credits").get_data(as_text=True)
    for entry in CREDITS.values():
        assert entry["file"] in page
