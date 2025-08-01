#!/usr/bin/env python3
"""Audit tool files against database structure."""

import os
from pathlib import Path
import json

def audit_tools():
    """Audit all tool files in the Hugo structure."""
    
    content_dir = Path('content/categories')
    
    # Track findings
    categories = {}
    all_tools = []
    subcategory_index_files = []
    category_index_files = []
    
    # Walk the directory structure
    for root, dirs, files in os.walk(content_dir):
        root_path = Path(root)
        
        # Skip if we're at the root categories level
        if root_path == content_dir:
            continue
            
        # Get relative path parts
        rel_parts = root_path.relative_to(content_dir).parts
        
        if len(rel_parts) == 1:
            # This is a category directory
            category = rel_parts[0]
            if category not in categories:
                categories[category] = {
                    'subcategories': {},
                    'tools': []
                }
            
            # Check for _index.md
            if '_index.md' in files:
                category_index_files.append(str(root_path / '_index.md'))
                
            # Check for tools directly in category (no subcategory)
            for file in files:
                if file.endswith('.md') and file != '_index.md':
                    tool_path = root_path / file
                    categories[category]['tools'].append({
                        'file': file,
                        'path': str(tool_path),
                        'subcategory': None
                    })
                    all_tools.append(str(tool_path))
                    
        elif len(rel_parts) == 2:
            # This is a subcategory directory
            category = rel_parts[0]
            subcategory = rel_parts[1]
            
            if category not in categories:
                categories[category] = {
                    'subcategories': {},
                    'tools': []
                }
                
            if subcategory not in categories[category]['subcategories']:
                categories[category]['subcategories'][subcategory] = []
            
            # Check for _index.md
            if '_index.md' in files:
                subcategory_index_files.append(str(root_path / '_index.md'))
                
            # Check for tools in subcategory
            for file in files:
                if file.endswith('.md') and file != '_index.md':
                    tool_path = root_path / file
                    categories[category]['subcategories'][subcategory].append({
                        'file': file,
                        'path': str(tool_path)
                    })
                    all_tools.append(str(tool_path))
    
    # Generate report
    print("=== TOOL AUDIT REPORT ===\n")
    
    print(f"Total categories found: {len(categories)}")
    print(f"Total tools found: {len(all_tools)}")
    print(f"Category index files: {len(category_index_files)}")
    print(f"Subcategory index files: {len(subcategory_index_files)}")
    print(f"Total index files: {len(category_index_files) + len(subcategory_index_files)}")
    
    print("\n=== CATEGORIES BREAKDOWN ===\n")
    
    # Sort categories by name
    for cat_name in sorted(categories.keys()):
        cat_data = categories[cat_name]
        total_tools = len(cat_data['tools'])
        
        # Count tools in subcategories
        for subcat_name, subcat_tools in cat_data['subcategories'].items():
            total_tools += len(subcat_tools)
            
        print(f"\n{cat_name}: {total_tools} tools")
        
        # Show tools directly in category
        if cat_data['tools']:
            print(f"  Direct tools (no subcategory): {len(cat_data['tools'])}")
            
        # Show subcategories
        if cat_data['subcategories']:
            print(f"  Subcategories: {len(cat_data['subcategories'])}")
            for subcat_name in sorted(cat_data['subcategories'].keys()):
                subcat_tools = cat_data['subcategories'][subcat_name]
                print(f"    - {subcat_name}: {len(subcat_tools)} tools")
    
    print("\n=== SUMMARY ===")
    print(f"\nTotal files in content/categories: {len(all_tools) + len(category_index_files) + len(subcategory_index_files)}")
    print(f"  - Tool pages (.md): {len(all_tools)}")
    print(f"  - Index pages (_index.md): {len(category_index_files) + len(subcategory_index_files)}")
    
    # Check for expected 1,296 tools
    print(f"\nExpected tools: 1,296")
    print(f"Actual tools: {len(all_tools)}")
    print(f"Difference: {len(all_tools) - 1296}")

if __name__ == '__main__':
    audit_tools()