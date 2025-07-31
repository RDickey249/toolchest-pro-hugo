#!/usr/bin/env python3
"""
Add proper frontmatter to the 233 pages that are missing it.
"""

import glob
import os
import re

def extract_category_info(file_path):
    """Extract category and subcategory from file path."""
    parts = file_path.split('/')
    if len(parts) >= 4:
        category = parts[2].replace('-', ' ').title()
        subcategory = parts[3].replace('-', ' ').title()
        return category, subcategory
    return "Unknown", "Unknown"

def extract_tool_name_from_content(content):
    """Extract tool name from the first heading."""
    # Look for first # heading
    match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Fallback: extract from filename
    return None

def generate_frontmatter(file_path, content):
    """Generate appropriate frontmatter for a file."""
    
    # Extract tool name from content
    tool_name = extract_tool_name_from_content(content)
    if not tool_name:
        # Fallback to filename
        filename = os.path.basename(file_path)
        tool_name = filename.replace('.md', '').replace('-', ' ').title()
    
    # Extract category info from path
    category, subcategory = extract_category_info(file_path)
    
    # Generate a simple tagline from first paragraph
    tagline = "Professional tool for enhanced productivity and workflow management"
    
    # Try to extract a better tagline from content
    paragraphs = content.split('\n\n')
    for p in paragraphs:
        if len(p) > 50 and len(p) < 200 and not p.startswith('#'):
            # Clean the paragraph
            clean_p = re.sub(r'[*_`]', '', p).strip()
            if clean_p:
                tagline = clean_p[:150] + "..."
                break
    
    # Create frontmatter
    frontmatter = f'''---
title: "{tool_name}"
tagline: "{tagline}"
category: "{category}"
subcategory: "{subcategory}"
tool_name: "{tool_name}"
deployment_status: "deployed"
image: "/images/tools/{os.path.basename(file_path).replace('.md', '')}-placeholder.jpg"
---

'''
    
    return frontmatter

def fix_file(file_path):
    """Add frontmatter to a file that's missing it."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has frontmatter
        if content.startswith('---'):
            return False
        
        # Generate and prepend frontmatter
        frontmatter = generate_frontmatter(file_path, content)
        new_content = frontmatter + content
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all files missing frontmatter."""
    
    # Find all tool files
    md_files = glob.glob('content/categories/**/*.md', recursive=True)
    tool_files = [f for f in md_files if not f.endswith('_index.md')]
    
    # Find files missing frontmatter
    missing_frontmatter = []
    for file_path in tool_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if not content.startswith('---'):
                missing_frontmatter.append(file_path)
        except:
            continue
    
    print(f"Found {len(missing_frontmatter)} files missing frontmatter")
    print("=" * 60)
    
    fixed_count = 0
    for file_path in missing_frontmatter:
        if fix_file(file_path):
            fixed_count += 1
            print(f"✓ Added frontmatter: {file_path}")
        else:
            print(f"✗ Failed: {file_path}")
    
    print("=" * 60)
    print(f"Successfully added frontmatter to {fixed_count} files")

if __name__ == "__main__":
    main()