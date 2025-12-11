# Element State Methods - Quick Reference

Quick reference for the element state and property methods in ElementManager.

## Methods at a Glance

| Method | Purpose | Returns | Common Use Cases |
|--------|---------|---------|------------------|
| `get_text()` | Get visible text | `str` | Verify messages, extract data |
| `get_attribute()` | Get HTML attribute | `Optional[str]` | Get href, class, id, data-* |
| `get_value()` | Get input value | `str` | Verify form inputs |
| `get_location()` | Get position/size | `Dict[str, float]` | Layout verification, positioning |
| `is_selected()` | Check checkbox/radio | `bool` | Verify form selections |

## Quick Examples

### Get Text
```python
# Simple
text = await element_manager.get_text("css=h1")

# With fallback
text = await element_manager.get_text(
    "css=#message",
    fallback_locators=["xpath=//div[@class='message']"]
)
```

### Get Attribute
```python
# Get href
url = await element_manager.get_attribute("css=#link", "href")

# Check if disabled
disabled = await element_manager.get_attribute("css=#button", "disabled")
if disabled is not None:
    print("Button is disabled")
```

### Get Value
```python
# Get input value
username = await element_manager.get_value("css=#username")

# Verify after fill
await element_manager.fill("css=#email", "test@example.com")
assert await element_manager.get_value("css=#email") == "test@example.com"
```

### Get Location
```python
# Get position and size
loc = await element_manager.get_location("css=#button")
print(f"At ({loc['x']}, {loc['y']}), size {loc['width']}x{loc['height']}")
```

### Is Selected
```python
# Check checkbox
if await element_manager.is_selected("css=#terms"):
    print("Terms accepted")

# Verify after click
await element_manager.click("css=#newsletter")
assert await element_manager.is_selected("css=#newsletter") == True
```

## Common Patterns

### Form Validation
```python
# Fill and verify
await element_manager.fill("css=#username", "john")
await element_manager.click("css=#terms")

assert await element_manager.get_value("css=#username") == "john"
assert await element_manager.is_selected("css=#terms") == True
```

### Extract Link Info
```python
href = await element_manager.get_attribute("css=#link", "href")
text = await element_manager.get_text("css=#link")
print(f"{text}: {href}")
```

### Check Multiple Selections
```python
checkboxes = ["#opt1", "#opt2", "#opt3"]
selected = [
    cb for cb in checkboxes 
    if await element_manager.is_selected(f"css={cb}")
]
```

## Error Handling

```python
try:
    text = await element_manager.get_text("css=#message")
except ElementNotFoundException:
    print("Element not found")
except RaptorException as e:
    print(f"Error: {e}")
```

## All Methods Support

- ✅ Fallback locators
- ✅ Custom timeouts
- ✅ Multiple locator strategies (CSS, XPath, text, role, ID)
- ✅ Comprehensive error handling
- ✅ Detailed logging

## See Full Documentation

- [Element State Methods Guide](ELEMENT_STATE_METHODS.md)
- [Element Manager Implementation](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Task 8 Completion Summary](TASK_8_COMPLETION_SUMMARY.md)
