#!/usr/bin/env python3
"""
Weekly Newsletter Generator — West Africa Daily Briefs

Reads all daily briefs from the current week, compiles them into
a single engaging newsletter, and outputs a Markdown file.

Usage:
    python scripts/newsletter.py [--week YYYY-WNN] [--output path]
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BRIEFS_DIR = REPO_ROOT / "briefs"
NEWSLETTER_DIR = REPO_ROOT / "newsletters"


def get_week_bounds(week_num: int, year: int) -> tuple[date, date]:
    """Get Monday and Sunday dates for a given ISO week."""
    monday = datetime.strptime(f"{year}-W{week_num:02d}-1", "%G-W%V-%u").date()
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_current_week() -> tuple[int, int]:
    """Returns (week_number, year) for the current ISO week."""
    today = date.today()
    year, week, _ = today.isocalendar()
    return week, year


def collect_briefs(week_num: int, year: int) -> list[dict]:
    """Collect all briefs for a given week."""
    monday, sunday = get_week_bounds(week_num, year)
    briefs = []

    for i in range(7):
        day = monday + timedelta(days=i)
        pattern = str(BRIEFS_DIR / str(day.year) / f"{day.month:02d}" / f"{day.strftime('%Y-%m-%d')}*.md")
        matches = glob.glob(pattern)
        for match in matches:
            with open(match, "r") as f:
                content = f.read()
            briefs.append({"date": day, "file": match, "content": content})

    return sorted(briefs, key=lambda x: x["date"])


def extract_frontmatter(content: str) -> dict:
    """Simple YAML frontmatter extraction."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value.startswith("["):
                # Simple list parsing
                value = [v.strip().strip("- ").strip() for v in value.strip("[]").split(",") if v.strip()]
            fm[key] = value
    return fm


def generate_newsletter(briefs: list[dict], week_num: int, year: int) -> str:
    """Generate the weekly newsletter markdown."""
    monday, sunday = get_week_bounds(week_num, year)

    topic_emojis = {
        "tech": "📱",
        "crypto": "₿",
        "agribusiness": "🌾",
        "energy": "⚡",
        "stocks": "📈",
        "governance": "🌍",
        "trade": "📦",
    }

    topic_titles = {
        "tech": "Local App & Digital Product Ideas",
        "crypto": "Crypto & Digital Assets",
        "agribusiness": "Agribusiness & Commodities",
        "energy": "Renewable Energy & Power",
        "stocks": "IPOs & Stock Market Watch",
        "governance": "Governance, Regulation & Trade",
        "trade": "Import/Export Trade Trends",
    }

    lines = []
    lines.append(f"# West Africa Weekly Brief — Week {week_num}, {year}")
    lines.append(f"*{monday.strftime('%B %d')} – {sunday.strftime('%B %d, %Y')}*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## This Week at a Glance")
    lines.append("")

    # Summary table from frontmatter
    for brief in briefs:
        fm = extract_frontmatter(brief["content"])
        cat = fm.get("category", "general")
        emoji = topic_emojis.get(cat, "📋")
        topic = fm.get("topic", topic_titles.get(cat, "Daily Brief"))
        sentiment = fm.get("sentiment", "neutral")
        sentiment_icon = {"bullish": "🟢", "bearish": "🔴", "mixed": "🟡", "neutral": "⚪"}.get(sentiment, "⚪")
        takeaways = fm.get("key_takeaways", [])
        if isinstance(takeaways, list) and takeaways:
            top_takeaway = takeaways[0]
        else:
            top_takeaway = "See full brief below"
        day_name = brief["date"].strftime("%A")
        lines.append(f"{emoji} **{day_name} — {topic}** {sentiment_icon}")
        lines.append(f"  → {top_takeaway}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Full briefs
    for brief in briefs:
        fm = extract_frontmatter(brief["content"])
        cat = fm.get("category", "general")
        emoji = topic_emojis.get(cat, "📋")
        topic = fm.get("topic", topic_titles.get(cat, "Daily Brief"))
        day_name = brief["date"].strftime("%A %B %d")

        lines.append(f"## {emoji} {day_name} — {topic}")
        lines.append("")

        # Strip frontmatter from content for display
        body = re.sub(r"^---\n.*?\n---\n", "", brief["content"], flags=re.DOTALL).strip()
        lines.append(body)
        lines.append("")
        lines.append("---")
        lines.append("")

    # Footer
    lines.append("## Weekly Watch List")
    lines.append("")
    all_watch = []
    for brief in briefs:
        fm = extract_frontmatter(brief["content"])
        watch = fm.get("watch_list", [])
        if isinstance(watch, list):
            all_watch.extend(watch)
    for item in all_watch:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Compiled from daily research briefs. Published every Sunday.*")
    lines.append("*Source: [github.com/Oswald-Benjamin/west-africa-daily-briefs](https://github.com/Oswald-Benjamin/west-africa-daily-briefs)*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate weekly newsletter")
    parser.add_argument("--week", type=int, help="ISO week number (default: current week)")
    parser.add_argument("--year", type=int, help="Year (default: current year)")
    parser.add_argument("--output", type=str, help="Output file path (default: auto)")
    args = parser.parse_args()

    week_num = args.week or get_current_week()[0]
    year = args.year or get_current_week()[1]

    print(f"Generating newsletter for Week {week_num}, {year}...")

    briefs = collect_briefs(week_num, year)
    if not briefs:
        print(f"No briefs found for Week {week_num}, {year}")
        sys.exit(1)

    print(f"Found {len(briefs)} briefs")

    newsletter = generate_newsletter(briefs, week_num, year)

    if args.output:
        output_path = Path(args.output)
    else:
        NEWSLETTER_DIR.mkdir(parents=True, exist_ok=True)
        output_path = NEWSLETTER_DIR / str(year) / f"{year}-W{week_num:02d}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(newsletter)

    print(f"Newsletter written to {output_path}")


if __name__ == "__main__":
    main()
