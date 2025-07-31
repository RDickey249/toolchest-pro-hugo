#!/usr/bin/env python3
"""
Duplicate Tool Analyzer - Analyzes duplicate tools and provides consolidation recommendations
"""

import json
from collections import defaultdict
from pathlib import Path

def analyze_duplicates(report_file: str = 'comprehensive_audit_report.json'):
    """Analyze duplicate tools and provide detailed recommendations"""
    
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    duplicates = report['duplicate_analysis']
    
    print("🔍 DUPLICATE ANALYSIS REPORT")
    print("="*60)
    
    # Categorize duplicates by type
    duplicate_stats = defaultdict(int)
    cross_category_duplicates = []
    same_category_duplicates = []
    
    for dup in duplicates:
        duplicate_stats[dup['type']] += 1
        
        # Check if duplicates are across categories
        categories = set(tool['category'] for tool in dup['tools'])
        
        if len(categories) > 1:
            cross_category_duplicates.append({
                'key': dup['key'],
                'type': dup['type'],
                'tools': dup['tools'],
                'categories': list(categories)
            })
        else:
            same_category_duplicates.append({
                'key': dup['key'], 
                'type': dup['type'],
                'tools': dup['tools'],
                'category': list(categories)[0]
            })
    
    print(f"📊 Total duplicate groups: {len(duplicates)}")
    for dup_type, count in duplicate_stats.items():
        print(f"   - {dup_type}: {count}")
    
    print(f"\n🔄 Cross-category duplicates: {len(cross_category_duplicates)}")
    print(f"📁 Same-category duplicates: {len(same_category_duplicates)}")
    
    # Analyze high-priority cross-category duplicates
    print("\n" + "="*60)
    print("🚨 HIGH PRIORITY: CROSS-CATEGORY DUPLICATES")
    print("="*60)
    
    priority_duplicates = []
    
    for dup in cross_category_duplicates[:20]:  # Top 20
        # Calculate priority based on category popularity
        popular_categories = ['ai-tools-assistants', 'productivity-task-management', 
                            'design-creative-tools', 'development-technical-tools']
        
        priority = 0
        for tool in dup['tools']:
            if tool['category'] in popular_categories:
                priority += 1
        
        recommendation = analyze_duplicate_recommendation(dup)
        
        priority_duplicates.append({
            **dup,
            'priority_score': priority,
            'recommendation': recommendation
        })
        
        print(f"\n🔧 {dup['key'].upper()}")
        print(f"   Type: {dup['type']}")
        print(f"   Categories: {', '.join(dup['categories'])}")
        print(f"   Tools:")
        for tool in dup['tools']:
            print(f"      - {tool['name']} ({tool['category']})")
        print(f"   💡 Recommendation: {recommendation}")
    
    # Analyze tool consolidation opportunities
    print("\n" + "="*60)
    print("🔗 CONSOLIDATION OPPORTUNITIES")
    print("="*60)
    
    consolidation_plan = create_consolidation_plan(cross_category_duplicates)
    
    for plan in consolidation_plan[:10]:  # Top 10
        print(f"\n📋 {plan['primary_tool']} consolidation:")
        print(f"   Keep: {plan['keep_file']}")
        print(f"   Merge from:")
        for merge_file in plan['merge_files']:
            print(f"      - {merge_file}")
        if plan['redirect_needed']:
            print(f"   🔀 Redirects needed: {len(plan['redirect_files'])}")
    
    # Save detailed analysis
    analysis_result = {
        'summary': {
            'total_duplicates': len(duplicates),
            'cross_category': len(cross_category_duplicates),
            'same_category': len(same_category_duplicates),
            'duplicate_types': dict(duplicate_stats)
        },
        'priority_duplicates': priority_duplicates,
        'consolidation_plan': consolidation_plan
    }
    
    with open('duplicate_analysis.json', 'w') as f:
        json.dump(analysis_result, f, indent=2)
    
    print(f"\n📄 Detailed analysis saved to duplicate_analysis.json")
    
    return analysis_result

def analyze_duplicate_recommendation(dup: dict) -> str:
    """Analyze a duplicate group and provide specific recommendation"""
    tools = dup['tools']
    categories = dup['categories']
    
    # Check if tools are exactly the same vs variations
    if dup['type'] == 'title_similarity':
        if len(set(tool['title'] for tool in tools)) == 1:
            return "CONSOLIDATE - Exact duplicate titles, merge into one category"
        else:
            return "DIFFERENTIATE - Similar names but may be different tools, verify uniqueness"
    
    elif dup['type'] == 'url_similarity':
        return "CONSOLIDATE - Same URL indicates same tool, keep only one instance"
    
    elif dup['type'] == 'content_similarity':
        return "CONSOLIDATE - Identical content, merge into primary category"
    
    return "REVIEW - Manual review needed to determine best action"

def create_consolidation_plan(cross_category_duplicates: list) -> list:
    """Create a consolidation plan for duplicate tools"""
    consolidation_plan = []
    
    for dup in cross_category_duplicates:
        tools = dup['tools']
        
        # Determine primary tool (usually in most popular category)
        category_priority = {
            'ai-tools-assistants': 1,
            'productivity-task-management': 2, 
            'design-creative-tools': 3,
            'development-technical-tools': 4
        }
        
        # Sort tools by category priority
        sorted_tools = sorted(tools, key=lambda x: category_priority.get(x['category'], 999))
        primary_tool = sorted_tools[0]
        other_tools = sorted_tools[1:]
        
        plan = {
            'primary_tool': primary_tool['name'],
            'keep_file': primary_tool['file_path'],
            'merge_files': [tool['file_path'] for tool in other_tools],
            'redirect_needed': len(other_tools) > 0,
            'redirect_files': [tool['file_path'] for tool in other_tools],
            'categories_affected': dup['categories']
        }
        
        consolidation_plan.append(plan)
    
    return consolidation_plan

if __name__ == "__main__":
    analyze_duplicates()