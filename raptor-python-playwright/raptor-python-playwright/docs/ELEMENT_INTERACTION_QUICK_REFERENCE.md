# Element Interaction Methods - Quick Reference

## Overview

This guide provides quick reference for all element interaction methods in the RAPTOR ElementManager.

## Click Methods

### Basic Click
```python
await element_manager.click("css=#submit-button")
```

### Click with Fallback
```python
await element_manager.click(
    "css=#primary-btn",
    fallback_locators=["xpath=//button[@id='primary-btn']"],
    timeout=5000
)
```

### Right Click
```python
await element_manager.click("css=#context-menu", button="right")
```

### Double Click
```python
await element_manager.click("css=#item", click_count=2)
```

### Click with Delay
```python
await element_manager.click("css=#button", delay=100)  # 100ms delay
```

## Text Input Methods

### Fill Input
```python
await element_manager.fill("css=#username", "john.doe")
```

### Fill with Fallback
```python
await element_manager.fill(
    "css=#email",
    "test@example.com",
    fallback_locators=["xpath=//input[@name='email']"]
)
```

### Fill with Force (bypass actionability checks)
```python
await element_manager.fill("css=#hidden-input", "value", force=True)
```

## Dropdown Selection Methods

### Select by Value
```python
await element_manager.select_option("css=#country", value="US")
```

### Select by Label
```python
await element_manager.select_option("css=#country", label="United States")
```

### Select by Index
```python
await element_manager.select_option("css=#country", index=0)
```

### Multiple Selection
```python
await element_manager.select_option(
    "css=#colors",
    value=["red", "blue", "green"]
)
```

### Select with Fallback
```python
await element_manager.select_option(
    "css=#dropdown",
    value="option1",
    fallback_locators=["xpath=//select[@name='dropdown']"]
)
```

## Hover Methods

### Basic Hover
```python
await element_manager.hover("css=#menu-item")
```

### Hover at Position
```python
await element_manager.hover(
    "css=#element",
    position={"x": 10, "y": 10}
)
```

### Hover with Fallback
```python
await element_manager.hover(
    "css=#dropdown-trigger",
    fallback_locators=["text=Products"]
)
```

## Element State Checks

### Check if Visible
```python
is_visible = await element_manager.is_visible("css=#element")
if is_visible:
    print("Element is visible")
```

### Check if Hidden
```python
is_hidden = await element_manager.is_hidden("css=#element")
if is_hidden:
    print("Element is hidden")
```

### Check if Enabled
```python
is_enabled = await element_manager.is_enabled("css=#submit-button")
if is_enabled:
    await element_manager.click("css=#submit-button")
```

## Common Patterns

### Conditional Click
```python
# Check if element is enabled before clicking
if await element_manager.is_enabled("css=#submit-btn"):
    await element_manager.click("css=#submit-btn")
else:
    print("Button is disabled, skipping click")
```

### Fill Form with Multiple Fields
```python
# Fill multiple form fields
await element_manager.fill("css=#username", "john.doe")
await element_manager.fill("css=#email", "john@example.com")
await element_manager.select_option("css=#country", value="US")
await element_manager.click("css=#submit")
```

### Hover and Click Menu Item
```python
# Hover over menu to reveal submenu, then click item
await element_manager.hover("css=#products-menu")
await asyncio.sleep(0.5)  # Wait for submenu animation
await element_manager.click("css=#submenu-item")
```

### Robust Element Interaction with Fallbacks
```python
# Use multiple fallback strategies for critical elements
await element_manager.click(
    "css=#submit-button",
    fallback_locators=[
        "xpath=//button[@id='submit-button']",
        "text=Submit",
        "role=button[name='Submit']"
    ],
    timeout=10000
)
```

## Error Handling

### Handle Element Not Found
```python
from raptor.core.exceptions import ElementNotFoundException

try:
    await element_manager.click("css=#maybe-exists")
except ElementNotFoundException as e:
    print(f"Element not found: {e.context['primary_locator']}")
    # Handle gracefully
```

### Handle Interaction Failure
```python
from raptor.core.exceptions import ElementNotInteractableException

try:
    await element_manager.click("css=#button")
except ElementNotInteractableException as e:
    print(f"Cannot interact with element: {e.context['reason']}")
    # Try alternative approach
```

### Handle Timeout
```python
from raptor.core.exceptions import TimeoutException

try:
    await element_manager.fill("css=#slow-input", "text", timeout=5000)
except TimeoutException as e:
    print(f"Operation timed out after {e.context['timeout_seconds']}s")
    # Retry or skip
```

## Best Practices

### 1. Use Specific Locators
```python
# Good: Specific ID selector
await element_manager.click("css=#submit-button")

# Avoid: Generic class selector
await element_manager.click("css=.button")
```

### 2. Always Provide Fallbacks for Critical Elements
```python
# Good: Multiple fallback strategies
await element_manager.click(
    "css=#critical-button",
    fallback_locators=["xpath=//button[@id='critical-button']", "text=Submit"]
)

# Risky: No fallbacks
await element_manager.click("css=#critical-button")
```

### 3. Set Appropriate Timeouts
```python
# Fast elements: Short timeout
await element_manager.click("css=#instant-button", timeout=2000)

# Slow elements: Longer timeout
await element_manager.click("css=#slow-loading-button", timeout=30000)
```

### 4. Check State Before Interaction
```python
# Good: Check before clicking
if await element_manager.is_enabled("css=#submit"):
    await element_manager.click("css=#submit")

# Risky: Click without checking
await element_manager.click("css=#submit")
```

### 5. Use Meaningful Variable Names
```python
# Good: Clear intent
submit_button_enabled = await element_manager.is_enabled("css=#submit")
if submit_button_enabled:
    await element_manager.click("css=#submit")

# Unclear: Generic names
x = await element_manager.is_enabled("css=#submit")
if x:
    await element_manager.click("css=#submit")
```

## Locator Strategies

### CSS Selectors
```python
await element_manager.click("css=#id")           # By ID
await element_manager.click("css=.class")        # By class
await element_manager.click("css=[name='btn']")  # By attribute
await element_manager.click("css=button.primary") # By tag and class
```

### XPath
```python
await element_manager.click("xpath=//button[@id='submit']")
await element_manager.click("xpath=//div[@class='container']//button")
```

### Text Content
```python
await element_manager.click("text=Submit")
await element_manager.click("text=Click Me")
```

### Role (Accessibility)
```python
await element_manager.click("role=button[name='Submit']")
await element_manager.click("role=link[name='Home']")
```

### ID (Shorthand)
```python
await element_manager.click("id=submit-button")
```

## Performance Tips

1. **Use ID selectors when possible** - Fastest lookup
2. **Avoid complex XPath** - Can be slow on large DOMs
3. **Set reasonable timeouts** - Balance speed and reliability
4. **Use fallbacks strategically** - Don't add unnecessary fallbacks
5. **Batch operations** - Use async/await efficiently

## Troubleshooting

### Element Not Found
- Verify locator is correct
- Check if element is in iframe
- Ensure page has loaded
- Try different locator strategies

### Element Not Interactable
- Check if element is visible
- Verify element is not disabled
- Ensure no overlay is blocking element
- Wait for animations to complete

### Timeout Issues
- Increase timeout value
- Check network conditions
- Verify element actually appears
- Use wait_for_element first

## Additional Resources

- [ElementManager API Documentation](./ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Task 6 Completion Summary](./TASK_6_COMPLETION_SUMMARY.md)
- [Example Code](../examples/element_interaction_example.py)
- [Playwright Documentation](https://playwright.dev/python/)
