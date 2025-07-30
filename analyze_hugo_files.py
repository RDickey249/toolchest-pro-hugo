#!/usr/bin/env python3
"""
Hugo Files Analysis Script

Analyzes two lists of Hugo files to find differences and extract subcategory information.
- List 1: Files containing "Get Started with" text
- List 2: Files containing HTML button format
- Finds files in List 1 but NOT in List 2 (files missing HTML button format)
- Groups by subcategory and counts tools needing fixes
"""

import os
import re
from collections import defaultdict, Counter
from pathlib import Path


def parse_file_path(file_path):
    """
    Parse Hugo file path to extract main category, subcategory, and tool name.
    
    Expected pattern: content/categories/[main-category]/[subcategory]/[tool].md
    
    Args:
        file_path (str): Full file path
        
    Returns:
        tuple: (main_category, subcategory, tool_name) or (None, None, None) if parsing fails
    """
    # Normalize path and extract the relevant part
    path = Path(file_path)
    
    # Look for the pattern: content/categories/[main-category]/[subcategory]/[tool].md
    parts = path.parts
    
    try:
        # Find 'content' and 'categories' in the path
        content_idx = None
        categories_idx = None
        
        for i, part in enumerate(parts):
            if part == 'content':
                content_idx = i
            elif part == 'categories' and content_idx is not None and i == content_idx + 1:
                categories_idx = i
                break
        
        if categories_idx is None or len(parts) < categories_idx + 4:
            return None, None, None
            
        main_category = parts[categories_idx + 1]
        subcategory = parts[categories_idx + 2]
        tool_name = path.stem  # filename without extension
        
        return main_category, subcategory, tool_name
        
    except (IndexError, AttributeError):
        return None, None, None


def read_file_list(file_content, list_name):
    """
    Read and parse file list from content.
    
    Args:
        file_content (str): Content containing file paths (one per line)
        list_name (str): Name for logging purposes
        
    Returns:
        set: Set of file paths
    """
    if not file_content.strip():
        print(f"Warning: {list_name} is empty")
        return set()
    
    # Split by lines and filter out empty lines
    file_paths = [line.strip() for line in file_content.strip().split('\n') if line.strip()]
    
    print(f"{list_name}: {len(file_paths)} files")
    return set(file_paths)


def analyze_hugo_files(list1_content, list2_content):
    """
    Main analysis function to find differences and group by subcategory.
    
    Args:
        list1_content (str): Content of List 1 (files with "Get Started with")
        list2_content (str): Content of List 2 (files with HTML button format)
        
    Returns:
        dict: Analysis results
    """
    print("=== Hugo Files Analysis ===\n")
    
    # Parse file lists
    list1_files = read_file_list(list1_content, "List 1 (Get Started with)")
    list2_files = read_file_list(list2_content, "List 2 (HTML button format)")
    
    # Find files in List 1 but NOT in List 2 (files needing fixes)
    files_needing_fixes = list1_files - list2_files
    
    print(f"\nFiles needing HTML button format fixes: {len(files_needing_fixes)}")
    print(f"Files already with proper format: {len(list1_files & list2_files)}")
    
    if not files_needing_fixes:
        print("No files need fixes!")
        return {}
    
    # Group by subcategory
    subcategory_data = defaultdict(lambda: {'count': 0, 'files': []})
    parsing_errors = []
    
    for file_path in files_needing_fixes:
        main_category, subcategory, tool_name = parse_file_path(file_path)
        
        if subcategory is None:
            parsing_errors.append(file_path)
            continue
            
        subcategory_data[subcategory]['count'] += 1
        subcategory_data[subcategory]['files'].append({
            'path': file_path,
            'main_category': main_category,
            'tool_name': tool_name
        })
    
    if parsing_errors:
        print(f"\nWarning: Could not parse {len(parsing_errors)} file paths:")
        for error_path in parsing_errors[:5]:  # Show first 5 errors
            print(f"  {error_path}")
        if len(parsing_errors) > 5:
            print(f"  ... and {len(parsing_errors) - 5} more")
    
    # Sort by count (descending) and get top 10
    sorted_subcategories = sorted(
        subcategory_data.items(), 
        key=lambda x: x[1]['count'], 
        reverse=True
    )
    
    return {
        'total_files_needing_fixes': len(files_needing_fixes),
        'total_files_with_format': len(list1_files & list2_files),
        'subcategory_data': dict(subcategory_data),
        'sorted_subcategories': sorted_subcategories,
        'parsing_errors': parsing_errors
    }


def print_top_subcategories(results, top_n=10):
    """Print the top N subcategories with most fixes needed."""
    
    if not results or 'sorted_subcategories' not in results:
        print("No results to display")
        return
    
    sorted_subcategories = results['sorted_subcategories']
    
    print(f"\n=== Top {top_n} Subcategories Needing Fixes ===\n")
    
    for i, (subcategory, data) in enumerate(sorted_subcategories[:top_n], 1):
        count = data['count']
        files = data['files']
        
        print(f"{i}. {subcategory}")
        print(f"   Files needing fixes: {count}")
        
        # Show main categories for this subcategory
        main_categories = set(f['main_category'] for f in files)
        if main_categories:
            print(f"   Main categories: {', '.join(sorted(main_categories))}")
        
        # Show example file paths (up to 3)
        print("   Example files:")
        for j, file_info in enumerate(files[:3], 1):
            print(f"     {j}. {file_info['tool_name']} ({file_info['path']})")
        
        if len(files) > 3:
            print(f"     ... and {len(files) - 3} more files")
        
        print()


def main():
    """
    Main function - prompts user for file lists and runs analysis.
    """
    print("Hugo Files Analysis Tool")
    print("========================")
    print()
    print("This script will analyze two lists of Hugo files to find differences.")
    print("Please provide the file lists when prompted.")
    print()
    
    # Get List 1 content
    print("Please paste List 1 content (files with 'Get Started with' text):")
    print("Paste the content and press Enter twice when finished:")
    list1_lines = []
    while True:
        try:
            line = input()
            if line == "" and list1_lines and list1_lines[-1] == "":
                break
            list1_lines.append(line)
        except EOFError:
            break
    
    list1_content = '\n'.join(list1_lines).strip()
    
    print("\nPlease paste List 2 content (files with HTML button format):")
    print("Paste the content and press Enter twice when finished:")
    list2_lines = []
    while True:
        try:
            line = input()
            if line == "" and list2_lines and list2_lines[-1] == "":
                break
            list2_lines.append(line)
        except EOFError:
            break
    
    list2_content = '\n'.join(list2_lines).strip()
    
    # Run analysis
    results = analyze_hugo_files(list1_content, list2_content)
    
    if results:
        print_top_subcategories(results, top_n=10)
        
        # Summary
        print("=== Summary ===")
        print(f"Total files with 'Get Started with': {len(read_file_list(list1_content, 'temp'))}")
        print(f"Total files with HTML button format: {len(read_file_list(list2_content, 'temp'))}")
        print(f"Files needing fixes: {results['total_files_needing_fixes']}")
        print(f"Files already formatted: {results['total_files_with_format']}")
        print(f"Unique subcategories needing fixes: {len(results['subcategory_data'])}")


if __name__ == "__main__":
    main()