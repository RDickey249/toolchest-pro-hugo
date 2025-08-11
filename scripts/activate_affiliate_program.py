#!/usr/bin/env python3
"""
Affiliate Program Activation Script
===================================

This script prepares your ToolChest site to generate revenue through affiliate partnerships.
Run this when you get approved for affiliate programs to instantly activate money-making links.

Usage:
  python3 scripts/activate_affiliate_program.py --tool shopify --affiliate-url "https://shopify.com/ref=YOUR_ID"
  python3 scripts/activate_affiliate_program.py --batch-activate affiliate_urls.txt
  python3 scripts/activate_affiliate_program.py --status (shows current affiliate status)
"""

import os
import sys
import yaml
import argparse
from pathlib import Path

class AffiliateActivator:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.data_dir = self.root_dir / "data"
        self.content_dir = self.root_dir / "content"
        
    def load_affiliate_config(self):
        """Load current affiliate configuration"""
        config_file = self.data_dir / "affiliate_links.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_affiliate_config(self, config):
        """Save affiliate configuration"""
        config_file = self.data_dir / "affiliate_links.yaml" 
        with open(config_file, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=True)
            
    def activate_tool_affiliate(self, tool_slug, affiliate_url, commission_rate="", custom_cta=""):
        """Activate affiliate link for a specific tool"""
        config = self.load_affiliate_config()
        
        if tool_slug not in config:
            print(f"⚠️  Tool '{tool_slug}' not found in affiliate config")
            return False
            
        # Update with real affiliate URL
        config[tool_slug]['url'] = affiliate_url
        config[tool_slug]['status'] = 'active'
        config[tool_slug]['activated_date'] = str(datetime.now().date())
        
        if commission_rate:
            config[tool_slug]['commission'] = commission_rate
        if custom_cta:
            config[tool_slug]['cta'] = custom_cta
            
        self.save_affiliate_config(config)
        
        # Update tool content file
        self.update_tool_content(tool_slug, affiliate_url, config[tool_slug]['cta'])
        
        print(f"✅ Activated affiliate for {tool_slug}")
        print(f"   URL: {affiliate_url}")
        print(f"   Commission: {config[tool_slug].get('commission', 'Not set')}")
        return True
        
    def update_tool_content(self, tool_slug, affiliate_url, cta):
        """Update tool content file with affiliate data"""
        # Find tool content file
        tool_files = list(self.content_dir.rglob(f"{tool_slug}.md"))
        
        if not tool_files:
            print(f"⚠️  Could not find content file for {tool_slug}")
            return False
            
        tool_file = tool_files[0]
        
        # Read current content
        with open(tool_file, 'r') as f:
            content = f.read()
            
        # Update frontmatter
        lines = content.split('\n')
        in_frontmatter = False
        updated_lines = []
        affiliate_url_set = False
        affiliate_cta_set = False
        
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                updated_lines.append(line)
                continue
                
            if in_frontmatter:
                if line.startswith('affiliate_url:'):
                    updated_lines.append(f'affiliate_url: "{affiliate_url}"')
                    affiliate_url_set = True
                elif line.startswith('affiliate_cta:'):
                    updated_lines.append(f'affiliate_cta: "{cta}"')
                    affiliate_cta_set = True
                elif line.startswith('affiliate:'):
                    updated_lines.append('affiliate: true')
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
                
        # Add missing affiliate fields if needed
        if in_frontmatter and not affiliate_url_set:
            updated_lines.insert(-1, f'affiliate_url: "{affiliate_url}"')
        if in_frontmatter and not affiliate_cta_set:
            updated_lines.insert(-1, f'affiliate_cta: "{cta}"')
            
        # Write updated content
        with open(tool_file, 'w') as f:
            f.write('\n'.join(updated_lines))
            
        return True
    
    def batch_activate(self, urls_file):
        """Activate multiple affiliate links from a file"""
        if not os.path.exists(urls_file):
            print(f"❌ File {urls_file} not found")
            return
            
        with open(urls_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) >= 2:
                        tool_slug = parts[0].strip()
                        affiliate_url = parts[1].strip()
                        commission = parts[2].strip() if len(parts) > 2 else ""
                        self.activate_tool_affiliate(tool_slug, affiliate_url, commission)
    
    def show_status(self):
        """Show current affiliate program status"""
        config = self.load_affiliate_config()
        
        print("🚀 ToolChest Affiliate Program Status")
        print("=" * 50)
        
        active_count = 0
        pending_count = 0
        total_commission_potential = 0
        
        for tool, data in config.items():
            status = data.get('status', 'pending')
            commission = data.get('commission', '0%')
            
            if status == 'active':
                active_count += 1
                print(f"✅ {tool.ljust(20)} | {status.ljust(8)} | {commission}")
            else:
                pending_count += 1
                print(f"⏳ {tool.ljust(20)} | {status.ljust(8)} | {commission}")
                
        print("=" * 50)
        print(f"📊 Summary: {active_count} active, {pending_count} pending")
        print(f"💰 Ready to earn from {len(config)} affiliate partnerships!")
        
        if pending_count > 0:
            print("\n🎯 Next Steps:")
            print("1. Get approved for affiliate programs")
            print("2. Run activation script with real URLs")
            print("3. Start earning commissions!")

def main():
    parser = argparse.ArgumentParser(description='Activate ToolChest affiliate program')
    parser.add_argument('--tool', help='Tool slug to activate')
    parser.add_argument('--affiliate-url', help='Affiliate URL')
    parser.add_argument('--commission', help='Commission rate', default='')
    parser.add_argument('--cta', help='Custom call-to-action', default='')
    parser.add_argument('--batch-activate', help='File with tool,url,commission lines')
    parser.add_argument('--status', action='store_true', help='Show affiliate status')
    
    args = parser.parse_args()
    
    activator = AffiliateActivator()
    
    if args.status:
        activator.show_status()
    elif args.tool and args.affiliate_url:
        activator.activate_tool_affiliate(args.tool, args.affiliate_url, args.commission, args.cta)
    elif args.batch_activate:
        activator.batch_activate(args.batch_activate)
    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("  python3 scripts/activate_affiliate_program.py --status")

if __name__ == "__main__":
    import datetime
    main()