## Test Execution Control Guide

This guide covers the test execution control features in the RAPTOR framework, including test filtering, skip functionality, retry mechanisms, and parallel execution.

### Overview

The Test Execution Control module provides:
- **Test Filtering**: Filter tests by ID, iteration, tag, or marker
- **Skip Functionality**: Skip tests with detailed reason logging
- **Retry Mechanism**: Automatically retry flaky tests
- **Parallel Execution**: Run tests in parallel with pytest-xdist

### Test Filtering

#### Filter by Test ID

Run specific tests by their node ID:

```bash
# Run single test
pytest --test-id test_login

# Run multiple tests
pytest --test-id test_login --test-id test_logout

# Run all tests in a file
pytest --test-id test_authentication.py
```

#### Filter by Iteration

For data-driven tests with iteration parameters:

```bash
# Run specific iterations
pytest --iteration 1 --iteration 2

# Run all tests for iteration 1
pytest --iteration 1
```

#### Filter by Tag

Filter tests by tags in test names:

```bash
# Run smoke tests
pytest --tag smoke

# Run smoke and regression tests
pytest --tag smoke --tag regression

# Exclude tests with specific tag
pytest --exclude-tag skip
```

#### Filter by Marker

Filter tests by pytest markers:

```bash
# Run tests marked as slow
pytest --marker slow

# Run integration tests
pytest --marker integration

# Run browser tests
pytest --marker browser
```

#### Combining Filters

Filters can be combined for precise test selection:

```bash
# Run smoke tests for iteration 1
pytest --tag smoke --iteration 1

# Run specific test excluding flaky ones
pytest --test-id test_feature --exclude-tag flaky
```

### Skip Functionality

#### Basic Skip

Skip a test with a reason:

```python
from raptor.core.test_execution_control import skip_test, SkipReason

def test_feature():
    skip_test("Feature not implemented", SkipReason.NOT_IMPLEMENTED)
    # Test code here
```

#### Conditional Skip

Skip based on a condition:

```python
from raptor.core.test_execution_control import skip_if, skip_unless

def test_database_feature(database):
    # Skip if database not available
    skip_if(database is None, "Database not configured", SkipReason.CONFIGURATION)
    
    # Test code here

def test_platform_feature():
    import platform
    # Skip unless on Windows
    skip_unless(
        platform.system() == "Windows",
        "Only supported on Windows",
        SkipReason.PLATFORM
    )
    
    # Test code here
```

#### Skip Reasons

Standard skip reasons are provided:

- `SkipReason.NOT_IMPLEMENTED`: Feature not yet implemented
- `SkipReason.ENVIRONMENT`: Not available in current environment
- `SkipReason.DEPENDENCY`: Required dependency not available
- `SkipReason.CONFIGURATION`: Required configuration missing
- `SkipReason.PLATFORM`: Not supported on current platform
- `SkipReason.FLAKY`: Test is known to be flaky
- `SkipReason.MANUAL`: Manual test - requires human interaction
- `SkipReason.CUSTOM`: Custom skip reason

### Retry Mechanism

#### Basic Retry

Automatically retry flaky tests:

```python
from raptor.core.test_execution_control import retry_on_failure

@retry_on_failure(max_retries=3, retry_delay=1.0)
async def test_flaky_feature(page):
    await page.goto("https://example.com")
    # Flaky test code
```

#### Retry Configuration

Customize retry behavior:

```python
@retry_on_failure(
    max_retries=5,              # Maximum retry attempts
    retry_delay=2.0,            # Initial delay between retries
    exponential_backoff=True,   # Double delay after each retry
    log_retries=True            # Log each retry attempt
)
async def test_with_custom_retry(page):
    # Test code
    pass
```

#### Retry on Specific Exceptions

Only retry on certain exception types:

```python
from playwright.async_api import TimeoutError

@retry_on_failure(
    max_retries=3,
    retry_delay=1.0,
    retry_on_exceptions=[TimeoutError, AssertionError]
)
async def test_with_exception_filter(page):
    # Only retries on TimeoutError or AssertionError
    # Other exceptions fail immediately
    pass
```

#### Synchronous Tests

Retry decorator works with both async and sync tests:

```python
@retry_on_failure(max_retries=3, retry_delay=1.0)
def test_sync_flaky():
    # Synchronous test code
    pass
```

### Parallel Execution

#### Running Tests in Parallel

Use pytest-xdist for parallel execution:

```bash
# Auto-detect CPU count
pytest -n auto

# Use specific number of workers
pytest -n 4

# Distribute by test file
pytest -n auto --dist loadfile

# Distribute by test function
pytest -n auto --dist loadscope
```

#### Test Isolation

Each parallel worker has isolated resources:

```python
@pytest.fixture
def worker_specific_resource(worker_id):
    """Create worker-specific resource."""
    return f"resource_{worker_id}"

def test_parallel_isolation(worker_specific_resource):
    # Each worker gets unique resource
    assert worker_specific_resource is not None
```

#### Parallel-Safe Fixtures

Ensure fixtures are parallel-safe:

```python
@pytest.fixture(scope="function")
async def isolated_browser(browser_manager, worker_id):
    """Create isolated browser for each worker."""
    browser = await browser_manager.launch_browser(
        "chromium",
        headless=True
    )
    yield browser
    await browser_manager.close_browser()
```

### Command-Line Options

#### Test Execution Control Options

```bash
# Filter options
--test-id ID          Filter tests by ID (can be used multiple times)
--iteration NUM       Filter tests by iteration number
--tag TAG             Filter tests by tag
--marker MARKER       Filter tests by pytest marker
--exclude-tag TAG     Exclude tests with tag

# Retry options
--max-retries NUM     Maximum number of retries for failed tests

# Parallel execution (pytest-xdist)
-n NUM                Number of parallel workers
--dist MODE           Distribution mode (loadfile, loadscope, etc.)
```

### Best Practices

#### 1. Use Appropriate Skip Reasons

Always use descriptive skip reasons:

```python
# Good
skip_test("Database connection requires VPN", SkipReason.DEPENDENCY)

# Bad
skip_test("Skipped", SkipReason.CUSTOM)
```

#### 2. Limit Retry Attempts

Don't over-retry tests:

```python
# Good - reasonable retry count
@retry_on_failure(max_retries=3, retry_delay=1.0)

# Bad - too many retries
@retry_on_failure(max_retries=10, retry_delay=0.5)
```

#### 3. Use Exponential Backoff

For network-related flakiness:

```python
@retry_on_failure(
    max_retries=3,
    retry_delay=1.0,
    exponential_backoff=True  # 1s, 2s, 4s delays
)
async def test_network_operation(page):
    pass
```

#### 4. Filter Exceptions for Retry

Only retry on expected transient failures:

```python
from playwright.async_api import TimeoutError

@retry_on_failure(
    max_retries=3,
    retry_on_exceptions=[TimeoutError]  # Only retry timeouts
)
async def test_element_interaction(page):
    pass
```

#### 5. Tag Tests Appropriately

Use consistent tagging for filtering:

```python
@pytest.mark.smoke
def test_critical_path():
    """Critical smoke test."""
    pass

@pytest.mark.regression
def test_edge_case():
    """Regression test for edge case."""
    pass

@pytest.mark.flaky
@retry_on_failure(max_retries=3)
def test_known_flaky():
    """Known flaky test with retry."""
    pass
```

### Examples

#### Example 1: Smoke Test Suite

```python
import pytest
from raptor.core.test_execution_control import retry_on_failure

@pytest.mark.smoke
@retry_on_failure(max_retries=2, retry_delay=1.0)
async def test_smoke_login(page):
    """Smoke test for login functionality."""
    await page.goto("https://example.com/login")
    await page.fill("#username", "testuser")
    await page.fill("#password", "testpass")
    await page.click("#login-button")
    
    # Verify login success
    await page.wait_for_selector("#dashboard")

@pytest.mark.smoke
async def test_smoke_navigation(page):
    """Smoke test for basic navigation."""
    await page.goto("https://example.com")
    await page.click("text=About")
    assert "about" in page.url.lower()
```

Run smoke tests:
```bash
pytest --marker smoke -n auto
```

#### Example 2: Data-Driven Test with Iterations

```python
import pytest

@pytest.mark.parametrize("iteration,username,password", [
    (1, "user1", "pass1"),
    (2, "user2", "pass2"),
    (3, "user3", "pass3"),
])
async def test_login_iterations(page, iteration, username, password):
    """Data-driven login test."""
    await page.goto("https://example.com/login")
    await page.fill("#username", username)
    await page.fill("#password", password)
    await page.click("#login-button")
```

Run specific iterations:
```bash
pytest --iteration 1 --iteration 2
```

#### Example 3: Conditional Skip

```python
import pytest
import os
from raptor.core.test_execution_control import skip_unless, SkipReason

def test_production_feature():
    """Test that only runs in production environment."""
    env = os.getenv("TEST_ENV", "dev")
    skip_unless(
        env == "prod",
        "Only runs in production environment",
        SkipReason.ENVIRONMENT
    )
    
    # Production-specific test code
    pass
```

#### Example 4: Flaky Test with Retry

```python
from playwright.async_api import TimeoutError
from raptor.core.test_execution_control import retry_on_failure

@pytest.mark.flaky
@retry_on_failure(
    max_retries=3,
    retry_delay=2.0,
    exponential_backoff=True,
    retry_on_exceptions=[TimeoutError, AssertionError]
)
async def test_flaky_element_interaction(page):
    """Test with known flakiness - automatically retries."""
    await page.goto("https://example.com")
    
    # Sometimes slow to load
    await page.wait_for_selector("#dynamic-content", timeout=5000)
    
    # Sometimes fails to click
    await page.click("#submit-button")
    
    # Verify result
    assert await page.is_visible("#success-message")
```

### Troubleshooting

#### Tests Not Being Filtered

Check that filters match test attributes:

```bash
# Enable verbose output to see filter application
pytest --marker smoke -v

# Check test collection
pytest --collect-only --marker smoke
```

#### Retries Not Working

Verify decorator is applied correctly:

```python
# Correct - decorator before async def
@retry_on_failure(max_retries=3)
async def test_function():
    pass

# Incorrect - decorator after async def
async def test_function():
    pass
retry_on_failure(max_retries=3)(test_function)  # Won't work
```

#### Parallel Execution Issues

Ensure fixtures are parallel-safe:

```python
# Use function scope for isolation
@pytest.fixture(scope="function")
async def browser(browser_manager):
    # Each test gets fresh browser
    pass

# Avoid session scope for stateful resources
@pytest.fixture(scope="session")  # May cause issues
async def shared_browser():
    pass
```

### Performance Considerations

#### Optimal Parallel Workers

```bash
# Auto-detect (recommended)
pytest -n auto

# Manual tuning based on CPU cores
pytest -n 4  # For 4-core CPU

# Consider I/O vs CPU bound tests
pytest -n 8  # More workers for I/O bound tests
```

#### Retry Delays

Balance between test speed and reliability:

```python
# Fast retry for quick operations
@retry_on_failure(max_retries=3, retry_delay=0.5)

# Slower retry for network operations
@retry_on_failure(max_retries=3, retry_delay=2.0, exponential_backoff=True)
```

### Related Documentation

- [pytest Fixtures Guide](PYTEST_FIXTURES_GUIDE.md)
- [Test Reporter Guide](TEST_REPORTER_GUIDE.md)
- [Configuration Guide](CONFIG_MANAGER_IMPLEMENTATION.md)
- [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/)

### Requirements Validation

This implementation satisfies:
- **Requirement 12.1**: Test filtering by ID, iteration, and tag
- **Requirement 12.2**: Test skip functionality with reason logging
- **Requirement 12.3**: Retry mechanism for flaky tests
- **Requirement 12.4**: Parallel execution support with pytest-xdist
