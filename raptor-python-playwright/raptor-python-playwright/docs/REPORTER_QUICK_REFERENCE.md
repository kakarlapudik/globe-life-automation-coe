# Test Reporter Quick Reference

## Import

```python
from raptor.utils.reporter import TestReporter, TestResult, TestStatus
from datetime import datetime
```

## Basic Workflow

```python
# 1. Initialize
reporter = TestReporter(report_dir="reports")

# 2. Start suite
reporter.start_suite("My Test Suite")

# 3. Add results
result = TestResult(
    test_id="TC_001",
    test_name="Test Name",
    status=TestStatus.PASSED,
    duration=2.5,
    start_time=datetime.now(),
    end_time=datetime.now()
)
reporter.add_test_result(result)

# 4. End suite
reporter.end_suite()

# 5. Generate reports
html_path = reporter.generate_html_report()
json_path = reporter.export_json()
```

## Test Status

```python
TestStatus.PASSED   # ✓ Test passed
TestStatus.FAILED   # ✗ Test failed
TestStatus.SKIPPED  # ⊘ Test skipped
TestStatus.ERROR    # ⚠ Test error
```

## TestResult Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `test_id` | str | Yes | Unique test identifier |
| `test_name` | str | Yes | Human-readable test name |
| `status` | TestStatus | Yes | Test execution status |
| `duration` | float | Yes | Duration in seconds |
| `start_time` | datetime | Yes | Test start timestamp |
| `end_time` | datetime | Yes | Test end timestamp |
| `error_message` | str | No | Error message if failed |
| `stack_trace` | str | No | Stack trace if failed |
| `screenshots` | List[str] | No | Screenshot file paths |
| `metadata` | Dict | No | Custom metadata |

## Common Patterns

### Failed Test with Error

```python
TestResult(
    test_id="TC_002",
    test_name="Test Failed",
    status=TestStatus.FAILED,
    duration=1.2,
    start_time=start,
    end_time=end,
    error_message="AssertionError: Expected X but got Y",
    stack_trace="Traceback...",
    screenshots=["error.png"]
)
```

### Test with Metadata

```python
TestResult(
    test_id="TC_003",
    test_name="Test with Metadata",
    status=TestStatus.PASSED,
    duration=2.0,
    start_time=start,
    end_time=end,
    metadata={
        "browser": "chromium",
        "environment": "staging",
        "priority": "high"
    }
)
```

### Skipped Test

```python
TestResult(
    test_id="TC_004",
    test_name="Skipped Test",
    status=TestStatus.SKIPPED,
    duration=0.0,
    start_time=now,
    end_time=now,
    error_message="Test skipped: Feature not available"
)
```

## Reporter Methods

### Suite Management

```python
reporter.start_suite("Suite Name")  # Start test suite
reporter.end_suite()                # End test suite
```

### Adding Results

```python
reporter.add_test_result(result)    # Add single result
```

### Statistics

```python
stats = reporter.get_statistics()
# stats.total_tests
# stats.passed
# stats.failed
# stats.skipped
# stats.errors
# stats.pass_rate
# stats.total_duration
```

### Report Generation

```python
# HTML report
html_path = reporter.generate_html_report()
html_path = reporter.generate_html_report(output_file="custom.html")
html_path = reporter.generate_html_report(embed_screenshots=False)

# JSON export
json_path = reporter.export_json()
json_path = reporter.export_json(output_file="results.json")
```

## HTML Report Features

- ✓ Interactive expandable test details
- ✓ Embedded or linked screenshots
- ✓ Color-coded status indicators
- ✓ Statistics dashboard
- ✓ Error messages and stack traces
- ✓ Test metadata display
- ✓ Responsive design
- ✓ Screenshot modal viewer

## JSON Export Structure

```json
{
  "suite_name": "string",
  "start_time": "ISO 8601",
  "end_time": "ISO 8601",
  "statistics": {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": 0,
    "total_duration": 0.0,
    "pass_rate": 0.0
  },
  "test_results": [...]
}
```

## Duration Formatting

- < 1s: "123ms"
- < 60s: "5.67s"
- ≥ 60s: "2m 5.1s"

## Tips

1. **Call `start_suite()` before adding results**
2. **Call `end_suite()` before generating reports**
3. **Use descriptive test names and IDs**
4. **Include relevant metadata for filtering**
5. **Capture screenshots on failures**
6. **Use absolute or relative paths for screenshots**
7. **Clean up old reports periodically**

## Example: Complete Test Run

```python
from raptor.utils.reporter import TestReporter, TestResult, TestStatus
from datetime import datetime, timedelta

# Setup
reporter = TestReporter(report_dir="reports")
reporter.start_suite("Login Tests")

# Test 1: Pass
start = datetime.now()
# ... run test ...
reporter.add_test_result(TestResult(
    test_id="TC_001",
    test_name="Valid Login",
    status=TestStatus.PASSED,
    duration=2.5,
    start_time=start,
    end_time=start + timedelta(seconds=2.5)
))

# Test 2: Fail
start = datetime.now()
# ... run test ...
reporter.add_test_result(TestResult(
    test_id="TC_002",
    test_name="Invalid Password",
    status=TestStatus.FAILED,
    duration=1.2,
    start_time=start,
    end_time=start + timedelta(seconds=1.2),
    error_message="Login failed",
    screenshots=["failure.png"]
))

# Finish
reporter.end_suite()
stats = reporter.get_statistics()
print(f"Pass Rate: {stats.pass_rate:.1f}%")

# Generate reports
reporter.generate_html_report()
reporter.export_json()
```

## See Also

- [Full Guide](TEST_REPORTER_GUIDE.md)
- [Examples](../examples/reporter_example.py)
- [API Reference](API_REFERENCE.md)
