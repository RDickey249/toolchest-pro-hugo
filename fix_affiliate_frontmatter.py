#!/usr/bin/env python3
"""Fix affiliate frontmatter formatting issues."""

import os
from pathlib import Path
import re

def fix_frontmatter_formatting(file_path):
    """Fix frontmatter formatting issues."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.startswith('---'):
        return False
    
    # Find where the frontmatter ends incorrectly
    if '---' in content and content.count('---') >= 2:
        # Split and fix
        parts = content.split('---')
        if len(parts) >= 3:
            frontmatter = parts[1]
            
            # Check if frontmatter has affiliate fields at the end without proper closing
            if ('affiliate_tier:' in frontmatter and 
                not frontmatter.strip().endswith('---') and 
                frontmatter.count('\n') > 1):
                
                # Fix the frontmatter
                lines = frontmatter.split('\n')
                clean_lines = []
                
                for line in lines:
                    if line.strip():
                        clean_lines.append(line)
                
                # Rebuild content
                new_frontmatter = '\n'.join(clean_lines)
                body = '---'.join(parts[2:])
                
                new_content = f"---\n{new_frontmatter}\n---{body}"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
    
    return False

def main():
    """Fix all affiliate tool files."""
    content_dir = Path('content/categories')
    fixed_count = 0
    
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                file_path = Path(root) / file
                try:
                    if fix_frontmatter_formatting(file_path):
                        fixed_count += 1
                        print(f"✅ Fixed frontmatter: {file_path.name}")
                except Exception as e:
                    print(f"❌ Error fixing {file_path.name}: {e}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()