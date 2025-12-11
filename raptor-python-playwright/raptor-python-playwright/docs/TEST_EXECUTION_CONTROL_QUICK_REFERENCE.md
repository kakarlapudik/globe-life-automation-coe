# Test Execution Control - Quick Reference

## Command-Line Options

### Test Filtering
```bash
# Filter by test ID
pytest --test-id test_login

# Filter by iteration
pytest --iteration 1 --iteration 2

# Filter by tag
pytest --tag smoke --tag regression

# Filter by marker
pytest --marker slow

# Exclude tests
pytest --exclude-tag flaky
```

### Parallel Execution
```bash
# Auto-detect CPU count
pytest -n auto

# Use 4 workers
pytest -n 4

# Distribute by file
pytest -n auto --dist loadfile
```

## Skip Functions

### Basic Skip
```python
from raptor.core.test_execution_control import skip_test, SkipReason

skip_test("Reason", SkipReason.NOT_IMPLEMENTED)
```

### Conditional Skip
```python
from raptor.core.test_execution_control import skip_if, skip_unless

skip_if(condition, "Reason", SkipReason.DEPENDENCY)
skip_unless(condition, "Reason", SkipReason.CONFIGURATION)
```

### Skip Reasons
- `SkipReason.NOT_IMPLEMENTED`
- `SkipReason.ENVIRONMENT`
- `SkipReason.DEPENDENCY`
- `SkipReason.CONFIGURATION`
- `SkipReason.PLATFORM`
- `SkipReason.FLAKY`
- `SkipReason.MANUAL`
- `SkipReason.CUSTOM`

## Retry Decorator

### Basic Retry
```python
from raptor.core.test_execution_control import retry_on_failure

@retry_on_failure(max_retries=3, retry_delay=1.0)
async def test_flaky():
    pass
```

### Advanced Retry
```python
@retry_on_failure(
    max_retries=5,
    retry_delay=2.0,
    exponential_backoff=True,
    retry_on_exceptions=[TimeoutError],
    log_retries=True
)
async def test_with_retry():
    pass
```

## Test Markers

### Standard Markers
```python
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.flaky
@pytest.mark.browser
@pytest.mark.database
```

### Custom Markers
```python
@pytest.mark.custom_tag
def test_with_custom_marker():
    pass
```

## Common Patterns

### Smoke Test with Retry
```python
@pytest.mark.smoke
@retry_on_failure(max_retries=2, retry_delay=1.0)
async def test_smoke_feature(page):
    pass
```

### Conditional Skip
```python
def test_feature(database):
    skip_if(database is None, "DB not configured", SkipReason.CONFIGURATION)
    # test code
```

### Parallel-Safe Fixture
```python
@pytest.fixture(scope="function")
async def isolated_resource(worker_id):
    return f"resource_{worker_id}"
```

## Running Tests

### Run Smoke Tests in Parallel
```bash
pytest --marker smoke -n auto
```

### Run Specific Iterations
```bash
pytest --iteration 1 --iteration 2 -v
```

### Run with Retries
```bash
pytest --max-retries 3
```

### Exclude Flaky Tests
```bash
pytest --exclude-tag flaky
```

### Combine Filters
```bash
pytest --tag smoke --exclude-tag flaky -n auto
```

## Requirements

- **12.1**: Test filtering by ID, iteration, tag
- **12.2**: Skip functionality with reason logging
- **12.3**: Retry mechanism for flaky tests
- **12.4**: Parallel execution with pytest-xdist
