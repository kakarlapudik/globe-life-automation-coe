# Property Test: Screenshot Capture Reliability

## Overview

This document describes the property-based test for **Property 9: Screenshot Capture Reliability**, which validates that screenshots are reliably captured and saved with unique identifiers when test failures occur.

**Validates:** Requirements 9.1

## Property Statement

> For any test failure, a screenshot should be captured and saved with a unique identifier.

## Test Implementation

**File:** `tests/test_property_screenshot_capture.py`

### Property Test Function

```python
@pytest.mark.asyncio
@given(failures=test_failure_scenarios)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_property_screenshot_capture_reliability(failures, temp_screenshot_dir):
    """
    Property Test: Screenshot Capture Reliability
    
    Tests that screenshots:
    1. Are always captured when tests fail
    2. Have unique identifiers/filenames
    3. Are created as actual files
    4. Can be accessed and read
    5. Are properly tracked for reporting
    """
```

### Test Strategy

The property test uses Hypothesis to generate random test failure scenarios and verifies the following properties:

#### Property 1: Screenshot Capture
- **Assertion:** Screenshot path is returned for every test failure
- **Validation:** Path is not None and is a valid string

#### Property 2: File Existence
- **Assertion:** Screenshot file exists at the returned path
- **Validation:** `os.path.exists()` returns True

#### Property 3: File Readability
- **Assertion:** Screenshot file is readable and non-empty
- **Validation:** File is a regular file with size > 0

#### Property 4: Unique Identifiers
- **Assertion:** Each screenshot has a unique path/filename
- **Validation:** No duplicate paths in the set of all screenshots

#### Property 5: Count Consistency
- **Assertion:** Number of screenshots matches number of failures
- **Validation:** `len(screenshots) == len(failures)`

#### Property 6: Uniqueness Guarantee
- **Assertion:** All screenshot paths are unique
- **Validation:** `len(set(paths)) == len(paths)`

#### Property 7: Filename Format
- **Assertion:** Screenshot filenames follow expected format
- **Validation:** Filenames start with "failure_" and end with ".png"

## Test Data Generation

The test uses Hypothesis strategies to generate random test failure scenarios:

```python
test_failure_scenarios = st.lists(
    st.tuples(
        st.text(min_size=5, max_size=50),  # test_name
        st.sampled_from([
            "AssertionError",
            "TimeoutError",
            "ElementNotFoundError",
            "NetworkError",
            "ValidationError"
        ]),  # error_type
        st.text(min_size=10, max_size=100)  # error_message
    ),
    min_size=1,
    max_size=10
)
```

This generates:
- 1-10 test failures per test run
- Random test names (5-50 characters)
- Various error types
- Random error messages (10-100 characters)
- 100 different test scenarios (max_examples=100)

## Mock Implementation

The test uses mock objects to simulate screenshot capture without requiring a real browser:

### MockPage
Simulates Playwright's Page object and creates actual PNG files when `screenshot()` is called.

### MockBasePage
Simulates the RAPTOR BasePage class with the `take_screenshot()` method.

### FailureHandler
Simulates a test framework that automatically captures screenshots on test failures.

## Additional Test Cases

Beyond the main property test, the suite includes specific test cases for:

1. **Single Failure:** Basic screenshot capture for one test failure
2. **Multiple Failures (Same Test):** Ensures unique screenshots even for the same test
3. **Special Characters:** Validates filename sanitization for special characters
4. **Custom Names:** Tests custom screenshot naming
5. **Custom Paths:** Tests custom screenshot locations
6. **Full Page:** Tests full-page screenshot capture
7. **Rapid Captures:** Tests uniqueness with rapid successive captures
8. **Directory Creation:** Tests automatic directory creation
9. **File Format:** Validates PNG format with proper signature

## Running the Tests

### Run All Screenshot Property Tests
```bash
pytest tests/test_property_screenshot_capture.py -v
```

### Run Only the Main Property Test
```bash
pytest tests/test_property_screenshot_capture.py::test_property_screenshot_capture_reliability -v
```

### Run with Hypothesis Statistics
```bash
pytest tests/test_property_screenshot_capture.py -v --hypothesis-show-statistics
```

### Run with More Examples
```bash
pytest tests/test_property_screenshot_capture.py -v --hypothesis-seed=12345
```

## Expected Results

All tests should pass, demonstrating that:

✅ Screenshots are captured for every test failure  
✅ Each screenshot has a unique identifier  
✅ Screenshot files are created and accessible  
✅ Filenames are properly formatted and sanitized  
✅ The system handles edge cases (special characters, rapid captures, etc.)  

## Integration with Test Reporter

The screenshot capture mechanism integrates with the TestReporter class:

```python
# In test execution
try:
    # Test code that might fail
    await some_test_operation()
except Exception as e:
    # Capture screenshot on failure
    screenshot_path = await page.take_screenshot(name=f"failure_{test_name}")
    
    # Add to test result
    test_result = TestResult(
        test_id=test_id,
        test_name=test_name,
        status=TestStatus.FAILED,
        error_message=str(e),
        screenshots=[screenshot_path]
    )
    reporter.add_test_result(test_result)
```

## Screenshot Naming Convention

Screenshots follow this naming pattern:

```
failure_{sanitized_test_name}_{timestamp}.png
```

Where:
- `failure_` prefix identifies it as a failure screenshot
- `{sanitized_test_name}` is the test name with special characters replaced
- `{timestamp}` is in format `YYYYMMDD_HHMMSS_ffffff` (includes microseconds)
- `.png` extension indicates PNG format

Example: `failure_test_login_validation_20241128_143052_123456.png`

## Benefits of Property-Based Testing

This property-based approach provides several advantages:

1. **Comprehensive Coverage:** Tests 100 different failure scenarios automatically
2. **Edge Case Discovery:** Hypothesis finds edge cases we might not think of
3. **Regression Prevention:** Ensures screenshot capture works across all scenarios
4. **Confidence:** Validates the property holds for any test failure, not just specific examples
5. **Maintainability:** Single test validates multiple aspects of screenshot capture

## Troubleshooting

### Test Failures

If the property test fails, check:

1. **File System Permissions:** Ensure the test can create directories and files
2. **Disk Space:** Verify sufficient disk space for screenshot files
3. **Path Length:** On Windows, ensure paths don't exceed MAX_PATH
4. **Concurrent Access:** Check for file locking issues

### Common Issues

**Issue:** Screenshots not unique  
**Solution:** Verify timestamp includes microseconds for uniqueness

**Issue:** Special characters in filenames  
**Solution:** Ensure filename sanitization is working correctly

**Issue:** Files not created  
**Solution:** Check directory creation and file write permissions

## Related Documentation

- [Test Reporter Guide](TEST_REPORTER_GUIDE.md)
- [Base Page Implementation](../raptor/pages/base_page.py)
- [Requirements Document](../../.kiro/specs/raptor-playwright-python/requirements.md)
- [Design Document](../../.kiro/specs/raptor-playwright-python/design.md)

## Conclusion

The screenshot capture reliability property test ensures that the RAPTOR framework consistently captures screenshots for test failures with unique identifiers, providing essential debugging information for test analysis and failure investigation.
