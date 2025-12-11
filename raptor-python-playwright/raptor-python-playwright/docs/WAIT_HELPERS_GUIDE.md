## Wait and Synchronization Helpers Guide

### Overview

The Wait and Synchronization Helpers module provides advanced utilities for handling timing, waiting, and synchronization in test automation. These tools help you write more reliable tests that can handle dynamic page loading, network delays, and race conditions.

### Key Features

- **Custom Wait Conditions**: Define complex wait conditions beyond simple element visibility
- **Polling Mechanism**: Repeatedly check conditions until they're met or timeout
- **Exponential Backoff**: Implement intelligent retry delays that increase over time
- **Retry Decorators**: Automatically retry functions that may fail transiently
- **Timeout Handling**: Enforce time limits on operations
- **Synchronization**: Coordinate concurrent operations safely

---

## Custom Wait Conditions

### Built-in Wait Conditions

#### ElementTextContains

Wait for element text to contain a specific string.

```python
from raptor.utils.wait_helpers import ElementTextContains, wait_for_condition

# Wait for element to contain text
locator = page.locator("#status")
condition = ElementTextContains(locator, "Complete", case_sensitive=False)
result = await wait_for_condition(condition, timeout=10000)
print(f"Element text: {result}")
```

#### ElementAttributeEquals

Wait for element attribute to equal a specific value.

```python
from raptor.utils.wait_helpers import ElementAttributeEquals, wait_for_condition

# Wait for element class to change
locator = page.locator("#button")
condition = ElementAttributeEquals(locator, "class", "active")
await wait_for_condition(condition, timeout=5000)
```

#### ElementCountEquals

Wait for a specific number of elements to exist.

```python
from raptor.utils.wait_helpers import ElementCountEquals, wait_for_condition

# Wait for exactly 5 items to appear
locator = page.locator(".list-item")
condition = ElementCountEquals(locator, 5)
await wait_for_condition(condition, timeout=10000)
```

#### PageUrlContains

Wait for page URL to contain a specific fragment.

```python
from raptor.utils.wait_helpers import PageUrlContains, wait_for_condition

# Wait for navigation to dashboard
condition = PageUrlContains(page, "/dashboard")
await wait_for_condition(condition, timeout=10000)
```

### Creating Custom Conditions

Create your own wait conditions by subclassing `WaitCondition`:

```python
from raptor.utils.wait_helpers import WaitCondition, WaitConditionResult

class ElementHasChildren(WaitCondition):
    """Wait for element to have child elements."""
    
    def __init__(self, locator, min_children: int = 1):
        self.locator = locator
        self.min_children = min_children
    
    async def check(self) -> WaitConditionResult:
        try:
            children = await self.locator.locator("*").count()
            if children >= self.min_children:
                return WaitConditionResult(True, children)
            
            return WaitConditionResult(
                False,
                message=f"Element has {children} children, need {self.min_children}"
            )
        except Exception as e:
            return WaitConditionResult(False, message=str(e))

# Use custom condition
locator = page.locator("#container")
condition = ElementHasChildren(locator, min_children=3)
child_count = await wait_for_condition(condition, timeout=10000)
print(f"Element has {child_count} children")
```

### Using Custom Functions

For simple conditions, use `CustomCondition`:

```python
from raptor.utils.wait_helpers import CustomCondition, wait_for_condition

# Wait for API to be ready
async def check_api():
    response = await api_client.health_check()
    return response.status == "ready"

condition = CustomCondition(check_api, "API ready")
await wait_for_condition(condition, timeout=30000)
```

---

## Polling Mechanism

### Basic Polling

Use `poll_until` for simple polling scenarios:

```python
from raptor.utils.wait_helpers import poll_until

# Poll until function returns truthy value
async def check_data_loaded():
    data = await get_data()
    return data if data else None

result = await poll_until(
    check_data_loaded,
    timeout=30000,      # 30 seconds
    poll_interval=1000  # Check every 1 second
)
```

### Advanced Polling with Conditions

Use `wait_for_condition` for more control:

```python
from raptor.utils.wait_helpers import wait_for_condition, CustomCondition

async def check_processing_complete():
    status = await get_processing_status()
    return status == "complete"

condition = CustomCondition(check_processing_complete, "processing complete")
await wait_for_condition(
    condition,
    timeout=60000,
    poll_interval=2000,
    error_message="Processing did not complete in time"
)
```

### Polling Best Practices

1. **Choose appropriate intervals**: Balance between responsiveness and resource usage
2. **Set realistic timeouts**: Consider worst-case scenarios
3. **Provide clear error messages**: Help debugging when timeouts occur
4. **Log progress**: Use logging to track polling attempts

```python
import logging

logger = logging.getLogger(__name__)

async def check_with_logging():
    attempt = 0
    
    async def check():
        nonlocal attempt
        attempt += 1
        result = await some_check()
        
        if attempt % 5 == 0:
            logger.info(f"Still waiting... (attempt {attempt})")
        
        return result

    return await poll_until(check, timeout=60000, poll_interval=1000)
```

---

## Exponential Backoff

### Basic Usage

```python
from raptor.utils.wait_helpers import ExponentialBackoff
import asyncio

backoff = ExponentialBackoff(
    initial_delay=1.0,   # Start with 1 second
    max_delay=60.0,      # Cap at 60 seconds
    factor=2.0,          # Double each time
    jitter=True          # Add randomness
)

for attempt in range(5):
    try:
        await perform_operation()
        break
    except TransientError:
        if attempt < 4:
            await backoff.sleep(attempt)
```

### Backoff Parameters

- **initial_delay**: Starting delay in seconds
- **max_delay**: Maximum delay cap in seconds
- **factor**: Multiplication factor (typically 2.0)
- **jitter**: Add randomness to prevent thundering herd

### Calculating Delays

```python
backoff = ExponentialBackoff(initial_delay=1.0, factor=2.0, jitter=False)

# Get delays without sleeping
delays = [backoff.get_delay(i) for i in range(5)]
# [1.0, 2.0, 4.0, 8.0, 16.0]
```

---

## Retry with Backoff

### Function-based Retry

```python
from raptor.utils.wait_helpers import retry_with_backoff

async def flaky_operation():
    response = await api_call()
    if response.status != 200:
        raise ConnectionError("API unavailable")
    return response.data

# Retry with exponential backoff
result = await retry_with_backoff(
    flaky_operation,
    max_attempts=5,
    initial_delay=1.0,
    max_delay=30.0,
    factor=2.0,
    exceptions=(ConnectionError, TimeoutError)
)
```

### Decorator-based Retry

```python
from raptor.utils.wait_helpers import with_retry

@with_retry(
    max_attempts=3,
    initial_delay=2.0,
    exceptions=(ConnectionError, TimeoutError)
)
async def fetch_data():
    response = await api.get("/data")
    return response.json()

# Automatically retries on failure
data = await fetch_data()
```

### Selective Exception Handling

Only retry specific exceptions:

```python
@with_retry(
    max_attempts=5,
    exceptions=(ConnectionError, TimeoutError)  # Only retry these
)
async def critical_operation():
    # ValueError will not be retried
    if invalid_input:
        raise ValueError("Invalid input")
    
    # ConnectionError will be retried
    return await network_call()
```

---

## Timeout Handling

### Timeout Decorator

```python
from raptor.utils.wait_helpers import with_timeout

@with_timeout(30.0)  # 30 second timeout
async def long_running_operation():
    await process_large_dataset()
    return "completed"

try:
    result = await long_running_operation()
except TimeoutException:
    print("Operation timed out")
```

### Combining Retry and Timeout

```python
from raptor.utils.wait_helpers import with_retry, with_timeout

@with_retry(max_attempts=3, initial_delay=1.0)
@with_timeout(10.0)
async def fetch_with_retry_and_timeout():
    return await api.get_data()

# Each attempt has 10 second timeout
# Up to 3 attempts will be made
result = await fetch_with_retry_and_timeout()
```

---

## Synchronization

### Synchronized Decorator

Prevent concurrent execution of methods:

```python
from raptor.utils.wait_helpers import synchronized
import asyncio

class DataManager:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.data = []
    
    @synchronized()
    async def add_data(self, item):
        # Only one coroutine can execute this at a time
        current = self.data.copy()
        await asyncio.sleep(0.1)  # Simulate processing
        current.append(item)
        self.data = current

manager = DataManager()

# Safe concurrent access
await asyncio.gather(
    manager.add_data("item1"),
    manager.add_data("item2"),
    manager.add_data("item3")
)
```

### Custom Lock Attribute

```python
class ResourceManager:
    def __init__(self):
        self._resource_lock = asyncio.Lock()
    
    @synchronized(lock_attr="_resource_lock")
    async def access_resource(self):
        # Uses _resource_lock instead of default _lock
        pass
```

---

## Concurrent Operations

### Wait for All

Wait for all operations to complete:

```python
from raptor.utils.wait_helpers import wait_for_all

async def fetch_users():
    return await api.get("/users")

async def fetch_products():
    return await api.get("/products")

async def fetch_orders():
    return await api.get("/orders")

# Wait for all to complete
users, products, orders = await wait_for_all(
    fetch_users(),
    fetch_products(),
    fetch_orders(),
    timeout=30.0
)
```

### Wait for Any

Wait for first operation to complete:

```python
from raptor.utils.wait_helpers import wait_for_any

async def fetch_from_cache():
    return await cache.get("data")

async def fetch_from_database():
    return await db.query("SELECT * FROM data")

async def fetch_from_api():
    return await api.get("/data")

# Use first available result
result, index = await wait_for_any(
    fetch_from_cache(),
    fetch_from_database(),
    fetch_from_api(),
    timeout=10.0
)

sources = ["cache", "database", "api"]
print(f"Got data from {sources[index]}")
```

### Handling Exceptions

```python
# Return exceptions instead of raising
results = await wait_for_all(
    operation1(),
    operation2(),
    operation3(),
    return_exceptions=True
)

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Operation {i} failed: {result}")
    else:
        print(f"Operation {i} succeeded: {result}")
```

---

## Common Patterns

### Pattern 1: Wait for Dynamic Content

```python
from raptor.utils.wait_helpers import ElementCountEquals, wait_for_condition

async def wait_for_search_results(page, expected_count):
    """Wait for search results to load."""
    results_locator = page.locator(".search-result")
    condition = ElementCountEquals(results_locator, expected_count)
    
    await wait_for_condition(
        condition,
        timeout=10000,
        error_message=f"Expected {expected_count} search results"
    )
```

### Pattern 2: Retry API Calls

```python
from raptor.utils.wait_helpers import with_retry

@with_retry(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=30.0,
    exceptions=(ConnectionError, TimeoutError)
)
async def reliable_api_call(endpoint):
    """Make API call with automatic retry."""
    response = await api.get(endpoint)
    if response.status >= 500:
        raise ConnectionError(f"Server error: {response.status}")
    return response.json()
```

### Pattern 3: Wait for Multiple Conditions

```python
from raptor.utils.wait_helpers import wait_for_all, CustomCondition, wait_for_condition

async def wait_for_page_ready(page):
    """Wait for multiple page ready conditions."""
    
    async def check_title():
        condition = CustomCondition(
            lambda: page.title() if page.title() else None,
            "page title set"
        )
        return await wait_for_condition(condition, timeout=5000)
    
    async def check_content():
        await page.wait_for_load_state("networkidle")
        return True
    
    async def check_no_spinners():
        spinner_count = await page.locator(".spinner").count()
        if spinner_count == 0:
            return True
        raise Exception("Spinners still visible")
    
    # Wait for all conditions
    await wait_for_all(
        check_title(),
        check_content(),
        check_no_spinners(),
        timeout=30.0
    )
```

### Pattern 4: Graceful Degradation

```python
from raptor.utils.wait_helpers import wait_for_any

async def get_data_with_fallback():
    """Try multiple data sources, use first available."""
    
    async def from_cache():
        data = await cache.get("key")
        if data:
            return {"source": "cache", "data": data}
        raise Exception("Cache miss")
    
    async def from_primary_db():
        return {"source": "primary", "data": await primary_db.query()}
    
    async def from_backup_db():
        return {"source": "backup", "data": await backup_db.query()}
    
    try:
        result, index = await wait_for_any(
            from_cache(),
            from_primary_db(),
            from_backup_db(),
            timeout=10.0
        )
        return result
    except TimeoutException:
        return {"source": "default", "data": get_default_data()}
```

---

## Best Practices

### 1. Choose Appropriate Timeouts

```python
# Short timeout for fast operations
await poll_until(check_cache, timeout=1000)

# Medium timeout for network operations
await poll_until(check_api, timeout=10000)

# Long timeout for batch processing
await poll_until(check_batch_complete, timeout=300000)
```

### 2. Use Meaningful Error Messages

```python
await wait_for_condition(
    condition,
    timeout=10000,
    error_message="Login form did not appear after navigation"
)
```

### 3. Log Progress for Long Operations

```python
import logging

logger = logging.getLogger(__name__)

async def wait_with_progress(condition, timeout):
    start_time = time.time()
    
    while True:
        result = await condition.check()
        if result.success:
            return result.value
        
        elapsed = time.time() - start_time
        if elapsed > timeout / 1000:
            raise TimeoutException("Timeout")
        
        if int(elapsed) % 10 == 0:
            logger.info(f"Still waiting... ({elapsed:.0f}s elapsed)")
        
        await asyncio.sleep(0.5)
```

### 4. Handle Cleanup in Retry Logic

```python
@with_retry(max_attempts=3)
async def operation_with_cleanup():
    resource = None
    try:
        resource = await acquire_resource()
        return await use_resource(resource)
    finally:
        if resource:
            await release_resource(resource)
```

### 5. Combine Multiple Strategies

```python
@with_retry(max_attempts=3, initial_delay=1.0)
@with_timeout(30.0)
async def robust_operation():
    """Operation with both retry and timeout."""
    return await complex_task()
```

---

## Troubleshooting

### Issue: Timeouts Too Short

**Problem**: Operations timing out prematurely

**Solution**: Increase timeout or poll interval

```python
# Before
await poll_until(check, timeout=5000, poll_interval=100)

# After
await poll_until(check, timeout=30000, poll_interval=500)
```

### Issue: Too Many Retries

**Problem**: Retrying operations that will never succeed

**Solution**: Limit retry attempts and handle specific exceptions

```python
@with_retry(
    max_attempts=3,  # Limit attempts
    exceptions=(ConnectionError,)  # Only retry transient errors
)
async def operation():
    # ValueError will not be retried
    if invalid:
        raise ValueError("Invalid input")
    return await network_call()
```

### Issue: Race Conditions

**Problem**: Concurrent access causing data corruption

**Solution**: Use synchronization

```python
class DataStore:
    def __init__(self):
        self._lock = asyncio.Lock()
    
    @synchronized()
    async def update(self, data):
        # Safe concurrent access
        pass
```

---

## API Reference

See [WAIT_HELPERS_QUICK_REFERENCE.md](WAIT_HELPERS_QUICK_REFERENCE.md) for complete API documentation.
