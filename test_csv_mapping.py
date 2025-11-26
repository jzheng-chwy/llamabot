#!/usr/bin/env python3
"""
Test CSV page type mapping functionality
"""

import json
import os
from chewy_agent import ChewyAutomationAgent

def test_csv_loading():
    """Test that CSV loads correctly and URLs are converted"""
    print("Testing CSV page type mapping...")
    
    # Test with different environments
    for env in ["dev", "qat", "prod"]:
        print(f"\n=== Testing {env.upper()} Environment ===")
        agent = ChewyAutomationAgent(environment=env)
        
        # Check that mappings were loaded
        print(f"Loaded {len(agent.page_type_urls)} page type mappings")
        
        # Test a few specific page types
        test_page_types = ["home", "pdp", "cart", "account", "login", "checkout"]
        
        for page_type in test_page_types:
            if page_type in agent.page_type_urls:
                url = agent.page_type_urls[page_type]
                print(f"✅ {page_type}: {url}")
                
                # Verify URL uses correct environment
                expected_domain = agent.base_url.rstrip('/')
                if url.startswith(expected_domain):
                    print(f"   ✅ Correctly uses {env} domain")
                else:
                    print(f"   ❌ Wrong domain. Expected to start with: {expected_domain}")
            else:
                print(f"❌ {page_type}: Not found in mappings")

def test_event_with_page_type():
    """Test processing an event with a page_type from the CSV"""
    print("\n=== Testing Event Processing with CSV Page Types ===")
    
    # Test various page types from the CSV
    test_events = [
        {
            "event": "Navigation Clicked",
            "properties": {
                "eventCategory": "mini-cart",
                "eventAction": "view",
                "eventLabel": "mini-cart",
                "page_type": "checkout"
            }
        },
        {
            "event": "Page Viewed", 
            "properties": {
                "page_type": "pdp",
                "eventCategory": "product",
                "eventAction": "view"
            }
        },
        {
            "event": "Navigation Clicked",
            "properties": {
                "page_type": "cart",
                "eventCategory": "navigation",
                "eventAction": "click"
            }
        }
    ]
    
    agent = ChewyAutomationAgent(environment="dev")
    
    for i, event in enumerate(test_events, 1):
        print(f"\n--- Test Event {i} ---")
        print(f"Page Type: {event['properties']['page_type']}")
        
        # Check if URL mapping exists
        page_type = event['properties']['page_type'].lower()
        if page_type in agent.page_type_urls:
            url = agent.page_type_urls[page_type]
            print(f"✅ Found URL mapping: {url}")
        else:
            print(f"❌ No URL mapping found for: {page_type}")
        
        print(f"Event data: {json.dumps(event, indent=2)}")

if __name__ == "__main__":
    test_csv_loading()
    test_event_with_page_type()