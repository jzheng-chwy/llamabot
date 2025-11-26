"""
Test script for the Chewy Automation Agent
Run different event scenarios and see the results
"""

import json
from chewy_agent import ChewyAutomationAgent


def test_mini_cart_click():
    """Test clicking the mini-cart."""
    print("\n" + "="*70)
    print("TEST 1: Clicking Mini-Cart")
    print("="*70)
    
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
    print(f"\n✅ Event completed at hour: {result.get('hour')}")
    print(f"📅 Full timestamp: {result.get('completed_at')}")
    print("="*70 + "\n")
    
    return result


def test_search_click():
    """Test clicking the search."""
    print("\n" + "="*70)
    print("TEST 2: Clicking Search")
    print("="*70)
    
    event_data = {
        "event": "Navigation Clicked",
        "properties": {
            "eventCategory": "header-nav",
            "eventAction": "clicked",
            "eventLabel": "search"
        }
    }
    
    agent = ChewyAutomationAgent()
    result = agent.execute_event(event_data)
    
    print(json.dumps(result, indent=2))
    print(f"\n✅ Event completed at hour: {result.get('hour')}")
    print(f"📅 Full timestamp: {result.get('completed_at')}")
    print("="*70 + "\n")
    
    return result


def test_account_click():
    """Test clicking the account link."""
    print("\n" + "="*70)
    print("TEST 3: Clicking Account")
    print("="*70)
    
    event_data = {
        "event": "Navigation Clicked",
        "properties": {
            "page_type": "Header",
            "eventCategory": "user-nav",
            "eventAction": "clicked",
            "eventLabel": "account"
        }
    }
    
    agent = ChewyAutomationAgent()
    result = agent.execute_event(event_data)
    
    print(json.dumps(result, indent=2))
    print(f"\n✅ Event completed at hour: {result.get('hour')}")
    print(f"📅 Full timestamp: {result.get('completed_at')}")
    print("="*70 + "\n")
    
    return result


def run_all_tests():
    """Run all test scenarios."""
    print("\n🤖 CHEWY AUTOMATION AGENT - TEST SUITE")
    print("="*70)
    print("Running automated tests on https://www-dev.chewy.net/")
    print("="*70 + "\n")
    
    results = []
    
    # Run tests
    results.append(test_mini_cart_click())
    # Uncomment to run more tests:
    # results.append(test_search_click())
    # results.append(test_account_click())
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    successful = sum(1 for r in results if r.get('status') == 'success')
    print(f"Total tests run: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print("="*70 + "\n")


if __name__ == "__main__":
    # You can run individual tests or all tests
    run_all_tests()
    
    # Or run a single test:
    # test_mini_cart_click()
