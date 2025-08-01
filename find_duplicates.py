#!/usr/bin/env python3
"""Find duplicate tool files."""

import os
from pathlib import Path
from collections import defaultdict

def find_duplicates():
    """Find duplicate tool files based on filename."""
    
    content_dir = Path('content/categories')
    
    # Track tool names and their paths
    tool_files = defaultdict(list)
    
    # Walk the directory structure
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                tool_name = file[:-3]  # Remove .md extension
                full_path = os.path.join(root, file)
                tool_files[tool_name].append(full_path)
    
    # Find duplicates
    duplicates = {name: paths for name, paths in tool_files.items() if len(paths) > 1}
    
    print(f"=== DUPLICATE TOOLS REPORT ===\n")
    print(f"Total unique tool names: {len(tool_files)}")
    print(f"Duplicate tool names: {len(duplicates)}")
    
    if duplicates:
        print("\n=== DUPLICATES FOUND ===\n")
        for tool_name, paths in sorted(duplicates.items()):
            print(f"\n{tool_name}: {len(paths)} copies")
            for path in paths:
                # Show relative path from content/categories
                rel_path = Path(path).relative_to(content_dir)
                print(f"  - {rel_path}")
    else:
        print("\nNo duplicates found!")
    
    # Also check for common duplicate patterns
    print("\n=== CHECKING FOR COMMON PATTERNS ===\n")
    
    # Check for tools in wrong categories
    time_tracking_tools = []
    for tool_name, paths in tool_files.items():
        for path in paths:
            if 'time-tracking-scheduling' in path:
                time_tracking_tools.append((tool_name, path))
    
    print(f"Tools in time-tracking-scheduling: {len(time_tracking_tools)}")
    
    # Check for known duplicates
    known_duplicates = [
        'clockify', 'timely', 'harvest', 'toggl', 'rescuetime', 
        'buddy-punch', 'ontheclock', 'paymo', 'clickup'
    ]
    
    print("\n=== KNOWN DUPLICATE PATTERNS ===\n")
    for dup_name in known_duplicates:
        if dup_name in tool_files and len(tool_files[dup_name]) > 1:
            print(f"{dup_name}:")
            for path in tool_files[dup_name]:
                rel_path = Path(path).relative_to(content_dir)
                print(f"  - {rel_path}")

if __name__ == '__main__':
    find_duplicates()