#!/usr/bin/env python3
"""
Convert HTML button sections back to simple markdown links.
Reverts 392 pages with HTML buttons to match the simple format used by 904 pages.
"""

import os
import re
import glob

def convert_html_buttons_to_markdown(content):
    """Convert HTML button section to simple markdown link format."""
    
    # Pattern to match the HTML button section
    html_button_pattern = r'## Get Started with ([^\n]+)\n\n<div style="text-align: center; margin: 2rem 0;">\s*<a href="([^"]+)"[^>]*>([^<]+)</a>[^<]*(?:<a href="([^"]+)"[^>]*>([^<]+)</a>)?\s*</div>'
    
    # Find the HTML button section
    match = re.search(html_button_pattern, content, re.DOTALL)
    
    if match:
        tool_name = match.group(1)
        primary_url = match.group(2)
        primary_text = match.group(3)
        
        # Extract clean tool name from primary_text (remove arrow)
        clean_tool_name = primary_text.replace(' →', '').replace('Visit ', '').replace('Try ', '')
        
        # Create simple markdown replacement
        simple_format = f'## Get Started with {tool_name}\n\nReady to get started? Visit [{clean_tool_name}]({primary_url}) to explore the platform and begin using this tool.'
        
        # Replace the entire HTML section
        new_content = re.sub(html_button_pattern, simple_format, content, flags=re.DOTALL)
        return new_content, True
    
    return content, False

def main():
    """Main conversion function."""
    
    # Find all markdown files with HTML buttons
    all_md_files = glob.glob('content/categories/**/*.md', recursive=True)
    tool_files = [f for f in all_md_files if not f.endswith('_index.md')]
    
    converted_count = 0
    files_with_buttons = []
    
    print("Starting conversion of HTML buttons to simple markdown links...")
    print("=" * 60)
    
    for file_path in tool_files:
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has HTML buttons
            if 'target="_blank"' in content and '<div style="text-align: center' in content:
                files_with_buttons.append(file_path)
                
                # Convert buttons to simple markdown
                new_content, converted = convert_html_buttons_to_markdown(content)
                
                if converted:
                    # Write back to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    converted_count += 1
                    print(f"✓ Converted: {file_path}")
                else:
                    print(f"⚠ Could not convert: {file_path}")
        
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
    
    print("=" * 60)
    print(f"Conversion complete!")
    print(f"Files with buttons found: {len(files_with_buttons)}")
    print(f"Files successfully converted: {converted_count}")
    
    if converted_count > 0:
        print(f"\nNext steps:")
        print(f"1. Review a few converted files to ensure format is correct")
        print(f"2. Run git add and git commit to save changes")

if __name__ == "__main__":
    main()