# Test Cleanup and Teardown Guide

## Overview

The RAPTOR framework provides comprehensive cleanup and teardown functionality to ensure proper resource management during test execution. This guide covers automatic cleanup mechanisms, manual cleanup utilities, and graceful shutdown handling.

## Features

### Automatic Cleanup
- **Browser Cleanup**: Automatic cleanup of browser instances, contexts, and pages
- **Database Cleanup**: Automatic cleanup of database connections and pools
- **Screenshot Cleanup**: Intelligent cleanup of screenshots based on test results
- **Log Cleanup**: Automatic cleanup of old log files
- **Report Cleanup**: Automatic cleanup of old test reports

### Graceful Shutdown
- **Signal Handling**: Handles SIGINT (Ctrl+C) and SIGTERM signals
- **Exit Handlers**: Automatic cleanup on program exit
- **Priority-Based Execution**: Cleanup tasks execute in priority order
- **Error Resilience**: Cleanup continues even if individual tasks fail

## CleanupManager

The `CleanupManager` is the central component for managing cleanup tasks.

### Basic Usage

```python
from raptor.utils.cleanup import cleanup_manager

# Register a cleanup task
cleanup_manager.register_cleanup(
    name="close_browser",
    callback=browser_manager.close_browser,
    priority=10  # Lower priority = execute first
)

# Execute all cleanup tasks
cleanup_manager.cleanup_all()

# Unregister a task
cleanup_manager.unregister_cleanup("close_browser")
```

### Priority System

Cleanup tasks are executed in priority order (lowest to highest):

- **Priority 1-10**: Critical resources (browsers, database connections)
- **Priority 11-50**: Important resources (files, temporary data)
- **Priority 51-100**: Optional cleanup (logs, old reports)

### Convenience Functions

```python
from raptor.utils.cleanup import register_cleanup, cleanup_all

# Register cleanup
register_cleanup("my_task", my_callback, priority=50)

# Execute all cleanup
cleanup_all()
```

## Browser Cleanup

### Automatic Cleanup in Tests

Browser cleanup is automatic when using pytest fixtures:

```python
@pytest.mark.asyncio
async def test_navigation(browser_manager):
    await browser_manager.launch_browser("chromium", headless=True)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    
    # ... test code ...
    
    # Cleanup happens automatically after test
```

### Manual Browser Cleanup

```python
from raptor.utils.cleanup import BrowserCleanupHelper

# Clean up browser manager
await BrowserCleanupHelper.cleanup_browser_manager(browser_manager)

# Clean up individual page
await BrowserCleanupHelper.cleanup_page(page)

# Clean up context
await BrowserCleanupHelper.cleanup_context(context)
```

## Database Cleanup

### Automatic Cleanup in Tests

Database cleanup is automatic when using pytest fixtures:

```python
def test_database_query(database):
    if database is None:
        pytest.skip("Database not configured")
    
    result = database.execute_query("SELECT * FROM TestData")
    
    # Cleanup happens automatically after test
```

### Manual Database Cleanup

```python
from raptor.utils.cleanup import DatabaseCleanupHelper

# Clean up database manager
DatabaseCleanupHelper.cleanup_database_manager(database_manager)

# Clean up connection pool
DatabaseCleanupHelper.cleanup_connection_pool(connection_pool)
```

## Screenshot Cleanup

### Automatic Cleanup for Passed Tests

Screenshots for passed tests are automatically deleted to save disk space:

```python
# This happens automatically in conftest.py
# Screenshots for failed tests are kept for debugging
```

### Manual Screenshot Cleanup

```python
from raptor.utils.cleanup import ScreenshotCleanupHelper

# Clean up screenshots for passed tests
ScreenshotCleanupHelper.cleanup_passed_test_screenshots(
    screenshot_dir="screenshots/test_failures",
    test_results=test_results
)

# Clean up old screenshots (by age and count)
ScreenshotCleanupHelper.cleanup_old_screenshots(
    screenshot_dir="screenshots/test_failures",
    max_age_days=7,
    max_count=100
)

# Clean up all screenshots
ScreenshotCleanupHelper.cleanup_all_screenshots(
    screenshot_dir="screenshots/test_failures"
)
```

## Log Cleanup

### Automatic Cleanup

Log cleanup happens automatically at session start and end:

```python
# This happens automatically in conftest.py
# Keeps last 50 log files or logs from last 30 days
```

### Manual Log Cleanup

```python
from raptor.utils.cleanup import LogCleanupHelper

# Clean up old logs
LogCleanupHelper.cleanup_old_logs(
    log_dir="logs",
    max_age_days=30,
    max_count=50
)
```

## Report Cleanup

### Automatic Cleanup

Report cleanup happens automatically at session end:

```python
# This happens automatically in conftest.py
# Keeps last 50 reports or reports from last 30 days
```

### Manual Report Cleanup

```python
from raptor.utils.cleanup import ReportCleanupHelper

# Clean up old reports
ReportCleanupHelper.cleanup_old_reports(
    report_dir="reports",
    max_age_days=30,
    max_count=50
)
```

## Graceful Shutdown

### Signal Handling

The framework automatically handles interrupt signals:

```python
# Press Ctrl+C during test execution
# Framework will:
# 1. Catch the signal
# 2. Execute all registered cleanup tasks
# 3. Exit gracefully
```

### Exit Handlers

Cleanup happens automatically on program exit:

```python
# When program exits (normally or abnormally)
# Framework will:
# 1. Detect exit
# 2. Execute all registered cleanup tasks
# 3. Clean up resources
```

## Custom Cleanup Tasks

### Creating Custom Cleanup

```python
from raptor.utils.cleanup import cleanup_manager

def my_cleanup_function():
    """Custom cleanup logic."""
    # Close connections
    # Delete temporary files
    # etc.
    pass

# Register custom cleanup
cleanup_manager.register_cleanup(
    name="my_custom_cleanup",
    callback=my_cleanup_function,
    priority=50
)
```

### Cleanup with Arguments

```python
def cleanup_with_args(resource_id, force=False):
    """Cleanup with arguments."""
    # Cleanup logic
    pass

# Register with arguments
cleanup_manager.register_cleanup(
    name="cleanup_resource",
    callback=cleanup_with_args,
    priority=50,
    resource_id=123,
    force=True
)
```

## Best Practices

### 1. Use Appropriate Priorities

```python
# Critical resources - low priority numbers
cleanup_manager.register_cleanup("browser", close_browser, priority=10)

# Important resources - medium priority numbers
cleanup_manager.register_cleanup("files", close_files, priority=50)

# Optional cleanup - high priority numbers
cleanup_manager.register_cleanup("logs", cleanup_logs, priority=100)
```

### 2. Handle Errors Gracefully

```python
def safe_cleanup():
    """Cleanup that handles errors."""
    try:
        # Cleanup logic
        resource.close()
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        # Don't raise - allow other cleanup to continue

cleanup_manager.register_cleanup("safe", safe_cleanup)
```

### 3. Clean Up in Reverse Order

```python
# Register in order of creation
cleanup_manager.register_cleanup("create_resource", cleanup_resource, priority=10)
cleanup_manager.register_cleanup("use_resource", cleanup_usage, priority=20)

# Cleanup happens in reverse (usage first, then resource)
```

### 4. Use Context Managers

```python
class ManagedResource:
    """Resource with automatic cleanup."""
    
    def __enter__(self):
        cleanup_manager.register_cleanup(
            f"resource_{id(self)}",
            self.cleanup,
            priority=50
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        cleanup_manager.unregister_cleanup(f"resource_{id(self)}")
        self.cleanup()
    
    def cleanup(self):
        # Cleanup logic
        pass
```

## Configuration

### Screenshot Cleanup Settings

Configure in `conftest.py`:

```python
@pytest.fixture(scope="function", autouse=True)
def cleanup_screenshots(request):
    yield
    
    ScreenshotCleanupHelper.cleanup_old_screenshots(
        screenshot_dir="screenshots/test_failures",
        max_age_days=7,      # Adjust retention period
        max_count=100        # Adjust max count
    )
```

### Log Cleanup Settings

Configure in `conftest.py`:

```python
@pytest.fixture(scope="session", autouse=True)
def cleanup_logs():
    LogCleanupHelper.cleanup_old_logs(
        log_dir="logs",
        max_age_days=30,     # Adjust retention period
        max_count=50         # Adjust max count
    )
    yield
```

## Troubleshooting

### Cleanup Not Running

**Problem**: Cleanup tasks not executing

**Solution**:
```python
# Verify task is registered
tasks = cleanup_manager.get_registered_tasks()
print(f"Registered tasks: {tasks}")

# Manually trigger cleanup
cleanup_manager.cleanup_all()
```

### Cleanup Errors

**Problem**: Errors during cleanup

**Solution**:
```python
# Check logs for error details
# Cleanup continues even with errors
# Individual task failures don't stop other tasks
```

### Resource Leaks

**Problem**: Resources not being cleaned up

**Solution**:
```python
# Ensure cleanup is registered
cleanup_manager.register_cleanup("resource", cleanup_func, priority=10)

# Verify cleanup is called
# Add logging to cleanup function
def cleanup_func():
    logger.info("Cleanup starting")
    # cleanup logic
    logger.info("Cleanup completed")
```

## Examples

### Complete Test with Cleanup

```python
import pytest
from raptor.utils.cleanup import cleanup_manager

@pytest.mark.asyncio
async def test_with_cleanup(browser_manager, database):
    # Setup
    await browser_manager.launch_browser("chromium")
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    
    # Register custom cleanup
    cleanup_manager.register_cleanup(
        "test_cleanup",
        lambda: print("Custom cleanup"),
        priority=50
    )
    
    # Test logic
    await page.goto("https://example.com")
    result = database.execute_query("SELECT * FROM TestData")
    
    # Assertions
    assert await page.title() == "Example Domain"
    assert len(result) > 0
    
    # Cleanup happens automatically:
    # 1. Custom cleanup (priority 50)
    # 2. Database cleanup (priority 20)
    # 3. Browser cleanup (priority 10)
```

### Manual Cleanup Example

```python
from raptor.utils.cleanup import (
    BrowserCleanupHelper,
    DatabaseCleanupHelper,
    ScreenshotCleanupHelper
)

async def manual_cleanup_example():
    """Example of manual cleanup."""
    
    # Clean up browser
    await BrowserCleanupHelper.cleanup_browser_manager(browser_manager)
    
    # Clean up database
    DatabaseCleanupHelper.cleanup_database_manager(database_manager)
    
    # Clean up screenshots
    ScreenshotCleanupHelper.cleanup_old_screenshots(
        screenshot_dir="screenshots",
        max_age_days=7,
        max_count=100
    )
```

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 3.4**: Automatic session cleanup and resource management
- **Requirement 11.5**: Cleanup code execution even after failures
- **Requirement 12.5**: Graceful shutdown handling with signal handlers

## See Also

- [pytest Fixtures Guide](PYTEST_FIXTURES_GUIDE.md)
- [Browser Manager Implementation](BROWSER_MANAGER_IMPLEMENTATION.md)
- [Database Manager Implementation](DATABASE_MANAGER_IMPLEMENTATION.md)
- [Test Reporter Guide](TEST_REPORTER_GUIDE.md)
