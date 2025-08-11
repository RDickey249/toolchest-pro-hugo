#!/usr/bin/env python3
"""
MANDATORY FUNCTION TEST - PREVENTS ROGUE AGENT FAILURES
=======================================================

This script MUST be run before any subagent claims the site is "working great"
or completes an audit. It tests the actual core functionality that users depend on.

HISTORICAL CONTEXT: Last week Claude Code went "rogue" and claimed everything was
working while the main category page was completely blank. This prevented that.
"""

import subprocess
import requests
import sys
from pathlib import Path

def test_hugo_build():
    """Test that Hugo builds successfully"""
    print("🏗️  Testing Hugo Build Process...")
    
    try:
        result = subprocess.run(["./hugo", "--quiet", "--destination", "public_test"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Hugo build successful")
            return True
        else:
            print(f"❌ Hugo build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Hugo build error: {e}")
        return False

def test_categories_page_locally():
    """Test the generated categories page has content"""
    print("📋 Testing Categories Page Content...")
    
    categories_file = Path("public_test/categories/index.html")
    
    if not categories_file.exists():
        print("❌ Categories page not generated!")
        return False
    
    with open(categories_file, 'r') as f:
        content = f.read()
    
    # Check for key content that should be there
    required_content = [
        "CRM & Sales Tools",  # First weighted category
        "Marketing & Social Media",  # Second weighted category  
        "Design & Creative Tools",  # Third weighted category
        "grid grid-3",  # Grid layout
        "category-card",  # Category cards
    ]
    
    missing_content = []
    for item in required_content:
        if item not in content and item.replace("&", "&amp;") not in content:
            missing_content.append(item)
    
    if missing_content:
        print(f"❌ Categories page missing content: {missing_content}")
        print(f"   First 300 chars: {content[:300]}...")
        return False
    
    print("✅ Categories page contains expected content")
    return True

def test_live_site():
    """Test the live site if accessible"""
    print("🌐 Testing Live Site (if accessible)...")
    
    try:
        response = requests.get("https://toolchest.pro/categories/", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for the same key content
            if "CRM & Sales Tools" in content or "CRM &amp; Sales Tools" in content:
                print("✅ Live categories page is working")
                return True
            else:
                print("❌ Live categories page appears blank or broken")
                print(f"   Status: {response.status_code}")
                print(f"   First 300 chars: {content[:300]}...")
                return False
        else:
            print(f"⚠️  Live site returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not test live site: {e}")
        return False

def test_affiliate_system():
    """Test affiliate system files exist and are valid"""
    print("💰 Testing Affiliate System...")
    
    required_files = [
        "data/affiliate_links.yaml",
        "data/affiliate_tools.yaml", 
        "data/weighted_categories.yaml",
        "static/js/affiliate-tracking.js",
        "static/css/affiliate.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing affiliate files: {missing_files}")
        return False
    
    print("✅ Affiliate system files present")
    return True

def test_template_integrity():
    """Test that critical templates exist and don't have dangerous patterns"""
    print("📄 Testing Template Integrity...")
    
    # Test categories template
    categories_template = Path("layouts/categories/list.html")
    if not categories_template.exists():
        print("❌ Categories template missing!")
        return False
    
    with open(categories_template, 'r') as f:
        template_content = f.read()
    
    # Check for dangerous patterns that caused blank page
    dangerous_patterns = [
        'where site.Pages "Type" "categories"',
        'site.Taxonomies.categories',
    ]
    
    for pattern in dangerous_patterns:
        if pattern in template_content:
            print(f"❌ DANGEROUS PATTERN FOUND: {pattern}")
            print("   This will cause blank category page!")
            return False
    
    # Check for correct pattern
    if "site.Data.weighted_categories.categories" not in template_content:
        print("❌ Categories template missing correct data access pattern")
        return False
    
    print("✅ Template integrity check passed")
    return True

def cleanup():
    """Clean up test files"""
    import shutil
    if Path("public_test").exists():
        shutil.rmtree("public_test")

def main():
    """Run all mandatory tests"""
    print("🚨 MANDATORY FUNCTION TEST - PREVENTING ROGUE AGENT FAILURES")
    print("=" * 70)
    print("This test MUST pass before claiming 'everything is working great'")
    print()
    
    tests = [
        ("Hugo Build", test_hugo_build),
        ("Categories Page Content", test_categories_page_locally),
        ("Affiliate System", test_affiliate_system),
        ("Template Integrity", test_template_integrity),
        ("Live Site", test_live_site),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
        if not result:
            all_passed = False
    
    # Cleanup
    cleanup()
    
    print("\n" + "="*70)
    print("FINAL RESULTS:")
    print("=" * 70)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print("=" * 70)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("   Site core functionality is working correctly.")
        print("   Safe to claim 'everything is working great'.")
        sys.exit(0)
    else:
        print("💥 TESTS FAILED!")
        print("   DO NOT claim site is working until these are fixed!")
        print("   Core functionality is broken!")
        sys.exit(1)

if __name__ == "__main__":
    main()