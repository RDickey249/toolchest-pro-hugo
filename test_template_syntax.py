#!/usr/bin/env python3
"""Test Hugo template files for basic syntax issues."""

import os
from pathlib import Path
import re

def check_template_syntax(file_path):
    """Check for common Hugo template syntax issues."""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check for unmatched template delimiters
    open_delims = content.count('{{')
    close_delims = content.count('}}')
    if open_delims != close_delims:
        issues.append(f"Unmatched template delimiters: {open_delims} {{ vs {close_delims} }}")
    
    # Check for unmatched template blocks
    define_count = len(re.findall(r'{{\s*define\s+', content))
    end_count = len(re.findall(r'{{\s*end\s*}}', content))
    if define_count != end_count:
        issues.append(f"Unmatched define/end blocks: {define_count} define vs {end_count} end")
    
    # Check for suspicious patterns
    for i, line in enumerate(lines, 1):
        if '{{' in line and '}}' not in line:
            issues.append(f"Line {i}: Possible incomplete template expression")
        if 'Site.Data.' in line and ('-' in line.split('Site.Data.')[1].split()[0]):
            issues.append(f"Line {i}: Data file with hyphen should use underscore")
    
    return issues

def main():
    """Check all template files."""
    layouts_dir = Path('layouts')
    total_issues = 0
    
    for root, dirs, files in os.walk(layouts_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = Path(root) / file
                issues = check_template_syntax(file_path)
                
                if issues:
                    print(f"\n❌ {file_path}:")
                    for issue in issues:
                        print(f"  - {issue}")
                    total_issues += len(issues)
                else:
                    print(f"✅ {file_path.name}")
    
    print(f"\n=== TEMPLATE SYNTAX CHECK COMPLETE ===")
    print(f"Total issues found: {total_issues}")

if __name__ == '__main__':
    main()