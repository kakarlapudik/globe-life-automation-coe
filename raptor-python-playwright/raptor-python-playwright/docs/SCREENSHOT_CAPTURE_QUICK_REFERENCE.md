# Screenshot Capture - Quick Reference

## Property 9: Screenshot Capture Reliability

**Validates:** Requirements 9.1

> For any test failure, a screenshot should be captured and saved with a unique identifier.

## Quick Test Commands

```bash
# Run all screenshot property tests
pytest tests/test_property_screenshot_capture.py -v

# Run main property test only
pytest tests/test_property_screenshot_capture.py::test_property_screenshot_capture_reliability -v

# Run with statistics
pytest tests/test_property_screenshot_capture.py -v --hypothesis-show-statistics
```

## Screenshot Capture Usage

### Basic Screenshot
```python
screenshot_path = await page.take_screenshot()
```

### Named Screenshot
```python
screenshot_path = await page.take_screenshot(name="login_page")
```

### Full Page Screenshot
```python
screenshot_path = await page.take_screenshot(name="full_page", full_page=True)
```

### Custom Path
```python
screenshot_path = await page.take_screenshot(path="/custom/path/screenshot.png")
```

## Screenshot Naming Pattern

```
failure_{sanitized_test_name}_{timestamp}.png
```

Example: `failure_test_login_20241128_143052_123456.png`

## Verified Properties

✅ Screenshots captured for every failure  
✅ Unique identifiers for each screenshot  
✅ Files created and accessible  
✅ Proper PNG format  
✅ Special characters sanitized  
✅ Rapid captures handled  
✅ Directories auto-created  

## Test Coverage

- **100 scenarios** tested via property-based testing
- **10 specific test cases** for edge cases
- **All tests passing** ✓

## Integration Example

```python
try:
    await some_test_operation()
except Exception as e:
    screenshot_path = await page.take_screenshot(name=f"failure_{test_name}")
    test_result = TestResult(
        test_id=test_id,
        test_name=test_name,
        status=TestStatus.FAILED,
        error_message=str(e),
        screenshots=[screenshot_path]
    )
    reporter.add_test_result(test_result)
```

## Files

- **Test:** `tests/test_property_screenshot_capture.py`
- **Implementation:** `raptor/pages/base_page.py`
- **Documentation:** `docs/PROPERTY_TEST_SCREENSHOT_CAPTURE.md`
