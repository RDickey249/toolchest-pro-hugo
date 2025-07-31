#!/usr/bin/env python3
"""
Add "Get Started" sections to the 175 pages that are missing them.
"""

import glob
import os
import re

def extract_tool_name_from_frontmatter(content):
    """Extract tool name from frontmatter."""
    match = re.search(r'title: "([^"]+)"', content)
    if match:
        return match.group(1)
    return None

def extract_primary_url(tool_name):
    """Generate a likely URL for the tool."""
    # Clean the tool name for URL generation
    clean_name = tool_name.lower().replace(' ', '').replace('.', '').replace('-', '')
    
    # Common URL patterns
    url_patterns = [
        f"https://{clean_name}.com",
        f"https://www.{clean_name}.com",
        f"https://{clean_name}.io",
        f"https://{clean_name}.app"
    ]
    
    # Return the most likely URL (usually .com)
    return url_patterns[0]

def add_get_started_section(content, tool_name):
    """Add a Get Started section to content that's missing it."""
    
    # Generate URL
    primary_url = extract_primary_url(tool_name)
    
    # Create the Get Started section
    get_started_section = f'''
## Get Started with {tool_name}

Ready to get started? Visit [{tool_name}]({primary_url}) to explore the platform and begin using this tool.'''
    
    # Find the best place to insert it (before any "How It Compares" section or at the end)
    if "## How It Compares" in content:
        # Insert before "How It Compares"
        new_content = content.replace("## How It Compares", get_started_section + "\n\n## How It Compares")
    else:
        # Add at the end
        new_content = content.rstrip() + get_started_section + "\n"
    
    return new_content

def fix_file(file_path):
    """Add Get Started section to a file that's missing it."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has Get Started section
        if 'Get Started with' in content or 'Get started' in content:
            return False
        
        # Extract tool name
        tool_name = extract_tool_name_from_frontmatter(content)
        if not tool_name:
            # Fallback to filename
            filename = os.path.basename(file_path)
            tool_name = filename.replace('.md', '').replace('-', ' ').title()
        
        # Add Get Started section
        new_content = add_get_started_section(content, tool_name)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all files missing Get Started sections."""
    
    # Find all tool files
    md_files = glob.glob('content/categories/**/*.md', recursive=True)
    tool_files = [f for f in md_files if not f.endswith('_index.md')]
    
    # Find files missing Get Started sections
    missing_get_started = []
    for file_path in tool_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'Get Started with' not in content and 'Get started' not in content:
                missing_get_started.append(file_path)
        except:
            continue
    
    print(f"Found {len(missing_get_started)} files missing Get Started sections")
    print("=" * 60)
    
    fixed_count = 0
    for file_path in missing_get_started:
        if fix_file(file_path):
            fixed_count += 1
            print(f"✓ Added Get Started section: {file_path}")
        else:
            print(f"✗ Failed: {file_path}")
    
    print("=" * 60)
    print(f"Successfully added Get Started sections to {fixed_count} files")

if __name__ == "__main__":
    main()