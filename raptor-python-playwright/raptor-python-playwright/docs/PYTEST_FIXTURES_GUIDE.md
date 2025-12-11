# pytest Fixtures Guide

## Overview

The RAPTOR framework provides comprehensive pytest fixtures for test automation. These fixtures handle browser management, configuration, database connections, and test isolation, making it easy to write clean and maintainable tests.

## Available Fixtures

### Configuration Fixtures

#### `config`
**Scope:** Session  
**Type:** Synchronous

Provides a `ConfigManager` instance with test-specific configuration.

```python
def test_timeout_config(config):
    timeout = config.get("timeouts.default")
    assert timeout == 10000  # Test environment has shorter timeouts
```

**Features:**
- Loads test environment configuration
- Automatically sets headless mode for tests
- Provides shorter timeouts for faster test execution
- Session-scoped for efficiency

---

### Browser Management Fixtures

#### `browser_manager`
**Scope:** Function  
**Type:** Async

Provides a `BrowserManager` instance with automatic cleanup.

```python
@pytest.mark.asyncio
async def test_with_browser_manager(browser_manager):
    await browser_manager.launch_browser("chromium", headless=True)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    # Browser automatically cleaned up after test
```

**Features:**
- Function-scoped for test isolation
- Automatic browser cleanup
- Browser not launched by default (explicit launch required)
- Supports all browser types (chromium, firefox, webkit)

#### `browser`
**Scope:** Function  
**Type:** Async

Provides a launched `Browser` instance ready for use.

```python
@pytest.mark.asyncio
async def test_with_browser(browser):
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://example.com")
```

**Features:**
- Browser automatically launched
- Browser type configurable via `TEST_BROWSER` environment variable
- Headless mode enabled by default in tests
- Automatic cleanup

#### `context`
**Scope:** Function  
**Type:** Async

Provides a `BrowserContext` instance for test isolation.

```python
@pytest.mark.asyncio
async def test_with_context(context):
    page = await context.new_page()
    await page.goto("https://example.com")
```

**Features:**
- Fresh context for each test
- Configured with test-appropriate viewport (1920x1080)
- HTTPS errors ignored for testing
- Automatic cleanup

#### `page`
**Scope:** Function  
**Type:** Async

Provides a `Page` instance ready for navigation and interaction.

```python
@pytest.mark.asyncio
async def test_navigation(page):
    await page.goto("https://example.com")
    title = await page.title()
    assert "Example" in title
```

**Features:**
- Fresh page for each test
- Default timeout set to 10 seconds
- Automatic screenshot on test failure
- Automatic cleanup

---

### Element Management Fixtures

#### `element_manager`
**Scope:** Function  
**Type:** Async

Provides an `ElementManager` instance bound to the current page.

```python
@pytest.mark.asyncio
async def test_element_interaction(element_manager, page):
    await page.goto("https://example.com")
    await element_manager.click("css=#submit-button")
    await element_manager.fill("css=#username", "testuser")
```

**Features:**
- Bound to the page fixture
- Provides RAPTOR's element management capabilities
- Supports fallback locators
- Automatic waiting and retry logic

---

### Database Fixtures

#### `database`
**Scope:** Session  
**Type:** Synchronous

Provides a `DatabaseManager` instance for database operations.

```python
def test_database_query(database):
    if database is None:
        pytest.skip("Database not configured")
    
    result = database.execute_query("SELECT * FROM TestData")
    assert len(result) > 0
```

**Features:**
- Session-scoped for efficiency
- Returns `None` if database not configured
- Automatic connection pooling
- Automatic cleanup on session end
- Tests can skip if database unavailable

---

### Reporting Fixtures

#### `reporter`
**Scope:** Session  
**Type:** Synchronous

Provides a `TestReporter` instance for test reporting.

```python
def test_with_reporting(reporter):
    reporter.start_suite("My Test Suite")
    # ... test code ...
    reporter.end_suite()
```

**Features:**
- Session-scoped for aggregating results
- Generates HTML reports
- Tracks test statistics
- Embeds screenshots in reports

---

### Utility Fixtures

#### `temp_dir`
**Scope:** Function  
**Type:** Synchronous

Provides a temporary directory for file operations.

```python
def test_file_operations(temp_dir):
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
```

**Features:**
- Automatically cleaned up after test
- Unique directory per test
- Based on pytest's `tmp_path` fixture

#### `mock_page_url`
**Scope:** Function  
**Type:** Synchronous

Provides a mock page URL for testing.

```python
def test_url_handling(mock_page_url):
    assert mock_page_url.startswith("http")
```

#### `worker_id`
**Scope:** Session  
**Type:** Synchronous

Provides worker ID for parallel test execution.

```python
def test_parallel_isolation(worker_id):
    # Each worker gets unique resources
    db_name = f"test_db_{worker_id}"
```

**Features:**
- Returns "master" for single-process execution
- Returns worker ID when using pytest-xdist
- Useful for resource isolation in parallel tests

---

## Custom Markers

The conftest.py automatically adds markers to tests:

### `@pytest.mark.asyncio`
Automatically added to async test functions.

### `@pytest.mark.browser`
Automatically added to tests using browser fixtures.

### `@pytest.mark.database`
Automatically added to tests using database fixtures.

### `@pytest.mark.integration`
Manual marker for integration tests.

### `@pytest.mark.slow`
Manual marker for slow-running tests.

### `@pytest.mark.property`
Automatically added to property-based tests.

---

## Test Lifecycle Hooks

### Automatic Screenshot on Failure

The `page` fixture automatically captures screenshots when tests fail:

```python
@pytest.mark.asyncio
async def test_that_fails(page):
    await page.goto("https://example.com")
    assert False  # Screenshot automatically captured
```

Screenshots are saved to `screenshots/test_failures/`.

### Automatic Cleanup

All fixtures automatically clean up resources:
- Browsers are closed
- Contexts are closed
- Pages are closed
- Database connections are released
- Temporary files are removed

### Log Cleanup

Old log files are automatically cleaned up at session start (keeps last 5).

### Screenshot Cleanup

Old screenshots are automatically cleaned up after each test (keeps last 10).

---

## Environment Variables

### `TEST_ENV`
Set the test environment (default: "dev")
```bash
TEST_ENV=staging pytest
```

### `TEST_BROWSER`
Set the browser type (default: "chromium")
```bash
TEST_BROWSER=firefox pytest
```

### `SKIP_SLOW`
Skip slow tests
```bash
SKIP_SLOW=1 pytest
```

---

## Parallel Execution

The fixtures support parallel test execution with pytest-xdist:

```bash
pytest -n auto  # Use all CPU cores
pytest -n 4     # Use 4 workers
```

Each worker gets:
- Isolated browser contexts
- Unique worker ID
- Separate log files
- Independent database connections

---

## Configuration

### Test-Specific Settings

The `config` fixture automatically applies test-specific settings:

```python
# Automatically set in tests
config.set("browser.headless", True)
config.set("timeouts.default", 10000)
```

### Custom Configuration

You can override configuration in tests:

```python
def test_with_custom_timeout(config):
    config.set("timeouts.default", 30000)
    # Test uses 30 second timeout
```

---

## Best Practices

### 1. Use Appropriate Fixture Scope

```python
# Good: Use page fixture for isolated tests
@pytest.mark.asyncio
async def test_isolated(page):
    await page.goto("https://example.com")

# Bad: Don't share page between tests
page_instance = None

@pytest.mark.asyncio
async def test_shared(page):
    global page_instance
    page_instance = page  # Don't do this!
```

### 2. Skip Database Tests Gracefully

```python
def test_database_operation(database):
    if database is None:
        pytest.skip("Database not configured")
    
    # Test code here
```

### 3. Use Async Fixtures for Async Tests

```python
# Good
@pytest.mark.asyncio
async def test_async(page):
    await page.goto("https://example.com")

# Bad
def test_sync(page):  # Don't use async fixtures in sync tests
    pass
```

### 4. Leverage Automatic Markers

```python
# No need to add @pytest.mark.asyncio manually
async def test_auto_marked(page):
    # Automatically marked as asyncio test
    await page.goto("https://example.com")
```

### 5. Use Element Manager for Interactions

```python
@pytest.mark.asyncio
async def test_interaction(element_manager, page):
    await page.goto("https://example.com")
    
    # Use element_manager instead of page.locator()
    await element_manager.click("css=#button")
    await element_manager.fill("css=#input", "value")
```

---

## Troubleshooting

### Browser Not Launching

If you see "Executable doesn't exist" errors:

```bash
playwright install
```

### Database Tests Skipping

If database tests are being skipped, configure database in `config/settings.yaml`:

```yaml
database:
  server: "localhost"
  database: "DDFE"
  user: "testuser"
  password: "password"
```

### Async Warnings

If you see asyncio warnings, add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Screenshot Encoding Errors

If screenshots fail to save, ensure the screenshots directory is writable:

```python
# Check permissions
screenshot_dir = Path("screenshots/test_failures")
assert screenshot_dir.exists()
assert os.access(screenshot_dir, os.W_OK)
```

---

## Examples

### Complete Test Example

```python
import pytest
from raptor.core.element_manager import ElementManager
from playwright.async_api import Page


class TestLoginFlow:
    """Test login functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_login(self, page: Page, element_manager: ElementManager):
        """Test successful login flow."""
        # Navigate to login page
        await page.goto("https://example.com/login")
        
        # Fill in credentials
        await element_manager.fill("css=#username", "testuser")
        await element_manager.fill("css=#password", "password123")
        
        # Click login button
        await element_manager.click("css=#login-button")
        
        # Verify redirect to dashboard
        await page.wait_for_url("**/dashboard")
        assert "dashboard" in page.url
    
    @pytest.mark.asyncio
    async def test_invalid_credentials(self, page: Page, element_manager: ElementManager):
        """Test login with invalid credentials."""
        await page.goto("https://example.com/login")
        
        await element_manager.fill("css=#username", "invalid")
        await element_manager.fill("css=#password", "wrong")
        await element_manager.click("css=#login-button")
        
        # Verify error message
        error = await element_manager.locate_element("css=.error-message")
        assert await error.is_visible()
```

### Database Test Example

```python
def test_data_import(database):
    """Test importing data from DDDB."""
    if database is None:
        pytest.skip("Database not configured")
    
    # Import test data
    data = database.import_data(
        table="TestData",
        test_id=1,
        iteration=1,
        instance=1
    )
    
    assert data is not None
    assert "username" in data
```

### Parallel Test Example

```python
@pytest.mark.asyncio
async def test_parallel_safe(page: Page, worker_id: str):
    """Test that runs safely in parallel."""
    # Each worker gets unique URL
    test_url = f"https://example.com/test?worker={worker_id}"
    
    await page.goto(test_url)
    assert page.url == test_url
```

---

## Summary

The RAPTOR pytest fixtures provide:

✅ **Browser Management** - Automatic browser lifecycle management  
✅ **Test Isolation** - Each test gets fresh browser contexts  
✅ **Configuration** - Centralized test configuration  
✅ **Database Access** - Optional database connectivity  
✅ **Reporting** - Built-in test reporting  
✅ **Cleanup** - Automatic resource cleanup  
✅ **Parallel Support** - Safe parallel test execution  
✅ **Screenshots** - Automatic failure screenshots  

Use these fixtures to write clean, maintainable, and reliable tests!
