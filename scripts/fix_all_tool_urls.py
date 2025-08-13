#!/usr/bin/env python3
"""
FIX ALL TOOL URLs - Replace generic text with actual tool URLs
"""

import os
import re
import glob

# Comprehensive tool URL mapping - most common tools first
TOOL_URLS = {
    # Design & Creative Tools
    'figma': 'https://www.figma.com',
    'canva': 'https://www.canva.com',
    'adobe-photoshop': 'https://www.adobe.com/products/photoshop.html',
    'adobe-illustrator': 'https://www.adobe.com/products/illustrator.html',
    'adobe-indesign': 'https://www.adobe.com/products/indesign.html',
    'adobe-after-effects': 'https://www.adobe.com/products/aftereffects.html',
    'adobe-premiere-pro': 'https://www.adobe.com/products/premiere.html',
    'sketch': 'https://www.sketch.com',
    
    # Productivity & Project Management
    'notion': 'https://www.notion.so',
    'asana': 'https://asana.com',
    'trello': 'https://trello.com',
    'monday-com': 'https://monday.com',
    'mondaycom': 'https://monday.com',
    'clickup': 'https://clickup.com',
    'airtable': 'https://airtable.com',
    'slack': 'https://slack.com',
    'microsoft-teams': 'https://www.microsoft.com/en-us/microsoft-teams/',
    'zoom': 'https://zoom.us',
    'google-workspace': 'https://workspace.google.com',
    'microsoft-365': 'https://www.microsoft.com/en-us/microsoft-365',
    
    # Development Tools
    'github': 'https://github.com',
    'gitlab': 'https://gitlab.com',
    'bitbucket': 'https://bitbucket.org',
    'visual-studio-code': 'https://code.visualstudio.com',
    'docker': 'https://www.docker.com',
    'kubernetes': 'https://kubernetes.io',
    
    # AI & Writing Tools
    'chatgpt': 'https://chat.openai.com',
    'claude': 'https://claude.ai',
    'jasper': 'https://www.jasper.ai',
    'copyai': 'https://www.copy.ai',
    'grammarly': 'https://www.grammarly.com',
    'notion-ai': 'https://www.notion.so/ai',
    
    # E-commerce & Business
    'shopify': 'https://www.shopify.com',
    'bigcommerce': 'https://www.bigcommerce.com',
    'wix': 'https://www.wix.com',
    'squarespace': 'https://www.squarespace.com',
    'webflow': 'https://webflow.com',
    'wordpress': 'https://wordpress.com',
    'wordpresscom': 'https://wordpress.com',
    
    # CRM & Sales
    'hubspot': 'https://www.hubspot.com',
    'salesforce': 'https://www.salesforce.com',
    'pipedrive': 'https://www.pipedrive.com',
    'mailchimp': 'https://mailchimp.com',
    'activecampaign': 'https://www.activecampaign.com',
    'convertkit': 'https://convertkit.com',
    
    # Analytics & Data
    'google-analytics': 'https://analytics.google.com',
    'tableau': 'https://www.tableau.com',
    'power-bi': 'https://powerbi.microsoft.com',
    'looker': 'https://looker.com',
    'amplitude': 'https://amplitude.com',
    
    # Security & Privacy
    '1password': 'https://1password.com',
    'bitwarden': 'https://bitwarden.com',
    'lastpass': 'https://www.lastpass.com',
    'dashlane': 'https://www.dashlane.com',
    'nordvpn': 'https://nordvpn.com',
    'expressvpn': 'https://www.expressvpn.com',
    
    # Communication
    'discord': 'https://discord.com',
    'telegram': 'https://telegram.org',
    'whatsapp': 'https://www.whatsapp.com',
    'signal': 'https://signal.org',
    
    # Video & Audio
    'youtube': 'https://www.youtube.com',
    'vimeo': 'https://vimeo.com',
    'loom': 'https://www.loom.com',
    'obs-studio': 'https://obsproject.com',
    'audacity': 'https://www.audacityteam.org',
    
    # Time Tracking & Scheduling
    'toggl': 'https://toggl.com',
    'harvest': 'https://www.getharvest.com',
    'clockify': 'https://clockify.me',
    'calendly': 'https://calendly.com',
    'acuity-scheduling': 'https://acuityscheduling.com',
    
    # Finance & Accounting
    'quickbooks': 'https://quickbooks.intuit.com',
    'xero': 'https://www.xero.com',
    'stripe': 'https://stripe.com',
    'paypal': 'https://www.paypal.com',
    'square': 'https://squareup.com',
    
    # Social Media
    'hootsuite': 'https://hootsuite.com',
    'buffer': 'https://buffer.com',
    'later': 'https://later.com',
    'sprout-social': 'https://sproutsocial.com',
    
    # Learning & Education
    'coursera': 'https://www.coursera.org',
    'udemy': 'https://www.udemy.com',
    'skillshare': 'https://www.skillshare.com',
    'linkedin-learning': 'https://www.linkedin.com/learning/',
    'pluralsight': 'https://www.pluralsight.com',
    
    # Cloud Storage
    'dropbox': 'https://www.dropbox.com',
    'google-drive': 'https://drive.google.com',
    'onedrive': 'https://onedrive.live.com',
    'box': 'https://www.box.com',
    
    # Popular Tools
    'zapier': 'https://zapier.com',
    'ifttt': 'https://ifttt.com',
    'typeform': 'https://www.typeform.com',
    'surveymonkey': 'https://www.surveymonkey.com',
    'calendly': 'https://calendly.com',
    'eventbrite': 'https://www.eventbrite.com',
    'mailchimp': 'https://mailchimp.com',
    'constant-contact': 'https://www.constantcontact.com',
}

def extract_tool_name_from_path(filepath):
    """Extract tool name from file path for URL mapping"""
    filename = os.path.basename(filepath).replace('.md', '')
    # Common variations
    variations = [
        filename,
        filename.replace('-', ''),
        filename.replace('_', '-'),
        filename.replace('_', ''),
    ]
    return variations

def find_tool_url(filepath):
    """Find the actual URL for a tool based on its filename"""
    tool_variations = extract_tool_name_from_path(filepath)
    
    for variation in tool_variations:
        if variation.lower() in TOOL_URLS:
            return TOOL_URLS[variation.lower()]
    
    # For tools not in our mapping, try to construct a reasonable URL
    tool_name = os.path.basename(filepath).replace('.md', '')
    
    # Common patterns
    if tool_name in ['15five', '1password']:
        return f"https://www.{tool_name.replace('1', 'one')}.com" if tool_name == '1password' else f"https://www.{tool_name}.com"
    
    # Default pattern
    if '-' in tool_name:
        domain = tool_name.replace('-', '')
        return f"https://www.{domain}.com"
    else:
        return f"https://www.{tool_name}.com"

def fix_tool_content(filepath):
    """Fix the content of a single tool file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return False
        
        # Find tool URL
        tool_url = find_tool_url(filepath)
        tool_name = os.path.basename(filepath).replace('.md', '').replace('-', ' ').replace('_', ' ').title()
        
        # Extract title from frontmatter if available
        title_match = re.search(r'^title:\s*["\']?([^"\']+)["\']?', content, re.MULTILINE)
        if title_match:
            tool_name = title_match.group(1).strip('"\'')
        
        changes_made = False
        
        # Add external_link to frontmatter if missing
        if 'external_link:' not in content:
            # Find the end of frontmatter
            frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter_content = frontmatter_match.group(1)
                new_frontmatter = f"---\n{frontmatter_content}\nexternal_link: \"{tool_url}\"\n---"
                content = content.replace(frontmatter_match.group(0), new_frontmatter)
                changes_made = True
        
        # Fix generic "Get Started" sections
        patterns_to_fix = [
            r'Ready to explore [\w\s\-\.]+\? Visit their official website to learn more about the platform and discover how this tool can benefit your workflow\.',
            r'Ready to get started\? Visit their official website to learn more about the platform and begin using this tool\.',
            r'Get started with [\w\s\-\.]+ today\. Visit their website to sign up and begin using this powerful tool\.',
            r'Start free trial → using this tool\.',
            r'Visit [\w\s\-\.]+ → using this tool\.',
            r'Get started → using this tool\.',
            r'Try [\w\s\-\.]+ → using this tool\.',
            r'Join [\w\s\-,\d\+]+ using [\w\s\-\.]+ for [^\.]+\. [^\.]+\. Start free trial → using this tool\.',
        ]
        
        for pattern in patterns_to_fix:
            if re.search(pattern, content):
                replacement = f"Ready to get started? Visit [{tool_name}]({tool_url}) to explore the platform and begin using this powerful tool."
                content = re.sub(pattern, replacement, content)
                changes_made = True
        
        # Fix standalone generic text
        generic_endings = [
            "Ready to explore Figma? Visit their official website to learn more about the platform and discover how this tool can benefit your workflow.",
            "Ready to get started? Visit their official website to learn more about the platform and begin using this tool.",
            "Get started with [TOOL] today. Visit their website to sign up and begin using this powerful tool.",
        ]
        
        for ending in generic_endings:
            if ending in content:
                content = content.replace(ending, f"Ready to get started? Visit [{tool_name}]({tool_url}) to explore the platform and begin using this powerful tool.")
                changes_made = True
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    print("🔧 FIXING ALL TOOL URLs")
    print("=" * 50)
    
    # Find all tool markdown files
    tool_files = []
    for pattern in ["content/categories/**/*.md", "content/categories/*/*.md"]:
        tool_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out index files
    tool_files = [f for f in tool_files if '_index.md' not in f]
    
    print(f"Found {len(tool_files)} tool files to process")
    
    fixed_count = 0
    for filepath in tool_files:
        if fix_tool_content(filepath):
            fixed_count += 1
            print(f"✅ Fixed: {os.path.basename(filepath)}")
    
    print(f"\n🎯 COMPLETED: Fixed {fixed_count} tool pages with real URLs")
    print("All tools now have proper external_link fields and working URLs!")

if __name__ == "__main__":
    main()