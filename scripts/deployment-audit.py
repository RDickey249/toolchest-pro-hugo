#!/usr/bin/env python3
import os
import yaml
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
csv_tools = set()

def normalize_tool_name(name):
    """Convert tool name to Hugo slug format"""
    name = re.sub(r'\s*\(.*?\).*$', '', name)
    name = re.sub(r'\s*-.*$', '', name)
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'\s+', '-', name)
    name = re.sub(r'-+', '-', name)
    return name.strip('-')

def extract_front_matter(file_path):
    """Extract YAML front matter from markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            try:
                fm = yaml.safe_load(content[3:end])
                return fm
            except:
                return {}
    return {}

# Step 1: Scan all tool markdown files
print("🔍 Scanning tool landing pages...")
for root, dirs, files in os.walk(content_path):
    for file in files:
        if file.endswith('.md') and file != '_index.md':
            file_path = Path(root) / file
            relative_path = file_path.relative_to(content_path)
            
            # Extract front matter
            fm = extract_front_matter(file_path)
            
            if fm:
                tool_data = {
                    'file': str(relative_path),
                    'slug': file.replace('.md', ''),
                    'title': fm.get('title', ''),
                    'category': fm.get('category', ''),
                    'subcategory': fm.get('subcategory', ''),
                    'featured': fm.get('featured', False),
                    'homepage': fm.get('homepage', False),
                    'draft': fm.get('draft', False)
                }
                
                # Only count non-draft tools
                if not tool_data['draft']:
                    all_tools.append(tool_data)
                    
                    if tool_data['category']:
                        tools_by_category[tool_data['category']].append(tool_data)
                    if tool_data['subcategory']:
                        tools_by_subcategory[f"{tool_data['category']} > {tool_data['subcategory']}"].append(tool_data)

# Step 2: Read CSV database
print("📊 Reading CSV database...")
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 3 and row[0] and row[1] and row[2]:
            tool_name = row[0]
            if tool_name != '🤖 AI Tools & Assistants':  # Skip header
                tool_slug = normalize_tool_name(tool_name)
                csv_tools.add(tool_slug)

# Step 3: Analyze homepage content
print("🏠 Analyzing homepage featured tools...")
with open(homepage_path, 'r', encoding='utf-8') as f:
    homepage_content = f.read()
    
# Extract tool links from homepage
import re
tool_links = re.findall(r'href="/categories/[^"]+/([^/"]+)/"', homepage_content)
homepage_tools = list(set(tool_links))

# Step 4: Generate comprehensive report
print("\n" + "="*80)
print("📋 TOOLCHEST PRO - COMPREHENSIVE DEPLOYMENT AUDIT")
print("="*80 + "\n")

# Summary statistics
published_tools = [t for t in all_tools if not t['draft']]
print(f"📊 SUMMARY STATISTICS:")
print(f"- Total published landing pages: {len(published_tools)}")
print(f"- Total tools in CSV database: {len(csv_tools)}")
print(f"- Tools missing landing pages: {len(csv_tools) - len(published_tools)}")
print(f"- Completion rate: {(len(published_tools)/len(csv_tools)*100):.1f}%")

# Category breakdown
print(f"\n📁 TOOLS BY CATEGORY:")
for category in sorted(tools_by_category.keys()):
    print(f"- {category}: {len(tools_by_category[category])} tools")

# Subcategory breakdown
print(f"\n📂 TOOLS BY SUBCATEGORY:")
for subcategory in sorted(tools_by_subcategory.keys()):
    print(f"- {subcategory}: {len(tools_by_subcategory[subcategory])} tools")

# Homepage featured tools
print(f"\n🏠 HOMEPAGE FEATURED TOOLS: {len(homepage_tools)} tools")

# List all published tools
print(f"\n📄 ALL PUBLISHED TOOL SLUGS ({len(published_tools)} total):")
for tool in sorted(published_tools, key=lambda x: x['slug']):
    print(f"- {tool['slug']}")

# Generate JSON report
report = {
    "summary": {
        "total_published_landing_pages": len(published_tools),
        "total_tools_in_csv": len(csv_tools),
        "tools_missing_landing_pages": len(csv_tools) - len(published_tools),
        "completion_rate": f"{(len(published_tools)/len(csv_tools)*100):.1f}%"
    },
    "tools_by_category": {cat: len(tools) for cat, tools in tools_by_category.items()},
    "tools_by_subcategory": {subcat: len(tools) for subcat, tools in tools_by_subcategory.items()},
    "homepage_featured_tools": homepage_tools,
    "all_published_tools": [t['slug'] for t in published_tools]
}

# Save JSON report
report_path = Path.home() / "toolchest-pro-hugo" / "data" / "deployment-audit.json"
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

print(f"\n✅ Full JSON report saved to: {report_path}")

# Check for uncommitted files
print("\n🔍 Checking for uncommitted tool pages...")
os.system("cd ~/toolchest-pro-hugo && git status --porcelain content/categories/ | grep -E '\.md$' | head -20")