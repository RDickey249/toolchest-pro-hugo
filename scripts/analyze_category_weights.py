#!/usr/bin/env python3
"""
Analyze category weights for revenue optimization
Creates weighted category display order based on affiliate potential
"""

import os
import glob
from pathlib import Path

def analyze_categories():
    """Analyze categories and their affiliate potential"""
    base_path = Path("content/categories")
    results = []
    
    for category_dir in base_path.iterdir():
        if not category_dir.is_dir():
            continue
            
        category_name = category_dir.name
        
        # Count total tools
        tool_files = list(category_dir.rglob("*.md"))
        tool_files = [f for f in tool_files if f.name != "_index.md"]
        total_tools = len(tool_files)
        
        # Count affiliate tools
        affiliate_count = 0
        for tool_file in tool_files:
            try:
                with open(tool_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'affiliate: true' in content:
                        affiliate_count += 1
            except:
                pass
        
        # Calculate affiliate percentage
        affiliate_percentage = (affiliate_count / total_tools * 100) if total_tools > 0 else 0
        
        results.append({
            'category': category_name,
            'affiliate_count': affiliate_count,
            'total_tools': total_tools,
            'affiliate_percentage': affiliate_percentage
        })
    
    # Sort by affiliate count (descending), then by percentage, then alphabetically
    results.sort(key=lambda x: (-x['affiliate_count'], -x['affiliate_percentage'], x['category']))
    
    print("CATEGORY ANALYSIS - REVENUE POTENTIAL")
    print("=" * 60)
    print(f"{'Category':<35} {'Affiliate':<10} {'Total':<8} {'%':<6}")
    print("-" * 60)
    
    for result in results:
        print(f"{result['category']:<35} {result['affiliate_count']:<10} {result['total_tools']:<8} {result['affiliate_percentage']:<6.1f}")
    
    return results

def create_weighted_categories():
    """Create weighted category data for Hugo"""
    results = analyze_categories()
    
    print("\nWEIGHTED CATEGORY YAML:")
    print("=" * 40)
    
    weight = 100  # Start with high weight
    for result in results:
        category = result['category']
        
        # Convert directory name to display name
        display_name = category.replace('-', ' ').title()
        display_name = display_name.replace('Ai ', 'AI ')
        display_name = display_name.replace('Api ', 'API ')
        display_name = display_name.replace('Hr ', 'HR ')
        display_name = display_name.replace('Crm ', 'CRM ')
        
        print(f"- name: \"{display_name}\"")
        print(f"  slug: \"{category}\"") 
        print(f"  weight: {weight}")
        print(f"  affiliate_count: {result['affiliate_count']}")
        print(f"  total_tools: {result['total_tools']}")
        print(f"  affiliate_percentage: {result['affiliate_percentage']:.1f}")
        print()
        
        weight -= 1  # Decrease weight for next category

if __name__ == "__main__":
    create_weighted_categories()