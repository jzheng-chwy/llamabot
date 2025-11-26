# Chewy Automation Agent

An OpenAI-powered agent that performs automated actions on the Chewy website based on JSON event data.

## Features

- Takes JSON event data with categories like "Navigation Clicked", "Button Clicked", etc.
- Navigates to the Chewy website (dev environment)
- Performs the specified action (e.g., clicking mini-cart, search, account)
- Reports the hour when the event was completed
- Provides detailed execution logs

## Setup

1. Install dependencies:
```bash
poetry install
# or
pip install openai playwright python-dotenv
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Create a `.env` file with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

```python
from chewy_agent import ChewyAutomationAgent

# Create the agent
agent = ChewyAutomationAgent()

# Define your event
event_data = {
    "event": "Navigation Clicked",
    "properties": {
        "page_type": "Account",
        "eventCategory": "browse-nav",
        "eventAction": "clicked",
        "eventLabel": "mini-cart"
    }
}

# Execute the event
result = agent.execute_event(event_data)

# Check results
print(f"Completed at hour: {result['hour']}")
print(f"Full timestamp: {result['completed_at']}")
print(f"Status: {result['status']}")
```

### Run the Example

```bash
python chewy_agent.py
```

## Supported Events

### Navigation Clicked
- `mini-cart` - Clicks the shopping cart icon
- `search` - Clicks the search bar
- `account` - Clicks the account/profile icon

### Button Clicked
- Clicks any button by its label/text

### Form Submitted
- Form submission support (customizable)

### Page Viewed
- Records page view events

## Example JSON Events

### Mini-Cart Click
```json
{
  "event": "Navigation Clicked",
  "properties": {
    "page_type": "Account",
    "eventCategory": "browse-nav",
    "eventAction": "clicked",
    "eventLabel": "mini-cart"
  }
}
```

### Search Click
```json
{
  "event": "Navigation Clicked",
  "properties": {
    "eventCategory": "header-nav",
    "eventAction": "clicked",
    "eventLabel": "search"
  }
}
```

### Button Click
```json
{
  "event": "Button Clicked",
  "properties": {
    "eventCategory": "product-action",
    "eventAction": "clicked",
    "eventLabel": "Add to Cart"
  }
}
```

## Response Format

The agent returns a detailed response:

```json
{
  "status": "success",
  "event": "Navigation Clicked",
  "properties": {
    "page_type": "Account",
    "eventCategory": "browse-nav",
    "eventAction": "clicked",
    "eventLabel": "mini-cart"
  },
  "completed_at": "2025-11-26 14:30:45",
  "hour": 14,
  "duration_seconds": 3.2,
  "result": "Successfully clicked mini-cart. Current URL: https://www-dev.chewy.net/cart"
}
```

## Configuration

- **Base URL**: `https://www-dev.chewy.net/` (configured in the agent)
- **Headless Mode**: Set to `False` by default (you can see the browser). Change to `True` in the code for headless operation.
- **Timeout**: 5 seconds for network idle state

## Extending the Agent

To add support for new events, extend the `_perform_action` method in `chewy_agent.py`:

```python
def _perform_action(self, page: Page, event_type: str, properties: Dict[str, Any]) -> str:
    # Add your custom event handling here
    if event_type == "Your New Event":
        return self._your_custom_handler(page, properties)
```

## Troubleshooting

- **Element not found**: The agent uses multiple selector strategies. If an element isn't found, you may need to add custom selectors for that specific element.
- **Browser issues**: Make sure Playwright is properly installed: `playwright install chromium`
- **API key**: Ensure your `.env` file contains a valid OpenAI API key
