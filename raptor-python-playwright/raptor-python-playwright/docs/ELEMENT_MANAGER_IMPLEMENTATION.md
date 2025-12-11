# Element Manager Implementation

## Overview

The Element Manager is a core component of the RAPTOR framework that provides robust element location and interaction capabilities with automatic fallback strategies.

## Features

### 1. Multiple Locator Strategies

The Element Manager supports the following locator strategies:

- **CSS Selectors**: `css=#element-id` or `#element-id` (default)
- **XPath**: `xpath=//div[@class='test']`
- **Text Content**: `text=Click Me`
- **Role-based**: `role=button[name='Submit']`
- **ID**: `id=element-id`

### 2. Automatic Fallback Mechanism

When the primary locator fails, the Element Manager automatically tries fallback locators in order:

```python
element = await element_manager.locate_element(
    "css=#primary-id",  # Try this first
    fallback_locators=[
        "xpath=//button[@id='primary-id']",  # Then this
        "text=Submit"  # Finally this
    ]
)
```

### 3. Configurable Timeouts

All operations support custom timeouts:

```python
# Use default timeout from config
element = await element_manager.locate_element("css=#button")

# Use custom timeout (2 seconds)
element = await element_manager.locate_element("css=#button", timeout=2000)
```

### 4. Wait Conditions

Wait for elements to reach specific states:

```python
# Wait for element to be visible
await element_manager.wait_for_element("css=#loading", state="visible")

# Wait for element to be hidden
await element_manager.wait_for_element("css=#spinner", state="hidden")

# Wait for element to be attached to DOM
await element_manager.wait_for_element("css=#dynamic", state="attached")
```

### 5. Element State Checks

Convenient methods for checking element states:

```python
# Check if element is visible
is_visible = await element_manager.is_visible("css=#button")

# Check if element is hidden
is_hidden = await element_manager.is_hidden("css=#modal")

# Count matching elements
count = await element_manager.get_element_count("css=.item")
```

## API Reference

### ElementManager Class

#### Constructor

```python
ElementManager(page: Page, config: Optional[ConfigManager] = None)
```

**Parameters:**
- `page`: Playwright Page instance
- `config`: Optional ConfigManager for timeout configuration

#### Methods

##### locate_element()

```python
async def locate_element(
    locator: str,
    fallback_locators: Optional[List[str]] = None,
    timeout: Optional[int] = None,
) -> Locator
```

Locate an element using primary locator with automatic fallback.

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locators
- `timeout`: Optional timeout in milliseconds

**Returns:** Playwright Locator object

**Raises:** `ElementNotFoundException` if element cannot be found

##### wait_for_element()

```python
async def wait_for_element(
    locator: str,
    state: str = "visible",
    timeout: Optional[int] = None,
) -> Locator
```

Wait for an element to reach a specific state.

**Parameters:**
- `locator`: Locator string
- `state`: Element state ("visible", "hidden", "attached", "detached")
- `timeout`: Optional timeout in milliseconds

**Returns:** Playwright Locator object

**Raises:** `TimeoutException` if element doesn't reach desired state

##### is_visible()

```python
async def is_visible(locator: str, timeout: Optional[int] = None) -> bool
```

Check if an element is visible.

**Returns:** True if visible, False otherwise

##### is_hidden()

```python
async def is_hidden(locator: str, timeout: Optional[int] = None) -> bool
```

Check if an element is hidden.

**Returns:** True if hidden, False otherwise

##### get_element_count()

```python
async def get_element_count(locator: str) -> int
```

Get the count of elements matching the locator.

**Returns:** Number of matching elements

##### get_default_timeout()

```python
def get_default_timeout() -> int
```

Get the default timeout value in milliseconds.

##### set_default_timeout()

```python
def set_default_timeout(timeout_ms: int) -> None
```

Set the default timeout value in milliseconds.

## Usage Examples

### Basic Element Location

```python
from raptor.core.element_manager import ElementManager
from raptor.core.browser_manager import BrowserManager

# Initialize
browser_manager = BrowserManager()
await browser_manager.launch_browser("chromium")
page = await browser_manager.create_page()

element_manager = ElementManager(page)

# Locate element
element = await element_manager.locate_element("css=#submit-button")
await element.click()
```

### Using Fallback Locators

```python
# Try multiple strategies
element = await element_manager.locate_element(
    "css=#submit-btn",
    fallback_locators=[
        "xpath=//button[@type='submit']",
        "text=Submit",
        "role=button[name='Submit']"
    ]
)
```

### Waiting for Dynamic Elements

```python
# Wait for loading spinner to disappear
await element_manager.wait_for_element(
    "css=#loading-spinner",
    state="hidden",
    timeout=10000
)

# Wait for content to appear
await element_manager.wait_for_element(
    "css=#content",
    state="visible",
    timeout=5000
)
```

### Checking Element States

```python
# Check if element exists and is visible
if await element_manager.is_visible("css=#modal"):
    print("Modal is visible")

# Count items in a list
item_count = await element_manager.get_element_count("css=.list-item")
print(f"Found {item_count} items")
```

### Custom Timeouts

```python
# Set global default timeout
element_manager.set_default_timeout(15000)  # 15 seconds

# Use custom timeout for specific operation
element = await element_manager.locate_element(
    "css=#slow-element",
    timeout=30000  # 30 seconds for this specific element
)
```

## Error Handling

The Element Manager provides detailed error information:

```python
from raptor.core.exceptions import ElementNotFoundException, TimeoutException

try:
    element = await element_manager.locate_element(
        "css=#nonexistent",
        fallback_locators=["xpath=//div[@id='also-missing']"],
        timeout=5000
    )
except ElementNotFoundException as e:
    print(f"Element not found: {e.message}")
    print(f"Primary locator: {e.context['primary_locator']}")
    print(f"Fallback locators tried: {e.context['fallback_locators']}")
    print(f"Page URL: {e.context['page_url']}")
except TimeoutException as e:
    print(f"Operation timed out: {e.message}")
    print(f"Timeout: {e.context['timeout_seconds']} seconds")
```

## Best Practices

### 1. Use Specific Locators

Prefer specific locators over generic ones:

```python
# Good - specific and unique
"css=#submit-button"
"xpath=//button[@data-testid='submit']"

# Avoid - too generic
"css=button"
"xpath=//div"
```

### 2. Provide Fallback Strategies

Always provide fallback locators for critical elements:

```python
element = await element_manager.locate_element(
    "css=#primary-id",
    fallback_locators=[
        "xpath=//button[@id='primary-id']",
        "text=Submit",
        "role=button"
    ]
)
```

### 3. Use Appropriate Timeouts

Set timeouts based on expected element behavior:

```python
# Quick elements - short timeout
await element_manager.locate_element("css=#static-element", timeout=2000)

# Dynamic/AJAX elements - longer timeout
await element_manager.locate_element("css=#ajax-content", timeout=10000)

# Very slow loading - custom timeout
await element_manager.locate_element("css=#slow-chart", timeout=30000)
```

### 4. Check Element States

Verify element states before interactions:

```python
# Wait for element to be visible before clicking
if await element_manager.is_visible("css=#button"):
    element = await element_manager.locate_element("css=#button")
    await element.click()
```

### 5. Use Context Manager

Use async context manager for automatic cleanup:

```python
async with ElementManager(page, config) as em:
    element = await em.locate_element("css=#button")
    await element.click()
# Automatic cleanup happens here
```

## Integration with Other Components

### With Browser Manager

```python
browser_manager = BrowserManager()
await browser_manager.launch_browser("chromium")
page = await browser_manager.create_page()

element_manager = ElementManager(page)
```

### With Config Manager

```python
config = ConfigManager()
config.load_config("staging")

element_manager = ElementManager(page, config)
# Uses timeout settings from staging config
```

## Performance Considerations

1. **Locator Efficiency**: CSS selectors are generally faster than XPath
2. **Fallback Order**: Place most likely successful locators first
3. **Timeout Tuning**: Use shorter timeouts for fast elements to fail fast
4. **Element Caching**: Reuse located elements when possible

## Troubleshooting

### Element Not Found

If elements are consistently not found:

1. Verify the locator is correct using browser DevTools
2. Check if element is in an iframe
3. Ensure page has fully loaded
4. Increase timeout if element loads slowly
5. Try different locator strategies

### Timeout Issues

If operations frequently timeout:

1. Increase default timeout in configuration
2. Check network conditions
3. Verify element actually appears on page
4. Use wait conditions before locating elements

### Fallback Not Working

If fallback locators aren't being tried:

1. Verify fallback locators are valid
2. Check logs for detailed error messages
3. Ensure timeout is sufficient for all attempts
4. Test each locator individually

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 2.1**: Multiple locator strategies (CSS, XPath, text, role, ID)
- **Requirement 2.2**: Automatic fallback locator mechanism
- **Requirement 5.1**: Configurable wait and timeout handling
- **Requirement 11.1**: Comprehensive error handling with context preservation

## Next Steps

The Element Manager provides the foundation for:

1. **Element Interaction Methods** (Task 6): click, fill, select, hover
2. **Advanced Click Methods** (Task 7): clickXY, double-click, right-click
3. **Element State Methods** (Task 8): get_text, get_attribute, get_value
4. **Synchronization Methods** (Task 9): wait_for_load_state, wait_for_spinner
