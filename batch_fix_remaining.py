#!/usr/bin/env python3
"""
Batch fix all remaining HTML button files using direct string replacement.
"""

import glob
import re

def fix_file(file_path):
    """Fix a single file by replacing HTML buttons with simple markdown."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it has HTML buttons
        if 'target="_blank"' not in content:
            return False
        
        # Extract tool name from the title
        title_match = re.search(r'title: "([^"]+)"', content)
        tool_name = title_match.group(1) if title_match else "this tool"
        
        # Extract the first URL
        url_match = re.search(r'href="([^"]+)"', content)
        primary_url = url_match.group(1) if url_match else "#"
        
        # Replace the entire HTML section with simple format
        # Use a very broad pattern to catch all variations
        html_pattern = r'<div style="text-align: center.*?</div>'
        
        replacement = f'Ready to get started? Visit [{tool_name}]({primary_url}) to explore the platform and begin using this tool.'
        
        new_content = re.sub(html_pattern, replacement, content, flags=re.DOTALL)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    # Get all files that still have HTML buttons
    all_md_files = glob.glob('content/categories/**/*.md', recursive=True)
    tool_files = [f for f in all_md_files if not f.endswith('_index.md')]
    
    remaining_files = []
    for file in tool_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                if 'target="_blank"' in f.read():
                    remaining_files.append(file)
        except:
            continue
    
    print(f"Fixing {len(remaining_files)} remaining files...")
    fixed_count = 0
    
    for file_path in remaining_files:
        if fix_file(file_path):
            fixed_count += 1
            print(f"✓ Fixed: {file_path}")
        else:
            print(f"✗ Failed: {file_path}")
    
    print(f"\nFixed {fixed_count} files successfully!")

if __name__ == "__main__":
    main()