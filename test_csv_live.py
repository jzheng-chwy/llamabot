#!/usr/bin/env python3
"""
Test live browser automation with CSV page types
"""

import json
import os
from chewy_agent import ChewyAutomationAgent

def test_pdp_page_type():
    """Test navigating to a Product Detail Page (PDP) from the CSV"""
    print("=== Testing PDP Page Type Navigation ===")
    
    # Create test event with PDP page type
    event_data = {
        "event": "Mini-Cart Viewed",
        "properties": {
            "eventCategory": "mini-cart",
            "eventAction": "view",
            "eventLabel": "mini-cart", 
            "page_type": "pdp"  # This should map to the PDP URL from CSV
        }
    }
    
    print(f"Test event: {json.dumps(event_data, indent=2)}")
    
    # Execute with dev environment  
    agent = ChewyAutomationAgent(environment="dev")
    
    # Check the URL mapping first
    pdp_url = agent.page_type_urls.get("pdp")
    print(f"PDP URL from CSV: {pdp_url}")
    
    # Execute the event
    print("\n--- Executing Event ---")
    result = agent.execute_event(event_data)
    
    print(f"Execution result:")
    print(json.dumps(result, indent=2))
    
    # Verify result
    if result["status"] == "success":
        print("✅ Successfully executed PDP navigation and action")
    else:
        print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")

def test_checkout_page_type():
    """Test navigating to a Checkout page from the CSV"""
    print("\n=== Testing Checkout Page Type Navigation ===")
    
    # Create test event with checkout page type
    event_data = {
        "event": "Navigation Clicked",
        "properties": {
            "eventCategory": "mini-cart",
            "eventAction": "click",
            "eventLabel": "mini-cart",
            "page_type": "checkout"
        }
    }
    
    print(f"Test event: {json.dumps(event_data, indent=2)}")
    
    # Execute with QAT environment
    agent = ChewyAutomationAgent(environment="qat")
    
    # Check the URL mapping first
    checkout_url = agent.page_type_urls.get("checkout")
    print(f"Checkout URL from CSV: {checkout_url}")
    
    # Execute the event
    print("\n--- Executing Event ---")
    result = agent.execute_event(event_data)
    
    print(f"Execution result:")
    print(json.dumps(result, indent=2))
    
    # Verify result
    if result["status"] == "success":
        print("✅ Successfully executed checkout navigation and action")
    else:
        print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")

def test_privacy_page_type():
    """Test a simple content page that should load quickly"""
    print("\n=== Testing Privacy Page Type Navigation ===")
    
    # Create test event with privacy page type  
    event_data = {
        "event": "Page Viewed",
        "properties": {
            "eventCategory": "navigation",
            "eventAction": "view",
            "page_type": "privacy"
        }
    }
    
    print(f"Test event: {json.dumps(event_data, indent=2)}")
    
    # Execute with dev environment
    agent = ChewyAutomationAgent(environment="dev")
    
    # Check the URL mapping first
    privacy_url = agent.page_type_urls.get("privacy")
    print(f"Privacy URL from CSV: {privacy_url}")
    
    # Execute the event
    print("\n--- Executing Event ---")
    result = agent.execute_event(event_data)
    
    print(f"Execution result:")
    print(json.dumps(result, indent=2))
    
    # Verify result
    if result["status"] == "success":
        print("✅ Successfully executed privacy page navigation")
    else:
        print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    # Test different page types from the CSV
    test_privacy_page_type()  # Start with a simple content page
    # test_pdp_page_type()      # Product page (might be slower)
    # test_checkout_page_type() # Checkout page (might require auth)