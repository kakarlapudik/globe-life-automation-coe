# Wait and Synchronization Helpers - Quick Reference

## Import

```python
from raptor.utils.wait_helpers import (
    # Wait Conditions
    WaitCondition,
    ElementTextContains,
    ElementAttributeEquals,
    ElementCountEquals,
    PageUrlContains,
    CustomCondition,
    
    # Polling
    wait_for_condition,
    poll_until,
    
    # Backoff and Retry
    ExponentialBackoff,
    retry_with_backoff,
    with_retry,
    
    # Timeout
    with_timeout,
    
    # Synchronization
    synchronized,
    
    # Concurrent Operations
    wait_for_all,
    wait_for_any,
)
```

---

## Wait Conditions

### ElementTextContains

```python
condition = ElementTextContains(locator, "text", case_sensitive=True)
result = await wait_for_condition(condition, timeout=10000)
```

### ElementAttributeEquals

```python
condition = ElementAttributeEquals(locator, "class", "active")
await wait_for_condition(condition, timeout=5000)
```

### ElementCountEquals

```python
condition = ElementCountEquals(locator, 5)
await wait_for_condition(condition, timeout=10000)
```

### PageUrlContains

```python
condition = PageUrlContains(page, "/dashboard")
await wait_for_condition(condition, timeout=10000)
```

### CustomCondition

```python
async def check():
    return await some_check()

condition = CustomCondition(check, "description")
result = await wait_for_condition(condition, timeout=10000)
```

---

## Polling

### wait_for_condition

```python
result = await wait_for_condition(
    condition,
    timeout=30000,           # milliseconds
    poll_interval=500,       # milliseconds
    error_message="Custom error"
)
```

### poll_until

```python
result = await poll_until(
    check_func,
    timeout=30000,           # milliseconds
    poll_interval=500,       # milliseconds
    error_message="Custom error"
)
```

---

## Exponential Backoff

### Create Backoff

```python
backoff = ExponentialBackoff(
    initial_delay=1.0,       # seconds
    max_delay=60.0,          # seconds
    factor=2.0,              # multiplication factor
    jitter=True              # add randomness
)
```

### Get Delay

```python
delay = backoff.get_delay(attempt)  # Returns delay in seconds
```

### Sleep with Backoff

```python
await backoff.sleep(attempt)
```

---

## Retry

### retry_with_backoff

```python
result = await retry_with_backoff(
    func,
    max_attempts=3,
    initial_delay=1.0,
    max_delay=60.0,
    factor=2.0,
    exceptions=(Exception,),
    *args,
    **kwargs
)
```

### @with_retry Decorator

```python
@with_retry(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=60.0,
    factor=2.0,
    exceptions=(Exception,)
)
async def func():
    pass
```

---

## Timeout

### @with_timeout Decorator

```python
@with_timeout(30.0)  # seconds
async def func():
    pass
```

---

## Synchronization

### @synchronized Decorator

```python
class MyClass:
    def __init__(self):
        self._lock = asyncio.Lock()
    
    @synchronized()  # Uses self._lock
    async def method(self):
        pass
    
    @synchronized(lock_attr="_custom_lock")
    async def other_method(self):
        pass
```

---

## Concurrent Operations

### wait_for_all

```python
results = await wait_for_all(
    awaitable1(),
    awaitable2(),
    awaitable3(),
    timeout=30.0,            # seconds (optional)
    return_exceptions=False  # return exceptions instead of raising
)
```

### wait_for_any

```python
result, index = await wait_for_any(
    awaitable1(),
    awaitable2(),
    awaitable3(),
    timeout=30.0  # seconds (optional)
)
```

---

## Common Patterns

### Wait for Element Text

```python
locator = page.locator("#status")
condition = ElementTextContains(locator, "Complete")
await wait_for_condition(condition, timeout=10000)
```

### Retry API Call

```python
@with_retry(max_attempts=5, exceptions=(ConnectionError,))
async def api_call():
    return await api.get("/data")
```

### Timeout Long Operation

```python
@with_timeout(60.0)
async def long_operation():
    await process_data()
```

### Synchronized Access

```python
class DataManager:
    def __init__(self):
        self._lock = asyncio.Lock()
    
    @synchronized()
    async def update(self, data):
        self.data = data
```

### Fetch from Multiple Sources

```python
result, index = await wait_for_any(
    fetch_from_cache(),
    fetch_from_database(),
    fetch_from_api()
)
```

### Wait for Multiple Conditions

```python
results = await wait_for_all(
    check_condition1(),
    check_condition2(),
    check_condition3(),
    timeout=30.0
)
```

---

## Parameters Reference

### Timeouts

- `timeout`: Maximum wait time in **milliseconds** (wait_for_condition, poll_until)
- `timeout`: Maximum wait time in **seconds** (with_timeout, wait_for_all, wait_for_any)

### Retry Parameters

- `max_attempts`: Maximum number of retry attempts (default: 3)
- `initial_delay`: Starting delay in seconds (default: 1.0)
- `max_delay`: Maximum delay cap in seconds (default: 60.0)
- `factor`: Multiplication factor for backoff (default: 2.0)
- `exceptions`: Tuple of exception types to catch (default: (Exception,))

### Polling Parameters

- `poll_interval`: Time between checks in milliseconds (default: 500)
- `error_message`: Custom error message for timeout (optional)

---

## Exception Handling

### TimeoutException

Raised when operations exceed timeout:

```python
from raptor.core.exceptions import TimeoutException

try:
    await wait_for_condition(condition, timeout=5000)
except TimeoutException as e:
    print(f"Operation timed out: {e}")
```

### Retry Exceptions

Only specified exceptions are retried:

```python
@with_retry(exceptions=(ConnectionError, TimeoutError))
async def func():
    # ValueError will NOT be retried
    if invalid:
        raise ValueError("Invalid")
    
    # ConnectionError WILL be retried
    return await network_call()
```

---

## Best Practices

1. **Use appropriate timeouts**: Short for fast ops, long for slow ops
2. **Provide error messages**: Help debugging with clear messages
3. **Limit retry attempts**: Avoid infinite retries
4. **Handle specific exceptions**: Only retry transient errors
5. **Log progress**: Track long-running operations
6. **Use synchronization**: Prevent race conditions
7. **Combine strategies**: Use retry + timeout together

---

## Examples

### Complete Example

```python
from raptor.utils.wait_helpers import (
    ElementTextContains,
    wait_for_condition,
    with_retry,
    with_timeout,
    wait_for_all
)

@with_retry(max_attempts=3, exceptions=(ConnectionError,))
@with_timeout(30.0)
async def fetch_data():
    return await api.get("/data")

async def wait_for_page_ready(page):
    # Wait for multiple conditions
    async def check_title():
        locator = page.locator("h1")
        condition = ElementTextContains(locator, "Dashboard")
        return await wait_for_condition(condition, timeout=10000)
    
    async def check_content():
        await page.wait_for_load_state("networkidle")
        return True
    
    await wait_for_all(
        check_title(),
        check_content(),
        timeout=30.0
    )

# Use the functions
data = await fetch_data()
await wait_for_page_ready(page)
```

---

## See Also

- [WAIT_HELPERS_GUIDE.md](WAIT_HELPERS_GUIDE.md) - Comprehensive guide with detailed examples
- [wait_helpers_example.py](../examples/wait_helpers_example.py) - Working code examples
- [test_wait_helpers.py](../tests/test_wait_helpers.py) - Test suite
