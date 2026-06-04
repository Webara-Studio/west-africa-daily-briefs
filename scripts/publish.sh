#!/bin/bash
# Publish script — run after a new brief is added
# Usage: ./scripts/publish.sh "Brief title" [path/to/brief.md]

set -e

BRIEF_TITLE="${1:-New Brief}"
BRIEF_PATH="${2}"

cd "$(dirname "$0")/.."

# Copy brief to correct location if path provided
if [ -n "$BRIEF_PATH" ] && [ -f "$BRIEF_PATH" ]; then
    TARGET="briefs/$(date +%Y)/$(date +%m)/"
    mkdir -p "$TARGET"
    cp "$BRIEF_PATH" "$TARGET"
fi

# Build feeds
python3 scripts/build_feeds.py

# Commit and push
git add briefs/ site/data/ newsletters/
git commit -m "📋 $BRIEF_TITLE — $(date +%Y-%m-%d)" --allow-empty
git push

echo "✅ Published: $BRIEF_TITLE"
