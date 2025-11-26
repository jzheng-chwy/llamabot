"""
Test the Chewy agent with a public demo site first
"""

import json
from chewy_agent import ChewyAutomationAgent


def test_with_demo_site():
    """Test the agent with a demo site to verify it's working."""
    
    # Temporarily modify the agent to use a demo site
    agent = ChewyAutomationAgent()
    agent.base_url = "https://demo.playwright.dev/todomvc/"  # Public test site
    
    print("\n🧪 TESTING AGENT WITH DEMO SITE")
    print("="*60)
    print(f"Using demo site: {agent.base_url}")
    print("="*60)
    
    # Test event that clicks on an input field
    event_data = {
        "event": "Navigation Clicked",
        "properties": {
            "eventCategory": "test",
            "eventAction": "clicked", 
            "eventLabel": "input"
        }
    }
    
    result = agent.execute_event(event_data)
    
    print(json.dumps(result, indent=2))
    print(f"\n✅ Test completed at hour: {result.get('hour')}")
    print("="*60)
    
    return result


def test_chewy_site():
    """Test with the actual Chewy dev site."""
    
    print("\n🐕 TESTING AGENT WITH CHEWY DEV SITE")
    print("="*60)
    
    event_data = {
        "event": "Navigation Clicked",
        "properties": {
            "page_type": "Account",
            "eventCategory": "browse-nav",
            "eventAction": "clicked",
            "eventLabel": "mini-cart"
        }
    }
    
    agent = ChewyAutomationAgent()
    result = agent.execute_event(event_data)
    
    print(json.dumps(result, indent=2))
    print(f"\n✅ Test completed at hour: {result.get('hour')}")
    print("="*60)
    
    return result


if __name__ == "__main__":
    # First test with demo site to verify agent works
    demo_result = test_with_demo_site()
    
    # If demo works, try Chewy site
    if demo_result.get("status") == "success":
        print("\n✅ Demo test passed! Now trying Chewy dev site...")
        chewy_result = test_chewy_site()
    else:
        print("\n❌ Demo test failed. Check your setup:")
        print("- Is your virtual environment activated?")
        print("- Is Playwright installed with browsers?")
        print("- Is your internet connection working?")