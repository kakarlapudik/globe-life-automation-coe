# Verification Methods Guide

## Overview

The ElementManager provides comprehensive verification methods for asserting element states in automated tests. These methods raise `AssertionError` when verification fails, making them ideal for test assertions.

## Available Verification Methods

### 1. verify_exists()

Verify that an element exists on the page.

```python
await element_manager.verify_exists("css=#submit-button")
await element_manager.verify_exists(
    "css=#error-message",
    message="Error message should be displayed"
)
```

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locators
- `timeout`: Optional timeout in milliseconds
- `message`: Optional custom error message

**Raises:** `AssertionError` if element does not exist

---

### 2. verify_not_exists()

Verify that an element does NOT exist on the page.

```python
await element_manager.verify_not_exists("css=#error-message")
await element_manager.verify_not_exists(
    "css=#loading-spinner",
    timeout=5000,
    message="Loading spinner should not be visible"
)
```

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locators
- `timeout`: Optional timeout in milliseconds (default: 5000ms for negative assertions)
- `message`: Optional custom error message

**Raises:** `AssertionError` if element exists

---

### 3. verify_enabled()

Verify that an element is enabled (not disabled).

```python
await element_manager.verify_enabled("css=#submit-button")
await element_manager.verify_enabled(
    "css=#save-button",
    message="Save button should be enabled"
)
```

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locators
- `timeout`: Optional timeout in milliseconds
- `message`: Optional custom error message

**Raises:** `AssertionError` if element is disabled or does not exist

---

### 4. verify_disabled()

Verify that an element is disabled (not enabled).

```python
await element_manager.verify_disabled("css=#submit-button")
await element_manager.verify_disabled(
    "css=#delete-button",
    message="Delete button should be disabled"
)
```

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locators
- `timeout`: Optional timeout in milliseconds
- `message`: Optional custom error message

**Raises:** `AssertionError` if element is enabled or does not exist

---

### 5. verify_text()

Verify that an element contains the expected text.

```python
# Exact match (default)
await element_manager.verify_text("css=#message", "Success!")

# Partial match
await element_manager.verify_text(
    "css=#status",
    "processing",
    exact_match=False
)

# Case-insensitive comparison
await element_manager.verify_text(
    "css=#message",
    "success!",
    case_sensitive=False
)

# Partial and case-insensitive
await element_manager.verify_text(
    "css=#description",
    "important",
    exact_match=False,
    case_sensitive=False
)
```

**Parameters:**
- `locator`: Primary locator string
- `expected_text`: Expected text content
- `exact_match`: If True, requires exact match; if False, allows partial match (default: True)
- `case_sensitive`: If True, comparison is case-sensitive (default: True)
- `fallback_locators`: Optional list of fallback locators
- `timeout`: Optional timeout in milliseconds
- `message`: Optional custom error message

**Raises:** `AssertionError` if text does not match or element does not exist

---

### 6. verify_visible()

Verify that an element is visible on the page.

```python
await element_manager.verify_visible("css=#success-message")
await element_manager.verify_visible(
    "css=#notification",
    message="Notification should be visible"
)
```

**Parameters:**
- `locator`: Primary locator string
- `fallback_locators`: Optional list of fallback locators
- `timeout`: Optional timeout in milliseconds
- `message`: Optional custom error message

**Raises:** `AssertionError` if element is not visible or does not exist

---

## Usage Examples

### Basic Verification

```python
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager

# Initialize
config = ConfigManager()
element_manager = ElementManager(page, config)

# Verify element exists
await element_manager.verify_exists("css=#submit-button")

# Verify element is visible
await element_manager.verify_visible("css=#success-message")

# Verify element is enabled
await element_manager.verify_enabled("css=#save-button")
```

### Verification with Custom Messages

```python
# Custom error messages provide better test failure context
await element_manager.verify_exists(
    "css=#user-profile",
    message="User profile section should be displayed after login"
)

await element_manager.verify_text(
    "css=#welcome-message",
    "Welcome, John",
    message="Welcome message should display user's name"
)
```

### Verification with Fallback Locators

```python
# Try multiple locators
await element_manager.verify_exists(
    "css=#submit",
    fallback_locators=["xpath=//button[@type='submit']", "text=Submit"]
)

await element_manager.verify_enabled(
    "css=#save-btn",
    fallback_locators=["css=button.save", "text=Save"]
)
```

### Text Verification Variations

```python
# Exact match (case-sensitive)
await element_manager.verify_text("css=#status", "Active")

# Partial match
await element_manager.verify_text(
    "css=#description",
    "important information",
    exact_match=False
)

# Case-insensitive
await element_manager.verify_text(
    "css=#title",
    "welcome",
    case_sensitive=False
)

# Partial and case-insensitive
await element_manager.verify_text(
    "css=#content",
    "ERROR",
    exact_match=False,
    case_sensitive=False
)
```

### Negative Assertions

```python
# Verify element does not exist
await element_manager.verify_not_exists("css=#error-message")

# Verify element is disabled
await element_manager.verify_disabled("css=#submit-button")
```

### Complete Test Example

```python
import pytest
from playwright.async_api import async_playwright
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager


@pytest.mark.asyncio
async def test_login_flow():
    """Test complete login flow with verifications."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        config = ConfigManager()
        element_manager = ElementManager(page, config)
        
        # Navigate to login page
        await page.goto("https://example.com/login")
        
        # Verify login form elements exist
        await element_manager.verify_exists("css=#username")
        await element_manager.verify_exists("css=#password")
        await element_manager.verify_exists("css=#login-button")
        
        # Verify submit button is initially disabled
        await element_manager.verify_disabled("css=#login-button")
        
        # Fill in credentials
        await element_manager.fill("css=#username", "testuser")
        await element_manager.fill("css=#password", "password123")
        
        # Verify submit button is now enabled
        await element_manager.verify_enabled("css=#login-button")
        
        # Click login
        await element_manager.click("css=#login-button")
        
        # Verify success message appears
        await element_manager.verify_visible("css=#success-message")
        await element_manager.verify_text(
            "css=#success-message",
            "Login successful",
            exact_match=False
        )
        
        # Verify error message does not exist
        await element_manager.verify_not_exists("css=#error-message")
        
        await browser.close()
```

## Best Practices

### 1. Use Custom Messages

Always provide custom error messages for better test failure diagnostics:

```python
await element_manager.verify_exists(
    "css=#dashboard",
    message="Dashboard should be visible after successful login"
)
```

### 2. Choose Appropriate Timeouts

Use shorter timeouts for negative assertions:

```python
# Negative assertion - use short timeout
await element_manager.verify_not_exists("css=#loading", timeout=2000)

# Positive assertion - use longer timeout if needed
await element_manager.verify_exists("css=#data-table", timeout=10000)
```

### 3. Use Fallback Locators

Provide fallback locators for more robust tests:

```python
await element_manager.verify_visible(
    "css=#submit-btn",
    fallback_locators=["xpath=//button[@type='submit']", "text=Submit"]
)
```

### 4. Choose the Right Text Matching

Select appropriate text matching options:

```python
# Exact match for precise assertions
await element_manager.verify_text("css=#count", "5")

# Partial match for flexible assertions
await element_manager.verify_text(
    "css=#message",
    "success",
    exact_match=False
)

# Case-insensitive for user-generated content
await element_manager.verify_text(
    "css=#user-input",
    "hello world",
    case_sensitive=False
)
```

### 5. Combine Verifications

Chain multiple verifications for comprehensive checks:

```python
# Verify element exists, is visible, and has correct text
await element_manager.verify_exists("css=#notification")
await element_manager.verify_visible("css=#notification")
await element_manager.verify_text("css=#notification", "Operation completed")
```

## Error Handling

All verification methods raise `AssertionError` when verification fails:

```python
try:
    await element_manager.verify_exists("css=#missing-element")
except AssertionError as e:
    print(f"Verification failed: {e}")
    # Handle the failure (e.g., take screenshot, log error)
```

## Integration with pytest

Verification methods work seamlessly with pytest:

```python
@pytest.mark.asyncio
async def test_form_validation(element_manager):
    """Test form validation messages."""
    # These will cause test failure if assertions fail
    await element_manager.verify_exists("css=#email-error")
    await element_manager.verify_visible("css=#email-error")
    await element_manager.verify_text(
        "css=#email-error",
        "Invalid email format",
        message="Email validation message should be displayed"
    )
```

## Requirements Validation

These verification methods satisfy the following requirements:

- **Requirement 7.1**: Element state verification (enabled, disabled, visible, hidden)
- **Requirement 7.2**: Element existence verification (positive and negative)
- **Requirement 7.3**: Text content verification with comparison options
- **Requirement 7.4**: Detailed error messages with context

## See Also

- [Element Manager Implementation](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Element Interaction Quick Reference](ELEMENT_INTERACTION_QUICK_REFERENCE.md)
- [Testing Strategy](../README.md#testing-strategy)
