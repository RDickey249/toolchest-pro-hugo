#!/usr/bin/env python3
"""
Fix Duplicate Headers Script
Removes duplicate H1 headers from tool markdown files where the title already appears in frontmatter
"""

import os
import re
from pathlib import Path

def fix_duplicate_header(file_path):
    """Remove duplicate H1 header that matches the frontmatter title"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        if not content.startswith('---\n'):
            return False
            
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return False
            
        frontmatter = parts[1]
        body_content = parts[2]
        
        # Extract title from frontmatter
        title_match = re.search(r'^title:\s*["\']?([^"\'\n]+)["\']?', frontmatter, re.MULTILINE)
        if not title_match:
            return False
            
        title = title_match.group(1).strip()
        
        # Check if content starts with duplicate H1 header
        # Look for # Title at the beginning of content (after any whitespace)
        h1_pattern = rf'^\s*#\s+{re.escape(title)}\s*\n'
        
        if re.match(h1_pattern, body_content):
            # Remove the duplicate header
            new_body_content = re.sub(h1_pattern, '', body_content, count=1)
            
            # Reconstruct the file
            new_content = f"---\n{frontmatter}---\n{new_body_content}"
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def fix_all_duplicate_headers():
    """Fix duplicate headers in all tool markdown files"""
    
    print("🔧 FIXING DUPLICATE HEADERS")
    print("=" * 50)
    
    content_dir = Path("content/categories")
    if not content_dir.exists():
        print("❌ Content directory not found")
        return
    
    fixed_count = 0
    total_files = 0
    
    # Find all markdown files except _index.md
    for md_file in content_dir.rglob("*.md"):
        if md_file.name == "_index.md":
            continue
            
        total_files += 1
        
        if fix_duplicate_header(md_file):
            fixed_count += 1
            print(f"✅ Fixed: {md_file.name}")
        
        # Progress indicator
        if total_files % 100 == 0:
            print(f"   Processed {total_files} files...")
    
    print(f"\n🎯 SUMMARY")
    print("-" * 30)
    print(f"Total files processed: {total_files}")
    print(f"Duplicate headers removed: {fixed_count}")
    
    if fixed_count > 0:
        print(f"\n✅ DUPLICATE HEADERS FIXED")
        print(f"Tool pages now have single headers instead of duplicates")
        print(f"Layout displays title from frontmatter, content no longer has redundant H1")
    else:
        print(f"\n✅ NO DUPLICATE HEADERS FOUND")
        print(f"All tool pages already have proper single headers")
    
    return fixed_count

def main():
    """Main execution function"""
    
    print("🚀 TOOLCHEST PRO HUGO - DUPLICATE HEADER FIX")
    print("=" * 60)
    
    fixed_count = fix_all_duplicate_headers()
    
    if fixed_count > 0:
        print(f"\n🔄 NEXT STEPS:")
        print("1. Test individual tool pages to confirm single headers")
        print("2. Commit and push changes to production")
        print("3. Verify fix on live site")
        
        print(f"\n🚀 Tool pages now have clean, single headers!")
    
    return fixed_count

if __name__ == "__main__":
    main()