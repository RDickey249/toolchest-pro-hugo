#!/usr/bin/env python3
"""Add affiliate fields to tool files based on affiliate-links.yaml data."""

import os
import yaml
from pathlib import Path
import re

def load_affiliate_data():
    """Load affiliate links data."""
    with open('data/affiliate-links.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = re.sub(r'[^\w\s&-]', '', text)
    text = re.sub(r'[\s&]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-').lower()
    return text

def update_tool_file(file_path, affiliate_data):
    """Update a tool file with affiliate information."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.startswith('---'):
        return False
    
    # Split frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    
    frontmatter = parts[1]
    body = parts[2]
    
    # Extract tool title
    title_match = re.search(r'^title:\s*["\']([^"\']+)["\']', frontmatter, re.MULTILINE)
    if not title_match:
        return False
    
    tool_title = title_match.group(1)
    tool_slug = slugify(tool_title)
    
    # Check if this tool has affiliate data
    if tool_slug not in affiliate_data:
        return False
    
    affiliate_info = affiliate_data[tool_slug]
    
    # Add affiliate fields if not present
    changes_made = False
    
    # Add affiliate: true if not present
    if 'affiliate:' not in frontmatter:
        frontmatter += '\naffiliate: true'
        changes_made = True
    
    # Add affiliate_url if not present
    if 'affiliate_url:' not in frontmatter:
        frontmatter += f'\naffiliate_url: "{affiliate_info["url"]}"'
        changes_made = True
    
    # Add affiliate_cta if not present
    if 'affiliate_cta:' not in frontmatter:
        frontmatter += f'\naffiliate_cta: "{affiliate_info["cta"]}"'
        changes_made = True
    
    # Add commission info if not present
    if 'commission:' not in frontmatter:
        frontmatter += f'\ncommission: "{affiliate_info["commission"]}"'
        changes_made = True
    
    # Add tier info if not present
    if 'affiliate_tier:' not in frontmatter:
        frontmatter += f'\naffiliate_tier: "{affiliate_info["tier"]}"'
        changes_made = True
    
    if changes_made:
        # Write back the file
        new_content = f"---{frontmatter}---{body}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def add_affiliate_disclosure_to_content(file_path):
    """Add affiliate disclosure to tool content if needed."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '## Affiliate Disclosure' in content:
        return False  # Already has disclosure
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    
    frontmatter = parts[1]
    body = parts[2]
    
    # Check if this is an affiliate tool
    if 'affiliate: true' not in frontmatter:
        return False
    
    # Add disclosure before the final "Get Started" section
    if '## Get Started with' in body:
        disclosure = """
## Affiliate Disclosure

**Transparency Notice:** This page contains affiliate links. When you click through and make a purchase, ToolChest may earn a commission at no additional cost to you. This helps us maintain our free resource while ensuring we only recommend tools we genuinely believe will benefit your business.

"""
        body = body.replace('## Get Started with', disclosure + '## Get Started with')
        
        new_content = f"---{frontmatter}---{body}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def main():
    """Main function to update all tool files."""
    # Load affiliate data
    affiliate_data = load_affiliate_data()
    print(f"Loaded {len(affiliate_data)} affiliate tools")
    
    # Find all tool files
    content_dir = Path('content/categories')
    tool_files = []
    
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md') and file != '_index.md':
                tool_files.append(Path(root) / file)
    
    print(f"Found {len(tool_files)} tool files")
    
    # Update files
    updated_count = 0
    disclosure_count = 0
    
    for file_path in tool_files:
        try:
            # Update affiliate fields
            if update_tool_file(file_path, affiliate_data):
                updated_count += 1
                print(f"✅ Updated affiliate fields: {file_path.name}")
            
            # Add disclosure
            if add_affiliate_disclosure_to_content(file_path):
                disclosure_count += 1
                print(f"📝 Added disclosure: {file_path.name}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
    
    print(f"\n=== AFFILIATE FIELDS UPDATE COMPLETE ===")
    print(f"Updated affiliate fields: {updated_count} files")
    print(f"Added disclosures: {disclosure_count} files")

if __name__ == '__main__':
    main()