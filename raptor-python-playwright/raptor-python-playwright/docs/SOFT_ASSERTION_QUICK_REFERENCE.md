# Soft Assertion Quick Reference

## Overview

Soft assertions allow you to perform multiple verifications without stopping test execution at the first failure. All failures are collected and reported at the end, giving you a comprehensive view of all issues.

## When to Use Soft Assertions

✅ **Use soft assertions when:**
- Validating multiple elements on a page
- Performing comprehensive form validation
- You want to see all failures, not just the first one
- Testing multiple related conditions
- Reducing test execution time by not stopping early

❌ **Don't use soft assertions when:**
- A failure makes subsequent tests meaningless
- You need to stop immediately on critical failures
- Testing sequential operations where order matters
- Each verification depends on the previous one

## Basic Usage

```python
from raptor.core.element_manager import ElementManager
from raptor.core.soft_assertion_collector import SoftAssertionCollector

# Create collector
collector = SoftAssertionCollector()

# Perform soft verifications
await element_manager.soft_verify_exists("css=#element1", collector)
await element_manager.soft_verify_enabled("css=#button", collector)
await element_manager.soft_verify_text("css=#message", "Success", collector)

# Assert all at the end (raises if any failures)
collector.assert_all()
```

## Available Soft Assertion Methods

### 1. soft_verify_exists()
Verify element exists without stopping on failure.

```python
await element_manager.soft_verify_exists(
    "css=#submit-button",
    collector,
    fallback_locators=["xpath=//button[@id='submit']"],
    timeout=10000,
    message="Submit button should be present"
)
```

### 2. soft_verify_not_exists()
Verify element does not exist without stopping on failure.

```python
await element_manager.soft_verify_not_exists(
    "css=#error-message",
    collector,
    timeout=5000,
    message="Error message should not be displayed"
)
```

### 3. soft_verify_enabled()
Verify element is enabled without stopping on failure.

```python
await element_manager.soft_verify_enabled(
    "css=#save-button",
    collector,
    message="Save button should be enabled"
)
```

### 4. soft_verify_disabled()
Verify element is disabled without stopping on failure.

```python
await element_manager.soft_verify_disabled(
    "css=#delete-button",
    collector,
    message="Delete button should be disabled"
)
```

### 5. soft_verify_text()
Verify element text without stopping on failure.

```python
# Exact match (default)
await element_manager.soft_verify_text(
    "css=#status",
    "Active",
    collector,
    message="Status should be 'Active'"
)

# Partial match, case-insensitive
await element_manager.soft_verify_text(
    "css=#message",
    "success",
    collector,
    exact_match=False,
    case_sensitive=False,
    message="Message should contain 'success'"
)
```

### 6. soft_verify_visible()
Verify element is visible without stopping on failure.

```python
await element_manager.soft_verify_visible(
    "css=#notification",
    collector,
    message="Notification should be visible"
)
```

## Collector Methods

### Check for Failures

```python
# Check if any failures occurred
if collector.has_failures():
    print(f"Found {collector.get_failure_count()} failures")

# Get total verification count
total = collector.get_verification_count()
```

### Get Failure Details

```python
# Get all failures
failures = collector.get_failures()

for failure in failures:
    print(f"Type: {failure.verification_type}")
    print(f"Locator: {failure.locator}")
    print(f"Expected: {failure.expected}")
    print(f"Actual: {failure.actual}")
    print(f"Message: {failure.message}")
    print(f"Page URL: {failure.page_url}")
```

### Get Summary

```python
summary = collector.get_summary()
print(f"Total: {summary['total_verifications']}")
print(f"Passed: {summary['passed']}")
print(f"Failed: {summary['failures']}")
```

### Clear Collector

```python
# Clear for reuse
collector.clear()
```

### Assert All

```python
# Raise AssertionError if any failures
# This should be called at the end of your test
collector.assert_all()
```

## Complete Example

```python
import asyncio
from playwright.async_api import async_playwright
from raptor.core.element_manager import ElementManager
from raptor.core.soft_assertion_collector import SoftAssertionCollector

async def test_user_profile():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com/profile")
        
        element_manager = ElementManager(page)
        collector = SoftAssertionCollector()
        
        # Perform multiple verifications
        await element_manager.soft_verify_exists(
            "css=#profile-container",
            collector,
            message="Profile container should exist"
        )
        
        await element_manager.soft_verify_text(
            "css=#username",
            "john_doe",
            collector,
            message="Username should be displayed"
        )
        
        await element_manager.soft_verify_enabled(
            "css=#edit-button",
            collector,
            message="Edit button should be enabled"
        )
        
        await element_manager.soft_verify_visible(
            "css=#profile-picture",
            collector,
            message="Profile picture should be visible"
        )
        
        # Check results
        print(f"Verifications: {collector.get_verification_count()}")
        print(f"Failures: {collector.get_failure_count()}")
        
        # Assert all (raises if failures)
        collector.assert_all()
        
        await browser.close()

asyncio.run(test_user_profile())
```

## Return Values

All soft assertion methods return a boolean:
- `True` if verification passed
- `False` if verification failed

```python
# You can check individual results
passed = await element_manager.soft_verify_exists("css=#element", collector)
if not passed:
    print("Element verification failed, but continuing...")

# Continue with more verifications
await element_manager.soft_verify_enabled("css=#button", collector)

# Assert all at the end
collector.assert_all()
```

## Custom Error Messages

Always provide meaningful custom messages:

```python
# ❌ Not helpful
await element_manager.soft_verify_exists("css=#btn", collector)

# ✅ Helpful
await element_manager.soft_verify_exists(
    "css=#submit-button",
    collector,
    message="Submit button must be present for form submission"
)
```

## Best Practices

1. **Create one collector per test**
   ```python
   # ✅ Good
   collector = SoftAssertionCollector()
   # ... perform verifications ...
   collector.assert_all()
   ```

2. **Always call assert_all() at the end**
   ```python
   # ✅ Good
   collector.assert_all()  # Raises if failures
   
   # ❌ Bad - failures not reported
   if collector.has_failures():
       pass  # Failures silently ignored
   ```

3. **Use descriptive messages**
   ```python
   # ✅ Good
   message="User profile name should match logged-in user"
   
   # ❌ Bad
   message="Check failed"
   ```

4. **Clear collector between test scenarios**
   ```python
   # Test scenario 1
   collector.assert_all()
   collector.clear()
   
   # Test scenario 2
   # ... new verifications ...
   collector.assert_all()
   ```

5. **Don't mix hard and soft assertions**
   ```python
   # ❌ Bad - mixing styles
   await element_manager.verify_exists("css=#critical")  # Hard - stops on failure
   await element_manager.soft_verify_text("css=#msg", "Hi", collector)  # Soft
   
   # ✅ Good - consistent style
   await element_manager.soft_verify_exists("css=#critical", collector)
   await element_manager.soft_verify_text("css=#msg", "Hi", collector)
   collector.assert_all()
   ```

## Comparison: Hard vs Soft Assertions

### Hard Assertions (Regular verify_* methods)
```python
# Stops at first failure
await element_manager.verify_exists("css=#element1")  # ✅ Pass
await element_manager.verify_exists("css=#element2")  # ❌ Fails - stops here
await element_manager.verify_exists("css=#element3")  # Never executed
```

### Soft Assertions
```python
# Continues through all verifications
await element_manager.soft_verify_exists("css=#element1", collector)  # ✅ Pass
await element_manager.soft_verify_exists("css=#element2", collector)  # ❌ Fails - continues
await element_manager.soft_verify_exists("css=#element3", collector)  # ✅ Pass - executed

collector.assert_all()  # Reports all failures at once
```

## Error Output Example

When `assert_all()` is called with failures:

```
================================================================================
SOFT ASSERTION FAILURES: 2 of 5 verifications failed
Passed: 3, Failed: 2
================================================================================

Failure 1 of 2:
--------------------------------------------------------------------------------
Verification Failed: verify_exists
  Locator: css=#nonexistent-button
  Expected: element exists
  Actual: element not found
  Message: Submit button should be present
  Page URL: https://example.com/form
  Timestamp: 2025-01-15 10:30:45.123

Failure 2 of 2:
--------------------------------------------------------------------------------
Verification Failed: verify_text
  Locator: css=#status
  Expected: Active
  Actual: Inactive
  Message: Status should be 'Active'
  Page URL: https://example.com/profile
  Timestamp: 2025-01-15 10:30:45.456

================================================================================
```

## Integration with pytest

```python
import pytest
from raptor.core.soft_assertion_collector import SoftAssertionCollector

@pytest.fixture
def soft_collector():
    """Fixture providing a fresh collector for each test."""
    return SoftAssertionCollector()

@pytest.mark.asyncio
async def test_form_validation(page, element_manager, soft_collector):
    """Test form with soft assertions."""
    await page.goto("https://example.com/form")
    
    # Perform soft verifications
    await element_manager.soft_verify_exists("css=#username", soft_collector)
    await element_manager.soft_verify_enabled("css=#submit", soft_collector)
    
    # This will fail the test if any soft assertions failed
    soft_collector.assert_all()
```

## See Also

- [Verification Methods Guide](VERIFICATION_METHODS_GUIDE.md)
- [Element Manager Implementation](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Examples](../examples/soft_assertion_example.py)
