#!/usr/bin/env python3
"""
Test the specific Button Clicked event with PDP page_type
"""

import json
import os
from chewy_agent import ChewyAutomationAgent

def test_button_clicked_pdp():
    """Test the Button Clicked event on PDP page"""
    print("=== Testing Button Clicked Event with PDP Page Type ===")
    
    # Load the event from the JSON file
    event_data = {
        "event": "Button Clicked",
        "properties": {
            "page_type": "PDP",
            "eventCategory": "header-icon",
            "eventAction": "click",
            "eventLabel": "search-icon"
        }
    }
    
    print(f"Test event: {json.dumps(event_data, indent=2)}")
    
    # Create agent with dev environment
    agent = ChewyAutomationAgent(environment="dev")
    
    # Check if PDP URL mapping exists
    pdp_url = agent.page_type_urls.get("pdp")
    print(f"PDP URL from CSV: {pdp_url}")
    
    if pdp_url:
        print("✅ PDP URL mapping found in CSV")
    else:
        print("❌ PDP URL mapping not found in CSV")
        # Show available page types
        available_types = list(agent.page_type_urls.keys())[:10]
        print(f"Available page types (first 10): {available_types}")
    
    # Execute the event
    print("\n--- Executing Event ---")
    result = agent.execute_event(event_data)
    
    print(f"\nExecution result:")
    print(json.dumps(result, indent=2))
    
    # Verify result
    if result["status"] == "success":
        print("\n✅ Successfully executed Button Clicked event on PDP page")
        print(f"Event completed at hour: {result['hour']}")
        print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")
        print(f"Action result: {result.get('result', 'No result')}")
    else:
        print(f"\n❌ Execution failed: {result.get('error', 'Unknown error')}")
        
    return result

if __name__ == "__main__":
    test_button_clicked_pdp()