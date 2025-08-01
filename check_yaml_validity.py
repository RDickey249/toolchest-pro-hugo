#!/usr/bin/env python3
"""Check for YAML parsing issues that could break Hugo builds."""

import os
import yaml
from pathlib import Path
import re

def check_frontmatter_validity(file_path):
    """Check if frontmatter is valid YAML."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return True, "No frontmatter"
        
        # Split frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "Invalid frontmatter structure"
        
        frontmatter = parts[1]
        
        # Try to parse as YAML
        try:
            yaml.safe_load(frontmatter)
            return True, "Valid YAML"
        except yaml.YAMLError as e:
            return False, f"YAML Error: {str(e)}"
            
    except Exception as e:
        return False, f"File error: {str(e)}"

def main():
    """Check all markdown files for YAML validity."""
    content_dir = Path('content/categories')
    issues = []
    checked = 0
    
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                file_path = Path(root) / file
                checked += 1
                
                is_valid, message = check_frontmatter_validity(file_path)
                if not is_valid:
                    issues.append((str(file_path), message))
                    print(f"❌ {file}: {message}")
    
    print(f"\n=== YAML VALIDATION COMPLETE ===")
    print(f"Checked: {checked} files")
    print(f"Issues found: {len(issues)}")
    
    if issues:
        print("\n=== PROBLEMATIC FILES ===")
        for file_path, error in issues[:10]:  # Show first 10
            print(f"{file_path}: {error}")

if __name__ == '__main__':
    main()