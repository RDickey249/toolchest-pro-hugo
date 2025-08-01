#!/usr/bin/env python3
"""Fix YAML parsing issues in taglines containing markdown links."""

import os
import re
from pathlib import Path

def fix_tagline_yaml(file_path):
    """Fix taglines that contain markdown links or other YAML-breaking characters."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.startswith('---'):
        return False
    
    # Split frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    
    frontmatter = parts[1]
    body = parts[2]
    
    # Check for problematic taglines
    tagline_match = re.search(r'^tagline:\s*"([^"]*)"', frontmatter, re.MULTILINE)
    if not tagline_match:
        return False
    
    tagline = tagline_match.group(1)
    
    # Check if tagline contains markdown links or other problematic characters
    if '[' in tagline and ']' in tagline and '(' in tagline and ')' in tagline:
        # Clean the tagline by removing markdown links
        # Convert [text](url) to just text
        clean_tagline = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', tagline)
        
        # Remove any remaining brackets or problematic characters
        clean_tagline = re.sub(r'[\[\]()]', '', clean_tagline)
        
        # Clean up multiple spaces and trailing text
        clean_tagline = re.sub(r'\s+', ' ', clean_tagline).strip()
        
        # Truncate if too long
        if len(clean_tagline) > 80:
            clean_tagline = clean_tagline[:77] + '...'
        
        # Replace the tagline in frontmatter
        new_frontmatter = re.sub(
            r'^tagline:\s*"[^"]*"',
            f'tagline: "{clean_tagline}"',
            frontmatter,
            flags=re.MULTILINE
        )
        
        # Write back the file
        new_content = f"---{new_frontmatter}---{body}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    
    return False

def main():
    """Fix all problematic taglines."""
    content_dir = Path('content/categories')
    fixed_count = 0
    
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                file_path = Path(root) / file
                try:
                    if fix_tagline_yaml(file_path):
                        fixed_count += 1
                        print(f"✅ Fixed tagline YAML: {file_path.name}")
                except Exception as e:
                    print(f"❌ Error fixing {file_path.name}: {e}")
    
    print(f"\nFixed {fixed_count} files with problematic taglines")

if __name__ == '__main__':
    main()