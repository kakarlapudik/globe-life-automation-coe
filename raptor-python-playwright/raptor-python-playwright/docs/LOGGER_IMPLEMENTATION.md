# RAPTOR Logger Implementation Guide

## Overview

The RAPTOR Logger provides comprehensive logging functionality with structured logging, context management, log rotation, and multiple output handlers. It supports all standard log levels and includes features specifically designed for test automation.

## Features

### Core Features
- ✅ **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Console Output**: Colored console output with ANSI codes
- ✅ **File Output**: Rotating file handlers with configurable size limits
- ✅ **Structured Logging**: JSON-formatted logs with full context
- ✅ **Context Management**: Add context to all log messages
- ✅ **Log Rotation**: Automatic rotation with configurable backup count
- ✅ **Error Log**: Separate error log file for ERROR and CRITICAL messages
- ✅ **Exception Logging**: Full traceback capture for exceptions

## Quick Start

### Basic Usage

```python
from raptor.utils.logger import get_logger

# Get logger instance
logger = get_logger(name="my_test", log_level="INFO")

# Log messages
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### With Context

```python
from raptor.utils.logger import get_logger

logger = get_logger(name="my_test")

# Set context for all subsequent logs
logger.set_context(
    test_id="TC001",
    browser="chromium",
    environment="staging"
)

logger.info("Starting test")  # Context included
logger.info("Test completed")  # Context included

# Clear context
logger.clear_context()
```

### Exception Logging

```python
from raptor.utils.logger import get_logger

logger = get_logger(name="my_test")

try:
    result = risky_operation()
except Exception:
    logger.exception("Operation failed")  # Includes full traceback
```

## Configuration

### Logger Initialization

```python
from pathlib import Path
from raptor.utils.logger import RaptorLogger

logger = RaptorLogger(
    name="raptor",                    # Logger name
    log_dir=Path("logs"),             # Log directory
    log_level="INFO",                 # Minimum log level
    console_output=True,              # Enable console output
    file_output=True,                 # Enable file output
    max_bytes=10 * 1024 * 1024,      # Max file size (10 MB)
    backup_count=5,                   # Number of backup files
    structured_format=False           # Use JSON format
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "raptor" | Logger name (used for log files) |
| `log_dir` | Path | Path("logs") | Directory for log files |
| `log_level` | str | "INFO" | Minimum log level |
| `console_output` | bool | True | Enable console output |
| `file_output` | bool | True | Enable file output |
| `max_bytes` | int | 10485760 | Max file size before rotation |
| `backup_count` | int | 5 | Number of backup files to keep |
| `structured_format` | bool | False | Use JSON format for file logs |

## Log Levels

### Level Hierarchy

```
DEBUG < INFO < WARNING < ERROR < CRITICAL
```

### When to Use Each Level

- **DEBUG**: Detailed diagnostic information (element locators, wait times, etc.)
- **INFO**: General informational messages (test started, page navigated, etc.)
- **WARNING**: Warning messages (deprecated features, fallback used, etc.)
- **ERROR**: Error messages (test failures, element not found, etc.)
- **CRITICAL**: Critical errors (framework failures, unrecoverable errors, etc.)

### Filtering by Level

```python
# Only log WARNING and above
logger = get_logger(log_level="WARNING")

logger.debug("Not logged")
logger.info("Not logged")
logger.warning("Logged")
logger.error("Logged")
logger.critical("Logged")
```

### Dynamic Level Changes

```python
logger = get_logger(log_level="INFO")

# Change level at runtime
logger.set_level("DEBUG")
```

## Output Handlers

### Console Output

Console output uses colored formatting for better readability:

- **DEBUG**: Cyan
- **INFO**: Green
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Magenta

```python
# Console only
logger = RaptorLogger(
    name="console_test",
    console_output=True,
    file_output=False
)
```

### File Output

File output creates two log files:

1. **Main log file**: `{name}.log` - All log levels
2. **Error log file**: `{name}_error.log` - Only ERROR and CRITICAL

```python
# File only
logger = RaptorLogger(
    name="file_test",
    console_output=False,
    file_output=True
)
```

### Both Console and File

```python
# Both outputs (default)
logger = RaptorLogger(
    name="both_test",
    console_output=True,
    file_output=True
)
```

## Log Rotation

### Automatic Rotation

Logs automatically rotate when they reach the configured size:

```python
logger = RaptorLogger(
    name="rotating_test",
    max_bytes=1024 * 1024,  # 1 MB
    backup_count=3           # Keep 3 backups
)
```

### Rotation Behavior

When `test.log` reaches 1 MB:
1. `test.log` → `test.log.1`
2. `test.log.1` → `test.log.2`
3. `test.log.2` → `test.log.3`
4. `test.log.3` is deleted
5. New `test.log` is created

## Structured Logging

### JSON Format

Enable structured logging for machine-readable logs:

```python
logger = RaptorLogger(
    name="structured_test",
    structured_format=True
)

logger.info("Test started", test_id="TC001")
```

### Output Format

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "structured_test",
  "message": "Test started",
  "module": "test_module",
  "function": "test_function",
  "line": 42,
  "context": {
    "test_id": "TC001"
  }
}
```

## Context Management

### Setting Context

Context values are added to all subsequent log messages:

```python
logger.set_context(
    test_id="TC001",
    browser="chromium",
    user="testuser"
)

logger.info("Message 1")  # Includes context
logger.info("Message 2")  # Includes context
```

### Clearing Context

```python
logger.clear_context()

logger.info("Message 3")  # No context
```

### Per-Message Context

Add context to individual messages:

```python
logger.info("Element located", element_id="username", locator="css=#username")
```

## Exception Logging

### Full Traceback

```python
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed")
```

### With Additional Context

```python
try:
    process_data(data)
except ValueError as e:
    logger.error(
        "Data processing failed",
        exc_info=True,
        data_size=len(data),
        error_type=type(e).__name__
    )
```

## Integration with Tests

### pytest Integration

```python
import pytest
from raptor.utils.logger import get_logger

@pytest.fixture
def logger():
    """Provide logger for tests."""
    return get_logger(name="test_suite", log_level="DEBUG")

def test_example(logger):
    """Example test with logging."""
    logger.set_context(test_name="test_example")
    
    logger.info("Test started")
    
    # Test logic here
    
    logger.info("Test completed")
    logger.clear_context()
```

### Test Execution Logging

```python
def test_user_login(logger):
    """Test user login with detailed logging."""
    logger.set_context(test_id="TC001", test_name="test_user_login")
    
    logger.info("Starting login test")
    
    logger.debug("Navigating to login page")
    page.goto("https://example.com/login")
    
    logger.debug("Entering credentials")
    page.fill("#username", "testuser")
    page.fill("#password", "password123")
    
    logger.debug("Clicking login button")
    page.click("#login-button")
    
    logger.info("Verifying successful login")
    assert page.is_visible("#dashboard")
    
    logger.info("Login test completed successfully")
    logger.clear_context()
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# Good
logger.debug("Located element with locator: css=#username")
logger.info("Test TC001 started")
logger.warning("Using fallback locator")
logger.error("Element not found after timeout")

# Bad
logger.info("Located element with locator: css=#username")  # Too verbose for INFO
logger.error("Test started")  # Not an error
```

### 2. Add Context for Test Execution

```python
# Good
logger.set_context(test_id="TC001", browser="chromium")
logger.info("Test started")

# Bad
logger.info("Test TC001 started in chromium")  # Context in message
```

### 3. Log Exceptions with Context

```python
# Good
try:
    element.click()
except Exception:
    logger.exception("Click failed", element_id="submit-button")

# Bad
try:
    element.click()
except Exception as e:
    logger.error(str(e))  # No traceback
```

### 4. Clear Context Between Tests

```python
# Good
def test_example(logger):
    logger.set_context(test_id="TC001")
    # Test logic
    logger.clear_context()

# Bad
def test_example(logger):
    logger.set_context(test_id="TC001")
    # Test logic
    # Context not cleared - affects next test
```

### 5. Use Structured Logging for Analysis

```python
# Good for log analysis
logger = RaptorLogger(structured_format=True)
logger.info("Test completed", duration_ms=1234, assertions=5, status="PASSED")

# Good for human reading
logger = RaptorLogger(structured_format=False)
logger.info("Test completed successfully")
```

## Global Logger Functions

### get_logger()

Get or create a global logger instance:

```python
from raptor.utils.logger import get_logger

logger = get_logger(name="my_test", log_level="INFO")
```

### configure_logger()

Create a new logger instance (replaces global):

```python
from raptor.utils.logger import configure_logger

logger = configure_logger(
    name="my_test",
    log_level="DEBUG",
    structured_format=True
)
```

## File Structure

### Log Files

```
logs/
├── raptor.log              # Main log file
├── raptor_error.log        # Error log file
├── raptor.log.1            # Backup 1
├── raptor.log.2            # Backup 2
└── raptor.log.3            # Backup 3
```

### Log Format

**Standard Format:**
```
2024-01-15 10:30:45 - raptor - INFO - test_module:test_function:42 - Test started
```

**Structured Format:**
```json
{"timestamp": "2024-01-15T10:30:45.123456", "level": "INFO", "message": "Test started"}
```

## Requirements Satisfied

- ✅ **Requirement 1.4**: Comprehensive logging and error handling
- ✅ **Requirement 9.3**: Structured logging with context
- ✅ **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Log Rotation**: Configurable file rotation
- ✅ **Multiple Handlers**: Console and file output

## See Also

- [Reporter Implementation](./TEST_REPORTER_GUIDE.md)
- [Exception Handling](../raptor/core/exceptions.py)
- [Examples](../examples/logger_example.py)
