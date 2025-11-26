"""
Test script for flexible JSON parsing with any size JSON containing page_type
"""

import json
from chewy_agent import ChewyAutomationAgent


def test_large_complex_json():
    """Test with a large, complex JSON structure."""
    
    # Large, complex JSON with nested structures
    event_data = {
        "metadata": {
            "version": "1.2.3",
            "timestamp": "2025-11-26T09:00:00Z",
            "source": "web",
            "environment": "qat",
            "user": {
                "id": "user_12345",
                "session_id": "sess_abcdef",
                "preferences": {
                    "theme": "dark",
                    "language": "en-US"
                }
            },
            "device": {
                "type": "desktop",
                "browser": "chrome",
                "version": "119.0",
                "screen": {
                    "width": 1920,
                    "height": 1080,
                    "density": 1
                }
            }
        },
        "tracking": {
            "google_analytics": {
                "tracking_id": "UA-12345-1",
                "client_id": "client_xyz"
            },
            "adobe_analytics": {
                "suite_id": "chewy-prod"
            },
            "custom_events": [
                {
                    "name": "page_load",
                    "value": 1250
                },
                {
                    "name": "time_on_page", 
                    "value": 45.7
                }
            ]
        },
        "page": {
            "page_type": "home",  # This is what we need!
            "url": "https://www-qat.chewy.net/",
            "title": "Chewy - Pet Food, Products, Supplies at Low Prices",
            "referrer": "https://google.com/search?q=pet+food",
            "navigation": {
                "type": "page_load",
                "timing": {
                    "dom_ready": 1200,
                    "load_complete": 2500
                }
            }
        },
        "event": {
            "category": "mini-cart",
            "action": "subtotal-view",
            "label": "view_cart_summary",
            "value": 0,
            "custom_dimensions": {
                "cd1": "logged_out",
                "cd2": "desktop",
                "cd3": "homepage"
            }
        },
        "cart": {
            "items": [],
            "total_items": 0,
            "subtotal": 0.00,
            "currency": "USD",
            "last_updated": "2025-11-26T09:00:00Z"
        },
        "additional_data": {
            "experiment_groups": ["control", "new_header"],
            "feature_flags": {
                "new_checkout": True,
                "recommendation_engine_v2": False
            },
            "performance_metrics": {
                "page_load_time": 2.5,
                "time_to_interactive": 3.2,
                "largest_contentful_paint": 2.8
            }
        }
    }
    
    print("="*80)
    print("TESTING LARGE COMPLEX JSON PARSING")
    print("="*80)
    print(f"JSON size: {len(json.dumps(event_data))} characters")
    print(f"Nested levels: {count_nesting_levels(event_data)} levels deep")
    print(f"Total keys: {count_total_keys(event_data)} keys")
    print("="*80)
    
    agent = ChewyAutomationAgent(environment="qat")
    result = agent.execute_event(event_data)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    print("="*80)
    print(f"✅ Event completed at hour: {result.get('hour')}")
    print(f"Status: {result.get('status')}")
    print("="*80)
    
    return result


def test_deeply_nested_json():
    """Test with very deeply nested JSON."""
    
    event_data = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "level5": {
                            "page_type": "product",  # Deep nesting
                            "eventCategory": "product-interaction",
                            "eventAction": "view-details"
                        }
                    }
                }
            }
        },
        "other_data": {
            "analytics": ["event1", "event2", "event3"],
            "metadata": {"source": "web", "version": "1.0"}
        }
    }
    
    print("="*80)
    print("TESTING DEEPLY NESTED JSON")
    print("="*80)
    
    agent = ChewyAutomationAgent(environment="qat")
    result = agent.execute_event(event_data)
    
    print("Result:")
    print(json.dumps(result, indent=2))
    print("="*80)
    print(f"✅ Event completed at hour: {result.get('hour')}")
    print("="*80)
    
    return result


def test_array_with_page_type():
    """Test with page_type inside an array."""
    
    event_data = {
        "events": [
            {
                "type": "click",
                "element": "button"
            },
            {
                "type": "view",
                "page_type": "cart",  # Inside array
                "eventCategory": "navigation",
                "eventAction": "view-cart"
            },
            {
                "type": "scroll",
                "position": 250
            }
        ],
        "session": {
            "id": "abc123",
            "start_time": "2025-11-26T09:00:00Z"
        }
    }
    
    print("="*80)
    print("TESTING ARRAY-BASED JSON")
    print("="*80)
    
    agent = ChewyAutomationAgent(environment="qat")
    result = agent.execute_event(event_data)
    
    print("Result:")
    print(json.dumps(result, indent=2))
    print("="*80)
    print(f"✅ Event completed at hour: {result.get('hour')}")
    print("="*80)
    
    return result


def test_missing_page_type():
    """Test with JSON that has no page_type - should fail gracefully."""
    
    event_data = {
        "event": "click",
        "data": {
            "button": "submit",
            "form": "contact",
            "metadata": {
                "timestamp": "2025-11-26T09:00:00Z",
                "source": "web"
            }
        }
    }
    
    print("="*80)
    print("TESTING MISSING PAGE_TYPE (Should Fail)")
    print("="*80)
    
    agent = ChewyAutomationAgent(environment="qat")
    result = agent.execute_event(event_data)
    
    print("Result:")
    print(json.dumps(result, indent=2))
    print("="*80)
    print(f"Status: {result.get('status')} (Expected: error)")
    print("="*80)
    
    return result


def count_nesting_levels(obj, level=0):
    """Count the maximum nesting level in a JSON object."""
    if isinstance(obj, dict):
        if not obj:
            return level
        return max(count_nesting_levels(value, level + 1) for value in obj.values())
    elif isinstance(obj, list):
        if not obj:
            return level
        return max(count_nesting_levels(item, level + 1) for item in obj)
    else:
        return level


def count_total_keys(obj):
    """Count total number of keys in a nested JSON object."""
    if isinstance(obj, dict):
        count = len(obj)
        for value in obj.values():
            count += count_total_keys(value)
        return count
    elif isinstance(obj, list):
        return sum([count_total_keys(item) for item in obj])
    else:
        return 0


def run_all_flexible_tests():
    """Run all flexible JSON tests."""
    print("\\n" + "="*80)
    print("FLEXIBLE JSON PARSING TEST SUITE")
    print("Testing agent's ability to handle any size JSON with page_type")
    print("="*80)
    
    tests = [
        ("Large Complex JSON", test_large_complex_json),
        ("Deeply Nested JSON", test_deeply_nested_json), 
        ("Array-based JSON", test_array_with_page_type),
        ("Missing page_type", test_missing_page_type)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- Running: {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result.get('status', 'unknown')))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, 'exception'))
    
    # Summary
    print("\\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, status in results:
        status_icon = "✅" if status == "success" else "❌"
        print(f"{status_icon} {test_name}: {status}")
    print("="*80)


if __name__ == "__main__":
    run_all_flexible_tests()