#!/usr/bin/env python3
"""
Search Index Generator for ToolChest Pro Hugo
Generates search-index.json from all tool markdown files
"""

import os
import json
import re
from pathlib import Path
import yaml

def extract_frontmatter_and_content(file_path):
    """Extract YAML frontmatter and content from a markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1]
                body_content = parts[2]
                
                # Parse YAML frontmatter
                try:
                    frontmatter = yaml.safe_load(frontmatter_str)
                except yaml.YAMLError:
                    frontmatter = {}
                
                return frontmatter, body_content
        
        return {}, content
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}, ""

def extract_tool_url(content):
    """Extract the primary tool URL from markdown content"""
    # Look for "Visit [toolname](url)" pattern
    visit_pattern = r'Visit \[([^\]]+)\]\(([^)]+)\)'
    match = re.search(visit_pattern, content)
    if match:
        return match.group(2)
    
    # Look for any markdown link as fallback
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    match = re.search(link_pattern, content)
    if match:
        return match.group(2)
    
    return None

def extract_tags_from_content(content):
    """Extract tags from content if not in frontmatter"""
    # Look for tag-like words or categories
    tags = []
    
    # Common patterns that might indicate tags
    tag_patterns = [
        r'#(\w+)',  # hashtags
        r'Tags?:\s*([^\n]+)',  # explicit tags
        r'Keywords?:\s*([^\n]+)',  # keywords
    ]
    
    for pattern in tag_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, str):
                # Split comma-separated tags
                tag_list = [tag.strip() for tag in match.split(',')]
                tags.extend(tag_list)
    
    return tags[:5]  # Limit to 5 tags

def generate_search_index():
    """Generate search index from all tool markdown files"""
    
    content_dir = Path("content")
    if not content_dir.exists():
        print("❌ Content directory not found")
        return
    
    search_data = []
    processed_count = 0
    
    print("🔍 Generating search index...")
    
    # Walk through all markdown files in content directory
    for md_file in content_dir.rglob("*.md"):
        if md_file.name in ['_index.md', 'index.md']:
            continue  # Skip index files
            
        frontmatter, content = extract_frontmatter_and_content(md_file)
        
        # Extract required data
        title = frontmatter.get('title', md_file.stem.replace('-', ' ').title())
        tagline = frontmatter.get('tagline', '')
        category = frontmatter.get('category', '')
        subcategory = frontmatter.get('subcategory', '')
        tool_name = frontmatter.get('tool_name', title)
        
        # Extract URL from content
        tool_url = extract_tool_url(content)
        
        # Generate Hugo URL path
        relative_path = md_file.relative_to(content_dir)
        hugo_url = "/" + str(relative_path).replace('.md', '/').replace('\\', '/')
        
        # Extract tags
        tags = frontmatter.get('tags', [])
        if not tags:
            tags = extract_tags_from_content(content)
        
        # Create search entry
        search_entry = {
            "title": title,
            "tagline": tagline,
            "category": category,
            "subcategory": subcategory,
            "tool_name": tool_name,
            "url": hugo_url,
            "external_url": tool_url,
            "tags": tags if isinstance(tags, list) else []
        }
        
        search_data.append(search_entry)
        processed_count += 1
        
        if processed_count % 100 == 0:
            print(f"   Processed {processed_count} tools...")
    
    # Sort by title for consistent ordering
    search_data.sort(key=lambda x: x['title'].lower())
    
    # Write search index
    output_path = Path("static/search-index.json")
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Search index generated: {processed_count} tools")
    print(f"📄 Output: {output_path}")
    
    # Generate some statistics
    categories = {}
    for tool in search_data:
        cat = tool['category']
        if cat:
            categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📊 Statistics:")
    print(f"   Total tools: {len(search_data)}")
    print(f"   Categories: {len(categories)}")
    print(f"   Tools with tags: {sum(1 for tool in search_data if tool['tags'])}")
    print(f"   Tools with external URLs: {sum(1 for tool in search_data if tool['external_url'])}")
    
    return len(search_data)

if __name__ == "__main__":
    print("🚀 TOOLCHEST PRO HUGO - SEARCH INDEX GENERATOR")
    print("=" * 60)
    
    tool_count = generate_search_index()
    
    print(f"\n🎯 SUMMARY")
    print("-" * 30)
    print(f"✅ Search index created with {tool_count} tools")
    print(f"📁 File: static/search-index.json")
    print(f"🔍 Ready for client-side search!")