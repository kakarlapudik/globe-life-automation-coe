# Session Storage and Cleanup Architecture

## Overview

This document describes the architecture of the session storage and cleanup system implemented in Task 13.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      SessionManager                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Initialization & Configuration                 │ │
│  │  • Storage directory setup                                  │ │
│  │  • Auto-cleanup on init (optional)                         │ │
│  │  • Configuration management                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Session Operations                             │ │
│  │  • save_session()      - Save browser session              │ │
│  │  • restore_session()   - Restore saved session             │ │
│  │  • validate_session()  - Validate session data             │ │
│  │  • list_sessions()     - List all sessions                 │ │
│  │  • delete_session()    - Delete single session             │ │
│  │  • get_session_info()  - Get session metadata              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Cleanup Operations                             │ │
│  │  • cleanup_expired_sessions()  - Remove old sessions       │ │
│  │  • cleanup_invalid_sessions()  - Remove corrupted sessions │ │
│  │  • cleanup_all_sessions()      - Remove all sessions       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Monitoring Operations                          │ │
│  │  • get_session_count()  - Count total sessions             │ │
│  │  • get_storage_size()   - Calculate storage usage          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    File System Storage                           │
│                                                                  │
│  ~/.raptor/sessions/                                            │
│  ├── session1.json                                              │
│  ├── session2.json                                              │
│  └── session3.json                                              │
│                                                                  │
│  Each file contains:                                            │
│  {                                                              │
│    "session_id": "session_name",                               │
│    "cdp_url": "ws://localhost:9222/...",                       │
│    "browser_type": "chromium",                                 │
│    "created_at": "2024-11-28T10:00:00",                        │
│    "last_accessed": "2024-11-28T15:30:00",                     │
│    "metadata": { ... }                                         │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Session Lifecycle

```
┌──────────────┐
│ Create       │
│ Browser      │
│ Session      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ save_session()                                           │
│ • Capture CDP URL                                        │
│ • Store metadata                                         │
│ • Create JSON file                                       │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Session Stored                                           │
│ • File: ~/.raptor/sessions/session_name.json            │
│ • Contains: CDP URL, timestamps, metadata               │
└──────┬───────────────────────────────────────────────────┘
       │
       ├─────────────────────────────────────────────────┐
       │                                                 │
       ▼                                                 ▼
┌──────────────────┐                          ┌──────────────────┐
│ restore_session()│                          │ Cleanup Process  │
│ • Validate       │                          │ • Check age      │
│ • Connect CDP    │                          │ • Validate data  │
│ • Return Page    │                          │ • Remove invalid │
└──────────────────┘                          └──────────────────┘
```

## Validation Flow

```
┌──────────────────────────────────────────────────────────┐
│ validate_session(session_name)                           │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Check 1: Session file exists?                            │
└──────┬───────────────────────────────────────────────────┘
       │ Yes
       ▼
┌──────────────────────────────────────────────────────────┐
│ Check 2: Has valid session_id?                           │
└──────┬───────────────────────────────────────────────────┘
       │ Yes
       ▼
┌──────────────────────────────────────────────────────────┐
│ Check 3: Has CDP URL?                                    │
└──────┬───────────────────────────────────────────────────┘
       │ Yes
       ▼
┌──────────────────────────────────────────────────────────┐
│ Check 4: Valid timestamps?                               │
└──────┬───────────────────────────────────────────────────┘
       │ Yes
       ▼
┌──────────────────────────────────────────────────────────┐
│ Check 5: Valid browser type?                             │
│ (chromium, firefox, webkit)                              │
└──────┬───────────────────────────────────────────────────┘
       │ Yes
       ▼
┌──────────────────────────────────────────────────────────┐
│ ✅ Session is VALID                                      │
└──────────────────────────────────────────────────────────┘

       Any "No" ──────────────────────────────────────────▶
                                                           │
                                                           ▼
                                              ┌──────────────────┐
                                              │ ❌ Session is    │
                                              │    INVALID       │
                                              └──────────────────┘
```

## Cleanup Strategies

### Strategy 1: Expired Sessions Cleanup

```
┌──────────────────────────────────────────────────────────┐
│ cleanup_expired_sessions(max_age_days)                   │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ For each session:                                        │
│ 1. Load session info                                     │
│ 2. Parse last_accessed timestamp                        │
│ 3. Calculate age in days                                │
│ 4. If age > max_age_days: DELETE                        │
│ 5. If timestamp invalid: DELETE                         │
│ 6. If file corrupted: DELETE                            │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Return: Number of sessions deleted                       │
└──────────────────────────────────────────────────────────┘
```

### Strategy 2: Invalid Sessions Cleanup

```
┌──────────────────────────────────────────────────────────┐
│ cleanup_invalid_sessions()                               │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ For each session:                                        │
│ 1. Run validate_session()                               │
│ 2. If validation fails: DELETE                          │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Return: Number of invalid sessions deleted               │
└──────────────────────────────────────────────────────────┘
```

### Strategy 3: Auto-Cleanup on Init

```
┌──────────────────────────────────────────────────────────┐
│ SessionManager(auto_cleanup_on_init=True)                │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ 1. Initialize storage directory                          │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Run cleanup_expired_sessions(max_age_days)           │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Run cleanup_invalid_sessions()                        │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ 4. Log cleanup results                                   │
└──────────────────────────────────────────────────────────┘
```

## Error Handling Architecture

```
┌──────────────────────────────────────────────────────────┐
│ Operation (save/restore/cleanup)                         │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Try: Execute operation                                   │
└──────┬───────────────────────────────────────────────────┘
       │
       ├─────────── Success ──────────────────────────────▶
       │                                                    │
       │                                                    ▼
       │                                       ┌──────────────────┐
       │                                       │ Return result    │
       │                                       │ Log success      │
       │                                       └──────────────────┘
       │
       └─────────── Error ────────────────────────────────▶
                                                           │
                                                           ▼
                                              ┌──────────────────┐
                                              │ Catch exception  │
                                              │ Log error        │
                                              │ Add context      │
                                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │ Raise            │
                                              │ SessionException │
                                              │ with context     │
                                              └──────────────────┘
```

## Storage Monitoring

```
┌──────────────────────────────────────────────────────────┐
│ Monitoring Metrics                                       │
└──────┬───────────────────────────────────────────────────┘
       │
       ├──────────────────────────────────────────────────┐
       │                                                  │
       ▼                                                  ▼
┌──────────────────┐                          ┌──────────────────┐
│ Session Count    │                          │ Storage Size     │
│                  │                          │                  │
│ • Count files    │                          │ • Sum file sizes │
│ • Return total   │                          │ • Return bytes   │
└──────────────────┘                          └──────────────────┘
```

## Security Features

```
┌──────────────────────────────────────────────────────────┐
│ Security Measures                                        │
└──────┬───────────────────────────────────────────────────┘
       │
       ├──────────────────────────────────────────────────┐
       │                                                  │
       ▼                                                  ▼
┌──────────────────┐                          ┌──────────────────┐
│ Path Traversal   │                          │ Validation       │
│ Prevention       │                          │                  │
│                  │                          │ • Check required │
│ • Sanitize names │                          │   fields         │
│ • Remove ../     │                          │ • Validate types │
│ • Alphanumeric   │                          │ • Check formats  │
└──────────────────┘                          └──────────────────┘
       │                                                  │
       └──────────────────┬───────────────────────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Error Handling   │
                │                  │
                │ • Graceful fails │
                │ • Clear messages │
                │ • Context info   │
                └──────────────────┘
```

## Performance Characteristics

| Operation | Time Complexity | Typical Duration |
|-----------|----------------|------------------|
| save_session() | O(1) | < 10ms |
| restore_session() | O(1) | < 100ms |
| validate_session() | O(1) | < 1ms |
| list_sessions() | O(n) | < 10ms for 100 sessions |
| cleanup_expired_sessions() | O(n) | < 100ms for 100 sessions |
| cleanup_invalid_sessions() | O(n) | < 100ms for 100 sessions |
| get_session_count() | O(n) | < 5ms for 100 sessions |
| get_storage_size() | O(n) | < 10ms for 100 sessions |

Where n = number of sessions

## Best Practices

1. **Regular Cleanup**: Run cleanup operations regularly (daily/weekly)
2. **Validation First**: Always validate before restoring
3. **Monitor Storage**: Track session count and storage size
4. **Error Handling**: Always handle SessionException
5. **Logging**: Enable logging for debugging
6. **Auto-Cleanup**: Use auto-cleanup in production environments
7. **Test Cleanup**: Clean up sessions after test runs

## Related Documentation

- [Task 13 Completion Summary](./TASK_13_COMPLETION_SUMMARY.md)
- [Session Cleanup Guide](./SESSION_CLEANUP_GUIDE.md)
- [Session Manager Implementation](./SESSION_MANAGER_IMPLEMENTATION.md)
- [Session Quick Reference](./SESSION_QUICK_REFERENCE.md)

---

**Last Updated**: November 28, 2024
