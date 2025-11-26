"""
Quick test script for the flexible JSON format
"""

import json
from chewy_agent import ChewyAutomationAgent


def test_flexible_json():
    """Test the exact JSON format you provided."""
    
    # Your example JSON
    event_data = {
        "properties": {
            "page_type": "home",
            "eventCategory": "mini-cart",
            "eventAction": "subtotal-view"
        }
    }
    
    print("\n" + "="*70)
    print("🧪 TESTING FLEXIBLE JSON FORMAT")
    print("="*70)
    print("Input JSON:")
    print(json.dumps(event_data, indent=2))
    print("="*70)
    
    # Create agent and execute
    agent = ChewyAutomationAgent(environment="qat")
    result = agent.execute_event(event_data)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    print("="*70)
    print(f"\n✅ Event completed at hour: {result.get('hour')}")
    print(f"📅 Full timestamp: {result.get('completed_at')}")
    print(f"🎯 Action performed: {result.get('result')}")
    print("="*70 + "\n")
    
    return result


def test_multiple_formats():
    """Test various JSON formats to show flexibility."""
    
    test_cases = [
        {
            "name": "Your format - properties only",
            "json": {
                "properties": {
                    "page_type": "home",
                    "eventCategory": "mini-cart",
                    "eventAction": "subtotal-view"
                }
            }
        },
        {
            "name": "Root level properties",
            "json": {
                "page_type": "home",
                "eventCategory": "mini-cart", 
                "eventAction": "click"
            }
        },
        {
            "name": "Traditional format",
            "json": {
                "event": "Navigation Clicked",
                "properties": {
                    "page_type": "home",
                    "eventCategory": "mini-cart",
                    "eventAction": "clicked",
                    "eventLabel": "mini-cart"
                }
            }
        }
    ]
    
    agent = ChewyAutomationAgent(environment="qat")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test_case['name']}")
        print("="*70)
        print("Input:")
        print(json.dumps(test_case['json'], indent=2))
        
        result = agent.execute_event(test_case['json'])
        
        print(f"\nResult: {result.get('status')} - Hour: {result.get('hour')}")
        print(f"Action: {result.get('result', 'No result')}")
        print("="*70)


if __name__ == "__main__":
    # Test your specific JSON format
    test_flexible_json()
    
    # Uncomment to test multiple formats:
    # test_multiple_formats()