"""
OpenAI Agent for Chewy Website Automation
Takes JSON event data and performs corresponding actions on the Chewy website.
"""

import json
import os
import csv
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright, Page, Browser

load_dotenv()

class ChewyAutomationAgent:
    def __init__(self, environment="dev"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.environment = environment
        self.base_urls = {
            "dev": "https://www-dev.chewy.net/",
            "qat": "https://www-qat.chewy.net/",
            "prod": "https://www.chewy.com/"
        }
        self.base_url = self.base_urls.get(environment, self.base_urls["dev"])
        
        # Load page type URL mappings from CSV
        self.page_type_urls = self._load_page_type_mappings()
        
    def execute_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a website action based on the event JSON.
        
        Args:
            event_data: JSON object containing event details (any size, requires page_type)
            
        Returns:
            Dictionary with execution details including timestamp
        """
        start_time = datetime.now()
        
        # Validate that page_type exists somewhere in the JSON
        page_type = self._extract_page_type(event_data)
        if not page_type:
            return {
                "status": "error",
                "event": "Invalid JSON",
                "error": "page_type is required but not found in JSON",
                "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hour": datetime.now().hour
            }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=['--no-sandbox', '--disable-dev-shm-usage'])
            context = browser.new_context()
            page = context.new_page()
            
            try:
                # Navigate to Chewy with timeout and fallback
                print(f"Navigating to: {self.base_url}")
                try:
                    page.goto(self.base_url, wait_until="networkidle", timeout=15000)
                    print("✅ Successfully loaded the page")
                except Exception as nav_error:
                    print(f"Navigation timeout, trying with domcontentloaded...")
                    page.goto(self.base_url, wait_until="domcontentloaded", timeout=10000)
                    print("✅ Page loaded with DOM content")
                
                # Parse the event and execute the action - handle flexible JSON formats
                parsed_data = self._parse_flexible_json(event_data)
                event_type = parsed_data["event_type"]
                properties = parsed_data["properties"]
                
                print(f"Executing event: {event_type}")
                print(f"Properties: category={properties.get('eventCategory')}, action={properties.get('eventAction')}, label={properties.get('eventLabel')}, page_type={properties.get('page_type')}")
                
                # Navigate to the correct page type first if specified
                if properties.get('page_type'):
                    nav_result = self._navigate_to_page_type(page, properties.get('page_type'))
                    print(f"Page navigation: {nav_result}")
                
                result = self._perform_action(page, event_type, properties)
                
                end_time = datetime.now()
                
                return {
                    "status": "success",
                    "event": event_type,
                    "properties": properties,
                    "completed_at": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "hour": end_time.hour,
                    "duration_seconds": (end_time - start_time).total_seconds(),
                    "result": result
                }
                
            except Exception as e:
                end_time = datetime.now()
                return {
                    "status": "error",
                    "event": event_data.get("event", "Unknown"),
                    "error": str(e),
                    "completed_at": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "hour": end_time.hour
                }
            finally:
                try:
                    if page and not page.is_closed():
                        page.close()
                    if context:
                        context.close()
                    if browser:
                        browser.close()
                except:
                    pass
    
    def _extract_page_type(self, data: Any, path: str = "") -> str:
        """
        Recursively search for page_type in any JSON structure.
        
        Args:
            data: JSON data to search (dict, list, or primitive)
            path: Current path for debugging (optional)
            
        Returns:
            page_type value if found, empty string otherwise
        """
        if isinstance(data, dict):
            # Check if page_type is directly in this dict
            for key in data:
                if key.lower() in ['page_type', 'pagetype', 'page-type']:
                    return str(data[key])
            
            # Recursively search in nested dicts
            for key, value in data.items():
                result = self._extract_page_type(value, f"{path}.{key}" if path else key)
                if result:
                    return result
                    
        elif isinstance(data, list):
            # Search in list items
            for i, item in enumerate(data):
                result = self._extract_page_type(item, f"{path}[{i}]" if path else f"[{i}]")
                if result:
                    return result
        
        return ""
    
    def _load_page_type_mappings(self) -> Dict[str, str]:
        """
        Load page type to URL mappings from CSV file.
        Convert URLs to use the current environment's base URL.
        
        Returns:
            Dict mapping page_type to environment-specific URL
        """
        mappings = {}
        csv_file_path = os.path.join(os.path.dirname(__file__), "chewy_page_types.csv")
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    page_type = row.get('PAGE_TYPE', '').strip()
                    url = row.get('URL', '').strip()
                    
                    if page_type and url:
                        # Convert URL to use current environment
                        converted_url = self._convert_url_to_environment(url)
                        mappings[page_type.lower()] = converted_url
                        
            print(f"Loaded {len(mappings)} page type mappings from CSV")
            return mappings
            
        except Exception as e:
            print(f"Warning: Could not load page type mappings: {e}")
            return {}
    
    def _convert_url_to_environment(self, url: str) -> str:
        """
        Convert a URL to use the current environment's base URL.
        
        Args:
            url: Original URL from CSV
            
        Returns:
            URL adapted for current environment
        """
        if not url or url == 'undefined':
            return self.base_url
            
        # Remove existing domain and replace with environment domain
        if url.startswith('https://www.chewy.com/'):
            path = url.replace('https://www.chewy.com/', '')
            return f"{self.base_url.rstrip('/')}/{path}"
        elif url.startswith('https://www-qat.chewy.net/'):
            path = url.replace('https://www-qat.chewy.net/', '')
            return f"{self.base_url.rstrip('/')}/{path}"
        elif url.startswith('https://www-dev.chewy.net/'):
            path = url.replace('https://www-dev.chewy.net/', '')
            return f"{self.base_url.rstrip('/')}/{path}"
        elif url.startswith('www.chewy.com/'):
            path = url.replace('www.chewy.com/', '')
            return f"{self.base_url.rstrip('/')}/{path}"
        elif url.startswith('https://zeus-price-ui.'):
            # Special case for Zeus URLs - keep as is for now
            return url
        elif url.startswith('https://www.chewyhealth.com/'):
            # Special case for Chewy Health URLs - keep as is
            return url
        else:
            # For relative URLs or other formats, append to base URL
            if url.startswith('/'):
                return f"{self.base_url.rstrip('/')}{url}"
            else:
                return f"{self.base_url.rstrip('/')}/{url}"
    
    def _parse_flexible_json(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse JSON of any size and structure, extracting relevant fields.
        
        Args:
            event_data: Raw JSON event data
            
        Returns:
            Standardized dict with event_type and properties
        """
        # Extract all relevant fields from anywhere in the JSON
        extracted_fields = self._extract_all_fields(event_data)
        
        # Determine event type - check for direct event field first
        event_type = None
        
        # Check for 'event' field at top level first
        if "event" in event_data:
            event_type = str(event_data["event"])
        else:
            # Then check extracted fields
            event_type = (
                extracted_fields.get("event") or 
                extracted_fields.get("eventType") or
                self._infer_event_type(extracted_fields)
            )
        
        # Build standardized properties
        properties = {
            "page_type": extracted_fields.get("page_type", ""),
            "eventCategory": extracted_fields.get("eventCategory", ""),
            "eventAction": extracted_fields.get("eventAction", ""), 
            "eventLabel": extracted_fields.get("eventLabel", ""),
            # Include any additional fields found
            **{k: v for k, v in extracted_fields.items() 
               if k not in ["event", "eventType", "page_type", "eventCategory", "eventAction", "eventLabel"]}
        }
        
        print(f"Parsed JSON: Found {len(extracted_fields)} total fields")
        print(f"Key fields: page_type='{properties['page_type']}', category='{properties['eventCategory']}', action='{properties['eventAction']}'")
        
        return {
            "event_type": event_type,
            "properties": properties
        }
    
    def _extract_all_fields(self, data: Any, extracted: Optional[Dict[str, Any]] = None, path: str = "") -> Dict[str, Any]:
        """
        Recursively extract all relevant fields from JSON of any structure.
        
        Args:
            data: JSON data to search
            extracted: Dict to accumulate results
            path: Current path for debugging
            
        Returns:
            Dict with all extracted fields
        """
        if extracted is None:
            extracted = {}
            
        if isinstance(data, dict):
            for key, value in data.items():
                # Map common field variations
                normalized_key = self._normalize_field_name(key)
                
                if normalized_key and normalized_key not in extracted:
                    # Store the value if it's a simple type
                    if isinstance(value, (str, int, float, bool)):
                        extracted[normalized_key] = value
                    elif isinstance(value, dict) and len(value) == 1:
                        # If it's a single-item dict, extract the value
                        single_value = list(value.values())[0]
                        if isinstance(single_value, (str, int, float, bool)):
                            extracted[normalized_key] = single_value
                
                # Recursively search nested structures
                self._extract_all_fields(value, extracted, f"{path}.{key}" if path else key)
                
        elif isinstance(data, list):
            # Search in list items
            for i, item in enumerate(data):
                self._extract_all_fields(item, extracted, f"{path}[{i}]" if path else f"[{i}]")
        
        return extracted
    
    def _normalize_field_name(self, field_name: str) -> str:
        """
        Normalize field names to standard format.
        
        Args:
            field_name: Original field name
            
        Returns:
            Normalized field name or empty string if not relevant
        """
        if not isinstance(field_name, str):
            return ""
            
        lower_name = field_name.lower()
        
        # Map field name variations to standard names
        field_mappings = {
            # Page type variations
            'page_type': 'page_type',
            'pagetype': 'page_type', 
            'page-type': 'page_type',
            'page': 'page_type',
            'type': 'page_type',
            
            # Event variations
            'event': 'event',
            'eventtype': 'eventType',
            'event_type': 'eventType',
            'event-type': 'eventType',
            
            # Category variations
            'eventcategory': 'eventCategory',
            'event_category': 'eventCategory',
            'event-category': 'eventCategory',
            'category': 'eventCategory',
            
            # Action variations  
            'eventaction': 'eventAction',
            'event_action': 'eventAction',
            'event-action': 'eventAction',
            'action': 'eventAction',
            
            # Label variations
            'eventlabel': 'eventLabel',
            'event_label': 'eventLabel', 
            'event-label': 'eventLabel',
            'label': 'eventLabel',
            'name': 'eventLabel',
            
            # Other common fields
            'timestamp': 'timestamp',
            'time': 'timestamp',
            'userid': 'userId',
            'user_id': 'userId',
            'sessionid': 'sessionId',
            'session_id': 'sessionId',
            'url': 'url',
            'path': 'path',
            'value': 'value'
        }
        
        return field_mappings.get(lower_name, field_name if lower_name in field_mappings.values() else "")
    
    def _infer_event_type(self, properties: Dict[str, Any]) -> str:
        """Infer event type from properties when not explicitly provided."""
        event_category = properties.get("eventCategory", "").lower()
        event_action = properties.get("eventAction", "").lower()
        event_label = properties.get("eventLabel", "").lower()
        
        # Check if we have an explicit event field at root level
        if "event" in properties:
            explicit_event = str(properties["event"]).lower()
            if explicit_event == "tab":
                return "Tab Navigation"
            return explicit_event.title()
        
        # Map common patterns to event types
        if "click" in event_action or "clicked" in event_action:
            if any(nav_term in event_category for nav_term in ["nav", "header", "menu", "mini-cart"]):
                return "Navigation Clicked"
            elif "button" in event_category or "btn" in event_category:
                return "Button Clicked"
            else:
                return "Element Clicked"
        
        elif "view" in event_action or "viewed" in event_action:
            return "Element Viewed"
        
        elif "submit" in event_action or "form" in event_category:
            return "Form Submitted"
        
        elif "hover" in event_action or "mouseover" in event_action:
            return "Element Hovered"
        
        elif event_category == "mini-cart":
            if "view" in event_action:
                return "Mini-Cart Viewed"
            elif "click" in event_action:
                return "Navigation Clicked"
            else:
                return "Mini-Cart Action"
        
        else:
            # Default based on category or action
            if event_category:
                return f"Custom Action: {event_category}"
            elif event_action:
                return f"Custom Action: {event_action}"
            else:
                return "Generic Action"
    
    def _navigate_to_page_type(self, page: Page, page_type: str) -> str:
        """Navigate to the specified page type using CSV mappings."""
        try:
            page_type_lower = page_type.lower()
            
            # Check if we have a URL mapping for this page type
            if page_type_lower in self.page_type_urls:
                target_url = self.page_type_urls[page_type_lower]
                print(f"Navigating to {page_type} page: {target_url}")
                page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                return f"Navigated to {page_type} page: {page.url}"
            
            # Fallback to custom navigation methods for special cases
            elif page_type_lower == "account":
                return self._navigate_to_account_page(page)
            elif page_type_lower == "cart":
                return self._navigate_to_cart_page(page)
            elif page_type_lower == "search":
                return self._navigate_to_search_page(page)
            else:
                return f"Unknown page_type: {page_type}. No mapping found in CSV and no fallback available."
                
        except Exception as e:
            return f"Error navigating to {page_type}: {str(e)}"
    
    def _navigate_to_account_page(self, page: Page) -> str:
        """Navigate to account/sign-in page."""
        try:
            # Look for account/sign-in links
            account_selectors = [
                'a[href*="account"]',
                'a[href*="signin"]',
                'a[href*="login"]',
                '[data-testid*="account"]',
                '[data-testid*="signin"]',
                'button[aria-label*="account" i]',
                '.account-link',
                '.signin-link'
            ]
            
            for selector in account_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=3000):
                        print(f"Found account link with selector: {selector}")
                        element.click()
                        page.wait_for_load_state("domcontentloaded", timeout=8000)
                        return f"Navigated to account page via {selector}: {page.url}"
                except:
                    continue
            
            # Fallback: try direct URL navigation
            account_url = f"{self.base_url.rstrip('/')}/account"
            print(f"Trying direct account URL: {account_url}")
            page.goto(account_url, wait_until="domcontentloaded", timeout=10000)
            return f"Navigated to account page via direct URL: {page.url}"
            
        except Exception as e:
            return f"Could not navigate to account page: {str(e)}"
    
    def _navigate_to_cart_page(self, page: Page) -> str:
        """Navigate to cart page."""
        try:
            cart_url = f"{self.base_url.rstrip('/')}/cart"
            page.goto(cart_url, wait_until="domcontentloaded", timeout=10000)
            return f"Navigated to cart page: {page.url}"
        except Exception as e:
            return f"Could not navigate to cart page: {str(e)}"
    
    def _navigate_to_search_page(self, page: Page) -> str:
        """Navigate to search page or activate search."""
        try:
            # Try clicking search input to activate search
            search_selectors = [
                'input[type="search"]',
                'input[placeholder*="Search" i]',
                '[data-testid="search"]',
                '.search-input'
            ]
            
            for selector in search_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        element.click()
                        return f"Activated search via {selector}"
                except:
                    continue
            
            return "Search element not found"
            
        except Exception as e:
            return f"Could not activate search: {str(e)}"
    
    def _perform_action(self, page: Page, event_type: str, properties: Dict[str, Any]) -> str:
        """
        Perform the specific action based on event type and properties.
        """
        event_label = properties.get("eventLabel", "")
        event_action = properties.get("eventAction", "")
        page_type = properties.get("page_type", "")
        
        if event_type == "Navigation Clicked":
            if event_label == "mini-cart":
                return self._click_mini_cart(page)
            elif event_label == "search":
                return self._click_search(page)
            elif event_label == "account":
                return self._click_account(page)
            else:
                return self._generic_navigation_click(page, event_label)
        
        elif event_type == "Button Clicked":
            return self._click_button(page, event_label)
        
        elif event_type == "Tab Navigation" or event_type == "Tab" or event_type.lower() == "tab":
            return self._handle_tab_navigation(page, properties)
        
        elif event_type == "Form Submitted":
            return self._submit_form(page, properties)
        
        elif "Page Viewed" in event_type or "Element Viewed" in event_type:
            return self._handle_view_action(page, properties)
        
        else:
            return f"Unhandled event type: {event_type}"
    
    def _click_mini_cart(self, page: Page) -> str:
        """Click on the mini-cart icon."""
        try:
            print("Looking for mini-cart elements...")
            
            # Enhanced selectors for mini-cart on Chewy
            selectors = [
                # Specific cart button/link selectors
                'button[aria-label*="cart" i]',
                'a[aria-label*="cart" i]',
                'button[title*="cart" i]',
                'a[title*="cart" i]',
                
                # Test ID selectors
                '[data-testid="mini-cart"]',
                '[data-testid*="cart"]',
                '[data-qa*="cart"]',
                
                # Common class and href patterns
                'a[href*="/cart"]',
                'button[class*="cart"]',
                '.cart-button',
                '.mini-cart',
                '.cart-icon',
                '#cart',
                
                # SVG and icon selectors
                'svg[class*="cart"] parent::button',
                'svg[class*="cart"] parent::a',
                'i[class*="cart"] parent::button',
                'i[class*="cart"] parent::a',
                
                # Generic cart class selectors
                '[class*="cart"][role="button"]',
                '[class*="cart"]:has(svg)',
                'button:has([class*="cart"])',
                'a:has([class*="cart"])'
            ]
            
            for selector in selectors:
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    if count > 0:
                        print(f"Found {count} elements with selector: {selector}")
                        for i in range(min(count, 3)):  # Try up to 3 elements
                            try:
                                element = elements.nth(i)
                                if element.is_visible(timeout=2000):
                                    print(f"Clicking element {i+1} with selector: {selector}")
                                    element.click()
                                    page.wait_for_load_state("domcontentloaded", timeout=5000)
                                    new_url = page.url
                                    if "cart" in new_url.lower():
                                        return f"✅ Successfully clicked mini-cart using selector: {selector}. Navigated to cart: {new_url}"
                                    else:
                                        return f"✅ Successfully clicked mini-cart using selector: {selector}. Current URL: {new_url}"
                            except Exception as element_error:
                                print(f"Element {i+1} failed: {element_error}")
                                continue
                except Exception as selector_error:
                    continue
            
            # Enhanced fallback: search for any clickable element with "cart" text
            try:
                print("Searching for elements containing 'cart' text...")
                cart_text_elements = page.get_by_text("cart", exact=False)
                count = cart_text_elements.count()
                if count > 0:
                    print(f"Found {count} elements with 'cart' text")
                    for i in range(min(count, 3)):
                        try:
                            element = cart_text_elements.nth(i)
                            if element.is_visible(timeout=2000):
                                element.click()
                                page.wait_for_load_state("domcontentloaded", timeout=5000)
                                return f"✅ Successfully clicked cart element by text. Current URL: {page.url}"
                        except:
                            continue
            except:
                pass
            
            # Final fallback: log available cart-related elements for debugging
            try:
                all_elements = page.evaluate("""
                    () => {
                        const elements = Array.from(document.querySelectorAll('*'))
                        return elements.filter(el => {
                            const text = el.textContent?.toLowerCase() || '';
                            const className = el.className?.toLowerCase() || '';
                            const id = el.id?.toLowerCase() || '';
                            const testId = el.getAttribute('data-testid')?.toLowerCase() || '';
                            const ariaLabel = el.getAttribute('aria-label')?.toLowerCase() || '';
                            const href = el.getAttribute('href')?.toLowerCase() || '';
                            
                            return text.includes('cart') || 
                                   className.includes('cart') || 
                                   id.includes('cart') ||
                                   testId.includes('cart') ||
                                   ariaLabel.includes('cart') ||
                                   href.includes('cart');
                        }).slice(0, 10).map(el => ({
                            tag: el.tagName,
                            class: el.className,
                            id: el.id,
                            text: el.textContent?.slice(0, 50),
                            testId: el.getAttribute('data-testid'),
                            ariaLabel: el.getAttribute('aria-label'),
                            href: el.getAttribute('href'),
                            visible: el.offsetParent !== null
                        }))
                    }
                """)
                print(f"Available cart-related elements: {json.dumps(all_elements, indent=2)}")
            except:
                pass
            
            return "❌ Mini-cart element not found with any selector"
            
        except Exception as e:
            return f"❌ Error clicking mini-cart: {str(e)}"
    
    def _click_search(self, page: Page) -> str:
        """Click on the search icon/button."""
        try:
            selectors = [
                'input[type="search"]',
                'input[placeholder*="Search" i]',
                '[data-testid="search"]',
                '.search-input',
                '#search'
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        element.click()
                        return f"Successfully clicked search. Current URL: {page.url}"
                except:
                    continue
            
            return "Search element not found"
            
        except Exception as e:
            return f"Error clicking search: {str(e)}"
    
    def _click_account(self, page: Page) -> str:
        """Click on the account icon/link."""
        try:
            selectors = [
                'a[href*="account"]',
                '[data-testid="account"]',
                'button[aria-label*="account" i]',
                '.account-link'
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        element.click()
                        page.wait_for_load_state("networkidle", timeout=5000)
                        return f"Successfully clicked account. Current URL: {page.url}"
                except:
                    continue
            
            return "Account element not found"
            
        except Exception as e:
            return f"Error clicking account: {str(e)}"
    
    def _generic_navigation_click(self, page: Page, label: str) -> str:
        """Handle generic navigation clicks by label."""
        try:
            # Try to find element by text content
            element = page.get_by_text(label, exact=False).first
            if element.is_visible(timeout=2000):
                element.click()
                page.wait_for_load_state("networkidle", timeout=5000)
                return f"Clicked navigation element '{label}'. Current URL: {page.url}"
            
            return f"Navigation element '{label}' not found"
            
        except Exception as e:
            return f"Error clicking navigation '{label}': {str(e)}"
    
    def _click_button(self, page: Page, label: str) -> str:
        """Click a button by label with enhanced search icon support."""
        try:
            print(f"Looking for button with label: {label}")
            
            # Special handling for search-related buttons
            if "search" in label.lower():
                return self._click_search_button(page, label)
            
            # Try standard button role first
            try:
                element = page.get_by_role("button", name=label).first
                if element.is_visible(timeout=2000):
                    element.click()
                    return f"✅ Successfully clicked button '{label}'"
            except:
                print(f"Button with exact name '{label}' not found, trying alternatives...")
            
            # Try alternative approaches for button clicking
            button_selectors = [
                f'button[aria-label*="{label}" i]',
                f'button[title*="{label}" i]',
                f'[role="button"][aria-label*="{label}" i]',
                f'input[type="button"][value*="{label}" i]',
                f'input[type="submit"][value*="{label}" i]'
            ]
            
            for selector in button_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        element.click()
                        return f"✅ Successfully clicked button using selector: {selector}"
                except:
                    continue
            
            # Try finding by text content
            try:
                element = page.get_by_text(label, exact=False).first
                if element.is_visible(timeout=2000):
                    element.click()
                    return f"✅ Successfully clicked element with text '{label}'"
            except:
                pass
            
            return f"❌ Button '{label}' not found with any method"
            
        except Exception as e:
            return f"❌ Error clicking button '{label}': {str(e)}"
    
    def _click_search_button(self, page: Page, label: str) -> str:
        """Enhanced search button/icon clicking with multiple strategies."""
        try:
            print("Using enhanced search button detection...")
            
            # Comprehensive search selectors
            search_selectors = [
                # Search input fields (most common)
                'input[type="search"]',
                'input[placeholder*="search" i]',
                'input[placeholder*="Search" i]',
                
                # Search buttons and icons
                'button[aria-label*="search" i]',
                'button[title*="search" i]',
                '[role="button"][aria-label*="search" i]',
                'button:has(svg[class*="search"])',
                'button:has([class*="search"])',
                
                # Search-specific test IDs and classes
                '[data-testid*="search"]',
                '[data-qa*="search"]',
                '.search-button',
                '.search-icon',
                '.search-trigger',
                '#search',
                '#search-button',
                
                # Generic search patterns
                'button[class*="search"]',
                'a[class*="search"]',
                '[class*="search"][onclick]',
                
                # Icon-specific patterns
                'svg[class*="search"] parent::button',
                'i[class*="search"] parent::button',
                '[class*="magnify"] parent::button',
                '[class*="lens"] parent::button',
                
                # Form-related search
                'form[class*="search"] button',
                'form[action*="search"] button[type="submit"]',
                
                # Header/navigation search
                'nav button[aria-label*="search" i]',
                'header button[aria-label*="search" i]',
                '.header button[class*="search"]'
            ]
            
            print(f"Trying {len(search_selectors)} search-specific selectors...")
            
            for i, selector in enumerate(search_selectors):
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    
                    if count > 0:
                        print(f"Found {count} elements with selector: {selector}")
                        
                        # Try each matching element
                        for j in range(min(count, 3)):
                            try:
                                element = elements.nth(j)
                                if element.is_visible(timeout=2000):
                                    print(f"Clicking search element {j+1} with selector: {selector}")
                                    element.click()
                                    page.wait_for_load_state("domcontentloaded", timeout=3000)
                                    return f"✅ Successfully clicked search using selector: {selector}"
                            except Exception as element_error:
                                print(f"Element {j+1} failed: {element_error}")
                                continue
                                
                except Exception as selector_error:
                    continue
            
            # Fallback: Look for any clickable element with search-related text
            try:
                print("Trying text-based search...")
                search_texts = ["Search", "search", "🔍", "Find"]
                
                for search_text in search_texts:
                    elements = page.get_by_text(search_text, exact=False)
                    count = elements.count()
                    
                    if count > 0:
                        print(f"Found {count} elements with text '{search_text}'")
                        for i in range(min(count, 2)):
                            try:
                                element = elements.nth(i)
                                if element.is_visible(timeout=2000):
                                    element.click()
                                    return f"✅ Successfully clicked search by text: '{search_text}'"
                            except:
                                continue
            except:
                pass
            
            # Final fallback: Log available search-related elements for debugging
            try:
                search_elements = page.evaluate("""
                    () => {
                        const elements = Array.from(document.querySelectorAll('*'));
                        return elements.filter(el => {
                            const text = (el.textContent || '').toLowerCase();
                            const className = (el.className && typeof el.className === 'string') ? el.className.toLowerCase() : '';
                            const id = (el.id || '').toLowerCase();
                            const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                            const placeholder = (el.getAttribute('placeholder') || '').toLowerCase();
                            
                            return text.includes('search') || 
                                   className.includes('search') || 
                                   id.includes('search') ||
                                   ariaLabel.includes('search') ||
                                   placeholder.includes('search') ||
                                   el.type === 'search';
                        }).slice(0, 10).map(el => ({
                            tag: el.tagName,
                            text: el.textContent?.slice(0, 50) || '',
                            className: el.className,
                            id: el.id,
                            ariaLabel: el.getAttribute('aria-label'),
                            placeholder: el.getAttribute('placeholder'),
                            type: el.type,
                            visible: el.offsetParent !== null
                        }));
                    }
                """)
                
                if search_elements:
                    print(f"Available search elements: {json.dumps(search_elements, indent=2)}")
                else:
                    print("No search-related elements found on page")
                    
            except:
                pass
            
            return f"❌ Search button/icon not found. Tried {len(search_selectors)} selectors and text patterns."
            
        except Exception as e:
            return f"❌ Error in enhanced search button clicking: {str(e)}"
    
    def _handle_tab_navigation(self, page: Page, properties: Dict[str, Any]) -> str:
        """Handle tab navigation events - simulate pressing Tab key or navigate between UI tabs."""
        try:
            print("Handling tab navigation event...")
            
            # Look for actual tab elements first (like product info tabs, reviews tabs, etc.)
            tab_selectors = [
                # Common tab patterns
                '[role="tab"]',
                '.tab',
                '.tabs [role="button"]',
                '[data-testid*="tab"]',
                '.tab-button',
                '.tab-link',
                
                # Product page tabs
                '.product-tabs [role="button"]',
                '.product-info-tabs button',
                '[aria-selected]',
                
                # Review/info tabs
                '.reviews-tab',
                '.description-tab',
                '.specifications-tab',
                '.ingredients-tab',
                
                # Navigation tabs
                'nav [role="tab"]',
                '.navigation-tabs button'
            ]
            
            print(f"Searching for tab elements with {len(tab_selectors)} selectors...")
            
            found_tabs = []
            for selector in tab_selectors:
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    if count > 0:
                        print(f"Found {count} tab elements with selector: {selector}")
                        found_tabs.append((selector, count))
                        
                        # Try to interact with the first tab
                        element = elements.first
                        if element.is_visible(timeout=2000):
                            # Get tab information
                            tab_info = element.evaluate("""
                                el => ({
                                    text: el.textContent?.trim() || '',
                                    ariaLabel: el.getAttribute('aria-label') || '',
                                    ariaSelected: el.getAttribute('aria-selected') || '',
                                    role: el.getAttribute('role') || '',
                                    className: el.className || '',
                                    tagName: el.tagName
                                })
                            """)
                            
                            print(f"Tab info: {json.dumps(tab_info, indent=2)}")
                            
                            # Click the tab if it's not already selected
                            if tab_info.get('ariaSelected') != 'true':
                                element.click()
                                page.wait_for_load_state("domcontentloaded", timeout=3000)
                                return f"✅ Successfully clicked tab using {selector}. Tab info: {tab_info.get('text', 'No text')} | {tab_info.get('ariaLabel', 'No aria-label')}"
                            else:
                                return f"✅ Tab already selected: {tab_info.get('text', 'No text')} | {tab_info.get('ariaLabel', 'No aria-label')}"
                                
                except Exception as selector_error:
                    continue
            
            # Fallback: Look for any clickable elements with "tab" in text or class
            try:
                print("Searching for elements with 'tab' in text or classes...")
                tab_text_elements = page.get_by_text("tab", exact=False)
                count = tab_text_elements.count()
                
                if count > 0:
                    print(f"Found {count} elements with 'tab' text")
                    element = tab_text_elements.first
                    if element.is_visible(timeout=2000):
                        text = element.text_content()
                        element.click()
                        return f"✅ Clicked tab by text: '{text}'"
            except:
                pass
            
            # Alternative: Simulate keyboard Tab navigation
            try:
                print("Attempting keyboard Tab navigation...")
                page.keyboard.press("Tab")
                
                # Get the currently focused element
                focused_element = page.evaluate("""
                    () => {
                        const active = document.activeElement;
                        if (active) {
                            return {
                                tagName: active.tagName,
                                text: active.textContent?.slice(0, 50) || '',
                                className: active.className || '',
                                id: active.id || '',
                                type: active.type || '',
                                role: active.getAttribute('role') || ''
                            };
                        }
                        return null;
                    }
                """)
                
                if focused_element:
                    return f"✅ Tab navigation completed. Focused element: {json.dumps(focused_element, indent=2)}"
                else:
                    return "✅ Tab navigation completed, but no specific element focused"
                    
            except Exception as keyboard_error:
                print(f"Keyboard tab navigation failed: {keyboard_error}")
            
            # Summary of what we found
            if found_tabs:
                tab_summary = ", ".join([f"{selector} ({count} elements)" for selector, count in found_tabs[:3]])
                return f"✅ Found tab elements but couldn't interact: {tab_summary}"
            else:
                return "❌ No tab elements found on the page"
            
        except Exception as e:
            return f"❌ Error handling tab navigation: {str(e)}"
    
    def _submit_form(self, page: Page, properties: Dict[str, Any]) -> str:
        """Submit a form based on properties."""
        try:
            # This would be customized based on specific form requirements
            return "Form submission logic not yet implemented"
        except Exception as e:
            return f"Error submitting form: {str(e)}"
    
    def _handle_view_action(self, page: Page, properties: Dict[str, Any]) -> str:
        """Handle view/visibility actions."""
        try:
            event_category = properties.get("eventCategory", "")
            event_action = properties.get("eventAction", "")
            
            if "mini-cart" in event_category:
                return self._view_mini_cart(page)
            elif "subtotal" in event_action:
                return self._view_subtotal(page)
            else:
                return f"Viewed element: {event_category} - {event_action}. Current URL: {page.url}"
                
        except Exception as e:
            return f"Error handling view action: {str(e)}"
    
    def _view_mini_cart(self, page: Page) -> str:
        """View/inspect the mini-cart without clicking."""
        try:
            print("Performing deep search for mini-cart elements...")
            
            # First, let's get ALL possible cart-related elements on the page
            all_cart_elements = page.evaluate("""
                () => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    const cartElements = [];
                    
                    elements.forEach(el => {
                        const text = (el.textContent || '').toLowerCase();
                        const className = (el.className && typeof el.className === 'string') ? el.className.toLowerCase() : '';
                        const id = (el.id || '').toLowerCase();
                        const testId = (el.getAttribute('data-testid') || '').toLowerCase();
                        const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                        const href = (el.getAttribute('href') || '').toLowerCase();
                        const role = (el.getAttribute('role') || '').toLowerCase();
                        
                        // More comprehensive cart detection
                        const isCartRelated = 
                            text.includes('cart') || text.includes('bag') || text.includes('basket') ||
                            className.includes('cart') || className.includes('bag') || className.includes('basket') ||
                            className.includes('minicart') || className.includes('mini-cart') ||
                            id.includes('cart') || id.includes('bag') || id.includes('basket') ||
                            testId.includes('cart') || testId.includes('bag') ||
                            ariaLabel.includes('cart') || ariaLabel.includes('bag') ||
                            href.includes('/cart') || href.includes('/bag') ||
                            text.includes('shopping') || text.includes('checkout') ||
                            text.match(/\\$\\d+/) || text.match(/\\d+\\s*item/) ||
                            className.includes('total') || className.includes('subtotal') ||
                            className.includes('price') || className.includes('count');
                        
                        if (isCartRelated && el.offsetParent !== null) {
                            cartElements.push({
                                tag: el.tagName,
                                text: text.slice(0, 100),
                                className: className.slice(0, 100),
                                id: id,
                                testId: testId,
                                ariaLabel: ariaLabel,
                                href: href,
                                role: role,
                                visible: true,
                                bounds: el.getBoundingClientRect(),
                                hasChildren: el.children.length > 0,
                                parentTag: el.parentElement?.tagName || '',
                                xpath: getXPath(el)
                            });
                        }
                    });
                    
                    function getXPath(element) {
                        try {
                            if (!element) return '';
                            if (element.id) return `//*[@id="${element.id}"]`;
                            
                            let path = '';
                            let current = element;
                            while (current && current.nodeType === Node.ELEMENT_NODE) {
                                let index = 1;
                                let siblings = current.parentNode?.children || [];
                                for (let i = 0; i < siblings.length; i++) {
                                    if (siblings[i] === current) {
                                        index = i + 1;
                                        break;
                                    }
                                }
                                path = `/${current.tagName.toLowerCase()}[${index}]` + path;
                                current = current.parentElement;
                                if (path.split('/').length > 6) break; // Limit depth
                            }
                            return path;
                        } catch (e) {
                            return '';
                        }
                    }
                    
                    return cartElements.slice(0, 20); // Return top 20 matches
                }
            """)
            
            print(f"Found {len(all_cart_elements)} cart-related elements")
            
            if not all_cart_elements:
                # Fallback: Try common e-commerce patterns
                return self._fallback_cart_search(page)
            
            # Try to interact with the most promising elements
            promising_elements = []
            
            for element_info in all_cart_elements:
                score = self._score_cart_element(element_info)
                promising_elements.append((score, element_info))
            
            # Sort by score (highest first)
            promising_elements.sort(key=lambda x: x[0], reverse=True)
            
            print(f"Top 5 promising cart elements:")
            for i, (score, elem) in enumerate(promising_elements[:5]):
                print(f"   {i+1}. Score: {score} | {elem['tag']} | Text: '{elem['text'][:50]}' | Class: '{elem['className'][:30]}'")
            
            # Try to interact with top elements (skip very low scores)
            for score, element_info in promising_elements[:10]:
                try:
                    if score < 2:  # Skip very low-scoring elements
                        print(f"Skipping low-score element: {element_info['tag']} (score: {score})")
                        continue
                    
                    # Skip empty SVGs without meaningful attributes    
                    if (element_info['tag'].upper() == 'SVG' and 
                        not element_info['text'].strip() and 
                        not element_info['ariaLabel'] and 
                        not element_info['testId']):
                        print(f"Skipping empty SVG element")
                        continue
                        
                    success = self._try_interact_with_element(page, element_info)
                    if success and "✅" in success:
                        return success
                        
                except Exception as e:
                    print(f"❌ Failed to interact with element: {e}")
                    continue
            
            # If we get here, log all found elements for debugging
            print("All cart elements found:")
            for i, elem in enumerate(all_cart_elements[:10]):
                print(f"{i+1}. {elem['tag']} | '{elem['text'][:30]}' | Class: '{elem['className'][:20]}'")
            
            return "❌ Mini-cart elements found but could not interact with any successfully"
            
        except Exception as e:
            return f"❌ Error in deep cart search: {str(e)}"
    
    def _score_cart_element(self, element_info: Dict) -> int:
        """Score cart elements by likelihood of being the mini-cart."""
        score = 0
        text = element_info['text'].lower()
        className = element_info['className'].lower()
        tag = element_info['tag'].lower()
        
        # Penalize elements with no text content
        if not text.strip():
            score -= 5
        
        # High-value indicators
        if 'mini-cart' in className or 'minicart' in className:
            score += 10
        if 'cart' in element_info['testId']:
            score += 8
        if 'cart' in element_info['ariaLabel']:
            score += 8
        if '/cart' in element_info['href']:
            score += 7
        
        # Boost for cart text content
        if 'cart' in text:
            score += 8
            if 'empty' in text:
                score += 5  # "cart is empty" is very specific
            if 'item' in text:
                score += 3
        
        # Medium-value indicators
        if 'cart' in className:
            score += 5
        if tag in ['button', 'a', 'div']:  # Clickable or container elements
            score += 2
        if '$' in text or 'total' in text or 'subtotal' in text:
            score += 4
        
        # Bonus for meaningful text length
        if len(text.strip()) > 10:
            score += 3
        elif len(text.strip()) > 3:
            score += 1
        
        # Penalize SVG without meaningful attributes
        if tag == 'svg' and not element_info['ariaLabel'] and not element_info['testId']:
            score -= 3
        
        # Bonus for specific patterns
        if 'shopping' in text:
            score += 2
        if 'checkout' in text:
            score += 2
        if element_info['hasChildren'] and len(text) > 5:  # Complex elements with content
            score += 2
        
        return max(score, 0)  # Ensure non-negative score
    
    def _try_interact_with_element(self, page: Page, element_info: Dict) -> str:
        """Try to interact with a specific cart element."""
        try:
            print(f"Trying to interact with: {element_info['tag']} | Text: '{element_info['text'][:50]}' | Class: '{element_info['className'][:30]}'")
            
            # Build multiple selector strategies
            selectors_to_try = []
            
            # Strategy 1: ID selector
            if element_info['id']:
                selectors_to_try.append(f"#{element_info['id']}")
                print(f"   Added ID selector: #{element_info['id']}")
            
            # Strategy 2: Test ID selector  
            if element_info['testId']:
                selectors_to_try.append(f"[data-testid='{element_info['testId']}']")
                print(f"   Added test-id selector: [data-testid='{element_info['testId']}']")
            
            # Strategy 3: Class selector (use individual classes)
            if element_info['className']:
                classes = element_info['className'].strip().split()
                for cls in classes[:2]:  # Try first 2 classes
                    if cls and len(cls) > 2 and not cls.startswith('_'):  # Skip very short or generated class names
                        clean_cls = cls.replace('__', '-').replace(':', '')
                        if clean_cls:
                            selectors_to_try.append(f".{clean_cls}")
                            print(f"   Added class selector: .{clean_cls}")
            
            # Strategy 4: Attribute selectors for common patterns
            if 'cart' in element_info['className'].lower():
                selectors_to_try.append(f"{element_info['tag'].lower()}[class*='cart']")
                print(f"   Added attribute selector for cart class")
            
            # Strategy 5: Text-based selector (for elements with specific cart text)
            if element_info['text'] and 'cart' in element_info['text'].lower():
                # Try to find by partial text match
                text_words = element_info['text'].strip().split()[:3]  # First 3 words
                for word in text_words:
                    if len(word) > 3 and word.lower() in ['cart', 'empty', 'items']:
                        selectors_to_try.append(f":has-text('{word}')")
                        print(f"   Added text selector: :has-text('{word}')")
            
            # Strategy 6: Parent-child relationship
            if element_info['parentTag']:
                parent_tag = element_info['parentTag'].lower()
                selectors_to_try.append(f"{parent_tag} > {element_info['tag'].lower()}")
                print(f"   Added parent-child selector")
            
            # Try each selector strategy
            for i, selector in enumerate(selectors_to_try):
                try:
                    print(f"   Trying selector {i+1}: {selector}")
                    
                    # Handle XPath differently
                    if selector.startswith('/'):
                        continue  # Skip XPath for now as it needs special handling
                    
                    # Locate element
                    element = page.locator(selector).first
                    
                    # Check if element exists and is visible
                    if element.count() == 0:
                        print(f"   ❌ Element not found with {selector}")
                        continue
                        
                    if not element.is_visible(timeout=2000):
                        print(f"   ❌ Element not visible with {selector}")
                        continue
                    
                    print(f"   ✅ Found visible element with {selector}")
                    
                    # For viewing action, extract information without clicking
                    info = element.evaluate("""
                        el => {
                            try {
                                const rect = el.getBoundingClientRect();
                                return {
                                    text: el.textContent?.slice(0, 200) || '',
                                    tag: el.tagName,
                                    visible: el.offsetParent !== null,
                                    bounds: {
                                        x: rect.x,
                                        y: rect.y, 
                                        width: rect.width,
                                        height: rect.height
                                    },
                                    computedStyle: window.getComputedStyle(el).display,
                                    className: el.className,
                                    id: el.id,
                                    innerHTML: el.innerHTML?.slice(0, 300) || '',
                                    children: el.children.length
                                };
                            } catch (e) {
                                return { error: e.toString() };
                            }
                        }
                    """)
                    
                    # Check if we got useful cart information
                    if info and not info.get('error'):
                        text = info.get('text', '').lower()
                        innerHTML = info.get('innerHTML', '').lower()
                        
                        # Look for cart-specific content
                        cart_indicators = ['cart', 'item', 'total', 'subtotal', '$', 'empty', 'checkout', 'bag']
                        found_indicators = [ind for ind in cart_indicators if ind in text or ind in innerHTML]
                        
                        if found_indicators:
                            return f"✅ Successfully viewed mini-cart using {selector}. Found indicators: {found_indicators}. Content: {json.dumps(info, indent=2)}"
                        else:
                            print(f"   Element found but no cart indicators in content")
                            continue
                    else:
                        print(f"   ❌ Error extracting element info: {info.get('error', 'Unknown error')}")
                        continue
                        
                except Exception as selector_error:
                    print(f"   ❌ Selector {selector} failed: {str(selector_error)}")
                    continue
            
            # If we get here, none of the selectors worked
            return f"❌ Could not interact with element. Tried {len(selectors_to_try)} selectors: {selectors_to_try[:3]}"
            
        except Exception as e:
            return f"❌ Error in interaction attempt: {str(e)}"
    
    def _fallback_cart_search(self, page: Page) -> str:
        """Fallback search when no obvious cart elements found."""
        try:
            print("Running fallback search patterns...")
            
            # Try searching for common e-commerce patterns
            fallback_patterns = [
                "Shopping Cart",
                "My Cart", 
                "Bag",
                "Checkout",
                "$",
                "item",
                "total",
                "subtotal"
            ]
            
            found_elements = []
            
            for pattern in fallback_patterns:
                try:
                    elements = page.get_by_text(pattern, exact=False)
                    count = elements.count()
                    if count > 0:
                        found_elements.append(f"{pattern}: {count} elements")
                        
                        # Try to get info from first matching element
                        element = elements.first
                        if element.is_visible(timeout=1000):
                            text = element.text_content()
                            if text and len(text) < 200:
                                return f"✅ Fallback found cart-related content '{pattern}': {text[:100]}"
                except:
                    continue
            
            if found_elements:
                return f"✅ Fallback search found: {', '.join(found_elements)}"
            else:
                return "❌ Even event fallback search found no cart-related elements"
                
        except Exception as e:
            return f"❌ Fallback search error: {str(e)}"
    
    def _view_subtotal(self, page: Page) -> str:
        """View subtotal information."""
        try:
            print("Looking for subtotal information...")
            
            subtotal_selectors = [
                '[class*="subtotal"]',
                '[data-testid*="subtotal"]',
                '.cart-subtotal',
                '.total',
                '[class*="total"]'
            ]
            
            for selector in subtotal_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        text = element.text_content()
                        return f"✅ Subtotal viewed: {text}"
                except:
                    continue
            
            return "❌ Subtotal information not found"
            
        except Exception as e:
            return f"❌ Error viewing subtotal: {str(e)}"
    
    def _handle_hover_action(self, page: Page, properties: Dict[str, Any]) -> str:
        """Handle hover actions."""
        try:
            event_label = properties.get("eventLabel", "")
            event_category = properties.get("eventCategory", "")
            
            target = event_label or event_category
            if target:
                element = page.get_by_text(target, exact=False).first
                if element.is_visible(timeout=2000):
                    element.hover()
                    return f"✅ Hovered over: {target}"
            
            return f"❌ Could not find element to hover: {target}"
            
        except Exception as e:
            return f"❌ Error hovering: {str(e)}"
    
    def _handle_generic_action(self, page: Page, properties: Dict[str, Any]) -> str:
        """Handle any generic action based on properties."""
        try:
            event_category = properties.get("eventCategory", "")
            event_action = properties.get("eventAction", "")
            event_label = properties.get("eventLabel", "")
            
            action_summary = f"Category: {event_category}, Action: {event_action}, Label: {event_label}"
            
            # Try to find and interact with relevant elements
            if event_label:
                try:
                    element = page.get_by_text(event_label, exact=False).first
                    if element.is_visible(timeout=2000):
                        if "click" in event_action:
                            element.click()
                            return f"✅ Clicked element: {event_label}"
                        else:
                            return f"✅ Found element: {event_label} - {action_summary}"
                except:
                    pass
            
            return f"✅ Processed generic action: {action_summary}. Current URL: {page.url}"
        except Exception as e:
            return f"❌ Error handling generic action: {str(e)}"


def main():
    """Example usage of the Chewy Automation Agent with flexible JSON."""
    
    # Test different JSON formats
    test_scenarios = [
        {
            "name": "Flexible JSON - Mini-cart subtotal view",
            "environment": "qat",
            "event": {
                "properties": {
                    "page_type": "home",
                    "eventCategory": "mini-cart",
                    "eventAction": "subtotal-view"
                }
            }
        },
        {
            "name": "Standard JSON - Account page mini-cart click",
            "environment": "qat",
            "event": {
                "event": "Navigation Clicked",
                "properties": {
                    "page_type": "Account",
                    "eventCategory": "browse-nav",
                    "eventAction": "clicked",
                    "eventLabel": "mini-cart"
                }
            }
        },
        {
            "name": "Root-level properties",
            "environment": "qat",
            "event": {
                "page_type": "product",
                "eventCategory": "product-action",
                "eventAction": "view",
                "eventLabel": "Add to Cart"
            }
        }
    ]
    
    # Run first scenario by default
    scenario = test_scenarios[0]
    print(f"\nRunning scenario: {scenario['name']}")
    print(f"Environment: {scenario['environment']}")
    print(f"Event JSON: {json.dumps(scenario['event'], indent=2)}")
    print("="*60)
    
    # Create agent and execute
    agent = ChewyAutomationAgent(environment=scenario['environment'])
    result = agent.execute_event(scenario['event'])
    
    # Print results
    print("\n" + "="*60)
    print("CHEWY AUTOMATION AGENT - EXECUTION REPORT")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("="*60)
    print(f"\nAgent completed the event at hour: {result.get('hour')}")
    print(f"Full timestamp: {result.get('completed_at')}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
