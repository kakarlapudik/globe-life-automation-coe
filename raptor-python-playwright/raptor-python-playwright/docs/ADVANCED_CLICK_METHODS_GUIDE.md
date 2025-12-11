# Advanced Click Methods - Developer Guide

## Quick Reference

This guide provides practical examples for using the advanced click methods in the RAPTOR Python Playwright Framework.

## Table of Contents
1. [click_at_position()](#click_at_position)
2. [double_click()](#double_click)
3. [right_click()](#right_click)
4. [click_if_exists()](#click_if_exists)
5. [click_with_retry()](#click_with_retry)
6. [Common Patterns](#common-patterns)

---

## click_at_position()

**Use Case**: Click at a specific coordinate within an element (canvas, map, image, etc.)

### Basic Usage
```python
# Click at position (100, 50) in a canvas
await element_manager.click_at_position("css=#canvas", x=100, y=50)
```

### With Options
```python
# Right-click at position
await element_manager.click_at_position(
    "css=#map",
    x=200,
    y=150,
    button="right"
)

# Double-click at position
await element_manager.click_at_position(
    "css=#drawing-area",
    x=300,
    y=200,
    click_count=2
)
```

### With Fallback
```python
# Try multiple locators
await element_manager.click_at_position(
    "css=#interactive-map",
    x=150,
    y=100,
    fallback_locators=["id=map-container", "xpath=//div[@class='map']"]
)
```

### Real-World Examples
```python
# Click on a specific point in a chart
await element_manager.click_at_position("css=#sales-chart", x=250, y=180)

# Click on a map marker
await element_manager.click_at_position("css=#google-map", x=400, y=300)

# Click on a specific area of an image
await element_manager.click_at_position("css=#product-image", x=50, y=75)
```

---

## double_click()

**Use Case**: Double-click to select text, open files, or trigger double-click events

### Basic Usage
```python
# Double-click a file item
await element_manager.double_click("css=#file-item")
```

### With Options
```python
# Double-click with delay between clicks
await element_manager.double_click(
    "css=#text-field",
    delay=100  # 100ms delay between clicks
)

# Double-click at specific position
await element_manager.double_click(
    "css=#document",
    position={"x": 50, "y": 20}
)
```

### With Fallback
```python
# Try multiple locators
await element_manager.double_click(
    "text=Document.txt",
    fallback_locators=["css=.file-item", "xpath=//div[@data-file='document']"]
)
```

### Real-World Examples
```python
# Open a file in file explorer
await element_manager.double_click("css=.file-item[data-name='report.pdf']")

# Select a word in text editor
await element_manager.double_click("css=#editor-content")

# Open a folder
await element_manager.double_click("css=.folder-icon[data-folder='Documents']")

# Expand a tree node
await element_manager.double_click("css=.tree-node[data-id='node-123']")
```

---

## right_click()

**Use Case**: Open context menus or trigger right-click events

### Basic Usage
```python
# Right-click to open context menu
await element_manager.right_click("css=#context-target")
```

### With Options
```python
# Right-click at specific position
await element_manager.right_click(
    "css=#file-item",
    position={"x": 10, "y": 10}
)

# Right-click with delay
await element_manager.right_click(
    "css=#menu-trigger",
    delay=50
)
```

### With Fallback
```python
# Try multiple locators
await element_manager.right_click(
    "text=File Item",
    fallback_locators=["css=.file", "xpath=//div[@class='item']"]
)
```

### Real-World Examples
```python
# Open file context menu
await element_manager.right_click("css=.file-item[data-name='document.txt']")

# Open text editor context menu
await element_manager.right_click("css=#editor-content")

# Open table row context menu
await element_manager.right_click("css=tr[data-id='row-5']")

# Open image context menu
await element_manager.right_click("css=#product-image")
```

---

## click_if_exists()

**Use Case**: Conditionally click optional elements (popups, banners, modals)

### Basic Usage
```python
# Try to close optional popup
clicked = await element_manager.click_if_exists("css=#popup-close")
if clicked:
    print("Popup was closed")
else:
    print("No popup found")
```

### With Custom Timeout
```python
# Use shorter timeout for quick check
clicked = await element_manager.click_if_exists(
    "css=#cookie-banner-accept",
    timeout=2000  # 2 seconds
)
```

### With Fallback
```python
# Try multiple locators
clicked = await element_manager.click_if_exists(
    "css=#modal-close",
    fallback_locators=["css=.close-button", "text=Close"]
)
```

### Real-World Examples
```python
# Close cookie banner if present
await element_manager.click_if_exists("css=#cookie-accept")

# Dismiss notification if present
await element_manager.click_if_exists("css=.notification-dismiss")

# Close welcome modal if present
await element_manager.click_if_exists("css=#welcome-modal-close")

# Skip tutorial if present
await element_manager.click_if_exists("css=#tutorial-skip")

# Close advertisement if present
await element_manager.click_if_exists("css=.ad-close-button")
```

### Pattern: Clean Navigation
```python
async def navigate_to_page(url: str):
    """Navigate to page and handle optional popups."""
    await page.goto(url)
    
    # Handle optional elements
    await element_manager.click_if_exists("css=#cookie-accept", timeout=2000)
    await element_manager.click_if_exists("css=#newsletter-close", timeout=2000)
    await element_manager.click_if_exists("css=#promo-banner-close", timeout=2000)
```

---

## click_with_retry()

**Use Case**: Handle flaky elements or elements that may be temporarily obscured

### Basic Usage
```python
# Click with default retry (3 attempts, 1s initial delay)
await element_manager.click_with_retry("css=#flaky-button")
```

### With Custom Retry Settings
```python
# More aggressive retry
await element_manager.click_with_retry(
    "css=#submit-button",
    max_retries=5,
    initial_delay=0.5  # Start with 0.5s delay
)

# Patient retry for slow-loading elements
await element_manager.click_with_retry(
    "css=#dynamic-button",
    max_retries=4,
    initial_delay=2.0  # Start with 2s delay
)
```

### With Fallback
```python
# Retry with fallback locators
await element_manager.click_with_retry(
    "css=#primary-button",
    fallback_locators=["xpath=//button[@type='submit']", "text=Submit"],
    max_retries=3
)
```

### Real-World Examples
```python
# Click button that may be temporarily disabled
await element_manager.click_with_retry("css=#submit-form")

# Click element that loads dynamically
await element_manager.click_with_retry(
    "css=#load-more",
    max_retries=5,
    initial_delay=1.0
)

# Click element that may be obscured by animations
await element_manager.click_with_retry(
    "css=#menu-item",
    max_retries=3,
    initial_delay=0.5
)

# Click element in single-page app with dynamic rendering
await element_manager.click_with_retry(
    "css=#react-button",
    max_retries=4,
    initial_delay=1.0
)
```

### Retry Timing Example
```python
# With max_retries=4 and initial_delay=1.0:
# Attempt 1: Immediate
# Attempt 2: After 1.0 seconds
# Attempt 3: After 2.0 seconds (1.0 * 2)
# Attempt 4: After 4.0 seconds (2.0 * 2)
# Total max wait: 7.0 seconds
```

---

## Common Patterns

### Pattern 1: Robust Form Submission
```python
async def submit_form_robustly():
    """Submit form with multiple fallback strategies."""
    # Try normal click first
    try:
        await element_manager.click("css=#submit-button")
    except ElementNotInteractableException:
        # Try clicking at center position
        try:
            await element_manager.click_at_position(
                "css=#submit-button",
                x=50,
                y=20
            )
        except:
            # Last resort: retry with exponential backoff
            await element_manager.click_with_retry(
                "css=#submit-button",
                max_retries=5
            )
```

### Pattern 2: Clean Test Setup
```python
async def setup_test_environment():
    """Set up test environment by handling optional UI elements."""
    # Close all optional popups/banners
    await element_manager.click_if_exists("css=#cookie-banner-accept", timeout=2000)
    await element_manager.click_if_exists("css=#welcome-modal-close", timeout=2000)
    await element_manager.click_if_exists("css=#promo-close", timeout=2000)
    await element_manager.click_if_exists("css=#survey-dismiss", timeout=2000)
```

### Pattern 3: Context Menu Interaction
```python
async def select_context_menu_option(element_locator: str, menu_option: str):
    """Right-click element and select menu option."""
    # Right-click to open context menu
    await element_manager.right_click(element_locator)
    
    # Wait for menu to appear
    await element_manager.wait_for_element("css=.context-menu", state="visible")
    
    # Click menu option
    await element_manager.click(f"text={menu_option}")
```

### Pattern 4: File Selection
```python
async def open_file_with_double_click(filename: str):
    """Open file by double-clicking in file explorer."""
    # Locate and double-click file
    await element_manager.double_click(
        f"css=.file-item[data-name='{filename}']",
        fallback_locators=[f"text={filename}"]
    )
    
    # Wait for file to open
    await element_manager.wait_for_element("css=#file-viewer", state="visible")
```

### Pattern 5: Canvas Interaction
```python
async def draw_on_canvas(points: list[tuple[int, int]]):
    """Draw on canvas by clicking multiple points."""
    for x, y in points:
        await element_manager.click_at_position(
            "css=#drawing-canvas",
            x=x,
            y=y
        )
        # Small delay between points
        await asyncio.sleep(0.1)
```

### Pattern 6: Flaky Element Handling
```python
async def handle_flaky_element(locator: str):
    """Handle element that may be flaky or slow to load."""
    # First try: conditional click (fast fail if not present)
    clicked = await element_manager.click_if_exists(locator, timeout=2000)
    
    if not clicked:
        # Second try: retry with backoff (element may be loading)
        try:
            await element_manager.click_with_retry(
                locator,
                max_retries=3,
                initial_delay=1.0
            )
        except ElementNotFoundException:
            # Element truly doesn't exist
            logger.warning(f"Element not found after retries: {locator}")
            raise
```

## Best Practices

### 1. Choose the Right Method
- Use `click()` for standard, reliable elements
- Use `click_at_position()` for canvas, maps, or coordinate-based interactions
- Use `double_click()` for file/folder operations or text selection
- Use `right_click()` for context menus
- Use `click_if_exists()` for optional UI elements
- Use `click_with_retry()` for flaky or dynamically-loaded elements

### 2. Timeout Configuration
```python
# Short timeout for optional elements
await element_manager.click_if_exists("css=#popup", timeout=2000)

# Standard timeout for normal elements
await element_manager.click("css=#button")  # Uses default

# Long timeout for slow-loading elements
await element_manager.click("css=#slow-button", timeout=30000)
```

### 3. Fallback Strategies
```python
# Always provide fallbacks for critical elements
await element_manager.click(
    "css=#submit",
    fallback_locators=[
        "xpath=//button[@type='submit']",
        "text=Submit",
        "role=button[name='Submit']"
    ]
)
```

### 4. Error Handling
```python
try:
    await element_manager.click_with_retry("css=#button")
except ElementNotFoundException:
    # Element doesn't exist
    logger.error("Button not found")
except ElementNotInteractableException:
    # Element exists but can't be clicked
    logger.error("Button not clickable")
```

### 5. Logging
All methods automatically log their actions. Enable debug logging for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Tips

1. **Use click_if_exists() with short timeouts** for optional elements to avoid unnecessary waits
2. **Adjust retry parameters** based on your application's loading characteristics
3. **Use fallback locators** to avoid multiple retry attempts
4. **Combine methods** for robust interactions (try click_if_exists first, then click_with_retry)

## Migration from Java

| Java Method | Python Method | Notes |
|------------|---------------|-------|
| `clickXY(x, y)` | `click_at_position(locator, x, y)` | Now requires element locator |
| `doubleClick()` | `double_click(locator)` | Same functionality |
| `rightClick()` | `right_click(locator)` | Same functionality |
| `clickIfExists()` | `click_if_exists(locator)` | Returns boolean |
| Custom retry logic | `click_with_retry(locator)` | Built-in exponential backoff |

## Additional Resources

- [Element Manager Implementation](./ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Task 7 Completion Summary](./TASK_7_COMPLETION_SUMMARY.md)
- [Element Interaction Examples](../examples/element_interaction_example.py)
- [API Documentation](../README.md)
