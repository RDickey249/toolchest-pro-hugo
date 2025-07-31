#!/usr/bin/env python3
"""
Comprehensive Tool Audit Script for Toolchest Pro Hugo
Performs systematic analysis of all tool pages for URL validation, duplicates, and quality issues.
"""

import os
import re
import requests
import yaml
import json
import csv
import time
from pathlib import Path
from collections import defaultdict, Counter
from urllib.parse import urlparse, urljoin
import concurrent.futures
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional
import hashlib

@dataclass
class ToolInfo:
    """Data class to store tool information"""
    name: str
    title: str
    category: str
    subcategory: str
    file_path: str
    url: str
    description: str
    tags: List[str]
    features: List[str]
    pricing_model: str
    content_hash: str

class ToolAuditor:
    def __init__(self, content_dir: str):
        self.content_dir = Path(content_dir)
        self.tools: List[ToolInfo] = []
        self.url_status_cache = {}
        self.broken_urls = []
        self.duplicate_tools = []
        self.url_patterns = defaultdict(list)
        self.category_stats = defaultdict(lambda: {
            'total_tools': 0,
            'broken_urls': 0,
            'suspicious_urls': 0,
            'missing_descriptions': 0
        })
        
    def parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Parse YAML frontmatter from markdown content"""
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    return frontmatter or {}, body
            except yaml.YAMLError as e:
                print(f"YAML parse error: {e}")
                return {}, content
        return {}, content
    
    def extract_url_from_content(self, content: str, tool_name: str) -> str:
        """Extract the main URL from markdown content"""
        # Look for "Visit [toolname](url)" pattern first
        visit_pattern = rf'Visit \[([^\]]+)\]\(([^)]+)\)'
        match = re.search(visit_pattern, content, re.IGNORECASE)
        if match:
            return match.group(2)
        
        # Look for any URL in markdown link format
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        if matches:
            # Prefer URLs that contain the tool name or are likely to be the main site
            tool_name_clean = tool_name.lower().replace('-', '').replace('_', '')
            for text, url in matches:
                if tool_name_clean in url.lower() or url.startswith('https://'):
                    return url
            # Return first URL if no name match
            return matches[0][1]
        
        # Look for plain URLs
        url_pattern = r'https?://[^\s)]+(?:\.[^\s)]+)+'
        match = re.search(url_pattern, content)
        if match:
            return match.group(0)
        
        return ""

    def extract_tools_from_directory(self):
        """Extract all tool information from markdown files"""
        print("🔍 Scanning tool files...")
        
        for md_file in self.content_dir.rglob("*.md"):
            if md_file.name == "_index.md":
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, body = self.parse_frontmatter(content)
                
                # Extract path components for categorization
                rel_path = md_file.relative_to(self.content_dir)
                path_parts = rel_path.parts
                
                if len(path_parts) >= 3:  # categories/main-cat/sub-cat/tool.md
                    category = path_parts[1]
                    subcategory = path_parts[2] if len(path_parts) > 3 else ""
                else:
                    category = "uncategorized"
                    subcategory = ""
                
                # Extract URL from frontmatter or content
                url = frontmatter.get('url', '') or self.extract_url_from_content(content, md_file.stem)
                
                # Create content hash for duplicate detection
                content_for_hash = f"{frontmatter.get('title', '')}{frontmatter.get('description', '')}{url}"
                content_hash = hashlib.md5(content_for_hash.encode()).hexdigest()
                
                tool = ToolInfo(
                    name=md_file.stem,
                    title=frontmatter.get('title', md_file.stem.replace('-', ' ').title()),
                    category=category,
                    subcategory=subcategory,
                    file_path=str(md_file),
                    url=url,
                    description=frontmatter.get('description', '') or self.extract_description_from_content(body),
                    tags=frontmatter.get('tags', []),
                    features=frontmatter.get('features', []),
                    pricing_model=frontmatter.get('pricing_model', ''),
                    content_hash=content_hash
                )
                
                self.tools.append(tool)
                self.category_stats[category]['total_tools'] += 1
                
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
        
        print(f"📊 Found {len(self.tools)} tools across {len(self.category_stats)} categories")
    
    def extract_description_from_content(self, content: str) -> str:
        """Extract description from the main content if not in frontmatter"""
        lines = content.strip().split('\n')
        # Look for the first substantial paragraph
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 50:
                return line[:200] + "..." if len(line) > 200 else line
        return ""
    
    def validate_url(self, url: str, timeout: int = 10) -> Tuple[int, str]:
        """Validate a single URL and return status code and message"""
        if not url or url.strip() == '':
            return 0, "Empty URL"
        
        if url in self.url_status_cache:
            return self.url_status_cache[url]
        
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            status = response.status_code
            message = "OK" if status == 200 else f"HTTP {status}"
            
        except requests.exceptions.Timeout:
            status, message = -1, "Timeout"
        except requests.exceptions.ConnectionError:
            status, message = -2, "Connection Error"
        except requests.exceptions.RequestException as e:
            status, message = -3, f"Request Error: {str(e)[:50]}"
        except Exception as e:
            status, message = -4, f"Unknown Error: {str(e)[:50]}"
        
        self.url_status_cache[url] = (status, message)
        return status, message
    
    def analyze_url_patterns(self):
        """Analyze URL patterns to identify auto-generated URLs"""
        print("🔗 Analyzing URL patterns...")
        
        for tool in self.tools:
            if tool.url:
                # Extract domain pattern
                try:
                    parsed = urlparse(tool.url if tool.url.startswith(('http://', 'https://')) else f"https://{tool.url}")
                    domain = parsed.netloc.lower()
                    
                    # Check for simple pattern matching (toolname.com, toolname.io, etc.)
                    tool_name_normalized = tool.name.lower().replace('-', '').replace('_', '')
                    domain_base = domain.split('.')[0] if '.' in domain else domain
                    
                    if tool_name_normalized == domain_base:
                        self.url_patterns['simple_pattern'].append({
                            'tool': tool.name,
                            'url': tool.url,
                            'pattern': f"{tool_name_normalized}.{domain.split('.')[-1] if '.' in domain else 'com'}"
                        })
                    
                except Exception:
                    pass
    
    def validate_urls_batch(self, sample_size: int = 100):
        """Validate URLs in batches with threading"""
        print(f"🌐 Validating URLs (sample size: {sample_size})...")
        
        # Sample URLs for validation (prioritize different categories)
        urls_to_check = []
        category_samples = defaultdict(list)
        
        for tool in self.tools:
            if tool.url:
                category_samples[tool.category].append(tool)
        
        # Take samples from each category
        for category, tools in category_samples.items():
            sample_count = min(len(tools), max(1, sample_size // len(category_samples)))
            urls_to_check.extend(tools[:sample_count])
        
        print(f"Checking {len(urls_to_check)} URLs across {len(category_samples)} categories...")
        
        def check_url(tool):
            status, message = self.validate_url(tool.url)
            return tool, status, message
        
        # Use ThreadPoolExecutor for concurrent URL checking
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_tool = {executor.submit(check_url, tool): tool for tool in urls_to_check}
            
            for future in concurrent.futures.as_completed(future_to_tool):
                try:
                    tool, status, message = future.result()
                    
                    if status != 200:
                        self.broken_urls.append({
                            'tool': tool.name,
                            'title': tool.title,
                            'category': tool.category,
                            'url': tool.url,
                            'status': status,
                            'message': message,
                            'file_path': tool.file_path
                        })
                        
                        if status < 0:  # Connection issues
                            self.category_stats[tool.category]['broken_urls'] += 1
                        else:
                            self.category_stats[tool.category]['suspicious_urls'] += 1
                    
                    # Small delay to be respectful to servers
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error checking URL: {e}")
    
    def find_duplicates(self):
        """Find duplicate tools based on various criteria"""
        print("🔍 Detecting duplicates...")
        
        # Group by title similarity
        title_groups = defaultdict(list)
        for tool in self.tools:
            # Normalize title for comparison
            norm_title = re.sub(r'[^a-zA-Z0-9]', '', tool.title.lower())
            title_groups[norm_title].append(tool)
        
        # Group by URL similarity
        url_groups = defaultdict(list)
        for tool in self.tools:
            if tool.url:
                # Normalize URL for comparison
                norm_url = tool.url.lower().replace('www.', '').replace('http://', '').replace('https://', '')
                url_groups[norm_url].append(tool)
        
        # Group by content hash
        hash_groups = defaultdict(list)
        for tool in self.tools:
            hash_groups[tool.content_hash].append(tool)
        
        # Find groups with multiple tools
        for norm_title, tools in title_groups.items():
            if len(tools) > 1:
                self.duplicate_tools.append({
                    'type': 'title_similarity',
                    'key': norm_title,
                    'tools': [{'name': t.name, 'title': t.title, 'category': t.category, 'file_path': t.file_path} for t in tools]
                })
        
        for norm_url, tools in url_groups.items():
            if len(tools) > 1:
                self.duplicate_tools.append({
                    'type': 'url_similarity',
                    'key': norm_url,
                    'tools': [{'name': t.name, 'title': t.title, 'category': t.category, 'url': t.url, 'file_path': t.file_path} for t in tools]
                })
        
        for content_hash, tools in hash_groups.items():
            if len(tools) > 1:
                self.duplicate_tools.append({
                    'type': 'content_similarity',
                    'key': content_hash,
                    'tools': [{'name': t.name, 'title': t.title, 'category': t.category, 'file_path': t.file_path} for t in tools]
                })
    
    def analyze_quality_issues(self):
        """Analyze content quality issues"""
        print("🔍 Analyzing content quality...")
        
        for tool in self.tools:
            # Check for missing descriptions
            if not tool.description or len(tool.description.strip()) < 10:
                self.category_stats[tool.category]['missing_descriptions'] += 1
    
    def generate_priority_fixes(self) -> List[Dict]:
        """Generate prioritized list of fixes"""
        priority_fixes = []
        
        # Sort broken URLs by category popularity (estimated)
        popular_categories = ['ai-tools-assistants', 'productivity-task-management', 'design-creative-tools', 'development-technical-tools']
        
        for broken in self.broken_urls:
            priority = 1  # default
            if broken['category'] in popular_categories:
                priority = 0  # high priority
            elif broken['status'] < 0:  # connection errors are higher priority
                priority = 1
            else:
                priority = 2  # low priority
            
            # Try to suggest URL fix
            suggested_url = self.suggest_url_fix(broken['tool'], broken['url'])
            
            priority_fixes.append({
                'priority': priority,
                'type': 'broken_url',
                'tool': broken['tool'],
                'category': broken['category'],
                'issue': f"{broken['message']} - {broken['url']}",
                'suggested_fix': suggested_url,
                'file_path': broken['file_path']
            })
        
        # Add duplicate consolidation tasks
        for dup in self.duplicate_tools:
            if len(dup['tools']) > 1:
                priority_fixes.append({
                    'priority': 1,
                    'type': 'duplicate',
                    'issue': f"Duplicate tools detected: {dup['type']}",
                    'tools': dup['tools'],
                    'suggested_fix': 'Consolidate or differentiate these tools'
                })
        
        return sorted(priority_fixes, key=lambda x: x['priority'])
    
    def suggest_url_fix(self, tool_name: str, broken_url: str) -> str:
        """Suggest a corrected URL based on common patterns"""
        # Common domain patterns for tools
        common_patterns = [
            f"https://www.{tool_name.replace('-', '')}.com",
            f"https://{tool_name.replace('-', '')}.com",
            f"https://www.{tool_name.replace('-', '')}.io",
            f"https://{tool_name.replace('-', '')}.io",
            f"https://www.{tool_name.replace('-', '')}.ai",
            f"https://{tool_name.replace('-', '')}.ai"
        ]
        
        # Return the most likely pattern (could be enhanced with actual validation)
        return common_patterns[0]
    
    def generate_report(self) -> Dict:
        """Generate comprehensive audit report"""
        print("📋 Generating comprehensive report...")
        
        total_broken = len(self.broken_urls)
        total_tools = len(self.tools)
        broken_percentage = (total_broken / total_tools * 100) if total_tools > 0 else 0
        
        # Category breakdown
        category_breakdown = []
        for category, stats in self.category_stats.items():
            if stats['total_tools'] > 0:
                category_breakdown.append({
                    'category': category,
                    'total_tools': stats['total_tools'],
                    'broken_urls': stats['broken_urls'],
                    'suspicious_urls': stats['suspicious_urls'],
                    'missing_descriptions': stats['missing_descriptions'],
                    'broken_percentage': (stats['broken_urls'] / stats['total_tools'] * 100)
                })
        
        # Sort by broken percentage (highest first)
        category_breakdown.sort(key=lambda x: x['broken_percentage'], reverse=True)
        
        # Top broken links
        top_broken = sorted(self.broken_urls, 
                          key=lambda x: (0 if x['category'] in ['ai-tools-assistants', 'productivity-task-management'] else 1, x['status']))
        
        report = {
            'summary': {
                'total_tools': len(self.tools),
                'total_categories': len(self.category_stats),
                'total_broken_urls': total_broken,
                'broken_percentage': round(broken_percentage, 2),
                'total_duplicates': len(self.duplicate_tools),
                'url_patterns_detected': len(self.url_patterns['simple_pattern'])
            },
            'category_breakdown': category_breakdown[:10],  # Top 10 worst categories
            'priority_fixes': self.generate_priority_fixes()[:20],  # Top 20 priority fixes
            'duplicate_analysis': self.duplicate_tools[:10],  # Top 10 duplicate groups
            'url_pattern_analysis': {
                'simple_patterns': self.url_patterns['simple_pattern'][:20]
            },
            'top_broken_links': top_broken[:20]
        }
        
        return report
    
    def save_report(self, report: Dict, filename: str = "comprehensive_audit_report.json"):
        """Save the audit report to file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📄 Report saved to {filename}")
    
    def run_full_audit(self, url_sample_size: int = 100) -> Dict:
        """Run the complete audit process"""
        print("🚀 Starting comprehensive tool audit...")
        
        # Phase 1: Extract all tools
        self.extract_tools_from_directory()
        
        # Phase 2: Analyze URL patterns
        self.analyze_url_patterns()
        
        # Phase 3: Validate URLs (sample)
        self.validate_urls_batch(url_sample_size)
        
        # Phase 4: Find duplicates
        self.find_duplicates()
        
        # Phase 5: Analyze quality issues
        self.analyze_quality_issues()
        
        # Phase 6: Generate report
        report = self.generate_report()
        
        # Save report
        self.save_report(report)
        
        return report

def main():
    content_dir = "/home/yan/toolchest-pro-hugo/content/categories"
    
    auditor = ToolAuditor(content_dir)
    report = auditor.run_full_audit(url_sample_size=100)
    
    # Print summary
    print("\n" + "="*60)
    print("🎯 COMPREHENSIVE AUDIT SUMMARY")
    print("="*60)
    print(f"📊 Total Tools: {report['summary']['total_tools']}")
    print(f"📁 Categories: {report['summary']['total_categories']}")
    print(f"❌ Broken URLs: {report['summary']['total_broken_urls']} ({report['summary']['broken_percentage']}%)")
    print(f"👥 Duplicates Found: {report['summary']['total_duplicates']}")
    print(f"🔗 Auto-generated URL Patterns: {report['summary']['url_patterns_detected']}")
    
    print("\n🏆 TOP PRIORITY CATEGORIES FOR FIXES:")
    for i, cat in enumerate(report['category_breakdown'][:5], 1):
        print(f"{i}. {cat['category']}: {cat['broken_urls']} broken ({cat['broken_percentage']:.1f}%)")
    
    print(f"\n📄 Detailed report saved to comprehensive_audit_report.json")

if __name__ == "__main__":
    main()