#!/usr/bin/env python3
"""Fix category assignments in tool frontmatter based on directory structure."""

import os
import re
from pathlib import Path

# Directory to category mapping (based on actual directory names)
DIR_TO_CATEGORY = {
    'ai-tools-assistants': 'AI Tools & Assistants',
    'analytics-data-tools': 'Analytics & Data Tools',
    'automation-workflows': 'Automation & Workflows',
    'backup-disaster-recovery': 'Backup & Disaster Recovery',
    'cloud-storage-file-management': 'Cloud Storage & File Management',
    'communication-collaboration': 'Communication & Collaboration',
    'crm-sales-tools': 'CRM & Sales Tools',
    'customer-support-tools': 'Customer Support Tools',
    'database-data-management': 'Database & Data Management',
    'design-creative-tools': 'Design & Creative Tools',
    'development-technical-tools': 'Development & Technical Tools',
    'devops-infrastructure-tools': 'DevOps & Infrastructure Tools',
    'ecommerce-business-tools': 'E-commerce & Business Tools',
    'event-management-tools': 'Event Management Tools',
    'finance-accounting': 'Finance & Accounting',
    'hardware-equipment-tools': 'Hardware & Equipment Tools',
    'hr-recruiting-tools': 'HR & Recruiting Tools',
    'learning-development': 'Learning & Development',
    'legal-compliance-tools': 'Legal & Compliance Tools',
    'marketing-social-media': 'Marketing & Social Media',
    'media-entertainment-tools': 'Media & Entertainment Tools',
    'note-taking-knowledge-management': 'Note-taking & Knowledge Management',
    'productivity-task-management': 'Productivity & Task Management',
    'research-survey-tools': 'Research & Survey Tools',
    'scientific-research-tools': 'Scientific & Research Tools',
    'security-privacy-tools': 'Security & Privacy Tools',
    'testing-quality-assurance': 'Testing & Quality Assurance',
    'time-tracking-scheduling': 'Time Tracking & Scheduling',
    'translation-localization-tools': 'Translation & Localization Tools',
    'travel-expense-management': 'Travel & Expense Management',
    'accessibility-inclusion-tools': 'Accessibility & Inclusion Tools',
    'api-integration-tools': 'API & Integration Tools'
}

# Subcategory mapping (convert directory names to readable format)
def dir_to_subcategory(dir_name):
    """Convert directory name to proper subcategory name."""
    # Replace hyphens with spaces and capitalize properly
    words = dir_name.replace('-', ' ').split()
    return ' '.join(word.capitalize() for word in words)

def fix_frontmatter(file_path):
    """Fix category and subcategory in frontmatter based on file path."""
    try:
        # Extract category and subcategory from path
        path_parts = Path(file_path).parts
        
        # Find the index of 'categories' in path
        cat_index = path_parts.index('categories')
        
        # Get category directory name
        cat_dir = path_parts[cat_index + 1]
        
        # Get subcategory directory name (if exists)
        subcat_dir = None
        if len(path_parts) > cat_index + 3:  # has subcategory
            subcat_dir = path_parts[cat_index + 2]
        
        # Get proper category name
        category = DIR_TO_CATEGORY.get(cat_dir, '')
        if not category:
            print(f"Warning: Unknown category directory: {cat_dir}")
            return False
            
        # Get proper subcategory name
        subcategory = dir_to_subcategory(subcat_dir) if subcat_dir else category
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has frontmatter
        if not content.startswith('---'):
            print(f"Warning: No frontmatter found in {file_path}")
            return False
        
        # Split frontmatter and content
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"Warning: Invalid frontmatter in {file_path}")
            return False
            
        frontmatter = parts[1]
        body = parts[2]
        
        # Update category field (remove emoji and fix value)
        frontmatter = re.sub(
            r'^category:\s*"[^"]*"$',
            f'category: "{category}"',
            frontmatter,
            flags=re.MULTILINE
        )
        
        # Update subcategory field (remove emoji and fix value)
        frontmatter = re.sub(
            r'^subcategory:\s*"[^"]*"$',
            f'subcategory: "{subcategory}"',
            frontmatter,
            flags=re.MULTILINE
        )
        
        # Reconstruct file
        new_content = f"---{frontmatter}---{body}"
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    """Process all markdown files in categories directory."""
    content_dir = Path('content/categories')
    
    if not content_dir.exists():
        print("Error: content/categories directory not found!")
        return
    
    # Find all markdown files (excluding _index.md)
    md_files = []
    for file_path in content_dir.rglob('*.md'):
        if file_path.name != '_index.md':
            md_files.append(file_path)
    
    print(f"Found {len(md_files)} tool files to process")
    
    # Process each file
    success_count = 0
    for i, file_path in enumerate(md_files, 1):
        if i % 100 == 0:
            print(f"Processing file {i}/{len(md_files)}...")
            
        if fix_frontmatter(file_path):
            success_count += 1
    
    print(f"\nCompleted! Successfully updated {success_count}/{len(md_files)} files")

if __name__ == '__main__':
    main()