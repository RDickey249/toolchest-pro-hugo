#!/usr/bin/env python3
"""
Audit Summary Generator - Creates executive summary of all audit findings
"""

import json
from pathlib import Path

def generate_executive_summary():
    """Generate executive summary from all audit data"""
    
    # Load all report files
    reports = {}
    
    try:
        with open('comprehensive_audit_report.json', 'r') as f:
            reports['main'] = json.load(f)
    except FileNotFoundError:
        print("❌ Main audit report not found")
        return
    
    try:
        with open('url_corrections.json', 'r') as f:
            reports['corrections'] = json.load(f)
    except FileNotFoundError:
        reports['corrections'] = []
    
    try:
        with open('duplicate_analysis.json', 'r') as f:
            reports['duplicates'] = json.load(f)
    except FileNotFoundError:
        reports['duplicates'] = {}
    
    main_report = reports['main']
    
    print("🎯 TOOLCHEST PRO HUGO - AUDIT EXECUTIVE SUMMARY")
    print("="*70)
    
    # High-level metrics
    print(f"📊 SCOPE: {main_report['summary']['total_tools']} tools across {main_report['summary']['total_categories']} categories")
    print(f"🔗 URL HEALTH: {main_report['summary']['total_broken_urls']} broken ({main_report['summary']['broken_percentage']}%)")
    print(f"👥 DUPLICATES: {main_report['summary']['total_duplicates']} instances")
    print(f"🤖 AUTO-GENERATED: {main_report['summary']['url_patterns_detected']} pattern-based URLs")
    
    # Calculate production readiness score
    total_issues = (
        main_report['summary']['total_broken_urls'] + 
        len([d for d in main_report.get('duplicate_analysis', []) if d.get('type') == 'title_similarity'])
    )
    
    readiness_score = max(0, 100 - (total_issues / main_report['summary']['total_tools'] * 100))
    
    print(f"\n🚀 PRODUCTION READINESS: {readiness_score:.1f}%")
    
    if readiness_score >= 95:
        print("   ✅ READY TO LAUNCH")
    elif readiness_score >= 85:
        print("   ⚠️  READY WITH MINOR FIXES")
    elif readiness_score >= 75:
        print("   🔧 NEEDS TARGETED FIXES")
    else:
        print("   ❌ SIGNIFICANT WORK NEEDED")
    
    # Critical issues
    print("\n🚨 CRITICAL ISSUES (Launch Blockers)")
    print("-" * 40)
    
    critical_count = 0
    connection_errors = [url for url in main_report['top_broken_links'] if url['status'] < 0]
    
    if connection_errors:
        print(f"🔗 {len(connection_errors)} URLs with complete connection failures:")
        for error in connection_errors[:5]:  # Top 5
            print(f"   • {error['tool']} ({error['category']}): {error['url']}")
            critical_count += 1
    
    # Duplicate issues
    testing_duplicates = [d for d in reports.get('duplicates', {}).get('priority_duplicates', []) 
                         if 'testing' in str(d.get('categories', [])).lower()]
    
    if testing_duplicates:
        print(f"👥 {len(testing_duplicates)} high-priority duplicate consolidations needed:")
        for dup in testing_duplicates[:3]:  # Top 3
            print(f"   • {dup['key']} across {len(dup['categories'])} categories")
            critical_count += 1
    
    if critical_count == 0:
        print("   ✅ No critical launch-blocking issues found!")
    
    # Medium priority issues
    print(f"\n⚠️  MEDIUM PRIORITY ISSUES")
    print("-" * 40)
    
    http_errors = [url for url in main_report['top_broken_links'] if url['status'] >= 400]
    print(f"🌐 {len(http_errors)} URLs with HTTP errors (may work for users)")
    
    pattern_urls = main_report['summary']['url_patterns_detected']
    print(f"🤖 {pattern_urls} auto-generated URLs need spot-checking")
    
    # Success metrics
    print(f"\n✅ SUCCESS METRICS")
    print("-" * 40)
    
    working_percentage = 100 - main_report['summary']['broken_percentage']
    print(f"🔗 {working_percentage:.1f}% of URLs working correctly")
    print(f"📁 {main_report['summary']['total_categories']} well-organized categories")
    print(f"📊 {main_report['summary']['total_tools']} tools comprehensively catalogued")
    
    # Quick wins available
    if reports.get('corrections'):
        quick_fixes = len([c for c in reports['corrections'] if c.get('working_urls')])
        print(f"🛠️  {quick_fixes} quick URL fixes available")
    
    # Action plan summary
    print(f"\n📋 RECOMMENDED ACTION PLAN")
    print("-" * 40)
    
    print("Phase 1 (Critical - 4-6 hours):")
    if connection_errors:
        print(f"   • Fix {len(connection_errors)} broken URLs with verified corrections")
    if testing_duplicates:
        print(f"   • Consolidate {len(testing_duplicates)} duplicate testing tools")
    
    print("Phase 2 (Quality - 1-2 days):")
    print(f"   • Review {len(http_errors)} HTTP error URLs")
    print(f"   • Spot-check sample of {pattern_urls} auto-generated URLs")
    
    print("Phase 3 (Ongoing):")
    print("   • Implement automated URL monitoring")
    print("   • Set up duplicate prevention workflow")
    
    # Final recommendation
    print(f"\n🎯 FINAL RECOMMENDATION")
    print("-" * 40)
    
    if critical_count <= 5:
        print("✅ PROCEED WITH LAUNCH after Phase 1 fixes")
        print(f"   Estimated fix time: {critical_count * 30} minutes per critical issue")
    else:
        print("⚠️  DELAY LAUNCH until critical issues resolved")
        print(f"   Estimated fix time: {critical_count * 45} minutes")
    
    print(f"\n📄 Detailed reports available:")
    print("   • COMPREHENSIVE_AUDIT_REPORT.md (full analysis)")
    print("   • comprehensive_audit_report.json (raw data)")
    print("   • url_corrections.json (verified URL fixes)")
    print("   • duplicate_analysis.json (consolidation plan)")

if __name__ == "__main__":
    generate_executive_summary()