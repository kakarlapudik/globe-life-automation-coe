# Test Reporter Guide

## Overview

The RAPTOR Test Reporter provides comprehensive test reporting capabilities with HTML and JSON output formats. It tracks test execution, captures screenshots, and generates detailed reports with statistics and visualizations.

## Features

- **HTML Report Generation**: Beautiful, interactive HTML reports with embedded screenshots
- **JSON Export**: Machine-readable JSON format for integration with other tools
- **Execution Tracking**: Automatic duration tracking for tests and test suites
- **Statistics**: Pass/fail rates, execution times, and test counts
- **Screenshot Embedding**: Embed screenshots directly in HTML reports or link to files
- **Error Details**: Capture error messages and stack traces
- **Metadata Support**: Attach custom metadata to test results

## Quick Start

### Basic Usage

```python
from raptor.utils.reporter import TestReporter, TestResult, TestStatus
from datetime import datetime

# Initialize reporter
reporter = TestReporter(report_dir="reports")

# Start test suite
reporter.start_suite("My Test Suite")

# Create and add test result
result = TestResult(
    test_id="TC_001",
    test_name="Test Login",
    status=TestStatus.PASSED,
    duration=2.5,
    start_time=datetime.now(),
    end_time=datetime.now()
)
reporter.add_test_result(result)

# End suite and generate reports
reporter.end_suite()
html_path = reporter.generate_html_report()
json_path = reporter.export_json()
```

## TestResult Class

### Creating Test Results

```python
from raptor.utils.reporter import TestResult, TestStatus
from datetime import datetime, timedelta

start_time = datetime.now()
end_time = start_time + timedelta(seconds=2.5)

result = TestResult(
    test_id="TC_001",              # Unique test identifier
    test_name="Test Login",         # Human-readable name
    status=TestStatus.PASSED,       # Test status
    duration=2.5,                   # Duration in seconds
    start_time=start_time,          # Test start time
    end_time=end_time,              # Test end time
    error_message=None,             # Optional error message
    stack_trace=None,               # Optional stack trace
    screenshots=[],                 # Optional screenshot paths
    metadata={}                     # Optional metadata dict
)
```

### Test Status Values

```python
from raptor.utils.reporter import TestStatus

TestStatus.PASSED   # Test passed successfully
TestStatus.FAILED   # Test failed with assertion error
TestStatus.SKIPPED  # Test was skipped
TestStatus.ERROR    # Test encountered an error
```

### Adding Error Information

```python
failed_result = TestResult(
    test_id="TC_002",
    test_name="Test Data Validation",
    status=TestStatus.FAILED,
    duration=1.2,
    start_time=start_time,
    end_time=end_time,
    error_message="AssertionError: Expected 'test' but got 'prod'",
    stack_trace="Traceback (most recent call last):\n  File 'test.py', line 10"
)
```

### Adding Screenshots

```python
result_with_screenshots = TestResult(
    test_id="TC_003",
    test_name="Test UI Elements",
    status=TestStatus.FAILED,
    duration=3.0,
    start_time=start_time,
    end_time=end_time,
    screenshots=[
        "screenshots/before_click.png",
        "screenshots/after_error.png"
    ]
)
```

### Adding Metadata

```python
result_with_metadata = TestResult(
    test_id="TC_004",
    test_name="Test API Call",
    status=TestStatus.PASSED,
    duration=1.5,
    start_time=start_time,
    end_time=end_time,
    metadata={
        "browser": "chromium",
        "environment": "staging",
        "test_type": "api",
        "priority": "high",
        "test_data": "user_001"
    }
)
```

## TestReporter Class

### Initialization

```python
from raptor.utils.reporter import TestReporter

# Default report directory
reporter = TestReporter()

# Custom report directory
reporter = TestReporter(report_dir="custom_reports")
```

### Managing Test Suites

```python
# Start a test suite
reporter.start_suite("Login Module Tests")

# Add test results
reporter.add_test_result(result1)
reporter.add_test_result(result2)

# End the test suite
reporter.end_suite()
```

### Getting Statistics

```python
stats = reporter.get_statistics()

print(f"Total Tests: {stats.total_tests}")
print(f"Passed: {stats.passed}")
print(f"Failed: {stats.failed}")
print(f"Skipped: {stats.skipped}")
print(f"Errors: {stats.errors}")
print(f"Pass Rate: {stats.pass_rate:.1f}%")
print(f"Total Duration: {stats.total_duration:.2f}s")
```

### Generating HTML Reports

```python
# Generate with default filename (timestamp-based)
html_path = reporter.generate_html_report()

# Generate with custom filename
html_path = reporter.generate_html_report(output_file="my_report.html")

# Generate without embedding screenshots
html_path = reporter.generate_html_report(embed_screenshots=False)
```

### Exporting JSON

```python
# Export with default filename
json_path = reporter.export_json()

# Export with custom filename
json_path = reporter.export_json(output_file="results.json")
```

## HTML Report Features

### Interactive Elements

- **Expandable Test Details**: Click test headers to expand/collapse details
- **Screenshot Modal**: Click screenshots to view full-size in modal
- **Color-Coded Status**: Visual indicators for pass/fail/skip/error
- **Statistics Dashboard**: Overview cards with key metrics

### Report Sections

1. **Header**: Suite name and generation timestamp
2. **Summary**: Statistics cards with totals and pass rate
3. **Test Results**: Detailed list of all test executions
4. **Test Details**: Error messages, stack traces, screenshots, metadata

### Styling

The HTML reports include:
- Responsive design for mobile and desktop
- Modern gradient headers
- Color-coded status indicators
- Professional typography
- Interactive hover effects

## JSON Export Format

```json
{
  "suite_name": "My Test Suite",
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T10:35:00",
  "statistics": {
    "total_tests": 5,
    "passed": 3,
    "failed": 1,
    "skipped": 1,
    "errors": 0,
    "total_duration": 12.5,
    "pass_rate": 60.0
  },
  "test_results": [
    {
      "test_id": "TC_001",
      "test_name": "Test Login",
      "status": "passed",
      "duration": 2.5,
      "start_time": "2024-01-15T10:30:00",
      "end_time": "2024-01-15T10:30:02.5",
      "error_message": null,
      "stack_trace": null,
      "screenshots": [],
      "metadata": {}
    }
  ]
}
```

## Integration with pytest

### Using with pytest Fixtures

```python
import pytest
from raptor.utils.reporter import TestReporter, TestResult, TestStatus
from datetime import datetime

@pytest.fixture(scope="session")
def test_reporter():
    """Create a test reporter for the session."""
    reporter = TestReporter(report_dir="reports")
    reporter.start_suite("pytest Test Suite")
    yield reporter
    reporter.end_suite()
    reporter.generate_html_report()
    reporter.export_json()

@pytest.fixture(autouse=True)
def record_test_result(request, test_reporter):
    """Automatically record test results."""
    start_time = datetime.now()
    yield
    end_time = datetime.now()
    
    # Determine test status
    if hasattr(request.node, 'rep_call'):
        if request.node.rep_call.passed:
            status = TestStatus.PASSED
        elif request.node.rep_call.failed:
            status = TestStatus.FAILED
        elif request.node.rep_call.skipped:
            status = TestStatus.SKIPPED
        else:
            status = TestStatus.ERROR
    else:
        status = TestStatus.PASSED
    
    # Create test result
    result = TestResult(
        test_id=request.node.nodeid,
        test_name=request.node.name,
        status=status,
        duration=(end_time - start_time).total_seconds(),
        start_time=start_time,
        end_time=end_time
    )
    
    test_reporter.add_test_result(result)
```

### Capturing Screenshots on Failure

```python
@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, page, test_reporter):
    """Capture screenshot on test failure."""
    yield
    
    if request.node.rep_call.failed:
        screenshot_path = f"screenshots/{request.node.name}.png"
        page.screenshot(path=screenshot_path)
        
        # Add screenshot to the last test result
        if test_reporter.test_results:
            test_reporter.test_results[-1].screenshots.append(screenshot_path)
```

## Best Practices

### 1. Organize Reports by Date

```python
from datetime import datetime

date_str = datetime.now().strftime("%Y-%m-%d")
reporter = TestReporter(report_dir=f"reports/{date_str}")
```

### 2. Use Descriptive Test Names

```python
result = TestResult(
    test_id="TC_LOGIN_001",
    test_name="Test Login with Valid Credentials - Chrome Browser",
    # ... other fields
)
```

### 3. Include Relevant Metadata

```python
metadata = {
    "browser": "chromium",
    "browser_version": "120.0",
    "environment": "staging",
    "test_type": "functional",
    "priority": "high",
    "test_data_id": "user_001",
    "execution_node": "jenkins-node-1"
}
```

### 4. Capture Screenshots Strategically

```python
# Capture on failure
if test_failed:
    screenshots = [
        "screenshots/before_action.png",
        "screenshots/at_failure.png",
        "screenshots/page_state.png"
    ]

# Capture for visual verification
if visual_test:
    screenshots = [
        "screenshots/baseline.png",
        "screenshots/actual.png",
        "screenshots/diff.png"
    ]
```

### 5. Clean Up Old Reports

```python
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_reports(report_dir, days_to_keep=7):
    """Remove reports older than specified days."""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    for report_file in Path(report_dir).glob("*.html"):
        if report_file.stat().st_mtime < cutoff_date.timestamp():
            report_file.unlink()
```

## Advanced Usage

### Custom Report Styling

You can customize the HTML report appearance by modifying the CSS in the reporter:

```python
# Extend TestReporter class
class CustomReporter(TestReporter):
    def _get_css_styles(self):
        # Return custom CSS
        return """
        /* Your custom CSS here */
        """
```

### Multiple Report Formats

```python
# Generate multiple report formats
reporter.generate_html_report(output_file="report.html")
reporter.generate_html_report(output_file="report_no_screenshots.html", embed_screenshots=False)
reporter.export_json(output_file="results.json")
```

### Parallel Test Execution

```python
from threading import Lock

class ThreadSafeReporter(TestReporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = Lock()
    
    def add_test_result(self, result):
        with self._lock:
            super().add_test_result(result)
```

## Troubleshooting

### Screenshots Not Appearing

- Verify screenshot paths are correct
- Check file permissions
- Ensure screenshots exist before generating report
- Use absolute paths or paths relative to report directory

### Large Report Files

- Use `embed_screenshots=False` to link instead of embed
- Compress screenshots before adding to report
- Clean up old screenshots regularly

### Missing Statistics

- Ensure `start_suite()` is called before adding results
- Call `end_suite()` before generating reports
- Verify test results are added with `add_test_result()`

## See Also

- [Examples](../examples/reporter_example.py)
- [API Reference](API_REFERENCE.md)
- [pytest Integration Guide](PYTEST_INTEGRATION.md)
