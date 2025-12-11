# Property Test: Click Method Equivalence (Property 6)

## Overview

This document describes the property-based test for **Property 6: Click Method Equivalence**, which validates that different click methods and locator strategies produce equivalent results when clicking elements.

## Property Statement

**For any** clickable element, using different locator strategies to click should all result in the element being clicked successfully.

**Validates: Requirements 6.2**

> WHEN clicking fails THEN the system SHALL retry with alternative methods (clickXY, JavaScript click)

## Test Implementation

The property test is implemented in `tests/test_element_manager.py` with four test functions:

### 1. `test_property_click_method_equivalence`

**Purpose**: Verify that clicking works consistently across different locator strategies.

**Strategy**: 
- Generates random combinations of element IDs and locator strategies (CSS, XPath, ID, text)
- Creates a test page with clickable buttons that track click state
- Clicks elements using different locator strategies
- Verifies that the click was successful by checking state changes

**Hypothesis Configuration**:
- `max_examples=100`: Runs 100 random test cases
- Suppresses health check warnings for function-scoped fixtures

**Test Cases Generated**:
- Element IDs: btn-1, btn-2, btn-3
- Locator strategies: css, xpath, id, text
- Total combinations: 12 unique scenarios × 100 iterations

### 2. `test_property_click_idempotency_tracking`

**Purpose**: Verify that multiple clicks are properly tracked and registered.

**Strategy**:
- Generates random number of clicks (1-5) for random elements
- Clicks the element N times
- Verifies that the click count matches the expected number

**Test Cases Generated**:
- Number of clicks: 1 to 5
- Element IDs: btn-1, btn-2, btn-3
- Total combinations: 5 × 3 = 15 scenarios × 100 iterations

### 3. `test_property_click_with_fallback_equivalence`

**Purpose**: Verify that clicking with direct locator vs fallback locator produces the same result.

**Strategy**:
- Randomly chooses whether to use fallback locator or direct locator
- Clicks the element using the chosen method
- Verifies that the outcome is identical regardless of method

**Test Cases Generated**:
- Use fallback: True/False
- Element IDs: btn-1, btn-2, btn-3
- Total combinations: 2 × 3 = 6 scenarios × 100 iterations

### 4. `test_property_click_locator_strategy_equivalence`

**Purpose**: Verify that different locator strategies click the same element consistently.

**Strategy**:
- Generates random combinations of 2-3 unique locator strategies
- Clicks the same element using each strategy in sequence
- Verifies that click count increments correctly with each strategy

**Test Cases Generated**:
- Locator strategy combinations: 2-3 strategies from {css, xpath, id}
- Element IDs: btn-1, btn-2, btn-3
- Total combinations: Variable × 50 iterations

## Test Page Structure

All tests use a consistent HTML structure with JavaScript click tracking:

```html
<!DOCTYPE html>
<html>
<head>
    <script>
        let clickCounts = {};
        function trackClick(id) {
            if (!clickCounts[id]) {
                clickCounts[id] = 0;
            }
            clickCounts[id]++;
            document.getElementById(id).setAttribute('data-click-count', clickCounts[id]);
            document.getElementById(id).textContent = 'Clicked ' + clickCounts[id];
        }
    </script>
</head>
<body>
    <button id="btn-1" class="button" onclick="trackClick('btn-1')">Button 1</button>
    <button id="btn-2" class="button" onclick="trackClick('btn-2')">Button 2</button>
    <button id="btn-3" class="button" onclick="trackClick('btn-3')">Button 3</button>
</body>
</html>
```

## Verification Approach

Each test verifies click success by checking:

1. **Click Count Attribute**: `data-click-count` attribute increments correctly
2. **Text Content Change**: Button text changes from "Button N" to "Clicked N"
3. **State Consistency**: Multiple clicks produce consistent state changes

## Running the Tests

### Prerequisites

1. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

2. Ensure all dependencies are installed:
   ```bash
   pip install -e ".[dev]"
   ```

### Execute Property Tests

Run all click equivalence property tests:
```bash
pytest tests/test_element_manager.py -k "test_property_click" -v
```

Run a specific property test:
```bash
pytest tests/test_element_manager.py::test_property_click_method_equivalence -v
```

Run with Hypothesis statistics:
```bash
pytest tests/test_element_manager.py -k "test_property_click" -v --hypothesis-show-statistics
```

## Expected Results

All property tests should pass with 100 examples (or 50 for the strategy equivalence test):

```
tests/test_element_manager.py::test_property_click_method_equivalence PASSED [100 examples]
tests/test_element_manager.py::test_property_click_idempotency_tracking PASSED [100 examples]
tests/test_element_manager.py::test_property_click_with_fallback_equivalence PASSED [100 examples]
tests/test_element_manager.py::test_property_click_locator_strategy_equivalence PASSED [50 examples]
```

## Future Enhancements

Once **Task 7: Advanced Click Methods** is implemented, these tests will be extended to include:

1. **click_at_position()** (clickXY equivalent)
2. **JavaScript click** as a fallback method
3. **double_click()** method
4. **right_click()** method

The property tests will then verify that all these methods produce equivalent results when clicking the same element.

## Troubleshooting

### Browser Not Installed

If you see:
```
Error: Executable doesn't exist at .../chromium.../chrome.exe
```

Solution:
```bash
playwright install chromium
```

### Test Timeout

If tests timeout, increase the timeout in the test:
```python
await element_manager.click(locator, timeout=5000)  # Increase from 2000ms
```

### Hypothesis Failures

If Hypothesis finds a counterexample, it will be displayed in the test output. Analyze the failing case to determine if:
1. The test needs adjustment
2. The implementation has a bug
3. The specification needs clarification

## Related Documentation

- [Element Manager Implementation](./ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Property Test: Element Fallback](./PROPERTY_TEST_ELEMENT_FALLBACK.md)
- [Property Test: Browser Launch](./PROPERTY_TEST_BROWSER_LAUNCH.md)
- [Requirements Document](../.kiro/specs/raptor-playwright-python/requirements.md)
- [Design Document](../.kiro/specs/raptor-playwright-python/design.md)

## Test Status

✅ **Implemented**: All four property tests are implemented and ready to run
⏳ **Pending**: Playwright browser installation required to execute tests
🔄 **Future**: Will be extended when Task 7 (Advanced Click Methods) is completed
