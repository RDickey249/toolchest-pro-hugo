#!/usr/bin/env python3
"""
Categories Page Validation Script
PREVENTS THE BLANK CATEGORY PAGE CATASTROPHE
"""

import os
import re
from pathlib import Path

def validate_categories_page():
    """Ensure categories page will display properly"""
    
    print("🔍 VALIDATING CATEGORIES PAGE...")
    
    # Check if weighted_categories.yaml exists
    data_file = Path("data/weighted_categories.yaml")
    if not data_file.exists():
        print("❌ CRITICAL: weighted_categories.yaml is missing!")
        return False
    
    # Check categories template
    template_file = Path("layouts/categories/list.html")
    if not template_file.exists():
        print("❌ CRITICAL: categories list template is missing!")
        return False
    
    # Read template content
    with open(template_file, 'r') as f:
        template_content = f.read()
    
    # Check for the critical patterns
    checks = [
        ("site.Data.weighted_categories.categories", "Weighted categories data access"),
        (".slug", "Category slug field access"),
        (".name", "Category name field access"),
        (".description", "Category description field access"),
        (".total_tools", "Tool count field access"),
        ("category-card", "CSS class for category cards"),
    ]
    
    print("\n📋 Template Content Validation:")
    all_passed = True
    
    for pattern, description in checks:
        if pattern in template_content:
            print(f"✅ {description}")
        else:
            print(f"❌ MISSING: {description}")
            all_passed = False
    
    # Check for the dangerous Hugo queries that caused the blank page
    dangerous_patterns = [
        'where site.Pages "Type" "categories"',
        'site.Taxonomies.categories',
        'where (where site.Pages',
    ]
    
    print("\n🚨 Checking for Dangerous Patterns:")
    for pattern in dangerous_patterns:
        if pattern in template_content:
            print(f"⚠️  WARNING: Found dangerous pattern: {pattern}")
            print("   This could cause blank page!")
            all_passed = False
        else:
            print(f"✅ Safe from: {pattern}")
    
    # Build test
    print("\n🏗️  Testing Hugo Build...")
    build_result = os.system("./hugo --quiet --destination public_test > /dev/null 2>&1")
    
    if build_result == 0:
        print("✅ Hugo build successful")
        
        # Check generated categories page
        categories_page = Path("public_test/categories/index.html")
        if categories_page.exists():
            with open(categories_page, 'r') as f:
                content = f.read()
            
            # Check for content (HTML encoded)
            if 'CRM &amp; Sales Tools' in content and 'Marketing &amp; Social Media' in content:
                print("✅ Categories page contains expected content")
            elif 'CRM & Sales Tools' in content and 'Marketing & Social Media' in content:
                print("✅ Categories page contains expected content")
            else:
                print("❌ Categories page is missing expected content!")
                print(f"   Content preview: {content[:200]}...")
                all_passed = False
        else:
            print("❌ Categories page was not generated!")
            all_passed = False
    else:
        print("❌ Hugo build failed!")
        all_passed = False
    
    # Cleanup
    if Path("public_test").exists():
        os.system("rm -rf public_test")
    
    if all_passed:
        print("\n🎉 CATEGORIES PAGE VALIDATION PASSED!")
        print("   The weighted category system is working correctly.")
    else:
        print("\n💥 CATEGORIES PAGE VALIDATION FAILED!")
        print("   Risk of blank category page!")
    
    return all_passed

if __name__ == "__main__":
    validate_categories_page()