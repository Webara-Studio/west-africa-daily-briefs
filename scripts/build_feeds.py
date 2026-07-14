#!/usr/bin/env python3
"""
Build JSON data feeds for the public site.

Reads all brief frontmatter and generates:
  - site/data/briefs.json     — All briefs metadata
  - site/data/latest.json     — Most recent brief per category
  - site/data/categories.json — Briefs grouped by category
"""

import glob
import json
import re
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BRIEFS_DIR = REPO_ROOT / "briefs"
DATA_DIR = REPO_ROOT / "site" / "data"


def extract_frontmatter(content: str) -> dict:
    """Simple YAML frontmatter extraction."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        if line.strip().startswith("-"):
            continue  # skip YAML block-list items; they are not scalar frontmatter keys
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value.startswith("["):
                value = [v.strip().strip("- ").strip() for v in value.strip("[]").split(",") if v.strip()]
            fm[key] = value
    return fm


def collect_all_briefs() -> list[dict]:
    """Collect all briefs with their frontmatter."""
    briefs = []
    pattern = str(BRIEFS_DIR / "**" / "*.md")
    for filepath in sorted(glob.glob(pattern, recursive=True)):
        with open(filepath, "r") as f:
            content = f.read()
        fm = extract_frontmatter(content)
        if fm:
            fm["_file"] = str(Path(filepath).relative_to(REPO_ROOT))
            briefs.append(fm)
    return briefs


def build_feeds():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    briefs = collect_all_briefs()

    # All briefs
    with open(DATA_DIR / "briefs.json", "w") as f:
        json.dump(briefs, f, indent=2, default=str)

    # Latest per category
    latest = {}
    for b in briefs:
        cat = b.get("category", "unknown")
        if cat not in latest or b.get("date", "") > latest[cat].get("date", ""):
            latest[cat] = b
    with open(DATA_DIR / "latest.json", "w") as f:
        json.dump(latest, f, indent=2, default=str)

    # Grouped by category
    categories = {}
    for b in briefs:
        cat = b.get("category", "unknown")
        categories.setdefault(cat, []).append(b)
    with open(DATA_DIR / "categories.json", "w") as f:
        json.dump(categories, f, indent=2, default=str)

    print(f"Generated feeds: {len(briefs)} briefs, {len(latest)} categories")


if __name__ == "__main__":
    build_feeds()
