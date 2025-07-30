#!/usr/bin/env python3
"""
Analyze Hugo files to find those with "Get Started with" but missing HTML button format.
Extract subcategories and count files needing fixes.
"""

import re
from collections import defaultdict, Counter
from pathlib import Path

def parse_file_path(file_path):
    """
    Parse Hugo file path to extract main category, subcategory, and tool name.
    Expected pattern: content/categories/[main-category]/[subcategory]/[tool].md
    """
    # Remove the base path and focus on the categories structure
    if '/content/categories/' in file_path:
        # Extract the part after /content/categories/
        categories_part = file_path.split('/content/categories/')[1]
        parts = categories_part.split('/')
        
        if len(parts) >= 3 and parts[-1].endswith('.md'):
            main_category = parts[0]
            subcategory = parts[1]
            tool = parts[-1].replace('.md', '')
            return main_category, subcategory, tool
    
    return None, None, None

def analyze_files():
    """Analyze the grep results and find files needing fixes."""
    
    # Files with "Get Started with" text
    list1_files = [
        "/home/yan/toolchest-pro-hugo/content/categories/communication-collaboration/document-collaboration/logseq.md",
        "/home/yan/toolchest-pro-hugo/content/categories/communication-collaboration/async-communication/screenpal.md",
        "/home/yan/toolchest-pro-hugo/content/categories/ai-tools-assistants/ai-productivity-business/monkeylearn.md",
        "/home/yan/toolchest-pro-hugo/content/categories/ai-tools-assistants/ai-productivity-business/polymer.md",
        "/home/yan/toolchest-pro-hugo/content/categories/ai-tools-assistants/ai-productivity-business/yurbi.md",
        # Add more files from grep results...
    ]
    
    # Files with HTML button format
    list2_files = [
        "/home/yan/toolchest-pro-hugo/content/categories/communication-collaboration/document-collaboration/logseq.md",
        "/home/yan/toolchest-pro-hugo/content/categories/communication-collaboration/async-communication/screenpal.md",
        "/home/yan/toolchest-pro-hugo/content/categories/ai-tools-assistants/ai-productivity-business/monkeylearn.md",
        "/home/yan/toolchest-pro-hugo/content/categories/ai-tools-assistants/ai-productivity-business/polymer.md",
        "/home/yan/toolchest-pro-hugo/content/categories/ai-tools-assistants/ai-productivity-business/yurbi.md",
        # Add more files from grep results...
    ]
    
    print("Reading actual grep results from files...")
    return list1_files, list2_files

def get_grep_results():
    """Get the actual grep results by running the commands again."""
    import subprocess
    
    print("Getting files with 'Get Started with' text...")
    result1 = subprocess.run(['grep', '-r', '-l', 'Get Started with', 'content/'], 
                           capture_output=True, text=True, cwd='/home/yan/toolchest-pro-hugo')
    list1_files = [line.strip() for line in result1.stdout.split('\n') if line.strip()]
    list1_files = [f'/home/yan/toolchest-pro-hugo/{f}' for f in list1_files]
    
    print("Getting files with HTML button format...")
    result2 = subprocess.run(['grep', '-r', '-l', 'div style="text-align: center; margin: 2rem 0;"', 'content/'], 
                           capture_output=True, text=True, cwd='/home/yan/toolchest-pro-hugo')
    list2_files = [line.strip() for line in result2.stdout.split('\n') if line.strip()]
    list2_files = [f'/home/yan/toolchest-pro-hugo/{f}' for f in list2_files]
    
    return list1_files, list2_files

def main():
    """Main analysis function."""
    
    # Get the file lists
    list1_files, list2_files = get_grep_results()
    
    print(f"Files with 'Get Started with': {len(list1_files)}")
    print(f"Files with HTML button format: {len(list2_files)}")
    
    # Convert to sets for set operations
    set1 = set(list1_files)
    set2 = set(list2_files)
    
    # Find files in List 1 but NOT in List 2 (files needing fixes)
    files_needing_fixes = set1 - set2
    
    print(f"\nFiles needing HTML button format fixes: {len(files_needing_fixes)}")
    
    # Group by subcategory
    subcategory_counts = defaultdict(list)
    subcategory_info = {}
    
    for file_path in files_needing_fixes:
        main_category, subcategory, tool = parse_file_path(file_path)
        
        if subcategory:  # Only count valid paths
            subcategory_counts[subcategory].append(file_path)
            subcategory_info[subcategory] = {
                'main_category': main_category,
                'count': len(subcategory_counts[subcategory])
            }
    
    # Sort subcategories by count (descending)
    sorted_subcategories = sorted(subcategory_counts.items(), 
                                key=lambda x: len(x[1]), 
                                reverse=True)
    
    print(f"\n{'='*80}")
    print("TOP 10 SUBCATEGORIES WITH MOST FILES NEEDING FIXES")
    print(f"{'='*80}")
    
    for i, (subcategory, files) in enumerate(sorted_subcategories[:10], 1):
        main_category = subcategory_info[subcategory]['main_category']
        count = len(files)
        
        print(f"\n{i}. {subcategory.upper().replace('-', ' ')}")
        print(f"   Main Category: {main_category}")
        print(f"   Files needing fixes: {count}")
        print(f"   Example files:")
        
        # Show up to 3 example files
        for j, file_path in enumerate(files[:3], 1):
            tool_name = Path(file_path).stem
            print(f"     {j}. {tool_name}.md")
        
        if count > 3:
            print(f"     ... and {count - 3} more files")
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total files with 'Get Started with': {len(list1_files)}")
    print(f"Total files with HTML button format: {len(list2_files)}")
    print(f"Total files needing fixes: {len(files_needing_fixes)}")
    print(f"Unique subcategories needing fixes: {len(subcategory_counts)}")
    
    # Show overlap statistics
    overlap = set1 & set2
    print(f"Files with both features: {len(overlap)}")
    print(f"Percentage needing fixes: {len(files_needing_fixes)/len(set1)*100:.1f}%")

if __name__ == "__main__":
    main()