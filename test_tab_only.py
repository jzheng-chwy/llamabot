#!/usr/bin/env python3
"""
Test just the tab event functionality
"""

import json
from chewy_agent import ChewyAutomationAgent

def test_tab_event_only():
    """Test just the tab event."""
    print("=== Testing Tab Event Only ===")
    
    # Test tab event on PDP page
    event_data = {
        "event": "tab",
        "properties": {
            "page_type": "PDP"
        }
    }
    
    print(f"Test event: {json.dumps(event_data, indent=2)}")
    
    # Execute with dev environment
    agent = ChewyAutomationAgent(environment="dev")
    
    result = agent.execute_event(event_data)
    
    print(f"\nTab event result:")
    print(json.dumps(result, indent=2))
    
    if result["status"] == "success":
        print("\n✅ Successfully executed tab event")
        print(f"Event type detected: {result.get('event', 'N/A')}")
        print(f"Action result: {result.get('result', 'No result')}")
    else:
        print(f"\n❌ Tab event failed: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    test_tab_event_only()