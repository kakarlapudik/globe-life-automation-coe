# Session Manager Quick Reference

## Import

```python
from raptor.core.session_manager import SessionManager
```

## Initialization

```python
# Default storage (~/.raptor/sessions)
session_manager = SessionManager()

# Custom storage location
session_manager = SessionManager(storage_dir="/path/to/sessions")
```

## Save Session

```python
# Basic save
session_info = await session_manager.save_session(page, "session_name")

# Save with metadata
session_info = await session_manager.save_session(
    page,
    "session_name",
    metadata={"user": "test_user", "env": "staging"}
)
```

## Restore Session

```python
# Restore session
page = await session_manager.restore_session("session_name")

# With validation
if session_manager.validate_session("session_name"):
    page = await session_manager.restore_session("session_name")
```

## List Sessions

```python
# Get all session names
sessions = session_manager.list_sessions()

# Get session details
for session_name in sessions:
    info = session_manager.get_session_info(session_name)
    print(f"{session_name}: {info.created_at}")
```

## Delete Sessions

```python
# Delete specific session
session_manager.delete_session("session_name")

# Clean up old sessions (older than 7 days)
deleted_count = session_manager.cleanup_expired_sessions(max_age_days=7)
```

## Validate Session

```python
# Check if session is valid
is_valid = session_manager.validate_session("session_name")

# Get session info
info = session_manager.get_session_info("session_name")
if info:
    print(f"Browser: {info.browser_type}")
    print(f"Created: {info.created_at}")
```

## Common Patterns

### Pattern 1: Save After Login

```python
# Launch browser and login
await browser_manager.launch_browser("chromium")
page = await browser_manager.create_page()
await page.goto("https://example.com/login")
# ... perform login ...

# Save authenticated session
await session_manager.save_session(page, "logged_in_session")
```

### Pattern 2: Restore or Create

```python
if session_manager.validate_session("my_session"):
    # Reuse existing session
    page = await session_manager.restore_session("my_session")
else:
    # Create new session
    page = await create_new_session()
    await session_manager.save_session(page, "my_session")
```

### Pattern 3: Multiple User Sessions

```python
for user in ["admin", "user1", "user2"]:
    page = await login_as_user(user)
    await session_manager.save_session(page, f"session_{user}")
```

### Pattern 4: Cleanup in Test Setup

```python
@pytest.fixture(scope="session", autouse=True)
def cleanup_sessions():
    session_manager = SessionManager()
    session_manager.cleanup_expired_sessions(max_age_days=7)
```

## Error Handling

```python
from raptor.core.exceptions import SessionException

try:
    page = await session_manager.restore_session("my_session")
except SessionException as e:
    print(f"Error: {e.message}")
    # Fallback to new session
```

## Browser Support

| Browser | Save | Restore | Notes |
|---------|------|---------|-------|
| Chromium | ✅ | ✅ | Full support |
| Firefox | ⚠️ | ❌ | No CDP URL |
| WebKit | ⚠️ | ❌ | No CDP URL |

## Performance

- **New browser launch**: 3-5 seconds
- **Session restoration**: 0.5-1 second
- **Time savings**: 70-80%

## Storage

- **Default location**: `~/.raptor/sessions/`
- **File format**: JSON
- **File size**: ~1-2 KB per session

## Tips

1. ✅ Use descriptive session names
2. ✅ Validate before restoring
3. ✅ Include useful metadata
4. ✅ Clean up old sessions regularly
5. ✅ Use Chromium for session reuse
6. ❌ Don't use empty session names
7. ❌ Don't rely on sessions older than 24 hours

## See Also

- [Full Documentation](SESSION_MANAGER_IMPLEMENTATION.md)
- [Examples](../examples/session_example.py)
- [Browser Manager](BROWSER_MANAGER_IMPLEMENTATION.md)
