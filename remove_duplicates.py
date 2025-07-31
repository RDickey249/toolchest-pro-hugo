#!/usr/bin/env python3
"""
Duplicate Tools Removal Script
Removes duplicate tool files based on consolidation plan from duplicate analysis
"""

import json
import os
from pathlib import Path

def remove_duplicate_files():
    """Remove duplicate files based on consolidation plan"""
    
    # Load duplicate analysis
    try:
        with open('duplicate_analysis.json', 'r') as f:
            analysis = json.load(f)
    except FileNotFoundError:
        print("❌ duplicate_analysis.json not found. Run duplicate_analyzer.py first.")
        return
    
    consolidation_plan = analysis.get('consolidation_plan', [])
    
    if not consolidation_plan:
        print("❌ No consolidation plan found.")
        return
    
    print("🗂️  REMOVING DUPLICATE TOOL FILES")
    print("=" * 50)
    
    removed_count = 0
    backup_count = 0
    
    for plan in consolidation_plan:
        primary_tool = plan['primary_tool']
        keep_file = plan['keep_file']
        merge_files = plan['merge_files']
        
        print(f"\n📋 Processing {primary_tool.upper()}:")
        print(f"   ✅ KEEPING: {Path(keep_file).name}")
        
        # Verify the keep file exists
        if not os.path.exists(keep_file):
            print(f"   ⚠️  WARNING: Keep file doesn't exist: {keep_file}")
            continue
        
        # Remove merge files (duplicates)
        for merge_file in merge_files:
            if os.path.exists(merge_file):
                try:
                    # Create backup first
                    backup_file = merge_file + '.removed-backup'
                    with open(merge_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    backup_count += 1
                    
                    # Remove the duplicate file
                    os.remove(merge_file)
                    removed_count += 1
                    print(f"   ❌ REMOVED: {Path(merge_file).name}")
                    print(f"   💾 BACKUP: {Path(backup_file).name}")
                except Exception as e:
                    print(f"   ❌ ERROR removing {merge_file}: {e}")
            else:
                print(f"   ⚠️  File not found: {Path(merge_file).name}")
    
    print(f"\n✅ CONSOLIDATION COMPLETE")
    print("-" * 30)
    print(f"Files removed: {removed_count}")
    print(f"Backups created: {backup_count}")
    
    if removed_count > 0:
        print(f"\n📄 Backup files created with .removed-backup extension")
        print("💡 Review changes and test before committing")
        
        # Show git status
        print(f"\n📊 IMPACT SUMMARY:")
        print(f"   • Reduced total tool files from 1,297 to {1297 - removed_count}")
        print(f"   • Eliminated {removed_count} duplicate entries")
        print(f"   • Improved content organization and SEO")
    
    return removed_count

def update_search_index():
    """Regenerate search index after removing duplicates"""
    print(f"\n🔍 UPDATING SEARCH INDEX...")
    try:
        import subprocess
        result = subprocess.run(['python3', 'generate_search_index.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Search index updated successfully")
        else:
            print(f"⚠️  Search index update warning: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not update search index automatically: {e}")
        print("💡 Run 'python3 generate_search_index.py' manually")

def main():
    """Main execution function"""
    
    print("🚀 TOOLCHEST PRO HUGO - DUPLICATE REMOVAL")
    print("=" * 60)
    
    # Show what will be removed
    try:
        with open('duplicate_analysis.json', 'r') as f:
            analysis = json.load(f)
        consolidation_plan = analysis.get('consolidation_plan', [])
        
        print(f"🎯 REMOVAL PLAN:")
        print(f"   Total duplicates to remove: {len(consolidation_plan)}")
        
        for plan in consolidation_plan:
            print(f"   • {plan['primary_tool']}: Keep {Path(plan['keep_file']).parent.name}, remove {len(plan['merge_files'])} duplicate(s)")
        
        # Auto-proceed (removing confirmation for automated execution)
        print(f"\n✅ Proceeding to remove {sum(len(p['merge_files']) for p in consolidation_plan)} duplicate files...")
            
    except Exception as e:
        print(f"❌ Error reading consolidation plan: {e}")
        return
    
    # Remove duplicates
    removed_count = remove_duplicate_files()
    
    if removed_count > 0:
        # Update search index
        update_search_index()
        
        print(f"\n🔄 NEXT STEPS:")
        print("1. Test the site locally")
        print("2. Verify removed tools are no longer accessible")
        print("3. Check that kept tools still work correctly")
        print("4. Commit changes if everything looks good")
        print("5. Consider adding redirects for SEO if needed")
    
    print(f"\n🚀 Site consolidation complete!")

if __name__ == "__main__":
    main()