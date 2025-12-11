# Cleanup and Teardown - Quick Reference

## Import

```python
from raptor.utils.cleanup import (
    cleanup_manager,
    register_cleanup,
    cleanup_all,
    BrowserCleanupHelper,
    DatabaseCleanupHelper,
    ScreenshotCleanupHelper,
    LogCleanupHelper,
    ReportCleanupHelper
)
```

## CleanupManager

### Register Cleanup Task
```python
cleanup_manager.register_cleanup(
    name="task_name",
    callback=cleanup_function,
    priority=50,  # Lower = execute first
    *args,
    **kwargs
)
```

### Execute All Cleanup
```python
cleanup_manager.cleanup_all()
```

### Unregister Task
```python
cleanup_manager.unregister_cleanup("task_name")
```

### Get Registered Tasks
```python
tasks = cleanup_manager.get_registered_tasks()
```

## Browser Cleanup

### Cleanup Browser Manager
```python
await BrowserCleanupHelper.cleanup_browser_manager(browser_manager)
```

### Cleanup Page
```python
await BrowserCleanupHelper.cleanup_page(page)
```

### Cleanup Context
```python
await BrowserCleanupHelper.cleanup_context(context)
```

## Database Cleanup

### Cleanup Database Manager
```python
DatabaseCleanupHelper.cleanup_database_manager(database_manager)
```

### Cleanup Connection Pool
```python
DatabaseCleanupHelper.cleanup_connection_pool(connection_pool)
```

## Screenshot Cleanup

### Cleanup Passed Test Screenshots
```python
ScreenshotCleanupHelper.cleanup_passed_test_screenshots(
    screenshot_dir="screenshots/test_failures",
    test_results=test_results
)
```

### Cleanup Old Screenshots
```python
ScreenshotCleanupHelper.cleanup_old_screenshots(
    screenshot_dir="screenshots/test_failures",
    max_age_days=7,
    max_count=100
)
```

### Cleanup All Screenshots
```python
ScreenshotCleanupHelper.cleanup_all_screenshots(
    screenshot_dir="screenshots/test_failures"
)
```

## Log Cleanup

### Cleanup Old Logs
```python
LogCleanupHelper.cleanup_old_logs(
    log_dir="logs",
    max_age_days=30,
    max_count=50
)
```

## Report Cleanup

### Cleanup Old Reports
```python
ReportCleanupHelper.cleanup_old_reports(
    report_dir="reports",
    max_age_days=30,
    max_count=50
)
```

## Convenience Functions

### Register Cleanup
```python
register_cleanup("task_name", callback, priority=50)
```

### Execute All Cleanup
```python
cleanup_all()
```

## Priority Guidelines

- **1-10**: Critical resources (browsers, databases)
- **11-50**: Important resources (files, connections)
- **51-100**: Optional cleanup (logs, reports)

## Automatic Cleanup

### In pytest Tests

Cleanup happens automatically:
- Browser cleanup after each test
- Database cleanup after session
- Screenshot cleanup for passed tests
- Log cleanup at session start/end
- Report cleanup at session end

### Graceful Shutdown

Automatic cleanup on:
- Ctrl+C (SIGINT)
- Termination signal (SIGTERM)
- Program exit

## Common Patterns

### Custom Cleanup
```python
def my_cleanup():
    # cleanup logic
    pass

cleanup_manager.register_cleanup("my_cleanup", my_cleanup, priority=50)
```

### Cleanup with Arguments
```python
cleanup_manager.register_cleanup(
    "cleanup_resource",
    cleanup_function,
    priority=50,
    resource_id=123,
    force=True
)
```

### Context Manager
```python
class ManagedResource:
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
```

## Error Handling

Cleanup continues even if tasks fail:
```python
def safe_cleanup():
    try:
        # cleanup logic
        pass
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        # Don't raise

cleanup_manager.register_cleanup("safe", safe_cleanup)
```

## Requirements

- **3.4**: Automatic session cleanup
- **11.5**: Cleanup after failures
- **12.5**: Graceful shutdown
