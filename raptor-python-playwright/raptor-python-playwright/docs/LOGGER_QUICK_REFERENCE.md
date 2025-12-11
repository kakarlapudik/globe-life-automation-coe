# RAPTOR Logger - Quick Reference

## Import

```python
from raptor.utils.logger import get_logger, configure_logger, RaptorLogger
```

## Basic Usage

```python
# Get logger
logger = get_logger(name="my_test", log_level="INFO")

# Log messages
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
logger.exception("Exception with traceback")
```

## Configuration

```python
from pathlib import Path

logger = RaptorLogger(
    name="raptor",
    log_dir=Path("logs"),
    log_level="INFO",
    console_output=True,
    file_output=True,
    max_bytes=10 * 1024 * 1024,  # 10 MB
    backup_count=5,
    structured_format=False
)
```

## Context Management

```python
# Set context
logger.set_context(test_id="TC001", browser="chromium")

# Log with context
logger.info("Test started")  # Context included

# Clear context
logger.clear_context()
```

## Log Levels

| Level | When to Use |
|-------|-------------|
| DEBUG | Detailed diagnostic info |
| INFO | General informational messages |
| WARNING | Warning messages |
| ERROR | Error messages |
| CRITICAL | Critical errors |

## Output Control

```python
# Console only
logger = RaptorLogger(console_output=True, file_output=False)

# File only
logger = RaptorLogger(console_output=False, file_output=True)

# Both (default)
logger = RaptorLogger(console_output=True, file_output=True)
```

## Structured Logging

```python
# Enable JSON format
logger = RaptorLogger(structured_format=True)

logger.info("Test completed", duration_ms=1234, status="PASSED")
```

## Exception Logging

```python
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed")  # Full traceback
```

## Dynamic Level Change

```python
logger.set_level("DEBUG")  # Change at runtime
```

## Common Patterns

### Test Execution

```python
logger.set_context(test_id="TC001")
logger.info("Test started")
# Test logic
logger.info("Test completed")
logger.clear_context()
```

### Element Interaction

```python
logger.debug("Locating element", locator="css=#username")
logger.debug("Element found", element_id="username")
logger.debug("Entering text", value="testuser")
```

### Error Handling

```python
try:
    element.click()
except Exception:
    logger.exception("Click failed", element_id="submit-button")
```

## File Locations

- Main log: `logs/{name}.log`
- Error log: `logs/{name}_error.log`
- Backups: `logs/{name}.log.1`, `logs/{name}.log.2`, etc.

## Color Codes (Console)

- DEBUG: Cyan
- INFO: Green
- WARNING: Yellow
- ERROR: Red
- CRITICAL: Magenta
