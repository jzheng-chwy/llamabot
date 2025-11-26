"""
Enhanced test script for the Chewy Automation Agent
Tests different page types and navigation scenarios
"""

import json
from chewy_agent import ChewyAutomationAgent


def test_account_page_mini_cart():
    """Test navigating to account page and clicking mini-cart."""
    print("\n" + "="*70)
    print("TEST 1: Account Page → Mini-Cart Click")
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
    
    agent = ChewyAutomationAgent(environment="qat")  # Using QAT environment
    result = agent.execute_event(event_data)
    
    print(json.dumps(result, indent=2))
    print(f"\n✅ Event completed at hour: {result.get('hour')}")
    print(f"📅 Full timestamp: {result.get('completed_at')}")
    print("="*70 + "\n")
    
    return result


def test_product_page_add_to_cart():
    """Test navigating to product page and clicking add to cart."""
    print("\n" + "="*70)
    print("TEST 2: Product Page → Add to Cart Click")
    print("="*70)
    
    event_data = {
        "event": "Button Clicked",
        "properties": {
            "page_type": "Product",
            "eventCategory": "product-action",
            "eventAction": "clicked",
            "eventLabel": "Add to Cart"
        }
    }
    
    agent = ChewyAutomationAgent(environment="qat")
    result = agent.execute_event(event_data)
    
    print(json.dumps(result, indent=2))
    print(f"\n✅ Event completed at hour: {result.get('hour')}")
    print(f"📅 Full timestamp: {result.get('completed_at')}")
    print("="*70 + "\n")
    
    return result


def test_home_page_search():
    """Test search functionality from home page."""
    print("\n" + "="*70)
    print("TEST 3: Home Page → Search Click")
    print("="*70)
    
    event_data = {
        "event": "Navigation Clicked",
        "properties": {
            "page_type": "Search",
            "eventCategory": "header-nav",
            "eventAction": "clicked",
            "eventLabel": "search"
        }
    }
    
    agent = ChewyAutomationAgent(environment="qat")
    result = agent.execute_event(event_data)
    
    print(json.dumps(result, indent=2))
    print(f"\n✅ Event completed at hour: {result.get('hour')}")
    print(f"📅 Full timestamp: {result.get('completed_at')}")
    print("="*70 + "\n")
    
    return result


def test_custom_scenarios():
    """Test custom scenarios with different page types."""
    
    scenarios = [
        {
            "name": "Cart Page Navigation",
            "event": {
                "event": "Page Viewed",
                "properties": {
                    "page_type": "Cart",
                    "eventCategory": "page-view",
                    "eventAction": "viewed",
                    "eventLabel": "cart-page"
                }
            }
        },
        {
            "name": "Account Page Button Click",
            "event": {
                "event": "Button Clicked",
                "properties": {
                    "page_type": "Account", 
                    "eventCategory": "account-action",
                    "eventAction": "clicked",
                    "eventLabel": "Sign In"
                }
            }
        }
    ]
    
    results = []
    agent = ChewyAutomationAgent(environment="qat")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n" + "="*70)
        print(f"TEST {i+3}: {scenario['name']}")
        print("="*70)
        
        result = agent.execute_event(scenario["event"])
        results.append(result)
        
        print(json.dumps(result, indent=2))
        print(f"\n✅ Event completed at hour: {result.get('hour')}")
        print("="*70 + "\n")
    
    return results


def run_comprehensive_tests():
    """Run all test scenarios."""
    print("\n🤖 CHEWY AUTOMATION AGENT - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("Testing page_type navigation and actions on QAT environment")
    print("URL: https://www-qat.chewy.net/")
    print("Example Product: frisco-holiday-santas-helpers-plush/dp/191340")
    print("="*70 + "\n")
    
    all_results = []
    
    # Run main tests
    try:
        all_results.append(test_account_page_mini_cart())
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    try:
        all_results.append(test_product_page_add_to_cart())
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    try:
        all_results.append(test_home_page_search())
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    # Run custom scenarios
    try:
        custom_results = test_custom_scenarios()
        all_results.extend(custom_results)
    except Exception as e:
        print(f"❌ Custom tests failed: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*70)
    successful = sum(1 for r in all_results if r and r.get('status') == 'success')
    failed = len(all_results) - successful
    
    print(f"Total tests run: {len(all_results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    if successful > 0:
        print(f"\n🕐 Sample completion hours:")
        for i, result in enumerate(all_results[:3]):
            if result and result.get('status') == 'success':
                print(f"   Test {i+1}: Hour {result.get('hour')} ({result.get('completed_at')})")
    
    print("="*70 + "\n")
    
    return all_results


if __name__ == "__main__":
    # Run comprehensive tests
    run_comprehensive_tests()
    
    # Or run individual tests:
    # test_account_page_mini_cart()
    # test_product_page_add_to_cart()