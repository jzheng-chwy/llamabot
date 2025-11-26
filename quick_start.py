#!/usr/bin/env python3
"""
Quick Start Script for Hyperlink Automation
Creates instant automation URLs for immediate use
"""

try:
    from url_generator import AutomationURLGenerator
except ImportError:
    print("Error: url_generator module not found. Make sure you're in the correct directory.")
    exit(1)

def main():
    print("🚀 CHEWY HYPERLINK AUTOMATION - QUICK START")
    print("=" * 60)
    
    generator = AutomationURLGenerator()
    
    # Generate instant automation URLs
    print("\n🎯 INSTANT AUTOMATION LINKS:")
    print("Copy and paste these URLs to execute automation instantly!\n")
    
    quick_links = [
        {
            "description": "🔍 Search Button (DEV)",
            "event": {"page_type": "search", "event": "Button Clicked", "properties": {"button_text": "search"}},
            "env": "dev"
        },
        {
            "description": "👤 Account Login (DEV)", 
            "event": {"page_type": "account", "event": "Button Clicked", "properties": {"button_text": "sign in"}},
            "env": "dev"
        },
        {
            "description": "🛒 View Cart (DEV)",
            "event": {"page_type": "cart", "event": "Page Load", "properties": {"action": "view_cart"}},
            "env": "dev"
        },
        {
            "description": "📊 Data Analysis (2 days)",
            "event": {"days_back": 2},
            "env": "dev",
            "type": "data_driven"
        }
    ]
    
    for link in quick_links:
        url = generator.create_automation_url(
            event_data=link["event"],
            environment=link["env"],
            test_type=link.get("type", "single")
        )
        print(f"{link['description']}:")
        print(f"   {url}")
        print()
    
    print("🌐 DASHBOARD URL:")
    print("   http://localhost:5000")
    print("\n📋 TO USE:")
    print("   1. Run: python hyperlink_automation.py")
    print("   2. Click any link above")
    print("   3. Or visit dashboard for full interface")
    print("\n🔗 SHARE LINKS:")
    print("   ✅ Send URLs to anyone for instant automation")
    print("   ✅ Bookmark URLs for quick access")
    print("   ✅ Embed in documentation or wikis")

if __name__ == "__main__":
    main()