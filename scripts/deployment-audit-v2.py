#!/usr/bin/env python3
import os
import json
import csv
from pathlib import Path
from collections import defaultdict
import re

# Paths
content_path = Path.home() / "toolchest-pro-hugo" / "content" / "categories"
csv_path = Path.home() / "toolchest-pro-hugo" / "data" / "tool-database.csv"
homepage_path = Path.home() / "toolchest-pro-hugo" / "content" / "_index.md"

# Data structures
all_tools = []
tools_by_category = defaultdict(list)
tools_by_subcategory = defaultdict(list)
homepage_tools = []
csv_tools = {}

def normalize_tool_name(name):
    """Convert tool name to Hugo slug format"""
    name = re.sub(r'\s*\(.*?\).*$', '', name)
    name = re.sub(r'\s*-.*$', '', name)
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'\s+', '-', name)
    name = re.sub(r'-+', '-', name)
    return name.strip('-')

# Step 1: Scan all tool markdown files (based on directory structure)
print("🔍 Scanning tool landing pages...")
for root, dirs, files in os.walk(content_path):
    # Skip _index.md files and non-markdown files
    tool_files = [f for f in files if f.endswith('.md') and f != '_index.md']
    
    if tool_files:
        # Extract category and subcategory from path
        relative_path = Path(root).relative_to(content_path)
        path_parts = relative_path.parts
        
        if len(path_parts) >= 2:
            category = path_parts[0]
            subcategory = path_parts[1] if len(path_parts) > 1 else ""
            
            for file in tool_files:
                tool_slug = file.replace('.md', '')
                
                # Read first line to get title
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        title = first_line.replace('#', '').strip() if first_line.startswith('#') else tool_slug
                except:
                    title = tool_slug
                
                tool_data = {
                    'file': str(Path(root).relative_to(content_path) / file),
                    'slug': tool_slug,
                    'title': title,
                    'category': category.replace('-', ' ').title(),
                    'subcategory': subcategory.replace('-', ' ').title(),
                    'path': str(file_path)
                }
                
                all_tools.append(tool_data)
                tools_by_category[tool_data['category']].append(tool_data)
                tools_by_subcategory[f"{tool_data['category']} > {tool_data['subcategory']}"].append(tool_data)

# Step 2: Read CSV database
print("📊 Reading CSV database...")
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 3 and row[0] and row[1] and row[2]:
            tool_name = row[0]
            category = row[1]
            subcategory = row[2]
            
            if tool_name != '🤖 AI Tools & Assistants':  # Skip header
                tool_slug = normalize_tool_name(tool_name)
                csv_tools[tool_slug] = {
                    'name': tool_name,
                    'category': category,
                    'subcategory': subcategory
                }

# Step 3: Analyze homepage content
print("🏠 Analyzing homepage featured tools...")
with open(homepage_path, 'r', encoding='utf-8') as f:
    homepage_content = f.read()

# Extract all tool links from homepage
tool_links = re.findall(r'href="/categories/[^"]+/([^/"]+)/"', homepage_content)
homepage_tools = list(set(tool_links))

# Extract tools by category from homepage
homepage_by_category = defaultdict(list)
sections = homepage_content.split('###')
for section in sections[1:]:  # Skip first part before first ###
    lines = section.split('\n')
    if lines[0]:
        # Extract category emoji and name
        category_match = re.match(r'\s*([^A-Za-z]+)\s*(.+)', lines[0])
        if category_match:
            emoji = category_match.group(1).strip()
            category_name = category_match.group(2).strip()
            
            # Find tool links in this section
            section_tools = re.findall(r'href="/categories/[^"]+/([^/"]+)/"', section)
            homepage_by_category[category_name] = section_tools[:3]  # First 3 tools

# Step 4: Cross-reference and generate report
print("\n" + "="*80)
print("📋 TOOLCHEST PRO - COMPREHENSIVE DEPLOYMENT AUDIT")
print("="*80 + "\n")

# Summary statistics
deployed_slugs = {t['slug'] for t in all_tools}
csv_slugs = set(csv_tools.keys())
missing_slugs = csv_slugs - deployed_slugs

print(f"📊 SUMMARY STATISTICS:")
print(f"- Total published landing pages: {len(all_tools)}")
print(f"- Total tools in CSV database: {len(csv_tools)}")
print(f"- Tools missing landing pages: {len(missing_slugs)}")
print(f"- Completion rate: {(len(all_tools)/len(csv_tools)*100):.1f}%")

# Category breakdown
print(f"\n📁 TOOLS BY CATEGORY ({len(tools_by_category)} categories):")
for category in sorted(tools_by_category.keys()):
    print(f"- {category}: {len(tools_by_category[category])} tools")

# Homepage featured tools by category
print(f"\n🏠 HOMEPAGE FEATURED TOOLS BY CATEGORY:")
for category, tools in sorted(homepage_by_category.items()):
    print(f"\n{category} (featuring {len(tools)} tools):")
    for tool in tools:
        print(f"  - {tool}")

# Check git status
print("\n🔍 Checking for uncommitted changes...")
os.system("cd ~/toolchest-pro-hugo && git status --porcelain | grep -E 'content/.*\\.md$' | wc -l")

# Generate detailed JSON report
report = {
    "summary": {
        "total_published_landing_pages": len(all_tools),
        "total_tools_in_csv": len(csv_tools),
        "tools_missing_landing_pages": len(missing_slugs),
        "completion_rate": f"{(len(all_tools)/len(csv_tools)*100):.1f}%",
        "total_categories": len(tools_by_category),
        "total_subcategories": len(tools_by_subcategory)
    },
    "tools_by_category": {cat: len(tools) for cat, tools in tools_by_category.items()},
    "tools_by_subcategory": {subcat: len(tools) for subcat, tools in tools_by_subcategory.items()},
    "homepage_featured_by_category": dict(homepage_by_category),
    "all_published_tools": sorted([t['slug'] for t in all_tools]),
    "missing_tools": sorted(list(missing_slugs))
}

# Save reports
report_path = Path.home() / "toolchest-pro-hugo" / "data" / "deployment-audit-final.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

summary_path = Path.home() / "toolchest-pro-hugo" / "data" / "deployment-summary.txt"
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("TOOLCHEST PRO - DEPLOYMENT SUMMARY\n")
    f.write("="*50 + "\n\n")
    f.write(f"Total Published: {len(all_tools)} landing pages\n")
    f.write(f"Total in CSV: {len(csv_tools)} tools\n")
    f.write(f"Missing Pages: {len(missing_slugs)} tools\n")
    f.write(f"Completion: {(len(all_tools)/len(csv_tools)*100):.1f}%\n\n")
    
    f.write("PUBLISHED TOOLS BY SUBCATEGORY:\n")
    f.write("-"*50 + "\n")
    for subcat in sorted(tools_by_subcategory.keys()):
        f.write(f"\n{subcat} ({len(tools_by_subcategory[subcat])} tools):\n")
        for tool in sorted(tools_by_subcategory[subcat], key=lambda x: x['slug']):
            f.write(f"  - {tool['slug']}\n")

print(f"\n✅ Reports saved:")
print(f"  - JSON: {report_path}")
print(f"  - Summary: {summary_path}")

# Quick stats
print(f"\n🎯 QUICK REFERENCE:")
print(f"  - Need to create: {len(missing_slugs)} more landing pages")
print(f"  - Current progress: {len(all_tools)}/{len(csv_tools)} tools")

# Show sample of missing tools
if missing_slugs:
    print(f"\n📝 Sample of missing tools (first 10):")
    for slug in sorted(list(missing_slugs))[:10]:
        tool_info = csv_tools.get(slug, {})
        print(f"  - {slug} ({tool_info.get('category', 'Unknown')} > {tool_info.get('subcategory', 'Unknown')})")