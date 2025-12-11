# Synchronization Methods Guide

## Overview

The RAPTOR framework provides comprehensive synchronization methods to handle dynamic page loading, loading indicators, modal dialogs, and network activity. These methods ensure your tests wait for the right conditions before proceeding with interactions.

## Available Synchronization Methods

### 1. wait_for_load_state()

Wait for the page to reach a specific load state.

**Signature:**
```python
async def wait_for_load_state(
    state: str = "load",
    timeout: Optional[int] = None,
) -> None
```

**Parameters:**
- `state`: Load state to wait for
  - `"load"`: Page load event fired (default)
  - `"domcontentloaded"`: DOMContentLoaded event fired
  - `"networkidle"`: No network connections for at least 500ms
- `timeout`: Optional timeout in milliseconds

**Example:**
```python
# Wait for page load
await element_manager.wait_for_load_state("load")

# Wait for DOM content loaded
await element_manager.wait_for_load_state("domcontentloaded")

# Wait for network idle
await element_manager.wait_for_load_state("networkidle", timeout=30000)
```

**Use Cases:**
- After navigation to ensure page is fully loaded
- Before interacting with elements that require full page load
- When you need to ensure all resources are loaded

---

### 2. wait_for_spinner()

Wait for a loading spinner or indicator to disappear.

**Signature:**
```python
async def wait_for_spinner(
    spinner_locator: str,
    timeout: Optional[int] = None,
    check_interval: float = 0.5,
) -> None
```

**Parameters:**
- `spinner_locator`: Locator string for the loading spinner/indicator
- `timeout`: Optional timeout in milliseconds
- `check_interval`: Interval in seconds between visibility checks (default: 0.5)

**Example:**
```python
# Wait for a specific spinner
await element_manager.wait_for_spinner("css=#loading-spinner")

# Wait for spinner with custom timeout
await element_manager.wait_for_spinner("css=.loading-overlay", timeout=10000)

# Wait for spinner using XPath
await element_manager.wait_for_spinner("xpath=//div[@class='spinner']")
```

**Use Cases:**
- After clicking a button that triggers data loading
- After form submission while waiting for response
- During page transitions with loading indicators
- When AJAX requests show loading spinners

**Behavior:**
- If spinner doesn't exist, returns immediately (already gone)
- Waits for spinner to become hidden or detached from DOM
- Tries both "hidden" and "detached" states for reliability

---

### 3. wait_for_disabled_pane()

Wait for a disabled pane or modal dialog to disappear.

**Signature:**
```python
async def wait_for_disabled_pane(
    pane_locator: Optional[str] = None,
    timeout: Optional[int] = None,
) -> None
```

**Parameters:**
- `pane_locator`: Optional locator string for the disabled pane/modal
  - If not provided, waits for common modal patterns
- `timeout`: Optional timeout in milliseconds

**Default Modal Selectors:**
When no locator is provided, checks for:
- `.modal-backdrop`
- `.modal-overlay`
- `.overlay`
- `[role='dialog']`
- `.disabled-pane`
- `.loading-overlay`

**Example:**
```python
# Wait for specific modal
await element_manager.wait_for_disabled_pane("css=.modal-overlay")

# Wait for modal by ID
await element_manager.wait_for_disabled_pane("css=#loading-modal")

# Wait for any common modal pattern
await element_manager.wait_for_disabled_pane()

# Wait with custom timeout
await element_manager.wait_for_disabled_pane("css=.overlay", timeout=15000)
```

**Use Cases:**
- After closing modal dialogs
- Waiting for overlay screens to disappear
- Handling disabled panes that block interaction
- Waiting for popup dismissal

**Behavior:**
- If no pane exists, returns immediately
- Checks multiple default selectors if no locator provided
- Waits for pane to become hidden or detached

---

### 4. wait_for_network_idle()

Wait for network activity to become idle.

**Signature:**
```python
async def wait_for_network_idle(
    timeout: Optional[int] = None,
    idle_time: int = 500,
) -> None
```

**Parameters:**
- `timeout`: Optional timeout in milliseconds
- `idle_time`: Minimum idle time in milliseconds (default: 500ms)

**Example:**
```python
# Wait for network idle with default settings
await element_manager.wait_for_network_idle()

# Wait with custom timeout
await element_manager.wait_for_network_idle(timeout=30000)

# Wait with longer idle time
await element_manager.wait_for_network_idle(timeout=30000, idle_time=1000)
```

**Use Cases:**
- After page navigation to ensure all resources loaded
- After AJAX requests complete
- Before taking screenshots to ensure page is stable
- When waiting for dynamic content to finish loading

**Behavior:**
- Waits until no network connections for at least 500ms (default)
- Includes XHR, fetch, and resource requests
- Useful for single-page applications with dynamic loading

---

## Common Patterns

### Pattern 1: Complete Page Load Workflow

```python
# Navigate to page
await page.goto("https://example.com/dashboard")

# Wait for page load
await element_manager.wait_for_load_state("load")

# Wait for any loading spinners
await element_manager.wait_for_spinner("css=#loading-spinner")

# Wait for network idle
await element_manager.wait_for_network_idle()

# Now safe to interact with page
await element_manager.click("css=#submit-button")
```

### Pattern 2: Modal Dialog Handling

```python
# Click button that opens modal
await element_manager.click("css=#open-modal-button")

# Wait for modal to appear
await element_manager.wait_for_element("css=.modal-dialog", state="visible")

# Interact with modal
await element_manager.fill("css=#modal-input", "test data")
await element_manager.click("css=#modal-submit")

# Wait for modal to close
await element_manager.wait_for_disabled_pane("css=.modal-backdrop")

# Continue with main page
```

### Pattern 3: AJAX Request Handling

```python
# Click button that triggers AJAX
await element_manager.click("css=#load-data-button")

# Wait for loading indicator
await element_manager.wait_for_spinner("css=.ajax-loader")

# Wait for network idle to ensure request completed
await element_manager.wait_for_network_idle()

# Verify data loaded
data = await element_manager.get_text("css=#data-container")
assert "Expected Data" in data
```

### Pattern 4: Form Submission with Loading

```python
# Fill form
await element_manager.fill("css=#username", "testuser")
await element_manager.fill("css=#password", "password123")

# Submit form
await element_manager.click("css=#submit-button")

# Wait for submission spinner
await element_manager.wait_for_spinner("css=#submit-spinner")

# Wait for any disabled overlay
await element_manager.wait_for_disabled_pane()

# Wait for network idle
await element_manager.wait_for_network_idle()

# Verify success
success_msg = await element_manager.get_text("css=.success-message")
assert "Success" in success_msg
```

### Pattern 5: Single Page Application Navigation

```python
# Click navigation link
await element_manager.click("css=#nav-dashboard")

# Wait for route change (DOM content loaded)
await element_manager.wait_for_load_state("domcontentloaded")

# Wait for any loading indicators
await element_manager.wait_for_spinner("css=.page-loader")

# Wait for network idle (API calls)
await element_manager.wait_for_network_idle()

# Page is ready for interaction
```

## Error Handling

All synchronization methods raise `TimeoutException` if the condition is not met within the timeout period:

```python
from raptor.core.exceptions import TimeoutException

try:
    await element_manager.wait_for_spinner("css=#spinner", timeout=5000)
except TimeoutException as e:
    print(f"Spinner did not disappear: {e}")
    # Handle timeout - maybe take screenshot for debugging
    await page.screenshot(path="timeout_error.png")
```

## Best Practices

### 1. Use Appropriate Timeouts

```python
# Short timeout for elements that should appear quickly
await element_manager.wait_for_spinner("css=#quick-loader", timeout=3000)

# Longer timeout for slow operations
await element_manager.wait_for_network_idle(timeout=30000)
```

### 2. Combine Multiple Synchronization Methods

```python
# Comprehensive wait strategy
await element_manager.wait_for_load_state("load")
await element_manager.wait_for_spinner("css=#spinner")
await element_manager.wait_for_disabled_pane()
await element_manager.wait_for_network_idle()
```

### 3. Use Default Modal Detection

```python
# Let the framework detect common modal patterns
await element_manager.wait_for_disabled_pane()  # No locator needed
```

### 4. Handle Optional Spinners

```python
# If spinner might not appear, use shorter timeout
try:
    await element_manager.wait_for_spinner("css=#optional-spinner", timeout=2000)
except TimeoutException:
    # Spinner didn't appear, which is fine
    pass
```

### 5. Wait for Network Idle Before Assertions

```python
# Ensure all data is loaded before verifying
await element_manager.wait_for_network_idle()

# Now safe to assert on dynamic content
data = await element_manager.get_text("css=#dynamic-data")
assert data == "Expected Value"
```

## Performance Considerations

### Minimize Wait Times

```python
# Bad: Always wait maximum time
await element_manager.wait_for_spinner("css=#spinner", timeout=30000)

# Good: Use reasonable timeout
await element_manager.wait_for_spinner("css=#spinner", timeout=5000)
```

### Use Specific Locators

```python
# Bad: Generic locator might match wrong element
await element_manager.wait_for_spinner("css=.spinner")

# Good: Specific locator
await element_manager.wait_for_spinner("css=#main-content-spinner")
```

### Avoid Unnecessary Waits

```python
# Bad: Wait for everything always
await element_manager.wait_for_load_state("load")
await element_manager.wait_for_load_state("domcontentloaded")
await element_manager.wait_for_load_state("networkidle")

# Good: Wait for what you need
await element_manager.wait_for_load_state("networkidle")  # Implies others
```

## Troubleshooting

### Spinner Never Disappears

**Problem:** `wait_for_spinner()` times out

**Solutions:**
1. Verify spinner locator is correct
2. Check if spinner is actually hidden (not just invisible)
3. Increase timeout if operation is legitimately slow
4. Check browser console for JavaScript errors

```python
# Debug spinner state
count = await element_manager.get_element_count("css=#spinner")
print(f"Spinner count: {count}")

is_visible = await element_manager.is_visible("css=#spinner")
print(f"Spinner visible: {is_visible}")
```

### Network Never Becomes Idle

**Problem:** `wait_for_network_idle()` times out

**Solutions:**
1. Check for polling requests that never stop
2. Increase timeout for slow networks
3. Use `wait_for_load_state("load")` instead if appropriate

```python
# Alternative: Wait for specific element instead
await element_manager.wait_for_element("css=#data-loaded-indicator")
```

### Modal Not Detected

**Problem:** `wait_for_disabled_pane()` doesn't find modal

**Solutions:**
1. Provide specific locator instead of using defaults
2. Check modal's actual CSS classes
3. Verify modal is actually in DOM (not just hidden)

```python
# Debug modal presence
modal_count = await element_manager.get_element_count("css=.modal")
print(f"Modal count: {modal_count}")
```

## Requirements Validation

These synchronization methods satisfy the following requirements:

- **Requirement 5.1**: ✓ Wait for page load completion automatically
- **Requirement 5.2**: ✓ Wait for elements with configurable timeouts
- **Requirement 5.3**: ✓ Wait for spinners/loading indicators to disappear
- **Requirement 5.4**: ✓ Wait for disabled panes/modal dialogs
- **Requirement 5.5**: ✓ Wait for network idle state

## Related Documentation

- [Element Manager Implementation](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Browser Manager Implementation](BROWSER_MANAGER_IMPLEMENTATION.md)
- [Exception Handling](../raptor/core/exceptions.py)
- [Configuration Guide](CONFIG_MANAGER_IMPLEMENTATION.md)

## Examples

See [synchronization_example.py](../examples/synchronization_example.py) for complete working examples.
