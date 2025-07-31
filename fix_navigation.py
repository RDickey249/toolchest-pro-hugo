#!/usr/bin/env python3
"""
Emergency Navigation Fix
Updates the existing HTML files to fix the broken category navigation
"""

import os
import re
from pathlib import Path

def create_category_page_content(category_name, category_path, tools_data):
    """Create proper category page content showing subcategories and tools"""
    
    # Group tools by subcategory
    subcategories = {}
    for tool in tools_data:
        subcat = tool.get('subcategory', 'Other')
        if subcat not in subcategories:
            subcategories[subcat] = []
        subcategories[subcat].append(tool)
    
    # Build the HTML content
    content_sections = []
    
    for subcategory, tools in subcategories.items():
        tools_html = []
        for tool in tools:
            tool_html = f'''
                <div class="tool-card">
                    <div class="tool-category">{tool.get('category', 'Tool')}</div>
                    <h3><a href="{tool.get('url', '#')}">{tool.get('title', 'Tool')}</a></h3>
                    <p class="tool-tagline">{tool.get('tagline', 'Professional tool for enhanced productivity')}</p>
                    <a href="{tool.get('url', '#')}" class="tool-link">Learn More →</a>
                </div>
            '''
            tools_html.append(tool_html)
        
        section_html = f'''
            <div class="subcategory-section">
                <h2 class="subcategory-title">{subcategory} ({len(tools)} tools)</h2>
                <div class="tool-grid">
                    {''.join(tools_html)}
                </div>
            </div>
        '''
        content_sections.append(section_html)
    
    return f'''
        <h1>{category_name}</h1>
        <p>Browse tools and subcategories in {category_name}.</p>
        
        <style>
        .subcategory-section {{
            margin: 40px 0;
        }}
        
        .subcategory-title {{
            color: #9EC9FF;
            border-bottom: 2px solid #E74C3C;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}
        
        .tool-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .tool-card {{
            border: 1px solid #666;
            padding: 20px;
            border-radius: 8px;
            background: #444444;
            transition: all 0.3s ease;
            border-left: 3px solid #E74C3C;
        }}
        
        .tool-card:hover {{
            border-color: #9EC9FF;
            border-left-color: #9EC9FF;
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }}
        
        .tool-card h3 {{
            margin-top: 0;
            color: #9EC9FF;
            margin-bottom: 8px;
            font-size: 1.2rem;
        }}
        
        .tool-card h3 a {{
            text-decoration: none;
            color: inherit;
            transition: color 0.3s ease;
        }}
        
        .tool-card h3 a:hover {{
            color: #FFFFFF;
        }}
        
        .tool-category {{
            color: #E74C3C;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }}
        
        .tool-tagline {{
            color: #FFFFFF;
            margin-bottom: 15px;
            font-size: 0.95rem;
            line-height: 1.4;
        }}
        
        .tool-link {{
            display: inline-block;
            background: #39FF14;
            color: #000000;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }}
        
        .tool-link:hover {{
            background: #2BFF00;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(57, 255, 20, 0.3);
        }}
        </style>
        
        {''.join(content_sections)}
    '''

def extract_tools_from_search_index():
    """Extract tools data from the search index"""
    try:
        import json
        with open('static/search-index.json', 'r') as f:
            return json.load(f)
    except:
        return []

def fix_category_pages():
    """Fix the category pages to show actual content instead of the categories overview"""
    
    print("🔧 FIXING CATEGORY NAVIGATION")
    print("=" * 50)
    
    # Load tools data
    tools_data = extract_tools_from_search_index()
    if not tools_data:
        print("❌ Could not load search index data")
        return
    
    print(f"✅ Loaded {len(tools_data)} tools from search index")
    
    # Group tools by category
    categories = {}
    for tool in tools_data:
        category = tool.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(tool)
    
    # Map category names to directory names
    category_mappings = {
        'AI Tools & Assistants': 'ai-tools-assistants',
        'Analytics & Data Tools': 'analytics-data-tools',
        'Automation & Workflows': 'automation-workflows',
        'Business Marketing Tools': 'business-marketing-tools',
        'Cloud Storage & File Management': 'cloud-storage-file-management',
        'Communication & Collaboration': 'communication-collaboration',
        'CRM & Sales Tools': 'crm-sales-tools',
        'Customer Support': 'customer-support',
        'Database & Data Management': 'database-data-management',
        'Design & Creative Tools': 'design-creative-tools',
        'Development & Technical Tools': 'development-technical-tools',
        'DevOps & Infrastructure Tools': 'devops-infrastructure-tools',
        'E-commerce & Business Tools': 'ecommerce-business-tools',
        'Education & Learning Tools': 'education-learning-tools',
        'Finance & Accounting': 'finance-accounting',
        'HR & Recruiting Tools': 'hr-recruiting-tools',
        'Learning & Development': 'learning-development',
        'Legal & Compliance Tools': 'legal-compliance-tools',
        'Marketing & Social Media': 'marketing-social-media',
        'Media & Entertainment Tools': 'media-entertainment-tools',
        'Note-Taking & Knowledge Management': 'note-taking-knowledge-management',
        'Productivity & Task Management': 'productivity-task-management',
        'Research & Survey': 'research-survey',
        'Security & Privacy Tools': 'security-privacy-tools',
        'Testing & Quality Assurance': 'testing-quality-assurance',
        'Time Tracking & Scheduling': 'time-tracking-scheduling',
        'Video & Audio Tools': 'video-audio-tools'
    }
    
    fixed_count = 0
    
    # Fix each category page
    for category_name, category_dir in category_mappings.items():
        category_tools = categories.get(category_name, [])
        if not category_tools:
            continue
            
        # Path to the category HTML file
        html_path = f"public/categories/{category_dir}/index.html"
        
        if not os.path.exists(html_path):
            print(f"⚠️  Category page not found: {html_path}")
            continue
        
        try:
            # Read the existing HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Generate the new main content
            new_content = create_category_page_content(category_name, category_dir, category_tools)
            
            # Replace the main content between <main> tags
            main_pattern = r'(<main>)(.*?)(</main>)'
            replacement = r'\1' + new_content + r'\3'
            
            updated_html = re.sub(main_pattern, replacement, html_content, flags=re.DOTALL)
            
            # Write the updated HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(updated_html)
            
            fixed_count += 1
            print(f"✅ Fixed {category_name} ({len(category_tools)} tools)")
            
        except Exception as e:
            print(f"❌ Error fixing {category_name}: {e}")
    
    print(f"\n🎯 SUMMARY")
    print("-" * 30)
    print(f"Fixed {fixed_count} category pages")
    print(f"Categories now show subcategories and tools properly")
    
    return fixed_count

def main():
    """Main execution function"""
    
    print("🚀 TOOLCHEST PRO HUGO - EMERGENCY NAVIGATION FIX")
    print("=" * 60)
    
    fixed_count = fix_category_pages()
    
    if fixed_count > 0:
        print(f"\n✅ NAVIGATION FIX COMPLETE")
        print(f"Category pages now show actual tools instead of the categories overview")
        print(f"Users can now drill down: Categories → Subcategories → Tools")
        print(f"\n🔄 Next: Test the navigation on https://toolchest.pro/categories/")
    else:
        print(f"\n❌ NO FIXES APPLIED")
        print(f"Check if search index exists and category pages are present")

if __name__ == "__main__":
    main()