# Synchronization Methods - Quick Reference

## Quick Method Overview

| Method | Purpose | Common Use Case |
|--------|---------|-----------------|
| `wait_for_load_state()` | Wait for page load state | After navigation |
| `wait_for_spinner()` | Wait for loading indicator | After button click |
| `wait_for_disabled_pane()` | Wait for modal to close | After modal interaction |
| `wait_for_network_idle()` | Wait for AJAX/network | Before assertions |

## Method Signatures

```python
# Wait for page load state
await element_manager.wait_for_load_state(
    state: str = "load",  # "load", "domcontentloaded", "networkidle"
    timeout: Optional[int] = None
)

# Wait for spinner to disappear
await element_manager.wait_for_spinner(
    spinner_locator: str,
    timeout: Optional[int] = None,
    check_interval: float = 0.5
)

# Wait for modal/disabled pane
await element_manager.wait_for_disabled_pane(
    pane_locator: Optional[str] = None,  # None = use defaults
    timeout: Optional[int] = None
)

# Wait for network idle
await element_manager.wait_for_network_idle(
    timeout: Optional[int] = None,
    idle_time: int = 500
)
```

## Common Patterns

### Pattern 1: After Navigation
```python
await page.goto("https://example.com")
await element_manager.wait_for_load_state("load")
await element_manager.wait_for_network_idle()
```

### Pattern 2: After Button Click
```python
await element_manager.click("css=#submit-button")
await element_manager.wait_for_spinner("css=#loading-spinner")
await element_manager.wait_for_network_idle()
```

### Pattern 3: Modal Handling
```python
await element_manager.click("css=#open-modal")
# ... interact with modal ...
await element_manager.click("css=#modal-close")
await element_manager.wait_for_disabled_pane("css=.modal-backdrop")
```

### Pattern 4: Complete Workflow
```python
# Navigate
await page.goto(url)
await element_manager.wait_for_load_state("load")

# Wait for spinners
await element_manager.wait_for_spinner("css=#spinner")

# Wait for modals
await element_manager.wait_for_disabled_pane()

# Wait for network
await element_manager.wait_for_network_idle()

# Now safe to interact
```

## Default Modal Selectors

When `wait_for_disabled_pane()` is called without a locator, it checks:
- `.modal-backdrop`
- `.modal-overlay`
- `.overlay`
- `[role='dialog']`
- `.disabled-pane`
- `.loading-overlay`

## Error Handling

All methods raise `TimeoutException` on timeout:

```python
from raptor.core.exceptions import TimeoutException

try:
    await element_manager.wait_for_spinner("css=#spinner", timeout=5000)
except TimeoutException:
    # Handle timeout
    print("Spinner did not disappear in time")
```

## Tips

### ✅ DO
- Use appropriate timeouts for each operation
- Combine methods for comprehensive waiting
- Use specific locators when possible
- Handle timeouts gracefully

### ❌ DON'T
- Use excessively long timeouts
- Wait for everything always
- Ignore timeout exceptions
- Use generic locators

## Performance Tips

```python
# Good: Specific and efficient
await element_manager.wait_for_spinner("css=#main-spinner", timeout=5000)

# Bad: Generic and slow
await element_manager.wait_for_spinner("css=.spinner", timeout=30000)
```

## See Also

- [Complete Guide](SYNCHRONIZATION_METHODS_GUIDE.md)
- [Examples](../examples/synchronization_example.py)
- [Element Manager](ELEMENT_MANAGER_IMPLEMENTATION.md)
