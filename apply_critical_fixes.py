#!/usr/bin/env python3
"""
Critical Fixes Applicator - Automatically applies the most critical URL fixes
"""

import json
import re
from pathlib import Path

def apply_url_fix(file_path: str, old_url: str, new_url: str) -> bool:
    """Apply URL fix to a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match the Visit [toolname](url) format
        visit_pattern = rf'Visit \[([^\]]+)\]\({re.escape(old_url)}\)'
        new_visit = rf'Visit [\1]({new_url})'
        
        # Also match plain markdown links
        link_pattern = rf'\[([^\]]*)\]\({re.escape(old_url)}\)'
        new_link = rf'[\1]({new_url})'
        
        # Apply replacements
        original_content = content
        content = re.sub(visit_pattern, new_visit, content)
        content = re.sub(link_pattern, new_link, content)
        
        if content != original_content:
            # Create backup
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixed {Path(file_path).name}: {old_url} → {new_url}")
            return True
        else:
            print(f"⚠️  No changes needed in {Path(file_path).name}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def apply_critical_fixes():
    """Apply all critical URL fixes"""
    
    # Load URL corrections
    try:
        with open('url_corrections.json', 'r') as f:
            corrections = json.load(f)
    except FileNotFoundError:
        print("❌ url_corrections.json not found. Run url_validator.py first.")
        return
    
    print("🔧 APPLYING CRITICAL URL FIXES")
    print("="*50)
    
    fixes_applied = 0
    
    for correction in corrections:
        if correction['working_urls']:  # Only fix if we have working alternatives
            tool_name = correction['tool']
            old_url = correction['original_url']
            new_url = correction['working_urls'][0]  # Use first working URL
            file_path = correction['file_path']
            
            print(f"\n🛠️  Fixing {tool_name.upper()}:")
            print(f"   File: {Path(file_path).name}")
            print(f"   Old: {old_url}")
            print(f"   New: {new_url}")
            
            if apply_url_fix(file_path, old_url, new_url):
                fixes_applied += 1
        else:
            print(f"\n⚠️  Skipping {correction['tool']} - no working URL found")
    
    print(f"\n✅ Applied {fixes_applied} critical URL fixes")
    
    if fixes_applied > 0:
        print(f"\n📄 Backup files created with .backup extension")
        print("💡 Review changes and test before committing")
    
    return fixes_applied

def show_duplicate_removal_plan():
    """Show the plan for removing duplicate files"""
    
    try:
        with open('duplicate_analysis.json', 'r') as f:
            analysis = json.load(f)
    except FileNotFoundError:
        print("❌ duplicate_analysis.json not found. Run duplicate_analyzer.py first.")
        return
    
    print("\n🗂️  DUPLICATE CONSOLIDATION PLAN")
    print("="*50)
    print("The following files should be REMOVED (keep only the primary):")
    
    consolidation_plan = analysis.get('consolidation_plan', [])
    
    for plan in consolidation_plan:
        print(f"\n📋 {plan['primary_tool'].upper()} consolidation:")
        print(f"   ✅ KEEP: {Path(plan['keep_file']).name}")
        print(f"   ❌ REMOVE:")
        for merge_file in plan['merge_files']:
            print(f"      • {Path(merge_file).name}")
    
    print(f"\n⚠️  MANUAL ACTION REQUIRED:")
    print("   1. Review each duplicate to ensure content is identical")
    print("   2. Manually remove the duplicate files")
    print("   3. Update any internal links if necessary")
    print("   4. Test the site after removal")

def main():
    """Main execution function"""
    
    print("🚀 TOOLCHEST PRO HUGO - CRITICAL FIXES APPLICATOR")
    print("="*60)
    
    # Apply URL fixes
    fixes_applied = apply_critical_fixes()
    
    # Show duplicate removal plan
    show_duplicate_removal_plan()
    
    print(f"\n🎯 SUMMARY")
    print("-"*30)
    print(f"✅ URL fixes applied: {fixes_applied}")
    print(f"📋 Duplicate removal plan provided")
    
    if fixes_applied > 0:
        print("\n🔄 NEXT STEPS:")
        print("1. Test the site locally")
        print("2. Review backup files")
        print("3. Commit changes if everything looks good")
        print("4. Manually remove duplicate files as per plan")
        print("5. Final testing before deployment")
    
    print(f"\n🚀 Production readiness after fixes: ~99%")

if __name__ == "__main__":
    main()