#!/usr/bin/env python3
"""
URL Validator Script - Validates specific broken URLs and suggests corrections
"""

import requests
import json
from typing import Dict, List, Tuple

def validate_single_url(url: str, timeout: int = 10) -> Tuple[int, str]:
    """Validate a single URL and return status code and message"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        response = requests.head(url, timeout=timeout, allow_redirects=True, 
                               headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        return response.status_code, f"HTTP {response.status_code}"
        
    except requests.exceptions.Timeout:
        return -1, "Timeout"
    except requests.exceptions.ConnectionError:
        return -2, "Connection Error"
    except requests.exceptions.RequestException as e:
        return -3, f"Request Error: {str(e)[:50]}"
    except Exception as e:
        return -4, f"Unknown Error: {str(e)[:50]}"

def suggest_url_corrections(broken_urls: List[Dict]) -> List[Dict]:
    """Suggest URL corrections for broken URLs"""
    corrections = []
    
    # Known URL corrections based on common patterns
    url_fixes = {
        'studygpt.ai': 'studygpt.ai',  # This might be the correct URL but down
        'projecteuler.com': 'projecteuler.net',  # Project Euler is at .net
        'www.mutable.ai': 'mutable.ai',  # Remove www
        'keepass.com': 'keepass.info',  # KeePass official site is .info
        'studygpt': ['studygpt.ai', 'study-gpt.com', 'studygpt.com'],
        'project-euler': ['projecteuler.net'],
        'mutable-ai': ['mutable.ai', 'www.mutable.ai'],
        'keepass': ['keepass.info', 'keepass.sourceforge.io']
    }
    
    for broken in broken_urls:
        tool_name = broken['tool']
        original_url = broken['url']
        
        suggested_urls = []
        
        # Check if we have specific known fixes
        if tool_name in url_fixes:
            suggested_urls = url_fixes[tool_name] if isinstance(url_fixes[tool_name], list) else [url_fixes[tool_name]]
        else:
            # Generate common alternatives
            base_name = tool_name.replace('-', '').replace('_', '')
            suggested_urls = [
                f"https://{base_name}.com",
                f"https://www.{base_name}.com",
                f"https://{base_name}.io",
                f"https://{base_name}.ai",
                f"https://{base_name}.app"
            ]
        
        # Test suggested URLs
        working_urls = []
        for suggested_url in suggested_urls:
            status, message = validate_single_url(suggested_url)
            if status == 200:
                working_urls.append(suggested_url)
        
        correction = {
            'tool': tool_name,
            'original_url': original_url,
            'original_status': broken['status'],
            'original_message': broken['message'],
            'suggested_urls': suggested_urls,
            'working_urls': working_urls,
            'file_path': broken['file_path']
        }
        
        corrections.append(correction)
        print(f"✓ Checked {tool_name}: {len(working_urls)} working alternatives found")
    
    return corrections

def main():
    # Load the audit report
    with open('comprehensive_audit_report.json', 'r') as f:
        report = json.load(f)
    
    print("🔍 Validating broken URLs and suggesting corrections...")
    
    # Get broken URLs with connection errors (priority)
    broken_connection_urls = [url for url in report['top_broken_links'] if url['status'] < 0]
    
    print(f"Found {len(broken_connection_urls)} URLs with connection errors")
    
    corrections = suggest_url_corrections(broken_connection_urls)
    
    # Save corrections
    with open('url_corrections.json', 'w') as f:
        json.dump(corrections, f, indent=2)
    
    print("\n" + "="*60)
    print("🎯 URL CORRECTION RESULTS")
    print("="*60)
    
    for correction in corrections:
        print(f"\n🔧 {correction['tool'].upper()}")
        print(f"   Original: {correction['original_url']} ({correction['original_message']})")
        if correction['working_urls']:
            print(f"   ✅ Working: {', '.join(correction['working_urls'])}")
        else:
            print(f"   ❌ No working alternatives found")
            print(f"   💡 Tried: {', '.join(correction['suggested_urls'])}")
    
    print(f"\n📄 Detailed corrections saved to url_corrections.json")

if __name__ == "__main__":
    main()