#!/usr/bin/env python3
"""Fix all category assignments comprehensively."""

import os
import re
from pathlib import Path

# All 32 categories from the database (NO EMOJIS)
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

# Map variants to correct names
CATEGORY_FIXES = {
    "Customer Support": "Customer Support Tools",
    "Business Marketing": "Marketing & Social Media",
    "DevOps & Infrastructure": "DevOps & Infrastructure Tools",
    "Media & Entertainment": "Media & Entertainment Tools",
    "Research & Survey": "Research & Survey Tools",
    "Video & Audio": "Media & Entertainment Tools",
    # Emoji versions
    "⚖️ Legal & Compliance Tools": "Legal & Compliance Tools",
    "🎨 Design & Creative Tools": "Design & Creative Tools",
    "🎵 Media & Entertainment Tools": "Media & Entertainment Tools",
    "💻 Development & Technical Tools": "Development & Technical Tools"
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
    'customer-support': 'Customer Support Tools',  # variant
    'database-data-management': 'Database & Data Management',
    'design-creative-tools': 'Design & Creative Tools',
    'development-technical-tools': 'Development & Technical Tools',
    'devops-infrastructure-tools': 'DevOps & Infrastructure Tools',
    'devops-infrastructure': 'DevOps & Infrastructure Tools',  # variant
    'ecommerce-business-tools': 'E-commerce & Business Tools',
    'event-management-tools': 'Event Management Tools',
    'finance-accounting': 'Finance & Accounting',
    'hardware-equipment-tools': 'Hardware & Equipment Tools',
    'hr-recruiting-tools': 'HR & Recruiting Tools',
    'learning-development': 'Learning & Development',
    'legal-compliance-tools': 'Legal & Compliance Tools',
    'marketing-social-media': 'Marketing & Social Media',
    'business-marketing-tools': 'Marketing & Social Media',  # variant
    'media-entertainment-tools': 'Media & Entertainment Tools',
    'media-entertainment': 'Media & Entertainment Tools',  # variant
    'note-taking-knowledge-management': 'Note-taking & Knowledge Management',
    'productivity-task-management': 'Productivity & Task Management',
    'research-survey-tools': 'Research & Survey Tools',
    'research-survey': 'Research & Survey Tools',  # variant
    'scientific-research-tools': 'Scientific & Research Tools',
    'security-privacy-tools': 'Security & Privacy Tools',
    'testing-quality-assurance': 'Testing & Quality Assurance',
    'time-tracking-scheduling': 'Time Tracking & Scheduling',
    'translation-localization-tools': 'Translation & Localization Tools',
    'travel-expense-management': 'Travel & Expense Management',
    'accessibility-inclusion-tools': 'Accessibility & Inclusion Tools',
    'api-integration-tools': 'API & Integration Tools',
    'video-audio-tools': 'Media & Entertainment Tools',  # variant
    'video-audio': 'Media & Entertainment Tools'  # variant
}

def dir_to_subcategory(dir_name):
    """Convert directory name to proper subcategory name."""
    words = dir_name.replace('-', ' ').split()
    return ' '.join(word.capitalize() for word in words)

def fix_frontmatter(file_path):
    """Fix category and subcategory in frontmatter."""
    try:
        # Extract category from path
        path_parts = Path(file_path).parts
        cat_index = path_parts.index('categories')
        cat_dir = path_parts[cat_index + 1]
        
        # Get proper category name
        category = DIR_TO_CATEGORY.get(cat_dir)
        if not category:
            print(f"Warning: Unknown category directory: {cat_dir} for {file_path}")
            return False
            
        # Get subcategory if exists
        subcat_dir = None
        if len(path_parts) > cat_index + 3:
            subcat_dir = path_parts[cat_index + 2]
        
        subcategory = dir_to_subcategory(subcat_dir) if subcat_dir else category
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            print(f"Warning: No frontmatter found in {file_path}")
            return False
        
        # Split content
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"Warning: Invalid frontmatter in {file_path}")
            return False
            
        frontmatter = parts[1]
        body = parts[2]
        
        # Remove all emojis from frontmatter
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
            "\U00002702-\U000027B0"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642" 
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+", re.UNICODE
        )
        
        # Update category field
        frontmatter = re.sub(
            r'^category:\s*"[^"]*"$',
            f'category: "{category}"',
            frontmatter,
            flags=re.MULTILINE
        )
        
        # Update subcategory field
        frontmatter = re.sub(
            r'^subcategory:\s*"[^"]*"$',
            f'subcategory: "{subcategory}"',
            frontmatter,
            flags=re.MULTILINE
        )
        
        # Remove any remaining emojis
        frontmatter = emoji_pattern.sub('', frontmatter)
        
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
    print("\nVerifying categories...")
    categories_found = set()
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'^category:\s*"([^"]*)"', content, re.MULTILINE)
            if match:
                categories_found.add(match.group(1))
    
    print(f"\nFound {len(categories_found)} unique categories:")
    for cat in sorted(categories_found):
        if cat in VALID_CATEGORIES:
            print(f"  ✓ {cat}")
        else:
            print(f"  ✗ {cat} (INVALID)")

if __name__ == '__main__':
    main()