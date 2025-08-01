#!/usr/bin/env python3
"""Fix categories field for Hugo taxonomy."""

import os
import re
from pathlib import Path

# All 32 categories from the database
VALID_CATEGORIES = {
    "AI Tools & Assistants",
    "Analytics & Data Tools",
    "Automation & Workflows",
    "Backup & Disaster Recovery",
    "Cloud Storage & File Management",
    "Communication & Collaboration",
    "CRM & Sales Tools",
    "Customer Support Tools",
    "Database & Data Management",
    "Design & Creative Tools",
    "Development & Technical Tools",
    "DevOps & Infrastructure Tools",
    "E-commerce & Business Tools",
    "Event Management Tools",
    "Finance & Accounting",
    "Hardware & Equipment Tools",
    "HR & Recruiting Tools",
    "Learning & Development",
    "Legal & Compliance Tools",
    "Marketing & Social Media",
    "Media & Entertainment Tools",
    "Note-taking & Knowledge Management",
    "Productivity & Task Management",
    "Research & Survey Tools",
    "Scientific & Research Tools",
    "Security & Privacy Tools",
    "Testing & Quality Assurance",
    "Time Tracking & Scheduling",
    "Translation & Localization Tools",
    "Travel & Expense Management",
    "Accessibility & Inclusion Tools",
    "API & Integration Tools"
}

# Directory to category mapping
DIR_TO_CATEGORY = {
    'ai-tools-assistants': 'AI Tools & Assistants',
    'analytics-data-tools': 'Analytics & Data Tools',
    'automation-workflows': 'Automation & Workflows',
    'backup-disaster-recovery': 'Backup & Disaster Recovery',
    'cloud-storage-file-management': 'Cloud Storage & File Management',
    'communication-collaboration': 'Communication & Collaboration',
    'crm-sales-tools': 'CRM & Sales Tools',
    'customer-support-tools': 'Customer Support Tools',
    'customer-support': 'Customer Support Tools',
    'database-data-management': 'Database & Data Management',
    'design-creative-tools': 'Design & Creative Tools',
    'development-technical-tools': 'Development & Technical Tools',
    'devops-infrastructure-tools': 'DevOps & Infrastructure Tools',
    'devops-infrastructure': 'DevOps & Infrastructure Tools',
    'ecommerce-business-tools': 'E-commerce & Business Tools',
    'event-management-tools': 'Event Management Tools',
    'finance-accounting': 'Finance & Accounting',
    'hardware-equipment-tools': 'Hardware & Equipment Tools',
    'hr-recruiting-tools': 'HR & Recruiting Tools',
    'learning-development': 'Learning & Development',
    'legal-compliance-tools': 'Legal & Compliance Tools',
    'marketing-social-media': 'Marketing & Social Media',
    'business-marketing-tools': 'Marketing & Social Media',
    'media-entertainment-tools': 'Media & Entertainment Tools',
    'media-entertainment': 'Media & Entertainment Tools',
    'note-taking-knowledge-management': 'Note-taking & Knowledge Management',
    'productivity-task-management': 'Productivity & Task Management',
    'research-survey-tools': 'Research & Survey Tools',
    'research-survey': 'Research & Survey Tools',
    'scientific-research-tools': 'Scientific & Research Tools',
    'security-privacy-tools': 'Security & Privacy Tools',
    'testing-quality-assurance': 'Testing & Quality Assurance',
    'time-tracking-scheduling': 'Time Tracking & Scheduling',
    'translation-localization-tools': 'Translation & Localization Tools',
    'travel-expense-management': 'Travel & Expense Management',
    'accessibility-inclusion-tools': 'Accessibility & Inclusion Tools',
    'api-integration-tools': 'API & Integration Tools',
    'video-audio-tools': 'Media & Entertainment Tools',
    'video-audio': 'Media & Entertainment Tools'
}

def fix_frontmatter(file_path):
    """Fix categories field in frontmatter for Hugo taxonomy."""
    try:
        # Extract category from path
        path_parts = Path(file_path).parts
        cat_index = path_parts.index('categories')
        cat_dir = path_parts[cat_index + 1]
        
        # Get proper category name
        category = DIR_TO_CATEGORY.get(cat_dir)
        if not category:
            print(f"Warning: Unknown category directory: {cat_dir}")
            return False
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return False
        
        # Split content
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False
            
        frontmatter = parts[1]
        body = parts[2]
        
        # Update categories field (plural) for Hugo taxonomy
        # First check if categories field exists
        if re.search(r'^categories:', frontmatter, re.MULTILINE):
            # Update existing categories field
            frontmatter = re.sub(
                r'^categories:\s*\[[^\]]*\]$',
                f'categories: ["{category}"]',
                frontmatter,
                flags=re.MULTILINE
            )
        else:
            # Add categories field if it doesn't exist
            # Add after category field
            frontmatter = re.sub(
                r'(^category:\s*"[^"]*"$)',
                f'\\1\ncategories: ["{category}"]',
                frontmatter,
                flags=re.MULTILINE
            )
        
        # Reconstruct file
        new_content = f"---{frontmatter}---{body}"
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    """Process all markdown files."""
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
    
    # Verify categories
    print("\nVerifying categories field...")
    categories_found = set()
    for file_path in md_files[:5]:  # Check first 5 files
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'^categories:\s*\["([^"]*)"\]', content, re.MULTILINE)
            if match:
                print(f"  {file_path.name}: {match.group(1)}")

if __name__ == '__main__':
    main()