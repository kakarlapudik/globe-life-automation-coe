# Verification Methods - Quick Reference

## Quick Method Overview

| Method | Purpose | Raises AssertionError When |
|--------|---------|---------------------------|
| `verify_exists()` | Element exists | Element not found |
| `verify_not_exists()` | Element does not exist | Element found |
| `verify_enabled()` | Element is enabled | Element disabled or not found |
| `verify_disabled()` | Element is disabled | Element enabled or not found |
| `verify_text()` | Element has expected text | Text doesn't match |
| `verify_visible()` | Element is visible | Element hidden or not found |

## Quick Examples

```python
# Element existence
await element_manager.verify_exists("css=#submit-button")
await element_manager.verify_not_exists("css=#error-message")

# Element state
await element_manager.verify_enabled("css=#save-button")
await element_manager.verify_disabled("css=#delete-button")
await element_manager.verify_visible("css=#success-message")

# Text verification
await element_manager.verify_text("css=#status", "Active")
await element_manager.verify_text("css=#msg", "success", exact_match=False)
await element_manager.verify_text("css=#title", "WELCOME", case_sensitive=False)

# With custom messages
await element_manager.verify_exists(
    "css=#profile",
    message="User profile should be displayed"
)

# With fallback locators
await element_manager.verify_visible(
    "css=#submit",
    fallback_locators=["xpath=//button[@type='submit']"]
)
```

## Common Patterns

### Login Form Validation
```python
await element_manager.verify_exists("css=#username")
await element_manager.verify_exists("css=#password")
await element_manager.verify_disabled("css=#login-button")
# ... fill form ...
await element_manager.verify_enabled("css=#login-button")
```

### Success/Error Messages
```python
await element_manager.verify_visible("css=#success-message")
await element_manager.verify_text("css=#success-message", "Success!")
await element_manager.verify_not_exists("css=#error-message")
```

### Dynamic Content
```python
await element_manager.verify_exists("css=#data-table", timeout=10000)
await element_manager.verify_visible("css=#data-table")
await element_manager.verify_not_exists("css=#loading-spinner", timeout=2000)
```

## Parameters Reference

### Common Parameters (All Methods)
- `locator`: Primary locator string (required)
- `fallback_locators`: List of fallback locators (optional)
- `timeout`: Timeout in milliseconds (optional)
- `message`: Custom error message (optional)

### verify_text() Additional Parameters
- `expected_text`: Expected text content (required)
- `exact_match`: True for exact, False for partial (default: True)
- `case_sensitive`: True for case-sensitive (default: True)

## Default Timeouts

- **Positive assertions**: Uses default timeout from config (typically 20000ms)
- **Negative assertions**: Uses 5000ms by default (can be overridden)

## Tips

1. **Always use custom messages** for better test failure diagnostics
2. **Use shorter timeouts** for negative assertions (`verify_not_exists`)
3. **Provide fallback locators** for more robust tests
4. **Choose appropriate text matching** (exact vs partial, case-sensitive vs insensitive)
5. **Chain verifications** for comprehensive checks

## See Full Documentation

For detailed information, see [Verification Methods Guide](VERIFICATION_METHODS_GUIDE.md)
