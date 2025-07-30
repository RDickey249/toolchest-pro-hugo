#!/usr/bin/env python3
"""
Get detailed examples for the top subcategories needing fixes.
"""

import subprocess
from collections import defaultdict
from pathlib import Path

def parse_file_path(file_path):
    """Parse Hugo file path to extract subcategory info."""
    if '/content/categories/' in file_path:
        categories_part = file_path.split('/content/categories/')[1]
        parts = categories_part.split('/')
        
        if len(parts) >= 3 and parts[-1].endswith('.md'):
            main_category = parts[0]
            subcategory = parts[1]
            tool = parts[-1].replace('.md', '')
            return main_category, subcategory, tool
    
    return None, None, None

def get_files_needing_fixes():
    """Get files that need HTML button format fixes."""
    
    # Get files with "Get Started with"
    result1 = subprocess.run(['grep', '-r', '-l', 'Get Started with', 'content/'], 
                           capture_output=True, text=True, cwd='/home/yan/toolchest-pro-hugo')
    list1_files = [line.strip() for line in result1.stdout.split('\n') if line.strip()]
    list1_files = [f'/home/yan/toolchest-pro-hugo/{f}' for f in list1_files]
    
    # Get files with HTML button format
    result2 = subprocess.run(['grep', '-r', '-l', 'div style="text-align: center; margin: 2rem 0;"', 'content/'], 
                           capture_output=True, text=True, cwd='/home/yan/toolchest-pro-hugo')
    list2_files = [line.strip() for line in result2.stdout.split('\n') if line.strip()]
    list2_files = [f'/home/yan/toolchest-pro-hugo/{f}' for f in list2_files]
    
    # Find files needing fixes
    set1 = set(list1_files)
    set2 = set(list2_files)
    files_needing_fixes = set1 - set2
    
    return files_needing_fixes

def main():
    """Show detailed examples for top subcategories."""
    
    files_needing_fixes = get_files_needing_fixes()
    
    # Group by subcategory
    subcategory_files = defaultdict(list)
    
    for file_path in files_needing_fixes:
        main_category, subcategory, tool = parse_file_path(file_path)
        if subcategory:
            subcategory_files[subcategory].append({
                'path': file_path,
                'main_category': main_category,
                'tool': tool
            })
    
    # Sort by count
    sorted_subcategories = sorted(subcategory_files.items(), 
                                key=lambda x: len(x[1]), 
                                reverse=True)
    
    print("DETAILED BREAKDOWN - TOP 10 SUBCATEGORIES NEEDING FIXES")
    print("=" * 80)
    
    for i, (subcategory, files) in enumerate(sorted_subcategories[:10], 1):
        main_category = files[0]['main_category']
        count = len(files)
        
        print(f"\n{i}. {subcategory.upper().replace('-', ' ')} ({count} files)")
        print(f"   Main Category: {main_category}")
        print(f"   File examples:")
        
        # Show all files for smaller categories, or first 5 for larger ones
        show_count = min(count, 8)
        for j, file_info in enumerate(files[:show_count], 1):
            print(f"     • {file_info['tool']}.md")
        
        if count > show_count:
            print(f"     • ... and {count - show_count} more files")
        
        print()

if __name__ == "__main__":
    main()