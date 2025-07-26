#!/usr/bin/env python3
import csv
import os
import re
from pathlib import Path
from collections import defaultdict

# Paths
csv_path = Path.home() / "toolchest-pro-hugo" / "data" / "tool-database.csv"
content_path = Path.home() / "toolchest-pro-hugo" / "content" / "categories"

# Read existing tool pages
existing_tools = set()
existing_tool_paths = {}

for root, dirs, files in os.walk(content_path):
    for file in files:
        if file.endswith('.md') and file != '_index.md':
            tool_slug = file.replace('.md', '')
            existing_tools.add(tool_slug)
            existing_tool_paths[tool_slug] = os.path.join(root, file)

# Read CSV and analyze
audit_results = defaultdict(list)
total_tools = 0
existing_count = 0
missing_count = 0

def normalize_tool_name(name):
    """Convert tool name to Hugo slug format"""
    # Remove anything after parentheses or dashes
    name = re.sub(r'\s*\(.*?\).*$', '', name)
    name = re.sub(r'\s*-.*$', '', name)
    # Convert to lowercase and replace spaces with hyphens
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'\s+', '-', name)
    name = re.sub(r'-+', '-', name)
    return name.strip('-')

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    
    current_category = None
    current_subcategory = None
    
    for row in reader:
        if len(row) >= 3:
            col1, col2, col3 = row[0], row[1], row[2]
            
            # Skip header
            if col1 == '🤖 AI Tools & Assistants' and col2 == 'CATEGORY':
                continue
                
            # Check if this is a category header
            if col2 == '' and col3 == '':
                current_subcategory = col1
                continue
                
            # Skip empty rows
            if col1 == '' and col2 == '' and col3 == '':
                continue
                
            # This is a tool row
            if col1 and col2 and col3:
                tool_name = col1
                category = col2
                subcategory = col3
                
                # Normalize tool name to match file naming
                tool_slug = normalize_tool_name(tool_name)
                
                if tool_slug:
                    total_tools += 1
                    
                    # Check if tool exists
                    status = "✅ Existing" if tool_slug in existing_tools else "❌ Missing"
                    
                    if tool_slug in existing_tools:
                        existing_count += 1
                    else:
                        missing_count += 1
                    
                    # Store in audit results by subcategory
                    audit_results[f"{category} > {subcategory}"].append({
                        'name': tool_name,
                        'slug': tool_slug,
                        'status': status,
                        'category': category,
                        'subcategory': subcategory
                    })

# Generate report
print("🚀 TOOLCHEST PRO - TOOL AUDIT REPORT")
print("=" * 80)
print(f"\n📊 SUMMARY:")
print(f"Total tools in database: {total_tools}")
print(f"✅ Existing landing pages: {existing_count}")
print(f"❌ Missing landing pages: {missing_count}")
print(f"📈 Completion rate: {(existing_count/total_tools*100):.1f}%")
print("\n" + "=" * 80)

# Sort subcategories for organized output
sorted_subcategories = sorted(audit_results.keys())

print("\n📋 DETAILED AUDIT BY SUBCATEGORY:\n")

for subcategory in sorted_subcategories:
    tools = audit_results[subcategory]
    missing_in_subcat = sum(1 for t in tools if t['status'] == "❌ Missing")
    
    print(f"\n### {subcategory}")
    print(f"Total: {len(tools)} | Missing: {missing_in_subcat}")
    print("-" * 60)
    
    # Show all tools with their status
    for tool in sorted(tools, key=lambda x: (x['status'], x['name'])):
        print(f"{tool['status']} {tool['name']} → {tool['slug']}.md")

# Generate missing tools summary for batch processing
print("\n\n" + "=" * 80)
print("🎯 MISSING TOOLS BY SUBCATEGORY (For Batch Processing):\n")

for subcategory in sorted_subcategories:
    tools = audit_results[subcategory]
    missing_tools = [t for t in tools if t['status'] == "❌ Missing"]
    
    if missing_tools:
        print(f"\n{subcategory} ({len(missing_tools)} missing):")
        for tool in missing_tools:
            print(f"  - {tool['name']}")

# Save detailed results to file
output_path = Path.home() / "toolchest-pro-hugo" / "data" / "audit-results.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("TOOLCHEST PRO - DETAILED AUDIT RESULTS\n")
    f.write("=" * 80 + "\n\n")
    
    for subcategory in sorted_subcategories:
        tools = audit_results[subcategory]
        f.write(f"\n{subcategory}\n")
        f.write("-" * 60 + "\n")
        for tool in sorted(tools, key=lambda x: (x['status'], x['name'])):
            f.write(f"{tool['status']} {tool['name']} → {tool['slug']}.md\n")

print(f"\n✅ Detailed results saved to: {output_path}")