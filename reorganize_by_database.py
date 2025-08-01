#!/usr/bin/env python3
"""Reorganize Hugo directory structure to match database exactly."""

import os
import csv
import shutil
from pathlib import Path
import re

def slugify(text):
    """Convert text to URL-friendly slug."""
    # Remove emojis and special characters
    text = re.sub(r'[^\w\s&-]', '', text)
    # Replace spaces and & with hyphens
    text = re.sub(r'[\s&]+', '-', text)
    # Convert to lowercase and remove multiple hyphens
    text = re.sub(r'-+', '-', text).strip('-').lower()
    return text

def parse_tool_name(full_name):
    """Extract just the tool name from 'Tool Name - Description' format."""
    # Split on ' - ' and take the first part
    if ' - ' in full_name:
        return full_name.split(' - ')[0].strip()
    return full_name.strip()

def find_existing_tool_file(tool_name, content_dir):
    """Find existing tool file anywhere in the content directory."""
    tool_slug = slugify(tool_name)
    
    # Common variations to check
    variations = [
        f"{tool_slug}.md",
        f"{tool_name.lower().replace(' ', '-')}.md",
        f"{tool_name.lower().replace(' ', '_')}.md",
        f"{tool_name.replace(' ', '').lower()}.md"
    ]
    
    # Search all .md files
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                file_path = Path(root) / file
                
                # Check if this matches any variation
                if file in variations:
                    return str(file_path)
                
                # Also check if the title in frontmatter matches
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.startswith('---'):
                            frontmatter = content.split('---')[1]
                            if f'title: "{tool_name}"' in frontmatter or f"title: '{tool_name}'" in frontmatter:
                                return str(file_path)
                except:
                    continue
    
    return None

def reorganize_by_database():
    """Reorganize files based on database structure."""
    
    # Read the database
    database_path = Path('data_backup/tool-database.csv')
    content_dir = Path('content/categories')
    
    if not database_path.exists():
        print(f"Error: Database file not found at {database_path}")
        return
    
    # Parse database
    tools_to_move = []
    current_category = None
    current_subcategory = None
    
    with open(database_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
                
            tool_name, category, subcategory = [cell.strip() for cell in row[:3]]
            
            # Skip header-like rows
            if not tool_name or tool_name in ['CATEGORY', '']:
                continue
            
            # Check if this is a category header
            if category == 'CATEGORY' and subcategory == 'SUBCATEGORY':
                current_category = tool_name
                continue
            
            # Check if this is a subcategory header
            if not category and not subcategory and tool_name:
                current_subcategory = tool_name
                continue
            
            # This is a tool entry
            if category and subcategory:
                # Remove emojis from category
                clean_category = re.sub(r'[^\w\s&-]', '', category).strip()
                clean_subcategory = subcategory.strip()
                
                # Parse tool name (remove description)
                clean_tool_name = parse_tool_name(tool_name)
                
                tools_to_move.append({
                    'tool_name': clean_tool_name,
                    'category': clean_category,
                    'subcategory': clean_subcategory,
                    'category_slug': slugify(clean_category),
                    'subcategory_slug': slugify(clean_subcategory),
                    'tool_slug': slugify(clean_tool_name)
                })
    
    print(f"Found {len(tools_to_move)} tools in database")
    
    # Create directory structure and move files
    moved_count = 0
    not_found_count = 0
    
    for tool_info in tools_to_move:
        # Find existing file
        existing_file = find_existing_tool_file(tool_info['tool_name'], content_dir)
        
        if not existing_file:
            print(f"⚠️  Tool not found: {tool_info['tool_name']}")
            not_found_count += 1
            continue
        
        # Determine target location
        target_dir = content_dir / tool_info['category_slug'] / tool_info['subcategory_slug']
        target_file = target_dir / f"{tool_info['tool_slug']}.md"
        
        # Skip if already in correct location
        if Path(existing_file) == target_file:
            continue
        
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Move file
        try:
            shutil.move(existing_file, target_file)
            print(f"✅ Moved: {tool_info['tool_name']} -> {target_file.relative_to(content_dir)}")
            moved_count += 1
            
            # Update frontmatter
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                frontmatter = parts[1]
                body = parts[2]
                
                # Update category and subcategory
                frontmatter = re.sub(
                    r'^category:\s*"[^"]*"$',
                    f'category: "{tool_info["category"]}"',
                    frontmatter,
                    flags=re.MULTILINE
                )
                frontmatter = re.sub(
                    r'^subcategory:\s*"[^"]*"$',
                    f'subcategory: "{tool_info["subcategory"]}"',
                    frontmatter,
                    flags=re.MULTILINE
                )
                frontmatter = re.sub(
                    r'^categories:\s*\[[^\]]*\]$',
                    f'categories: ["{tool_info["category"]}"]',
                    frontmatter,
                    flags=re.MULTILINE
                )
                
                # Write back
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(f"---{frontmatter}---{body}")
            
        except Exception as e:
            print(f"❌ Error moving {tool_info['tool_name']}: {e}")
    
    print(f"\n=== REORGANIZATION COMPLETE ===")
    print(f"Moved: {moved_count} files")
    print(f"Not found: {not_found_count} files")
    
    # Clean up empty directories
    print("\nCleaning up empty directories...")
    for root, dirs, files in os.walk(content_dir, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    print(f"Removed empty directory: {dir_path.relative_to(content_dir)}")
            except:
                pass

if __name__ == '__main__':
    reorganize_by_database()