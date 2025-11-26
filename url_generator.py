#!/usr/bin/env python3
"""
URL Generator Utility
Creates shareable automation URLs for any event configuration
"""

import json
import base64
import urllib.parse
from typing import Dict, Any, List
from datetime import datetime

class AutomationURLGenerator:
    """Generates clickable URLs for automation tasks"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        
    def create_automation_url(self, 
                            event_data: Dict[str, Any],
                            environment: str = "dev",
                            test_type: str = "single") -> str:
        """
        Create a single automation URL
        
        Args:
            event_data: The JSON event to execute
            environment: Target environment (dev/qat/prod)  
            test_type: Type of automation (single/data_driven/analysis)
            
        Returns:
            Complete automation URL
        """
        # Encode event data
        encoded_data = base64.b64encode(
            json.dumps(event_data).encode('utf-8')
        ).decode('utf-8')
        
        # Build query parameters
        params = {
            'data': encoded_data,
            'env': environment,
            'type': test_type
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.base_url}/execute?{query_string}"
    
    def create_bookmark_collection(self) -> Dict[str, str]:
        """Create a collection of bookmark-ready URLs"""
        
        bookmarks = {}
        
        # Common automation scenarios
        scenarios = [
            # Search functionality
            {
                "name": "Search - Button Click (DEV)",
                "event": {"page_type": "search", "event": "Button Clicked", "properties": {"button_text": "search"}},
                "env": "dev"
            },
            {
                "name": "Search - Button Click (PROD)",
                "event": {"page_type": "search", "event": "Button Clicked", "properties": {"button_text": "search"}},
                "env": "prod"
            },
            
            # Account functionality
            {
                "name": "Account - Login (DEV)",
                "event": {"page_type": "account", "event": "Button Clicked", "properties": {"button_text": "sign in"}},
                "env": "dev"
            },
            {
                "name": "Account - Orders Tab (DEV)",
                "event": {"page_type": "account", "event": "Tab", "properties": {"tab_name": "Orders"}},
                "env": "dev"
            },
            {
                "name": "Account - Profile Tab (QAT)",
                "event": {"page_type": "account", "event": "Tab", "properties": {"tab_name": "Profile"}},
                "env": "qat"
            },
            
            # Shopping cart
            {
                "name": "Cart - View Cart (DEV)",
                "event": {"page_type": "cart", "event": "Page Load", "properties": {"action": "view_cart"}},
                "env": "dev"
            },
            {
                "name": "Cart - Checkout (QAT)",
                "event": {"page_type": "checkout", "event": "Button Clicked", "properties": {"button_text": "checkout"}},
                "env": "qat"
            },
            
            # Product pages
            {
                "name": "Product - Add to Cart (DEV)",
                "event": {"page_type": "product", "event": "Button Clicked", "properties": {"button_text": "add to cart"}},
                "env": "dev"
            },
            {
                "name": "Product - View Details (PROD)",
                "event": {"page_type": "product", "event": "Page Load", "properties": {"action": "view_product"}},
                "env": "prod"
            },
            
            # Data-driven testing
            {
                "name": "Data Analysis - 2 Days (DEV)",
                "event": {"days_back": 2},
                "env": "dev",
                "type": "data_driven"
            },
            {
                "name": "Data Analysis - 7 Days (PROD)",
                "event": {"days_back": 7},
                "env": "prod", 
                "type": "data_driven"
            },
            
            # Event analysis
            {
                "name": "Event Patterns - Recent",
                "event": {"days_back": 2},
                "env": "prod",
                "type": "analysis"
            },
            {
                "name": "Event Patterns - Weekly",
                "event": {"days_back": 7}, 
                "env": "prod",
                "type": "analysis"
            }
        ]
        
        # Generate URLs for each scenario
        for scenario in scenarios:
            bookmarks[scenario["name"]] = self.create_automation_url(
                event_data=scenario["event"],
                environment=scenario["env"],
                test_type=scenario.get("type", "single")
            )
        
        return bookmarks
    
    def create_html_bookmark_page(self) -> str:
        """Create an HTML page with all automation bookmarks"""
        
        bookmarks = self.create_bookmark_collection()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Chewy Automation Bookmarks</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px auto; max-width: 1000px; background: #f8fafc; }}
        .container {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a365d; text-align: center; margin-bottom: 30px; }}
        .bookmark-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .bookmark {{ 
            display: block; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; text-decoration: none; border-radius: 10px; text-align: center;
            transition: all 0.3s ease; font-weight: 500; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .bookmark:hover {{ 
            transform: translateY(-3px); box-shadow: 0 6px 25px rgba(0,0,0,0.2); color: white; text-decoration: none; 
        }}
        .bookmark-dev {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .bookmark-qat {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        .bookmark-prod {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .bookmark-data {{ background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #2d3748; }}
        .bookmark-analysis {{ background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #2d3748; }}
        .timestamp {{ text-align: center; margin-top: 30px; color: #718096; font-size: 14px; }}
        .header-emoji {{ font-size: 2em; margin-right: 10px; }}
        .copy-btn {{ 
            display: inline-block; margin-top: 10px; padding: 5px 10px; 
            background: rgba(255,255,255,0.2); border-radius: 5px; font-size: 12px; cursor: pointer;
        }}
        .copy-btn:hover {{ background: rgba(255,255,255,0.3); }}
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="header-emoji">🔗</span>Chewy Automation Bookmarks</h1>
        <p style="text-align: center; color: #4a5568; margin-bottom: 30px;">
            Click any link below to instantly execute automation tasks. Bookmark this page for quick access!
        </p>
        
        <div class="bookmark-grid">"""
        
        for name, url in bookmarks.items():
            # Determine bookmark class based on environment and type
            bookmark_class = "bookmark"
            if "DEV" in name:
                bookmark_class += " bookmark-dev"
            elif "QAT" in name:
                bookmark_class += " bookmark-qat"
            elif "PROD" in name:
                bookmark_class += " bookmark-prod"
            elif "Data Analysis" in name:
                bookmark_class += " bookmark-data"
            elif "Event Patterns" in name:
                bookmark_class += " bookmark-analysis"
                
            html += f'''
            <a href="{url}" class="{bookmark_class}" target="_blank">
                {name}
                <div class="copy-btn" onclick="navigator.clipboard.writeText('{url}'); event.preventDefault(); event.stopPropagation(); alert('URL copied to clipboard!');">
                    📋 Copy URL
                </div>
            </a>'''
        
        html += f"""
        </div>
        
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def create_slack_friendly_links(self) -> List[str]:
        """Create Slack-friendly automation links"""
        
        bookmarks = self.create_bookmark_collection()
        slack_links = []
        
        for name, url in bookmarks.items():
            # Create Slack-friendly format
            slack_links.append(f"• <{url}|{name}>")
        
        return slack_links
    
    def create_markdown_links(self) -> str:
        """Create markdown-formatted automation links"""
        
        bookmarks = self.create_bookmark_collection()
        markdown = "# Chewy Automation Links\n\n"
        
        # Group by environment
        environments = {"DEV": [], "QAT": [], "PROD": [], "DATA": []}
        
        for name, url in bookmarks.items():
            if "DEV" in name:
                environments["DEV"].append(f"- [{name}]({url})")
            elif "QAT" in name:
                environments["QAT"].append(f"- [{name}]({url})")
            elif "PROD" in name:
                environments["PROD"].append(f"- [{name}]({url})")
            elif any(x in name for x in ["Data Analysis", "Event Patterns"]):
                environments["DATA"].append(f"- [{name}]({url})")
        
        for env, links in environments.items():
            if links:
                if env == "DATA":
                    markdown += "## 📊 Data Analysis & Event Patterns\n\n"
                else:
                    markdown += f"## {env} Environment\n\n"
                markdown += "\n".join(links) + "\n\n"
        
        return markdown

def main():
    """Generate automation URLs and bookmarks"""
    
    generator = AutomationURLGenerator()
    
    print("🔗 Chewy Automation URL Generator")
    print("=" * 50)
    
    # Example: Generate a single URL
    example_event = {
        "page_type": "search",
        "event": "Button Clicked", 
        "properties": {"button_text": "search"}
    }
    
    example_url = generator.create_automation_url(example_event, "dev")
    print(f"\n📋 Example URL:\n{example_url}")
    
    # Generate bookmark collection
    print(f"\n📚 Generated {len(generator.create_bookmark_collection())} automation bookmarks")
    
    # Save HTML bookmark page
    html_content = generator.create_html_bookmark_page()
    with open("automation_bookmarks.html", "w") as f:
        f.write(html_content)
    print("💾 Saved: automation_bookmarks.html")
    
    # Save markdown links
    markdown_content = generator.create_markdown_links()
    with open("automation_links.md", "w") as f:
        f.write(markdown_content)
    print("💾 Saved: automation_links.md")
    
    print(f"\n🚀 Start the automation service:")
    print("   python hyperlink_automation.py")
    print("\n🌐 Then open: http://localhost:5000")

if __name__ == "__main__":
    main()