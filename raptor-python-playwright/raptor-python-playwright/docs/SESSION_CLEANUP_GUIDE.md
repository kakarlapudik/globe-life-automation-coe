# Session Cleanup Guide

## Overview

The SessionManager provides comprehensive cleanup capabilities to manage session storage efficiently. This guide covers all cleanup methods and best practices.

## Cleanup Methods

### 1. Cleanup Expired Sessions

Remove sessions older than a specified age.

```python
from raptor.core.session_manager import SessionManager

manager = SessionManager()

# Cleanup sessions older than 7 days (default)
deleted_count = manager.cleanup_expired_sessions()
print(f"Deleted {deleted_count} expired sessions")

# Cleanup sessions older than 3 days
deleted_count = manager.cleanup_expired_sessions(max_age_days=3)
```

**What it removes**:
- Sessions with `last_accessed` older than `max_age_days`
- Sessions with invalid or unparseable timestamps
- Corrupted session files

### 2. Cleanup Invalid Sessions

Remove sessions that fail validation checks.

```python
# Cleanup all invalid sessions
deleted_count = manager.cleanup_invalid_sessions()
print(f"Deleted {deleted_count} invalid sessions")
```

**What it removes**:
- Sessions with missing `session_id`
- Sessions with missing `cdp_url`
- Sessions with invalid timestamps
- Sessions with invalid browser types
- Corrupted JSON files

### 3. Cleanup All Sessions

Remove all saved sessions (useful for test cleanup).

```python
# Delete all sessions
deleted_count = manager.cleanup_all_sessions()
print(f"Deleted all {deleted_count} sessions")
```

**Use cases**:
- Test teardown
- Resetting development environment
- Clearing storage before deployment

### 4. Automatic Cleanup on Initialization

Enable automatic cleanup when creating SessionManager.

```python
# Enable auto-cleanup with default settings (7 days)
manager = SessionManager(auto_cleanup_on_init=True)

# Enable auto-cleanup with custom age
manager = SessionManager(
    auto_cleanup_on_init=True,
    max_age_days=3  # Cleanup sessions older than 3 days
)
```

**What it does**:
1. Removes expired sessions (older than `max_age_days`)
2. Removes invalid sessions
3. Logs cleanup results

## Storage Monitoring

### Check Session Count

```python
count = manager.get_session_count()
print(f"Total sessions: {count}")
```

### Check Storage Size

```python
size_bytes = manager.get_storage_size()
size_mb = size_bytes / (1024 * 1024)
print(f"Storage size: {size_mb:.2f} MB")
```

### Monitor and Cleanup Based on Size

```python
# Cleanup if storage exceeds threshold
if manager.get_storage_size() > 10 * 1024 * 1024:  # 10 MB
    print("Storage limit exceeded, cleaning up...")
    manager.cleanup_expired_sessions(max_age_days=1)
```

## Best Practices

### 1. Regular Cleanup in Production

```python
# Run cleanup daily or weekly
import schedule

def cleanup_old_sessions():
    manager = SessionManager()
    expired = manager.cleanup_expired_sessions(max_age_days=7)
    invalid = manager.cleanup_invalid_sessions()
    print(f"Cleanup: {expired} expired, {invalid} invalid")

# Schedule daily cleanup
schedule.every().day.at("02:00").do(cleanup_old_sessions)
```

### 2. Test Environment Cleanup

```python
import pytest
from raptor.core.session_manager import SessionManager

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_sessions():
    """Cleanup all sessions after test suite."""
    yield
    manager = SessionManager()
    deleted = manager.cleanup_all_sessions()
    print(f"\nTest cleanup: Deleted {deleted} sessions")
```

### 3. Conditional Cleanup

```python
# Cleanup based on conditions
manager = SessionManager()

# Only cleanup if storage is large
if manager.get_session_count() > 50:
    manager.cleanup_expired_sessions(max_age_days=3)

# Only cleanup if storage size exceeds limit
if manager.get_storage_size() > 5 * 1024 * 1024:  # 5 MB
    manager.cleanup_invalid_sessions()
```

### 4. Graceful Cleanup with Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_cleanup(manager, max_age_days=7):
    """Perform cleanup with error handling."""
    try:
        expired = manager.cleanup_expired_sessions(max_age_days)
        invalid = manager.cleanup_invalid_sessions()
        
        logger.info(
            f"Cleanup successful: {expired} expired, {invalid} invalid sessions"
        )
        return expired + invalid
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return 0
```

## Cleanup Strategies

### Strategy 1: Aggressive Cleanup (Development)

```python
# Keep only recent sessions
manager = SessionManager(
    auto_cleanup_on_init=True,
    max_age_days=1  # Only keep sessions from last 24 hours
)
```

### Strategy 2: Conservative Cleanup (Production)

```python
# Keep sessions longer for debugging
manager = SessionManager(
    auto_cleanup_on_init=True,
    max_age_days=30  # Keep sessions for 30 days
)
```

### Strategy 3: Manual Cleanup (CI/CD)

```python
# No auto-cleanup, manual control
manager = SessionManager(auto_cleanup_on_init=False)

# Cleanup before test run
manager.cleanup_all_sessions()

# Run tests...

# Cleanup after test run
manager.cleanup_all_sessions()
```

### Strategy 4: Size-Based Cleanup

```python
def cleanup_by_size(manager, max_size_mb=10):
    """Cleanup sessions if storage exceeds size limit."""
    current_size_mb = manager.get_storage_size() / (1024 * 1024)
    
    if current_size_mb > max_size_mb:
        # Start with invalid sessions
        manager.cleanup_invalid_sessions()
        
        # If still too large, cleanup old sessions
        if manager.get_storage_size() / (1024 * 1024) > max_size_mb:
            manager.cleanup_expired_sessions(max_age_days=7)
        
        # If still too large, be more aggressive
        if manager.get_storage_size() / (1024 * 1024) > max_size_mb:
            manager.cleanup_expired_sessions(max_age_days=1)
```

## Validation Before Cleanup

Always validate sessions before attempting to restore them:

```python
# Check if session is valid before restoring
if manager.validate_session("my_session"):
    page = await manager.restore_session("my_session")
else:
    print("Session is invalid, creating new session...")
    # Create new session instead
```

## Troubleshooting

### Issue: Cleanup not removing sessions

**Solution**: Check if sessions are actually expired or invalid

```python
# List all sessions
sessions = manager.list_sessions()

# Check each session
for session_name in sessions:
    info = manager.get_session_info(session_name)
    is_valid = manager.validate_session(session_name)
    
    print(f"Session: {session_name}")
    print(f"  Valid: {is_valid}")
    print(f"  Last accessed: {info.last_accessed if info else 'N/A'}")
```

### Issue: Storage size not decreasing

**Solution**: Ensure cleanup is actually deleting files

```python
# Check storage before and after
before = manager.get_storage_size()
deleted = manager.cleanup_expired_sessions()
after = manager.get_storage_size()

print(f"Before: {before} bytes")
print(f"Deleted: {deleted} sessions")
print(f"After: {after} bytes")
print(f"Freed: {before - after} bytes")
```

### Issue: Auto-cleanup not working

**Solution**: Verify auto-cleanup is enabled

```python
# Check if auto-cleanup is enabled
manager = SessionManager(
    auto_cleanup_on_init=True,  # Must be True
    max_age_days=7
)

# Verify cleanup happened by checking logs
# Look for: "Automatic cleanup complete: X expired, Y invalid sessions removed"
```

## Performance Tips

1. **Batch Cleanup**: Run cleanup during off-peak hours
2. **Incremental Cleanup**: Use shorter age thresholds for frequent cleanup
3. **Monitor First**: Check storage size before deciding to cleanup
4. **Log Results**: Always log cleanup results for monitoring

## Security Considerations

1. **Permissions**: Ensure cleanup process has write permissions to session directory
2. **Concurrent Access**: Avoid running cleanup while sessions are being created
3. **Backup**: Consider backing up sessions before aggressive cleanup
4. **Audit**: Log all cleanup operations for audit trail

## Related Documentation

- [Session Manager Implementation](./SESSION_MANAGER_IMPLEMENTATION.md)
- [Session Quick Reference](./SESSION_QUICK_REFERENCE.md)
- [Task 13 Completion Summary](./TASK_13_COMPLETION_SUMMARY.md)

---

**Last Updated**: November 28, 2024
