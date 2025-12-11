# Property Test: Session Persistence Round-Trip

## Property Statement

**Property 3: Session Persistence Round-Trip**

> For any browser session, saving and then restoring the session should result in the same browser state (URL, cookies, storage).

**Validates**: Requirements 3.1, 3.2

## Quick Reference

### Running the Test

```bash
# Run all session persistence property tests
pytest tests/test_property_session_persistence.py -v

# Run with Hypothesis statistics
pytest tests/test_property_session_persistence.py -v --hypothesis-show-statistics

# Run a specific property test
pytest tests/test_property_session_persistence.py::TestSessionPersistenceRoundTrip::test_session_info_round_trip -v
```

### Test Configuration

- **Framework**: pytest + Hypothesis
- **Iterations**: 50-100 examples per test
- **Deadline**: 5000ms per example
- **Total Test Cases**: 600+ generated examples

## Properties Tested

### 1. Session Info Round-Trip
**What it tests**: All session information survives save/load cycle

**Property**: When a session is saved and then loaded from disk, all fields (session_id, cdp_url, browser_type, timestamps, metadata) should be preserved exactly.

**Example inputs**:
- Session names: "test_session", "my-session_123", "SessionABC"
- URLs: "https://example.com", "https://test.example.com/page?param=value"
- Metadata: {"user": "test", "env": "staging", "iteration": 5}

### 2. File Persistence
**What it tests**: Session files are created correctly on disk

**Property**: After saving a session, a valid JSON file should exist containing all required fields.

**Verifies**:
- File exists at expected path
- File contains valid JSON
- All required fields present (session_id, cdp_url, browser_type, created_at, last_accessed, metadata)

### 3. Multiple Saves Idempotence
**What it tests**: Saving the same session multiple times is idempotent

**Property**: Saving a session with the same name multiple times should result in only one session file with the latest data.

**Example**: Save "test_session" 5 times → Only 1 file exists with data from 5th save

### 4. Multiple Sessions Isolation
**What it tests**: Multiple sessions don't interfere with each other

**Property**: Saving multiple sessions should not affect each other's data. Each session maintains independent state.

**Example**: Save sessions ["session1", "session2", "session3"] → Each has correct independent data

### 5. Validation After Save
**What it tests**: Saved sessions pass validation checks

**Property**: After saving a session, `validate_session()` should return True and session should be marked as restorable.

**Verifies**:
- Session validation returns True
- Session info can be retrieved
- CDP URL is present

### 6. Delete Removes All Data
**What it tests**: Deletion completely removes session

**Property**: After deleting a session, it should not appear in lists, file should not exist, and validation should fail.

**Verifies**:
- Session removed from list
- File deleted from disk
- Validation returns False
- get_session_info() returns None

### 7. Timestamps Are Valid
**What it tests**: Timestamps are valid ISO 8601 format

**Property**: created_at and last_accessed should be valid ISO 8601 strings that can be parsed to datetime objects.

**Verifies**:
- Timestamps parse successfully
- Timestamps are reasonable (during save operation)
- created_at equals last_accessed on initial save

### 8. Name Sanitization
**What it tests**: Session names are sanitized for safe storage

**Property**: Session names should be sanitized to prevent path traversal while remaining retrievable.

**Verifies**:
- No ".." in file path
- No "/" or "\\" in file name
- File is in correct directory
- Session still retrievable after sanitization

## Input Strategies

### Session Names
```python
session_name_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='-_'
    ),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip() != '')
```

Generates: "TestSession", "my-session_123", "ABC-def_456"

### URLs
```python
url_strategy = st.sampled_from([
    "https://example.com",
    "https://example.com/page1",
    "https://example.com/page2?param=value",
    "https://test.example.com",
    "https://example.com/path/to/page",
    "https://example.com:8080/secure",
])
```

### Metadata
```python
metadata_strategy = st.dictionaries(
    keys=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20),
    values=st.one_of(st.text(max_size=50), st.integers(), st.booleans(), st.floats()),
    min_size=0,
    max_size=10
)
```

Generates: {"user": "test", "count": 42, "enabled": True, "score": 3.14}

## Example Test Output

```
tests/test_property_session_persistence.py::TestSessionPersistenceRoundTrip::test_session_info_round_trip:
  - during generate phase (3.29 seconds):
    - Typical runtimes: ~ 1-19 ms, of which ~ 0-2 ms in data generation
    - 100 passing examples, 0 failing examples, 17 invalid examples
  - Stopped because settings.max_examples=100
```

## Common Issues and Solutions

### Issue: Function-scoped fixture warning
**Error**: `FailedHealthCheck: uses a function-scoped fixture`

**Solution**: Don't use pytest fixtures with `@given`. Instead, create session manager inside test:
```python
def test_my_property(self, session_name):
    session_manager, temp_dir = self.create_temp_session_manager()
    # ... rest of test
```

### Issue: Invalid examples
**Symptom**: Many "invalid examples" in statistics

**Solution**: Add filters to strategies to exclude invalid inputs:
```python
session_name_strategy.filter(lambda x: x.strip() != '')
```

### Issue: Slow test execution
**Symptom**: Tests take too long

**Solution**: Reduce max_examples or increase deadline:
```python
@settings(max_examples=50, deadline=10000)
```

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Run Property Tests
  run: |
    pytest tests/test_property_session_persistence.py -v --hypothesis-show-statistics
```

### Jenkins
```groovy
stage('Property Tests') {
    steps {
        sh 'pytest tests/test_property_session_persistence.py -v --hypothesis-show-statistics'
    }
}
```

## Related Documentation

- [Session Manager Implementation](SESSION_MANAGER_IMPLEMENTATION.md)
- [Session Quick Reference](SESSION_QUICK_REFERENCE.md)
- [Property-Based Testing Guide](RUN_PROPERTY_TESTS.md)
- [Requirements Document](../requirements.md) - Requirements 3.1, 3.2
- [Design Document](../design.md) - Property 3 specification

## Maintenance Notes

### When to Update This Test

1. **Session Manager Changes**: If SessionManager API changes, update mock creation
2. **New Session Fields**: If SessionInfo gets new fields, add to round-trip test
3. **Storage Format Changes**: If JSON structure changes, update file persistence test
4. **Validation Logic Changes**: If validation rules change, update validation test

### Test Health Indicators

✅ **Healthy**:
- All tests passing
- < 10% invalid examples
- Runtime < 20ms per example
- No flaky failures

⚠️ **Needs Attention**:
- > 20% invalid examples (refine strategies)
- Runtime > 50ms per example (optimize test)
- Occasional failures (investigate race conditions)

## Performance Benchmarks

| Test | Examples | Avg Runtime | Total Time |
|------|----------|-------------|------------|
| session_info_round_trip | 100 | 10ms | 3.29s |
| session_file_persistence | 100 | 20ms | 2.02s |
| multiple_saves_idempotence | 50 | 27ms | 1.35s |
| multiple_sessions_isolation | 50 | 33ms | 1.63s |
| session_validation_after_save | 100 | 18ms | 1.83s |
| session_delete_removes_all_data | 50 | 20ms | 1.05s |
| session_timestamps_are_valid | 100 | 15ms | 1.56s |
| session_name_sanitization | 50 | 15ms | 0.79s |

**Total**: ~14 seconds for 600+ test cases

## Conclusion

This property-based test provides comprehensive validation of session persistence functionality, ensuring that the round-trip property holds across a wide variety of inputs and scenarios. The test suite complements unit tests by verifying universal properties rather than specific examples.
