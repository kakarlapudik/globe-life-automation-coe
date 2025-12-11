# Element State and Property Methods

This document describes the element state and property methods implemented in Task 8 of the RAPTOR Python Playwright Framework.

## Overview

The ElementManager now provides comprehensive methods for retrieving element state and properties:

- **get_text()** - Retrieve visible text content from elements
- **get_attribute()** - Get HTML attribute values
- **get_value()** - Get input/textarea/select values
- **get_location()** - Get element position and dimensions
- **is_selected()** - Check checkbox/radio button selection state

All methods support fallback locators and configurable timeouts, consistent with other ElementManager methods.

## Methods

### get_text()

Retrieves the visible text content of an element (inner text).

**Signature:**
```python
async def get_text(
    locator: str,
    fallback_locators: Optional[List[str]] = None,
    timeout: Optional[int] = None,
) -> str
```

**Parameters:**
- `locator`: Primary locator string (e.g., "css=#message", "xpath=//p")
- `fallback_locators`: Optional list of fallback locator strings
- `timeout`: Optional timeout in milliseconds

**Returns:** Text content as string

**Example:**
```python
# Get text from heading
heading = await element_manager.get_text("css=h1")
print(f"Heading: {heading}")

# Get text with fallback
message = await element_manager.get_text(
    "css=#message",
    fallback_locators=["xpath=//div[@class='message']", "text=Welcome"]
)
```

**Notes:**
- Returns the visible text only (excludes hidden elements, scripts, styles)
- Equivalent to JavaScript's `innerText` property
- Returns empty string for elements with no text content

---

### get_attribute()

Retrieves the value of an HTML attribute from an element.

**Signature:**
```python
async def get_attribute(
    locator: str,
    attribute: str,
    fallback_locators: Optional[List[str]] = None,
    timeout: Optional[int] = None,
) -> Optional[str]
```

**Parameters:**
- `locator`: Primary locator string
- `attribute`: Name of the attribute to retrieve (e.g., "href", "class", "id", "disabled")
- `fallback_locators`: Optional list of fallback locator strings
- `timeout`: Optional timeout in milliseconds

**Returns:** Attribute value as string, or None if attribute doesn't exist

**Example:**
```python
# Get href from link
href = await element_manager.get_attribute("css=#link", "href")
print(f"Link URL: {href}")

# Get class attribute
class_name = await element_manager.get_attribute("css=#button", "class")

# Check for disabled attribute
disabled = await element_manager.get_attribute("css=#submit", "disabled")
if disabled is not None:
    print("Button is disabled")
```

**Notes:**
- Returns None if the attribute doesn't exist (not an error)
- Boolean attributes (like "disabled", "checked") return their value or None
- Use this for any HTML attribute: id, class, href, src, data-*, aria-*, etc.

---

### get_value()

Retrieves the current value of an input, textarea, or select element.

**Signature:**
```python
async def get_value(
    locator: str,
    fallback_locators: Optional[List[str]] = None,
    timeout: Optional[int] = None,
) -> str
```

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locator strings
- `timeout`: Optional timeout in milliseconds

**Returns:** Current value as string

**Example:**
```python
# Get value from text input
username = await element_manager.get_value("css=#username")
print(f"Username: {username}")

# Get value from textarea
bio = await element_manager.get_value("css=#bio")

# Get value after filling
await element_manager.fill("css=#email", "test@example.com")
email = await element_manager.get_value("css=#email")
assert email == "test@example.com"
```

**Notes:**
- Works with input, textarea, and select elements
- More reliable than using `get_attribute("value")` for inputs
- Returns the current value, which may differ from the "value" attribute for user-modified inputs

---

### get_location()

Retrieves the position and dimensions of an element.

**Signature:**
```python
async def get_location(
    locator: str,
    fallback_locators: Optional[List[str]] = None,
    timeout: Optional[int] = None,
) -> Dict[str, float]
```

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locator strings
- `timeout`: Optional timeout in milliseconds

**Returns:** Dictionary with keys: `x`, `y`, `width`, `height`

**Example:**
```python
# Get element location
location = await element_manager.get_location("css=#button")
print(f"Position: ({location['x']}, {location['y']})")
print(f"Size: {location['width']}x{location['height']}")

# Check if element is in viewport
if location['y'] < 0:
    print("Element is above viewport")
```

**Notes:**
- Coordinates are relative to the viewport
- Raises RaptorException if element has no bounding box (hidden or not rendered)
- Useful for position-based interactions or layout verification

---

### is_selected()

Checks if a checkbox or radio button is selected/checked.

**Signature:**
```python
async def is_selected(
    locator: str,
    fallback_locators: Optional[List[str]] = None,
    timeout: Optional[int] = None,
) -> bool
```

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locator strings
- `timeout`: Optional timeout in milliseconds

**Returns:** True if checked/selected, False otherwise

**Example:**
```python
# Check checkbox state
is_checked = await element_manager.is_selected("css=#terms")
if is_checked:
    print("Terms accepted")

# Check radio button
option1_selected = await element_manager.is_selected("css=#option1")
option2_selected = await element_manager.is_selected("css=#option2")

# Verify state after clicking
await element_manager.click("css=#newsletter")
assert await element_manager.is_selected("css=#newsletter") == True
```

**Notes:**
- Only works with checkbox and radio button elements
- Returns the checked state, not the "checked" attribute
- Use this instead of `get_attribute("checked")` for reliable state checking

---

## Common Patterns

### Verify Form Data

```python
# Fill form
await element_manager.fill("css=#username", "john.doe")
await element_manager.fill("css=#email", "john@example.com")
await element_manager.click("css=#terms")

# Verify values
assert await element_manager.get_value("css=#username") == "john.doe"
assert await element_manager.get_value("css=#email") == "john@example.com"
assert await element_manager.is_selected("css=#terms") == True
```

### Extract Link Information

```python
# Get all link details
href = await element_manager.get_attribute("css=#link", "href")
text = await element_manager.get_text("css=#link")
target = await element_manager.get_attribute("css=#link", "target")

print(f"Link: {text} -> {href} (opens in {target or 'same window'})")
```

### Validate Element Position

```python
# Check if element is visible in viewport
location = await element_manager.get_location("css=#element")

viewport_height = await page.evaluate("window.innerHeight")
viewport_width = await page.evaluate("window.innerWidth")

is_in_viewport = (
    location['x'] >= 0 and
    location['y'] >= 0 and
    location['x'] + location['width'] <= viewport_width and
    location['y'] + location['height'] <= viewport_height
)
```

### Check Multiple Checkboxes

```python
checkboxes = ["#option1", "#option2", "#option3"]
selected = []

for checkbox in checkboxes:
    if await element_manager.is_selected(f"css={checkbox}"):
        # Get the label text
        label_text = await element_manager.get_text(f"css=label[for='{checkbox[1:]}']")
        selected.append(label_text)

print(f"Selected options: {', '.join(selected)}")
```

## Error Handling

All methods follow the standard ElementManager error handling:

- **ElementNotFoundException**: Raised if element cannot be found with any locator
- **RaptorException**: Raised for other errors (e.g., element has no bounding box)
- **TimeoutException**: Raised if operation exceeds timeout

```python
try:
    text = await element_manager.get_text("css=#message", timeout=5000)
except ElementNotFoundException as e:
    print(f"Element not found: {e.locator}")
except RaptorException as e:
    print(f"Error: {e}")
```

## Fallback Locators

All methods support fallback locators for resilience:

```python
# Try multiple strategies
value = await element_manager.get_value(
    "css=#username",
    fallback_locators=[
        "xpath=//input[@name='username']",
        "xpath=//input[@type='text'][1]"
    ]
)
```

## Requirements Validation

These methods satisfy the following requirements from the design document:

- **Requirement 2.4**: Element interaction methods (get text, attributes, values)
- **Requirement 7.1**: Verification methods (checking element state)

## Java Framework Equivalents

| Java Method | Python Method | Notes |
|-------------|---------------|-------|
| `getText()` | `get_text()` | Gets visible text content |
| `getAttribute()` | `get_attribute()` | Gets HTML attribute value |
| `getValue()` | `get_value()` | Gets input/textarea value |
| `getLocation()` | `get_location()` | Gets element coordinates |
| `isSelected()` | `is_selected()` | Checks checkbox/radio state |

## See Also

- [Element Manager Implementation](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Element Interaction Methods](ELEMENT_INTERACTION_QUICK_REFERENCE.md)
- [Advanced Click Methods](ADVANCED_CLICK_METHODS_GUIDE.md)
