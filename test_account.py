"""
Test account page_type and tab event functionality
"""

import json
from chewy_agent import ChewyAutomationAgent


def test_account_page_type():
    """Test navigating to account page and performing actions."""
    
    print("\n" + "="*70)
    print("TESTING ACCOUNT PAGE_TYPE")
    print("="*70)
    
    # Test account page with mini-cart view
    event_data = {
        "event": "Element Viewed",
        "properties": {
            "page_type": "Account",
            "eventCategory": "mini-cart", 
            "eventAction": "subtotal-view",
            "eventLabel": "cart-summary"
        }
    }
    
    print("Test Event JSON:")
    print(json.dumps(event_data, indent=2))
    print("="*70)
    
    agent = ChewyAutomationAgent(environment="qat")
    result = agent.execute_event(event_data)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    print("="*70)
    print(f"✅ Event completed at hour: {result.get('hour')}")
    print(f"Status: {result.get('status')}")
    print(f"Action performed: {result.get('result', 'No result')}")
    print("="*70 + "\n")
    
    return result


def test_tab_event():
    """Test the tab event with PDP page_type."""
    
    print("\n" + "="*70)
    print("TESTING TAB EVENT")
    print("="*70)
    
    # Test tab event on PDP page
    event_data = {
        "event": "tab",
        "properties": {
            "page_type": "PDP"
        }
    }
    
    print("Test Event JSON:")
    print(json.dumps(event_data, indent=2))
    print("="*70)
    
    # Execute with dev environment
    agent = ChewyAutomationAgent(environment="dev")
    
    # Check if PDP URL mapping exists
    pdp_url = agent.page_type_urls.get("pdp")
    if pdp_url:
        print(f"✅ PDP URL from CSV: {pdp_url[:80]}...")
    else:
        print("❌ PDP URL mapping not found in CSV")
    
    print("="*70)
    
    result = agent.execute_event(event_data)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    print("="*70)
    print(f"✅ Event completed at hour: {result.get('hour')}")
    print(f"Status: {result.get('status')}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f} seconds")
    print(f"Action performed: {result.get('result', 'No result')}")
    print("="*70 + "\n")
    
    return result


if __name__ == "__main__":
    print("Running account and tab event tests...")
    
    # Test 1: Account page
    account_result = test_account_page_type()
    
    # Test 2: Tab event  
    tab_result = test_tab_event()
    
    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Account test: {'✅ SUCCESS' if account_result['status'] == 'success' else '❌ FAILED'}")
    print(f"Tab test: {'✅ SUCCESS' if tab_result['status'] == 'success' else '❌ FAILED'}")
    print("="*70)