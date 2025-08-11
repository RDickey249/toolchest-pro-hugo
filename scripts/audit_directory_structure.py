#!/usr/bin/env python3
"""
Directory Structure Audit Script
Verifies that all tool pages have correct category/subcategory breadcrumb paths
and identifies any 404 potential issues
"""

import os
import yaml
from pathlib import Path
import re

def load_weighted_categories():
    """Load the weighted categories mapping"""
    with open('data/weighted_categories.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_tool_files():
    """Get all tool markdown files"""
    tool_files = []
    for root, dirs, files in os.walk('content/categories'):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                tool_files.append(os.path.join(root, file))
    return tool_files

def parse_frontmatter(file_path):
    """Extract frontmatter from markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    if content.startswith('---'):
        try:
            end = content.find('\n---\n', 3)
            if end != -1:
                frontmatter_str = content[3:end]
                return yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return {}
    return {}

def slugify(text):
    """Convert text to URL slug format"""
    # Remove emojis and special characters
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def check_directory_structure():
    """Main audit function"""
    print("🔍 DIRECTORY STRUCTURE AUDIT - BREADCRUMB VERIFICATION")
    print("=" * 70)
    
    # Load category mappings
    weighted_cats = load_weighted_categories()
    category_slug_map = {}
    
    for cat in weighted_cats['categories']:
        category_slug_map[cat['name']] = cat['slug']
    
    print(f"📊 Found {len(category_slug_map)} weighted categories")
    
    # Get all tool files
    tool_files = get_tool_files()
    print(f"📁 Found {len(tool_files)} tool files")
    
    print("\n🚨 POTENTIAL ISSUES FOUND:")
    print("-" * 50)
    
    issues = []
    correct_files = 0
    
    for file_path in tool_files:
        # Parse file path components
        path_parts = Path(file_path).parts
        if len(path_parts) >= 4:  # content/categories/category/subcategory/tool.md
            file_category_slug = path_parts[2]
            file_subcategory_slug = path_parts[3] if len(path_parts) > 4 else None
            tool_filename = path_parts[-1]
            
            # Parse frontmatter
            frontmatter = parse_frontmatter(file_path)
            fm_category = frontmatter.get('category', '')
            fm_subcategory = frontmatter.get('subcategory', '')
            tool_title = frontmatter.get('title', tool_filename)
            
            # Check category consistency
            expected_category_slug = category_slug_map.get(fm_category)
            if not expected_category_slug:
                # Try to find closest match
                fm_category_slug = slugify(fm_category)
                expected_category_slug = fm_category_slug
            
            # Identify issues
            category_mismatch = file_category_slug != expected_category_slug
            
            if category_mismatch:
                issues.append({
                    'file': file_path,
                    'title': tool_title,
                    'issue': 'Category path mismatch',
                    'file_path': f"{file_category_slug}/{file_subcategory_slug if file_subcategory_slug else ''}",
                    'frontmatter': f"{fm_category} > {fm_subcategory}",
                    'expected_path': f"{expected_category_slug}/{slugify(fm_subcategory) if fm_subcategory else ''}",
                    'severity': 'HIGH' if expected_category_slug else 'MEDIUM'
                })
            else:
                correct_files += 1
    
    # Report results
    print(f"\n✅ CORRECT FILES: {correct_files}")
    print(f"❌ ISSUES FOUND: {len(issues)}")
    
    if issues:
        print(f"\n🔧 DETAILED ISSUE REPORT:")
        print("-" * 70)
        
        high_priority = [i for i in issues if i.get('severity') == 'HIGH']
        medium_priority = [i for i in issues if i.get('severity') == 'MEDIUM']
        
        print(f"\n🚨 HIGH PRIORITY (Category not in weighted_categories.yaml): {len(high_priority)}")
        for issue in high_priority[:10]:  # Show first 10
            print(f"   📄 {issue['title']}")
            print(f"      File: {issue['file']}")
            print(f"      Category mismatch: '{issue['frontmatter']}' vs path '{issue['file_path']}'")
            print()
        
        print(f"\n⚠️  MEDIUM PRIORITY (Path doesn't match slug): {len(medium_priority)}")
        for issue in medium_priority[:10]:  # Show first 10
            print(f"   📄 {issue['title']}")
            print(f"      File: {issue['file']}")
            print(f"      Should be: {issue['expected_path']}")
            print(f"      Currently: {issue['file_path']}")
            print()
        
        if len(issues) > 20:
            print(f"   ... and {len(issues) - 20} more issues")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Tools: {len(tool_files)}")
    print(f"   Correct Structure: {correct_files}")
    print(f"   Need Fixing: {len(issues)}")
    print(f"   Success Rate: {(correct_files / len(tool_files) * 100):.1f}%")
    
    return issues

def suggest_fixes(issues):
    """Suggest specific fixes for the issues found"""
    print(f"\n🔧 SUGGESTED FIXES:")
    print("=" * 50)
    
    category_issues = {}
    for issue in issues:
        category = issue['frontmatter'].split(' > ')[0]
        if category not in category_issues:
            category_issues[category] = []
        category_issues[category].append(issue)
    
    for category, cat_issues in category_issues.items():
        print(f"\n📂 {category} ({len(cat_issues)} files)")
        print(f"   Suggested fixes:")
        
        # Group by expected path
        path_groups = {}
        for issue in cat_issues:
            expected = issue['expected_path']
            if expected not in path_groups:
                path_groups[expected] = []
            path_groups[expected].append(issue)
        
        for expected_path, path_issues in list(path_groups.items())[:3]:  # Show top 3
            print(f"   📁 Move to: content/categories/{expected_path}/")
            print(f"      Files affected: {len(path_issues)}")

if __name__ == "__main__":
    issues = check_directory_structure()
    if issues:
        suggest_fixes(issues)
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Review high-priority category mismatches")
    print("2. Update weighted_categories.yaml if needed")
    print("3. Move files to correct directory structure") 
    print("4. Test site build and navigation")