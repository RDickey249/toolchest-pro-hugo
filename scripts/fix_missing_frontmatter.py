#!/usr/bin/env python3
"""
Fix Missing Frontmatter Script
Adds complete frontmatter to tools missing category metadata
"""

import os
import re
from pathlib import Path

def get_category_from_path(file_path):
    """Extract category and subcategory from file path"""
    path_parts = Path(file_path).parts
    if len(path_parts) >= 4:
        category_slug = path_parts[2]
        subcategory_slug = path_parts[3] if len(path_parts) > 4 else None
        
        # Convert slug to display name
        category_name = category_slug.replace('-', ' ').title()
        subcategory_name = subcategory_slug.replace('-', ' ').title() if subcategory_slug else ""
        
        # Special case mappings
        category_mapping = {
            'hr-recruiting-tools': 'HR & Recruiting Tools',
            'time-tracking-scheduling': 'Time Tracking & Scheduling',
            'e-commerce-business-tools': '🛍️ E-commerce & Business Tools',
            'ai-tools-assistants': '🤖 AI Tools & Assistants',
            'crm-sales-tools': '🎯 CRM & Sales Tools',
            'design-creative-tools': '🎨 Design & Creative Tools'
        }
        
        category_display = category_mapping.get(category_slug, category_name)
        
        return category_display, subcategory_name
    
    return None, None

def fix_frontmatter(file_path):
    """Add missing frontmatter to a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract existing title if present
    title_match = re.search(r'^title:\s*["\']?([^"\']+)["\']?', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    else:
        # Get title from filename
        filename = Path(file_path).stem
        title = filename.replace('-', ' ').title()
    
    # Get category info from path
    category, subcategory = get_category_from_path(file_path)
    if not category:
        print(f"⚠️  Could not determine category for {file_path}")
        return False
    
    # Extract external link if present
    external_link = ""
    external_match = re.search(r'^external_link:\s*["\']?([^"\']+)["\']?', content, re.MULTILINE)
    if external_match:
        external_link = external_match.group(1)
    
    # Create complete frontmatter
    frontmatter = f"""---
title: "{title}"
tagline: "Professional {category.lower().replace('🎯', '').replace('🤖', '').replace('🎨', '').replace('🛍️', '').strip()} solution"
category: "{category}"
categories: ["{category}"]
subcategory: "{subcategory}"
tool_name: "{title}"
deployment_status: "deployed"
image: "/images/tools/{Path(file_path).stem}-placeholder.jpg"
"""
    
    if external_link:
        frontmatter += f'external_link: "{external_link}"\n'
    
    frontmatter += f"""rating: 4.3
starting_price: 29
primary_use: "improve {category.lower().replace('🎯', '').replace('🤖', '').replace('🎨', '').replace('🛍️', '').strip()} processes"
top_alternatives: "Similar tools in this category"
---
"""
    
    # Remove existing incomplete frontmatter
    if content.startswith('---'):
        end = content.find('\n---\n', 3)
        if end != -1:
            content = content[end + 5:]
    
    # Combine new frontmatter with content
    new_content = frontmatter + content
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed: {title} in {category} > {subcategory}")
    return True

def main():
    """Find and fix files missing category frontmatter"""
    print("🔧 FIXING MISSING FRONTMATTER")
    print("=" * 50)
    
    fixed_count = 0
    
    # Find files missing category frontmatter
    for root, dirs, files in os.walk('content/categories'):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                file_path = os.path.join(root, file)
                
                # Check if file has category frontmatter
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'category:' not in content:
                    if fix_frontmatter(file_path):
                        fixed_count += 1
    
    print(f"\n📊 SUMMARY: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()