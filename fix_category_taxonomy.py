#!/usr/bin/env python3
"""Fix category taxonomy issues where tools aren't showing up in categories."""

import os
import yaml
from pathlib import Path
import re

def load_category_mappings():
    """Load the category mappings from categories.yaml."""
    with open('data/categories.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_category_from_path(file_path, category_mappings):
    """Determine the correct category from the file path."""
    path_parts = Path(file_path).parts
    if len(path_parts) >= 3 and path_parts[1] == 'categories':
        category_slug = path_parts[2]
        return category_mappings.get(category_slug, category_slug)
    return None

def fix_tool_categories(file_path, category_mappings):
    """Fix category assignments in a tool file."""
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
    
    # Determine correct category from file path
    correct_category = get_category_from_path(file_path, category_mappings)
    if not correct_category:
        return False
    
    # Check current category field
    category_match = re.search(r'^category:\s*"([^"]*)"', frontmatter, re.MULTILINE)
    categories_match = re.search(r'^categories:\s*\["([^"]*)"\]', frontmatter, re.MULTILINE)
    
    changes_made = False
    
    # Update category field
    if category_match and category_match.group(1) != correct_category:
        frontmatter = re.sub(
            r'^category:\s*"[^"]*"',
            f'category: "{correct_category}"',
            frontmatter,
            flags=re.MULTILINE
        )
        changes_made = True
    elif not category_match:
        frontmatter += f'\ncategory: "{correct_category}"'
        changes_made = True
    
    # Update categories field
    if categories_match and categories_match.group(1) != correct_category:
        frontmatter = re.sub(
            r'^categories:\s*\[[^\]]*\]',
            f'categories: ["{correct_category}"]',
            frontmatter,
            flags=re.MULTILINE
        )
        changes_made = True
    elif not categories_match:
        frontmatter += f'\ncategories: ["{correct_category}"]'
        changes_made = True
    
    if changes_made:
        # Write back the file
        new_content = f"---{frontmatter}---{body}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def main():
    """Fix category taxonomy for all tools."""
    category_mappings = load_category_mappings()
    
    # Focus on the problematic categories
    problem_categories = [
        'cloud-storage-file-management',
        'database-data-management', 
        'hardware-equipment-tools',
        'legal-compliance-tools',
        'travel-expense-management',
        'e-commerce-business-tools'
    ]
    
    fixed_count = 0
    
    for category_slug in problem_categories:
        category_dir = Path(f'content/categories/{category_slug}')
        if not category_dir.exists():
            continue
        
        print(f"\n=== Fixing {category_slug} ===")
        
        for root, dirs, files in os.walk(category_dir):
            for file in files:
                if file.endswith('.md') and file != '_index.md':
                    file_path = Path(root) / file
                    try:
                        if fix_tool_categories(file_path, category_mappings):
                            fixed_count += 1
                            print(f"✅ Fixed: {file_path.name}")
                    except Exception as e:
                        print(f"❌ Error fixing {file_path.name}: {e}")
    
    print(f"\n=== CATEGORY TAXONOMY FIX COMPLETE ===")
    print(f"Fixed {fixed_count} tool files")

if __name__ == '__main__':
    main()