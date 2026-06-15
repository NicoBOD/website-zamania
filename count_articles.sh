#!/bin/bash
DOCS_DIR="/opt/data/wiki-tech-automation/repo/docs"
CATEGORIES=("systemes" "reseaux" "cloud" "cybersecurite" "ia" "automatisation" "logiciels" "debug" "astuces")

echo "Counts (excluding index.md):"
for cat in "${CATEGORIES[@]}"; do
    if [ -d "$DOCS_DIR/$cat" ]; then
        count=$(find "$DOCS_DIR/$cat" -name "*.md" ! -name "index.md" | wc -l)
        echo "$cat: $count"
    else
        echo "$cat: 0 (dir not found)"
    fi
done
