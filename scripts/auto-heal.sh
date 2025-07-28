#!/bin/bash

# Auto-healing script for ToolChest Hugo site
# Creates missing _index.md files automatically
# Run before every build to ensure structural integrity

echo "🔧 Auto-healing ToolChest structure..."

# Function to create a basic _index.md file
create_index_file() {
    local dir="$1"
    local category=$(basename $(dirname "$dir"))
    local subcategory=$(basename "$dir")
    
    # Convert dashes to spaces and capitalize
    local title=$(echo "$subcategory" | sed 's/-/ /g' | sed 's/\b\w/\U&/g')
    
    cat > "$dir/_index.md" << EOF
---
title: "$title"
description: "Tools and solutions in the $title category"
---
EOF
    echo "✅ Created: $dir/_index.md"
}

# Find and fix missing _index.md files in subcategories
missing_count=0
for dir in $(find content/categories -mindepth 2 -maxdepth 2 -type d); do
    if [ ! -f "$dir/_index.md" ]; then
        create_index_file "$dir"
        ((missing_count++))
    fi
done

# Verify all tool files have proper frontmatter
echo "🔍 Checking tool files..."
tool_fixes=0
for file in $(find content/categories -name "*.md" -not -name "_index.md"); do
    if ! grep -q "^---" "$file"; then
        echo "⚠️  Missing frontmatter: $file"
        # Could add auto-fix here if needed
    fi
done

echo "🏁 Auto-healing complete:"
echo "   - Fixed $missing_count missing _index.md files"
echo "   - Site structure is now tank-proof!"