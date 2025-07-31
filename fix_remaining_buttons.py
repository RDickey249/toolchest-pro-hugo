#!/usr/bin/env python3
"""
Fix remaining HTML button sections that the first script missed.
"""

import os
import re
import glob

def convert_html_buttons_to_markdown_v2(content):
    """Convert HTML button section to simple markdown link format - improved version."""
    
    # More flexible pattern to match various HTML button formats
    html_section_pattern = r'## Get Started with ([^\n]+)\n\n<div[^>]*>.*?</div>'
    
    # Find the HTML button section
    match = re.search(html_section_pattern, content, re.DOTALL)
    
    if match:
        tool_name = match.group(1)
        
        # Extract the first URL from the HTML section
        url_pattern = r'href="([^"]+)"'
        url_match = re.search(url_pattern, match.group(0))
        
        if url_match:
            primary_url = url_match.group(1)
            
            # Extract clean tool name from the tool_name or create one
            clean_tool_name = tool_name.strip()
            
            # Create simple markdown replacement
            simple_format = f'## Get Started with {tool_name}\n\nReady to get started? Visit [{clean_tool_name}]({primary_url}) to explore the platform and begin using this tool.'
            
            # Replace the entire HTML section
            new_content = re.sub(html_section_pattern, simple_format, content, flags=re.DOTALL)
            return new_content, True
    
    return content, False

def main():
    """Fix remaining files with HTML buttons."""
    
    # Find all remaining files with HTML buttons
    all_md_files = glob.glob('content/categories/**/*.md', recursive=True)
    tool_files = [f for f in all_md_files if not f.endswith('_index.md')]
    
    remaining_files = []
    for file in tool_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'target="_blank"' in content:
                    remaining_files.append(file)
        except:
            continue
    
    print(f"Found {len(remaining_files)} files still needing conversion...")
    print("=" * 60)
    
    converted_count = 0
    
    for file_path in remaining_files:
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert buttons to simple markdown
            new_content, converted = convert_html_buttons_to_markdown_v2(content)
            
            if converted:
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                converted_count += 1
                print(f"✓ Converted: {file_path}")
            else:
                print(f"⚠ Manual fix needed: {file_path}")
        
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
    
    print("=" * 60)
    print(f"Fixed {converted_count} additional files")

if __name__ == "__main__":
    main()